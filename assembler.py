#!/usr/bin/env python3
"""
Hack assembler  (Nand to Tetris I, Capstone Part B)

Usage:
    python assembler.py Box.asm              -> writes Box.hack next to Box.asm
    python assembler.py Box.asm -o out.hack  -> choose the output name
    python assembler.py A.asm B.asm          -> assemble several files

Extra feature for K = 19  (19 mod 3 = 1):
    A wrong line never crashes the program. Every problem is reported as
        <file>: Line <n>: <clear message>
    where <n> is the line number in the ORIGINAL .asm file.
    If any error is found, no .hack file is written.

How it works (two readings of the file):
    Reading 1: remove comments / blank lines, note where each (LABEL) points.
    Reading 2: turn every remaining line into 16 bits.
               New variables get RAM addresses 16, 17, 18, ...
"""
import argparse
import os
import re
import sys

# ----------------------------------------------------------------- tables
# comp field: 7 bits = a-bit + c1..c6
_COMP_A0 = {
    "0": "101010", "1": "111111", "-1": "111010",
    "D": "001100", "A": "110000", "!D": "001101", "!A": "110001",
    "-D": "001111", "-A": "110011", "D+1": "011111", "A+1": "110111",
    "D-1": "001110", "A-1": "110010", "D+A": "000010", "D-A": "010011",
    "A-D": "000111", "D&A": "000000", "D|A": "010101",
}
_COMP_A1 = {
    "M": "110000", "!M": "110001", "-M": "110011", "M+1": "110111",
    "M-1": "110010", "D+M": "000010", "D-M": "010011", "M-D": "000111",
    "D&M": "000000", "D|M": "010101",
}
COMP = {k: "0" + v for k, v in _COMP_A0.items()}
COMP.update({k: "1" + v for k, v in _COMP_A1.items()})

DEST = {"": "000", "M": "001", "D": "010", "MD": "011",
        "A": "100", "AM": "101", "AD": "110", "AMD": "111"}

JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}

PREDEFINED = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
              "SCREEN": 16384, "KBD": 24576}
PREDEFINED.update({"R%d" % i: i for i in range(16)})

SYMBOL_RE = re.compile(r"[A-Za-z_.$:][A-Za-z0-9_.$:]*")
NUMBER_RE = re.compile(r"[0-9]+")
MAX_A_VALUE = 32767          # A-instruction has 15 value bits


# ------------------------------------------------------------ reading 1
def first_reading(source_lines, symbols, errors):
    """Return [(original_line_number, cleaned_text)] without labels.
    Fills `symbols` with label -> instruction index."""
    program = []
    for lineno, raw in enumerate(source_lines, start=1):
        text = raw.split("//", 1)[0]          # drop comment
        text = "".join(text.split())          # drop all white space
        if not text:
            continue                          # blank / comment-only line
        if text.startswith("("):
            if not text.endswith(")"):
                errors.append((lineno, "invalid label, missing ')': %s" % raw.strip()))
                continue
            name = text[1:-1]
            if not SYMBOL_RE.fullmatch(name):
                errors.append((lineno, "invalid label name '%s'" % name))
                continue
            if name in symbols:
                errors.append((lineno, "label '%s' is already defined" % name))
                continue
            symbols[name] = len(program)      # address of NEXT instruction
            continue
        program.append((lineno, text))
    return program


# ------------------------------------------------------------ reading 2
class Assembler:
    def __init__(self):
        self.symbols = dict(PREDEFINED)
        self.next_var = 16
        self.errors = []                      # list of (line_number, message)

    # -- A instruction: @value  ->  0vvvvvvvvvvvvvvv
    def _a_instruction(self, lineno, text):
        body = text[1:]
        if body == "":
            self.errors.append((lineno, "invalid instruction, '@' needs a number or symbol"))
            return None
        if NUMBER_RE.fullmatch(body):
            value = int(body)
            if value > MAX_A_VALUE:
                self.errors.append((lineno, "invalid instruction, constant %d is larger than %d"
                                    % (value, MAX_A_VALUE)))
                return None
        elif SYMBOL_RE.fullmatch(body):
            if body not in self.symbols:      # new variable
                self.symbols[body] = self.next_var
                self.next_var += 1
            value = self.symbols[body]
        else:
            self.errors.append((lineno, "invalid instruction, bad symbol or number '%s'" % body))
            return None
        return format(value, "016b")

    # -- C instruction: dest=comp;jump  ->  111accccccdddjjj
    def _c_instruction(self, lineno, text):
        dest, jump = "", ""
        rest = text
        if "=" in rest:
            dest, rest = rest.split("=", 1)
        if ";" in rest:
            rest, jump = rest.split(";", 1)
        comp = rest
        if dest not in DEST:
            self.errors.append((lineno, "invalid instruction, unknown dest '%s'" % dest))
            return None
        if comp not in COMP:
            self.errors.append((lineno, "invalid instruction, unknown comp '%s'" % comp))
            return None
        if jump not in JUMP:
            self.errors.append((lineno, "invalid instruction, unknown jump '%s'" % jump))
            return None
        return "111" + COMP[comp] + DEST[dest] + JUMP[jump]

    def assemble(self, source_lines):
        """Return the list of 16-bit strings (may be incomplete if errors)."""
        program = first_reading(source_lines, self.symbols, self.errors)
        out = []
        for lineno, text in program:
            if text.startswith("@"):
                word = self._a_instruction(lineno, text)
            else:
                word = self._c_instruction(lineno, text)
            if word is not None:
                out.append(word)
        return out


# ----------------------------------------------------------------- main
def assemble_file(path, out_path=None):
    """Assemble one file. Returns True on success."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError as e:
        print("%s: cannot open file (%s)" % (path, e.strerror))
        return False

    asm = Assembler()
    words = asm.assemble(lines)

    if asm.errors:
        for lineno, msg in sorted(asm.errors):
            print("%s: Line %d: %s" % (path, lineno, msg))
        print("%s: %d error(s) found, no .hack file written." % (path, len(asm.errors)))
        return False

    if out_path is None:
        out_path = os.path.splitext(path)[0] + ".hack"
    with open(out_path, "w", newline="\n") as f:
        f.write("\n".join(words) + ("\n" if words else ""))
    print("%s -> %s  (%d instructions)" % (path, out_path, len(words)))
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description="Hack assembler (.asm -> .hack)")
    ap.add_argument("files", nargs="+", help=".asm file(s) to assemble")
    ap.add_argument("-o", "--output", help="output file (only with one input file)")
    args = ap.parse_args(argv)
    if args.output and len(args.files) != 1:
        ap.error("-o can only be used with a single input file")
    ok = True
    for p in args.files:
        ok = assemble_file(p, args.output) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
