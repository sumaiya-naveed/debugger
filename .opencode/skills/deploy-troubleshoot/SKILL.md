---
name: deploy-troubleshoot
description: "Analyzes Docker, Kubernetes, and CI/CD deployment failure logs (CrashLoopBackOff, exit codes, timeouts, missing env vars) and identifies root causes with fixes. Use when the user shares deployment logs, stack traces, or CI output."
---

# deploy-troubleshoot Skill

## What it does
- Analyzes deployment failure logs from Docker, Kubernetes, CI pipelines, cloud functions
- Identifies: missing config, resource limits, env variables, exit codes, health check failures

## When to provoke it
- User shares deployment error stack trace, container restart logs, CI error output
- Failure involves `Error:`, `Exit code`, `Backoff`, `CrashLoopBackOff`, or timeouts
- New dependency or config change broke deployment

## Inputs
- `Log`: deployment error output/stack trace
- `Platform`: Kubernetes/Docker/CI/CD name
- `RecentChanges`: new dependencies/config changes

## Workflow
1. Parse the supplied log for `Error:`, `Exit code`, `CrashLoopBackOff`, `OOMKilled`, and timeout markers.
2. Classify the failure: config/env, resources, image/build, networking/health check, or permissions.
3. Rank at most 5 root causes with evidence from the log.
4. Provide fix commands or configuration snippets.
5. End with a verification checklist, or "No deployment issues detected – appears healthy."

## Safety
- Confirm with the user before applying any state-changing fix (e.g. `kubectl set`, `kubectl delete`, restarts).
- Prefer read-only diagnostics and dry runs (`--dry-run=server`) before changing a live workload.

## Output
- **root_causes**: max 5 root causes with brief explanations
- **fixes**: commands or configuration snippets
- **checklist**: verify the fix
- **healthy**: "No deployment issues detected – appears healthy."

The `healthy` field is used only when no issues are found.

## Failure Handling
- If the log is empty or unparseable, return "insufficient log data" and name the missing input.
- If `Platform` is missing, infer it from log markers or ask; state the assumption.
- If `RecentChanges` is missing or irrelevant, proceed with log-only analysis and state that recent changes were unavailable.
- If multiple platforms are present, analyze each separately and label findings by platform.

## Example
```yaml
error: "CrashLoopBackOff"
log_excerpt: "Last State: Terminated  Reason: OOMKilled  Exit Code: 137"
root_causes:
  - insufficient memory limit (container OOMKilled, exit code 137)
fixes:
  - kubectl set resources deployment/<name> --limits=memory=1Gi --dry-run=server   # review first
  - kubectl set resources deployment/<name> --limits=memory=1Gi                    # apply after confirmation
checklist:
  - kubectl get pods -w   # pod reaches Running
  - kubectl describe pod <name>   # no repeated OOMKilled restarts
  - confirm readiness probe passes
```
