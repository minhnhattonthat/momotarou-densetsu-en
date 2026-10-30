"""Insert: script/ -> replaced disc files for tools/build.py (docs/re/text.md §Script, docs/re/engine.md).

    files(marker_build=False) -> {disc path: bytes}

Authored `en` is word-wrapped and paged by tools/layout.py first (qa overrides and markers go in as written).
A table with any `en` is rebuilt from its doc (`en`, else the original `jp` bytes) and written to every `copies`
location; overlay strings are written in place (`max` bytes), or packed into a shared pool and repointed when only
pointer words reach them (repacked). The EXE always gets the engine hook and FONT.PAC the
English glyphs; graphics text gets tools/gfx_en.py's redrawn images. marker_build=True gives every non-data string `[n.i]` + filler of the Japanese line's pixel width
(phase 5 marker build): n = the doc's number in docs() order, i = the string index; build/markers.tsv maps n back.
"""
import hashlib
import re
import struct
from pathlib import Path

import engine
import extract
import gfx_en
import layout
import lzss
import pac
from write_audit import Audit, Buffer

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / 'work/disc/tree'
EN = engine.table()
# drawn glyph by glyph by the effect 0x80022750 (glyph_prim, no digraph hook): single glyph codes only
SINGLE = {'SMAP16_36:46c4'}
EN1 = engine.table(pairs=False)
# Word Maze splits these answers into individual letter clues and compares them to keyboard input.
# Reserve a new pool beyond the overlay's code/data/BSS (original ends +0x2628).
WORD_MAZE = 'HMAP2606_65'
WORD_MAZE_POOL, WORD_MAZE_END = 0x3000, 0x4000
FONT = '0/03FONT/FONT.PAC'
EXE = 'SLPS_017.85'
FILLER = 'The quick brown fox jumps over the lazy dog. '
JP_W = {'{sp8}': 8, '{sp13}': 13}     # Japanese spaces: part of the text run they sit in
# Size gate (docs/re/engine.md §Load buffers): 0x10D table slot by param & 0xFF -> bytes to the next thing in RAM.
SLOT_LIMIT = {1: 0x4000, 2: 0x8000, 3: 0x4000, 4: 0x2A00, 5: 0x1600, 6: 0x8000, 7: 0x8000}
BATTLE_LIMIT = 20542                  # type 0x116 load buffer not traced: the largest JP table is the known-safe bound
SHOP_LIMIT = 0xB000                   # SHOP.MMB at 0x80155000, map dialogue slot at 0x80160000
PAC_LIMIT = 0x38000                   # whole map PAC at 0x80110000, decompress temp at 0x80148000
WIDTH = engine.widths()


def docs():
    return [(p.relative_to(ROOT / 'script').as_posix(), extract.load(p))
            for p in sorted((ROOT / 'script').rglob('*.json'))]


def text_width(s):
    return sum(WIDTH[ord(c) - engine.FIRST] for c in s)


def fill(px):
    """Filler text at most px wide."""
    out = ''
    while text_width(out + FILLER[len(out) % len(FILLER)]) <= px:
        out += FILLER[len(out) % len(FILLER)]
    return out.rstrip()


def marker(tag, jp, max_chars=None):
    """tag + filler, keeping jp's control codes; each text run between them becomes filler of its JP pixel width
    (13 px per glyph). The tag goes at the start of the first run and may overflow a short one."""
    items = []                     # control tokens and pixel widths of the text runs between them
    for tok in re.split(r'(\{\w+(?::[0-9A-Fa-f]*)?\}|\{sp8\}|\{sp13\})', jp):
        if tok.startswith('{') and tok not in JP_W:
            items.append(tok)
        elif tok:
            px = JP_W.get(tok, 13 * len(tok))
            if items and isinstance(items[-1], int):
                items[-1] += px
            else:
                items.append(px)
    if not any(isinstance(t, int) for t in items):
        items.insert(0, 0)
    out, tagged = [], False
    for t in items:
        if isinstance(t, str):
            out.append(t)
        elif not tagged:
            head = f'{tag} '
            out.append((head + fill(t - text_width(head))).rstrip())
            tagged = True
        else:
            out.append(fill(t))
    text = ''.join(out)
    if max_chars is not None and len(EN.encode(text)) // 2 > max_chars:
        text = tag[:max_chars]
    return text


