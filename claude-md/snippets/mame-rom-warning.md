# Snippet: MAME's ROM warning

For projects that run MAME windowed (or through a launcher app). Paste the block into your `CLAUDE.md`.

```markdown
## MAME stops on the ROM warning
- MAME stops on a "One or more ROMs ... incorrect" warning at each start. About half a second after starting it, send
  a couple of SPACE key presses into the emulator to skip it (a Lua key schedule, the launcher's MCP tools, or a
  key-sending tool). Headless runs (`-video none`) are not held by it.
- Never edit the ROM zip; use a private `-rompath` copy if a ROM must change.
- Run on a fresh copy of the SD image, never on the original, and keep at most two MAME processes running at once.
```
