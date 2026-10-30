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
| Collectible cards: 297 cards, name + circled initial + flavour text (cards 1-60) or stat labels 体力/攻撃/守備/速さ (61-297) | CR_PG01-99.PAC entries 0/2/4 (8bpp 96x136) | **English** (tools/cards.py: names, initials, HP/Atk/Def/Spd; flavour text of cards 1-60 from script/cards.tsv), cards 1-3 seen in-game; 5 cards carry real people's names (dajare contest winners) |
| Shop-sign plates 茶 医 防 足 武 ど つ 旅 銭 宿 湯 ... and 八百屋 | SMAPxx.PAC:3/4/6, OMAP00/01 | one shared sign strip per town tileset |
| Bath signs 男湯 / 女湯; inn and shop boards | HMAP8200.PAC:3/0, HMAP8500.PAC:0/3, HMAP8600.PAC:3, HMAP26.PAC:3 | |
| Map flag (3-4 chars) | AMAP.PAC:9-11 | unread |
| Banner 天下一…大会 | SMAP13.PAC:5 | |
| カート… sign, 湯 mark | SMAP16.PAC:6 | |
| Dungeon plates 東 西 南 北 鬼 + colour plates, kana column | DMAP03.PAC:2/0 | |
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
