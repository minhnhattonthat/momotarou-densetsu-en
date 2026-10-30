-- FORCED entry: next Big Sis talk runs the maze NPC clue routine for SLOT (0..19), keeping $ra.
-- The clue table and message path remain the game's own. Use --debugger --var SLOT=10 on map 312.
local done = false
L.on_exec(0x80168850, function()
  if done then return end
  done = true
  local r = PCSX.getRegisters()
  L.log(string.format("f%d redirect 80168850 -> 8016932C slot=%d ra=%08X", L.frame, SLOT, r.GPR.n.ra))
  r.GPR.n.a0 = SLOT
  r.pc = 0x8016932C
end)
