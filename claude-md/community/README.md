# Community CLAUDE.md files

Full `CLAUDE.md` files from real projects, shared as examples. Read them for ideas; copy what fits your project.

## Add yours
1. Create `claude-md/community/<author>-<project>.md` (lowercase, hyphens; `<author>` is your GitHub name).
2. Start the file with a short comment block: the platform (Next, 48K, 128K), the toolchain (z88dk, sjasmplus,
   pasmo), how long you have used it, and anything you would change.
3. Remove anything private before you open the pull request: personal paths, email addresses, machine names, tokens,
   and names of projects you cannot share. `python tools/validate.py` catches some of it, not all.
4. Keep Markdown lines at most 120 characters (tables and code blocks are exempt).

Short reusable blocks belong in `claude-md/snippets/`; whole starting points in `claude-md/templates/`.
