# Review Log

A running log of code-review cycles. Add one entry per cycle, following the template below.

## Template

```markdown
## Cycle <number> — <YYYY-MM-DD>

- **Model used for review:** <model name>
- **Review prompt / agent:** <exact prompt text or agent name, in a code block>

### Issues found
- **Critical:** ...
- **High:** ...
- **Medium:** ...
- **Low:** ...

### Fixes applied
- <what was changed, with file paths>

### Re-review result
- <outcome: issues remaining, new issues, or clean>
```

---

## Cycle 1 — 2026-11-08

- **Model used for review:** `opencode/deepseek-v4.1-flash-free`
- **Review prompt / agent:** `agent-reviewer` subagent — "Review all files in `.opencode/agents/` and every `SKILL.md` under `.opencode/skills/`, validating against the official opencode schema (`https://opencode.ai/config.json`) and opencode conventions. Report per-file status, issues by severity, and concrete fixes."

### Issues found

# OpenCode Agent & Skill Audit — Review Only

**Scope:** `/home/talha/Desktop/debugger/.opencode/agents/` (5 files) and `/home/talha/Desktop/debugger/.opencode/skills/` (3 `SKILL.md` files; no `references/` or `scripts/` subdirectories exist).
**Schema source:** `https://opencode.ai/config.json` (fetched).
**No files were modified.**

## Summary

| File | Status | Critical | Major | Minor | Stylistic |
|---|---|---:|---:|---:|---:|
| `.opencode/agents/agent-reviewer.md` | Needs Fix | 0 | 1 | 4 | 1 |
| `.opencode/agents/data-pipeline.md` | Broken | 2 | 1 | 3 | 1 |
| `.opencode/agents/shape-dtype.md` | Broken | 1 | 2 | 3 | 1 |
| `.opencode/agents/training-instability.md` | Broken | 2 | 1 | 3 | 1 |
| `.opencode/agents/work.md` | Broken | 2 | 1 | 3 | 1 |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Needs Fix | 0 | 2 | 3 | 1 |
| `.opencode/skills/env-conflict/SKILL.md` | Needs Fix | 0 | 3 | 3 | 1 |
| `.opencode/skills/numpy-serialization/SKILL.md` | Needs Fix | 0 | 3 | 5 | 1 |
| Cross-file / directory-level (unique issues) | Needs Fix | 0 | 2 | 5 | 0 |
| **TOTAL** | | **7** | **16** | **32** | **8** |

**Status legend:** `OK` = schema-valid and complete; `Needs Fix` = loads but has significant gaps; `Broken` = intended behaviour/permissions are not enforced or the file cannot fulfil its stated purpose reliably.

**Important schema nuance:** `config.json` defines two different agent shapes. `Config.AgentEncoded` (used by the `agents` object in `opencode.json`) has a `permissions` array of `{action, resource, effect}` rules. Markdown agent frontmatter uses `AgentConfig`, which has `permission` (singular), an object/action map. The four ML agents below use the `opencode.json` ruleset shape inside markdown frontmatter; that field is unknown there and is silently ignored. Also, the top-level config property `shell` is a default-shell string, not an agent permission key; the permission key is `bash`.

---

## `.opencode/agents/agent-reviewer.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/agents/agent-reviewer.md`
**Status:** Needs Fix

**Frontmatter found:**
```yaml
description: Reviews agent and skill files for quality and correctness
mode: subagent
tools:
  write: false
  edit: false
  bash: false
```

| Severity | Issue | Suggested fix |
|---|---|---|
| Major | Line 12 says `1. Frontmatter is valid (description, mode, tools/permissions correct)`. The plural `permissions` is not valid markdown-agent frontmatter and is exactly the bug present in sibling agents. A reviewer following this checklist may approve invalid files. | Change to: `Frontmatter is valid (description, mode, permission (singular) object/action map; tools is deprecated)`. Add the allowed field list and schema URL. |
| Minor | Lines 4–7 use the deprecated `tools` field. `write: false` is not a permission key in the valid permission set; `edit` is the relevant key. | Migrate to `permission:` and use `edit: deny`, `bash: deny`. |
| Minor | No input/scope definition: it does not say which directories/globs to audit, or what to do when a path is missing. | Add an **Inputs** section (`agents/**/*.md`, `skills/**/SKILL.md`) and a failure rule for missing paths. |
| Minor | Least privilege is incomplete: `task`, `skill`, `websearch`, and `external_directory` remain allowed by default. The reviewer only needs read/grep/glob/list/webfetch. | Add explicit denies for `task`, `skill`, `websearch`, `external_directory`. |
| Minor | Output format is only `Output a table: File | Severity | Issue | Suggested fix.` It lacks a Status column, per-file sections, and a severity-count example. | Add a full output template with summary table, per-file detail, and counts. |
| Stylistic | Uses "OpenCode" rather than the project's "opencode" branding. | Use "opencode". |

**Corrected frontmatter:**
```yaml
---
description: Reviews opencode agent and skill markdown files for schema validity, scope, safety, and clarity
mode: subagent
permission:
  edit: deny
  bash: deny
  read: allow
  grep: allow
  glob: allow
  list: allow
  webfetch: allow
  task: deny
  skill: deny
  websearch: deny
  external_directory: deny
---
```

---

## `.opencode/agents/data-pipeline.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/agents/data-pipeline.md`
**Status:** Broken

**Offending frontmatter (lines 5–20):**
```yaml
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: deny
  - action: read
    resource: "*"
    effect: allow
  - action: grep
    resource: "*"
    effect: allow
  - action: glob
    resource: "*"
    effect: allow
```

| Severity | Issue | Suggested fix |
|---|---|---|
| Critical | `permissions:` is a ruleset array, not the markdown-agent `permission` map. It is unknown in frontmatter and silently ignored, so `edit: deny` and `shell: deny` are **not enforced**. The agent can edit files and use the shell. | Replace with `permission:` object map; see corrected YAML. |
| Critical | Line 9 `- action: shell` uses an invalid permission key. The key is `bash`, not `shell`. Even after renaming the parent field, this rule would never match. | Use `bash: deny` or a scoped `bash` object. |
| Major | Capability contradiction: line 112 says `Statistical checks (KS test, correlation, variance) should be sampled rather than run on full datasets...`, but the intended `shell` denial means the agent cannot execute Python to compute them. | Either grant scoped execution (`"python *": allow`, `"*": deny`) or narrow the body to static inspection and remove execution claims. |
| Minor | No failure behaviour for missing/unreadable datasets, unsupported formats, or insufficient permissions. | Add a fallback finding such as `unable_to_inspect` with the path and error. |
| Minor | Output category includes `split_overlap` (line 78), but there is no dedicated "Split overlap" check heading; overlap is discussed under label leakage. | Add a "Split overlap" heading or rename the category to `label_leakage`. |
| Minor | Subagent can inherit `task`, `webfetch`, and `websearch` by default; least privilege is not explicit. | Add `task: deny`, `webfetch: deny`, `websearch: deny` under `permission`. |
| Stylistic | The "Config" section only restates `steps`; it adds no real configuration guidance. | Remove it or document actual configuration assumptions. |

**Corrected frontmatter:**
```yaml
---
description: Inspects datasets and dataloaders for label leakage, class imbalance, wrong normalization, train/test shift, split overlap, and corrupted samples
mode: subagent
steps: 12
permission:
  edit: deny
  read: allow
  grep: allow
  glob: allow
  list: allow
  bash:
    "python *": allow
    "*": deny
  task: deny
  webfetch: deny
  websearch: deny
---
```
If the agent should remain strictly read-only, use `bash: deny` and remove the statistical-execution claims from the body.

---

## `.opencode/agents/shape-dtype.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/agents/shape-dtype.md`
**Status:** Broken

**Offending frontmatter (lines 5–17):**
```yaml
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: allow
  - action: read
    resource: "*"
    effect: allow
  - action: grep
    resource: "*"
    effect: allow
```

| Severity | Issue | Suggested fix |
|---|---|---|
| Critical | `permissions:` is the `opencode.json` ruleset shape, not the markdown-agent `permission` map. It is ignored, so `edit: deny` is **not enforced**. | Replace with `permission:` object map; see corrected YAML. |
| Major | Line 9 `- action: shell` is invalid. The permission key is `bash`. Because this rule is an `allow`, no restriction is lost, but the rule is dead. | Use `bash: allow` or a scoped `bash` object. |
| Major | `bash: allow` is unnecessarily broad for the stated work (forward hooks and shape tracing). | Scope execution, e.g. `bash: { "python *": allow, "*": deny }`, or use `bash: ask`. |
| Minor | No failure behaviour when no representative batch exists and static inference cannot determine shapes. | Return a static trace with `confidence: low` and list unresolved layers. |
| Minor | `task`, `webfetch`, and `websearch` remain allowed by default; least privilege is not explicit. | Add `task: deny`, `webfetch: deny`, `websearch: deny`. |
| Minor | Output schema differs from sibling agents: it has no `first_observed_at` or `evidence`, making Work Agent consolidation harder. | Standardize fields across subagents or document the variance. |
| Stylistic | The "Config" section only restates `steps`. | Remove it or add real configuration notes. |

**Corrected frontmatter:**
```yaml
---
description: Traces tensor shapes, dtypes, and devices through a model (static or via forward hooks) to catch mismatches and silent broadcasting bugs
mode: subagent
steps: 12
permission:
  edit: deny
  read: allow
  grep: allow
  glob: allow
  list: allow
  bash:
    "python *": allow
    "*": deny
  task: deny
  webfetch: deny
  websearch: deny
---
```

---

## `.opencode/agents/training-instability.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/agents/training-instability.md`
**Status:** Broken

**Offending frontmatter (lines 5–11):**
```yaml
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: deny
```

| Severity | Issue | Suggested fix |
|---|---|---|
| Critical | `permissions:` is invalid in markdown-agent frontmatter and is ignored, so both `edit: deny` and `shell: deny` are unenforced. | Replace with `permission:` object map. |
| Critical | Line 9 `- action: shell` is invalid; the permission key is `bash`. The intended shell denial therefore cannot match even after fixing the parent field. | Use `bash: deny` or `bash: ask`. |
| Major | Line 17 says `Monitor a training run in progress`, but a denied shell prevents tailing/querying live logs. The agent can only read static files. | Use `bash: ask` or scoped log-reading commands, or reword to "analyze supplied or completed run logs". |
| Minor | Output schema lacks `expected`, `actual`, and `location` fields used by sibling agents. | Add these fields or explicitly document the reduced schema. |
| Minor | No failure behaviour when gradient norms or activation statistics are absent; only a per-epoch confidence note is given. | Add an explicit degraded-analysis path with reduced-confidence findings. |
| Minor | `task`, `webfetch`, and `websearch` remain allowed by default. | Add `task: deny`, `webfetch: deny`, `websearch: deny`. |
| Stylistic | The "Config" section only restates `steps`. | Remove it or add real configuration notes. |

**Corrected frontmatter:**
```yaml
---
description: Analyzes loss curves, gradients, and activation stats for NaN/Inf, exploding/vanishing gradients, dead ReLUs, plateaus, and oscillation, and suggests fixes
mode: subagent
steps: 10
permission:
  edit: deny
  bash: ask
  read: allow
  grep: allow
  glob: allow
  list: allow
  task: deny
  webfetch: deny
  websearch: deny
---
```
If it only analyzes static logs, use `bash: deny` and reword line 17.

---

## `.opencode/agents/work.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/agents/work.md`
**Status:** Broken

**Offending frontmatter (lines 5–20):**
```yaml
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: ask
  - action: read
    resource: "*"
    effect: allow
  - action: grep
    resource: "*"
    effect: allow
  - action: glob
    resource: "*"
    effect: allow
```

| Severity | Issue | Suggested fix |
|---|---|---|
| Critical | `permissions:` is invalid in markdown-agent frontmatter and is ignored. The intended `edit: deny` and `shell: ask` are unenforced; the agent can edit files and run shell commands without confirmation, contradicting line 43 (`Does not fix code or retrain automatically`). | Replace with `permission:` object map. |
| Critical | Line 9 `- action: shell` is invalid; use `bash`. The `effect: ask` must live under `permission.bash`, not a ruleset entry. | Use `bash: ask`. |
| Major | The agent routes work via the Task tool (line 30) but does not declare `task: allow`; it relies on the default. | Add `task: allow` explicitly. |
| Minor | No failure behaviour if a subagent errors, times out, or returns no findings. | Add a fallback that reports which subagent failed and continues with available findings. |
| Minor | No structured handoff contract or consolidated output template; "passing complete context" is vague. | Define handoff fields (symptom, traceback, paths, expected/observed) and a final report schema. |
| Minor | `steps: 12` is low for three subagent calls plus consolidation. | Raise to 20–30 or omit `steps` to use the default. |
| Stylistic | Roster uses `@data-pipeline`, `@shape-dtype`, `@training-instability`; these resolve, but `@` is UI mention syntax. | Use backticks/plain names in prose and keep Task-tool invocation explicit. |

**Corrected frontmatter:**
```yaml
---
description: Primary agent that owns the ML training debugging workflow and coordinates the data pipeline, shape/dtype, and training instability subagents
mode: primary
steps: 24
permission:
  edit: deny
  bash: ask
  read: allow
  grep: allow
  glob: allow
  list: allow
  task: allow
  webfetch: ask
  websearch: ask
---
```

---

## `.opencode/skills/deploy-troubleshoot/SKILL.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/skills/deploy-troubleshoot/SKILL.md`
**Status:** Needs Fix

**Frontmatter found:**
```yaml
name: "deploy-troubleshoot"
description: "Analyzes deployment failure logs and identifies root causes with fixes."
role: "deploy-troubleshoot"
capabilities: ["log-analysis"]
priority: "high"
```

| Severity | Issue | Suggested fix |
|---|---|---|
| Major | Description states only what the skill does; it does not front-load when to use it (deployment logs, `CrashLoopBackOff`, exit codes, CI output). Auto-selection depends on this description. | Rewrite with trigger keywords and an explicit "Use when..." clause. |
| Major | No workflow section; the body jumps from "What it does" to "When to provoke it" to output/example. | Add a numbered workflow: parse log → classify failure → rank max 5 causes → provide fixes → checklist. |
| Minor | Extra frontmatter keys `role`, `capabilities`, and `priority` are not allowed by the skill schema. | Remove them or move them under `metadata` as string values. |
| Minor | Example output uses `solution` and omits `checklist`, while the Output section requires `fixes` and `checklist`. | Align example keys with the documented output contract. |
| Minor | Does not mirror the AGENTS.md required input format (`Log`, `Platform`, `RecentChanges`). | Add an Inputs section matching AGENTS.md. |
| Stylistic | "When to provoke it" is awkward wording. | Rename to "When to use it". |

**Corrected frontmatter:**
```yaml
---
name: deploy-troubleshoot
description: "Analyzes Docker, Kubernetes, and CI/CD deployment failure logs (CrashLoopBackOff, exit codes, timeouts, missing env vars) and identifies root causes with fixes. Use when the user shares deployment logs, stack traces, or CI output."
metadata:
  role: "deploy-troubleshoot"
  capabilities: "log-analysis"
  priority: "high"
---
```

**Suggested workflow addition:**
```markdown
## Workflow
1. Parse the supplied log for `Error:`, `Exit code`, `CrashLoopBackOff`, `OOMKilled`, and timeout markers.
2. Classify the failure: config/env, resources, image/build, networking/health check, or permissions.
3. Rank at most 5 root causes with evidence from the log.
4. Provide fix commands or configuration snippets.
5. End with a verification checklist, or "No deployment issues detected – appears healthy."
```

---

## `.opencode/skills/env-conflict/SKILL.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/skills/env-conflict/SKILL.md`
**Status:** Needs Fix

**Frontmatter found:**
```yaml
name: "env-conflict"
description: "Scans Python environment for missing packages and reports version mismatches."
role: "env-conflict"
capabilities: ["env-scanning"]
priority: "medium"
```

