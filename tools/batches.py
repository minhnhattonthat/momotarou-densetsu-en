"""Translation batches (docs/translator-brief.md): split the untranslated script into work/tl/bNNN.tsv, check a
translator's work/tl/bNNN.out.tsv, merge checked batches into script/ `en`.

    python -X utf8 tools/batches.py split [--names] [--size 3500] [--only TABLE ...]   batches for untranslated JP
    python -X utf8 tools/batches.py check bNNN                              id set, codes, ASCII, layout, glossary
    python -X utf8 tools/batches.py merge bNNN ...                          check, then write en to every string
    python -X utf8 tools/batches.py terms bNNN ...                          (re)write build/terms_bNNN.txt

Each unique JP text is translated once (id = its first occurrence); merge writes the English to every string with the
same JP and the check fits it to the tightest box any of them is drawn in. Batch TSV: id, speaker, form (box),
limit, JP with in-page line breaks as ' / ' and pages as {wait}.
"""
import re
import sys
from collections import Counter
from pathlib import Path

import extract
import layout

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / 'work/tl'
ORDER = ['03FONT/FONT_7', '03FONT/FONT_6', '03FONT/FONT_5', '03FONT/FONT_10', '03FONT/FONT_11', 'exe/', '03FONT/SHOP',
         '30EV/EVTOP', '06CITY/', '06CITY01/', '06WMAP/', '06DAN01/', '07HMAP/', '07HMAP3/', '04HEX/', '13BTL/',
         '20BTL/', '21BTL/', '22BTL/', '23BTL/', '24BTL/', '30EV/']
JA = re.compile(r'[぀-ヿ㐀-鿿＀-￯〇～…・]')
TOKEN = re.compile(r'\{[^}]*\}')
FREE = {'{n}', '{wait}'}                       # layout tokens the English may place freely


def rank(rel):
    return next((i for i, p in enumerate(ORDER) if rel.startswith(p)), len(ORDER)), rel


def docs():
    paths = sorted((ROOT / 'script').rglob('*.json'), key=lambda p: rank(p.relative_to(ROOT / 'script').as_posix()))
    return [(p, extract.load(p)) for p in paths]


def units(ds=None):
    """{jp: {'id', 'ids', 'box', 'rel', 'en'}} for every unique JP text that needs English, in story order."""
    out = {}
    for p, doc in ds or docs():
        rel = p.relative_to(ROOT / 'script').as_posix()
        for s in doc['strings']:
            jp = s.get('jp')
            if not jp or 'data' in s or not JA.search(TOKEN.sub('', jp)):
                continue
            u = out.setdefault(jp, {'id': s['id'], 'jp': jp, 'ids': [], 'box': None, 'rel': rel,
                                    'en': s.get('en', '')})
            u['ids'].append(s['id'])
            b = layout.box(s['id'], jp)
            if u['box'] is None or layout.budget(b, jp)[0] < layout.budget(u['box'], jp)[0]:
                u['box'] = b
    return out


def show_jp(jp):
    """JP for the batch file: pages by {wait}, in-page breaks ' / ', padding {n} dropped."""
    pages = []
    for seg in jp.split('{wait}'):
        seg = re.sub(r'^(\{n\})+|(\{n\})+$', '', seg)
        pages.append(seg.replace('{n}', ' / '))
    return ' {wait} '.join(pages).strip()


def read_tsv(path):
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():
            rows.append(line.split('\t'))
    return rows


def batch_ids():
    return {r[0] for p in TL.glob('b[0-9][0-9][0-9].tsv') for r in read_tsv(p)}


def split(argv):
    only = argv[argv.index('--only') + 1:] if '--only' in argv else None
    size = int(argv[argv.index('--size') + 1]) if '--size' in argv else 3500
    TL.mkdir(parents=True, exist_ok=True)
    taken = batch_ids()
    n = max([int(p.stem[1:4]) for p in TL.glob('b[0-9][0-9][0-9].tsv')] or [0])
    names = '--names' in argv          # wave 0: one-line names and labels of the FONT tables (they seed the glossary)
    todo = [u for u in units().values() if not u['en'] and u['id'] not in taken
            and (only is None or u['id'].split(':')[0] in only)
            and (not names or u['id'].startswith('FONT_') and u['box'] not in ('dlg', 'side'))]
    batches, cur, chars, group = [], [], 0, None
    for u in todo:
        g = u['rel'].split('/')[0]
        c = len(TOKEN.sub('', u['jp']))
        if cur and (chars + c > size or len(cur) >= 150 or g != group):
            batches.append(cur)
            cur, chars = [], 0
        cur.append(u)
        chars += c
        group = g
    if cur:
        batches.append(cur)
    for b in batches:
        n += 1
        name = f'b{n:03d}'
        path = TL / f'{name}.tsv'
        assert not path.exists(), path
        lines = []
        for u in b:
            px, nl = layout.budget(u['box'], u['jp'])
            lines.append(f"{u['id']}\t\t{u['box']}\t{px}px x{nl}\t{show_jp(u['jp'])}")
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
        terms([name])
        print(name, len(b), 'entries', sum(len(TOKEN.sub('', u['jp'])) for u in b), 'chars', b[0]['rel'])


