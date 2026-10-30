"""Create complete story-review inputs from the current authored script.

Chapter order follows docs/synopsis.md; alternate NPC responses within each
location remain in resource order and are explicitly labelled as alternatives.
Shared battle lines are deduplicated only in the supplemental battle chapter.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import insert

CHAPTERS = {
    '01_departure': ['EVTOP_25', 'SMAP00_28', 'SMAP01_33', 'SMAP02_33', 'EVT003_11',
                     'SMAP03_113', 'SMAP04_35', 'EVT006_11', 'SMAP05_31'],
    '02_companions': ['SMAP06_36', 'EVT015_11', 'SMAP07_23', 'DMAP00_26', 'DMAP01_26',
                      'SMAP08_35', 'DMAP02_42', 'SMAP09_33', 'SMAP10_36', 'SMAP11_23', 'OMAP00_43'],
    '03_rival_and_princess': ['DMAP03_92', 'SMAP12_33', 'DMAP16_37', 'DMAP05_65', 'OMAP00_45'],
    '04_hope': ['SMAP13_37', 'ATOK_9', 'SMAP15_37', 'DMAP04_21', 'SMAP16_37', 'SMAP16_36',
                'HMAP20_18', 'HMAP26_66', 'OMAP00_47'],
    '05_friendship': ['SMAP17_22', 'SMAP25_31', 'SMAP19_28', 'SMAP20_33', 'SMAP21_33',
                      'OMAP00_49', 'DMAP06_20', 'DMAP07_28', 'DMAP08_43', 'EVT057_11'],
    '06_five_treasures': ['SMAP22_35', 'EVT069_11', 'SMAP23_33', 'SMAP24_30', 'DMAP09_29', 'OMAP00_51'],
    '07_hell': ['DMAP11_47', 'DMAP12_47', 'DMAP13_47', 'DMAP14_28', 'EVT076_14', 'DMAP15_56', 'OMAP00_53'],
    '08_farewells': ['END00_7', 'SMAP26_37', 'END02_14', 'END01_11'],
    '09_hermits': [f'WMAP{i:02d}_28' for i in range(26) if i != 19] + ['WMAP19_34', 'DMAP18_27', 'JMAP00_35'],
    '10_museum_and_cards': ['HMAP2607_66', 'HMAP2606_66', 'HMAP2606_65', 'HMAP8300_18', 'HMAP8500_18'],
    '11_minigames_and_travel': ['AMAP_18', 'PT00_5', 'Z00_19', 'DARUMA_11', 'FUKU_11', 'FURO_0_7',
                               'MOGURA_11', 'SUIEI_9', 'YUMI1_11', 'YUMI2_10'],
    '12_system_and_shops': ['FONT_5', 'FONT_6', 'FONT_7', 'FONT_10', 'FONT_11', 'SHOP', 'MECD_1', 'SLPS_017'],
}


def generate(out):
    docs = {d['id']: d for _, d in insert.docs()}
    chapters = {**CHAPTERS, '13_battle': sorted(k for k in docs if k.startswith('BM'))}
    assigned = [k for keys in chapters.values() for k in keys]
    excluded = {k for k, d in docs.items() if all('data' in s or 'same' in s for s in d['strings'])}
    assert len(assigned) == len(set(assigned)), 'table assigned twice'
    assert set(assigned) | excluded == set(docs), set(docs) - set(assigned) - excluded
    out.mkdir(parents=True, exist_ok=True)
    counts = {}
    for chapter, keys in chapters.items():
        lines = [f'# {chapter}',
                 'Read with docs/synopsis.md, docs/style-reference.md and glossary.md.',
                 'Locations follow the story arc; each location includes alternative NPC/state responses.',
                 'These alternatives are not consecutive utterances. Speaker is inferred from the JP, not invented.',
                 'All source entries are included; identical battle messages are cross-referenced below.', '']
        seen = {}
        count = 0
        aliases = {}
        for key in keys:
            lines.append(f'## {key} (resource order; conditional responses included)')
            for s in docs[key]['strings']:
                if 'same' in s:
                    lines.append(f'Alias {s["id"]} -> {key}:{s["same"]:03d}')
                    continue
                if 'data' in s:
                    continue
                pair = (s['jp'], s.get('en', ''))
                if chapter == '13_battle' and pair in seen:
                    aliases[s['id']] = seen[pair]
                    continue
                seen[pair] = s['id']
                lines.extend([f'>> {s["id"]} | speaker: infer from context | {s["jp"]}', f'EN {s.get("en", "")}'])
                count += 1
        # Boss exchanges are needed to judge character transitions in the story,
        # even though they also receive complete coverage in the battle supplement.
        bounds = {'03_rival_and_princess': (160, 183), '04_hope': (144, 159),
                  '05_friendship': (184, 189), '07_hell': (131, 143)}
        if chapter in bounds:
            lo, hi = bounds[chapter]
            lines.append('## Boss battle dialogue context (occurs between challenge and reconciliation)')
            for s in docs['BM000_1']['strings']:
                if 'jp' in s and lo <= int(s['id'].split(':')[1]) <= hi:
                    lines.extend([f'>> {s["id"]} | battle context | {s["jp"]}', f'EN {s.get("en", "")}'])
        if aliases:
            lines.append(f'{len(aliases)} byte-for-byte identical JP/EN repetitions omitted; see battle-aliases.json.')
            (out.parent / 'battle-aliases.json').write_text(json.dumps(aliases, indent=2) + '\n', encoding='utf-8')
        (out / f'{chapter}.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
        counts[chapter] = count
    print(json.dumps(counts, indent=2))
    return counts


if __name__ == '__main__':
    generate(ROOT / 'work/qa/story/chapters')
