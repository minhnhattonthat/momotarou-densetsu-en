"""English engine (tools/engine.py): VWF hook in draw_string, English glyphs, English table."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import engine  # noqa: E402
import font  # noqa: E402

EXE = ROOT / 'work/disc/tree/SLPS_017.85'
pytestmark = pytest.mark.skipif(not EXE.is_file(), reason='needs the unpacked disc (tools/build.py)')


@pytest.fixture(scope='module')
def exe():
    return engine.patch_exe(EXE.read_bytes())


def test_nothing_else_enters_freed_block(exe):
    """The old sheet 1 paths (HOOK..FREE1_END, DIGRAPH..FREE2_END) are reused: no jump or branch anywhere in the EXE
    may land in them except the patched ones that enter the hooks and the VWF hook's own branch."""
    hits = {}
    ws = struct.unpack_from(f'<{(len(exe) - 0x800) // 4}I', exe, 0x800)
    for k, w in enumerate(ws):
        pc = 0x80010000 + 4 * k
        op = w >> 26
        if op in (2, 3):
            t = (pc & 0xF0000000) | (w & 0x3FFFFFF) << 2
        elif op in (1, 4, 5, 6, 7):
            t = pc + 4 + ((w & 0xFFFF) - (0x10000 if w & 0x8000 else 0)) * 4
        else:
            continue
        for lo, hi in ((engine.HOOK, engine.FREE1_END), (engine.DIGRAPH, engine.FREE2_END)):
            if lo <= t < hi:
                hits.setdefault(lo, []).append(pc)
    assert hits == {engine.HOOK: [0x8003E258, engine.HOOK + 4 * [i.split()[0] for i in engine.hook_asm()].index('beqz')],
                    engine.DIGRAPH: [0x8003E430]}


def test_no_load_delay_hazard(exe):
    """R3000: the instruction after a load still sees the old register (unicorn doesn't model it; a hook that read
    t0 right after lhu t0 kept the 13 px pitch in-game)."""
    from capstone import CS_ARCH_MIPS, CS_MODE_LITTLE_ENDIAN, CS_MODE_MIPS32, Cs
    cs = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN)
    cs.detail = True
    ins = []
    for start, n in ((engine.HOOK, len(engine.hook_asm())), (engine.DIGRAPH, len(engine.digraph_asm()))):
        o = start - engine.EXE_BASE
        ins.append(list(cs.disasm(exe[o:o + 4 * n], start)))
        assert len(ins[-1]) == n
    for a, b in [p for block in ins for p in zip(block, block[1:])]:
        if a.mnemonic in ('lb', 'lbu', 'lh', 'lhu', 'lw'):
            loaded = a.op_str.split(',')[0]
            assert loaded not in b.op_str.split(',', 1)[-1], (hex(a.address), a.op_str, b.op_str)


UC = []


def run_glyph(exe, code, x=100):
    """Run draw_string's glyph path for one code under unicorn; return (new x, tpage, u, v, clut add)."""
    from unicorn import UC_ARCH_MIPS, UC_MODE_LITTLE_ENDIAN, UC_MODE_MIPS32, Uc
    from unicorn.mips_const import (UC_MIPS_REG_A0, UC_MIPS_REG_GP, UC_MIPS_REG_PC, UC_MIPS_REG_S1,
                                    UC_MIPS_REG_S2, UC_MIPS_REG_S3, UC_MIPS_REG_V0)
    if not UC:                                  # one instance: each mem_map logs a handled access violation on Windows
        UC.append(Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 | UC_MODE_LITTLE_ENDIAN))
        UC[0].mem_map(0, 0x200000)              # kseg0 0x80000000 fetches/loads hit physical 0; the mem_* API doesn't
    mu = UC[0]
    mu.mem_write(0, bytes(0x200000))
    mu.mem_write(0x10000, exe[0x800:])
    gp, ctx, prim, s = 0x80180000, 0x80181000, 0x80182000, 0x80183000
    mu.mem_write(gp + 0x3C8 & 0x1FFFFF, struct.pack('<I', prim))
    mu.mem_write(gp + 0x3E4 & 0x1FFFFF, struct.pack('<HH', x, 50))
    mu.mem_write(s & 0x1FFFFF, struct.pack('<HH', code, 0x8000))
    for r, v in ((UC_MIPS_REG_GP, gp), (UC_MIPS_REG_S1, ctx), (UC_MIPS_REG_S2, s), (UC_MIPS_REG_S3, 12)):
        mu.reg_write(r, v)
    mu.emu_start(0x8003E168, engine.TAIL, count=200)
    assert mu.reg_read(UC_MIPS_REG_PC) == engine.TAIL
    u, v = mu.mem_read(prim + 0xE & 0x1FFFFF, 2)
    clut = struct.unpack('<H', mu.mem_read(prim + 0x12 & 0x1FFFFF, 2))[0]
    return mu.reg_read(UC_MIPS_REG_A0), mu.reg_read(UC_MIPS_REG_V0), u, v, clut


