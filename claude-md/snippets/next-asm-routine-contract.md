# Snippet: what a new assembly routine must keep

For ZX Spectrum Next projects that mix C (z88dk) and hand-written assembly, with an interrupt handler and banked
pages. Paste the block into your project's `CLAUDE.md` and delete the lines that do not apply. Pairs with the
`zxnext-c-to-asm` skill and the `zxnext-banked-code` skill of the `jclauzel-z88dk-banked-c` plugin.

Where it comes from: one z88dk `+zxn` application's Z80N rewrites of its drawing routines. The IY line is from a
routine that used IY as a spare pair and passed every test on the PC; the project's C-against-asm test now loads IY
with $5C3A before each call and checks it afterwards.

```markdown
## Assembly: what a new routine must keep
- IX and IY come back as they were. IY looks free and is not: the ROM's IM 1 handler reads the system variables
  through it, and it runs whenever the program calls the OS.
- No alternate register set (`exx`, `ex af,af'`) unless our interrupt handler saves it. Ours <does | does not>.
- A page swap goes through `<the project's shared routine>`, called by name, and puts back the page it found, never a
  constant.
- Code that runs under an open Layer 2 write window makes no store to a static, has no self-modifying code and
  never reads the frame buffer: a write there is a pixel.
- Say which Z80N instructions a routine uses in its header comment, so the next reader knows it cannot run on a plain
  Z80.
- A routine with a C twin is held to it by `<the test>`: change both sides and run it.
```
