# Graphics text

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
| Status-ailment lettering 病気 混乱 眠り マヒ 封印 + effect kanji | FONT.PAC:4 (VRAM 960,0 sprite sheet) | battle |
| Status-summary time 日目 | FONT atlas, direct EXE sprite UVs at 0x8003EE80/0x8003EED8 | **Open**: seen in `work/qa/warp_review7_fixed/status_summary/scene.png`; cold-boot scene `status_summary` holds left to expose it. Outside extracted text tables; patch renderer or dedicated atlas cells, not the shared kanji. |
| Collectible cards: 297 cards, name + circled initial + flavour text (cards 1-60) or stat labels 体力/攻撃/守備/速さ (61-297) | CR_PG01-99.PAC entries 0/2/4 (8bpp 96x136) | **English** (tools/cards.py: names, initials, HP/Atk/Def/Spd; flavour text of cards 1-60 from script/cards.tsv), cards 1-3 seen in-game; 5 cards carry real people's names (dajare contest winners) |
| Shop-sign plates 茶 医 防 足 武 ど つ 旅 銭 宿 湯 ... and 八百屋 | wood row SMAP00.PAC:3 y80 (16 plates 16x16); oval building signs OMAP00.PAC:4 y54 (8 x 32x20: 宿 茶 医 防 足 武 銭 刃) + y86 (八百屋 64 wide, つ, 易); byte-identical copies in ~30 SMAP/OMAP/JMAP/HMAP8600 tilesets (lists in gfx_en.PLATE_KINDS) | **English** (gfx_en.plates(), 3x5 pixel caps: INN TEA DOC ARMOR SHOES ARMS BANK SMITH GROCER SHOP SEER; wood row TEA DOC ARM SHOE WPN ITEM SHOP SEER BANK RENT BATH SHOP FEST BATH JOKE EDGE), ovals seen in-game (map_36, town2). Unsure: つ ど 薪? -> SHOP (shop type unknown); wood row not seen in-game yet |
| Bath-event band ゆ 湯 ゆ 湯 (brush on wood under the FURO pictures) | FURO_0-4.PAC:6 (identical; 8bpp, CLUT :5) | **English** Hot Bath Hot Bath (gfx_en.bath()), seen in ev_furo0/1 |
| Bath curtains 男湯 / 女湯 | HMAP8200.PAC:3 (map 378) | **English** Men / Women (bath_signs, sprite mode with `erase` so the curtain seams stay), seen in-game |
| Inn and shop boards, price lists (tiny vertical kanji) | HMAP8200.PAC:0, HMAP8500.PAC:0/3 | open: illegible at 1:1 even in JP |
| Celebration banner おめでとう (unrolls in 4 frames) | HMAP26.PAC:3 (maps 306-314) | **English** Congrats! rotated, clipped per frame (gfx_en.banner()), preview only |
| Light 宿 plates on inn roofs | OMAP00.PAC:1 (218,46) + (224,176), copies in ~25 town tilesets | **English** INN (PLATE_KINDS), preview only |
| Banner 天下一だじゃれ大会 | SMAP13.PAC:5 (map 18) | **English** Grand Pun Contest (pun_banner), seen in-game |
| SMAP16 extra plates 衣 着 料亭 カード道場 湯 | SMAP16.PAC:6 | **English** CLOTH KIMONO RESTAURANT CARD DOJO BATH (PLATE_KINDS), preview only (not found in map 22 warps yet) |
| Map flag (3-4 chars) | AMAP.PAC:9-11 | unread |
| Shuten-doji's cave puzzles: quiz panels 東 西 南 北, colour panels 赤 青 黄 白, 7 kana floor tiles しゅてんどうじ | DMAP03.PAC:2 (cave_panels), DMAP03.PAC:0 (PLATE_KINDS, 2x pixel font) | **English** East/West/South/North, Red/Blue/Yellow/White, tiles SH u TE N DO U JI (small ゅ = small U; hint DMAP03_92:001/002 now spells "Sh-u-te-n-do-u-ji"), all seen in-game (maps 402, 405, 407). 鬼 plate (DMAP03.PAC:2 x192) not yet placed/seen |
| Seal 封 talismans, circled 技 | BM000.PAC:12/16, BM091.PAC:24 | battle effects |
| Minigame words すたーと げーむおーばー そこまで！ げーむくりあー 得点 最高得点 | DARUMA.PAC:10, MOGURA.PAC:10, YUMI1.PAC:9 | **English** (+ 失敗 Miss, 時間 Time), all three seen in-game |
| Daruma-otoshi banner | DARUMA.PAC:6 | |
| Fuku-warai title | FUKU.PAC:3/5 | unsure |
| Ending めでたし | END01.PAC:2 | **English** "The End" (end_plate); not yet seen in-game |
| Card-album index page 目次 桃太郎の仲間 村人 仙人 ボス鬼 鬼 現在合計 枚 + kanji numerals | EVTCARD.PAC:5 (4bpp; in-game CLUT is not EVTCARD.PAC:7: index 15 = black, 0 transparent) | **English** (album_index), seen in-game: Contents / Momotaro's Friends / Folk / Hermit / Boss Oni / Oni / Cards. The game cuts each label at the JP glyph length (村人 仙人 32 px), hence Folk/Hermit. Savestates hold the old texture in VRAM: re-warp from cold boot after a rebuild |
| Calligraphy scrolls | BB241.PAC:2 | decorative, likely leave |

Font-drawn UI (menus, battle commands, status labels, 8x8 体力/技/段 etc.) is text, not graphics: see text.md.

## Not yet covered
- Tour-only check: every element above must be seen in a cold-boot shot of the marker build (phase 5/8) via the
  debug tool (phase 2), including each minigame, the card album, the ending and the bath/inn interiors.
- Video: none found (no STR files); JING.XA is audio only.
