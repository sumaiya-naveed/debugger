---
name: env-conflict
description: "Detects missing Python packages and version mismatches (ModuleNotFoundError, ImportError, pip/conda conflicts) and reports the exact fix. Use when imports fail or before running code in a fresh VM, CI, or container."
---

# env-conflict Skill

## What it does
- Detects missing packages and version mismatches in Python environment
- Reports exact package/version that is missing or incompatible

## When to provoke it
- User posts `ModuleNotFoundError` or `ImportError`
- Before running code in new environment (CI/CD, fresh VM, container)

## Inputs
- `Error`: error message (ModuleNotFoundError, ImportError, etc.)
- `Imports`: list of imports used
- `Environment`: pip/conda, OS details if relevant

## Workflow
1. Confirm the interpreter: `which python`, `python -V`, `python -m pip -V`.
2. Reproduce the import and capture the exact exception, including the full traceback.
3. Check the installed version: `python -m pip show <pkg>` or `conda list <pkg>`.
4. Read the declared requirement from requirements.txt, pyproject.toml, or environment.yml.
5. Detect transitive dependency conflicts: `python -m pip check` (and `pipdeptree` if installed), or `conda env update --dry-run` for conda environments.
6. If imports fail despite the package being installed, check for multiple interpreters/venvs and path shadowing using `python -c "import sys; print(sys.executable)"` and `python -m pip -V`; also check the traceback for missing system libraries (e.g. `libGL`, `libstdc++`) and for conflicting manifests.
7. Report missing/mismatched/conflicting packages and the minimal install/upgrade command.
8. If no manifest exists, say so and avoid inventing a required version.

## Safety
- Prefer a virtual environment. Confirm with the user before installing or upgrading packages, since `pip install` modifies the active environment.

## Output
- **table**: package, required version, installed version, status (missing | mismatched | conflict), fix suggestion
- **required_version_source**: the manifest/lockfile the required version came from; if none exists, say so explicitly
- **fallback**: "No environment conflicts detected."

## Failure Handling
- If `pip`/`conda` is unavailable, report the interpreter state and ask which package manager the environment uses.
- If an install or upgrade is denied by permissions, report the error and recommend a user-writable virtual environment.
- If multiple manifests declare conflicting requirements, list each manifest and its constraint and ask which one is authoritative.

## Example
```bash
# Detect the interpreter and the installed package version
which python
python -V
python -m pip -V
python -m pip show numpy

# Detect transitive dependency conflicts
python -m pip check

# Read the declared requirement before changing anything
# requirements.txt: numpy==1.24.0
python -m pip install "numpy==1.24.0"   # only after confirming the declared requirement
```

Sample output table:

| package | required | installed | status | fix |
|---|---|---|---|---|
| numpy | 1.24.0 | 1.26.4 | mismatched | `python -m pip install "numpy==1.24.0"` |
| torch | 2.1.0 | 2.2.1 | conflict | `pip check` reports `torchvision` needs `torch<2.2`; `python -m pip install "torch==2.1.0"` |
