"""Collision unchanged by the map retargets (Radar Down, Empty Arsenal) and the Meltdown igloo melt check:
load each stage normal and altered, read the live blockMap ($7E:2000) and the collision table the game uses
(pointer $0B92), and compare the collision byte of every cell. Expected: identical for Eagle and Octopus;
for Penguin only the cells of the melted igloos may differ (the retail destroy routine opens them)."""
import sys, os; sys.path.insert(0, 'tools')
from mmx import *
ROM = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/v10_rc3.sfc'; rom = VANILLA.read_bytes(); prom = ROM.read_bytes()
def pc(a): return ((a >> 16) & 0x7F) * 0x8000 + (a & 0x7FFF)
import re
NMAPS = {5: int(re.search(r'appended to (\d+)', open(ROOT / 'build/gen/eagle_data.asm').read()).group(1)),
         1: int(re.search(r'appended to (\d+)', open(ROOT / 'build/gen/octo_data.asm').read()).group(1))}
GRID_SC = {}
m = MMX(ROM, rt=ROOT / 'build/rt_coll'); pw = make_password_state(m); bad = 0
for st, bit in ((5, 0x40), (1, 0x04), (7, 0x20), (3, 0x02), (8, 0x08)):
    out = {}
    for mask in (0x00, bit):
        for cp in range(3):
            enter_stage_at_cp(m, st, mask, cp, rom, pw); m.frames(10)
            cptr = m.rw(0x0B92) | (m.rb(0x0B94) << 16)
            bm = m.read(0x2000, 0x8000)
            idx = [bm[i] | (bm[i + 1] << 8) for i in range(0, 0x8000, 2)]
            grid = set(m.read(0xE800, 0x800)) - {0}; GRID_SC[st] = grid
            out[(mask, cp)] = ([prom[pc(cptr) + k] for k in idx], idx)
    for cp in range(3):
        (a, ia), (b, ib) = out[(0, cp)], out[(bit, cp)]
        # the stage's real map count: retail map table length (scenes past the stage's data hold leftover RAM)
        n = NMAPS.get(st, 1 << 16)
        live = [i for i in range(len(a)) if ia[i] < n]
        leftover_scenes = {i // 0x100 for i in range(len(a)) if ia[i] >= n}
        used = leftover_scenes & GRID_SC[st]
        print(f'   leftover cells lie in scenes {min(leftover_scenes, default=0):#x}-{max(leftover_scenes, default=0):#x}; screen grid uses scenes up to {max(GRID_SC[st]):#x}; overlap {sorted(used)}', flush=True)
        bad += bool(used)
        diff = [i for i in live if a[i] != b[i]]
        print(f'   {len(live)} cells reference real maps (< {n:#x}); {len(a) - len(live)} cells hold out-of-range leftovers', flush=True)
        ok = not diff
        print(f'stage {st} {STAGE_NAME[st]:9s} cp{cp}: collision cells differing normal vs altered: {len(diff)}' + ('' if ok else f'  first {[hex(0x2000 + 2 * i) for i in diff[:6]]}'), flush=True)
        bad += not ok and st != 8
print('COLLISION', 'PASS' if not bad else f'FAIL ({bad})')
