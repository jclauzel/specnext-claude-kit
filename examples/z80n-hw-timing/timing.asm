; timing.asm - the measured blocks and the line-counting driver of z80ntime.
;
; Each block is one instruction (or one short group) repeated BLOCK_N times by REPT, then a ret. The driver calls a
; block LOOPS times with interrupts off and counts the raster lines that pass, reading the Next's active video line
; counter (NextReg $1E/$1F) after every call so that frame wraps are counted (a block is far shorter than a frame).
; The C side subtracts the empty block (a lone ret: the loop's own cost) and divides by the nop block.
;
; Everything here lives at $8000 and up (banks 2 and 0: never contended), and so does the stack.

SECTION code_user

PUBLIC _m_block, _m_loops, _m_flen
PUBLIC _measure_run, _frame_lines, _set_speed, _read_reg, _soft_reset

defc BLOCK_N = 500              ; the repeat count of every block (the same for all of them)

; ---------------------------------------------------------------- the measured blocks
; Keep these exactly the instructions named: the C table's labels describe them.

PUBLIC _blk_empty, _blk_nop, _blk_and, _blk_test, _blk_pushnn, _blk_pushhl, _blk_addhla, _blk_mul, _blk_addhlde

_blk_empty:
   ret

_blk_nop:
   REPT BLOCK_N
      nop
   ENDR
   ret

_blk_and:
   REPT BLOCK_N
      and $0F
   ENDR
   ret

_blk_test:
   REPT BLOCK_N
      test $0F                  ; Z80N: ED 27 n
   ENDR
   ret

_blk_pushnn:
   REPT BLOCK_N
      push $1234                ; Z80N: ED 8A hi lo
      pop hl
   ENDR
   ret

_blk_pushhl:
   REPT BLOCK_N
      ld hl,$1234
      push hl
      pop hl
   ENDR
   ret

_blk_addhla:
   REPT BLOCK_N
      add hl,a                  ; Z80N: ED 31
   ENDR
   ret

_blk_mul:
   REPT BLOCK_N
      mul d,e                   ; Z80N: ED 30
   ENDR
   ret

_blk_addhlde:
   REPT BLOCK_N
      ld e,a
      ld d,0
      add hl,de
   ENDR
   ret

; ---------------------------------------------------------------- the driver

; read_line: HL = the active video line (0 = the first line of the ULA display). The two halves are read
; MSB, LSB, MSB again and read again if the MSB moved (the 255 -> 256 step or the frame wrap fell between them).
; Uses A, BC.
read_line:
   ld bc,$243B
rl_again:
   ld a,$1E
   out (c),a
   inc b                        ; $253B
   in h,(c)
   dec b
   ld a,$1F
   out (c),a
   inc b
   in l,(c)
   dec b
   ld a,$1E
   out (c),a
   inc b
   in a,(c)
   dec b
   cp h
   jr nz,rl_again
   and $01
   ld h,a
   ret

; uint16_t measure_run(void): call the block at m_block m_loops times (m_loops >= 1), interrupts off;
; return the lines counted from the start of line 0 to the read after the last call. m_flen must hold the frame's
; line count (frame_lines). Keeps IX and IY (zsdcc's), restores the interrupt state.
_measure_run:
   ld a,i                       ; P/V = IFF2: were interrupts on?
   push af
   di
   ld hl,(_m_block)
   ld (mr_call+1),hl            ; patch the call below
   ld hl,(_m_loops)
   ld (mr_count),hl
   ld hl,0
   ld (mr_base),hl
mr_sync1:                       ; wait to leave line 0 ...
   call read_line
   ld a,h
   or l
   jr z,mr_sync1
mr_sync2:                       ; ... then for line 0 to start
   call read_line
   ld a,h
   or l
   jr nz,mr_sync2
   ld (mr_prev),hl              ; 0
mr_loop:
mr_call:
   call _blk_empty              ; operand patched to m_block
   call read_line
   ld de,(mr_prev)
   ld (mr_prev),hl
   or a
   sbc hl,de
   jr nc,mr_nowrap
   ld hl,(mr_base)              ; the line counter wrapped: one more frame
   ld de,(_m_flen)
   add hl,de
   ld (mr_base),hl
mr_nowrap:
   ld hl,(mr_count)
   dec hl
   ld (mr_count),hl
   ld a,h
   or l
   jr nz,mr_loop
   ld hl,(mr_base)
   ld de,(mr_prev)
   add hl,de                    ; lines = frames x m_flen + the last line (the start was line 0)
   pop af
   ret po
   ei
   ret

; uint16_t frame_lines(void): the frame's line count (the highest line seen + 1), interrupts off meanwhile.
; Call it at 28 MHz: a pass of the loop must be shorter than a line.
_frame_lines:
   ld a,i
   push af
   di
   call read_line
fl_wrap1:                       ; wait for a wrap
   ld (mr_prev),hl
   call read_line
   ld de,(mr_prev)
   ex de,hl
   or a
   sbc hl,de                    ; prev - cur: carry when cur > prev
   ex de,hl
   jr c,fl_wrap1
   jr z,fl_wrap1
fl_wrap2:                       ; follow the frame to the next wrap
   ld (mr_prev),hl
   call read_line
   ld de,(mr_prev)
   ex de,hl
   or a
   sbc hl,de
   ex de,hl
   jr c,fl_wrap2
   jr z,fl_wrap2
   ld hl,(mr_prev)              ; the last line before the wrap
   inc hl
   pop af
   ret po
   ei
   ret

; void set_speed(uint8_t s) __z88dk_fastcall: NextReg $07 = s (0 3.5 MHz, 1 7, 2 14, 3 28)
_set_speed:
   ld a,l
   nextreg $07,a                ; Z80N
   ret

; void soft_reset(void): back to NextZXOS. Its .nex loader has no way back to BASIC (a plain return crashed back
; through the boot on MAME), so the program leaves the way the NextZXOS menu's own reset does: NextReg $02 bit 0.
_soft_reset:
   di
   nextreg $02,$01              ; Z80N: soft reset
sr_wait:
   jr sr_wait

; uint8_t read_reg(uint8_t r) __z88dk_fastcall: read a Next register (reading needs the ports)
_read_reg:
   ld bc,$243B
   out (c),l
   inc b
   in l,(c)
   ret

SECTION bss_user

_m_block:   defw 0
_m_loops:   defw 0
_m_flen:    defw 0
mr_prev:    defw 0
mr_base:    defw 0
mr_count:   defw 0
