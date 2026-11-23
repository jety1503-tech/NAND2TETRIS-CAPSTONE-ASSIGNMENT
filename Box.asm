// Box.asm  --  Nand to Tetris Capstone, Part C
// Student K = 19
//   start row  = 19
//   height     = 20 rows      (rows 19 .. 38)
//   width      = 16 * ((19 mod 4) + 1) = 64 pixels = 4 words
//   first word = SCREEN + 32*19 = 16384 + 608 = 16992
//
// While ANY key is pressed -> black box.  Key released -> box disappears.
//
// Variables (RAM 16..19, given by the assembler in order of first use):
//   fill = -1 (black) or 0 (white)
//   addr = address of the screen word being written
//   row  = rows still to draw
//   col  = words still to draw in the current row

(LOOP)                  // main loop: runs forever
    @KBD
    D=M                 // D = keyboard value (0 = no key)
    @BLACK
    D;JNE               // a key is pressed -> go and choose black
    @fill
    M=0                 // no key -> fill with white
    @DRAW
    0;JMP
(BLACK)
    @fill
    M=-1                // key pressed -> fill with black (all 16 bits = 1)

(DRAW)
    @16992              // <<< CHANGE HERE to move the box: SCREEN + 32*row
    D=A
    @addr
    M=D                 // addr = first word of the box
    @20                 // <<< box height in rows
    D=A
    @row
    M=D                 // row = 20

(ROW)                   // start of one row of the box
    @4                  // <<< box width in words
    D=A
    @col
    M=D                 // col = 4

(COL)                   // write one word
    @fill
    D=M                 // D = fill value
    @addr
    A=M                 // A = address to write
    M=D                 // RAM[addr] = fill
    @addr
    M=M+1               // next word in the same row
    @col
    M=M-1               // one word less to do in this row
    D=M
    @COL
    D;JGT               // more words in this row? repeat

    @28                 // <<< 32 - box width in words
    D=A
    @addr
    M=D+M               // addr jumps to the start of the next row
    @row
    M=M-1               // one row less to do
    D=M
    @ROW
    D;JGT               // more rows? repeat

    @LOOP
    0;JMP               // all rows drawn, check the keyboard again
