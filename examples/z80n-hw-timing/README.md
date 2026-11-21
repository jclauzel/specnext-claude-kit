# z80ntime: Z80N instruction timing on real Next hardware

A small ZX Spectrum Next program (`z80ntime.nex`) that measures how many T-states some Z80N instructions take, on
the machine itself, by counting raster lines. It was written to settle one question: z88dk-ticks counts `test n` as
18 T, the SpecNext wiki's instruction table says 11 T. It also checks `push nn`, `add hl,a` and `mul d,e` against
their plain Z80 forms, and shows what the 28 MHz wait states cost.

## What it measures
Each block is one instruction (or one short group) repeated 500 times with z80asm `REPT`, then a `ret`:

| Row on screen | Block (500 times) | Wiki T-states at 3.5 MHz |
|---|---|---|
| `(loop)` | nothing: a lone `ret` (the loop's own cost: `call`, `ret`, reading the line) | |
| `nop` | `nop` (the reference) | 4 |
| `and n` | `and $0F` (a known check) | 7 |
| `test n` | `test $0F` (Z80N) | 11 (z88dk-ticks: 18) |
| `push nn/pop` | `push $1234` (Z80N) + `pop hl` | 23 + 10 = 33 |
| `ld/push/pop` | `ld hl,$1234` + `push hl` + `pop hl` | 10 + 11 + 10 = 31 |
| `add hl,a` | `add hl,a` (Z80N) | 8 |
| `mul d,e` | `mul d,e` (Z80N) | 8 |
| `ld/ld/add` | `ld e,a` + `ld d,0` + `add hl,de` | 4 + 7 + 11 = 22 |

## How it measures
- Interrupts off; the code and the stack sit at `$8000` and up (banks 2 and 0, never contended).
- It syncs to the start of raster line 0, then calls a block `loops` times, reading the active video line counter
  (NextReg `$1E`/`$1F`, through ports `$243B`/`$253B`) after every call. A block is far shorter than a frame, so every
  wrap of the counter is seen and counted as one frame (the frame's line count is measured first).
- Lines net = lines(block) - lines(empty block). Then **T = 4 x net(block) / net(nop)**: relative to `nop` with the
  same repeat count and loops, so the result depends neither on the CPU clock nor on the line length.
- The whole set runs at each CPU speed (NextReg `$07` = 0, 1, 2, 3: 3.5, 7, 14, 28 MHz). The loops double with each
  speed step (64, 128, 256, 512), so `nop` takes about 560 lines at every speed: one line is under 0.2 % of it, and
  the T values are good to about 0.1 T.
- Because the loops double with the clock, equal cycles give equal lines at every speed. So **cycles = 4 x net(block)
  / net(nop at 3.5 MHz)** gives each block's cost in cycles of its own clock, wait states included (the file's last
  column). At 3.5, 7 and 14 MHz the two numbers agree; at 28 MHz the Next adds wait states, `nop` itself among them,
  so the relative T drifts and the cycles column shows the real cost.
- Afterwards it gives back the CPU speed it found.

## Build
Needs z88dk (`zcc +zxn`, zsdcc, newlib) in `C:\z88dk` or in `$env:Z88DK_DIR`:

```powershell
.\build.ps1                    # or: .\build.ps1 -Z88dk D:\tools\z88dk
```

It runs `zcc +zxn -startup=0 -clib=sdcc_iy -SO3 --opt-code-size -pragma-include:zpragma.inc z80ntime.c timing.asm
-subtype=nex -Cz--clean -create-app -m -o build/z80ntime`, then checks from the `.map` that the blocks start at
`$8000` or above and that the program stays clear of the stack, and prints the size and MD5. The output
(`build/z80ntime.nex`, `build/z80ntime.map`) is generated and kept out of git.

## Run it on a Next
1. Copy `z80ntime.nex` to a folder on the SD card (the program writes its results file to the same folder).
2. In the NextZXOS browser, select it and press ENTER (or `.nexload z80ntime.nex` from BASIC in that folder).
3. It shows "Measuring..." for about 6 seconds (the screen stays still meanwhile), then the table, then
   `SAVED Z80NTIME.TXT` (or `SAVE ERROR n` with the esxDOS error code).
4. Note or photograph the table. Press any key: the program clears the screen and leaves through a soft reset
   (NextReg `$02`), back to NextZXOS. NextZXOS's `.nex` loader has no way back to BASIC: on MAME a plain return
   crashed back through the boot, so the soft reset is the clean exit.

## Read the screen
- Line 1: the title and the core version (NextReg `$01` and `$0E`, for example `3.03.03`).
- Line 2: the frame's line count (264 at 60 Hz, 312 at 50 Hz).
- The first table: **T per block, relative to `nop` = 4**, one column per speed (3.5, 7, 14, 28 MHz). The 3.5 MHz
  column gives the clean T-states. For the pairs and triples, the value is the whole group.
- The second table: the net lines each block took (the `(loop)` row: the empty block's raw lines). Divide a 28 MHz
  value by the 3.5 MHz `nop` value and multiply by 4 for the cycles at 28 MHz.
- Read `test n`: about 11.0 means the wiki is right, about 18.0 means z88dk-ticks is.

## The results file: Z80NTIME.TXT
Written with the esxDOS calls (`F_OPEN` create-or-truncate, `F_WRITE`, `F_CLOSE`, through z88dk's `esx_f_*`) to the
current folder, overwriting an old one. It is **CSV** with CRLF line ends: a quoted title line, `core,<version>`,
`frame_lines,<n>`, `block_repeats,500`, a header, then one row per speed and block:

```text
mhz,instruction,loops,lines_net,t_states,cycles_vs_3.5mhz_nop
3.5,"test n",64,1547,11.0,11.0
28,"test n",512,1965,11.2,14.0
```

`lines_net` is the block's lines minus the empty block's (for the empty block itself: its raw lines, and the two
T columns are empty). The instruction names are quoted because some contain commas.

## Results
### MAME 0.289, specnext_ks3 (core 3.02.04 model), 60 Hz, 264 lines a frame
MAME's own Z80N timing is a model and may differ from the hardware.

| Block | 3.5 MHz T | 7 MHz T | 14 MHz T | 28 MHz T | 28 MHz cycles |
|---|---|---|---|---|---|
| `nop` | 4.0 | 4.0 | 4.0 | 4.0 | 5.0 |
| `and n` | 7.0 | 7.0 | 7.0 | 7.2 | 9.0 |
| `test n` | 11.0 | 11.0 | 11.0 | 11.2 | 14.0 |
| `push nn` + `pop hl` | 34.0 | 34.0 | 34.0 | 32.8 | 41.0 |
| `ld hl,nn` + `push hl` + `pop hl` | 31.0 | 31.0 | 31.0 | 30.4 | 38.0 |
| `add hl,a` | 8.0 | 8.0 | 8.0 | 8.0 | 10.0 |
| `mul d,e` | 8.0 | 8.0 | 8.0 | 8.0 | 10.0 |
| `ld e,a` + `ld d,0` + `add hl,de` | 22.0 | 22.0 | 22.0 | 20.8 | 26.0 |

On MAME `test n` takes 11 T (the wiki's figure) and `push nn` 24 T (34 - 10 for `pop hl`; the wiki says 23). At
28 MHz MAME adds one wait cycle to every memory read (each opcode, operand and stack read) and none to writes.

### Next hardware (to fill in)
Machine: ______ (KS1 / KS2 / KS3), core: ______, video: ______ Hz, frame lines: ______

| Block | 3.5 MHz T | 7 MHz T | 14 MHz T | 28 MHz T | 28 MHz cycles |
|---|---|---|---|---|---|
| `nop` | 4.0 | 4.0 | 4.0 | 4.0 | |
| `and n` | | | | | |
| `test n` | | | | | |
| `push nn` + `pop hl` | | | | | |
| `ld hl,nn` + `push hl` + `pop hl` | | | | | |
| `add hl,a` | | | | | |
| `mul d,e` | | | | | |
| `ld e,a` + `ld d,0` + `add hl,de` | | | | | |

## Files
- `z80ntime.c`: the driver (speeds, the arithmetic, the screen, the results file).
- `timing.asm`: the measured blocks (`REPT`) and the line-counting loop.
- `zpragma.inc`: the crt settings (the terminal's own font copy, so the text does not depend on the paged ROM).
- `build.ps1`: the build.
