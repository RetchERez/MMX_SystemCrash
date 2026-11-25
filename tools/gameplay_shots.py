"""Gameplay comparison shots: each new reaction played from its nearest checkpoint with controller input (walk right,
jump over trouble), original left / changed right, 2x, no text. Same inputs in both versions; each shot is taken when
X first reaches the same spot. TEST ONLY: HP refill (keeps X alive) and, for Storm Eagle's long opening climb, a guided
path through open air to the walkway (camera untouched, so it follows X normally). Output (private, git-ignored):
reference/gameplay_<n>_<stage>.png and reference/gameplay_all_five.png"""
import sys; sys.path.insert(0, 'tools')
from mmx import *
from PIL import Image
ROM = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/system_crash_v1.0.sfc'
rom = VANILLA.read_bytes(); P = 0x0BA8
# name, stage, source bit, checkpoint, guided path (or []), shoot when X >= this x, extra frames after reaching it
STAGES = [
    ('1_meltdown', 8, 0x08, 1, [], 4690, 0),
    ('2_grid_down', 7, 0x20, 0, [], 200, 0),
    ('3_radar_down', 5, 0x40, 1, [], 3462, 0),
    ('4_empty_arsenal', 1, 0x04, 1, [], 4740, 0),
    ('5_ambush_called_off', 3, 0x02, 0, [], 470, 0),
]
only = sys.argv[2:] if len(sys.argv) > 2 else None
m = MMX(ROM, rt=ROOT / 'build/rt_gp'); pw = make_password_state(m)
def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
def play(st, mask, cp, path, shoot_x, extra):
    enter_stage_at_cp(m, st, mask, cp, rom, pw); m.frames(30)
    x, y = m.rw(P + 5), m.rw(P + 8)
    for tx, ty in path:                       # guided through open air; the camera follows on its own
        n = max(abs(tx - x), abs(ty - y)) // 3 + 1
        for i in range(1, n + 1):
            ww(P + 5, x + (tx - x) * i // n); ww(P + 8, y + (ty - y) * i // n); m.wb(0x0BCF, 0x10); m.frames(1)
        x, y = tx, ty
    if path: m.frames(40)                     # land
    last_x, stuck = m.rw(P + 5), 0
    for f in range(12000):
        b = ['right']
        if stuck > 20 and f % 40 < 16: b.append('b')     # jump when blocked
        if stuck > 30:                                     # blocked: face the nearest enemy and fire at it
            foes = [m.rw(0x0E68 + s * 0x40 + 5) for s in range(15) if m.rb(0x0E68 + s * 0x40)]
            if foes:
                fx = min(foes, key=lambda v: abs(v - x))
                b = (['left'] if fx < x else ['right']) + (['y'] if f % 8 < 2 else [])
        m.frames(1, b); m.wb(0x0BCF, 0x10); m.wb(0x1F80, 2)
        x = m.rw(P + 5); stuck = stuck + 1 if x == last_x else 0; last_x = x
        if x >= shoot_x:
            for k in range(extra): m.frames(1, ['right']); m.wb(0x0BCF, 0x10)
            m.shot(str(ROOT / 'build/gp_tmp.png')); return Image.open(ROOT / 'build/gp_tmp.png').convert('RGB').copy(), f
    raise RuntimeError(f'stage {st} mask {mask:02X}: X never reached x {shoot_x} (at {m.rw(P + 5)},{m.rw(P + 8)})')
pairs = []
for name, st, bit, cp, path, sx, extra in STAGES:
    if only and name not in only: continue
    a, fa = play(st, 0x00, cp, path, sx, extra); b, fb = play(st, bit, cp, path, sx, extra)
    pair = Image.new('RGB', (512, 224)); pair.paste(a, (0, 0)); pair.paste(b, (256, 0))
    pair = pair.resize((1024, 448), Image.NEAREST); pair.save(ROOT / f'reference/gameplay_{name}.png'); pairs.append(pair)
    print('saved', name, 'frames', fa, fb, flush=True)
if not only:
    col = Image.new('RGB', (1024, 448 * len(pairs)))
    for i, p in enumerate(pairs): col.paste(p, (0, 448 * i))
    col.save(ROOT / 'reference/gameplay_all_five.png'); print('saved gameplay_all_five')
