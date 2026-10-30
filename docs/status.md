# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1 (research and recon) done 2026-10-30; next is phase 2 (debug tool). No build yet.
- **Done (phase 1):** disc unpacked with dumpsxiso (`tools/mkpsxiso/`); PAC archive format, LZSS (Okumura, encoder
  byte-exact), TIM variant, text encoding (u16 glyph codes `plane<<12|sheet<<9|cell`, verified on in-game text),
  renderer at 0x8003E128 + control-code jump table (no inline args), string-table format and containers, script
  volume (~5.9k unique strings), MMPS_CD.SFS file table, free-space candidates, static graphics sweep (1,055 images,
  all 44 sheets read) -> `docs/re/{archives,text,graphics}.md`, `docs/re/gfx_survey.tsv`. Draft `tbl/jp.tbl`
  (kana verified, kanji OCR). Tests: `tests/test_formats.py` (LZSS roundtrip/byte-exact, code mapping, menu decode).
  No earlier PS1 patch exists; NES patch (KingMike) + owner's SNES Shin Momotarou glossary are the name sources.
- **Next (phase 2):** debug tool `tools/debug/warp.lua` + scene list: find map id / story-flag RAM (ramsearch over
  `work/qa/recon1` style dumps), warp to towns, dungeons, battle, card album, minigames (DARUMA, MOGURA, YUMI, FUKU,
  FURO, SUIEI), ending (END00-02), memory-card menu. States in `work/qa/recon1/s00{1..5}000.sstate` (boot, title,
  first village intro at f5000).
- **Later notes:** kanji table needs reviewer pass (92 duplicate OCR values; known misreads in docs/re/text.md) before
  phase 4 jp text is final. Check whether the game reads files via MMPS_CD.SFS (phase 3 rebuild must update it).
  SMAP16.PAC:37 string table doesn't decode with the simple rule. PCSX-Redux nightly `GPU.getVRAM()` returns 2 MB
  (1024 rows), not the 1 MB the skill's pcsx_lib comment says: read the first 512 rows.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) PCSX-Redux GUI keyboard input not checked by hand (no interactive session
  in one-shot runs); scripted input verified.
