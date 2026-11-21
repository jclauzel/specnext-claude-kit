# The build table in detail

## Roles and flavours
A **flavour** is one build: a name, the switches it passes, the files it writes. A **role** is a part of the table run
in one worktree. A typical trimmed table for one step:

| Flavour | Switches | Why |
|---|---|---|
| `game` | defaults | what players get |
| `game-new0` | defaults, the new switch at 0 | must equal the previous step's `game` byte for byte |
| `rep` | `-DFRAME_REPORT=1` (or your debug report) | timing proofs on the emulator |
| `rep-new0` | as `rep`, new switch at 0 | must equal the previous `rep` |
| `probe` | every debug option on | the tightest room; decides the memory budget |
| `probe-new0` | as `probe`, new switch at 0 | must equal the previous `probe` |
| `release0` | the oldest release's switches | the outer anchor: the last release, byte for byte |
| refusals | each bad combination | must stop before writing any file |

Add the flavours your testers use (for example a no-save build for hardware tests).

## Side by side in worktrees
```sh
git worktree add --detach ../tbl-a HEAD
git worktree add --detach ../tbl-b HEAD
git worktree add --detach ../tbl-c HEAD
# run one role in each, each writing to its own output folder; wait for all three
git worktree remove ../tbl-a   # and the others, after the outputs are merged
```
Run the refusals first in one tree, because they must leave it untouched.

## Refusal tests
For each bad combination: snapshot the list of files under the output folders and `git status --porcelain --ignored`,
run the build, expect a non-zero exit with a clear message, then check that both snapshots are unchanged. A refusal
that writes even one file is a failure.

## Comparing two tables
- `.nex` and binary outputs: byte for byte (MD5 or a direct compare).
- Build logs: line for line after dropping fields that legitimately changed (a new switch's line).
- `.map` files: line for line after removing zcc's temporary names. A regex that worked for one project:
  `[A-Za-z0-9_~\-]*zcc[A-Za-z0-9_~\-]*|\\?Temp\\?\S*|/tmp/\S*`
- Any other difference is a real difference: find its cause before going on.

## What to report at the end of a step
- The MD5 of each flavour (full in the project docs, the first 8 hex digits in prose) and which anchors matched.
- Free bytes per flavour: the main bank and every page, before and after.
- The number of builds each role made and the total.
- The refusals tested and that each wrote nothing.
