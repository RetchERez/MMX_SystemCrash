"""Hadouken. Retail capsule init ($87:CA86) needs: stage 3, visit counter $1F7E reaching 5, all armour and
Heart Tanks ($1F99 & $1F9C = FF), fortress opened ($1F7C bit 6, set only once all 8 Mavericks are beaten) and full
HP 32. So in real play it exists only with Sting Chameleon beaten, i.e. in the ALTERED (Ambush Called Off) stage.
Password with all 8 beaten (sets $1F7C bit 6 for real); TEST ONLY pokes: gear, full HP, counter = 4 (four earlier
visits). Glide onto the capsule; pass when the retail award ($87:D0DB TSB $1F7E bit 7) is set, on vanilla and patch."""
import sys, os; sys.path.insert(0, 'tools')
from mmx import *
ROM = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/v10_rc3.sfc'; rom = VANILLA.read_bytes(); P = 0x0BA8
m = MMX(ROM, rt=ROOT / 'build/rt_hadou'); pw = make_password_state(m)
def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
def opencam(): ww(0x1E56, 0); ww(0x1E58, 0x1F00); ww(0x1E5A, 0); ww(0x1E5C, 0x0F00)
def gear():
    m.wb(0x1F99, 0xFF); m.wb(0x1F9A, 32); m.wb(0x1F9C, 0xFF)
    for i in range(4): m.wb(0x1F83 + i, 0x8E)
X, Y = 4844, 2386; fails = 0
for mask in (0xFF,):
    got = False
    for cp in range(3):
        to_stage_select(m, mask, rom, pw); m.wb(0x1F7E, 4); gear(); assert m.rb(0x1F7C) & 0x40
        gx, gy = GRID[3]
        while m.rb(0x1E4C) != gx: press(m, 'right')
        while m.rb(0x1E4F) != gy: press(m, 'down')
        m.fe.run_frames(4, ['b']); m.fe.clear_buttons()
        for _ in range(2400):
            m.frames(1); m.wb(0x1F81, cp)
            if m.rb(0xD2) == 4 and m.rb(0xD3) == 4: break
        assert m.rb(0x1F7A) == 3 and m.rb(0x1F7E) == 4, (m.rb(0x1F7A), m.rb(0x1F7E))
        gear(); m.wb(0x0BCF, 32); m.frames(30)
        x0, y0 = m.rw(P + 5), m.rw(P + 8); cap = 0
        for i in range(1800):
            opencam(); gear()
            if i < 400: ww(P + 5, x0 + (X - x0) * i // 400); ww(P + 8, y0 + (Y - 6 - y0) * i // 400); m.wb(0x0BCF, 32)
            m.frames(1, ['b'] if i > 600 and i % 40 < 2 else None)
            cap += 0x4D in enemy_ids(m)
            if m.rb(0x1F7E) & 0x80: got = True; break
        print(f'{ROM.name} mask {mask:02X} {"ALTERED" if mask & 2 else "normal "} cp{cp}: capsule frames {cap}, Hadouken {"AWARDED" if got else "no"} at frame {i}', flush=True)
        if got: break
    fails += not got
print('HADOUKEN', 'PASS' if not fails else f'FAIL ({fails})')
