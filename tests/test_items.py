"""Items in both states of every stage: glide X onto every Heart Tank and Sub Tank and check the item RAM
($1F80-$1F9F) records it; for capsules ($4D: armour parts, Hadouken) check the capsule spawns.
Heart = a $1F9C bit, Sub Tank = $1F83-86. Retail stages are included as controls. Camera borders opened for the glide (TEST ONLY)."""
import sys, os, csv; sys.path.insert(0, 'tools')
from mmx import *
ROM = Path(os.environ.get('SC_ROM', ROOT / 'build/v10_rc3.sfc')); rom = VANILLA.read_bytes(); P = 0x0BA8
SRC = {1: 0x04, 2: 0x01, 3: 0x02, 4: 0x80, 5: 0x40, 6: 0x10, 7: 0x20, 8: 0x08}
items = {}
for r in csv.DictReader(open(ROOT / 'audit_output/events.csv')):
    st = int(r['stage_id'])
    if not 1 <= st <= 8: continue
    t, a = int(r['type']), int(r['actor_id_hex'], 16)
    if (t == 0 and a in (0x05, 0x0B)) or (t == 3 and a == 0x4D):
        items.setdefault(st, []).append(({0x05: 'SubTank', 0x0B: 'Heart', 0x4D: 'Capsule'}[a] if t == 0 or a == 0x4D else '?', int(r['x']), int(r['y'])))
m = MMX(ROM, rt=ROOT / 'build/rt_items'); pw = make_password_state(m)
def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
def opencam(): ww(0x1E56, 0); ww(0x1E58, 0x1F00); ww(0x1E5A, 0); ww(0x1E5C, 0x0F00)
fails = 0
for st in range(1, 9):
    for mask in (0x00, SRC[st]):
        for kind, x, y in items.get(st, []):
          for cp in range(3):  # items spawn only once their section loads: try each checkpoint
              enter_stage_at_cp(m, st, mask, cp, rom, pw); m.frames(30)
              before = m.read(0x1F80, 0x20)
              x0, y0 = m.rw(P + 5), m.rw(P + 8); n = 400
              seen_capsule = 0
              for i in range(n + 200):
                  opencam()
                  if i < n: ww(P + 5, x0 + (x - x0) * i // n); ww(P + 8, y0 + (y - 6 - y0) * i // n)
                  else: ww(P + 5, x); ww(P + 8, y - 6)
                  m.wb(0x0BCF, 0x10); m.frames(1)
                  if kind == 'Capsule' and 0x4D in enemy_ids(m): seen_capsule += 1
              after = m.read(0x1F80, 0x20)
              changed = [hex(0x1F80 + i) for i in range(0x20) if before[i] != after[i]]
              ok = seen_capsule > 0 if kind == 'Capsule' else (before[0x1C] != after[0x1C] if kind == 'Heart' else any(before[i] != after[i] for i in range(3, 7)))
              print(f'stage {st} {STAGE_NAME[st]:9s} {"ALTERED" if mask else "normal "} {kind:8s} at ({x},{y}) cp{cp}: '
                    + (f'capsule present {seen_capsule} frames' if kind == 'Capsule' else f'item RAM changed {changed}')
                    + ('' if ok else '   (not here)'), flush=True)
              if ok: break
          fails += not ok
          if not ok: print('   <-- FAIL: not collected from any checkpoint')
print('ITEMS', 'PASS' if not fails else f'FAIL ({fails})')
