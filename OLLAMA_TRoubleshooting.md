# Ollama "Models Not Found" Troubleshooting

## Problem
- `ollama list` shows models are installed
- API endpoint returns `{"models":[]}` (empty)
- This means the Ollama daemon isn't serving models

## Root Cause
The Ollama server daemon and the `ollama` command-line client are separate. 
When you run `ollama pull`, it might connect to a different daemon instance or the daemon isn't running.

## Solution

### Step 1: Check Ollama Daemon Status
```bash
# Check if Ollama process is running
ps aux | grep ollama

# On macOS, check if the app is running
ps aux | grep -i ollama.app
```

### Step 2: Restart Ollama Daemon

**On macOS (GUI App):**
1. Quit the Ollama app completely
2. Restart it from Applications

**On macOS (Terminal):**
```bash
# Kill all ollama processes
pkill -f ollama

# Restart (on macOS)
open -a Ollama
```

**On Linux:**
```bash
# If installed via systemctl
sudo systemctl restart ollama

# Or restart the daemon directly
ollama serve &
```

**On Docker:**
```bash
# Restart container
docker restart ollama

# Or recreate it with fresh data
docker stop ollama && docker rm ollama
docker run -d -p 11434:11434 --name ollama -v ollama:/root/.ollama ollama/ollama
```

### Step 3: Verify Models via API

```bash
# Check models through the API
curl http://localhost:11434/api/tags

# Expected: {"models":[{"name":"llama3:latest"},{"name":"llama3.2:latest"}]}
```

### Step 4: If Still Empty, Re-pull Models

```bash
# Pull model again (this should connect to the daemon)
ollama pull llama3.2

# Verify it's serving now
curl http://localhost:11434/api/tags
```

### Step 5: Check Ollama Log Files

**On macOS (GUI app):**
- Logs are in `~/Library/Logs/Ollama/`
```bash
tail -f ~/Library/Logs/Ollama/*.log
```

**On Docker:**
```bash
docker logs ollama -f
```

## Common Issues

### Issue: Multiple Ollama Processes
```bash
# Kill all and restart cleanly
pkill -9 ollama
ps aux | grep ollama  # Should show nothing

# Then start Ollama fresh
open -a Ollama
```

### Issue: Model Pull Succeeds but API Empty
This suggests multiple daemon instances. Check ports:
```bash
lsof -i :11434  # Should show only ONE process
```

If multiple processes, kill all and restart:
```bash
lsof -t -i :11434 | xargs kill -9
```

### Issue: Model Data Path Mismatch
The daemon might be looking for models in a different directory.

**On macOS (Docker):**
```bash
# Ensure you're using the same volume
docker run -d -p 11434:11434 \
  -v ollama:/root/.ollama \
  --name ollama ollama/ollama
```

**On macOS (GUI App):**
The app uses `~/.ollama/models/` by default. Check:
```bash
ls -la ~/.ollama/models/
```

### Step 6: Use Docker (Most Reliable on macOS)

If the GUI app continues to fail, use Docker:

```bash
# Stop and remove existing Ollama
docker stop ollama 2>/dev/null || true
docker rm ollama 2>/dev/null || true

# Pull latest image
docker pull ollama/ollama:latest

# Create fresh volume and start
docker run -d \
  -p 11434:11434 \
  --name ollama \
  -v ollama:/root/.ollama \
  ollama/ollama

# Wait for it to start
sleep 5

# Pull model
docker exec ollama ollama pull llama3.2

# Verify API is working
curl http://localhost:11434/api/tags
```

## Test Ollama API

```bash
# Test 1: List models
curl http://localhost:11434/api/tags

# Test 2: Generate text
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "test"
}'

# Test 3: Show model info
curl http://localhost:11434/api/show -d '{"name": "llama3.2"}'
```

## If All Else Fails

Switch to a different local LLM server:

### Using LM Studio
1. Download: https://lmstudio.ai/
2. Start local server on port 1234
3. Update config:
```toml
api_type = 'lmstudio'
base_url = "http://localhost:1234/v1"
```

### Using Local Llama with Ollama-compatible API
- Use vLLM or text-generation-webui
- Both have Ollama-compatible endpoints
