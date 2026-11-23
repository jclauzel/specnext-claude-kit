#!/usr/bin/env python3
"""Boot sQLux with a PC folder as WIN1_, run one SuperBASIC line, and come back when the emulator quits.

    python run_sqlux.py --home <sQLux folder> --mount <folder> --boot "EXEC_W win1_app_exe"
    python run_sqlux.py ... --boot "EW win1_app_exe;'a b c'" --timeout 60
    python run_sqlux.py ... --no-exit                          (leave the emulator open for a person)

The program writes its results to a file on win1_; read <mount>/<file> on the PC afterwards. Give it a folder made for
the run, never a folder you care about: the QL can write and delete there.

 - ":EMU_EXIT" is added to the line so that the emulator quits by itself (not with --no-exit).
 - Use single quotes for strings in the line: double quotes are lost on the way to the emulator on Windows.
 - It refuses to start while another sQLux runs, and waits for every sQLux process to end: on Windows the process
   that is started re-launches itself and returns at once.
 - After --timeout seconds it stops the sQLux processes that were not there before it started, and returns 124.
 - The folder --home must hold the emulator and its roms folder. The ROM names are sQLux's own by default.

Released under the MIT licence of the repository it comes from.
"""

import argparse
import os
import subprocess
import sys
import tempfile
import time

WINDOWS = os.name == "nt"
PROCESS = "sqlux.exe" if WINDOWS else "sqlux"


def running():
    """The pids of every sQLux on this machine."""
    if WINDOWS:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq " + PROCESS, "/FO", "CSV", "/NH"],
                             capture_output=True, text=True).stdout
        return {int(row.split('","')[1]) for row in out.splitlines() if row.lower().startswith('"' + PROCESS)}
    out = subprocess.run(["pgrep", "-x", PROCESS], capture_output=True, text=True).stdout
    return {int(pid) for pid in out.split()}


def stop(pids):
    for pid in pids:
        if WINDOWS:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
        else:
            subprocess.run(["kill", "-9", str(pid)], capture_output=True)


def main():
    parser = argparse.ArgumentParser(description="Run one SuperBASIC line in sQLux")
    parser.add_argument("--home", default=os.environ.get("SQLUX_HOME"), help="the sQLux folder (or SQLUX_HOME)")
    parser.add_argument("--mount", required=True, help="the PC folder shown as win1_")
    parser.add_argument("--boot", required=True, help="the SuperBASIC line")
    parser.add_argument("--timeout", type=int, default=120, help="seconds (120)")
    parser.add_argument("--no-exit", action="store_true", help="leave the emulator running")
    parser.add_argument("--rom", default="Minerva_1.98a1.bin", help="the system ROM, in roms")
    parser.add_argument("--tk2", default="TK236.rom", help="the Toolkit II ROM, in roms; '' for none")
    parser.add_argument("--ram", type=int, default=4096, help="RAMTOP in KB (4096)")
    parser.add_argument("--speed", default="0", help="0 flat out, 1 about an original QL")
    parser.add_argument("--size", default="2x", help="WIN_SIZE (2x)")
    parser.add_argument("--device", action="append", default=[], metavar="NAME,FOLDER", help="another drive: WIN2,<folder>")
    args = parser.parse_args()

    if not args.home:
        sys.exit("run_sqlux: give --home or set SQLUX_HOME")
    home = os.path.abspath(args.home)
    exe = os.path.join(home, PROCESS)
    if not os.path.isfile(exe):
        sys.exit("run_sqlux: no %s in that folder" % PROCESS)
    if not os.path.isdir(args.mount):
        sys.exit("run_sqlux: the --mount folder does not exist")
    line = args.boot if args.no_exit else args.boot + ":EMU_EXIT"
    if '"' in line:
        sys.exit("run_sqlux: use single quotes for strings in --boot")
    if running():
        sys.exit("run_sqlux: an sQLux is already running: close it first (it may be someone's session)")

    devices = ["WIN1," + args.mount] + args.device
    text = ["SYSROM = " + args.rom]
    if args.tk2:
        text.append("ROMIM = " + args.tk2)
    text += ["RAMTOP = %d" % args.ram, "FAST_STARTUP = 1", "SKIP_BOOT = 1", "BOOT_DEVICE = WIN1",
             "WIN_SIZE = " + args.size, "SPEED = " + args.speed]
    for device in devices:
        name, _, folder = device.partition(",")
        text.append("DEVICE = %s,%s/,qdos-like" % (name, os.path.abspath(folder).replace("\\", "/").rstrip("/")))
    handle, ini = tempfile.mkstemp(suffix=".ini", prefix="sqlux_")
    with os.fdopen(handle, "w", encoding="ascii", newline="\n") as stream:
        stream.write("\n".join(text) + "\n")

    environment = dict(os.environ, SDL_WINDOW_NO_ACTIVATION_WHEN_SHOWN="1")   # SDL: do not take the focus
    print("run_sqlux: %s" % line)
    subprocess.Popen([exe, "-f", ini, "-b", line], cwd=home, env=environment)
    if args.no_exit:
        print("run_sqlux: running; its settings are in %s" % ini)
        return 0
    try:
        time.sleep(1)
        deadline = time.time() + args.timeout
        while running():
            if time.time() > deadline:
                print("run_sqlux: still running after %d s, stopping it" % args.timeout)
                stop(running())
                return 124
            time.sleep(0.25)
    finally:
        try:
            os.remove(ini)
        except OSError:
            pass
    print("run_sqlux: finished")
    return 0


if __name__ == "__main__":
    sys.exit(main())
