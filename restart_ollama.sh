#!/bin/bash
# Restart Ollama daemon

echo "=== Ollama Restart Script ==="

# Check if running
if pgrep -x "ollama" > /dev/null; then
    echo "Ollama is running. Restarting..."
    
    # On macOS, kill the GUI app
    if [ "$(uname)" == "Darwin" ]; then
        pkill -f Ollama.app
        sleep 2
        
        # Restart the app
        open -a Ollama
        echo "Restarted Ollama app"
    else
        # Linux/other - kill and restart daemon
        pkill ollama
        sleep 2
        
        # Start daemon in background
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        echo "Restarted Ollama daemon"
    fi
else
    echo "Ollama is not running. Starting..."
    
    if [ "$(uname)" == "Darwin" ]; then
        open -a Ollama
        echo "Started Ollama app"
    else
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        echo "Started Ollama daemon"
    fi
fi

# Wait for it to start
echo "Waiting for Ollama to initialize..."
sleep 5

# Check API
echo ""
echo "=== Checking API ==="
curl -s http://localhost:11434/api/tags || echo "API not responding yet"

# Show model list
echo ""
echo "=== Model List via CLI ==="
ollama list

echo ""
echo "Done!"
