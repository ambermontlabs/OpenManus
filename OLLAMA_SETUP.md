# Ollama Setup for OpenManus

This guide will help you set up Ollama for local LLM inference (free, no API key required).

## Prerequisites

- Docker (recommended for easy installation)
- or direct installation on your system

## Method 1: Using Docker (Recommended)

If you have Docker installed and the daemon is running:

```bash
# Start Ollama container
docker run -d -p 11434:11434 --name ollama -v ollama:/root/.ollama ollama/ollama

# Wait a few seconds for it to start
sleep 5

# Pull the model you need
docker exec -it ollama ollama pull llama3.2

# Verify Ollama is running
curl http://localhost:11434
```

## Method 2: Direct Installation

### macOS/Windows
Download and install from: https://ollama.com/download

### Linux

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start the Ollama service
sudo systemctl start ollama  # For systemd-based systems
# or
ollama serve &              # Run in background

# Pull the model
ollama pull llama3.2
```

## Verification

After installation, verify Ollama is running:

```bash
curl http://localhost:11434
```

You should get a response like:
```json
{"error":"model \"\" not found"}
```

This is actually a good sign - it means Ollama is running!

## Pull Models

```bash
# Base model
ollama pull llama3.2

# Vision model (optional)
ollama pull llama3.2-vision
```

## Usage with OpenManus

Once Ollama is installed and running:

1. Make sure your config file exists:
   ```bash
   cp config/config.example.toml config/config.toml
   ```

2. The `config.toml` is already configured for Ollama (see `config/config.toml`)

3. Run OpenManus:
   ```bash
   python main.py
   ```

## Troubleshooting

### Ollama not starting
- Check if port 11434 is already in use: `lsof -i :11434`
- Try a different port: `OLLAMA_HOST=0.0.0.0 OLLAMA_PORT=11435 ollama serve`

### Model not found
- Make sure you pulled the model: `ollama pull llama3.2`
- Check available models: `ollama list`

### Connection refused
- Verify Ollama is running: `curl http://localhost:11434`
- Check if the service is active: `systemctl status ollama`

## Alternative: LM Studio

If Ollama doesn't work for your environment, try LM Studio:

1. Download from: https://lmstudio.ai/
2. Install and launch LM Studio
3. Load a model from the UI
4. Start the local server (port 1234 by default)
5. Use `config/example-lmstudio.toml` as template

