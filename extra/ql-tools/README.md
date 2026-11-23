# ql-tools: scripts for Sinclair QL projects

Standalone Python 3.9+ scripts, nothing to install. MIT, like the rest of the repository: copy them into your project.

| Script | What it does |
|---|---|
| `a6scan.py` | names functions that qdos-gcc 2.95.3 made read `a6` with no frame pointer (its `-O2` bug) |
| `stack_frames.py` | lists each function's stack frame from `qdos-gcc -S` output; `--limit` fails a build |
| `qlheader.py` | shows a linked job's dataspace; writes it with the Q-emuLator prefix, or raw for `SEXEC` |
| `sbasic_lint.py` | static checks for SuperBASIC programs |
| `run_sqlux.py` | one SuperBASIC line in sQLux, then back with the results (Windows, Linux, macOS) |
| `test_ql_tools.py` | tests of the first four on made-up input; `--sync` copies the scripts into the plugin |

Each script's own header says how to run it.

## Two copies, on purpose
The `zxnext-ql` plugin's skills carry the same files: installing a plugin copies only the plugin's folder, so the skills
cannot reach this one. Edit here, then:

```sh
python extra/ql-tools/test_ql_tools.py --sync     # copy them into the skills
python extra/ql-tools/test_ql_tools.py            # tests, and the copies must be the same
```

## Tested on
Python on Windows 11 and, for the tests, in this repository's checks on Linux. `a6scan.py` and `stack_frames.py`: the
output of qdos-gcc-win-1.0 (gcc 2.95.3) for a 44-file project; the scan finds the known bug when its cure is taken out
and reports nothing else in 1 695 functions. `qlheader.py`: both forms run on sQLux 1.1.2. `run_sqlux.py`: sQLux 1.1.2
on Windows only; Linux and macOS are untested. `sbasic_lint.py`: seven programs that ran on QLs, no false report.
