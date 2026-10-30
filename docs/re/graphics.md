# Graphics text

## Latest coverage (2026-10-31)

The 83-scene tour and 13 late-graphics/fragment sheets have current read-only `ok` verdicts:
`work/qa/phase8_cardsfix/tour_manifest.tsv` and `work/qa/graphics_final/manifest.tsv`; both qa_gate checks pass.
The album has separate green gates: all 297 original/English comparisons pass in
`work/qa/cards_final_pass/assets_manifest.tsv`, and all 99 runtime pages pass in
`work/qa/cards_final_pass/manifest.tsv`. These proofs
supersede older per-row "preview only" notes for the museum, AMAP, Daruma ribbons, roof signs and ending.

- `amap_stage3/5`: island アホ -> Fool; compass -> N, reached through the Map item.
- `congrats`: full Congrats! below the open ball; both 祝 caps -> YAY. The cloth border and top folds survive.
- `museum_sign`: peach exhibit たべるな! -> Don't eat!; the unused vertical texture is translated too.
- `daruma_advanced`: Daruma / Drop! ribbons and cleaned Time; fixed menu possessive spacing.
- Six large battle-status words draw correctly through the engine renderer with forced sprite IDs. Natural
  ailment rendering uses small pictorial icons instead. See [status-qa.md](status-qa.md); no natural caller is claimed.
- BB241 scroll marks were inspected in both boss battles and by an independent translator. No reliable words
  were recoverable; retained as decorative brushwork under D12. The folding screen is a pine painting.

Routes, addresses and unused-art evidence: [graphics-qa.md](graphics-qa.md). RESTAURANT, the bath price board,
restaurant menu and yellow Oni highlight have fresh cold-boot proofs and four independent `ok` verdicts in
`work/qa/boards_final`. KIMONO is unused in the shipped placement/animation/script data. The unreadable board
details are adapted under D13; the readable ADULT/CHILD labels are translated.

## Phase-8 runtime follow-up (2026-10-30)

- Town sweep found additional glyphs omitted by the original plate matching: SMAP03B:3 stone signs (map 5),
  SMAP06/0601:6 FLOWER (maps 9/10), SMAP15/1501:6 round-hut signs (maps 20/21), SMAP16:6 PLAY (map 22),
  SMAP27/28:3 GROCER (maps 34/35). All now have explicit PLATE_KINDS and cold-boot scenes `signs_*`.
  The round-hut :3 small variants are also translated; the larger :6 plates are the ones seen in-game.
- Wood SHOE/WPN/ARM and the thatched-roof INN were seen on map 34. CLOTH, BATH and CARD DOJO were seen on map 22.
  RESTAURANT was later found at map 22 tile 107,13; the earlier camera grid had missed it. KIMONO has no shipped
  placement or caller (graphics-qa.md).
- DMAP03:2's green Oni puzzle is map 403, tile 22,33 (`puzzle_oni`): eight panels. The glyph uses both palette
  ramps 1..4 and 11..15, unlike the adjacent direction panels. Its inset is cleared to the dark stone colour
  before lettering, preserving the border. The other panel is the yellow flip highlight; its geometry now
  matches the base exactly and is verified through the real guard/puzzle sequence.
- END01 repeats one sprite twice to form the Japanese closing idiom. `engine.OVERLAY_PATCH` centers the first
  sprite (entry 1 offset 0x206, signed x -13) and sets the second's width to zero (0x210). The texture is unchanged
  by this placement fix. Fresh-build proof: `work/qa/phase8_latest/end_scan/f000240.png`, a single centered
  "The End". Named cold-boot scene `ending_plate` settles at 35640 frames after event start.
- All 99 album pages were captured by `tools/debug/album.lua`, showing all 297 cards. Read-only visual review
  found leftover JP punctuation/antialiasing and erased character art. `cards.py` now erases common stat-label
  glyphs instead of the entire stat box, preserves coloured art in the name column, erases the full flavour
  lettering including its tinted fringe, and keeps the inner frame. The latest source comparisons all pass;
  all 33 final runtime sheets also pass the independent album gate.
  Kanji drawn into miniature props are retained under D11, while the card labels and explanations are English.
- The four remaining runtime groups listed in this checkpoint are now covered as detailed above.

## Card cleanup and regression evidence

`tools/cards.py` recovers two consensus disc outlines from the 297 originals, fits the appropriate outline to
each card, and clears only its enclosed lettering and halo. A flood started inside a Japanese glyph could
otherwise remain trapped in the glyph's closed pocket; an approximate radius erased the hand-drawn rim.
The shared stat-letter mask comes from card 110, whose illustration does not intersect the labels. This keeps
staff tips, horns and fingers below/beside the Japanese stat lettering. Explicit flavour/name protections retain
original art that touches those columns. The English stat row pitch is 14 pixels to match the game's numbers.

