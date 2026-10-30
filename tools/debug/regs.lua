-- Log registers at an exec address (first MAX hits): --var AT=0x8003E3FC [--var MAX=20]
local n, max = 0, MAX or 20
L.on_exec(AT, function()
  n = n + 1
  if n > max then return end
  local r = PCSX.getRegisters().GPR.n
  L.log(string.format("f%d %08X a0=%08X a1=%08X a2=%08X v0=%08X v1=%08X t0=%08X t1=%08X t3=%08X s2=%08X ra=%08X",
    L.frame, AT, r.a0, r.a1, r.a2, r.v0, r.v1, r.t0, r.t1, r.t3, r.s2, r.ra))
end)
