# Nand to Tetris Capstone: Make the Computer Draw a Box

**Student K = 19**  (last two digits of roll number)

| Item | Value for K = 19 |
|---|---|
| Box start row | 19 |
| Box height | 20 rows (rows 19 to 38) |
| Box width | 16 x ((19 mod 4) + 1) = **64 pixels = 4 words** |
| First screen word | 16384 + 32 x 19 = **16992** |
| Assembler extra feature | 19 mod 3 = 1 -> **clear error message with line number** |

<img width="815" height="446" alt="image" src="https://github.com/user-attachments/assets/aa65a8c3-6ec5-4a95-a93e-2ca91b181a62" />

<img width="792" height="418" alt="image" src="https://github.com/user-attachments/assets/10e0c98c-63e1-42d2-8136-5536b811b124" />

<img width="825" height="477" alt="image" src="https://github.com/user-attachments/assets/c39fcb9b-889b-4a6f-ad20-00c7b46796cb" />

<img width="823" height="460" alt="image" src="https://github.com/user-attachments/assets/18c04bb6-cbfe-44e6-80a8-638ed8522bd2" />

<img width="833" height="451" alt="image" src="https://github.com/user-attachments/assets/c5b0fc26-7a2a-428a-8c7b-cb75823a0d18" />

<img width="823" height="553" alt="image" src="https://github.com/user-attachments/assets/0465328a-c0b0-40b2-8e72-8bee474d3e81" />

<img width="820" height="460" alt="image" src="https://github.com/user-attachments/assets/76541358-de48-46a7-a087-190be2a92eb0" />

## Folder contents

```
capstone/
  README.md            this file
  assembler.py         Part B: the Hack assembler (Python 3, no libraries needed)
  Box.asm              Part C: the box program
  Box.hack             made by assembler.py from Box.asm
  hdl/
    CPU.hdl  Memory.hdl  Computer.hdl      Part A
  tests/               small test programs + automatic self-tests
  tools/
    hack_sim.py        tiny simulator for a quick preview (not for the report)
    compare.py         compares your .hack file with the official one
  run_all.py           ONE command that checks everything
  REPORT_TEMPLATE.md   fill-in text for the 3-4 page report
```

## Quick start (2 minutes)

You need Python 3.8 or newer. Open a terminal in the `capstone` folder:

```
python run_all.py
```

It runs the self-tests, builds `Box.hack` with your assembler and shows the box
for "key pressed" and "key released". If it ends with "All good", Parts B and C
work. (On some systems the command is `python3`.)

Optional: `pip install pillow` lets the preview also save `box_preview_pressed.png`.

---

## Part A: Build the computer (HDL)

1. Copy `hdl/CPU.hdl`, `hdl/Memory.hdl`, `hdl/Computer.hdl` into the folder
   `nand2tetris/projects/05` (the official project 5 folder).
2. Start the **Hardware Simulator** (`tools/HardwareSimulator.bat` or `.sh`).
3. For each test: **File -> Load Script**, choose the `.tst` file, click **Run** (the double-arrow
   button) until the script ends, then take a screenshot that shows "End of script - Comparison ended successfully".
   - `CPU.tst`, `Memory.tst`
   - `ComputerAdd.tst`, `ComputerMax.tst`, `ComputerRect.tst`
4. If a chip fails because one of YOUR older lab chips (ALU, PC, Register ...) is wrong,
   remove your version from the folder: the simulator then uses the built-in one.
   Write this in your report.

**Note:** I could not run the official Hardware Simulator here, so the three HDL files are
written carefully but you must run the official tests yourself. If a test fails, the simulator
shows the first wrong line, fix that part and run again.

### How the three chips work

* **CPU**: bit 15 tells A-instruction (0) or C-instruction (1). An A-instruction loads the 15-bit value
  into the A register. A C-instruction goes to the ALU: x = D, y = A or M (bit 12 = a-bit),
  control bits come from bits 11..6. Destination bits 5, 4, 3 load A, load D, write M. Jump bits 2..0
  are compared with the ALU flags `zr` and `ng` to decide if the PC loads A or counts up.
* **Memory**: address bit 14 = 0 -> RAM16K; bit 14 = 1 and bit 13 = 0 -> Screen; both 1 -> Keyboard (24576).
  Two `DMux` send `load` to the right place, two `Mux16` pick what to read.
