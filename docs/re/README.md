# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| [archives.md](archives.md) | disc layout, MMPS_CD.SFS file table, PAC archives, LZSS, TIM variant | verified (SFS use by the game: guess) |
| [text.md](text.md) | u16 glyph codes, font pages, control codes, renderer, string tables, volume | encoding/renderer verified; kanji table OCR draft |
| [debug.md](debug.md) | main loop, map/event/minigame/battle RAM, file loader, warp tool | verified (warps with proof shots) |
| [graphics.md](graphics.md) | graphics-text survey (static sweep + boot tour), cards, signs, title | survey done; sources partly guessed |

## Prior work (checked 2026-10-30)
- No fan translation of the PS1 game (SLPS-01785) found. KingMike translated the NES/Famicom Momotarou Densetsu
  (romhacking.net #1779, 2012): the "earlier fan patch" for name romanisation (D2). The owner's own SNES
  `shin-momotarou-densetsu` repo (H:/translation/shin-momotarou-densetsu, glossary.md) shares most names
  (Momotaro, Kintaro, Urashima, Yasha, Enma, Ashura, Karura, Kaguya...) — reuse its spellings, but note its
  honorific ruling differs from this repo's D1.
- No official English names (never released outside Japan).
