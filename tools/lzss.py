"""LZSS codec for PAC entries with type bit 0x10000 (docs/re/archives.md).

Stream: u32 decompressed size, then Okumura LZSS: 4096-byte ring zero-filled, write pos 0xFEE, flag byte LSB first,
bit 1 = literal byte, bit 0 = 2-byte ref (offset = b0 | (b1 & 0xF0) << 4, length = (b1 & 0x0F) + 3).
"""
import struct

N, F, THRESHOLD = 4096, 18, 2


def decompress(src):
    size = struct.unpack_from('<I', src, 0)[0]
    ring = bytearray(N)
    r, pos = N - F, 4
    out = bytearray()
    while len(out) < size:
        flags = src[pos]; pos += 1
        for b in range(8):
            if len(out) >= size:
                break
            if flags >> b & 1:
                c = src[pos]; pos += 1
                out.append(c); ring[r] = c; r = (r + 1) & (N - 1)
            else:
                b0, b1 = src[pos], src[pos + 1]; pos += 2
                off = b0 | (b1 & 0xF0) << 4
                for k in range((b1 & 0x0F) + THRESHOLD + 1):
                    c = ring[(off + k) & (N - 1)]
                    out.append(c); ring[r] = c; r = (r + 1) & (N - 1)
    return bytes(out), pos


def compress(data):
    """Okumura's LZSS.C encoder (binary-tree match finder), ported for byte-identical output."""
    text = bytearray(N + F - 1)
    lson = [N] * (N + 1)
    rson = [N] * (N + 257)
    dad = [N] * (N + 1)
    st = {'pos': 0, 'len': 0}

    def insert(r):
        cmp = 1
        p = N + 1 + text[r]
        rson[r] = lson[r] = N
        st['len'] = 0
        while True:
            if cmp >= 0:
                if rson[p] != N:
                    p = rson[p]
                else:
                    rson[p] = r; dad[r] = p; return
            else:
                if lson[p] != N:
                    p = lson[p]
                else:
                    lson[p] = r; dad[r] = p; return
            i = 1
            while i < F:
                cmp = text[r + i] - text[p + i]
                if cmp != 0:
                    break
                i += 1
            if i > st['len']:
                st['pos'] = p; st['len'] = i
                if i >= F:
                    break
        dad[r] = dad[p]; lson[r] = lson[p]; rson[r] = rson[p]
        dad[lson[p]] = r; dad[rson[p]] = r
        if rson[dad[p]] == p:
            rson[dad[p]] = r
        else:
            lson[dad[p]] = r
        dad[p] = N

    def delete(p):
        if dad[p] == N:
            return
        if rson[p] == N:
            q = lson[p]
        elif lson[p] == N:
            q = rson[p]
        else:
            q = lson[p]
            if rson[q] != N:
                while rson[q] != N:
                    q = rson[q]
                rson[dad[q]] = lson[q]; dad[lson[q]] = dad[q]
                lson[q] = lson[p]; dad[lson[p]] = q
            rson[q] = rson[p]; dad[rson[p]] = q
        dad[q] = dad[p]
        if rson[dad[p]] == p:
            rson[dad[p]] = q
        else:
            lson[dad[p]] = q
        dad[p] = N

    out = bytearray(struct.pack('<I', len(data)))
    code = bytearray([0])
    mask = 1
    s, r = 0, N - F
    src = 0
    ln = 0
    while ln < F and src < len(data):
        text[r + ln] = data[src]; src += 1; ln += 1
    if ln == 0:
        return bytes(out)
    for i in range(1, F + 1):
        insert(r - i)
    insert(r)
    while ln > 0:
        if st['len'] > ln:
            st['len'] = ln
        if st['len'] <= THRESHOLD:
            st['len'] = 1
            code[0] |= mask
            code.append(text[r])
        else:
            code.append(st['pos'] & 0xFF)
            code.append(((st['pos'] >> 4) & 0xF0) | (st['len'] - (THRESHOLD + 1)))
        mask = (mask << 1) & 0xFF
        if mask == 0:
            out += code
            code = bytearray([0]); mask = 1
        last = st['len']
        i = 0
        while i < last and src < len(data):
            delete(s)
            c = data[src]; src += 1
            text[s] = c
            if s < F - 1:
                text[s + N] = c
            s = (s + 1) & (N - 1); r = (r + 1) & (N - 1)
            insert(r)
            i += 1
        while i < last:
            delete(s)
            s = (s + 1) & (N - 1); r = (r + 1) & (N - 1)
            ln -= 1
            if ln:
                insert(r)
            i += 1
    if len(code) > 1:
        out += code
    return bytes(out)