def test_glyph_path(exe):
    w = engine.widths()
    for ch in 'AiW ~':
        code = engine.EN_BASE + ord(ch) - 0x20
        cell = code & 0x1FF
        assert run_glyph(exe, code) == (100 + w[ord(ch) - 0x20], 0x1E, cell % 21 * 12, cell // 21 * 12, 0x1F1)
    # Japanese glyphs keep their 13 px pitch, sheet 0 and sheet 1, plane 0 and 1
    assert run_glyph(exe, 0x02AE)[:4] == (113, 0x1E, 0xAE % 21 * 12, 0xAE // 21 * 12)
    assert run_glyph(exe, 0x1078)[:4] == (113, 0x1D, 0x78 % 21 * 12, 0x78 // 21 * 12)
    assert run_glyph(exe, 0x002B)[4] == 0x1F0


def test_font_cells_were_blank_and_now_hold_glyphs():
    old = font.pages()[3]
    new = font.pages_from(engine.patch_font(font.FONT_PAC.read_bytes()))
    pages = font.pages()
    assert all((a == b).all() for a, b in zip(pages[:2], new[:2]))
    # sheet 1 plane 0: only the 8x8 HUD label cells (体 技 段 -> HP SP Lv) are redrawn
    diff = pages[2] != new[2]
    ys, xs = diff.nonzero()
    assert set(ys) <= set(range(engine.SMALL_Y, engine.SMALL_Y + 8)) and {x // 8 for x in xs} == set(engine.SMALL)
    lo = (engine.EN_BASE & 0x1FF)
    for i in range(engine.LAST - engine.FIRST + 1):
        c = lo + i
        sl = (slice(c // 21 * 12, c // 21 * 12 + 12), slice(c % 21 * 12, c % 21 * 12 + 12))
        assert not old[sl].any()
        assert new[3][sl].any() == (i != 0), chr(engine.FIRST + i)


def test_table():
    b = engine.table(pairs=False).encode('Hi, [x]{n}{end}')
    assert struct.unpack('<7H', b[:14]) == tuple(engine.EN_BASE + ord(c) - 0x20 for c in 'Hi, [x]')
    assert b[14:] == b'\x01\x80\x00\x80'
    b = engine.table().encode('Hi, [x]{n}A{str}{end}')
    pair = lambda s: 0x8000 | ord(s[0]) << 7 | ord(s[1])
    assert struct.unpack(f'<{len(b) // 2}H', b) == (pair('Hi'), pair(', '), pair('[x'), engine.EN_BASE + 0x3D,
                                                    0x8001, engine.EN_BASE + 0x21, 0x8007, 0x8000)


def run_string(exe, codes, x=100):
    """Run draw_string on a u16 string under unicorn, with the window-list call (0x8003F2AC) stubbed to record each
    queued glyph sprite; return [(x, u, v, tpage)] per glyph."""
    from unicorn import UC_ARCH_MIPS, UC_HOOK_CODE, UC_MODE_LITTLE_ENDIAN, UC_MODE_MIPS32, Uc
    from unicorn.mips_const import (UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2, UC_MIPS_REG_A3, UC_MIPS_REG_GP,
                                    UC_MIPS_REG_PC, UC_MIPS_REG_RA, UC_MIPS_REG_SP)
    if not UC:
        UC.append(Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 | UC_MODE_LITTLE_ENDIAN))
        UC[0].mem_map(0, 0x200000)
    mu = UC[0]
    mu.mem_write(0, bytes(0x200000))
    mu.mem_write(0x10000, exe[0x800:])
    gp, win, ctx, prim, s, stop = 0x80180000, 0x80181000, 0x80182000, 0x80183000, 0x80184000, 0x80001000
    P = lambda a: a & 0x1FFFFF
    mu.mem_write(P(gp + 0x3C8), struct.pack('<I', prim))
    mu.mem_write(P(gp + 0x3E4), struct.pack('<HH', x, 50))
    mu.mem_write(P(s), struct.pack(f'<{len(codes)}H', *codes))
    out = []

    def stub(uc, addr, size, _):
        if addr == 0x8003F2AC:
            p = uc.reg_read(UC_MIPS_REG_A2)
            if uc.reg_read(UC_MIPS_REG_A3) == 0:
                px = struct.unpack('<h', uc.mem_read(P(p + 4), 2))[0] + 0xA0
                u, v = uc.mem_read(P(p + 0xE), 2)
                out.append((px, u, v, struct.unpack('<H', uc.mem_read(P(p + 0xC), 2))[0]))
            uc.reg_write(UC_MIPS_REG_PC, uc.reg_read(UC_MIPS_REG_RA))
    h = mu.hook_add(UC_HOOK_CODE, stub, begin=0x8003F2AC, end=0x8003F2AC)
    for r, v in ((UC_MIPS_REG_GP, gp), (UC_MIPS_REG_A0, win), (UC_MIPS_REG_A1, ctx), (UC_MIPS_REG_A2, s),
                 (UC_MIPS_REG_SP, 0x801FF000), (UC_MIPS_REG_RA, stop)):
        mu.reg_write(r, v)
    mu.emu_start(engine.DRAW_STRING, stop, count=20000)
    mu.hook_del(h)
    assert mu.reg_read(UC_MIPS_REG_PC) == stop and mu.reg_read(UC_MIPS_REG_SP) == 0x801FF000
    return out


def test_draw_string_digraphs(exe):
    """'Hi' as one digraph code + 'W' + 'ok' draws the same sprites as the five single glyphs."""
    t1, t2 = engine.table(pairs=False), engine.table()
    one = lambda t, s: list(struct.unpack(f'<{len(t.encode(s)) // 2}H', t.encode(s)))
    single, paired = one(t1, 'Hi Wok{end}'), one(t2, 'Hi Wok{end}')
    assert len(paired) < len(single)
    a, b = run_string(exe, single), run_string(exe, paired)
    w = engine.widths()
    assert a == b and [g[0] for g in a] == [100 + sum(w[ord(c) - 0x20] for c in 'Hi Wok'[:i]) for i in range(6)]
    assert run_string(exe, [0x02AE, 0x002B, 0x8000]) == [(100, 0xAE % 21 * 12, 0xAE // 21 * 12, 0x1E),
                                                         (113, 0x2B % 21 * 12, 0x2B // 21 * 12, 0x1D)]
