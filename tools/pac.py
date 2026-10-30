"""PAC archive reader (Momotarou Densetsu PS1). See docs/re/archives.md.

Header: N entries of 24 bytes {u32 offset, u32 size, u32 type, 12 zero bytes}; the first offset ends the table.
"""
import struct
import sys


def entries(data):
    first = struct.unpack_from('<I', data, 0)[0]
    out = []
    for i in range(first // 24):
        off, size, typ = struct.unpack_from('<III', data, i * 24)
        out.append((off, size, typ))
    return out


def unpack(data):
    """[(type, bytes, extra)] per entry. extra = header bytes 12-24 kept raw (u32 at 12 is a per-entry id/param,
    e.g. a battle sprite index). An all-zero entry comes back as (0, b'', zeros) and repacks as zeros."""
    return [(typ, data[off:off + size], data[i * 24 + 12:i * 24 + 24])
            for i, (off, size, typ) in enumerate(entries(data))]


def pack(items):
    """Inverse of unpack: header, then entries back to back (no padding)."""
    head, body = bytearray(), bytearray()
    first = 24 * len(items)
    for typ, blob, extra in items:
        off = first + len(body) if typ or blob else 0
        head += struct.pack('<III', off, len(blob), typ) + extra
        body += blob
    return bytes(head + body)


def main(paths):
    for p in paths:
        data = open(p, 'rb').read()
        print(f'== {p} ({len(data)} bytes)')
        for i, (off, size, typ) in enumerate(entries(data)):
            print(f'  {i:3d} off={off:#08x} size={size:#07x} type={typ:#010x} head={data[off:off + 8].hex()}')


if __name__ == '__main__':
    main(sys.argv[1:])
