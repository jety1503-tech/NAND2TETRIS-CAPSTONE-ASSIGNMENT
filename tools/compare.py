#!/usr/bin/env python3
"""Compare two .hack files line by line (your assembler vs the official one).

    python tools/compare.py mine/Rect.hack official/Rect.hack
"""
import sys

def read(p):
    with open(p) as f:
        return [l.strip() for l in f if l.strip()]

if len(sys.argv) != 3:
    sys.exit("usage: compare.py mine.hack official.hack")
a, b = read(sys.argv[1]), read(sys.argv[2])
bad = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
if len(a) != len(b):
    print("DIFFERENT LENGTH: %d vs %d instructions" % (len(a), len(b)))
for i in bad[:10]:
    print("line %d:\n  mine     %s\n  official %s" % (i + 1, a[i], b[i]))
if not bad and len(a) == len(b):
    print("IDENTICAL (%d instructions)" % len(a)); sys.exit(0)
print("%d differing line(s)" % len(bad)); sys.exit(1)
