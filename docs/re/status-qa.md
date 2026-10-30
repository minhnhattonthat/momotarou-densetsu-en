# Status probe: FONT.PAC:4 status words (FONT.PAC:8 sprites 42-47) in battle (2026-10-30)

ROM `work/qa/phase8_latest/momotarou_en.cue`, state `work/states/m8_fix2_battle_cmd.sstate` (opens in Fight target
select; `6 cross` backs out to the grid). Nothing tracked edited, no build. All probes/shots in this folder.
`SK` = `python tools/skill.py`.

## Verdict
- **No natural game path found that shows sprites 42-47.** Not claimed visible in normal play.
- **Forced render: all six words draw correctly through the engine's own sprite renderer** (0x8001D194, bank 0 =
  FONT.PAC:8 table 0x80170000): `forced_words.png` (2x; left Sick / Con-fused / Asleep, right Para-lyzed / Poison /
  Sealed). Colours, two-line splits, no clipping or bleed. Debug-forced: object anim stopped, id/xy written by Lua.
- What battle really shows for ailments: **16x16 icons on the HP box** (skull, lightning, ...: FONT.PAC:8 sprites
  48-64), shot `sC/f000390.png`. Those are pictures, no text.

## Sprite system (RAM facts, this battle)
- Object list head u32 `0x800846B4`, next `+0x68`; `+0x00` flags (<0 off), `+0x04/+0x06` x/y (relative to parent),
  `+0x0A` u16 sprite id, `+0x4C` anim script ptr, `+0x5C` sprite bank, `+0x5D` anim bank. Alloc `0x8001C52C()`,
  free `0x8001C6B0(obj)`, set anim `0x8001C768(obj, anim)`. Sprite banks `0x800ACF00[]` (0 = 0x80170000 FONT.PAC:8),
  anim banks `0x800ACF40[]` (0 = 0x8017A000, 25 anims). Anim script u16: `< 0x8001` = sprite id, `0x8001 n` = wait.
- Bank-0 anims 0x00-0x18 use frames 1-3, 5-14, 0x17-0x44, 0x52..0x312: **never 42-47**. Static scan of 2 MB RAM:
  no `addiu rt, 0x2A..0x2F` -> `sh rt, 0xA(obj)`, no u8 table of 42-47; only u16 table `0x800FD4D8` (2C 2B 2D 2A
  2F 2E), which is a message-id table (below), not sprite ids.

## Battle ailment display path (found, real)
- `0x800F9B54` (battle): `0x800D85C8` (free icons, calls `0x800D81D8(m, -1)` per member) -> `0x80029CE4` ->
  `0x800D83C4` -> `0x800D81D8(member, a1)`: up to 3 objects per member, anim `0x800E33B4[s]` (s 0-5 -> anim 0x16,
  0x12, 0x15, 0x14, 0x13, 0x17 = sprites 62-64 / 48-50 / 58-61 / ...), s = `0x800D8050(member, k)` = k-th active of:
  - battle (u8 `0x800FE3D0` != 0): s0 `0x800FE9F8[m] & 3`, s1 `& 4`, s2 `& 0x40`, s3 `& 8`, s4 `0x800FEA30[m] & 8`,
    s5 `0x800FE980[m] != 0`;
  - field: s0-s2 from field flags u16 `0x80091238 + 0x52 + 2m` (`&3`, `&4`, `&0x40`).
  Seen: closing the battle Status panel with s0-s2 forced -> icons on Momotaro's HP box (`sC`, f381).
  `0x800D83C4` callers: `0x800F9B7C` (battle), `0x80035D54`, `0x80036554`, `0x800466C4` (field).
