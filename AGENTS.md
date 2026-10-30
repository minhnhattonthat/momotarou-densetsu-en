# Momotarou Densetsu (PS1, Hudson 1996) English translation

Skill: translate-retro-game; `python tools/skill.py` prints its folder (`$SKILL` below). Read its SKILL.md before ROM, text or QA work. `"$(python tools/skill.py)"` works in bash and PowerShell; never paste a `plugins/cache/<hash>` path.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py` -> build/momotarou_en.bin + .cue (checks the dump against `rom.sha1` first; unpacks to work/disc if missing; regenerates MMPS_CD.SFS; ~1 s)
- Check:    `python -X utf8 tools/check.py`  (pytest `tests/` + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 "$(python tools/skill.py)/scripts/emu.py" build/momotarou_en.cue --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py <scene>.. | map:<id>:<x>:<y> | --all [--jobs 4] | --list` -> `work/qa/warp/<scene>/scene.png` + `work/states/<scene>.sstate` (cold boot; scenes in `tools/debug/scenes.lua`, RAM map `docs/re/debug.md`; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (xdelta vs the .bin + verify; never publish without the user) — phase 9
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original disc: `rom/Momotarou Densetsu (Japan).bin/.cue` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: PCSX-Redux in `tools/pcsx/` (nightly 29954.20261029.10 x64, via `$SKILL/scripts/fetch_emu.py pcsx` from distrib.app; gitignored). BIOS: `tools/bios/scph5500.bin` (`fetch_emu.py psx-bios`, picked up by emu.py). Savestates: `work/states/`.
- Disc tools: `tools/mkpsxiso/` (mkpsxiso 2.30 win64 from github.com/Lameguy64/mkpsxiso releases; gitignored). Unpacked disc: `work/disc/tree` + `layout.xml` (`dumpsxiso -x work/disc/tree -s work/disc/layout.xml rom/<cue>`).
- Format tools: `tools/pac.py` (PAC archives), `lzss.py`, `tim.py`, `font.py` (glyph code -> cell), `text.py` (decode string tables), `gfxdump.py` (image sweep).
- Text: `script/` (format TBD in phase 4). Tables: `tbl/jp.tbl` (u16 LE keys; kanji = OCR draft). Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- PS1: Japanese game confirms with circle (`--mash-key circle`). Title screen timing varies ~f1100-1700 from cold boot. Stop only your own emulator run (PID that emu.py prints).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
