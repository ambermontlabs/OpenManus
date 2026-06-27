# Conda Environment Setup

This document describes how to set up the OpenManus project using conda.

## Prerequisites

- Conda or Miniconda installed on your system
- Python 3.12 recommended

## Installation Steps

### 1. Create the Conda Environment

You can create the environment from the `environment.yml` file:

```bash
# Using the provided environment.yml file
conda env create -f environment.yml

# Or if you want to specify a custom name
conda env create -f environment.yml -n openmanus
```

### 2. Activate the Environment

```bash
conda activate openmanus
```

### 3. Verify Installation

Check that all dependencies are installed:

```bash
python --version
pip list | grep -E "(openai|pydantic|fastapi|playwright)"
```

## Using with LM Studio

The `environment.yml` file includes all dependencies needed for LM Studio integration:

- `docker` - For containerized sandbox environment
- `openai` - OpenAI-compatible API client
- `pydantic` - Data validation and settings management

## Configuration

1. Copy the example config:
```bash
cp config/config.example-lmstudio.toml config/config.toml
```

2. Edit `config/config.toml` with your LM Studio settings

3. Run OpenManus:
```bash
python main.py
```

## Environment Overview

The `environment.yml` includes:

- **Core packages**: Python 3.12, pip, requests, setuptools
- **Data processing**: numpy, pandas, datasets
- **Web frameworks**: fastapi, uvicorn, httpx
- **ML/AI packages**: pydantic, openai
- **HTTP clients and tools**: beautifulsoup4, html2text
- **Utility libraries**: loguru, pyyaml, colorama
- **Testing**: pytest, pytest-asyncio
- **Development tools**: All packages from requirements.txt

## Troubleshooting

### Import Errors

If you encounter import errors, ensure all packages are installed:

```bash
pip install -r requirements.txt
```

### Docker Issues

If using Docker sandbox, ensure Docker is running:

```bash
# On Linux
sudo dockerd > /tmp/docker.log 2>&1 &

# Wait for Docker to initialize
sleep 5
```

### Version Conflicts

If you encounter version conflicts, try:

```bash
# Remove existing environment
conda env remove -n openmanus

# Recreate from environment.yml
conda env create -f environment.yml
```

## Additional Resources

- [Conda Documentation](https://docs.conda.io/)
- [OpenManus GitHub Repository](https://github.com/FoundationAgents/OpenManus)