def marked(n, doc):
    """A copy of doc with marker text in `en`."""
    doc = {**doc, 'strings': [dict(s) for s in doc['strings']]}
    for i, s in enumerate(doc['strings']):
        if 'jp' in s and 'data' not in s:
            s['en'] = f'[{n}.{i}]' if s['id'] in SINGLE else marker(f'[{n}.{i}]', s['jp'],
                                                                         s['max'] // 2 - 1 if 'max' in s else None)
    return doc


def laid_out(doc):
    """A copy of doc whose authored `en` is word-wrapped and paged like its `jp` (tools/layout.py)."""
    strs = []
    for s in doc['strings']:
        if s.get('en') and 'jp' in s:
            s = {**s, 'en': layout.layout(s['en'], s['jp'], layout.box(s['id'], s['jp']))[0]}
        strs.append(s)
    return {**doc, 'strings': strs}


def repacked(doc, b, audit=None):
    """Overlay strings reached only through pointer words (HMAP2606 proverbs, EXE name-entry labels) share one pool:
    pack them end to end (`en`, else the original bytes) and repoint, so a long line borrows a short one's slack."""
    audit = audit if audit is not None else Buffer(b, doc['id'])
    b = audit.data
    ss, orig, at = doc['strings'], audit.original, int(doc['base'], 16)
    assert all(a['off'] + a['max'] == c['off'] for a, c in zip(ss, ss[1:])), doc['id']
    pos, end = ss[0]['off'], ss[-1]['off'] + ss[-1]['max']
    maze = doc['id'] == WORD_MAZE
    if maze:
        assert len(orig) <= WORD_MAZE_POOL
        audit.put(len(orig), bytes(WORD_MAZE_POOL - len(orig)), 'word-maze:pool-gap', append=True)
        pos, end = WORD_MAZE_POOL, WORD_MAZE_END
    for s in ss:
        enc = (EN1 if maze else EN).encode(s['en'] + '{end}') if s.get('en') else orig[s['off']:s['off'] + 2 * len(extract.string_words(orig, s['off']))]
        assert pos + len(enc) <= end, (doc['id'], s['id'], pos + len(enc) - end, 'bytes over the pool')
        audit.put(pos, enc, s['id'], append=maze)
        for p in s['ptrs']:
            audit.put(int(p[5:], 16), struct.pack('<I', at + pos), f"{s['id']}:{p}")
        pos += len(enc)
    if pos < end and not maze:
        audit.put(pos, bytes(end - pos), f"{doc['id']}:pool-padding")
    audit.verify(b)
    return bytes(b)


def compressed(b):
    """lzss.compress(b), kept in build/lzss/<sha1> across runs (pure-Python LZSS: the 240 cards take minutes)."""
    p = ROOT / 'build/lzss' / hashlib.sha1(b).hexdigest()
    if p.exists():
        return p.read_bytes()
    out = lzss.compress(b)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(out)
    return out


def files(marker_build=False, qa=None, audit=None):
    """{disc path: bytes} for build.build. qa: {string id: text} overrides (stress lines, torture line)."""
    entries, raw = {}, {}          # {pac path: {entry: decompressed bytes}}, {raw file: bytes}
    audit = audit if audit is not None else Audit()

    def buffer(path, ent):
        data = (TREE / path).read_bytes()
        loc = path if ent is None else f'{path}:{ent}'
        original = data if ent is None else extract.blob(data, *pac.entries(data)[ent])
        return audit.buffer(loc, original)

    def base(path, ent):
        if ent is None:
            return raw.get(path) or (TREE / path).read_bytes()
        cur = entries.setdefault(path, {})
        if ent not in cur:
            data = (TREE / path).read_bytes()
            cur[ent] = extract.blob(data, *pac.entries(data)[ent])
        return cur[ent]

    def put(path, ent, b):
        if ent is None:
            raw[path] = b
        else:
            entries.setdefault(path, {})[ent] = b

    tags = []
    for n, (rel, doc) in enumerate(docs()):
        tags.append(f'{n}\t{rel}')
        if marker_build:
            doc = marked(n, doc)
        else:
            doc = laid_out(doc)
        if qa and any(s['id'] in qa for s in doc['strings']):
            doc = {**doc, 'strings': [{**s, 'en': qa[s['id']]} if s['id'] in qa else s for s in doc['strings']]}
        if not any(s.get('en') for s in doc['strings']):
            continue
        for loc in doc['copies']:
            path, _, ent = loc.partition(':')
            ent = int(ent) if ent else None
            buf = buffer(path, ent)
            if doc['kind'] == 'table':
                buf.put(0, extract.build_table(doc, 'en', EN), doc['id'], replace=True)
                put(path, ent, bytes(buf.data))
                continue
            b = bytearray(base(path, ent))
            if all(p.startswith('word@') for s in doc['strings'] for p in s['ptrs']):
                put(path, ent, repacked(doc, b, buf))
                continue
            for s in doc['strings']:
                if s.get('en'):
                    enc = (EN1 if s['id'] in SINGLE else EN).encode(s['en'] + '{end}')
                    assert len(enc) <= s['max'], (s['id'], len(enc), s['max'])
                    buf.put(s['off'], enc + bytes(s['max'] - len(enc)), s['id'])
            put(path, ent, bytes(buf.data))
    if marker_build:
        (ROOT / 'build').mkdir(exist_ok=True)
        (ROOT / 'build/markers.tsv').write_text('\n'.join(tags) + '\n', encoding='utf-8', newline='\n')
    else:
        for loc, b in gfx_en.entries().items():
            path, ent = loc.rsplit(':', 1)
            buffer('0/' + path, int(ent)).put(0, b, f'graphics:{loc}', replace=True)
            put('0/' + path, int(ent), b)

    for loc, off, old, new in [] if marker_build else engine.OVERLAY_PATCH:
        path, ent = loc.rsplit(':', 1)
        buf = buffer(path, int(ent))               # shared with the string pass (HMAP2606:65 proverb pool)
        buf.put(off, new, f'overlay-patch:{loc}:{off:#x}', expected=old)
        put(path, int(ent), bytes(buf.data))
    raw[EXE] = engine.patch_exe(base(EXE, None), buffer(EXE, None))
    cache = {}
    for path, ents in entries.items():
        items = pac.unpack((TREE / path).read_bytes())
        for i, b in ents.items():
            typ, _, extra = items[i]
            lim = {0x10D: SLOT_LIMIT.get(extra[0]), 0x116: BATTLE_LIMIT}.get(typ & 0xFFFF)
            assert marker_build or lim is None or len(b) <= lim, (f'{path}:{i}', len(b), 'bytes over slot', lim)
            if typ & 0x10000:
                b = cache[b] if b in cache else cache.setdefault(b, compressed(b))
            items[i] = (typ, b, extra)
        raw[path] = pac.pack(items)
        assert marker_build or len(raw[path]) < PAC_LIMIT, (path, len(raw[path]), 'bytes, PAC over the load buffer')
    assert marker_build or len(raw.get('0/03FONT/SHOP.MMB', b'')) <= SHOP_LIMIT, 'SHOP.MMB over its buffer'
    raw[FONT] = engine.patch_font(base(FONT, None), lambda ent: buffer(FONT, ent))
    # Validate against the final compressed containers, not merely the work buffers.
    for loc, buf in audit.buffers.items():
        path, _, ent = loc.partition(':')
        final = raw[path]
        if ent:
            final = extract.blob(final, *pac.entries(final)[int(ent)])
        buf.verify(final)
    audit.save(ROOT / 'build/insert-writes.jsonl')
    return raw
