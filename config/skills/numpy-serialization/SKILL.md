---
name: "numpy-serialization"
description: "Detects and resolves NumPy serialization errors, identifying the root cause and suggesting the appropriate save/load pattern for the use case."
role: "numpy-serialization"
capabilities: ["error-detection", "format-suggestion", "code-snippet-generation"]
priority: "medium"
---

# numpy-serialization Skill

## What it does

- Detects errors when saving or loading NumPy arrays, including `ValueError: setting an array element with a incompatible shape`, `TypeError: cannot serialize object type`, and pickle errors
- Identifies misuse of serialization functions (`np.save`, `np.load`, `np.savez`, `pickle`, `json`)
- Determines the most reliable format for the intended use case (local disk, network transfer, long-term storage)

## When to provoke it

- User posts an error while calling `np.save`, `np.load`, `np.savez`, or pickling a NumPy array
- The error message mentions `Pickle`, `dtype`, `shape`, or `truncated`
- When the user wants to store arrays across Python versions or platforms

## Output of the skill

- A table of the encountered error, its probable cause, and a suggested code change
- Recommended serialization method:
  - `np.save` / `np.load` for binary NumPy format (`.npy`/`.npz`)
  - `np.savez_compressed` for compressed multi-array files
  - `json` conversion via `np.array.tolist()` for human-readable needs
  - `pickle` only for internal Python use, with a warning about version compatibility
- A short code snippet demonstrating the suggested save/load pattern
- If no error is present, the skill returns "No serialization issues detected – array handling looks correct."

## Example

```python
import numpy as np

# Correct pattern for binary NumPy format
array = np.array([1, 2, 3, 4, 5])
np.save("array.npy", array)
loaded = np.load("array.npy.npy")
```