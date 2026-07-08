"""
Script to suppress dependency warnings before importing any other modules.
Run this first, then import the rest of your code.
"""
import warnings

# Suppress pydantic V2 config warning for underscore_attrs_are_private
warnings.filterwarnings(
    "ignore",
    message="Valid config keys have changed in V2:",
    category=UserWarning,
)

# Suppress requests dependency warning about urllib3/chardet compatibility
warnings.filterwarnings(
    "ignore",
    message="urllib3.*chardet.*charset_normalizer.*doesn't match a supported version",
    category=UserWarning,
)

# Also suppress the specific warnings if they've already been triggered
warnings.filterwarnings(
    "ignore",
    message="urllib3.*chardet",
    category=UserWarning,
)

# Suppress the Python version warning from app/__init__.py
warnings.filterwarnings(
    "ignore",
    message="Unsupported Python version.*please use 3.11-3.13",
    category=UserWarning,
)