| Severity | Issue | Suggested fix |
|---|---|---|
| Major | Description lacks trigger tokens such as `ModuleNotFoundError`, `ImportError`, version mismatch, fresh VM/CI/container. | Rewrite with triggers front-loaded and an explicit "Use when..." clause. |
| Major | No workflow/procedure; "Detects" is a claim, not an actionable scan. | Add steps using `which python`, `python -m pip show`, `pip list`, `conda list`, and comparison against `requirements.txt`/`pyproject.toml`/`environment.yml`. |
| Major | Example uses `pip list --outdated`, which does not detect missing packages, and `pip install --upgrade numpy==1.24.0`, which is a fix step and can change versions unexpectedly. | Replace with detection commands and a safe install after confirming the declared requirement. |
| Minor | Extra frontmatter keys `role`, `capabilities`, and `priority` are not allowed. | Remove them or move them under `metadata`. |
| Minor | Output requires a "required version", but the source of that requirement is undefined. | State that it comes from a manifest/lockfile, with a fallback when none exists. |
| Minor | No handling for multiple interpreters/venvs or "installed but import fails" cases such as path shadowing. | Add checks for `sys.executable`, `pip -V`, and the full import traceback. |
| Stylistic | "When to provoke it" is awkward wording. | Rename to "When to use it". |

**Corrected frontmatter:**
```yaml
---
name: env-conflict
description: "Detects missing Python packages and version mismatches (ModuleNotFoundError, ImportError, pip/conda conflicts) and reports the exact fix. Use when imports fail or before running code in a fresh VM, CI, or container."
metadata:
  role: "env-conflict"
  capabilities: "env-scanning"
  priority: "medium"
---
```

**Suggested workflow addition:**
```markdown
## Workflow
1. Confirm the interpreter: `which python`, `python -V`, `python -m pip -V`.
2. Reproduce the import and capture the exact exception.
3. Check the installed version: `python -m pip show <pkg>` or `conda list <pkg>`.
4. Read the declared requirement from requirements.txt, pyproject.toml, or environment.yml.
5. Report missing/mismatched packages and the minimal install/upgrade command.
6. If no manifest exists, say so and avoid inventing a required version.
```

---

## `.opencode/skills/numpy-serialization/SKILL.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/skills/numpy-serialization/SKILL.md`
**Status:** Needs Fix

**Frontmatter found:**
```yaml
name: "numpy-serialization"
description: "Detects NumPy save/load errors and suggests the binary format fix pattern."
role: "numpy-serialization"
capabilities: ["np-save-load-detection"]
priority: "medium"
```

**Broken example (lines 24–28):**
```python
array = np.array([1, 2, 3, 4, 5])
np.save("array.npy", array)
loaded = np.load("array.npy.npy")
```

| Severity | Issue | Suggested fix |
|---|---|---|
| Major | Line 28 loads `"array.npy.npy"`, but `np.save("array.npy", ...)` writes `"array.npy"`. The example raises `FileNotFoundError`. | Change to `loaded = np.load("array.npy")`. |
| Major | No diagnostic workflow from error → cause → code change; the body only states what it does and shows one save/load snippet. | Add a numbered workflow and an error/cause/fix table. |
| Major | Claims detection of shape/dtype errors but omits common real failures: object arrays with `allow_pickle=False`, truncated/corrupt files, missing `.npz` keys, and dtype/endianness issues. | Add coverage for these common errors. |
| Minor | Extra frontmatter keys `role`, `capabilities`, and `priority` are not allowed. | Remove them or move them under `metadata`. |
| Minor | Description lacks exact trigger tokens such as `np.save`, `np.load`, `np.savez`, `allow_pickle`, and "truncated". | Rewrite the description with those tokens front-loaded. |
| Minor | Mentions `np.savez` but gives no `.npz` example. | Add a `np.savez`/`np.load` example with key access. |
| Minor | No security warning about `allow_pickle=True` (arbitrary code execution risk). | Add a warning and default to `allow_pickle=False`. |
| Minor | No failure behaviour for missing, corrupt, or permission-denied files. | Add fallback guidance for each case. |
| Stylistic | "When to provoke it" is awkward wording. | Rename to "When to use it". |

**Corrected frontmatter:**
```yaml
---
name: numpy-serialization
description: "Diagnoses NumPy np.save/np.load/np.savez failures (dtype/shape errors, truncated files, allow_pickle errors) and recommends the correct .npy/.npz pattern. Use when NumPy save/load raises an error."
metadata:
  role: "numpy-serialization"
  capabilities: "np-save-load-detection"
  priority: "medium"
---
```

**Corrected example:**
```python
import numpy as np

array = np.array([1, 2, 3, 4, 5])
np.save("array.npy", array)
loaded = np.load("array.npy")
```

**Suggested `.npz` example:**
```python
np.savez("arrays.npz", a=array, b=array * 2)
with np.load("arrays.npz", allow_pickle=False) as data:
    a = data["a"]
```

---

## Cross-file / directory-level issues

| Severity | Location | Issue | Suggested fix |
|---|---|---|---|
| Major | `/home/talha/Desktop/debugger/AGENTS.md` lines 3 and 117 | The harness says skills are in `config/skills/` and says not to modify `config/skills/*/SKILL.md`, but the actual path is `.opencode/skills/`. Agents following the harness will look in a non-existent directory. | Replace both references with `.opencode/skills/` and `.opencode/skills/*/SKILL.md`. |
| Major | All agent frontmatter | Systemic schema drift: `agent-reviewer.md` uses deprecated `tools`; the four ML agents use the `opencode.json` `permissions` ruleset; none uses the markdown-agent `permission` map. | Standardize every agent on `permission:` with an object/action map. |
| Minor | `AGENTS.md` lines 19 and 26 | Line 19 lists `pickle` as a NumPy function, and line 26 uses `ValueError: setting an array element with a incompatible shape`, which is an assignment error, not an `np.save`/`np.load` error. | Say `pickle` is a Python module, and replace the example with a real serialization error such as an `allow_pickle` or truncated-file error. |
| Minor | `AGENTS.md` | The root instructions never mention `.opencode/agents/` or the agent roster, so the primary workflow and `agent-reviewer` are undiscoverable from AGENTS.md. | Add an "Agents" section or cross-reference `work.md`. |
| Minor | `AGENTS.md` vs all `SKILL.md` files | The harness-required input formats (`Context`, `Imports`, `Environment`, `Log`, `Platform`, `RecentChanges`) are not reflected in any skill body. | Add matching Inputs sections to each skill. |
| Minor | `.opencode/agents/agent-reviewer.md` | `agent-reviewer` is an orphan: no agent or AGENTS.md references it. It is loaded but not routed by `work.md`. | Document how to invoke it or remove it if unused. |
| Minor | All skill frontmatter | If `capabilities` is moved under `metadata`, it is currently an array (`["log-analysis"]`), but skill `metadata` must be a string-string map. | Flatten to `capabilities: "log-analysis"` or a comma-separated string. |

**Systemic patterns already counted per-file:**
- All four ML agents use `permissions` (plural) with `{action, resource, effect}` entries and `action: shell`; none use the correct `permission`/`bash` form.
- All three skills use non-schema frontmatter keys and have weak trigger descriptions.
- Subagent output schemas are inconsistent (`training-instability` lacks `expected`/`actual`/`location`).

**Positive checks:**
- All agent `mode` values are valid (`primary`/`subagent`).
- Agent filenames and skill folder names match their intended names; all skill names are lowercase, hyphenated, and under 64 characters.
- No `prompt:` key appears in frontmatter; bodies are correctly treated as prompts.
- All three skills are loaded (confirmed by `available_skills`).
- No `references/` or `scripts/` directories exist, so there are no broken script/path references to report.
- All `@`-references in `work.md` (`data-pipeline`, `shape-dtype`, `training-instability`) resolve to existing agent files.
- No duplicate skill folders or agent filename collisions were found.

---

## Final severity counts

| Scope | Critical | Major | Minor | Stylistic | Total |
|---|---:|---:|---:|---:|---:|
| Per-file issues | 7 | 14 | 27 | 8 | 56 |
| Cross-file unique issues | 0 | 2 | 5 | 0 | 7 |
| **Grand total** | **7** | **16** | **32** | **8** | **63** |

## Executive verdict

The directory is **not production-ready**. The highest-priority defect is that the four ML agents express permissions in the wrong schema (`permissions` ruleset with `action: shell`), so every intended `deny`/`ask` is silently ignored. In practice, `data-pipeline`, `shape-dtype`, `training-instability`, and `work` can edit files and use the shell despite their stated restrictions; `work` can modify code despite its non-goal. Fix those Critical items first by converting all agents to the singular `permission` map and `bash` key.

The skills load, but their descriptions do not reliably advertise when to use them, none has a real workflow, and `numpy-serialization` contains a broken `np.load("array.npy.npy")` example. `AGENTS.md` also points to a non-existent `config/skills/` path. After the Critical permission fixes, standardize frontmatter, add workflows and correct examples, and reconcile AGENTS.md with the actual `.opencode/` layout.

### Fixes applied

**Critical**
- **Critical — invalid `permissions` ruleset (ignored)**: `.opencode/agents/data-pipeline.md` — replaced with a singular `permission` object/action map.
- **Critical — invalid `action: shell` key**: `.opencode/agents/data-pipeline.md` — replaced with the `bash` permission key.
- **Critical — invalid `permissions` ruleset (ignored)**: `.opencode/agents/shape-dtype.md` — replaced with a singular `permission` object/action map.
- **Critical — invalid `permissions` ruleset (ignored)**: `.opencode/agents/training-instability.md` — replaced with a singular `permission` object/action map.
- **Critical — invalid `action: shell` key**: `.opencode/agents/training-instability.md` — replaced with the `bash` permission key.
- **Critical — invalid `permissions` ruleset (ignored)**: `.opencode/agents/work.md` — replaced with a singular `permission` object/action map.
- **Critical — invalid `action: shell` key**: `.opencode/agents/work.md` — replaced with `bash: ask`.

**Major**
- **Major — reviewer checklist endorsed the invalid `tools/permissions` schema**: `.opencode/agents/agent-reviewer.md` — rewrote checklist item with the valid field list, `permission` (singular), and schema URL.
- **Major — capability contradiction (stats checks vs shell deny)**: `.opencode/agents/data-pipeline.md` — scoped `bash` to allow `python *` and deny everything else.
- **Major — invalid `action: shell` key**: `.opencode/agents/shape-dtype.md` — replaced with the `bash` permission key.
- **Major — `bash: allow` unnecessarily broad**: `.opencode/agents/shape-dtype.md` — scoped `bash` to allow `python *` and deny everything else.
- **Major — "monitor in progress" contradicted denied shell**: `.opencode/agents/training-instability.md` — reworded purpose and granted `bash: ask`.
- **Major — `task` tool not declared for routing**: `.opencode/agents/work.md` — added explicit `task: allow`.
- **Major — weak skill description (no triggers)**: `.opencode/skills/deploy-troubleshoot/SKILL.md` — rewrote description with trigger keywords and "Use when".
- **Major — no workflow section**: `.opencode/skills/deploy-troubleshoot/SKILL.md` — added a numbered Workflow section.
- **Major — weak skill description (no triggers)**: `.opencode/skills/env-conflict/SKILL.md` — rewrote description with trigger keywords and "Use when".
- **Major — no workflow/procedure**: `.opencode/skills/env-conflict/SKILL.md` — added a numbered Workflow using interpreter/package checks.
- **Major — misleading example (`pip list --outdated`, blind upgrade)**: `.opencode/skills/env-conflict/SKILL.md` — replaced with detection commands and install only after confirming the declared requirement.
- **Major — broken `np.load("array.npy.npy")` example**: `.opencode/skills/numpy-serialization/SKILL.md` — corrected to `np.load("array.npy")`.
- **Major — no diagnostic workflow**: `.opencode/skills/numpy-serialization/SKILL.md` — added Workflow plus an error/cause/fix table.
- **Major — missing common failure coverage**: `.opencode/skills/numpy-serialization/SKILL.md` — added `allow_pickle`, truncated/corrupt, missing `.npz` key, and dtype/endianness cases.
- **Major — systemic agent frontmatter schema drift**: `.opencode/agents/{agent-reviewer,data-pipeline,shape-dtype,training-instability,work}.md` — standardized all agents on the singular `permission` map and `bash` key.

**Minor**
- **Minor — deprecated `tools` field**: `.opencode/agents/agent-reviewer.md` — migrated to `permission` with `edit: deny`, `bash: deny`.
- **Minor — no input/scope definition or missing-path rule**: `.opencode/agents/agent-reviewer.md` — added Inputs section and missing-input handling.
- **Minor — incomplete least privilege**: `.opencode/agents/agent-reviewer.md` — added denies for `task`, `skill`, `websearch`, `external_directory`.
- **Minor — weak output format**: `.opencode/agents/agent-reviewer.md` — added template with Status column, per-file sections, and severity counts.
- **Minor — no failure behaviour on unreadable datasets**: `.opencode/agents/data-pipeline.md` — added Failure Handling and `unable_to_inspect` category.
- **Minor — `split_overlap` category had no check heading**: `.opencode/agents/data-pipeline.md` — added "### 6. Split overlap" and renumbered dataloader section.
- **Minor — implicit least privilege**: `.opencode/agents/data-pipeline.md` — added `task`, `webfetch`, `websearch` denies.
- **Minor — no failure behaviour without a representative batch**: `.opencode/agents/shape-dtype.md` — added Failure Handling with `confidence: low` and `unresolved`.
- **Minor — implicit least privilege**: `.opencode/agents/shape-dtype.md` — added `task`, `webfetch`, `websearch` denies.
- **Minor — output schema missing `first_observed_at`/`evidence`**: `.opencode/agents/shape-dtype.md` — added fields to schema and example.
- **Minor — output schema missing `expected`/`actual`/`location`**: `.opencode/agents/training-instability.md` — added fields to schema.
- **Minor — no degraded-analysis path**: `.opencode/agents/training-instability.md` — added Failure Handling for missing gradient/activation stats.
- **Minor — implicit least privilege**: `.opencode/agents/training-instability.md` — added `task`, `webfetch`, `websearch` denies.
- **Minor — no subagent failure behaviour**: `.opencode/agents/work.md` — added Failure Handling for errors/timeouts/empty results.
- **Minor — vague handoff and no report template**: `.opencode/agents/work.md` — added Handoff Contract and Consolidated Report Schema.
- **Minor — `steps: 12` too low for three subagents**: `.opencode/agents/work.md` — raised to `steps: 24`.
- **Minor — disallowed skill frontmatter keys**: `.opencode/skills/deploy-troubleshoot/SKILL.md` — moved `role`/`capabilities`/`priority` under `metadata` as strings.
- **Minor — example keys mismatch output contract**: `.opencode/skills/deploy-troubleshoot/SKILL.md` — aligned example to `fixes` and added `checklist`.
- **Minor — no Inputs matching AGENTS.md**: `.opencode/skills/deploy-troubleshoot/SKILL.md` — added Inputs (`Log`, `Platform`, `RecentChanges`).
- **Minor — disallowed skill frontmatter keys**: `.opencode/skills/env-conflict/SKILL.md` — moved `role`/`capabilities`/`priority` under `metadata` as strings.
- **Minor — required-version source undefined**: `.opencode/skills/env-conflict/SKILL.md` — added `required_version_source` with no-manifest fallback.
- **Minor — no handling for multiple interpreters/path shadowing**: `.opencode/skills/env-conflict/SKILL.md` — added `sys.executable`/`pip -V`/traceback checks.
- **Minor — disallowed skill frontmatter keys**: `.opencode/skills/numpy-serialization/SKILL.md` — moved `role`/`capabilities`/`priority` under `metadata` as strings.
- **Minor — description lacked trigger tokens**: `.opencode/skills/numpy-serialization/SKILL.md` — rewrote with `np.save`/`np.load`/`np.savez`/`allow_pickle`/truncated triggers.
- **Minor — no `.npz` example**: `.opencode/skills/numpy-serialization/SKILL.md` — added `np.savez`/`np.load` key-access example.
- **Minor — no `allow_pickle` security warning**: `.opencode/skills/numpy-serialization/SKILL.md` — added Security section defaulting to `allow_pickle=False`.
- **Minor — no failure behaviour for missing/corrupt/permission-denied files**: `.opencode/skills/numpy-serialization/SKILL.md` — added Failure Handling guidance.
- **Minor — AGENTS.md input formats not reflected in skills**: `.opencode/skills/{deploy-troubleshoot,env-conflict,numpy-serialization}/SKILL.md` — added matching Inputs sections.
- **Minor — `agent-reviewer` orphan/undocumented**: `.opencode/agents/agent-reviewer.md` — added Usage section documenting manual invocation.
- **Minor — `capabilities` array incompatible with `metadata` map**: `.opencode/skills/{deploy-troubleshoot,env-conflict,numpy-serialization}/SKILL.md` — flattened to string values.

