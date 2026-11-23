# Console windows, keys, mouse and colour from C

## Windows and modes
- Take one full-screen console (`con_512x256a0x0`, or `fgetchid(stdout)` with `_condetails` set) and draw inside it.
  Plain QDOS saves nothing under overlapping windows.
- Coordinates stay in 512 x 256 units in mode 8, where a pixel is two units wide. Mode 4 has black 0, red 2, green 4 and
  white 7; mode 8 has eight colours.
- Text cells: CSIZE width 0, 1, 2, 3 = 6, 8, 12, 16 units (85, 64, 42, 32 columns); height 0, 1 = 10, 20. In mode 8,
  widths 0 and 1 become 2 and 3.
- `sd_fill` is the rectangle primitive (bars, lines, highlights). `sd_point`, `sd_line` and their kind convert `double`
  arguments at each call: avoid them.
- `mt_dmode` with -1 asks: 0 or 4 is the 4-colour mode, 8 the 8-colour one (Minerva answers 0 or 8). Setting a mode
  clears every window, so set it once, before you draw, and put it back when you leave.
- **The pending newline.** A string that ends at the right edge leaves the cursor waiting to wrap, and Minerva's
  `sd_setsz` acts on it: at the bottom of the screen the whole console scrolls. Move the cursor to 0,0 before you change
  the size and after any string that fills the line.
- `sd_setmd` -1 (exclusive or) holds for text and block fills.

## Keys
- `io_fbyte(con, 1, &c)` is a natural 20 ms tick. Drain type-ahead with timeout 0. Use one console for the keys and
  enable its cursor once (`sd_cure`).
- ENTER 10, ESC 27, TAB 9, SPACE 32. LEFT 192, RIGHT 200, UP 208, DOWN 216; **add 1 for ALT, 2 for CTRL, 4 for SHIFT**
  (212 is SHIFT+UP). Two sources that swap ALT and SHIFT are wrong: C68's `curses.h` and QPC2's manual agree on this.
  F1 to F5: 232, 236, 240, 244, 248. CTRL+LEFT (194) is delete-left.
- CTRL+C switches the keyboard between consoles and never reaches you. CTRL+SPACE is not a job kill.
- QPC2's mouse wheel sends several ALT+UP or ALT+DOWN at a time: make those one row, never "first" and "last".
- `keyrow()` reads the matrix through the slow IPC and leaves the key in the queue: only for "is it held?".

## A mouse: the Pointer Environment
- QPC2 (SMSQ/E) has it built in. On sQLux, Q-emuLator and most QLs the user loads `ptr_gen`. Ask with `iop_pinf`: it
  returns an error cast to a pointer, so test `(long)p < 0`.
- **Claim your window** (`iop_outl`) or the Pointer Environment repaints over what you drew at the start.
- C68's `fclose` of stdin, stdout and stderr leaves the QDOS console open, and it stays the job's primary window: close
  it by its channel id before you open the console you want managed.
- Test a program under `ptr_gen` even if it has no mouse: the keyboard path changes.
- On the Next's QL core without `ptr_gen`, the mouse is read directly: see the `ql-next-core` skill.

## Colour past 8 on SMSQ/E (seen on QPC2 5.02, SMSQ/E 3.38, mode 32)
- `mt_dmode(-1)` answers 16 for 8-bit colour, 32 for QPC2's 16-bit colour and 33 for the Q40 and Q68's. A mode you
  set on such a display changes nothing.
- 24-bit colour is plain trap #3 on the console: `$54` paper, `$55` strip, `$56` ink (D1 = `$RRGGBB00`, D2 = -1 for
  solid) and `$5D` block (A1 = four words: width, height, x, y; A2 = colour, contrast, stipple -1). A block is not
  clipped: past the window it answers -4.
- Probe first: try a black paper and a 2 x 1 black block on the fresh console; both must answer 0. Elsewhere those keys
  answer an error, and you stay in mode 8 or 4.
- Any answer of `mt_dmode` other than 0, 4 and 8 is an extended display: make no mode call there.

## Unverified here
The default console geometry, the composite colour byte's contrast and stipple bits, the sign of `sd_scrol`, the user
font format: check them before you rely on them.
