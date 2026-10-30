"""Collectible cards (CR_PG01-99.PAC, docs/re/graphics.md): 297 cards of 96x136 8bpp, card n at entry
(n-1)%3*2 of CR_PG<(n-1)//3+1>, its CLUT in the next entry.

    python -X utf8 tools/cards.py templates   # work/cards/template_<k>.png: clean background per card family

Cards of one family share a background (pink swirls for monsters, cream for villagers...); the per-pixel mode of
the family's colours is that background without names, art or labels (each card's own art is in the minority).
"""
import functools
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


@functools.cache
def name_rects():
    """The disc holds the first Japanese character; the vertical column holds the remaining characters."""
    doc = extract.load(next((ROOT / 'script').rglob('HMAP8500_18.json')))
    jp = [s['jp'][:-3] for s in doc['strings'] if (s.get('jp') or '').endswith('カード')]
    # A lone glyph is centred lower (down to y55); longer columns have a two-pixel halo below their last cell.
    out = [(69, 32, 90, min(131, 34 + 18 * max(1, len(s) - 1) + (4 if len(s) <= 2 else 0))) for s in jp]
    out[56] = (69, 32, 90, 110)  # Kaguya's green card uses larger, more widely spaced kana/kanji
    return out


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
        inpaint(t, COLUMN)
        inpaint(t, STATS)
        out[k] = t
    return out


CIRCLE = (66, 6, 87, 27)        # the initial's glyph inside the disc
COLUMN = (69, 30, 92, 133)      # keep the English inside the JP column, clear of adjacent illustration
NAME_ERASE = (69, 30, 90, 131)  # JP halo begins at x69; art to its left and the bottom frame must survive
STAT_GLYPHS = (4, 4, 32, 62)  # the inner frame is x3/y3
STAT_ART = {109: [(29, 42, 32, 62)]}  # Enma's left horn outline
# Original illustration visible beside/below the JP halo (card-native, half-open rectangles).
NAME_ART = {
    148: [(69, 68, 83, 94)], 158: [(69, 76, 72, 93)], 159: [(69, 74, 71, 91)],
    171: [(69, 83, 70, 119), (69, 119, 80, 130)], 174: [(69, 88, 70, 111), (69, 111, 72, 122)],
    179: [(69, 61, 71, 80)], 180: [(69, 85, 82, 110)], 182: [(69, 54, 70, 68)],
    221: [(69, 86, 73, 105)], 223: [(69, 58, 70, 86)], 238: [(69, 100, 70, 114)],
    256: [(69, 46, 71, 71), (69, 86, 80, 97)], 257: [(69, 47, 70, 70)],
    260: [(69, 64, 70, 119), (69, 84, 74, 89), (69, 119, 77, 128)], 261: [(69, 78, 70, 95)],
    264: [(69, 63, 70, 76), (69, 109, 70, 113)], 267: [(69, 71, 70, 89), (69, 109, 70, 113)],
    294: [(69, 63, 70, 76), (69, 109, 70, 113)],
}
STATS = (2, 2, 60, 62)          # 体力 攻撃 守備 速さ rows (monster families) or flavour text (cream family)
FLAVOUR_RECT = (5, 4, 63, 72)   # preserve the frame at y3; JP punctuation extends below the old 62-row box
# the game draws each value at x ~34 on the label's row, so a label has the JP label's ~29 px: abbreviated (D9)
STAT_EN = ['HP', 'Atk', 'Def', 'Spd']
STAT_W = 30
FLAVOUR_TSV = ROOT / 'script/cards.tsv'        # card<TAB>Japanese<TAB>English lines joined by " / "
FLAVOUR_PX, FLAVOUR_LH = 9, 12                  # font size and line pitch: 5 lines in the 60-row box
REVIEW = []                     # cards whose name was lettered over art (check them by eye)


