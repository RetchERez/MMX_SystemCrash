"""Third emulator: Mesen 2 (--testrunner, Lua). For each of the 8 stages, with its source Maverick alive and beaten,
on vanilla and on the patch: boot with WRAM cleared, enter the real password, pick the stage on the real stage select,
play 240 frames of fixed input (right, jump, fire; HP refill = the one TEST ONLY poke) and dump WRAM.
Checks: source alive -> patch WRAM == vanilla WRAM after 240 frames of play (stack zone, header-checksum copy and the
frame counter's phase excluded); source beaten -> retail-reaction stages (Mammoth, Mandrill, Chameleon) == vanilla;
Grid Down / Radar Down / Empty Arsenal differ at load only inside their own regions (palette rows, level pointers,
blockMap; loader scratch $10-$1F); Ambush / Meltdown identical at load (their changes act on actors as they spawn)."""
import sys, subprocess, os
sys.path.insert(0, 'tools')
from pathlib import Path
import password
ROOT = Path(__file__).resolve().parent.parent
MESEN = ROOT / 'tools/vendor/mesen2/Mesen.exe'   # portable copy: its settings.json plugs a SNES pad into port 1, allows Lua file IO, zero RAM
VAN = ROOT / 'rom_private/Mega Man X (USA) (Rev 1).sfc'; rom = VAN.read_bytes()
PATCH = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/chain_reaction_v1.0.sfc'
W = ROOT / 'build/mesen'; W.mkdir(parents=True, exist_ok=True)
GRID = {1: (1, 0), 8: (2, 0), 3: (0, 1), 4: (3, 1), 5: (0, 2), 7: (3, 2), 6: (1, 3), 2: (2, 3)}
SRC = {1: 0x04, 2: 0x01, 3: 0x02, 4: 0x80, 5: 0x40, 6: 0x10, 7: 0x20, 8: 0x08}
LUA = r'''
local cells = {CELLS}; local GX, GY = {GX}, {GY}; local OUT = "{OUT}"
local f, phase, t, pad = 0, 0, 0, {}
local function rd(a) return emu.read(a, emu.memType.snesWorkRam) end
local function wr(a, v) emu.write(a, v, emu.memType.snesWorkRam) end
-- boot script identical to tools/mmx.py make_password_state: list of {button-or-nil, frames}
local script = {{nil,300}}
for i=1,5 do table.insert(script,{"start",2}); table.insert(script,{nil,58}) end
for _,s in ipairs({{nil,500},{"start",3},{nil,90},{"down",10},{nil,30},{"start",3},{nil,120}}) do table.insert(script,s) end
local si, sleft = 1, script[1][2]
emu.addEventCallback(function()
  local inp = {}
  if pad.b then inp[pad.b] = true end
  if pad.b2 then inp[pad.b2] = true end
  emu.setInput(inp, 0)
end, emu.eventType.inputPolled)
emu.addEventCallback(function()
  f = f + 1; pad = {}
  if f == 1 then for a=0,0x1FFFF do wr(a, 0) end end
  if os.getenv('CR_MESEN_SHOT') and f % 100 == 0 and f <= 2000 then local sh = io.open(OUT .. '.' .. f .. '.png', 'wb'); sh:write(emu.takeScreenshot()); sh:close() end
  if phase == 0 then
    if script[si][1] then pad.b = script[si][1] end
    sleft = sleft - 1
    if sleft <= 0 then si = si + 1; if si > #script then phase = 1; t = 5; if os.getenv('CR_MESEN_SHOT') then local sh = io.open(OUT .. '.pw.png', 'wb'); sh:write(emu.takeScreenshot()); sh:close() end else sleft = script[si][2] end end
  elseif phase == 1 then  -- password screen: write cells, cursor on END, press start
    for i=1,#cells do wr(0x1E60 + i - 1, cells[i]) end; wr(0x1E4F, 3)
    t = t - 1; if t <= 0 then phase = 2; t = 0 end
  elseif phase == 2 then
    t = t + 1; if t % 40 < 3 and rd(0xD1) == 0 then for i=1,#cells do wr(0x1E60 + i - 1, cells[i]) end; wr(0x1E4F, 3); pad.b = "start" end
    if t > 4 and rd(0xD1) == 2 and rd(0xD2) == 0 and rd(0xD3) == 1 then phase = 3; t = 300 end
  elseif phase == 3 then t = t - 1; if t <= 0 then phase = 4; t = 0 end
  elseif phase == 4 then  -- stage select cursor
    t = t + 1
    if t % 38 < 8 then
      if rd(0x1E4C) ~= GX then pad.b = "right" elseif rd(0x1E4F) ~= GY then pad.b = "down" end
    end
    if t % 38 == 37 and rd(0x1E4C) == GX and rd(0x1E4F) == GY then phase = 5; t = 0 end
  elseif phase == 5 then
    t = t + 1; if t <= 4 then pad.b = "b" end
    if rd(0xD2) == 4 and rd(0xD3) == 4 then phase = 6; t = 0 end
    if t > 2400 then emu.stop(3) end
  elseif phase == 6 then
    t = t + 1; pad.b = "right"; if t % 60 >= 40 then pad.b2 = "b" end
    if t == 1 then local fh = io.open(OUT .. ".load", "wb"); local buf = {}
      for a=0,0x1FFFF do buf[#buf+1] = string.char(rd(a)) end; fh:write(table.concat(buf)); fh:close() end
    wr(0x0BCF, 0x10)
    if t >= 240 then
      local fh = io.open(OUT, "wb"); local buf = {}
      for a=0,0x1FFFF do buf[#buf+1] = string.char(rd(a)) end
      fh:write(table.concat(buf)); fh:close(); emu.stop(0)
    end
  end
  if f % 200 == 0 then local th = io.open(OUT .. '.trace', 'a'); th:write(f .. ' phase ' .. phase .. ' D ' .. rd(0xD1) .. ',' .. rd(0xD2) .. ',' .. rd(0xD3) .. ' cur ' .. rd(0x1E4C) .. ',' .. rd(0x1E4F) .. string.char(10)); th:close() end
  if f > 20000 then emu.stop(2) end
end, emu.eventType.endFrame)
'''
def run(path, stage, mask, tag):
    out = W / f'{tag}_{stage}_{mask:02X}.bin'
    if out.exists(): out.unlink()
    cells = password.encode(rom, mask); gx, gy = GRID[stage]
    lua = W / 'run.lua'
    lua.write_text(LUA.replace('{CELLS}', '{' + ','.join(map(str, cells)) + '}').replace('{GX}', str(gx)).replace('{GY}', str(gy)).replace('{OUT}', out.as_posix()))
    r = subprocess.run([str(MESEN), '--testrunner', str(path), str(lua)], capture_output=True, timeout=600)
    if r.returncode != 0 or not out.exists(): raise RuntimeError(f'mesen run failed {tag} {stage} {mask:02X}: exit {r.returncode}')
    def clean(b):
        w = bytearray(b); w[0x100:0x300] = bytes(0x200); w[0xFFBC:0xFFC0] = bytes(4); return bytes(w)
    return clean(out.read_bytes()), clean(Path(str(out) + '.load').read_bytes())
