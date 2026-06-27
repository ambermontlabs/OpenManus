# Config Fix Summary

## Issues Fixed

### 1. Pydantic V2 Compatibility Warning
**Issue:** The config was using Pydantic V1 syntax (`class Config:`) which caused warnings in Pydantic V2:
```
Valid config keys have changed in V2:
* 'underscore_attrs_are_private' has been removed
```

**Fix:** Updated to Pydantic V2 syntax:
```python
# Old (Pydantic V1)
class Config:
    arbitrary_types_allowed = True

# New (Pydantic V2)
model_config = {"arbitrary_types_allowed": True}
```

### 2. Invalid API Key Error
**Issue:** Users were getting "Invalid Anthropic API Key" errors because:
- No `config.toml` file existed (only example files)
- Example configs had placeholder values ("YOUR_API_KEY")
- No way to use environment variables for API keys

**Fix:** Added multiple improvements:

1. **Environment Variable Support**: The config now checks environment variables before reading from `config.toml`:
   - `ANTHROPIC_API_KEY` for Anthropic models
   - `OPENAI_API_KEY` for OpenAI-compatible APIs

2. **Priority Order**:
   1. Environment variable (ANTHROPIC_API_KEY or OPENAI_API_KEY)
   2. config.toml file
   3. config.example.toml (fallback)

3. **Placeholder Detection**: Added validation to detect placeholder API keys and warn users:
   - Detects values like "YOUR_API_KEY", "your_api_key", etc.
   - Provides helpful warning message suggesting env vars or updating config.toml

4. **Improved Documentation**: Updated example configs with clear instructions on using environment variables.

## How to Use

### Option 1: Using Environment Variables (Recommended)
Set your API key as an environment variable:

```bash
# For Anthropic models
export ANTHROPIC_API_KEY=sk-...

# For OpenAI-compatible APIs
export OPENAI_API_KEY=sk-...
```

Then run the application:
```bash
python main.py --prompt "your prompt"
```

### Option 2: Using config.toml
1. Copy the example config:
   ```bash
   cp config/config.example.toml config/config.toml
   ```

2. Update the API key in `config/config.toml`:
   ```toml
   [llm]
   model = "claude-3-7-sonnet-20250219"
   base_url = "https://api.anthropic.com/v1/"
   api_key = "sk-..."  # Replace with your actual key
   ```

## Files Modified

1. **app/config.py**
   - Added `_get_api_key_from_env()` function for env var support
   - Updated `LLMSettings` with Pydantic V2 validation decorator
   - Updated `AppConfig` class to use `model_config`
   - Modified `_load_initial_config()` to check env vars
   - Added `model_validator` import

2. **config/config.example.toml**
   - Added comments explaining environment variable usage
   - Updated api_key comment to mention env vars

## Testing

Run the test script to verify the changes:
```bash
python3 test_config_fix.py
```

The tests verify:
- Pydantic V2 syntax works correctly
- Placeholder values are detected with warnings
- Environment variables take priority over config files

## Benefits

1. **No Breaking Changes**: Existing configs continue to work
2. **More Flexible**: Users can now use env vars, which is a best practice
3. **Better UX**: Clear warnings help users fix issues quickly
4. **Security**: Encourages using env vars instead of storing keys in files
5. **Compatibility**: Fully compatible with Pydantic V2
