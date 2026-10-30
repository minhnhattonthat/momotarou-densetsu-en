"""Collectible cards (CR_PG01-99.PAC, docs/re/graphics.md): 297 cards of 96x136 8bpp, card n at entry
(n-1)%3*2 of CR_PG<(n-1)//3+1>, its CLUT in the next entry.

    python -X utf8 tools/cards.py templates   # work/cards/template_<k>.png: clean background per card family

Cards of one family share a background (pink swirls for monsters, cream for villagers...); the per-pixel mode of
the family's colours is that background without names, art or labels (each card's own art is in the minority).
"""
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

import extract
import gfx

ROOT = Path(__file__).resolve().parents[1]
W, H = 96, 136
MIN_FAMILY = 20                 # smaller families (boss cards with their own art) get no template


def loc(n):
    return f'30EV/CR_PG{(n - 1) // 3 + 1:02d}.PAC:{(n - 1) % 3 * 2}'


def card(n):
    """(palette RGB list, pixel indices) of card n."""
    path, e = loc(n).rsplit(':', 1)
    pal = [c[:3] for c in gfx.palette(gfx.entry(f'{path}:{int(e) + 1}'))]
    return pal, gfx.indices(gfx.entry(loc(n)))[3]


def names():
    """English card names, card 1..297 (HMAP8500_18 "<name>カード" strings, " Card" dropped)."""
    doc = extract.load(next((ROOT / 'script').rglob('HMAP8500_18.json')))
    out = [s['en'] for s in doc['strings'] if (s.get('jp') or '').endswith('カード')]
    assert len(out) == 297 and all(e.endswith(' Card') for e in out)
    return [e[:-5] for e in out]


def key(pal, px):
    return pal[px[133 * W + 60]]                # bottom border colour: one per background family


def families():
    fam = {}
    for n in range(1, 298):
        pal, px = card(n)
        fam.setdefault(key(pal, px), []).append(n)
    return {k: v for k, v in fam.items() if len(v) >= MIN_FAMILY}


def glyphish(c):
    """Any grey (white, black and the antialiasing between): lettering colours, never a card background's."""
    return max(c) - min(c) < 16


def templates():
    """{family key: [RGB per pixel]} by per-pixel mode over the family's cards, lettering colours outvoted."""
    out = {}
    for k, ns in families().items():
        cols = [card(n) for n in ns]
        t = []
        for i in range(W * H):
            votes = Counter(pal[px[i]] for pal, px in cols)
            bg = [c for c, _ in votes.most_common() if not glyphish(c)]
            t.append(bg[0] if bg else votes.most_common(1)[0][0])
        out[k] = t
    return out


CIRCLE = (66, 6, 87, 27)        # the initial's glyph inside the disc
COLUMN = (62, 30, 92, 133)      # vertical name
STATS = (2, 2, 60, 62)          # 体力 攻撃 守備 速さ rows (monster families) or flavour text (cream family)
# the game draws each value at x ~34 on the label's row, so a label has the JP label's ~29 px: abbreviated (D9)
STAT_EN = ['HP', 'Atk', 'Def', 'Spd']
STAT_W = 30
REVIEW = []                     # cards whose name was lettered over art (check them by eye)
STAT_FAMILIES = {(224, 240, 240), (248, 216, 216)}      # cyan and pink backgrounds: monster stat labels


