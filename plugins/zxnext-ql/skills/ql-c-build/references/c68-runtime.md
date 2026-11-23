# qdos-gcc 2.95.3 and the C68 library: what the compiler and the start-up really do

Read from the toolchain itself (gcc's `qdos.h` target file, the headers, a disassembly of `libc.a` v4.24.5 and `crt.o`
v4.24i) and checked by a second pass. Anything not settled that way is marked **unverified**.

## Language and types
- GNU C89: declarations at the start of a block, no `stdint.h`, no `snprintf`. `//` comments and `inline` are accepted
  unless you pass `-ansi`.
- `int`, `long`, pointers, `chanid_t`, `jobid_t`: 4 bytes. `short` and `timeout_t`: 2. `colour_t`: 1. `char` is signed.
  Big-endian.
- **Everything is aligned to 2 bytes**: `sizeof(struct {char c; long l;})` is 6. QDOS's 64-byte file header needs no
  packing pragma. A word or long access at an odd address is an address error: read wire fields byte by byte or with
  `memcpy`.
- 32-bit `*`, `/` and `%` and every `double` operation are library calls. Keep inner loops to `short` and shifts. A `%`
  per byte in a ring buffer is a library call per byte: compare and wrap instead.
- `long long` helpers are in `libgcc.a`; a program that uses them without stdio may not link (**unverified**).
- The library's `wchar_t` is `char` but `L"..."` literals are 4 bytes each: never use wide literals.
- `atoi`, `atol` and `atof` are macros; `EXIT_FAILURE` is -1; `clock()` always returns -1.
- A CRC-32 is not a `long`: half of all values look negative, hence like an error. Return it through a pointer.

## Calling convention
- Scratch: `d0-d2`, `a0`, `a1`. Kept: `d3-d7`, `a2-a6`. Result in `d0` (`double` in `d0/d1`).
- **Prototypes are mandatory.** `short` and `char` arguments take one 16-bit slot when a prototype is in scope (a `char`
  in the low byte, the high byte undefined) and 4 bytes when it is not, so an unprototyped call shifts every argument
  after it. Always include `<qdos.h>`.
- Never make a `char` or `short` the last fixed parameter of a variadic function (`va_start` is off by 2), and never
  `va_arg(ap, short)`.
- Structs of exactly 1, 2, 4 or 8 bytes come back in registers, others through a hidden pointer in `a1` (C68 differs):
  return through a pointer argument.

## Traps from C
- Without assembly: `qdos1` / `qdos2` / `qdos3(REGS_t *in, REGS_t *out)` load `d0-d3/a0-a3`, trap, and store them back.
- Inline: `register long d0v asm("d0") = op;` and so on, then `asm volatile("trap #3" : ... : ... : "memory", "cc")`.
  Declare every register the trap may change, `a3` included for extension traps.
- `IO.OPEN` by an inline `trap #2` answered -15 each time in one project, with the real job id as the owner: use the
  library's `io_open`, which passes -1 and hands the key through untouched.

## Start-up
1. `crt.o` takes `_stack` bytes from the common heap, clears the bss, writes `_prog_name` (30 characters at most) into
   the job, then calls the library.
2. The library reads the command string **in place** and consumes its own options before `argv` is built: `<file`,
   `>file`, `>>file`, `2>file`, a bare `&`, `=N` (raise the stack), `%N` (raise the first heap). `=0` and `%0` kill the
   job with -15. Keep `< > = % &` out of the first character of your own arguments; a user's `>win1_x` truncates that
   file before `main` runs.
3. The first heap is `_mneed` + `_stack` + 8 bytes. When it does not fit, the job ends at once with error 0.
4. stdin, stdout and stderr: channels given with `EX job,#a,#b,#c` become stdin, **stderr, stdout** in that order. If
   none is given, a console is opened, redefined and cleared, even by a program that never prints. Set `_consetup = 0`
   to keep a console you pass in untouched.

## Variables you can define in your program
| Variable | Default | Meaning |
|---|---|---|
| `long _stack` | 5120 | the C stack |
| `long _mneed` | 8192 | the first heap (0: all but `_memqdos`; negative: leave that much) |
| `long _memqdos` | 20480 | bytes always left to QDOS when the heap grows |
| `long _memincr` | 4096 | heap growth step (each is an `MT.ALCHP`) |
| `char *_endmsg` | "Press a key to exit" | set to 0 for scripted runs, or the job waits for a key |
| `char _prog_name[]` | "C_Program" | the name in `JOBS`; an array, 30 characters |
| `WINDOWDEF_t _condetails` | 484 x 215 at 16,26, red border | the console's geometry and colours |
| `void (*_consetup)(chanid_t, WINDOWDEF_t *)` | the library's | 0 keeps the console as opened |

The heap is the common heap, not the dataspace: `mt_free()` gives the largest free block. `mt_alchp` and `iop_pinf`
return the error code cast to a pointer, never NULL: test `(long)p < 0`.

## Exit, being killed, starting another job
- `exit(0)` or a return from `main`: `atexit` runs, stdio is flushed, the job is removed. `EW` shows a non-zero code as
  a QDOS error.
- A job that is removed by another gets no notice. Write to a temporary name and rename at the end.
- `qforkv` with owner 0 starts a job that lives on after its parent ends (seen on sQLux; a release that restarts itself
  this way has run on a Next's QL core and on QPC2).
- There is no break signal: `CTRL+SPACE` stops SuperBASIC, not a C job. Give every long loop its own ESC check.

## Timing
- Timeouts are 1/50 s frames in a `short`; -1 waits for ever. `sleep()` wraps past 655 s.
- The clock (`mt_rclck`) counts whole seconds since 1961. There is no 50 Hz counter in Minerva's system variables: pace
  a loop with 1-frame waits and count those.
