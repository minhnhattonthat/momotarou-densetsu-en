# Disc, archives, compression

## Disc (verified: dumpsxiso 2.30 extracts it; tools/mkpsxiso/)
- One MODE2 data track, ISO9660, volume SLPS_01785 (Hudson, 1998-11-18). Boot `SLPS_017.85` (PS-X EXE, load
  0x80010000, entry 0x8004F8F4, 980,992 bytes).
- `0/<dir>/*.PAC` hold everything (fonts, maps, battles, events, sound); `0/97XA/JING.XA` audio; `GAISYU.DAT` is
  36,864,000 zero bytes (outer-ring filler); `MMPS_CD.SFS` (6,400 bytes) = 800 x {u32 LBA, u32 size} file table
  (entry 0 = itself at LBA 0x17, entry 1 = FONT.PAC, 0x1F66F bytes) — **the game reads files by this table,
  not ISO9660** (verified: `cd_load` 0x8001AC54 indexes it in RAM at 0x8008F710, docs/re/debug.md): a rebuild
  that moves or resizes a file must rewrite it.
- Unpack: `tools/mkpsxiso/dumpsxiso.exe -x work/disc/tree -s work/disc/layout.xml rom/<cue>`.

## Free space (candidates only, none trap-tested)
- Disc: files are rebuilt by mkpsxiso, so text can grow; GAISYU.DAT's 36 MB of zeros can be shrunk if the disc
  size ever matters. Limits are RAM load buffers per file class (not measured; phase 5).
- EXE zero runs (file loads 0x80010000-0x800FF000): 0x8008466F-0x800D6AE0 (337 KB, almost certainly a runtime
  buffer: overlays/PAC data, NOT free), 0x8007D51D (4.2 KB), 0x800FE2DC (3.3 KB), 0x8007CB38 (1 KB),
  0x800E5EEC (1 KB). Trap-fill and tour before using any (pipeline.md §Recon 2).

## PAC (verified on every PAC: `tools/pac.py`)
- Header: N x 24 bytes `{u32 offset, u32 size, u32 type, 12 zero bytes}`, N = first offset / 24; entries packed
  back to back, byte-aligned (no padding). Some PACs end with an all-zero entry.
- Type low 16 bits = content, bit 16 (0x10000) = LZSS-compressed. Seen: 0x11 CLUT TIM, 0x12 image TIM,
  0x10d / 0x116 string tables (docs/re/text.md), 0x102 MIPS code overlay, 0x22/0x23 map data, 0x106/0x10e/0x114/
  0x118-0x11a data (not identified), 0x110 extra image pages (4bpp, 256x96).

## LZSS (verified: `tools/lzss.py`; every compressed entry on the disc decodes to exactly its stored size, and the
encoder reproduces 60/60 sampled entries byte-for-byte)
- u32 decompressed size, then Okumura LZSS: 4096-byte ring zero-filled, write position 0xFEE, flag byte LSB-first,
  1 = literal, 0 = 2-byte reference `off = b0 | (b1 & 0xF0) << 4`, `len = (b1 & 0x0F) + 3`.
- `lzss.compress` is a port of Okumura's LZSS.C encoder (binary-tree match finder).

## TIM variant (verified: `tools/tim.py`)
- Standard TIM layout but magic 0x11 = CLUT-only file, 0x12 = image-only file (no CLUT block). FONT.PAC: entries 0-1
  CLUTs (16x16 at 272,496 / 288,496), 2-3 font sheets, 4 = UI/effect sprite sheet (960,0).
