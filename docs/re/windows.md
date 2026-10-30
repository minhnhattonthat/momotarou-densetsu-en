# Text windows: width budgets (phase 5 width gate)

Pixel budgets for English text drawn with the VWF (`tools/engine.py` widths: advance = ink + 1, space 4). Measured =
read off a 320x240 shot with `tools/debug/boxmeasure.py` (navy box interior / ink spans); the shot is named. A line
fits when the sum of its advances minus 1 is at most the budget. Never derive a budget from the Japanese length.

| Variant | Where (tables) | Text x | Right edge | Budget | Lines | Status |
|---|---|---|---|---|---|---|
| Dialogue box (field NPC, shop talk, events, battle messages, minigames, ATOK, title prompts) | SHOP, map tables (06*, 07*, 04HEX, 30EV), BM*, FONT_10/11 | 48 | 281 (interior 38..281) | 234 px | 3 per page ({n}; {wait} pages) | measured: talk_134, ev_00..04, battle, title_load (`work/qa/warp/<scene>/scene.png`); JP lines reach 18 glyphs = 234 px |
| Field menu commands (2 x 4 grid) | FONT_7 | 20 (col 1), 88 (col 2) | col 2 start - 6; box interior 18..141 | 62 px col 1, 54 px col 2 | 1 | measured: menu (marker shot `work/qa/warp_marker/menu`) |
| Item / technique list (right box) | FONT_6 / FONT_7 names | 160 | 293 (interior 154..293) | 133 px minus the count column | 1 | partly measured: menu_dougu, menu_jutsu; count column x not read yet |
| Item description box | FONT_6 | 160 | 293 | 133 px | 3 | guess from menu_dougu interior |
| HUD name box (top) | FONT_7 names | - | - | - | 1 | not measured (marker overflows: party names must be short) |
| Status screen labels | FONT_7 | 24 | label column ~100 | ~76 px | 1 | guess from menu_tsuyosa |
| Gold box | {gold} + unit | 217..292 | - | - | 1 | measured interior |

Open (phase 5 width gate not complete): HUD name box, equipment screen (menu_soubi: 154..278 box), shop buy list,
save/load slots (title_load 128..290), card album, minigame score boxes, staff roll, name entry. Measure each with a
stress line in the marker build before translators get those tables.
