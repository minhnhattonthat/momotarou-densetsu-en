-- Exercise the real battle message builder with the reward/theft fragment substitutions.
-- Use a fresh battle_cmd state, --debugger --var "MODE='each'" (alone|ryo|item also supported).
-- This swaps the first attack message's arguments; it does not claim a natural victory or theft reproduction.
local m = PCSX.getMemPtr()
local function w16(a, v) a = a & 0x1FFFFF; m[a] = v & 0xFF; m[a + 1] = (v >> 8) & 0xFF end
local variants = {
  each = { 83, 4, { { 5, 29 } } }, alone = { 83, 4, { { 5, 78 } } },
  ryo = { 47, 5, { { 5, 30 } } }, item = { 23, 5, { { 5, 30 }, { 2, 61 } } },
}
local variant = variants[MODE] or error("MODE each|alone|ryo|item")
local done = false
for _, at in ipairs({ 0x800F877C, 0x800F86AC }) do
  L.on_exec(at, function()
    local r = PCSX.getRegisters().GPR.n
    if done or tonumber(r.a0) ~= 0 or tonumber(r.a1) ~= 4 then return end
    done = true
    r.a0, r.a1 = variant[1], variant[2]
    for i = 0, 3 do
      local p = variant[3][i + 1] or { 0, 0 }
      w16(0x800FECE8 + 2 * i, p[1]); w16(0x800FECF0 + 2 * i, p[2])
    end
    L.log(string.format("f%d injected %s message through builder %08X", L.frame, MODE, at))
  end)
end
