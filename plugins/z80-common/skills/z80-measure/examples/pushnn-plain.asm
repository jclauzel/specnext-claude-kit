; Push a constant, plain Z80 (HL is lost).
        org     0
        ld      sp,$8000
t_start:
        ld      hl,$1234
        push    hl
t_end:
        halt
