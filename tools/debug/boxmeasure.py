"""Measure a text box in a scene shot (width gate, docs/re/windows.md).

    python -X utf8 tools/debug/boxmeasure.py SHOT.png Y [Y2]   # rows Y..Y2: box fill span, ink span, per row

The box interior is the widest run of navy pixels (the game's window fill, a dithered dark blue) on the row; ink is
any bright pixel (text) inside it. Budget = interior end + 1 - ink start, read on a row through the text.
"""
import sys

from PIL import Image


def navy(p):
    return p[0] < 48 and p[1] < 48 and p[2] >= 40


def bright(p):
    return min(p) >= 120


def row(img, y):
    px = [img.getpixel((x, y))[:3] for x in range(img.width)]
    runs, start = [], None
    for x in range(img.width + 1):
        inside = x < img.width and (navy(px[x]) or bright(px[x]))
        if inside and start is None:
            start = x
        elif not inside and start is not None:
            runs.append((start, x - 1)); start = None
    lo, hi = max(runs, key=lambda r: r[1] - r[0]) if runs else (0, -1)
    ink = [x for x in range(lo, hi + 1) if bright(px[x])]
    return lo, hi, (min(ink), max(ink)) if ink else None


def scan(path, min_w=40):
    """Every box (rows sharing one navy interior span at least min_w wide): (y0, y1, x0, x1, ink x0, ink x1)."""
    img = Image.open(path).convert('RGB')
    boxes = []
    for y in range(img.height):
        lo, hi, ink = row(img, y)
        if hi - lo + 1 < min_w:
            continue
        b = boxes[-1] if boxes else None
        if b and b[1] == y - 1 and (b[2], b[3]) == (lo, hi):
            b[1] = y
        else:
            boxes.append(b := [y, y, lo, hi, None, None])
        if ink:
            b[4] = min(ink[0], b[4] if b[4] is not None else 999)
            b[5] = max(ink[1], b[5] if b[5] is not None else -1)
    return [tuple(b) for b in boxes if b[1] - b[0] >= 8]


def segments(path, y0, y1, gap=5):
    """Ink segments (x0, x1) of the bright pixels on rows y0..y1 (merged), split at gaps of `gap`+ px: where each
    field of a row starts and ends."""
    img = Image.open(path).convert('RGB')
    cols = sorted({x for y in range(y0, y1 + 1) for x in range(img.width)
                   if min(img.getpixel((x, y))[:3]) >= 120 or max(img.getpixel((x, y))[:3]) >= 200})
    segs = []
    for x in cols:
        if segs and x - segs[-1][1] <= gap:
            segs[-1][1] = x
        else:
            segs.append([x, x])
    return [tuple(s) for s in segs]


def main(argv):
    if argv[0] == '--segments':
        print(segments(argv[1], int(argv[2]), int(argv[3])))
        return
    if argv[0] == '--scan':
        for p in argv[1:]:
            for b in scan(p):
                print(f'{p}: rows {b[0]}-{b[1]} interior x={b[2]}..{b[3]} ink x={b[4]}..{b[5]}')
        return
    img = Image.open(argv[0]).convert('RGB')
    y0 = int(argv[1]); y1 = int(argv[2]) if len(argv) > 2 else y0
    for y in range(y0, y1 + 1):
        lo, hi, ink = row(img, y)
        print(f'y={y} interior x={lo}..{hi} ink={ink}')


if __name__ == '__main__':
    main(sys.argv[1:])
