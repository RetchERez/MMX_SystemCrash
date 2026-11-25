"""Radar Down airport lights: the platform light chaser (effect $33 sub $09, BG row 1 colours 1-7/13/14).
Expected: normal = animator present and the colours cycle (as vanilla); Radar Down = before Death Rogumer
(checkpoints 0 and 1) no sub-$09 animator and every light colour steady at $0000; at Death Rogumer
(checkpoint 2) the ship's animator runs and row 1 matches the normal stage frame for frame."""
import sys, os; sys.path.insert(0, 'tools')
from mmx import *
from PIL import Image
ROM = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/sc_v10_rc4.sfc'; rom = VANILLA.read_bytes(); P = 0x0BA8
LIGHTS = (1, 2, 3, 4, 5, 6, 7, 13, 14)
m = MMX(ROM, rt=ROOT / 'build/rt_rl'); pw = make_password_state(m)
def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
fails = 0; ref = {}
for cp in (0, 1, 2):
    for mask in (0x00, 0x40):
        enter_stage_at_cp(m, 5, mask, cp, rom, pw); m.frames(5)
        seen = {i: set() for i in LIGHTS}; anim = 0; seq = []
        for f in range(150):
            m.frames(1); m.wb(0x0BCF, 0x10)
            anim = max(anim, sum(1 for s in range(31) if m.rb(0x1928 + s * 0x20) and m.rb(0x1928 + s * 0x20 + 0xA) == 0x33 and m.rb(0x1928 + s * 0x20 + 0xB) == 0x09))
            for i in LIGHTS: seen[i].add(m.rw(0x0320 + 2 * i))
            seq.append(m.read(0x0320, 0x20))
        cycling = any(len(v) > 1 for v in seen.values()); dark = all(v == {0} for v in seen.values())
        want_dark = mask and cp < 2
        if mask == 0: ref[cp] = seq
        ok = (dark and not anim) if want_dark else (anim and (cycling if cp < 2 else seq == ref[cp]))
        fails += not ok
        print(f'cp{cp} {"RADAR DOWN" if mask else "normal    "}: light animator {anim}, lights cycling {cycling}, all dark {dark}' + ('' if ok else '   <-- FAIL'), flush=True)
        if cp == 1: m.shot(f'build/rl_cp1_{mask:02X}.png')
print('RADAR LIGHTS', 'PASS' if not fails else f'FAIL ({fails})')
