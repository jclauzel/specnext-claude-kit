---
name: z80n-optimize
description: Write and review ZX Spectrum Next assembly Z80N first, memory first, speed always - which Z80N instructions replace plain Z80 sequences (add hl,a, mul d,e, the barrel shifts, ldix/ldirx/ldws, nextreg, pixelad/pixeldn), which ones can lose (push nn, test n), the hardware that beats any instruction (Copper, sprites, DMA, scroll registers), and how to flag Z80N opportunities in existing code with bytes and T-states. Use this skill whenever you write, change, review or optimise Z80 or Z80N assembly for the Next, read code zsdcc generated, or talk to Next registers, even if the user only says "make this faster" or "save some bytes".
---

# Z80N first, memory first, speed always

## The three priorities, in order
1. **Memory.** Prefer the form that frees bytes. When a faster form costs bytes, give the bytes and T-states of both
   forms and let the user decide.
2. **Speed.** When a change saves bytes and time, take both. Say each change's effect on the frame (T-states, and
   lines when measured) as well as its bytes.
3. **Measure, do not assume.** Not every instruction gets faster: a plain `ld` or `add a` costs the same on the Next.
   Give bytes and T-states before and after for every change (the `z80-measure` skill of the `z80-common` plugin).
   Instruction tables give T-states only: lines per frame must be measured on MAME or on a Next.

## The Z80N forms to reach for
| Instead of | Use | Notes |
|---|---|---|
| `ld e,a / ld d,0 / add hl,de` (4 bytes, 22 T) | `add hl,a` (2 bytes, 8 T) | also `add de,a`, `add bc,a`; A is zero-extended; carry is undefined afterwards |
| `ld de,nn / add hl,de` | `add hl,nn` (4 bytes, 16 T) | also `add de,nn`, `add bc,nn`; keeps DE |
| a multiply loop | `mul d,e` (2 bytes, 8 T) | DE = D x E unsigned; flags unchanged |
| a chain or loop of shifts | `bsla` / `bsra` / `bsrl` / `bsrf` / `brlc de,b` (2 bytes, 8 T) | B holds the count |
| a copy loop that skips a transparent byte | `ldix`, `ldirx`, `lddx`, `lddrx`, `ldpirx` | the byte in A is not copied |
| `out` to $243B then $253B | `nextreg n,a` (3 bytes, 17 T) / `nextreg n,n` (4 bytes, 20 T) | for every Next register |
| screen address arithmetic | `pixelad`, `pixeldn`, `setae` | Spectrum screen layout in hardware |
| four `rrca` or `rlca` | `swapnib` (8 T) | |
| bit reversal | `mirror a` (8 T) | |
| a port loop | `outinb` | like `outi` but B is unchanged |
| a jump table on an input byte | `jp (c)` | |

**Only after measuring:** `push nn` (4 bytes, 23 T) against `ld hl,nn / push hl` (4 bytes, 21 T), and `test n`
(3 bytes) against `and n` (2 bytes, 7 T). In one project both lost; they win only when the register you would lose
is worth more than the bytes and T-states. `push nn` stores its operand high byte first, the only big-endian operand
in the set.

Full table: `references/z80n-table.md`.

## Hardware beats instructions
The biggest wins on the Next are hardware, not opcodes: the Copper for per-line register changes, hardware sprites
instead of drawing, the DMA for large copies (far faster than `ldir`), and the scroll registers instead of redrawing.
Writing to the screen while the raster is elsewhere (the frame's quiet window) removes tearing at almost no cost.

## Layout counts as much as instructions
Make the common branch fall through (the `z80-code-layout` skill of the `z80-common` plugin). In one project's
per-frame walk this alone saved about half a line a frame and 6 bytes.

## Reading existing code: flag, do not rewrite
When you read existing Z80 code (hand-written asm, or the code zsdcc generates) and see a plain Z80 sequence a Z80N
instruction would replace, flag it: name the file and line, the Z80N form, and the bytes and T-states it would save.
Do not change working code for it unless the user asks or it is part of the task.

## z88dk notes
- `+zxn` targets assemble every instruction above; for a plain `+z80` build pass `-mz80n` to the assembler.
- `z88dk-ticks -mz80n` counts Z80N cycles, but reads `push nn`'s operand in the wrong byte order (the timing is
  right, the value is swapped). Its count for `test n` (18 T) is wrong: a KS3 (core 3.03.03) measures 11 T, the wiki's.
