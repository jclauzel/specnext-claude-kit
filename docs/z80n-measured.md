# Z80N: measured wins and losses

Only measured claims go on this page. Each entry says what was measured, how, and where the number came from. An
instruction table's T-states are not a measurement; they are listed only beside a measurement for comparison.

How to add an entry: measure both forms (bytes and T-states at least; lines per frame if you measured on MAME or a
Next), say the tool and its version, and open a pull request. Losses are as welcome as wins.

## Measured with z88dk-ticks (this repository's examples)
Run: `python plugins/z80-common/skills/z80-measure/scripts/measure.py <files>` with z88dk-ticks v0.14c beta,
`-mz80n`. These are ticks' cycle counts: instruction timing with no contention and no wait states.

| Change | Before | After | Saved |
|---|---|---|---|
| HL += A | `ld e,a / ld d,0 / add hl,de`: 4 bytes, 22 T | `add hl,a`: 2 bytes, 8 T | 2 bytes, 14 T; DE kept |
| DE = D x E (8x8 unsigned) | shift-and-add loop: 16 bytes, 371 T (D=$5A, E=$C3) | `mul d,e`: 2 bytes, 8 T | 14 bytes, 363 T |
| DE <<= 3 | `sla e / rl d` x 3: 12 bytes, 48 T | `ld b,3 / bsla de,b`: 4 bytes, 15 T | 8 bytes, 33 T |
| push a constant | `ld hl,nn / push hl`: 4 bytes, 21 T | `push nn`: 4 bytes, 23 T | **loses** 2 T (keeps HL) |
| test bits of A | `and n`: 2 bytes, 7 T | `test n`: 3 bytes, 11 T on hardware (18 in ticks) | **loses** 1 byte and 4 T (keeps A) |
| common branch, 100 passes | taken `jr cc`: 9 bytes, 3202 T | falls through: 13 bytes, 2714 T | 488 T; costs 4 bytes here |

Notes:
- `test n`: ticks counts 18 T, which is wrong: a KS3 on core 3.03.03 measures 11 T, the SpecNext wiki's figure
  (`examples/z80n-hw-timing`). Even at 11 T it loses to `and n` (7 T, one byte less) whenever A may be destroyed.
- On that KS3, `push nn` measures 23 T (MAME 0.289 counts 24), and code running from $8000 up shows no wait states at
  28 MHz, while MAME 0.289 adds one per memory read there: MAME's 28 MHz timings are an upper bound.
- z88dk-ticks reads `push nn`'s operand low byte first; the Next stores it high byte first. The timing above is
  unaffected, but a harness that checks the pushed value must swap the operand.

## Measured in a game project (z88dk +zxn, MAME 0.289 specnext_ks3, Next hardware)
Reported by the maintainer from a z88dk `+zxn` game project; the figures are that project's, measured with its
frame-report builds on MAME and played on Next hardware.

| Finding | Measurement |
|---|---|
| `add hl,a` (and `add de,a`, `add hl,nn`) in place of `ld e,a / ld d,0 / add hl,de` | the biggest everyday win of the project's Z80N pass, in every table and pointer sum |
| `mul d,e` | the other clear win |
| `push nn` and `test n` | both lost to `ld hl,nn / push hl` and `and n` in that project's routines |
| making the common branch of a per-frame walk fall through | about half a raster line a frame and 6 bytes saved, no instruction changed |

## Wanted
Measurements of `ldirx` / `ldpirx` against plain copy loops, the DMA against `ldir` for large copies, `pixelad` /
`pixeldn` against hand-written screen address code, and `nextreg` against `out` to $243B / $253B, ideally in lines
per frame on MAME and on a Next.
