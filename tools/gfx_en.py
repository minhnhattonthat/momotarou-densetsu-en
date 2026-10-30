"""English lettering for graphics text (docs/re/graphics.md): one entry per image, redrawn from the original pixels.

    python -X utf8 tools/gfx_en.py [NAME ...]   # preview: work/gfx_en/<name>.png = original over English, zoomed

insert.files() writes entries() into the build. Each edit clears a rect of the original image to one background
index and draws the English there with an antialiased font mapped onto a ramp of palette indices (background ->
ink), so only pixels inside the declared rects change (asserted).
"""
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import gfx

ROOT = Path(__file__).resolve().parents[1]
ROUND = ROOT / 'fonts/mplus/MPLUSRounded1c-ExtraBold-latin.ttf'

# name: (image, (clut, row) for the preview, [(rect x0, y0, x1, y1), English, ramp, font px, options)])
# ramp: palette indices background..ink (antialiased onto a flat background), or one ink index over a textured
# background (each row filled with its commonest index). options: align left|center (default).
MECD_STRIP = [(8, 59, 'Save'), (77, 128, 'Copy'), (141, 188, 'Erase'), (198, 249, 'Quit')]   # memory-card menu
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
    # つづき うつす けす やめる strip (title > Continue)
    'mecd_load': ('13BTL/MECD.PAC:2', ('13BTL/MECD.PAC:5', 0), [
        ((x0, 162, x1, 181), 'Load' if t == 'Save' else t, 1, 14, {}) for x0, x1, t in MECD_STRIP]),
}


def coverage(text, size, w, h, align='center', font=ROUND):
    """L image w x h with text centred vertically (align: left or center), 0 = background, 255 = ink."""
    f = ImageFont.truetype(str(font), size)
    im = Image.new('L', (w, h))
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    _, top, _, base = d.textbbox((0, 0), 'H', font=f)        # caps centred, so every word sits on one baseline
    y = (h - (base - top)) // 2 - top
    assert x1 - x0 <= w and y + y0 >= 0 and y + y1 <= h, (text, x1 - x0, y1 - y0, 'does not fit', w, h)
    d.text(((w - (x1 - x0)) // 2 * (align == 'center') - x0, y), text, font=f, fill=255)
    return im


def sprite(px, new, w, rect, text, size, opt):
    """Lettering on a sprite (background = the rect border's commonest index): outline = the index most found on the JP glyphs' edge, fill per
    row = the commonest inner index of that JP row (keeps vertical gradients); opt 'edge': outline width (1)."""
    x0, y0, x1, y1 = rect
    bg = Counter([px[y * w + x] for x in range(x0, x1) for y in (y0, y1 - 1)] +
                 [px[y * w + x] for y in range(y0, y1) for x in (x0, x1 - 1)]).most_common(1)[0][0]
    at = lambda x, y: px[y * w + x] if x0 <= x < x1 and y0 <= y < y1 and px[y * w + x] != bg else 0  # noqa: E731
    edge = Counter(at(x, y) for y in range(y0, y1) for x in range(x0, x1) if at(x, y) and
                   not all(at(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))).most_common(1)[0][0]
    fills = {y: Counter(at(x, y) for x in range(x0, x1) if at(x, y) not in (0, edge)).most_common(1) for y in
             range(y0, y1)}
    known = [(y, f[0][0]) for y, f in fills.items() if f]
    fill = {y: min(known, key=lambda k: abs(k[0] - y))[1] for y in range(y0, y1)}
    e = opt.get('edge', 1)
    cov = coverage(text, size, x1 - x0 - 2 * e, y1 - y0 - 2 * e, opt.get('align', 'center')).point(
        lambda v: 255 * (v > 110)).load()
    hw, hh = x1 - x0 - 2 * e, y1 - y0 - 2 * e
    ink = lambda x, y: 0 <= x < hw and 0 <= y < hh and cov[x, y]  # noqa: E731
    for y in range(y0, y1):
        for x in range(x0, x1):
            cx, cy = x - x0 - e, y - y0 - e
            if ink(cx, cy):
                new[y * w + x] = fill[y]
            elif any(ink(cx + dx, cy + dy) for dx in range(-e, e + 1) for dy in range(-e, e + 1)):
                new[y * w + x] = edge
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


def entries():
    """{image location: new TIM bytes} for every image in IMAGES."""
    out = {}
    for name in IMAGES:
        raw, new = redraw(name)
        out[IMAGES[name][0]] = gfx.repack(raw, new)
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


if __name__ == '__main__':
    for n in sys.argv[1:] or IMAGES:
        preview(n)
