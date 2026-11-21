# Snippet: memory first, speed always

For any 8-bit project where bytes are scarce. Paste the block into your `CLAUDE.md`.

```markdown
## Memory first, speed always
- Memory is the top priority. Prefer the form that frees bytes. When a faster form costs bytes, say so with the bytes
  and T-states of both forms, and let me decide.
- Optimise for frame time as well: keep every frame as light as it can be (our budget: the worst line of every level
  at most <N> of <lines per frame>). When a change saves bytes and time, take both.
- For every change, say each memory page's and the main bank's free bytes before and after, where the bytes came
  from, and the change's effect on the frame (T-states, lines).
```
