# zxnext-core

Skills for ZX Spectrum Next development with z88dk.

| Skill | What it does |
|---|---|
| `zxnext-build` | Build with z88dk `+zxn` into a `.nex`; room per page and in the main bank; the switch pattern (a 0 build that reproduces the previous build byte for byte); refusals before any file is written; the trimmed build table in side-by-side worktrees with MD5 anchors |
| `zxnext-mame` | Run and prove a `.nex` on MAME `specnext_ks3`: SD image copies, an untouched ROM zip, a cap on concurrent MAME processes, the ROM warning SPACE presses, a Lua autoboot runner, log costs, the frame report, the phase rule, comparing runs and looking at shots |
| `z80n-optimize` | Z80N first, memory first, speed always: the Z80N replacements with bytes and T-states, the ones that can lose, hardware before opcodes, flagging opportunities in existing code |
| `zxnext-c-to-asm` | Rewriting the hottest C (zsdcc) in Z80N asm safely: profile first, the C kept above the asm in `; C:` blocks, zsdcc's calling convention, a switch whose 0 build is the old C byte for byte, a C-against-asm harness with mutants, a stop rule, one shared bank door, proving nothing visible changed |

Install: `claude plugin install zxnext-core@specnext-claude-kit` (and `z80-common@specnext-claude-kit`, which these
skills refer to).

## Tested on
- **zxnext-build**: generalised from a z88dk `+zxn` game project (C with zsdcc `sdcc_iy`, Z80N asm, many 16 KB pages,
  a PowerShell build script, release `.nex` files run on Next hardware). The commands and flags are the ones that
  project uses. Not tested as written: the generic wording, other build systems (Make, sjasmplus).
- **zxnext-mame**: MAME 0.289, machine `specnext_ks3` (its default BIOS models core 3.02.04), runs headless and
  windowed on Windows. `references/lua-runner.md` is a shortened skeleton of a working runner and is **untested as
  written**.
- **z80n-optimize**: the instruction table is the SpecNext wiki's (its own caveat: limited testing). The byte and
  T-state comparisons in the skill were checked with `z88dk-ticks -mz80n` (see `z80-common`'s README). The "lost in
  one project" and "half a line a frame" notes are measurements from that game project on MAME.

- **Added in 0.2.1, from a second project** (a z88dk `+zxn` application with banked code pages, z88dk nightly of
  2026-08-10, z88dk-ticks v0.14c beta, MAME 0.289, run on an N-Go, a KS2 and a KS3): in `zxnext-build`, the
  `-startup=31` figure, the pinned toolchain, the zsdcc flag pair and the two-compiler test rounds, stale objects, and
  naming the banks in which two `.nex` files differ; in `zxnext-c-to-asm`, the early-exit and routine-shape notes and
  the IY rule; in `zxnext-mame`, timing a program that has no frame loop. The figures are that project's.

## Not here (yet)
- sjasmplus-based builds: contributions welcome (see `claude-md/templates/next-sjasmplus-asm.md` for a starting point).
- CSpect-based proofs: the ZX-Next-Unite plugin can start CSpect; a timing skill for it would be welcome.
