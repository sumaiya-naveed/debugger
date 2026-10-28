## Review: `@shape-dtype` Subagent

**Prompt:** Review the `@shape-dtype` subagent.

### Context

Review run via:

```bash
opencode run --agent work --auto "review the shape-dtype subagent" >> test-agent/shape.md
```

The live definition (`.opencode/agents/shape-dtype.md`) was compared against its siblings (`data-pipeline.md`, `training-instability.md`), the primary `work.md`, the project `AGENTS.md`, and the opencode 1.18.34 config schema.

### Current state of `.opencode/agents/shape-dtype.md`

- Frontmatter: `description`, `mode: subagent`, `steps: 12`.
- Permission block (list of `{ action, resource, effect }` rules): `edit` deny, `shell` allow, `read` allow, `grep` allow. No `glob` rule.
- Body: Purpose, Inputs, structured `Outputs` JSON contract, five check categories (shape, dtype, device, silent broadcast, dimension order), example finding, tracing modes, integration notes, non-goals.

### Findings

| # | Severity | Area | Issue | Recommendation |
|---|----------|------|-------|----------------|
| 1 | High | Frontmatter / permissions | The block uses the key `permissions:` with a rule list. In the documented markdown-agent frontmatter the field is `permission:` (singular, `PermissionConfig`), and unknown frontmatter fields are silently routed into `options`. The list shape is valid only for the encoded `agents` config, not necessarily for `.md` frontmatter. Enforcement is therefore unverified and may be silently ignored. | Empirically confirm enforcement with a throwaway agent before editing, then use the correct key/shape so `edit` deny and `read`/`grep` allow are actually applied. Note: the previous `pipeline.md` review assumed this block worked; that assumption should be re-checked for all agents. |
| 2 | Medium | Permissions | `shell: allow` diverges from the stated convention: `data-pipeline` and `training-instability` use `shell: deny`, and the primary `work` uses `shell: ask`. Dynamic-mode hook tracing may legitimately need shell, but that exception is undocumented. | Either set `shell: deny` for consistency (static-only tracing) or explicitly document why this subagent needs shell access for dynamic mode. |
| 3 | Medium | Permissions / Inputs | No `glob` rule, although the Inputs section expects model/data paths and every sibling diagnostic agent declares `glob: allow`. | Add `glob: allow` (or justify its absence). |
| 4 | Medium | Output contract | Finding schema omits `evidence` and `first_observed_at`, which `data-pipeline` (and partly `training-instability`) use. Also `shape_trace[]` records `dtype` but **not `device`**, even though device mismatches are one of its own declared checks. | Align `findings[]` with the sibling superset, and add a `device` field to each `shape_trace` entry. |
| 5 | Low | Config | No `## Config` section documenting `steps`, unlike both sibling subagents. | Add `## Config` describing the `steps` budget. |
| 6 | Low | Non-goals | Non-goals say "the primary Work Agent handles fix suggestion and routing," but this agent emits `suggested_fix`, and `work.md` itself declares it does not fix code. | Reword to "flags and suggests fixes only; does not apply them or edit model code." |
| 7 | Low | Integration | Integration notes only reference the primary Work Agent. | Add hand-offs: dtype/device/mixed-precision findings feed `training-instability` (e.g. fp16 overflow to NaN); data-dependent shape issues may feed `data-pipeline`. |
| 8 | Info | Budget | `steps: 12` may be tight for dynamic per-layer forward-hook tracing on a large model. | Acceptable for static mode; consider raising or documenting a scoped trace for reactive use. |
| 9 | Info | Content accuracy | The five check categories and the example finding are technically correct (3D input to `Linear`, `[B,1]` vs `[B]` broadcast, missing `keepdim`, `batch_first`). | No change needed. |

### Verdict

The diagnostic content is coherent and technically accurate, with a clear output envelope and useful tracing modes. The blocking concerns are configuration-level, not diagnostic-logic-level: permission enforcement is unverified and inconsistent with siblings, and the output contract drops the `device` field it needs for one of its own checks. Not ready to sign off until permission behavior is confirmed.

### Recommended next steps

1. Empirically verify whether `permissions:` in `.md` frontmatter is honored; if not, migrate the agents to the correct `permission:` shape.
2. Normalize permission rules across subagents (`shell` policy, `glob` allow).
3. Add `device` to `shape_trace` and align `findings[]` fields (`evidence`, `first_observed_at`) with siblings.
4. Add the `## Config` section and fix the non-goal wording.
5. Cross-reference `training-instability` and `data-pipeline` in Integration Notes.
6. Restart opencode after any agent-file edit — config is not hot-reloaded.

---
