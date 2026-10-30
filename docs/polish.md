# Polish pass (phase 9)

Every deferred Minor from `docs/review-minors.md`, one line each: `- [x] id - note: fixed: new English` or
`waived: reason`. The release script refuses to run while any line is unticked.

Method: source edits with the file-edit tool, then `work/tl/polish.tsv` / `polish.out.tsv` (108 changed JP units)
went through `python -X utf8 tools/batches.py merge polish`, which re-checks layout, codes and glossary and copies
each English to every string with the same JP (the five BM000_1 battle lines live in 78 BM tables).
`python -X utf8 tools/check.py` after the merge: 49 passed, lint 0 errors (6,027 checks).

## b056-b060
- [x] MECD_1:032 - "Which save do you want to save to?": fixed: "Save to which slot?"
- [x] BM000_1:025 - "Defense went down!": fixed: "Defense fell!" (matches :018/:026/:033; all 78 BM copies)
- [x] BM000_1:105 - "everyone" not in JP: fixed: "{str}{str} scattered a shower of wing dust!" (JP names no target)
- [x] BM000_1:123 - Kappa Ebisen slogan: fixed: "Betcha can't stop!" (やめられない とまらない)
- [x] BM000_1:157 - Ashura "Will fall!": fixed: "Shall fall by my hand!"
- [x] BM000_1:043 - "got caught by the feet": fixed: "{str}{str} got tripped up and can't move!" (not "had its feet trapped": {str}{str} can be a party member, so no "its")
- [x] PT00_5:005 - name repeated: fixed: "...your first companion, Pheasant-san, who'd been caught by the oni, remember?"
- [x] PT00_5:023 - "buried ... in salt": fixed: "covered Shiobuki Village in salt"
- [x] Z00_19:014 - "being of use": fixed: "Are my fellow Jizo proving useful to you?"

## b011-b015
- [x] SHOP:462 - "broke as a Bombee": fixed: "You're broke, just like us Bombees, bombee!"
- [x] SHOP:483/484/487/497/498/511/512/515 - "save to save slot {num}": fixed: "slot {num}" in all eight plus the same pattern in SHOP:501/525/526/529; the "Saving to save slot" status lines SHOP:492/506/520/534 now "Writing save data to slot {num}..."; "I can't find save slot {num}!" keeps "save" (no doubling, and glossary 記録 -> save requires it)
- [x] SHOP:493/507/521/535 - "removed or inserted": fixed: "The Memory Card was taken out or swapped!" (voice tags kept: ", bombee!")
- [x] SHOP:555 - "keen eye": fixed: "You have a keen eye!"
- [x] SHOP:299 - add subject: fixed: "Momotaro looked in the item bag, but there was nothing inside."
- [x] SMAP01_33:046 - "quilty" reads as a typo: fixed: "The quilt up and quit on me!" (ふとんが ふっとんだ groaner rebuilt as quilt/quit)
- [x] EVTOP_25:000 - "far away" not in JP: fixed: "Once upon a time, in a certain land..."

## b016-b020
- [x] SMAP02_33:008 - stiff: fixed: "Talk to the hermit at any hermit's hut to fully restore your HP and SP!" / "If your HP gets low on your journey, pay one a visit!"
- [x] SMAP02_33:013 - stiff: fixed: "I'll be praying for your victory over the oni! Hop hop!"
- [x] SMAP02_33:078 - stiff: fixed: "Mmm, the rice is cooking up nice and tasty!"
- [x] SMAP03_113:061 - stiff: fixed: "Being able to eat whenever you like... that's real happiness, isn't it, Momotaro-san!"
- [x] SMAP03_113:075 - stiff: waived: "Out of the blue fell a pie in the sky!" already fuses two English idioms exactly as the JP fuses 薮から棒 + 棚からぼた餅, and the sign's "Oh, come on!" groan follows; not stiff
- [x] SMAP04_35:033 - "token of my joy": fixed: "Please accept this as a token of my joy, bombee!"
- [x] SMAP04_35:068 - "the way it is now": fixed: "I hate the way this village is now, bombee!"
- [x] SMAP05_31:006 - "an honest soul": fixed: "You seem to be an honest soul..." / "To an honest soul like you..."
- [x] SMAP06_36:050 - stiff: fixed: "My Pochi is a very, very clever dog!"
- [x] SMAP06_36:083 - "Patience is a virtue... so WHAT?!": fixed as suggested
- [x] SMAP04_35:034 - quotes dropped on a narration line: waived: reviewer accepted; the JP wraps a "Momotaro got" narration in 「」 by mistake, the English follows every other unquoted "Momotaro got" line

