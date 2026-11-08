---
name: numpy-serialization
description: "Diagnoses NumPy np.save/np.load/np.savez serialization failures (truncated files, allow_pickle errors, dtype/endianness mismatches, .npz key errors) and recommends the correct .npy/.npz pattern. Use when NumPy save/load raises an error."
---

# numpy-serialization Skill

## What it does
- Detects `np.save`/`np.load`/`np.savez` errors: truncated or corrupt files, `allow_pickle` failures, dtype/endianness mismatches, and `.npz` key errors
- Shape errors during array assignment occur before serialization and are out of scope

## When to provoke it
- User calls `np.save`, `np.load`, or `np.savez` and encounters an error
- Error message mentions `truncated`, `allow_pickle`, `pickle`, dtype/endianness, or `.npz` keys

## Inputs
- `Error`: error message
- `Code`: relevant code snippet
- `Context`: storage scenario (disk/transfer/storage)

## Workflow
1. Extract the exact error message and the NumPy call that raised it.
2. If no error is present (prevention), inspect `print(array.dtype, array.shape)` so the serialized array has the expected dtype and shape.
3. Match the error to a cause using the table below.
4. Recommend the matching fix and verify the filename passed to `np.load` matches what `np.save` wrote.
5. Provide a minimal save/load snippet for the chosen format.

## Error/Cause/Fix Table

| Error / symptom | Likely cause | Fix |
|---|---|---|
| `FileNotFoundError` on load | Wrong filename (e.g. double `.npy`) or wrong directory; `np.save("array", ...)` appends `.npy` automatically | Pass the exact path written by `np.save` (e.g. `np.save("array")` writes `array.npy`). |
| `ValueError: setting an array element with an incompatible shape` | Shape mismatch during array assignment, not a save/load error — occurs before serialization | Fix the array construction/assignment shapes, then save the corrected array. |
| `ValueError: Object arrays cannot be loaded when allow_pickle=False` | Object dtype array saved, but loading with `allow_pickle=False` | Store primitive dtypes, or explicitly pass `allow_pickle=True` only for trusted files. |
| `ValueError: Cannot load file containing pickled data when allow_pickle=False` | File was saved as a pickle/object array but loaded with `allow_pickle=False` | Load with `allow_pickle=True` only for trusted files, or re-save as a primitive dtype. |
| `OSError: Failed to interpret file ... as a pickle` | File is corrupt, truncated, or not a valid `.npy`/`.npz` file | Re-save or re-transfer the file; verify it is a NumPy file and not a different format. |
| `EOFError` / truncated or corrupt file | Incomplete download/write | Re-save the array; verify file size and checksum after transfer. |
| `KeyError` on `.npz` load | Requested key missing from archive | Inspect `data.files` and use a key that exists. |
| dtype/endianness mismatch | Array saved on a different platform or with a different dtype | Cast explicitly (`array.astype(np.float32)`) before saving or after loading. |

## Security
- `allow_pickle=True` can execute arbitrary code from untrusted files. Default to `allow_pickle=False` and only enable it for files you trust.

## Output
- **table**: error → cause → code change; see the Error/Cause/Fix Table for the canonical mapping, e.g. `FileNotFoundError` on load → wrong filename (e.g. double `.npy`) → pass the exact path written by `np.save`.
- **method**: `np.save` for `.npy`; `np.savez` for `.npz`; `np.load` for both
- **snippet**: save/load pattern demonstration

## Example
```python
import numpy as np

array = np.array([1, 2, 3, 4, 5])
np.save("array.npy", array)
loaded = np.load("array.npy")
```

## Example (.npz)
```python
import numpy as np

array = np.array([1, 2, 3, 4, 5])
np.savez("arrays.npz", a=array, b=array * 2)
with np.load("arrays.npz", allow_pickle=False) as data:
    a = data["a"]
    b = data["b"]
```

## Failure Handling
- Missing file: verify the path and that `np.save` ran successfully.
- Corrupt/truncated file: re-save or re-transfer the array; do not attempt to repair partial data.
- Permission denied on save: check directory permissions and write to a writable location.
- Permission denied on load: check read permissions and that the path is accessible to the running user.
- Never silently fall back to `allow_pickle=True`; report the risk and require explicit user confirmation.
