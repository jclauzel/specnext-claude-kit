# z80-common

Skills shared by every Z80 machine (classic Spectrum, Spectrum Next, and any other Z80 target z88dk supports).

| Skill | What it does |
|---|---|
| `z80-measure` | Measure bytes and T-states with z88dk (`z88dk-z80asm` + `z88dk-ticks`); a C-against-asm harness; the `push nn` byte-order quirk of `z88dk-ticks` (matters only for Z80N) |
| `z80-code-layout` | Make the common branch fall through; branch costs taken and not taken; loop shapes |

Install: `claude plugin install z80-common@specnext-claude-kit`. The skills run as `/z80-common:z80-measure` and
`/z80-common:z80-code-layout`, and Claude loads them on its own when a task matches.

## Tested on
- `scripts/measure.py` and every file in `skills/z80-measure/examples/`: run with z88dk's `z88dk-z80asm` and
  `z88dk-ticks` v0.14c beta (`-mz80n` and `-mz80`), Python 3.14, on Windows. The figures below are that run's output.
- The harness advice and the `push nn` quirk: from a z88dk `+zxn` game project's C-against-asm harnesses.
- Not tested: macOS and Linux (the script uses only the standard library and should work there).

## Measured examples (`python scripts/measure.py examples/*.asm`)
| Snippet | Bytes | T-states (z88dk-ticks) |
|---|---|---|
| `addhl-plain` (`ld e,a / ld d,0 / add hl,de`) | 4 | 22 |
| `addhl-z80n` (`add hl,a`) | 2 | 8 |
| `mul-plain` (8x8 shift-and-add loop, D=$5A E=$C3) | 16 | 371 |
| `mul-z80n` (`mul d,e`) | 2 | 8 |
| `shift-plain` (`sla e / rl d` three times) | 12 | 48 |
| `shift-z80n` (`ld b,3 / bsla de,b`) | 4 | 15 |
| `pushnn-plain` (`ld hl,nn / push hl`) | 4 | 21 |
| `pushnn-z80n` (`push nn`) | 4 | 23 |
| `test-plain` (`and n`) | 2 | 7 |
| `test-z80n` (`test n`) | 3 | 18 |
| `branch-taken` (100 passes) | 9 | 3202 |
| `branch-fallthrough` (100 passes) | 13 | 2714 |

`test n`: z88dk-ticks counts 18 T, while the SpecNext wiki's table gives 11 T. One of them is wrong; until someone
measures it on a Next, treat both figures as unconfirmed. Either way it loses to `and n` when A may be destroyed.

## Contributing
Add a snippet pair to `skills/z80-measure/examples/` with both figures in this table, and say what you ran it on.
