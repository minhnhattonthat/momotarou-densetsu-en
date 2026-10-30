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

# (px, lines) per box variant, docs/re/windows.md. 'label' = a short label with no measured consumer: budget 0, so
# any English fails the lint until its window is measured. 'unused' = no consumer exists (windows.md §Unused labels).
BOX = {'dlg': (234, 3), 'side': (134, 3), 'item': (103, 1), 'tech': (85, 1), 'monster': (114, 1), 'cmd': (52, 1),
       'party': (44, 1), 'shop': (58, 1), 'namecmd': (56, 1), 'staff': (250, 3), 'place': (110, 1),
       'status': (40, 1), 'stat': (72, 1), 'slot': (20, 1), 'label': (0, 1), 'unused': (10 ** 6, 1),
       'settings': (106, 1), 'settingchoice': (86, 1), 'treasure': (78, 1), 'summary': (111, 1),
       'oniunit': (18, 1), 'cardunit': (34, 1), 'moneyunit': (17, 1), 'namemode': (57, 1),
       'itemlist': (114, 1), 'equipslot': (103, 1), 'popup': (58, 1), 'op': (9, 1), 'skill': (74, 1), 'townwarp': (66, 1),
       'floor': (34, 1), 'strslot': (114, 1), 'soundtest': (242, 1), 'bankmenu': (42, 1), 'bankmove': (66, 1),
       'bankbalance': (80, 1), 'clinic': (50, 1), 'fragment': (234, 1),
       'cardname': (134, 1), 'floortravel': (122, 1), 'floorguide': (74, 1),
       'musicname': (194, 1), 'puzzlechoice': (48, 1), 'savefile': (106, 1),
       'savelevel': (22, 1), 'debugdest': (122, 1), 'difficulty': (70, 1),
       'mgcharacter': (58, 1), 'darumatitle': (90, 1), 'fukutitle': (70, 1), 'points': (30, 1),
       'proverb': (234, 1), 'carddlg': (234, 3), 'proverbdlg': (234, 3), 'scoretotal': (16, 1),
       'choices': (234, 4)}

UNUSED = {'FONT_6': [(579, 579), (595, 605), (661, 662), (681, 681), (683, 686), (796, 796)],
          'FONT_7': [(19, 23)], 'FONT_5': [(93, 93)], 'FONT_10': [(122, 154)],
          'YUMI2_10': [(3, 4)]}
# first match wins: a string drawn in several windows sits under its narrowest one, listed before its range
FONT_6 = [(588, 588, 'bankmenu'), (654, 654, 'bankmenu'),
          (0, 31, 'tech'), (32, 60, 'side'), (61, 301, 'item'), (302, 526, 'side'), (536, 550, 'party'),
          (559, 573, 'status'), (574, 576, 'stat'), (584, 591, 'cmd'), (606, 630, 'place'), (651, 654, 'shop'),
          (655, 655, 'item'), (656, 658, 'slot'), (663, 663, 'stat'), (556, 556, 'moneyunit'),
          (577, 577, 'treasure'), (578, 578, 'summary'), (580, 581, 'summary'), (582, 582, 'oniunit'),
          (583, 583, 'cardunit'), (592, 592, 'cmd'), (786, 786, 'settings'), (787, 788, 'settingchoice'),
          (789, 789, 'settings'), (790, 791, 'settingchoice'), (792, 792, 'settings'), (793, 795, 'settingchoice'),
          (530, 530, 'soundtest'), (593, 593, 'equipslot'), (594, 594, 'itemlist'), (646, 647, 'popup'),
          (649, 650, 'popup'), (659, 660, 'op'), (682, 682, 'popup'), (693, 698, 'skill'), (700, 707, 'townwarp'),
          (733, 740, 'strslot'), (747, 748, 'popup'), (799, 803, 'floor')]
