"""Visual check sheet: normal vs altered for all eight reactions at a representative spot (private, not shipped)."""
import sys, os; sys.path.insert(0, 'tools')
from mmx import *
from PIL import Image, ImageDraw
ROM = Path(os.environ.get('SC_ROM', ROOT / 'build/sc_v10_rc4.sfc')); rom = VANILLA.read_bytes(); P = 0x0BA8
m = MMX(ROM, rt=ROOT / 'build/rt_vs'); pw = make_password_state(m)
def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
def opencam(): ww(0x1E56, 0); ww(0x1E58, 0x1F00); ww(0x1E5A, 0); ww(0x1E5C, 0x0F00)
def glide(tx, ty, n=300):
    x0, y0 = m.rw(P + 5), m.rw(P + 8)
    for i in range(n):
        opencam(); ww(P + 5, x0 + (tx - x0) * i // n); ww(P + 8, y0 + (ty - y0) * i // n); m.wb(0x0BCF, 0x10); m.frames(1)
    for i in range(60): opencam(); m.wb(0x0BCF, 0x10); m.frames(1)
CASES = [  # name, stage, source bit, checkpoint, glide target or None
    ('Frozen Factory (retail)', 4, 0x80, 0, None),
    ('Blackout (retail)', 6, 0x10, 0, None),
    ('Flooded Forest (retail)', 2, 0x01, 0, (1500, 700)),
    ('Meltdown', 8, 0x08, 1, (5200, 660)),
    ('Grid Down', 7, 0x20, 0, None),
    ('Radar Down', 5, 0x40, 1, (3560, 200)),
    ('Empty Arsenal', 1, 0x04, 1, (4700, 640)),
    ('Ambush Called Off', 3, 0x02, 0, (560, 520)),
]
rows = []
for name, st, bit, cp, tgt in CASES:
    pair = []
    for mask in (0x00, bit):
        enter_stage_at_cp(m, st, mask, cp, rom, pw); m.frames(30)
        if tgt: glide(*tgt)
        else: m.frames(60)
        m.shot('build/t.png'); im = Image.open('build/t.png')
        ImageDraw.Draw(im).rectangle([0, 206, 255, 223], fill=(0, 0, 0))
        ImageDraw.Draw(im).text((4, 208), ('normal' if mask == 0 else 'ALTERED') + ': ' + name, fill=(255, 255, 0)); pair.append(im)
    rows.append(pair); print('captured', name, flush=True)
W = Image.new('RGB', (512, 224 * len(rows)))
for i, (a, b) in enumerate(rows): W.paste(a, (0, 224 * i)); W.paste(b, (256, 224 * i))
W.save('build/v10_visual_sheet.png')
