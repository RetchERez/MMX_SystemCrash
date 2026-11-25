"""Reference pictures: each new reaction side by side (original left, changed right), 2x, no text.
Output (private, ROM-derived, git-ignored PNGs): reference/<stage>.png and reference/all_five.png"""
import sys; sys.path.insert(0, 'tools')
from mmx import *
from PIL import Image
ROM = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/chain_reaction_v1.0.sfc'
rom = VANILLA.read_bytes(); P = 0x0BA8
SPOTS = [  # file, stage, source bit, checkpoint, (x, y) or None, settle frames
    ('1_meltdown', 8, 0x08, 1, (5200, 660), 40),
    ('2_grid_down', 7, 0x20, 0, None, 60),
    ('3_radar_down', 5, 0x40, 0, (1700, 640), 40),
    ('4_empty_arsenal', 1, 0x04, 1, (4700, 640), 40),
    ('5_ambush_called_off', 3, 0x02, 0, (560, 520), 60),
]
only = sys.argv[2:] if len(sys.argv) > 2 else None
m = MMX(ROM, rt=ROOT / 'build/rt_ref'); pw = make_password_state(m)
def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
def opencam(): ww(0x1E56, 0); ww(0x1E58, 0x1F00); ww(0x1E5A, 0); ww(0x1E5C, 0x0F00)
pairs = []
for name, st, bit, cp, tgt, settle in SPOTS:
    if only and name not in only: continue
    half = []
    for mask in (0x00, bit):
        enter_stage_at_cp(m, st, mask, cp, rom, pw); m.frames(30)
        if tgt:
            x0, y0 = m.rw(P + 5), m.rw(P + 8)
            for i in range(300):
                opencam(); ww(P + 5, x0 + (tgt[0] - x0) * i // 300); ww(P + 8, y0 + (tgt[1] - y0) * i // 300); m.wb(0x0BCF, 0x10); m.frames(1)
            for i in range(settle): opencam(); ww(P + 5, tgt[0]); ww(P + 8, tgt[1]); m.wb(0x0BCF, 0x10); m.frames(1)
        else:
            m.frames(settle)
        m.shot(str(ROOT / 'build/ref_tmp.png')); half.append(Image.open(ROOT / 'build/ref_tmp.png').convert('RGB').copy())
    pair = Image.new('RGB', (512, 224)); pair.paste(half[0], (0, 0)); pair.paste(half[1], (256, 0))
    pair = pair.resize((1024, 448), Image.NEAREST); pair.save(ROOT / f'reference/{name}.png'); pairs.append(pair)
    print('saved', name, flush=True)
if not only:
    col = Image.new('RGB', (1024, 448 * len(pairs)))
    for i, p in enumerate(pairs): col.paste(p, (0, 448 * i))
    col.save(ROOT / 'reference/all_five.png'); print('saved all_five')