- Forcing `0x800FE9F8[0] = 0x45` makes the engine act on it ("Momotaro is paralyzed and can do nothing!", `sA`).
- Field status summary (`0x800D9DEC` loop) writes ailments as text FONT_6 0x23B/0x23C/0x23D from the same flags.
- Status tick `0x800E9668` walks 12 per-unit arrays (ptr table `0x800FD498`: FEB30 FEC20 FEAB8 FEC08 FEB60 FEC60
  FE980 FEBD0 FEB48 FEBA0 FE950 FEBB8); bits 0x38 = turns left, 0xC0 = level. On expiry it calls
  `0x800F8D98(0, 0x800FD4CC[k])`: **0x800F8D98 is the battle message call** (swapping a1 changed the shown line,
  `sw2a`), so `0x800FD4D8` 2A..2F are message ids, not sprites. 0x800FEBD0 = array 7; 0x8019AF10 / 0x8019B654
  (FBTL) read it for the "can't act" check (`& 0x38` -> flag 0x100 at 0x800FE402), no sprite work.
- Monster ailments forced (`monst.lua`, units 4-7, all arrays + FE9F8/FEA30/FE980): "woke up / is asleep / poison"
  messages, no sprite-table reads of 42-47 in 900 frames (`mo1`).

## Repro
For the current build, first run `python -X utf8 tools/debug/warp.py build/momotarou_en.cue --tag status_final
battle_cmd`. The promoted `tools/debug/status_flags.lua` and `status_words.lua` need no scratch script for the
proof shot: use both with `--debugger --var "SET={0,1,2}" --var FROM=135 --var WFROM=383`, the route below,
`--frames 400 --shots 390`, and `IDS`/`XS`/`YS` as below. Fresh-build proof images are
`work/qa/phase8_cardsfix/status_a/f000390.png` and `status_b/f000390.png`. The original optional read/object logs
below document how the renderer was identified; they are not needed to repeat the render.

Real icons (s0-s2 forced, panel opened then closed):

    python -X utf8 $SK/scripts/emu.py work/qa/phase8_latest/momotarou_en.cue --out work/qa/status_probe/sC --debugger \
      --state-in work/states/m8_fix2_battle_cmd.sstate --script tools/debug/status_flags.lua \
      --script work/qa/status_probe/objwalk.lua --var "SET={0,1,2}" --var "FROM=135" \
      --route-str "20 -;6 cross;24 -;6 down;24 -;6 down;24 -;6 right;24 -;6 circle;200 -;6 cross;60 -" --shots 390

Forced words (same + `--script work/qa/battle_probe/sprread.lua --script tools/debug/status_words.lua
--var "WFROM=383" --var "IDS={42,43,44}" --var "XS={-95,-15,65}" --var "YS={-30,-30,-30}" --shots 390,400`; B run
`IDS={45,46,47}`). sprread logs `pc=8001D268 ra=8001D6CC id=42..47` at f383: the real renderer reads the records.

## Not checked / open
- Field status menu with forced field flags (code read only: text, plus the same HP-box icons).
- Any overlay not resident in this battle (other FBTL/BM overlays, boss scripts, event scenes) could still use 42-47;
  a scan of those files for `sh rt, 0xA` near 0x2A-0x2F or anim scripts with frames 42-47 is the next step.
- Possible conclusion for the owner: 42-47 may be unused leftovers; translating them costs nothing but is unverifiable
  in play. Do not mark them "seen in battle" from this report.

## Files
Probes: `poke.lua` (hold status arrays + sprite reads), `once.lua`, `stamp.lua` (force s0-s5 for a member; hooks
0x800D81D8 / 0x8001C768), `objwalk.lua` (object list walker), `idwrite.lua` (who writes +0x0A/+0x5C), `f8swap.lua`,
`monst.lua`, `textcall.lua` (text-object callers), `forceword.lua` (forced render). State `status_panel.sstate`
(battle Status panel open, no ailment). Shots: `forced_words.png`, `forced_words_zoom.png` (overlapping first try),
`sC/f000390.png` (real icons), `sA/final.png` (paralysis effect), `arr_sheet.png`.
