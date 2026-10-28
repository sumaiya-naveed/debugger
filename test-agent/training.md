## Review: `@training-instability` Subagent

**Prompt:** Review the `training-instability` subagent.

### Context

Review run via:

```bash
opencode run --agent work --auto "review the training-instability subagent" >> test-agent/training.md
```

The live definition (`.opencode/agents/training-instability.md`) was compared against its siblings (`data-pipeline.md`, `shape-dtype.md`), the primary `work.md`, the project `AGENTS.md`, and the opencode 1.18.34 config schema.

### Current state of `.opencode/agents/training-instability.md`

- Frontmatter: `description`, `mode: subagent`, `steps: 10`.
- Permission block: only `edit` deny and `shell` deny. No `read`, `grep`, or `glob` rule.
- Body: Purpose, Config, Inputs, structured `Outputs` JSON contract, six check categories, example finding, integration notes, non-goals.

### Findings

| # | Severity | Area | Issue | Recommendation |
|---|----------|------|-------|----------------|
| 1 | High | Frontmatter / permissions | The block uses `permissions:` with a rule list. The documented markdown-agent field is `permission:` (singular), and unknown frontmatter fields are routed to `options`, so the rules may not be enforced. Same concern as flagged in `test-agent/shape.md`. | Verify enforcement empirically for one agent, then apply the correct key/shape across all agents. |
| 2 | Medium | Permissions | Only `edit` and `shell` are declared. There is no `read`, `grep`, or `glob` rule, unlike every sibling, even though this agent must read loss logs, gradient dumps, and model code. Behavior depends on inherited defaults. | Add explicit `read`/`grep`/`glob` allow rules matching the other diagnostic subagents. |
| 3 | Medium | Output contract | Findings lack a `location` field and `expected`/`actual` pairs, although the checks are explicitly layer/parameter-group specific ("specific layers with disproportionately large gradient norms"). Without `location`, the Work Agent cannot say *where* the instability originated. | Add `location` (layer / parameter group / step) and align `expected`/`actual` with the sibling schema. |
| 4 | Medium | Inputs | Inputs omit training-config values the checks depend on: batch size, gradient-accumulation steps, AMP/mixed-precision and loss-scale state, and the configured gradient-clipping value. Several checks reason about exactly these. | Add those config fields to Inputs so findings can attribute oscillation/NaN rather than guess. |
| 5 | Medium | Check coverage | No explicit mixed-precision / AMP overflow check (loss-scale collapse, fp16 overflow producing Inf/NaN), despite this being a common source of sudden loss NaNs and directly adjacent to the `shape-dtype` agent's dtype findings. | Add an AMP/loss-scale check or fold it into the NaN/Inf section, and cross-reference `@shape-dtype`. |
| 6 | Low | Integration | Integration notes reference the Work Agent and Data Pipeline Agent but not `@shape-dtype`, even though dtype/device/overflow bugs are a common upstream cause of NaN. | Add a hand-off note from `@shape-dtype` findings into this agent's NaN/Inf analysis. |
| 7 | Low | Schema drift | `first_observed_at` is free text ("step or epoch"), while `data-pipeline` uses an enum. Category enum has no slot for LR-schedule issues even though the checks discuss "LR decayed too early"; those get bucketed under `loss_plateau`/`oscillation`. | Normalize `first_observed_at` or document the free-text intent; consider an `lr_schedule` category or explicit mapping note. |
| 8 | Info | Budget | `steps: 10` is slightly lower than the other subagents (12). Fine for log inspection, but per-layer gradient/activation sweeps can be step-heavy. | Acceptable; consider 12 for parity if dynamic profiling is expected. |
| 9 | Info | Content accuracy | Checks for NaN/Inf, exploding/vanishing gradients, dead ReLUs, plateaus (including the `ln(num_classes)` baseline), and oscillation are technically correct, and the example finding is well-formed. | No change needed. |

### Verdict

The instability content is the strongest of the three diagnostic agents: the checks map cleanly to symptoms, include a useful baseline (random-guess loss) for distinguishing "stuck" from "converged", and the example finding tells a coherent causal story. The gaps are contract-level — permissions and the missing `location`/config inputs — rather than diagnostic reasoning. Cross-linking with `@shape-dtype` for dtype/AMP-induced NaNs would close the main coverage gap.

### Recommended next steps

1. Verify the `permissions:` frontmatter key is honored; fix the key/shape if not.
2. Add explicit `read`/`grep`/`glob` allow rules to match sibling subagents.
3. Add `location` (and `expected`/`actual`) to the finding schema and example.
4. Extend Inputs with batch size, grad accumulation, AMP/loss scale, and clipping config.
5. Add an AMP/mixed-precision overflow check and a `@shape-dtype` hand-off in Integration Notes.
6. Restart opencode after any agent-file edit — config is not hot-reloaded.

---
