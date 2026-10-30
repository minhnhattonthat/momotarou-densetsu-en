-- Scene list for tools/debug/warp.lua. name = { map, x, y, dir (field start; default map 1 at 25,20),
-- event = n (0x800847DF) | minigame = n (0x800846E8) | until_state = n (walk up/down until the main-loop
-- state is n: 1 = random battle) | title = true (no New Game: route starts at the title menu box),
-- route = {{frames, "keys"}, ...} after arrival, pokes = {{addr, size, value}, ...} before the map load, hold =
-- pokes rewritten every frame after it, money = n, god = true (as --var MONEY= / GOD=1),
-- settle = frames after the route before the proof shot, mash = n (press circle every n frames while settling) }.
-- Ad hoc: SCENE='map:<id>:<x>:<y>'. Map ids: tools/debug/maps.txt. Events / minigames: docs/re/debug.md.
local TALK = { { 6, "up" }, { 20, "-" }, { 6, "circle" }, { 30, "-" }, { 6, "circle" } }  -- menu > hanasu
local SHOP_BUY = { { 6, "up" }, { 20, "-" }, { 6, "circle" }, { 30, "-" }, { 6, "circle" }, { 240, "-" } }
for _ = 1, 4 do SHOP_BUY[#SHOP_BUY + 1] = { 6, "circle" }; SHOP_BUY[#SHOP_BUY + 1] = { 50, "-" } end
SHOP_BUY[#SHOP_BUY + 1] = { 6, "circle" }                    -- the buy / sell / trade-in / leave menu: buy
SHOP_BUY[#SHOP_BUY + 1] = { 40, "-" }; SHOP_BUY[#SHOP_BUY + 1] = { 6, "circle" }
SHOP_BUY[#SHOP_BUY + 1] = { 240, "-" }; SHOP_BUY[#SHOP_BUY + 1] = { 6, "circle" } -- past "what will you buy?"
local ITEMS = {}                                             -- inventory: 6-byte slots, u16 item id (0xFFFF empty)
for i = 0, 23 do ITEMS[#ITEMS + 1] = { 0x8009133A + 6 * i, 2, i + 1 } end
local PARTY = {}                                             -- u16 per character id != 0: with the party (0x8003FB64)
for id = 4, 13 do PARTY[#PARTY + 1] = { 0x80091310 + 2 * id, 2, 1 } end
local SKILLS = { { 0x8009195C, 2, 0xFFFF } }                -- every companion skill unlocked (bits read at 0x80040568)
for _, p in ipairs(PARTY) do SKILLS[#SKILLS + 1] = p end
local function menu(downs, right)
  local r = { { 6, "circle" }, { 20, "-" } }
  if right then r[#r + 1] = { 6, "right" }; r[#r + 1] = { 20, "-" } end
  for _ = 1, downs do r[#r + 1] = { 6, "down" }; r[#r + 1] = { 20, "-" } end
  r[#r + 1] = { 6, "circle" }
  return r
end
local function status_scroll(key)
  local r = menu(3)
  r[#r + 1] = { 90, "-" }
  r[#r + 1] = { 650, key }  -- these panels scroll only while a direction is held
  return r
end
local function setting(which)
  local r = menu(3, true)
  r[#r + 1] = { 90, "-" }
  for _ = 1, which do r[#r + 1] = { 6, "down" }; r[#r + 1] = { 30, "-" } end
  r[#r + 1] = { 6, "circle" }
  return r
end
return {
  -- title (title = true: no New Game; the route starts once the title menu box is on screen)
  title          = { title = true, settle = 30 },
  title_load     = { title = true, route = { { 6, "right" }, { 20, "-" }, { 6, "circle" } }, settle = 300 },
  -- field
  house          = { map = 292, x = 18, y = 13 },
  village        = { map = 1 },
  world          = { map = 0, x = 60, y = 60 },
  -- field menu: hanasu shiraberu / jutsu soubi / dougu meirei / tsuyosa settei (2 columns x 4 rows)
  menu           = { map = 1, route = { { 6, "circle" } }, settle = 60 },
  menu_jutsu     = { map = 1, settle = 90, route = menu(1) },
  menu_dougu     = { map = 1, settle = 90, route = menu(2) },
  menu_items     = { map = 1, settle = 90, route = menu(2), pokes = ITEMS },  -- item list, items 1-24
  -- techniques: 9 learned bits per member at 0x800FE3A8 + 2 * member (flag check 0x800FC0C8, count 0x800DF5A4)
  menu_techs     = { map = 1, settle = 90, route = menu(1), hold = { { 0x800FE3A8, 2, 0x1FF } } },
  menu_tsuyosa   = { map = 1, settle = 90, route = menu(3) },
  menu_shiraberu = { map = 1, settle = 90, route = menu(0, true) },
  menu_soubi     = { map = 1, settle = 90, route = menu(1, true) },
  menu_meirei    = { map = 1, settle = 90, route = menu(2, true) },
  menu_settei    = { map = 1, settle = 90, route = menu(3, true) },
  orders_party   = { map = 1, settle = 90, route = menu(2, true), hold = PARTY },  -- companions 4-13 with Momotaro
  enon_world     = { map = 0, x = 60, y = 60, settle = 300, hold = SKILLS, mash = 60,  -- Enon's skill: direction
                     route = { { 6, "circle" }, { 20, "-" }, { 6, "right" }, { 20, "-" }, { 6, "down" }, { 20, "-" },
                               { 6, "down" }, { 20, "-" }, { 6, "circle" }, { 30, "-" }, { 6, "down" }, { 20, "-" },
                               { 6, "down" }, { 20, "-" }, { 6, "down" }, { 20, "-" }, { 6, "down" }, { 20, "-" },
                               { 6, "circle" }, { 30, "-" }, { 6, "circle" }, { 30, "-" }, { 6, "circle" } } },
  town_warp      = { map = 2, settle = 240, hold = SKILLS, mash = 60,               -- pheasant's Town Warp list
                     route = { { 6, "circle" }, { 20, "-" }, { 6, "right" }, { 20, "-" }, { 6, "down" }, { 20, "-" },
                               { 6, "down" }, { 20, "-" }, { 6, "circle" }, { 30, "-" }, { 6, "down" }, { 20, "-" },
                               { 6, "down" }, { 20, "-" }, { 6, "circle" }, { 40, "-" }, { 6, "down" }, { 20, "-" },
                               { 6, "circle" } } },
  status_summary = { map = 1, settle = 60, route = status_scroll("left") },
  signs_stone    = { map = 5, x = 50, y = 26 },
  signs_flower   = { map = 9, x = 20, y = 41 },
  signs_hut_inn  = { map = 20, x = 20, y = 41 },
  signs_hut_tea  = { map = 20, x = 20, y = 67 },
  signs_hut_bank = { map = 20, x = 90, y = 67 },
  signs_play     = { map = 22, x = 92, y = 41 },
  signs_carddojo = { map = 22, x = 20, y = 67 },
  signs_cloth    = { map = 22, x = 25, y = 20 },
  signs_wood     = { map = 34, x = 40, y = 22 },
  signs_roof     = { map = 34, x = 20, y = 31 },
  puzzle_oni     = { map = 403, x = 22, y = 33 },
  status_treasure = { map = 1, settle = 60, route = status_scroll("right") },
  setting_rumble = { map = 1, settle = 90, route = setting(0) },
  setting_music  = { map = 1, settle = 90, route = setting(1) },
  setting_text   = { map = 1, settle = 90, route = setting(2) },
  -- 2nd town (SMAP01 = map 2) and its interiors HMAP00-12 room 0: stand at 20,18, face up, talk, click on
  town2          = { map = 2 },
  shop_65        = { map = 65, x = 20, y = 18, route = TALK, mash = 40, settle = 240 },  -- weapons: buy list
  shop_82        = { map = 82, x = 20, y = 18, route = TALK, mash = 40, settle = 240 },  -- buy list
  shop_99        = { map = 99, x = 20, y = 18, route = TALK, mash = 40, settle = 240 },  -- buy list
  -- weapon buy list; timed for marker/English text (JP types faster and the last press closes the list)
  shop_65_buy    = { map = 65, x = 20, y = 18, money = 99999, settle = 120, route = SHOP_BUY },
  talk_134       = { map = 134, x = 20, y = 18, route = TALK, mash = 40, settle = 240 },
  talk_151       = { map = 151, x = 20, y = 18, route = TALK, mash = 40, settle = 240 },
  talk_36        = { map = 36, route = TALK, mash = 40, settle = 600 },  -- OMAP00 town: NPC north of the start
  map_36         = { map = 36 },  -- same spot, no talk: base state for name entry (docs/re/debug.md, call.lua)
  -- the other interiors (nobody at 20,18): temple 47, houses
  in2_47         = { map = 47, x = 20, y = 18 },
  in2_116        = { map = 116, x = 20, y = 18 },
  in2_168        = { map = 168, x = 20, y = 18 },
  in2_185        = { map = 185, x = 20, y = 18 },
  in2_202        = { map = 202, x = 20, y = 18 },
  in2_218        = { map = 218, x = 20, y = 18 },
  in2_241        = { map = 241, x = 20, y = 18 },
  dungeon1       = { map = 395, x = 21, y = 15 },  -- DMAP01
  -- battle (main-loop state 1)
  battle         = { map = 0, x = 60, y = 60, until_state = 1, settle = 400 },
  battle_long    = { map = 0, x = 60, y = 60, until_state = 1, settle = 2400, mash = 100, god = true },
  battle_lists   = { map = 0, x = 60, y = 60, until_state = 1, settle = 2400, mash = 100, god = true, pokes = ITEMS,
                     hold = { { 0x800FE3A8, 2, 0x1FF } } },  -- items + techniques for the battle lists
  -- events (main-loop state 5): file loaded in brackets
  ev_00          = { event = 0, settle = 300 },     -- EVT003
  ev_01          = { event = 1, settle = 300 },     -- EVT006
  ev_02          = { event = 2, settle = 300 },     -- EVT015 / EVT057
  ev_03          = { event = 3, settle = 300 },     -- EVT057
  ev_04          = { event = 4, settle = 300 },     -- EVT076
  ev_furo0       = { event = 7, settle = 300 },     -- FURO_0..4
  ev_furo1       = { event = 8, settle = 300 },
  ev_furo2       = { event = 9, settle = 300 },
  ev_furo3       = { event = 10, settle = 300 },
  ev_furo4       = { event = 11, settle = 300 },
  ev_atok        = { event = 12, settle = 300 },    -- ATOK
  ev_amap        = { event = 13, settle = 300 },    -- AMAP
  ev_card        = { event = 14, settle = 300 },    -- EVTCARD: card album
  ev_card_all    = { event = 14, settle = 300, hold = { { 0x8004295C, 2, 1 } } },  -- GameShark "all cards open"
  ev_end00       = { event = 15, settle = 600 },    -- END00
  ev_end01       = { event = 16, settle = 600 },    -- END02 (staff roll over the walk) then END01 (epilogue)
  credits_end    = { event = 16, settle = 5400 },   -- last staff-roll page
  ending_plate   = { event = 16, settle = 35640, mash = 120 }, -- centered final plate, after the right-to-left wipe
  epilogue       = { event = 16, settle = 24600, mash = 60 },  -- END01: village at night
  ev_pt00        = { event = 17, settle = 300 },    -- PT00
  -- minigames (main-loop state 4)
  mg_fuku        = { minigame = 0, settle = 300 },  -- FUKU
  battle_cmd     = { map = 0, x = 60, y = 60, until_state = 1, settle = 1420, mash = 40, god = true },
  fuku_choices   = { minigame = 0, settle = 220,
    route = { { 400, "-" }, { 6, "circle" }, { 100, "-" }, { 6, "circle" } } },
  mg_yumi1b      = { minigame = 2, settle = 300 },  -- YUMI1, archery
  mg_yumi2       = { minigame = 3, settle = 300 },  -- YUMI2
  mg_suiei       = { minigame = 4, settle = 300 },  -- SUIEI
  mg_daruma      = { minigame = 5, settle = 300 },  -- DARUMA
  daruma_choices = { minigame = 5, settle = 300,
    route = { { 400, "-" }, { 6, "circle" }, { 100, "-" }, { 6, "circle" }, { 100, "-" },
              { 6, "circle" }, { 200, "-" }, { 6, "up" }, { 40, "-" }, { 6, "circle" },
              { 600, "-" }, { 6, "circle" } } },
  mg_mogura      = { minigame = 6, settle = 300 },  -- MOGURA
  -- Not reachable by a plain warp (overlay loads, screen stays black; needs its caller's context):
  -- event 5 (EVT069), minigame 1 (YUMI1 other entry). docs/re/debug.md.
}
