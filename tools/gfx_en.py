"""English lettering for graphics text (docs/re/graphics.md): one entry per image, redrawn from the original pixels.

    python -X utf8 tools/gfx_en.py [NAME ...]   # preview: work/gfx_en/<name>.png = original over English, zoomed

insert.files() writes entries() into the build. Each edit clears a rect of the original image to one background
index and draws the English there with an antialiased font mapped onto a ramp of palette indices (background ->
ink), so only pixels inside the declared rects change (asserted).
"""
import functools
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import cards
import gfx

ROOT = Path(__file__).resolve().parents[1]
ROUND = ROOT / 'fonts/mplus/MPLUSRounded1c-ExtraBold-latin.ttf'

# name: (image, (clut, row) for the preview, [(rect x0, y0, x1, y1), English, ramp, font px, options)])
# ramp: palette indices background..ink (antialiased onto a flat background), or one ink index over a textured
# background (each row filled with its commonest index). options: align left|center (default).
MECD_STRIP = [(8, 59, 'Save'), (77, 128, 'Copy'), (141, 188, 'Erase'), (198, 249, 'Quit')]   # memory-card menu
COVER, COVER_CLUT = ['30EV/EVTCARD.PAC:1', '30EV/EVTCARD.PAC:2'], '30EV/EVTCARD.PAC:6'   # album cover: left 240 + right 80 px
STAMP, STAMP_TILT = (208, 6, 287, 86), 22     # its カードアルバム stamp (cover coords) and the stamp's clockwise tilt in degrees
# town sign plates (shop names FONT_6:700-707; docs/re/graphics.md). Per kind: reference image, first plate x y,
# plate w x h, words left to right (None: no plate there), glyph indices, glyph rows (in the plate), ink, light edge,
# text row, tilesets holding copies. Wood row 茶 医 防 足 武 ど つ 易 銭 借? 湯? 薪? 祭 ゆ 笑 刃 (ど つ 薪? unknown ->
# SHOP); oval building signs 宿 茶 医 防 足 武 銭 刃, then 八百屋 (wide) つ 易.
WOOD_IMAGES = ['06CITY/SMAP%s.PAC:3' % n for n in ('00', '04', '0401', '06', '0601', '08', '09', '13', '14', '16', '20',
                                                   '2001', '21', '22', '23', '24', '26', '27', '28')] + \
    ['06CITY01/JMAP00.PAC:1', '06CITY01/OMAP00.PAC:1'] + \
    ['06CITY01/OMAP0%d.PAC:%d' % (n, e) for n in range(1, 6) for e in (3, 5)]
OVAL_IMAGES = ['06CITY/SMAP%s.PAC:6' % n for n in ('00', '01', '02', '04', '0401', '06', '0601', '08', '09', '12', '13',
                                                   '16', '20', '2001', '21', '22', '23', '24', '26')] + \
    ['06CITY01/JMAP00.PAC:4', '06CITY01/OMAP00.PAC:4', '07HMAP3/HMAP8600.PAC:3']