* **Computer**: ROM32K gives the instruction at address `pc`, CPU runs it, Memory is the data memory.

---

## Part B: The assembler

```
python assembler.py Box.asm                 # makes Box.hack
python assembler.py Add.asm Max.asm         # several files at once
python assembler.py Rect.asm -o mine/Rect.hack
```

### How it works

**Reading 1** (`first_reading`): go through the file once. Delete comments (`//`) and spaces, skip blank lines.
For a label `(LOOP)` store the number of the next real instruction in the symbol table. Labels are not
instructions, so they take no space.

**Reading 2** (`Assembler.assemble`): go through the remaining lines again.

* `@value` -> A-instruction `0` + 15-bit binary. A number is used directly. A name is looked up
  in the symbol table; if it is new it is a variable and gets RAM address 16, then 17, 18, ...
* `dest=comp;jump` -> C-instruction `111` + `a c1..c6` + `d1 d2 d3` + `j1 j2 j3`, using three
  small lookup tables (`COMP`, `DEST`, `JUMP`).

**Predefined symbols:** `R0..R15`, `SP`, `LCL`, `ARG`, `THIS`, `THAT`, `SCREEN` (16384), `KBD` (24576).

### Extra feature for K = 19: clear errors, no crash

Every problem is printed as `file: Line N: message` where N is the line in the **original** file.
All errors are listed (not only the first). If there is any error, no `.hack` file is written.
Try it:

```
python assembler.py tests/bad.asm
```

### Test against the official assembler (needed for the marks)

Copy `Add.asm`, `Max.asm`, `Rect.asm`, `Pong.asm` from the official `nand2tetris/projects/06`
folders into a work folder. For each one:

1. Official: open `tools/Assembler`, load the `.asm`, translate. It writes `X.hack` (rename it `X.official.hack`).
2. Yours: `python assembler.py X.asm -o X.mine.hack`
3. Compare: `python tools/compare.py X.mine.hack X.official.hack` -> must print `IDENTICAL`.

Take a screenshot of the four `IDENTICAL` results.

---

## Part C: The box program

`Box.asm` forever repeats: read the keyboard, choose the fill (-1 = all pixels black, 0 = white),
then write the fill into 20 rows x 4 words.

Pseudo code:

```
LOOP:
   fill = (KBD != 0) ? -1 : 0
   addr = 16992 ; row = 20
   ROW: col = 4
        COL: RAM[addr] = fill ; addr++ ; col--      repeat while col > 0
        addr = addr + 28                            (32 - 4: jump to the next row)
        row--                                       repeat while row > 0
   goto LOOP
```

Build and run:

```
python assembler.py Box.asm       # YOUR assembler, not the official one
```

Then in the official **CPU Emulator** (`tools/CPUEmulator`):

1. **File -> Load Program**, choose `Box.hack`.
2. **View -> Screen** (so the screen is visible).
3. Press **Run**. Click inside the emulator's keyboard area and hold any key: the black box appears
   (64 px wide, rows 19 to 38, at the left edge). Release the key: it disappears.
4. Take the screenshot while the key is held. If the screen does not update, change
   **Animate** in the toolbar (for example to "Program flow") and use a faster speed.

---

## Viva cheat sheet (5 minutes)

Typical live changes and where to do them (all marked `<<< CHANGE HERE` in `Box.asm`):

| Change | What to edit | Remember |
|---|---|---|
| Move box down by d rows | `@16992` -> `16992 + 32*d` | last row must stay under row 255 |
| Make it taller/shorter | `@20` | |
| Make it wider by one word | `@4` -> `@5` **and** `@28` -> `@27` | the two always add up to 32 |
| Invert (white box on black) | swap `M=0` and `M=-1` | |

Then run `python assembler.py Box.asm` again and reload `Box.hack` in the CPU Emulator.

Be ready to explain: why labels take no ROM space, why variables start at 16, why `A=M` is needed before
`M=D`, why the gap is 32 - 4 = 28, why -1 gives 16 black pixels, and why the error line number comes from
the original file.

## Submit

1. Put this folder into your lab repository as `capstone/`:
   ```
   git add capstone
   git commit -m "Capstone: HDL, assembler, Box"
   git push
   ```
   Do not commit `__pycache__` or the preview PNG.
2. Report (3-4 pages) from `REPORT_TEMPLATE.md`, plus your screenshots, on the course platform.
