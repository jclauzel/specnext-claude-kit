<!--
Template: a classic 48K/128K ZX Spectrum project in assembly.
Status: UNTESTED starting point. It has not been used on a real project yet: adapt the commands to your assembler and
emulator, and send corrections.
-->

# <Project name>: notes for Claude

## The project
- <One paragraph: what it is, the target (48K, 128K, +2A/+3), the media (.tap, .tzx, .sna).>
- Build: `<pasmo --tapbas main.asm game.tap | sjasmplus main.asm | zcc +zx ...>`. <Say where the output goes.>
- Run: `<fuse game.tap | MAME spectrum / spec128 | another emulator>`. Screenshots and timing come from an emulator
  that models contended memory.
- Load the `zx-memory-map` skill for addresses, paging and contention.

## Memory map
- <Where the code, data, stack and IM 2 table live. Keep time-critical code and the stack in uncontended RAM: $8000
  up on the 48K, banks 0, 2, 4, 6 on the 128K.>
- <RAMTOP / CLEAR value, and what sits above it.>

## Assembly: memory first, speed always
- Memory is the top priority. When a faster form costs bytes, give both forms' bytes and T-states and let me decide.
- Measure, do not assume: bytes and T-states before and after for each change (the `z80-measure` skill with
  `--cpu z80`). Code that touches the screen during the display runs slower than its table T-states: time it on an
  emulator.
- Make the common branch fall through (the `z80-code-layout` skill).
- The frame is <69 888 T-states on the 48K | 70 908 on the 128K>; say each change's effect on it.

## Helper tools and output
- Every helper tool is committed under `extra/<topic>/` with a short README. Generated output stays out of git.

## Git
- Commit only when I ask; never push without my word.
