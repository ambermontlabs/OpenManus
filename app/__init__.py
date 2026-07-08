# Python version check: 3.11-3.13
import sys
import warnings

# Suppress pydantic V2 config warning for underscore_attrs_are_private
warnings.filterwarnings(
    "ignore",
    message="Valid config keys have changed in V2:",
    category=UserWarning,
)

# Suppress requests dependency warning
warnings.filterwarnings(
    "ignore",
    message="urllib3.*chardet.*charset_normalizer.*doesn't match a supported version",
    category=UserWarning,
)

if sys.version_info < (3, 11) or sys.version_info > (3, 13):
    print(
        "Warning: Unsupported Python version {ver}, please use 3.11-3.13".format(
            ver=".".join(map(str, sys.version_info))
        )
    )
