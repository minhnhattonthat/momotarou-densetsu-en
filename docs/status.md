# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8 (QA in the emulator) in progress, 2026-10-30.
- **Phase 7 review follow-up:** whole-script lint now validates every authored non-data entry, including ASCII
  and control-only sources; unauthored ASCII/control-only entries explicitly retain original bytes. The exact
  FONT_6:556 `{sm_ryo}` -> `ryo` substitution is documented in lint. This exposed YUMI2_10:009's untranslated
  comma, now fixed. Control-only/ASCII regression probes pass; `check.py`: 38 passed, lint 0 errors over 6018
  text/box checks. Write provenance audit now records original/new bytes and owner for table/graphics entries,
  overlay strings and pointers, EXE patches, font rows and SFS updates; verifies final decompressed entries and
  final-disc file payloads. Regression probes reject bad originals, overlaps, overwrites and unlogged changes.
  `check.py`: 42 passed, lint 0 errors; fresh build + `work/qa/review7_smoke` smoke passed.
  Remaining Important finding: replace guessed label widths with measurements. Phase 7 completion is reopened
  pending that work; a green legacy width lint is not proof of measured coverage.
- **Phase 8 progress:** phase 6 review fixes done (d047a7c: glossary names + character honorifics are lint/batch
  ERRORS now, reviewed exceptions in script/glossary_ok.txt; Enma-sama; art-use spacing). Graphics lettering
  pipeline: `tools/gfx.py` (TIM decode/repack, `show`/`dump`/`words` CLI to find text rects), `tools/gfx_en.py`
  (IMAGES table: rect, English, palette-index ramp, font size; asserts no pixel changes outside rects; preview to
  work/gfx_en/; insert.files() writes it into the build). Font fonts/mplus (Rounded M+ ExtraBold, OFL, ASCII
  subset). Done and seen in-game: title menu New Game / Continue (EVTTIT.PAC:9), memory-card menus
  Save/Copy/Erase/Quit + Load (MECD.PAC:2/3; `title_load`), DARUMA.PAC:10 words Start!/Game Over/Time's Up!/Game
  Clear!/Score/Best/Time ('sprite' mode: outline from JP glyph edges, per-row fill; seen via route from
  work/states/en_mg_daruma.sstate: `30 -;6 up;20 -;6 circle;...` answers Yes), MOGURA.PAC:10 + YUMI1.PAC:9
  (Miss/Time/Best/Score, Start!/Game Over/Time's Up!; seen in mg_mogura / mg_yumi1b routes; YUMI "Score" rect
  widened past the JP glyphs and still drawn whole, so sprite rects are not clipped to the JP width). Find text
  rects: `tools/gfx.py words|dump`, or a gridded zoom render. END01.PAC:2 めでたし plate -> "The End" (preview
  only: not seen in-game yet; from work/states/en_epilogue.sstate + mash circle the ending runs to a teaser
  ~f15000 and then the post-game house ~f15600 without showing the plate in 60-frame shots; find when it is
  drawn). FONT.PAC:4 status-ailment kanji (病気 混乱 眠 マヒ どく 封印, vertical 16x20 cells, battle sprites):
  needs a battle with a status to see how they are placed before redrawing.
- **Card album done (seen in-game, cold boot):** 297 cards (tools/cards.py: names, initials, HP/Atk/Def/Spd (D9),
  flavour text of cards 1-60 from script/cards.tsv, translated by a translator agent; `cards.py check` = fit),
  index page (album_index: Contents/Momotaro's Friends/Folk/Hermit/Boss Oni/Oni/Cards; labels are cut at the JP
  length), cover stamp CARD / ALBUM (gfx_en.stamp()). 77 REVIEW cards (name lettered over art) still want an eye
  check. Savestates keep old textures in VRAM: after a rebuild re-warp (cold boot) before judging graphics.
- **Graphics done since (all seen in-game unless noted; per-row detail in docs/re/graphics.md):** town sign plates
  (gfx_en.PLATE_KINDS: byte-identical plate blocks replaced in every tileset copy, 3x5 pixel caps), bath band Hot /
  Bath (FURO_n), bath curtains Men / Women (map 378), Grand Pun Contest banner (map 18), Shuten-doji cave puzzles
  (DMAP03: direction/colour panels, kana floor tiles SH u TE N DO U JI + hint line). Still Japanese: status
  ailments FONT.PAC:4 (battle), seal talismans BM000/BM091, AMAP flag, DARUMA.PAC:6 banner, FUKU title, HMAP26
  おめでとう banners, 宿 roof boards in OMAP00.PAC:1, DMAP03 鬼 plate; END01 "The End" not seen in-game. Find maps
  with tools/debug/maps.txt (line = map id, PAC, room) + `warp.py map:<id>:<x>:<y>`.
