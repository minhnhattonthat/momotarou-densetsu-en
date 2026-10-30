# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) **done** 2026-10-30. Next: phase 6 (translate).
- **Next (phase 6):** give translators the per-table pixel budgets from docs/re/windows.md (item names 103 px,
  techniques 85 px, monster names 114 px, commands 52/54 px, dialogue 234 px x 3 lines, side box 134 px, staff roll
  250 px, shop menu 58 px, name-entry commands 56 px); `max` bytes on EXE/overlay strings still cap those first.
  Glossary first (names per D1/D2). Phase 7 carry-overs: slot size gate + dictionary codes (engine.md "Remedies"),
  HUD stat labels (12 px), the ？？？ battle-command string (its marker overflows into col 2), name-entry English
  grid (EXE 0xD4158.., use the 英数字 page), glyph_prim's caller (0x80022840, needs single glyphs).
- **Done (phase 5, width gate, this session):** every box variant measured (windows.md table). Debug tool additions:
  scenes `shop_65_buy` (buy list; timed for marker/English text), `menu_items` (inventory poke), `menu_techs`
  (learned-technique bits), `battle_long` / `battle_lists` (command menu on round 2, god mode), `ev_card_all`,
  `talk_36`; scene fields `hold`, `money`, `god`; `tools/debug/call.lua` reaches name entry (debug.md). Inventory
  0x8009133A, technique bits 0x800FE3A8, name entry 0x800DC3D0 in docs/re/debug.md.
- **Done (phase 5, engine):** VWF + English glyphs + digraph codes (docs/re/engine.md): `tools/engine.py` patches the
  EXE (draw_string advance per glyph; pairs of letters as one u16 code drawn by a recursive hook) and FONT.PAC (95
  ASCII glyphs from `fonts/en12.txt`). `tools/insert.py` builds every table from `en` (else original JP bytes) and
  writes all `copies`; `tools/build.py --marker` -> build/momotarou_marker.cue with `[n.i] filler` in every string
  (n -> build/markers.tsv). Marker build: smoke ok; all 52 warp scenes reach (`warp.py build/momotarou_marker.cue
  --tag marker --all`), ids show in dialogue, menus, HUD, shop. Tests: tests/test_engine.py (unicorn runs of
  draw_string incl. digraphs, freed-block branch check, load-delay check).
  Table limits (docs/re/engine.md table): PAC < 0x38000; FONT_6 slot 32 KB (marker 38 KB), FONT_10 5.6 KB (7.1 KB),
  SMAP16_37 32 KB (35.5 KB), SHOP.MMB 45 KB (49.8 KB) overflow even with digraphs.
- **Done (phase 4):** `tools/extract.py` -> `script/` (191 JSON files: 187 unique string tables, SHOP.MMB, 3 code
  overlays, EXE). 23,175 strings, 5,981 unique, ~281k chars. Format and findings in docs/re/text.md §Script.
  `extract.build_table(doc, 'jp')` rebuilds every table byte-identical; `tests/test_extract.py` checks that, overlay
  strings in place, script/ == fresh extraction, no `[XX]`, every 0x10d entry covered, and a run scan of the whole
  disc (PACs, EXE, loose files) finds no text outside script/ (reviewed non-text runs listed in the test).
  Kanji table: all 1,070 used kanji eye-checked against glyphs, ~230 OCR misreads fixed (郎/鬼/都/撃...), values
  unique. New text sources found: HMAP2606.PAC:65 overlay (41 card-game proverbs, pointer list), SMAP16.PAC:36
  (1 shop line, lui/addiu), EXE name-entry labels + kana/alnum grids (grids not extracted: phase 5 name entry).
- **Older phase 5 notes:** trace how events index strings (not needed so far: tables keep their indices), overlay
  and EXE strings go in place within `max` (insert.py asserts it). LZSS recompress verified on 60
  sampled entries only.
- **Done (phase 3):** `tools/build.py` -> build/momotarou_en.bin/.cue, byte-identical to the dump (sha1 test), ~1 s.
  `build.build({disc path: bytes}, out_bin)` replaces files via `build/layout.xml` sources and regenerates
  MMPS_CD.SFS from mkpsxiso's LBA log (docs/re/archives.md). `pac.unpack`/`pac.pack` repack all 585 PACs
  byte-identical (header has a per-entry u32 param at +12: keep it). Tests in `tests/test_build.py` (identity,
  SFS after a 5000-byte growth, all PACs). In-game: build with GUEST.PAC +2048 bytes warps to the village fine.
  Smoke on build/momotarou_en.cue: ok (title).
- **Done (phase 2):** `tools/debug/warp.py` + `warp.lua` + `scenes.lua`: cold boot -> any scene, proof shot
  `work/qa/warp/<scene>/scene.png`, state `work/states/<scene>.sstate`; `--all` regenerates every state, `map:<id>:x:y`
  reaches any of the 560 maps. Scenes: title + load screen, village/house/2nd town/overworld/dungeon, field menu and
  all 7 submenus, 3 shops (buy lists), NPC talk, random battle, events 0-4/7-17 (intro-free: baths, ATOK, AMAP,
  card album, END00, staff roll start + last page, END01 epilogue, PT00), minigames 0/2-6. RAM map, main-loop states,
  file loader and map tables in `docs/re/debug.md`. `tools/debug/fileload.lua` logs every disc file load (--debugger).
  Confirmed: the game loads files through MMPS_CD.SFS (build.py rewrites it).
- **Later notes:** rare kanji (staff-roll names) may still be misread: fix in tbl/jp.tbl, then
  `extract.py --force` (refuses once `en` exists: then patch jp by hand). `check.py` takes ~70 s (disc scans). PCSX-Redux nightly
  `GPU.getVRAM()` returns 2 MB (1024 rows): read the first 512 rows.
  Debug-tool gaps (add when a phase needs them): event 5 (EVT069) and minigame 1 (YUMI1 other entry) stay black
  from a plain warp (need their calling script's context); no fixed-enemy-group battle yet (exec hook on
  0x8004540C a0 with --debugger); no story-flag array yet (events/NPCs that depend on progress); party is the
  New Game party (1 member, no items: `MONEY=` var exists, inventory RAM unknown); shops/NPCs found only for town 2.
  GOD uses the GameShark HP addresses (not checked per member). CR_PG01-99 not loaded by the ending (card pages?).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) PCSX-Redux GUI keyboard input not checked by hand (no interactive session
  in one-shot runs); scripted input verified.
