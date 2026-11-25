"""Metal Wings during a REAL minecart ride (Armadillo). Checkpoint 1, walk into the shaft (the real way into the
lower track), glide inside that region to the parked cart (TEST ONLY position; camera untouched), jump in, then ride
hands-off to the end of the track. Records every Metal Wing: frames allocated and highest state (>= 2 = attacking).
Runs vanilla, patch normal, patch Ambush. Expected: patch normal == vanilla; Ambush: every listed wing declined
(1 frame, state 0) and every unlisted wing that attacks in vanilla attacks."""
import sys; sys.path.insert(0, 'tools')
from mmx import *
rom = VANILLA.read_bytes(); P = 0x0BA8
def ride(ROM, mask):
  m = MMX(ROM, rt=ROOT / f'build/rt_ride_{ROM.stem[:6]}'); pw = make_password_state(m)
  enter_stage_at_cp(m, 3, mask, 1, rom, pw); m.frames(20)
  for f in range(300):
      m.frames(1, ['right'] if f < 200 else (['left'] if f < 260 else None)); m.wb(0x0BCF, 0x10)
  def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
  x0, y0 = m.rw(P + 5), m.rw(P + 8)   # glide inside the lower track only (TEST ONLY position; no camera pokes)
  for (tx, ty) in ((900, 2330), (1774, 2330)):
      n = max(abs(tx - x0), abs(ty - y0)) // 2 + 1
      for i in range(1, n + 1):
          ww(P + 5, x0 + (tx - x0) * i // n); ww(P + 8, y0 + (ty - y0) * i // n); m.wb(0x0BCF, 0x10); m.frames(1)
      x0, y0 = tx, ty
  mw = {}; cur = {}; riding = 0; log = []; riding_ever = 0; hop = 0
  for f in range(5000):
      rid = m.rb(0x0C26) & 0x20
      if rid or riding_ever: b = None
      else: b = ['right', 'b'] if f % 50 < 16 else (['right'] if m.rw(P + 5) < 1774 else None)
      riding_ever = riding_ever or rid
      m.frames(1, b); m.wb(0x0BCF, 0x10); m.wb(0x1F80, 2)
      if rid and not riding: log.append(('board', f, m.rw(P + 5)))
      if not rid and riding: log.append(('off', f, m.rw(P + 5)))
      riding = rid
      for s in range(15):
          bb = 0x0E68 + s * 0x40
          if m.rb(bb) and m.rb(bb + 0xA) == 0x35:
              if s not in cur: cur[s] = m.rw(bb + 5); mw.setdefault(cur[s], [0, 0])
              mw[cur[s]][0] += 1; mw[cur[s]][1] = max(mw[cur[s]][1], m.rb(bb + 1))
          else: cur.pop(s, None)
          if m.rw(P + 5) > 4800 and m.rw(P + 8) > 2550: log.append(('end of track', f, m.rw(P + 5))); break
  m.close(); return log, mw
ROMP = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/system_crash_v1.0.sfc'
gen = open(ROOT / 'build/gen/halves.asm').read().split('SC_MetalWingDead:')[1].split(chr(10))[1]
DEAD = [int(v.strip().strip('$'), 16) for v in gen.replace('dw', '').split(',') if v.strip() != '$FFFF']
V = ride(VANILLA, 0x00); N = ride(ROMP, 0x00); A = ride(ROMP, 0x02)
for tag, (log, mw) in (('vanilla', V), ('patch normal', N), ('patch Ambush', A)):
    print(f'{tag:13s} ride {log}; attacking wings {sorted(x for x, (n, st) in mw.items() if st >= 2)}')
ok = N[1] == V[1] and N[0] == V[0]
ok &= all(A[1].get(x, [0, 0])[1] == 0 for x in DEAD)
ok &= all(A[1].get(x, [0, 0])[1] >= 2 for x in V[1] if x not in DEAD and V[1][x][1] >= 2)   # every unlisted wing that attacks in vanilla attacks in Ambush
print('listed (declined in Ambush):', DEAD)
print('MINECART', 'PASS' if ok else 'FAIL')
