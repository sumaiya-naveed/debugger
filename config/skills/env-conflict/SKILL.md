# env-conflict Skill

**What it does**
- Detects environment‑related problems such as missing packages, version mismatches, and conflicting dependencies.
- Scans the current Python environment (via `pip list`, `conda list`) and compares it against the imports used in the user's code.
- Reports the exact package/version that is missing or incompatible.

**When to provoke it**
- User posts an error that includes `ModuleNotFoundError`, `ImportError`, or messages about version incompatibility.
- The error message mentions “requirement” or “conflicting”.
- Before running code in a new environment (CI/CD, fresh VM, container).

**Output of the skill**
- A markdown table listing each problematic package, the required version, the installed version, and a suggested fix (`pip install <pkg>==<version>` or `pip install --upgrade <pkg>`).
- Optional: a short shell snippet to reinstall the environment from a `requirements.txt`.
- If no conflicts are found, the skill returns “No environment conflicts detected.”

--- 
