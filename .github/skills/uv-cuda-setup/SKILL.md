---
name: uv-cuda-setup
description: |
  Configures Python projects with uv package manager to use CUDA-enabled PyTorch.
  Handles the common issue where uv installs CPU-only torch by default.
  Use when setting up GPU-accelerated machine learning projects, fixing CUDA not available errors,
  or configuring PyTorch with GPU support in uv-managed projects.
compatibility: Requires NVIDIA GPU, CUDA toolkit, uv package manager
metadata:
  author: video2doc
  version: "1.0"
---

# UV CUDA Setup

Configure uv-managed Python projects to use CUDA-enabled PyTorch instead of CPU-only version.

## When to Use

- User reports `CUDA available: False` in PyTorch
- Setting up new ML/AI project with GPU requirements
- Migrating pip-based project to uv with CUDA dependencies
- User asks about GPU acceleration in Python projects

## Problem

By default, `uv add torch` installs the CPU-only version from PyPI. This is because:

1. PyPI hosts CPU-only torch wheels
2. CUDA wheels are on a separate PyTorch index
3. uv respects the lock file which pins CPU version

## Solution

### Step 1: Check Current State

```python
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
```

If output shows `CUDA available: False`, proceed with fix.

### Step 2: Identify CUDA Version

```powershell
# Check NVIDIA driver
nvidia-smi

# Check CUDA toolkit
echo $env:CUDA_PATH
```

Match CUDA version to PyTorch index:
- CUDA 11.8 → `cu118`
- CUDA 12.1 → `cu121`
- CUDA 12.4 → `cu124`
- CUDA 12.6 → `cu126`

### Step 3: Configure pyproject.toml

Add the following to `pyproject.toml`:

```toml
[project]
dependencies = [
    "torch>=2.0",
    # other dependencies...
]

# Define PyTorch CUDA index
[[tool.uv.index]]
name = "pytorch-cu126"  # adjust version as needed
url = "https://download.pytorch.org/whl/cu126"
explicit = true

# Source torch from CUDA index
[tool.uv.sources]
torch = { index = "pytorch-cu126" }
```

### Step 4: Reinstall Dependencies

```powershell
# Delete existing lock file
Remove-Item uv.lock -Force

# Sync dependencies (will fetch CUDA torch)
uv sync
```

### Step 5: Verify

```powershell
uv run python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

Expected output: `CUDA: True`

## Common Issues

### Lock File Conflict

If `uv run` reinstalls CPU version:
- The lock file takes precedence
- Always delete `uv.lock` after changing indexes

### Wrong CUDA Version

If PyTorch fails to load:
- Check CUDA toolkit version matches index
- Use `nvidia-smi` to see driver CUDA version

### Multiple GPU Indexes

For projects needing specific torch+torchvision+torchaudio:

```toml
[tool.uv.sources]
torch = { index = "pytorch-cu126" }
torchvision = { index = "pytorch-cu126" }
torchaudio = { index = "pytorch-cu126" }
```

## Quick Reference

| CUDA Version | Index URL |
|--------------|-----------|
| 11.8 | `https://download.pytorch.org/whl/cu118` |
| 12.1 | `https://download.pytorch.org/whl/cu121` |
| 12.4 | `https://download.pytorch.org/whl/cu124` |
| 12.6 | `https://download.pytorch.org/whl/cu126` |
