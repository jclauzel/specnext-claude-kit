---
name: zxnext-mame
description: Run, time and prove a ZX Spectrum Next program on MAME (specnext_ks3) - start runs safely (a fresh copy of the SD image, an untouched ROM zip, a cap on concurrent MAME processes), skip the ROM warning, drive keys and take per-frame shots and logs through a Lua autoboot script, read a frame report (worst raster line out of the frame's lines) against a budget, apply the phase rule, and compare runs frame for frame and pixel for pixel. Use this skill whenever a Next .nex has to be run, played, timed, screenshotted, logged or compared on MAME or an emulator, including frame-time questions ("is level 5 still under budget?"), "take a shot of", "prove it on MAME", or checking that a change kept every game value, even if MAME is not named.
---

# Running and proving ZX Spectrum Next programs on MAME

If the ZX-Next-Unite MCP tools are connected (the `zxnext-unite-mcp` plugin), they can load a disk image, put a file
in it and start or stop MAME or CSpect: use them for a quick look. For timed proofs, logs and named shots, use a
runner script of your own that starts MAME with a Lua autoboot script (`references/lua-runner.md`), which gives exact
control over keys, frames and logs.

## Safety first (each of these has bitten someone)
- **The SD image:** never run on the original. Copy it into the run's own work folder for every run, check the copy's
  hash against the original's, and delete the copy (often 2 GB) once the evidence is saved. MAME writes to the image.
- **The ROM zip:** never edit it. If a ROM must change, use a private `-rompath` copy. Check its hash before each run.
- **Processes:** cap the MAME processes running at once on the machine (two is a sensible cap; other projects may run
  MAME too). Count them before starting, wait while the cap is reached, never kill a MAME you did not start, and leave
  nothing running when you finish.
- **One configuration for proofs:** pick the refresh rate and display mode the release uses (for example 60 Hz only)
  and prove everything there; runs in other modes are not comparable.

## Launching a run
- Tested with MAME 0.289, machine `specnext_ks3`. Its default BIOS models core 3.02.04; a real Next may run a newer
  core, so MAME is a close model, not the hardware. Headless: `-video none -sound none -str <seconds> -nothrottle`.
- **MAME's frame lines are an upper bound at 28 MHz.** MAME 0.289 adds one wait cycle to every memory read at 28 MHz;
  a KS3 on core 3.03.03 shows none for code running from $8000 up (`examples/z80n-hw-timing`). So a frame that fits
  the budget on MAME fits on that hardware, which reads lower; do not tune to MAME's last line.
  The image goes in with `-hard1 <img>`; the script with `-autoboot_script <lua> -autoboot_delay <s>`.
- **The ROM warning:** a windowed MAME (and one started through ZX-Next-Unite) stops on a "One or more ROMs ...
  incorrect" message at every start. About half a second after starting it, send a couple of SPACE presses into the
  emulator (the Lua key schedule can do it with its first keys, or the MCP or a key-sending tool when MAME runs
  interactively); otherwise the run sits on the warning and every frame count after it is off. Headless runs
  (`-video none`) are not held by it.
- Keep the `.map` beside the `.nex`: the Lua script finds the program's variables through it.
- Keys are a schedule (`token@from-to`, frames counted from when the script starts, which is after the autoboot
  delay). Hold a key 20-40 frames: a key held for a frame or two is lost inside the program's own waits. Reuse the
  previous step's key files so runs line up.
- Shots: a range (`from,to,every`) or a list of named frames. Name each file by its frame number: MAME's own numbering
  slows down badly once a snapshot folder holds thousands of files.

## The logs and what they cost
- A write tap (`install_write_tap`) on an address the program writes, or a read of a memory share, costs the emulated
  program nothing: use them for game values, sound registers, sprite attributes.
- A Lua read through the CPU's program space every frame can cost emulated CPU time: in one project a tile log read
  that way added about 1.4 lines to every frame. Leave such logs off in timed runs and take them in a separate run.
- Lua reads can move counters the program keeps: only compare runs made with the same log options.

## The frame report (a debug build)
- A debug build records, at the end of each frame's work, the raster line it reached (Next registers $1E/$1F give the
  active video line) and keeps each level's worst, plus counts of late frames (more than one frame's work) and sprite
  overflow. It shows the figures on a screen the runner can photograph.
- A Next frame at 60 Hz has 264 lines. Set a budget below that with headroom (one project allows a worst line of 245
  of 264 and no late frames) and report each level's worst against the previous step on the same keys, naming the
  frame of any change. MAME never sets the sprite overflow flag, so check that one on hardware.

## The phase rule
Only compare runs whose program frame counters line up at the same point (for example each level's first frame). A
run that is one frame out against the reference is repeated and named, never counted.

## Comparing runs
- Game values frame for frame from the logs, from the first frame that matters, ignoring bytes nothing has written.
- The sound log equal once the addresses of moved code are set aside.
- Shots pixel for pixel against the previous step's same frames. Expect some known classes (an effect a frame sooner
  because the CPU finished sooner) and name them; anything else is a real difference: find its cause.
- **Look at the shots** yourself at 1x and 3x and say what you saw, not only what a script counted.
- Keep the runner and proof scripts in the repo (for example `extra/proofs/` with a README); their output stays out.

## What to report
The bytes run (hash), the runs made (keys, shift, options, in phase or repeated), each level's worst line against the
reference, late frames, game values and sound equal or not, shot classes with counts, what you looked at, where the
evidence is, and that nothing of yours is left running.

## Additional resources
- `references/lua-runner.md`: the shape of a Lua autoboot runner (keys, shots, write taps, the reset guard).