### Skipped
- **Major — `AGENTS.md` lines 3/117 reference non-existent `config/skills/`**: skipped — `AGENTS.md` is at the repo root, outside the instructed scope (`.opencode/agents` and skills folders).
- **Minor — `AGENTS.md` lines 19/26 misstate `pickle` and give a non-serialization error example**: skipped — `AGENTS.md` is outside the instructed scope.
- **Minor — `AGENTS.md` never references `.opencode/agents/` or the agent roster**: skipped — `AGENTS.md` is outside the instructed scope.
- **Stylistic items** ("OpenCode" branding, "When to provoke it" wording, `@` mentions, redundant "Config" sections): not fixed — the task scoped fixes to Critical, Major, and Minor only.

### Re-review result
- All in-scope Critical, Major, and Minor issues addressed; 3 `AGENTS.md` issues skipped as out of scope. All 8 files still parse with valid YAML/opencode frontmatter. A re-review is needed to confirm the fixes and catch regressions.

---

## Cycle 2 — 2026-11-08

- **Model used for review:** `opencode/deepseek-v4.1-flash-free`
- **Review prompt / agent:** `agent-reviewer` — "Review all files in `.opencode/agents` and every skill folder in the repository, validating frontmatter, scope, instructions, permissions, handoffs, edge cases, examples, and cross-file consistency."
- **Schema source:** `https://opencode.ai/config.json` and the built-in `customize-opencode` skill.
- **Repository root:** `/home/talha/Desktop/debugger`
- **No files were modified.**

### Scope and files reviewed

No `config/skills/` directory and no nested `skills/` directories exist. The only skill definitions are under `.opencode/skills/`.

| # | Path | Kind |
|---:|---|---|
| 1 | `.opencode/agents/agent-reviewer.md` | Agent — subagent |
| 2 | `.opencode/agents/data-pipeline.md` | Agent — subagent |
| 3 | `.opencode/agents/shape-dtype.md` | Agent — subagent |
| 4 | `.opencode/agents/training-instability.md` | Agent — subagent |
| 5 | `.opencode/agents/work.md` | Agent — primary |
| 6 | `.opencode/skills/deploy-troubleshoot/SKILL.md` | Skill |
| 7 | `.opencode/skills/env-conflict/SKILL.md` | Skill |
| 8 | `.opencode/skills/numpy-serialization/SKILL.md` | Skill |
| 9 | `AGENTS.md` | Harness reference, reviewed for cross-file consistency |

### Frontmatter validation

| File | Result | Notes |
|---|---|---|
| `.opencode/agents/agent-reviewer.md` | Valid | `description`, `mode: subagent`, `permission` map. No `name` (derived from filename); no deprecated `tools`. |
| `.opencode/agents/data-pipeline.md` | Valid | `description`, `mode`, `steps`, `permission`. `bash` rule order is correct: broad `"*": deny` first, narrow `"python *": allow` last. Security caveat below. |
| `.opencode/agents/shape-dtype.md` | Valid | Same valid frontmatter shape as `data-pipeline`. Security caveat below. |
| `.opencode/agents/training-instability.md` | Valid | `bash: ask` is valid; `read`/`grep`/`glob`/`list` now declared. |
| `.opencode/agents/work.md` | Valid | `mode: primary`, `task: allow`; no `edit`. |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Valid | `name` matches folder; `metadata` is a string-string map; no stray top-level keys. |
| `.opencode/skills/env-conflict/SKILL.md` | Valid | `name` matches folder; metadata is a string-string map. |
| `.opencode/skills/numpy-serialization/SKILL.md` | Valid | `name` matches folder; metadata is a string-string map. |
| `AGENTS.md` | N/A | Not an agent/skill frontmatter file. Its skill path is wrong; see findings. |

No invalid YAML, no `permissions:` plural rulesets, no `shell` permission key, and no `prompt:` frontmatter remain. Cycle 1's schema migrations are present.

---

### Per-file findings

#### `.opencode/agents/agent-reviewer.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/agent-reviewer.md` | Minor | The output template uses a `Stylistic` column while the classification is `Stylistic/Nitpick`; it does not define `Status` values or require a full-path inventory of every file reviewed. | Use `Stylistic/Nitpick` consistently, define `OK / Needs Fix / Broken`, and require one row per file with its path. |
| `.opencode/agents/agent-reviewer.md` | Minor | Inputs cover agent and skill globs but omit `AGENTS.md`, even though harness consistency is part of the review. There is also no rule for an unparseable YAML/frontmatter block. | Add `AGENTS.md` to Inputs and add a `parse_error`/`frontmatter_invalid` finding path. |
| `.opencode/agents/agent-reviewer.md` | Minor | Checklist item 1 omits two schema details: `webfetch`, `websearch`, `todowrite`, `question`, and `doom_loop` accept only a flat action, and file agents must not put `prompt:` in frontmatter. | Add both notes under checklist item 1 so the reviewer does not approve invalid frontmatter. |

#### `.opencode/agents/data-pipeline.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/data-pipeline.md` | Critical | `bash: { "*": deny, "python *": allow }` grants arbitrary Python execution. A command such as `python -c "open('x','w')..."` can write or delete files, bypassing the intended `edit: deny`. The agent is described as inspect-only. | Use `bash: deny` and remove the statistical-execution claims, or use `bash: ask`/a dedicated pre-approved read-only inspector script. Document that Python execution is not sandboxed. |
| `.opencode/agents/data-pipeline.md` | Minor | `"python *"` does not match `python3 ...`, so the statistical checks can fail on systems without a `python` alias. | Add `"python3 *"` and/or document the required interpreter. |
| `.opencode/agents/data-pipeline.md` | Minor | No handoff mapping to `work.md`'s required fields (`symptom`, `traceback`, `paths`, `expected`, `observed`, `context`). | Add a Handoff section that maps or references the Work Agent contract. |
| `.opencode/agents/data-pipeline.md` | Stylistic/Nitpick | The `## Config` section only restates `steps` and adds no configuration guidance. | Remove it or document real configuration assumptions. |

#### `.opencode/agents/shape-dtype.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/shape-dtype.md` | Critical | `bash: { "*": deny, "python *": allow }` grants arbitrary Python execution, which can write/delete files and bypass `edit: deny`. | Use `bash: deny` for static-only tracing, or `bash: ask`/a dedicated read-only tracer for dynamic mode. Document the boundary. |
| `.opencode/agents/shape-dtype.md` | Major | Non-Goals says "the primary Work Agent handles fix suggestion and routing," but the agent's output includes `suggested_fix` and its purpose is to suggest fixes. This is a direct contradiction. | Reword to: "flags and suggests fixes only; does not apply them; Work consolidates and routes." |
| `.opencode/agents/shape-dtype.md` | Major | `shape_trace[]` records `dtype` but not `device`, even though device mismatch is one of the declared checks. The output cannot show device evidence for the trace. | Add `device` to each `shape_trace` entry and to the example trace. |
| `.opencode/agents/shape-dtype.md` | Minor | Failure Handling only covers the missing representative-batch case. It does not cover an unparseable model, unsupported framework, or failed forward pass. | Add an `unable_to_inspect`/`confidence: low` fallback containing the error and unresolved layers. |
| `.opencode/agents/shape-dtype.md` | Minor | Integration Notes only reference the Work Agent. There is no handoff to `data-pipeline` or `training-instability`. | Add cross-links for data-dependent shapes and dtype/AMP-induced instability. |
| `.opencode/agents/shape-dtype.md` | Stylistic/Nitpick | The `## Config` section only restates `steps`. | Remove it or document real configuration assumptions. |

#### `.opencode/agents/training-instability.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/training-instability.md` | Major | Failure Handling instructs the agent to "mark those findings as reduced confidence," but the Outputs schema has no `confidence` field. The fallback behavior cannot be represented. | Add `confidence: "high | medium | low"` to each finding or the top-level envelope, and include it in the example. |
| `.opencode/agents/training-instability.md` | Minor | The Example Finding omits `location`, `expected`, and `actual`, although all three are defined in the schema. | Add those fields to the example. |
| `.opencode/agents/training-instability.md` | Minor | The `category` enum has no `lr_schedule` even though the checks discuss LR schedules decaying too early or aggressively. | Add `lr_schedule`, or document that those findings map to `loss_plateau`/`oscillation`. |
| `.opencode/agents/training-instability.md` | Minor | `bash: ask` is broad for an agent that mainly reads logs. | Scope it to log-reading commands (`tail *`, `grep *`, `journalctl *`) or document why arbitrary shell access is needed. |
| `.opencode/agents/training-instability.md` | Minor | Integration Notes omit a `shape-dtype` handoff for dtype/device/AMP-induced NaNs. | Add a cross-reference to `shape-dtype`. |
| `.opencode/agents/training-instability.md` | Stylistic/Nitpick | The `## Config` section only restates `steps`. | Remove it or document real configuration assumptions. |

#### `.opencode/agents/work.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/work.md` | Major | The primary workflow routes only to the three ML subagents. The three skills defined by `AGENTS.md` (`env-conflict`, `numpy-serialization`, `deploy-troubleshoot`) are never mentioned, and `skill` is not explicitly declared. Env/serialization/deploy reports may be misrouted or ignored. | Add a "Skill Routing" section listing each skill's trigger and declare `skill: allow` if it is not inherited by default. |
| `.opencode/agents/work.md` | Minor | There is no Inputs section for the initial user request; the handoff contract is only for subagents. | Add Inputs: symptom, traceback, paths, expected/observed behavior, context, and recent changes. |
| `.opencode/agents/work.md` | Minor | The Consolidated Report Schema drops `location`, `evidence`, `expected`, and `actual` from subagent findings, losing where-and-why detail. | Add these as optional fields or define how `root_cause_chain` preserves them. |
| `.opencode/agents/work.md` | Minor | `bash: ask` permits arbitrary commands even though Non-Goals says no retraining. A user can approve a training command. | Scope `bash` to diagnostic commands, or state that confirmation is required before any state-changing command. |
| `.opencode/agents/work.md` | Minor | There is no example consolidated report, and `source_agent` only allows the three subagents, so Work-originated or skill-originated findings have no valid source value. | Add an example report and extend `source_agent` to `work` or `skill:<name>`. |
| `.opencode/agents/work.md` | Stylistic/Nitpick | The roster uses `@data-pipeline` etc. in prose. | Use backticks or plain names in prose and keep Task-tool invocation explicit. |

#### `.opencode/skills/deploy-troubleshoot/SKILL.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Minor | The Output section names the root-cause field `list`, but the example uses `root_causes`; the output contract and example use different shapes. | Rename one to match the other, preferably `root_causes` in both. |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Minor | The example root causes have no log evidence and the "fixes" are prose, while the Workflow requires evidence and fix commands/configuration snippets. | Add a log excerpt and concrete `kubectl`/Docker commands. |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Minor | There is no failure handling for an empty/unparseable log, a missing `Platform`, or multiple platforms. | Add a Failure Handling section returning "insufficient log data" and naming the missing input. |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Stylistic/Nitpick | "When to provoke it" is awkward wording. | Rename to "When to use it". |

#### `.opencode/skills/env-conflict/SKILL.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/skills/env-conflict/SKILL.md` | Major | The description promises "pip/conda conflicts," but the workflow only checks one package with `pip show`/`conda list` plus a manifest. It never runs `pip check`, `pipdeptree`, or a conda dependency solve, so transitive dependency conflicts are not detected. | Add `python -m pip check`, `pipdeptree`, or `conda env update --dry-run`/conda conflict checks, and define the conflict output. |
| `.opencode/skills/env-conflict/SKILL.md` | Minor | The Output section specifies a table but the example shows only commands, not a sample output table. | Add a sample table for missing, mismatched, and conflicting packages. |
| `.opencode/skills/env-conflict/SKILL.md` | Minor | There is no fallback for `ImportError` caused by missing system libraries (e.g. `libGL`) or by conflicting manifests; step 5 only covers path shadowing. | Add system-library/traceback checks and a "conflicting manifests" fallback. |
| `.opencode/skills/env-conflict/SKILL.md` | Stylistic/Nitpick | "When to provoke it" is awkward wording. | Rename to "When to use it". |

#### `.opencode/skills/numpy-serialization/SKILL.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/skills/numpy-serialization/SKILL.md` | Major | The Output section says "`np.save` / `np.load` for `.npy`/`.npz`," but `.npz` archives are written with `np.savez`/`np.savez_compressed`, not `np.save`. | Correct to: "`np.save` for `.npy`; `np.savez` for `.npz`; `np.load` for both." |
| `.opencode/skills/numpy-serialization/SKILL.md` | Minor | The description/What-it-does claims shape errors, but the error table has no shape-mismatch row. `ValueError: setting an array element with an incompatible shape` is an assignment error, not an `np.save`/`np.load` error. | Add a row clarifying that shape errors usually occur before saving, and keep the serialization table focused on real save/load failures. |
| `.opencode/skills/numpy-serialization/SKILL.md` | Minor | The `.npz` example uses `array` from the previous example, so it is not self-contained. | Define `array` in the `.npz` example or state that it continues from above. |
| `.opencode/skills/numpy-serialization/SKILL.md` | Minor | Failure Handling says "Permission denied: check directory permissions and write to a writable location." That is write-oriented; load failures need read-permission/path checks. | Split read and write permission guidance. |
| `.opencode/skills/numpy-serialization/SKILL.md` | Minor | There is no mention that `np.save("array", ...)` appends `.npy`, which is a common cause of the wrong filename on load. | Add this to the `FileNotFoundError`/filename row. |
| `.opencode/skills/numpy-serialization/SKILL.md` | Stylistic/Nitpick | "When to provoke it" is awkward wording. | Rename to "When to use it". |

#### `AGENTS.md` (harness reference)

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `AGENTS.md` | Major | Lines 3 and 117 say skills live in `config/skills/` and `config/skills/*/SKILL.md`; the actual path is `.opencode/skills/`. The harness points at a non-existent directory. | Replace both references with `.opencode/skills/` and `.opencode/skills/*/SKILL.md`. |
| `AGENTS.md` | Minor | Line 19 lists `pickle` as a NumPy function in the numpy-serialization instruction. | Identify `pickle` as a separate Python module; keep NumPy calls to `np.save`/`np.load`/`np.savez`. |
| `AGENTS.md` | Minor | Line 26 uses `ValueError: setting an array element with a incompatible shape`, which is an assignment error, not an `np.save`/`np.load` error. The grammar is also wrong. | Replace it with a real serialization error (e.g. `allow_pickle=False` object array or `FileNotFoundError` from a doubled `.npy`) and fix "an incompatible". |
| `AGENTS.md` | Minor | The harness never mentions `.opencode/agents/` or the agent roster, so the primary workflow and `agent-reviewer` are not discoverable from the root instructions. | Add an "Agents" section pointing to `.opencode/agents/` and `work.md`. |
| `AGENTS.md` | Minor | It claims each skill follows the Single Responsibility Principle, but `deploy-troubleshoot` classifies config/env failures that overlap `env-conflict`. | Clarify the boundary (deployment runtime config vs Python package/import environment) or drop the SRP claim. |
| `AGENTS.md` | Minor | The expected output for numpy-serialization repeats the incorrect "`np.save`/`np.load` for `.npy`/`.npz`" method mapping. | Update it to `np.save` for `.npy`, `np.savez` for `.npz`, `np.load` for both. |
| `AGENTS.md` | Stylistic/Nitpick | "Do not modify the skill files ... use this harness" is confusing because the harness is documentation, not an executor. | Reword to: "Do not edit skill files directly; edit them only as part of a reviewed change." |

---

### Summary

Status legend: `OK` = no Critical or Major issues; `Needs Fix` = at least one Major issue; `Broken` = at least one Critical issue.

