"""Stage-select OFFLINE label. For each set of beaten Mavericks: real password -> real stage select, vanilla and patch run
the same input. Checks, every frame for 240 frames on the stage select (cursor moved around):
  - badge sprites (tile $C0, attr $3E) sit exactly on the portraits of the CHANGED stages, nowhere else;
  - every original sprite entry is identical to vanilla (badges are only appended after them);
  - all of WRAM identical to vanilla except the sprite buffer ($0700-$091F), OBJ palette 7 ($04E0-$04FF),
    the upload queue ($0500-$05FF) and its two flags ($A1, $A3) and the builder's last-frame sprite count ($E3).
Then a stage is picked: once the game leaves the stage select, no badge is drawn and WRAM matches vanilla again
(outside the same buffers) through 600 frames of the stage intro and gameplay start."""
import sys
sys.path.insert(0, 'tools')
from pathlib import Path
from mmx import *

ROM = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/system_crash_v1.0.sfc'
rom = VANILLA.read_bytes()
SRC = {1: 3, 2: 1, 3: 2, 4: 8, 5: 7, 6: 5, 7: 6, 8: 4}            # changed stage -> Maverick whose defeat changes it
POS = {s: (35 + 48 * GRID[s][0] + 5, 18 + 48 * GRID[s][1] + 34) for s in SRC}   # left sprite of the label
OUT = ROOT / 'build/qa/badge'; OUT.mkdir(parents=True, exist_ok=True)
# stack zone and boot-time header-checksum copy excluded as in test_parity.py
SKIP = [(0x0100, 0x0300), (0xFFBC, 0xFFC0), (0x0700, 0x0920), (0x04E0, 0x0500), (0x0500, 0x0600), (0xA1, 0xA2), (0xA3, 0xA4), (0xE3, 0xE4),
        (0x1E000, 0x1E200),   # $7F:E000-E1FF (the game's fade copy): the label keeps the palette row, queue bytes and sprite entries here while browsing (the game overwrites it at the pick)
        (0x0B9B, 0x0B9C)]     # free-running frame counter: its phase after the pick varies with menu time (v1.0 shows the same)


