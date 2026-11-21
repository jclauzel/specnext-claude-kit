; DE <<= 3, Z80N barrel shift (B = shift count).
        org     0
        ld      de,$1234
t_start:
        ld      b,3
        bsla    de,b
t_end:
        halt