## b031-b035
- [x] SMAP21_33:013 - "turtle-y" pun: waived: turtle-y/totally rebuilds the カメ (turtle) = 噛め (chew) pun, and the next page says "I can finally crack jokes like that again", so the line needs a visible pun; "Kame kame!" tic per style reference
- [x] SMAP21_33:003 - "Bring everyone along": fixed: "And of course, bring everyone along! Hop hop!"
- [x] SMAP22_35:007 - "work together with the men": fixed: "From now on we'll work together with the men to make this a wonderful village, Momotaro-san!"
- [x] SMAP22_35:054 - word order: fixed: "Momotaro-san, we have readied a sailing ship so that you and your friends can set out to sea."
- [x] SMAP23_33:018 - "are going to take": fixed: "The bad guys are going to take Princess Kaguya away!"
- [x] OMAP00_49:036 - pheasant proverb not a real idiom twist: fixed: "A watched pheasant never sings!"
- [x] SMAP21_33:033 - weak twist: fixed: "It's an ill wind that blows nobody good... and it's blowing my way! Profits! Profits!"
- [x] SMAP22_35:074 - weak twist: waived: "Don't count your chickens before they're in the hotpot!" twists a real English proverb into the same hotpot punchline as 鴨がネギを しょっつる鍋; the duck-and-leeks idiom has no English counterpart to twist instead
- [x] SMAP22_35:067 - "Like father, like son? Nope, the son's a tadpole!": fixed: "Like father, like son? Not for frogs... the son's a tadpole!" (real idiom as setup, frog kept)
- [x] SMAP22_35:002/005 - rustic dialect uneven vs :023+: fixed: :002 "Oni've gone an' holed up..." / "Now there ain't no way to get to Orihime Village!", :004 "The oni went an' blocked off...", :005 (and identical :009/:011) "If we go gettin' carried away now... Back to workin' hard!"
- [x] "Mysterier Forest" (もっとふしぎな森) - waived: deliberate kid-grammar comparative of the nearby ふしぎな森; consistent in all four OMAP00_47 lines; no name table, map label or graphic uses it

## b036-b040
- [x] OMAP00_51:003 - "they" antecedent: fixed: "If you carry a cucumber from the greengrocer's, the Black Kappa will stare at it and won't be able to move!"
- [x] OMAP00_51:019 - phrasing: fixed: "What's that? I should be able to tell whether you've met her just by looking?"
- [x] OMAP00_51:026 - weak setup: fixed: "Peaches and chestnuts take three years to bear fruit... but oysters are best from Hiroshima!" (real 桃栗三年 proverb as setup)
- [x] OMAP00_53:030 - half-lost: fixed: "A sparrow never forgets its dance... and a fool who watches is still a fool!" (both 雀百まで and 踊るあほうに見るあほう halves)
- [x] OMAP00_53:025/027/028 - mapmaker んだな tic absent: resolved earlier: all three end ", I reckon" since 272d36c (phase 6 reviewer fixes); rechecked this pass
- [x] WMAP00_28:006 - "Ryoma wasn't built in a day": fixed: "Romeo wasn't built in a day." (竜馬/ローマ name pun rebuilt on Rome/Romeo)
- [x] WMAP14_28:002 - fixed: "Hmm! A good, honest child. Rare these days!"
- [x] WMAP13_28:000 - item-name capitals: fixed: "First rice balls, and later on millet dumplings!" (glossary: millet dumpling, lower case in prose)
- [x] WMAP15_28:007 - "10 to 18 characters": waived: the English name-entry grid types one glyph code per letter or space (docs/re/engine.md "Name entry 0x800DC3D0", engine.NAME_GRID single English codes), the same unit the overlay counted for kana, so the stated range still counts exactly what the player types; WMAP15's own length check was not run in the emulator this pass

## b026-b030
- [x] MUST - mapmaker なんだな tic -> ", I reckon." in SMAP12_33:049-054, SMAP16_37:255/258, OMAP00_53:025/027/028: resolved: every listed line already ends ", I reckon" (272d36c; all 21 "I reckon" lines rechecked). This pass also fixed the voice's person-mixing: SMAP12_33:051, SMAP16_37:256 and the SMAP22_35 copy "Momotaro-san gets the map I drew" -> "Here's the map I drew for you, Momotaro-san, I reckon."; SMAP12_33:053 "I'll give Momotaro-san ... you'd best find me" -> "I'll give you the rest of the map too, Momotaro-san, so I want you to find me on your travels, I reckon." (style-reference example)
- [x] SMAP15_37:077 - belly link: fixed: "Go poking a belly with nothing to hide, and all you'll do is tickle it!"
- [x] SMAP15_37:057/058 - Kame kame kept: waived: style reference (Turtles row) sets "Kame kame!" as the romaji tic
- [x] SMAP16_37:004 - fixed: "It's so dark out, a body isn't safe!"
- [x] SMAP16_37:033 - fixed: "Hey, you ain't got any money! Beat it, and don't come back!" (おととい きやがれ)
- [x] SMAP16_37:243 - fixed: "So the Capital is never plunged into darkness again, humans and oni have to get along!"
- [x] SMAP16_37:254 - fixed: "They say home is where you make it, but the Capital of Hope truly is a wonderful town!" (すめば都)
- [x] SMAP20_33:028 - "at the far end": fixed: "The Salt Oni is in the back of this village!" (おく)
- [x] SMAP20_33:036 - "let bygones be bygones": fixed: "Just like the rain washed away the salt, everyone has let the past wash away!" (水に流す image kept)
- [x] SMAP16_37:192/194 - kappa casing: resolved earlier: both read "Kappa" (272d36c), as glossary line 107 lists it

