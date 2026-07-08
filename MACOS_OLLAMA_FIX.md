# macOS Ollama Setup Guide

## Issue: "model not found" error

Even though `ollama list` shows models, the API might not be running.

## Step 1: Start Ollama Server

On macOS, Ollama is a GUI app. Make sure it's running:

```bash
# Check if Ollama is running
ps aux | grep -i ollama

# If not, start it from the Applications folder or:
open -a Ollama
```

## Step 2: Verify API Endpoint

```bash
# Test the API directly (should return model list or error)
curl http://localhost:11434/api/tags
```

Expected response:
```json
{"models":[{"name":"llama3:latest"},{"name":"llama3.2:latest"}]}
```

## Step 3: Use Correct Model Name

Ollama might use the full model name with tag. Update `config/config.toml`:

```toml
[llm]
api_type = 'ollama'
model = "llama3.2:latest"  # Use full name with tag
base_url = "http://localhost:11434/v1"
api_key = "ollama"

[llm.vision]
model = "llama3.2-vision:latest"  # Use full name with tag
```

## Step 4: Pull Models via API

If `ollama pull` doesn't work, try the API:

```bash
# Check what models are available via API
curl http://localhost:11434/api/pull -d '{"name": "llama3.2"}'

# Check if models exist
curl http://localhost:11434/api/tags
```

## Step 5: Restart Ollama

If still getting errors:

```bash
# Kill and restart Ollama
pkill -f ollama
open -a Ollama

# Or use the app menu: Ollama > Restart
```

## Step 6: Verify with Python

```bash
python -c "
import requests
response = requests.get('http://localhost:11434/api/tags')
print(response.json())
"
```

## Common Issues

### Issue: "connection refused"
**Solution**: Ollama server isn't running. Start the app.

### Issue: "model not found"
**Solution**: Model exists but Ollama daemon isn't serving it. Restart the app.

### Issue: "404 Not Found"
**Solution**: Check if models exist with `ollama list` and verify API is responding.

## Alternative: Use Docker for Ollama (macOS)

If the app continues to have issues:

```bash
# Stop and remove existing container
docker stop ollama
docker rm ollama

# Pull latest image
docker pull ollama/ollama:latest

# Run Ollama
docker run -d -p 11434:11434 --name ollama -v ollama:/root/.ollama ollama/ollama

# Pull models
docker exec -it ollama ollama pull llama3.2
```
