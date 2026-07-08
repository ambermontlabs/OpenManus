# Ollama Configuration for OpenManus

## ✅ What's Been Done

The following has been set up to use Ollama for local inference:

1. **Config file created**: `/workspace/project/OpenManus/config/config.toml`
   - Configured for Ollama (`api_type = 'ollama'`)
   - Uses model: `llama3.2`
   - Base URL: `http://localhost:11434/v1`
   - No API key required for local Ollama

2. **Ollama Python client installed**: 
   - Installed package: `ollama` (v0.6.2)

3. **Setup script created**: `/workspace/project/OpenManus/setup_ollama.sh`
   - Automated setup for Ollama installation
   - Model pulling automation

4. **Documentation created**: `/workspace/project/OpenManus/OLLAMA_SETUP.md`
   - Comprehensive guide for Ollama setup
   - Docker and direct installation methods

## 📋 Setup Steps Required

### Step 1: Install Ollama Server

You need to install the Ollama server (not just the Python client). Choose one method:

#### Option A: Using Docker (Recommended)

```bash
# Start Ollama container
docker run -d -p 11434:11434 --name ollama -v ollama:/root/.ollama ollama/ollama
```

#### Option B: Direct Installation

**macOS/Windows:**
- Download from: https://ollama.com/download

**Linux (Debian/Ubuntu):**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Linux (manual):**
```bash
# Download from GitHub releases
curl -L https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64.tar.gz -o /tmp/ollama.tar.gz
tar -xzf /tmp/ollama.tar.gz -C /usr/local
```

### Step 2: Start Ollama Service

If not auto-started:
```bash
ollama serve &
```

### Step 3: Verify Ollama is Running

```bash
curl http://localhost:11434
```

Expected response: `{"error":"model \"\" not found"}` (this is normal!)

### Step 4: Pull a Model

```bash
ollama pull llama3.2
```

For vision capabilities (optional):
```bash
ollama pull llama3.2-vision
```

### Step 5: Run OpenManus

```bash
cd /workspace/project/OpenManus
python main.py
```

## 🔍 Configuration Details

Your `config.toml` is already set up:

```toml
[llm]
api_type = 'ollama'
model = "llama3.2"
base_url = "http://localhost:11434/v1"
api_key = "ollama"  # Placeholder (not used for Ollama)
max_tokens = 4096
temperature = 0.0

[llm.vision]
api_type = 'ollama'
model = "llama3.2-vision"
base_url = "http://localhost:11434/v1"
api_key = "ollama"  # Placeholder (not used for Ollama)
```

## ⚠️ Important Notes

1. **Ollama Server vs Python Client**: 
   - You installed the `ollama` Python package (this is just a client library)
   - You still need to install the `ollama` server separately
   - The server is a binary that runs on your system

2. **No API Key Required**: 
   - Ollama is free and local
   - No cloud API keys needed
   - All processing happens on your machine

3. **Dependencies**:
   - The project requires: openai, tiktoken, tenacity, pydantic
   - These are used to communicate with Ollama (which uses OpenAI-compatible API)

## 🔧 Troubleshooting

### "Connection refused" error
- Ollama server is not running
- Start it: `ollama serve &`

### "Model not found" error
- Pull the model first: `ollama pull llama3.2`

### Port already in use
- Check what's using port 11434: `lsof -i :11434`
- Or use a different port: `OLLAMA_PORT=11435 ollama serve`

## 📚 Alternative Options

If Ollama doesn't work in your environment:

1. **LM Studio**: Local LLM server with GUI
   - Download: https://lmstudio.ai/
   - Configure port 1234

2. **OpenAI API**: Cloud-based
   - Get key: https://platform.openai.com/api-keys
   - Update `config.toml` with your API key

3. **Anthropic API**: Cloud-based (Claude models)
   - Get key: https://console.anthropic.com/
   - Update `config.toml` with your API key

## 🎯 Next Steps

1. Install Ollama server (see Step 1 above)
2. Pull the llama3.2 model
3. Verify Ollama is running
4. Run `python main.py`

For detailed instructions, see: `/workspace/project/OpenManus/OLLAMA_SETUP.md`
