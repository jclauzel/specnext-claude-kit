# specnext-claude-kit

Claude Code skills and `CLAUDE.md` material for ZX Spectrum development, shared by the community: the ZX Spectrum
Next first (its QL core included), the classic 48K/128K Spectrum beside it, and Z80 material common to both.

It is two things in one repository:
- a **Claude Code plugin marketplace**: install the skills with two commands, and get updates when they improve;
- a **CLAUDE.md library**: snippets to paste into your own `CLAUDE.md`, whole templates per project type, and
  community examples.

## One prompt away
Open Claude Code in your own game's folder and paste one of these.

**Use the kit:** see what fits your project, and get the changes offered to you. Commit your project first, so every
change it makes shows in `git diff` and can be undone (see "Install in two commands").
```text
Look at https://github.com/jclauzel/specnext-claude-kit and compare it with this project: my CLAUDE.md files,
my build scripts and toolchain, the platform I target (Spectrum Next, its QL core, classic Spectrum), my assembly and
how I test (emulators, real hardware). Tell me which of its plugins, skills, CLAUDE.md snippets and templates
would help me and why, and which would not. Then offer me the concrete changes: the install commands, and the
edits to my CLAUDE.md as a diff. Change nothing until I say yes to each one.
```

**Contribute back:** turn what you have learned into a pull request. Tip: run `/doctor` in your project first; it
trims and checks your `CLAUDE.md` files and skills, so what you share is lean and loads (see CONTRIBUTING.md).
```text
Look at this project's CLAUDE.md files, Claude skills and helper tools, and at
https://github.com/jclauzel/specnext-claude-kit (read its CONTRIBUTING.md first). Compare what I have with
everything the kit already has, including its open pull requests and issues, and skip what is already covered;
where mine overlaps an existing skill or snippet, propose an improvement to that one instead of a second version.
For the rest, draft a contribution: a plugin under plugins/community/<my-github-name>-<topic>/ and/or CLAUDE.md
snippets, made generic so they work for anyone's project. Keep my privacy: leave out my game's name, code, art,
story and unreleased details, any personal or absolute paths, emails, names I have not made public, keys, tokens
and anything I mark private; only measured claims, each with what it was tested on. Run its tools/validate.py.
Show me every file and the full diff, and ask me before you fork, push or open the pull request.
```

## Which plugins do I need?
| You are... | Install | Why |
|---|---|---|
| writing for the **Spectrum Next** (C, asm or both) | `zxnext-core` and `z80-common` | the Next skills; `zxnext-core` refers to `z80-common`'s measuring |
| writing for the **Next's QL core**, or any Sinclair QL | `zxnext-ql` | a 68000 machine: none of the Z80 plugins apply to it |
| using the **ZX-Next-Unite** app, or want Claude to start MAME / CSpect or reach a real Next | add `zxnext-unite-mcp` | a connection to the app (an MCP server), not skills: the app must be running |
| writing for the **classic 48K / 128K Spectrum** | `zx-classic` and `z80-common` | the classic machine's map and timing, plus Z80 measuring |
| writing Z80 for **any other machine** | `z80-common` | measuring T-states and laying out code, for any Z80 |

The plugins in short:
- **`z80-common`** is the shared base: how to measure bytes and T-states instead of guessing, and how to lay out
  branches. The other Z80 plugins build on it.
- **`zxnext-core`** is the Spectrum Next: building with z88dk `+zxn` (the .nex, room per page, build switches, a build
  table), proving and timing on MAME safely, writing Z80N first, and rewriting the hottest C in Z80N asm without
  changing what the player sees.
- **`zxnext-ql`** is the Sinclair QL, with the Next's QL core first: C with qdos-gcc, QDOS and SMSQ/E, SuperBASIC, the
  core's own hardware, and scripted runs on sQLux. It stands alone.
- **`zxnext-unite-mcp`** adds tools rather than knowledge: it lets Claude drive the ZX-Next-Unite app (load a disk
  image, put files on it, start MAME or CSpect, push a build to a real Next). See its README to enable the app's server.
- **`zx-classic`** is the classic Spectrum: the memory map, the screen layout, 128K paging and contended memory.

## Install in two commands
**Before you start, take a backup.** Installing a plugin writes nothing into your project (see below), but the steps
around it can: the **Use the kit** prompt edits your `CLAUDE.md`, and `/doctor` (after installing) can trim your
`CLAUDE.md` files and skills. So first commit your project (`git status` clean, ideally pushed), or copy its folder if
it is not in git, and copy your own `~/.claude/CLAUDE.md`, `~/.claude/skills/` and `~/.claude/settings.json` if you
have them. Then any change you regret is one `git checkout` or one copy away.

