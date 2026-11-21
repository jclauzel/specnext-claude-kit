; DE = D * E (unsigned 8x8), Z80N.
        org     0
        ld      d,$5A
        ld      e,$C3
t_start:
        mul     d,e
t_end:
        halt
