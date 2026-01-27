#!/usr/bin/env python3
"""Lab 10: Simple A2A Agent Registry

A minimal registry server for discovering agents in the lab.
Run this on a central machine and have participants register their agents.

Usage:
    pixi run registry
"""
import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Registry storage (in-memory for simplicity)
agents: dict[str, dict] = {}
message_history: list[dict] = []  # Last 20 messages
MAX_HISTORY = 20

app = FastAPI(title="A2A Agent Registry", version="1.0.0")


class RegisterRequest(BaseModel):
    """Request to register an agent."""
    card_url: Optional[str] = None
    agent_url: Optional[str] = None
    name: Optional[str] = None


class MessageRequest(BaseModel):
    """Request to send a message to an agent."""
    agent_url: str
    message: str


# --- API Endpoints ---

@app.post("/register")
async def register_agent(req: RegisterRequest):
    """Register an agent by its card URL or base URL."""
    card_url = req.card_url
    if not card_url and req.agent_url:
        card_url = f"{req.agent_url.rstrip('/')}/.well-known/agent-card.json"

    if not card_url:
        raise HTTPException(400, "Provide card_url or agent_url")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(card_url)
            resp.raise_for_status()
            card = resp.json()
    except Exception as err:
        raise HTTPException(400, f"Failed to fetch agent card: {err}") from err

    name = req.name or card.get("name", "Unknown Agent")
    url = card.get("url", req.agent_url or card_url)
    description = card.get("description", "No description")
    skills = [s.get("name", s.get("id", "unknown")) for s in card.get("skills", [])]

    # Extract provider/author info
    provider = card.get("provider", {})
    author = provider.get("organization", provider.get("name", ""))
    author_url = provider.get("url", "")
    version = card.get("version", "")

    now = datetime.now().isoformat()
    agents[url] = {
        "name": name,
        "description": description,
        "url": url,
        "card_url": card_url,
        "skills": skills,
        "author": author,
        "author_url": author_url,
        "version": version,
        "card": card,  # Store full card for popup
        "registered_at": agents.get(url, {}).get("registered_at", now),
        "last_seen": now,
    }

    print(f"[+] Registered: {name} at {url}")
    return {"status": "registered", "name": name, "url": url}


@app.delete("/agents/{agent_url:path}")
async def unregister_agent(agent_url: str):
    """Unregister an agent."""
    if agent_url in agents:
        name = agents[agent_url]["name"]
        del agents[agent_url]
        print(f"[-] Unregistered: {name}")
        return {"status": "unregistered"}
    raise HTTPException(404, "Agent not found")


@app.get("/agents")
async def list_agents():
    """List all registered agents."""
    return {"agents": list(agents.values())}


@app.get("/agents/{agent_url:path}/card")
async def get_agent_card(agent_url: str):
    """Get full agent card."""
    if agent_url in agents:
        return agents[agent_url].get("card", {})
    raise HTTPException(404, "Agent not found")


@app.get("/history")
async def get_history():
    """Get message history."""
    return {"history": message_history}


