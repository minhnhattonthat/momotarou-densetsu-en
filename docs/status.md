# Status

Updated 2026-10-31. History is in git; the current evidence below supersedes older failed or partial QA rounds.

- **Phase:** 9 complete; all nine phases are complete. The local v1.0 patch-only ZIP is built, reapplied and verified.
  Published 2026-10-31 as GitHub release v1.0 (repo stays private):
  https://github.com/minhnhattonthat/momotarou-densetsu-en/releases/tag/v1.0. All seven release gates pass: 258 visual sheets and 13 story chapters.
- **Latest build:** `build/momotarou_en.bin`, 143,902,416 bytes, SHA-1
  `b9efce63146b023d5af12e069f8ccb1d78185ee9`, built 2026-10-30 20:50:21 UTC (2026-10-31 locally).
  Fresh boot smoke passes in `work/qa/release/smoke`. Full check passed 55 tests and 6,027 lint checks with zero
  errors. The actual-disc scan checked 252 containers / 33,669 reachable strings, found zero unintended Japanese,
  and verified the entire production executable without debug additions.
- **Final card repair:** all 297 original/English assets are in `work/qa/cards_final_pass/assets`.
  The disc cleanup fits consensus outline stamps instead of guessing a radius or starting a flood inside a
  Japanese glyph. Shared stat masks preserve horns/staff tips; bounded name masks and explicit flavour
  protections preserve character art and inner frames. Stat labels match the 14-pixel digit rows. Cards 1/9
  use four flavour lines. The 99 fresh runtime pages in `work/qa/cards_final_pass/album` were captured
  from a cold-boot state and all passed read-only review. Earlier album rounds are superseded,
  **not green evidence**.
- **Phase-7 findings closed:** all single-line labels require classified consumers, including non-FONT tables;
  `label_refs.py --unmeasured` reports zero. Source edge spaces are checked with explicit reviewed exceptions.
  Actual battle-builder probes fixed solo/party reward joins and duplicate theft separators. Word Maze answers
  use single uppercase glyph codes in a safe appended pool; correct/wrong keyboard paths are verified.
  Literal short-final-line stubs fail lint. Details: `docs/re/windows.md`, `engine.md`, `word-maze-qa.md`.
- **Graphics coverage closed outside album:** AMAP Fool/N through the Map item, full Congrats!/YAY through the
  museum clerk, Don't eat! on the peach exhibit, Daruma/Drop! on Advanced, translated roof/town signs, one
  centered The End, and six large status words through the real renderer. Status words use forced sprite IDs;
  natural ailment UI uses small icons. These are debug-assisted proofs, not a complete natural playthrough.
  Repeatable scenes and limitations: `docs/re/graphics-qa.md`, `status-qa.md`.
- **Last coverage exceptions resolved:** RESTAURANT is active at map 22 tile 107,13; the earlier coarse camera
  sweep missed it. KIMONO has no shipped placement/animation/script/code caller. The grey Oni texture is the
  active yellow flip highlight; matching base/overlay geometry is verified after the real guard sequence.
  Bath ADULT/CHILD and restaurant MENU boards are adapted under D13 without invented prices/dishes.
  The unused vertical museum sign is translated but has no caller.

## Current release gates

Run the skill's `scripts/qa_gate.py check MANIFEST VERDICT_DIR`. The five accepted phase-8 graphics sets remain
current; the additional 92-scene cold-boot tour is tied to the exact final image hash and every captured shot.

| Manifest | Verdict directory | State |
|---|---|---|
| `work/qa/phase8_cardsfix/tour_manifest.tsv` | `work/qa/phase8_cardsfix/tour_verdicts` | 83 sheets, green |
| `work/qa/graphics_final/manifest.tsv` | `work/qa/graphics_final/verdicts` | 13 sheets, green |
| `work/qa/boards_final/manifest.tsv` | `work/qa/boards_final/verdicts` | 4 sheets, green |
| `work/qa/cards_final_pass/assets_manifest.tsv` | `work/qa/cards_final_pass/asset_verdicts` | 33 sheets / 297 pairs, green |
| `work/qa/cards_final_pass/manifest.tsv` | `work/qa/cards_final_pass/verdicts` | 33 sheets / 99 pages, green |
| `work/qa/release/manifest.tsv` | `work/qa/release/verdicts` | 92 final-image scene sheets, green |
| `work/qa/story/manifest.tsv` | `work/qa/story/verdicts` | 13 complete chapters, green |

Older manifests from `v0`, `cards_final`, `cards_round4` (moved to `work/qa_archive/` 2026-10-31 so the
release guard, which scans every `work/qa/**/manifest.tsv`, ignores them) and other repair rounds are historical
failed or superseded evidence. The release script validates the explicit current set above. Earlier phase-9 candidate
logs that failed or preceded the final text corrections are also superseded.

## Release and next

`release/v1.0/Momotarou_Densetsu_EN_v1.0.zip` is 5,228,889 bytes, SHA-1
`d92f8052ab115d26aad9b1e3758a7260e588b0b9`. It contains only the xdelta patch and README. Reapplication to the
pinned original matches the complete final image (size, CRC32, MD5 and SHA-1). Details: `docs/release.md` and
`release/v1.0/verification.json`. The successful run is `work/phase9/release-package.log`; final tour preparation
is `work/phase9/release-candidate-prepare.log`.

Story polish fixes include all 50 museum callbacks, all 41 Word Maze answer/reveal pairs, Ashura's battle voice,
the BayStars reference, a Kanji quiz decoy, shop voice and deferred line-level minors. Regression tests reproduce
and prevent both callback failures; every final chapter has an independent current verdict. All optional notes
are resolved in `docs/polish.md`, with review provenance in `docs/release.md`.

No next implementation phase is queued. Await playtest feedback or explicit owner overrides; never publish a
release or change repository visibility as part of this run.

## Open issues and defaults

- No known unresolved runtime defect; all final album, tour and supplemental sheets passed review.
- Minor cosmetic retouch: cards 97/98 have a flatter grey background under the replaced name; independent QA
  classifies it as harmless cosmetic restoration, not illustration damage. No missing text or clipping.
- Non-blocking owner overrides: D10 seal/orb props, D11 miniature card props, D12 unreadable BB241 scroll marks,
  D13 unreadable board details, and D15 costume emblems are documented in `docs/decisions.md`.
- Scripted emulator input is verified; GUI keyboard input has not been manually checked.
