-- FORCED render (debug, not a game path): from frame WFROM, take the three bank-0 status-icon objects the game itself
-- creates on the HP box (0x800D81D8 -> 0x8001C768, objects 0x80086734 / 0x800867B0 / 0x8008682C once status_flags.lua forces
-- 3 ailments) and every frame stop their anim (+0x4C = 0) and set sprite id +0x0A = IDS[i] (42-47 = FONT.PAC:8 status
-- words), x +0x04 = XS[i], y +0x06 = YS[i]. The engine's own sprite renderer 0x8001D194 then draws the records.
local m = PCSX.getMemPtr()
local function w16(a, v) a = a & 0x1FFFFF; m[a] = v & 0xFF; m[a + 1] = (v >> 8) & 0xFF end
local function r16(a) a = a & 0x1FFFFF; return m[a] | (m[a + 1] << 8) end
local objs = { 0x80086734, 0x800867B0, 0x8008682C }
local logged = false
L.on_frame(function(f)
  if f < WFROM then return end
  if not logged then
    logged = true
    for i, o in ipairs(objs) do
      L.log(string.format("f%d obj %08X bank=%d id=%d x=%d y=%d", f, o, m[(o + 0x5C) & 0x1FFFFF], r16(o + 0xA), r16(o + 4), r16(o + 6)))
    end
  end
  for i, o in ipairs(objs) do
    w16(o + 0x4C, 0); w16(o + 0x4E, 0)
    w16(o + 0x0A, IDS[i])
    if XS then w16(o + 4, XS[i]); w16(o + 6, YS[i]) end
  end
end)
