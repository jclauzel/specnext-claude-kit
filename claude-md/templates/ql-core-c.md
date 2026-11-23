<!--
Template: a Sinclair QL program in C (qdos-gcc), for the ZX Spectrum Next's QL core and other QLs.
Status: UNTESTED as a template. Its rules come from a released project of that kind.
-->

# <Project name>: notes for Claude

## The project
- <One paragraph: what it is, and the machines it must run on: the Next's QL core (which core, which board), QPC2,
  other QLs, sQLux.>
- **68000 code only.** The QL core is not the Next's Z80N machine: no Z80N, no z88dk, no `.nex`, no Next registers. If
  a parent `CLAUDE.md` says "Z80N first", it does not apply here.
- Build: `<your build script>` (qdos-gcc 2.95.3, `-O2 -m68000 -Wall`). Load the `ql-c-build` skill.
- Run: `<your run script>` (sQLux). Load the `ql-emulators` skill before running anything.

## Building
- The linker and the assembler exit 0 on errors: the build fails on `Undefined Symbol` in the link's output, and on a
  missing or empty `.o`.
- Every build runs `a6scan.py` over `qdos-gcc -S` output. A hit fails the build.
- `_stack` is <N> bytes; no frame over <N> (`stack_frames.py --limit`). Recursive walks stop with 8 KB left.

## The machine
- Nothing at `$80xxxx` or `$C0xxxx` is touched before the Next's core has been recognised (the `ql-next-core` skill).
- Names are 36 characters at most after the device, and folders are only prefixes of names (the `ql-qdos-c` skill).
- Every wait can be stopped with ESC.

## Proof
- Pure logic lives in files without `<qdos.h>` and is unit-tested on the PC.
- Say where each thing has run: sQLux, QPC2, the Next (which core). Keep the list of what is owed on real machines in
  `<docs/owed.md>`. I run the hardware tests myself: never deploy to a machine unless I ask.

## Helper tools and output
- Every helper tool is committed under `extra/<topic>/` with a short README. Generated output stays out of git.

## Git
- Commit only when I ask; never push without my word.