@app.post("/send-message")
async def send_message(req: MessageRequest):
    """Send an A2A message to an agent using a2a-sdk."""
    from uuid import uuid4
    from a2a.client import A2ACardResolver, A2AClient
    from a2a.types import MessageSendParams, SendMessageRequest, GetTaskRequest

    if req.agent_url not in agents:
        raise HTTPException(404, "Agent not registered")

    agent = agents[req.agent_url]
    agent_name = agent.get("name", "Unknown")
    timestamp = datetime.now().isoformat()

    def add_to_history(response_text: str, is_error: bool = False):
        """Add message to history."""
        message_history.insert(0, {
            "agent_name": agent_name,
            "agent_url": req.agent_url,
            "message": req.message,
            "response": response_text,
            "is_error": is_error,
            "timestamp": timestamp,
        })
        # Keep only last MAX_HISTORY
        while len(message_history) > MAX_HISTORY:
            message_history.pop()

    try:
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            # Get agent card and create client
            resolver = A2ACardResolver(httpx_client=http_client, base_url=agent["url"])
            agent_card = await resolver.get_agent_card()
            client = A2AClient(httpx_client=http_client, agent_card=agent_card)

            # Send message
            request = SendMessageRequest(
                id=str(uuid4()),
                params=MessageSendParams(
                    message={
                        "role": "user",
                        "parts": [{"kind": "text", "text": req.message}],
                        "messageId": uuid4().hex,
                    }
                ),
            )
            response = await client.send_message(request)

            # Extract result
            result = response.root.result if hasattr(response, "root") else response.result

            # If it's a Task, poll for completion
            if hasattr(result, "id") and hasattr(result, "status"):
                task_id = result.id
                for _ in range(30):
                    task_request = GetTaskRequest(id=str(uuid4()), params={"id": task_id})
                    task_response = await client.get_task(task_request)
                    task = task_response.root.result if hasattr(task_response, "root") else task_response.result

                    if hasattr(task, "status") and hasattr(task.status, "state"):
                        state = str(task.status.state.value) if hasattr(task.status.state, "value") else str(task.status.state)
                        if state == "completed":
                            if hasattr(task, "artifacts") and task.artifacts:
                                for artifact in task.artifacts:
                                    if hasattr(artifact, "parts"):
                                        for part in artifact.parts:
                                            if hasattr(part, "root") and hasattr(part.root, "text"):
                                                add_to_history(part.root.text)
                                                return {"response": part.root.text}
                                            if hasattr(part, "text"):
                                                add_to_history(part.text)
                                                return {"response": part.text}
                            add_to_history("Completed (no text)")
                            return {"response": "Completed (no text)"}
                        if state in ("failed", "canceled"):
                            add_to_history(f"Task {state}", is_error=True)
                            return {"response": f"Task {state}"}

                    await asyncio.sleep(1)

                add_to_history("Timeout waiting for response", is_error=True)
                return {"response": "Timeout waiting for response"}

            # Direct message response
            if hasattr(result, "parts") and result.parts:
                for part in result.parts:
                    if hasattr(part, "root") and hasattr(part.root, "text"):
                        add_to_history(part.root.text)
                        return {"response": part.root.text}
                    if hasattr(part, "text"):
                        add_to_history(part.text)
                        return {"response": part.text}

            add_to_history(str(response))
            return {"response": str(response)}

    except Exception as err:
        add_to_history(f"Error: {err}", is_error=True)
        raise HTTPException(500, f"Failed to send message: {err}") from err


@app.get("/.well-known/agents/index.json")
async def agents_index():
    """A2A-style agent index."""
    return {
        "agents": [
            {"name": a["name"], "url": a["url"], "card_url": a["card_url"]}
            for a in agents.values()
        ]
    }


# --- Web UI ---

def generate_history_rows() -> str:
    """Generate HTML rows for message history."""
    if not message_history:
        return '<tr><td colspan="4" class="empty">No messages yet. Send a message to an agent!</td></tr>'

    rows = ""
    for h in message_history:
        ts = h.get("timestamp", "")[:19].replace("T", " ")  # Format timestamp
        agent = h.get("agent_name", "Unknown")
        msg = h.get("message", "")[:50]
        resp = h.get("response", "")[:80]
        error_class = "error-row" if h.get("is_error") else ""
        rows += f"""
        <tr class="{error_class}">
            <td class="timestamp">{ts}</td>
            <td class="name">{agent}</td>
            <td class="msg">{msg}{"..." if len(h.get("message", "")) > 50 else ""}</td>
            <td class="resp">{resp}{"..." if len(h.get("response", "")) > 80 else ""}</td>
        </tr>
        """
    return rows


