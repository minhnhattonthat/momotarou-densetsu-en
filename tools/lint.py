"""Text lint over the whole script (check.py runs it; exit 1 on any error).

    python -X utf8 tools/lint.py

Per non-data string: the batch checks (tools/batches.py problems: printable ASCII, control codes JP == EN,
{wait} pages, ordinal suffix, box width and line count, glossary names and honorifics), plus every copy of a JP text
holds the same English, no Japanese left in any `en`, and no `en` missing unless listed in script/keep_jp.txt.
"""
import sys

import batches

KEEP = batches.ROOT / 'script/keep_jp.txt'


def validate(ds, gl, ok, keep=()):
    """Validate all source entries, independently of translation-batch selection.

    Unauthored control-only and printable-ASCII sources deliberately retain their original bytes.
    This classification does not exempt an authored English field from any check.
    """
    errs, seen, copies = [], set(), {}
    avoid = [r for r in gl if r[2]]
    reviewed = {}
    for _, doc in ds:
        for s in doc['strings']:
            if s['id'] in ok:
                reviewed.setdefault((s.get('jp'), s.get('en')), set()).update(ok[s['id']])
    for _, doc in ds:
        for s in doc['strings']:
            jp, en = s.get('jp', ''), s.get('en', '')
            if 'data' in s or not (jp or en):
                continue
            sid = s['id']
            plain = batches.TOKEN.sub('', jp)
            unchanged = all(' ' <= c <= '~' for c in plain)
            if not en:
                if not unchanged and sid not in keep:
                    errs.append(f'{sid}: no English (add it, or list the id in script/keep_jp.txt with a reason)')
                continue
            copies.setdefault(jp, {}).setdefault(en, []).append(sid)
            box = batches.layout.box(sid, jp)
            exceptions = tuple(sorted(reviewed.get((jp, en), ())))
            # The money label is a single redrawn glyph replaced with literal ASCII, per engine.md.
            # Match both source and replacement exactly; any other token change must still fail.
            control_jp = en if (sid, jp, en) == ('FONT_6:556', '{sm_ryo}', 'ryo') else jp
            key = (jp, en, box, exceptions, control_jp)
            if key in seen:
                continue
            seen.add(key)
            if batches.JA.search(en):
                errs.append(f'{sid}: Japanese left in the English')
            errors = batches.problems(control_jp, en, box,
                                      avoid + [r for r in gl if not r[2] and r[0] in jp], exceptions)
            errs.extend(f'{sid}: {e}' for e in errors)
    for jp, variants in copies.items():
        if len(variants) > 1:
            errs.append(f'{next(iter(variants.values()))[0]}: copies of the same JP differ in English: {sorted(variants)}')
    return errs, len(seen)


def run():
    keep = {ln.split()[0] for ln in KEEP.read_text(encoding='utf-8').splitlines() if ln.strip()} if KEEP.exists() \
        else set()
    errs, count = validate(batches.docs(), batches.glossary(), batches.glossary_ok(), keep)
    for e in errs:
        print('ERROR', e)
    print(f'lint: {len(errs)} errors ({count} unique text/box checks)')
    return not errs


if __name__ == '__main__':
    sys.exit(0 if run() else 1)
