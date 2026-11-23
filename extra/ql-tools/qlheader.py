#!/usr/bin/env python3
"""Read a linked QL job's dataspace and write it in the forms each kind of QL needs.

    python qlheader.py info  build/app.exe                    (what the file is)
    python qlheader.py wrap  build/app.exe -o dist/app_exe    (30-byte "]!QDOS File Header" in front)
    python qlheader.py raw   build/app.exe -o dist/app_bin    (no trailer; prints the SEXEC line to install it)

C68's ld leaves the job's dataspace in an 8-byte trailer ("XTcc" + a big-endian long). sQLux and uQLx read it. A real
QDOS or SMSQ/E drive keeps the type and the dataspace in the file's own header, and loses them on the way from a PC:
  wrap  for drives that live on a PC and whose emulator knows the prefix (Q-emuLator, QPC2's DOS device, sQLux);
  raw   for everything else: LBYTES it into memory on the QL, then SEXEC it with the size and dataspace printed.

--margin (default 16384) is added to the linker's figure, which is then rounded up to 1 KB. The linker's figure covers
the bss beyond the end of the file; the first stack and the loss of the 8 trailer bytes come on top. Never go below it.

Nothing is overwritten unless you pass --force. Released under the MIT licence of the repository it comes from.
"""

import argparse
import os
import struct
import sys

MAGIC = b"]!QDOS File Header"
TRAILER = b"XTcc"


def read(path):
    with open(path, "rb") as handle:
        return handle.read()


def split(data, path):
    """-> (job without header or trailer, the linker's dataspace or None, the form it was in)"""
    if data.startswith(MAGIC):
        words = data[19]
        return data[2 * words:], struct.unpack(">I", data[22:26])[0], "Q-emuLator header of %d bytes" % (2 * words)
    if len(data) > 8 and data[-8:-4] == TRAILER:
        return data[:-8], struct.unpack(">I", data[-4:])[0], "XTcc trailer"
    return data, None, "no header and no trailer"


def header(dataspace):
    block = MAGIC + bytes([0, 15])                            # reserved, header length in 16-bit words
    block += bytes([0, 1])                                    # access, type 1 = executable
    block += struct.pack(">II", dataspace, 0)                 # dataspace, reserved
    assert len(block) == 30
    return block


def main():
    parser = argparse.ArgumentParser(description="A QL job's dataspace: show it, or write the job in another form")
    parser.add_argument("command", choices=("info", "wrap", "raw"))
    parser.add_argument("file")
    parser.add_argument("-o", "--out")
    parser.add_argument("--margin", type=int, default=16384, help="bytes added to the linker's dataspace (16384)")
    parser.add_argument("--force", action="store_true", help="overwrite the output file")
    args = parser.parse_args()

    body, linked, form = split(read(args.file), args.file)
    name = os.path.basename(args.file)
    job = body[6:8] == b"\x4a\xfb"
    print("%s: %d bytes, %s, %s" % (name, len(body), form, "a QDOS job ($4AFB at 6)" if job else "NOT a QDOS job"))
    if linked is not None:
        print("dataspace in the file: %d" % linked)
    if args.command == "info":
        return 0
    if linked is None or form.startswith("Q-emuLator"):
        sys.exit("qlheader: %s needs a file as linked, with its XTcc trailer" % args.command)
    if not job:
        sys.exit("qlheader: refused, this is not a QDOS job")
    if args.margin < 8:
        sys.exit("qlheader: --margin must be at least 8 (the trailer's own bytes)")
    if not args.out:
        sys.exit("qlheader: -o is needed")
    if os.path.exists(args.out) and not args.force:
        sys.exit("qlheader: %s exists (--force overwrites it)" % args.out)
    dataspace = (linked + args.margin + 1023) // 1024 * 1024
    out = header(dataspace) + body if args.command == "wrap" else body
    with open(args.out, "wb") as handle:
        handle.write(out)
    print("wrote %s: %d bytes, dataspace %d" % (args.out, len(out), dataspace))
    if args.command == "raw":
        print("on the QL:  a = ALCHP(%d): LBYTES win1_app_bin,a: SEXEC win1_app_exe,a,%d,%d: RECHP a"
              % (len(body), len(body), dataspace))
    return 0


if __name__ == "__main__":
    sys.exit(main())