`tools/debug/card_sheets.py` generates all 297 original/English pairs; `tools/debug/album.lua` captures every
runtime album page from a fresh first-page state. Tests preserve known art/frame pixels and check the formerly
missed closed-kana residue and low snow-character bar while keeping the rim. Cards 97/98 retain a slightly
flatter grey patch under their replaced names; independent QA classified this as minor cosmetic retouch with
no lost illustration, missing text or clipping.

## Static sweep (done 2026-10-30)
`python -X utf8 tools/gfxdump.py work/gfx` renders every unique TIM image in every PAC (1,055 unique of 3,406;
duplicates listed in `work/gfx/index.tsv`) to 44 labelled sheets; 4 read-only reviewer agents read all 44 and listed
every tile with Japanese. Result: [gfx_survey.tsv](gfx_survey.tsv) (index = tile in `work/gfx/index.tsv`).
Skipped entries are printed by the tool (all non-image entries whose first word happens to be 0x10/0x12).
Images are drawn as grey index ramps, so faint or small text is under-reported: the sheets 011-021 pass (dungeon/
house maps, battle backgrounds) returned few rows; re-check those scenes on the marker-build tour (phase 5).

## Elements (source = PAC entry, compressed 4bpp/8bpp TIM unless noted)
| Element | Source | Notes |
|---|---|---|
| Title logo 桃太郎伝説 | EVTTIT.PAC:6 (8bpp, VRAM 832,0; drawn stroke by stroke from EVTTIT.PAC:5 in the intro), also MECD.PAC:4 stamp, EVTCARD.PAC:1 | **kept Japanese**: D5 keeps the original logo when no official English logo exists (none does) |
| Title menu はじめて / つづきから | EVTTIT.PAC:9 | **English** (tools/gfx_en.py title_menu), seen in-game |
| Memory-card menu きろく うつす けす やめる / つづき | MECD.PAC:3, MECD.PAC:2 | **English** (mecd_menu, mecd_load), Load menu seen in-game |
| Card-album cover stamp カードアルバム | EVTCARD.PAC:1 right edge + EVTCARD.PAC:2 (red stamp, tilted; 8bpp halves 240 + 80 px, CLUT EVTCARD.PAC:6) | **English** CARD / ALBUM (gfx_en.stamp(): old stamp -> nearest paper, new stamp drawn), seen in-game |
| Status-ailment lettering 病気 混乱 眠り マヒ どく 封印 | FONT.PAC:4 (VRAM 960,0 sprite sheet): one 40x32 sprite per word; sprite records in FONT.PAC:8 at 0x1604.. | **English** Sick / Con-fused / Asleep / Para-lyzed / Poison / Sealed. All six verified in a cold-boot battle through the real renderer with forced sprite IDs; natural ailment UI uses small icons. See status-qa.md. |
| Circled 技 orb (FONT.PAC:4 80,104 32x30; BM091.PAC:24) | | kept as an icon for now (no sprite record found in FONT.PAC:8; context unknown) |
| Status-summary time 日目 | FONT atlas, direct EXE sprite UVs at 0x8003EE80/0x8003EED8 | **English** "Day 1 00:00:14": engine.PATCH reorders the 12 right-to-left slots (day digits after the hours, slot -3 = 6 px gap, slot -2 = one 24 px sprite) and engine.patch_day redraws the 日目 cells (sheet 0 plane 0, 302-303; no English text uses Japanese glyphs) as "Day"; seen in `work/qa/warp_day/status_summary/scene.png` |
| Collectible cards: 297 cards, name + circled initial + flavour text (cards 1-60) or stat labels 体力/攻撃/守備/速さ (61-297) | CR_PG01-99.PAC entries 0/2/4 (8bpp 96x136) | **English** names, initials, HP/Atk/Def/Spd and flavour text; all 99 pages captured. Current independent gates and repair details above. Five cards carry real people's names (pun-contest winners). |
| Shop-sign plates 茶 医 防 足 武 ど つ 旅 銭 宿 湯 ... and 八百屋 | wood row SMAP00.PAC:3 y80 (16 plates 16x16); oval building signs OMAP00.PAC:4 y54 (8 x 32x20: 宿 茶 医 防 足 武 銭 刃) + y86 (八百屋 64 wide, つ, 易); byte-identical copies in ~30 SMAP/OMAP/JMAP/HMAP8600 tilesets (lists in gfx_en.PLATE_KINDS) | **English** (gfx_en.plates(), 3x5 pixel caps: INN TEA DOC ARMOR SHOES ARMS BANK SMITH GROCER SHOP SEER; wood row TEA DOC ARM SHOE WPN ITEM SHOP SEER BANK RENT BATH SHOP FEST BATH JOKE EDGE), ovals seen in-game (map_36, town2). Unsure: つ ど 薪? -> SHOP (shop type unknown); wood row not seen in-game yet |
| Bath-event band ゆ 湯 ゆ 湯 (brush on wood under the FURO pictures) | FURO_0-4.PAC:6 (identical; 8bpp, CLUT :5) | **English** Hot Bath Hot Bath (gfx_en.bath()), seen in ev_furo0/1 |
| Bath curtains 男湯 / 女湯 | HMAP8200.PAC:3 (map 378) | **English** Men / Women (bath_signs, sprite mode with `erase` so the curtain seams stay), seen in-game |
| Bath price board and restaurant menu | HMAP8200.PAC:3; HMAP8500.PAC:0/3 | **English/adapted under D13:** ADULT / CHILD with neutral price marks; MENU with decorative strokes. Original remaining prices/labels/dishes unreadable even under independent zoom review; no invented amounts or dishes. Both seen in cold-boot scenes. Four-opening shapes in :0 are window lattices, not lettering. |
| Celebration banner おめでとう (unrolls in 4 frames) | HMAP26.PAC:3 (maps 306-314) | **English** Congrats! and YAY on both caps; verified through the museum clerk in `congrats` |
| Light 宿 plates on inn roofs | OMAP00.PAC:1 (218,46) + (224,176), copies in ~25 town tilesets | **English** INN (PLATE_KINDS), verified in town scenes including map 34 |
| Banner 天下一だじゃれ大会 | SMAP13.PAC:5 (map 18) | **English** Grand Pun Contest (pun_banner), seen in-game |
| SMAP16 extra plates 衣 着 料亭 カード道場 湯 | SMAP16.PAC:6 | **English** CLOTH / RESTAURANT / CARD DOJO / BATH verified on map 22. KIMONO is translated unused art; no shipped placement or caller. |
| Map island アホ | AMAP.PAC:9-11 (8bpp, x164-184 y63-90) | **English** Fool, verified through the Map item at stages 3 and 5 |
| Map-event compass 北 | AMAP.PAC:2 (19,16)-(30,25), fill 57 outline 63 | **English** N, verified with the island in `amap_stage3/5` |
| Shuten-doji's cave puzzles: quiz panels 東 西 南 北, colour panels 赤 青 黄 白, 鬼 panels, 7 kana floor tiles しゅてんどうじ | DMAP03.PAC:2 (cave_panels), DMAP03.PAC:0 (PLATE_KINDS, 2x pixel font) | **English** East/West/South/North, Red/Blue/Yellow/White, Oni (base and yellow highlight), tiles SH u TE N DO U JI. Hint DMAP03_92:001/002 spells "Sh-u-te-n-do-u-ji". All verified on maps 402/403/405/407. |
| Seal 封 talismans | BM000.PAC:12/16 (4 ofuda frames) | kept: a prop (an ofuda carries its kanji like the 酒 gourd); owner may override (status.md) |
| Minigame words すたーと げーむおーばー そこまで！ げーむくりあー 得点 最高得点 | DARUMA.PAC:10, MOGURA.PAC:10, YUMI1.PAC:9 | **English** (+ 失敗 Miss, 時間 Time), all three seen in-game |
| Daruma-otoshi banner | DARUMA.PAC:6 | **English** Daruma / Drop!, verified on the tall Advanced tower |
| Fuku-warai wallpaper 福笑い (slanted, pink on yellow between peaches) | FUKU.PAC:3 + FUKU.PAC:5 (8bpp, side by side on screen; CLUTs :2/:4) | **English** Fukuwarai (gfx_en.fuku(): both images as one 512 px canvas, words found as pink components touching no peach colour, redrawn at 40 deg), seen in mg_fuku |
| Shrine offering box 賽銭 | HMAP00.PAC:0 (216,23)-(248,30), map 47 | **English** OFFERING (gfx_en.offering(), 3x5 caps on the box dither), seen in in2_47 |
| Ending めでたし | END01.PAC:2 | **English** one centered "The End", verified in `ending_plate`; duplicate placement disabled in the overlay |
| Card-album index page 目次 桃太郎の仲間 村人 仙人 ボス鬼 鬼 現在合計 枚 + kanji numerals | EVTCARD.PAC:5 (4bpp; in-game CLUT is not EVTCARD.PAC:7: index 15 = black, 0 transparent) | **English** (album_index), seen in-game: Contents / Momotaro's Friends / Folk / Hermit / Boss Oni / Oni / Cards. The game cuts each label at the JP glyph length (村人 仙人 32 px), hence Folk/Hermit. Savestates hold the old texture in VRAM: re-warp from cold boot after a rebuild |
| Calligraphy scrolls | BB241.PAC:2 | Inspected in both boss backgrounds by independent translator/playtester; no recoverable words, retained as brush marks under D12 |

Font-drawn UI (menus, battle commands, status labels, 8x8 体力/技/段 etc.) is text, not graphics: see text.md.

## Coverage gate
- The current tour and supplemental manifests are listed above. The album has its own gate and must pass
  independently; old green tour verdicts do not approve a later card redraw.
- Video: none found (no STR files); JING.XA is audio only.