## b006-b010
- [x] FONT_10:023/047 - first {str} unknown: resolved phase 7/8: it is the FONT_10:030 join fragment ("Also, "); docs/re/windows.md "Battle joins" and "Battle fragment runtime recheck", work/qa/phase8_latest/join_*/final.png show "Also, 37 ryo was stolen!" and the item theft without doubled separators
- [x] FONT_10:056 - "The two {str} merged" with singular names: fixed: "The {str} pair merged into one!"
- [x] FONT_10:041 - stiff "Label: {num}": fixed: "Yashahime's clones appeared, {num} in all!" (reads for 1 too)
- [x] FONT_6:711 - stiff "Steps away: {num}": waived: the count can be 1 and the brief bans "(s)"; every sentence form ("{num} steps away") breaks at 1, so the label form stays
- [x] FONT_6:725/727 - stiff "Label: {num}": fixed: "The wicker chest count on this floor is {num}!" / "...around here is {num}!" (zero has its own lines :726/:728)
- [x] FONT_6:461 - Kitchomu vs Kicchomu: waived: Revised Hepburn writes っち as "tch" (matcha, Kitchomu); "cch" is Nihon-shiki style; D2 picks Hepburn
- [x] FONT_6:496 - "defense" case: fixed: "at the cost of Defense" (stat name, like Attack)
- [x] FONT_6:512 - "A mystery Bean": waived: the line already reads "A Bean that raises who knows what!", which says the same with the item term kept
- [x] FONT_6:775 - "did great things": fixed: "Momotaro-san was a real hero again this week!" (大かつやく; "big hit" meant popular)
- [x] FONT_11:095 - "O countless stars...": fixed as suggested

## b041-b045
- [x] DMAP03_92:001/002 - 7-tile name puzzle: resolved phase 8: docs/re/graphics.md (Shuten-doji cave row): tiles redrawn SH u TE N DO U JI, the hint spells "Sh-u-te-n-do-u-ji", verified on maps 402/403/405/407
- [x] WMAP19_34:007 - acceptable as is: waived: reviewer's own verdict; natural line ("I see! Then I'll go on ahead of you.")
- [x] WMAP21_28:012 - acceptable as is: waived: reviewer's own verdict; hermit voice and art name correct
- [x] DMAP03_92:046 - acceptable as is: waived: reviewer's own verdict; the North Pole quiz keeps the 北斗七星 answer (North)

## b046-b050
- [x] HMAP2606_66:088 - catchphrase: fixed: "Forget the courtesy, show me the money! Hee hee, that one's a bit dated, hop!" (同情するなら金をくれ parody)
- [x] HMAP2606_66:087 - "courtesy": fixed: "Hmm, it's true. You can't live on courtesy alone!" (ties to the saying "Better cash than courtesy")
- [x] HMAP2606_66:091 - bean joke vs :090: fixed: "I always thought soybeans grew in soy sauce, hop! Tee-hee!" (a soybean mix-up, like the JP misreading of 大豆/小豆)
- [x] HMAP2606_66:031 - "{num} minutes and {num} seconds": fixed: "...was... {num} min, {num} sec. So..." (minutes can be 0 or 1, so the plural words are unsafe; this is time notation, not a fit abbreviation)
- [x] HMAP2606_66:015 - "saying": fixed: "This time the saying has {num} letters!"
- [x] HMAP2606_66:066 - fixed: "Even oni cry" (story pass: the shown saying now matches the typed Word Maze key exactly, see Story review 10)
- [x] HMAP2606_66:228 - "greedy guts": fixed: "Th-that's just plain gluttony..."
- [x] HMAP2607_66:010 - shop names romaji vs translated: fixed: "the Max Shop" (matches its own sign line SHOP:549); Tamaya stays romaji because SHOP:548's fireworks joke needs the name; Heart Books matches SHOP:550
- [x] HMAP2607_66 - "the bean shop": resolved: no "bean shop" string remains in script/ (grep); the Bean shop is "the Max Shop" everywhere
- [x] HMAP2607_66:037 - repetitive: fixed: "Beans are mysterious little things that raise your HP and Attack!"
- [x] DMAP18_27:000/001 - hermit voice flat: fixed: "My training's a simple one!... Let an old man give you one piece of advice!... borrow a hand from your companions, eh!... Don't dawdle! Uhyahya..." / "So you made it all the way here, did you!... I shall bestow upon you the Float art!"
- [x] Word Maze - letter-by-letter answers, multi-word/spaces: resolved phase 7: docs/re/engine.md "Word Maze answer encoding" and "Word Maze runtime verification", work/qa/word_maze_probe/report.md (A-Z only, no spaces, 1-18 letters; RAISEDWITHCARE typed and accepted, wrong last letter rejected)

