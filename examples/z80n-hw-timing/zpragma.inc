// zpragma.inc - the crt settings of z80ntime (z88dk newlib, +zxn, the 48K RAM model at $8000).
#pragma output CLIB_MALLOC_HEAP_SIZE = 0
#pragma output CLIB_STDIO_HEAP_SIZE  = 0
#pragma output CLIB_FOPEN_MAX        = 0
// The terminal's own copy of the Spectrum font, so the text does not depend on which ROM is paged in.
#pragma redirect CRT_OTERM_FONT_8X8 = _font_8x8_zx_system
