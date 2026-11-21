; Test bits of A, Z80N (A kept).
        org     0
        ld      a,$5A
t_start:
        test    $0F
t_end:
        halt
