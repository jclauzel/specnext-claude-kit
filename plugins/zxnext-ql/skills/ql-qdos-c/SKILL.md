---
name: ql-qdos-c
description: Call QDOS and SMSQ/E from C with the C68 library - channels and their return conventions, file names and the 36-character limit, directories that are only name prefixes, 64-byte entries, headers, rename and delete, console windows and modes 4 and 8, key codes, the Pointer Environment and 24-bit colour on SMSQ/E. Use this skill whenever C code for a Sinclair QL, QPC2, SMSQ/E, sQLux or the ZX Spectrum Next's QL core opens, lists, copies, renames or deletes files, reads keys, draws in a window or handles a mouse, or when a QDOS error code (-1, -7, -8, -9, -15, -19, -20) needs explaining, even if only "the listing is wrong" or "the key does nothing" is said. Not for NextZXOS, esxDOS or z88dk.
---

# QDOS and SMSQ/E from C

Facts from the C68 library's own code, from QDOS sources (Minerva, SMSQ/E) and from a released program that runs on
sQLux, QPC2 and a Next's QL core. What differs between them is said. Read `references/console.md` for windows, keys,
mouse and colour.

## Error codes
0 fine, -1 not complete (timeout), -3 out of memory, -4 out of range, -5 buffer full, -6 channel not open, -7 not found,
-8 already exists, -9 in use, -10 end of file, -11 drive full, -12 bad name, -15 bad parameter, -19 not implemented,
-20 read only.

## Reading and writing
- `io_fstrg`, `io_sstrg` and `io_fline` return **the count**, and also a **partial count** when they time out or meet
  the end of the file with at least one byte moved. A negative result means nothing moved. Compare with the length you
  asked for.
- A length is a `short`: 32 767 bytes at most a call. 4 096 is a good slice. Loop on a short `io_sstrg`.
- `io_fbyte` writes its byte whatever happens: use it only when the call returned 0.
- Timeouts are 1/50 s frames, -1 for ever, 0 at once. There is no finer clock.
- `fs_pos(ch, off, mode)`: 0 absolute, 1 relative, 2 from the end; it returns the position, and for modes 0 and 1 you
  never see the error. `fs_pos(ch, 0, 2)` is the portable way to get a file's length: the length in an open channel's
  header is the raw size on sQLux and 64 more on QDOS.
- Name buffers in the library: `io_open` 62 characters, `io_delete` 126, a rename's new name 94. Nothing checks them.

## Opening
| Key | Means |
|---|---|
| 0 | existing file, exclusive (a second open gets -9) |
| 1 | existing file, shared, for reading |
| 2 | new file (-8 if it exists) |
| 3 | new or overwrite (not on every driver) |
| 4 | a directory, to read its entries |

- **Deleting first and creating with key 2 is safer than key 3.** On sQLux, key 3 over a file that carries a QDOS-header
  prefix leaves 30 NUL bytes in front of the new data.
- A probe for "does this device exist" uses key 0: key 2 may create a file of that name in the default directory.
- Use full names (`win1_...`). The C library's `fopen` and `stat` put the default directory in front of others.
- Never call `io_format`.

## Names
- **36 characters after the device**, folders included. Check before you create: some drivers cut instead of refusing,
  and two long names that start alike become one file. On sQLux a name of exactly 36 does not open at all.
- Case does not matter. The folder separator is `_`, so `win1_a_b` may be the file `a_b` or the file `b` in folder `a`.
  Never invent folders from the `_` in a name.
- `.` and `_` can be the same character on an emulator's PC folder: `k.tap` and `k_tap` are one file there. A pull of
  both overwrites the first; compare names with `.` read as `_` and case folded.
- At most 18 folders deep (36 characters, `a_b_...`): that bounds every recursive walk.

## Directories
- Open with key 4 (`win1_` is the root) and read 64-byte entries with `io_fstrg` until it returns less than 64.
- Entry: length (4 bytes, **64 more than the data**), access, type, dataspace (4), extra (4), name length (2), name
  (36), dates. Types: 0 data, 1 executable, 2 relocatable, 255 directory.
- The name is the path from the device's root: take the folder's own prefix off.
- Skip a name length of 0 (a deleted entry) and any name that is not printable ASCII: a real disc had a damaged slot
  that listed as `??`.
- **Opening with key 4 is not a test for a directory**: a directory is a name prefix, and on sQLux the open succeeds for
  any name. A path is a file if it opens as a file (key 1) and its header does not say 255; otherwise ask the parent
  folder's listing.
- An open that answers -9 means a file that is open elsewhere, not a directory (SMSQ/E locks a file open for writing).
- Some drivers show a directory's name with a trailing `_`, some without: accept both.
- Listing order is the disk's. Sort it yourself; 500 entries are 32 KB, so keep short records.

## Make, rename, delete
- Make a directory: `io_open(name, 2)`, `fs_mkdir(ch)`, `io_close(ch)`. Files already called `name_...` move into it.
  If it fails, delete the empty file you made.
- Rename: an exclusive (key 0) channel; a shared one is refused with -20. Have a copy-and-delete fallback, and make the
  copy keep the header's type and dataspace.
- Write to a temporary name and rename at the end: a job that is removed, or a full drive, leaves a short file.
- A running job's own file can be renamed aside and replaced (seen on QPC2, a `win1_` drive).
- Setting a header (`fs_heads`): give it a **64-byte** buffer, since sQLux reads 64 whatever length you pass. Do it on
  the fresh channel before the data.
- Free space: `fs_xinf`, then `fs_mdinf`. sQLux's numbers are fixed, not real.
- Never delete a pulled or copied file because its check failed before you know that two names did not map to one file.

## Long operations
- Poll the keyboard (ESC) and anything else that waits inside every copy, walk and transfer loop.
- An emulator copies hundreds of times faster than the machine: run sQLux at `SPEED = 1` to test progress and cancel.
- Keep a log file with a size cap and flush it: on real hardware it is all you will get back.
