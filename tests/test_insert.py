"""English build (tools/insert.py): every table holds all its strings, and nothing changes outside text, the engine's
patch sites and the font cells it draws (the disc-file form of romdiff's allowed-ranges check)."""
import struct
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import engine  # noqa: E402
import cards  # noqa: E402
import extract  # noqa: E402
import gfx  # noqa: E402
import gfx_en  # noqa: E402
import insert  # noqa: E402
import pac  # noqa: E402

TREE = ROOT / 'work/disc/tree'
pytestmark = pytest.mark.skipif(not (TREE / insert.EXE).is_file(), reason='needs the unpacked disc (tools/build.py)')


@pytest.fixture(scope='module')
def built():
    return insert.files()


def entry(data, i):
    return extract.blob(data, *pac.entries(data)[i])


def changed(old, new):
    assert len(old) == len(new)
    return np.flatnonzero(np.frombuffer(old, np.uint8) != np.frombuffer(new, np.uint8)).tolist()


def allowed():
    """{location: [(lo, hi)]} byte spans the insert may change; None = the whole entry (a rebuilt string table)."""
    out = {}
    for _, d in insert.docs():
        for loc in d['copies']:
            if d['kind'] == 'table':
                out[loc] = None
            else:
                out.setdefault(loc, []).extend((s['off'], s['off'] + s['max']) for s in d['strings'])
                out[loc] += [(int(p[5:], 16), int(p[5:], 16) + 4) for s in d['strings'] for p in s['ptrs']
                             if p.startswith('word@')]          # repointed by a repacked pool
    exe = out.setdefault(insert.EXE, [])
    exe += [(a - engine.EXE_BASE, a - engine.EXE_BASE + 4) for a, _, _ in engine.PATCH]
    exe += [(lo - engine.EXE_BASE, hi - engine.EXE_BASE) for lo, hi in ((engine.HOOK, engine.FREE1_END),
                                                                         (engine.DIGRAPH, engine.FREE2_END))]
    exe += [(g, g + 4 * engine.GRID_CELLS) for g in (engine.GRID_FIRST, engine.GRID_ALNUM)]
    for loc, _, edits in gfx_en.IMAGES.values():       # redrawn graphics text: pixel bytes of the declared rects
        bpp, w, _, _ = gfx.indices(gfx.entry(loc))
        out['0/' + loc] = [(20 + (y * w + x0) * bpp // 8, 20 + (y * w + x1) * bpp // 8)
                           for (x0, y0, x1, y1), *_ in edits for y in range(y0, y1)]
    x0, y0, x1, y1 = gfx_en.STAMP                        # album-cover stamp: STAMP across both 8bpp halves of the cover
    left = 0
    for loc in gfx_en.COVER:
        _, w, _, _ = gfx.indices(gfx.entry(loc))
        a, b = max(x0 - left, 0), min(x1 - left, w)
        out['0/' + loc] = [(20 + y * w + a, 20 + y * w + b) for y in range(y0, y1)] if a < b else []
        left += w
    for loc in gfx_en.BATH_LOCS:                        # bath-event band (8bpp, 256 wide)
        out['0/' + loc] = [(20 + y * 256 + x0, 20 + y * 256 + x1) for (x0, y0, x1, y1), *_ in gfx_en.BATH_WORDS
                           for y in range(y0, y1)]
    bpp, w, _, _ = gfx.indices(gfx.entry(gfx_en.CONGRATS[0]))   # celebration banner frames
    out['0/' + gfx_en.CONGRATS[0]] = [(20 + (y * w + x0) * bpp // 8, 20 + ((y * w + x1) * bpp + 7) // 8)
                                      for x0, y0, x1, y1 in gfx_en.CONGRATS[-1] for y in range(y0, y1)]
    for loc, (_, rects) in gfx_en.plates().items():     # shop-sign plates (4bpp tilesets)
        _, w, _, _ = gfx.indices(gfx.entry(loc))
        out['0/' + loc] = [(20 + (y * w + x0) // 2, 20 + (y * w + x1) // 2) for x0, y0, x1, y1 in rects
                           for y in range(y0, y1)]
    for n in range(1, 298):                             # redrawn cards: pixel data only, never the TIM header
        out['0/' + cards.loc(n)] = [(20, 20 + cards.W * cards.H)]
    return out


def font_cell_ok(off, stride):
    """A changed byte of the font sheet TIM lies in an English cell (12x12) or a redrawn 8x8 HUD label cell."""
    y, x = divmod(off - 20, stride)
    x *= 2
    for c in range(engine.FIRST, engine.LAST + 1):
        cell = engine.EN_BASE - 0x1200 + c - engine.FIRST
        if cell // 21 * 12 <= y < cell // 21 * 12 + 12 and cell % 21 * 12 <= x < cell % 21 * 12 + 12:
            return True
    return engine.SMALL_Y <= y < engine.SMALL_Y + 8 and any(i * 8 <= x < i * 8 + 8 for i in engine.SMALL)


def test_only_text_and_engine_bytes_change(built):
    ok = allowed()
    bad = []
    for path, new in built.items():
        old = (TREE / path).read_bytes()
        if not path.endswith('.PAC'):
            spans = ok.get(path, [])
            if spans is not None:
                bad += [(path, hex(i)) for i in changed(old, new) if not any(lo <= i < hi for lo, hi in spans)]
            continue
        uo, un = pac.unpack(old), pac.unpack(new)
        assert len(uo) == len(un) and all(a[0] == b[0] and a[2] == b[2] for a, b in zip(uo, un)), path
        for i, ((_, ra, _), (_, rb, _)) in enumerate(zip(uo, un)):
            if ra == rb:                    # untouched entries keep their stored (compressed) bytes
                continue
            a, b = entry(old, i), entry(new, i)
            loc = f'{path}:{i}'
            if path == insert.FONT and i == engine.FONT_ENTRY:
                stride = struct.unpack_from('<H', a, 16)[0] * 2
                bad += [(loc, hex(o)) for o in changed(a, b) if not font_cell_ok(o, stride)]
            elif loc not in ok:
                bad.append((loc, 'changed but holds no text'))
            elif ok[loc] is not None:
                bad += [(loc, hex(o)) for o in changed(a, b) if not any(lo <= o < hi for lo, hi in ok[loc])]
    assert not bad, bad[:20]


def test_every_table_holds_all_its_strings(built):
    """Each copy of each table holds, at each string's offset, the laid-out English (else the Japanese) bytes."""
    for _, doc in insert.docs():
        if doc['kind'] != 'table' or not any(s.get('en') for s in doc['strings']):
            continue
        want = insert.laid_out(doc)['strings']
        for loc in doc['copies']:
            path, _, ent = loc.partition(':')
            b = entry(built[path], int(ent)) if ent else built[path]
            offs = struct.unpack_from(f'<{len(want)}I', b, 0)
            for s, o in zip(want, offs):
                if 'same' in s:
                    continue
                exp = insert.EN.encode(s['en'] + '{end}') if s.get('en') else extract.TBL.encode(s['jp'] + '{end}')
                assert b[o:o + len(exp)] == exp, (loc, s['id'])
