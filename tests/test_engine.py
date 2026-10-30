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
    """The old sheet 1 path (HOOK..0x8003E307) is reused: no jump or branch anywhere in the EXE may land in it
    except the patched sheet 0 path's jump to HOOK and the hook's own branch."""
    lo, hi = engine.HOOK, 0x8003E308
    ws = struct.unpack_from(f'<{(len(exe) - 0x800) // 4}I', exe, 0x800)
    hits = []
    for k, w in enumerate(ws):
        pc = 0x80010000 + 4 * k
        op = w >> 26
        if op in (2, 3):
            t = (pc & 0xF0000000) | (w & 0x3FFFFFF) << 2
        elif op in (1, 4, 5, 6, 7):
            t = pc + 4 + ((w & 0xFFFF) - (0x10000 if w & 0x8000 else 0)) * 4
        else:
            continue
        if lo <= t < hi:
            hits.append(pc)
    assert hits == [0x8003E258, engine.HOOK + 4 * [i.split()[0] for i in engine.hook_asm()].index('beqz')]


def test_no_load_delay_hazard(exe):
    """R3000: the instruction after a load still sees the old register (unicorn doesn't model it; a hook that read
    t0 right after lhu t0 kept the 13 px pitch in-game)."""
    from capstone import CS_ARCH_MIPS, CS_MODE_LITTLE_ENDIAN, CS_MODE_MIPS32, Cs
    cs = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN)
    cs.detail = True
    o = engine.HOOK - engine.EXE_BASE
    ins = list(cs.disasm(exe[o:o + engine.TABLE - engine.HOOK], engine.HOOK))
    for a, b in zip(ins, ins[1:]):
        if a.mnemonic in ('lb', 'lbu', 'lh', 'lhu', 'lw'):
            loaded = a.op_str.split(',')[0]
            assert loaded not in b.op_str.split(',', 1)[-1], (hex(a.address), a.op_str, b.op_str)


def run_glyph(exe, code, x=100):
    """Run draw_string's glyph path for one code under unicorn; return (new x, tpage, u, v, clut add)."""
    from unicorn import UC_ARCH_MIPS, UC_MODE_LITTLE_ENDIAN, UC_MODE_MIPS32, Uc
    from unicorn.mips_const import (UC_MIPS_REG_A0, UC_MIPS_REG_GP, UC_MIPS_REG_PC, UC_MIPS_REG_S1,
                                    UC_MIPS_REG_S2, UC_MIPS_REG_S3, UC_MIPS_REG_V0)
    mu = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 | UC_MODE_LITTLE_ENDIAN)
    mu.mem_map(0, 0x200000)                     # kseg0 0x80000000 fetches/loads hit physical 0; the mem_* API doesn't
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
    assert all((a == b).all() for a, b in zip(font.pages()[:3], new[:3]))
    lo = (engine.EN_BASE & 0x1FF)
    for i in range(engine.LAST - engine.FIRST + 1):
        c = lo + i
        sl = (slice(c // 21 * 12, c // 21 * 12 + 12), slice(c % 21 * 12, c % 21 * 12 + 12))
        assert not old[sl].any()
        assert new[3][sl].any() == (i != 0), chr(engine.FIRST + i)


def test_table():
    t = engine.table()
    b = t.encode('Hi, [x]{n}{end}')
    assert struct.unpack('<7H', b[:14]) == tuple(engine.EN_BASE + ord(c) - 0x20 for c in 'Hi, [x]')
    assert b[14:] == b'\x01\x80\x00\x80'
