---
name: zxnext-build
description: Build ZX Spectrum Next programs with z88dk (+zxn, zsdcc, z80asm) into a .nex, measure the room left in every page and the main bank, land each feature behind a build switch whose 0 build reproduces the previous build byte for byte, refuse bad switch combinations before writing any file, and run a build table (side by side in detached git worktrees) checked by MD5 anchors. Use this skill whenever you build, rebuild, compare or check the size of a Next program or .nex, add or change a build switch, write or run a build table, check memory or bank room, or prove that a change leaves an old build unchanged, even if the user just says "build it", "how much room is left" or "does the 0 build still match".
---

# Building ZX Spectrum Next programs (z88dk +zxn)

These rules come from a z88dk `+zxn` game project with a C core, Z80N assembly, many 16 KB pages and a PowerShell
build script, refined over many milestones. They apply to any Next project; replace "the build script" with yours
(`build.ps1`, a Makefile, a shell script). `references/build-table.md` has the build table and comparison details.

## The toolchain
- z88dk lives where `$Z88DK_DIR` points (or on `PATH`); `ZCCCFG` must point at `<z88dk>/lib/config`.
- C compiles with zsdcc, for example `-clib=sdcc_iy -SO3 --max-allocs-per-node200000 --opt-code-size`. With
  `sdcc_iy` the IY register belongs to the library: asm that C calls must preserve IY, and whatever else the calling
  convention says.
- Compile: `zcc +zxn -c <flags> [--codesegPAGE_nn] -pragma-include:<zpragma.inc> -o <obj> <src>`.
  Link: `zcc +zxn -startup=31 <flags> -pragma-include:<zpragma.inc> -subtype=nex -Cz--clean -create-app -m -o <name>
  <objs>`. `-m` writes the `.map`; every room check and every emulator log reader needs it: keep it beside the `.nex`.
- `-startup=31` is the CRT with no console driver: a program that draws its own screen needs no other, and one
  application got about 3.3 KB of its main bank back by moving to it from a console startup. `printf` to the screen
  then goes nowhere: keep a console startup for a debug flavour that prints.
- **Pin the z88dk build, and check it before believing an overflow.** One module compiled to 59 428 bytes with a
  z88dk of December 2023 and to 56 844 with a nightly of 2026-08-10: with the old one a page overflowed on unmodified
  sources, which looked exactly like a regression. Compare the first line `zcc` prints with the build the project
  pins (in CI, a dated container image). The Windows nightly and the `z88dk/z88dk` container image of that same date
  gave byte-identical `.nex` files.
- **Test with the compiler and flags you ship.** In one application, zsdcc with `-SO3` and
  `--max-allocs-per-node200000` **together** (z88dk nightly, August 2026) compiled a function that ORs event bits into
  a local across several calls so that it returned 0: every bit set before a call was lost, a bit set after the last
  call survived. Either flag alone, plain zsdcc and sccz80 compiled it correctly; making the accumulator a file-static
  `volatile` fixed it. The unit tests stayed green throughout because the `+test` target's default compiler is
  sccz80: they never compiled what shipped. Run every test twice, for example sccz80 `-O2` and
  `zcc +test -compiler=sdcc -SO3 --max-allocs-per-node200000`. (Under `+test`, `--opt-code-size` garbled the test
  harness's own `printf` output in that project; it was left out of the test builds only. Not investigated.)
- A switch reaches both languages: `-DX=v` for C and `-Ca-DX=v` for the assembler, always with an explicit value.
- Asm is Z80N first, memory first, speed always: load the `z80n-optimize` skill, and give bytes and T-states before
  and after for every change (the `z80-measure` skill of the `z80-common` plugin).

## The .nex and the memory map
- Let the build check the file it made: the header's bank count (byte 9) equals the banks the program loads, the bank
  list holds exactly those banks (nothing from bank 48 up if it must run on an unexpanded 1 MB Next), the required core
  version is stamped, and with no loading screen or palette the size is 512 + 16 384 x banks. A failed check deletes
  the `.nex`, so the project folder never offers a broken build.
- appmake writes each bank as exactly 16 384 bytes and refuses a section that crosses 16 KB, but it does not bound
  what you put in a page: the build script must cap each page itself. Leave room for what the page shares its address
  range with (for example the divMMC automap area near $3D00 for code that runs in the bottom 16 KB).
- Keep the 64 KB map in the project's design notes: which page sits in which MMU slot during each phase. Code that
  changes an MMU slot gives it back exactly as it found it.

## Room: measure it, say it, keep the floors
- Every build prints the main bank's free bytes (to the stack fence) and each page's used and free bytes against its
  cap. Read them from the build log or the `.map`; never guess.
- Keep a floor in the main bank (one project keeps 2 048 bytes free: below about 2 KB its debugging tools froze). The
  build warns under the floor and fails when the room goes negative.
- Memory is the top priority: for every change, say each page's and the main bank's free bytes before and after, and
  where the bytes came from. The tightest build flavour (usually the one with every debug option on) decides.

## The switch pattern (how every feature lands)
1. Put the feature behind a switch whose default lives only in the build script, with an option to turn it off
   (`-Feature0`) and a define (`-DFEATURE=0|1`).
2. Commit the feature with the default **0** first. The 0 build must be the previous commit's program **byte for
   byte**: that is the anchor. Then commit the **switch-on** (default 1) on its own.
3. Every older switch at its old value must still give its old row: the oldest release build is the outer anchor.
4. **Refusals**: a switch that needs another switch, an off option beside the same define, or a malformed value must
   stop the build **before any file is written**. Test it: count the files written under the output folders (0), and
   check that `git status --porcelain --ignored` is unchanged.

## The build table
- Build only what the step needs: a **trimmed table** (about 15 flavours: the game, its debug-report twin, the tightest
  flavour, each with the new switch at 0, the oldest release anchor, and the refusals). The full table (every switch
  combination) runs at a release candidate.
- Run it in a few detached git worktrees side by side, each with its own output folder; wait for all, merge the
  outputs, remove the trees. Never build in a tree someone else is committing to.
- Every log shows the project's always-on checks passing, one line per switch with its value, and no "fail" or
  "error" beyond the known notes.
- Compare tables with a script, not by eye: `.nex` byte for byte, `.map` files line for line once zcc's temporary
  names are removed. Report MD5s (full in the docs, 8 hex digits in prose), free bytes per flavour, and **the number of
  builds each part made and the total**.
- Keep the build-table and comparison scripts in the repo (for example `extra/builds/` with a README); their output
  stays out of git.

## Other rules that bite
- Debug builds (any extra define) carry a visible marker and go to a separate `debug/` folder, so the project folder's
  `.nex` is always the build to play. Never leave a debug build there; never overwrite a file in `debug/`, add names.
- The version lives in one place (the build script); a check refuses disagreeing copies in the changelog and README.
- Assets regenerate from their sources on every build; generated files stay out of git.
- **A stale object links without a word.** When several flavours reuse the same object names, a compile that fails
  or is dropped leaves the other flavour's object in place, and a check that the file exists passes. One project
  released a `.nex` carrying one module of another flavour that way (compiles run in the background in a container,
  exit codes unread). Delete each object before compiling it, read every compiler's exit code (when compiles run in
  parallel, wait for each by its process ID), and require every linked object to be newer than the flavour's start.
- Never run two builds in the same checkout at once: they overwrite each other's objects.

## Additional resources
- `references/build-table.md`: the trimmed table, worktrees, refusal tests, the comparison regex, what to report.
