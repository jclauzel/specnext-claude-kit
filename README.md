# specnext-claude-kit

Claude Code skills and `CLAUDE.md` material for ZX Spectrum development, shared by the community: the ZX Spectrum
Next first, the classic 48K/128K Spectrum beside it, and Z80 material common to both.

It is two things in one repository:
- a **Claude Code plugin marketplace**: install the skills with two commands, and get updates when they improve;
- a **CLAUDE.md library**: snippets to paste into your own `CLAUDE.md`, whole templates per project type, and
  community examples.

## One prompt away
Open Claude Code in your own game's folder and paste one of these.

**Use the kit:** see what fits your project, and get the changes offered to you.
```text
Look at https://github.com/jclauzel/specnext-claude-kit and compare it with this project: my CLAUDE.md files,
my build scripts and toolchain, the platform I target (Spectrum Next, classic Spectrum or both), my assembly and
how I test (emulators, real hardware). Tell me which of its plugins, skills, CLAUDE.md snippets and templates
would help me and why, and which would not. Then offer me the concrete changes: the install commands, and the
edits to my CLAUDE.md as a diff. Change nothing until I say yes to each one.
```

**Contribute back:** turn what you have learned into a pull request.
```text
Look at this project's CLAUDE.md files, Claude skills and helper tools, and at
https://github.com/jclauzel/specnext-claude-kit (read its CONTRIBUTING.md first). Find what I have that the kit
does not, and draft a contribution: a plugin under plugins/community/<my-github-name>-<topic>/ and/or CLAUDE.md
snippets, made generic so they work for anyone's project. Keep my privacy: leave out my game's name, code, art,
story and unreleased details, any personal or absolute paths, emails, names I have not made public, keys, tokens
and anything I mark private; only measured claims, each with what it was tested on. Run its tools/validate.py.
Show me every file and the full diff, and ask me before you fork, push or open the pull request.
```

## Which plugins do I need?
| You are... | Install | Why |
|---|---|---|
| writing for the **Spectrum Next** (C, asm or both) | `zxnext-core` and `z80-common` | the Next skills; `zxnext-core` refers to `z80-common`'s measuring |
| using the **ZX-Next-Unite** app, or want Claude to start MAME / CSpect or reach a real Next | add `zxnext-unite-mcp` | a connection to the app (an MCP server), not skills: the app must be running |
| writing for the **classic 48K / 128K Spectrum** | `zx-classic` and `z80-common` | the classic machine's map and timing, plus Z80 measuring |
| writing Z80 for **any other machine** | `z80-common` | measuring T-states and laying out code, for any Z80 |

The plugins in short:
- **`z80-common`** is the shared base: how to measure bytes and T-states instead of guessing, and how to lay out
  branches. Every other plugin builds on it.
- **`zxnext-core`** is the Spectrum Next: building with z88dk `+zxn` (the .nex, room per page, build switches, a build
  table), proving and timing on MAME safely, and writing Z80N first.
- **`zxnext-unite-mcp`** adds tools rather than knowledge: it lets Claude drive the ZX-Next-Unite app (load a disk
  image, put files on it, start MAME or CSpect, push a build to a real Next). See its README to enable the app's server.
- **`zx-classic`** is the classic Spectrum: the memory map, the screen layout, 128K paging and contended memory.

## Install in two commands
```sh
claude plugin marketplace add jclauzel/specnext-claude-kit
claude plugin install zxnext-core@specnext-claude-kit
```
Then add the others the table above says you need, the same way (`z80-common@specnext-claude-kit`,
`zx-classic@specnext-claude-kit`, `zxnext-unite-mcp@specnext-claude-kit`), or browse them with `/plugin` inside a
session. You do not call a skill by name: Claude loads it by itself when your task matches its description ("build
it", "how much room is left", "time it on MAME"). To run one on purpose, type its plugin and skill name as a
command, for example `/zxnext-core:zxnext-build` or `/z80-common:z80-measure`.

## Platforms and plugins
| Plugin | Platform | Skills | What it gives you |
|---|---|---|---|
| [`z80-common`](plugins/z80-common/) | every Z80 machine | `z80-measure`, `z80-code-layout` | bytes and T-states measured with z88dk-ticks; branch layout |
| [`zxnext-core`](plugins/zxnext-core/) | ZX Spectrum Next | `zxnext-build`, `zxnext-mame`, `z80n-optimize` | z88dk `+zxn` builds and room; MAME proofs; Z80N first |
| [`zxnext-unite-mcp`](plugins/zxnext-unite-mcp/) | ZX Spectrum Next | (an MCP server) | connects the ZX-Next-Unite app: disk images, MAME, CSpect, real Nexts |
| [`zx-classic`](plugins/zx-classic/) | 48K / 128K Spectrum | `zx-memory-map` | memory map, screen layout, paging, contended memory |
| [`community/`](plugins/community/) | any | yours | add your own plugin here |

Each plugin's README says what it was tested on and marks what is untested.

## The CLAUDE.md library
- [`claude-md/snippets/`](claude-md/snippets/): small blocks to paste (Z80N first, memory first, measure do not
  assume, tools in `extra/`, the MAME ROM warning, the scratchpad can be wiped, the ZX-Next-Unite MCP server).
- [`claude-md/templates/`](claude-md/templates/): a whole `CLAUDE.md` per project type (Next with z88dk C, Next with
  sjasmplus, classic Spectrum asm). The untested ones say so.
- [`claude-md/community/`](claude-md/community/): full `CLAUDE.md` files from real projects.

## Docs
- [How CLAUDE.md files layer](docs/how-claude-md-layers.md): user, parent folders, project; what loads when; subagents.
- [Writing a good skill](docs/writing-a-good-skill.md): frontmatter, descriptions that trigger, progressive disclosure.
- [Z80N measured](docs/z80n-measured.md): measured wins and losses only, with bytes and T-states.

## Examples
- [`examples/z80n-hw-timing/`](examples/z80n-hw-timing/): `z80ntime.nex`, a Next program that measures Z80N
  instruction T-states on the hardware by counting raster lines (`test n`, `push nn`, `add hl,a`, `mul d,e` against
  their plain forms, at 3.5 to 28 MHz), shows a table and writes it to a CSV file on the SD card.

## Contribute
Pull requests are welcome: a new skill, a fix, a measurement, your `CLAUDE.md`. Read [CONTRIBUTING.md](CONTRIBUTING.md),
then run the checks locally before you open the pull request:

```sh
python tools/validate.py              # Python 3.9+ with PyYAML (installing it: below)
pwsh -File tools/validate.ps1         # or PowerShell 7, no Python needed
```

On Windows without PowerShell 7, `powershell -ExecutionPolicy Bypass -File tools\validate.ps1` runs the
same checks in the PowerShell built into Windows. Both run on every pull request.

To run the Python version you need Python 3.9 or later and its YAML library, PyYAML, installed once:

```sh
python -m pip install pyyaml          # Windows (use "py -m pip install pyyaml" if "python" is not found)
python3 -m pip install --user pyyaml  # macOS and Linux
```

If pip refuses with "externally managed environment" (recent Linux and Homebrew Pythons), use your system's package
(`sudo apt install python3-yaml` on Debian or Ubuntu, `sudo dnf install python3-pyyaml` on Fedora) or a virtual
environment (`python3 -m venv .venv`, then `.venv/bin/pip install pyyaml` and `.venv/bin/python tools/validate.py`).
Check it with `python -c "import yaml; print(yaml.__version__)"`. No Python? Use the PowerShell version: same checks.

## Licence
MIT, see [LICENSE](LICENSE). Not affiliated with Anthropic or with SpecNext Ltd.
