; The same 100 passes laid out so the common case FALLS THROUGH: jr cc costs 7 T not taken.
        org     0
        ld      a,1
t_start:
        ld      c,100
br_loop:
        or      a
        jr      z,br_rare
br_back:
        dec     c
        jr      nz,br_loop
        jr      t_end
br_rare:
        inc     e               ; the rare case, out of line
        jr      br_back
t_end:
        halt
