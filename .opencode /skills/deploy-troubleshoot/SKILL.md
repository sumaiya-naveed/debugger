---
name: "deploy-troubleshoot"
description: "Analyzes deployment failure logs from Docker, Kubernetes, CI pipelines, and cloud functions, identifying root causes and providing remediation steps."
role: "deploy-troubleshoot"
capabilities: ["log-analysis", "root-cause-identification", "fix-recommendations"]
priority: "high"
---

# deploy-troubleshoot Skill

## What it does

- Analyzes deployment failure logs (Docker, Kubernetes, CI pipelines, cloud functions)
- Identifies common failure causes: missing configuration, resource limits, incorrect environment variables, container exit codes, failed health checks
- Provides step-by-step remediation suggestions

## When to provoke it

- User shares a deployment error stack trace, container restart logs, or CI error output
- The failure involves `Error:`, `Exit code`, `Backoff`, `CrashLoopBackOff`, or timeout messages
- When a newly added dependency or config change seems to break the deployment

## Output of the skill

- A concise list of the most likely root causes (max 5) with brief explanations
- Recommended fix commands or configuration snippets (e.g., add missing env var, increase resource limits, adjust Dockerfile)
- A "next-steps" checklist the user can run to verify the fix
- If the log is clean, the skill returns "No deployment issues detected – appears healthy."

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