#!/usr/bin/env python3
"""List the stack frame of every function in qdos-gcc's assembler output, biggest first.

    qdos-gcc -O2 -m68000 -S -o build/s/main.s src/main.c      (once per .c file)
    python stack_frames.py build/s                            (all frames)
    python stack_frames.py build/s --top 20
    python stack_frames.py build/s --limit 512                (exit 1 when a frame is bigger than 512 bytes)

A C68 job runs on `_stack` bytes that nothing checks, so the frames are what you can measure beforehand. A frame here is
the locals (link, lea -N(sp),sp, subq / sub / add #-N) plus 4 bytes for each register saved in the prologue. Not
counted: the return address and the arguments of the calls a function makes. A recursive level costs its frame, plus 4
for the return address, plus the arguments of the recursive call.

Exits 1 when --limit is passed, 2 when there is nothing to read.
Released under the MIT licence of the repository it comes from.
"""

import argparse
import os
import re
import sys

FUNCTION = re.compile(r"^(_[A-Za-z0-9_]+):")
RULES = (
    (re.compile(r"^link(?:\.[wl])?\s+a6,#-?(\d+)$"), 4),                # the saved a6, then the locals
    (re.compile(r"^lea\s+-(\d+)\(sp\),sp$"), 0),
    (re.compile(r"^sub[aq]?(?:\.[wl])?\s+#(\d+),sp$"), 0),
    (re.compile(r"^add[aq]?(?:\.[wl])?\s+#-(\d+),sp$"), 0),
)
MOVEM = re.compile(r"^movem\.l\s+([ad0-7/\-]+),-\(sp\)$")
PUSH = re.compile(r"^move\.l\s+(d[2-7]|a[2-6]),-\(sp\)$")               # a scratch register is never saved


def saved(registers):
    total = 0
    for part in registers.split("/"):
        match = re.match(r"^[ad](\d)-[ad](\d)$", part)
        total += int(match.group(2)) - int(match.group(1)) + 1 if match else 1
    return 4 * total


def frames(path):
    """Yield (function, frame in bytes)."""
    name, size, prologue = None, 0, False
    with open(path, encoding="latin-1") as handle:
        for raw in handle:
            match = FUNCTION.match(raw)
            if match:
                if name:
                    yield name, size
                name, size, prologue = match.group(1), 0, True
                continue
            text = raw.split(";")[0].strip()
            if not name or not prologue or not text or text.startswith("."):
                continue
            for pattern, extra in RULES:
                match = pattern.match(text)
                if match:
                    size += int(match.group(1)) + extra
                    break
            else:
                match = MOVEM.match(text)
                if match:
                    size += saved(match.group(1))
                elif PUSH.match(text):
                    size += 4
                else:
                    prologue = False
    if name:
        yield name, size


def main():
    parser = argparse.ArgumentParser(description="Stack frames from qdos-gcc -S output, biggest first")
    parser.add_argument("paths", nargs="+", help=".s files, or folders of them")
    parser.add_argument("--top", type=int, default=0, help="only the N biggest")
    parser.add_argument("--limit", type=int, default=0, help="fail when a frame is bigger than N bytes")
    args = parser.parse_args()
    files = []
    for item in args.paths:
        if os.path.isdir(item):
            files += [os.path.join(item, name) for name in sorted(os.listdir(item)) if name.endswith(".s")]
        else:
            files.append(item)
    if not files:
        print("stack_frames: no .s file to read")
        return 2
    found = [(size, name, os.path.basename(path)) for path in files for name, size in frames(path)]
    found.sort(key=lambda row: (-row[0], row[1]))
    for size, name, where in found[:args.top] if args.top else found:
        print("%6d  %-32s %s" % (size, name, where))
    over = [row for row in found if args.limit and row[0] > args.limit]
    print("stack_frames: %d function(s) in %d file(s)%s" % (
        len(found), len(files), ", %d over %d bytes" % (len(over), args.limit) if args.limit else ""))
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