PLATE_KINDS = [
    ('06CITY/SMAP00.PAC:3', (0, 80), 16, 16, ['TEA', 'DOC', 'ARM', 'SHOE', 'WPN', 'ITEM', 'SHOP', 'SEER', 'BANK', 'RENT',
                                              'BATH', 'SHOP', 'FEST', 'BATH', 'JOKE', 'EDGE'], (12, 13, 14), (1, 15), 12,
     13, 5, WOOD_IMAGES),
    ('06CITY01/OMAP00.PAC:4', (0, 54), 32, 20, ['INN', 'TEA', 'DOC', 'ARMOR', 'SHOES', 'ARMS', 'BANK', 'SMITH'], (6, 7),
     (2, 17), 6, 7, 7, OVAL_IMAGES),
    ('06CITY01/OMAP00.PAC:4', (16, 86), 32, 20, [None, None, 'SHOP', 'SEER'], (6, 7, 8), (2, 17), 6, 7, 7, OVAL_IMAGES),
    ('06CITY01/OMAP00.PAC:4', (8, 86), 64, 20, ['GROCER'], (6, 7, 8), (2, 17), 6, 7, 7, OVAL_IMAGES),
    # SMAP16's own: 8th oval 衣, then 着 料亭 カード道場 and a big 湯
    ('06CITY/SMAP16.PAC:6', (224, 54), 32, 20, ['CLOTH'], (6, 7, 8), (2, 17), 6, 7, 7, ['06CITY/SMAP16.PAC:6']),
    ('06CITY/SMAP16.PAC:6', (0, 86), 32, 20, ['KIMONO'], (6, 7, 8), (2, 17), 6, 7, 7, ['06CITY/SMAP16.PAC:6']),
    ('06CITY/SMAP16.PAC:6', (32, 86), 64, 20, ['RESTAURANT'], (6, 7, 8), (2, 17), 6, 7, 7, ['06CITY/SMAP16.PAC:6']),
    ('06CITY/SMAP16.PAC:6', (96, 86), 104, 20, ['CARD DOJO'], (6, 7, 8), (2, 17), 6, 7, 7, ['06CITY/SMAP16.PAC:6']),
    ('06CITY/SMAP16.PAC:6', (200, 84), 48, 28, ['BATH'], (6, 7, 8), (3, 25), 6, 7, 11, ['06CITY/SMAP16.PAC:6']),
] + [  # Shuten-doji's cave, 7-tile floor word しゅてんどうじ (DMAP03_92:002): SH u TE N DO U JI, small ゅ -> small U
    ('06DAN01/DMAP03.PAC:0', (x, y), 16, 16, [word], (1, 2, 3), (1, 15), 3, 1, 3 if s == 2 else 8, ['06DAN01/DMAP03.PAC:0'], s)
    for x, y, word, s in ((64, 160, 'SH', 2), (64, 176, 'U', 1), (64, 192, 'TE', 2), (64, 208, 'N', 2), (64, 224, 'DO', 2),
                          (80, 160, 'U', 2), (80, 176, 'JI', 2))]
PIXEL_FONT = {ch: rows.split('/') for ch, rows in {     # 3x5 caps
    'A': '.#./#.#/###/#.#/#.#', 'B': '##./#.#/##./#.#/##.', 'C': '.##/#../#../#../.##', 'D': '##./#.#/#.#/#.#/##.',
    'E': '###/#../##./#../###', 'F': '###/#../##./#../#..', 'G': '.##/#../#.#/#.#/.##', 'H': '#.#/#.#/###/#.#/#.#',
    'I': '###/.#./.#./.#./###', 'J': '..#/..#/..#/#.#/.#.', 'K': '#.#/#.#/##./#.#/#.#', 'M': '#.#/###/###/#.#/#.#',
    'N': '##./#.#/#.#/#.#/#.#', 'O': '.#./#.#/#.#/#.#/.#.', 'P': '##./#.#/##./#../#..', 'R': '##./#.#/##./#.#/#.#',
    'S': '.##/#../.#./..#/##.', 'T': '###/.#./.#./.#./.#.', 'W': '#.#/#.#/###/###/#.#', 'L': '#../#../#../#../###',
    'U': '#.#/#.#/#.#/#.#/###', ' ': '.../.../.../.../...'}.items()}
# bath-event band: 8bpp 256x256, band y5-80 (ゆ 湯 ゆ + edge) and a 湯 tile below it; rects, word, font px
BATH_IMAGE, BATH_CLUT, BATH_INK = '30EV/FURO_0.PAC:6', '30EV/FURO_0.PAC:5', (160, 80, 0)
BATH_LOCS = ['30EV/FURO_%d.PAC:6' % n for n in range(5)]
BATH_WORDS = [((0, 5, 76, 80), 'Hot', 30), ((82, 5, 144, 80), 'Bath', 24), ((168, 5, 238, 80), 'Hot', 30),
              ((8, 84, 80, 160), 'Bath', 26)]
