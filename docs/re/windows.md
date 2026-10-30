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

Width gate complete (phase 5): every variant above is measured. Phase 7 layout work done (docs/re/engine.md §Layout
patches): HUD labels, money unit, name-entry English page, {num} pitch; staff-roll lines fit 250 px (lint). The
？？？ battle command: its overflow was the marker text; the grid strings (FONT_7:026-034, ？？？ = FONT_10:117 "???")
are short in English and pass the lint, but the English grid is not shot yet (phase 8, battle_lists route). Minigame
result/score screens beyond the message box were not reached (HUDs are graphics); treat any new box found in phase 8
as unmeasured and measure it before fitting.