| File | Status | Critical | Major | Minor | Stylistic/Nitpick |
|---|---|---:|---:|---:|---:|
| `.opencode/agents/agent-reviewer.md` | OK | 0 | 0 | 3 | 0 |
| `.opencode/agents/data-pipeline.md` | Broken | 1 | 0 | 2 | 1 |
| `.opencode/agents/shape-dtype.md` | Broken | 1 | 2 | 2 | 1 |
| `.opencode/agents/training-instability.md` | Needs Fix | 0 | 1 | 4 | 1 |
| `.opencode/agents/work.md` | Needs Fix | 0 | 1 | 4 | 1 |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | OK | 0 | 0 | 3 | 1 |
| `.opencode/skills/env-conflict/SKILL.md` | Needs Fix | 0 | 1 | 2 | 1 |
| `.opencode/skills/numpy-serialization/SKILL.md` | Needs Fix | 0 | 1 | 4 | 1 |
| `AGENTS.md` (harness) | Needs Fix | 0 | 1 | 5 | 1 |
| **Total** |  | **2** | **7** | **29** | **8** |

### What is correct

- All eight agent/skill frontmatters are valid YAML and use valid opencode fields.
- All five agents now use the singular `permission` map and the `bash` key; no `permissions:` ruleset or `shell` key remains.
- All three skill `name` values match their folder names, and all skill metadata values are strings.
- All skill descriptions front-load trigger keywords and include "Use when..." guidance.
- All skill bodies now have Inputs, Workflow, Output, and some failure handling.
- All `@` references in `work.md` resolve to real agent files, and all skill names referenced by `AGENTS.md` exist.
- The previously broken `np.load("array.npy.npy")` example is fixed, and the `allow_pickle` security warning is present.

### Out-of-scope note

`test-agent/pipeline.md`, `test-agent/shape.md`, and `test-agent/training.md` are review logs, not agent or skill definitions, so they were not counted as reviewed files. They contain stale claims (`permissions:` lists and `shell` allow/deny) that no longer match the current frontmatter; archive them or update them if they are kept as documentation.

### Overall verdict

Cycle 2 is **not clean**. The Cycle 1 schema defects are fixed, but two Critical security issues remain: `data-pipeline` and `shape-dtype` grant arbitrary Python execution, which can write or delete files and therefore defeats their `edit: deny` restriction. Seven Major issues remain in output contracts, routing, and harness paths: the `shape-dtype` non-goal contradiction and missing `device` in its trace, the missing confidence field in `training-instability`, the missing skill routing in `work.md`, the missing conflict detection in `env-conflict`, the `.npz` method error in `numpy-serialization`, and the non-existent `config/skills/` path in `AGENTS.md`.

The skills are structurally usable, but several examples and output contracts still do not match their instructions. Fix the two Critical permission issues first, then the Major contract/routing issues. Restart opencode after any config-time file change; it is not hot-reloaded. Re-review is required after the fixes.

### Severity counts

| Severity | Count |
|---|---:|
| Critical | 2 |
| Major | 7 |
| Minor | 29 |
| Stylistic/Nitpick | 8 |
| **Total** | **46** |

### Fixes applied

**Critical**
- **Critical — `bash` `"python *": allow` grants arbitrary Python execution, bypassing `edit: deny`**: `.opencode/agents/data-pipeline.md` — replaced the `bash` map with `bash: ask` and added a Permissions note that Python execution is not sandboxed.
- **Critical — `bash` `"python *": allow` grants arbitrary Python execution, bypassing `edit: deny`**: `.opencode/agents/shape-dtype.md` — replaced the `bash` map with `bash: ask` and added a Permissions note that dynamic tracing executes unsandboxed Python.

**Major**
- **Major — Non-Goals contradicts `suggested_fix` (fix suggestion)**: `.opencode/agents/shape-dtype.md` — reworded to "flags and suggests fixes only; does not apply them; Work consolidates and routes."
- **Major — `shape_trace[]` records `dtype` but not `device`**: `.opencode/agents/shape-dtype.md` — added `device` to the `shape_trace` schema and example.
- **Major — failure handling says "reduced confidence" but no `confidence` field**: `.opencode/agents/training-instability.md` — added `confidence` to the finding schema and example.
- **Major — primary workflow never routes to skills and `skill` not declared**: `.opencode/agents/work.md` — added a "Skill Routing" section and `skill: allow`.
- **Major — env-conflict never detects transitive dependency conflicts**: `.opencode/skills/env-conflict/SKILL.md` — added `pip check`/`pipdeptree`/conda dry-run steps and a conflict status in the output table.
- **Major — `.npz` incorrectly mapped to `np.save`**: `.opencode/skills/numpy-serialization/SKILL.md` — corrected to "`np.save` for `.npy`; `np.savez` for `.npz`; `np.load` for both."

**Minor**
- **Minor — `Stylistic` column label inconsistent and Status values/complete inventory undefined**: `.opencode/agents/agent-reviewer.md` — renamed to `Stylistic/Nitpick`, defined `OK / Needs Fix / Broken`, and required one row per full path.
- **Minor — Inputs omit `AGENTS.md` and no unparseable-frontmatter rule**: `.opencode/agents/agent-reviewer.md` — added `AGENTS.md` to Inputs and a `frontmatter_invalid` finding path.
- **Minor — checklist item 1 missing flat-action tools and `prompt:` restriction**: `.opencode/agents/agent-reviewer.md` — added the flat-action tool list and the no-`prompt:` rule.
- **Minor — `"python *"` does not match `python3`**: `.opencode/agents/data-pipeline.md` — resolved by replacing the glob map with `bash: ask`.
- **Minor — no handoff mapping to `work.md` fields**: `.opencode/agents/data-pipeline.md` — added a Handoff section using `symptom`/`traceback`/`paths`/`expected`/`observed`/`context`.
- **Minor — Failure Handling covers only missing batch**: `.opencode/agents/shape-dtype.md` — added an unparseable/unsupported/failed-forward fallback with `confidence: "low"` and error text.
- **Minor — no cross-links to `data-pipeline`/`training-instability`**: `.opencode/agents/shape-dtype.md` — added both cross-references.
- **Minor — Example Finding omits `location`/`expected`/`actual`**: `.opencode/agents/training-instability.md` — added the missing fields.
- **Minor — category enum lacks `lr_schedule`**: `.opencode/agents/training-instability.md` — added `lr_schedule` to the enum.
- **Minor — `bash: ask` unnecessarily broad**: `.opencode/agents/training-instability.md` — scoped to `tail *`, `grep *`, `journalctl *` with a broad deny.
- **Minor — Integration Notes omit a `shape-dtype` handoff**: `.opencode/agents/training-instability.md` — added the shape/dtype cross-reference.
- **Minor — no Inputs section for the initial user request**: `.opencode/agents/work.md` — added an Inputs section mirroring the handoff contract.
- **Minor — report schema drops `location`/`evidence`/`expected`/`actual`**: `.opencode/agents/work.md` — added them to the consolidated report schema.
- **Minor — `bash: ask` permits arbitrary state-changing commands**: `.opencode/agents/work.md` — added an explicit confirmation-before-state-change rule under Non-Goals.
- **Minor — no example report and `source_agent` lacks Work/skill sources**: `.opencode/agents/work.md` — added an Example Consolidated Report and extended `source_agent` to `work | skill:<name>`.
- **Minor — Output field `list` vs example `root_causes`**: `.opencode/skills/deploy-troubleshoot/SKILL.md` — renamed the field to `root_causes`.
- **Minor — example lacks log evidence and concrete fix commands**: `.opencode/skills/deploy-troubleshoot/SKILL.md` — added a `log_excerpt` and `kubectl` commands.
- **Minor — no failure handling for empty/missing/multiple platforms**: `.opencode/skills/deploy-troubleshoot/SKILL.md` — added a Failure Handling section.
- **Minor — Output says table but example has no sample table**: `.opencode/skills/env-conflict/SKILL.md` — added a sample output table.
- **Minor — no fallback for missing system libs or conflicting manifests**: `.opencode/skills/env-conflict/SKILL.md` — extended step 6 to check tracebacks for system libraries and conflicting manifests.
- **Minor — shape errors claimed but no shape-mismatch row**: `.opencode/skills/numpy-serialization/SKILL.md` — added a row clarifying shape errors occur before serialization.
- **Minor — `.npz` example not self-contained**: `.opencode/skills/numpy-serialization/SKILL.md` — defined `array` in the `.npz` example.
- **Minor — permission-denied guidance is write-only**: `.opencode/skills/numpy-serialization/SKILL.md` — split into save (write) and load (read) guidance.
- **Minor — no mention that `np.save` appends `.npy`**: `.opencode/skills/numpy-serialization/SKILL.md` — added it to the `FileNotFoundError` row.

### Skipped
- **Out of scope — all `AGENTS.md` findings** (Major `config/skills/` path; Minors on `pickle`, error example, agent roster, SRP claim, method mapping; Stylistic wording): `AGENTS.md` is outside the instructed scope (`.opencode/agents` and skill folders), matching Cycle 1's handling.
- **Out of requested severity — all Stylistic/Nitpick findings** (redundant `## Config` sections in `data-pipeline`, `shape-dtype`, `training-instability`; "When to provoke it" wording in the three skills; `@agent` prose in `work.md`): only Critical, Major, and Minor were requested.

### Re-review result
- All in-scope Critical (2), Major (7), and Minor (24) issues were addressed; 1 Minor (`python3`) was resolved by the Critical `bash` change. The 6 `AGENTS.md` findings (1 Major, 5 Minor) and the 8 Stylistic/Nitpick items were skipped as out of scope. All 8 agent/skill files still parse as valid YAML/opencode frontmatter. Re-review is required to confirm the fixes and catch regressions.

---

## Cycle 3 — 2026-11-08

- **Model used for review:** `opencode/deepseek-v4.1-flash-free`
- **Review prompt / agent:** `agent-reviewer` — review all agent files and skill folders, validate structure, frontmatter, scope, permissions, handoffs, edge cases, examples, and consistency with `AGENTS.md`.
- **Schema source:** `https://opencode.ai/config.json` and the built-in `customize-opencode` skill.
- **Repository root:** `/home/talha/Desktop/debugger`
- **Files modified:** none (read-only review).

### Scope and files reviewed

No `config/skills/` directory exists. No skill folder contains `references/` or `scripts/`. The only skill definitions are under `.opencode/skills/`.

| # | Path | Kind |
|---:|---|---|
| 1 | `.opencode/agents/agent-reviewer.md` | Agent — subagent |
| 2 | `.opencode/agents/data-pipeline.md` | Agent — subagent |
| 3 | `.opencode/agents/shape-dtype.md` | Agent — subagent |
| 4 | `.opencode/agents/training-instability.md` | Agent — subagent |
| 5 | `.opencode/agents/work.md` | Agent — primary |
| 6 | `.opencode/skills/deploy-troubleshoot/SKILL.md` | Skill |
| 7 | `.opencode/skills/env-conflict/SKILL.md` | Skill |
| 8 | `.opencode/skills/numpy-serialization/SKILL.md` | Skill |
| 9 | `AGENTS.md` | Harness reference, reviewed for cross-file consistency |

`test-agent/{pipeline,shape,training}.md` are stale review artifacts, not agent or skill definitions; they are noted out of scope below.

### Frontmatter validation

| File | Result | Notes |
|---|---|---|
| `.opencode/agents/agent-reviewer.md` | Valid | `description`, `mode: subagent`, singular `permission` map. No deprecated `tools`, no `prompt:`. |
| `.opencode/agents/data-pipeline.md` | Valid | `description`, `mode`, `steps`, singular `permission`; `bash: ask` is valid. |
| `.opencode/agents/shape-dtype.md` | Valid | Same valid shape as `data-pipeline`; `bash: ask`. |
| `.opencode/agents/training-instability.md` | Valid | `bash` object uses correct broad-deny-first, narrow-ask-last order. |
| `.opencode/agents/work.md` | Valid | `mode: primary`, `task: allow`, `skill: allow`; no `edit`. |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Valid | `name` matches folder; `metadata` is a string-string map. |
| `.opencode/skills/env-conflict/SKILL.md` | Valid | `name` matches folder; metadata values are strings. |
| `.opencode/skills/numpy-serialization/SKILL.md` | Valid | `name` matches folder; metadata values are strings. |
| `AGENTS.md` | N/A | Not an agent/skill frontmatter file; its path and method references are reviewed below. |

No invalid YAML, no `permissions:` plural rulesets, no `shell` permission key, and no `prompt:` frontmatter remain. The Cycle 1 and Cycle 2 schema migrations are present.

### Summary

Status legend: `OK` = no Critical or Major issues; `Needs Fix` = at least one Major issue; `Broken` = at least one Critical issue. `Needs Fix*` means the file has no local Major issue but is affected by cross-file Major X-1.

| File | Status | Critical | Major | Minor | Stylistic/Nitpick |
|---|---|---:|---:|---:|---:|
| `.opencode/agents/agent-reviewer.md` | Needs Fix | 0 | 3 | 1 | 0 |
| `.opencode/agents/data-pipeline.md` | Needs Fix | 0 | 1 | 2 | 0 |
| `.opencode/agents/shape-dtype.md` | Needs Fix* | 0 | 0 | 1 | 0 |
| `.opencode/agents/training-instability.md` | Needs Fix* | 0 | 0 | 1 | 0 |
| `.opencode/agents/work.md` | Needs Fix | 0 | 2 | 6 | 0 |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Needs Fix | 0 | 1 | 3 | 0 |
| `.opencode/skills/env-conflict/SKILL.md` | Needs Fix | 0 | 1 | 3 | 0 |
| `.opencode/skills/numpy-serialization/SKILL.md` | Needs Fix | 0 | 1 | 2 | 0 |
| `AGENTS.md` + cross-file | Needs Fix | 0 | 3 | 8 | 5 |
| **Total** |  | **0** | **12** | **27** | **5** |

### Detailed findings

#### `.opencode/agents/agent-reviewer.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/agent-reviewer.md` | Major | Checklist item 1 defines only **agent** frontmatter. It never states the skill frontmatter contract: `name` required and matching the folder, lowercase/hyphenated and at most 64 chars; `description` required and trigger-oriented; allowed keys are `name`, `description`, `license`, `compatibility`, `metadata`; `metadata` must be a string-string map. The reviewer can therefore approve invalid skill frontmatter. | Split item 1 into "Agent frontmatter" and "Skill frontmatter" subsections and add the skill rules above. |
| `.opencode/agents/agent-reviewer.md` | Major | Inputs only cover `.opencode/agents/**/*.md` and `.opencode/skills/**/SKILL.md`. They omit `config/skills/**/SKILL.md` and any other `**/SKILL.md` location named by `AGENTS.md` and the task. The reviewer's scope is narrower than the harness it is supposed to validate. | Add `config/skills/**/SKILL.md` and a recursive `**/SKILL.md` sweep (excluding vendor directories), or state the canonical skill path explicitly. |
| `.opencode/agents/agent-reviewer.md` | Major | Checklist item 5 does not require checking permission rule order. opencode evaluates the **last matching rule**, so a broad rule placed after a narrow rule can silently negate it. The reviewer may approve a broken permission map. | Add: "Verify order: broad rules first, narrow rules last; the last matching rule wins." |
| `.opencode/agents/agent-reviewer.md` | Minor | Checklist item 1 says file-based agents "must not" set `prompt:` in frontmatter. `prompt` is a valid `AgentConfig` field; the real rule is that the file body becomes the prompt, so duplicating `prompt:` is a convention violation, not a schema violation. The absolute wording can cause false positives. | Change to "should not duplicate the body in `prompt:`" and explain that the body is the prompt. |

#### `.opencode/agents/data-pipeline.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/data-pipeline.md` | Major | The Handoff section says to use `symptom`, `traceback`, `paths`, `expected`, `observed`, `context`, but the output schema has `actual` (not `observed`) and none of those fields. It is unclear whether these are invocation inputs or output fields, so the subagent cannot reliably satisfy the Work contract. | Define a `handoff` object, or map `observed` to `actual`, and state explicitly that the contract fields are invocation inputs supplied by Work. |
| `.opencode/agents/data-pipeline.md` | Minor | Label leakage (section 1) and split overlap (section 6) both check duplicate or near-duplicate rows. The same issue can be reported twice under different categories. | Keep row/group overlap under split overlap; restrict label leakage to target-derived features and duplicate labels. |
| `.opencode/agents/data-pipeline.md` | Minor | `bash: ask` is broad for an agent described as inspect-only; it permits any command after confirmation. | Scope `bash` to read-only commands, or keep `ask` with an explicit "read-only commands only" rule in the Permissions section. |