## b051-b055
- [x] HMAP26_66 - casing tabi/Kimono/Harpoon: fixed: :055/:060 "kimono", :056 "harpoon"; tabi (:027/:048) was already lower case
- [x] HMAP26_66:170 - weaker twist: waived: "When in Rome, eat persimmons!" is a clean English proverb twist carrying the JP's persimmon (かき) pun
- [x] HMAP26_66:200 - weaker twist: waived: "Spare the rod, spoil the child... with socks!" keeps the child-raising proverb and the 旅/足袋 (tabi socks) swerve; no English saying about sending children travelling to twist instead
- [x] HMAP26_66:204 - weaker twist: fixed: "In one ear and out the other... on a sightseeing tour!" (馬の耳に念仏 -> 見物)
- [x] HMAP26_66:212 - weaker twist: fixed: "Sounds like heaven, looks like... well, looks aren't everything!"
- [x] HMAP26_66:191 - weaker twist: fixed: "Throw a sprat to catch a mackerel... and catch a cold!" (real idiom as setup)
- [x] HMAP26_66:041 - "your clockwork dolls": fixed: "The clockwork dolls of your party on display in this museum are my proudest works!"
- [x] HMAP26_66:057 - "How handy!": fixed as suggested
- [x] HMAP8500_18:003-007 - sentence continued across {wait}, lowercase start: fixed: each page a full sentence ("...for a different one." / "If you want to trade, choose Yes. If not, choose No!"; "...know important things." / "So don't forget to talk to everyone!")
- [x] HMAP26_66:269 - "Rula-Pea" (ルラ☆ピー): waived: a nonsense music title with no meaning or known reading (ル could be ru/lu); readable, fits the 194 px title row
- [x] HMAP26_66:270 - fixed: "Steamy Hot Spring Inn"
- [x] HMAP8500_18:127-131 - real-person name readings unverified: waived: magazine reader-contest winners (SMAP13_37); no romanised source exists in the game or turned up in a web search; the most common readings are used identically in the SMAP13_37 dialogue (counts checked) and the cards; 門臨 忍 is glossary-bound

## b061-b065
- [x] BM008_1:286 - "Yokohama Silver Fly": waived: "Yokohama Blowfly" keeps the fly (蝿) the 五月蝿 kanji quiz hinges on; the Yokohama Ginbae band nod is lost on English players either way
- [x] BM008_1:298 - pun lost, "Dummy" reused (:238): fixed: "Quince / Dope / Dimwit / Dregs"; pun part waived: no English word is both quince and idiot (ぼけ)
- [x] BM008_1:236 - "Goofe": fixed: "Goatee" (ギョーテ Goethe parody, like the other near-miss decoys Vernal/Benz/Beret)
- [x] BM008_1:302 - "Misora": waived: the decoy is the singer Hibari Misora, the same reference as the JP, beside the answer Skylark (ひばり)
- [x] BM008_1:258 - "Gallstone Natsume": fixed: "Tanseki Natsume" -> "Gallstone Natsume" (胆石 joke visible)
- [x] BM008_1:239 - title choice: waived: "Two Years' Vacation" is the standard English title of Verne's Deux Ans de vacances (十五少年漂流記); answer Verne
- [x] BM024_1:298 - hint gives the answer away: waived: reviewer accepted; the JP hint does the same
- [x] Number style "1000 ryo" vs "10,000 ryo": fixed: commas for every amount/count of 1,000+ (SHOP:549, SMAP16_37:166/:179, HMAP26_66:000, BM024_1:215 and its BM026_1 copy, SUIEI_9:004/:017); years (1960, 1998) stay plain

