; 100 passes (t_start sits before the loop: ticks restarts its count each time PC hits it)
; where the common case (A <> 0) TAKES the branch: jr cc costs 12 T taken.
        org     0
        ld      a,1
t_start:
        ld      c,100
br_loop:
        or      a
        jr      nz,br_common
        inc     e               ; the rare case
br_common:
        dec     c
        jr      nz,br_loop
t_end:
        halt
