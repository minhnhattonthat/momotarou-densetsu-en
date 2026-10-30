# Visual-QA reviewer brief - Momotarou Densetsu (PS1) English

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- Each sheet shows the English build's shot; where the original's shot of the same scene exists it is beside it
  (left = English, right = Japanese original). `glossary.md` has the names.

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 "$(python tools/skill.py)/scripts/sheet.py" SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png`
  (scratch = your temp dir, not the repo) and read that.
- When something looks wrong, compare with the Japanese half. If the original shows the same thing, it is the
  game's own behaviour: `ok`, with a note.

## Judge
An `issue` is any of:
- Japanese still visible (text or lettering in graphics: signs, banners, labels);
- text overflowing a box, clipped by a frame, or running off screen;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok`:
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp; a scene shot at a different moment than the original's;
- anything identical in the original's half;
- the title logo 桃太郎伝説 (on the title screen, the memory-card stamp and the card-album cover) stays Japanese
  by the owner's decision (docs/decisions.md D5);
- numbers drawn in the game's bold 8x12 digits beside the narrower English letters;
- card stat labels abbreviated HP / Atk / Def / Spd (decision D9); sign plates in small pixel capitals (INN, TEA,
  DOC, ARMOR, SHOES, ARMS, BANK, SMITH, GROCER, SHOP, SEER);
- crests and pictures without writing (the purple banners' crest, the 酒 on Shuten-doji's gourd is a picture
  detail: flag it only if you are sure it is a readable word in the scene);
- props kept by decision: the 封 on the battle seal talismans (ofuda) and the circled 技 orb;
- the status-summary time reads "Day 1 00:00:14" (smaller "Day" beside the bold digits is intended).

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which part of the screen, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
