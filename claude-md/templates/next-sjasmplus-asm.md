<!--
Template: a ZX Spectrum Next project written in assembly with sjasmplus.
Status: UNTESTED starting point. It has not been used on a real project yet: check every command against your
sjasmplus version and your build, and send corrections.
-->

# <Project name>: notes for Claude

## The project
- <One paragraph: what it is, the target (Next core version, 50 or 60 Hz, display mode).>
- Build: `sjasmplus --zxnext --msg=war --lst=<name>.lst --sym=<name>.sym <main>.asm`; the source writes the `.nex`
  with `SAVENEX` directives. <Adjust to your build script.>
- The listing and symbol files are kept beside the `.nex`: room checks and emulator logs read them.
- Run: <CSpect or MAME command, or the ZX-Next-Unite MCP tools>. For MAME, load the `zxnext-mame` skill.
- The memory map lives in `<docs/memory.md>`: which page sits in which MMU slot in each phase, and each page's cap.

## Assembly: Z80N first, memory first, speed always
- Use a Z80N instruction wherever one can replace plain Z80 (load the `z80n-optimize` skill); sjasmplus needs
  `--zxnext` to accept them.
- Memory is the top priority. When a faster form costs bytes, give both forms' bytes and T-states and let me decide.
- Frame budget: the worst line of every <level> at most <N> of <264 at 60 Hz | 311 at 50 Hz>.
- Measure, do not assume: bytes and T-states before and after for each change (the `z80-measure` skill measures
  snippets with z88dk-ticks even in an sjasmplus project).
- Make the common branch fall through (the `z80-code-layout` skill).
- When you read existing code and see a plain sequence a Z80N instruction would replace, flag it; do not change
  working code for it unless asked.

## Room
- After every build, say each page's used and free bytes against its cap and the free bytes below the stack. Read
  them from the listing or symbols; never guess.
- <Use ASSERT directives so a page that overflows its cap fails the build.>

## Helper tools and output
- Every helper tool is committed under `extra/<topic>/` with a short README. Generated output stays out of git.

## Git
- Commit only when I ask; never push without my word.
