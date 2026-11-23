---
name: ql-emulators
description: Run and test QL programs on sQLux and QPC2 - a scripted sQLux run (boot, one SuperBASIC line, results file, quit) that an agent can use in tests, what the Windows sQLux build gets wrong (mkdir, rename, directory types, listening ports, fake free space), how the TCP_ / SCK_ / UDP_ device really behaves on sQLux and QPC2, and what no emulator can prove about the ZX Spectrum Next's QL core. Use this skill whenever a QL job or SuperBASIC program has to be run, tested, screenshotted or debugged on an emulator, when files or sockets behave oddly on sQLux or QPC2, or when you write a test suite for QL code, even if the emulator is not named ("try it", "does it work on a QL?"). Not for MAME, CSpect or Z80 programs.
---

# QL emulators

sQLux (<https://github.com/SinclairQL/sQLux>) is the one to script. QPC2 is the one that shows how SMSQ/E behaves; it
is run by hand, by the user. Neither has the registers of the Next's QL core.

## A scripted run on sQLux
```sh
python ${CLAUDE_SKILL_DIR}/scripts/run_sqlux.py --home <sQLux folder> --mount build/win1 \
    --boot "EXEC_W win1_app_exe;'arg1 arg2'" --timeout 60
```
The folder is `win1_`; the program writes its results there and you read the file afterwards. A run takes about 2
seconds. Rules:
- **Mount a folder made for the run**, never one that matters: the QL can write and delete there.
- **Never start while an sQLux is running** (it may be the user's), and leave none behind. The script refuses to start,
  and stops its own after `--timeout` seconds (exit code 124).
- Set `_endmsg = 0` in the job, or it waits for a key at its end.
- The line has no double quotes: use `'...'`. `EMU_EXIT` is added to its end, but **`LRUN` drops the rest of the line**:
  a program run that way must end with `EMU_EXIT` itself.
- sQLux must run from its own folder, so that its `roms` folder is found. `app.exe` in the folder is `win1_app_exe`.
- The first use of the network opens a Windows Firewall dialog: the user has to answer it.
- `--speed 1` is about an original QL. Flat out (0), a copy is over before a progress line or an ESC can be tested.

## What a scripted run cannot replace
- Keys: let the program take a script of keys as an argument (test builds), and log what each did. A key injected
  before the program's first read goes to SuperBASIC.
- The screen: capture the emulator's window by its handle, and compare colours or text, or have the program dump its
  own text screen to a file. A window moved off the desktop captures black.
- SDL turns host mouse motion over the window into QL mouse motion: park the window away before mouse tests.
- Look at the picture before you say it works.

## The Windows build of sQLux is not QDOS
Read `references/sqlux-files.md` before you trust a file operation. The worst, on 1.1.2: **making and renaming fail**
because the emulator still holds the file open (fixed in sQLux's master on 2026-10-10, pull request 112: use a newer
build when there is one); a sub-directory lists as type 0, length 0; deleting a folder does nothing; free space is a
fixed number. Write fallbacks that fail cleanly, and say "an emulator fault" in the code, so that nobody removes the
right code because the emulator disagrees.

## Networking
There is no socket library in qdos-gcc's `libc.a` (headers only). Use the `TCP_` device through `io_open` and traps:
read `references/tcp-device.md`. Three rules that save days: poll (`io_pend`) before every accept and every read;
always write `TCP_0.0.0.0:port` to listen; on Windows sQLux, listen **once** and keep the channel, since a closed
listening port stays busy until the emulator quits.

## QPC2 and SMSQ/E: what differs
- The PC's drive is `dos1_`, with folders as `_`: `C:\QL\app` is `dos1_QL_app`. Run jobs that carry the 30-byte header
  from there; `win1_` is a container file (the demo one is 10 MB and can be full).
- SMSQ/E locks a file open for writing: -9 to everyone else. It opens a folder as a file of type 255.
- The Pointer Environment is always there; the display may be in 16-bit colour (no mode 4 or 8 calls).
- Keep a list of what only sQLux has run ("owed on QPC2", "owed on the Next's QL core") and give the user a short check
  list for each. Do not call a feature done on a machine that has not run it.

## Fault tests worth having
Host the other end in a small Python server that can half-close, stall, send slowly and refuse. Cases that found real
bugs: a link closed while you wait for a reply; a send whose buffers are full; a peer that floods; a reader that fails
in the middle (do not turn it into a short but "successful" file); a listen port already taken.
