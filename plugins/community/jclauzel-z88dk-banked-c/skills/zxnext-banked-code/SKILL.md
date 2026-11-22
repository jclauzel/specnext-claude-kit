---
name: zxnext-banked-code
description: Keep C code that runs from banked pages safe on a ZX Spectrum Next (z88dk --codesegPAGE_nn, several pages taking turns in one MMU slot) - why a direct call between two pages links without a word and runs the wrong code, why an esxDOS call made from a page in the bottom 16 KB does not come back, wrappers in the main bank, trampolines that put back the page they found, where string constants really go, what an interrupt handler may touch, and how to check it all with a call-graph walk instead of grep. Use this skill whenever you add, move or review code in a banked page, write a page swap or a trampoline, call esxDOS or the OS from banked code, move a module out of the main bank to free room, or chase a freeze that happens only sometimes after a file operation, even if the user only says "move this into a page".
---

# Banked C code on the Next, safely

The setting these rules were learned in: a z88dk `+zxn` program whose main bank sits at $8000 and up, and whose other
modules are compiled with `--codesegPAGE_nn` into 8 KB pages that take turns in **one** MMU slot (slot 1, $2000-$3FFF
in the measured program). Neither the compiler nor the linker knows which page is mapped when a call is made: that
is yours to keep right. Every rule below was a freeze or a wrong build before it was a rule.

## Rule 1: no direct call between two pages
- Every page is linked for the same address range. A call from a function in one page to a function in another
  links without a warning and, at run time, jumps to whatever the **caller's** page holds at that address.
- Modules that share a page may call each other directly: whenever either runs, their page is the one mapped.
- Code in different pages meets only through a wrapper in the main bank that swaps the pages over and back.

## Rule 2: nothing banked reaches the OS without a wrapper
- An esxDOS call (`rst $08`) hands $0000-$3FFF to the divMMC, and the OS expects the ROM there. Code that made the
  call from a page mapped in that range is not there when the call returns. Seen twice on hardware (an N-Go, which is
  an issue 2 board): a hang on one run, a crash on the next, depending on what replaced the code.
- The fix is a wrapper in the main bank for each OS call the banked code needs: it maps the ROM back into the slot
  (page 255), makes the call, then maps the caller's page again.
- The rule is about **reachability**, not about who types the call. In the measured program a banked module with no
  esxDOS call anywhere in its text still trapped four calls down. Grep cannot see that; a call graph can (below).

## Trampolines put back what they found
- A trampoline that maps a page for a call saves the slot's current page first and restores **that**, never a
  constant. Its callers arrive with different pages in the slot (or the ROM); a constant unmaps one of them from
  under its own return address. Only the OS wrappers of rule 2 write a constant, because the OS needs the ROM.
- Use one shared pair of small assembly routines for every swap (map a page and return the old one; set a page), called
  by name, rather than a register read and two register writes at each site. The one-door design is in the
  `zxnext-c-to-asm` skill. **Measured:** with a C register writer that takes two pushed arguments, a save, map and
  restore cost about 24 bytes a site; the shared pair, taking the page in L, about 5. Over the program's 52 sites that
  freed 591 bytes of the main bank in one flavour and 428 in another (the build's room figures).
- Do not hide the swap behind a macro or a per-file helper the checker does not know (see its blind spots).

## Where the constants go
- `--codesegPAGE_nn` moves a module's code only. Its string literals and `const` tables stay in the main bank unless
  the module is also compiled with `--constsegPAGE_nn`.
- Banking the constants is safe only for a **leaf**: no pointer to a banked constant may reach code that runs with
  another page in the slot. Two ways it escapes: a drawing or printing helper that lives in another page, and a
  main-bank wrapper that swaps pages **before** it reads through its pointer argument.
- **Measured:** moving one main-bank module, constants included, into a page that was already loaded freed 838 bytes
  of the main bank (1 020 moved, about 200 spent on the trampoline) and did not grow the `.nex`.

## Interrupt handlers
- An interrupt can arrive with any page in the slot, or with the ROM there during an OS call. The handler's code and
  everything it touches live in the main bank; it never depends on the banked slot and never swaps it.
- A handler never calls a routine that ends in an unconditional `ei`: the handler would nest. Keep a raw variant for
  the handler and a guarded one for the main loop.
- A port that is written as "select, then data" (the sprite slot select, a Next register read through $243B and
  $253B) and is used by both the handler and the main loop needs the main loop's sequence bracketed by `di` / `ei`,
  or run while a flag keeps the handler off it.
- State shared with the handler is `volatile`.

## Code under an open Layer 2 write window
When Layer 2 write paging (port $123B) is open over the addresses a routine runs from, every write to that range
is a pixel. Such a routine makes no store to a static, has no self-modifying code, and never reads the frame buffer
through that range (reads still see the code's own page). Keep its variables in registers, on the stack or in the
main bank.

## Check it with a call graph, not with grep
The measured program runs this check on every commit. The tool is tied to that project's layout and is **not
included**; this is how to build yours:
1. Read the list of banked modules and their pages from the build script's `--codesegPAGE_nn` stages. Derive it;
   never keep a second copy of the list.
2. Parse the C sources into a call graph. Key definitions by file, so a `static` helper with the same name in two
   files stays two functions: a call resolves to the caller's own file first, then to the one external definition.
3. Recognise wrappers by what they do: a paging primitive is a function that writes the slot's MMU register or calls
   the shared pair; a wrapper is a main-bank function that calls one.
4. Walk the graph out of every banked module and stop at wrappers. Fail when what is still reachable calls the OS
   (rule 2) or enters a module in a different page (rule 1). Keep walking into same-page callees: rule 2 covers them.

Its blind spots, both met in practice:
- A function that swaps pages itself is taken for a boundary, so a direct call to it from a page passes the check
  and still freezes the machine. Give such functions a separate paged entry for banked callers.
- A swap hidden behind a helper the checker does not recognise stops being a boundary: in the measured program the
  boundary list fell from 115 entries to 37 and the report filled with false findings. Teach the checker any new
  paging helper in the same change.

## What to report
Which page each new or moved function lives in, every wrapper added and what it restores, the constants' section, the
room before and after in the main bank and in each page touched, and the check's result.

## Additional resources
- The `z88dk-map-room` skill: find what is worth moving before moving it.
- `zxnext-build` (the `zxnext-core` plugin): page caps, room figures and stale objects.