FONT_7 = [(3, 9, 'monster'),(10, 16, 'cmd'), (24, 25, 'dlg'), (26, 34, 'cmd'), (35, 271, 'monster')]
FONT_5 = [(0, 91, 'place'), (94, 98, 'namecmd')]
SHOP = [(259, 260, 'bankmenu'), (261, 262, 'bankmove'), (263, 263, 'bankbalance'), (342, 343, 'clinic'),
        (344, 346, 'strslot')]
RANGES = {'FONT_6': FONT_6, 'FONT_7': FONT_7, 'FONT_5': FONT_5, 'SHOP': SHOP}
# Non-FONT consumers traced in docs/re/windows.md. No table-wide dialogue default:
# a single-line string outside these ranges must be classified before it can pass.
RANGES.update({
    'FONT_10': [(28, 30, 'fragment'), (79, 99, 'strslot'), (102, 102, 'strslot'), (117, 117, 'cmd')],
    'FONT_11': [(i, i, 'fragment') for i in (47, 48, 50, 51, 53, 54, 59, 61, 62, 71, 72, 74, 75,
                                               77, 78, 80, 81, 83, 84, 86, 87, 89, 90, 100, 101,
                                               103, 104, 106, 107, 109, 110)],
    'HMAP8500_18': [(82, 84, 'popup'), (85, 381, 'cardname')],
    'SMAP01_33': [(41, 43, 'popup'), (53, 70, 'debugdest')],
    'SMAP16_37': [(130, 133, 'cmd'), (134, 137, 'settings')],
    'HMAP8300_18': [(38, 41, 'settingchoice')],
    'DMAP03_92': [(27, 36, 'puzzlechoice')],
    'HMAP26_66': [(163, 164, 'floortravel'), (215, 270, 'musicname')],
    'HMAP2606_66': [(45, 85, 'fragment'), (287, 288, 'floortravel')],
    'HMAP2607_66': [(21, 25, 'floorguide')],
    'MECD_1': [(0, 0, 'savelevel'), (1, 18, 'savefile')],
    'DARUMA_11': [(15, 17, 'difficulty'), (18, 20, 'mgcharacter'), (21, 21, 'darumatitle')],
    'FUKU_11': [(6, 8, 'difficulty'), (9, 11, 'mgcharacter'), (12, 12, 'fukutitle'), (44, 44, 'points')],
    'MOGURA_11': [(16, 17, 'popup')],
    'YUMI2_10': [(2, 2, 'points'), (9, 9, 'op'), (10, 10, 'scoretotal'), (11, 11, 'op')],
    'BM008_1': [(278, 278, 'dlg')], 'BM028_1': [(222, 233, 'fragment')],
})


def box(sid, jp):
    """Box variant name for string id 'TABLE:index' (overlays: 'TABLE:hexoff')."""
    table, _, idx = sid.partition(':')
    if table == 'HMAP2606_65':
        return 'proverb'
    if table == 'BM008_1' and jp.count('{n}') == 3 and '{wait}' not in jp:
        return 'choices'  # four independent answers in the literary/kanji quiz
    if sid in ('SLPS_017:d44f4', 'SLPS_017:d4500', 'SLPS_017:d450c'):
        return 'namemode'
    if idx.isdigit() and any(lo <= int(idx) <= hi for lo, hi in UNUSED.get(table, [])):
        return 'unused'
    for lo, hi, name in RANGES.get(table, []):
        if idx.isdigit() and lo <= int(idx) <= hi:
            return name
    if table == 'END02_14':
        return 'staff'
    if sid == 'HMAP2606_66:030':
        return 'proverbdlg'
    if '{n}' in jp or '{wait}' in jp or '「' in jp:
        return 'carddlg' if table == 'HMAP8500_18' else 'dlg'
    return 'label'


def budget(name, jp):
    return BOX[name]


def width(text, str_width=114):
    """px of one line of English, control tokens counted at TOKEN_W (a run of {str} counts once)."""
    px, prev = 0, None
    for t in TOKEN.split(text):
        if not t:
            continue
        if t.startswith('{'):
            if not (t == '{str}' and prev == '{str}'):
                px += str_width if t == '{str}' else TOKEN_W.get(t, 0)
            prev = t
            continue
        for c in t:
            px += WIDTH[ord(c) - engine.FIRST] if engine.FIRST <= ord(c) <= engine.LAST else 13
        prev = None
    return max(0, px - 1)


