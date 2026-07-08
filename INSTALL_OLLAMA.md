# Install Ollama to Run OpenManus

## Problem
You're seeing errors like:
```
Error code: 401 - {'error': {'code': 'authentication_error', 'message': 'Invalid Anthropic API Key'
```

But this is misleading! The real issue is that **Ollama is not installed or not running**.

## Solution

Install the Ollama server (the binary that runs LLMs locally).

### Step 1: Install Ollama Server

**Option A: Using Docker (Easiest)**
```bash
docker run -d -p 11434:11434 --name ollama -v ollama:/root/.ollama ollama/ollama
```

**Option B: Direct Download (macOS/Windows)**
- Visit: https://ollama.com/download
- Download and install the app

**Option C: Linux Installation**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Pull a Model

Once Ollama is installed, pull the model:

```bash
ollama pull llama3.2
```

### Step 3: Verify Ollama is Running

```bash
curl http://localhost:11434
```

Expected response:
```json
{"error":"model \"\" not found"}
```
(This is normal - it means Ollama is running but no model was specified)

### Step 4: Run OpenManus

```bash
cd /workspace/project/OpenManus
python main.py
```

## What Was Happening

The config file (`config/config.toml`) was correctly set to use Ollama:
```toml
[llm]
api_type = 'ollama'
base_url = "http://localhost:11434/v1"
model = "llama3.2"
```

But the Ollama **server** wasn't installed or running, so:
1. The app couldn't connect to `localhost:11434`
2. The OpenAI SDK tried to authenticate anyway
3. It gave a confusing "Anthropic API Key" error

## Alternative: Use Cloud LLMs

If you don't want to install Ollama, you can use cloud APIs:

### OpenAI
1. Get an API key from: https://platform.openai.com/api-keys
2. Update `config/config.toml`:
```toml
[llm]
api_type = 'openai'
model = "gpt-4o-mini"
api_key = "sk-your-api-key-here"
```

### Anthropic (Claude)
1. Get an API key from: https://console.anthropic.com/
2. Update `config/config.toml`:
```toml
[llm]
api_type = 'anthropic'
model = "claude-3-5-sonnet-latest"
api_key = "sk-ant-api-key-here"
```

## Check Ollama Status

If you think Ollama is installed but still getting errors:

```bash
# Check if Ollama is running
ps aux | grep ollama

# Or check the port
lsof -i :11434

# Check logs (Docker)
docker logs ollama
```

## Install Ollama Python Client

The Python client is already installed, but if you need to reinstall:

```bash
pip install ollama
```
