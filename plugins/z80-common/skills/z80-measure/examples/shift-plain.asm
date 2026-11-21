; DE <<= 3, plain Z80 chain.
        org     0
        ld      de,$1234
t_start:
        sla     e
        rl      d
        sla     e
        rl      d
        sla     e
        rl      d
t_end:
        halt
