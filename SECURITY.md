# Security

## What a plugin can do
A Claude Code plugin runs with your user permissions: its skills tell Claude what to do, and its MCP servers and any
hooks run as you. Read a plugin before you install it, as you would any script. The plugins in this repository hold
skills (Markdown), small scripts you can read, and one MCP configuration that points at a server on your own machine
(127.0.0.1); none of them installs hooks.

## What reviewers check
- No hooks, executables in `bin/`, or MCP servers that reach the network unless the pull request explains why, and the
  reviewers agree.
- No instructions that tell Claude to send data anywhere, to disable safety prompts, or to act on hardware or files
  without the user asking.
- No secrets, personal paths or email addresses (`tools/validate.py` checks simple patterns).

## Reporting a problem
If you find a plugin or skill in this repository that could harm a user (a dangerous instruction, a leaked secret, a
malicious script), open an issue titled "Security:" with the file and what you found. Do not paste a live secret into
the issue: describe where it is, and the maintainers will remove it and rewrite history if needed.

The ZX-Next-Unite app's own security notes are in its repository's `docs/MCP_SERVER.md`.
