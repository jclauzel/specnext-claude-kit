#!/usr/bin/env python3
"""Find m68k functions that use a6 as a frame pointer without ever setting it up.

    qdos-gcc -O2 -m68000 -S -o build/s/main.s src/main.c      (once per .c file)
    python a6scan.py build/s                                  (a folder of .s files, or single .s files)

gcc 2.95.3 for QDOS, at -O2, can drop a function's frame pointer (no `link a6`) and still address a local array as
-16(a6). It gives no warning: the function reads and writes stray memory, and may still look right most of the time.
This script names every function that has no `link a6` and reads a6, as a value or as a base, before loading it.

A function gcc uses a6 in as an ordinary register loads it first (lea _x,a6), so it is not reported. The check follows
the text from top to bottom, not the branches: look at each hit in the .s file before you act on it.

The cure for a hit: take the array out of the frame (make it static, if the function is not re-entered), or compile
that one file with -O1, then scan again.

Exits 1 with one line per function found, 0 when there is none, 2 when there is nothing to read.
Released under the MIT licence of the repository it comes from.
"""

import os
import re
import sys

FUNCTION = re.compile(r"^(_[A-Za-z0-9_]+):")
A6 = re.compile(r"\ba6\b")
SAVE = re.compile(r"^(movem?)(\.l)?$")


def operands(text):
    """Split an operand list on commas outside parentheses."""
    return [part.strip() for part in re.split(r",(?![^(]*\))", text) if part.strip()]


def first_bad_use(instructions):
    """The first instruction that reads a6 before it is loaded, or None."""
    for _, op, args in instructions[:3]:
        if op.split(".")[0] == "link" and A6.search(args):
            return None                                     # a real frame pointer
    for index, (line, op, args) in enumerate(instructions):
        if not A6.search(args):
            continue
        parts = operands(args)
        source, target = parts[:-1], parts[-1]
        if SAVE.match(op) and (target == "-(sp)" or source == ["(sp)+"]):
            if op.startswith("movem") or index < 4 or source == ["(sp)+"]:
                continue                                    # saved in the prologue, restored in the epilogue
        if target == "a6" and not any(A6.search(part) for part in source) and op.split(".")[0] in ("lea", "move", "movea"):
            return None                                     # loaded first: an ordinary register here
        return line, op, args
    return None


def functions(path):
    """Yield (name, [(line number, op, args)]) for each function of a .s file."""
    name, body = None, []
    with open(path, encoding="latin-1") as handle:
        for number, raw in enumerate(handle, start=1):
            match = FUNCTION.match(raw)
            if match:
                if name:
                    yield name, body
                name, body = match.group(1), []
                continue
            text = raw.split(";")[0].strip()
            if not name or not text or text.startswith(".") or text.endswith(":"):
                continue
            text = re.sub(r"^L\d+:\s*", "", text)
            op, _, args = text.partition(" ") if " " in text else text.partition("\t")
            body.append((number, op.strip(), args.strip()))
    if name:
        yield name, body


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    files = []
    for item in argv:
        if os.path.isdir(item):
            files += [os.path.join(item, name) for name in sorted(os.listdir(item)) if name.endswith(".s")]
        else:
            files.append(item)
    if not files:
        print("a6scan: no .s file to read")
        return 2
    hits = count = 0
    for path in files:
        for name, body in functions(path):
            count += 1
            bad = first_bad_use(body)
            if bad:
                hits += 1
                print("%s:%d: %s reads a6 with no frame: %s %s" % (os.path.basename(path), bad[0], name, bad[1], bad[2]))
    print("a6scan: %d function(s) in %d file(s), %d suspect" % (count, len(files), hits))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