#### `.opencode/agents/shape-dtype.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/shape-dtype.md` | Minor | `bash: ask` is broad for a tracing agent; dynamic mode executes arbitrary Python after confirmation, which can write or delete files despite `edit: deny`. | Scope execution to a trusted tracer script, or keep `ask` with a clear "trusted code only" rule. |

#### `.opencode/agents/training-instability.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/training-instability.md` | Minor | The `bash` map only allows `tail`, `grep`, and `journalctl`. Common read-only log commands such as `head`, `cat`, `awk`, `sed`, and `wc` are denied, which can block analysis of live or supplied logs. | Add the read-only log commands, or document that the `read` and `grep` tools cover file logs and shell is only for live streams. |

#### `.opencode/agents/work.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/work.md` | Major | The Consolidated Report Schema drops `confidence` and `first_observed_at`, which `training-instability` and `data-pipeline`/`shape-dtype` emit. Uncertainty and first-observation information are lost during consolidation. | Add optional `confidence` and `first_observed_at` to each finding, or map them into `root_cause_chain`/`evidence`. |
| `.opencode/agents/work.md` | Major | Workflow step 2 routes only to subagents via the Task tool. Skill Routing is a separate section and is not part of the numbered workflow, so the primary agent may never invoke the three skills. | Add a workflow step: "If a skill trigger matches, invoke the skill tool before or alongside subagents." |
| `.opencode/agents/work.md` | Minor | `missing_coverage` only lists subagents. Skills can fail, time out, or return nothing too. | Allow `skill:<name>` entries in `missing_coverage`. |
| `.opencode/agents/work.md` | Minor | Purpose says "ML training debugging", but Skill Routing includes deployment/CI and environment failures. The stated scope is narrower than the actual routing. | Broaden the purpose, or label skills as adjacent escalation paths outside the ML training core. |
| `.opencode/agents/work.md` | Minor | `webfetch: ask` and `websearch: ask` are not used by the stated workflow. | Set to `deny` unless web lookup is an intended capability. |
| `.opencode/agents/work.md` | Minor | There is no explicit instruction to request missing required inputs; "clarify scope" is vague. | Add: "Ask for symptom, traceback, paths, expected, observed, and context when missing." |
| `.opencode/agents/work.md` | Minor | Consolidated `category` is a free string, while subagents use enums. The consolidated report can contain inconsistent category names. | Define allowed categories, or state that `category` is copied verbatim from the source subagent. |
| `.opencode/agents/work.md` | Minor | No `external_directory` permission is declared; behavior for paths outside the workspace is unspecified. | Add `external_directory: ask` or `deny` and document the choice. |

#### `.opencode/skills/deploy-troubleshoot/SKILL.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Major | No safety or confirmation guidance is given for state-changing fixes. The example runs `kubectl set resources` and `kubectl set env`, which can restart or modify production workloads. | Add "confirm before applying; prefer read-only diagnostics and dry runs first." |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Minor | The example root cause "incorrect environment variable configuration" has no supporting evidence in `log_excerpt`. | Add evidence for that cause or remove it from the example. |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Minor | The Output section defines `healthy`, but the example only shows a failure case. | Add a short healthy example, or state that `healthy` is used only when no issues are found. |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Minor | Failure Handling covers a missing `Platform` but not a missing `RecentChanges`. | Add a fallback for missing or irrelevant `RecentChanges`. |

#### `.opencode/skills/env-conflict/SKILL.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/skills/env-conflict/SKILL.md` | Major | The sample table is logically inconsistent: `torch` is required at 2.1.0 and installed at 2.1.0 but marked `conflict`, while the stated `torchvision` requirement `torch<2.2` is satisfied by 2.1.0. | Change installed `torch` to 2.2.x, or change the requirement to `torch>=2.2`, and show the actual `pip check` evidence. |
| `.opencode/skills/env-conflict/SKILL.md` | Minor | There is no explicit Failure Handling section for pip/conda unavailable, permission denied, or multiple conflicting manifests. | Add a Failure Handling section covering those cases. |
| `.opencode/skills/env-conflict/SKILL.md` | Minor | Workflow says to check `sys.executable` but gives no command. | Add `python -c "import sys; print(sys.executable)"`. |
| `.opencode/skills/env-conflict/SKILL.md` | Minor | No safety note for `pip install` modifying the environment. | Add "prefer a virtual environment; confirm before installing or upgrading." |

#### `.opencode/skills/numpy-serialization/SKILL.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/skills/numpy-serialization/SKILL.md` | Major | The description and "What it does" claim diagnosis of dtype/shape errors, but the error table correctly says shape errors are assignment errors that occur before serialization. The trigger overpromises and can invoke the skill for non-serialization errors. | Narrow the description to serialization errors, or explicitly say shape errors are usually pre-serialization and out of scope. |
| `.opencode/skills/numpy-serialization/SKILL.md` | Minor | The error table lacks rows for `ValueError: Cannot load file containing pickled data when allow_pickle=False` and `OSError: Failed to interpret file ... as a pickle`. | Add those rows with the `allow_pickle`/trusted-file fix. |
| `.opencode/skills/numpy-serialization/SKILL.md` | Minor | There is no workflow step to inspect `array.dtype` and `array.shape` before saving. | Add `print(array.dtype, array.shape)` to the diagnostic workflow. |

### Cross-file and `AGENTS.md` findings

| File / scope | Severity | Issue | Suggested fix |
|---|---|---|---|
| `AGENTS.md` lines 3 and 117 | Major | The harness says skills live in `config/skills/` and `config/skills/*/SKILL.md`, but the actual path is `.opencode/skills/`. The harness points at a non-existent directory. | Replace both references with `.opencode/skills/` and `.opencode/skills/*/SKILL.md`. |
| `AGENTS.md` line 33 | Major | The expected output says "`np.save`/`np.load` for `.npy`/`.npz`". `.npz` archives are written with `np.savez`/`np.savez_compressed`, not `np.save`. This contradicts the numpy skill. | Correct to "`np.save` for `.npy`; `np.savez` for `.npz`; `np.load` for both." |
| All agents — `first_observed_at` | Major | `first_observed_at` has three incompatible meanings: `data-pipeline` uses a stage enum (`split`/`preprocessing`/`training_step`), `shape-dtype` uses a layer/module name, and `training-instability` uses free-text step/epoch. The field cannot be consolidated reliably. | Define one shared finding envelope: `first_observed_at` = time/step; `location` = layer/stage. Update all agents. |
| Subagent handoff sections | Minor | `data-pipeline` has an explicit Handoff section; `shape-dtype` and `training-instability` only mention the Work Agent in Integration Notes. Handoff behavior is inconsistent. | Add a Handoff section to every subagent, or remove the data-pipeline-only contract. |
| All five agents — least privilege | Minor | None of the agents deny `todowrite` or `question`, even though the workflows do not require them. | Add `todowrite: deny` and `question: deny` to `agent-reviewer`, `data-pipeline`, `shape-dtype`, `training-instability`, and `work`. |
| `AGENTS.md` lines 19 and 26 | Minor | Line 19 lists `pickle` as a NumPy function; it is a separate Python module. Line 26 uses `ValueError: setting an array element with a incompatible shape`, which is an array-assignment error, not an `np.save`/`np.load` error, and has a grammar error. | Separate `pickle` from NumPy; replace the example with a real serialization error and fix "a incompatible". |
| `AGENTS.md` | Minor | The harness never mentions `.opencode/agents/` or the agent roster, so `work.md` and `agent-reviewer` are not discoverable from the root instructions. | Add an "Agents" section pointing to `.opencode/agents/` and `work.md`. |
| `AGENTS.md` | Minor | It claims each skill follows the Single Responsibility Principle, but `deploy-troubleshoot` overlaps `env-conflict` on config/environment failures. | Clarify the boundary (deployment runtime config vs Python package environment) or drop the SRP claim. |
| `AGENTS.md` vs `work.md` | Minor | `AGENTS.md` defines a priority order (env-conflict → numpy-serialization → deploy-troubleshoot), but `work.md` Skill Routing does not mention it. | Add the priority order to `work.md`, or have it reference `AGENTS.md`. |
| `AGENTS.md` vs `env-conflict` | Minor | The harness expected output table is `[package, required version, installed version, fix suggestion]`, omitting the `status` column that the skill's output includes. | Add `status` to the harness table or state that it is optional. |
| All three skills — metadata | Minor | `metadata.role`, `metadata.capabilities`, and `metadata.priority` duplicate the skill name/description and are not consumed by opencode. `deploy-troubleshoot` sets `priority: "high"` while `AGENTS.md` places it last. | Remove the redundant metadata, or align `priority` with the harness order. |
| `data-pipeline`, `shape-dtype`, `training-instability` — `## Config` | Stylistic/Nitpick | Each `## Config` section only restates `steps` and adds no configuration guidance. | Remove the sections or document real configuration assumptions. |
| All three `SKILL.md` files | Stylistic/Nitpick | All three use "When to provoke it", which is awkward. | Rename to "When to use it". |
| `.opencode/agents/work.md` | Stylistic/Nitpick | The roster uses `@data-pipeline`, `@shape-dtype`, and `@training-instability` in prose. `@` is TUI mention syntax. | Use backticks or plain names in prose and keep Task-tool invocation explicit. |
| `AGENTS.md` line 117 | Stylistic/Nitpick | "use this harness" reads as if the harness executes; the harness is documentation. | Reword to "follow this harness" or "apply these rules". |
| `.opencode/skills/numpy-serialization/SKILL.md` | Stylistic/Nitpick | Inputs says "storage scenario (disk/transfer/storage)"; "storage" is repeated. | Reword to "disk, transfer, or long-term storage". |

### Out-of-scope observations

- `test-agent/pipeline.md`, `test-agent/shape.md`, and `test-agent/training.md` are review logs, not agent or skill definitions. They contain stale claims about `permissions:` rulesets and `shell` allow/deny that no longer match the current frontmatter. Archive them or update them if they are kept as documentation.
- `frontend/index.html` is not an agent or skill file and was not reviewed.
- No supporting skill files exist (`references/` or `scripts/`), so there are no broken script or reference paths to report.

### Positive checks

- All eight agent/skill frontmatter blocks parse as valid YAML and use valid opencode fields.
- All five agents use the singular `permission` map and the `bash` key; no `permissions:` ruleset or `shell` key remains.
- All three skill `name` values match their folder names, and all `metadata` values are strings.
- All three skill descriptions front-load trigger keywords and include "Use when..." guidance.
- All `@` agent references in `work.md` resolve to existing agent files.
- All skill names referenced by `AGENTS.md` exist under `.opencode/skills/`.
- The previously broken `np.load("array.npy.npy")` example is fixed; the `.npz` example uses `np.savez` and `np.load`.
- The `allow_pickle=False` security warning is present.
- Failure handling exists in seven of eight files; `env-conflict` is the only one without a dedicated Failure Handling section.
- No Critical issues remain.

### Severity counts

| Severity | Count |
|---|---:|
| Critical | 0 |
| Major | 12 |
| Minor | 27 |
| Stylistic/Nitpick | 5 |
| **Total** | **44** |

### Overall verdict

Cycle 3 is **not clean**, but it has no Critical issues. The permission schema migrations from Cycles 1 and 2 are complete: every agent uses the singular `permission` map and the `bash` key, and every skill has valid frontmatter with trigger-oriented descriptions.

The remaining Major issues are contract and safety problems rather than schema failures:

1. `agent-reviewer` cannot fully validate skill frontmatter, does not scan every skill location, and does not check permission rule order.
2. `work` drops `confidence` and `first_observed_at` during consolidation and does not invoke skills in its numbered workflow.
3. `deploy-troubleshoot` gives state-changing `kubectl` fixes without a confirmation or dry-run rule.
4. `env-conflict` has a logically impossible conflict example.
5. `numpy-serialization` overpromises shape-error diagnosis.
6. `AGENTS.md` points to `config/skills/` instead of `.opencode/skills/` and repeats the wrong `.npz` method mapping.
7. `first_observed_at` has incompatible semantics across the three diagnostic subagents.

Fix the 12 Major issues first, then the Minor contract and example inconsistencies. Restart opencode after any agent/skill/AGENTS.md change; configuration is not hot-reloaded.

### Fixes applied

- **Critical:** none listed in Cycle 3, so none to fix.
- **Major — agent-reviewer checklist defines only agent frontmatter:** `.opencode/agents/agent-reviewer.md` — split item 1 into "Agent frontmatter" and "Skill frontmatter" and added the skill contract (`name` matches folder, allowed keys, string-string `metadata`).
- **Major — agent-reviewer Inputs omit `config/skills/**/SKILL.md` and other `**/SKILL.md` locations:** `.opencode/agents/agent-reviewer.md` — added `config/skills/**/SKILL.md` and a recursive `**/SKILL.md` sweep (excluding vendor directories).
- **Major — agent-reviewer does not check permission rule order:** `.opencode/agents/agent-reviewer.md` — item 5 now requires broad rules first, narrow rules last, because the last matching rule wins.
- **Major — data-pipeline Handoff fields do not match its output schema:** `.opencode/agents/data-pipeline.md` — stated that `symptom`/`traceback`/`paths`/`expected`/`observed`/`context` are Work-supplied invocation inputs and mapped `observed` to output `actual`.
- **Major — work Consolidated Report Schema drops `confidence` and `first_observed_at`:** `.opencode/agents/work.md` — added optional `confidence` and `first_observed_at` to the schema and example report.
- **Major — work Skill Routing is outside the numbered workflow:** `.opencode/agents/work.md` — added workflow step 2 to invoke the skill tool before or alongside subagents.
- **Major — deploy-troubleshoot has no safety/confirmation guidance for state-changing fixes:** `.opencode/skills/deploy-troubleshoot/SKILL.md` — added a Safety section (confirm first, prefer read-only diagnostics and `--dry-run=server`) and a dry-run step in the example.
- **Major — env-conflict sample table is logically inconsistent:** `.opencode/skills/env-conflict/SKILL.md` — changed installed `torch` to 2.2.1 and added the `pip check`-based downgrade fix.
- **Major — numpy-serialization overpromises dtype/shape diagnosis:** `.opencode/skills/numpy-serialization/SKILL.md` — narrowed the description, "What it does", and trigger to serialization errors and marked pre-serialization shape errors out of scope.
- **Major — `first_observed_at` has incompatible semantics across subagents:** `.opencode/agents/data-pipeline.md`, `.opencode/agents/shape-dtype.md`, `.opencode/agents/training-instability.md` — defined `first_observed_at` as time/step and kept layer/stage in `location`, updating schemas and examples.
- **Minor — agent-reviewer says file-based agents "must not" set `prompt:`:** `.opencode/agents/agent-reviewer.md` — reworded to "should not duplicate the body in `prompt:`; the file body is the prompt".
- **Minor — data-pipeline label leakage duplicates split-overlap checks:** `.opencode/agents/data-pipeline.md` — removed the duplicate-row bullet from label leakage and pointed row/group overlap to Split overlap.
- **Minor — data-pipeline `bash: ask` is broad:** `.opencode/agents/data-pipeline.md` — added a read-only-only command rule under Permissions.
- **Minor — shape-dtype `bash: ask` is broad:** `.opencode/agents/shape-dtype.md` — added a trusted-tracing-code-only rule under Permissions.
- **Minor — training-instability `bash` map denies common read-only log commands:** `.opencode/agents/training-instability.md` — added `head`, `cat`, `awk`, `sed`, and `wc` as `ask` after the broad deny.
- **Minor — work `missing_coverage` only lists subagents:** `.opencode/agents/work.md` — allowed `skill:<name>` entries.
- **Minor — work Purpose is narrower than its skill routing:** `.opencode/agents/work.md` — labeled environment/deployment failures as adjacent escalation paths via skills.
- **Minor — work declares unused `webfetch`/`websearch: ask`:** `.opencode/agents/work.md` — set both to `deny`.
- **Minor — work does not explicitly request missing inputs:** `.opencode/agents/work.md` — workflow step 1 now asks for the six handoff fields when missing.
- **Minor — work `category` is a free string:** `.opencode/agents/work.md` — added that `category` is copied verbatim from the source subagent or skill.
- **Minor — work has no `external_directory` permission:** `.opencode/agents/work.md` — added `external_directory: deny` and documented it under Non-Goals.
- **Minor — deploy-troubleshoot example root cause lacks log evidence:** `.opencode/skills/deploy-troubleshoot/SKILL.md` — removed the unsupported env-var cause and its `kubectl set env` fix.
- **Minor — deploy-troubleshoot defines `healthy` but only shows a failure example:** `.opencode/skills/deploy-troubleshoot/SKILL.md` — added that `healthy` is used only when no issues are found.
- **Minor — deploy-troubleshoot Failure Handling omits missing `RecentChanges`:** `.opencode/skills/deploy-troubleshoot/SKILL.md` — added a log-only fallback bullet.
- **Minor — env-conflict has no Failure Handling section:** `.opencode/skills/env-conflict/SKILL.md` — added handling for unavailable pip/conda, permission denial, and conflicting manifests.
- **Minor — env-conflict mentions `sys.executable` without a command:** `.opencode/skills/env-conflict/SKILL.md` — added `python -c "import sys; print(sys.executable)"` to step 6.
- **Minor — env-conflict has no safety note for `pip install`:** `.opencode/skills/env-conflict/SKILL.md` — added a Safety section (prefer a virtual environment, confirm before installing/upgrading).
- **Minor — numpy-serialization error table lacks `allow_pickle` load errors:** `.opencode/skills/numpy-serialization/SKILL.md` — added rows for `Cannot load file containing pickled data` and `Failed to interpret file ... as a pickle`.
- **Minor — numpy-serialization has no dtype/shape inspection step:** `.opencode/skills/numpy-serialization/SKILL.md` — added `print(array.dtype, array.shape)` as workflow step 1.
- **Minor — subagent handoff sections are inconsistent:** `.opencode/agents/shape-dtype.md`, `.opencode/agents/training-instability.md` — added the same Handoff section used by data-pipeline; `.opencode/agents/data-pipeline.md` — clarified its existing section.
- **Minor — no agent denies `todowrite`/`question`:** `.opencode/agents/agent-reviewer.md`, `.opencode/agents/data-pipeline.md`, `.opencode/agents/shape-dtype.md`, `.opencode/agents/training-instability.md`, `.opencode/agents/work.md` — added `todowrite: deny` and `question: deny`.
- **Minor — work Skill Routing omits the harness priority order:** `.opencode/agents/work.md` — added `env-conflict` → `numpy-serialization` → `deploy-troubleshoot`.
- **Minor — redundant skill `metadata`:** `.opencode/skills/deploy-troubleshoot/SKILL.md`, `.opencode/skills/env-conflict/SKILL.md`, `.opencode/skills/numpy-serialization/SKILL.md` — removed the redundant `metadata` blocks.

