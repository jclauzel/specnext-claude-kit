---
name: ql-c-build
description: Build QL jobs in C with qdos-gcc 2.95.3 and the C68 library (Sinclair QL, the ZX Spectrum Next's QL core, QPC2, SMSQ/E) - the toolchain's silent failures (ld and the assembler exit 0 on errors), the -O2 bug that reads locals through a6 with no frame pointer, stack and dataspace sizing, and the header a job needs on each kind of QL (XTcc trailer, Q-emuLator prefix, SEXEC). Use this skill whenever you build, link, package or install a QL or QDOS program, see "Undefined Symbol", a crash or garbage in a local array, "not a job" or a dataspace question, size a stack, or write a build script for qdos-gcc or C68, even if the user just says "build it" in a QL project. Not for z88dk or Z80 code, since the QL core is a 68000.
---

# Building QL jobs with qdos-gcc

The compiler is gcc 2.95.3 for QDOS (<https://github.com/xXorAa/qdos-gcc-2.95.3>), its library is C68's. It targets a
68000: none of the Z80 or Z80N material applies. Read `references/c68-runtime.md` before you touch argument passing,
inline traps, job start-up, the runtime variables or exit codes.

## The toolchain fails without saying so
- **`ld` exits 0 on undefined symbols.** It prints `Undefined Symbol: '_X'` and still writes a file that looks like a
  job. Search the link's output for `Undefined Symbol`; never trust the exit code. Link to a temporary name and move
  the file into place only when the log is clean, or a broken job sits beside a good build.
- **The assembler exits 0 on errors.** The Windows `as.exe` is a wrapper that ignores `as68`'s result: a bad `asm()`
  statement prints one `jas: line N` message, leaves an empty (0 byte) or stale `.o`, and the driver reports success.
  Delete the `.o` before each compile, then require that it exists and is not empty.
- **The toolchain must sit at `\qdos-gcc` on the current drive.** The driver, the linker and the assembler wrapper
  hard-code `/qdos-gcc/...`. Run the compiler from that drive (`Push-Location C:\`), with full paths for the sources.
- **`-o name` becomes `name.exe`** on Windows. Never use `con`, `aux`, `nul` or `prn` as a source name: gcc compiles
  `con.c`, git on Windows cannot open it.
- **Keep `-m68000`** (the default). `-m68020` or `-m68881` switch the assembler syntax, and the wrapper hides the
  errors that follow. Never `-mshort`, which makes `int` 16 bits against a library built with 32.

Flags that worked on a released job: `-O2 -m68000 -Wall -Wno-unused`.

## Scan every build for the a6 bug
At `-O2`, gcc 2.95.3 can drop a function's frame pointer and still address a local array as `-16(a6)`. No warning: the
function reads and writes stray memory. It can look right most of the time: in one project a single test saw it.

```sh
qdos-gcc -O2 -m68000 -S -o build/s/main.s src/main.c     # each .c, with the build's own flags
python ${CLAUDE_SKILL_DIR}/scripts/a6scan.py build/s     # exit 1 and a line per suspect function
```
The cure is to take the array out of the frame: `static char letters[16];`, if nothing re-enters the function. Any edit
to the file can bring the bug back elsewhere, so make the scan part of the build or the tests. Checked on 1 695
functions: no false report, and it names the known case when the `static` is removed again.

## The stack is the only stack, and nothing checks it
- `long _stack = 16384;` in your program sets the C stack (default 5 120), carved from the common heap at start-up. A
  call past its low end writes over the heap, with no message.
- `python ${CLAUDE_SKILL_DIR}/scripts/stack_frames.py build/s --top 20` lists every frame; `--limit 512` fails a build
  whose frames grow. A recursive level costs its frame, 4 for the return address, and the call's arguments.
- `stackreport()` (C68) returns the bytes left at run time. Before each level of a recursive walk, stop when fewer than
  8 KB are left: the deepest library call in one project took 4 KB (`sprintf` alone is estimated at 1 KB).
- Move path buffers and directory entries of recursive functions to `static` storage when they are used only before the
  next level runs. This halved one walk's frame (1 980 to 928 bytes). An edit that reads one of them after the recursive
  call breaks silently: test with a deep tree, byte for byte.
- A big stack is also a start-up risk on a small machine: when the first allocation fails the job dies with no message.

## Dataspace and headers: a job needs its header back on each machine
`ld` puts the dataspace in an 8-byte trailer (`XTcc` + a big-endian long). Only sQLux and uQLx read it. Everywhere else
the type and dataspace live in the QDOS file header, which is lost whenever the file passes through a PC.

| Where the job will live | Form |
|---|---|
| a folder sQLux mounts | the file as linked |
| Q-emuLator, QPC2's `dos1_`, sQLux | `qlheader.py wrap`: the 30-byte `]!QDOS File Header` prefix |
| any real QDOS or SMSQ/E drive, the Next's QL core | `qlheader.py raw`, then `LBYTES` and `SEXEC` on the QL |

```sh
python ${CLAUDE_SKILL_DIR}/scripts/qlheader.py info build/app.exe
python ${CLAUDE_SKILL_DIR}/scripts/qlheader.py wrap build/app.exe -o dist/app_exe
python ${CLAUDE_SKILL_DIR}/scripts/qlheader.py raw  build/app.exe -o dist/app_bin
```
- The linker's figure is not the bss size: it is what the bss needs beyond the end of the file. Never go below it. The
  released job adds 16 KB and rounds up to 1 KB, which is the script's default.
- The figure is per job and per build: generate the installer's size and dataspace, never type them.

## Installing on the QL
- `a = ALCHP(size): LBYTES file,a: SEXEC target,a,size,dataspace: RECHP a` (Toolkit II or SMSQ/E). Guard with `FTEST`
  first: an `LBYTES` of a missing file stops SuperBASIC half-way.
- **A full drive leaves a truncated job behind.** `SEXEC` stops with "medium is full" but the short file stays, and
  `EW` would start it. Check the room first where you can (`DMEDIUM_FREE`, SMSQ/E only) and compare `FLEN` with the
  size afterwards.
- Generated `_bas` files: ASCII, LF only, with a final LF. Run `sbasic_lint.py` (the `ql-superbasic` skill) on them.

## Prove it
- Keep the logic in files that do not include `<qdos.h>`, and unit-test those with a PC compiler; a small stub header
  covers the rest. Run the job itself with the `ql-emulators` skill.
- A build switch for a new feature: compile the same sources with one extra define and prove the 0 build is
  byte-identical to the previous release. qdos-gcc builds are reproducible enough for that check.
- An emulator proves the code, not the machine: say what has only run on sQLux.
