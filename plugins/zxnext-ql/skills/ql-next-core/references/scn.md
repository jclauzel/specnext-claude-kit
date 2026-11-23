# Drawing in 256 colours through SCN

SCN is Simon N Goodwin's colour device driver for the Spectrum Next's QL core
(<https://simon.mooli.org.uk/QL/SCN/>, CC BY-NC-SA 4.0). These are behaviours of version 1.48, from its documentation
and published source, and from use on a KS2 with the 2024 core. Do not bundle it or copy from it: the user fetches it
and your program opens its device. Credit its author on your project's page.

- `OPEN #3,scn_512x256a0x0` opens the whole 256 x 256 screen, a byte a pixel. **The byte is RRRGGGBB** (seen on the
  KS2).
- **Output only.** Every input call and the cursor calls answer -19: keep your console for keys and draw on SCN's
  channel.
- Coordinates are mode 8's: x in 512 units, halved. CSIZE 0 and 1 become 2 and 3.
- Keep text x on a multiple of 4 units: the fast text paths store words at the character's own address, and an odd pixel
  would be an odd address.
- The block fill takes the raw colour byte and **does not clip**: past the edge it answers -4 and draws nothing. Clip
  first.
- Position every string and send no line feed: a pending newline can scroll the screen.

## Loading and starting
- On the 2024 core SCN's screen is at `$20000`, over the QL's two screens, so the system variables must be at `$30000`:
  start Minerva with **twin screens**. With one screen the load (`LRESPR`) stops with "in use". On later cores SCN uses
  `$4C0000` (source, not run).
- SCN chooses by the ID word when it loads. Do not decide by that word yourself: it is not decoded on the 2024 core, and
  a check on it failed at one start and passed a minute later. Read where the channel really draws, from its channel
  block, instead.
- Load it once: look for its name in the device driver list first.

## Showing it
SCN does not switch the display. Its own `MODE256` writes `$800012` = 0, then `$80000E` = 9; going back writes
`$80000E` = 0, then `$800012` = 0. Do the same with byte stores from variables, after the gates of `SKILL.md`, and:
1. have no console call pending; clear SCN's screen; then switch;
2. on the way out clear it to black first (the QL screens are under it), switch back, then set the mode you found;
3. at your program's start, switch back once if the gates pass: a killed run may have left the colours on.

Only test by the display on the machine itself: no emulator has SCN's registers. Write a fallback to mode 8 or 4, with
the reason logged, and test that on the emulators.

## 256 colours elsewhere
On QPC2 and other SMSQ/E high-colour displays the console itself takes 24-bit colours: see the console notes of the
`ql-qdos-c` skill.
