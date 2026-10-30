# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4 (extract) done 2026-10-30; next is phase 5 (engine spike + marker build).
- **Done (phase 4):** `tools/extract.py` -> `script/` (191 JSON files: 187 unique string tables, SHOP.MMB, 3 code
  overlays, EXE). 23,175 strings, 5,981 unique, ~281k chars. Format and findings in docs/re/text.md §Script.
  `extract.build_table(doc, 'jp')` rebuilds every table byte-identical; `tests/test_extract.py` checks that, overlay
  strings in place, script/ == fresh extraction, no `[XX]`, every 0x10d entry covered, and a run scan of the whole
  disc (PACs, EXE, loose files) finds no text outside script/ (reviewed non-text runs listed in the test).
  Kanji table: all 1,070 used kanji eye-checked against glyphs, ~230 OCR misreads fixed (郎/鬼/都/撃...), values
  unique. New text sources found: HMAP2606.PAC:65 overlay (41 card-game proverbs, pointer list), SMAP16.PAC:36
  (1 shop line, lui/addiu), EXE name-entry labels + kana/alnum grids (grids not extracted: phase 5 name entry).
- **Next (phase 5):** font/VWF decision (12x12 fixed 13 px pitch now; glyph sheets FONT.PAC 2/3), marker build:
  every string -> `[id]` marker via `build_table(doc, 'en')`, insert path = decompress entry, replace, `lzss.compress`,
  `pac.pack` for every `copies` location, `build.build`. Then measure each box variant's width in-game (width gate),
  find PAC load-buffer limits (tables grow), trace how events index strings, decide overlay/EXE strings (in place
  within `max`, or move + repoint `ptrs`) and the name-entry grid (English alphabet). LZSS recompress verified on 60
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
