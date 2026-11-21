# Snippet: Z80N first

For ZX Spectrum Next projects with assembly. Paste the block into your project's `CLAUDE.md` (or your user
`~/.claude/CLAUDE.md` if every project of yours targets the Next). Pairs with the `z80n-optimize` skill.

```markdown
## Assembly language: Z80N first
- Whenever you write or change assembly, use a Z80N instruction wherever one can replace plain Z80.
  z88dk's `+zxn` (or `-mz80n`) assembles all of them. Our Nexts run core <your core version>.
- The forms to reach for: `add hl,a` / `add de,a` / `add bc,a` and `add hl,nn` / `add de,nn` / `add bc,nn` for index
  and pointer sums (in place of `ld e,a / ld d,0 / add hl,de`); `mul d,e` for multiplies; the barrel shifts
  `bsla de,b`, `bsra de,b`, `bsrl de,b`, `bsrf de,b`, `brlc de,b` in place of shift chains; `ldix`, `ldirx`, `lddx`,
  `lddrx`, `ldpirx`, `ldws` for copies and fills; `nextreg n,a` / `nextreg n,n` for every Next register, never `out`
  to $243B / $253B; `outinb`, `pixeldn`, `pixelad`, `setae`, `swapnib`, `mirror a`, `jp (c)` where they fit.
- `push nn` and `test n` only after measuring: they can lose to `ld hl,nn / push hl` and `and n`.
- The biggest wins are hardware, not instructions: the Copper, hardware sprites, the DMA for large copies, the
  scroll registers instead of redrawing.
- When you read existing Z80 code and see a plain sequence a Z80N instruction would replace, flag it (file, line, the
  Z80N form, bytes and T-states saved). Do not change working code for it unless asked or it is part of the task.
```
