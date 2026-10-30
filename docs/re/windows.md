# Text windows: width budgets (phase 5 width gate)

Pixel budgets for English text drawn with the VWF (`tools/engine.py` widths: advance = ink + 1, space 4). Measured =
read off a 320x240 shot with `tools/debug/boxmeasure.py` (navy box interior / ink spans); the shot is named. A line
fits when the sum of its advances minus 1 is at most the budget. Never derive a budget from the Japanese length.

| Variant | Where (tables) | Text x | Right edge | Budget | Lines | Status |
|---|---|---|---|---|---|---|
| Dialogue box (field NPC, shop talk, events, battle messages, minigames, ATOK, title prompts) | SHOP, map tables (06*, 07*, 04HEX, 30EV), BM*, FONT_10/11 | 48 | 281 (interior 38..281) | 234 px | 3 per page ({n}; {wait} pages) | measured: talk_134, ev_00..04, battle, title_load (`work/qa/warp/<scene>/scene.png`); JP lines reach 18 glyphs = 234 px |
| Field menu commands (2 x 4 grid) | FONT_7 | 28 (col 1), 88 (col 2) | col 2 cursor at 80; interior right 141 | 52 px col 1, 54 px col 2 | 1 | measured: menu, menu_soubi (JP はなす 28..64, しらべる 88..137) |
| Side message box (item / technique menus' messages) | FONT_10/11, FONT_6 | 160 | 293 (interior 154..293) | 134 px | 3 | measured: menu_dougu, menu_jutsu (どうぐぶくろを / のぞいたが なにも / はいって...) |
| Item list (field menu どうぐ) | FONT_6 item names (id i = FONT_6:060+i) | 27 | interior 17..140, no count column | 114 px | 1 | measured: menu_items (items 1-24 poked) |
| Item list (battle どうぐ) | same | 32 | interior to ~145 | 114 px | 1 | measured: `work/qa/b_items/final.png` (battle_lists state s005480 + right, circle) |
| Shop buy list | item names + price | 32 | price right-aligned to 180, 7 px per digit (5 digits from 147) | 110 px | 1 | measured: shop_65_buy |
| **Item name (all screens)** | FONT_6 items | - | - | **103 px** (equip slot is the smallest) | 1 | min of equip 103, shop 110, lists 114 |
| Shop choice menu (買う 売る 下取り やめる) | FONT_6 :651-654 | 32 | interior 22..89 | 58 px | 1 | measured: `work/qa/shopbuy/f000220.png` |
| Technique list (field じゅつ and battle じゅつ) | FONT_6 technique names (:000 きんたん ..) | 28 | cost right-aligned to 130 (2 digits from 116) | 85 px | 1 | measured: menu_techs (learned bits poked), `work/qa/b_techs/final.png` |
| Battle command grid (2 x 4: たたかう どうぐ じゅつ まもる かばう つよさ ？？？ にげる) | FONT_7 | 28 (col 1), 88 (col 2) | col 2 cursor at 80; interior right 141 | 52 px col 1, 54 px col 2 | 1 | measured: battle_long marker f005480 (same grid as the field menu). The ？？？ row's marker overflows into col 2: its string is long, check it in phase 7 |
| Battle enemy list (right of the commands) | FONT_7 monster names | 164 | count right-aligned to 294 (2 digits from 282) | 114 px | 1 | measured: battle_long; monster names also go into battle messages via {str} |
| Staff roll | END02_14 | 56 (lines indented with spaces in JP) | glyphs past 256 px from the line start are dropped (a 72-char line lost "nopq") | 250 px (measured fit) | 3 per page | measured: credits_end with `--qa END02_14:051=...` stress lines |
| Minigame message box | FONT_10/11 + 30EV minigame tables | 48 | 281 (semi-transparent fill) | 234 px | 3 | measured: mg_* (same frame as the dialogue box); minigame HUDs (矢数, 時間) are graphics |
| Name entry commands (すすむ もどる いれる けずる おわる) | FONT_5 :094-098 | 16, 76, 136, 196, 256 | 60 px pitch, interior right 313 | 56 px | 1 | measured: `work/qa/name1/f000200.png` (JP; `tools/debug/call.lua` redirect) |
| Name entry mode labels (英数字 left, ひらがな/カタカナ right) | EXE d44f4/d4500/d450c (max 12/12/8 bytes) | 16 / 256 | interior 313 | 100 px left, 57 px right | 1 | measured: same shot; byte max caps them first (5/5/3 codes) |
| Entered name ({str} in OMAP00 fortune teller lines) | player input | 32 | interior 297 | 8 characters (game cap) | 1 | measured: 8 kana fill the field; English grid = the 英数字 page (phase 7) |
| Card album | - | - | - | - | - | no script text: index, cards and labels are graphics (docs/re/graphics.md, CR_PG*) |
| Battle messages | FONT_10/11 + {str} monster/party names (FONT_7) | 48 | 281 | 234 px incl. the longest inserted name | 3 | measured: battle (marker `[4.126] The[0.1] The quick brown fox`, `work/qa/battle_cmd/`) |
| Glyph torture line | SHOP:347 via `--qa` | 48 | - | - | 3 | booted: every printable glyph draws (`@` is a heart in en12.txt), double spaces keep 8 px; `work/qa/torture/f000230.png` |
| HUD name box (top centre) | party names (FONT_6 :536..) | 148 | interior ~192 | 44 px | 1 | measured: menu_soubi (桃太郎 148..186) |
| HUD stat labels (体 技 under the name) | FONT_6 :551, :553 | 146 | number at ~158 | 12 px | 1 | measured: menu_soubi; done in phase 7: 8x8 cells redrawn as HP / SP / Lv (engine.SMALL) |
| Equip slot label (武 防 足) | FONT_6 | 168 | item name at 190 | 20 px | 1 | measured: menu_soubi |
| Equip slot item name | FONT_6 items | 190 | interior ~293 | 103 px | 1 | measured: menu_soubi |
| Status labels (段 体 技 心 次 状態) | FONT_6 | 24 | numbers from ~66 | 40 px | 1 | measured: menu_tsuyosa |
| Status labels (攻撃力 守備力 素早さ) | FONT_6 | 24 | numbers from ~98 | 72 px | 1 | measured: menu_tsuyosa |
| Status name (top) | party name | 72 | - | ~80 px | 1 | measured position, right side free |
| Save slot label (空きファイル) | EXE/title tables | 178 | scroll interior ~290 | ~110 px | 1 | measured: title_load |
| Gold box | {gold} + unit 両 | 217..292 | - | - | 1 | measured interior; unit glyph after the number |

Label coverage (phase 7 review follow-up, done): every authored FONT_5/6/7 label maps to a measured box or to the
explicit unused list below. The Japanese-length fallback is gone: an unmapped label gets box `label` with budget 0,
so any English fails the lint (fail closed). `python -X utf8 tools/debug/label_refs.py --unmeasured` exits 0.

## Window descriptors

Menu windows come from 16-byte descriptors in RAM: u16 width, height in 8 px tiles, then flags, then the draw
callback (find one with `tools/debug/xref.py <callback>`: the descriptor starts 12 bytes before the data word).
Callbacks draw each row with `0x8003D968(index a0, table a1, x a2, y a3)`, x relative to the window. For x = 16 the
text budget is **8 x width - 22 px** (x = 10: 8 x width - 16): checked in-game on six windows (rows marked
measured below). Windows only read from code are marked static; they use the same formula.

| Variant | Strings | Window | Budget | Evidence |
|---|---|---|---|---|
| Item popup Use / Drop | FONT_6:646-647 | 10 tiles, desc 0x800E34F8 | 58 px | measured `work/qa/m8_use/f000040.png` (x207, interior ends 264) |
| Yes / No | FONT_6:649-650 | 10 tiles, desc 0x800E34A0 | 58 px | measured `work/qa/m8_elev3/f000420.png` (x48, ends 105) |
| Play / Info / Exit | FONT_5:058, FONT_6:682, :654 | 10 tiles, desc 0x800E34BC / 0x800E3DFC | 58 px | static |
| Companion Skills / Part | FONT_6:747-748 | 10 tiles, desc 0x8007AC70 | 58 px | measured `work/qa/m8_part/f000100.png` (x195, ends 252) |
| Companion skill list | FONT_6:693-698 | 12 tiles, desc 0x8007AC8C | 74 px | measured `work/qa/m8_skills/f000020.png` (x195, ends 268); all six seen (strlog) |
| Town Warp list | FONT_6:700-707 | 11 tiles, desc 0x8007ACA8 | 66 px | measured `work/qa/warp_m8/town_warp/scene.png` (x48, ends 113) |
| Elevator floors (maps 309-314) | FONT_6:799-803 | was 6 tiles = 26 px: cut "Floor 5" to "Floor" | 34 px | **fixed**: engine.OVERLAY_PATCH widens HMAP26/2606/2607:65 to 7 tiles; measured `work/qa/m8_elev3/f000250.png` (x48, ends 81) |
| Equip: Unequip row | FONT_6:594 | item list | 114 px | measured `work/qa/m8_equip/f000300.png` (x28, ends 141) |
| Equip slot None | FONT_6:593 | equip slot, side box | 103 px | measured (equip slot, above); also drawn in the 134 px side box |
| Equip stat + / = | FONT_6:659-660 | + at x212, base stat right-aligned before the = (3 digits from ~222) | 9 px | measured `work/qa/m8_equip/zoom_stats.png`; code 0x800DA650 |
| {str} slot in dialogue | FONT_6:733-740 (into :730), SHOP:344-346, floors into :805/806 | lint counts {str} as 114 px | 114 px | directions seen: `work/qa/warp_m8/enon_world/scene.png` ("Head West ..."); set by 0x8003B650/0x8003B63C |
| Bank menu | SHOP:259-260, FONT_6:588, :654 | 8 tiles, desc 0x8007A904 | 42 px | static (code 0x800365D0) |
| Bank Deposit / Withdraw | SHOP:261-262 | 11 tiles, desc 0x8007A920 | 66 px | static |
| Bank balance heading | SHOP:263 | 12 tiles, x 10 | 80 px | static (0x800368BC) |
| Clinic menu | SHOP:342-343 (FONT_6:572-573, :654 too) | 9 tiles, desc 0x8007A974 | 50 px | static; SHOP:342 "Cure Poison" (52) -> "Poison" |
| Sound test Exit (debug) | FONT_6:530 | 34 tiles, desc 0x800E3EE8, x 24 | 242 px | static |

## Unused labels

No consumer found: no `addiu/ori rt, rs, index` with the index (or base + offset forms) in the EXE, SHOP.MMB or any
decompressed PAC entry, no u16 data word with it in the EXE, and never fetched by `tools/debug/strlog.lua` in the
screens above. Box `unused` (no width check): FONT_6:579 (ターボ), 595 + 597-605 (debug menu: かり, ATRきりかえ ...
フィールドマップへ), 661-662 (性能値, キャラの力), 681 + 683-686 (bank labels; the bank draws its SHOP copies),
796 (デバッグ); FONT_7:019-023 (はやい/ふつう/おそい, おじいさん/おばあさん); FONT_5:093 (文字を入力してください: the
name-entry screen never fetches it). A computed index can hide from the static scan (the directions are reached
that way), so if one of these ever shows in game, measure its window and move it to a box.

Not covered by this gate: single-line strings of non-FONT tables (FONT_10/11, MECD, card names in HMAP8500_18,
minigame tables ...) still default to the dialogue box (234 px) unless listed above.

Additional measurements from fresh English-build states (2026-10-30 review follow-up):

| Variant | Source | Evidence | Measured budget |
|---|---|---|---|
| Settings heading list | FONT_6:786/789/792 | `work/qa/review7_settings/f000060.png`, text x32, interior ends137 | 106 px |
| Settings choices | FONT_6:787-788/790-791/793-795 | same route, f000060/180/330, text x208, interior ends293 | 86 px |
| Treasure heading | FONT_6:577 | `work/qa/review7_status_pages/final.png`, text x84, interior ends161 | 78 px |
| Time/cards/defeated headings | FONT_6:578/580-581 | `work/qa/review7_status_left/final.png`, x64, first time digit x176 | 111 px (smallest field) |
| Defeated count suffix | FONT_6:582 | same shot, x264, interior ends281 | 18 px |
| Card count suffix | FONT_6:583 | originally x264..281 (18 px); engine shifts count and suffix 16 px left | 34 px after patch |
| Money HUD suffix | FONT_6:556 | `work/qa/warp_review7/menu_settei/scene.png`, unit x276, interior ends292 | 17 px |
| Name mode labels | EXE d44f4/d4500/d450c | original name-entry measurement above; use smaller right-hand field for all three | 57 px |

New repeatable cold-boot scenes: `status_summary`, `status_treasure`, `setting_rumble`, `setting_music`,
`setting_text`. Hold left/right for 650 frames to expose the status panels; 6-frame taps only move them a few pixels.
The summary also exposes hardcoded Japanese `日目` in the time renderer, outside the extracted string tables.
The renderer near 0x8003EE80/0x8003EED8 builds those two sprites directly from FONT atlas UVs (see engine notes).

Other phase 7 layout work (docs/re/engine.md §Layout
patches): HUD labels, money unit, name-entry English page, {num} pitch; staff-roll lines fit 250 px (lint). The
？？？ battle command: its overflow was the marker text; the grid strings (FONT_7:026-034, ？？？ = FONT_10:117 "???")
are short in English and pass the lint, but the English grid is not shot yet (phase 8, battle_lists route). Minigame
result/score screens beyond the message box were not reached (HUDs are graphics); treat any new box found in phase 8
as unmeasured and measure it before fitting.
