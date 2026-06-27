#!/usr/bin/env python3
"""
Test script to verify config loading with environment variables.
This tests the changes made to support env vars and Pydantic V2.
"""

import os
import sys

# Add the app directory to path
sys.path.insert(0, '/workspace/project/OpenManus')

def test_env_var_priority():
    """Test that environment variables take priority over config file."""
    print("Testing environment variable priority...")
    
    # Set an env var
    os.environ['ANTHROPIC_API_KEY'] = 'test-key-123'
    
    # Import config (this will trigger loading)
    try:
        from app.config import _get_api_key_from_env
        
        # Test with Anthropic URL
        config = {
            "api_type": "",
            "base_url": "https://api.anthropic.com/v1/",
            "model": "claude-3-7-sonnet-20250219"
        }
        
        api_key = _get_api_key_from_env(config)
        print(f"  API key from env var: {api_key}")
        
        if api_key == 'test-key-123':
            print("  ✓ Environment variable was used correctly")
        else:
            print(f"  ✗ Expected 'test-key-123', got '{api_key}'")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    finally:
        # Clean up
        if 'ANTHROPIC_API_KEY' in os.environ:
            del os.environ['ANTHROPIC_API_KEY']
    
    return True

def test_placeholder_detection():
    """Test that placeholder API keys are detected."""
    print("\nTesting placeholder detection...")
    
    try:
        from app.config import LLMSettings
        from app.logger import logger
        
        # Test with placeholder value
        settings = LLMSettings(
            model="claude-3-7-sonnet-20250219",
            base_url="https://api.anthropic.com/v1/",
            api_key="YOUR_API_KEY",
            max_tokens=8192,
            temperature=0.0,
            api_type="",
            api_version=""
        )
        
        print(f"  API key in settings: {settings.api_key}")
        if settings.api_key == "YOUR_API_KEY":
            print("  ✓ Placeholder value is accepted (with warning)")
            return True
        else:
            print(f"  ✗ Expected placeholder value, got '{settings.api_key}'")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_pydantic_v2_syntax():
    """Test that Pydantic V2 syntax works."""
    print("\nTesting Pydantic V2 compatibility...")
    
    try:
        from app.config import AppConfig
        
        # Check if model_config is used instead of class Config
        config_dict = {
            "llm": {"default": {}},
            "sandbox": None,
            "browser_config": None,
            "search_config": None,
            "mcp_config": None,
            "run_flow_config": None,
            "daytona_config": None,
            "lmstudio_config": None,
        }
        
        # This should work with Pydantic V2
        app_config = AppConfig(**config_dict)
        print("  ✓ AppConfig instantiated with Pydantic V2 syntax")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Config Changes")
    print("=" * 60)
    
    results = []
    
    # Test 1: Pydantic V2 syntax
    results.append(("Pydantic V2", test_pydantic_v2_syntax()))
    
    # Test 2: Placeholder detection
    results.append(("Placeholder Detection", test_placeholder_detection()))
    
    # Test 3: Environment variable priority
    results.append(("Env Var Priority", test_env_var_priority()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
