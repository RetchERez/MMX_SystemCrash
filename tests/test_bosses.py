"""Bosses untouched: every boss whose stage SYSTEM CRASH changes is fought from checkpoint 2 with the same controller
input (walk right, jump, fire; HP refill is the one TEST ONLY poke) in the original and the changed stage. From the
frame the boss appears, 600 frames of the fight are compared: the boss's own actor memory every frame, and every
displayed frame. Pass = identical, except that Boomer Kuwanger's arena is on Grid Down's emergency lighting by design,
so for him the screen is expected to differ in colour only and his actor memory must still be identical."""
import sys, hashlib; sys.path.insert(0, 'tools')
from mmx import *
ROM = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/system_crash_v1.0.sfc'; rom = VANILLA.read_bytes(); P = 0x0BA8
BOSSES = [(8, 0x02, 0x08, 'Chill Penguin'), (7, 0x05, 0x20, 'Boomer Kuwanger'), (5, 0x52, 0x40, 'Storm Eagle'),
          (1, 0x07, 0x04, 'Launch Octopus'), (3, 0x14, 0x02, 'Armored Armadillo')]
def fight(m, pw, st, boss, mask):
    enter_stage_at_cp(m, st, mask, 2, rom, pw); m.frames(30)
    rec = []; start = None
    for f in range(4000):
        b = ['right'] if f % 50 < 38 else ['right', 'b']
        if start is not None and f % 10 < 2: b = b + ['y']
        m.fe.run_frames(1, b); m.wb(0x0BCF, 0x10); m.wb(0x1F80, 2)
        slot = next((0x0E68 + s * 0x40 for s in range(15) if m.rb(0x0E68 + s * 0x40) and m.rb(0x0E68 + s * 0x40 + 0xA) == boss), None)
        if start is None and slot is not None: start = f
        if start is not None:
            rec.append((hashlib.sha1(m.raw_frame()).hexdigest(), m.read(slot, 0x40) if slot else b''))
            if len(rec) == 600: break
    return start, rec
fails = 0
m = MMX(ROM, rt=ROOT / 'build/rt_boss'); pw = make_password_state(m)
for st, boss, bit, name in BOSSES:
    s0, a = fight(m, pw, st, boss, 0x00); s1, b = fight(m, pw, st, boss, bit)
    frames_same = sum(1 for x, y in zip(a, b) if x[0] == y[0]); boss_same = sum(1 for x, y in zip(a, b) if x[1] == y[1])
    dark = st == 7   # Grid Down keeps the arena dark
    ok = s0 is not None and s0 == s1 and len(a) == len(b) == 600 and boss_same == 600 and (dark or frames_same == 600)
    fails += not ok
    print(f'{name:18s}: appears at frame {s0} / {s1}; of 600 fight frames, screens identical {frames_same}, boss memory identical {boss_same}'
          + (' (arena dark by design)' if dark else '') + ('' if ok else '   <-- FAIL'), flush=True)
print('BOSSES', 'PASS' if not fails else f'FAIL ({fails})')
