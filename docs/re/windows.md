# Text windows: width budgets (phase 5 width gate)

Pixel budgets for English text drawn with the VWF (`tools/engine.py` widths: advance = ink + 1, space 4). Measured =
read off a 320x240 shot with `tools/debug/boxmeasure.py` (navy box interior / ink spans); the shot is named. A line
fits when the sum of its advances minus 1 is at most the budget. Never derive a budget from the Japanese length.

| Variant | Where (tables) | Text x | Right edge | Budget | Lines | Status |
|---|---|---|---|---|---|---|
| Dialogue box (field NPC, shop talk, events, battle messages, minigames, ATOK, title prompts) | SHOP, map tables (06*, 07*, 04HEX, 30EV), BM*, FONT_10/11 | 48 | 281 (interior 38..281) | 234 px | 3 per page ({n}; {wait} pages) | measured: talk_134, ev_00..04, battle, title_load (`work/qa/warp/<scene>/scene.png`); JP lines reach 18 glyphs = 234 px |
| Field menu commands (2 x 4 grid) | FONT_7 | 28 (col 1), 88 (col 2) | col 2 cursor at 80; interior right 141 | 52 px col 1, 54 px col 2 | 1 | measured: menu, menu_soubi (JP はなす 28..64, しらべる 88..137) |
| Side message box (item / technique menus' messages) | FONT_10/11, FONT_6 | 160 | 293 (interior 154..293) | 134 px | 3 | measured: menu_dougu, menu_jutsu (どうぐぶくろを / のぞいたが なにも / はいって...) |
| Item / technique list | FONT_6 / FONT_7 names | 160? | count column? | - | 1 | not reachable yet: the New Game party has no items or techniques (inventory RAM unknown) |
| Battle messages | FONT_10/11 + {str} monster/party names (FONT_7) | 48 | 281 | 234 px incl. the longest inserted name | 3 | measured: battle (marker `[4.126] The[0.1] The quick brown fox`, `work/qa/battle_cmd/`) |
| Glyph torture line | SHOP:347 via `--qa` | 48 | - | - | 3 | booted: every printable glyph draws (`@` is a heart in en12.txt), double spaces keep 8 px; `work/qa/torture/f000230.png` |
| HUD name box (top centre) | party names (FONT_6 :536..) | 148 | interior ~192 | 44 px | 1 | measured: menu_soubi (桃太郎 148..186) |
| HUD stat labels (体 技 under the name) | FONT_6 :551, :553 | 146 | number at ~158 | 12 px | 1 | measured: menu_soubi; the marker overlaps the numbers. Needs a 1-glyph label or a layout change |
| Equip slot label (武 防 足) | FONT_6 | 168 | item name at 190 | 20 px | 1 | measured: menu_soubi |
| Equip slot item name | FONT_6 items | 190 | interior ~293 | 103 px | 1 | measured: menu_soubi |
| Status labels (段 体 技 心 次 状態) | FONT_6 | 24 | numbers from ~66 | 40 px | 1 | measured: menu_tsuyosa |
| Status labels (攻撃力 守備力 素早さ) | FONT_6 | 24 | numbers from ~98 | 72 px | 1 | measured: menu_tsuyosa |
| Status name (top) | party name | 72 | - | ~80 px | 1 | measured position, right side free |
| Save slot label (空きファイル) | EXE/title tables | 178 | scroll interior ~290 | ~110 px | 1 | measured: title_load |
| Gold box | {gold} + unit 両 | 217..292 | - | - | 1 | measured interior; unit glyph after the number |

Open (phase 5 width gate not complete): item/technique list (debug tool needs an inventory cheat), shop buy list
(a warp that opens the buy menu), battle command and target menus (warp to the command phase), card album,
minigame score boxes, staff roll, name entry grid. Measure each in the marker build before translators get those
tables. Dialogue tables (SHOP, map tables, events, BM*) can go to translators now: their box is measured.
