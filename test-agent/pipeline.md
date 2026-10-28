## Review: `@data-pipeline` Subagent

**Prompt:** Review the `@data-pipeline` subagent.

### Context

Follow-up review run of the `@work` agent via:

```bash
opencode run --agent work --auto "review the data-pipeline subagent" >> test-agent/pipeline.md
```

This run followed the application of the previously recommended fixes to the live agent definition and its siblings.

### Current state of `.opencode/agents/data-pipeline.md`

- Frontmatter valid — `description`, `mode: subagent`, `steps: 12`; permissions: edit/shell `deny`, read/grep/glob `allow`.
- Purpose, six check categories, structured `Outputs` contract, example finding, integration notes, and non-goals are coherent and complete.

### Verification of the draft review's claims

1. **Stale cross-references:** Overturned — the live file had already been corrected to point at the primary Work Agent / mark non-existent agents appropriately.
2. **Missing formal `Outputs` contract:** Resolved — the live agent now defines the structured `findings[]` + `summary` envelope.
3. **Finding-schema drift:** Resolved — the live example finding now uses `category: split_overlap` and includes `location`, `first_observed_at`, `expected`, and `actual`.
4. **Permissions:** Corrected — all diagnostic subagents use `shell: deny`; only the primary Work Agent uses `shell: ask`.
5. **`steps`:** Documented via a new `## Config` section.

### Verdict

The `@data-pipeline` subagent is now consistent with its siblings and its own declared checks. The previously flagged issues have been addressed; no further edits are warranted unless new issues surface.

### Recommended next steps

1. Re-run the review after future changes to the agent definitions.
2. Keep the structured output contract aligned across subagents as they evolve.
