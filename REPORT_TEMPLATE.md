# Capstone Report: Make the Computer Draw a Box

**Name:** ______________________   **Roll no.:** ______________________   **K = 19**

**Course:** Nand to Tetris - I (ETCCNT301), School of Engineering & Technology, K.R. Mangalam University

## 1. My box (K = 19)
* Start row 19, 20 rows tall (rows 19 to 38)
* Width = 16 x ((19 mod 4) + 1) = 64 pixels = 4 words, starting at the left edge
* First word address = 16384 + 32 x 19 = 16992
* Assembler extra feature (19 mod 3 = 1): clear error messages with line numbers

## 2. Part A: the computer
Short description of CPU, Memory and Computer (3-4 lines each, from the README).
Screenshots (each showing "Comparison ended successfully"):
* CPU.tst  [screenshot]
* Memory.tst  [screenshot]
* ComputerAdd.tst  [screenshot]
* ComputerMax.tst  [screenshot]
* ComputerRect.tst  [screenshot]

Built-in chips used instead of my own: ______________ (write "none" if none)

## 3. Part B: the assembler
* Two readings: ...
* Symbol table and variables from address 16: ...
* Output compared with the official assembler: Add / Max / Rect / Pong  [screenshot of IDENTICAL x4]
* Extra feature: output of `python assembler.py tests/bad.asm`  [screenshot]

## 4. Part C: Box.asm
* Idea in a few lines (loop, key check, fill value, rows and columns, gap 28)
* Assembled with my own assembler: `python assembler.py Box.asm`
* Screenshot of the box in the CPU Emulator (key pressed)  [screenshot]
* Screenshot with key released (optional)  [screenshot]

## 5. One mistake I fixed
Write one honest paragraph about a real mistake you hit and how you fixed it
(what you expected, what happened, how you found the cause, the fix).