## b066-b070
- [x] BM102_1:216 - month pun: fixed: "Gotcha! Gotcha! January! February! Marchgotcha! April! May! Junegotcha!" (3月/3ガッチュー)
- [x] BM081_1:212 - "did a check!": fixed: "{str}{str} inspected the troops!" (the commander line before charge/retreat orders)
- [x] ATOK_9:000 - gloss: fixed: "We're Ari to Kirigirisu... the Ant and the Grasshopper!" (sets up their animal-pun act)
- [x] SUIEI_9:004/005/017/018 - pidgin heavier than the style reference: fixed: lighter, keeps the ", yes!" tic ("Momotaro-san, you did it, yes!", "Roll-roll the two dice, then push the Circle button, yes!")
- [x] END02_14 - staff readings guessed, 天辺日朗 pen name: waived: no official romanised credits found (web search) and none in the game; common readings kept, "Hiroaki Tenpen" as written; D3 English credits

## Name tables
- [x] FONT_7:245 - えんおうば "Enoba" vs Enba family: waived: Hepburn without the long-vowel u (glossary rule) gives Enoba, a distinct monster from Enba (:194); renaming would ripple into HMAP8500_18:378 and the redrawn card art whose album gate is green
- [x] FONT_7:086 - とびてん夜叉 "Sky Yasha" vs "Flying Yasha": waived: 飛天 is the sky-dancing celestial, and Sky parallels Void Yasha (こくう夜叉 :085); same card-art ripple (HMAP8500_18:268)

# Story review (work/qa/story/reports, 13 chapters)

Every Important and Minor note, one line each. Method: primary rows edited with the file-edit tool; same-JP copies in
the 77 other BM tables (BM000_1:144-153, :180) go through `work/phase9/story-duplicates.patch` (847 en lines, applied
by the parent). Word Maze (HMAP2606_65/66) and museum scrolls (HMAP26_66:165-214) are the parent's.
`python -X utf8 tools/check.py` after the patch and mirrors: exit 0, lint 0 errors (6,027 checks), 55 passed.

