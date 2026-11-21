---
name: z80-measure
description: Measure the bytes and T-states of Z80 or Z80N code instead of guessing - a two-label snippet run through z88dk-z80asm and z88dk-ticks, before and after figures for every change, a C-against-asm harness, and the z88dk-ticks push nn byte-order quirk. Use this skill whenever you write, change, optimise or compare Z80 or Z80N assembly, claim that one form is faster or smaller, rewrite a C routine in asm, or need a cycle count, even if the user only asks "is this faster?" or "how many T-states?".
---

# Measuring Z80 and Z80N code

Measure, do not assume. Every change to assembly comes with the bytes and the T-states before and after. When a faster
form costs bytes, give both forms' bytes and T-states and let the user decide.

## Three levels of evidence (say which one you have)
1. **The instruction table**: T-states per instruction, no contention, no wait states. Good for a first estimate only.
2. **A cycle-counting emulator** such as `z88dk-ticks`: the whole routine on real data, branches and loops included.
   It still uses its own timing model (no contended memory, no video wait states).
3. **The machine or an emulator that models it** (for the Next, MAME's `specnext_*` drivers or the hardware itself):
   the only place where lines per frame, contention and DMA can be measured. A frame-time claim needs this level.

## A snippet in two minutes
Mark the code under test with the labels `t_start` and `t_end`; set up registers before `t_start`:

```asm
        org     0
        ld      hl,$1234
        ld      a,$56
t_start:
        add     hl,a            ; Z80N
t_end:
        halt
```

Run `python ${CLAUDE_SKILL_DIR}/scripts/measure.py <snippet.asm> [...]` (default `--cpu z80n`; `--cpu z80` for a
plain Z80). It assembles with `z88dk-z80asm -m<cpu> -b -m`, reads both labels from the `.map`, runs
`z88dk-ticks -m<cpu> -start <t_start> -end <t_end>` and prints bytes and T-states. `examples/` holds measured pairs
(`addhl`, `mul`, `pushnn`, `test`, `shift`, `branch`): copy one as a starting point.

By hand, the same thing is:

```sh
z88dk-z80asm -mz80n -b -m snippet.asm
z88dk-ticks -mz80n -start <t_start hex> -end <t_end hex> snippet.bin
```

**Pitfall:** ticks restarts its count each time PC reaches `-start`. Put `t_start` before a loop, never on the loop's
first instruction, or you get the last pass only.

## A routine moved from C to asm (the harness)
- Build a PC harness that calls both the C version and the asm version on the same inputs and compares every output:
  `zcc +z80 -mz80n` (or `+z80` for plain Z80) with the project's own C flags, run in `z88dk-ticks`. Cover the edge
  cases (zero, the largest value, the sign boundary, the end of every table).
- `z88dk-ticks` stops at its cycle limit (`-w`, 400 million cycles per unit): split long case lists into chunks.
- Keep the C version beside the asm (for example in a comment block above the routine) so the next reader can check it.

## The push nn quirk (Z80N only)
`z88dk-ticks` reads the operand of Z80N `push nn` low byte first. The Next, and z88dk's assembler, store it **high byte
first** (it is the only big-endian operand in the Z80N set). The timing is right; the value pushed in ticks is
byte-swapped. In a harness, swap those operands (or avoid `push nn` in the code under test), or the C side will
"fail" where the hardware is right.

## Reporting a change
Give, for each change: the old and new form, bytes before and after, T-states before and after (with the level of
evidence), and the effect per frame when the code runs every frame (T-states times calls per frame, and lines when
measured on the machine). Example line: `HL += A: ld e,a / ld d,0 / add hl,de (4 bytes, 22 T) -> add hl,a (2 bytes,
8 T), z88dk-ticks; saves 2 bytes and 14 T per call`.

## Additional resources
- `scripts/measure.py`: the snippet runner described above.
- `examples/`: measured snippet pairs; their figures are in the plugin README.
- The `z80-code-layout` skill: branch layout, often worth more than any instruction swap.
