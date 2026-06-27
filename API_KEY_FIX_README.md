# API Key Authentication Fix

## Problem Statement

The application was failing with authentication errors:
```
ERROR | app.llm:ask_tool:786 - OpenAI API error: Error code: 401 - {'error': {'code': 'authentication_error', 'message': 'Invalid Anthropic API Key', 'type': 'invalid_request_error', 'param': None}}
```

## Root Causes

1. **Pydantic V2 Compatibility**: The code used Pydantic V1 syntax (`class Config:`) causing warnings
2. **Missing Configuration**: No `config.toml` file existed, only example files with placeholder values
3. **No Environment Variable Support**: API keys could only be set in config files

## Solution Implemented

### 1. Pydantic V2 Compatibility Fix
Changed from Pydantic V1 to V2 syntax:
```python
# Before (V1)
class Config:
    arbitrary_types_allowed = True

# After (V2)
model_config = {"arbitrary_types_allowed": True}
```

### 2. Environment Variable Support
Added automatic support for environment variables:
- `ANTHROPIC_API_KEY` - For Anthropic models (Claude)
- `OPENAI_API_KEY` - For OpenAI-compatible APIs

**Priority Order:**
1. Environment variables (checked first)
2. config.toml file
3. config.example.toml (fallback)

### 3. Placeholder Detection
Added validation to detect common placeholder values and warn users:
- "YOUR_API_KEY"
- "your_api_key"
- "api_key_here"
- "YOUR_OPENAI_API_KEY"

### 4. Improved Documentation
Updated example configs with clear instructions on using environment variables.

## Usage

### Option 1: Environment Variable (Recommended)
```bash
export ANTHROPIC_API_KEY=sk-<your-key-here>
python main.py --prompt "clear"
```

### Option 2: Config File
```bash
cp config/config.example.toml config/config.toml
# Edit config.toml and replace "YOUR_API_KEY" with your actual key
python main.py --prompt "clear"
```

## Files Changed

1. **app/config.py** - Added env var support, Pydantic V2 fixes, and validation
2. **config/config.example.toml** - Added documentation about env vars

## Testing

Run the test script:
```bash
python3 test_config_fix.py
```

## Verification

Check for the following before and after:

**Before:**
- Pydantic V2 warning about underscore_attrs_are_private
- "Invalid Anthropic API Key" error
- No helpful guidance for setting API keys

**After:**
- ✓ No Pydantic warnings
- ✓ Clear error messages about placeholder API keys
- ✓ Support for ANTHROPIC_API_KEY and OPENAI_API_KEY environment variables
- ✓ Helpful warnings when using placeholder values

## Benefits

1. **Security**: Encourages using environment variables (best practice)
2. **Flexibility**: Multiple options for configuring API keys
3. **User-Friendly**: Clear error messages and warnings
4. **Compatible**: Works with Pydantic V2 without breaking changes
5. **Well-Documented**: Clear instructions for users

## Example Workflow

### For Anthropic (Claude) Users:
```bash
export ANTHROPIC_API_KEY=sk-ant-api01-...
python main.py --prompt "write a haiku"
```

### For OpenAI Users:
```bash
export OPENAI_API_KEY=sk-proj-...
python main.py --prompt "write a haiku"
```

### For Local LLMs (Ollama, LM Studio):
```bash
# Set up config.toml with local endpoint
python main.py --prompt "write a haiku"
```

## Troubleshooting

If you still get authentication errors:

1. Check if environment variable is set:
   ```bash
   echo $ANTHROPIC_API_KEY  # or $OPENAI_API_KEY
   ```

2. Verify API key is valid (not a placeholder like "YOUR_API_KEY")

3. Check your API plan/subscription is active

4. Ensure the API key has not expired or been revoked
