#!/usr/bin/env python
"""Test script to verify config loading"""

import sys
print(f"Python path: {sys.executable}")
print(f"Python version: {sys.version}")

# Import and check config
from app.config import config, PROJECT_ROOT

print(f"\nProject root: {PROJECT_ROOT}")
print(f"Config file path: {PROJECT_ROOT / 'config' / 'config.toml'}")

# Check which config file is being used
import os
config_path = PROJECT_ROOT / "config" / "config.toml"
print(f"\nConfig file exists: {os.path.exists(config_path)}")

if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        content = f.read()
        print("\n=== CONFIG FILE CONTENT ===")
        print(content)
        print("=== END CONFIG FILE ===")

print(f"\nActive configuration:")
for key, value in config.llm.items():
    print(f"  {key}:")
    print(f"    api_type: {value.api_type}")
    print(f"    model: {value.model}")
    print(f"    base_url: {value.base_url}")
    print(f"    api_key: {'*' * len(value.api_key) if value.api_key else '(empty)'}")
