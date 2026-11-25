"""Generic persistence: for a stage/source bit, the altered runtime state (palette buffer, map/collision
pointers, blockMap, screen grid) at every checkpoint and after a real death equals the altered state;
the normal state equals vanilla.
Palette bytes that vanilla itself changes across a death (retail palette animation, e.g. Eagle row 1)
are learned from a vanilla death run and ignored.
usage: test_persist.py <rom> <stage> <source_bit_hex>"""
import sys, hashlib; sys.path.insert(0, 'tools')
from mmx import *
ROM = Path(sys.argv[1]); ST = int(sys.argv[2]); BIT = int(sys.argv[3], 16); rom = VANILLA.read_bytes(); P = 0x0BA8


def state(m):
    return bytearray(m.read(0x300, 0x200)) + m.read(0x0B92, 6) + m.read(0x7E2000, 0x8000) + m.read(0x7EE800, 0x400)


def die(m):
    """Real death: HP 1 and a Turn Cannon spawned on X (contact damage); wait for the respawn."""
    def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
    lives = m.rb(0x1F80); m.wb(0x0BCF, 1); b = 0x0E68 + 14 * 0x40
    for k in range(0x40): m.wb(b + k, 0)
    m.wb(b, 1); m.wb(b + 0xA, 0x17); m.wb(b + 0xB, 1); ww(b + 5, m.rw(P + 5)); ww(b + 8, m.rw(P + 8) - 8)
    died = False
    for f in range(3000):
        m.frames(1)
        if m.rb(0x1F80) != lives: died = True
        if died and f > 400 and m.rb(0xD2) == 4 and m.rb(0xD3) in (4, 6): break
    m.frames(60)
    return died, lives, m.rb(0x1F80)


vm = MMX(VANILLA, rt=ROOT / f'build/rt_pv{ST}'); vpw = make_password_state(vm); van = {}
for cp in range(3):
    enter_stage_at_cp(vm, ST, 0, cp, rom, vpw); vm.frames(30); van[cp] = state(vm)
enter_stage_at_cp(vm, ST, 0, 0, rom, vpw); vm.frames(30); before = state(vm); die(vm); after = state(vm)
animated = {i for i in range(len(before)) if before[i] != after[i]}
vm.close()
print(f'stage {ST}: {len(animated)} bytes change across a death in vanilla (ignored)')


def sig(s):
    s = bytearray(s)
    for i in animated: s[i] = 0
    return hashlib.sha1(s).hexdigest()[:12]


m = MMX(ROM, rt=ROOT / f'build/rt_pp{ST}'); pw = make_password_state(m); ok = True; alt = {}
for cp in range(3):
    enter_stage_at_cp(m, ST, 0, cp, rom, pw); m.frames(30); n = state(m)
    enter_stage_at_cp(m, ST, BIT, cp, rom, pw); m.frames(30); a = state(m); alt[cp] = a
    r = (n == van[cp]) and (a != n)
    print(f'stage {ST} cp{cp}: normal==vanilla {n == van[cp]}  altered!=normal {a != n}'); ok &= r
enter_stage_at_cp(m, ST, BIT, 0, rom, pw); m.frames(30)
died, l0, l1 = die(m); s = state(m)
print(f'death: lives {l0}->{l1} respawned state == altered cp0 (animated bytes ignored): {sig(s) == sig(alt[0])}')
ok &= died and sig(s) == sig(alt[0])
print('PERSISTENCE', 'PASS' if ok else 'FAIL')
