# A Lua autoboot runner for MAME's Next drivers

Status: the calls below are the ones a working runner used on MAME 0.289 (`specnext_ks3`). This skeleton puts them
together in a shorter form and has **not** been run as written: check it on your MAME version before relying on it.

## How the pieces fit
- A runner script (PowerShell, Python, shell) copies the SD image into a work folder, sets environment variables for
  the schedule (a Lua autoboot script takes no arguments), then starts MAME:
  `mame specnext_ks3 -rompath <roms> -hard1 <copy.img> -autoboot_delay <s> -autoboot_script runner.lua`
  plus `-video none -sound none -str <seconds> -nothrottle` for a headless run, and `-snapshot_directory <dir>` for
  shots.
- The frame counter starts when MAME runs the script, after `-autoboot_delay`, not at power-on.
- MAME runs the autoboot script **again after a machine reset**, and the Next resets itself during its boot. Without a
  guard, two copies of the frame callback run and every shot comes out twice.

## Skeleton
```lua
-- runner.lua: keys and shots on a frame schedule (sketch; see the status note above)
if _G.runner_loaded then return end            -- the reset guard
_G.runner_loaded = true

-- every input field by name; MAME names Spectrum keys by their whole keycap legend
local fields = {}
for _, port in pairs(manager.machine.ioport.ports) do
  for name, field in pairs(port.fields) do fields[tostring(name)] = field end
end
local function key(pattern)                    -- e.g. key("^SPACE"), key("^q%s")
  for name, field in pairs(fields) do if name:match(pattern) then return field end end
end

-- schedule: { field, from, to } holds a key down from frame `from` to frame `to`
local holds = { { key("^SPACE"), 30, 34 }, { key("^SPACE"), 40, 44 } }   -- skip the ROM warning
local shots = { [200] = true, [400] = true }

local frame = 0
emu.register_frame_done(function()
  frame = frame + 1
  for _, h in ipairs(holds) do
    if h[1] then h[1]:set_value((frame >= h[2] and frame < h[3]) and 1 or 0) end
  end
  if shots[frame] then manager.machine.video:snapshot() end
end)
```
Write a key's field only when its level changes if several entries can hold the same key.

## Logging without slowing the program
Find the CPU's address spaces, then tap writes the program makes anyway:

```lua
local prog
for _, dev in pairs(manager.machine.devices) do
  if dev.spaces and dev.spaces["program"] and dev.spaces["io"] then prog = dev.spaces["program"]; break end
end
local log = io.open(os.getenv("RUNNER_LOG"), "w")
local tap = prog:install_write_tap(0x8000, 0x8000, "frame_tap", function(offset, data, mask)
  log:write(string.format("%d %02X\n", frame, data & 0xff))
end)
local stop = emu.add_machine_stop_notifier(function() log:close() end)
```
Keep the returned handles (`tap`, `stop`) in variables that live as long as the run, or the tap is collected. Take the
address from the `.map` (the runner can pass it in an environment variable).