VERT = {'rotate': True, 'ink': 15} # album index labels: index 15 = the JP glyph fill, black in-game (grey in the preview CLUT)
IMAGES = {
    'title_menu': ('30EV/EVTTIT.PAC:9', ('30EV/EVTTIT.PAC:19', 0), [
        # left edges = the JP words' (the cursor peach sits just left of them)
        ((51, 10, 122, 28), 'New Game', range(47, 32, -1), 14, {'align': 'left'}),
        ((128, 10, 214, 28), 'Continue', range(47, 32, -1), 14, {'align': 'left'}),
    ]),
    # きろく うつす けす やめる strip; きろく やめる and つづき やめる buttons
    'mecd_menu': ('13BTL/MECD.PAC:3', ('13BTL/MECD.PAC:5', 0), [
        ((x0, 139, x1, 157), t, 1, 14, {}) for x0, x1, t in MECD_STRIP] + [
        ((36, 187, 88, 203), 'Save', 1, 14, {}), ((105, 187, 157, 203), 'Quit', 1, 14, {}),
        ((27, 227, 79, 244), 'Load', 1, 14, {}), ((97, 227, 149, 244), 'Quit', 1, 14, {}),
    ]),
    # minigame words: すたーと げーむおーばー そこまで！ げーむくりあー, 得点 最高得点 時間
    'daruma_words': ('30EV/DARUMA.PAC:10', ('30EV/DARUMA.PAC:11', 0), [
        ((0, 152, 104, 176), 'Start!', 'sprite', 22, {}),
        ((0, 176, 182, 201), 'Game Over', 'sprite', 22, {}),
        ((0, 201, 115, 225), "Time's Up!", 'sprite', 18, {}),
        ((0, 225, 182, 249), 'Game Clear!', 'sprite', 22, {}),
        ((168, 56, 196, 73), 'Score', 'sprite', 9, {}),
        ((196, 56, 249, 73), 'Best', 'sprite', 11, {}),
        ((203, 74, 246, 96), 'Time', 'sprite', 16, {}),
    ]),
    'mogura_words': ('30EV/MOGURA.PAC:10', ('30EV/MOGURA.PAC:11', 0), [
        ((40, 176, 144, 198), 'Start!', 'sprite', 22, {}),
        ((40, 198, 222, 222), 'Game Over', 'sprite', 22, {}),
        ((40, 222, 160, 248), "Time's Up!", 'sprite', 18, {}),
        ((184, 1, 232, 22), 'Miss', 'sprite', 14, {}),          # 失敗; the x after it stays
        ((184, 22, 242, 40), 'Best', 'sprite', 13, {}),
        ((184, 40, 228, 64), 'Time', 'sprite', 16, {}),
        ((144, 78, 178, 98), 'Score', 'sprite', 10, {}),
    ]),
    'yumi_words': ('30EV/YUMI1.PAC:9', ('30EV/YUMI1.PAC:10', 0), [
        ((0, 152, 104, 176), 'Start!', 'sprite', 22, {}),
        ((0, 176, 182, 199), 'Game Over', 'sprite', 22, {}),
        ((0, 199, 116, 224), "Time's Up!", 'sprite', 18, {}),
        ((0, 80, 46, 103), 'Miss', 'sprite', 14, {}),
        ((64, 80, 108, 103), 'Time', 'sprite', 16, {}),
        ((0, 104, 57, 121), 'Best', 'sprite', 13, {}),
        ((57, 104, 84, 121), 'Score', 'sprite', 8, {}),
    ]),
    # めでたし (the folk-tale closing formula) on the white plate of the ending frame
    'end_plate': ('30EV/END01.PAC:2', ('30EV/END01.PAC:3', 0), [
        ((40, 192, 132, 216), 'The End', [48, 54, 56, 63], 22, {}),
    ]),
    # card-album index: vertical labels (rotated English) and the kanji numerals of the card count (digits)
    'album_index': ('30EV/EVTCARD.PAC:5', ('30EV/EVTCARD.PAC:7', 0), [
        ((96, 1, 124, 62), 'Contents', 'sprite', 12, VERT),
        ((80, 1, 96, 100), "Momotaro's Friends", 'sprite', 9, VERT),
        ((64, 2, 80, 35), 'Folk', 'sprite', 10, VERT),      # the game cuts each label at the JP length: 32 px
        ((48, 2, 64, 35), 'Hermit', 'sprite', 9, VERT),
        ((32, 3, 48, 52), 'Boss Oni', 'sprite', 10, VERT),
        ((16, 1, 32, 21), 'Oni', 'sprite', 9, VERT),
        ((0, 0, 16, 62), 'Cards', 'sprite', 12, VERT),      # 現在合計 (total)
        ((0, 119, 16, 137), '', 'sprite', 9, {}),                        # 枚 (counter): "Cards" says it
        ((144, 0, 160, 15), '0', 'sprite', 13, {}),                      # 〇
    ] + [((100, 64 + 16 * i, 124, 80 + 16 * i), str(i + 1), 'sprite', 13, {}) for i in range(9)]),
    # pun-contest hall banner 天下一だじゃれ大会 (SMAP13)
    'pun_banner': ('06CITY/SMAP13.PAC:5', ('06CITY/SMAP13.PAC:7', 0), [
        ((6, 4, 140, 14), 'Grand Pun Contest', [1, 2, 3, 4, 5], 11, {}),
        ((5, 2, 141, 3), '', [3], 11, {}),          # the bevel rows under the frame, minus the JP glyph tops
        ((5, 3, 141, 4), '', [2], 11, {}),
    ]),
    # Shuten-doji's cave quiz panels (DMAP03_92:044-055): 東 西 南 北 on stone, 赤 青 黄 白 on flat grey
    'cave_panels': ('06DAN01/DMAP03.PAC:2', ('06DAN01/DMAP03.PAC:4', 0), [
        ((x + 3, 8, x + 45, 40), word, 'sprite', 13, {'erase': (1, 2, 3, 4)})
        for x, word in ((0, 'East'), (48, 'West'), (96, 'South'), (144, 'North'))] + [
        ((x + 4, 58, x + 44, 88), word, 'sprite', 11, {}) for x, word in ((0, 'Red'), (48, 'Blue'), (96, 'Yellow'),
                                                                          (144, 'White'))]),
    # bathhouse curtains 男湯 / 女湯
    'bath_signs': ('07HMAP3/HMAP8200.PAC:3', ('07HMAP3/HMAP8200.PAC:4', 0), [
        ((8, 3, 56, 25), 'Men', 'sprite', 14, {'erase': (10, 11, 12, 13)}),
        ((70, 3, 122, 25), 'Women', 'sprite', 13, {'erase': (10, 11, 12, 13)}),
    ]),
    # つづき うつす けす やめる strip (title > Continue)
    'mecd_load': ('13BTL/MECD.PAC:2', ('13BTL/MECD.PAC:5', 0), [
        ((x0, 162, x1, 181), 'Load' if t == 'Save' else t, 1, 14, {}) for x0, x1, t in MECD_STRIP]),
}


