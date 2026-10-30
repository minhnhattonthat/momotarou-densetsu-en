# English engine (phase 5; `tools/engine.py`, `tools/insert.py`, `tests/test_engine.py`)

## Font and VWF (verified: unicorn tests + marker build in-game, `work/qa/warp_marker/`)
- Glyphs: `fonts/en12.txt` (owner's GaiaMaster 12 px VWF font, MIT) drawn into FONT.PAC entry 3 (sheet 1) plane 1,
  cells 0xA0-0xFE: codes `EN_BASE 0x12A0 + (ord(c) - 0x20)` for ASCII 0x20-0x7E. Those cells were blank and no
  Japanese string uses codes 0x1286-0x13B8. Rows 2-11 of the 12x12 cell, no shadow (the game's text has none).
- draw_string (0x8003E128) drew one 12x12 sprite per glyph and advanced x (gp+0x3E4) by 13. Patch: the sheet 0 and
  sheet 1 glyph paths were identical but for cell base and tpage, so sheet 1 now runs the sheet 0 path (cell =
  code & 0x1FF, tpage 0x1D + (code >> 9 & 1)); the freed sheet 1 block 0x8003E260-0x8003E307 holds the VWF hook
  (advance = width table byte for English codes, 13 for every other glyph) and the 95-byte width table at 0x8003E290.
  Advance = ink width + 1; space 4 px.
- **R3000 load delay** bit here: an `addiu` right after `lhu t0` used the stale t0 (unicorn doesn't model it, the
  first in-game build kept 13 px). `test_no_load_delay_hazard` checks both hooks.

## Digraphs (verified: unicorn draws the same sprites; marker build in-game)
- Every printable ASCII pair is one u16 code `0x8000 | c1 << 7 | c2` (0x9000-0xBF7E), in the control range that
  draw_string skipped as a no-op (jump table only covers 0x8001-0x802E). Control dispatch (0x8003E430) now branches
  to the hook at 0x8003F704, which builds `[glyph c1, glyph c2, 0x8000]` on the stack and
  calls draw_string on it, as the {str} handler does. English costs 1 byte per letter.
- The hook lives in glyph_prim's (0x8003F644) freed sheet 1 block 0x8003F704-0x8003F78F (same merge as above).
  glyph_prim's only caller is a per-glyph effect at 0x80022840: text drawn by it must use single glyph codes
  (`engine.table(pairs=False)`); which strings those are is not traced yet.
- `engine.table()` encodes pairs greedily; a pair never ends in `{` or `[` (it would eat a control token).

## Load buffers and table slots (verified by disassembly of the PAC loader 0x800D6BC4 and the 0x10D handler)
- Map PACs load whole to 0x80110000; compressed entries decompress to a temp at 0x80148000, so a **PAC file must stay
  under 0x38000 bytes (229,376)** or its tail is overwritten while it unpacks. Largest JP PAC 224,136.
- 0x10D text tables are copied to a fixed slot by the entry's param byte (slot table 0x800E330C):

| param | slot | holds | JP max | limit (to the next thing) | marker build (digraphs) |
|---|---|---|---|---|---|
| 1 | 0x80180000 | FONT_7 | 4,084 | 0x4000 (FONT_6) | 5,446 |
| 2 | 0x80184000 | FONT_6 | 28,512 | **0x8000** (FONT_5; base hardcoded in ~300 places) | 38,116 over |
| 3 | 0x8018C000 | FONT_5 | 1,640 | 0x4000 (0x80190000) | 2,150 |
| 4 | 0x8017D600 | FONT_11 | 6,152 | 0x2A00 (FONT_7) | 8,100 |
| 5 | 0x8017C000 | FONT_10 | 5,458 | **0x1600** (FONT_11) | 7,154 over |
| 6 | 0x80160000 | map dialogue | 26,652 | **0x8000** where the map has an overlay at 0x80168000 (SMAP16) | 35,544 over |
| 7 | 0x80190000 | minigame text | 5,778 | not traced | 7,814 |
- SHOP.MMB (560 strings: shop and most interior NPC talk) loads raw to 0x80155000; limit 0xB000 (45,056) to the
  dialogue slot. JP 37,282, marker 49,830 over. Battle tables (BMxxx:1, type 0x116, handler 0x800D787C) not traced.
- FONT_5 / FONT_6 bases are hardcoded (`lui 0x8018`): can't move. FONT_10 / FONT_11 / FONT_7 / map slot are reached
  only through the pointer words at EXE 0xD3AF8-0xD3B24 and 0xEE68C-0xEE6B0 (and 0x800E330C): those can be rebalanced
  (FONT_10 + FONT_11 share 0x4000).
- Remedies for phase 7, in order: a size gate in the build (fail on any slot over its limit); rebalance FONT_10/11;
  dictionary codes 0xC000-0xFFFF = extra strings appended to FONT_5's table (slot has ~13 KB spare and is always
  resident), drawn by the digraph hook calling draw_string on them (~13 more instructions fit in the freed block);
  concise wording only as the last step.
- RAM after the EXE (0x800FF000-0x80110000) is zero in 12 scenes but is BSS (libraries reference 0x801049D8.. and
  0x80101238): not free. `tools/debug/ramfree.py` intersects zero runs over scene states.

## Tools
- `python -X utf8 tools/build.py --marker` -> build/momotarou_marker.bin/.cue: every string `[n.i] filler` at the
  JP line's pixel width (n = doc number in build/markers.tsv, i = string index); overlay strings cut to `max`.
- `tools/debug/warp.py ROM.cue --tag marker SCENE..`, `hits.lua` (exec counts + RAM dump), `regs.lua` (registers at
  an address), `boxmeasure.py` (box interior / ink spans from a shot).
