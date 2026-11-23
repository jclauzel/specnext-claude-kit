# The TCP_ / SCK_ / UDP_ device

The same device (from uQLx) is in sQLux, QPC2, SMSQmulator and the Q68's Ethernet driver. Notes from sQLux 1.1.2's
sources and measurements on its Windows build, and from use on QPC2 5.02. **No original QL and no Next QL core has it.**

## Opening
| Open | Does |
|---|---|
| `io_open("TCP_host:port", 1)` | connect |
| `io_open("TCP_0.0.0.0:port", 2)` | bind; then trap #3 `$50` with D1 = backlog to listen |
| `io_open("SCK_", <the listening channel's id>)` | accept |
| `io_open("UDP_host:port", 1)` | a UDP socket with a peer (nothing is sent) |

- **Connect blocks the whole emulator** until the PC's kernel answers: at once for a refused port, 20 seconds or more
  for a machine that is off. Warn the user; there is no QL-side way round it on Windows.
- **Always write `0.0.0.0` to listen.** `TCP_:port` binds whatever address the PC's name lookup lists first, often a
  virtual adapter: nobody can reach it.
- Never port 0. Write the name as `TCP_a.b.c.d:port`, with the underscore and the colon.
- **Accept only after `io_pend` on the listening channel answers 0.** Without it: the emulator freezes (Linux, macOS) or
  you get an arbitrary error, usually -19 (Windows). Pass the listening channel's id exactly; sQLux checks nothing, and
  a stale id can crash it.
- **Windows sQLux never frees a closed listening port** until it exits: keep the channel and reuse it. On Linux and
  macOS a quick re-listen can fail while old connections linger.

## Reading and writing
- `io_pend` 0 = something to read, **or the peer has closed, or an error waits**; -1 nothing yet.
- `io_fstrg` with a timeout: 0 = full; -1 = timeout with what came so far (the count is positive); -10 = the peer
  closed, after any last bytes. Keep the partial count. It fills its buffer: ask for what you need, or use a short
  timeout.
- `io_sstrg` may send less than asked, with no error: loop on the count.
- `io_fline` costs one host call per byte: fine for short lines only.
- **Do not use trap #3 `$53` (IP_RECV)**: it ignores the timeout, blocks on Linux, and answers -19 for "nothing yet" on
  Windows.
- `$57` (shutdown) returns its own number in D0, and the datagram calls return a count there: test `D0 < 0`, never
  `D0 != 0`. `$7C` (last error) clears itself when read and is useless on Windows.

## Errors
Most network errors are -19 on sQLux. On its Windows build the code can be a stale one: treat any negative result of a
connect or an accept as "failed" and do not branch on the number. -7 from the open means there is no such device: that
is how to tell a QL without networking. Ask with key 0, once, and remember the answer.

## This machine's own address
Open `UDP_<a host you would talk to>:<any port>` with key 1 (no packet leaves), then trap #3 `$5C` (IP_GETSOCKNAME),
D2 = 16, A1 = a 16-byte buffer. Read the port at bytes 2-3 and the address at 4-7; ignore the first two (they are the
PC's own byte order on sQLux). The answer is the adapter that reaches that host. With no host in mind, `192.0.2.1` (a
documentation address) gives the default route's adapter. Looking up the PC's own name may give a virtual adapter. Do
it once a run: on Windows sQLux each closed socket may stay open on the PC.

## Elsewhere
SMSQmulator implements fewer calls; the Q68's driver is for a local network only (no retransmission). On an original QL,
networking is a modem on a serial port. Put your network code behind a few functions (connect, listen, accept, read,
write, pend, close), so that another back end, such as the Next core's Wi-Fi module, can be slotted in.