def inpaint(img, rect, todo=None, coloured=False, background=False, palette=None):
    """Replace the greys and dark pixels (glyph residue; the backgrounds are light) in rect, or the pixels in todo,
    by their neighbours, growing inwards."""
    x0, y0, x1, y1 = rect
    todo = set(todo) if todo is not None else {(x, y) for y in range(y0, y1) for x in range(x0, x1)
                                               if glyphish(img[y * W + x]) or sum(img[y * W + x]) < 360}
    while todo:
        done = {}
        for x, y in todo:
            nb = [img[(y + dy) * W + x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                  if 0 <= x + dx < W and 0 <= y + dy < H and (x + dx, y + dy) not in todo
                  and (not coloured or (img[(y + dy) * W + x + dx][1] > img[(y + dy) * W + x + dx][0]
                                        and img[(y + dy) * W + x + dx][1] > img[(y + dy) * W + x + dx][2]))
                  and (not background or (sum(img[(y + dy) * W + x + dx]) > 180
                                          and min(img[(y + dy) * W + x + dx]) < 230))
                  and (palette is None or img[(y + dy) * W + x + dx] in palette)]
            if nb:
                done[(x, y)] = tuple(round(sum(c[i] for c in nb) / len(nb)) for i in range(3)) if palette is not None \
                    else Counter(nb).most_common(1)[0][0]
                if palette is not None:
                    done[(x, y)] = min(palette, key=lambda c: sum((a - b) ** 2 for a, b in zip(c, done[(x, y)])))
        if not done:
            break
        for (x, y), c in done.items():
            img[y * W + x] = c
        todo -= done.keys()


def nearest(pal, c):
    return min((i for i in range(1, len(pal)) if pal[i] != (0, 0, 0) or i == 0),
               key=lambda i: sum((a - b) ** 2 for a, b in zip(pal[i], c)))


def letters(text, size, w, h, rotate=False, align='center', ref='H'):
    """{(x, y): 'fill'|'edge'} of text in a w x h box: black fill, 1 px white outline (the cards' lettering)."""
    import gfx_en
    bw, bh = (h, w) if rotate else (w, h)
    cov = gfx_en.coverage(text, size, bw - 2, bh - 2, align, ref=ref)
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


def lettering(rgb, rect):
    """Black core/white outline and their nearby antialias pixels, without flooding into grey backgrounds."""
    x0, y0, x1, y1 = rect
    grey = {(x, y) for x in range(x0, x1) for y in range(y0, y1)
            if max(rgb[y * W + x]) - min(rgb[y * W + x]) < 32 or max(rgb[y * W + x]) < 80}
    out = {(x, y) for x, y in grey if min(rgb[y * W + x]) > 230 or max(rgb[y * W + x]) < 80}
    for _ in range(2):
        out |= {(x + dx, y + dy) for x, y in out for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if (x + dx, y + dy) in grey}
    return out


def flavour():
    """{card: [English lines]} from script/cards.tsv (cards with flavour text instead of stat labels)."""
    if not FLAVOUR_TSV.exists():
        return {}
    out = {}
    for ln in FLAVOUR_TSV.read_text(encoding='utf-8').splitlines():
        if ln.strip() and not ln.startswith('#'):
            n, _, en = ln.split('\t')
            out[int(n)] = [s.strip() for s in en.split(' / ')]
            assert len(out[int(n)]) <= 5, ln
    return out


@functools.cache
def label_mask():
    """Shared stat lettering, sampled from a card with no illustration behind the labels."""
    pal, px = card(110)
    return frozenset(lettering([pal[i] for i in px], (4, 4, 32, 58)))


def has_stats(rgb):
    return sum(glyphish(rgb[y * W + x]) for x, y in label_mask()) > 0.85 * len(label_mask())


def own_template(rgb, name_rect=NAME_ERASE, protect=(), stat_protect=()):
    """Background of a card with its own art: JP lettering inpainted from its surroundings."""
    t = list(rgb)
    background = {rgb[y * W + x] for y in range(4, 40) for x in range(34, 60)
                  if sum(rgb[y * W + x]) > 180 and min(rgb[y * W + x]) < 230}
    stats = has_stats(rgb)
    green = rgb[133 * W + 60] in {(192, 136, 0), (184, 136, 0), (184, 152, 0)}
    green |= sum(c[1] > c[0] and c[1] > c[2] for c in background) > len(background) * 0.8
    name = lettering(rgb, name_rect)
    for x0, y0, x1, y1 in protect:
        name -= {(x, y) for x in range(x0, x1) for y in range(y0, y1)}
    # The top-right sample is clear on stat cards, but holds flavour lettering on the other cards.
    # Enma's green background changes to his purple robe below the name: let that local colour continue.
    inpaint(t, COLUMN, name, coloured=green and not stats, background=True,
            palette=background if stats and not green else None)
    stat_mask = set(label_mask()) if stats else lettering(rgb, STATS)
    for x0, y0, x1, y1 in stat_protect:
        stat_mask -= {(x, y) for x in range(x0, x1) for y in range(y0, y1)}
    inpaint(t, STATS, stat_mask,
            coloured=green, background=True, palette=background if stats and not green else None)
    return t


def disc_box(rgb):
    return {(x, y): rgb[y * W + x] for y in range(2, 35) for x in range(60, 94)}


def disc_stamp(boxes):
    """Recover the shared hand-drawn outline; differing Japanese initials vote each other out."""
    votes = Counter(p for b in boxes for p, c in b.items() if max(c) < 120)
    ring = {p for p, count in votes.items() if count >= 0.6 * len(boxes)}
    area = {(x, y) for y in range(2, 35) for x in range(60, 94)}
    outside = {p for p in area - ring if p[0] in (60, 93) or p[1] in (2, 34)}
    stack = list(outside)
    while stack:
        x, y = stack.pop()
        for p in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if p in area and p not in ring and p not in outside:
                outside.add(p)
                stack.append(p)
    return ring, area - outside - ring


def disc_hits(box, ring, dx=0, dy=0):
    return sum(max(box.get((x + dx, y + dy), (255, 255, 255))) < 120 for x, y in ring) / len(ring)


@functools.cache
def disc_stamps():
    boxes = [disc_box([pal[i] for i in px]) for pal, px in (card(n) for n in range(1, 298))]
    common = disc_stamp(boxes)
    # The green illustration cards have a slightly different, shifted outline.
    own = [b for b in boxes if disc_hits(b, common[0]) < 0.85]
    return common, disc_stamp(own)


def disc_fit(box):
    best = None
    for k, (ring, _) in enumerate(disc_stamps()):
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                score = disc_hits(box, ring, dx, dy)
                if best is None or score > best[0]:
                    best = score, dx, dy, k
        if best[0] >= 0.85:
            break  # prefer the common stamp; the smaller own-art stamp fits it too easily
    assert best[0] >= 0.85, f'no disc outline fits ({best[0]:.2f})'
    return best


def disc_fix(rgb):
    """Clear initials and their halo inside the fitted outline; retain the original rim and outside art."""
    box = disc_box(rgb)
    _, dx, dy, k = disc_fit(box)
    ring, inside = ({(x + dx, y + dy) for x, y in part} for part in disc_stamps()[k])
    band = {p for p in inside if any((p[0] + a, p[1] + b) in ring
                                   for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    disc = Counter(box[p] for p in inside if not glyphish(box[p])).most_common(1)[0][0]
    edge = Counter(box[p] for p in ring if max(box[p]) < 120).most_common(1)[0][0]
    distance = lambda a, b: sum((p - q) ** 2 for p, q in zip(a, b))  # noqa: E731
    out = {}
    for p in inside:
        if p in band:
            if glyphish(box[p]) and distance(box[p], edge) > 40 ** 2:
                out[p] = disc
        elif distance(box[p], disc) >= 40 ** 2:
            out[p] = disc
    for _ in range(2):
        grow = [p for p in inside - band - set(out) if distance(box[p], disc) >= 16 ** 2
                and any((p[0] + a, p[1] + b) in out for a in (-1, 0, 1) for b in (-1, 0, 1))]
        out.update((p, disc) for p in grow)
    for p in ring:
        if min(box[p]) > 140:  # restore the rim where a Japanese stroke touched it
            out[p] = edge
    return out


def redraw(n, tmpl, name):
    """New pixel indices of card n; tmpl: its family's background, or None (a card with its own art)."""
    pal, px = card(n)
    rgb = [pal[i] for i in px]
    name_rect = name_rects()[n - 1]
    if tmpl is None:
        tmpl = own_template(rgb, name_rect, NAME_ART.get(n, ()), STAT_ART.get(n, ()))
    t = tmpl
    out = list(rgb)
    name_glyphs = lettering(rgb, name_rect)
    for ax0, ay0, ax1, ay1 in NAME_ART.get(n, ()):
        name_glyphs -= {(x, y) for x in range(ax0, ax1) for y in range(ay0, ay1)}
    # Restore only the bounded JP halo; grey illustration beside it stays intact.
    for x, y in name_glyphs:
        out[y * W + x] = t[y * W + x]
    white, black = (248, 248, 248), (8, 8, 8)
    # Rotate the English name into the original JP name's height.
    x0, y0, x1, y1 = COLUMN
    span = list(range(y0, name_rect[3]))  # stay in the JP name area instead of extending into art below it
    try:
        lt = fit(name, x1 - x0, len(span), range(16, 7, -1), rotate=True)
    except AssertionError:
        REVIEW.append(n)
        span = list(range(y0, y1))
        lt = fit(name, x1 - x0, len(span), range(16, 7, -1), rotate=True)
    y0 = span[0]
    for (x, y), k in lt.items():
        out[(y0 + y) * W + x0 + x] = black if k == 'fill' else white
    # stat labels, or the flavour text (script/cards.tsv) on the other cards
    stats = has_stats(rgb)
    lines = flavour().get(n)
    x0, y0, x1, y1 = STATS
    if stats:
        # Reset only the common JP label glyphs, not the whole box: horns and heads extend into it.
        mask = set(label_mask())
        for ax0, ay0, ax1, ay1 in STAT_ART.get(n, ()):
            mask -= {(x, y) for x in range(ax0, ax1) for y in range(ay0, ay1)}
        for x, y in mask:
            out[y * W + x] = t[y * W + x]
        x0, y0 = 5, 3  # preserve the inner frame and a one-pixel gap before the English labels
    elif lines:
        x0, y0, x1, y1 = FLAVOUR_RECT
        clean = list(rgb)
        erase_rect = (4, y0, x1, y1)
        mask = lettering(rgb, erase_rect)
        # Include isolated white antialias pixels; seed inpainting from coloured background only.
        mask.update((x, y) for y in range(y0, y1) for x in range(4, x1)
                    if glyphish(rgb[y * W + x]) and min(rgb[y * W + x]) > 180)
        # A one-pixel fringe is tinted toward the green background, so it is not classified as grey.
        green = key(pal, px) in {(192, 136, 0), (184, 136, 0), (184, 152, 0)} or n == 5
        if green:
            mask = {(x + dx, y + dy) for x, y in mask for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                    if 4 <= x + dx < x1 and y0 <= y + dy < y1}
        for ax0, ay0, ax1, ay1 in {1: [(31, 58, 43, 66), (18, 65, 53, 72)],
                                  3: [(24, 61, 61, 72), (54, 57, 61, 61)],
                                  4: [(21, 61, 49, 72), (37, 58, 43, 61)],
                                  6: [(14, 65, 51, 72)],
                                  8: [(14, 66, 58, 72)], 9: [(12, 56, 59, 72)],
                                  12: [(24, 66, 50, 72)],
                                  28: [(11, 61, 63, 72), (47, 52, 59, 61)]}.get(n, []):
            mask -= {(x, y) for x in range(ax0, ax1) for y in range(ay0, ay1)}
        if n == 9:
            mask |= lettering(rgb, (52, 50, 58, 61))  # JP exclamation mark above the headband
        # Exclude the dark shadow just left of the disc; otherwise it streaks left into Monkey's old text.
        palette = {c for c in rgb if c[1] > c[0] and c[1] > c[2] and sum(c) > 240} if green else None
        inpaint(clean, erase_rect, mask, coloured=green, background=True, palette=palette)
        for x, y in mask:
            out[y * W + x] = clean[y * W + x]
    rows = [(label, 10, STAT_W, 15, 'H') for label in STAT_EN] if stats else \
        [(line, FLAVOUR_PX, x1 - x0, FLAVOUR_LH, 'Hg') for line in lines or []]
    for r, (text, size, w, lh, ref) in enumerate(rows):
        for (x, y), k in letters(text, size, w, lh, align='left', ref=ref).items():
            out[(y0 + r * (14 if stats else lh) + y) * W + x0 + x] = black if k == 'fill' else white
    # initial in the disc: greys -> disc colour, then the letter in white with a black outline
    x0, y0, x1, y1 = CIRCLE
    for (x, y), colour in disc_fix(rgb).items():
        out[y * W + x] = colour
    for (x, y), k in letters(name[0], 16, x1 - x0, y1 - y0).items():
        out[(y0 + y) * W + x0 + x] = white if k == 'fill' else black
    idx = {c: nearest(pal, c) for c in {out[i] for i in range(W * H) if out[i] != rgb[i]}}
    return [px[i] if out[i] == rgb[i] else idx[out[i]] for i in range(W * H)]


@functools.cache
def entries():
    """{card location: new TIM bytes} for every card of a template family (cached: ~10 s, built per process)."""
    tm = templates()
    nm = names()
    out = {}
    for n in range(1, 298):
        pal, px = card(n)
        out[loc(n)] = gfx.repack(gfx.entry(loc(n)), redraw(n, tm.get(key(pal, px)), nm[n - 1]))
    return out


def preview(ns):
    tm = templates()
    nm = names()
    tiles = []
    for n in ns:
        pal, px = card(n)
        new = redraw(n, tm.get(key(pal, px)), nm[n - 1])
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


def flavour_sheets():
    """work/cards/flavour_NN.png: the flavour-text box of every card without stat labels, zoomed, numbered."""
    from PIL import ImageDraw
    ns = [n for n, (pal, px) in ((n, card(n)) for n in range(1, 298)) if not has_stats([pal[i] for i in px])]
    x0, y0, x1, y1 = STATS
    Z, per = 4, 8
    for s in range(0, len(ns), per):
        tiles = []
        for n in ns[s:s + per]:
            pal, px = card(n)
            im = Image.new('RGB', (W, H))
            im.putdata([pal[i] for i in px])
            im = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * Z, (y1 - y0) * Z), Image.NEAREST)
            tile = Image.new('RGB', (im.width, im.height + 20), (255, 255, 255))
            tile.paste(im, (0, 20))
            ImageDraw.Draw(tile).text((4, 4), f'card {n}', fill=(255, 0, 0))
            tiles.append(tile)
        sheet = Image.new('RGB', (tiles[0].width * 4 + 12, tiles[0].height * 2 + 4), (255, 0, 255))
        for i, t in enumerate(tiles):
            sheet.paste(t, (i % 4 * (t.width + 4), i // 4 * (t.height + 4)))
        sheet.save(ROOT / f'work/cards/flavour_{s // per:02d}.png')
    print(len(ns), 'cards:', ns)


def check():
    """Every flavour line fits the box (exit 1 if not)."""
    bad = 0
    for n, lines in flavour().items():
        for line in lines:
            try:
                letters(line, FLAVOUR_PX, FLAVOUR_RECT[2] - FLAVOUR_RECT[0], FLAVOUR_LH, align='left', ref='Hg')
            except AssertionError:
                bad += 1
                print(f'card {n}: too wide: {line!r}')
    print(f'{len(flavour())} cards, {bad} lines too wide')
    return not bad


def main(argv):
    if argv[:1] == ['check']:
        sys.exit(0 if check() else 1)
    if argv[:1] == ['flavour']:
        flavour_sheets()
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
