"""Identity build (phase 3): disc rebuild, PAC repack, MMPS_CD.SFS regeneration (tools/build.py, docs/re/archives.md)."""
import hashlib
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import pac  # noqa: E402

TREE = build.DISC / "tree"
ORIG_SHA1 = next(l.split()[0] for l in (ROOT / "rom.sha1").read_text().splitlines() if l and not l.startswith("#"))
needs_disc = pytest.mark.skipif(not (build.DISC / "layout.xml").is_file() or not build.MKPSXISO.is_file(),
                                reason="disc not unpacked or mkpsxiso missing (docs/re/archives.md)")


def sector_data(img, lba, n):
    """User data of n Mode 2 Form 1 sectors (2352-byte raw sectors, 24-byte header)."""
    out = bytearray()
    with open(img, "rb") as f:
        for i in range(n):
            f.seek((lba + i) * 2352 + 24)
            out += f.read(2048)
    return bytes(out)


def raw_sector(img, lba):
    with open(img, "rb") as f:
        f.seek(lba * 2352 + 16)
        return f.read(2336)


@needs_disc
def test_identity_build_is_byte_identical(tmp_path):
    out = tmp_path / "id.bin"
    build.build({}, out)
    with open(out, "rb") as f:
        assert hashlib.file_digest(f, "sha1").hexdigest() == ORIG_SHA1


@needs_disc
def test_sfs_follows_grown_file(tmp_path):
    font = (TREE / "0/03FONT/FONT.PAC").read_bytes()
    out = tmp_path / "grown.bin"
    build.build({"0/03FONT/FONT.PAC": font + bytes(5000)}, out)   # 3 sectors more: every later file moves
    old_sfs = (TREE / build.SFS).read_bytes()
    sfs = sector_data(out, 23, 4)[:len(old_sfs)]
    ents = [struct.unpack_from("<II", sfs, i * 8) for i in range(800)]
    old = [struct.unpack_from("<II", old_sfs, i * 8) for i in range(800)]
    assert ents[1] == (old[1][0], len(font) + 5000)
    assert ents[2][0] == old[2][0] + 3
    moved = 0
    for (lba, size), (olba, osize) in zip(ents[2:], old[2:]):
        if size == 0:
            continue
        assert size == osize
        moved += lba != olba
        # the new LBA holds the sector the old one did (past sync + address, so XA Form 2 sectors compare too)
        assert raw_sector(out, lba) == raw_sector(build.ROOT / "rom/Momotarou Densetsu (Japan).bin", olba)
    assert moved > 500


@needs_disc
def test_every_pac_repacks_byte_identical():
    pacs = sorted(TREE.rglob("*.PAC"))
    assert len(pacs) == 585
    for p in pacs:
        data = p.read_bytes()
        assert pac.pack(pac.unpack(data)) == data, p
