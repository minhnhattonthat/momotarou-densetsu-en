"""Phase 4: every string on the disc -> script/ (docs/re/text.md §Script).

    python -X utf8 tools/extract.py [--force]   # writes missing script/<dir>/<name>.json; --force rewrites, but
                                                # refuses while any target file holds English

Sources: string tables (PAC entries of type 0x10d/0x116 detected by content, plus SHOP.MMB) and strings inside code
overlays reached by pointers (OVERLAYS). Byte-identical tables are stored once; `copies` lists every place the insert
writes them back. `jp` omits the final {end}; build_table / overlay insert add it back.
"""
import json
import struct
import sys
from pathlib import Path

import lzss
import pac
from tbl import Table

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / 'work/disc/tree'
SCRIPT = ROOT / 'script'
TBL = Table.load(ROOT / 'tbl/jp.tbl')
RAW_TABLES = ['0/03FONT/SHOP.MMB']          # whole file is one string table
EMPTY = b'\x01\x80\x00\x80'                  # 14 map PACs carry a lone {n}{end} in place of a table (no text)

# Code overlays (PAC type 0x102) holding strings, with their load address (verified: their own data pointers land on
# function prologues and on these strings). A full sweep of every overlay, the EXE and the other files finds no other
# text (tests/test_extract.py::test_no_text_outside_script).
OVERLAYS = {
    '0/07HMAP/HMAP2606.PAC:65': 0x80168000,  # proverb card game: 41 proverbs in hiragana
    '0/06CITY/SMAP16.PAC:36': 0x80168000,    # one shopkeeper line
    '0/06WMAP/WMAP08.PAC:27': 0x80168000,    # すもも tongue-twister board: game data, not text
    'SLPS_017.85': 0x80010000 - 0x800,       # EXE (2 KB header): name-entry mode labels ひらがな/カタカナ/英数字
}
# Not extracted, handled with the name-entry screen (phase 5): the EXE's name-entry grids at file 0xD4158 (hiragana,
# pointer at 0xD44E8), 0xD4288 (katakana, 0xD44EC), then A-Z 0-9 symbols and small kana; one {end}-terminated glyph
# per cell, 0xFFFFFFFF between grids.
DATA = {'WMAP08_27:0004': 'tongue-twister board read by the minigame code; keep the Japanese'}


def blob(data, off, size, typ):
    b = data[off:off + size]
    return lzss.decompress(b)[0] if typ & 0x10000 else b


def wanted(loc, typ):
    return typ & 0xFFFF in (0x10D, 0x116) or loc in OVERLAYS


def sources(tree=TREE, want=wanted):
    """(location 'dir/FILE.PAC:entry' or 'dir/FILE', type, decompressed bytes) for the PAC entries want(loc, type)
    accepts (want=None: all of them) and the raw tables."""
    for p in sorted(tree.rglob('*.PAC')):
        data = p.read_bytes()
        rel = p.relative_to(tree).as_posix()
        for i, (o, s, t) in enumerate(pac.entries(data)):
            if s and (want is None or want(f'{rel}:{i}', t)):
                yield f'{rel}:{i}', t, blob(data, o, s, t)
    for rel in RAW_TABLES:
        yield rel, 0x10d, (tree / rel).read_bytes()
    for rel in OVERLAYS:
        if ':' not in rel:
            yield rel, 0x102, (tree / rel).read_bytes()


def string_words(b, off):
    """u16 words of the string at off up to and including 0x8000, or None if it isn't one (bad code / no end)."""
    ws = []
    while off + 2 <= len(b) and len(ws) < 4000:
        w = struct.unpack_from('<H', b, off)[0]
        ws.append(w)
        off += 2
        if w == 0x8000:
            return ws
        if w & 0x8000 and w > 0x802E or not w & 0x8000 and (w >= 0x1400 or (w & 0x1FF) >= 441):
            return None
    return None


def parse_table(b):
    """u32 offsets of a string table (docs/re/text.md), or None if b isn't one. The offset list ends at the lowest
    offset; a 2-byte gap may follow it (SMAP16.PAC:37)."""
    if len(b) < 8:
        return None
    offs, i = [], 0
    while i + 4 <= min(offs + [len(b)]):
        offs.append(struct.unpack_from('<I', b, i)[0])
        i += 4
    if min(offs) < 4 * len(offs) or max(offs) >= len(b) or any(o % 2 for o in offs):
        return None
    if any(string_words(b, o) is None for o in set(offs)):
        return None
    return offs


def decode(b, off):
    text, used = TBL.decode(b, off)
    assert text.endswith('{end}'), text
    return text[:-5], used


def name_of(loc):
    file, _, entry = loc.partition(':')
    p = Path(file)
    return (f'{p.stem}_{entry}' if entry else p.stem), p.parent.name or 'exe'


def table_doc(name, b, offs):
    """JSON doc for one table. Offsets are ascending (checked on the whole disc), so strings sit in index order."""
    first = {}
    strings = []
    for i, o in enumerate(offs):
        sid = f'{name}:{i:03d}'
        if o in first:
            strings.append({'id': sid, 'same': first[o]})
            continue
        first[o] = i
        strings.append({'id': sid, 'jp': decode(b, o)[0], 'en': ''})
    doc = {'id': name, 'kind': 'table', 'copies': []}
    pad = b[4 * len(offs):min(offs)]
    if pad:
        doc['pad'] = pad.hex()
    doc['strings'] = strings
    return doc


