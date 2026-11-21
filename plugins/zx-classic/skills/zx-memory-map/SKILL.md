---
name: zx-memory-map
description: The classic ZX Spectrum (16K, 48K, 128K, +2) memory map and the facts that shape Z80 code on it - ROM, screen bitmap and attribute addresses, the screen's interleaved line order, system variables and RAMTOP, 128K paging through port $7FFD, contended memory and its timings, the ULA port $FE, and IM 2 vector tables. Use this skill whenever you write, place or optimise Z80 code or data for a classic Spectrum, compute a screen or attribute address, choose where code, stack or tables live, page 128K memory, or ask why code runs slower in some addresses, even if the user only says "where should this go?".
---

# The classic ZX Spectrum memory map

Written from the published references listed at the end. Where sources use different conventions (the first
contended T-state, for example) both are noted. Check timing-critical figures against those references and your
emulator before relying on them.

## 48K map
| Address | Size | Contents |
|---|---|---|
| $0000-$3FFF | 16 KB | ROM (BASIC and the system routines) |
| $4000-$57FF | 6 144 | screen bitmap, 256 x 192 pixels |
| $5800-$5AFF | 768 | attributes, 32 x 24 cells |
| $5B00-$5BFF | 256 | printer buffer (on the 128K, used by the system: see below) |
| $5C00 (23552) | | system variables, then the channel area (CHANS) and the BASIC program at PROG |
| ... | | BASIC variables, edit line, workspace, calculator stack, machine stack, GOSUB stack |
| RAMTOP | | the top of BASIC's memory: 65367 ($FF57) by default on the 48K; `CLEAR n` moves it |
| $FF58-$FFFF | 168 | user-defined graphics (UDG) by default on the 48K |

- On the 16K model RAM ends at $7FFF, and RAMTOP and the UDGs sit 32 KB lower.
- Code and data above RAMTOP are safe from BASIC. Without Interface 1 the BASIC program normally starts at 23755
  ($5CCB); Interface 1 and Microdrive maps move it up, so read PROG (23635) rather than assuming.

## The screen
- Pixel byte for (x 0-255, y 0-191):
  high byte = `$40 | ((y AND $C0) >> 3) | (y AND $07)`, low byte = `((y AND $38) << 2) | (x >> 3)`.
  The bit order is `010 y7 y6 y2 y1 y0 | y5 y4 y3 x7 x6 x5 x4 x3`: the screen is three thirds of 64 lines, and inside a
  third, consecutive pixel lines are 256 bytes apart.
- Attribute for the cell holding (x, y): `$5800 + (y >> 3) * 32 + (x >> 3)`. Attribute byte: bit 7 FLASH, bit 6
  BRIGHT, bits 5-3 PAPER, bits 2-0 INK; colours 0 black, 1 blue, 2 red, 3 magenta, 4 green, 5 cyan, 6 yellow, 7 white.
- One pixel line down from HL:

```asm
        inc     h               ; next line inside the character cell
        ld      a,h
        and     7
        jr      nz,down_done    ; still inside the cell (7 lines in 8): done
        ld      a,l
        add     a,32            ; next character row
        ld      l,a
        jr      c,down_done     ; crossed into the next third: H is already right
        ld      a,h
        sub     8               ; same third: undo the cell's carry into H
        ld      h,a
down_done:
```

## 128K and +2 paging
- `$4000-$7FFF` is always RAM bank 5 (the normal screen), `$8000-$BFFF` always bank 2, and `$C000-$FFFF` any of banks
  0-7.
- Port `$7FFD` (write only): bits 0-2 the bank at $C000, bit 3 the screen shown (0 = bank 5, 1 = bank 7), bit 4 the ROM
  (0 = the 128K editor, 1 = 48K BASIC), bit 5 locks paging until reset. The port cannot be read: keep a copy, and when
  BASIC's ROM is in use update its copy BANKM (23388, $5B5C) before the `out`, with interrupts off around the pair.
- The system uses $5B00-$5BFF on the 128K for its paging routines and variables: do not treat it as free.
- The +2A and +3 add port `$1FFD` (special all-RAM modes, the high ROM bit, disk motor, printer strobe).
- The AY sound chip: select a register at port `$FFFD`, write it at `$BFFD`.

## Contended memory (why the same code runs slower in some addresses)
The ULA reads the screen from RAM while it draws the 192 display lines. When the CPU touches contended memory during
that time it is held for a few T-states.

| | 48K | 128K / +2 | +2A / +3 |
|---|---|---|---|
| CPU clock | 3.5 MHz | 3.5469 MHz | 3.5469 MHz |
| T-states per line, lines per frame | 224 x 312 | 228 x 311 | 228 x 311 |
| T-states per frame | 69 888 | 70 908 | 70 908 |
| Contended RAM | $4000-$7FFF | banks 1, 3, 5, 7 | banks 4, 5, 6, 7 |
| Delay pattern (each 8 T-states) | 6,5,4,3,2,1,0,0 | 6,5,4,3,2,1,0,0 | 1,0,7,6,5,4,3,2 |
| First contended T-state | 14335 (some emulators count 14336) | 14361 (or 14362) | see the references |

- Contention applies during the 128 T-states of each display line that fetch the screen, for the 192 display lines.
- On the 48K and 128K, I/O is contended too: ports with bit 0 low (the ULA), and any port whose high byte is
  $40-$7F. The +2A and +3 differ. The exact per-cycle patterns are in the references.
- Practical rules: keep time-critical code, its data and the stack in uncontended RAM ($8000 up on the 48K; banks 0,
  2, 4, 6 on the 128K); expect screen writes during the display to be slower than their table T-states; any code that
  races the beam must be timed on an emulator that models contention, not from the instruction table.

## The ULA port $FE
- Write: bits 0-2 the border colour, bit 3 MIC, bit 4 the speaker (EAR).
- Read: bits 0-4 the keys of the half-rows whose bit is 0 in the port's high byte (a pressed key reads 0), bit 6 the
  EAR input. Half-rows: $FE CAPS SHIFT-V, $FD A-G, $FB Q-T, $F7 1-5, $EF 0-6, $DF P-Y, $BF ENTER-H, $7F SPACE-B.

## Interrupts
- The ULA raises a maskable interrupt once a frame (50 Hz). In IM 1 the CPU calls $0038, where the ROM counts FRAMES
  and scans the keyboard.
- In IM 2 the vector address is I x 256 + the byte on the data bus, which is not guaranteed: use a 257-byte table
  filled with one value and point I at it, and put the handler at the address that value makes (for example a table
  of $FD bytes and the handler at $FDFD).
- Do not set I to $40-$7F on the 48K or 128K: the ULA then sees the refresh addresses in contended memory, which
  causes screen "snow" and can crash some machines.

## References
- World of Spectrum FAQ, the 48K and 128K technical references:
  <https://worldofspectrum.org/faq/reference/48kreference.htm>,
  <https://worldofspectrum.org/faq/reference/128kreference.htm>.
- The ZX Spectrum manuals (system variables and memory map chapters) and "The Complete Spectrum ROM Disassembly".
- The Sinclair Wiki: <https://sinclair.wiki.zxnet.co.uk/>.
