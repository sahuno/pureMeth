# pureMeth

A Python utilities package for Oxford Nanopore DNA methylation data analysis.

## Features

- Recursive directory search for sample files
- YAML configuration file generation
- Oxford Nanopore data processing utilities

## Installation

### For Colleagues/Collaborators

**Option 1: Install from GitHub (Recommended)**
```bash
pip install git+https://github.com/yourusername/pureMeth.git
```

**Option 2: Install from local wheel file**
```bash
# Download the .whl file shared by the developer
pip install pureMeth-0.1.0-py3-none-any.whl
```

**Option 3: Install from source**
```bash
# Clone or download the repository
git clone https://github.com/yourusername/pureMeth.git
cd pureMeth
pip install -e .
```

### For Developers
```bash
# Development installation
git clone https://github.com/yourusername/pureMeth.git
cd pureMeth
pip install -e ".[dev]"
```

## Usage

```python
from pureMeth.utils import generate_samples_yaml

# Generate samples YAML file from directory
generate_samples_yaml(
    directory="/path/to/data", 
    file_extension=".fast5",
    output_filename="my_samples"
)
```