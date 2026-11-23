#!/usr/bin/env python3
"""
Tiny Hack computer simulator, only for a QUICK PREVIEW on your laptop.
(The screenshot for your report must still come from the official CPU Emulator.)

Examples:
    python tools/hack_sim.py Box.hack --key 65            # key 'A' held down
    python tools/hack_sim.py Box.hack --key 0             # no key
    python tools/hack_sim.py Box.hack --key 65 --png box.png
"""
import argparse
import sys

SCREEN, KBD = 16384, 24576


def load_rom(path):
    rom = []
    with open(path) as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            if len(line) != 16 or set(line) - {"0", "1"}:
                raise ValueError("%s line %d is not a 16-bit instruction" % (path, n))
            rom.append(int(line, 2))
    return rom


def alu(c, x, y):
    zx, nx, zy, ny, f, no = [(c >> s) & 1 for s in (5, 4, 3, 2, 1, 0)]
    if zx: x = 0
    if nx: x = ~x & 0xFFFF
    if zy: y = 0
    if ny: y = ~y & 0xFFFF
    out = (x + y) & 0xFFFF if f else x & y
    if no: out = ~out & 0xFFFF
    return out


class Hack:
    def __init__(self, rom):
        self.rom = rom
        self.ram = [0] * (KBD + 1)
        self.A = self.D = self.pc = 0

    def step(self):
        if self.pc >= len(self.rom):
            return False
        ins = self.rom[self.pc]
        if not ins & 0x8000:                       # A-instruction
            self.A = ins
            self.pc += 1
            return True
        a = (ins >> 12) & 1
        y = self.ram[self.A & 0x7FFF] if a else self.A
        out = alu((ins >> 6) & 0x3F, self.D, y)
        old_a = self.A
        if ins & 0x08: self.ram[old_a & 0x7FFF] = out   # d3 -> M
        if ins & 0x20: self.A = out                      # d1 -> A
        if ins & 0x10: self.D = out                      # d2 -> D
        neg = out >= 0x8000
        zero = out == 0
        pos = not neg and not zero
        if ((ins & 4) and neg) or ((ins & 2) and zero) or ((ins & 1) and pos):
            self.pc = old_a
        else:
            self.pc += 1
        return True

    def run(self, cycles):
        for _ in range(cycles):
            if not self.step():
                break

    def pixel(self, x, y):
        word = self.ram[SCREEN + 32 * y + x // 16]
        return (word >> (x % 16)) & 1             # bit 0 = leftmost pixel


def bounding_box(m):
    xs, ys = [], []
    for y in range(256):
        for x in range(512):
            if m.pixel(x, y):
                xs.append(x); ys.append(y)
    if not xs:
        return None
    return min(xs), max(xs), min(ys), max(ys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hack")
    ap.add_argument("--key", type=int, default=0, help="keyboard value (0 = none, 65 = 'A')")
    ap.add_argument("--cycles", type=int, default=200000)
    ap.add_argument("--png", help="save the 512x256 screen as a PNG (needs Pillow)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    m = Hack(load_rom(args.hack))
    m.ram[KBD] = args.key
    m.run(args.cycles)

    bb = bounding_box(m)
    if bb is None:
        print("Screen is empty (all white).")
    else:
        x0, x1, y0, y1 = bb
        print("Black area: x %d..%d (%d px wide), rows %d..%d (%d rows tall)"
              % (x0, x1, x1 - x0 + 1, y0, y1, y1 - y0 + 1))
        if not args.quiet:
            for y in range(y0, min(y1, y0 + 2) + 1):
                print("".join("#" if m.pixel(x, y) else "." for x in range(x0, min(x1, x0 + 79) + 1)))
            if y1 - y0 > 2:
                print("... (%d more rows)" % (y1 - y0 - 2))

    if args.png:
        try:
            from PIL import Image
        except ImportError:
            print("Pillow not installed: run  pip install pillow  to save PNGs.")
            return 0
        img = Image.new("L", (512, 256), 255)
        for y in range(256):
            for x in range(512):
                if m.pixel(x, y):
                    img.putpixel((x, y), 0)
        img.resize((1024, 512), Image.NEAREST).save(args.png)
        print("saved", args.png)
    return 0


if __name__ == "__main__":
    sys.exit(main())