```sh
claude plugin marketplace add jclauzel/specnext-claude-kit
claude plugin install zxnext-core@specnext-claude-kit
```
Then add the others the table above says you need, the same way (`z80-common@specnext-claude-kit`,
`zx-classic@specnext-claude-kit`, `zxnext-ql@specnext-claude-kit`, `zxnext-unite-mcp@specnext-claude-kit`), or browse
them with `/plugin` inside a session. You do not call a skill by name: Claude loads it by itself when your task matches
its description ("build it", "how much room is left", "time it on MAME"). To run one on purpose, type its plugin and
skill name as a command, for example `/zxnext-core:zxnext-build` or `/z80-common:z80-measure`.

**After installing, tidy up with `/doctor`.** Start a new session in your project and run `/doctor`. On recent Claude
Code it checks your `CLAUDE.md` files and skills next to the ones you just installed: a skill of your own that now
does the same job as a kit skill, `CLAUDE.md` lines the kit's skills now cover, unused skills. It asks before changing
anything; review each change with `git diff` and keep your project's rules where they differ from the kit (see "Can it
interfere" below). Run it again in each project where you use the kit, and after a big kit update. Older Claude Code
has a simpler `/doctor` (installation checks only); then compare by hand, or paste the **Use the kit** prompt.

## How it works, and what it changes in your setup
Know what you are adding before you install it.

**What installing does**
- Claude Code copies the plugins you install into its own plugin folder (under `~/.claude/plugins`). Nothing is copied
  into your projects.
- By default a plugin is installed for you (user scope), so it is available in **every** project you open. To keep it to
  one project, install it from that project with `--scope project` (shared with the repository through its
  `.claude/settings.json`) or `--scope local` (only you).

**What it never does**
- It never edits your code, your `CLAUDE.md`, your settings or any file by itself, and it has no hooks or background
  scripts: nothing runs when a session starts, and the kit makes no network calls. The skills are instructions Claude
  reads; Claude still asks before acting, as your permission settings say.
- The `claude-md/` snippets and templates are not installed: they only change your `CLAUDE.md` if you copy them in.
- `zxnext-unite-mcp` is the one plugin that adds tools: a connection to the ZX-Next-Unite app on your own PC
  (`127.0.0.1`). It does something only when the app is running and Claude uses one of its tools.

**How a skill loads (and what it costs)**
Claude reads each installed skill's name and one-line description at the start of every session, so it knows the skill
exists; the rest of the skill loads only when your task matches (or when you run it as `/plugin:skill`), and a skill's
`references/` files only when it needs them. Estimates, at about 4 characters a token:

| Plugin | Always in context (every session) | When a skill is used |
|---|---|---|
| `zxnext-core` (4 skills) | about 760 tokens | about 900-1 500 per skill, plus 600-750 if it reads its reference |
| `z80-common` (2 skills) | about 230 tokens | about 650-900 per skill |
| `zxnext-ql` (5 skills) | about 920 tokens | about 1 200-1 700 per skill, plus 600-1 300 per reference it reads |
| `zx-classic` (1 skill) | about 150 tokens | about 1 450 |
| `zxnext-unite-mcp` | the names of its tools (a few hundred tokens); each tool's details load only when used | the tool calls you make |

So the Next set (`zxnext-core` and `z80-common`) adds about 1 000 tokens to every session, and a skill in use adds one
to two thousand more for that task. After installing, `claude plugin details zxnext-core@specnext-claude-kit` shows the
projected cost on your machine, and `/context` in a session shows what is loaded right now.

**Can it interfere with what I already have?**
- **Skills load on matching tasks, in every project** (user scope): a Z80 or emulator task in another project may load
  them too. If that is not wanted, install with `--scope project`, or `claude plugin disable` it where you do not
  want it.
- **Your `CLAUDE.md` is your project's rule.** If a skill's advice differs from it (another build system, another
  budget, another emulator), say which wins in your `CLAUDE.md` and Claude follows it.
- **Overlapping skills:** if you already have your own skill for the same job, keep one (`/doctor` finds unused ones),
  or Claude may read both.
- **Nothing to undo but the install:** disable or uninstall a plugin (below) and it stops loading; nothing else was
  changed.

## Is the kit being used?
Skills load by themselves, so it is fair to ask whether they did. Check from the outside in.

**1. Installed and enabled?**
- `claude plugin list` shows each plugin you installed, its version and whether it is enabled. In a session,
  `/plugin` shows the same under **Installed**.
