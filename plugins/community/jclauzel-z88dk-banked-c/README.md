# jclauzel-z88dk-banked-c

For ZX Spectrum Next programs written in C with z88dk that have outgrown the main bank: finding where the bytes go,
and keeping code that runs from banked pages safe. It adds to `zxnext-core` (building, room figures, the shared bank
door) and repeats none of it.

| Skill | What it does |
|---|---|
| `z88dk-map-room` | Rank a z88dk `.map` by symbol size in the main bank and in each banked page (`scripts/map_report.py`); library code the source never names; the no-console startup `-startup=31` and the heap pragmas; reading room figures without being fooled (room that only moved, big structs as locals under zsdcc) |
| `zxnext-banked-code` | The rules for C code in pages that share one MMU slot: no direct call between two pages, no OS call without a main-bank wrapper, trampolines that restore the page they found, where constants go, interrupt handlers, code under an open Layer 2 write window, and a call-graph check to build for your project |

Install: `claude plugin install jclauzel-z88dk-banked-c@specnext-claude-kit` (with `zxnext-core@specnext-claude-kit`,
which these skills refer to).

## Tested on
- **Where the rules and figures come from:** one z88dk `+zxn` application (C with zsdcc `-clib=sdcc_iy -SO3
  --max-allocs-per-node200000 --opt-code-size`, some Z80N assembly, a main bank at $8000 and a dozen 8 KB code pages
  that share MMU slot 1), built in several flavours and released, run on an N-Go (an issue 2 board), a KS2 and a KS3.
  z88dk nightly of 2026-08-10 for the later figures; the `-startup=31` figure is from an earlier 2026 z88dk whose
  exact build was not recorded.
- **Byte figures** are differences in that project's own build room figures (free bytes in the main bank and in each
  page), before and after the change named. They are one program's numbers: expect the direction, not the amount.
- **`scripts/map_report.py`:** run with Python 3.14 on Windows on three maps of that application. For the main area
  its sizes equal those of the PowerShell tool it was ported from (the 25 biggest symbols, all three maps; only the
  order of equal sizes differs). The per-page areas are new in the port: run on the same maps, not checked against
  another tool. Not tested: macOS and Linux (standard library only), maps from targets other than `+zxn`.
- **The freeze after an OS call from banked code:** seen twice on the N-Go before the wrappers existed, not since.
- **The call-graph check:** described, not included. The original is a PowerShell script tied to one project's build
  script; the steps and blind spots listed are that script's.
- **Not tested:** the generic wording of both skills on another project; pages mapped in a slot other than slot 1;
  sccz80 (the notes on locals are zsdcc's).
