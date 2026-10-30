-- Force battle ailments on party member MEMBER (default 0 = Momotaro) every frame from FROM, through the bytes the
-- status-stamp picker 0x800D8050 reads in battle (u8 0x800FE3D0 != 0):
--   status 0 Sick?  0x800FE9F8[m] & 3      status 3  0x800FE9F8[m] & 8
--   status 1        0x800FE9F8[m] & 4      status 4  0x800FEA30[m] & 8
--   status 2        0x800FE9F8[m] & 0x40   status 5  0x800FE980[m] != 0
-- SET = which statuses (e.g. {0,1,2}); 0x800D81D8 shows at most 3 per member (anim 0x800E33B4[status]).
-- Logs calls of 0x800D81D8 (a0 member, a1) and 0x8001C768 (obj, anim) from it.
local m = PCSX.getMemPtr()
local mb = MEMBER or 0
local set = {}
for _, s in ipairs(SET or { 0, 1, 2 }) do set[s] = true end
local f9 = (set[0] and 1 or 0) | (set[1] and 4 or 0) | (set[2] and 0x40 or 0) | (set[3] and 8 or 0)
L.on_frame(function(f)
  if f < (FROM or 0) then return end
  m[0xFE9F8 + mb] = f9
  m[0xFEA30 + mb] = set[4] and 8 or 0
  m[0xFE980 + mb] = set[5] and 1 or 0
end)
local seen = {}
local function hook(at, name)
  L.on_exec(at, function()
    local g = PCSX.getRegisters().GPR.n
    local s = string.format("%s a0=%X a1=%X ra=%08X", name, tonumber(g.a0), tonumber(g.a1), tonumber(g.ra))
    if seen[s] then return end
    seen[s] = true
    L.log(string.format("f%d %s", L.frame, s))
  end)
end
hook(0x800D81D8, "stamps")
hook(0x8001C768, "anim")
