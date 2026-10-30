# Word Maze probe (map 312, HMAP2606:65) — build work/qa/review7_new/momotarou_en.cue

Verdict: PASS. A real game-path answer RAISEDWITHCARE is accepted (memcmp 0, SUCCESS branch); a one-letter-wrong
answer takes the FAIL branch. Clue letters display correctly. One step (the clue NPC) used a forced entry; see below.

Reusable probes are promoted to `tools/debug/type_route.py` and `tools/debug/maze_clue.lua`; the original scratch
names below describe the recorded run. The route generator prints only controller input and never changes RAM.

## Base state (fresh, new build)
- `work/states/review7_labels_map_312_46_43.sstate` predates the build (emu.py warns it carries old overlay code and
  pointers), so it was NOT used. Fresh cold-boot warp on the new build:
  `emu.py work/qa/review7_new/momotarou_en.cue --out work/qa/word_maze_probe/warp --script tools/debug/warp.lua
  --var "SCENE='map:312:46:43'" --var "SCENES=[[<abs>/tools/debug/scenes.lua]]"
  --var "STATE_SAVE=[[<abs>/work/qa/word_maze_probe/map312.sstate]]" --frames 30000` (arrived f1989).
  Note: SCENES/STATE_SAVE need absolute paths (relative `tools/debug/scenes.lua` failed: emu cwd differs).
- RAM check (`ram_start.bin`): pointer list 0x8016A09C -> 0x8016B000..0x8016B52A (pool at overlay +0x3000), so the
  relocated pool is the one loaded. No pokes, no holds anywhere in this probe.

- Image: `map312.sstate` written 11:58 UTC, after the 11:57 UTC review7_new rebuild (Fukuwarai-only change), so every
  run here used the current image.

## Steps (probe hooks: `probe.lua`, log only, no register/RAM writes except `clue.lua`)
1. Start game — real path. From `map312.sstate`, route `10 -;3 up;20 -;2 right;20 -;2 up;20 -;6 circle;40 -;6 circle;30 -`,
   then `--mash 25 --mash-key circle` (`r5/`). Big Sis handler 0x80168850 entered f132 (active=0); mash picked the
   first choice (play). Count +0x1400 called with a0=0x8016B146 -> len 14; 14 calls of the distribution store loop.
   Result idx=10, len=14 ("This time the word has 14 letters!"). State `r5/s002400.sstate` (game active, field).
2. Clue table (RAM `ram_started.bin`, 0x8016A5D8, 20 x {u16 code, u8 pos}): 14 filled slots hold exactly the
   single glyphs of RAISEDWITHCARE with positions 1..14 (slot 10 = R/1, 15 = A/2, 1 = I/3, 9 = S/4, 2 = E/5,
   18 = D/6, 14 = W/7, 16 = I/8, 6 = T/9, 7 = H/10, 17 = C/11, 11 = A/12, 5 = R/13, 12 = E/14). Answer string at
   0x8016B146 = 12D2 12C1 12C9 12D3 12C5 12C4 12D7 12C9 12D4 12C8 12C3 12C1 12D2 12C5 8000 (EN_BASE single glyphs).
3. Clue message — FORCED ENTRY. Clue NPCs (id-0x82 = slot, handler 0x801692E8 -> 0x8016932C) sit behind maze walls;
   navigation not attempted. `clue.lua` redirects the next Big Sis talk (0x80168850, ra kept) into the real clue
   routine 0x8016932C with a0=SLOT; data and message path are the game's own. From `r5/s002400.sstate`, route
   `5 -;2 right;20 -;2 up;20 -;6 circle;40 -;6 circle;20 -`. Shots: `clue_10/f000600.png` "letter No. 1: R!",
   `clue_14/final.png` "No. 7: W!", `clue_17/final.png` (C), `clue_0/f000600.png` empty slot "I don't know any letters".
4. Answer input — real caller. Same talk route without redirect (`a1/`): handler f104 active=1, then name entry
   0x800DC3D0 a0=6 from ra=0x801688EC (the 0x801688E4 call) at f460. Keyboard shot `a1/final.png`.
5. Typing — real input. From `a1/s000400.sstate`, route from `type_route.py RAISEDWITHCARE "57 -;6 circle;100 -" "60 -"`
   (d-pad 4 frames + 8 gap, circle per letter; cursor stays on the last letter) -> `typed.sstate`, `a2/final.png`
   shows R A I S E D W I T H C A R E.
6. Confirm + compare — real path. `ok_done/`: cursor down x5, right x3 onto Done, circle, then mash circle.
   Entry returned v0=14, buffer 0x800ACDF0 = same 14 codes + 8000. "So the word is 'RAISEDWITHCARE', right?" Yes.
   memcmp 0x80069C18 entry (ra 0x80168984): a0=0x800ACDF0, a1=0x8016B146, a2=28 bytes -> v0=0; length 14 == 14 ->
   SUCCESS branch 0x80168998 (f642). Shots `ok_key.png`: confirm prompt, "Amaaazing, that's right!!", full saying
   "Raised with loving care", meaning; `ok_key2.png` continuation. `ok_start/`: Start on the keyboard also acts as
   Done, same SUCCESS.
7. Negative control: `wrong/` types RAISEDWITHCARS -> memcmp v0=14 (nonzero) -> FAIL branch 0x80168AB8,
   "Sniff! That's wr..." (`ok_key2.png` bottom right).

## Residual uncertainties
- Clue message reached by redirect, not by walking to an NPC; NPC-to-slot mapping (byte 0x800919A9 - 0x82) not
  exercised in-world.
- Only answer idx 10 tested end to end; the other 40 answers rely on tests/static checks (rand pick, no forced idx).
- Hook at the jal 0x8016897C logs a stale a1/a2 (load/delay slot); trust the memcmp-entry line.
- Reward/time dialogue after success only skimmed (not part of this check); no text-overflow review done.
- The wrong-answer run's later "come play again" exit and game reset (active=0) not inspected.
