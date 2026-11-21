; Push a constant, Z80N (HL kept). z88dk-ticks reads this operand in the opposite
; byte order from the Next: the timing is right, the pushed value is not.
        org     0
        ld      sp,$8000
t_start:
        push    $1234
t_end:
        halt
