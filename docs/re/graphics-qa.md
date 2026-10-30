# Late graphics routes and evidence

These routes use the original game loaders and renderers after debug warps or story-flag setup. They do not
establish that a complete natural playthrough has been performed. Named scenes are in `tools/debug/scenes.lua`.

| Scene | Setup and evidence |
|---|---|
| `amap_stage3`, `amap_stage5` | Put Map (item 264) in slot 0, set u16 `800846AC` to stage 3/5, and use it through Items. Handler `8004E760` checks usability at `800340B4`, then `800341E4` starts event 13. The event copies the stage to byte `80084840`. Stage 0 is unusable. The NE island reads Fool and the compass N. |
| `congrats` | Museum map 311, tile 64,40; story u16 `80084786=202`, steps u32 `800918DC=30000`, talk to the clerk. The ball cap overlays the first four cloth rows: size 8 with a four-row inset makes the full Congrats! visible. Both caps read YAY. |
| `museum_sign` | Map 311, tile 49,29, the same museum-open/lit flag. The giant peach's sign reads Don't eat!; HMAP26:9 frame 29, texture :3 rectangle 80,232..128,248, CLUT :7 row 10. Paper index 10, ink 11/12/13. |
| `daruma_advanced` | Choose Advanced after the rules. Its 12-block tower places the Daruma / Drop! ribbons within the camera, unlike Beginner. The Time label now clears the old glyph's top pixel at texture y73. |
| `signs_restaurant` | Map 22, tile 107,14: the RESTAURANT sign is on the building immediately north. The earlier coarse camera grid missed this position; it was not an exhaustive placement search. |
| `bath_prices` | Map 378, tile 21,19: ADULT / CHILD on the wall board. HMAP8200:3 rectangle 129,1..159,17, CLUT :7 row 2. The original third label and prices are unreadable; neutral dashes follow D13. |
| `restaurant_menu` | Map 381, tile 22,12: MENU with decorative horizontal strokes, following D13 rather than inventing dishes or prices. Both HMAP8500:3 sprite and :0 background copies are redrawn. |
| `puzzle_oni_flip` | Map 403, tile 26,27: talk to the guard, advance the instructions, then walk left/down onto a panel. The yellow overlay appears briefly during the flip. The base and overlay use identical glyph geometry at texture y4/y100, font 13; CLUT :6 row 6 makes index 8 yellow. |

Fresh English proofs are `work/qa/warp_final_graphics/<scene>/scene.png` (2026-10-31). All five scenes passed after
the museum redraw. The menu suffix origins also follow each actual rendered name width, so Red Oni's,
Momotaro's and Poverty God's no longer have a detached possessive.

The four final scenes above have fresh English proofs in `work/qa/warp_final_boards/<scene>/scene.png` and
independent `ok` verdicts in `work/qa/boards_final/verdicts/boards_final.tsv`; its manifest gate passes. The
previously described "spare grey Oni" is this active yellow highlight, not unused art. Its 99 fill pixels and
129 outline pixels now align with the green base without a double image.

KIMONO is unused in the shipped map data: SMAP16:14 frame 909 has no placement in :34, no animation reference
in :35, no script reference, and no matching immediate in the executable or 133 overlays. The translated
texture remains available, but no runtime draw is claimed. Detailed searches and placement evidence are in
`work/qa/graphics_exceptions/report.md`. The four-opening squares in HMAP8200/8500:0 are window lattices;
the bath price board and restaurant menu are separate objects and are handled above.

The vertical food-sign variant at HMAP26:3 rectangle 128,64..144,120 is also translated. No HMAP26/2606/2607
frame-table part, tile set, or code immediate references it; a disc-wide sprite-part search found only the
horizontal sign. Its palette is inferred from the identical paper/ink index scheme, not a runtime draw.

## Battle-room scrolls

BB241:2 is a 256x256 background with CLUT BB241:1. Background index 73 maps to file 332 through the s16 table at
`8007B8A8`; fixed battles 2 (Gold Oni, SMAP04/0401) and 15 (wind boss, SMAP21) select it. The fixed-battle table
at `8007A61C` has eight-byte records, background index in byte 2. Call sites are SMAP04:34 `80168C98` and
SMAP21:32 `801686A8`.

Verified runtime probe from cold boot:

```powershell
$skillPath = python tools/skill.py
python -X utf8 "$skillPath/scripts/emu.py" build/momotarou_en.cue --out work/qa/scroll_room --debugger `
  --script tools/debug/warp.lua --script tools/debug/call.lua --script tools/debug/fileload.lua `
  --var "SCENE='talk_36'" --var "SCENES=[[$((Resolve-Path tools/debug/scenes.lua).Path.Replace('\','/'))]]" `
  --var AT=0x8003B284 --var CALL=0x80032A94 --var A0=2 --var AFTER=1600 --var SETTLE=1900 --var GOD=1 --frames 7000
```

This redirects an NPC message into the real fixed-battle starter; it is a forced caller, not the natural Gold
Oni encounter. `A0=15` reaches the other boss. Proofs: `work/qa/museum_signs/bb/fb_sheet.png`.

Each scroll's ink occupies only about 10x45 native pixels (x72,120,167; y61..106). Independent translator and
playtester inspections could not establish a Japanese word; candidate kana sequences did not form words and
the script provides no confirmed reading. The lower-right screen contains a pine painting, not lettering.
Keep the brush marks under D12, without presenting speculative English as a translation. Detailed scratch
analyses: `work/qa/bb241_reading.md`, `work/qa/museum_signs/report.md`.
