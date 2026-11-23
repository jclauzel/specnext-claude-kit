#!/usr/bin/env python3
"""Check a SuperBASIC program on the PC, before it is loaded on a QL. Nothing is run.

    python sbasic_lint.py boot_bas                 (Minerva and other QDOS ROMs)
    python sbasic_lint.py boot_bas --smsqe         (SMSQ/E's SBASIC: $hex and %binary literals are allowed)
    python sbasic_lint.py probe_bas --byte-only 98304-114687
                                                   (PEEK_W / PEEK_L / POKE of any size in that range is an error:
                                                    Minerva reads a word as two bytes, so registers with side effects
                                                    need plain PEEK)

Errors: CR line ends, no final LF, bytes outside ASCII, a line with no number, numbers out of order or range, blocks that
do not close (DEFine, IF, FOR, REPeat, SELect, WHEN), EXIT / NEXT of a loop that is not open, GO TO / GO SUB / RESTORE to
a line that is not there, a keyword used as a variable, procedure or loop name.
Warnings: long lines, && || ^^ beside a comparison with no brackets, MOD / DIV of a number past 16 bits, $hex / %binary
literals, whole numbers of 8 digits or more (SAVE and PRINT write them in exponent form).

It reads the text with patterns, not SuperBASIC's own parser: a warning is a question. LOAD the program on an emulator
and look for MISTake lines as well.

Exits 1 when there is an error, 0 otherwise. Released under the MIT licence of the repository it comes from.
"""

import argparse
import re
import sys

KEYWORDS = set("""abs acos acot alchp and arc at atan auto baud beep beeping bin bin$ block border call chr$ circle clchp
clear clock close cls code continue copy copy_n cos cot csize cursor data date date$ day$ ddown default define deg delete
dim dimn dir div dlist dline do dup edit ellipse else end eof ernum erlin ew ex exec exec_w exit exp fdat fex fill fill$
flash flen flush fop_dir fop_in fop_new fop_over fopen for format fpos free_mem ftest ftyp function get go hex hex$ if ink
inkey$ input instr int jobs keyrow lbytes len let line list ln load local log10 lrespr lrun mend merge mod mode move mrun
net new next nxjob ojob on open open_dir open_in open_new open_over or over pan paper pause peek peek_l peek_w pend penup
pi pjob point poke poke_l poke_w print procedure put rad randomise read recol rechp remark remainder renum repeat report
resident respr restore retry return rjob rnd run save save_o sbytes scale scroll sdate select sexec sin spjob sqrt stat
step stop strip tan then to truncate turn turnto under ver$ view when width window xor""".split())

NAME = r"[A-Za-z_][A-Za-z0-9_]*[%$]?"
RE_REM = re.compile(r"^REM(?:ARK)?\b", re.I)
RE_DEF = re.compile(r"^DEF(?:INE)?\s+(?:PROC(?:EDURE)?|FN|FUN?CTION|FUNC)\s+(" + NAME + r")", re.I)
RE_END = re.compile(r"^END\s+(DEF(?:INE)?|IF|FOR|REP(?:EAT)?|SEL(?:ECT)?|WHEN)\b\s*(" + NAME + r")?", re.I)
RE_FOR = re.compile(r"^FOR\s+(" + NAME + r")\s*=", re.I)
RE_REP = re.compile(r"^REP(?:EAT)?\b\s*(" + NAME + r")?", re.I)
RE_SEL = re.compile(r"^SEL(?:ECT)?\s+ON\b", re.I)
RE_WHEN = re.compile(r"^WHEN\b", re.I)
RE_IF = re.compile(r"^IF\b", re.I)
RE_EXIT = re.compile(r"\b(EXIT|NEXT)\s+(" + NAME + r")", re.I)
RE_GO = re.compile(r"\b(GO\s*TO|GO\s*SUB|RESTORE)\s+(\d+)\b", re.I)
RE_ASSIGN = re.compile(r"^(?:LET\s+)?(" + NAME + r")\s*=(?!=)", re.I)
RE_BITWISE = re.compile(r"(?:&&|\|\||\^\^)\s*[\w%$.]+\s*(?:==|<>|<=|>=|=|<|>)")
RE_NOT = re.compile(r"\bNOT\s+[\w%$.]+\s*(?:&&|\|\||\^\^)", re.I)
RE_MODDIV = re.compile(r"\b(\d{5,})\s*(?:MOD|DIV)\b|\b(?:MOD|DIV)\s+(\d{5,})\b", re.I)
RE_HEX = re.compile(r"(?<![\w$])\$[0-9A-Fa-f]+\b|(?<![\w%])%[01]{2,}\b")
RE_BIG = re.compile(r"(?<![\w.])\d{8,}(?![\w.])")
RE_ACCESS = re.compile(r"\b(PEEK_[WL]|POKE(?:_[WL])?)\s*\(?\s*(\d+)\b", re.I)
KIND = {"DEF": "DEFine", "IF": "IF", "FOR": "FOR", "REP": "REPeat", "SEL": "SELect", "WHE": "WHEN"}


