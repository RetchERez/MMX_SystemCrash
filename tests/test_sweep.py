"""Whole-stage sweep of every half-power actor placement, both states, real event spawns (no test spawns):
Batton Bone roosts and Metal Wings (Armadillo), Sky Claws (Eagle), Turn Cannon (Kuwanger). For each retail event
X glides there (TEST ONLY: camera borders opened, HP refill, position; for Metal Wings the minecart-ride flag
$0C26 bit 5) from the first checkpoint whose section spawns it, waits, and records whether the actor came alive:
  Batton $2D woke (state >= 2) | Metal Wing $35 ran past its init state | Sky Claw $49 moved from where it spawned |
  Turn Cannon $17 fired (new enemy shots appearing at the cannon).
Differential: the same sweep runs on vanilla first (same inputs). Expected: normal = vanilla's metrics exactly;
altered = the listed placements dead (bat never wakes, claw never moves, Metal Wing declined, cannon silent) and
every unlisted placement alive exactly when it is alive on vanilla."""
import sys, os, csv; sys.path.insert(0, 'tools')
from mmx import *
ROMP = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/v10_rc3.sfc'; rom = VANILLA.read_bytes(); P = 0x0BA8
gen = open(ROOT / 'build/gen/halves.asm').read()
def lst(label):
    line = gen.split(label + ':')[1].split('\n')[1]
    return [int(v.strip().strip('$'), 16) for v in line.replace('dw', '').split(',') if v.strip() != '$FFFF']
DEAD = {0x2D: lst('CR_BattonDead'), 0x35: lst('CR_MetalWingDead'), 0x49: lst('CR_SkyClawDead'), 0x17: [1408]}   # the one Turn Cannon is dead in Grid Down
ev = list(csv.DictReader(open(ROOT / 'audit_output/events.csv')))
JOBS = [(3, 0x02, 0x2D, 'Batton'), (3, 0x02, 0x35, 'MetalWing'), (5, 0x40, 0x49, 'SkyClaw'), (7, 0x20, 0x17, 'TurnCannon')]
only = sys.argv[2] if len(sys.argv) > 2 else None
def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
def opencam(): ww(0x1E56, 0); ww(0x1E58, 0x1F00); ww(0x1E5A, 0); ww(0x1E5C, 0x0F00)
def near(x, L): return any(abs(x - d) <= 2 for d in L)
cache = {}
def at_cp(st, mask, cp):
    k = (st, mask, cp)
    if k not in cache:
        enter_stage_at_cp(m, st, mask, cp, rom, pw); m.frames(20); cache[k] = m.save()
    m.load(cache[k])
