---
name: z80-code-layout
description: Lay out Z80 and Z80N code so the common path falls through - conditional jump costs taken and not taken, moving rare cases out of line, choosing jr or jp, loop shapes, and measuring the result. Use this skill whenever you write or optimise a hot Z80 routine (a per-frame loop, a sprite or tile walk, an interrupt handler), reorder branches, or ask why a routine is slow even though its instructions look optimal.
---

# Code layout on the Z80

Instructions are only half of a routine's cost. Where the branches go is the other half, and on a per-frame loop it
can matter more than any single instruction swap. In one Next project, making the common branch of a per-frame walk
fall through saved about half a raster line every frame and 6 bytes, with no instruction changed.

## The costs that drive layout (instruction table, plain Z80)
| Instruction | Taken | Not taken | Bytes |
|---|---|---|---|
| `jr cc,e` | 12 T | 7 T | 2 |
| `jr e` | 12 T | - | 2 |
| `jp cc,nn` | 10 T | 10 T | 3 |
| `jp nn` | 10 T | - | 3 |
| `djnz e` | 13 T | 8 T | 2 |
| `ret cc` | 11 T | 5 T | 1 |
| `call cc,nn` | 17 T | 10 T | 3 |

So a `jr cc` that is usually **not** taken is the cheapest branch there is; one that is usually taken costs 5 T more
than falling through each time, and a `jp cc` costs the same either way.

## Rules
1. **Make the common case fall through.** Test for the rare case and jump away to it; put its code out of line (after
   the loop or after the routine's `ret`) and jump back.
2. **Know which case is common** before reordering: count it (a counter in a debug build, a log from the emulator) or
   reason from the data. Do not guess on a routine that matters.
3. **`jr` for short branches that usually fall through**; `jp cc` when the branch is taken about half the time and
   you can spare the byte (10 T either way), or when the target is out of `jr` range.
4. **Loops**: put the test at the bottom (`djnz` or `dec / jr nz`), and hoist work that does not change out of the loop.
   Unroll only when the bytes are affordable, and say what the unrolling costs.
5. **Early exits**: a `ret cc` that is usually not taken costs 5 T; put the most common exit test first.
6. **Measure the layout**, not the instructions: the effect depends on the data. The `z80-measure` skill's `branch`
   example pair shows 100 passes laid out both ways.

## Example (measured with z88dk-ticks, the plugin's examples)
100 passes where the common case is "A is not zero":

| Layout | Bytes | T-states |
|---|---|---|
| Common case takes the branch | 9 | 3202 |
| Common case falls through, rare case out of line | 13 | 2714 |

The fall-through layout saves 488 T over 100 passes (about 5 T a pass) and, in this small example, costs 4 bytes for
the jumps out and back. In a real routine the rare-case code often merges with an existing exit, so it can save bytes
as well. Memory first: when a layout costs bytes, report both figures and let the user decide.
