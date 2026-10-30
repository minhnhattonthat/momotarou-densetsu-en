-- Cold-boot warp to any scene in tools/debug/scenes.lua (docs/re/debug.md has the RAM map).
--   emu.py rom/x.cue --out D --script tools/debug/warp.lua --var "SCENE='village'" --frames 3000 [--state-out S]
-- Flow: mash circle until New Game starts the intro event (state 5, event 6), replace it with a map load
-- (what goto_map 0x8001A4D8 writes), wait for the field loop, then start the scene's event / minigame / battle.
-- Arrival: shot "scene.png", state to STATE_OUT, exit 0. Not reached by FRAMES: exit 2 (L.fail).
-- Opt-in globals: GOD=1 (party HP pinned), MONEY=n.
local scenes = dofile(SCENES or "tools/debug/scenes.lua")
local sc = scenes[SCENE]
if not sc and tostring(SCENE):match("^map:") then  -- ad-hoc "map:<id>[:x:y]" (tools/debug/maps.txt)
  local id, x, y = SCENE:match("^map:(%d+):?(%d*):?(%d*)")
  sc = { map = tonumber(id), x = tonumber(x), y = tonumber(y) }
end
if not sc then error("unknown SCENE " .. tostring(SCENE)) end
local m = PCSX.getMemPtr()
local function r8(a) return m[a & 0x1FFFFF] end
local function r16(a) a = a & 0x1FFFFF; return m[a] | (m[a + 1] << 8) end
local function w8(a, v) m[a & 0x1FFFFF] = v & 0xFF end
local function w16(a, v) a = a & 0x1FFFFF; m[a] = v & 0xFF; m[a + 1] = (v >> 8) & 0xFF end
local function w32(a, v) w16(a, v & 0xFFFF); w16(a + 2, (v >> 16) & 0xFFFF) end

local STATE, MAP, EVENT, MINIGAME, FIELD_RUN = 0x800847E0, 0x800847D6, 0x800847DF, 0x800846E8, 0x800846FA
local function state() local s = r16(STATE); return s >= 0x8000 and s - 0x10000 or s end
local function in_field() return state() == 2 and r16(FIELD_RUN) == 1 end

local function goto_map(map, x, y, dir)
  w16(0x80094A50, 1); w16(0x80094A52, map); w16(0x80094A54, x); w16(0x80094A56, y); w16(0x80094A58, dir or 2)
  w16(MAP, map); w16(STATE, 0)
end
local function apply_pokes(list)
  for _, p in ipairs(list or {}) do ({ [1] = w8, [2] = w16, [4] = w32 })[p[2]](p[1], p[3]) end
end

-- Title menu box on screen: white box top edge and green post (pixels read from f002000 of a cold boot).
local function title_ready()
  local s = PCSX.GPU.takeScreenShot()
  if s.width ~= 320 or s.height < 200 or tonumber(s.bpp) ~= 0 then return false end
  local p = require("ffi").cast("const uint16_t*", s.data.data)
  local function px(x, y) return p[y * s.width + x] & 0x7FFF end
  local g = px(60, 152)
  return px(100, 154) == 0x7FFF and px(150, 154) == 0x7FFF and px(200, 154) == 0x7FFF
    and (g >> 5 & 31) > 15 and (g & 31) < 4
end

local phase, t, quiet = sc.title and "title" or "boot", 0, 0
local routing = true                         -- the scene's own route is still playing (mash presses don't count)
local fmap = sc.map or 1                     -- events, minigames and battles start from a field map
local SETTLE = SETTLE or sc.settle or 120    -- frames after the scene starts before the proof shot (--var SETTLE=n)
local function arrive(f)
  L.shot("scene.png")
  L.log(string.format("%d arrived %s map %d state %d", f, SCENE, r16(MAP), state()))
  if STATE_SAVE or STATE_OUT then L.save_state(STATE_SAVE or STATE_OUT) end
  L.finish(0)
end

L.on_frame(function(f)
  if GOD then for _, a in ipairs({ 0x800849D8, 0x80091252, 0x800FE300, 0x800FEE30 }) do w16(a, 999) end end -- GS code
  if MONEY then w32(0x800912E0, MONEY) end
  if phase == "title" then
    if f % 5 == 0 and title_ready() then
      L.log(f .. " title menu up")
      for _, s in ipairs(sc.route or {}) do L.press(s[2], s[1]) end
      phase = "scene"; t = f
    elseif f % 90 == 0 and L.route_done() then
      L.press("circle", 6)                           -- the logo screen shows the menu box after a press
    end
  elseif phase == "boot" then
    if state() == 5 and r8(EVENT) == 6 then         -- New Game picked: the intro event is about to load
      apply_pokes(sc.pokes)
      goto_map(fmap, sc.x or 25, sc.y or 20, sc.dir)
      phase = "map"; L.log(f .. " intro replaced, loading map " .. fmap)
    elseif L.route_done() and f % 30 == 0 then
      L.press("circle", 6)                           -- title: "Hajimete" is the default
    end
  elseif phase == "map" then
    quiet = in_field() and quiet + 1 or 0
    if quiet >= 30 then
      if sc.event then
        w8(EVENT, sc.event); w16(STATE, 5); w16(FIELD_RUN, 0); phase = "scene"; t = f
      elseif sc.minigame then
        w8(MINIGAME, sc.minigame); w16(STATE, 4); w16(FIELD_RUN, 0); phase = "scene"; t = f
      else
        phase = "scene"; t = f
      end
      for _, s in ipairs(sc.route or {}) do L.press(s[2], s[1]) end
    end
  elseif phase == "scene" and routing then
    t = f                                            -- settle counts from the end of the scene's route
    routing = not L.route_done()
  elseif phase == "scene" and sc.until_state and state() ~= sc.until_state then
    if L.route_done() then L.press(math.floor(f / 90) % 2 == 0 and "down" or "up", 90) end  -- walk until it happens
    t = f
  elseif phase == "scene" and L.route_done() and f - t >= SETTLE then
    arrive(f)
  elseif phase == "scene" and sc.mash and L.route_done() and (f - t) % sc.mash == 0 then
    L.press("circle", 6)                             -- click through dialogue while settling
  end
  if FRAMES and f >= FRAMES - 1 then L.fail(string.format("%s not reached (phase %s, state %d map %d)",
    SCENE, phase, state(), r16(MAP))) end
end)