### Skipped

- **Major — `AGENTS.md` lines 3 and 117 point to `config/skills/`:** skipped because `AGENTS.md` is outside the instructed scope (`.opencode/agents` and skill folders).
- **Major — `AGENTS.md` line 33 maps `.npz` to `np.save`:** skipped for the same out-of-scope reason.
- **Minor — `AGENTS.md` lines 19 and 26 (pickle listed as NumPy, bad error example/grammar):** skipped because `AGENTS.md` is out of scope.
- **Minor — `AGENTS.md` omits the agent roster:** skipped because `AGENTS.md` is out of scope.
- **Minor — `AGENTS.md` Single Responsibility Principle claim:** skipped because `AGENTS.md` is out of scope.
- **Minor — `AGENTS.md` vs `env-conflict` output table lacks `status`:** skipped because the fix would require editing out-of-scope `AGENTS.md`.
- **Stylistic/Nitpick — all 5 items:** skipped because only Critical, Major, and Minor fixes were requested.

### Verification

- All eight agent/skill frontmatter blocks parse as valid YAML.
- All JSON code blocks in the agents and skills parse as valid JSON.
- No files outside `.opencode/agents` and `.opencode/skills` were edited.

## Cycle 4 — 2026-11-08

**Model used:** `opencode/deepseek-v4.1-flash-free` · **Reviewer agent:** `agent-reviewer` · **Cycle:** 4 · **Mode:** read-only
**Schema sources:** `https://opencode.ai/config.json` (fetched) and the built-in `customize-opencode` skill.
**No files were modified.**

---

### 1. Scope and files reviewed

| # | Path | Kind | Notes |
|---:|---|---|---|
| 1 | `.opencode/agents/agent-reviewer.md` | Agent — subagent | Standalone meta-reviewer; not in `work.md` roster |
| 2 | `.opencode/agents/data-pipeline.md` | Agent — subagent | ML diagnostic subagent |
| 3 | `.opencode/agents/shape-dtype.md` | Agent — subagent | ML diagnostic subagent |
| 4 | `.opencode/agents/training-instability.md` | Agent — subagent | ML diagnostic subagent |
| 5 | `.opencode/agents/work.md` | Agent — primary | Primary router/consolidator |
| 6 | `.opencode/skills/deploy-troubleshoot/SKILL.md` | Skill | Deployment log analysis |
| 7 | `.opencode/skills/env-conflict/SKILL.md` | Skill | Python environment/import diagnosis |
| 8 | `.opencode/skills/numpy-serialization/SKILL.md` | Skill | NumPy serialization diagnosis |
| 9 | `AGENTS.md` | Harness reference | Reviewed for cross-file consistency only |

There is no `config/skills/` directory and no `references/` or `scripts/` directory under any skill. The only skill definitions are under `.opencode/skills/`.

---

### 2. Frontmatter validation

| File | Result | Mode / skill name | Permission shape | Deprecated keys | Notes |
|---|---|---|---|---|---|
| `.opencode/agents/agent-reviewer.md` | Valid | `mode: subagent` | Singular `permission` map; `bash: deny`; read-only tools allowed | None in frontmatter | Body text *describes* deprecated `tools`/`maxSteps`, but does not use them |
| `.opencode/agents/data-pipeline.md` | Valid | `mode: subagent` | Singular `permission` map; `bash: ask` | None | `steps: 12` valid |
| `.opencode/agents/shape-dtype.md` | Valid | `mode: subagent` | Singular `permission` map; `bash: ask` | None | `steps: 12` valid |
| `.opencode/agents/training-instability.md` | Valid | `mode: subagent` | Singular `permission` map; `bash` object with broad `"*": deny` first, narrow `ask` rules last | None | Rule order is correct for “last matching rule wins” |
| `.opencode/agents/work.md` | Valid | `mode: primary` | Singular `permission` map; `bash: ask`; `task: allow`; `skill: allow` | None | `external_directory: deny`, `webfetch`/`websearch: deny` |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Valid | `name: deploy-troubleshoot` matches folder | N/A | None | Description is trigger-oriented; no `metadata` block (optional) |
| `.opencode/skills/env-conflict/SKILL.md` | Valid | `name: env-conflict` matches folder | N/A | None | No `metadata` block; no string-string violation |
| `.opencode/skills/numpy-serialization/SKILL.md` | Valid | `name: numpy-serialization` matches folder | N/A | None | No `metadata` block; no string-string violation |
| `AGENTS.md` | N/A | N/A | N/A | N/A | Not an agent/skill frontmatter file |

**Frontmatter conclusions:** all five agents use the singular `permission` map and the `bash` key. No file uses `permissions:` plural, `shell`, `tools`, `maxSteps`, or `prompt:` frontmatter. All three skill names are lowercase, hyphenated, under 64 characters, and match their folder names. No skill has an invalid top-level frontmatter key or a non-string `metadata` value.

> Schema nuance: `Config.AgentEncoded` in `opencode.json` accepts a plural `permissions` ruleset, but that shape does **not** apply to markdown agent frontmatter. Markdown agents use `AgentConfig.permission` (singular). None of the reviewed markdown files uses the `opencode.json` ruleset shape.

---

### 3. Summary table

Status legend: `OK` = no Critical or Major issues; `Needs Fix` = at least one Major; `Broken` = at least one Critical.

| File | Status | Critical | Major | Minor | Stylistic/Nitpick |
|---|---|---:|---:|---:|---:|
| `.opencode/agents/agent-reviewer.md` | Needs Fix | 0 | 1 | 2 | 0 |
| `.opencode/agents/data-pipeline.md` | OK | 0 | 0 | 3 | 1 |
| `.opencode/agents/shape-dtype.md` | Needs Fix | 0 | 1 | 3 | 1 |
| `.opencode/agents/training-instability.md` | OK | 0 | 0 | 3 | 1 |
| `.opencode/agents/work.md` | Needs Fix | 0 | 2 | 4 | 1 |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | OK | 0 | 0 | 2 | 1 |
| `.opencode/skills/env-conflict/SKILL.md` | OK | 0 | 0 | 2 | 1 |
| `.opencode/skills/numpy-serialization/SKILL.md` | OK | 0 | 0 | 2 | 1 |
| **Subtotal — agent/skill files** |  | **0** | **4** | **21** | **7** |
| `AGENTS.md` + cross-file (unique) | Needs Fix | 0 | 3 | 6 | 2 |
| **TOTAL** |  | **0** | **7** | **27** | **9** |

---

### 4. Per-file detailed findings

#### 4.1 `.opencode/agents/agent-reviewer.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/agent-reviewer.md` | Major | Checklist item 1 lists allowed agent fields as `name, model, ...` “plus deprecated `tools` and `maxSteps`.” This treats deprecated keys as allowable and lists `name`, which is not a canonical file-agent field because the filename supplies the agent name. A reviewer following this checklist may approve non-compliant frontmatter, contrary to the “no deprecated keys” requirement. | List only current `AgentConfig` fields; add an explicit rule that `tools`/`maxSteps` are deprecated and must be reported; state that file agents derive `name` from the filename. |
| `.opencode/agents/agent-reviewer.md` | Minor | Inputs include `config/skills/**/SKILL.md`, but no `config/skills/` directory exists. The agent’s own missing-input rule will therefore emit a false positive on every review. | Use `.opencode/skills/**/SKILL.md` as the canonical path, or label `config/skills/` as optional/legacy and suppress missing-input findings for it. |
| `.opencode/agents/agent-reviewer.md` | Minor | Output format defines summary, per-file details, and counts only. Although `AGENTS.md` is an input, the format does not require a frontmatter-validation table, cross-file/AGENTS findings, positive checks, or an overall verdict. | Add those sections to the output template and require a full scope inventory. |

#### 4.2 `.opencode/agents/data-pipeline.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/data-pipeline.md` | Minor | `bash: ask` is a flat permission for every command. An approved `python -c` command or shell write can mutate files despite `edit: deny`. The body says “read-only,” but the permission does not enforce it. | Scope `bash` to read-only commands with a broad `"*": deny` first, or add a dedicated read-only inspector script. If `ask` remains, state that user approval is the only guard. |
| `.opencode/agents/data-pipeline.md` | Minor | No explicit `skill` or `external_directory` permission. Least privilege depends on inherited/default behavior, while `work.md` declares `external_directory: deny`. | Add `skill: deny` and `external_directory: deny` unless this subagent genuinely needs them, and document inheritance behavior. |
| `.opencode/agents/data-pipeline.md` | Minor | Integration Notes say it “should run early … before the Training Instability Agent,” but `work.md` has no ordering rule that enforces this. The recommendation can be skipped during routing. | Encode the ordering in `work.md`, or rephrase this as a recommendation rather than an expected sequence. |
| `.opencode/agents/data-pipeline.md` | Stylistic/Nitpick | The `## Config` section only restates `steps` and adds no configuration guidance. | Remove it or document real configuration assumptions. |

#### 4.3 `.opencode/agents/shape-dtype.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/shape-dtype.md` | Major | Failure Handling says to report an unparseable model, unsupported framework, or failed forward pass “in `unresolved` and a finding message,” but the finding `category` enum has no failure or `unable_to_inspect` value. The failure cannot be represented without inventing an out-of-enum category. | Add `unable_to_inspect` (or `trace_failed`) to the enum and example, or state that failures are returned only through `unresolved` and `confidence: "low"` with no finding object. |
| `.opencode/agents/shape-dtype.md` | Minor | `confidence` is top-level, and `shape_trace`/`unresolved` are extra envelope fields. `work.md` expects per-finding `confidence` and has no `shape_trace`/`unresolved` fields, so trace detail is lost during consolidation. | Add optional `shape_trace`/`unresolved` to the Work schema, map top-level confidence into each finding, or define an explicit merge rule. |
| `.opencode/agents/shape-dtype.md` | Minor | `bash: ask` permits any command after confirmation. Dynamic tracing runs unsandboxed Python, which can write or delete files despite `edit: deny`. The trusted-code note is guidance, not enforcement. | Scope execution to a trusted tracer command or keep `ask` with an explicit approved-command list and a “trusted code only” rule. |
| `.opencode/agents/shape-dtype.md` | Minor | No explicit `skill` or `external_directory` denies. Least privilege is incomplete relative to `work.md`. | Add `skill: deny` and `external_directory: deny` unless needed. |
| `.opencode/agents/shape-dtype.md` | Stylistic/Nitpick | The `## Config` section only restates `steps`. | Remove it or document real configuration assumptions. |

#### 4.4 `.opencode/agents/training-instability.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/training-instability.md` | Minor | Failure Handling covers missing gradient norms and activation statistics, but not a missing or unreadable log path, even though “supplied logs or log paths” is a primary input. | Add an `unable_to_inspect`/`log_unavailable` fallback containing the path and underlying error, and continue with any readable inputs. |
| `.opencode/agents/training-instability.md` | Minor | No explicit `skill` or `external_directory` denies. | Add `skill: deny` and `external_directory: deny` unless the workflow requires them. |
| `.opencode/agents/training-instability.md` | Minor | The `bash` map allows `cat *`, `sed *`, and `awk *` after confirmation. `sed -i` can modify files, and `cat` can read arbitrary paths; this is broader than log analysis. The broad deny first is correct, but the narrow rules are still wide. | Restrict rules to read-only forms/arguments and log paths, or document that only read-only log operations are approved. |
| `.opencode/agents/training-instability.md` | Stylistic/Nitpick | The `## Config` section only restates `steps`. | Remove it or document real configuration assumptions. |

#### 4.5 `.opencode/agents/work.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/agents/work.md` | Major | Skill Routing assigns `np.save`/`np.load`/`np.savez` failures including `dtype/shape` to `numpy-serialization`, but that skill explicitly says shape errors occur before serialization and are out of scope. Shape errors will be misrouted to a skill that will not diagnose them. | Remove `shape` from the `numpy-serialization` trigger; route `shape_mismatch` findings to `shape-dtype` or `data-pipeline`, and keep dtype/endianness with the NumPy skill. |
| `.opencode/agents/work.md` | Major | The Consolidated Report Schema says `category` is “copied verbatim from the source subagent or skill,” but no skill output defines `category`. `deploy-troubleshoot` emits `root_causes`/`fixes`/`checklist`/`healthy`; `env-conflict` emits a table/`required_version_source`/`fallback`; `numpy-serialization` emits a table/`method`/`snippet`. Skill-originated findings cannot populate the required schema. | Define a skill→finding mapping (for example `deployment`, `environment`, `serialization`) or extend each skill’s output contract with `category`/`severity`. Alternatively allow `category: null` for skill sources with evidence in `root_cause_chain`. |
| `.opencode/agents/work.md` | Minor | Failure Handling covers subagent errors, timeouts, and empty results, but not skill errors, timeouts, or empty results, even though `missing_coverage` accepts `skill:<name>`. | Add an explicit skill-failure rule that records `skill:<name>` in `missing_coverage` and continues with available findings. |
| `.opencode/agents/work.md` | Minor | The Handoff Contract says “Every subagent invocation” must include six fields. `agent-reviewer` is a subagent with a different input contract and is intentionally outside the roster. The rule is overbroad. | Change to “every ML diagnostic subagent invocation” and reference the roster. |
| `.opencode/agents/work.md` | Minor | The consolidated schema has no `shape_trace`, `unresolved`, or top-level confidence field, while `shape-dtype` emits all three. Trace detail and unresolved layers are dropped. | Add optional `shape_trace`/`unresolved` fields or define how they fold into `evidence` and `root_cause_chain`. |
| `.opencode/agents/work.md` | Minor | `bash: ask` is broad. Non-Goals says the agent does not retrain, but any command can be approved by the user; confirmation is the only guard. | Scope `bash` to diagnostic commands, or keep `ask` and explicitly require per-command approval for state-changing commands (already partly stated) with examples. |
| `.opencode/agents/work.md` | Stylistic/Nitpick | The Subagent Roster uses `@data-pipeline`, `@shape-dtype`, and `@training-instability` in prose. `@` is TUI mention syntax. | Use backticks or plain names in prose and keep Task-tool invocation explicit. |

