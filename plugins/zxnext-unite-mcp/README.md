# zxnext-unite-mcp

Connects Claude Code to the MCP server built into [ZX-Next-Unite](https://github.com/jclauzel/ZX-Next-Unite), a
desktop app for the ZX Spectrum Next. The plugin holds one `.mcp.json` that points at the app's server on
`http://127.0.0.1:2050/mcp`; it adds no code of its own.

## What it drives
Every tool is the same operation as a button in the app, so an agent can do what you can from the app and no more:

| Family | What the tools do |
|---|---|
| `app_*` | the app's status and log tails |
| `image_*` | load, create or download a NextZXOS SD image; list, get, put, rename and remove files in it; check whether MAME will boot it |
| `emulator_*` | start and stop MAME or CSpect on the loaded image, optionally running a program file |
| `catalog_*` | search the software catalogues (GetIt, ZXDB, zxArt, your itch.io library) and send downloads to the image or a Next |
| `next_*` | files on a real Next seated on the NextSync listener, and `next_deploy` (upload, CRC-32 check on the Next, run) |
| `nextsync_*`, `esp_emulation_*` | the NextSync servers and the RS232 ESP emulation |

The app's own documentation (`docs/MCP_SERVER.md` in its repository) lists every tool and has example prompts.

## Enable the server in the app
1. Start ZX-Next-Unite.
2. Settings: tick **Enable MCP server** (port 2050 by default). The NextSync console then says
   `MCP server listening on http://127.0.0.1:2050/mcp`. The setting persists.
3. The server binds to 127.0.0.1 only and refuses requests from web pages.

## Connect Claude Code
Either install this plugin:

```sh
claude plugin marketplace add jclauzel/zx-next-claude-kit
claude plugin install zxnext-unite-mcp@zx-next-claude-kit
```

or skip the plugin and add the server directly (the one-line connect; the app's Settings has a button that copies it,
with your port and token):

```sh
claude mcp add --transport http zx-next-unite http://127.0.0.1:2050/mcp
```

Use one or the other, not both, or you get the same tools twice. Check with `claude mcp list` (or `/mcp` in a
session): the server should show as connected. Tools are discovered when a session starts; in an open session `/mcp`
reconnects. Through the plugin, the tools are named `mcp__plugin_zxnext-unite-mcp_zx-next-unite__<tool>`; through
`claude mcp add`, `mcp__zx-next-unite__<tool>`.

**Another port or a bearer token:** this plugin's `.mcp.json` uses port 2050 and no token. If you changed the port or
turned on **Require bearer token**, use the `claude mcp add` line from the app's Settings instead (it includes both).

## If it does not connect
`Failed to connect` or `ECONNREFUSED` means the app is not running, the MCP toggle is off, or the port differs. Start
the app, tick the toggle, and reconnect with `/mcp`.

## Good manners for agents (put these in your CLAUDE.md)
- It is a desktop app: ask before starting it, and never stop it if you did not start it.
- `next_deploy` and the other `next_*` tools act on real hardware: use them only when the user asks.
- `image_rm`, `next_rm` and `next_rmtree` ask no confirmation.
- `claude-md/snippets/zx-next-unite-mcp.md` in this repository is a ready-made block.

## Tested on
The server address, the `claude mcp add` line and the tool families come from the app's documentation and from daily
use with Claude Code on Windows. This plugin's `.mcp.json` passes `claude plugin validate`; installing it from the
marketplace has **not** been tested yet.
