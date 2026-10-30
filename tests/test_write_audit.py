"""Audit rejects incorrect origins, overlapping writes, and unaudited final edits."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from write_audit import Buffer


def test_wrong_original_and_overlaps_fail():
    b = Buffer(b'abcdef', 'overlay')
    with pytest.raises(AssertionError, match='wrong expected original'):
        b.put(1, b'XY', 'first', expected=b'cd')
    b.put(1, b'XY', 'first', expected=b'bc')
    with pytest.raises(AssertionError, match='overlap'):
        b.put(2, b'Y', 'second')  # identical overlapping data is still ambiguous ownership
    with pytest.raises(AssertionError, match='overlap'):
        b.put(0, b'ABCDEF', 'replacement', replace=True)


def test_final_bytes_and_unlogged_changes_fail():
    b = Buffer(b'abcdef', 'overlay')
    b.put(1, b'XY', 'text')
    b.verify(b'aXYdef')
    with pytest.raises(AssertionError, match='overwritten write'):
        b.verify(b'aXZdef')
    with pytest.raises(AssertionError, match='unlogged mutation'):
        b.verify(b'aXYde!')


@pytest.mark.parametrize('new', [b'longer table', b'a'])
def test_atomic_table_resize(new):
    b = Buffer(b'table', 'PAC:1')
    b.put(0, new, 'table', replace=True)
    assert b.data == new
    b.verify(new)


def test_appended_pool_has_no_gaps_or_overwrites():
    b = Buffer(b'code', 'overlay')
    with pytest.raises(AssertionError, match='out of bounds'):
        b.put(5, b'text', 'pool', append=True)
    b.put(4, b'text', 'pool', append=True)
    b.put(8, b'more', 'pool2', append=True)
    b.verify(b'codetextmore')
    with pytest.raises(AssertionError):
        b.put(4, b'bad!', 'overwrite', append=True)
    with pytest.raises(AssertionError, match='overwritten write'):
        b.verify(b'codetextoops')
