# numpy-serialization Skill

**What it does**
- Detects errors when saving or loading NumPy arrays (e.g., `ValueError: setting an array element with a incompatible shape`, `TypeError: cannot serialize object type`, pickle errors).
- Identifies misuse of serialization functions (`np.save`, `np.savetxt`, `np.savez`, `pickle`, `json`).
- Suggests the most reliable format for the intended use case (local disk, network transfer, long‑term storage).

**When to provoke it**
- User posts an error while calling `np.save`, `np.load`, `np.savez`, or pickling a NumPy array.
- The error message mentions `Pickle`, `dtype`, `shape`, or `truncated`.
- When the user wants to store arrays across Python versions or platforms.

**Output of the skill**
- A table of the encountered error, its probable cause, and a suggested code change.
- Recommended serialization method:
  - `np.save` / `np.load` for binary NumPy format (`.npy`/`.npz`).
  - `np.savez_compressed` for compressed multi‑array files.
  - `json` conversion via `np.array.tolist()` for human‑readable needs.
  - `pickle` only for internal Python use, with a warning about version compatibility.
- A short code snippet demonstrating the suggested save/load pattern.
- If no error is present, the skill returns “No serialization issues detected – array handling looks correct.”

--- 
