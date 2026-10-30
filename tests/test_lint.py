"""Regression probes for the whole-script acceptance gate."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import lint


def errors(*strings):
    return lint.validate([(None, {'strings': strings})], [], {})[0]


def test_authored_control_only_source_is_validated():
    assert any('control codes differ' in e for e in errors(
        {'id': 'FONT_7:001', 'jp': '{num}', 'en': '{str}'}))


def test_authored_ascii_source_is_validated():
    assert any('Japanese left' in e for e in errors({'id': 'FONT_7:017', 'jp': 'ON', 'en': 'オン'}))


def test_unchanged_ascii_and_control_sources_are_classified():
    assert not errors({'id': 'FONT_7:001', 'jp': '{num}', 'en': ''},
                      {'id': 'FONT_7:017', 'jp': 'ON'}, {'id': 'FONT_6:551', 'jp': '{sm_tai}'})
    assert errors({'id': 'FONT_7:019', 'jp': 'はやい'})


def test_money_substitution_exception_is_exact():
    assert not errors({'id': 'FONT_6:556', 'jp': '{sm_ryo}', 'en': 'ryo'})
    assert any('control codes differ' in e for e in errors(
        {'id': 'FONT_6:556', 'jp': '{sm_ryo}', 'en': '{num} ryo'}))
