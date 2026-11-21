# Snippet: helper tools live in the repo

For projects where Claude writes helper scripts (build tables, emulator drivers, log readers, converters). Paste the
block into your `CLAUDE.md`.

```markdown
## Helper tools live in the repo, under extra/
- Every helper tool written for this project (build and compare scripts, emulator drivers and log readers, proof
  checkers, art and sound tools) is committed under `extra/`, in a subfolder per topic (for example `extra/builds/`,
  `extra/proofs/`, `extra/art/`), with a short README saying how to run it. If there is no `extra/` yet, create it.
- Generated output (builds, emulator runs, screenshots, renders) stays out of git; the tool that makes it goes in
  `extra/`.
```
