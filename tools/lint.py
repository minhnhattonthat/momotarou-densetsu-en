"""Text lint over the whole script (check.py runs it; exit 1 on any error).

    python -X utf8 tools/lint.py

Per string with Japanese: the batch checks (tools/batches.py problems: printable ASCII, control codes JP == EN,
{wait} pages, ordinal suffix, box width and line count, glossary names and honorifics), plus every copy of a JP text
holds the same English, no Japanese left in any `en`, and no `en` missing unless listed in script/keep_jp.txt.
"""
import sys

import batches

KEEP = batches.ROOT / 'script/keep_jp.txt'


def run():
    keep = {ln.split()[0] for ln in KEEP.read_text(encoding='utf-8').splitlines() if ln.strip()} if KEEP.exists() \
        else set()
    ds = batches.docs()
    us = batches.units(ds)
    by_id = {s['id']: s for _, d in ds for s in d['strings']}
    gl = batches.glossary()
    avoid = [r for r in gl if r[2]]
    ok = batches.glossary_ok()
    errs = []
    for u in us.values():
        ens = {by_id[i].get('en', '') for i in u['ids']}
        if ens == {''}:
            if u['id'] not in keep:
                errs.append(f"{u['id']}: no English (add it, or list the id in script/keep_jp.txt with a reason)")
            continue
        if len(ens) > 1:
            errs.append(f"{u['id']}: copies of the same JP differ in English: {sorted(ens)}")
        for en in ens:
            if batches.JA.search(en):
                errs.append(f"{u['id']}: Japanese left in the English")
            # only the rows that can fire: a JP term in this text, or an avoided spelling (same result, ~20x faster)
            e = batches.problems(u['jp'], en, u['box'], avoid + [r for r in gl if not r[2] and r[0] in u['jp']],
                                 ok.get(u['id'], ()))
            errs += [f"{u['id']}: {x}" for x in e]
    for e in errs:
        print('ERROR', e)
    print(f'lint: {len(errs)} errors ({len(us)} unique texts)')
    return not errs


if __name__ == '__main__':
    sys.exit(0 if run() else 1)
