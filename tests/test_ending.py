"""The ending, vanilla vs patch, with every Maverick beaten. Fortress icon -> Sigma stage 4 (TEST ONLY: stage number
set during the intro; the final shaft climbed by position). Velguarder: HP set to 1 once it fights, killed by X's own
shot. Sigma: real buster hits only. Wolf Sigma: its head is out of reach from the floor, so after 300 frames of its
fight the game's own lethal-hit writes ($88:CBF3-CC0F) stand in for the final shot. Then the game runs its death
sequence, the escape, the epilogue, the credits and Sigma's last message on its own. All of WRAM (stack zone and
header-checksum copy excluded) is compared every 300 frames; screenshots of the ending in build/."""
import sys, hashlib; sys.path.insert(0, 'tools')
from mmx import *
rom = VANILLA.read_bytes(); P = 0x0BA8
def run(ROM, TAG, N=40000):
  m = MMX(ROM, rt=ROOT / f'build/rt_end_{TAG}'); pw = make_password_state(m)
  def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
  to_stage_select(m, 0xFF, rom, pw); m.frames(60); m.fe.run_frames(4, ['b']); m.fe.clear_buttons()
  for f in range(2400):
      m.wb(0x1F7A, 12); m.frames(1)      # TEST ONLY: Sigma stage 4 (the final room) instead of Sigma 1
      if m.rb(0xD2) == 4 and m.rb(0xD3) == 4: break
  SIGMA_FIGHT = set(eval(__import__('os').environ.get('CR_SIGMA_FIGHT', '[]')))
  BOSS = {0x26, 0x65, 0x66, 0x67, 0x69, 0x6B, 0x6C, 0x6D}
  last = None; hashes = []; full = set(); top = {}; wolf = None; killed = False; wolf_frames = 0
  for f in range(N):
      if f < 1200: ww(P + 5, 128); ww(P + 8, 1695 - (1695 - 180) * f // 1200)   # TEST ONLY: up the shaft
      elif f < 1400: ww(P + 5, 128); ww(P + 8, 180)
      b = (['y'] if f % 8 < 2 else [])
      if f > 3200:
          ph = f % 240
          b += ['right'] if ph < 50 else (['b'] if 60 <= ph < 75 else (['left'] if 120 <= ph < 160 else []))
          if wolf: b = (['y'] if f % 8 < 2 else []) + (['right'] if f % 50 == 25 else [])
      b = b or None
      if f >= 1400 and m.rb(0xD2) == 4 and m.rb(0xD3) == 4:
          tgt = [(m.rw(0x0E68 + s * 0x40 + 5), m.rw(0x0E68 + s * 0x40 + 8)) for s in range(15)
                 if m.rb(0x0E68 + s * 0x40) and m.rb(0x0E68 + s * 0x40 + 0xA) in BOSS and 0 < m.rb(0x0E68 + s * 0x40 + 0x27) < 0x80]
          pass
      if wolf: ww(P + 5, wolf[0] - 40); ww(P + 8, wolf[1] - 19 + 4 * ((f // 600) % 3))   # TEST ONLY: beside Wolf Sigma's head, sweeping height (on the floor it is out of reach)
      m.frames(1, b); m.wb(0x0BCF, 0x10); m.wb(0x1F80, 2)
      if m.rb(0xD2) == 4 and m.rb(0xD3) == 4:
          for s in range(15):
              a = 0x0E68 + s * 0x40
              if not (m.rb(a) and m.rb(a + 0xA) in BOSS): full.discard(s); top.pop(s, None); continue
              hp = m.rb(a + 0x27)
              if m.rb(a + 0xA) == 0x26 and m.rb(a + 1) >= 4: full.add(s)     # Velguarder out of its intro
              if m.rb(a + 0xA) == 0x65 and m.rb(a + 1) == 16 and not killed:
                  wolf = (m.rw(a + 5), m.rw(a + 8)); wolf_frames += 1
                  if wolf_frames == 300:   # TEST ONLY: the game's own lethal-hit writes ($88:CBF3-CC0F) in place of the final shot
                      m.wb(a + 1, 0x12); m.wb(a + 2, 0); m.wb(a + 3, 0)
                      m.wb(0x1F3F, 0x80); [m.wb(0x1F40 + k, 0) for k in range(4)]
                      m.wb(0x0BD8, (m.rb(0x0BD8) + 1) & 0xFF); m.wb(0x1F0C, (m.rb(0x1F0C) + 1) & 0xFF)
                      killed = True; wolf = None; print(f, 'Wolf Sigma: lethal hit applied', flush=True)
              if m.rb(a + 0xA) == 0x65: continue                          # Sigma: real buster hits only
              if s in full and 1 < hp < 0x80: m.wb(a + 0x27, 1)          # TEST ONLY: the next hit finishes it
      key = (m.rb(0xD1), m.rb(0xD2), m.rb(0xD3), tuple(sorted({m.rb(0x0E68 + s * 0x40 + 0xA) for s in range(15) if m.rb(0x0E68 + s * 0x40)})))
      if key != last:
          print(f, 'D', key[:3], 'actors', [hex(x) for x in key[3]], 'X', m.rw(P + 5), m.rw(P + 8), flush=True); last = key
          m.shot(f'build/end_{TAG}_{f}.png')
      if f % 1500 == 0: m.shot(f'build/end_{TAG}_t{f}.png')
      if f % 1000 == 0: m.shot(f'build/end_{TAG}_t{f}.png')
      if f > 3000 and f % 1000 == 0:
          sg = [(m.rb(0x0E68 + s * 0x40 + 1), m.rb(0x0E68 + s * 0x40 + 2), m.rb(0x0E68 + s * 0x40 + 0x27), m.rw(0x0E68 + s * 0x40 + 5), m.rw(0x0E68 + s * 0x40 + 8)) for s in range(15) if m.rb(0x0E68 + s * 0x40) and m.rb(0x0E68 + s * 0x40 + 0xA) == 0x65]
          print(f, 'sigma(st,sub,hp,x,y)', sg, 'X', m.rw(P + 5), m.rw(P + 8), flush=True)
      if f % 300 == 0:
          w = bytearray(m.read(0, 0x20000)); w[0x100:0x300] = bytes(0x200); w[0xFFBC:0xFFC0] = bytes(4); hashes.append(hashlib.sha1(w).hexdigest())
  open(ROOT / f'build/end_{TAG}.hashes', 'w').write('\n'.join(hashes)); m.close(); return hashes, killed, last

ROMP = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/chain_reaction_v1.0.sfc'
V = run(VANILLA, 'v'); Pt = run(ROMP, 'p')
first = next((i for i, (a, b) in enumerate(zip(V[0], Pt[0])) if a != b), None)
print(f'ending: Wolf Sigma defeated vanilla {V[1]} patch {Pt[1]}; final mode vanilla {V[2][:3]} patch {Pt[2][:3]}; '
      f'{len(V[0])} WRAM snapshots, identical {V[0] == Pt[0]}, first difference at snapshot {first}')
print('ENDING', 'PASS' if V[1] and Pt[1] and V[0] == Pt[0] else 'FAIL')
