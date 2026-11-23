#!/usr/bin/env python3
"""Tests for the QL scripts, on made-up input: no QL, no emulator and no compiler needed.

    python extra/ql-tools/test_ql_tools.py            (run the tests; also checks the copies below are the same)
    python extra/ql-tools/test_ql_tools.py --sync     (copy the scripts from here into the plugin's skills)

This folder holds the scripts to edit. The plugin's skills carry a copy of each, because installing a plugin copies only
the plugin's own folder: after an edit here, run --sync, then the tests.
"""

import os
import shutil
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "plugins", "zxnext-ql", "skills")
COPIES = {
    "a6scan.py": "ql-c-build",
    "stack_frames.py": "ql-c-build",
    "qlheader.py": "ql-c-build",
    "sbasic_lint.py": "ql-superbasic",
    "run_sqlux.py": "ql-emulators",
}
failures = 0


def check(name, condition, detail=""):
    global failures
    if not condition:
        failures += 1
    print("%s %s %s" % ("PASS" if condition else "FAIL", name, "" if condition else detail))


def run(script, *args):
    done = subprocess.run([sys.executable, os.path.join(HERE, script)] + list(args), capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def read(path):
    with open(path, "rb") as handle:
        return handle.read()


def write(folder, name, text):
    path = os.path.join(folder, name)
    with open(path, "wb") as handle:
        handle.write(text if isinstance(text, bytes) else text.encode("ascii"))
    return path


FRAMELESS = """.sect .text
_bad:
\tmovem.l d3/a2/a3,-(sp)
\tlea _draw,a2
\tlea -16(a6),a3
\tjsr (a2)
\tmovem.l (sp)+,d3/a2/a3
\trts
"""
CLEAN = """.sect .text
_framed:
\tlink a6,#-16
\tmove.b d0,-16(a6)
\tunlk a6
\trts
_register:
\tmovem.l d3/a6,-(sp)
\tlea _draw,a6
\tjsr (a6)
\tmovem.l (sp)+,d3/a6
\trts
_saved:
\tmove.l a6,-(sp)
\tlea _draw,a6
\tjsr (a6)
\tmove.l (sp)+,a6
\trts
_plain:
\tlea -100(sp),sp
\tmovem.l d3-d5/a2,-(sp)
\tmove.l d0,-(sp)
\trts
"""


def test_assembler(folder):
    path = write(folder, "bad.s", FRAMELESS)
    code, out = run("a6scan.py", path)
    check("a6scan finds a frameless a6", code == 1 and "_bad" in out and "bad.s:5" in out, out)
    os.remove(path)
    write(folder, "clean.s", CLEAN)
    code, out = run("a6scan.py", folder)
    check("a6scan passes frames and registers", code == 0 and "4 function(s)" in out, out)
    code, out = run("stack_frames.py", folder)
    rows = {row.split()[1]: int(row.split()[0]) for row in out.splitlines() if row.split()[0].isdigit()}
    check("stack_frames sizes", rows == {"_framed": 20, "_register": 8, "_saved": 4, "_plain": 116}, out)
    code, out = run("stack_frames.py", folder, "--limit", "100")
    check("stack_frames --limit", code == 1 and "1 over 100" in out, out)


def test_header(folder):
    body = b"\x60\x2e\0\0\0\0\x4a\xfb\0\x06C_PROG" + bytes(100)
    job = write(folder, "app.exe", body + b"XTcc" + struct.pack(">I", 1000))
    code, out = run("qlheader.py", "info", job)
    check("qlheader info", code == 0 and "dataspace in the file: 1000" in out, out)
    wrapped = os.path.join(folder, "app_exe")
    code, out = run("qlheader.py", "wrap", job, "-o", wrapped)
    data = read(wrapped) if code == 0 else bytes(30)
    check("qlheader wrap", data[:18] == b"]!QDOS File Header" and data[21] == 1 and data[30:] == body
          and struct.unpack(">I", data[22:26])[0] == 17408, out)
    code, out = run("qlheader.py", "wrap", job, "-o", wrapped)
    check("qlheader does not overwrite", code != 0 and "exists" in out, out)
    raw = os.path.join(folder, "app_bin")
    code, out = run("qlheader.py", "raw", job, "-o", raw)
    check("qlheader raw", code == 0 and read(raw) == body and "SEXEC" in out, out)
    code, out = run("qlheader.py", "info", wrapped)
    check("qlheader reads the prefix back", "dataspace in the file: 17408" in out, out)
    code, out = run("qlheader.py", "raw", write(folder, "x.exe", bytes(40)), "-o", raw + "2")
    check("qlheader refuses a file that is no job", code != 0 and not os.path.exists(raw + "2"), out)


GOOD = """100 REMark loops: one-line and block forms (IF FOR x in a REMark is ignored)
110 FOR t = 1 TO 200: IF PEEK(163840) && 2 THEN EXIT t
120 FOR a = 1, 2
130   IF a = 1 THEN
140     PRINT "GO TO 999"; 'it: is'
150   ELSE
160     IF (a && 2) = 2 THEN PRINT a: ELSE PRINT -a
170   END IF
180 END FOR a
190 REPeat w
200   k$ = INKEY$(-1): IF k$ == "q" THEN EXIT w
210 END REPeat w
220 SELect ON a
230   ON a = 1: PRINT "one"
240 END SELect
250 show 3: GO TO 270
260 REMark next
270 STOP
300 DEFine PROCedure show(n)
310   LOCal i
320   FOR i = 1 TO n
330     PRINT i
340   END FOR i
350 END DEFine show
"""
BAD = {
    "CR": ("100 PRINT 1\r\n", "CR found"),
    "no final LF": ("100 PRINT 1", "no LF at the end"),
    "not ASCII": (b"100 PRINT \"\xc2\xa3\"\n", "not ASCII"),
    "no line number": ("PRINT 1\n", "no line number"),
    "line order": ("110 PRINT 1\n100 PRINT 2\n", "not above line"),
    "missing target": ("100 GO TO 200\n", "no such line"),
    "unclosed IF": ("100 IF a = 1 THEN\n110 PRINT 1\n", "never closed"),
    "unclosed DEFine": ("100 DEFine PROCedure p\n110 PRINT 1\n", "never closed"),
    "wrong END FOR": ("100 FOR a = 1 TO 2\n110 PRINT a\n120 END FOR b\n", "is open"),
    "stray END REPeat": ("100 END REPeat w\n", "no open REPeat"),
    "EXIT of nothing": ("100 EXIT w\n", "no such loop"),
    "keyword as a variable": ("100 step = 3\n", "is a keyword"),
}
WARN = {
    "bitwise beside a comparison": ("100 IF b && 32 = 0 THEN PRINT 1\n", "bracket it"),
    "NOT beside a bitwise": ("100 x = NOT s && 36\n", "bracket it"),
    "MOD of a big number": ("100 x = 196608 MOD 2\n", "16-bit"),
    "hex literal": ("100 x = $28000\n", "literal"),
    "eight digits": ("100 x = 12582912\n", "7 digits"),
}


def test_lint(folder):
    path = write(folder, "t_bas", GOOD)
    code, out = run("sbasic_lint.py", path)
    check("lint passes a good program", code == 0 and "0 error(s), 0 warning(s)" in out, out)
    for name, (text, expected) in sorted(BAD.items()):
        code, out = run("sbasic_lint.py", write(folder, "t_bas", text))
        check("lint error: " + name, code == 1 and expected in out, out)
    for name, (text, expected) in sorted(WARN.items()):
        code, out = run("sbasic_lint.py", write(folder, "t_bas", text))
        check("lint warning: " + name, code == 0 and expected in out, out)
    path = write(folder, "t_bas", "100 x = $28000\n")
    check("lint --smsqe", "0 warning" in run("sbasic_lint.py", path, "--smsqe")[1])
    path = write(folder, "t_bas", "100 PRINT PEEK(114622)\n110 PRINT PEEK_W(114622)\n")
    code, out = run("sbasic_lint.py", path, "--byte-only", "98304-0x1BFFF")
    check("lint --byte-only", code == 1 and "110:" in out and "100:" not in out, out)


def test_copies():
    for name, skill in sorted(COPIES.items()):
        copy = os.path.join(SKILLS, skill, "scripts", name)
        same = os.path.isfile(copy) and read(copy) == read(os.path.join(HERE, name))
        check("the copy of %s in %s is the same" % (name, skill), same, "run --sync")


def main():
    if "--sync" in sys.argv:
        for name, skill in sorted(COPIES.items()):
            shutil.copyfile(os.path.join(HERE, name), os.path.join(SKILLS, skill, "scripts", name))
            print("copied %s to %s" % (name, skill))
        return 0
    for test in (test_assembler, test_header, test_lint):
        with tempfile.TemporaryDirectory() as folder:
            test(folder)
    test_copies()
    print("test_ql_tools: %s" % ("ALL PASS" if not failures else "%d FAILED" % failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
