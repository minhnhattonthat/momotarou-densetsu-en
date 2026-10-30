-- Log the first fetch of each FONT table string through get_string(index a0, table a1) at 0x8003D944, with its
-- caller: which screen draws a label (docs/re/windows.md width coverage).
--   emu.py ROM --debugger --state-in S --script tools/debug/strlog.lua --route-str "..."
local TABLES = { [0x80180000] = "FONT_7", [0x80184000] = "FONT_6", [0x8018C000] = "FONT_5" }
local seen = {}
L.on_exec(0x8003D944, function()
  local r = PCSX.getRegisters().GPR.n
  local t = TABLES[tonumber(r.a1)]  -- registers are uint32 cdata: never equal to a number table key
  if not t then return end
  local idx = tonumber(r.a0) % 0x10000
  local key = t .. idx .. ":" .. tonumber(r.ra)
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("f%d %s:%03d ra=%08X", L.frame, t, idx, r.ra))
end)
