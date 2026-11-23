---
name: ql-next-core
description: Program the ZX Spectrum Next's QL core - telling it apart from any other QL before touching its registers, what the 2024 and 2026 cores each have (win1_ or SDA1_, the ESP1 / SER3 driver or the bare UART), the Wi-Fi module through the core's UART (baud divisor, 1 KB FIFO, no flow control), the 1 MHz counter, 256 colours through the SCN driver and twin screens, the PS/2 mouse (QIMI) and the hardware sprite, and getting files onto it. Use this skill whenever code or SuperBASIC runs on the Next's QL core, addresses $800000 or $C00000, mentions ESP1, SER3, SDA1_, SCN, QIMI or twin screens, or the user asks why something works on an emulator or QPC2 but not on the Next's QL core, even if they only say "on the KS2". Not for NextZXOS, .nex or Z80N programs, since with the QL core loaded the Next is a 68000 QL.
---

# The ZX Spectrum Next's QL core

With this core loaded the Next is a Sinclair QL: a 68000-type CPU, Minerva and Toolkit II, QDOS devices. NextZXOS,
Next registers ($243B), the Copper, Layer 2, `.nex` files and Z80N do not exist there.

Say which core and machine each claim comes from. In these notes **2024** and **2026** are the cores, **KS2** is the
machine they were run on. No claim here was checked on a KS3 or on a 2025 core.

| | 2024 core | 2026 core |
|---|---|---|
| ROM seen | Minerva 1.98a1, Toolkit II 2.36 | not recorded |
| Files | a QL disk image as `win1_` | the FAT32 card as `SDA1_`, no disk image at start |
| Wi-Fi module | a driver from the image's boot: `SER3`, also named `ESP1` | no driver loaded: use the UART registers |
| ID word at `$80001E` | **not decoded**: a read returns whatever was last on the bus | `$4E32` (20018) |
| Network | no `TCP_` device | no `TCP_` device |

## First rule: know the machine before you touch `$80xxxx`
On QPC2, a Q68 or any QL with a lot of RAM those addresses are ordinary memory, perhaps your own. Writing a baud divisor
there corrupts it. Use these gates, in this order:
1. **`ESP1` opens** (`io_open("ESP1", 0)`, or `FTEST("ESP1")` = 0, quoted): the Next's core, with its driver. No other
   QL has a device of that name. Open with key 0, which creates nothing; -9 (in use) also means it exists.
2. **No driver?** Only if RAM ends at or below `$800000` (system variables + `$20`), read the word at `$80001E`; it is
   the core if it equals `$4E32`. Test for that exact value: on the 2024 core a read is noise, so "not zero" means
   nothing, and two reads in a row can differ.
3. Write nothing at `$80xxxx` or `$C0xxxx` before one of the two has passed.

Find the system variables (`MT.INF` in C, `VER$(-2)` in Minerva or SMSQ/E); they are at `$28000`, or at `$30000` when
Minerva was started with twin screens.

## Drives
Use `win1_` when it answers; on the Next's core only, `SDA1_` when it does not. Do not ask for `SDA1_` on other
machines. Do not probe microdrives: a missing cartridge spins the motor and waits.

## Getting a program onto the 2024 core
The FAT32 card is not a QDOS device there. The disk image brings two programs: `EW win1_sdir,#1` lists the card, and
`EW win1_scopy;'source win1_target'` copies from it.
- **`scopy` ends with a non-zero code even after `Done!`**, and `EW` then stops the SuperBASIC program that called it.
  In a program, start it with `EX`, then poll: `FTEST(file)` = 0 first, and `FLEN(\file)` equal to the expected size.
- Copy the raw job, then install it with `SEXEC` (the `ql-c-build` skill): a file from the card has no QDOS header.
- `LRUN` and `LOAD` need the program on a QDOS device: `scopy` it to `win1_` too.

## The Wi-Fi module (ESP)
Read `references/registers.md` for the UART registers before you write a driverless version. What matters in both:
- AT firmware on the KS2: 1.6.2.0 (SDK 2.2.1), 115200 baud, 8N1, and it stays joined to the Wi-Fi across a core switch.
- **There is no flow control and no reset line** on the QL side, and the FIFO is 1 024 bytes: 5 ms at 2 000 000
  baud. 115200 is safe; 1 152 000 held on the 2024 core (a 663 KB transfer, CRC equal); **2 000 000 lost data**.
  Poll, do not sleep, while data may come: one 20 ms frame brings 2 304 bytes at 1 152 000.
- Ten times the rate gained about 20 % on small transfers: the time goes to the round trip for each block (the `CIPSEND`
  prompt, `SEND OK`, the peer's answer). Send bigger blocks before raising the rate.
- Look for the module at 115200, then at the faster rates: an earlier run may have left it fast. **Put it back to 115200
  on exit**, or NextZXOS's tools will not find it.
- Replies can hold NUL bytes (power-up noise): search the bytes with a length, not `strstr`. A wait that counts only
  empty reads never ends while a peer floods you: count time as well.
- `CIPMUX=1` can answer `link is builded`: send `CIPCLOSE=5` first. With no reset line, a module that never gives its
  `>` prompt needs a power cycle: say so to the user.

## 256 colours: the SCN driver
Simon N Goodwin's SCN (<https://simon.mooli.org.uk/QL/SCN/>, CC BY-NC-SA 4.0: do not bundle it) adds a `SCN_` device
with a 256 x 256 colour screen. Read `references/scn.md` first. The trap that costs hours: on the 2024 core SCN puts its
screen over both QL screens, so **Minerva must be started with twin screens** (F3 or F4 at its start screen; on the
Next: reset, hold NMI and press 3). Otherwise loading it answers "in use".

## The mouse and the hardware sprite
A PS/2 mouse is read through a QIMI interface at `$1BFxx`; the KS2's sprite engine is at `$C00000`. Read
`references/mouse.md`: those addresses acknowledge on a read, so one wrong access size eats the movement.

## Keyboard (KS2)
BREAK gives ESC, GRAPH is CTRL, EXTEND is ALT. SHIFT and ALT with the cursor keys reach a program (seen in use).

## Prove it
- sQLux and QPC2 cannot show any of this. A register program needs the core, and needs a path that stays quiet on every
  other QL: run that path on an emulator.
- Write a short SuperBASIC probe first (`PEEK` only, results to a file), have the user run it, and code against its
  figures. Guesses made before one such probe were wrong by a factor of ten.
- Ask the user to run things on the real machine; never deploy to it unasked.
