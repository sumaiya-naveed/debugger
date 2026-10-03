---
name: "numpy-serialization"
description: "Detects NumPy save/load errors and suggests the binary format fix pattern."
role: "numpy-serialization"
capabilities: ["np-save-load-detection"]
priority: "medium"
---

# numpy-serialization Skill

## What it does
- Detects `np.save`/`np.load`/`np.savez` errors including shape/dtype mismatches

## When to provoke it
- User calls `np.save`, `np.load`, or `np.savez` and encounters an error
- Error message mentions `dtype`, `shape`, or `truncated`

## Output
- **table**: error → cause → code change
- **method**: `np.save` / `np.load` for `.npy`/`.npz`
- **snippet**: save/load pattern demonstration

## Example
```python
import numpy as np
array = np.array([1, 2, 3, 4, 5])
np.save("array.npy", array)
loaded = np.load("array.npy.npy")
```