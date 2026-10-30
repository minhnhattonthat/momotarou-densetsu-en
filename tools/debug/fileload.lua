-- Log every disc file load: "<frame> load <index> <dest>". Index = MMPS_CD.SFS entry = EXE path-table entry
-- (0x8006FB94; tools/debug/files.txt). Needs emu.py --debugger.
--   emu.py rom/x.cue --out D --debugger --script tools/debug/fileload.lua
local function a(n) return PCSX.getRegisters().GPR.n[n] end
L.on_exec(0x8001AC54, function()  -- cd_load(index a0, dest a1, ?, mode a3)
  L.log(string.format("%d load %d %08X ra %08X", L.frame, a("a0"), a("a1"), a("ra")))
end)
L.on_exec(0x8001AF70, function()  -- cd_seek(index a0)?
  L.log(string.format("%d seek %d", L.frame, a("a0")))
end)