#### 4.6 `.opencode/skills/deploy-troubleshoot/SKILL.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Minor | Failure Handling says to return “insufficient log data,” but the Output section has no field or shape for that result. It may be emitted as unstructured text. | Add an `error`/`status` field for unparseable input, or state that it is a plain-text response outside the normal output object. |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Minor | `healthy` is textual and the example shows only a failure case; the healthy-case output shape is not demonstrated. | Add a short healthy example or define the exact healthy response object. |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Stylistic/Nitpick | “When to provoke it” is awkward wording. | Rename to “When to use it.” |

#### 4.7 `.opencode/skills/env-conflict/SKILL.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/skills/env-conflict/SKILL.md` | Minor | Workflow step 1 uses `which python`. On systems with only `python3`, this fails and can misdiagnose the environment. | Use `command -v python3 || command -v python`, then use the resolved executable consistently. |
| `.opencode/skills/env-conflict/SKILL.md` | Minor | The sample table omits `required_version_source`; the `torch<2.2` constraint appears only in prose, so the source of the “required” version is unclear. | Add a source column/row or explicitly reference the manifest or `pip check` output that supplied the constraint. |
| `.opencode/skills/env-conflict/SKILL.md` | Stylistic/Nitpick | “When to provoke it” is awkward wording. | Rename to “When to use it.” |

#### 4.8 `.opencode/skills/numpy-serialization/SKILL.md`

| File | Severity | Issue | Suggested fix |
|---|---|---|---|
| `.opencode/skills/numpy-serialization/SKILL.md` | Minor | Workflow step 1 inspects `array.dtype` and `array.shape` before saving, but the skill is triggered by an existing save/load error. This preventive step is out of diagnostic order. | Move it to a “prevention” note or run it after extracting the error; keep error extraction and matching first. |
| `.opencode/skills/numpy-serialization/SKILL.md` | Minor | The Output section promises an error → cause → code-change table, but the examples show only save/load snippets; no sample error table is provided. | Add a small sample error/cause/fix table matching the Output contract. |
| `.opencode/skills/numpy-serialization/SKILL.md` | Stylistic/Nitpick | Inputs says “storage scenario (disk/transfer/storage)”; “storage” is repeated. | Reword to “disk, transfer, or long-term storage.” |

---

### 5. Cross-file and `AGENTS.md` findings

> Work’s own Major findings (`W1`/`W2`) are cross-file in effect but are counted under `work.md` above to avoid double counting. The table below contains unique `AGENTS.md`/systemic issues not counted elsewhere.

| File / scope | Severity | Issue | Suggested fix |
|---|---|---|---|
| `AGENTS.md` lines 3 and 117 | Major | The harness says skills live in `config/skills/` and `config/skills/*/SKILL.md`, but the actual path is `.opencode/skills/`. The harness points at a non-existent directory. | Replace both references with `.opencode/skills/` and `.opencode/skills/*/SKILL.md`. |
| `AGENTS.md` line 33 | Major | The expected output says “`np.save`/`np.load` for `.npy`/`.npz`.” `.npz` archives are written with `np.savez`/`np.savez_compressed`, not `np.save`. This contradicts the NumPy skill. | Correct to “`np.save` for `.npy`; `np.savez` for `.npz`; `np.load` for both.” |
| `AGENTS.md` lines 8–29 | Major | The canonical NumPy invocation example uses `ValueError: setting an array element with a incompatible shape`, which is an array-assignment error that the NumPy skill explicitly marks out of scope. The grammar is also wrong (“a incompatible”). The trigger “or wants to store arrays” is broader than the skill’s error-oriented trigger. | Replace the example with a real serialization error (for example `allow_pickle=False` on an object array, or a doubled `.npy` `FileNotFoundError`); fix “an incompatible”; clarify the storage-only trigger. |
| `AGENTS.md` line 105 | Minor | Harness Workflow step 4 says “Apply the skill’s output to fix the issue.” This conflicts with `work.md`’s Non-Goals (“does not fix code or retrain automatically”) and with the skills’ confirm-before-changing safety rules. | Reword to “prepare the recommended fix and apply it only after user confirmation” or “route the suggested fix to the user.” |
| `AGENTS.md` line 119 | Minor | It claims every skill maintains the Single Responsibility Principle, but `deploy-troubleshoot` classifies config/env failures that can overlap `env-conflict`. The boundary is not stated. | Clarify the boundary (deployment runtime/config vs Python package environment), or soften the absolute SRP claim. |
| `AGENTS.md` line 63 | Minor | The expected `env-conflict` output table is `[package, required version, installed version, fix suggestion]`, omitting `status` and `required_version_source`, which the skill now emits. | Add `status` and `required_version_source` or state that they are optional additions. |
| `AGENTS.md` line 19 | Minor | Lists `pickle` as a NumPy function. It is a separate Python module. | Separate `pickle` from NumPy calls; keep `np.save`/`np.load`/`np.savez` as the NumPy functions. |
| `AGENTS.md` | Minor | The harness never mentions `.opencode/agents/`, the agent roster, or `agent-reviewer`, so the primary workflow and the meta-reviewer are not discoverable from the root instructions. | Add an “Agents” section pointing to `.opencode/agents/` and `work.md`, or state explicitly that this harness covers skills only. |
| `AGENTS.md` line 96 vs deploy skill Output | Minor | The harness calls the deployment result a “next-steps checklist,” while the skill output contract names the field `checklist`. | Align the field name to `checklist`. |
| `AGENTS.md` line 102 | Stylistic/Nitpick | “(serialization/env/ deployment)” has a stray space after the slash. | Change to “(serialization/env/deployment).” |
| `AGENTS.md` line 117 | Stylistic/Nitpick | “Do not modify the skill files … use this harness” reads as if the harness executes or applies edits; it is documentation. | Reword to “follow this harness” or “apply these invocation rules.” |

#### Systemic note

All three ML diagnostic subagents omit explicit `skill` and `external_directory` permissions. This is counted per file (`D2`, `S4`, `T2`). `work.md` declares `external_directory: deny`, but its child agents do not, so the primary’s workspace-confinement claim is not obviously inherited by its subagents. If opencode does not propagate the primary’s permission map, this is a least-privilege gap worth closing explicitly.

---

### 6. Out-of-scope observations

- `REVIEW_LOG.md` is historical review documentation, not an agent or skill definition. It was used only for context and was not counted as a reviewed deliverable. It contains older issue counts that do not match Cycle 4.
- `frontend/index.html` is not an agent or skill file and was not reviewed.
- `.opencode/.gitignore` was not reviewed.
- No `config/skills/`, `references/`, or `scripts/` directories exist, so there are no broken script or reference paths to report.
- The `customize-opencode` skill lists `name` among allowed agent fields, while the fetched JSON Schema’s `AgentConfig` does not list `name` (the filename supplies it). This is a documentation nuance; no current agent uses `name` in frontmatter.
- The plural `permissions` ruleset in `Config.AgentEncoded` applies to inline `opencode.json` agents, not markdown agent frontmatter. No reviewed markdown file uses that shape.

---

### 7. Positive checks

- All five agent files use the singular `permission` map and the `bash` key.
- No agent frontmatter uses deprecated `tools`, deprecated `maxSteps`, plural `permissions`, `shell`, or `prompt:`.
- All `mode` values are valid (`subagent` or `primary`).
- `training-instability` places its broad `"*": deny` rule before narrow `ask` rules, which is the correct order for “last matching rule wins.”
- All three skill `name` values match their folder names and satisfy the lowercase/hyphenated/length constraints.
- All three skill descriptions front-load trigger keywords and include “Use when…” guidance.
- No skill has an invalid top-level frontmatter key; no skill has non-string `metadata` because no `metadata` block is present.
- All `@` references in `work.md` resolve to existing agent files (`data-pipeline`, `shape-dtype`, `training-instability`).
- `agent-reviewer` is intentionally excluded from the `work.md` roster, and its Usage section documents standalone invocation.
- All subagent Handoff sections use the same six invocation fields as `work.md`: `symptom`, `traceback`, `paths`, `expected`, `observed`, `context`; they map `observed` to output `actual`.
- All three skills have explicit failure handling, and `deploy-troubleshoot`/`env-conflict` have safety guidance; `numpy-serialization` has an `allow_pickle=True` security warning.
- `work.md`’s skill priority order (`env-conflict` → `numpy-serialization` → `deploy-troubleshoot`) matches `AGENTS.md`.
- No Critical permission bypass remains: `edit` is denied for all ML agents, `bash` is ask/deny, and the previously dangerous `"python *": allow` rules are gone.
- All fenced JSON examples are syntactically JSON-shaped on inspection; no code was executed.

---

### 8. Severity counts

| Severity | Per-file | Cross-file / `AGENTS.md` | Total |
|---|---:|---:|---:|
| Critical | 0 | 0 | **0** |
| Major | 4 | 3 | **7** |
| Minor | 21 | 6 | **27** |
| Stylistic/Nitpick | 7 | 2 | **9** |
| **Total** | **32** | **11** | **43** |

---

### 9. Overall verdict

Cycle 4 is **not clean**, but it has **no Critical issues**. The schema migrations from Cycles 1–3 remain intact: every agent uses the singular `permission` map and `bash` key, every skill has valid frontmatter, and no dangerous `"python *": allow` permission remains.

The remaining Major issues are contract and consistency problems:

1. `agent-reviewer` treats deprecated `tools`/`maxSteps` as allowable fields, so it may approve non-compliant frontmatter.
2. `shape-dtype` cannot represent a failed inspection with its current finding-category enum.
3. `work.md` routes shape errors to `numpy-serialization`, which explicitly says shape errors are out of scope.
4. `work.md` requires a `category` from skills, but none of the three skills emits one.
5. `AGENTS.md` points to `config/skills/` instead of `.opencode/skills/`.
6. `AGENTS.md` maps `.npz` to `np.save` instead of `np.savez`.
7. `AGENTS.md` uses an out-of-scope shape-assignment error as the canonical NumPy serialization example.

**Recommended fix order:** fix the three `AGENTS.md` Major issues, then `work.md`’s skill routing and category contract, then `shape-dtype`’s failure category and `agent-reviewer`’s deprecated-field rule. Minor items can follow. Restart opencode after any agent, skill, or `AGENTS.md` change because configuration is not hot-reloaded.

**Explicit Critical statement:** **No Critical issues remain in Cycle 4.**

---

### Fixes applied

**Critical**
- **Critical — none:** Cycle 4 reported no Critical issues, so no Critical fixes were required.

**Major**
- **Major — agent-reviewer checklist item 1 listed deprecated `tools`/`maxSteps` as allowable and included the non-canonical `name` field:** `.opencode/agents/agent-reviewer.md` — rewrote the allowed agent-frontmatter field list, added an explicit deprecated-keys rule, and stated that file-based agents derive `name` from the filename.
- **Major — shape-dtype failure category enum lacked a failure/`unable_to_inspect` value:** `.opencode/agents/shape-dtype.md` — added `unable_to_inspect` to the finding category enum and updated Failure Handling to emit an `unable_to_inspect` finding.
- **Major — work skill routing assigned shape errors to `numpy-serialization`, which excludes shape errors:** `.opencode/agents/work.md` — removed `shape` from the `numpy-serialization` trigger and routed `shape_mismatch` findings to `shape-dtype`.
- **Major — work consolidated report claimed `category` was copied verbatim from a subagent or skill, but no skill emits `category`:** `.opencode/agents/work.md` — added a skill-to-finding category mapping and allowed `category: null` for skill-sourced findings.

**Minor**
- **Minor — agent-reviewer Inputs included the non-existent `config/skills/**/SKILL.md`:** `.opencode/agents/agent-reviewer.md` — labelled `config/skills/` as optional/legacy and added a missing-input suppression for optional paths.
- **Minor — agent-reviewer Output format lacked frontmatter-validation, cross-file, positive-check, and verdict sections:** `.opencode/agents/agent-reviewer.md` — added output template items for frontmatter validation, cross-file findings, positive checks, and the overall verdict.
- **Minor — data-pipeline `bash: ask` did not state that user approval is the only guard:** `.opencode/agents/data-pipeline.md` — added the user-approval-is-the-only-guard statement.
- **Minor — data-pipeline lacked explicit `skill`/`external_directory` permissions:** `.opencode/agents/data-pipeline.md` — added `skill: deny` and `external_directory: deny`.
- **Minor — data-pipeline Integration Notes treated the early-run ordering as expected rather than recommended:** `.opencode/agents/data-pipeline.md` — rephrased the note as a recommendation.
- **Minor — shape-dtype top-level confidence/shape_trace and missing work-side consolidation fields:** `.opencode/agents/shape-dtype.md`, `.opencode/agents/work.md` — added optional `shape_trace`/`unresolved` fields and a confidence-mapping merge rule to the consolidated report schema.
- **Minor — shape-dtype `bash: ask` enforcement relied on guidance rather than an approved-command rule:** `.opencode/agents/shape-dtype.md` — required user approval as the only guard and restricted execution to pre-approved read-only tracer commands.
- **Minor — shape-dtype lacked explicit `skill`/`external_directory` denies:** `.opencode/agents/shape-dtype.md` — added `skill: deny` and `external_directory: deny`.
- **Minor — training-instability Failure Handling lacked a missing/unreadable log path fallback:** `.opencode/agents/training-instability.md` — added an `unable_to_inspect` finding fallback.
- **Minor — training-instability lacked explicit `skill`/`external_directory` denies:** `.opencode/agents/training-instability.md` — added `skill: deny` and `external_directory: deny`.
- **Minor — training-instability bash map allowed broader-than-log-analysis commands:** `.opencode/agents/training-instability.md` — added a Permissions section restricting `bash` to read-only log operations.
- **Minor — work Failure Handling lacked a skill-failure rule:** `.opencode/agents/work.md` — added a skill-error/timeout/empty-result rule recording `skill:<name>` in `missing_coverage`.
- **Minor — work Handoff Contract was overbroad:** `.opencode/agents/work.md` — scoped it to ML diagnostic subagents and added the roster reference.
- **Minor — work consolidated schema lacked `shape_trace`/`unresolved` and confidence mapping:** `.opencode/agents/work.md` — added optional `shape_trace`/`unresolved` fields and the confidence merge rule.
- **Minor — work `bash: ask` broadness / per-command approval:** `.opencode/agents/work.md` — required per-command user approval for state-changing commands.
- **Minor — deploy-troubleshoot Failure Handling used unstructured "insufficient log data" with no Output field:** `.opencode/skills/deploy-troubleshoot/SKILL.md` — added a `status` output field (`insufficient_log_data`).
- **Minor — deploy-troubleshoot healthy-case output shape was undefined:** `.opencode/skills/deploy-troubleshoot/SKILL.md` — defined the healthy response shape.
- **Minor — env-conflict workflow used `which python`, failing on `python3`-only systems:** `.opencode/skills/env-conflict/SKILL.md` — switched to `command -v python3 || command -v python`.
- **Minor — env-conflict sample table omitted the requirement source:** `.opencode/skills/env-conflict/SKILL.md` — added a `source` column to the sample table.
- **Minor — numpy-serialization preventive dtype/shape step preceded error extraction:** `.opencode/skills/numpy-serialization/SKILL.md` — moved preventive inspection after error extraction.
- **Minor — numpy-serialization Output lacked a sample error/cause/fix mapping:** `.opencode/skills/numpy-serialization/SKILL.md` — added a canonical error→cause→fix example to the Output table.

### Skipped

