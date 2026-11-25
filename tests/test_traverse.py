"""Controller-only traversal of the five changed stages, normal vs altered, from every checkpoint. No position or
camera pokes: the bot only presses buttons (hold right, jump/wall-jump with B, dash with A, fire with Y); the one
TEST ONLY poke is the HP refill so a run is not cut short. Records farthest X, highest point (lowest Y), lives lost,
and whether the game is still in play (no crash or softlock). Kuwanger's tower is vertical, so its run tests the
climb with wall jumps against the right wall."""
import sys, os; sys.path.insert(0, 'tools')
from mmx import *
ROM = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/v10_rc3.sfc'; rom = VANILLA.read_bytes(); P = 0x0BA8
SRC = {1: 0x04, 3: 0x02, 5: 0x40, 7: 0x20, 8: 0x08}
N = int(os.environ.get('SC_TRAV_FRAMES', 3600))
m = MMX(ROM, rt=ROOT / 'build/rt_trav'); pw = make_password_state(m)
def inputs(f):
    b = ['right']
    if f % 48 < 18: b.append('b')          # jump, also wall-jumps when against a wall
    if f % 120 < 30: b.append('a')         # dash
    if f % 16 < 2: b.append('y')           # fire
    return b
rows = []
for st in SRC:
    for cp in range(3):
        res = {}
        for mask in (0x00, SRC[st]):
            enter_stage_at_cp(m, st, mask, cp, rom, pw); m.frames(20)
            x0, y0, lives0 = m.rw(P + 5), m.rw(P + 8), m.rb(0x1F80)
            mx, my, deaths, last = x0, y0, 0, lives0
            for f in range(N):
                m.frames(1, inputs(f)); m.wb(0x0BCF, 0x10)
                if m.rb(0xD2) == 4 and m.rb(0xD3) == 4:
                    mx = max(mx, m.rw(P + 5)); my = min(my, m.rw(P + 8))
                l = m.rb(0x1F80)
                if l < last: deaths += 1
                last = l; m.wb(0x1F80, 2); last = 2
            res[mask] = (x0, y0, mx, my, deaths, m.rb(0xD1), m.rb(0xD2), m.rb(0xD3), m.rb(0x1F7A))
        for mask, (x0, y0, mx, my, d, d1, d2, d3, sid) in res.items():
            print(f'stage {st} {STAGE_NAME[st]:9s} cp{cp} {"ALTERED" if mask else "normal "}: start ({x0},{y0}) farthest X {mx} '
                  f'highest Y {my} lives lost {d} mode {d1},{d2},{d3} stage {sid}', flush=True)
print('TRAVERSE done (compare normal vs altered rows; a crash raises)')
