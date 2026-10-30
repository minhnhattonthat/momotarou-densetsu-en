"""Regressions found by comparing complete album captures with the original cards."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import cards  # noqa: E402

pytestmark = pytest.mark.skipif(not (ROOT / 'work/disc/tree/0/30EV/CR_PG01.PAC').exists(),
                                reason='needs the unpacked disc')


def test_horn_and_inner_frame_survive_lettering():
    templates = cards.templates()
    names = cards.names()
    for n, points in ((260, [(33, 55), (32, 56), (34, 57), (35, 59)]),
                      (10, [(2, y) for y in range(4, 72)])):
        pal, original = cards.card(n)
        new = cards.redraw(n, templates.get(cards.key(pal, original)), names[n - 1])
        assert all(new[y * cards.W + x] == original[y * cards.W + x] for x, y in points)
