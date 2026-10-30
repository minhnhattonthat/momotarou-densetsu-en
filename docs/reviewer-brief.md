# Translation reviewer brief - Momotarou Densetsu (PS1)

You review one or more batches of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, control codes, encodable characters, width, page count) is already enforced by
`tools/batches.py check` - judge translation quality. Return the report as your final message: subagents cannot
write files, so the controller saves it.

## Inputs (paths in your dispatch)
- Pairs file `work/tl/review/<name>.txt`: every translated entry as `>> id | JP` / `   EN` in game order. `{wait}` is
  a page break, ` / ` a JP line break; the English has no line breaks (the build wraps it). Read ALL of it, in passes
  if large.
- `glossary.md` (rulings at the top), `docs/style-reference.md` (voices, tics), `docs/synopsis.md` (who is who, late
  reveals), and for names the batch's `build/terms_<batch>.txt`.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names and terms exactly (a one-letter slip is what players notice); honorific relationships
  stable within a scene; voice and animal tics as in the style reference.
- Things players caught that reviewers missed: jokes, puns and mangled proverbs losing their punch; ordinal suffix
  after a variable ("{num}th"); a/an before {str}; abbreviated names or terms; awkward stock phrases ("... GET!").
- Late reveals leaked early (docs/synopsis.md section 4).
- Naturalness: would a reader stumble? Register per scene.

## Report
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation, dead joke)
#### Minor (style - deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Per batch: Approved | Needs fixes - one sentence why.
