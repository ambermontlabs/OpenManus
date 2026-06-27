# Conda Environment Setup

## Quick Start

1. **Install Miniconda or Anaconda** (if not already installed)
   - Download from: https://docs.conda.io/en/latest/miniconda.html

2. **Create and activate the environment:**
```bash
# Create environment from environment.yml
conda env create -f environment.yml

# Activate the environment
conda activate openmanus
```

3. **Update environment (if dependencies change):**
```bash
conda env update -f environment.yml --prune
```

4. **Deactivate environment:**
```bash
conda deactivate
```

## Using pip packages in conda

Some packages are only available via pip. They're listed under the `pip:` section in `environment.yml`:

- tenacity
- tiktoken
- gymnasium
- pillow
- browser-use
- playwright
- docker
- mcp
- And more...

## Maintenance

### Adding a new dependency:

**Option 1 - Using conda:**
```bash
conda install <package-name>
conda env export > environment.yml
```

**Option 2 - Using pip:**
```bash
conda activate openmanus
pip install <package-name>
# Add to pip section in environment.yml manually
```

### Remove conda environment:
```bash
conda env remove -n openmanus
```
