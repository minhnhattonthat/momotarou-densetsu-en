-- Scene list for tools/debug/warp.lua. name = { map, x, y, dir (field start; default map 1 at 25,20),
-- event = n (0x800847DF) | minigame = n (0x800846E8) | until_state = n (walk up/down until the main-loop
-- state is n: 1 = random battle) | title = true (no New Game: route starts at the title menu box),
-- route = {{frames, "keys"}, ...} after arrival, pokes = {{addr, size, value}, ...} before the map load,
-- settle = frames after the route before the proof shot, mash = n (press circle every n frames while settling) }.
-- Ad hoc: SCENE='map:<id>:<x>:<y>'. Map ids: tools/debug/maps.txt. Events / minigames: docs/re/debug.md.
local TALK = { { 6, "up" }, { 20, "-" }, { 6, "circle" }, { 30, "-" }, { 6, "circle" } }  -- menu > hanasu
local function menu(downs, right)
  local r = { { 6, "circle" }, { 20, "-" } }
  if right then r[#r + 1] = { 6, "right" }; r[#r + 1] = { 20, "-" } end
  for _ = 1, downs do r[#r + 1] = { 6, "down" }; r[#r + 1] = { 20, "-" } end
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
  menu_tsuyosa   = { map = 1, settle = 90, route = menu(3) },
  menu_shiraberu = { map = 1, settle = 90, route = menu(0, true) },
  menu_soubi     = { map = 1, settle = 90, route = menu(1, true) },
  menu_meirei    = { map = 1, settle = 90, route = menu(2, true) },
  menu_settei    = { map = 1, settle = 90, route = menu(3, true) },
  -- 2nd town (SMAP01 = map 2) and its interiors HMAP00-12 room 0: stand at 20,18, face up, talk, click on
  town2          = { map = 2 },
  shop_65        = { map = 65, x = 20, y = 18, route = TALK, mash = 40, settle = 240 },  -- weapons: buy list
  shop_82        = { map = 82, x = 20, y = 18, route = TALK, mash = 40, settle = 240 },  -- buy list
  shop_99        = { map = 99, x = 20, y = 18, route = TALK, mash = 40, settle = 240 },  -- buy list
  talk_134       = { map = 134, x = 20, y = 18, route = TALK, mash = 40, settle = 240 },
  talk_151       = { map = 151, x = 20, y = 18, route = TALK, mash = 40, settle = 240 },
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
  ev_end00       = { event = 15, settle = 600 },    -- END00
  ev_end01       = { event = 16, settle = 600 },    -- END02 (staff roll over the walk) then END01 (epilogue)
  credits_end    = { event = 16, settle = 5400 },   -- last staff-roll page
  epilogue       = { event = 16, settle = 24600, mash = 60 },  -- END01: village at night
  ev_pt00        = { event = 17, settle = 300 },    -- PT00
  -- minigames (main-loop state 4)
  mg_fuku        = { minigame = 0, settle = 300 },  -- FUKU
  mg_yumi1b      = { minigame = 2, settle = 300 },  -- YUMI1, archery
  mg_yumi2       = { minigame = 3, settle = 300 },  -- YUMI2
  mg_suiei       = { minigame = 4, settle = 300 },  -- SUIEI
  mg_daruma      = { minigame = 5, settle = 300 },  -- DARUMA
  mg_mogura      = { minigame = 6, settle = 300 },  -- MOGURA
  -- Not reachable by a plain warp (overlay loads, screen stays black; needs its caller's context):
  -- event 5 (EVT069), minigame 1 (YUMI1 other entry). docs/re/debug.md.
}