- **Major — `AGENTS.md` lines 3 and 117 point to the non-existent `config/skills/` directory:** skipped — `AGENTS.md` is outside the instructed fix scope (files under `.opencode/agents` and skills folders).
- **Major — `AGENTS.md` line 33 maps `.npz` to `np.save` instead of `np.savez`:** skipped — outside the instructed fix scope.
- **Major — `AGENTS.md` lines 8–29 use an out-of-scope shape-assignment error as the canonical NumPy serialization example:** skipped — outside the instructed fix scope.
- **Minor — `AGENTS.md` line 105 says to "Apply the skill's output" to fix an issue, conflicting with safety rules:** skipped — outside the instructed fix scope.
- **Minor — `AGENTS.md` line 119 claims every skill follows the Single Responsibility Principle despite deploy/env overlap:** skipped — outside the instructed fix scope.
- **Minor — `AGENTS.md` line 63 env-conflict output table omits `status`/`required_version_source`:** skipped — outside the instructed fix scope.
- **Minor — `AGENTS.md` line 19 lists `pickle` as a NumPy function:** skipped — outside the instructed fix scope.
- **Minor — `AGENTS.md` never mentions `.opencode/agents/` or the agent roster:** skipped — outside the instructed fix scope.
- **Minor — `AGENTS.md` line 96 vs deploy skill Output field naming mismatch:** skipped — outside the instructed fix scope.

---

## Cycle 5 — 2026-11-08

# Cycle 5 — 2026-11-08 — opencode Agent & Skill Audit (Meta-Review)

**Note on execution:** The `task` subagent tool was **unavailable** in this session (`Model tried to call unavailable tool 'task'`), so the Cycle 5 re-review was performed directly by the reviewing model, following the instructions defined in `.opencode/agents/agent-reviewer.md` and the task constraints (read-only, no state-changing shell commands, no file edits).

**Scope inventory (verified):**
- Agents: `.opencode/agents/agent-reviewer.md`, `.opencode/agents/data-pipeline.md`, `.opencode/agents/shape-dtype.md`, `.opencode/agents/training-instability.md`, `.opencode/agents/work.md` (5 files).
- Skills: `.opencode/skills/deploy-troubleshoot/SKILL.md`, `.opencode/skills/env-conflict/SKILL.md`, `.opencode/skills/numpy-serialization/SKILL.md` (3 files; no nested `references/`/`scripts/` or additional skill folders exist; `config/skills/` absent).
- Cross-file/harness: `AGENTS.md`, `work.md`.

---

## 1. Summary table

| File | Status | Critical | Major | Minor | Stylistic/Nitpick |
|---|---:|---:|---:|---:|---:|
| `.opencode/agents/agent-reviewer.md` | OK | 0 | 0 | 2 | 0 |
| `.opencode/agents/data-pipeline.md` | OK | 0 | 0 | 0 | 1 |
| `.opencode/agents/shape-dtype.md` | OK | 0 | 0 | 0 | 1 |
| `.opencode/agents/training-instability.md` | OK | 0 | 0 | 0 | 1 |
| `.opencode/agents/work.md` | OK | 0 | 0 | 0 | 1 |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | OK | 0 | 0 | 1 | 1 |
| `.opencode/skills/env-conflict/SKILL.md` | OK | 0 | 0 | 0 | 1 |
| `.opencode/skills/numpy-serialization/SKILL.md` | OK | 0 | 0 | 0 | 1 |
| Cross-file — `AGENTS.md` (harness) | Needs Fix | 0 | 2 | 6 | 2 |
| **TOTAL** |  | **0** | **2** | **9** | **10** |

Status legend: `OK` = no Critical/Major; `Needs Fix` = at least one Major; `Broken` = at least one Critical.

---

## 2. Per-file detail

### `.opencode/agents/agent-reviewer.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/agents/agent-reviewer.md`
**Status:** OK

| Severity | Issue | Suggested fix |
|---|---|---|
| Minor | The agent’s self-declared **Output format** (items 1–7) omits the final mandatory step — an explicit Critical statement — that the Cycle 5 task’s required output format adds as item 8. The agent’s list ends at “7. Overall verdict”. | Append item 8: “End with an explicit Critical statement (e.g. ‘No Critical issues remain’ or list any Criticals).” |
| Minor | The agent’s own `permission` map does not declare `doom_loop`, which checklist item 1 names as a flat-action tool; unlisted tools fall under the default policy. | Add `doom_loop: deny` to the `permission` map. |

### `.opencode/agents/data-pipeline.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/agents/data-pipeline.md`
**Status:** OK

| Severity | Issue | Suggested fix |
|---|---|---|
| Stylistic/Nitpick | The `## Config` section only restates `steps` and adds no real configuration guidance. | Remove it or document actual configuration assumptions. |

### `.opencode/agents/shape-dtype.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/agents/shape-dtype.md`
**Status:** OK

| Severity | Issue | Suggested fix |
|---|---|---|
| Stylistic/Nitpick | The `## Config` section only restates `steps`. | Remove it or document real configuration assumptions. |

### `.opencode/agents/training-instability.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/agents/training-instability.md`
**Status:** OK

| Severity | Issue | Suggested fix |
|---|---|---|
| Stylistic/Nitpick | The `## Config` section only restates `steps`. | Remove it or document real configuration assumptions. |

### `.opencode/agents/work.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/agents/work.md`
**Status:** OK

| Severity | Issue | Suggested fix |
|---|---|---|
| Stylistic/Nitpick | The Subagent Roster uses `@data-pipeline`-style UI mention syntax in prose; the review checklist prefers backticks/plain names with explicit Task-tool invocation. | Use backticks or plain names in prose and keep Task-tool invocation explicit. |

### `.opencode/skills/deploy-troubleshoot/SKILL.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/skills/deploy-troubleshoot/SKILL.md`
**Status:** OK

| Severity | Issue | Suggested fix |
|---|---|---|
| Minor | The **Example** lacks the `status` field that the **Output** contract defines (the healthy shape uses `"status": "healthy"`; failure uses `status: "insufficient_log_data"`). | Add `status` to the example block (e.g. a failure case `status: "error"` or the healthy shape). |
| Stylistic/Nitpick | Heading `## When to provoke it` is awkward wording; rename to `## When to use it`. | Rename the heading. |

### `.opencode/skills/env-conflict/SKILL.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/skills/env-conflict/SKILL.md`
**Status:** OK

| Severity | Issue | Suggested fix |
|---|---|---|
| Stylistic/Nitpick | Heading `## When to provoke it` is awkward wording; rename to `## When to use it`. | Rename the heading. |

### `.opencode/skills/numpy-serialization/SKILL.md`

**Path:** `/home/talha/Desktop/debugger/.opencode/skills/numpy-serialization/SKILL.md`
**Status:** OK

| Severity | Issue | Suggested fix |
|---|---|---|
| Stylistic/Nitpick | Heading `## When to provoke it` is awkward wording; rename to `## When to use it`. | Rename the heading. |

---

## 3. Final severity counts table

| Severity | Count |
|---|---:|
| Critical | 0 |
| Major | 2 |
| Minor | 9 |
| Stylistic/Nitpick | 10 |
| **Total** | **21** |

Breakdown by scope:
- Per-file (agents + skills): Critical 0, Major 0, Minor 3, Stylistic/Nitpick 8.
- Cross-file (`AGENTS.md`): Critical 0, Major 2, Minor 6, Stylistic/Nitpick 2.

---

## 4. Frontmatter-validation table

| File | Result | Deprecated / invalid keys found |
|---|---|---|
| `.opencode/agents/agent-reviewer.md` | Valid | None |
| `.opencode/agents/data-pipeline.md` | Valid | None |
| `.opencode/agents/shape-dtype.md` | Valid | None |
| `.opencode/agents/training-instability.md` | Valid | None |
| `.opencode/agents/work.md` | Valid | None |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Valid | None |
| `.opencode/skills/env-conflict/SKILL.md` | Valid | None |
| `.opencode/skills/numpy-serialization/SKILL.md` | Valid | None |
| `AGENTS.md` | N/A (not an agent/skill file) | N/A |

**Validation conclusions:**
- All five agent frontmatter blocks use the singular `permission` map and the `bash` key; no `permissions:` plural ruleset, no `shell` key, no `tools`/`maxSteps`/`prompt:` keys remain.
- `training-instability.md` places the broad `"*": deny` bash rule before narrow `ask` rules (correct last-match-wins order).
- All three skill frontmatter blocks use only allowed keys (`name`, `description`) with valid `name`/folder match and trigger-oriented descriptions.
- No `frontmatter_invalid` findings were produced; all in-scope files parsed.

---

## 5. Cross-file findings

| Severity | Location | Issue | Suggested fix |
|---|---|---|---|
| Major | `AGENTS.md` lines 3 and 117 | The harness says skills are defined in `config/skills/` and says not to modify `config/skills/*/SKILL.md`; the actual path is `.opencode/skills/`. The harness points at a non-existent directory. | Replace both references with `.opencode/skills/` and `.opencode/skills/*/SKILL.md`. |
| Major | `AGENTS.md` line 33 | Expected-output method line says: “`np.save`/`np.load` for `.npy`/`.npz`” — `.npz` archives are written with `np.savez`/`np.savez_compressed`, not `np.save`. | Correct to: “`np.save` for `.npy`; `np.savez` for `.npz`; `np.load` for both.” |
| Minor | `AGENTS.md` line 19 | Lists `pickle` as a NumPy function; it is a separate Python module, not a NumPy serialization function. | Separate `pickle` from NumPy calls; keep `np.save`/`np.load`/`np.savez`. |
| Minor | `AGENTS.md` lines 8–29 | Canonical NumPy example uses `ValueError: setting an array element with an incompatible shape` (an array-assignment error, explicitly out of scope for `numpy-serialization`) as the serialization error; also has grammar error (“a incompatible”). | Replace with a real serialization error (e.g. `allow_pickle=False` object-array error or doubled-`.npy` `FileNotFoundError`); fix grammar. |
| Minor | `AGENTS.md` line 63 | The expected `env-conflict` output table omits `status` and `required_version_source`, which the skill emits. | Add `status` and `required_version_source` to the harness table or mark them optional. |
| Minor | `AGENTS.md` line 105 | Says to “Apply the skill’s output to fix the issue”, conflicting with skill safety rules (confirm before state-changing fix) and `work.md` Non-Goals. | Reword to route/prepare the fix and apply only after user confirmation. |
| Minor | `AGENTS.md` | The harness never mentions `.opencode/agents/`, the agent roster, or `agent-reviewer`, so the primary workflow and meta-reviewer are undiscoverable from root instructions. | Add an “Agents” section pointing to `.opencode/agents/` and `work.md`. |

---

## 6. Positive checks

Verified and passed in Cycle 5:
- All five agent frontmatter blocks parse as valid YAML and use valid opencode fields; no deprecated/invalid keys.
- All five agents use the singular `permission` map and the `bash` key; no `permissions:`/`shell`/`tools`/`maxSteps`/`prompt:` remain.
- `training-instability.md` bash rule ordering is correct (broad deny before narrow ask; last match wins).
- All three skill frontmatter blocks use only allowed keys (`name`, `description`) with valid `name`/folder match and trigger-oriented descriptions.
- No invalid skill top-level keys; no non-string `metadata`.
- All `@` references in `work.md` resolve to existing agent files.
- `agent-reviewer` is intentionally outside the `work.md` roster; standalone invocation documented.
- All subagent Handoff sections share the six invocation fields; `observed`→`actual` mapping consistent.
- All three skills have explicit failure handling; deploy/env have safety guidance; numpy has `allow_pickle=False` security default.
- `work.md` skill priority order matches `AGENTS.md`.
- No dangerous `"python *": allow` permission remains; `edit` denied for ML agents; bash ask/deny; no Critical permission bypass.
- All fenced JSON examples are JSON-shaped.

---

## 7. Overall verdict

Cycle 5 found **no Critical issues** and **no remaining Major issues in any agent or skill file**. All agent/skill files are schema-valid and substantively complete per the post-Cycle-4 fixes.

The only **remaining Major** findings are cross-file (`AGENTS.md`): the harness skill path (`config/skills/` → `.opencode/skills/`) and the `.npz` method mapping (`np.save` → `np.savez`).

Remaining Minor/Sticky items are limited to: the reviewer agent’s self-declared output format missing the final explicit Critical statement, one example/output-field mismatch in `deploy-troubleshoot`, and awkward heading wording across the three skills.

---

## 8. Explicit Critical statement

**No Critical issues remain.**

---

## Final severity counts table (Cycle 5)

| Severity | Count |
|---|---:|
| Critical | 0 |
| Major | 2 |
| Minor | 9 |
| Stylistic/Nitpick | 10 |
| **Grand total** | **21** |

## Frontmatter-validation summary (Cycle 5)

| File | Result | Deprecated / invalid keys |
|---|---|---|
| `.opencode/agents/agent-reviewer.md` | Valid | None |
| `.opencode/agents/data-pipeline.md` | Valid | None |
| `.opencode/agents/shape-dtype.md` | Valid | None |
| `.opencode/agents/training-instability.md` | Valid | None |
| `.opencode/agents/work.md` | Valid | None |
| `.opencode/skills/deploy-troubleshoot/SKILL.md` | Valid | None |
| `.opencode/skills/env-conflict/SKILL.md` | Valid | None |
| `.opencode/skills/numpy-serialization/SKILL.md` | Valid | None |
| `AGENTS.md` | N/A | N/A |

**Result:** no deprecated or invalid frontmatter keys found; no `frontmatter_invalid` findings.

## Cross-file findings (Cycle 5)

| Severity | Location | Issue | Suggested fix |
|---|---|---|---|
| Major | `AGENTS.md` lines 3, 117 | `config/skills/` → should be `.opencode/skills/` | Fix path references. |
| Major | `AGENTS.md` line 33 | `.npz` mapped to `np.save` → should be `np.savez` | Fix method mapping. |
| Minor | `AGENTS.md` line 19 | `pickle` listed as a NumPy function | Separate it from NumPy calls. |
| Minor | `AGENTS.md` lines 8–29 | Out-of-scope shape-assignment error used as canonical NumPy example; grammar error | Replace with real serialization error; fix grammar. |
| Minor | `AGENTS.md` line 63 | env-conflict output table omits `status`/`required_version_source` | Add fields. |
| Minor | `AGENTS.md` line 105 | “Apply the skill’s output to fix the issue” conflicts with safety rules | Reword to confirm-before-apply. |
| Minor | `AGENTS.md` | No mention of `.opencode/agents/`/roster | Add Agents section. |

## Positive checks (Cycle 5)

- Valid frontmatter, no deprecated keys, correct permission shape across all agents.
- Correct bash rule ordering in `training-instability`; safe `bash: ask` posture elsewhere.
- Valid skill frontmatter/names/descriptions; security and failure handling present.
- No Critical permission bypass; no dangerous Python-allow rules remain.

## Overall verdict (Cycle 5)

**No Critical issues remain.** Remaining work: fix the two cross-file **Major** items in `AGENTS.md` (skill path + `.npz` method mapping), then address Minor items.

## Final Critical statement (Cycle 5)

**No Critical issues remain.**

---

### Fixes applied

- **Minor — agent-reviewer self-declared Output format omitted the final explicit Critical statement (item 8):** `.opencode/agents/agent-reviewer.md` — appended item 8 to the Output format checklist.
- **Minor — agent-reviewer permission map omitted the flat-action tool `doom_loop`:** `.opencode/agents/agent-reviewer.md` — added `doom_loop: deny` to the permission map.
- **Minor — deploy-troubleshoot Example lacked the `status` field required by the Output contract:** `.opencode/skills/deploy-troubleshoot/SKILL.md` — added `status: "error"` to the Example block.

### Skipped

- **Major — `AGENTS.md` lines 3 and 117 (skills path `config/skills/` → should be `.opencode/skills/`):** skipped — `AGENTS.md` is outside the instructed fix scope (files under `.opencode/agents` and skills folders).
- **Major — `AGENTS.md` line 33 (`.npz` mapped to `np.save` → should be `np.savez`):** skipped — outside the instructed fix scope.
- **Minor — cross-file `AGENTS.md` findings (pickle listed as a NumPy function; out-of-scope shape-assignment error as canonical NumPy example; env-conflict output table omission; “apply the skill’s output” wording; no agent-roster mention):** skipped — cross-file/`AGENTS.md` issues fall outside the instructed fix scope.
