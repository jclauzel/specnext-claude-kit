; DE = D * E (unsigned 8x8), plain Z80 shift-and-add loop. Time depends on the data.
        org     0
        ld      d,$5A
        ld      e,$C3
t_start:
        ld      hl,0
        ld      a,d
        ld      d,0
        ld      b,8
mul_loop:
        add     hl,hl
        rla
        jr      nc,mul_skip
        add     hl,de
mul_skip:
        djnz    mul_loop
        ex      de,hl
t_end:
        halt
