-- Redirect the first call to AT (after frame AFTER) into CALL with a0 = A0, keeping $ra: CALL runs in place of
-- AT and returns to AT's caller. Reaches screens whose caller is hard to trigger (name entry 0x800DC3D0 from the
-- message call 0x8003B284 an NPC's talk makes).
--   emu.py ROM --debugger --state-in S --script tools/debug/call.lua --var AT=0x8003B284 --var CALL=0x800DC3D0
--     --var A0=1 [--var AFTER=0] --route-str "..."
local done = false
L.on_exec(AT, function()
  if done or L.frame < (AFTER or 0) then return end
  done = true
  local r = PCSX.getRegisters()
  L.log(string.format("f%d redirect %08X -> %08X a0=%d ra=%08X", L.frame, AT, CALL, A0 or 0, r.GPR.n.ra))
  r.GPR.n.a0 = A0 or 0
  r.pc = CALL
end)
