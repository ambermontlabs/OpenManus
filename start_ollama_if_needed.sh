#!/bin/bash
# Check if Ollama is running and start it if not

echo "Checking Ollama status..."

# Check if port 11434 is listening
if lsof -i :11434 > /dev/null 2>&1; then
    echo "✓ Ollama is running"
    
    # Test the API
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✓ Ollama API is responding"
    else
        echo "⚠ Ollama process running but API not responding - restarting..."
        pkill -f ollama 2>/dev/null || true
        sleep 2
        open -a Ollama
    fi
else
    echo "⚠ Ollama is not running - starting..."
    
    # Check if Ollama app exists
    if [ -d "/Applications/Ollama.app" ]; then
        open -a Ollama
        echo "Started Ollama app"
    else
        echo "❌ Ollama not found in /Applications/"
        echo "Please install from https://ollama.com/download"
        exit 1
    fi
fi

# Wait for Ollama to start
echo "Waiting for Ollama to initialize..."
sleep 5

# Verify it's working
if curl -s http://localhost:11434/api/tags | grep -q "models"; then
    echo "✓ Ollama is ready!"
    exit 0
else
    echo "❌ Ollama not responding properly"
    exit 1
fi
