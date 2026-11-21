# How CLAUDE.md files layer

Claude Code reads instructions from several `CLAUDE.md` files and puts them all in context: they add up, they do not
replace each other. Knowing what loads when lets you put each rule in the right place. This summary follows the
official memory documentation (<https://code.claude.com/docs/en/memory>); check it for changes.

## The layers, broadest first
| Layer | Where | Who it is for |
|---|---|---|
| Managed policy | set by an organisation's IT (a system folder, or managed settings) | everyone on the machine |
| User | `~/.claude/CLAUDE.md` (and `~/.claude/rules/*.md`) | you, in every project |
| Parent folders | `CLAUDE.md` in each folder above the one you start Claude in | everything under that folder |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` (and `./.claude/rules/*.md`) | everyone working in the repo |
| Local | `./CLAUDE.local.md` (add it to `.gitignore`) | you, in this repo only |
| Subfolders | `CLAUDE.md` in a folder below the start folder | loaded when Claude reads or edits a file there |

## What loads when
- **At launch:** the managed file, your user file, and every `CLAUDE.md` and `CLAUDE.local.md` from the filesystem
  root down to the folder you started in. They are concatenated in that order, so the instructions closest to your
  start folder are read last; in each folder `CLAUDE.local.md` comes after `CLAUDE.md`.
- **On demand:** a `CLAUDE.md` in a subfolder loads the first time Claude reads, writes or edits a file in that
  subfolder. Rules in `.claude/rules/` with a `paths:` frontmatter load only when Claude touches a matching file.
- **Imports:** a line `@path/to/file.md` pulls another file in (relative to the importing file, up to four hops deep).
  Imports outside the project ask for approval once. Imports organise a file but do not save context: imported files
  load with the file that imports them.
- **`--add-dir` folders** do not load their `CLAUDE.md` unless `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` is set.
- **AGENTS.md:** by default Claude reads a repo's `AGENTS.md` only when there is no `CLAUDE.md` in the start folder or
  above it. To use both, put `@AGENTS.md` in your `CLAUDE.md`.

## Subagents
- A subagent (one Claude starts with the Agent tool) begins with a fresh context: it does not see your conversation,
  only the brief it is given. It does load the same `CLAUDE.md` layers as the main session.
- Exceptions: the built-in Explore and Plan agents start without your `CLAUDE.md` files, and a custom subagent with
  `omitClaudeMd: true` skips them too. A rule a subagent must follow should therefore be in its brief as well, or
  in a skill it loads.
- Subagents do not preload skills unless their definition lists them, but they can still invoke skills.

## Where to put what (for Spectrum work)
| Rule | Best place |
|---|---|
| "Z80N first, memory first" for all your Next projects | user `~/.claude/CLAUDE.md`, or a parent folder holding all your Next repos |
| This game's build command, memory map, frame budget | the project `CLAUDE.md` |
| Your local paths (emulator folder, SD image location) | `CLAUDE.local.md`, never committed |
| Rules for one part of the tree (`src/asm/`) | a `CLAUDE.md` in that folder, or a path-scoped rule |
| A multi-step procedure (run the build table, prove on MAME) | a skill, which loads only when needed |

A parent-folder `CLAUDE.md` is a good fit for shared Spectrum rules: put your Next repos side by side under one
folder, put the shared rules in that folder's `CLAUDE.md`, and every repo gets them without copying.

## Keep it short
Each `CLAUDE.md` loads in every session, so it costs context every turn. Aim for under about 200 lines per file. Keep
facts and "always do X" rules in `CLAUDE.md`; move procedures into skills. `/memory` opens the loaded files for
editing; `/init` drafts a first project `CLAUDE.md` from the code.
