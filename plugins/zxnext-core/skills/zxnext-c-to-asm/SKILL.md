---
name: zxnext-c-to-asm
description: How to win back memory and frame time on a ZX Spectrum Next game written in C (z88dk zsdcc) by rewriting its hottest routines in Z80N assembly safely - profile first, keep each routine's C whole above its asm in a "; C:" comment block, keep zsdcc's calling convention, put the rewrite behind a build switch whose 0 build is the old C byte for byte, prove the asm against its C on thousands of random inputs, apply a stop rule, replace many per-page bank-switching doors with one shared trampoline, and prove on the emulator that nothing a player could see or hear changed. Use this skill whenever a Next C program is short of memory or frame time, when the user asks to rewrite C in assembly, to move code into asm, to free bytes in the main bank or a page, to share or shrink bank-switching code, or to prove a rewrite changed nothing, even if they only say "we are running out of room" or "make it faster".
---

# Rewriting hot C in Z80N assembly, safely

A z88dk C game on the Next runs out of two things: bytes (the main bank, each 16 KB page) and frame time (the raster
lines a frame may take). zsdcc's code for small per-frame routines is often a third bigger and a third slower than
hand-written Z80N. This method came from a real game: three rewrite steps freed about 1.3 KB of the main bank and
nearly a line of every frame, with nothing a player could see or hear changed. Load `z80n-optimize` (the forms) and
`z80-measure` (counting T-states) beside it.

## 1. Profile first, biggest first
- Find where the bytes and the time go before choosing anything: the `.map` gives each routine's size; the frame report
  (or MAME's line counts per stage) gives where a frame spends its lines. Rank the per-frame routines by size and by
  calls per frame.
- Rewrite the biggest per-frame routines first, a few at a time (one step), measuring after each. Leave one-time setup
  and title-screen-only code for last: they cost bytes but no frame time.
- **Look for the cheaper exit first.** Slow code is not always slow instructions. In an application's window drag,
  the cost was repainting rows that a clip then threw away: assembly drawing routines alone made that step 7 % faster,
  and two early returns in the C made it 2.2 to 6.2 times faster (for example 17.75 M to 2.86 M T-states,
  z88dk-ticks).
- **What assembly buys depends on the routine's shape.** zsdcc reaches arguments and locals through `(ix+d)`: a glyph
  loop with 8 arguments and 3 locals cost about 300 T-states a pixel. Rewritten, that application's text and fill
  routines ran 1.7 to 6.6 times faster (z88dk-ticks, the shipped flags) but were about the size of the C. Expect time
  from pixel loops, and bytes mostly from routines that carry call overhead and 16-bit bookkeeping.
- **The stop rule:** if a routine's asm saves under 20 bytes and under 0.2 of a line on the worst frame, keep the C and
  say why with the numbers. Small helpers that only the rewritten routines call can move with them when that pays.

## 2. Write the asm next to its C
- Above each asm routine, put the C function it replaces, **whole**, in a `; C:` comment block, so the file still reads
  as the C and anyone can check the asm against it line by line. Keep the block in step with the C when either changes.
- Keep zsdcc's interface exactly: the same calling convention (`__z88dk_fastcall` takes its argument in L or HL;
  other arguments on the stack), the registers each caller expects kept (with `-clib=sdcc_iy` the library owns **IY**:
  never touch it; say whether IX is used), the same signedness, carries and return registers.
- IY is not a spare pair even where the compiled C never uses it: the ROM's IM 1 handler reads the system variables
  through IY, and it runs whenever the program calls the OS. A routine that borrows IY passes every PC test and fails
  in the field. Make the harness load IY (and IX) with a known value before each call and check it afterwards.
- No alternate register set (`exx`, `ex af,af'`) unless the program's interrupt handler saves it.
- The same calls in the same order: every bank door, every sound call, every helper. A rewrite changes how, never what.
- Statics the asm must reach lose `static` only under the switch (a macro such as `OBJ_STATIC` that is `static` when the
  switch is 0), so the 0 build stays the old bytes.
- Pin every C constant the asm hard-codes with a compile-time check in the C (a negative array size when they
  disagree), and every assumption in the asm with an assembler `IF` that stops the build. Note: z88dk's assembler reads
  quotes even inside a false `IF`, so an apostrophe in an error message breaks every assembly.
- Z80N first (`add hl,a`, `mul d,e`, `ldix`, `nextreg`...), but measure: some Z80N forms lose (`push nn`, `test n`).

## 3. The switch: the old C stays one build away
- Put the whole step behind a build switch (for example `ASM_GAME`): at 0 it compiles the C exactly as before, and the
  0 build must be the previous step's build **byte for byte** (the anchor). Commit with the default 0, then the
  switch-on as its own commit. Refuse, before any file is written, a build that turns the asm on together with options
  the asm does not carry (debug variants of the C, other switches it depends on being off).
- Keep each source file's symbols on the same lines when only comments or checks change, so the 0 build's map does not
  move and comparisons stay simple.

## 4. Prove the asm equals its C, on the PC
- Build a harness with `zcc +z80 -mz80n` and the game's C flags that links the C routine and the asm routine side by
  side, feeds both the same random states (thousands of cases, a fixed seed), and compares every output and every
  global they touch. Plant a few mutants in the asm (a wrong flag, an off-by-one) and check the harness catches each
  one: a harness that cannot fail proves nothing.
- Count T-states in `z88dk-ticks` on recorded real states (a quiet frame, a busy frame, the heaviest event), C against
  asm, call included; report the medians. Mind ticks' quirks: it reads Z80N `push nn`'s operand in the wrong byte order
  (swap it in the harness) and miscounts `test n` (18 T in ticks, 11 T on a real Next). For code that pages memory
  or draws on Layer 2, read "Other ways z88dk-ticks is not a Next" in `z80-measure` before trusting a result.

## 5. One shared bank door instead of many
- Programs that call code in other 16 KB pages often grow one small door function per page, each in C: map the page
  into an MMU slot, call the routine, map the old page back. Replace them with **one** asm trampoline: the page and the
  routine given in registers (for example A = page, DE = routine, L = the routine's argument), the old MMU value saved
  and restored exactly, and each old door becomes a few bytes of entry. Check every caller gets the same MMU state back.
- It saves bytes on every door and makes later pages cheap to add.

## 6. Prove that nothing a player could see or hear changed (on the emulator)
- Replay the same recorded inputs (key schedules) on the old build and the new one, and log per frame what the game
  decides: positions, scores, spawns, sound register writes. Logs taken by write taps or by reading a memory share cost
  the emulated machine nothing (see `zxnext-mame`).
- Every game value must be equal frame for frame; the sound log equal once the addresses of moved code are set aside;
  every screenshot equal pixel for pixel, except pictures the CPU's spare time places (something drawn while the
  raster runs may land a frame sooner when the code gets faster): name those, look at them, and accept them knowingly.
- Compare only runs whose frame counters line up at each level's start (the phase rule in `zxnext-mame`).
- Report each level's worst frame line before and after (expected lower), the bytes freed per page, and the T-states
  per routine.

## What to report
Per routine: bytes C and asm, T-states C and asm (with the scenes), the Z80N forms used and the ones rejected with why;
the room before and after in every page; the harness result (cases, mutants caught); the anchors (the 0 build byte for
byte); each level's worst line before and after; and anything named for a later step (the next biggest routines).
