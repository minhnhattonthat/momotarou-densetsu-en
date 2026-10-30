"""Layout of authored English into game pages (tools/layout.py) and the batch check (tools/batches.py)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import batches  # noqa: E402
import layout  # noqa: E402

SHOP0 = '「いらっしゃーい！{n} 茶店へようこそ！」{n}{wait}{n}「どんなご用ですか？」{n}{n}'


def test_pages_padded_like_the_japanese():
    out, probs = layout.layout('"Welcome!"{wait}"What can I do for you?"', SHOP0)
    assert probs == []
    assert out == '"Welcome!"{n}{n}{wait}{n}"What can I do for you?"{n}{n}'


def test_wrap_and_quote_indent():
    text = '"' + 'word ' * 20 + 'end."'
    out, probs = layout.layout(text + '{wait}x', SHOP0.split('{wait}')[0] + '{wait}{n}x')
    lines = out.split('{wait}')[0].split('{n}')
    assert probs == [] and len(lines) == 3
    assert lines[1].startswith(' word') and all(layout.width(ln) <= 234 for ln in lines)


def test_extra_page_gets_a_standard_page():
    out, _ = layout.layout('One.{wait}Two.{wait}Three.', '一{n}{n}{wait}{n}二{n}{n}')
    assert out == 'One.{n}{n}{wait}{n}Two.{n}{n}{wait}{n}Three.{n}{n}'


def test_string_ending_in_wait_and_battle_names():
    out, probs = layout.layout('{str}{str} attacks!{wait}', '{str}{str}の 攻撃！{n}{n}{wait}')
    assert (out, probs) == ('{str}{str} attacks!{n}{n}{wait}', [])


def test_overflow_and_too_many_lines_reported():
    assert layout.layout('A very long item name indeed', 'はりせん', 'item')[1]
    assert layout.layout(' '.join(['word'] * 120), '一{n}二{n}三')[1]


def test_check_problems():
    gl = [('桃太郎', 'Momotaro', ['Momotarou'])]
    errs, warns = batches.problems('{str}の 攻撃！', '{str} attacks{num}!', 'dlg', gl)
    assert any('control codes' in e for e in errs)
    errs, _ = batches.problems('{num}回目', 'the {num}th time', 'dlg', gl)
    assert any('ordinal' in e for e in errs)
    errs, warns = batches.problems('桃太郎は 走った', 'Momotarou ran.', 'dlg', gl)
    assert any('avoided' in e for e in errs)
    assert batches.problems('桃太郎は 走った', 'He ran.', 'dlg', gl)[1]
    assert batches.problems('桃太郎は 走った', 'Momotaro ran.', 'dlg', gl) == ([], [])
    assert batches.has_term('桃太郎さん', '桃太郎') and not batches.has_term('タイミング', 'ミン')
