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
                      (148, [(70, 80), (75, 80), (65, 85)]),  # grey axe beside the name
                      (1, [(35, 60), (36, 62), (22, 68)]),  # topknot and headband
                      (3, [(56, 59), (30, 65), (48, 67)]),  # Urashima's hair under the old flavour text
                      (4, [(40, 59), (25, 68)]),  # crown and hair
                      (6, [(25, 68), (46, 69)]),  # Monkey's head outline
                      (8, [(20, 70), (48, 70)]),  # round figures' top outlines
                      (12, [(35, 69), (40, 70)]),  # Jizo's head outline
                      (28, [(54, 59), (30, 68)]),  # statue crown spikes
                      (93, [(8, 60), (20, 60), (30, 60)]),  # ornament below the stat lettering
                      (97, [(10, 60), (22, 60)]),  # flower and fingertips
                      (109, [(29, 48), (29, 60), (30, 45)]),  # Enma's horn beside the stat labels
                      (86, [(66, 6), (88, 8)]),  # the circle's outer outline is not lettering
                      (10, [(2, y) for y in range(4, 72)] + [(3, y) for y in range(4, 62)] +
                       [(x, 3) for x in range(4, 32)])):
        pal, original = cards.card(n)
        new = cards.redraw(n, templates.get(cards.key(pal, original)), names[n - 1])
        assert all(new[y * cards.W + x] == original[y * cards.W + x] for x, y in points), n


def test_disc_clears_closed_kana_and_snow_bar_without_cutting_the_rim():
    templates, names = cards.templates(), cards.names()
    for n, points, fill in ((157, [(68, 20), (68, 24)], (216, 48, 136)),
                            (177, [(72, 27), (80, 27)], (208, 48, 136))):
        pal, original = cards.card(n)
        new = cards.redraw(n, templates.get(cards.key(pal, original)), names[n - 1])
        for x, y in points:
            assert pal[original[y * cards.W + x]] != fill
            assert pal[new[y * cards.W + x]] == fill
        for x, y in ((64, 18), (90, 18)):
            assert new[y * cards.W + x] == original[y * cards.W + x]
