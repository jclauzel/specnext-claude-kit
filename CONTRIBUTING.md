# Contributing

Thank you for sharing what you learned. Everything here is meant to help someone else's Spectrum project, so the
rules are about being accurate, generic and safe.

The quickest way: open Claude Code in your own project and paste the **Contribute back** prompt from the
[README](README.md#one-prompt-away). It drafts the contribution to these rules, keeps your project private and
asks you before it forks, pushes or opens the pull request.

## What you can contribute
| You have | Put it in |
|---|---|
| a skill or a set of skills | `plugins/community/<author>-<topic>/` (see `plugins/community/README.md`) |
| a fix or an improvement to an existing skill | the skill itself; say what you tested it on |
| a measurement (a Z80N win or loss) | `docs/z80n-measured.md`, with bytes, T-states and how you measured |
| a reusable `CLAUDE.md` block | `claude-md/snippets/` |
| a whole `CLAUDE.md` for a project type | `claude-md/templates/` (mark it untested if it is) |
| your project's full `CLAUDE.md` as an example | `claude-md/community/<author>-<project>.md` |

A skill that proves itself in the community folder can later move into one of the main plugins.

## The rules
1. **Nothing private.** No personal paths (home or user folders on any system), no email addresses, no tokens or
   keys, no hashes or names from projects you cannot share. Use "your project's build script", not your own file
   names.
2. **Measured claims only.** "Faster" and "smaller" come with bytes and T-states, and with how they were measured
   (instruction table, z88dk-ticks, MAME, hardware).
3. **Say what you tested on.** Each plugin README lists the machine or emulator and version, the core, the toolchain.
   Mark anything untested as untested.
4. **Safe by default.** A skill that runs tools tells Claude how to run them safely: copies of disk images, never the
   originals; limits on concurrent emulators; nothing left running; hardware deploys only when the user asks.
5. **Formats** (checked by `tools/validate.py`): UTF-8, a final newline, no trailing spaces, Markdown lines at most
   120 characters outside tables and code blocks; every `SKILL.md` has `name` (the same as its folder) and
   `description`; `plugin.json` and the marketplace entry agree.

## Before you open a pull request
```sh
python tools/validate.py              # needs Python 3.9+ and PyYAML (see below)
pwsh -File tools/validate.ps1         # or the same checks in PowerShell 7, no Python needed
powershell -ExecutionPolicy Bypass -File tools\validate.ps1   # or Windows PowerShell 5.1, built into Windows
claude plugin validate .              # optional, if you have Claude Code
claude --plugin-dir plugins/<yours>   # optional: try the skill in a session
```

To run the Python version you need Python 3.9 or later and its YAML library, PyYAML, installed once:

```sh
python -m pip install pyyaml          # Windows (use "py -m pip install pyyaml" if "python" is not found)
python3 -m pip install --user pyyaml  # macOS and Linux
```

If pip refuses with "externally managed environment" (recent Linux and Homebrew Pythons), use your system's package
(`sudo apt install python3-yaml` on Debian or Ubuntu, `sudo dnf install python3-pyyaml` on Fedora) or a virtual
environment (`python3 -m venv .venv`, then `.venv/bin/pip install pyyaml` and `.venv/bin/python tools/validate.py`).
Check it with `python -c "import yaml; print(yaml.__version__)"`. No Python? Use the PowerShell version: same checks.

Fill in the pull request template. One topic per pull request keeps reviews quick.

## Reviews
The maintainers listed in `.github/CODEOWNERS` review pull requests. Expect questions about what a skill was tested
on and where its numbers came from: that is the point of the repository, not a hurdle.

## Licence
By contributing you agree that your contribution is released under the repository's MIT licence.
