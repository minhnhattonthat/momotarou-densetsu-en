"""Indexed TIM images in PAC entries (docs/re/graphics.md): decode to pixel indices, show with a CLUT, write back.

    python -X utf8 tools/gfx.py show 30EV/CR_PG01.PAC:0 [30EV/CR_PG01.PAC:1[:row]] --out x.png [--zoom 3]

Locations are 'dir/FILE.PAC:entry' under work/disc/tree/0/. With no CLUT the image is drawn as a grey ramp.
"""
import argparse
import struct
from pathlib import Path

from PIL import Image

import extract
import pac

TREE = Path(__file__).resolve().parents[1] / 'work/disc/tree/0'


def entry(loc):
    path, ent = loc.rsplit(':', 1)
    data = (TREE / path).read_bytes()
    return extract.blob(data, *pac.entries(data)[int(ent)])


def indices(raw):
    """(bpp, width in pixels, height, bytearray of one palette index per pixel) of a 4/8bpp image TIM."""
    _, flags, size, _, _, w, h = struct.unpack_from('<IIIHHHH', raw, 0)
    data = raw[20:20 + size - 12]
    bpp = (4, 8)[flags & 3]
    if bpp == 8:
        return 8, w * 2, h, bytearray(data[:w * 2 * h])
    px = bytearray()
    for b in data[:w * 2 * h]:
        px += bytes((b & 15, b >> 4))
    return 4, w * 4, h, px


def repack(raw, px):
    """raw with its pixels replaced by px (same size and depth as indices(raw) gave)."""
    bpp, w, h, old = indices(raw)
    assert len(px) == len(old) and max(px) < 1 << bpp
    data = bytes(px) if bpp == 8 else bytes(px[i] | px[i + 1] << 4 for i in range(0, len(px), 2))
    return raw[:20] + data + raw[20 + len(data):]


def palette(raw, row=0):
    """RGBA colours of one CLUT row (a 0x11 TIM)."""
    _, _, _, _, _, w, h = struct.unpack_from('<IIIHHHH', raw, 0)
    out = []
    for i in range(w):
        c = struct.unpack_from('<H', raw, 20 + (row * w + i) * 2)[0]
        out.append(((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3, 0 if c == 0 else 255))
    return out


def image(raw, pal=None, px=None):
    bpp, w, h, idx = indices(raw)
    idx = px if px is not None else idx
    pal = pal or [(i * 255 // ((1 << bpp) - 1),) * 3 + (255,) for i in range(1 << bpp)]
    im = Image.new('RGBA', (w, h))
    im.putdata([pal[i] if i < len(pal) else (255, 0, 255, 255) for i in idx])
    return im


def words(im, rect, dark=80, gap=6):
    """[(y0, x0, y1, x1)] boxes of dark (ink) pixel runs in rect: rows split into bands, bands into words."""
    x0, y0, x1, y1 = rect

    def ink(x, y):
        r, g, b, al = im.getpixel((x, y))
        return al and (r * 3 + g * 6 + b) // 10 < dark
    rows = [y for y in range(y0, y1) if any(ink(x, y) for x in range(x0, x1))]
    out = []
    for band in _runs(rows, 1):
        cols = [x for x in range(x0, x1) if any(ink(x, y) for y in band)]
        out += [(band[0], c[0], band[-1] + 1, c[-1] + 1) for c in _runs(cols, gap)]
    return out


def _runs(xs, gap):
    out = []
    for x in xs:
        if out and x - out[-1][-1] <= gap:
            out[-1].append(x)
        else:
            out.append([x])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['show', 'dump', 'words'])
    ap.add_argument('--dark', type=int, default=80, help='words: ink = brightness below this (0-255)')
    ap.add_argument('--gap', type=int, default=6, help='words: blank columns that split two words')
    ap.add_argument('loc')
    ap.add_argument('clut', nargs='?')
    ap.add_argument('--out')
    ap.add_argument('--zoom', type=int, default=1)
    ap.add_argument('--rect', help='x0,y0,x1,y1 for dump: one char per pixel by brightness, column ruler every 10')
    a = ap.parse_args()
    pal = None
    if a.clut:
        parts = a.clut.split(':')
        pal = palette(entry(':'.join(parts[:2])), int(parts[2]) if len(parts) > 2 else 0)
    im = image(entry(a.loc), pal)
    if a.cmd == 'show':
        im.resize((im.width * a.zoom, im.height * a.zoom), Image.NEAREST).save(a.out)
        return
    x0, y0, x1, y1 = map(int, a.rect.split(','))
    if a.cmd == 'words':
        for y, x, yb, xb in words(im, (x0, y0, x1, y1), a.dark, a.gap):
            print(f'ink x {x}-{xb} y {y}-{yb}')
        return
    print('    ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1)))
    for y in range(y0, y1):
        row = ''
        for x in range(x0, x1):
            r, g, b, al = im.getpixel((x, y))
            row += ' ' if not al else ' .:-=+*#%@'[9 - (r * 3 + g * 6 + b) // 10 * 9 // 255]
        print(f'{y:3d} {row}')


if __name__ == '__main__':
    main()
