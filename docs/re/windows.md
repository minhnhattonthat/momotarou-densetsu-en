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

Label coverage now includes every authored non-data table and overlay. A single-line string without a mapped
consumer gets box `label` with budget 0 and fails lint. `label_refs.py --unmeasured` checks that classification
directly (its previous `is None` test missed budget 0). Dialogue page markers remain a dialogue classification;
known labels and fragments override it. The non-FONT consumers and static evidence are listed below.

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

## Non-FONT consumers (phase 7 second review)

Use `tools/debug/code.py FILE[:ENTRY] BASE --calls ADDRESS...`, `--refs ADDRESS...`, or `--range START SIZE`
to reproduce these disassemblies, including decompression. Map overlays load at 0x80168000, minigames at
0x801C0000, MECD:0 at 0x80110000, and FBTL.BIN at 0x80190000. Static budgets use the same descriptor formula
validated against the six measured windows above; column limits also reserve the following cursor/value field.

| Source | Consumer / evidence | Budget |
|---|---|---|
| FONT_10:117 | FBTL 0x80190188 passes 117, table 0x8017C000, x16 to draw_string; battle grid | 52 x 1 |
| FONT_10:028-030 | Battle sentence fragments (company, each, Also); appended to battle dialogue | 234 x 1 |
| FONT_10:079-099, :102 | Battle name / None substitutions | 114 x 1 |
| FONT_11 plain subject fragments :047-110 | Subject prefixes joined to battle messages; only the enumerated plain entries use this form | 234 x 1 |
| HMAP8500_18:082-084 | Rock/paper/scissors callback 0x80169028, descriptor +0x1FDC width10, x16 | 58 x 1 |
| HMAP8500_18:085-381 | Card names fed to `0x8003B63C` at overlay +0x570/+0x600/+0x6FC etc.; not an album list | 134 x 1; containing dialogue also reserves 134 per `{str}` (longest current name 131) |
| SMAP01_33:041-043 | Play/Info/Quit callback +0xD10, descriptor +0x1418 width10 | 58 x 1 |
| SMAP01_33:053-070 | Destination list callback +0xE2C reads records +0x13C0; descriptor +0x1434 widened 10 -> 18 tiles for bath names | 122 x 1 |
| SMAP16_37:130-137 | Callback +0x2628: two columns, x16/80; descriptor +0x46AC width24. First column ends before next cursor, second at interior186 | 52 first / 106 second, one line |
| DMAP03_92:027-036 | Animal puzzle callback +0x137C..+0x1490: x16+56*column; cursor reservation | 48 x 1 |
| HMAP26_66:163-164; HMAP2606_66:287-288 | Floor/swim travel callback +0x2C74 / +0x1468, descriptors +0x3B90 / +0x25A0, width18 | 122 x 1 |
| HMAP2607_66:021-025 | Floor guides callback +0x834, descriptor +0x1004 width12, x16 | 74 x 1 |
| HMAP26_66:215-270 | Music titles: callback +0x6D8, x40 after track number; descriptor +0x36FC width30 | 194 x 1 |
| HMAP2606_66:045-085 | Complete sayings inserted into :030 via `0x8003B63C` at +0x9F4 | 234 x 1; :030 reserves 180 for `{str}` (current maximum 178) |
| HMAP2606_65 | Word Maze letter clues/keyboard comparison, pointer list +0x209C; length routine +0x1400 caps at18, distribution +0xC78 copies individual u16 codes | 18 uppercase letters, no spaces/punctuation, single-glyph encoding; see engine.md |
| HMAP8300_18:038-041 | Restaurant callback +0x10DC: names x16, price right-aligned at144, suffix at148; reserve five 8px digits | 86 x 1 |
| MECD_1:000 | Save details callback +0xE2C, Level x24, party name x48 | 22 x 1 |
| MECD_1:001-018 | Save names enter prompts via +0x2F0/+0x30C; status labels via +0xF6C and position table +0x3108; descriptor +0x311C width20 | 106 x 1 (empty file starts x48, other states x8) |
| DARUMA_11:015-021 | Callback +0x154C; difficulty/character x16/88; suffix x121/142/109 (name's VWF advance), width32 | 70 / 58 / 90 x 1 |
| FUKU_11:006-012 | Callback +0xA58; difficulty/character x16/88; suffix x121/129/144; descriptor +0x1544 widened22 -> 28 and origin +0x1540 moved128 -> 80 to stay onscreen | 70 / 58 / 70 x 1 |
| FUKU_11:044 | Points at x36, descriptor +0x1524 widened7 -> 9 tiles | 30 x 1 |
| YUMI2_10:002 | Points at x40, descriptor +0x17CC widened8 -> 10 tiles | 30 x 1 (34 available) |
| YUMI2_10:009-011 | Score row separators / sum at callbacks +0x0000..+0x0258; sum heading beside final value | 9 / 16 / 9 x 1; Total -> Sum (a full equivalent word) |
| MOGURA_11:016-017 | Yes/No choice rows | 58 x 1 |
| BM008_1:278; BM028_1:222-233 | Battle quiz prompt / arithmetic question fragments | 234 px dialogue / one line |

Unused additions: FONT_10:122-154 are the unused monster-editor headings following the last battle message
(:121); no renderer consumer found in the EXE/FBTL/overlay inspection. YUMI2_10:003-004 are duplicate score-unit
strings with no caller (the score suffix callback uses :002). As with the earlier unused list, a newly found caller
must be measured and mapped. They are explicitly classified, never silently accepted as dialogue.

Source edge spaces are checked against the rendered insertion. The battle fragments :029/:030 preserve their
trailing separators; reviewed indentation and post-wait padding exceptions are in `script/space_ok.tsv`. Added
English joining spaces remain allowed. The short-final-line gate rejects literal final rows under six visible
characters after wrapping; runtime variables, independent quiz choices, credits rows and the exact two cipher
clues are treated separately. Wrapping also rebalances a short multi-word tail, not just a lone word.

Cold-boot verification: `work/qa/warp_review7_final/daruma_choices/scene.png` and
`work/qa/warp_review7_final/fuku_choices/scene.png` show all three rows and columns within their frames.
Both routes are named scenes in `tools/debug/scenes.lua`. The first Fuku probe exposed its wider frame running
past x320; the corrected x80 origin keeps the full 28-tile window and title suffix onscreen.

Battle joins: the consumer trace found FONT_10:029 only in every BM table's :083 reward, and :030 in
FONT_10:023/:047 theft messages. These templates now rely on the fragment's separator. Reward wording is
`{str}+{num} hearts!`, with `Each ` or an empty prefix, so both group and solo forms begin correctly.
`tools/debug/battle_join.lua` feeds these real strings and argument slots through the game's message builder;
it is an injected render check, not a claimed natural victory/theft. `battle_cmd` reaches the English command
grid from cold boot (settle1420, mash40); measured labels fit all four rows.

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
are short in English and pass the lint; the English grid is verified by the cold-boot `battle_cmd` scene. Minigame
result/score screens beyond the message box were not reached (HUDs are graphics); treat any new box found in phase 8
as unmeasured and measure it before fitting.

### Battle fragment runtime recheck

`tools/debug/battle_join.lua` exercises the real battle message builder with selected reward/theft arguments;
it substitutes the first attack message, rather than claiming a natural victory or theft. From a fresh
`battle_cmd` state, use `--debugger --var "MODE='each'"` (or alone/ryo/item), route
`6 circle;40 -;6 circle;300 -`, 400 frames. `work/qa/phase8_latest/join_*/final.png` verifies
"Each +37 hearts!", "+37 hearts!", "Also, 37 ryo was stolen!", and the item theft without doubled separators.
