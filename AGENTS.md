# Skill Usage Harness

This file defines the **rules and protocols** for invoking the skills defined in `config/skills/`. It provides a harness for the AI to correctly use these skills by specifying input formats, output expectations, and invocation patterns.

## Skill Invocation Rules

### 1. numpy-serialization Skill
**Invocation Trigger:** When user mentions NumPy save/load errors or wants to store arrays.

**Required Input Format:**
```
Error: <error message>
Code: <relevant code snippet>
Context: <storage scenario (disk/transfer/storage)>
```

**AI Must Follow:**
1. Extract the exact error message
2. Identify the NumPy function being used (`np.save`, `np.load`, `np.savez`, `pickle`)
3. Provide the serialization format recommendation from the skill
4. Include the code snippet demonstrated by the skill

**Example Invocation:**
```
Skill: numpy-serialization
Error: "ValueError: setting an array element with a incompatible shape"
Code: np.save("data.npy", array)
Context: Saving for long-term storage across Python versions
```

**Expected Output Format:**
- Table: [error, cause, suggested code change]
- Recommended method: `np.save`/`np.load` for `.npy`/`.npz`
- Code snippet demonstrating save/load pattern

---

### 2. env-conflict Skill
**Invocation Trigger:** When user mentions import errors, missing packages, or version conflicts.

**Required Input Format:**
```
Error: <error message (ModuleNotFoundError, ImportError, etc.)>
Imports: <list of imports used>
Environment: <pip/conda, OS details if relevant>
```

**AI Must Follow:**
1. Parse the error type (ModuleNotFoundError vs ImportError vs version mismatch)
2. List the problematic package(s)
3. Provide the exact pip install command from the skill
4. Include the version comparison if available

**Example Invocation:**
```
Skill: env-conflict
Error: "ModuleNotFoundError: no module named 'numpy'"
Imports: ["import numpy as np"]
Environment: fresh VM, pip environment
```

**Expected Output Format:**
- Markdown table: [package, required version, installed version, fix suggestion]
- Or: "No environment conflicts detected."

---

### 3. deploy-troubleshoot Skill
**Invocation Trigger:** When user shares deployment logs, stack traces, or CI/CD output.

**Required Input Format:**
```
Log: <deployment error output/stack trace>
Platform: <Kubernetes/Docker/CI/CD name>
RecentChanges: <new dependencies/config changes>
```

**AI Must Follow:**
1. Identify error patterns (`Error:`, `Exit code`, `CrashLoopBackOff`, timeouts)
2. List max 5 root causes with brief explanations
3. Provide fix commands/snippets from the skill
4. Include the "next-steps" checklist

**Example Invocation:**
```
Skill: deploy-troubleshoot
Log: "CrashLoopBackOff - container terminating with exit code 137"
Platform: Kubernetes
RecentChanges: added new Python dependency
```

**Expected Output Format:**
- Max 5 root causes with explanations
- Fix commands/configuration snippets
- Next-steps checklist to verify fix
- Or: "No deployment issues detected – appears healthy."

---

## Harness Workflow

1. **Identify the problem type** (serialization/env/ deployment)
2. **Provide the required input** in the specified format
3. **Invoke the appropriate skill** using the format above
4. **Apply the skill's output** to fix the issue
5. **Verify the fix** using the provided checklist/examples

## Priority Order

If multiple skills could apply, use this priority:
1. **env-conflict** - If imports are failing, fix environment first
2. **numpy-serialization** - If data persistence is the issue
3. **deploy-troubleshoot** - If deployment/container is the issue

## Notes

- Do not modify the skill files `config/skills/*/SKILL.md` directly - use this harness
- Each skill maintains Single Responsibility Principle - invoke only the relevant skill
- The harness ensures consistent AI behavior across different debugging scenarios