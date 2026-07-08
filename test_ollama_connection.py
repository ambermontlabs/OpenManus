#!/usr/bin/env python
"""Test script to diagnose Ollama connection issues"""

import requests
import sys

def test_ollama_connection():
    base_url = "http://localhost:11434"
    
    print("=== Ollama Connection Test ===\n")
    
    # Test 1: Basic connection
    print("Test 1: Check if Ollama server is responding")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}\n")
    except requests.exceptions.ConnectionError as e:
        print(f"CONNECTION ERROR: {e}")
        print("Ollama server is not responding. Make sure it's running.\n")
        return False
    except Exception as e:
        print(f"ERROR: {e}\n")
        return False
    
    # Test 2: List models via API
    print("Test 2: List available models (API)")
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}\n")
        
        if isinstance(data, dict) and "models" in data:
            models = data["models"]
            if isinstance(models, list) and len(models) > 0:
                print(f"✓ Found {len(models)} model(s):")
                for m in models:
                    name = m.get("name", "unknown")
                    print(f"  - {name}")
                return True
            else:
                print("✗ No models found via API")
    except Exception as e:
        print(f"ERROR: {e}\n")
    
    # Test 3: Try to generate text
    print("Test 3: Test model generation")
    test_models = ["llama3.2", "llama3", "llama3.2:latest"]
    
    for model_name in test_models:
        print(f"\nTrying model: {model_name}")
        try:
            response = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": "test",
                    "stream": False
                },
                timeout=10
            )
            print(f"Status: {response.status_code}")
            data = response.json()
            if response.status_code == 200:
                print(f"✓ Model '{model_name}' is working!")
                if "response" in data:
                    print(f"Response: {data['response']}")
                return True
            else:
                print(f"✗ Error: {data}")
        except requests.exceptions.ConnectionError:
            print("Connection refused")
            break
        except Exception as e:
            print(f"Exception: {e}")
    
    return False

if __name__ == "__main__":
    success = test_ollama_connection()
    if not success:
        print("\n" + "="*50)
        print("DIAGNOSIS:")
        print("- Ollama daemon might not be serving models")
        print("- Try restarting Ollama: ./restart_ollama.sh")
        print("- Or manually restart the Ollama app")
        print("="*50)
        sys.exit(1)
    else:
        print("\n✓ Ollama is working correctly!")
        sys.exit(0)
