# Translator brief - Momotarou Densetsu (PS1, Hudson 1996)

You translate part of the Japanese script of Momotarou Densetsu into English for a fan patch: a comic, all-ages RPG
retelling of the Momotaro folk tale (Momotaro, with Dog, Monkey and Pheasant, Kintaro, Urashima and Yashahime,
fights the oni). Work only on the batches named in your dispatch, one at a time in the order given, each to a passing
check before the next. Do all translation yourself; do not dispatch subagents.

## Read first
1. `docs/style-reference.md` - voices, animal tics and approved example pairs. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (`glossary.md` has the rulings and full tables).
3. `docs/synopsis.md` (when present) - plot, who is who, late reveals. Don't give a reveal away early.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`. form is the box the text is drawn in (dlg = 3-line dialogue box,
side = 3-line menu message box, item/tech/monster/party/place/cmd/shop/status/stat/slot/label = one-line name or
label, staff = staff roll). limit is `<px> x<lines>` per page. In the Japanese, ` / ` is a line break inside a page
and `{wait}` a page break (button press). Lines are in game order: use neighbours for context.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (never a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain printable ASCII only: straight quotes, `...`, `--`;
no tabs inside the English, no Japanese or fullwidth characters, no `\uXXXX`, no `\n`.
- **Do not write line breaks.** The build word-wraps each page to the box. Write each page as one run of text and
  separate pages with `{wait}` exactly where the JP has one. You may add extra `{wait}` page breaks when English
  runs longer than 3 lines (about 130 characters) in a dialogue page; never remove one. Where the JP ends with
  `{wait}`, the English ends with `{wait}` too.
- Copy every other control code exactly, same count: `{str}` (an inserted name, item or monster: `{str}{str}` is one
  name in two parts, keep them together), `{num}` (a number), `{col4}...{col0}` (highlight colour around a name:
  keep it around the English of the same words), `{c19}`, `{c28}`, `{name}`, `{gold}`.
- Forced break: only for lists or verse where a break must fall, write `{n}` (rare; never to fit text).
- One-line forms must fit their px on one line. Rough widths: lowercase ~5 px, capitals ~7 px, space 4 px; a 234 px
  dialogue line holds about 45 characters, 3 lines per page. Dry run: `python -X utf8 tools/layout.py "text" --box item`.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every ERROR until it prints OK.
A glossary term from the JP missing in your English, or a character's honorific dropped (桃太郎さん without
"Momotaro-san"), is an ERROR. When the JP word is not the glossary sense (a pun, a tic, a common noun like お地蔵さま),
keep your English and report `GLOSSARY: id term reason`; the controller reviews it and lists it in
`script/glossary_ok.txt`.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay, puns and parodies so the joke still lands (no translator notes).
- Names and terms exactly as in the glossary and terms file. Never abbreviate to fit; if a line can't fit its limit
  without losing meaning, keep the meaning, make the check pass by rephrasing, and report `LONG: id`.
- Honorifics kept and hyphenated (Momotaro-san, -sama, -kun, -dono); Western name order. Punctuation: 「」 -> "...",
  『』 -> '...', … -> `...`, ！？ -> `?!`.
- Placeholders: no suffix glued to a variable (write "No. {num}" not "{num}th"); no a/an right before {str} (write
  "Momotaro got {str}!" or "the {str}"); battle {str}{str} can be a party member or a monster: write lines that work
  for both ("{str}{str} attacks!", "{str}{str} was poisoned!"). {num} before a counted noun: "{num} ryo",
  "{num} HP"; plural-safe forms ("{num} hit(s)" is not allowed: rephrase, e.g. "hit {num} times" is fine since the
  game never shows 1 there; if it can be 1, use "Hits: {num}").
- Item, technique and monster names (wave 0): English names that say what the thing is, in title case, within the
  px limit; keep folklore names in romaji where English has no word (Kintan, Ryugu). Same JP word -> same English
  word across a family (鉄の = Iron, 銀の = Silver, 金の = Gold; 勇気/希望/正義/愛 = Courage/Hope/Justice/Love).
- Stock phrases: no "GET!" calques; "Obtained X!" / "Momotaro got X!".

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
