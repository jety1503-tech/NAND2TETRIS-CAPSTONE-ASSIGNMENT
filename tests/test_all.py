"""Automatic self-checks.  Run from the capstone folder:   python tests/test_all.py"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import assembler                      # noqa: E402
import hack_sim                       # noqa: E402

K = 19
START_ROW, HEIGHT = K, 20
WIDTH_WORDS = (K % 4) + 1             # 4
FIRST_ADDR = 16384 + 32 * START_ROW   # 16992


def asm_lines(path):
    with open(path) as f:
        return f.read().splitlines()


def run_machine(hack_path, key, cycles=200000):
    m = hack_sim.Hack(hack_sim.load_rom(hack_path))
    m.ram[hack_sim.KBD] = key
    m.run(cycles)
    return m


class AssemblerTests(unittest.TestCase):
    def test_add_matches_expected(self):
        a = assembler.Assembler()
        out = a.assemble(asm_lines(os.path.join(ROOT, "tests", "Add.asm")))
        with open(os.path.join(ROOT, "tests", "Add.expected.hack")) as f:
            self.assertEqual(out, f.read().split())
        self.assertEqual(a.errors, [])

    def test_labels_and_variables(self):
        a = assembler.Assembler()
        out = a.assemble(["@i", "M=1", "(END)", "@END", "0;JMP", "@j", "@i"])
        self.assertEqual(out[0], format(16, "016b"))   # i -> 16
        self.assertEqual(out[2], format(2, "016b"))    # END -> instruction 2
        self.assertEqual(out[4], format(17, "016b"))   # j -> 17
        self.assertEqual(out[5], format(16, "016b"))   # i again -> 16

    def test_comments_and_spaces(self):
        a = assembler.Assembler()
        out = a.assemble(["  // only comment", "", "  D = M  // x", "  @ 5"])
        self.assertEqual(len(out), 2)

    def test_max_behaviour(self):
        with tempfile.TemporaryDirectory() as d:
            hack = os.path.join(d, "Max.hack")
            self.assertTrue(assembler.assemble_file(os.path.join(ROOT, "tests", "Max.asm"), hack))
            for r0, r1 in [(3, 5), (7, 2), (4, 4), (0, 9)]:
                m = hack_sim.Hack(hack_sim.load_rom(hack))
                m.ram[0], m.ram[1] = r0, r1
                m.run(200)
                self.assertEqual(m.ram[2], max(r0, r1))

    def test_error_messages_have_line_numbers(self):
        a = assembler.Assembler()
        a.assemble(asm_lines(os.path.join(ROOT, "tests", "bad.asm")))
        lines = sorted(n for n, _ in a.errors)
        # bad.asm: 4 @12abc, 5 D*A, 6 Q=D, 7 @40000, 8 D;JXX, 9 (LOOP, 10 @
        self.assertEqual(lines, [4, 5, 6, 7, 8, 9, 10])

    def test_no_crash_and_no_output_on_error(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "bad.hack")
            ok = assembler.assemble_file(os.path.join(ROOT, "tests", "bad.asm"), out)
            self.assertFalse(ok)
            self.assertFalse(os.path.exists(out))

    def test_missing_file_does_not_crash(self):
        self.assertFalse(assembler.assemble_file("does_not_exist.asm"))

    def test_duplicate_label_is_reported(self):
        a = assembler.Assembler()
        a.assemble(["(X)", "D=A", "(X)", "D=A"])
        self.assertEqual([n for n, _ in a.errors], [3])


class BoxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.hack = os.path.join(cls.tmp.name, "Box.hack")
        assert assembler.assemble_file(os.path.join(ROOT, "Box.asm"), cls.hack)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_key_pressed_draws_exact_box(self):
        m = run_machine(self.hack, key=65)
        black = {FIRST_ADDR + 32 * r + c
                 for r in range(HEIGHT) for c in range(WIDTH_WORDS)}
        for addr in range(16384, 24576):
            expected = 0xFFFF if addr in black else 0
            self.assertEqual(m.ram[addr], expected, "screen word %d" % addr)
        self.assertEqual(hack_sim.bounding_box(m), (0, 63, 19, 38))

    def test_no_key_screen_is_white(self):
        m = run_machine(self.hack, key=0)
        self.assertTrue(all(m.ram[a] == 0 for a in range(16384, 24576)))

    def test_box_disappears_when_key_released(self):
        m = hack_sim.Hack(hack_sim.load_rom(self.hack))
        m.ram[hack_sim.KBD] = 65
        m.run(50000)
        self.assertIsNotNone(hack_sim.bounding_box(m))
        m.ram[hack_sim.KBD] = 0
        m.run(50000)
        self.assertIsNone(hack_sim.bounding_box(m))


if __name__ == "__main__":
    unittest.main(verbosity=2)
