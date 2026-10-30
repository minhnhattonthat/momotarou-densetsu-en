Momotarou Densetsu (PlayStation) - English fan translation v@VERSION@

This is an unofficial fan translation. It contains no playable game image.
Use your own clean Japanese disc dump. Do not distribute pre-patched ROMs.

BASE DISC
Name: Momotarou Densetsu (Japan).bin
Serial: SLPS-01785
Disc reference: http://redump.org/disc/17974/
Size: @BASE_SIZE@ bytes
CRC32: @BASE_CRC32@
MD5: @BASE_MD5@
SHA-1: @BASE_SHA1@

PATCHING
1. Keep an untouched backup of your original .bin and .cue.
2. Use xdelta3 or an xdelta-compatible patcher to apply @PATCH@ to the
   original .bin, saving the result as Momotarou Densetsu (Japan).bin in
   a separate folder. Never apply it to the .cue or an already-patched image.
3. Copy your original .cue into that folder. Its FILE entry must name the
   patched .bin exactly. The original single-track layout is retained.
4. Boot that .cue in your emulator. Start from a cold boot; old savestates
   contain old code and graphics. Circle confirms and Cross cancels.

Command-line example (choose a new output path):
xdelta3 -d -s "original.bin" "@PATCH@" "Momotarou Densetsu (Japan).bin"

PATCHED IMAGE
Size: @PATCHED_SIZE@ bytes
CRC32: @PATCHED_CRC32@
MD5: @PATCHED_MD5@
SHA-1: @PATCHED_SHA1@

TRANSLATION STATUS
Dialogue, story, menus, items, skills and system messages: English.
Readable signs, banners, cards, minigames and ending lettering: English.
Name entry: English default; optional Hiragana and Katakana pages retained.
Credits: English transliterations. Original audio/music is unchanged.
Original Japanese game logo: retained; no official English logo exists.
Decorative characters on illustrated props/costumes and unreadable background brush
marks remain. Tiny illegible board details are adapted as neutral marks;
no prices or dishes were invented. The tongue-twister board retains its
internal Japanese game data; player-facing instructions are English.

TESTING AND LIMITATIONS
Tested with PCSX-Redux nightly 29954.20261029.10 x64 and a Japanese PS1 BIOS.
The final image passed cold-boot smoke, automated scene routes, text/engine
checks, independent visual review and chapter-level story review. Routes
use external debugger warps; the release image contains no injected debug
tool or cheats. This is not a complete natural gameplay playthrough.
Some status sprites were verified by forcing the real renderer's sprite ID.
GUI keyboard input has not been manually checked; scripted input was tested.
Cards 97/98 have a slightly flatter grey background beneath the English name.
Some staff and contest-contributor name readings remain inferred from Japanese.
No known unresolved runtime defect. Real hardware has not been tested.

CREDITS
Original game: Hudson Soft and its original creators (see in-game credits).
English translation and tools: this project's contributors, with extensive
AI assistance from Claude (Anthropic) and Codex (OpenAI).
Earlier terminology reference: KingMike's Famicom Momotarou Densetsu patch;
the owner's Shin Momotarou Densetsu translation glossary.
Fonts: project MIT-licensed en12 glyphs; Rounded M+ ExtraBold (OFL 1.1),
rendered as pixels. Full font provenance and licences are in the source repo.
Tools: PCSX-Redux, mkpsxiso/dumpsxiso, xdelta3 and the retro-translation skill.

Source, build instructions and bug reports:
https://github.com/minhnhattonthat/momotarou-densetsu-en
For a bug report, include the patch version, emulator, steps and a savestate
if available. The source repository contains decisions and QA limitations.

This project is not affiliated with or endorsed by Hudson Soft or its owners.
