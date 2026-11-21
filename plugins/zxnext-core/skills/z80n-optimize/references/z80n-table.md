# Z80N extended instructions

Source: the SpecNext wiki's "Extended Z80 instruction set" page, as mirrored at
<https://k1.spdns.de/Develop/Projects/zasm/Info/Z80n/Extended%20Z80%20instruction%20set%20-%20SpecNext%20Wiki.html>.
The wiki says its T-states are based on limited testing and may not be accurate: measure anything that matters.

| Instruction | Encoding | Bytes | T-states | Notes |
|---|---|---|---|---|
| `swapnib` | ED 23 | 2 | 8 | swap the nibbles of A |
| `mirror a` | ED 24 | 2 | 8 | reverse the bits of A |
| `test n` | ED 27 n | 3 | 11 | A AND n, flags only; z88dk-ticks counts 18 |
| `bsla de,b` | ED 28 | 2 | 8 | DE shifted left by B (low 5 bits) |
| `bsra de,b` | ED 29 | 2 | 8 | arithmetic right |
| `bsrl de,b` | ED 2A | 2 | 8 | logical right |
| `bsrf de,b` | ED 2B | 2 | 8 | right, filling with ones |
| `brlc de,b` | ED 2C | 2 | 8 | rotate left |
| `mul d,e` | ED 30 | 2 | 8 | DE = D x E, flags unchanged |
| `add hl,a` | ED 31 | 2 | 8 | A zero-extended; carry undefined |
| `add de,a` | ED 32 | 2 | 8 | as above |
| `add bc,a` | ED 33 | 2 | 8 | as above |
| `add hl,nn` | ED 34 lo hi | 4 | 16 | |
| `add de,nn` | ED 35 lo hi | 4 | 16 | |
| `add bc,nn` | ED 36 lo hi | 4 | 16 | |
| `push nn` | ED 8A hi lo | 4 | 23 | operand high byte first |
| `outinb` | ED 90 | 2 | 16 | `outi` without decrementing B |
| `nextreg n,n` | ED 91 reg val | 4 | 20 | write a Next register |
| `nextreg n,a` | ED 92 reg | 3 | 17 | write A to a Next register |
| `pixeldn` | ED 93 | 2 | 8 | HL = the screen address one pixel row down |
| `pixelad` | ED 94 | 2 | 8 | HL = the screen address of pixel (E, D) |
| `setae` | ED 95 | 2 | 8 | A = the pixel mask for E |
| `jp (c)` | ED 98 | 2 | 13 | jump to the current 16 KB block + 64 x the byte read from port C |
| `ldix` | ED A4 | 2 | 16 | `ldi`, skipping the byte equal to A |
| `ldws` | ED A5 | 2 | 14 | copy (HL) to (DE), L and D incremented |
| `lddx` | ED AC | 2 | 16 | `ldd` skipping A, DE incremented |
| `ldirx` | ED B4 | 2 | 21 / 16 | repeating `ldix` |
| `ldpirx` | ED B7 | 2 | 21 / 16 | pattern fill from an 8-byte aligned source |
| `lddrx` | ED BC | 2 | 21 / 16 | repeating `lddx` |

For the plain Z80 instructions, any standard Z80 timing table gives the T-states. Time per frame still has to be
measured on the machine or on MAME (CPU speed, contention and wait states depend on the mode).
