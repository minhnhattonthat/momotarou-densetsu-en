"""Layout: authored English -> engine text (docs/re/windows.md budgets, docs/re/text.md page structure).

Authored `en` carries no {n} line breaks except forced ones; pages are split by {wait} as in the Japanese. layout()
word-wraps each page to the box width and pads it with {n} exactly as the Japanese page it replaces: a page is
`{n}`*lead + lines joined by {n} + `{n}` up to the JP page's line slots (3 in a dialogue box), so every page clears
the same way the original did. Inside a "quote", continuation lines get a 1-space indent (the JP indents after 「).

    python -X utf8 tools/layout.py "text" [--box dlg|side|item|...]   dry run: lines with their px widths
"""
import re
import sys

import engine

WIDTH = engine.widths()
TOKEN = re.compile(r'(\{[^}]*\})')
# px a control token takes when drawn: a {str} run is the longest monster name (114 px; items 103, party 44)
TOKEN_W = {'{str}': 114, '{num}': 40, '{gold}': 56, '{name}': 64}

# (px, lines) per box variant, docs/re/windows.md; 'label' = unmeasured short label: budget = the JP's own width
BOX = {'dlg': (234, 3), 'side': (134, 3), 'item': (103, 1), 'tech': (85, 1), 'monster': (114, 1), 'cmd': (52, 1),
       'party': (44, 1), 'shop': (58, 1), 'namecmd': (56, 1), 'staff': (250, 3), 'place': (110, 1),
       'status': (40, 1), 'stat': (72, 1), 'slot': (20, 1), 'label': (None, 1)}

FONT_6 = [(0, 31, 'tech'), (32, 60, 'side'), (61, 301, 'item'), (302, 526, 'side'), (536, 550, 'party'),
          (559, 573, 'status'), (574, 576, 'stat'), (584, 591, 'cmd'), (606, 630, 'place'), (651, 654, 'shop'),
          (655, 655, 'item'), (656, 658, 'slot'), (663, 663, 'stat')]
FONT_7 = [(3, 9, 'monster'),(10, 16, 'cmd'), (24, 25, 'dlg'), (26, 34, 'cmd'), (35, 271, 'monster')]
FONT_5 = [(0, 91, 'place'), (94, 98, 'namecmd')]
RANGES = {'FONT_6': FONT_6, 'FONT_7': FONT_7, 'FONT_5': FONT_5}


def box(sid, jp):
    """Box variant name for string id 'TABLE:index' (overlays: 'TABLE:hexoff')."""
    table, _, idx = sid.partition(':')
    for lo, hi, name in RANGES.get(table, []):
        if idx.isdigit() and lo <= int(idx) <= hi:
            return name
    if table == 'END02_14':
        return 'staff'
    if '{n}' in jp or '{wait}' in jp or '「' in jp or table not in RANGES and table != 'SLPS_017':
        return 'dlg'
    return 'label'


def budget(name, jp):
    px, lines = BOX[name]
    return (px if px is not None else max(40, jp_width(jp))), lines


def jp_width(jp):
    """Pixel width of the widest JP line (13 px per glyph)."""
    return max(13 * len(TOKEN.sub('', line)) for line in re.split(r'\{n\}|\{wait\}', jp))


def width(text):
    """px of one line of English, control tokens counted at TOKEN_W (a run of {str} counts once)."""
    px, prev = 0, None
    for t in TOKEN.split(text):
        if not t:
            continue
        if t.startswith('{'):
            if not (t == '{str}' and prev == '{str}'):
                px += TOKEN_W.get(t, 0)
            prev = t
            continue
        for c in t:
            px += WIDTH[ord(c) - engine.FIRST] if engine.FIRST <= ord(c) <= engine.LAST else 13
        prev = None
    return max(0, px - 1)


def wrap(text, px):
    """Greedy word wrap of one page; forced breaks at {n}; continuation lines inside a quote get a 1-space indent."""
    lines = []
    for para in text.split('{n}'):
        words, line = para.split(' '), ''
        for w in words:
            cand = f'{line} {w}' if line else w
            if line and width(cand) > px:
                lines.append(line)
                quoted = ''.join(lines).count('"') % 2 == 1
                line = (' ' if quoted else '') + w
            else:
                line = cand
        lines.append(line)
    return lines


def pages(jp):
    """[(lead, slots)] per {wait}-separated JP page: leading {n} count, line slots (lines + trailing {n})."""
    out = []
    for seg in jp.split('{wait}'):
        m = re.match(r'^((?:\{n\})*)(.*?)((?:\{n\})*)$', seg)
        body = m.group(2)
        out.append((len(m.group(1)) // 3, (body.count('{n}') + 1 if body else 0) + len(m.group(3)) // 3))
    return out


def layout(en, jp, name=None):
    """(engine text, [problems]) for authored en replacing jp."""
    name = name or 'dlg'
    px, max_lines = budget(name, jp)
    jpp, segs = pages(jp), en.split('{wait}')
    # English page i takes JP page i's template, the last takes the JP's last, extra pages a standard mid page
    tmpl = [jpp[-1] if i == len(segs) - 1 else jpp[i] if i < len(jpp) - 1 else (1, 3) for i in range(len(segs))]
    out, problems = [], []
    for i, (seg, (lead, slots)) in enumerate(zip(segs, tmpl)):
        seg = seg.strip(' ')
        seg = re.sub(r'^(\{n\})+|(\{n\})+$', '', seg)
        if not seg:
            if slots:
                problems.append(f'page {i + 1} is empty but the JP page has text')
            out.append('{n}' * (lead + slots))
            continue
        if not slots:
            problems.append(f'page {i + 1}: the JP has no text here (string ends with {{wait}}?)')
        lines = wrap(seg, px)
        cap = max(max_lines, slots if name == 'dlg' else 0)
        for ln in lines:
            if width(ln) > px:
                problems.append(f'line too wide: {width(ln)} > {px} px: {ln!r}')
        if len(lines) > cap:
            problems.append(f'page {i + 1} has {len(lines)} lines > {cap} (split the page with {{wait}} or cut)')
        out.append('{n}' * lead + '{n}'.join(lines) + '{n}' * max(0, slots - len(lines)))
    return '{wait}'.join(out), problems


def main(argv):
    name = argv[argv.index('--box') + 1] if '--box' in argv else 'dlg'
    text = argv[0]
    px, n = budget(name, '')
    jp = '{n}'.join(['x'] * n)
    for k, seg in enumerate(text.split('{wait}')):
        print(f'-- page {k + 1} ({name}: {px} px x {n})')
        for ln in wrap(seg.strip(), px):
            print(f'{width(ln):4d} {"!" if width(ln) > px else " "} {ln}')
    print('problems:', layout(text, '{wait}'.join([jp] * len(text.split('{wait}'))), name)[1] or 'none')


if __name__ == '__main__':
    main(sys.argv[1:])