def build_table(doc, field='jp', tbl=TBL):
    """Bytes of a table from its doc: header, optional pad, each string (+{end}) in index order; `same` entries share
    the offset of the string they point to. field='en' falls back to jp for untranslated lines (insert, phase 7)."""
    strs = doc['strings']
    head = 4 * len(strs) + len(bytes.fromhex(doc.get('pad', '')))
    body, offs = bytearray(), []
    for s in strs:
        if 'same' in s:
            offs.append(offs[s['same']])
            continue
        offs.append(head + len(body))
        body += tbl.encode((s.get(field) or s['jp']) + '{end}')
    return struct.pack(f'<{len(offs)}I', *offs) + bytes.fromhex(doc.get('pad', '')) + bytes(body)


def text_runs(b):
    """(start, end) byte spans of u16 runs that look like text anywhere in b: 3+ glyph/control words with 4+ kana,
    ending in 0x8000. The coverage test's net for strings no table or pointer reaches."""
    n = len(b) // 2
    ws = struct.unpack_from(f'<{n}H', b, 0)
    out, start, kana = [], None, 0
    for k, w in enumerate(ws):
        if w == 0x8000:
            if start is not None and k - start >= 3 and kana >= 4:
                out.append((2 * start, 2 * k + 2))
            start, kana = None, 0
        elif w < 0x1400 and (w & 0x1FF) < 441 or 0x8001 <= w <= 0x802E:
            start = k if start is None else start
            kana += 0x2A <= w <= 0xE6
        else:
            start, kana = None, 0
    return out


def overlay_refs(b, base):
    """{offset: ['word@0x..' | 'lui@0x..']} for every in-image address a data word or a lui/addiu(ori) pair makes."""
    n = len(b) // 4
    ws = struct.unpack_from(f'<{n}I', b, 0)
    out = {}
    for k, w in enumerate(ws):
        if base <= w < base + len(b):
            out.setdefault(w - base, []).append(f'word@{4 * k:#x}')
        if w >> 26 == 0x0F:                                    # lui rt, hi
            rt = w >> 16 & 31
            for j in range(k + 1, min(n, k + 12)):
                v = ws[j]
                if v >> 26 in (0x09, 0x0D) and v >> 21 & 31 == rt:   # addiu/ori rx, rt, lo
                    lo = v & 0xFFFF
                    a = ((w & 0xFFFF) << 16) + (lo - 0x10000 if v >> 26 == 0x09 and lo & 0x8000 else lo)
                    if base <= a < base + len(b):
                        out.setdefault(a - base, []).append(f'lui@{4 * k:#x}')
    return out


def is_text(ws):
    """At least two kana/kanji glyphs and no 0x0000 word: what separates a pointed-to string from a pointer that lands
    on code or on a record table (HMAP2606's kana cell records start with 0x0000)."""
    return ws is not None and len(ws) > 1 and 0 not in ws and sum(1 for w in ws if 0x2A <= w <= 0xE6 or 0xE7 <= w & 0x13FF and w < 0x1400) >= 2


def overlay_doc(name, b, base):
    strings = []
    for off, refs in sorted(overlay_refs(b, base).items()):
        ws = string_words(b, off) if off % 2 == 0 else None
        if not is_text(ws):
            continue
        sid = f'{name}:{off:04x}'
        s = {'id': sid, 'off': off, 'max': (2 * len(ws) + 3) & ~3, 'ptrs': refs, 'jp': decode(b, off)[0], 'en': ''}
        if sid in DATA:
            s['data'] = DATA[sid]
        strings.append(s)
    return {'id': name, 'kind': 'overlay', 'base': f'{base:#x}', 'copies': [], 'strings': strings}


def extract(tree=TREE):
    """{script path (relative to script/): doc}. Also returns {location: (doc id, bytes)} for tests."""
    docs, by_bytes, located = {}, {}, {}
    for loc, typ, b in sources(tree):
        if loc in OVERLAYS:
            key = ('ovl', b)
            make = lambda n: overlay_doc(n, b, OVERLAYS[loc])
        elif typ & 0xFFFF in (0x10D, 0x116) and (offs := parse_table(b)) is not None:
            key = ('tbl', b)
            make = lambda n: table_doc(n, b, offs)
        else:
            continue
        if key not in by_bytes:
            name, folder = name_of(loc)
            by_bytes[key] = f'{folder}/{name}.json'
            docs[by_bytes[key]] = make(name)
        doc = docs[by_bytes[key]]
        doc['copies'].append(loc)
        located[loc] = (by_bytes[key], b)
    return docs, located


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def dump(doc):
    return json.dumps(doc, ensure_ascii=False, indent=1) + '\n'


def main(argv):
    force = '--force' in argv
    docs, _ = extract()
    if force:
        held = [p for p in docs if (SCRIPT / p).is_file()
                and any(s.get('en') for s in load(SCRIPT / p)['strings'])]
        if held:
            sys.exit(f'refusing --force: English in {len(held)} files, e.g. {held[0]}')
    wrote = 0
    for rel, doc in docs.items():
        out = SCRIPT / rel
        if out.is_file() and not force:
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(dump(doc), encoding='utf-8', newline='\n')
        wrote += 1
    n = sum(1 for d in docs.values() for s in d['strings'] if 'jp' in s)
    print(f'{len(docs)} files ({wrote} written), {n} strings')


if __name__ == '__main__':
    main(sys.argv[1:])
