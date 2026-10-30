-- Capture all 99 album pages from a fresh first-page state (cards 1..3 visible).
-- First cold-boot warp ev_card_all, open Contents, choose Momotaro's Friends, then save the state.
-- emu.py ROM --state-in FIRST_PAGE --script tools/debug/album.lua --frames 30000 --out OUT
-- Every capture uses a loaded game page; left turns toward increasing card numbers.
local m = PCSX.getMemPtr()
local page = 0
L.on_frame(function(f)
  m[0x4295C], m[0x4295D] = 1, 0 -- reveal the collection for this QA run
  if f >= 60 and (f - 60) % 300 == 0 then
    page = page + 1
    L.shot(string.format("cards_%03d.png", (page - 1) * 3 + 1))
    if page == 99 then L.finish(0) else L.press("left", 6) end
  end
end)
