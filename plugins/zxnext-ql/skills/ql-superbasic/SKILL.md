---
name: ql-superbasic
description: Write and check SuperBASIC and SBASIC programs for the Sinclair QL, the ZX Spectrum Next's QL core, QPC2 and SMSQ/E - boot and installer programs, hardware probes, launchers - with the traps that bite (PEEK_W reads two bytes on Minerva, && binds looser than =, 16-bit MOD and DIV, no $hex on Minerva, 7-digit numbers in SAVE, EW stopping the caller, LRUN dropping the rest of the line) and a linter to run on the PC before loading. Use this skill whenever you write, edit, generate or debug a _bas file, a QL boot or installer program, or see MISTake, "bad line", "bad parameter" or "not complete" on a QL, even if the user only says "the QL won't load it". Not for Sinclair BASIC or NextBASIC.
---

# SuperBASIC on Minerva, Toolkit II and SMSQ/E

Lint every program on the PC, then load it on an emulator and look for `MISTake` lines:

```sh
python ${CLAUDE_SKILL_DIR}/scripts/sbasic_lint.py install_bas              # Minerva and other QDOS ROMs
python ${CLAUDE_SKILL_DIR}/scripts/sbasic_lint.py app_bas --smsqe          # SMSQ/E only
python ${CLAUDE_SKILL_DIR}/scripts/sbasic_lint.py probe_bas --byte-only 98304-114687
```
`--byte-only` refuses `PEEK_W`, `PEEK_L` and `POKE` with a literal address in that range (hardware registers).

## The file
ASCII, line numbers 1 to 32767, **LF only** with a final LF. A CR can become part of the line and turn it into a
`MISTake`. Keep lines under about 120 characters: they have to be edited on a QL.

## The traps
- **`PEEK_W` and `PEEK_L` are read byte by byte on Minerva**, and `POKE_W` and `POKE_L` written so. On a register where
  a read acknowledges something, they act two or four times: use `PEEK`. They allow odd addresses on Minerva 1.77 and
  later; SMSQ/E answers -15. `PEEK_W` and `PEEK_L` are signed: `IF w < 0 THEN w = w + 65536`.
- **`&&`, `||` and `^^` bind looser than `=`**: `b && 32 = 0` is `b && (32 = 0)`. `NOT s && 36` is `(NOT s) && 36`.
  Always bracket: `(b && 32) = 0`. They work on 16 bits: a value past 32767 overflows.
- **`MOD` and `DIV` work on 16-bit integers**: `196608 MOD 2` stops with an overflow. For "is it even":
  `l = INT(l / 2) * 2`.
- **No `$hex` and no `%binary` literals on Minerva** (SMSQ/E has them). Write decimal.
- **`PRINT` and `SAVE` show 7 digits**: 12582912 prints as `1.258291e7`, and a program that is saved and loaded again
  has lost it. Write big addresses as products (`192 * 65536`). Print with `HEX$(v, 32)` (Toolkit II; both arguments).
- **Anything after `LRUN` or `LOAD` on the same line is dropped**: `LOAD prog` and `RUN 300` are two lines. Put what
  must follow at the end of the program itself.
- **`EW` stops the calling program when the job returns a non-zero code**, even for a job that did its work. Start such
  a job with `EX` and watch its result (`FTEST`, then `FLEN`).
- **`OPEN_NEW` on an existing file asks the user** (Toolkit II): `IF FTEST(f$) = 0 THEN DELETE f$` first, or use
  `OPEN_OVER`.
- `FTEST` answers 0 when the file exists: `IF FTEST(f$) THEN` means missing. Quote device names (`FTEST("ESP1")`): a
  bare name is a variable if one exists.
- ESC at an `INPUT` on Minerva stops the program with "not complete": read keys with `INKEY$(#0,-1)` or `INKEY$(-1)`.
- `PAUSE n` on Minerva ends on a key and eats it; `PAUSE 0` does not wait, `PAUSE` waits for ever.
- `WHEN ERRor` does not catch a break (CTRL+SPACE), and stays active after the program ends. Test first (`FTEST`)
  rather than trap. A program stopped early leaves its channels open: tell the user to type `CLOSE #3`.
- `name%` is a 16-bit integer: use plain (floating) variables for addresses and lengths. A `FOR` loop's variable must
  be floating on old JS ROMs.
- An in-line `ELSE` needs a colon before it, and nested in-line `IF` is unreliable before Minerva 1.92: use
  `IF ... END IF` blocks.
- `==` compares strings without case: `k$ == "q"`.

## Idioms that work on both
- The system variables: `sv = VER$(-2)` (Minerva 1.77 and later, SMSQ/E; assign it first). 163840 is `$28000`, 196608 is
  `$30000` (Minerva's twin screens). Check with `PEEK_W(sv)`: the word is `$D254`.
- RAM top is `PEEK_L(sv + 32)`; the driver list starts at `sv + 68`.
- Time: `DATE` counts seconds; `INKEY$(#0,n)` waits n frames of 20 ms. Minerva has no frame counter to read.
- A results file instead of photographs: write each figure with `PRINT #3`, close, and say the file's name.
- Install a job: see the `ql-c-build` skill (`ALCHP`, `LBYTES`, `SEXEC`, `RECHP`).
- Room on a drive before you write: `DMEDIUM_FREE(\win1_)` (SMSQ/E only), in 512-byte sectors; a file takes its length
  plus 64. Read the length back after (`FLEN`).

## What needs which toolkit
`EW`, `EX`, `FTEST`, `FLEN`, `ALCHP`, `RECHP`, `HEX$`, `SAVE_O`, `LRESPR`: Toolkit II or SMSQ/E. `SEXEC`, `LBYTES`: in
the ROM. `DMEDIUM_FREE`, `$hex`: SMSQ/E. Say at the top of the program what it needs.

Reference: <https://superbasic-manual.readthedocs.io/>.