def inpaint(img, rect):
    """Replace the greys and dark pixels (glyph residue; the backgrounds are light) in rect by their neighbours."""
    x0, y0, x1, y1 = rect
    todo = {(x, y) for y in range(y0, y1) for x in range(x0, x1)
            if glyphish(img[y * W + x]) or sum(img[y * W + x]) < 360}
    while todo:
        done = {}
        for x, y in todo:
            nb = [img[(y + dy) * W + x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                  if 0 <= x + dx < W and 0 <= y + dy < H and (x + dx, y + dy) not in todo]
            if nb:
                done[(x, y)] = Counter(nb).most_common(1)[0][0]
        if not done:
            break
        for (x, y), c in done.items():
            img[y * W + x] = c
        todo -= done.keys()


def nearest(pal, c):
    return min((i for i in range(1, len(pal)) if pal[i] != (0, 0, 0) or i == 0),
               key=lambda i: sum((a - b) ** 2 for a, b in zip(pal[i], c)))


def letters(text, size, w, h, rotate=False, align='center'):
    """{(x, y): 'fill'|'edge'} of text in a w x h box: black fill, 1 px white outline (the cards' lettering)."""
    import gfx_en
    bw, bh = (h, w) if rotate else (w, h)
    cov = gfx_en.coverage(text, size, bw - 2, bh - 2, align)
    if rotate:
        cov = cov.rotate(-90, expand=True)
    c = cov.load()
    cw, ch = cov.size
    ink = lambda x, y: 0 <= x < cw and 0 <= y < ch and c[x, y] > 110  # noqa: E731
    out = {}
    for y in range(h):
        for x in range(w):
            if ink(x - 1, y - 1):
                out[x, y] = 'fill'
            elif any(ink(x - 1 + dx, y - 1 + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                out[x, y] = 'edge'
    return out


def fit(text, w, h, sizes, rotate=False):
    """letters() at the largest size that fits; a rotated name too long for one line goes on two (first line on
    the right: the tops of rotated letters face right)."""
    for s in sizes:
        try:
            return letters(text, s, w, h, rotate)
        except AssertionError:
            continue
    if rotate and ' ' in text:
        words = text.split()
        cut = min(range(1, len(words)), key=lambda i: abs(len(' '.join(words[:i])) - len(' '.join(words[i:]))))
        a, b = ' '.join(words[:cut]), ' '.join(words[cut:])
        for s in sizes:
            try:
                first, second = letters(a, s, w // 2 + 1, h, True), letters(b, s, w // 2 + 1, h, True)
            except AssertionError:
                continue
            out = {(x + w - w // 2 - 1, y): k for (x, y), k in first.items()}
            for (x, y), k in second.items():
                if k == 'fill' or (x, y) not in out:
                    out[x, y] = k
            return out
    raise AssertionError((text, 'does not fit', w, h))


def redraw(n, tmpl, name):
    """New pixel indices of card n (a template family card)."""
    pal, px = card(n)
    rgb = [pal[i] for i in px]
    t = list(tmpl)
    inpaint(t, COLUMN)
    inpaint(t, STATS)
    out = list(rgb)
    # JP name: components of "differs from the template" pixels lying wholly inside the name column
    diff = {(x, y) for y in range(H) for x in range(W) if rgb[y * W + x] != t[y * W + x]}
    seen = set()
    art = set()
    for p in sorted(diff):
        if p in seen:
            continue
        comp, stack = [], [p]
        seen.add(p)
        while stack:
            x, y = stack.pop()
            comp.append((x, y))
            for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if q in diff and q not in seen:
                    seen.add(q)
                    stack.append(q)
        # the name's first glyph can touch the disc's: the disc counts as inside, but keeps its own pixels
        inside = all(COLUMN[0] - 2 <= x < COLUMN[2] and 2 <= y < COLUMN[3] for x, y in comp)
        if inside:
            for x, y in comp:
                if y >= COLUMN[1]:
                    out[y * W + x] = t[y * W + x]
        elif len(comp) > 40 and max(y for _, y in comp) > STATS[3] and \
                any(COLUMN[0] <= x < COLUMN[2] and COLUMN[1] <= y < COLUMN[3] for x, y in comp):
            art.update(comp)            # (strays and the left box's text touching the column are not art)
    # name glyphs touching art survive the pass above: they are black with a white outline, so erase each
    # grey-connected group in the column that holds white (art outlines border colours, not white)
    grey = {(x, y) for x in range(COLUMN[0], COLUMN[2]) for y in range(COLUMN[1], COLUMN[3])
            if (x, y) in diff and glyphish(out[y * W + x])}
    seen = set()
    for p in sorted(grey):
        if p in seen:
            continue
        comp, stack = [], [p]
        seen.add(p)
        while stack:
            x, y = stack.pop()
            comp.append((x, y))
            for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if q in grey and q not in seen:
                    seen.add(q)
                    stack.append(q)
        if sum(min(out[y * W + x]) > 230 for x, y in comp) >= 3:
            for x, y in comp:
                out[y * W + x] = t[y * W + x]
    white, black = (248, 248, 248), (8, 8, 8)
    # name, rotated, from the top of the column down to the first art row
    x0, y0, x1, y1 = COLUMN
    rows = [y for y in range(y0, y1) if not any((x, y) in art for x in range(x0, x1))]
    span = max(gfx._runs(rows, 1) or [[]], key=len)  # longest run of rows with no art in the column
    if len(span) < 40:                              # art fills the column: letter over it (outlined)
        REVIEW.append(n)
        span = list(range(y0, y1))
    try:
        lt = fit(name, x1 - x0, len(span), range(16, 7, -1), rotate=True)
    except AssertionError:
        REVIEW.append(n)
        span = list(range(y0, y1))
        lt = fit(name, x1 - x0, len(span), range(16, 7, -1), rotate=True)
    y0 = span[0]
    for (x, y), k in lt.items():
        out[(y0 + y) * W + x0 + x] = black if k == 'fill' else white
    # stat labels (the cream family has flavour text there instead: todo)
    x0, y0, x1, y1 = STATS
    for y in range(y0, y1 if key(pal, px) in STAT_FAMILIES else y0):
        for x in range(x0, x1):
            out[y * W + x] = t[y * W + x]
    for r, label in enumerate(STAT_EN if key(pal, px) in STAT_FAMILIES else []):
        for (x, y), k in letters(label, 10, STAT_W, 15, align='left').items():
            out[(y0 + r * 15 + y) * W + x0 + x] = black if k == 'fill' else white
    # initial in the disc: greys -> disc colour, then the letter in white with a black outline
    x0, y0, x1, y1 = CIRCLE
    disc = Counter(rgb[y * W + x] for y in range(y0, y1) for x in range(x0, x1)
                   if not glyphish(rgb[y * W + x])).most_common(1)[0][0]
    for y in range(y0, y1):
        for x in range(x0, x1):
            if glyphish(rgb[y * W + x]):
                out[y * W + x] = disc
    for (x, y), k in letters(name[0], 16, x1 - x0, y1 - y0).items():
        out[(y0 + y) * W + x0 + x] = white if k == 'fill' else black
    cache = {}
    return [px[i] if out[i] == rgb[i] else cache.setdefault(out[i], nearest(pal, out[i])) for i in range(W * H)]


def entries():
    """{card location: new TIM bytes} for every card of a template family."""
    tm = templates()
    nm = names()
    out = {}
    for n in range(1, 298):
        pal, px = card(n)
        if key(pal, px) in tm:
            out[loc(n)] = gfx.repack(gfx.entry(loc(n)), redraw(n, tm[key(pal, px)], nm[n - 1]))
    return out


def preview(ns):
    tm = templates()
    nm = names()
    tiles = []
    for n in ns:
        pal, px = card(n)
        k = key(pal, px)
        if k not in tm:
            print(n, 'no template')
            continue
        new = redraw(n, tm[k], nm[n - 1])
        a, b = Image.new('RGB', (W, H)), Image.new('RGB', (W, H))
        a.putdata([pal[i] for i in px])
        b.putdata([pal[i] for i in new])
        tiles += [a, b]
    sheet = Image.new('RGB', (len(tiles) * (W + 2), H), (255, 0, 255))
    for i, t in enumerate(tiles):
        sheet.paste(t, (i * (W + 2), 0))
    dst = ROOT / 'work/cards/preview.png'
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(dst)
    print(dst)


def main(argv):
    if argv[:1] == ['preview']:
        preview([int(a) for a in argv[1:]])
    if argv[:1] == ['templates']:
        dst = ROOT / 'work/cards'
        dst.mkdir(parents=True, exist_ok=True)
        for i, (k, t) in enumerate(templates().items()):
            im = Image.new('RGB', (W, H))
            im.putdata(t)
            im.resize((W * 3, H * 3), Image.NEAREST).save(dst / f'template_{i}.png')
            print(dst / f'template_{i}.png', k, len(families()[k]), 'cards')


if __name__ == '__main__':
    main(sys.argv[1:])
