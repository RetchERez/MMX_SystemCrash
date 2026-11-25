"""Death Rogumer and the Storm Eagle fight never show the platform light colours (BG row 1, colours 1-7/13/14):
walk into the fight from checkpoint 2 with controller input, then run the same 60 frames twice from one save state,
once as is and once with those colours forced to the unlit value every frame. Pass when every screen is identical,
i.e. whether the light animator runs or not cannot change what the ship or the boss fight looks like."""
import sys, os; sys.path.insert(0, 'tools')
from mmx import *
import ctypes
ROM = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/system_crash_v1.0.sfc'; rom = VANILLA.read_bytes(); P = 0x0BA8
LIGHTS = (1, 2, 3, 4, 5, 6, 7, 13, 14)
m = MMX(ROM, rt=ROOT / 'build/rt_sl'); pw = make_password_state(m)
enter_stage_at_cp(m, 5, 0x00, 2, rom, pw); m.frames(30)
seen = 0; checks = {}
for f in range(3000):
    m.fe.run_frames(1, ['right'] if f % 50 < 38 else ['right', 'b']); m.wb(0x0BCF, 0x10)
    if 0x52 in enemy_ids(m): seen += 1
    if f in (200, 600) or seen in (60, 330, 600):
        tag = f'deck f{f}' if f in (200, 600) else f'fight +{seen}'
        if tag in checks: continue
        st = m.save(); a = []; b = []
        for k in range(60):
            m.fe.run_frames(1, ['right']); m.wb(0x0BCF, 0x10); a.append(bytes(m.raw_frame() if hasattr(m, 'raw_frame') else b''))
        m.load(st)
        for k in range(60):
            for i in LIGHTS: m.wb(0x0320 + 2 * i, 0); m.wb(0x0321 + 2 * i, 0)
            m.wb(0xA1, (m.rb(0xA1) + 1) & 0xFF)
            m.fe.run_frames(1, ['right']); m.wb(0x0BCF, 0x10); b.append(bytes(m.raw_frame() if hasattr(m, 'raw_frame') else b''))
        m.load(st)
        diff = sum(1 for x, y in zip(a, b) if x != y)
        checks[tag] = diff; print(f'{tag}: X {m.rw(P + 5)}, boss present {0x52 in enemy_ids(m)}, frames that look different: {diff} of 60', flush=True)
    if seen > 650: break
ok = len(checks) >= 3 and all(v == 0 for v in checks.values())
print('SHIP LIGHTS', 'PASS' if ok else 'FAIL')
