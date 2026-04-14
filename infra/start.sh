#!/usr/bin/env bash
# Start all hackathon infrastructure services.
# Usage: ./start.sh          # foreground (Ctrl+C stops everything)
#        ./start.sh -d       # daemon mode (survives logout, use stop.sh to stop)
#
# Reads config from .env (create from .env.example).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
ENV_FILE="$SCRIPT_DIR/.env"
PID_FILE="$SCRIPT_DIR/infra.pid"

# --- Daemon mode: re-exec detached ---
if [[ "${1:-}" == "-d" || "${1:-}" == "--daemon" ]]; then
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Already running (pid $(cat "$PID_FILE")). Use ./stop.sh first."
        exit 1
    fi
    nohup setsid "$0" --_daemonized > "$LOG_DIR/start.log" 2>&1 &
    mkdir -p "$LOG_DIR"
    echo $! > "$PID_FILE"
    echo "Started in daemon mode (pid $!, log: $LOG_DIR/start.log)"
    echo "Stop with: ./stop.sh"
    exit 0
fi

# Strip internal flag so the rest of the script runs normally
if [[ "${1:-}" == "--_daemonized" ]]; then shift; fi

# --- Load config ---
if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: $ENV_FILE not found. Copy .env.example and fill in your keys:"
    echo "  cp .env.example .env"
    exit 1
fi
source "$ENV_FILE"

: "${OLLAMA_API_KEY:?Set OLLAMA_API_KEY in .env}"
: "${DIRIGERA_MCP_DIR:?Set DIRIGERA_MCP_DIR in .env (path to mcp-agents/dirigera/fastmcp)}"

# Defaults for optional settings
OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1}"
OLLAMA_PORT="${OLLAMA_PORT:-11434}"
OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-4}"
OLLAMA_MAX_LOADED_MODELS="${OLLAMA_MAX_LOADED_MODELS:-3}"
OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:-60m}"
OLLAMA_MODELS="${OLLAMA_MODELS:-gemma4:e2b gemma3:latest qwen3:14b}"
OLLAMA_PROXY_HOST="${OLLAMA_PROXY_HOST:-127.0.0.1}"
OLLAMA_PROXY_PORT="${OLLAMA_PROXY_PORT:-11435}"
DIRIGERA_MCP_HOST="${DIRIGERA_MCP_HOST:-127.0.0.1}"
DIRIGERA_MCP_PORT="${DIRIGERA_MCP_PORT:-8000}"
CLOUDFLARED_BIN="${CLOUDFLARED_BIN:-/tmp/cloudflared}"
CLOUDFLARED_TUNNEL_NAME="${CLOUDFLARED_TUNNEL_NAME:-dirigera-mcp}"

mkdir -p "$LOG_DIR"

PIDS=()

cleanup() {
    echo ""
    echo "Stopping all services..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null
    rm -f "$PID_FILE"
    echo "All services stopped."
}
trap cleanup EXIT INT TERM

start_service() {
    local name="$1"
    shift
    local log="$LOG_DIR/$name.log"
    "$@" > "$log" 2>&1 &
    PIDS+=($!)
    echo "Starting $name (pid: $!, log: $log)"
}

# --- 1. Ollama ---
if curl -sf "http://$OLLAMA_HOST:$OLLAMA_PORT/api/tags" >/dev/null 2>&1; then
    echo "Ollama already running on $OLLAMA_HOST:$OLLAMA_PORT — skipping."
else
    start_service ollama env \
        OLLAMA_HOST="$OLLAMA_HOST:$OLLAMA_PORT" \
        OLLAMA_NUM_PARALLEL="$OLLAMA_NUM_PARALLEL" \
        OLLAMA_MAX_LOADED_MODELS="$OLLAMA_MAX_LOADED_MODELS" \
        OLLAMA_KEEP_ALIVE="$OLLAMA_KEEP_ALIVE" \
        OLLAMA_ORIGINS="*" \
        ollama serve

    echo "Waiting for Ollama to be ready..."
    for i in $(seq 1 15); do
        if curl -sf "http://$OLLAMA_HOST:$OLLAMA_PORT/api/tags" >/dev/null 2>&1; then
            echo "Ollama is ready."
            break
        fi
        sleep 1
    done
fi

# Pre-pull models (in background, won't block startup)
for model in $OLLAMA_MODELS; do
    if ! curl -sf "http://$OLLAMA_HOST:$OLLAMA_PORT/api/tags" | grep -q "\"$model\""; then
        echo "Pulling model: $model (background)"
        curl -sf "http://$OLLAMA_HOST:$OLLAMA_PORT/api/pull" \
            -d "{\"name\": \"$model\"}" >/dev/null 2>&1 &
    fi
done

# --- 2. Ollama auth proxy ---
start_service ollama-proxy \
    pixi run -e default python "$SCRIPT_DIR/ollama_proxy.py" \
        --api-key "$OLLAMA_API_KEY" \
        --host "$OLLAMA_PROXY_HOST" \
        --port "$OLLAMA_PROXY_PORT" \
        --ollama-url "http://$OLLAMA_HOST:$OLLAMA_PORT"

# --- 3. Dirigera MCP server ---
start_service dirigera-mcp \
    uv run --directory "$DIRIGERA_MCP_DIR" dirigeramcp.py \
        --transport streamable-http --auth \
        --host "$DIRIGERA_MCP_HOST" \
        --port "$DIRIGERA_MCP_PORT"

# --- 4. Cloudflare tunnel ---
start_service cloudflared \
    "$CLOUDFLARED_BIN" tunnel run "$CLOUDFLARED_TUNNEL_NAME"

echo ""
echo "All services started. PIDs: ${PIDS[*]}"
echo "Logs in: $LOG_DIR/"
echo ""
echo "  tail -f $LOG_DIR/ollama.log"
echo "  tail -f $LOG_DIR/ollama-proxy.log"
echo "  tail -f $LOG_DIR/dirigera-mcp.log"
echo "  tail -f $LOG_DIR/cloudflared.log"
echo ""

# Write PID file for stop.sh (covers both foreground and daemon mode)
echo $$ > "$PID_FILE"

echo "Press Ctrl+C to stop all services (or ./stop.sh if running as daemon)."

# Wait for any child to exit — if one crashes, report it
while true; do
    for i in "${!PIDS[@]}"; do
        pid="${PIDS[$i]}"
        if ! kill -0 "$pid" 2>/dev/null; then
            wait "$pid" 2>/dev/null || true
            echo "WARNING: Process $pid exited (check logs)"
            unset 'PIDS[$i]'
        fi
    done
    # If all processes are gone, exit
    if [[ ${#PIDS[@]} -eq 0 ]]; then
        echo "All services have exited."
        exit 1
    fi
    sleep 5
done
