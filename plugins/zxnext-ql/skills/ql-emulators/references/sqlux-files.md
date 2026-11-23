# sQLux: files on a PC folder (`DEVICE = WIN1,<folder>/,qdos-like`)

Read in sQLux 1.1.2's sources and measured on its Windows build in October 2026. Other builds may differ: check a newer
one before you work round something.

| What | Detail |
|---|---|
| names | host `.` shows as `_`, host folders as `name_`; a new file keeps the QL's spelling; `a.b` and `a_b` cannot be told apart; case is ignored |
| directory open (key 4) | succeeds for **any** name and lists what starts with it: not a test for a directory |
| a sub-directory's entry | Windows: type 0, length 0 (Linux: 255). A 0-length entry that cannot be opened as a file is a directory |
| an entry's length | size + 64; an **open channel's header** says the raw size (64 less than on QDOS): seek to the end instead |
| a file with the `]!QDOS` prefix | the length in a listing is not its data length: compare contents, not sizes |
| make directory | Windows 1.1.2: fails with -7, the empty placeholder stays: delete it. Fixed in master (pull request 112) |
| rename | Windows 1.1.2: -20 always (same cause, same fix); on every build -20 on a shared channel, -12 past 36 characters, -8 if the target exists |
| delete a directory | answers 0 and does nothing: the empty folder stays on the PC |
| key 3 over a file with the prefix | the new data lands after 30 NUL bytes: delete first, create with key 2 |
| setting a header | puts a 30-byte `]!QDOS File Header` in front of the file on the PC, and reads 64 bytes from your buffer; setting type 0 on such a file can crash the emulator |
| an `XTcc` trailer | read when there is no prefix: type 1 and the dataspace, so a linked job runs as it is |
| free space | fixed numbers on every call |
| a name of exactly 36 characters | does not open |
| a folder whose QDOS name is 32 characters or more | does not list: its entries come back garbled or not at all |
| a trailing dot or space | dropped by Windows: a copy onto `name.` can truncate `name` itself |
| file locking | none: two jobs can open one file for writing, unlike SMSQ/E |
| the resolved path on the PC | keep it short: a path of more than 63 characters can overrun a buffer in the emulator |

## Configuration that works for tests
`SYSROM`, `ROMIM` (Toolkit II, for `EW` and `EX`), `RAMTOP = 4096`, `FAST_STARTUP = 1`, `SKIP_BOOT = 1`,
`DEVICE = WIN1,<folder>/,qdos-like`, `BOOT_DEVICE = WIN1`, `SPEED = 0`; start with `-f <ini> -b "<line>"`. The script
writes exactly this. The 50 Hz tick stays real at every `SPEED`.

## The picture
`FIXASPECT = 1` gives a 4:3 picture, `FILTER = 0` crisp pixels. `WIN_SIZE` 1x, 2x, 3x, max and full all work. A
`RESOLUTION` above 512x256 leaves a 512 x 256 program in the top left corner.

## Pointer Environment
Copy a `ptr_gen` into the mounted folder and start with `LRESPR win1_ptr_gen:PAUSE#2,1:` in front of your line. The user
supplies the file. sQLux has no mouse without it.
