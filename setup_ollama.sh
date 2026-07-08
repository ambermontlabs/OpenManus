#!/bin/bash
# Ollama Setup Script for OpenManus
# This script helps set up Ollama for local LLM inference

set -e

echo "=== OpenManus Ollama Setup Script ==="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Warning: Running as root. This may cause permission issues."
    echo ""
fi

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is already installed!"
    ollama --version
else
    echo "Installing Ollama..."
    
    # Try to install using the official installer
    if curl -fsSL https://ollama.com/install.sh | sh; then
        echo "✓ Ollama installed successfully!"
    else
        echo "ERROR: Failed to install Ollama using the official installer."
        echo ""
        echo "Manual installation options:"
        echo "  - macOS/Windows: Download from https://ollama.com/download"
        echo "  - Linux (Debian/Ubuntu): curl -fsSL https://ollama.com/install.sh | sh"
        echo "  - Linux (manual): Download binary from https://github.com/ollama/ollama/releases"
        echo ""
        exit 1
    fi
fi

echo ""
echo "Checking Ollama service..."
if curl -s http://localhost:11434 > /dev/null; then
    echo "✓ Ollama service is running!"
else
    echo "Starting Ollama service..."
    if command -v ollama &> /dev/null; then
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        echo "✓ Ollama service started in background (PID: $!)"
        sleep 3
        
        if curl -s http://localhost:11434 > /dev/null; then
            echo "✓ Ollama service is now running!"
        else
            echo "Warning: Could not verify Ollama service is running."
            echo "Please check /tmp/ollama.log for errors."
        fi
    else
        echo "ERROR: Ollama not found in PATH. Please install it manually."
        exit 1
    fi
fi

echo ""
echo "Pulling llama3.2 model (this may take a while)..."
ollama pull llama3.2

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "You can now run: python main.py"
echo ""
echo "For vision models, also run: ollama pull llama3.2-vision"
