# Community plugins

Your own skills, packaged as a plugin under `plugins/community/<author>-<topic>/`, for example
`plugins/community/alice-tilemaps/`. Start from `_template/`.

## Add a plugin
1. Copy `_template/` to `plugins/community/<author>-<topic>/` (lowercase letters, digits and hyphens; `<author>` is
   your GitHub name).
2. Edit `.claude-plugin/plugin.json`: `name` is the folder name, plus a one-line `description`, a `version` and your
   `author` (name and GitHub URL; no email address).
3. Rename `skills/example-skill/` to your skill's name and set the same `name` in its `SKILL.md` frontmatter. Write the
   `description` as a trigger: what the skill does, then "Use this skill whenever ...". Add more skills beside it.
4. Fill in `README.md`: what each skill does and **what you tested it on** (machine or emulator and version, core,
   toolchain). Mark anything untested as untested.
5. Add an entry to `.claude-plugin/marketplace.json` at the repository root:

   ```json
   {
     "name": "alice-tilemaps",
     "source": "./plugins/community/alice-tilemaps",
     "description": "One line, the same as plugin.json"
   }
   ```

6. Run `python tools/validate.py` or `tools/validate.ps1` (PowerShell, no Python needed), and `claude plugin
   validate .` if you have Claude Code, then open a pull request.

## Rules
- Nothing private: no personal paths, no email addresses, no tokens, no project names you cannot share.
- Measured claims only: when a skill says one form is faster or smaller, give the bytes and T-states and say how they
  were measured.
- A skill that runs tools (emulators, builds) must say how to run them safely: copies of disk images, never the
  originals; no processes left running.
- One topic per plugin; keep `SKILL.md` under 500 lines and move detail into `references/`.

`docs/writing-a-good-skill.md` explains frontmatter, descriptions that trigger, and progressive disclosure.
