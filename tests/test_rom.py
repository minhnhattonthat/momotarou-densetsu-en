import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402

BIN = ROOT / "rom" / "Momotarou Densetsu (Japan).bin"


@pytest.mark.skipif(not BIN.is_file(), reason="no ROM dump in rom/")
def test_rom_matches_sha1():
    check_rom.check()
