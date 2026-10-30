# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** Step 0 (repo setup) done; next is phase 1 (research and recon). No build yet.
- **Done:** template filled; `tools/skill.py`; PCSX-Redux nightly in `tools/pcsx/` + SCPH-5500 in `tools/bios/`; `rom.sha1`
  pins the .bin (850eaabb…); `tools/check.py` (pytest `tests/`) wired into `.git/hooks/pre-commit` (CHECK line edited;
  a failing test was proven to block a commit); plugin guard hook blocks `sed -i` (canary checked); original disc
  boots with `--smoke` (`tools/routes/boot.txt`), circle on title starts a new game, a Lua probe's `L.log` lands in
  log.txt. Decisions D1-D8 recorded.
- **Next:** phase 1: dumpsxiso the disc (get mkpsxiso/dumpsxiso into `tools/`), list files, find the text engine
  (SJIS? custom table?), pointer tables, compression, font; check for earlier fan patches / official English names;
  graphics-text survey (title logo 桃太郎伝説, menu はじめて/つづきから, etc.). Write `docs/re/*.md`.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) PCSX-Redux GUI keyboard input not checked by hand (no interactive session
  in one-shot runs); scripted input verified.
