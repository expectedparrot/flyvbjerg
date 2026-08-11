# Agent instructions for Flyvbjerg

Use the CLI as the workflow source of truth:

```bash
flyvbjerg guide
flyvbjerg next
```

Every command emits one versioned JSON envelope on stdout. The coding agent
performs web discovery and retrieval; Flyvbjerg never browses or downloads.
EDSL processing is limited to registered captures, and building jobs never
authorizes model execution.

Run `flyvbjerg next` after material stages. Before handoff run
`python -m compileall -q src`, `pytest -q`, and `git diff --check` when this is a
git worktree.

