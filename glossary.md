# Glossary - Momotarou Densetsu (PS1)

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
The English of the name tables is binding too, once merged: items and techniques (`script/03FONT/FONT_6.json`),
monsters and battle commands (`FONT_7.json`), place words (`FONT_5.json`). `tools/batches.py terms` puts the rows a
batch needs into `build/terms_<batch>.txt`.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Momotaro-san, Kintaro-kun, -sama, -dono). Name order: Western (given name first).
  Hepburn drops the long-vowel u (Momotaro, Ryugu). 姫 in a name: Yashahime; in a fairy-tale title: Princess Kaguya.
- Romanisation source: official English names where they exist, else an earlier fan patch, else Hepburn without
  macrons.
- Credits: English.
- Register: light, comic, all-ages Hudson humour; keep Japanese folklore flavour (oni, ryo, sennin hermits, shrines),
  translate everything else. Sound effects and cries in plain caps-free English or romaji onomatopoeia that reads
  well (*Ka-chink!*, "Chirp chirp!").
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening (HP / SP are the stat names,
  not abbreviations to fit).

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...', ・・・ / … -> ..., ！？ -> ?!, ～ (drawn-out) -> repeat the vowel or
  "...", ー in a shout -> stretch the word ("Welcooome!").
- Dialogue is quoted with straight double quotes exactly where the JP uses 「」; narration is unquoted.
- Animal and character speech tics become an English tic, used as often as the JP uses it (see docs/style-reference.md).
- Puns, parodies and proverb jokes: rebuild the joke in English; never footnote.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 桃太郎 / ももたろう | Momotaro | | hero; 桃太郎さん -> Momotaro-san | Momotarou, Momotarō |
| 金太郎 / きんたろう | Kintaro | | party member; axe (まさかり) | Kintarou |
| 浦島 / 浦島太郎 / うらしまたろう | Urashima / Urashima Taro | | party member; harpoon (モリ) | Urashimataro |
| 夜叉姫 / やしゃひめ | Yashahime | | party member; hairpins (かんざし) | Yasha-hime, Princess Yasha |
| イヌ | Dog | | companion | |
| サル | Monkey | | companion | |
| キジ | Pheasant | | companion | |
| おじいさん / おばあさん | Grandpa / Grandma | | Momotaro's foster parents | |
| ボンビー | Bombee | | poverty god from Momotetsu; tic なのねん | Bonby, Bonbee |
| キングボンビー | King Bombee | | | |
| 阿修羅 | Ashura | | | Asura |
| えんま大王 / 閻魔 / えんま | Great King Enma / Enma / Enma | | えんま様 -> Enma-sama | Emma, Lord Enma |
| 酒呑童子 | Shuten-doji | | | |
| 風神 / 雷神 | Fujin / Raijin | | wind god / thunder god | |
| 乙姫 | Otohime | | Ryugu Palace | |
| かぐや姫 | Princess Kaguya | | | |
| 寝太郎 | Netaro | | the sleepy man of 寝太郎の村 | |
| 花咲かじいさん | Old Man Hanasaka | | 花咲かじじい: same man, rude | |
| スリの銀次 | Ginji the Pickpocket | | | |
| 福の神 | God of Fortune | | | |
| ウンチ | Poop | | companion from Tabidachi Village, tic ぷり -> "plop!" | Unchi |
| じんぱち | Jinpachi | | mouse | |
| えのん | Enon | | Bombee Village chief | |
| 両鉄 | Ryotetsu | | oni | |
| 竜燈鬼 | Ryutoki | | oni | |
| ましら | Mashira | | oni rock star | |
| 醜女 | Shikome | | oni | |
| 羅生門の鬼 | Rashomon Oni | | | |
| 門臨 忍 | Shinobu Kadorin | | pun-contest winner (SMAP13_37, card HMAP8500_18) | Monrin |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 鬼ヶ島 | Onigashima | | | Oni Island |
| 竜宮城 | Ryugu Palace | | | Ryuugu |
| 都 / 希望の都 | the Capital / Capital of Hope | | | |
| すずめのお宿 | Sparrow Inn | | | |
| 地獄 / じごく | Hell | | | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 鬼 | oni | | lowercase in prose, Oni in names (Red Oni); plural oni | ogre, demon |
| 仙人 | hermit / Hermit | | X仙人 -> "<art> Hermit" after the art he teaches | sage |
| 術 | art | | the magic-like techniques hermits teach (きんたんの術 -> the Kintan art: use the art's EN name) | spell, jutsu |
| 体力 / 体 | HP | | stat; prose may say "health" only where JP is not the stat | |
| 技 (stat) | SP | | points spent on arts; 技 meaning a move: "skill" | MP |
| 段 | level | | 27段 -> level 27; 昇段 -> level up | dan |
| 心 / ココロ / 心の数 | hearts / Hearts | | collectible hearts (会心のココロ critical heart) | |
| 両 | ryo | | currency, "100 ryo" | gold, yen |
| 茶店 | teahouse | | shop that sells food | tea house |
| といち屋 | Bank | | deposits / withdrawals | |
| 攻撃力 / 守備力 / 素早さ | Attack / Defense / Speed | | stats | |
| カード / カードアルバム | card / Card Album | | collectible cards (Xカード -> X Card) | |
| ウヒャヒャ | Uhyahya | | every hermit's opening laugh: "Uhyahya..." | |
| 修行 | training | | hermit training | |
| 会得 | master | | 術を会得 -> master an art | |
| 記録 | save | | shrines record (save) your journey | |
| メモリーカード | Memory Card | | | |
| 勇気の子 | child of courage | | how elders call Momotaro | |
| 友情 | friendship | | | |
| 貧乏神 | poverty god | | Bombee's kind | |
| 桃太郎博物館 | Momotaro Museum | | Capital of Hope | |
| 黄泉の塔 | Yomi Tower | | | |
| 仙人の庵 | hermit's hut | | | |
| 伝助 | Densuke | | tunnel digger | |
| 五重塔 | pagoda | | five-story pagoda in the Capital | |
| 福笑い | Fukuwarai | | face-arranging minigame | |
| オートバトル | Auto Battle | | | |
| ポンポコポン | Ponpoko-pon | | tanuki tic | |
| 大けが | injured / Injured | | status | |
| 道具 / どうぐ | item / Items | | どうぐぶくろ / 道具袋 -> item bag | |
| きびだんご | millet dumpling | | | kibidango |
| お供 | companion | | Dog, Monkey, Pheasant | |

## Decisions from earlier batches
- wave 0 (b001-b005, name tables): X鬼 / Xの鬼 -> "X Oni"; folklore beings without an English word stay romaji
  (Yasha, Hannya, Orochi, Kappa, Amanojaku, Gozu, Mezu); 亡者 Wraith, ごくそつ Jailer, 邪鬼 Imp, ごぜん "Lady X",
  びろーん Stretchy. Arts have English names (Escape, Lightning, Dash, Fart, Warp, Smash, Float, Seal, Soften, Power,
  Haste, Echo...), except きんたん = Kintan / Kintan Plus / Kintan Max; "X仙人" = "<Art> Hermit". Materials Bronze /
  Iron / Silver / Gold; virtues "<noun> of Courage/Hope/Justice/Love". 玉 Orb (treasure ほうらいの玉 = Horai Jewel),
  仙豆 Bean, 丹 Pill, お札 Talisman, 刀 alone Katana, X切りの刀 "Xcutter Sword". Villages "<Romaji> Village".
- ウンチ (the character) -> Poop, 鉄ウンチ Iron Poop; といち屋 -> Bank; 氷室 / ひむろ -> Icehouse (氷室の削り火 Icehouse
  Fire); 水鬼 Water Oni; 塩吹き鬼 Salt Oni; 竜燈鬼 Ryutoki; 左魂 / 右魂 Left Soul / Right Soul.
- Flagged abbreviations (phase 7 layout work, not translator choices): equip slot labels 武/防/足 = Wpn/Arm/Ft (20 px
  slot), directions 北東.. = NE/NW/SE/SW (label width unmeasured), HUD level label 段 = Lv (8x8 glyph cell beside
  HP/SP; the status screen spells Level). 両 after a number = "ryo" (money boxes moved 8 px to fit it).
- Name entry: the first page is English (A-Z a-z digits punctuation); hiragana is on the page labelled Hiragana.