@app.get("/", response_class=HTMLResponse)
async def web_ui():
    """Web UI with card popup and messaging."""
    import json

    agent_rows = ""
    for a in sorted(agents.values(), key=lambda x: x["last_seen"], reverse=True):
        skills = ", ".join(a["skills"]) if a["skills"] else "-"
        author = a.get("author", "-") or "-"
        version = a.get("version", "")
        version_badge = f'<span class="version">v{version}</span>' if version else ""
        card_json = json.dumps(a.get("card", {}), indent=2)

        agent_rows += f"""
        <tr data-url="{a['url']}" data-card='{json.dumps(a.get("card", {}))}'>
            <td class="name">{a['name']} {version_badge}</td>
            <td class="author">{author}</td>
            <td class="desc">{a['description'][:40]}...</td>
            <td class="url"><a href="{a['url']}" target="_blank">{a['url']}</a></td>
            <td class="skills">{skills}</td>
            <td class="actions">
                <button onclick="showCard(this.closest('tr'))" title="View Card">📄</button>
                <button onclick="showChat(this.closest('tr'))" title="Send Message">💬</button>
            </td>
        </tr>
        """

    if not agent_rows:
        agent_rows = '<tr><td colspan="6" class="empty">No agents registered yet. Run an agent with registration enabled!</td></tr>'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>A2A Agent Registry</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                min-height: 100vh;
                color: #fff;
                padding: 40px;
            }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                background: linear-gradient(90deg, #00d4ff, #7b2cbf);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .subtitle {{ color: #888; margin-bottom: 30px; }}
            .count {{
                background: #7b2cbf;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9rem;
                display: inline-block;
                margin-bottom: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: rgba(255,255,255,0.05);
                border-radius: 10px;
                overflow: hidden;
            }}
            th {{
                background: rgba(123, 44, 191, 0.3);
                padding: 15px;
                text-align: left;
                font-weight: 600;
            }}
            td {{
                padding: 12px 15px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }}
            tr:hover {{ background: rgba(255,255,255,0.05); }}
            .name {{ font-weight: 600; color: #00d4ff; }}
            .version {{
                background: rgba(0,212,255,0.2);
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 0.75rem;
                margin-left: 8px;
            }}
            .author {{ color: #aaa; }}
            .url a {{ color: #7b2cbf; text-decoration: none; }}
            .url a:hover {{ text-decoration: underline; }}
            .skills {{ color: #888; font-size: 0.9rem; }}
            .actions button {{
                background: rgba(255,255,255,0.1);
                border: none;
                padding: 8px 12px;
                border-radius: 5px;
                cursor: pointer;
                margin-right: 5px;
                font-size: 1rem;
                transition: background 0.2s;
            }}
            .actions button:hover {{ background: rgba(123, 44, 191, 0.5); }}
            .empty {{ text-align: center; color: #666; padding: 40px !important; }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                color: #666;
                font-size: 0.85rem;
            }}

            /* Modal */
            .modal {{
                display: none;
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background: rgba(0,0,0,0.8);
                z-index: 1000;
                justify-content: center;
                align-items: center;
            }}
            .modal.active {{ display: flex; }}
            .modal-content {{
                background: #1a1a2e;
                border-radius: 15px;
                padding: 30px;
                max-width: 700px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                border: 1px solid rgba(123, 44, 191, 0.5);
            }}
            .modal-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }}
            .modal-header h2 {{ color: #00d4ff; }}
            .modal-close {{
                background: none;
                border: none;
                color: #fff;
                font-size: 1.5rem;
                cursor: pointer;
            }}
            pre {{
                background: rgba(0,0,0,0.3);
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                font-size: 0.85rem;
                color: #aaa;
            }}

            /* Chat */
            .chat-input {{
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }}
            .chat-input input {{
                flex: 1;
                padding: 12px 15px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.2);
                background: rgba(0,0,0,0.3);
                color: #fff;
                font-size: 1rem;
            }}
            .chat-input button {{
                padding: 12px 25px;
                border-radius: 8px;
                border: none;
                background: linear-gradient(90deg, #00d4ff, #7b2cbf);
                color: #fff;
                font-weight: 600;
                cursor: pointer;
            }}
            .chat-input button:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            .chat-response {{
                margin-top: 15px;
                padding: 15px;
                background: rgba(0,212,255,0.1);
                border-radius: 8px;
                border-left: 3px solid #00d4ff;
            }}
            .chat-response.error {{
                background: rgba(255,0,0,0.1);
                border-left-color: #ff4444;
            }}
            .close-btn {{
                padding: 10px 25px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.3);
                background: rgba(255,255,255,0.1);
                color: #fff;
                cursor: pointer;
                font-size: 1rem;
            }}
            .close-btn:hover {{
                background: rgba(255,255,255,0.2);
            }}
            /* History table */
            .timestamp {{ color: #888; font-size: 0.85rem; }}
            .msg {{ color: #aaa; }}
            .resp {{ color: #ccc; }}
            .error-row {{ background: rgba(255, 68, 68, 0.1); }}
            .error-row .resp {{ color: #ff6666; }}
            #historyTable {{ margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>A2A Agent Registry</h1>
            <p class="subtitle">Jfokus 2026 - Physical Agent Lab</p>
            <div class="count">{len(agents)} agent(s) online</div>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Author</th>
                        <th>Description</th>
                        <th>URL</th>
                        <th>Skills</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {agent_rows}
                </tbody>
            </table>
            <p class="footer">
                Auto-refreshes every 10 seconds |
                <code>POST /register {{"agent_url": "http://your-ip:9999"}}</code>
            </p>

            <!-- Message History -->
            <h2 style="margin-top: 40px; color: #00d4ff;">📜 Message History</h2>
            <p class="subtitle" style="margin-bottom: 15px;">Last {MAX_HISTORY} messages</p>
            <table id="historyTable">
                <thead>
                    <tr>
                        <th style="width:120px;">Time</th>
                        <th style="width:150px;">Agent</th>
                        <th>Request</th>
                        <th>Response</th>
                    </tr>
                </thead>
                <tbody id="historyBody">
                    {generate_history_rows()}
                </tbody>
            </table>
        </div>

        <!-- Card Modal -->
        <div class="modal" id="cardModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>📄 Agent Card</h2>
                    <button class="modal-close" onclick="closeModal('cardModal')">&times;</button>
                </div>
                <pre id="cardContent"></pre>
            </div>
        </div>

        <!-- Chat Modal -->
        <div class="modal" id="chatModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>💬 Send Message to <span id="chatAgentName"></span></h2>
                    <button class="modal-close" onclick="closeAndRefresh('chatModal')">&times;</button>
                </div>
                <div class="chat-input">
                    <input type="text" id="chatMessage" placeholder="Type your message..."
                           onkeypress="if(event.key==='Enter')sendMessage()">
                    <button onclick="sendMessage()" id="sendBtn">Send</button>
                </div>
                <div id="chatResponse"></div>
                <div class="chat-actions" id="chatActions" style="display:none; margin-top:15px; text-align:right;">
                    <button onclick="closeAndRefresh('chatModal')" class="close-btn">Close</button>
                </div>
            </div>
        </div>

        <script>
            let currentAgentUrl = '';
            let refreshInterval = null;

            // Start auto-refresh via JavaScript (can be reliably stopped)
            function startAutoRefresh() {{
                if (!refreshInterval) {{
                    refreshInterval = setInterval(() => location.reload(), 10000);
                }}
            }}

            function stopAutoRefresh() {{
                if (refreshInterval) {{
                    clearInterval(refreshInterval);
                    refreshInterval = null;
                }}
            }}

            // Start refresh on page load
            startAutoRefresh();

            function showCard(row) {{
                stopAutoRefresh();
                const card = JSON.parse(row.dataset.card);
                document.getElementById('cardContent').textContent = JSON.stringify(card, null, 2);
                document.getElementById('cardModal').classList.add('active');
            }}

            function showChat(row) {{
                stopAutoRefresh();
                currentAgentUrl = row.dataset.url;
                const name = row.querySelector('.name').textContent.trim();
                document.getElementById('chatAgentName').textContent = name;
                document.getElementById('chatMessage').value = '';
                document.getElementById('chatResponse').innerHTML = '';
                document.getElementById('chatModal').classList.add('active');
                document.getElementById('chatMessage').focus();
            }}

            function closeModal(id) {{
                document.getElementById(id).classList.remove('active');
            }}

            function closeAndRefresh(id) {{
                document.getElementById(id).classList.remove('active');
                location.reload();
            }}

            async function sendMessage() {{
                const message = document.getElementById('chatMessage').value.trim();
                if (!message) return;

                const btn = document.getElementById('sendBtn');
                const responseDiv = document.getElementById('chatResponse');
                const actionsDiv = document.getElementById('chatActions');

                btn.disabled = true;
                btn.textContent = 'Sending...';
                responseDiv.innerHTML = '<em>Waiting for response...</em>';
                responseDiv.className = 'chat-response';
                actionsDiv.style.display = 'none';

                try {{
                    const resp = await fetch('/send-message', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{agent_url: currentAgentUrl, message: message}})
                    }});
                    const data = await resp.json();

                    if (resp.ok) {{
                        responseDiv.innerHTML = '<strong>Response:</strong><br>' + (data.response || 'No response');
                    }} else {{
                        responseDiv.innerHTML = '<strong>Error:</strong> ' + (data.detail || 'Unknown error');
                        responseDiv.className = 'chat-response error';
                    }}
                }} catch (err) {{
                    responseDiv.innerHTML = '<strong>Error:</strong> ' + err.message;
                    responseDiv.className = 'chat-response error';
                }}

                btn.disabled = false;
                btn.textContent = 'Send';
                actionsDiv.style.display = 'block';
            }}

            // Close card modal on escape (chat modal requires explicit close)
            document.addEventListener('keydown', (e) => {{
                if (e.key === 'Escape') {{
                    const cardModal = document.getElementById('cardModal');
                    if (cardModal.classList.contains('active')) {{
                        closeModal('cardModal');
                    }}
                    // Chat modal: don't close on escape, user must click Close button
                }}
            }});

            // Close card modal on backdrop click (chat modal requires explicit close)
            document.getElementById('cardModal').addEventListener('click', (e) => {{
                if (e.target === document.getElementById('cardModal')) closeModal('cardModal');
            }});
            // Chat modal: don't close on backdrop click, user must click X or Close button
        </script>
    </body>
    </html>
    """
    return html


# --- Cleanup old agents ---

async def healthcheck_agents():
    """Health-check agents every 5 minutes by re-fetching their cards."""
    while True:
        await asyncio.sleep(300)  # 5 minutes
        if not agents:
            continue

        print("[~] Health-checking registered agents...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            for url in list(agents.keys()):
                agent = agents.get(url)
                if not agent:
                    continue
                card_url = agent.get("card_url", f"{url.rstrip('/')}/.well-known/agent-card.json")
                try:
                    resp = await client.get(card_url)
                    resp.raise_for_status()
                    # Agent is alive, update last_seen
                    agents[url]["last_seen"] = datetime.now().isoformat()
                    print(f"    [✓] {agent['name']} - alive")
                except Exception:
                    # Agent is dead, remove it
                    name = agent.get("name", url)
                    del agents[url]
                    print(f"    [x] {name} - removed (unreachable)")


# --- Main ---

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("REGISTRY_PORT", "8000"))
    host = os.environ.get("REGISTRY_HOST", "0.0.0.0")

    print(f"""
╔═══════════════════════════════════════════════════════╗
║         A2A Agent Registry - Jfokus 2026              ║
╠═══════════════════════════════════════════════════════╣
║  Web UI:  http://{host}:{port}/
║  API:     http://{host}:{port}/agents
║                                                       ║
║  Register your agent:                                 ║
║  curl -X POST http://<this-ip>:{port}/register \\
║    -H "Content-Type: application/json" \\
║    -d '{{"agent_url": "http://<your-ip>:9999"}}'
╚═══════════════════════════════════════════════════════╝
""")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    config = uvicorn.Config(app, host=host, port=port, loop="asyncio")
    server = uvicorn.Server(config)

    loop.create_task(healthcheck_agents())
    loop.run_until_complete(server.serve())
