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
| 7 | 0x80190000 | minigame / event text | 5,778 | 0x8000 (RAM zero up to 0x80198000 in mg_fuku, mg_yumi2, ev_01, ev_furo0) | 7,814 |
- SHOP.MMB (560 strings: shop and most interior NPC talk) loads raw to 0x80155000; limit 0xB000 (45,056) to the
  dialogue slot. JP 37,282, marker 49,830 over. Battle tables (BMxxx:1, type 0x116, handler 0x800D787C) not traced.
- FONT_5 / FONT_6 bases are hardcoded (`lui 0x8018`): can't move. FONT_10 / FONT_11 / FONT_7 / map slot are reached
  only through the pointer words at EXE 0xD3AF8-0xD3B24 and 0xEE68C-0xEE6B0 (and 0x800E330C): those can be rebalanced
  (FONT_10 + FONT_11 share 0x4000).
- **Size gate (phase 7, `insert.py` SLOT_LIMIT etc.)**: a real build fails on any 0x10D table over its slot
  (param & 0xFF), a battle table (0x116) over the largest JP one (20,542; its buffer is not traced), SHOP.MMB over
  0xB000 or a PAC at 0x38000. Marker builds skip it (they overflow by design). The English fits with no rebalance and
  no dictionary codes: FONT_6 29,754 / 32,768, FONT_10 5,384 / 5,632, SMAP16_37 26,610 / 32,768, SHOP.MMB 36,136 /
  45,056, slot 7 5,962 (FUKU) / 32,768, battle 19,956, largest PAC SMAP16 224,388 / 229,376. If it ever overflows:
  rebalance FONT_10/11; dictionary codes 0xC000-0xFFFF appended to FONT_5's table (~13 KB spare, always resident),
  drawn by the digraph hook calling draw_string on them; concise wording last.
- RAM after the EXE (0x800FF000-0x80110000) is zero in 12 scenes but is BSS (libraries reference 0x801049D8.. and
  0x80101238): not free. `tools/debug/ramfree.py` intersects zero runs over scene states.

## Layout patches (phase 7, `engine.PATCH`, `engine.SMALL`, verified in-game on warp shots)
- `{num}` / `{gold}` digits (0x8003E8B8, 8x12 cells at v=228, its only callers are those two handlers) advanced 12 px:
  now 8 ("took 34 damage", not "3 4").
- HUD labels are 8x8 glyphs on an 8 px row pitch (12 px letters clip): the 体 技 段 cells (0x080A/0C/0D, sheet 1
  plane 0, y=240) are redrawn as 3x7 "HP" "SP" "Lv". The field HUD (0x800D87A4) draws 段 at x 0x20 after the level
  number: now Lv at x 8 (the HP/SP column) and the number right-aligned at 0x30 like HP/SP.
- 両 -> "ryo" (FONT_6:556, 12 px font): the six money boxes (number right-aligned to x, label at x) move both 8 px left.
- Name entry 0x800DC3D0: the first page (hiragana grid, EXE 0xD4158) holds A-Z, punctuation, a-z, space, digits
  (`engine.NAME_GRID`, single English codes); hiragana moves to the 英数字 page (0xD43B8); katakana stays. Mode labels
  follow the swap (d44f4 "ABC", d450c "Hiragana"). The cursor starts at column 0 (was 14, あ at top right):
  `0x8003C680(a0 = col, a1 = row)` sets it, called at 0x800DC5FC.
- glyph_prim's caller is the per-glyph effect 0x80022750, called only from overlays: SMAP16:36 (after name entry
  mode 4: the entered name, or the shop line SMAP16_36:46c4 when cancelled) and WMAP08:27 (tongue-twister board,
  kept Japanese). `insert.SINGLE` encodes that shop line without digraphs ("Buy or get out!", 15 glyphs, max 32 bytes).

## Tools
- `python -X utf8 tools/build.py --marker` -> build/momotarou_marker.bin/.cue: every string `[n.i] filler` at the
  JP line's pixel width (n = doc number in build/markers.tsv, i = string index); overlay strings cut to `max`.
- `tools/debug/warp.py ROM.cue --tag marker SCENE..`, `hits.lua` (exec counts + RAM dump), `regs.lua` (registers at
  an address), `boxmeasure.py` (box interior / ink spans from a shot).
# Write provenance (phase 7 review follow-up)

`tools/write_audit.py` records immutable original bytes, intended bytes, owner, and offset for every logical
write. `insert.files()` audits whole rebuilt string tables and graphics entries atomically, individual overlay
strings and repointed pointer words, executable instructions/hooks/name grids, and font-cell rows. Overlapping
producers fail even when they write identical bytes; graphics producers also reject duplicate entry ownership.
Font pixels are assembled in scratch rows before a single audited row write, avoiding ambiguous nibble writes.
Repacked PACs are decompressed again and checked against the records, including detection of unlogged changes.

`build/insert-writes.jsonl` is the durable build log (logical disc path plus optional decompressed entry number).
`build/sfs-writes.jsonl` records each SFS LBA/size update against the original SFS. `build.build()` reads every
replaced file back from the final disc at the new layout's LBA and compares it to the audited file. Thus shifted
compressed bytes do not need a blanket raw-disc permission range. Existing tests still independently validate
allowed changed ranges, PAC metadata, table contents, identity rebuilds, and SFS relocation. The one-command
check runs both the audits and probes proving wrong originals, overlaps, overwrites, and unlogged edits fail.

# Word Maze answer encoding (phase 7 second review)

HMAP2606.PAC:65's 41 answer strings are not ordinary dialogue. The overlay's +0x1400 counts u16 codes up to 18;
+0xC78 distributes one code per NPC clue, and +0x97C compares the player's keyboard answer byte-for-byte. Digraph
compression therefore made the previous translated answers impossible to type as individual letters. The layout
now normalizes these answers to uppercase A-Z without spaces or punctuation, checks 1..18 letters, and insertion
uses the same single-glyph codes as the English keyboard. Four answers were rephrased to fit 18 letters; the rule
explanation tells the player the input format. The full sayings in HMAP2606_66:045-085 remain ordinary prose.

The 928-byte old pool cannot hold single-glyph English. New strings live at overlay +0x3000 (RAM 0x8016B000),
after the original code/data/BSS through +0x2628; the new pool is bounded by +0x4000. Each appended span and each
original pointer word is audited, the original pool remains untouched, and tests reconstruct every expected answer
from individual keyboard glyph codes. No game code or runtime arrays occupy the reserved pool. The total overlay
remains well below its next resident FONT text region at 0x8017C000.

# Word Maze runtime verification

On the fresh review build, a playtester started the game through Big Sis on map 312, received fourteen clue
glyphs for `RAISEDWITHCARE`, opened keyboard mode 6 through its real caller, and entered the answer using the
directional controls. The 28-byte comparison returned zero and displayed the success response; changing the
last letter to S produced the failure response. No RAM pokes forced the selected answer or result. Clue display
was separately tested through the real clue routine with a redirected entry. Evidence and complete routes:
`work/qa/word_maze_probe/report.md`, `ok_key.png`, `ok_key2.png`. Other answers retain static encoding checks.

