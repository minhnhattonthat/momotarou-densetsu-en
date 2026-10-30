-- Rewrite RAM every frame (a scene's `hold`, for runs from a savestate):
--   emu.py ROM --state-in S --script tools/debug/hold.lua --var "HOLD={{0x8009195C,2,0xFFFF}}" --route-str "..."
local m = PCSX.getMemPtr()
L.on_frame(function()
  for _, p in ipairs(HOLD) do
    local a, v = p[1] & 0x1FFFFF, p[3]
    for i = 0, p[2] - 1 do m[a + i] = (v >> (8 * i)) & 0xFF end
  end
end)
