"""The debug tool's scene list parses and its tables are complete."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/debug'))
import warp  # noqa: E402


def test_scene_names_unique_and_present():
    names = warp.scene_names()
    assert len(names) == len(set(names))
    for must in ('title', 'title_load', 'village', 'world', 'battle', 'menu', 'ev_card', 'credits_end', 'epilogue'):
        assert must in names


def test_scene_maps_exist():
    maps = {int(l.split()[0]) for l in (ROOT / 'tools/debug/maps.txt').read_text().splitlines() if l[0].isdigit()}
    assert len(maps) == 560
    for m in re.findall(r'map = (\d+)', (ROOT / 'tools/debug/scenes.lua').read_text()):
        assert int(m) in maps
