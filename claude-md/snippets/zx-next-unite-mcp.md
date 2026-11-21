# Snippet: the ZX-Next-Unite MCP server

For Next projects that use the [ZX-Next-Unite](https://github.com/jclauzel/ZX-Next-Unite) app. Paste the block into
your user or project `CLAUDE.md`. The `zxnext-unite-mcp` plugin connects the server; this block tells Claude how to
behave with it.

```markdown
## The ZX-Next-Unite MCP server (MAME, CSpect, disk images and real Nexts)
- The ZX-Next-Unite app has an MCP server: its tools let an agent load or download a disk image, put files into it,
  start and stop MAME or CSpect on it (optionally with a program to run), push a build to a real Next and run it
  (`next_deploy`: upload, CRC-32 check, run), search the software catalogues and read the app's logs. Families:
  `app_*`, `image_*`, `emulator_*`, `catalog_*`, `next_*`, `nextsync_*`, `esp_emulation_*`. Prefer them to driving
  MAME by hand for a quick look.
- Push a build to a real Next (`next_deploy`) only when I ask: I run the hardware tests myself.
- Connect once: `claude mcp add --transport http zx-next-unite http://127.0.0.1:2050/mcp` (or install the
  `zxnext-unite-mcp` plugin), then check `claude mcp list`. In an open session, `/mcp` reconnects.
- If its tools are missing or it fails to connect (ECONNREFUSED), the app is not running or its server is off: ask me
  before starting the app, then make sure Settings -> Enable MCP server is ticked. Never stop the app if you did not
  start it.
```
