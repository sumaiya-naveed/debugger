---
name: "env-conflict"
description: "Scans Python environment for missing packages and reports version mismatches."
role: "env-conflict"
capabilities: ["env-scanning"]
priority: "medium"
---

# env-conflict Skill

## What it does
- Detects missing packages and version mismatches in Python environment
- Reports exact package/version that is missing or incompatible

## When to provoke it
- User posts `ModuleNotFoundError` or `ImportError`
- Before running code in new environment (CI/CD, fresh VM, container)

## Output
- **table**: package, required version, installed version, fix suggestion
- **fallback**: "No environment conflicts detected."

## Example
```bash
pip list --outdated
pip install --upgrade numpy==1.24.0
```