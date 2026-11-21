#!/usr/bin/env python3
"""Measure the bytes and T-states of a Z80 or Z80N snippet with z88dk.

Each snippet is a small .asm file that marks the code under test with two labels,
t_start and t_end (see ../examples/). The script assembles it with z88dk-z80asm,
reads both labels from the .map, runs z88dk-ticks from t_start to t_end and prints
the bytes (t_end - t_start) and the cycles ticks counted.

    python measure.py examples/addhl-plain.asm examples/addhl-z80n.asm
    python measure.py --cpu z80 examples/addhl-plain.asm

z88dk must be installed. The script looks for z88dk-z80asm and z88dk-ticks on PATH,
then under $Z88DK_DIR/bin. Output files go to a temporary folder that is removed after.

Remember what this measures: the T-states of ticks' CPU model (instruction-table
timing, no contention, no wait states). Lines per frame on real hardware still have
to be measured on the machine or an emulator that models it.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile


def find_tool(name):
    found = shutil.which(name)
    if found:
        return found
    root = os.environ.get("Z88DK_DIR")
    if root:
        for candidate in (name, name + ".exe"):
            path = os.path.join(root, "bin", candidate)
            if os.path.isfile(path):
                return path
    sys.exit(f"measure.py: cannot find {name} on PATH or under $Z88DK_DIR/bin")


def read_labels(map_path):
    labels = {}
    pattern = re.compile(r"^(\w+)\s*=\s*\$([0-9A-Fa-f]+)")
    with open(map_path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = pattern.match(line)
            if match:
                labels[match.group(1)] = int(match.group(2), 16)
    return labels


def measure(asm_path, cpu, z80asm, ticks):
    work = tempfile.mkdtemp(prefix="z80-measure-")
    try:
        source = os.path.join(work, "snippet.asm")
        shutil.copyfile(asm_path, source)
        cmd = [z80asm, f"-m{cpu}", "-b", "-m", source]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return None, f"assembly failed:\n{result.stdout}{result.stderr}"
        labels = read_labels(os.path.join(work, "snippet.map"))
        if "t_start" not in labels or "t_end" not in labels:
            return None, "the snippet must define the labels t_start and t_end"
        start, end = labels["t_start"], labels["t_end"]
        cmd = [ticks, f"-m{cpu}", "-start", f"{start:04X}", "-end", f"{end:04X}",
               os.path.join(work, "snippet.bin")]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        numbers = re.findall(r"^\s*(\d+)\s*$", result.stdout, re.MULTILINE)
        if result.returncode != 0 or not numbers:
            return None, f"z88dk-ticks gave no count:\n{result.stdout}{result.stderr}"
        return (end - start, int(numbers[-1])), None
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("snippets", nargs="+", help=".asm files with t_start and t_end labels")
    parser.add_argument("--cpu", default="z80n", choices=["z80", "z80n"],
                        help="CPU for both the assembler and ticks (default z80n)")
    args = parser.parse_args()
    z80asm = find_tool("z88dk-z80asm")
    ticks = find_tool("z88dk-ticks")
    failed = False
    print(f"{'snippet':40} {'bytes':>5} {'T-states':>9}")
    for path in args.snippets:
        values, error = measure(path, args.cpu, z80asm, ticks)
        name = os.path.basename(path)
        if error:
            failed = True
            print(f"{name:40} error: {error}")
        else:
            print(f"{name:40} {values[0]:5d} {values[1]:9d}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