- Installed for one project only (`--scope project` or `local`)? Then it loads only in that project.
- Just installed or updated? A running session does not see it: run `/reload-plugins` or start a new session.

**2. Does this session know the skills?**
- `/skills` lists the skills this session can load. The kit's appear with their plugin's name in front:
  `zxnext-core:zxnext-build`, `zxnext-core:zxnext-mame`, `z80-common:z80-measure` and so on.
- `/context` shows what is in context right now, skills included (their names and descriptions cost about 1 000 tokens
  for the Next set, see the table above).
- `zxnext-unite-mcp`: `/mcp` should show `zx-next-unite` as connected, with its tools. If it says failed, the app is not
  running or its server is off (see that plugin's README).

**3. Was a skill used for this task?**
- When Claude loads a skill, the conversation shows it: a `Skill` tool call naming it (for example
  `zxnext-core:z80n-optimize`) followed by **Successfully loaded skill**. In the desktop app it is a tool row you can
  expand. No such line means Claude answered from its own knowledge and your `CLAUDE.md`, not from the kit.
- The ZX-Next-Unite tools show as tool calls whose names begin with `mcp__plugin_zxnext-unite-mcp_zx-next-unite__`
  (or `mcp__zx-next-unite__` if you connected with `claude mcp add`).
- The answers carry the skills' habits: bytes and T-states before and after each change, measured with `z88dk-ticks`
  rather than guessed; the Z80N form named in place of the plain Z80 one; a 0 build checked byte for byte with an MD5;
  a frame report read as the worst line against the budget. Seeing these is a good sign; their absence on a task
  that matches a skill is a sign it did not load.
- Not sure? Ask Claude: "Which skills and MCP tools did you use in this session?" It can read its own transcript.

**4. A quick test.** In a project, ask something only a skill answers in its way, for example:
```text
Measure the bytes and T-states of "add hl,a" against "ld e,a / ld d,0 / add hl,de" on the Z80N.
```
You should see `z80-common:z80-measure` (and perhaps `zxnext-core:z80n-optimize`) load, then a measurement with
`z88dk-ticks`, not figures from memory.

**If a skill does not load when you expect it to**
- Run it by name to rule out the install: `/zxnext-core:zxnext-build`. If that works, the task's wording did not match
  the skill's description; say what you are doing in the skill's words ("build it", "time it on MAME"), or open an
  issue with the prompt you used so the description can be improved.
- Your own skill or your `CLAUDE.md` may cover the same job and win: that is by design (see "Can it interfere" above).
  Keep one of the two; `/doctor` finds unused skills.
- `claude plugin details zxnext-core@specnext-claude-kit` lists the skills Claude Code found in the plugin; a skill
  missing there did not install.

## Updating the kit and your plugins
When a new release is out (see [Releases](https://github.com/jclauzel/specnext-claude-kit/releases)), two steps:

```sh
claude plugin marketplace update specnext-claude-kit   # 1. fetch the kit's latest catalogue from GitHub
claude plugin update zxnext-core@specnext-claude-kit   # 2. update each plugin you installed (repeat per plugin)
```

Then restart Claude Code (or start a new session): a plugin update applies at the next start.

**Get updates automatically** (set it once): in a Claude Code session run `/plugin`, open the **Marketplaces** tab,
select `specnext-claude-kit` and choose **Enable auto-update**. Third-party marketplaces like this one start with it
off, and only you can turn it on. From then on, a little while after your first message in a session (a random wait of
up to ten minutes), Claude Code refreshes the kit and updates the plugins you installed. It then tells you
`Plugin updated: <name> · Run /reload-plugins to apply`: run `/reload-plugins` (or start a new session) to use the new
version; the running session keeps the old one until then. It is skipped when updates are turned off on your machine
(`DISABLE_UPDATES`, `DISABLE_AUTOUPDATER` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`; `FORCE_AUTOUPDATE_PLUGINS=1`
turns plugin updates back on). The kit itself never checks for updates or calls the network: Claude Code does it.

- `claude plugin list` shows what you have installed and each plugin's version.
- `claude plugin marketplace update` with no name refreshes every marketplace you have added.
- Inside a session, `/plugin` opens the same thing as a menu: browse the marketplace, see installed plugins and update
  them from there.
- A release that changes only the docs (like 0.1.1) changes no plugin: step 1 is enough to see the new README text on
  GitHub, and step 2 reports that your plugins are already up to date.
- Copied a snippet or template from `claude-md/` into your own `CLAUDE.md`? Those are not installed, so they do not
  update by themselves: compare yours with the new version (the release notes say what changed), or paste the README's
  **Use the kit** prompt again and Claude will offer you the changes.

## Uninstalling
To pause a plugin without removing it, disable it, and enable it again later:

```sh
claude plugin disable zxnext-core@specnext-claude-kit
claude plugin enable zxnext-core@specnext-claude-kit
```

To remove plugins, uninstall each one you installed, then remove the kit's marketplace:

```sh
claude plugin uninstall zxnext-core@specnext-claude-kit        # repeat for each one you installed
claude plugin marketplace remove specnext-claude-kit           # forget the kit itself (after its plugins are gone)
```

- `claude plugin list` shows what is still installed. Inside a session, `/plugin` does the same from a menu.
- A plugin installed for one project (`--scope project` or `local`) is uninstalled with the same `--scope`.
- `--keep-data` keeps a plugin's saved data (`~/.claude/plugins/data/...`) in case you install it again.
- Restart Claude Code (or start a new session) so the removed skills stop loading.
- Anything you copied from `claude-md/` into your own `CLAUDE.md` is yours: uninstalling does not touch it; delete those
  lines yourself if you no longer want them. If you connected ZX-Next-Unite with `claude mcp add`, remove that with
  `claude mcp remove zx-next-unite`.

## Platforms and plugins
| Plugin | Platform | Skills | What it gives you |
|---|---|---|---|
| [`z80-common`](plugins/z80-common/) | every Z80 machine | `z80-measure`, `z80-code-layout` | bytes and T-states measured with z88dk-ticks; branch layout |
| [`zxnext-core`](plugins/zxnext-core/) | ZX Spectrum Next | `zxnext-build`, `zxnext-mame`, `z80n-optimize`, `zxnext-c-to-asm` | z88dk `+zxn` builds and room; MAME proofs; Z80N first; hot C rewritten in Z80N asm |
| [`zxnext-ql`](plugins/zxnext-ql/) | the Next's QL core, any Sinclair QL | `ql-c-build`, `ql-next-core`, `ql-qdos-c`, `ql-superbasic`, `ql-emulators` | qdos-gcc's traps and a scanner for its a6 bug; the core's registers; QDOS from C; a SuperBASIC linter; sQLux runs |
| [`zxnext-unite-mcp`](plugins/zxnext-unite-mcp/) | ZX Spectrum Next | (an MCP server) | connects the ZX-Next-Unite app: disk images, MAME, CSpect, real Nexts |
| [`zx-classic`](plugins/zx-classic/) | 48K / 128K Spectrum | `zx-memory-map` | memory map, screen layout, paging, contended memory |
| [`jclauzel-z88dk-banked-c`](plugins/community/jclauzel-z88dk-banked-c/) | ZX Spectrum Next (community) | `z88dk-map-room`, `zxnext-banked-code` | where a z88dk program's bytes go; keeping C code in banked pages safe |
| [`community/`](plugins/community/) | any | yours | add your own plugin here |

Each plugin's README says what it was tested on and marks what is untested.

## The CLAUDE.md library
- [`claude-md/snippets/`](claude-md/snippets/): small blocks to paste (Z80N first, memory first, measure do not
  assume, tools in `extra/`, the MAME ROM warning, the scratchpad can be wiped, the ZX-Next-Unite MCP server, what a
  new assembly routine must keep).
- [`claude-md/templates/`](claude-md/templates/): a whole `CLAUDE.md` per project type (Next with z88dk C, Next with
  sjasmplus, classic Spectrum asm, the QL core in C). The untested ones say so.
- [`claude-md/community/`](claude-md/community/): full `CLAUDE.md` files from real projects.

## Docs
- [How CLAUDE.md files layer](docs/how-claude-md-layers.md): user, parent folders, project; what loads when; subagents.
- [Writing a good skill](docs/writing-a-good-skill.md): frontmatter, descriptions that trigger, progressive disclosure.
- [Z80N measured](docs/z80n-measured.md): measured wins and losses only, with bytes and T-states.

## Examples
- [`examples/z80n-hw-timing/`](examples/z80n-hw-timing/): `z80ntime.nex`, a Next program that measures Z80N
  instruction T-states on the hardware by counting raster lines (`test n`, `push nn`, `add hl,a`, `mul d,e` against
  their plain forms, at 3.5 to 28 MHz), shows a table and writes it to a CSV file on the SD card.

## Helper tools
- [`extra/ql-tools/`](extra/ql-tools/): the QL scripts that `zxnext-ql` carries, with their tests.

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
