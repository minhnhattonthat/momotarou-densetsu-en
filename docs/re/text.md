# Text engine

## Encoding (verified)
- Strings are **u16 little-endian codes**, terminated by `0x8000`. No Shift-JIS anywhere (EXE scan finds no text).
- **Glyph code** (`w & 0x8000 == 0`): `plane << 12 | sheet << 9 | cell`, cell 0-440 row-major in a 21x21 grid of
  12x12 cells. Sheet 0/1 = FONT.PAC entries 2/3 (4bpp TIMs at VRAM 832,256 / 896,256); plane = bit plane of the
  4bpp pixel, picked by CLUT (renderer adds 0x1F0 or 0x1F1 to the CLUT row for plane 0/1).
  Verified: in-game "昔々 / あるところに…" = `02AE 1078 8001 002B 0074 0051 003C 0076 0054 00DD` (RAM 0x80190020,
  scene after New Game), plus battle strings 回復 (`101E 101F`), 攻撃 (`1025 1026`); kana order read off the sheet
  and confirmed on おじいさんと おばあさんが. `tools/font.py` renders cells by code.
- `07xx` = 8x12 glyphs (10 px pitch): `0700-0709` big digits 0-9 (sheet 1 bottom, v=228).
  `08xx` = 8x8 glyphs (8 px pitch): `0800-0809` small digits, `080A-0812` 体 力 技 段 西 両 心 / 次 (v=240).
- Pitch: 13 px per 12x12 glyph (fixed), `8002` = 8 px space, `8003` = 13 px space, `0023` = full-width space glyph.
- Table: `tbl/jp.tbl`, keys are the little-endian bytes (`2B00=あ`). 0000-00E6 read by eye and checked on in-game
  text; kanji (00E7-01B8, 0200-03B8, 1000-11B8, 1200-12xx) are **OCR guesses** (`tools/font_ocr.py`, MS Gothic /
  Yu Gothic template match): ~92 duplicate values, known misses 郎→卯, 鬼→羌, 持→恃, 前→煎, 使→悚, 武器→試盟,
  防具→防異, 撃→掣. Review pass needed before the jp text is final (phase 4).

## Renderer (verified by watch.lua read breakpoints + disassembly)
- `0x8003E128 draw_string(win a0, ctx a1, str a2)`: loops until `0x8000`; glyph path computes u,v from code;
  control path `0x8001..0x802E` through the jump table at `0x80016C20` (EXE file offset 0x7420).
- **No control code takes an inline argument** (every handler advances 2 bytes). Arguments come from per-window
  arrays filled by the caller:

| code | tbl | effect |
|---|---|---|
| 8000 | {end} | end of string |
| 8001 | {n} | newline: y += 16, x = left margin |
| 8002 | {sp8} | x += 8 unless flag 0xCC set |
| 8003 | {sp13} | x += 13 |
| 8004 | {wait} | window op 4 (wait for button / next page) |
| 8005 | {num} | print next number arg (win+0x54C[i], digits win+0x56C[i]) via 0x8003E8B8 |
| 8007 | {str} | draw next string arg (win+0x528[i]) recursively (names, items) |
| 8008 | {c08} | set flag 0xCC (suppresses 8002 spacing) |
| 800B-8010 | {col0}..{col10} | colour = CLUT offset 0/2/4/6/8/10 (col4 = highlighted item names) |
| 8018 | {gold} | print number from gp+0x3D8 (money) |
| 8019 / 801A / 8028 / 802C | {c19} {c1a} {c28} {c2c} | window ops 8 / 10 / 11 / 9 (0x8003F2AC) |
| 8027 | {name} | draw string at gp+0x3E0 |
| others 8006-802E | {cNN} | no-op here (may be read by the event layer) |

## Containers (verified by decoding)
- **String table** (PAC entry type `0x10d`, `0x1010d` compressed, and some `0x10116` entries — 0x116 is a generic
  type that also holds code overlays and TIMs, so detect text by content): u32 offsets from the block start, table
  ends at the lowest offset; strings follow. Volume: 329 unique tables (many byte-identical copies), ~5,900 unique
  strings, ~315k characters including control tokens. SMAP16.PAC entry 37 (first offset 0x44A, not a multiple of 4)
  does not decode with this rule: check in phase 4. Offsets are self-relative, so a table can be
  rebuilt with any lengths (the PAC entry then changes size). `tools/text.py table FILE ENTRY` prints one.
  - FONT.PAC 5/6/7/10/11: names, techniques, menus, battle messages (system text).
  - each map PAC (SMAP/NMAP/OMAP/DMAP/HMAP/WMAP/AMAP/PT/Z/EVT/END...): its dialogue (0x10d, last entries).
  - BM000-BM124.PAC entry 1 (0x10116): battle message table, many byte-identical copies; MECD.PAC 1: training menu.
  - 15 entries are a lone `8001 8000` (4 bytes, no table): empty placeholders.
- **SHOP.MMB** (03FONT): raw file, same table format, 560 strings (shops, inns).
- How events pick a string (index into the scene's table) is not traced yet: phase 4/5.

## Open
- Load buffers: PAC files are read whole into RAM; maximum sizes per file class not measured yet (phase 5).
- Window widths per box variant: phase 5 width gate (not measured; dialogue strings use 2-3 `{n}` lines per page).
