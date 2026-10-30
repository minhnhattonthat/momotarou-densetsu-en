-- Count exec hits at addresses and log the first caller ($ra) of each; dump RAM at the end.
--   emu.py ROM --debugger --state-in S --script tools/debug/hits.lua --var "HITS={0x8003E128,0x8003E260}" --route-str "..."
local counts, ras = {}, {}
for _, a in ipairs(HITS) do
  counts[a] = 0
  ras[a] = {}
  L.on_exec(a, function()
    counts[a] = counts[a] + 1
    local ra = PCSX.getRegisters().GPR.n.ra
    if not ras[a][ra] then ras[a][ra] = true; L.log(string.format("f%d exec %08X ra=%08X", L.frame, a, ra)) end
  end)
end
L.on_frame(function()
  if L.frame == (DUMP_AT or 400) then
    for _, a in ipairs(HITS) do L.log(string.format("%08X hits %d", a, counts[a])) end
    L.dump_ram("ram.bin")
  end
end)
