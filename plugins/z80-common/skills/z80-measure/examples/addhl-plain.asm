; HL += A, plain Z80: zero-extend A into DE, then add.
        org     0
        ld      hl,$1234
        ld      a,$56
t_start:
        ld      e,a
        ld      d,0
        add     hl,de
t_end:
        halt
