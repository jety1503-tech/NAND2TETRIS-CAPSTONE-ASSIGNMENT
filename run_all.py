#!/usr/bin/env python3
"""
One command to check everything:      python run_all.py

1. runs all self-tests (assembler, error messages, Box program)
2. assembles Box.asm with YOUR assembler  -> Box.hack
3. previews the box on a tiny simulator (key pressed / key released)
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def run(title, cmd):
    print("\n=== %s ===" % title)
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        print(">>> FAILED: %s" % title)
        sys.exit(r.returncode)


run("1/3  self-tests", [PY, "tests/test_all.py"])
run("2/3  assemble Box.asm", [PY, "assembler.py", "Box.asm"])
print("\n=== 3/3  preview ===")
print("-- key pressed --")
subprocess.run([PY, "tools/hack_sim.py", "Box.hack", "--key", "65",
                "--png", "box_preview_pressed.png"], cwd=ROOT)
print("-- key released --")
subprocess.run([PY, "tools/hack_sim.py", "Box.hack", "--key", "0"], cwd=ROOT)
print("\nAll good. Next: open Box.hack in the official CPU Emulator and take your screenshot.")