def oam(m):
    o = m.read(0x700, 0x200); hi = m.read(0x900, 0x20)
    return [(o[i * 4], o[i * 4 + 1], o[i * 4 + 2], o[i * 4 + 3], (hi[i // 4] >> (2 * (i % 4))) & 3) for i in range(128)]


def wram_diff(a, b):
    return [i for i in range(0x20000) if a.read(i, 1) != b.read(i, 1) and not any(lo <= i < hi for lo, hi in SKIP)]


def wram_diff_fast(a, b):
    x, y = a.read(0, 0x20000), b.read(0, 0x20000)
    if x == y: return []
    return [i for i in range(0x20000) if x[i] != y[i] and not any(lo <= i < hi for lo, hi in SKIP)]


def play(path, mask, tag):
    """Same input on either ROM. Returns per-frame OAM, WRAM every 60 frames, mode bytes after the pick."""
    m = MMX(path, rt=ROOT / f'build/rt_badge_{tag}')
    pw = make_password_state(m)
    if LEFTOVER:   # TEST ONLY, same in both runs: a non-empty palette row 15, as another screen can leave it
        m.load(pw); m.frames(2)
        for i in range(32): m.wb(0x04E0 + i, 0x5A ^ i)
        pw = m.save()
    to_stage_select(m, mask, rom, pw)
    rec = {'oam': [], 'wram': [], 'after': [], 'mode': []}
    moves = ['right', 'down', 'down', 'left', 'up', None]
    for f in range(240):
        mv = moves[(f // 40) % len(moves)]
        m.frames(1, [mv] if (f % 40 < 6 and mv) else [])
        rec['oam'].append(oam(m))
        if f % 60 == 59: rec['wram'].append(m.read(0, 0x20000))
    m.shot(str(OUT / f'select_{tag}_{mask:02X}.png'))
    m.fe.run_frames(4, ['b']); m.fe.clear_buttons()
    for f in range(600):
        m.frames(1)
        rec['mode'].append((m.rb(0xD1), m.rb(0xD2), m.rb(0xD3)))
        rec['after'].append(oam(m))
        if f % 100 == 99: rec['wram'].append(m.read(0, 0x20000))
    m.shot(str(OUT / f'after_{tag}_{mask:02X}.png'))
    m.close()
    return rec


# after the pick only these remain excluded: stack zone, header-checksum copy, frame-counter phase
SKIP_AFTER = [(0x0100, 0x0300), (0xFFBC, 0xFFC0), (0x0B9B, 0x0B9C)]


def diff(x, y, skip=None):
    if x == y: return []
    return [i for i in range(0x20000) if x[i] != y[i] and not any(lo <= i < hi for lo, hi in (skip or SKIP))]


def run(mask):
    v = play(VANILLA, mask, 'v'); p = play(ROM, mask, 'p')
    beaten = {k for k, b in MASK_BIT.items() if mask & b}
    want = sorted(POS[s] for s in SRC if SRC[s] in beaten)
    fails = []
    isb = lambda e: e[1] < 0xE0 and 0xC0 <= e[2] <= 0xC3 and e[3] == 0x3E
    for f, (ov, op) in enumerate(zip(v['oam'], p['oam'])):
        badges = sorted((e[0], e[1]) for e in op if isb(e) and e[2] == 0xC0)
        if f >= 2 and sorted((e[0], e[1], e[2]) for e in op if isb(e)) != sorted((x + 8 * t, y, 0xC0 + t) for x, y in want for t in range(4)): fails.append(f'frame {f}: label sprites not in place')
        if f >= 2 and badges != want: fails.append(f'frame {f}: badges {badges} want {want}')
        if [e for e in ov if e[1] < 0xE0] != [e for e in op if e[1] < 0xE0 and not isb(e)]: fails.append(f'frame {f}: original sprites differ')
    still = next((f for f, md in enumerate(p['mode']) if md != (2, 0, 1)), None) is None   # no stage was started
    for k, (a, b) in enumerate(zip(v['wram'], p['wram'])):
        d = diff(a, b, SKIP if (k < 4 or still) else SKIP_AFTER)   # 4 snapshots while browsing, then 6 after the pick
        if d: fails.append(f'snapshot {k}: WRAM differs at {[hex(i) for i in d[:6]]}')
    left = next((f for f, md in enumerate(p['mode']) if md != (2, 0, 1)), None)
    left_v = next((f for f, md in enumerate(v['mode']) if md != (2, 0, 1)), None)
    if left != left_v: fails.append(f'left the stage select at frame {left}, original at {left_v}')
    if left is None:   # the cursor ended on a panel (MAP etc.): no stage starts in either game; screens must still match
        for f in range(len(p['after'])):
            if [e for e in v['after'][f] if e[1] < 0xE0] != [e for e in p['after'][f] if e[1] < 0xE0 and not isb(e)]: fails.append(f'frame {f} after the press: sprites differ'); break
    else:
        for f in range(left + 2, len(p['after'])):
            if any(isb(e) for e in p['after'][f]): fails.append(f'frame {f} after the pick: badge still drawn'); break
            if [e for e in v['after'][f] if e[1] < 0xE0] != [e for e in p['after'][f] if e[1] < 0xE0]: fails.append(f'frame {f} after the pick: sprites differ'); break
    return want, fails


LEFTOVER = False
if __name__ == '__main__':
    masks = [int(a, 16) for a in sys.argv[2:]] or [0x00] + [MASK_BIT[k] for k in range(1, 9)] + [0xA8, 0xFF]
    bad = 0
    for mask in masks:
        want, fails = run(mask)
        bad += bool(fails)
        print(f'mask {mask:02X}: {len(want)} labels expected; ' + ('PASS' if not fails else 'FAIL ' + '; '.join(fails[:4])), flush=True)
    LEFTOVER = True   # the label must hand back a non-empty row 15 exactly
    want, fails = run(0xA8); bad += bool(fails)
    print('mask A8 with a leftover palette row 15: ' + ('PASS' if not fails else 'FAIL ' + '; '.join(fails[:4])), flush=True)
    print('LABEL', 'PASS' if not bad else f'FAIL ({bad})')
