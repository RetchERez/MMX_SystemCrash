"""Title subtitle (SYSTEM CRASH) against the same build without it, same input in both:
  A. boot -> logo complete (subtitle) -> START -> menu (subtitle) -> PASS WORD -> password screen
  B. boot -> logo left idle until the game's own attract demo takes over
Checks: the subtitle's 7 sprites are in entries 9-15 exactly when the logo is complete or the menu waits for input,
and nowhere else; on every frame, all of WRAM matches the baseline except what the subtitle borrows (sprite buffer
$0700-$091F, OBJ palette 7 $04E0-$04FF, the upload queue $0500-$05FF with its flags $A1/$A3, and $00C0 on the logo
screen) is reported per frame (timing can shift work by a frame while the menu loads); once the title is left
(240 frames into the password screen / the attract demo) all of WRAM must match the baseline."""
import sys
sys.path.insert(0, 'tools')
from pathlib import Path
from mmx import *

ROM = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/system_crash_v1.0.sfc'
# baseline: the same build without the subtitle (tools/build.py --define SC_NO_TITLE). The title already differs from
# the original game in v1.0 without any title code (expanded ROM), so the subtitle is judged against that build
BASE = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / 'build/system_crash_notitle.sfc'
OUT = ROOT / 'build/qa/title'; OUT.mkdir(parents=True, exist_ok=True)
STACK = [(0x0100, 0x0300), (0xFFBC, 0xFFC0)]          # stack residue, boot-time header-checksum copy (as test_parity)
BORROW = STACK + [(0x0700, 0x0920), (0x04E0, 0x0500), (0x0500, 0x0600), (0xA1, 0xA2), (0xA3, 0xA4), (0xC0, 0xC1)]


def script_a():
    yield from [None] * 300
    for _ in range(5): yield from ['start'] * 2 + [None] * 58
    yield from [None] * 500
    yield from ['start'] * 3 + [None] * 90
    yield from ['down'] * 10 + [None] * 30
    yield from ['start'] * 3 + [None] * 900


def script_b():
    yield from [None] * 300
    for _ in range(5): yield from ['start'] * 2 + [None] * 58
    yield from [None] * 2200


def play(path, script, tag):
    m = MMX(path, rt=ROOT / f'build/rt_title_{tag}')
    rec = []
    for f, b in enumerate(script()):
        m.frames(1, [b] if b else [])
        o = m.read(0x724, 28)
        rec.append((m.read(0, 0x20000), [o[i * 4:i * 4 + 4] for i in range(7)], (m.rb(0x38), m.rb(0x39), m.rb(0x3A)), (m.rb(0xD1), m.rb(0xD2), m.rb(0xD3))))
    m.shot(str(OUT / f'{tag}_end.png'))
    m.close()
    return rec


def diff(a, b, skip):
    if a == b: return []
    return [i for i in range(0x20000) if a[i] != b[i] and not any(lo <= i < hi for lo, hi in skip)]


def check(name, script):
    v = play(BASE, script, 'v_' + name); p = play(ROM, script, 'p_' + name)
    fails, shown, in_title, transient, first_t = [], 0, True, [], ''
    for f, (a, b) in enumerate(zip(v, p)):
        st = b[2]
        want = st == (0, 4, 0x16) or st[:2] == (2, 2)
        drawn = all(s[1] == 0x72 and s[3] == 0x3E for s in b[1])
        cleared = b[1] == a[1]   # not drawn: entries 9-15 exactly as in the original
        if not want and not cleared and f > 0 and (v[f - 1][2][:2] not in ((0, 4), (2, 2))): fails.append(f'frame {f}: subtitle left on screen in state {st}'); break
        shown += drawn
        leaving = st[0] not in (0, 2) or (st[0] == 0 and st[1] == 6) or (st[0] == 2 and st[1] == 4)
        skip = BORROW if (want or not leaving) and f < len(v) - 120 else STACK
        d = diff(a[0], b[0], skip)
        if d:
            transient.append(f)
            if len(transient) == 1: first_t = f'frame {f} state {st} at {[hex(i) for i in d[:6]]}'
    if shown < 60: fails.append(f'subtitle shown on only {shown} frames')
    d = diff(v[-1][0], p[-1][0], STACK)
    if d:
        first = next(f for f in range(len(v)) if diff(v[f][0], p[f][0], BORROW))
        fails.append(f'end: WRAM differs at {[hex(i) for i in d[:6]]}; first frame outside the borrowed bytes {first} state {p[first][2]} at {[hex(i) for i in diff(v[first][0], p[first][0], BORROW)[:6]]}')
    last_t = transient[-1] if transient else None
    note = f'; transient differences on {len(transient)} frames (first {first_t}, last frame {last_t})' if transient else '; no transient differences'
    print(f'{name}: subtitle on {shown} frames; final title state {p[-1][2]}, game mode {p[-1][3]}{note}; ' + ('PASS' if not fails else 'FAIL ' + '; '.join(fails)), flush=True)
    return not fails


ok = check('menu_to_password', script_a) & check('idle_to_demo', script_b)
print('TITLE', 'PASS' if ok else 'FAIL')