def blank_strings(text):
    """Replace the inside of "..." and '...' so that nothing in them is read as code."""
    return re.sub(r'"[^"]*"|\'[^\']*\'', lambda match: match.group(0)[0] * 2, text)


def statements(text):
    """The statements of a line, up to a REMark; text after THEN or ELSE is a statement of its own."""
    result = []
    for part in blank_strings(text).split(":"):
        part = part.strip()
        if RE_REM.match(part):
            break
        pieces = re.split(r"\bTHEN\b", part, flags=re.I)
        for index, piece in enumerate(pieces):
            if index < len(pieces) - 1:
                result.append((piece.strip() + " THEN").strip())
            elif piece.strip() or len(pieces) == 1:
                result.append(piece.strip())
    final = []
    for item in result:
        if re.match(r"^ELSE\b\s*\S", item, re.I):
            final += ["ELSE", item[4:].strip()]
        elif item:
            final.append(item)
    return final


class Lint:
    def __init__(self, args):
        self.args = args
        self.errors, self.warnings = [], []
        self.stack = []                                     # (kind, line, loop name, may be a one-line form)

    def error(self, line, text):
        self.errors.append("%s: %s" % (line, text))

    def warn(self, line, text):
        self.warnings.append("%s: %s" % (line, text))

    def close(self, line, kind, name):
        while self.stack and self.stack[-1][3] and (self.stack[-1][0] != kind or (name and self.stack[-1][2] != name)):
            self.stack.pop()                                # a one-line FOR / REPeat / IF that needs no END
        if not self.stack or self.stack[-1][0] != kind:
            self.error(line, "END %s with no open %s" % (KIND[kind], KIND[kind]))
            return
        top = self.stack[-1]
        if kind in ("FOR", "REP") and name and top[2] and name != top[2]:
            self.error(line, "END %s %s, but %s of line %s is open" % (KIND[kind], name, top[2], top[1]))
            return
        self.stack.pop()

    def declared(self, line, name, what):
        if name and name.lower() in KEYWORDS:
            self.error(line, "%s is a keyword, used as a %s" % (name, what))

    def line(self, number, text):
        items = statements(text)
        in_line_if = False
        for index, item in enumerate(items):
            last = index == len(items) - 1
            match = RE_END.match(item)
            if match:
                self.close(number, match.group(1)[:3].upper().replace("IF", "IF"), (match.group(2) or "").lower())
                continue
            match = RE_DEF.match(item)
            if match:
                self.declared(number, match.group(1), "procedure or function")
                self.stack.append(("DEF", number, "", not last))
                continue
            match = RE_FOR.match(item)
            if match:
                self.declared(number, match.group(1), "loop name")
                self.stack.append(("FOR", number, match.group(1).lower(), not last))
                continue
            match = RE_REP.match(item)
            if match:
                self.declared(number, match.group(1), "loop name")
                self.stack.append(("REP", number, (match.group(1) or "").lower(), not last))
                continue
            if RE_SEL.match(item):
                self.stack.append(("SEL", number, "", not last))
                continue
            if RE_WHEN.match(item):
                self.stack.append(("WHE", number, "", not last))
                continue
            if RE_IF.match(item):
                if last and not in_line_if:
                    self.stack.append(("IF", number, "", False))
                else:
                    in_line_if = True
            elif item.upper() == "ELSE" and not in_line_if:
                if not any(entry[0] == "IF" for entry in self.stack):
                    self.error(number, "ELSE with no open IF")
            match = RE_ASSIGN.match(item)
            if match and not RE_IF.match(item):
                self.declared(number, match.group(1), "variable")
            for match in RE_EXIT.finditer(item):
                open_loops = [entry[2] for entry in self.stack if entry[0] in ("FOR", "REP")]
                if match.group(2).lower() not in open_loops:
                    self.error(number, "%s %s: no such loop is open" % (match.group(1), match.group(2)))
        code = " : ".join(items)
        if RE_BITWISE.search(code) or RE_NOT.search(code):
            self.warn(number, "a bitwise operator beside a comparison or NOT: bracket it, (x && 32) = 0")
        for match in RE_MODDIV.finditer(code):
            if int(match.group(1) or match.group(2)) > 32767:
                self.warn(number, "MOD / DIV work on 16-bit integers: %s overflows" % (match.group(1) or match.group(2)))
        if not self.args.smsqe and RE_HEX.search(code):
            self.warn(number, "a $hex or %binary literal: SMSQ/E only, a MISTake on Minerva and QDOS")
        match = RE_BIG.search(code)
        if match:
            self.warn(number, "%s: SAVE keeps 7 digits; write it as a product (192 * 65536)" % match.group(0))
        for low, high in self.args.ranges:
            for match in RE_ACCESS.finditer(code):
                if low <= int(match.group(2)) <= high:
                    self.error(number, "%s of %s, inside the byte-only range" % (match.group(1), match.group(2)))

    def run(self, data):
        if b"\r" in data:
            self.error("file", "CR found: use LF line ends only (a CR can become part of the line: MISTake)")
        if not data.endswith(b"\n"):
            self.error("file", "no LF at the end")
        try:
            data.decode("ascii")
        except UnicodeDecodeError as problem:
            self.error("file", "not ASCII: %s" % problem)
        lines = data.decode("ascii", "replace").replace("\r", "").split("\n")
        if lines and not lines[-1]:
            lines.pop()
        numbers, program = set(), []
        previous = 0
        for index, text in enumerate(lines, start=1):
            match = re.match(r"^\s*(\d+)(?:\s+(.*))?$", text)
            if not match:
                self.error("text line %d" % index, "no line number: %r" % text[:40])
                continue
            number = int(match.group(1))
            if not 1 <= number <= 32767:
                self.error(number, "line numbers go from 1 to 32767")
            if number <= previous:
                self.error(number, "not above line %d before it" % previous)
            previous = number
            if len(text) > self.args.max_line:
                self.warn(number, "%d characters (over %d): hard to EDIT on the QL" % (len(text), self.args.max_line))
            numbers.add(number)
            program.append((number, match.group(2) or ""))
        for number, text in program:
            self.line(number, text)
        for kind, number, name, short in self.stack:
            if not short:
                self.error(number, "%s %s is never closed" % (KIND[kind], name))
        for number, text in program:
            for match in RE_GO.finditer(" : ".join(statements(text))):
                if int(match.group(2)) not in numbers:
                    self.error(number, "%s %s: no such line" % (match.group(1), match.group(2)))
        return len(program)


def byte_range(text):
    low, _, high = text.partition("-")
    return int(low, 0), int(high or low, 0)


def main():
    parser = argparse.ArgumentParser(description="Static checks for a SuperBASIC program")
    parser.add_argument("file")
    parser.add_argument("--smsqe", action="store_true", help="SMSQ/E's SBASIC: allow $hex and %%binary literals")
    parser.add_argument("--max-line", type=int, default=160, help="warn past this many characters (160)")
    parser.add_argument("--byte-only", dest="ranges", type=byte_range, action="append", default=[], metavar="LOW-HIGH",
                        help="addresses where only PEEK is allowed (decimal or 0x)")
    args = parser.parse_args()
    with open(args.file, "rb") as handle:
        data = handle.read()
    lint = Lint(args)
    count = lint.run(data)
    for text in lint.errors:
        print("ERROR  " + text)
    for text in lint.warnings:
        print("warn   " + text)
    print("sbasic_lint: %d line(s), %d error(s), %d warning(s)" % (count, len(lint.errors), len(lint.warnings)))
    return 1 if lint.errors else 0


if __name__ == "__main__":
    sys.exit(main())
