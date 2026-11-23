# The PS/2 mouse (QIMI) and the hardware sprite

From the core's published sources, checked with a SuperBASIC probe and then used by a released program, on a KS2
with the 2024 core (Minerva 1.98a1, twin screens, SCN loaded). Not checked on other cores or machines.

## The QIMI addresses
| Address | Read | Notes |
|---|---|---|
| `$1BF9C` | buttons: bit 5 = 0 left down, bit 4 = 0 right down; `$30` idle | no side effect |
| `$1BF9E` | 0 | useful as a sanity check |
| `$1BFBC` | movement: bit 2 x moved, bit 4 right, bit 5 y moved, bit 0 up; `$11` idle | no side effect |
| `$1BFBE` | **any access acknowledges one step** | read it once per step, never write |

- **Byte reads only, and never write to `$18000`-`$1BFFF`**: the same addresses select the ZX8302 (a write to `$1BF9C`
  zeroes the clock). Minerva's `PEEK_W` and `PEEK_L` read byte by byte, so one of them acknowledges twice.
- Idle is `$11`, not 0: the two direction bits read 1. Emulators and most QLs read 0 everywhere, which is the quickest
  way to see there is no QIMI. The bytes look the same with no mouse plugged in, so show a pointer only after the first
  real move or press.
- Sane bytes: `$1BF9C` has only bits 4-5, `$1BFBC` has none of `$CA`, `$1BF9E` is 0.

## Reading it
- Drain: while `$1BFBC & $24` is not 0, count one step for each axis that moved, then read `$1BFBE` once. Cap the loop.
- The counters are 10 bits and wrap past 511: after a pause the direction can be wrong. Drop a drain of 384 steps or
  more on an axis, and any movement that waited for seconds. Flush at the start: 326 steps were waiting at one first
  read.
- SuperBASIC drained 340 steps a second, too slow for a quick hand. Do it in C: in short key-wait slices, and in the
  loops that draw or transfer. A slow move of the hand gave 1 200 to 1 400 steps.
- Carry fractions when you scale steps to pixels, and clear the fraction at the edge of the screen.

## Who owns it
Only one program may acknowledge. Do not read it when the external-interrupt list (system variables + `$38`) is not 0,
or when the Pointer Environment answers (`iop_pinf`): that driver drains it. Stop when either becomes true, and while
another job has the keyboard (CTRL+C); flush and take over the held buttons when it comes back.

Convention: left is HIT (like SPACE), right is DO (like ENTER).

## The sprite at `$C00000` (KS2)
- **Write-only**: reads give `$FF`. Pass the core gates first and check that RAM ends below it (system variables +
  `$20`); the probe also needed RAM at or below `$200000` to recognise the KS2. A KS1 core may have nothing there.
- Sprite 0: enable at `$C00000`, X at `$C00001`, Y at `$C00002` (bytes). X is the screen's x / 2 in 512 units; keep it
  at 246 or less with a 10-pixel arrow. Y is the line.
- Pattern at `$C00080`: 16 rows of 8 bytes, 4 bits a pixel (flash, red, green, blue; 15 is transparent), and each row's
  16 pixels are written **right to left**.
- Write the pattern, then X and Y, the enable last, from variables (no `CLR.B`). Hide it on every way out: it outlives a
  QL reset.
