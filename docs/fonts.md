# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/en12.txt | the owner's GaiaMaster translation (github.com/minhnhattonthat/gaiamaster-kamigami-no-board-game-en) | MIT, same owner | yes | dialogue/menu VWF (tools/engine.py), small graphics lettering (tools/gfx_en.py) | - |
| fonts/mplus/MPLUSRounded1c-ExtraBold-latin.ttf | github.com/google/fonts ofl/mplusrounded1c (Rounded M+ ExtraBold) | OFL 1.1 (fonts/mplus/OFL.txt) | yes, as rendered pixels | graphics lettering: title/menu/banner/card labels (tools/gfx_en.py) | subset to U+0020-007E with pyftsubset |