## 01 departure
- [x] SMAP01_33:005 - Mapmaker "I reckon" on a farmer: fixed: "If ya fight it and can't win, best run away, y'hear!"
- [x] SMAP02_33:054 - dialect flattened: fixed: "At this rate, there ain't gonna be no festival at all!"; :053 waived: its JP has no dialect marker
- [x] SMAP04_35:045/046 - literal "twist": fixed: "I'll squash you flat in no time!" / "I, the great Gold Oni, will squash you like a bug!"
- [x] SMAP04_35:055 - second person in narration: fixed: "The golden statue in front of Momotaro started to move!"
- [x] SMAP02_33:052 - flag-game half lost: fixed: "Lie down with dogs... and get up with flags!" (keep-bad-company idiom = 朱に交われば, flag swerve kept; scroll HMAP26_66:168 mirrored by parent)
- [x] Item-get articles (also 02 #6, 04 #3): fixed: "got a/an X" for consumables (Antidote, Rice Ball, Rice Bale, Millet Dumpling, Hermit's Peach, Oni Tear), "got the X" for one-off items and every card, as the 199 existing lines do: SMAP02_33:006/011/021/034/039/068/071/074/075/086-089, SMAP03_113:031/055/064/066/077/078, SMAP04_35:044/086/087/088, SMAP05_31:007/008/009, SMAP06_36:010/020/030/085, SMAP08_35:014/050, SMAP16_37:095; same-JP HMAP2606_66:036/039 mirrored by parent

## 02 companions
- [x] DMAP02_42:030 - ambiguous Ryutoki addressee: fixed: "But you can never defeat the great Ryutoki!"
- [x] DMAP00_26:001/004/005 - Pheasant refrain drift: fixed: "Those millet dumplings hanging at your waist... won't you give one to me?" (= Dog/Monkey), "That's too much!" / "Please don't say such cruel things...", :004 "I shall wait right here until you give me a millet dumpling! Kek kek!"
- [x] SMAP08_35:062 - あんちゃん two ways: fixed: "Be good friends with Big Bro Kintaro!" (= DMAP02_42:019/021)
- [x] SMAP08_35:054 - Kintaro stiff: fixed: "I'm joinin' up with ya!" / "With me on your side..." / "Let's be pals, Momotaro!"
- [x] Heal message (also 03 #4): fixed: one form "{str} recovered all SP and HP!" in SMAP06_36:027 and the cow-milk lines SMAP01_33:021, SMAP12_33:038, SMAP20_33:022 ("Gulp gulp gulp! ..."); no possessive glued to {str}
- [x] SMAP06_36:028 - cow line: fixed: "Is your tummy full? Moo!" (= SMAP01_33:022)
- [x] Item-get articles: see 01

## 03 rival and princess
- [x] BM000_1:180 (also 13 #2) - dangling grammar, "punished": fixed: "At last! At last!{wait}At last! Momotaro has taught Yashahime a lesson!" (78 BM copies; same verb as BM111_1:216 for Enma)
- [x] SMAP12_33:051/053 - person mixing: resolved earlier (b026-b030): both already read "...you, Momotaro-san, ... I reckon."
- [x] OMAP00_45:002 - fixed: "You saved the Turtle from Ryugu Palace?!"
- [x] Heal message: see 02

## 04 hope
- [x] Important 1 - museum scrolls vs village proverbs: resolved by parent: all 50 scrolls HMAP26_66:165-214 now copy their village proverb verbatim; 209's source is embedded inside OMAP00_43:056 and was found in the final independent review. The regression test covers that wrapped message explicitly, and village lines changed in this pass are re-mirrored (SMAP02_33:052, OMAP00_49:038).
- [x] Important 2 - Ashura laugh: fixed: BM000_1:144-151 "Fufufufufufu!" as in the field (HMAP26_66:000-019), closing laughs of :150/:151 too, all 78 BM copies
- [x] SMAP16_37:095 - fixed: "Momotaro got the {col4}Guts Orb{col0}!"
- [x] SMAP13_37:134 - waived: Buddha's Bowl is a possessive name and takes no article (rule from 06); :133 "the Dragon Necklace" is not possessive
- [x] SMAP16_37:028 - fixed: "It's a Ginji the Pickpocket Card!"
- [x] SMAP16_37:139 - stray closing quote: waived: the JP has a final page holding only a stray 」 after its last {wait}; lint needs the EN to end the same way ("page 2 is empty but the JP page has text" when removed)
- [x] Elder caps - fixed: HMAP20_18:001 "I am the Elder of the Capital!", :004 "The Elder was so happy..." (SMAP16_37:246/248 already "Elder")
- [x] BM000_1:153 - fixed: "N-no way!" (78 copies)
- [x] HMAP26_66:055/056/060 - resolved earlier (b051-b055): "kimono", "harpoon" already lower case

## 05 friendship
- [x] OMAP00_49:036 - resolved earlier (b031-b035): "A watched pheasant never sings!" twists a real idiom
- [x] OMAP00_49:038 - fixed: "Heaven is in the eye of the beholder... looks aren't everything!" (beauty/beholder idiom with 極楽's heaven, ends on 見てくれだけが人間じゃない; scroll :212 mirrored by parent)
- [x] Kappa number - fixed: plural in DMAP06_20:013/014/016/019 ("Kappa that steal anything show up...", "The Kappa always hide what they steal...") like the villagers
- [x] DMAP08_43:003 / OMAP00_49:027 - fixed: "Urashima rejoined the party!" / "Kintaro rejoined the party!"
- [x] DMAP07_28:000 - fixed: "rumors"; DMAP11_47:004 (07) "realize"; a final review found the isolated "travellers" variant below.
- [x] DMAP06_20:006 - fixed: "the three besides the Dragon Necklace and Buddha's Bowl!"
- [x] SMAP20_33:032/033 vs EVT057_11 - fixed: SMAP20_33 now "prayers" / "the light of a beautiful rainbow shone over the village!"
- [x] SMAP20_33:027 - fixed: "I'm the chief of this village, I am!"

## 06 five treasures
- [x] SMAP23_33:016 - trailing W: waived: no byte or runtime evidence that the decoded "W" is a wait code; a {wait} changes the box flow; left as is
- [x] Articles before possessive names - fixed: SMAP22_35:059 "Momotaro got {col4}Orihime's Flute{col0}!", SMAP23_33:030/034 "Momotaro got {col10}Kaguya's Grandpa Card{col0}!" / "...Grandma Card"
- [x] OMAP00_51:016 - fixed: "Kappa" both times
- [x] OMAP00_51:010 - fixed: "Good luck with your oni slaying!"
- [x] OMAP00_51:019 - fixed: "What's that? A fortune teller should know that just by looking at you?"
- [x] SMAP22_35:069 - resolved earlier (b026-b030): "Here's the map I drew for you, Momotaro-san, I reckon."
- [x] SMAP22_35:073 - fixed: "Age before beauty... so it's Granny's turn!" (07's corrected suggestion; no clash with OMAP00_53:029)

## 07 hell
- [x] DMAP11_47:007/009 - fixed: "Hmm! So you've finally come this far, Momotaro!" / "Hmm! Hmm! Hmmmm!"
- [x] North Cape article - fixed: no article, as a place name (FONT_5:033): OMAP00_53:002/016
- [x] OMAP00_53:027 - fixed: "oni-slaying journey" (= OMAP00_51:007)
- [x] BM000_1:139 "--" - waived: the translator brief allows ASCII `--` and the font draws it; lint clean
- [x] DMAP11_47:004 - fixed: "realize"
- [x] DMAP15_56:019 - fixed: "I could stay forever, but let's head on home now, Momotaro!"
- [x] OMAP00_53:019 - fixed: "Very well! Then let me tell your fortune!" (= OMAP00_49:020, OMAP00_51:020)
- [x] SMAP22_35:073 correction - applied in 06

## 08 farewells
- [x] END02_14:053 - fixed: "Confused Monk, Norihide Igarashi"
- [x] END02_14:016/018/021/027 - crying voice: fixed: "Hnngh!!" / "Hnnngh!!!" / "Hnnnngh!!" / "Hnngh!"
- [x] END02_14:004/005 - fixed: "Even if we alone were happy, that wouldn't be true happiness!" / "...that's true happiness!"
- [x] END02_14:003 - fixed: "But..."
- [x] END02_14:025 - fixed: "Come see the festival, y'hear!"
- [x] END01_11:004 - fixed: "I've been hearing tales of your deeds all along! Makes this old man proud!"

## 09 hermits
- [x] Hermit formula - fixed: "Hurry and learn my art, and teach those oni a lesson!" (WMAP20_28:005, WMAP21_28:005, WMAP22_28:006, WMAP23_28:006, WMAP24_28:001, WMAP25_28:001); "But first, you must undergo my rather strict training!" (WMAP21_28:005, WMAP22_28:007, WMAP23_28:006, WMAP24_28:001, WMAP25_28:001); "I'll be waiting here forever!" (WMAP21_28:004, WMAP23_28:004); WMAP23_28:003 the canon injured-Urashima pages; WMAP19_34:006 "At this rate, you'll never teach Enma a lesson!"; WMAP22_28:012 comma
- [x] Proverb frame - fixed: "There's a proverb written here!" in WMAP24_28:010, WMAP25_28:006, WMAP19_34:011
- [x] ぱわぁあっぷ - fixed: "gets a powwwer-up" in WMAP11_28:006, WMAP23_28:012, WMAP19_34:009
- [x] WMAP16_28:014 - fixed: "Fortune-telling: hit or miss... or hurl!" (当たるも八卦 -> 吐き気)
- [x] WMAP00_28:005 - fixed: "working hard at oni slaying!" (glossary form; "slaying oni" fails the 鬼たいじ check)
- [x] Cave case - fixed: "cave" in WMAP01_28:000/003/004, WMAP06_28:003; named caves (Row Cave...) and the FONT_5:000 label keep the capital
- [x] WMAP16_28:007 - fixed: "What's this! You lot have nothing on you at all!"

## 10 museum and cards
- [x] Important 1 - Word Maze key vs reveal: resolved by parent: four keys changed (Death at your door, Luck has its twists, Look before you leap, What's done is done) and all 41 HMAP2606_66:045-085 sayings match their accepted answers; regression and final independent chapter-10 review both pass.
- [x] HMAP2606_66:176 - fixed by parent: the oni-crying line ties to the answer "Even oni cry"
- [x] HMAP2606_66:091 - waived: the polish-pass "soybeans grew in soy sauce" mix-up already replaced the red-bean line and keeps the JP's bean misreading joke
- [x] HMAP8300_18:002 - fixed: "It's me! Ginji, the one who picked yer pocket and took yer treasure in Netaro Village!"
- [x] HMAP2607_66:005 - fixed: "Ask here for a guide to the tower!"

## 11 minigames and travel
- [x] Z00_19:021/025/028 - fixed: "Shall I join your party?" / "So Kintaro has joined you!"
- [x] ×ボタン - fixed: "Cross button" everywhere, beside "Circle button" (9 uses): WMAP02_28:001, WMAP08_28:001, SMAP13_37:125 (FUKU_11:002 already Cross)
- [x] Z00_19:035 - fixed: "'Momotaro-san! Surely you are someone who treasures friendship!'"
- [x] MOGURA_11:013 - fixed: "Remember, tomorrow's another day, and a bright one!"
- [x] PT00_5:019 - fixed: "The Jizo Row, friends to all travelers, are lending Momotaro-san a hand! How nice! How nice!"

## 12 system and shops
- [x] FONT_10:111 - fixed: "Enoppi-doo! That hurt a little, bombee!"
- [x] つづら wicker chest vs basket - waived (marked optional): the shop riffs on the tongue-cut-sparrow basket, the field lines count dungeon chests; each reads right in place
- [x] FONT_6:496, FONT_6:711/725/727, SHOP save slot lines - resolved earlier (b006-b010, b011-b015)

## 13 battle
- [x] Important 1 - BM008_1:248: fixed: "Camus{n}Malave{n}Rose{n}Mahomes" (BayStars decoys; single table)
- [x] BM000_1:180 - see 03
- [x] BM000_1:152 - fixed: "Grrr! But! Not yet! Me! Against me! You can't win! You cannot win!" (78 copies)
- [x] BM114_1:212 / BM115_1:212 - fixed: "Kintaaan Pluuus!" / "Kintaaan Maaax!" (= FONT_11:052/055)
- [x] BM008_1:258 - resolved earlier (b061-b065): "Gallstone Natsume"

## Final independent rereview decisions

The complete regenerated chapters are reviewed in `work/qa/story/reports/final_*.md`.
The following optional Minors are explicitly waived; no Critical or Important issue is waived.

- [x] 01 SMAP01_33:085 "punishing enemies": retained; it describes the battle/card mechanic accurately and is not a recurring character refrain.
- [x] 02 DMAP02_42:014 "teach you some pain": retained as Ryutoki's exaggerated villain threat; the meaning and speaker remain clear.
- [x] 02 OMAP00_43:017 "punish Enma": retained as a natural paraphrase of the goal; the fortune teller need not use the hermits' exact training formula.
- [x] 02 DMAP02_42:007 split vocative: retained; the emphatic separate "Momotaro!" fits Kintaro's excited voice.
- [x] 03 SMAP12_33:008/040 "the Hermit": retained as a title referring to the particular local hermit; no name or referent changes.
- [x] 05 SMAP20_33:039 "one twist": retained; Salt Oni's physical boast remains intelligible and need not copy Gold Oni's threat.
- [x] 05 OMAP00_49:014/015 fortune-teller paraphrases: retained; both preserve his repeated boast, register and timing without a callback depending on exact wording.
- [x] 05 DMAP06_20:000 "Momotaro, is it!": retained as an exclamatory recognition challenge rather than an information-seeking question.
- [x] 07 OMAP00_53:000 training paraphrase: retained; advice, level and voice are unchanged, and the location-specific instruction is clear.
- [x] 07 DMAP11_47:007 "the Yomi Tower": retained; the article is grammatical in this descriptive introduction and does not alter the place name.
- [x] 09 DMAP18_27:001 "bestow" vs "grant": retained; both have the same formal elder register, and the art name is exact.
- [x] 09 WMAP17_28:010 / WMAP22_28:012 "help" vs "save": retained; both express the same warning in their separate training contexts.
- [x] 09 WMAP01_28:001 "What were you listening to?!": retained as the hermit's sarcastic rebuke; the intended criticism is clear.
- [x] 10 HMAP2606_66:015/020 vs :021/025/026 "saying" / "word": retained; the saying is entered as one continuous letter sequence, so the input prompt's "word" still describes its game representation.
- [x] 10 HMAP8300_18:018 "Gah" build-up: retained as a gasp followed by delight; the comic reaction survives without reproducing the Japanese phonetic join.
- [x] 11 SUIEI_9:000/004/017 tilde: accepted as a specific sing-song announcer exception; the supported glyph communicates the drawn-out voice and passes fit checks.
- [x] 11 YUMI2_10:010 "Sum": retained; the compact scoreboard label accurately identifies the added score and is already fitted.
- [x] 11 PT00_5:010 "Momotaro-san's friends": retained; the museum narrator emphasizes friendship while recounting the same party-joining event.
- [x] 04 HMAP26_66:001: fixed "1,000th" to match the preceding count's formatting.
- [x] 04 HMAP26_66:209: fixed the final missed callback to match the quoted proverb inside OMAP00_43:056; the extended regression test reproduced the mismatch before the fix.
- [x] 12 SHOP:404/418/448: fixed "What would you like to sell?" to preserve the flower clerk's polite voice; all three word-identical shop prompts use the same neutral wording, as required by the duplicate-text gate.
- [x] 13 BM008_1:306: fixed the decoy "Cucumber" to "Melon" (うり), matching the Kanji Oni's literal component hint; the correct answer remains Pumpkin.
- [x] 04 DMAP04_21:003 "travellers": retained as an isolated regional spelling variant; it does not affect meaning, voice or readability. The earlier claim that none remained is corrected above.
- [x] 04 DMAP04_21:004/007 "punish" vs village "teach a lesson": retained; both communicate the same quest objective and target without a callback depending on exact wording.
- [x] 04 SMAP16_37:001 level advice: retained; the location's level 27 requirement and training instruction are exact, with the same advisory voice.
- [x] 04 SMAP13_37:000 "?!": retained as surprised recognition; the speaker and question are clear.
- [x] 04 repeated sleeping-animal proverb base: retained; the cow and riot twists make different jokes in separate locations, and each museum callback matches its source.
- [x] Earlier HMAP26_66:191 polish wording is historical; the subsequent callback repair supersedes it with SMAP21_33's exact wording, as recorded in the story-review section.