def coverage(text, size, w, h, align='center', font=ROUND, ref='H'):
    """L image w x h with text centred vertically (align: left or center), 0 = background, 255 = ink.
    ref: the sample centred ('Hg' leaves room for descenders in a tight box)."""
    f = ImageFont.truetype(str(font), size)
    im = Image.new('L', (w, h))
    if not text:                                # a rect only cleared
        return im
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    _, top, _, base = d.textbbox((0, 0), ref, font=f)        # same sample for every word: one baseline
    y = (h - (base - top)) // 2 - top
    assert x1 - x0 <= w and y + y0 >= 0 and y + y1 <= h, (text, x1 - x0, y1 - y0, 'does not fit', w, h)
    d.text(((w - (x1 - x0)) // 2 * (align == 'center') - x0, y), text, font=f, fill=255)
    return im


def sprite(px, new, w, rect, text, size, opt):
    """Lettering on a sprite (background = the rect border's commonest index): outline = the index most found on the JP glyphs' edge, fill per
    row = the commonest inner index of that JP row (keeps vertical gradients); opt 'edge': outline width (1);
    opt 'erase': the JP glyph's indices: only those are cleared (to the row's commonest other index), the rest of the
    rect (folds, seams) is kept."""
    x0, y0, x1, y1 = rect
    bg = Counter([px[y * w + x] for x in range(x0, x1) for y in (y0, y1 - 1)] +
                 [px[y * w + x] for y in range(y0, y1) for x in (x0, x1 - 1)]).most_common(1)[0][0]
    erase = opt.get('erase')
    glyph = (lambda v: v in erase) if erase else (lambda v: v != bg)  # noqa: E731
    rowbg = {y: Counter(px[y * w + x] for x in range(x0, x1) if not glyph(px[y * w + x])).most_common(1)[0][0]
             for y in range(y0, y1)} if erase else {}
    at = lambda x, y: px[y * w + x] if x0 <= x < x1 and y0 <= y < y1 and glyph(px[y * w + x]) else 0  # noqa: E731
    edge = Counter(at(x, y) for y in range(y0, y1) for x in range(x0, x1) if at(x, y) and
                   not all(at(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))).most_common(1)[0][0]
    fills = {y: Counter(at(x, y) for x in range(x0, x1) if at(x, y) not in (0, edge)).most_common(1) for y in
             range(y0, y1)}
    known = [(y, f[0][0]) for y, f in fills.items() if f]
    fill = {y: min(known, key=lambda k: abs(k[0] - y))[1] for y in range(y0, y1)}
    e = opt.get('edge', 1)
    if opt.get('rotate'):                       # vertical label, reads top to bottom: solid outline colour, row fills would stripe it
        e = opt.get('edge', 0)
        fill = dict.fromkeys(range(y0, y1), opt.get('ink', edge))
        cov = coverage(text, size, y1 - y0 - 2 * e, x1 - x0 - 2 * e, opt.get('align', 'center'))
        cov = cov.rotate(-90, expand=True)
    else:
        cov = coverage(text, size, x1 - x0 - 2 * e, y1 - y0 - 2 * e, opt.get('align', 'center'))
    cov = cov.point(lambda v: 255 * (v > 110)).load()
    hw, hh = x1 - x0 - 2 * e, y1 - y0 - 2 * e
    ink = lambda x, y: 0 <= x < hw and 0 <= y < hh and cov[x, y]  # noqa: E731
    for y in range(y0, y1):
        for x in range(x0, x1):
            cx, cy = x - x0 - e, y - y0 - e
            if ink(cx, cy):
                new[y * w + x] = fill[y]
            elif any(ink(cx + dx, cy + dy) for dx in range(-e, e + 1) for dy in range(-e, e + 1)):
                new[y * w + x] = edge
            elif erase:                         # glyph pixel -> the nearest non-glyph pixel above/below (keeps texture)
                new[y * w + x] = px[y * w + x] if px[y * w + x] not in erase else next(
                    (px[sy * w + x] for d in range(1, y1 - y0) for sy in (y - d, y + d)
                     if y0 <= sy < y1 and px[sy * w + x] not in erase), rowbg[y])
            else:
                new[y * w + x] = bg


def redraw(name):
    loc, _, edits = IMAGES[name]
    raw = gfx.entry(loc)
    _, w, h, px = gfx.indices(raw)
    new = bytearray(px)
    for (x0, y0, x1, y1), text, ramp, size, opt in edits:
        if ramp == 'sprite':
            sprite(px, new, w, (x0, y0, x1, y1), text, size, opt)
            continue
        cov = coverage(text, size, x1 - x0, y1 - y0, opt.get('align', 'center')).load()
        for y in range(y0, y1):
            if isinstance(ramp, int):       # textured background: each row takes the commonest index beside the rect
                side = [*range(max(0, x0 - 6), x0), *range(x1, min(w, x1 + 6))]
                r = [Counter(px[y * w + x] for x in side if px[y * w + x] != ramp).most_common(1)[0][0], ramp]
            else:
                r = list(ramp)
            for x in range(x0, x1):
                new[y * w + x] = r[(cov[x - x0, y - y0] * (len(r) - 1) + 127) // 255]
    inside = {(x, y) for (x0, y0, x1, y1), *_ in edits for y in range(y0, y1) for x in range(x0, x1)}
    assert all(new[i] == px[i] or (i % w, i // w) in inside for i in range(len(px))), name
    return raw, new


def stamp():
    """Album-cover stamp カードアルバム -> CARD / ALBUM. The red stamp pixels (and the white rim beside them) become the
    paper found nearest above/below/beside them, then a new tilted stamp is drawn. {image location: new pixels} for
    both halves of the cover; only pixels inside STAMP change (asserted)."""
    from PIL import ImageFilter
    pal = gfx.palette(gfx.entry(COVER_CLUT))
    halves = [gfx.indices(gfx.entry(loc))[1:] for loc in COVER]
    w, h = sum(hw for hw, _, _ in halves), halves[0][1]
    px = [i for y in range(h) for hw, _, p in halves for i in p[y * hw:(y + 1) * hw]]
    x0, y0, x1, y1 = STAMP
    red = lambda i: pal[i][0] > 180 and pal[i][0] - pal[i][2] > 80  # noqa: E731
    box = [(x, y) for y in range(y0, y1) for x in range(x0, x1)]
    reds = {(x, y) for x, y in box if red(px[y * w + x])}
    paper = lambda x, y: pal[px[y * w + x]][2] > pal[px[y * w + x]][0] or max(pal[px[y * w + x]][:3]) < 120  # noqa: E731
    gone, todo = set(reds), list(reds)          # the stamp: red, plus the light non-bluish pixels touching it (pinks, white rim)
    while todo:
        x, y = todo.pop()
        for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if x0 <= q[0] < x1 and y0 <= q[1] < y1 and q not in gone and not paper(*q) and not any(   # 説's outline
                    max(pal[px[(q[1] + dy) * w + q[0] + dx]][:3]) < 120 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                gone.add(q)
                todo.append(q)
    rim = {(x, y) for x, y in gone if min(pal[px[y * w + x]][:3]) > 200}
    ink = Counter(px[y * w + x] for x, y in reds).most_common(1)[0][0]
    white = Counter(px[y * w + x] for x, y in rim).most_common(1)[0][0]
    new = list(px)
    for x, y in gone:                           # paper: the nearest pixel outside the stamp, straight up/down/sideways
        src = next((sx, sy) for d in range(1, 80) for sx, sy in ((x, y - d), (x, y + d), (x - d, y), (x + d, y))
                   if 0 <= sx < w and 0 <= sy < h and (sx, sy) not in gone)
        new[y * w + x] = px[src[1] * w + src[0]]
    size = 76
    im = Image.new('L', (size, size))
    d = ImageDraw.Draw(im)
    s0 = (size - 52) // 2
    d.rounded_rectangle((s0, s0, s0 + 51, s0 + 51), radius=7, outline=255, width=3)
    for text, cy in (('CARD', s0 + 16), ('ALBUM', s0 + 34)):
        f = ImageFont.truetype(str(ROUND), 12)
        d.text((size // 2, cy), text, font=f, fill=255, anchor='mm')
    m = im.rotate(-STAMP_TILT, resample=Image.BICUBIC).point(lambda v: 255 * (v > 110))
    rimm = m.filter(ImageFilter.MaxFilter(3))
    m, rimm = m.load(), rimm.load()
    cx, cy = (x0 + x1) // 2 - size // 2, (y0 + y1) // 2 - size // 2
    for y in range(size):
        for x in range(size):
            if m[x, y] or rimm[x, y]:
                assert x0 <= cx + x < x1 and y0 <= cy + y < y1, 'stamp outside STAMP'
                new[(cy + y) * w + cx + x] = ink if m[x, y] else white
    out, left = {}, 0
    for loc, (hw, _, _) in zip(COVER, halves):
        out[loc] = [new[y * w + left + x] for y in range(h) for x in range(hw)]
        left += hw
    return out


def bath():
    """Bath-event band (FURO_n.PAC:6, same in all five): brush ゆ 湯 burnt into vertical-grain wood -> Hot / Bath.
    Brush pixels (orange: R-G >= 60 or B <= 24, plus 1 px) take the nearest wood pixel above/below (the grain is
    vertical), then the word is blended in the brush colour, each pixel the nearest CLUT colour. New pixels."""
    from PIL import ImageFilter
    pal = [c[:3] for c in gfx.palette(gfx.entry(BATH_CLUT))]
    _, w, h, px = gfx.indices(gfx.entry(BATH_IMAGE))
    new = bytearray(px)
    near = functools.cache(lambda c: min(range(1, 256), key=lambda i: sum((a - b) ** 2 for a, b in zip(pal[i], c))))
    for (x0, y0, x1, y1), word, size in BATH_WORDS:
        brush = Image.new('L', (x1 - x0, y1 - y0))
        brush.putdata([255 * (pal[px[y * w + x]][0] - pal[px[y * w + x]][1] >= 60 or pal[px[y * w + x]][2] <= 24)
                       for y in range(y0, y1) for x in range(x0, x1)])
        gone = brush.filter(ImageFilter.MaxFilter(3)).load()
        for y in range(y0, y1):
            for x in range(x0, x1):
                if gone[x - x0, y - y0]:
                    src = next(sy for d in range(1, h) for sy in (y - d, y + d)
                               if y0 <= sy < y1 and not gone[x - x0, sy - y0])
                    new[y * w + x] = px[src * w + x]
        cov = coverage(word, size, x1 - x0, y1 - y0).load()
        for y in range(y0, y1):
            for x in range(x0, x1):
                a = cov[x - x0, y - y0] / 255 * 0.8     # burnt into the wood, not painted on
                if a:
                    new[y * w + x] = near(tuple(round(i * a + b * (1 - a)) for i, b in zip(BATH_INK, pal[new[y * w + x]])))
    return new


def plates():
    """Town sign plates (PLATE_KINDS): every block equal to one of the reference row's plates, in the kind's tilesets,
    gets the English word in the 3x5 pixel font (ink, light edge under each stroke) on the glyph rows cleared to the
    commonest plate index of each row. {image location: (new pixels, [rects])}."""
    out = {}
    for ref_loc, (rx, ry), bw, bh, words, glyph, (g0, g1), ink_i, light, ty, images, *scale in PLATE_KINDS:
        s = scale[0] if scale else 1            # pixel-font scale
        ref = gfx.indices(gfx.entry(ref_loc))[3]
        blk = lambda p, w, x0, y0: bytes(p[y * w + x0 + x] for y in range(y0, y0 + bh) for x in range(bw))  # noqa: E731,B023
        new_blocks = {}
        for k, word in enumerate(words):
            if word is None:                    # slot holds no plate of this kind
                continue
            b = bytearray(blk(ref, 256, rx + k * bw, ry))
            for y in range(g0, g1):
                bg = Counter(v for v in b[y * bw:(y + 1) * bw] if v not in glyph and v).most_common(1)[0][0]
                for x in range(bw):
                    if b[y * bw + x] in glyph:
                        b[y * bw + x] = bg
            ink = set()
            x = (bw - (4 * len(word) - 1) * s) // 2
            for ch in word:
                for r, bits in enumerate(PIXEL_FONT[ch]):
                    ink |= {(x + c * s + i, ty + r * s + j) for c in range(3) if bits[c] == '#'
                            for i in range(s) for j in range(s)}
                x += 4 * s
            for px, py in ink:
                b[py * bw + px] = ink_i
            for px, py in ink:                  # carved look: light edge under each stroke
                if (px, py + 1) not in ink:
                    b[(py + 1) * bw + px] = light
            new_blocks[blk(ref, 256, rx + k * bw, ry)] = bytes(b)
        mid = {b[bh // 2 * bw:(bh // 2 + 1) * bw] for b in new_blocks}    # quick filter: a plate's middle row
        for loc in images:
            _, w, h, px = gfx.indices(gfx.entry(loc))
            new, rects = out.get(loc, (bytearray(px), []))
            for y0 in range(0, h - bh + 1):
                for x0 in range(0, w - bw + 1, 8):
                    m = (y0 + bh // 2) * w + x0
                    if bytes(px[m:m + bw]) in mid and (b := new_blocks.get(blk(px, w, x0, y0))):
                        rects.append((x0, y0, x0 + bw, y0 + bh))
                        for y in range(bh):
                            new[(y0 + y) * w + x0:(y0 + y) * w + x0 + bw] = b[y * bw:(y + 1) * bw]
            assert rects, loc
            out[loc] = (new, rects)
    return out


def entries():
    """{image location: new TIM bytes} for every image in IMAGES, the album stamp, and the redrawn cards (tools/cards.py)."""
    out = dict(cards.entries())
    for name in IMAGES:
        raw, new = redraw(name)
        out[IMAGES[name][0]] = gfx.repack(raw, new)
    for loc, new in stamp().items():
        out[loc] = gfx.repack(gfx.entry(loc), new)
    for loc, (new, _) in plates().items():
        out[loc] = gfx.repack(gfx.entry(loc), new)
    new = bath()
    for loc in BATH_LOCS:
        out[loc] = gfx.repack(gfx.entry(loc), new)
    return out


def preview(name, zoom=3):
    loc, (cl, row), edits = IMAGES[name]
    raw, new = redraw(name)
    pal = gfx.palette(gfx.entry(cl), row)
    x0 = min(r[0][0] for r in edits) - 4
    y0 = min(r[0][1] for r in edits) - 4
    x1 = max(r[0][2] for r in edits) + 4
    y1 = max(r[0][3] for r in edits) + 4
    a = gfx.image(raw, pal).crop((x0, y0, x1, y1))
    b = gfx.image(raw, pal, new).crop((x0, y0, x1, y1))
    out = Image.new('RGBA', (a.width, a.height * 2 + 2), (255, 0, 255, 255))
    out.paste(a, (0, 0))
    out.paste(b, (0, a.height + 2))
    dst = ROOT / f'work/gfx_en/{name}.png'
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.resize((out.width * zoom, out.height * zoom), Image.NEAREST).save(dst)
    print(dst)


def preview_stamp(zoom=4):
    pal = gfx.palette(gfx.entry(COVER_CLUT))
    new = stamp()
    a = [gfx.image(gfx.entry(loc), pal) for loc in COVER]
    b = [gfx.image(gfx.entry(loc), pal, new[loc]) for loc in COVER]
    out = Image.new('RGBA', (320, 176 * 2 + 2), (255, 0, 255, 255))
    for row, (l, r) in enumerate((a, b)):
        out.paste(l, (0, row * 178))
        out.paste(r, (240, row * 178))
    x0, y0, x1, y1 = STAMP
    out = out.crop((x0 - 30, 0, x1 + 4, 178 + y1 + 4))
    dst = ROOT / 'work/gfx_en/stamp.png'
    out.resize((out.width * zoom, out.height * zoom), Image.NEAREST).save(dst)
    print(dst)


def preview_plates(zoom=4):
    new = plates()
    out = Image.new('RGBA', (256, 2 * sum(k[3] + 2 for k in PLATE_KINDS)), (255, 0, 255, 255))
    y = 0
    for loc, (_, ry), _, bh, *_ in PLATE_KINDS:
        raw = gfx.entry(loc)
        for px in (None, new[loc][0]):
            out.paste(gfx.image(raw, None, px).crop((0, ry, 256, ry + bh)), (0, y))
            y += bh + 2
    dst = ROOT / 'work/gfx_en/plates.png'
    out.resize((out.width * zoom, out.height * zoom), Image.NEAREST).save(dst)
    print(dst)


def preview_bath(zoom=2):
    pal = gfx.palette(gfx.entry(BATH_CLUT))
    raw = gfx.entry(BATH_IMAGE)
    out = Image.new('RGBA', (512, 164), (255, 0, 255, 255))
    out.paste(gfx.image(raw, pal).crop((0, 0, 256, 164)), (0, 0))
    out.paste(gfx.image(raw, pal, bath()).crop((0, 0, 256, 164)), (256, 0))
    dst = ROOT / 'work/gfx_en/bath.png'
    out.resize((out.width * zoom, out.height * zoom), Image.NEAREST).save(dst)
    print(dst)


if __name__ == '__main__':
    for n in sys.argv[1:] or [*IMAGES, 'stamp', 'plates', 'bath']:
        {'stamp': preview_stamp, 'plates': preview_plates, 'bath': preview_bath}.get(n, lambda: preview(n))()
