# Momotarou Densetsu English translation

Unofficial English fan translation of **Momotarou Densetsu** (PlayStation, Hudson Soft): the source text and tools
that build the patch.

The local **v1.0** patch is built and verified; no release has been published. The ZIP at
`release/v1.0/Momotarou_Densetsu_EN_v1.0.zip` contains an xdelta patch and patching instructions.
You need your own clean dump of the Japanese game. See [the verification record](docs/release.md).

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue and story | English |
| Menus, items, skills and system messages | English |
| Signs, banners, cards, minigames and ending lettering | English |
| Original Japanese game logo | Retained; no official English logo exists |
| Name entry | English default, with optional Hiragana and Katakana pages |
| Credits | English transliterations |
| Audio and music | Original |

No known unresolved runtime defect. Cards 97/98 retain a slightly flatter grey background under their English
names. Decorative characters on illustrated props/costumes and unreadable brush marks remain; partly illegible boards
use neutral marks. These adaptations are recorded in [the decisions](docs/decisions.md).

Testing uses PCSX-Redux nightly 29954.20261029.10, cold boots and debugger-assisted scene routes. It is not a
complete natural playthrough, and real hardware has not been tested. See [current QA evidence](docs/status.md)
for coverage and limitations. Cold boot the patched image instead of loading an old savestate.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.claude/agents/` | Subagent types (translator, reviewer, visual QA, playtester) with only the tools each needs. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/momotarou-densetsu-en
cd momotarou-densetsu-en
# copy your dump to: rom/Momotarou Densetsu (Japan).bin + .cue
#   (144048240 bytes, SHA-1 850eaabb0feb0dda476471f4b69c67537755a7db; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/build.py                          # -> build/momotarou_en.bin
python -X utf8 tools/check.py                          # tests + text lint
```

The required base image is **144,048,240 bytes**, CRC32 `C591C72F`, MD5
`9af16cfdf494afb2535f0edc88adb9f5`, SHA-1 `850eaabb0feb0dda476471f4b69c67537755a7db`.
The disc serial is SLPS-01785; these values match [Redump disc 17974](http://redump.org/disc/17974/).
The build checks the SHA-1 before editing any data.

Release preparation additionally needs xdelta3, the project emulator and the translate-retro-game skill:

```sh
python -X utf8 tools/release.py --prepare               # build, tests, smoke, Japanese scan, fresh scene tour
# Independent reviewers supply current story and visual verdicts (docs/release.md).
python -X utf8 tools/release.py --skip-tour             # verify all gates, make/reapply patch, package ZIP
```

`--skip-tour` requires evidence from the exact same image. The command refuses an existing version unless
`--force` is supplied, keeps the playable image in `build/`, and never publishes anything.

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Hudson Soft's and is included only so
the translation can be checked against it. Momotarou Densetsu is (c) Hudson Soft; this project is not affiliated with them.
Do not share patched ROMs.

The translation was made with extensive AI assistance from Claude (Anthropic) and Codex (OpenAI).
Terminology references include KingMike's Famicom translation and the owner's Shin Momotarou Densetsu glossary.
Font provenance and licences are in [docs/fonts.md](docs/fonts.md). Corrections are welcome.
