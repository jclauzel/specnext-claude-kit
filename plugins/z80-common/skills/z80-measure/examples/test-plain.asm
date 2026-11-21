; Test bits of A, plain Z80 (A is lost).
        org     0
        ld      a,$5A
t_start:
        and     $0F
t_end:
        halt
