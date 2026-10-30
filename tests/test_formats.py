"""PAC / LZSS / font-code / text-table checks on the unpacked disc (work/disc/tree, docs/re/archives.md)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402
import lzss  # noqa: E402
import pac  # noqa: E402

TREE = ROOT / "work/disc/tree"
FONT_PAC = TREE / "0/03FONT/FONT.PAC"
needs_tree = pytest.mark.skipif(not FONT_PAC.is_file(), reason="disc not unpacked (dumpsxiso, docs/re/archives.md)")


def test_lzss_roundtrip_synthetic():
    for data in (b"", b"a", b"abcabcabcabc" * 50, bytes(range(256)) * 9, b"\x00" * 5000):
        assert lzss.decompress(lzss.compress(data))[0] == data


def test_font_code_mapping():
    assert font.code_to_index(0x002B) == 0x2B
    assert font.code_to_index(0x1078) == 441 + 0x78          # 々: sheet 0 plane 1
    assert font.code_to_index(0x02AE) == 2 * 441 + 0xAE      # 昔: sheet 1 plane 0
    for n in range(4 * 441):
        assert font.code_to_index(font.index_to_code(n)) == n


@needs_tree
@pytest.mark.parametrize("name", ["0/03FONT/FONT.PAC", "0/06CITY/SMAP00.PAC", "0/20BTL/BM000.PAC", "0/30EV/EVTOP.PAC"])
def test_pac_entries_decompress_and_recompress_exactly(name):
    data = (TREE / name).read_bytes()
    for off, size, typ in pac.entries(data):
        if not size or not typ & 0x10000:
            continue
        blk = data[off:off + size]
        raw, used = lzss.decompress(blk)
        assert used == size
        assert lzss.compress(raw) == blk


@needs_tree
def test_text_table_decodes_known_menu_strings():
    import text
    b = text.entry(FONT_PAC, 7)
    offs = text.table_offsets(b)
    assert text.decode(b, offs[3])[0] == "ももたろう{end}"
    assert text.decode(b, offs[24])[0] == "{str}が おそってきた！{end}"
