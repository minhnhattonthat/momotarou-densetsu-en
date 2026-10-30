"""Hudson TIM variant: magic 0x11 = CLUT-only TIM, 0x12 = image-only TIM (docs/re/archives.md).

Layout is standard TIM after the magic: u32 flags, then one block {u32 size, u16 x, y, w, h, data}.
"""
import struct


def block(data):
    magic, flags, size, x, y, w, h = struct.unpack_from('<IIIHHHH', data, 0)
    return magic, flags, x, y, w, h, data[20:20 + size - 12]


def clut(data, n=0):
    """Palette n (16 colours) of a 0x11 block as RGBA tuples."""
    *_, w, h, raw = block(data)
    out = []
    for i in range(16):
        c = struct.unpack_from('<H', raw, (n * 16 + i) * 2)[0]
        r, g, b = (c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3
        out.append((r, g, b, 0 if c == 0 else 255))
    return out


def image4(data, pal=None):
    """4bpp 0x12 block to a PIL image (grey ramp when no palette)."""
    from PIL import Image
    magic, flags, x, y, w, h, raw = block(data)
    pal = pal or [(i * 17, i * 17, i * 17, 255) for i in range(16)]
    img = Image.new('RGBA', (w * 4, h))
    px = img.load()
    for yy in range(h):
        for xx in range(w * 2):
            b = raw[yy * w * 2 + xx]
            px[xx * 2, yy] = pal[b & 15]
            px[xx * 2 + 1, yy] = pal[b >> 4]
    return img
