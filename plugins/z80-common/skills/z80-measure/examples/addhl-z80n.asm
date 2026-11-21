; HL += A, Z80N: one instruction, DE untouched.
        org     0
        ld      hl,$1234
        ld      a,$56
t_start:
        add     hl,a
t_end:
        halt