def wrap(text, px, str_width=114):
    """Greedy word wrap of one page; forced breaks at {n}; continuation lines inside a quote get a 1-space indent."""
    lines = []
    for para in text.split('{n}'):
        words, line, first = para.split(' '), '', len(lines)
        for w in words:
            cand = f'{line} {w}' if line else w
            if line and width(cand, str_width) > px:
                lines.append(line)
                quoted = ''.join(lines).count('"') % 2 == 1
                line = (' ' if quoted else '') + w
            else:
                line = cand
        lines.append(line)
        # no lone word on a paragraph's last line: pull the line above's last word down when it fits
        if len(lines) - first >= 2 and (' ' not in lines[-1].strip()
                                       or len(TOKEN.sub('', lines[-1]).strip(' "')) < 6):
            head, _, last = lines[-2].rpartition(' ')
            indent = lines[-1][:len(lines[-1]) - len(lines[-1].lstrip(' '))]
            moved = f'{indent}{last} {lines[-1].lstrip(" ")}'
            if ' ' in head.strip() and width(moved, str_width) <= px:
                lines[-2:] = [head, moved]
    return lines


def pages(jp):
    """[(lead, slots)] per {wait}-separated JP page: leading {n} count, line slots (lines + trailing {n})."""
    out = []
    for seg in jp.split('{wait}'):
        m = re.match(r'^((?:\{n\})*)(.*?)((?:\{n\})*)$', seg)
        body = m.group(2) if m.group(2).strip(' 　') else ''      # a lone space glyph draws nothing
        out.append((len(m.group(1)) // 3, (body.count('{n}') + 1 if body else 0) + len(m.group(3)) // 3))
    return out


def short_final(lines, name, source):
    """Reject literal paragraph stubs; runtime substitutions and independent answer rows are different units."""
    lines = [ln for ln in lines if ln.strip()]
    if len(lines) < 2 or name in ('choices', 'staff'):
        return False
    # These authored cipher clues are independent rows, not prose (DMAP03_92:054/055).
    if source in ('XIJUF{n}CMVF', 'ZFMMPX{n}SFE'):
        return False
    if re.search(r'\{(?:str|num|gold|name)\}', lines[-1]):
        return False  # runtime value length cannot be inferred from the literal token
    return len(TOKEN.sub('', lines[-1]).strip(' "')) < 6


def layout(en, jp, name=None):
    """(engine text, [problems]) for authored en replacing jp."""
    name = name or 'dlg'
    if name == 'proverb':
        answer = re.sub(r'[^A-Za-z]', '', en).upper()
        return answer, [] if 1 <= len(answer) <= 18 else ['Word Maze answer must have 1..18 letters']
    str_width = {'carddlg': 134, 'proverbdlg': 180}.get(name, 114)
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
        lines = wrap(seg, px, str_width)
        if short_final(lines, name, seg):
            problems.append(f'page {i + 1}: short final paragraph line: {lines[-1]!r}')
        cap = max(max_lines, slots if name in ('dlg', 'carddlg', 'proverbdlg') else 0)
        for ln in lines:
            if width(ln, str_width) > px:
                problems.append(f'line too wide: {width(ln, str_width)} > {px} px: {ln!r}')
        if len(lines) > cap:
            problems.append(f'page {i + 1} has {len(lines)} lines > {cap} (split the page with {{wait}} or cut)')
        out.append('{n}' * lead + '{n}'.join(lines) + '{n}' * max(0, slots - len(lines)))
    # a fragment the game joins to another string keeps its joining space ("Momotaro" + " used Kintan!")
    if en.startswith(' ') and not out[0].startswith(' '):
        out[0] = ' ' + out[0]
    if en.endswith(' ') and len(out) == 1 and '{n}' not in out[0]:
        out[0] += ' '
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
