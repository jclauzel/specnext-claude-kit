# Writing a good skill

A skill is a folder with a `SKILL.md`: YAML frontmatter, then the instructions Claude follows when the skill loads.
In a plugin, skills live in `skills/<name>/SKILL.md` and run as `/<plugin>:<name>`. The official reference is
<https://code.claude.com/docs/en/skills>; this page is the short version, with what we learned on Spectrum work.

## Frontmatter
```yaml
---
name: zx-memory-map
description: What the skill does, then when to use it. Use this skill whenever ...
---
```
- `name`: lowercase letters, digits and hyphens, the same as the folder (this repository's validator checks it).
- `description`: the most important field. Claude sees every skill's description on every turn and loads the full
  skill only when the description matches the task. The listing truncates the description (with `when_to_use`, if
  set) at 1 536 characters: put the key use case first.
- Optional fields exist (`allowed-tools`, `disable-model-invocation`, `paths`, `when_to_use`, and others). Use
  `disable-model-invocation: true` for skills with side effects that should run only when typed.

## Descriptions that trigger
- Say **what** the skill does in concrete nouns (".nex", "z88dk +zxn", "MAME specnext_ks3", "contended memory").
- Then say **when**: "Use this skill whenever you build, rebuild, compare or check the size of a Next program ...".
- Add the words people actually type: "build it", "how much room is left", "is level 5 still under budget?".
- Add "even if ..." for the indirect cases: "even if MAME is not named".
- Do not describe the skill's inner steps there; that is what the body is for.

## The body: progressive disclosure
- `SKILL.md` loads in full when the skill is used: keep it under 500 lines, and better well under. Lead with the
  rules that have bitten before, each with its reason in a few words.
- Put long material in files beside it (`references/*.md`, `scripts/`, `examples/`) and say in `SKILL.md` when to
  read or run each one. Those files cost nothing until Claude opens them.
- Refer to bundled files with `${CLAUDE_SKILL_DIR}` (for example `python ${CLAUDE_SKILL_DIR}/scripts/measure.py`),
  so the path works wherever the plugin is installed.
- Commands exactly as typed, in code spans. Numbers with their units and where they came from.

## What makes Spectrum skills useful
- **Hard-won rules with reasons:** "copy the SD image for every run (MAME writes to it)" beats "be careful".
- **Measured claims only:** bytes and T-states, and how they were measured (table, z88dk-ticks, emulator, hardware).
- **Tested-on notes** in the plugin README: machine or emulator and version, core, toolchain. Mark the untested.
- **Generic, not private:** no personal paths, project names or hashes from your own builds; show a generic example.
- **Safety for tools that run things:** emulators, builds and hardware deploys need limits (process caps, copies,
  never on the user's originals, nothing left running).

## Check it
- `python tools/validate.py` in this repository (frontmatter, names, privacy patterns, line lengths).
- `claude plugin validate plugins/<your-plugin>` if you have Claude Code.
- Try it: `claude --plugin-dir plugins/<your-plugin>`, then ask for the task in plain words and see whether the skill
  loads on its own.
