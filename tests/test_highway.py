"""Intro Highway (stage 0, played from GAME START): same input on the original and the patch, all of WRAM compared
every 30 frames from 60 frames after play starts, about 3,700 frames of play (stack zone and the boot-time header-checksum copy excluded, as in
test_parity.py). The patch has no change for this stage; this checks it stays exactly the original."""
import sys, hashlib
sys.path.insert(0, 'tools')
from pathlib import Path
from mmx import *
ROM = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/system_crash_v1.0.sfc'


def run(path, tag):
    m = MMX(path, rt=ROOT / f'build/rt_hw_{tag}')
    m.frames(300)
    for _ in range(5): m.tap('start', hold=2, settle=58)
    m.frames(500)
    m.tap('start', hold=3, settle=90)          # menu, cursor on GAME START
    m.tap('start', hold=3, settle=10)          # GAME START
    started = None
    snaps = []
    for f in range(4200):
        b = ['right'] if f % 120 < 100 else ['right', 'b']
        if f % 9 < 2: b = b + ['y']
        m.fe.run_frames(1, b); m.wb(0x0BCF, 0x10)   # TEST ONLY: HP refill, same in both
        if started is None and m.rb(0x1F7A) == 0 and (m.rb(0xD2), m.rb(0xD3)) == (4, 4): started = f
        if f % 30 == 0:
            w = bytearray(m.read(0, 0x20000)); w[0x100:0x300] = bytes(0x200); w[0xFFBC:0xFFC0] = bytes(4)
            snaps.append(hashlib.sha1(w).hexdigest())
    st = (m.rb(0x1F7A), m.rb(0xD2), m.rb(0xD3), m.rw(0xBAD))
    m.shot(str(ROOT / f'build/qa/highway_{tag}.png')); m.close()
    return snaps, started, st


v, vs, vst = run(VANILLA, 'v'); p, ps, pst = run(ROM, 'p')
# the title menu before the stage shows the subtitle's brief timing differences (tests/test_title.py); the stage
# itself is judged from 60 frames after play starts
k0 = (max(vs, ps) + 60) // 30 + 1
diff = [i for i in range(k0, len(v)) if v[i] != p[i]]
print(f'highway: play from frame {vs} / {ps}; end state (stage, mode, X) {vst} / {pst}; snapshots in play {len(v) - k0}, differing {len(diff)}' + (f' (first at frame {diff[0] * 30})' if diff else ''))
print('HIGHWAY', 'PASS' if not diff and vs == ps and vst == pst else 'FAIL')
