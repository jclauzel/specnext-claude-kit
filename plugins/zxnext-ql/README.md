# zxnext-ql

Skills for Sinclair QL programs, written for the ZX Spectrum Next's **QL core** and useful on any QL: with that core
loaded the Next is a 68000 machine, so the Z80 and Z80N plugins do not apply (and this one does not need them).

| Skill | What it does |
|---|---|
| `ql-c-build` | Build with qdos-gcc 2.95.3 and C68's library: the toolchain's silent failures, the `-O2` a6 bug and a scanner for it, stack frames, dataspace and headers, installing |
| `ql-next-core` | The Next's QL core: knowing it from other QLs, the 2024 and 2026 cores, the Wi-Fi module's UART, SCN's 256 colours, the PS/2 mouse and the sprite |
| `ql-qdos-c` | QDOS and SMSQ/E calls from C: channels, names, directories, console, keys, the Pointer Environment, 24-bit colour |
| `ql-superbasic` | SuperBASIC's traps on Minerva, Toolkit II and SMSQ/E, and a linter to run on the PC |
| `ql-emulators` | Scripted runs on sQLux, what its Windows build gets wrong, the `TCP_` device, QPC2 |

Install: `claude plugin install zxnext-ql@specnext-claude-kit`. Working on both kinds of Next program? If a project's
`CLAUDE.md` says "Z80N first", say there that its QL part is 68000 code (there is a template for a QL project in
`claude-md/templates/ql-core-c.md`).

## Scripts (MIT)
`a6scan.py`, `stack_frames.py` and `qlheader.py` (`ql-c-build`), `sbasic_lint.py` (`ql-superbasic`), `run_sqlux.py`
(`ql-emulators`). They need Python 3.9 or later. The same files, with their tests, are in `extra/ql-tools/`.

## Tested on
The knowledge comes from a released QL application. What each part was run on:
- **Next's QL core**: a KS2 with the 2024 core (Minerva 1.98a1, Toolkit II 2.36) for files, the Wi-Fi driver, SCN 1.48,
  the mouse and the sprite; a KS2 with the 2026 core for the bare UART and `SDA1_`. **Untested:** the 2025 cores, any
  core on a KS3 or KS1, other boards. `$800030` (the 1 MHz counter) was read in sources only.
- **QPC2** 5.02 with SMSQ/E 3.38: files, `TCP_`, 24-bit colour, the Pointer Environment.
- **sQLux** 1.1.2, the Windows build, Minerva 1.98a1 with Toolkit II 2.36: everything in `ql-emulators`, plus `ptr_gen`
  2.06. Its Linux and macOS behaviour is from its sources, not run.
- **qdos-gcc-win-1.0** (gcc 2.95.3 20010315, C68 libc v4.24.5): `ql-c-build`. Reproduced again for this plugin: the
  linker's exit code 0 on an undefined symbol, the assembler's exit code 0 and empty `.o` on a bad `asm()`.
- **Not run at all**: Q68, Q40, Q60, original QLs with their disk systems, Q-emuLator, SMSQmulator. What is said about
  them comes from documentation and sources.

The skills mark what is unverified. Corrections with the machine, core and version they were seen on are welcome.

## Credits
QL facts come from public work: Minerva (Laurence Reeves, kept by Marcel Kilgus), SMSQ/E (Tony Tebby and others),
Toolkit II, C68 (Dave Walker and others), qdos-gcc (Richard Zidlicky, Graeme Gregory), sQLux, the QL core's published
sources, and SCN by Simon N Goodwin (CC BY-NC-SA 4.0; behaviour described, nothing copied or bundled). None of them
endorses this plugin. Sinclair and QL are trademarks of their owners.
