# Local release verification

## Verified v1.0 artifact (2026-10-31)

The successful `tools/release.py --skip-tour` run created
`release/v1.0/Momotarou_Densetsu_EN_v1.0.zip` (5,228,889 bytes). Its only members are
`Momotarou_Densetsu_EN_v1.0.xdelta` and `README.txt`; nothing has been published.

| Artifact | SHA-1 |
|---|---|
| Clean original BIN | `850eaabb0feb0dda476471f4b69c67537755a7db` |
| Patched and independently reapplied BIN | `b9efce63146b023d5af12e069f8ccb1d78185ee9` |
| xdelta patch | `27e52d5b3af18a8c33f0e48404c44729985113ad` |
| ZIP | `d92f8052ab115d26aad9b1e3758a7260e588b0b9` |

The patched BIN is 143,902,416 bytes, CRC32 `140CA2E7`, MD5 `6bb797324c81a14bf2daf21a0089d344`.
Reapplication matched all these values. The final run passed 55 tests, 6,027 lint checks, cold-boot smoke,
the 33,669-string actual-disc scan, the production-EXE comparison, all six visual gates (258 sheets), and
the 13-chapter story gate. Every sheet of the final 92-scene tour received an independent visual verdict.
This is debugger-assisted scene coverage, not a complete natural playthrough or a real-hardware test.

Evidence: `release/v1.0/verification.json`, `work/phase9/release-package.log`,
`work/phase9/release-candidate-prepare.log`, and the manifests listed in `docs/release-gates.json`.
The scan adapter is necessary because the shared scanner does not directly follow compressed PACs or this
game's u16 `0x8000` string terminators; its pointer-based export is described below.

## Reproducing the release

`python -X utf8 tools/release.py --prepare` builds the normal English image, runs the complete check,
cold-boots it, scans its reachable text, exports the story chapters and captures every debug scene from
that image. It creates evidence, not a patch. Reviewers then assess the chapter files and scene sheets.
`python -X utf8 tools/release.py --skip-tour` rebuilds and checks again, requires the tour's image hash to
match, checks every active QA gate and the polish checklist, creates an xdelta patch, reapplies it to the
clean original and compares the complete image hashes before making a patch-and-README-only ZIP.

The default command captures a fresh tour. `--skip-tour` only reuses a receipt whose image SHA-1 and every
scene-shot SHA-1 still match. Every sheet also needs the independent `qa_gate.py` verdict. `--help` performs
no build or packaging; a version directory with files is refused without `--force`.

## Active evidence

`docs/release-gates.json` enumerates the current five phase-8 gates, the final release scene tour, and the
story gate. The explicit phase-8 set is the one recorded in `docs/status.md`. Earlier card repair rounds
and exploratory manifests are superseded, including rounds that failed; they are neither accepted as
release evidence nor silently converted into successful reviews. All active manifests are mandatory.

## Story coverage

`tools/story.py` exports eight narrative arcs following `docs/synopsis.md`, plus complete supplemental
chapters for hermits, museum/cards, minigames/travel, system/shops, and battles. It fails if a script table
is unassigned or assigned twice. All authored entries are included except the explicitly classified
non-display tongue-twister data table. Identical battle JP/EN pairs are read once, with every repeated
entry mapped to its reviewed counterpart in `work/qa/story/battle-aliases.json`.

Locations follow the story's progression. Within a location, alternative NPC responses and story-state
branches remain labelled in resource order, rather than pretending they are one continuous conversation.
The principal boss battle exchanges are included with the relevant arc to expose voice changes before
and after reconciliation. This textual continuity review complements, rather than claims to be, a full
natural gameplay playthrough. Every chapter needs a current read-only review; changed text invalidates
the chapter hash and requires another verdict.

The story pass exposed two consistency failures that now have regression tests: the 41 Word Maze answer
keys must normalize to exactly the letters in their displayed sayings, and museum scrolls must repeat the
same English as the matching Japanese proverb encountered in a village. The Word Maze keeps its verified
18-letter input limit; longer meanings remain in the following explanatory dialogue (decision D14).

All 13 final chapter verdicts passed on 2026-10-31. Full reports are under `work/qa/story/reports/final_*.md`;
chapter 04 has a fresh full reread in `recheck_04_hope.md`, and chapters 12/13 have subsequent rechecks.
The last two chapter-12 duplicate-prompt corrections were independently reviewed in context, with each
previous approved chapter reconstructed in memory and its SHA-1 verified to prove the exact one-line delta.
The final report is `finalcheck_12_system_and_shops.md`; `intermediate_12_system_and_shops.md` preserves the
preceding delta proof. `final_coverage_note.md` records completion of initially truncated read ranges for
chapters 09-11 before accepting their verdicts. Every optional Minor has an explicit decision in `docs/polish.md`.
The late museum finding extended the regression to all 50 scrolls, including the proverb embedded inside
OMAP00_43:056; its failed test was reproduced before correcting HMAP26_66:209.

## Japanese scan and debug exclusion

`tools/release_scan.py` reads ISO9660 files directly from the final raw disc, decompresses the PAC entries,
follows every extracted pointer in every copy, and compares each reachable string with the current
authored and laid-out text. It supports both word pointers and MIPS LUI/ADDIU pointers. The exported byte
corpus is scanned by the skill's `jp_left.py --le16 --min 1 --kanji-runs` using the full runtime table,
including English digraphs. It does not use `--orig`, sample strings, or filter by NUL bytes: this engine
uses a u16 `0x8000` terminator, and native glyphs frequently contain zero bytes.

The original extraction coverage test checks that text outside known tables/pointers is accounted for.
The final scan checks every known live text pointer; graphics are covered by the separate visual gates.
The optional kana name-entry pages and the internal tongue-twister board data remain deliberately
Japanese. The board is checked against the original bytes. The entire final EXE is compared with the
normal production transformation of the clean EXE, including its repointed name-entry labels, so added
debug hooks fail verification. Scene warps and cheats run only as external PCSX Lua scripts.

Scan details, corpus offsets and the exact image hash are saved under `work/qa/release/scan/`. The local
release directory contains `verification.json` with original, patched, patch and ZIP hashes. Only the
patch and README go into the ZIP; no BIN, CUE, BIOS or savestate is included. Nothing is uploaded.
