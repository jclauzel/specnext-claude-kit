# zx-classic

Skills for the classic ZX Spectrum: 16K, 48K, 128K, +2, +2A and +3.

| Skill | What it does |
|---|---|
| `zx-memory-map` | The memory map, screen and attribute addresses, 128K paging, contended memory timings, the ULA port, IM 2 tables |

Install: `claude plugin install zx-classic@zx-claude` (and `z80-common@zx-claude` for measuring and code layout,
which apply to every Z80 machine).

## Tested on
`zx-memory-map` is written from published references (the World of Spectrum FAQ's technical references, the Spectrum
manuals, "The Complete Spectrum ROM Disassembly", the Sinclair Wiki). It has **not** been reviewed by a classic
Spectrum developer or checked on hardware yet: a review is the most useful first contribution here.

## What belongs here (contributions welcome)
This plugin is for anything specific to the original Spectrum family. Ideas:
- building: pasmo, sjasmplus or z88dk `+zx` to a `.tap` or `.tzx`, with a loader; snapshot formats (`.sna`, `.z80`);
- running and proving: Fuse, ZEsarUX, SpecEmu or MAME `spectrum`/`spec128` runs driven from a script, with screenshots;
- timing: racing the beam, multicolour, contention-aware cycle counts, the floating bus;
- sound: the beeper, the 128K AY;
- the +3's disk and the +2A's all-RAM modes.

Shared Z80 material (measuring, layout) goes in `z80-common` instead. See `CONTRIBUTING.md` at the repository root.
