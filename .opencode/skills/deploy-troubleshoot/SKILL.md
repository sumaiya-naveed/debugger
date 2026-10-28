---
name: "deploy-troubleshoot"
description: "Analyzes deployment failure logs and identifies root causes with fixes."
role: "deploy-troubleshoot"
capabilities: ["log-analysis"]
priority: "high"
---

# deploy-troubleshoot Skill

## What it does
- Analyzes deployment failure logs from Docker, Kubernetes, CI pipelines, cloud functions
- Identifies: missing config, resource limits, env variables, exit codes, health check failures

## When to provoke it
- User shares deployment error stack trace, container restart logs, CI error output
- Failure involves `Error:`, `Exit code`, `Backoff`, `CrashLoopBackOff`, or timeouts
- New dependency or config change broke deployment

## Output
- **list**: max 5 root causes with brief explanations
- **fixes**: commands or configuration snippets
- **checklist**: verify the fix
- **healthy**: "No deployment issues detected – appears healthy."

## Example
```yaml
error: "CrashLoopBackOff"
root_causes:
  - insufficient memory limits
  - incorrect environment variable configuration
solution:
  - increase memory limit in Kubernetes deployment
  - verify environment variable values
```