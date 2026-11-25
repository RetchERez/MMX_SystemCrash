"""Visual glitch sweep: every screen of each changed stage, original vs changed, side by side at half size.
The camera is opened and X moved screen to screen (TEST ONLY: inspection, not gameplay). Output (private, git-ignored):
build/sweep/<stage>_<part>.png, 4 pairs per row, 8 rows per sheet."""
import sys; sys.path.insert(0, 'tools')
from mmx import *
from PIL import Image
ROM = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/chain_reaction_v1.0.sfc'
rom = VANILLA.read_bytes(); P = 0x0BA8
STAGES = [('meltdown', 8, 0x08, 0, 0, 1 << 16), ('grid_down', 7, 0x20, 0, 0, 1 << 16), ('radar_down', 5, 0x40, 0, 0, 1 << 16),
          ('empty_arsenal', 1, 0x04, 0, 0, 4352), ('empty_arsenal_cp1', 1, 0x04, 1, 4608, 7168), ('empty_arsenal_cp2', 1, 0x04, 2, 7168, 1 << 16),
          ('ambush', 3, 0x02, 0, 0, 1 << 16)]
only = sys.argv[2:] if len(sys.argv) > 2 else None
out = ROOT / 'build/sweep'; out.mkdir(parents=True, exist_ok=True)
m = MMX(ROM, rt=ROOT / 'build/rt_vsweep'); pw = make_password_state(m)
def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
def opencam(): ww(0x1E56, 0); ww(0x1E58, 0x1F00); ww(0x1E5A, 0); ww(0x1E5C, 0x0F00)
def tour(st, mask, cp=0, xmin=0, xmax=1 << 16):
    enter_stage_at_cp(m, st, mask, cp, rom, pw); m.frames(20)
    grid = m.read(0x7EE800, 0x400)
    cells = sorted(((r, c) for r in range(32) for c in range(32) if grid[r * 32 + c] and xmin <= c * 256 < xmax), key=lambda rc: (rc[1], rc[0]))
    shots = []
    x, y = m.rw(P + 5), m.rw(P + 8)
    for r, c in cells:
        tx, ty = c * 256 + 128, r * 256 + 112
        n = 60
        for i in range(1, n + 1):
            opencam(); ww(P + 5, x + (tx - x) * i // n); ww(P + 8, y + (ty - y) * i // n); m.wb(0x0BCF, 0x10); m.frames(1)
        for i in range(25): opencam(); ww(P + 5, tx); ww(P + 8, ty); m.wb(0x0BCF, 0x10); m.frames(1)
        x, y = tx, ty
        m.shot(str(ROOT / 'build/vs_tmp.png')); shots.append(((r, c), Image.open(ROOT / 'build/vs_tmp.png').convert('RGB').copy()))
    return shots
for name, st, bit, cp, xmin, xmax in STAGES:
    if only and name not in only: continue
    A = tour(st, 0x00, cp, xmin, xmax); B = tour(st, bit, cp, xmin, xmax)
    pairs = []
    for (rc, a), (_, b) in zip(A, B):
        p = Image.new('RGB', (512, 224)); p.paste(a, (0, 0)); p.paste(b, (256, 0)); pairs.append(p.resize((256, 112)))
    per = 32
    for k in range(0, len(pairs), per):
        chunk = pairs[k:k + per]; rows = (len(chunk) + 3) // 4
        sheet = Image.new('RGB', (1024 + 3 * 6, rows * 112 + (rows - 1) * 6), (255, 0, 255))
        for i, p in enumerate(chunk): sheet.paste(p, ((i % 4) * 262, (i // 4) * 118))
        sheet.save(out / f'{name}_{k // per + 1}.png')
    print(name, 'screens', len(pairs), flush=True)