pv = W / 'van.sfc'; pp = W / 'patch.sfc'; pv.write_bytes(rom); pp.write_bytes(PATCH.read_bytes())
# $0B9B is the free-running main-loop frame counter: its phase at stage start already varies with menu time
# $0010-$001F: direct-page scratch the level loader uses for temporary pointers
ALLOWED = {7: [(0x0340, 0x03A0)],                                    # Grid Down: BG palette rows 2-4
           5: [(0x0300, 0x0340), (0x0B92, 0x0B98), (0x2000, 0xA000),   # Radar Down: spare row 0, light row 1, level pointers, blockMap,
               (0x1928, 0x1D08), (0xFA00, 0xFB00)],                    # the refused light animator's effect slot and its event's active flag
           1: [(0x0300, 0x0320), (0x0B92, 0x0B98), (0x2000, 0xA000)]}  # Empty Arsenal: same
fails = 0
for st in [int(a) for a in os.environ.get('CR_MESEN_STAGES', '12345678')]:
    for mask in (0x00, SRC[st]):
        (v, vl), (p, pl) = run(pv, st, mask, 'v'), run(pp, st, mask, 'p')
        assert v[0x1F7A] == st and p[0x1F7A] == st, (v[0x1F7A], p[0x1F7A])
        alt = mask != 0 and st in ALLOWED
        if mask and st in (3, 8):   # Ambush / Meltdown act on actors as they spawn: compare at load, play differs by design
            diff = [i for i in range(0x20000) if vl[i] != pl[i] and i != 0x0B9B]
            ok = not diff; note = ('identical to vanilla at load (actor changes covered by the snes9x/bsnes suites)' if ok else f'{len(diff)} bytes differ at load, first {[hex(i) for i in diff[:6]]}')
        elif not alt:
            diff = [i for i in range(0x20000) if v[i] != p[i] and i != 0x0B9B]
            ok = not diff; note = 'identical to vanilla after 240 frames of play' if ok else f'{len(diff)} bytes differ, first {[hex(i) for i in diff[:6]]}'
            if v[0x0B9B] != p[0x0B9B]: note += f' (frame-counter phase $0B9B {v[0x0B9B]:02X} vs {p[0x0B9B]:02X}: the load ended one frame later)'
        else:
            diff = [i for i in range(0x20000) if vl[i] != pl[i]]
            stray = [i for i in diff if not any(a <= i < b for a, b in ALLOWED[st]) and not 0x10 <= i < 0x20 and i != 0x0B9B]
            mp = pl[0x0B95] | pl[0x0B96] << 8 | pl[0x0B97] << 16
            ok = bool(diff) and not stray and (st == 7 or (mp >> 16) in (0xB0, 0xB2))
            note = f'at load {len(diff)} bytes differ, all inside the reaction regions {not stray}' + ('' if st == 7 else f', level map pointer ${mp:06X}')
        fails += not ok
        print(f'stage {st} mask {mask:02X} {"source beaten" if mask else "source alive "}: {note}' + ('' if ok else '   <-- FAIL'), flush=True)
print('MESEN', 'PASS' if not fails else f'FAIL ({fails})')
