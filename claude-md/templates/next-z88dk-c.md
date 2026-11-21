<!--
Template: a ZX Spectrum Next project in C with z88dk (+zxn, zsdcc) and some Z80N assembly.
Status: distilled from the CLAUDE.md of a real z88dk +zxn game project. Replace every <placeholder>, delete what does
not apply, and keep the file short: procedures belong in skills (install the zx-claude plugins).
-->

# <Project name>: notes for Claude

## The project
- <One paragraph: what it is, who plays it, the target (Next core version, 50 or 60 Hz, display mode).>
- Build: `<.\build.ps1 | make>` writes `<name>.nex` and `<name>.map`. Debug flavours go to `debug/`, never over the
  project's `.nex`. Load the `zxnext-build` skill before building or checking room.
- Run and prove on MAME: load the `zxnext-mame` skill. MAME stops on a "One or more ROMs ... incorrect" warning at
  each start: about half a second after starting it, send a couple of SPACE presses (headless runs are not held).
- The memory map lives in `<docs/design.md>`: which page sits in which MMU slot in each phase.

## C with zsdcc
- `-clib=sdcc_iy`: IY belongs to the library. Asm called from C keeps IY and follows the calling convention.
- Switches reach C as `-DX=v` and the assembler as `-Ca-DX=v`, always with an explicit value.
- A routine moved from C to asm keeps its C version in a comment above it, and a PC harness proves them equal.

## Assembly: Z80N first, memory first, speed always
- Use a Z80N instruction wherever one can replace plain Z80 (load the `z80n-optimize` skill). z88dk's `+zxn`
  assembles all of them.
- Memory is the top priority. When a faster form costs bytes, give the bytes and T-states of both forms and let me
  decide. When a change saves bytes and time, take both.
- Frame budget: the worst line of every <level> at most <N> of <264 at 60 Hz | 311 at 50 Hz>. Say each change's
  effect on the frame (T-states, lines) as well as its bytes.
- Measure, do not assume (the `z80-measure` skill): bytes and T-states before and after for each change.
- When you read existing Z80 code and see a plain sequence a Z80N instruction would replace, flag it (file, line, the
  form, bytes and T-states saved); do not change working code for it unless asked.

## How features land
- Each feature sits behind a build switch. Commit it with the default 0 first: the 0 build must equal the previous
  commit's `.nex` byte for byte. Then commit the switch-on on its own.
- Bad switch combinations are refused before any file is written.
- Report every page's and the main bank's free bytes before and after, and the number of builds made.

## Helper tools and output
- Every helper tool is committed under `extra/<topic>/` with a short README. Generated output (builds, MAME runs,
  shots) stays out of git.
- The session scratchpad can be wiped: nothing needed again lives only there.

## Git
- Commit only when I ask; never push without my word. <Branch naming, release tagging.>
