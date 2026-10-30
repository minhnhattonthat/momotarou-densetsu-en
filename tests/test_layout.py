"""Layout of authored English into game pages (tools/layout.py) and the batch check (tools/batches.py)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import batches  # noqa: E402
import layout  # noqa: E402

SHOP0 = '「いらっしゃーい！{n} 茶店へようこそ！」{n}{wait}{n}「どんなご用ですか？」{n}{n}'


def test_repacked_pool_borrows_slack():
    import struct
    import insert
    jp = insert.EN.encode('a{end}')
    b = bytearray(jp + bytes(10) + jp + bytes(2) + bytes(8))          # slots of 12 and 4 at 0, 12; pointers at 16, 20
    doc = {'id': 't', 'base': '0x80000000', 'strings': [
        {'id': 't:0', 'off': 0, 'max': 12, 'ptrs': ['word@0x10'], 'en': 'Hi'},
        {'id': 't:c', 'off': 12, 'max': 4, 'ptrs': ['word@0x14'], 'en': 'Long one'}]}
    out = insert.repacked(doc, b)
    p0, p1 = struct.unpack_from('<II', out, 16)
    hi = insert.EN.encode('Hi{end}')
    assert p0 == 0x80000000 and p1 == 0x80000000 + len(hi)
    assert out[len(hi):len(hi) + len(insert.EN.encode('Long one{end}'))] == insert.EN.encode('Long one{end}')


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


def test_joining_spaces_kept():
    assert layout.layout(' used the Kintan art!', 'きんたんの術を 使った！')[0] == ' used the Kintan art!'
    assert layout.layout('Momotaro ', '桃太郎は')[0] == 'Momotaro '
    for jp, en in [('それぞれ ', 'each'), ('さらに ', 'Also,')]:
        assert any('trailing source blanks' in e for e in batches.problems(jp, en, 'dlg', []))
        assert not batches.problems(jp, en + ' ', 'dlg', [])
        assert layout.layout(en + ' ', jp)[0].endswith(' ')
    assert any('leading source blanks' in e for e in batches.problems(' 名前', 'Name', 'dlg', []))
    assert not batches.problems(' 名前', 'Name', 'dlg', [], space_ok={'leading'})


def test_overflow_and_too_many_lines_reported():
    assert layout.layout('A very long item name indeed', 'はりせん', 'item')[1]
    assert layout.layout(' '.join(['word'] * 120), '一{n}二{n}三')[1]


def test_no_lone_last_word_when_it_can_move():
    lines = layout.wrap("But the oni's attack only cut through the empty air!", 108)   # greedy: [..., 'cut through the empty', 'air!']
    assert ' ' in lines[-1].strip() and all(layout.width(ln) <= 108 for ln in lines)
    assert layout.wrap('Hello there friend', 1000) == ['Hello there friend']
    assert any('short final' in e for e in layout.layout('Hello{n}a', 'hello{n}a', 'dlg')[1])
    assert any('short final' in e for e in batches.problems('hello{n}a', 'Hello{n}a', 'dlg', []))
    assert not layout.layout('Choose{n}Yes{n}No{n}Exit', '選ぶ{n}はい{n}いいえ{n}出る', 'choices')[1]
    assert not layout.layout('Answer{n}{num}', '答え{n}{num}', 'dlg')[1]
    assert layout.box('HMAP8500_18:999', '未測定') == 'label'


def test_unmapped_labels_fail_closed():
    """A FONT label outside every measured range gets no width from its Japanese: any English overflows."""
    assert layout.box('FONT_6:9999', 'はい') == 'label'
    assert layout.layout('Yes', 'はい', 'label')[1]
    assert layout.box('FONT_6:799', '1階') == 'floor' and not layout.layout('Floor 5', '5階', 'floor')[1]
    assert layout.box('FONT_6:600', 'スクロールスピード') == 'unused'
    assert layout.box('FONT_10:117', '？？？') == 'cmd'
    for sid in ('MECD_1:999', 'FUKU_11:999', 'HMAP2607_66:999', 'UNKNOWN:001'):
        assert layout.box(sid, '未測定') == 'label'
    assert layout.layout('Capital letters only', 'ことば', 'proverb') == ('CAPITALLETTERSONLY', [])
    assert layout.layout('Too many letters to enter in this puzzle', 'ことば', 'proverb')[1]


def test_check_problems():
    gl = [('桃太郎', 'Momotaro', ['Momotarou'], True)]
    assert any('control codes' in e for e in batches.problems('{str}の 攻撃！', '{str} attacks{num}!', 'dlg', gl))
    assert any('ordinal' in e for e in batches.problems('{num}回目', 'the {num}th time', 'dlg', gl))
    assert any('avoided' in e for e in batches.problems('桃太郎は 走った', 'Momotarou ran.', 'dlg', gl))
    assert batches.problems('桃太郎は 走った', 'He ran.', 'dlg', gl)
    assert batches.problems('桃太郎は 走った', 'Momotaro ran.', 'dlg', gl) == []
    assert batches.problems('{str}の 攻撃！{n}{n}{wait}', '{str} attacks!{wait}', 'dlg', gl) == []
    # missing glossary names and dropped honorifics are errors unless a reviewed exception lists them
    assert any('glossary' in e for e in batches.problems('「桃太郎！」{wait}', '"Peach Boy!"{wait}', 'dlg', gl))
    assert batches.problems('「桃太郎！」{wait}', '"Peach Boy!"{wait}', 'dlg', gl, {'桃太郎'}) == []
    assert any('honorific' in e for e in batches.problems('「桃太郎さん！」{wait}', '"Momotaro!"{wait}', 'dlg', gl))
    assert batches.problems('「桃太郎さん！」{wait}', '"Momotaro-san!"{wait}', 'dlg', gl) == []
    assert batches.problems('「桃太郎君！」{wait}', '"Momotaro-kun!"{wait}', 'dlg', gl) == []
    assert batches.problems('お地蔵さまだ', 'A Jizo statue.', 'dlg', [('地蔵', 'Jizo', [], False)]) == []
    assert batches.has_term('桃太郎さん', '桃太郎') and not batches.has_term('タイミング', 'ミン')
