"""QA-tour sheets: every warp scene's English shot beside the original's, zoomed x2.

    python -X utf8 tools/debug/warp.py --all --tag en           # English shots -> work/qa/warp_en/<scene>/scene.png
    python -X utf8 tools/debug/warp.py "rom/<cue>" --all         # original's   -> work/qa/warp/<scene>/scene.png
    python -X utf8 tools/tour.py                                 # -> work/qa/tour/<scene>_sheet.png
    python -X utf8 "$(python tools/skill.py)/scripts/qa_gate.py" init work/qa/manifest.tsv work/qa/tour

Left = English, right = Japanese (blank when the original has no shot of that scene).
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EN, JP, OUT = ROOT / 'work/qa/warp_en', ROOT / 'work/qa/warp', ROOT / 'work/qa/tour'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for shot in sorted(EN.glob('*/scene.png')):
        en = Image.open(shot).convert('RGB')
        jp_path = JP / shot.parent.name / 'scene.png'
        jp = Image.open(jp_path).convert('RGB') if jp_path.exists() else Image.new('RGB', en.size)
        sheet = Image.new('RGB', (en.width + jp.width + 4, max(en.height, jp.height)), (255, 0, 255))
        sheet.paste(en, (0, 0))
        sheet.paste(jp, (en.width + 4, 0))
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(OUT / f'{shot.parent.name}_sheet.png')
        n += 1
    print(n, 'sheets in', OUT)


if __name__ == '__main__':
    main()