- **Card notes:** (CR_PGnn.PAC entries 0/2/4 = 3 cards per PAC, CLUT = next entry; 96x136 8bpp):** circled initial
  top-right (~x62-88 y4-30) -> Latin initial in the circle; vertical name in the right column (~x66-86 y32-128) ->
  English name rotated 90 deg clockwise in that column; top-left box (~x4-56 y4-60) holds either flavour text in
  vertical columns (cards 1-60: needs OCR + translation, ~45 chars of en12-size text fit) or the stat labels as 4
  rows 体力/攻撃/守備/速さ (cards 61-297) -> HP / Attack / Defense / Speed (same pixels on every monster card:
  draw once, paste). Names: match each card to its HMAP8500_18 "<name>カード" entry (English there minus " Card").
  Logo kept Japanese (D5). Skipped so far: DARUMA.PAC:6 banner and FUKU.PAC:3/5 not seen in mg_daruma/mg_fuku.
  Card n (1-based, = (PAC-1)*3 + entry/2 + 1) = the n-th "<name>カード" string in HMAP8500_18 (297, from :085;
  card 1 Momotaro). Album: ev_card_all + route `30 -;6 circle;90 -;6 circle;90 -;6 right;...` shows 3 cards 1:1
  with "No.001" under them, and an index page (EVTCARD.PAC:5: 目次, 桃太郎の仲間, 村人, 仙人, ボス鬼, 鬼, ...) to
  translate. Method for clean backgrounds: cards share a few background templates (pink swirl for monsters,
  green/orange for characters); the per-pixel mode over all cards of one template (same CLUT colours) is the clean
  background; JP name glyphs = "differs from template" components lying wholly inside the name column (art
  components reach outside it and are kept). Built: `tools/cards.py templates` (families keyed by the bottom
  border colour: cream 38 cards, cyan 25, pink 177; greys outvoted -> clean backgrounds, few specks; ~57 cards with
  their own art get no template -> use plates).
- **Next (phase 8):** graphics text (D5: translate all; seen Japanese in the tour: ev_amap title-menu banner
  はじめて/つづきから, card-album title 桃太郎伝説 カード, bath signs ゆ/湯, town shop signs 防/足/宿/つ; survey in
  docs/re/graphics.md), then `qa_gate.py` tour sheets + visual-qa verdicts over `work/qa/warp_en/` (all 61 scenes
  reach on the English build). Not seen in-game yet: proverb card game (HMAP2606:65), SMAP16 name-entry shop
  ("Buy or get out!" effect line), name-entry English page with a real caller (seen via call.lua only), English
  battle command grid (battle_long/battle_lists shots land on a message; time the route to the round-2 menu). `{num}` digits
  are the game's bold 8x12 cells (taller than the 12 px letters): fine at 8 px pitch, redraw only if QA objects.
  `jp_left.py` not run yet (phase 9 gate; needs a slot list for this u16 table format).
- **Done (phase 7):** size gate in `insert.py` (slot limits per table param, battle, SHOP.MMB, PAC size; skipped for
  marker builds): everything fits with no rebalance/dictionary (numbers in docs/re/engine.md). `tools/lint.py`
  (whole-script: codes, pages, widths/lines per box, ASCII, glossary avoids, same-JP-same-EN, no JP in en, no missing
  en unless in script/keep_jp.txt; 0 errors, 64 glossary warnings) wired into check.py. `tests/test_insert.py`: the
  English build changes only table entries, overlay string spans + their pointer words, `engine.PATCH` sites, the
  hook blocks, name grids and the redrawn font cells (romdiff equivalent), and every table copy holds every string.
  Layout patches (engine.md §Layout patches): HUD Lv/HP/SP 8x8 cells + Lv moved before the number, money unit "ryo"
  (6 boxes shifted 8 px), `{num}` pitch 12 -> 8, name entry English first page + cursor at A, SMAP16 effect line in
  single glyphs. New scene `map_36` (base state for name entry via call.lua). warp.py `--all` no longer picks up the
  `hold =` continuation line as a scene.
- **Done (phase 6):** every string has `en` (wave 0 names b001-b005, b006-b070 by translator agents, 13 reviewer
  passes, Important fixes applied; deferred minors in docs/review-minors.md). Tools: `tools/layout.py` (wrap/page
  authored English to the JP page shape and box width; 0 problems over the script), `tools/batches.py`
  (split/check/merge, work/tl/), `tools/pairs.py` (reviewer pairs files). Docs: glossary.md, docs/style-reference.md,
  docs/synopsis.md, docs/translator-brief.md, docs/reviewer-brief.md. 22 more OCR kanji fixed in tbl. `insert.py`
  repacks overlay strings reached only by pointer words into one pool (HMAP2606 proverbs, EXE name-entry labels);
  proverbs shortened to fit (928-byte pool). English build boots (smoke ok); talk_36, shop_65_buy, menu_items,
  battle_long show English. `tests/test_engine.py::test_glyph_path` crashed once in unicorn (Windows access
  violation), passed on rerun: flaky.
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
