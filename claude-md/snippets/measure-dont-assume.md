# Snippet: measure, do not assume

For any Z80 or Z80N project. Paste the block into your `CLAUDE.md`. Pairs with the `z80-measure` skill.

```markdown
## Measure, do not assume
- Not every instruction gets faster: a plain `ld` or `add a` costs the same on the Next. Give the bytes and T-states
  before and after for each change, and say how they were measured (instruction table, z88dk-ticks, MAME, hardware).
- Instruction tables give T-states only: lines per frame must be measured on the emulator or the machine.
- Code layout counts as much as instructions: make the common branch fall through.
- When you look at screenshots, look at them yourself and say what you saw, not only what a script counted.
```
