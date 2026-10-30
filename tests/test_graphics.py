"""Runtime graphics regressions, checked in the source texture and the engine's palette."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import gfx  # noqa: E402
import gfx_en  # noqa: E402

pytestmark = pytest.mark.skipif(not (ROOT / 'work/disc/tree/0/06DAN01/DMAP03.PAC').exists(),
                                reason='needs the unpacked disc')


def test_oni_flip_highlight_covers_green_letters():
    raw, pixels = gfx_en.redraw('cave_panels')
    palettes = gfx.entry('06DAN01/DMAP03.PAC:6')
    base = gfx.image(raw, gfx.palette(palettes, 0), pixels)
    highlight = gfx.image(raw, gfx.palette(palettes, 6), pixels)
    for y in range(40):
        for x in range(48):
            r, g, b, _ = base.getpixel((192 + x, y))
            if g > max(r, b) * 1.5:
                assert highlight.getpixel((192 + x, 96 + y))[3] == 255, (x, y)