def glossary():
    """[(jp, en, avoid list)] from glossary.md tables, plus the name tables' English (items, techniques, monsters,
    places, party: binding once translated)."""
    rows = []
    for line in (ROOT / 'glossary.md').read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if line.startswith('|') and len(cells) >= 2 and JA.search(cells[0]) and cells[1]:
            avoid = [a.strip() for a in cells[4].split(',') if a.strip()] if len(cells) > 4 else []
            jps = [re.sub(r'\(.*?\)', '', j).strip() for j in cells[0].split('/')]
            ens = [e.strip() for e in cells[1].split('/')]
            for k, j in enumerate(jps):          # 'A / B' | 'a / b' pair up; else every JP form -> the first EN
                rows.append((j, ens[k] if len(ens) == len(jps) else ens[0], avoid))
    names = {'item', 'tech', 'monster', 'party', 'place'}
    for p, doc in docs():
        if p.stem in ('FONT_5', 'FONT_6', 'FONT_7'):
            for s in doc['strings']:
                if s.get('en') and s.get('jp') and layout.box(s['id'], s['jp']) in names:
                    rows.append((s['jp'], s['en'], []))
    return rows


def kind(c):
    if '぀' <= c <= 'ゟ':
        return 'h'
    if '゠' <= c <= 'ヿ':
        return 'k'
    if '一' <= c <= '鿿' or c == '々':
        return 'c'
    return 'o'


def has_term(jp, term):
    """term occurs in jp as a whole run (not inside a longer run of the same script)."""
    if len(term) < 2:
        return False
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def terms(names):
    gl = glossary()
    (ROOT / 'build').mkdir(exist_ok=True)
    for name in names:
        jps = ' '.join(r[4] for r in read_tsv(TL / f'{name}.tsv'))
        rows = sorted({(j, e) for j, e, _ in gl if has_term(jps, j)})
        (ROOT / f'build/terms_{name}.txt').write_text(
            ''.join(f'{j}\t{e}\n' for j, e in rows) or '(no glossary terms in this batch)\n', encoding='utf-8',
            newline='\n')


def problems(jp, en, box, gl):
    errs, warns = [], []
    if not en.strip():
        return ['empty English'], warns
    bad = sorted({c for c in TOKEN.sub('', en) if not ' ' <= c <= '~' or c in '{}'})
    if bad:
        errs.append(f'characters outside printable ASCII or stray braces: {bad}')
    if '\\u' in en or '\\n' in en:
        errs.append('escape sequence in the English (write the character, or {n} for a forced break)')
    a = Counter(t for t in TOKEN.findall(jp) if t not in FREE)
    b = Counter(t for t in TOKEN.findall(en) if t not in FREE)
    if a != b:
        errs.append(f'control codes differ: JP {dict(a)} EN {dict(b)}')
    if en.count('{wait}') < jp.count('{wait}'):
        errs.append(f'{{wait}} count {en.count("{wait}")} < JP {jp.count("{wait}")} (keep every page break)')
    if re.sub(r'(\{n\}|\s)+$', '', jp).endswith('{wait}') != re.sub(r'(\{n\}|\s)+$', '', en).endswith('{wait}'):
        errs.append('the JP ends with {wait} and the English does not, or the reverse')
    if re.search(r'\{(num|str|name|gold)\}(st|nd|rd|th)\b', en):
        errs.append('ordinal suffix glued to a variable (write "No. {num}")')
    _, lp = layout.layout(en, jp, box)
    errs += lp
    for j, e, avoid in gl:
        for a_ in avoid:
            if re.search(rf'\b{re.escape(a_)}\b', en):
                errs.append(f'glossary: "{a_}" is an avoided spelling of {j} -> {e}')
        if has_term(TOKEN.sub('', jp), j) and e.lower() not in en.lower():
            warns.append(f'glossary: {j} -> {e} not in the English')
    return errs, warns


def check(name, quiet=False):
    rows = read_tsv(TL / f'{name}.tsv')
    out_path = TL / f'{name}.out.tsv'
    if not out_path.exists():
        print(f'{name}: no {out_path.name}')
        return None
    us = {u['id']: u for u in units().values()}
    gl = glossary()
    got, errs = {}, []
    for k, line in enumerate(out_path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        if line.count('\t') != 1:
            errs.append(f'line {k}: need exactly one tab (id<TAB>English)')
            continue
        i, en = line.split('\t')
        if i in got:
            errs.append(f'{i}: duplicate id')
        got[i] = en
    want = [r[0] for r in rows]
    for i in sorted(set(want) - set(got)):
        errs.append(f'{i}: missing')
    for i in sorted(set(got) - set(want)):
        errs.append(f'{i}: not in this batch')
    nwarn = 0
    for i in want:
        if i in got and i in us:
            e, w = problems(us[i]['jp'], got[i], us[i]['box'], gl)
            errs += [f'{i}: {x}' for x in e]
            if not quiet:
                for x in w:
                    print(f'WARN {i}: {x}')
            nwarn += len(w)
    for e in errs:
        print('ERROR', e)
    print(f'{name}: {"OK" if not errs else f"{len(errs)} errors"} ({len(got)} entries, {nwarn} warnings)')
    return got if not errs else None


def merge(names):
    trans = {}
    for name in names:
        got = check(name, quiet=True)
        if got is None:
            sys.exit(f'{name} failed its check; not merged')
        trans.update(got)
    by_jp = {u['jp']: trans[u['id']] for u in units().values() if u['id'] in trans}
    files = 0
    for p, doc in docs():
        changed = False
        for s in doc['strings']:
            en = by_jp.get(s.get('jp'))
            if en is not None and 'data' not in s and s.get('en') != en:
                s['en'] = en
                changed = True
        if changed:
            p.write_text(extract.dump(doc), encoding='utf-8', newline='\n')
            files += 1
    print(f'merged {len(trans)} entries into {files} files')


def main(argv):
    cmd, rest = argv[0], argv[1:]
    if cmd == 'split':
        split(rest)
    elif cmd == 'check':
        ok = all(check(n) is not None for n in rest)
        sys.exit(0 if ok else 1)
    elif cmd == 'merge':
        merge(rest)
    elif cmd == 'terms':
        terms(rest)
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
