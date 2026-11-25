"""Ambush Called Off.
Batton Bones: every allocation of a $2D slot is recorded with its spawn X; a bat 'lives' if it ever reaches
state >= 2. Expect: Chameleon alive -> listed and unlisted roosts both live; Chameleon beaten -> no listed
roost ever lives, unlisted ones still do; Penguin's bats unaffected even with every boss beaten.
Metal Wings: unit test on screen next to X on the rails, minecart flag $0C26 bit 5 set."""
import sys, os; sys.path.insert(0, 'tools')
from mmx import *
ROM = Path(os.environ.get('SC_ROM', ROOT / 'build/v10_rc1.sfc')); rom = VANILLA.read_bytes(); P = 0x0BA8
gen = open(ROOT / 'build/gen/halves.asm').read()


def lst(label):
    line = gen.split(label + ':')[1].split('\n')[1]
    return [int(v.strip().strip('$'), 16) for v in line.replace('dw', '').split(',') if v.strip() != '$FFFF']


BDEAD = lst('SC_BattonDead'); MDEAD = lst('SC_MetalWingDead')
m = MMX(ROM, rt=ROOT / 'build/rt_am'); pw = make_password_state(m)
def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
def near(x, L): return any(abs(x - d) <= 2 for d in L)
def opencam(): ww(0x1E56, 0); ww(0x1E58, 0x1F00); ww(0x1E5A, 0); ww(0x1E5C, 0x0F00)   # TEST ONLY


def batton_run(stage, mask, frames=3000):
    enter_stage_at_cp(m, stage, mask, 0, rom, pw); m.frames(30)
    slot = {}          # slot -> [spawnX, lived]
    spawns = []
    x = m.rw(P + 5)
    for f in range(frames):
        opencam()
        if f % 3 == 0: x += 1; ww(P + 5, x)
        m.frames(1); m.wb(0x0BCF, 0x10)
        for i in range(15):
            b = 0x0E68 + i * 0x40
            active = m.rb(b) and m.rb(b + 0xA) == 0x2D
            if active and i not in slot:
                slot[i] = [m.rw(b + 5), False]; spawns.append(slot[i])
            if active and m.rb(b + 1) >= 2:
                slot[i][1] = True
            if not active and i in slot:
                del slot[i]
    listed = [s for s in spawns if near(s[0], BDEAD)]; unlisted = [s for s in spawns if not near(s[0], BDEAD)]
    return (len(listed), sum(1 for s in listed if s[1]), len(unlisted), sum(1 for s in unlisted if s[1]), m.rw(P + 5))


for stage, mask, label in ((3, 0x00, 'Armadillo, Chameleon alive'), (3, 0x02, 'Armadillo, Chameleon beaten'),
                           (8, 0x00, 'Penguin, nobody beaten'), (8, 0xFF, 'Penguin, all beaten')):
    nl, ll, nu, lu, xr = batton_run(stage, mask)
    print(f'{label:28s} X->{xr}: listed-roost spawns {nl} (woke {ll}), unlisted spawns {nu} (woke {lu})')

for mask in (0x00, 0x02):
    enter_stage_at_cp(m, 3, mask, 0, rom, pw); m.frames(30)
    x0, y0 = m.rw(P + 5), m.rw(P + 8)
    for i in range(300):
        opencam(); ww(P + 5, x0 + (2650 - x0) * i // 300); ww(P + 8, y0 + (2380 - y0) * i // 300); m.wb(0x0BCF, 0x10); m.frames(1)
    m.frames(60)
    res = {}
    base = m.save()
    for xpos in (MDEAD[0], MDEAD[0] + 42):     # first listed placement, and a spot 42 px right of it (unlisted)
        m.load(base)
        b = 0x0E68 + 14 * 0x40
        for k in range(0x40): m.wb(b + k, 0)
        m.wb(b, 1); m.wb(b + 0xA, 0x35); ww(b + 5, xpos); ww(b + 8, m.rw(P + 8) - 24)
        alive = 0
        for f in range(40):
            m.wb(0x0C26, m.rb(0x0C26) | 0x20); m.frames(1)
            if m.rb(b) and m.rb(b + 0xA) == 0x35: alive += 1
        res[f'{xpos:#06x} ' + ('listed' if near(xpos, MDEAD) else 'unlisted')] = alive
    print(f'Metal Wing unit test mask {mask:02X} (X at {m.rw(P + 5)}): frames alive {res}')
