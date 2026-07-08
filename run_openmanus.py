#!/usr/bin/env python3
"""
OpenManus runner script with warnings suppressed.

This script suppresses dependency warnings that occur due to version
incompatibilities between urllib3, chardet, and charset_normalizer,
as well as Pydantic V2 configuration warnings.

Usage: python run_openmanus.py [options] --prompt "your prompt"

Or simply run: python main.py (but warnings may appear)
"""
import sys
import warnings

# Suppress all UserWarnings before any imports
warnings.filterwarnings("ignore", category=UserWarning)

# Import and run main
from main import main
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
