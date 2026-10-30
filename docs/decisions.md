# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-10-30 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-10-30 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. Owner's standing answer. |
| D3 | 2026-10-30 | Credits | stay Japanese, translate | English. Owner's standing answer. |
| D4 | 2026-10-30 | Abbreviations | engine work first (default), abbreviate | Engine work first (skill default; owner didn't override). |
| D5 | 2026-10-30 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); keep the original Japanese logo only if no official English version exists. |
| D6 | 2026-10-30 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through checkpoints, report at the end. |
| D7 | 2026-10-30 | Existing saves / memory cards | user supplies, none | None provided; build the debug tool (phase 2) as usual. |
| D8 | 2026-10-30 | Pushing / releases | ask each time, pre-approved | Commit and push to main at each phase end; never `gh release create`, never change repo visibility. Run ends at a built, verified release zip. |
| D10 | 2026-10-30 | Kanji on props in battle effects (agent default under D5/D6, owner may override) | letter them, keep | Keep the 封 on the seal talismans (ofuda) and the circled 技 orb: the kanji is part of the drawn object, like the 酒 on the gourd; the effect text names the status. |
| D9 | 2026-10-30 | Card stat labels (agent default under D6, owner may override) | full words (Attack/Defense/Speed) in a tiny font, abbreviate | HP / Atk / Def / Spd: the game draws each value ~29 px after the label's left edge, so full words collide with the numbers (seen in-game); flagged abbreviation per D4. D5 logo: kept Japanese (no official English logo). |
