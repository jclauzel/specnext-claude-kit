# Registers of the Next's QL core

Byte addresses, big-endian words. **Seen** means run on a KS2 with the core named; **source** means read in the core's
published sources or in SCN's published documentation, not run. Pass the gates in `SKILL.md` before any access.

| Address | Size | Meaning | Status |
|---|---|---|---|
| `$80000E` | byte | display mode: 0 the QL's screen, 9 with SCN's 256 colours | seen, 2024 (read-back not documented) |
| `$800012` | byte | a display switch SCN clears before `$80000E` = 9, and clears again on the way back | seen, 2024 |
| `$80001E` | word | the core's ID, `$4E32` | seen, 2026; **not decoded on 2024** |
| `$800024` | byte, read | UART status: bit 0 a byte has come, bit 1 room to send | seen, 2026 |
| `$800024` | byte, write | strobes: 1 = send the byte in `$800025`, 2 = step to the next received byte | seen, 2026 |
| `$800025` | byte | the data; a read does not step the FIFO | seen, 2026 |
| `$80002C` | word, write | UART divisor, 22 MHz / baud: 191 = 115200, 19 = 1 152 000, 11 = 2 000 000 | seen, 2024 and 2026 |
| `$800030` | word, read | high word of a 1 MHz counter; the read latches the low word | source; test that it counts |
| `$800032` | word, read | the latched low word | source; test that it counts |

## The UART without a driver
- A strobe acts on its rising edge: write 1 (or 2), then 0. Write 0 once before the first use.
- To send: wait for bit 1, write the byte to `$800025`, strobe 1. To receive: while bit 0 is set, read `$800025`, then
  strobe 2. Give both loops a limit.
- Write from variables. A constant 0 may compile to `CLR.B`, which **reads before it writes** on a 68000.
- The FIFOs hold 1 024 bytes each way. The module's CTS is tied low and its RTS and reset are not wired to the QL side.
- Where `ESP1` opens, use the driver instead: `io_fstrg` on it with a timeout behaves as a polled byte pipe (a timeout
  returns the partial count). Two users of the same UART take each other's bytes.
- Timing a wait: read `$800030` first, then `$800032`. If two readings over a second differ by nothing, the counter is
  not there: fall back to 1-frame suspends, and to a rate that 1 024 bytes a frame can carry (115200).

## Frame clock
The 50 Hz interrupt of the core does not follow the Next's 50 or 60 Hz display (source): frame timeouts are 20 ms.