def visit(st, mask, aid, ex, ey):
    """returns (spawned, alive) for the placement at ex"""
    for cp in range(3):
        at_cp(st, mask, cp)
        x0, y0 = m.rw(P + 5), m.rw(P + 8); tx, ty = ex, ey + (40 if aid in (0x2D, 0x49, 0x17) else -8)
        spawned = alive = False; moved = mwf = mws = 0; frames_alloc = {}; shots = 0; prev = set(); travel = {}
        for i in range(700):
            opencam(); m.wb(0x0BCF, 0x10)
            if aid == 0x35: m.wb(0x0C26, m.rb(0x0C26) | 0x20)
            if i < 400: ww(P + 5, x0 + (tx - x0) * i // 400); ww(P + 8, y0 + (ty - y0) * i // 400)
            else: ww(P + 5, tx); ww(P + 8, ty)
            m.frames(1)
            for s in range(15):
                b = 0x0E68 + s * 0x40
                if not (m.rb(b) and m.rb(b + 0xA) == aid):
                    frames_alloc.pop(s, None); travel.pop(s, None); continue
                sx = m.rw(b + 0x37) if aid == 0x49 else None
                if s not in frames_alloc: frames_alloc[s] = [m.rw(b + 5), 0]; travel[s] = (m.rw(b + 5), m.rw(b + 8))
                if aid == 0x49 and m.rb(b + 1) == 0: travel[s] = (m.rw(b + 5), m.rw(b + 8))   # spawn position, before it runs
                frames_alloc[s][1] += 1
                if abs(frames_alloc[s][0] - ex) > 2 and not (aid == 0x49 and abs(sx - ex) <= 2): continue
                spawned = True
                if aid == 0x2D and m.rb(b + 1) >= 2: alive = True
                if aid == 0x35 and frames_alloc[s][1] >= 10: alive = True
                if aid == 0x49: moved = max(moved, abs(m.rw(b + 5) - travel[s][0]) + abs(m.rw(b + 8) - travel[s][1]))
                if aid == 0x35: mwf = max(mwf, frames_alloc[s][1]); mws = max(mws, m.rb(b + 1))
            if aid == 0x17:
                cx, cy = (frames_alloc and next(((m.rw(0x0E68 + s * 0x40 + 5), m.rw(0x0E68 + s * 0x40 + 8)) for s in frames_alloc), (ex, ey))) or (ex, ey)
                cur = {k for k in range(8) if m.rb(0x1428 + k * 0x40)}
                for k in cur - prev:   # a new shot counts only if it appears at the cannon
                    b = 0x1428 + k * 0x40
                    if spawned and abs(m.rw(b + 5) - cx) < 40 and abs(m.rw(b + 8) - cy) < 40: shots += 1
                prev = cur
        if aid == 0x17: alive = shots > 0
        if aid == 0x49: alive = moved > 0
        if aid == 0x35: alive = mws > 0   # ran past its init state (a declined Metal Wing is freed inside init)
        metric = {0x2D: alive, 0x35: (mwf, mws), 0x49: moved, 0x17: shots}[aid]
        if spawned or (aid == 0x35 and mask and near(ex, DEAD[aid])):
            return spawned, alive, cp, metric
    return False, False, None, None
def sweep(path, tag):
    global m, pw, cache
    cache = {}; m = MMX(path, rt=ROOT / f'build/rt_sweep_{tag}'); pw = make_password_state(m); out = {}
    for st, bit, aid, name in JOBS:
        if only and name != only: continue
        places = sorted({(int(r['x']), int(r['y'])) for r in ev if int(r['stage_id']) == st and int(r['actor_id_hex'], 16) == aid and r['type'] == '3'})
        for mask in (0x00, bit):
            for ex, ey in places:
                out[(name, mask, ex, ey)] = visit(st, mask, aid, ex, ey)
    m.close(); return out
V = sweep(VANILLA, 'v'); R = sweep(ROMP, 'p')
# Placements whose own appearance depends on how many of their kind are already around (verified in vanilla):
KNOWN = {('SkyClaw', 4848): 'the game spawns this crane only when fewer cranes are present; from checkpoint 1 it does not '
                            'appear in vanilla either, and in Radar Down the dead crane hanging at x 4571 keeps one present'}
fails = 0; summary = {}
for (name, mask, ex, ey), (sp, al, cp, met) in R.items():
    vsp, val, vcp, vmet = V[(name, mask, ex, ey)]
    aid = {'Batton': 0x2D, 'MetalWing': 0x35, 'SkyClaw': 0x49, 'TurnCannon': 0x17}[name]
    listed = near(ex, DEAD[aid])
    if mask == 0: ok = (sp, al, met) == (vsp, val, vmet); why = 'identical to vanilla'
    elif listed: ok = not al; why = 'dead (listed)'
    else: ok = al == val; why = f'alive as on vanilla ({val})'
    if not ok and (name, ex) in KNOWN:
        print(f'   {name} ({ex},{ey}) {"ALTERED" if mask else "normal"}: not alive here; known variance: {KNOWN[(name, ex)]}'); ok = True
    k = (name, mask); s_ = summary.setdefault(k, [0, 0, 0, 0]); s_[0] += 1; s_[1] += al; s_[2] += listed and mask != 0; s_[3] += not ok
    fails += not ok
    if not ok: print(f'   {name} ({ex},{ey}) {"ALTERED" if mask else "normal"} cp{cp}: patch spawned {sp} alive {al} metric {met} | vanilla spawned {vsp} alive {val} metric {vmet}; expected {why}', flush=True)
for (name, mask), (n, al, ld, bad) in summary.items():
    print(f'{name:10s} {"ALTERED" if mask else "normal "}: {n} placements, alive {al}, listed dead {ld}, unexpected {bad}', flush=True)
print('SWEEP', 'PASS' if not fails else f'FAIL ({fails})')
