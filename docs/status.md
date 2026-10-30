# Status

Updated 2026-10-31. History is in git; the current evidence below supersedes older failed or partial QA rounds.

- **Phase:** 8 complete; next is phase 9 (release preparation). Phase-7 review fixes are committed and pushed in
  7899460; runtime joins/town graphics in 7f21653; museum/minigame graphics and repeatable routes in 7969510.
  No release has been published. All five current visual gates pass, including every final album page.
- **Latest build:** `build/momotarou_en.bin`, 143,902,416 bytes, SHA-1
  `e9be11b91158238ad63548489af9ba970fa3d639`. Fresh boot smoke passes in `work/qa/final_smoke`.
  Full check passed 48 tests and 6,027 lint checks with zero errors; the additional disc regression test also
  passes (49 tests now present; the commit hook will run the complete set).
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

## Current visual gates

Run the skill's `scripts/qa_gate.py check MANIFEST VERDICT_DIR`. All proofs use English builds with the relevant
changes; later card-only edits do not change the tour/sign textures.

| Manifest | Verdict directory | State |
|---|---|---|
| `work/qa/phase8_cardsfix/tour_manifest.tsv` | `work/qa/phase8_cardsfix/tour_verdicts` | 83 sheets, green |
| `work/qa/graphics_final/manifest.tsv` | `work/qa/graphics_final/verdicts` | 13 sheets, green |
| `work/qa/boards_final/manifest.tsv` | `work/qa/boards_final/verdicts` | 4 sheets, green |
| `work/qa/cards_final_pass/assets_manifest.tsv` | `work/qa/cards_final_pass/asset_verdicts` | 33 sheets / 297 pairs, green |
| `work/qa/cards_final_pass/manifest.tsv` | `work/qa/cards_final_pass/verdicts` | 33 sheets / 99 pages, green |

Older manifests under `work/qa/v0`, `cards_final`, `cards_round4` and other repair rounds are historical failed
or superseded evidence. Phase 9 should validate the explicit current set above, not silently accept old greens
or treat a failed intermediate build as the release candidate.

## Next

Phase 9 needs the chapter story-pass gate, `docs/polish.md`, a final-build unintended-Japanese scan, and a release script that checks the
current gates, creates/applies/verifies the patch and packages patch + README. `tools/release.py` does not yet
exist despite the command placeholder in AGENTS.md. Never publish a release or change repository visibility.

## Open issues and defaults

- No known unresolved runtime defect; all final album, tour and supplemental sheets passed review.
- Minor cosmetic retouch: cards 97/98 have a flatter grey background under the replaced name; independent QA
  classifies it as harmless cosmetic restoration, not illustration damage. No missing text or clipping.
- Non-blocking owner overrides: D10 seal/orb props, D11 miniature card props, D12 unreadable BB241 scroll marks,
  and D13 unreadable board details are documented in `docs/decisions.md`.
- Scripted emulator input is verified; GUI keyboard input has not been manually checked.
