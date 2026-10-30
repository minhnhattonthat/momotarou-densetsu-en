# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3 (identity build) done 2026-10-30; next is phase 4 (extract).
- **Done (phase 3):** `tools/build.py` -> build/momotarou_en.bin/.cue, byte-identical to the dump (sha1 test), ~1 s.
  `build.build({disc path: bytes}, out_bin)` replaces files via `build/layout.xml` sources and regenerates
  MMPS_CD.SFS from mkpsxiso's LBA log (docs/re/archives.md). `pac.unpack`/`pac.pack` repack all 585 PACs
  byte-identical (header has a per-entry u32 param at +12: keep it). Tests in `tests/test_build.py` (identity,
  SFS after a 5000-byte growth, all PACs). In-game: build with GUEST.PAC +2048 bytes warps to the village fine.
  Smoke on build/momotarou_en.cue: ok (title).
- **Next (phase 4):** extract every string table (types 0x10d/0x116 + EXE strings, docs/re/text.md) to `script/`,
  roundtrip test (re-encode == original bytes), coverage of text ranges. Insert path = decompress entry, edit,
  `lzss.compress`, `pac.pack`, `build.build`. LZSS recompress is verified on 60 sampled entries only.
- **Done (phase 2):** `tools/debug/warp.py` + `warp.lua` + `scenes.lua`: cold boot -> any scene, proof shot
  `work/qa/warp/<scene>/scene.png`, state `work/states/<scene>.sstate`; `--all` regenerates every state, `map:<id>:x:y`
  reaches any of the 560 maps. Scenes: title + load screen, village/house/2nd town/overworld/dungeon, field menu and
  all 7 submenus, 3 shops (buy lists), NPC talk, random battle, events 0-4/7-17 (intro-free: baths, ATOK, AMAP,
  card album, END00, staff roll start + last page, END01 epilogue, PT00), minigames 0/2-6. RAM map, main-loop states,
  file loader and map tables in `docs/re/debug.md`. `tools/debug/fileload.lua` logs every disc file load (--debugger).
  Confirmed: the game loads files through MMPS_CD.SFS (build.py rewrites it).
- **Later notes:** kanji table needs reviewer pass (92 duplicate OCR values; known misreads in docs/re/text.md) before
  phase 4 jp text is final. SMAP16.PAC:37 string table doesn't decode with the simple rule. PCSX-Redux nightly
  `GPU.getVRAM()` returns 2 MB (1024 rows): read the first 512 rows.
  Debug-tool gaps (add when a phase needs them): event 5 (EVT069) and minigame 1 (YUMI1 other entry) stay black
  from a plain warp (need their calling script's context); no fixed-enemy-group battle yet (exec hook on
  0x8004540C a0 with --debugger); no story-flag array yet (events/NPCs that depend on progress); party is the
  New Game party (1 member, no items: `MONEY=` var exists, inventory RAM unknown); shops/NPCs found only for town 2.
  GOD uses the GameShark HP addresses (not checked per member). CR_PG01-99 not loaded by the ending (card pages?).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) PCSX-Redux GUI keyboard input not checked by hand (no interactive session
  in one-shot runs); scripted input verified.
