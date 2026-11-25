"""Meltdown: (1) Penguin's cave bats unaffected (stage-scoped Ambush gate), (2) igloos melted: no igloo actor
alive, no igloo-spawned Tombots, map patched; Heart Tank item present, (3) no rolling snowballs; screenshots."""
import sys, os; sys.path.insert(0, 'tools')
from mmx import *
from PIL import Image, ImageDraw
ROM = Path(os.environ.get('SC_ROM', ROOT / 'build/v10_rc1.sfc')); rom = VANILLA.read_bytes(); P = 0x0BA8
m = MMX(ROM, rt=ROOT / 'build/rt_md'); pw = make_password_state(m)
def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
def opencam(): ww(0x1E56, 0); ww(0x1E58, 0x1F00); ww(0x1E5A, 0); ww(0x1E5C, 0x0F00)   # TEST ONLY
def glide(path, frames_per_px=3, watch=None):
    for (xa, ya), (xb, yb) in zip(path, path[1:]):
        n = max(abs(xb - xa), abs(yb - ya)) * frames_per_px // 2 or 1
        for i in range(n):
            opencam(); ww(P + 5, xa + (xb - xa) * i // n); ww(P + 8, ya + (yb - ya) * i // n); m.wb(0x0BCF, 0x10)
            m.frames(1)
            if watch: watch()
shots = []
for mask in (0x00, 0x08):
    # (1) bats in the cave (cp0)
    enter_stage_at_cp(m, 8, mask | 0x02, 0, rom, pw); m.frames(30)   # Chameleon beaten too: Ambush must NOT apply here
    bats = set(); woke = set()
    def wb():
        for i in range(15):
            b = 0x0E68 + i * 0x40
            if m.rb(b) and m.rb(b + 0xA) == 0x2D:
                bats.add(i); 
                if m.rb(b + 1) >= 2: woke.add(i)
    glide([(m.rw(P + 5), m.rw(P + 8)), (1600, 1080), (2300, 1300), (2700, 1260)], watch=wb)
    # (2)(3) igloo field and slopes (cp1)
    enter_stage_at_cp(m, 8, mask, 1, rom, pw); m.frames(30)
    seen = {'igloo': 0, 'tombot': set(), 'snowball': 0, 'heart': 0}
    def wi():
        for i in range(15):
            b = 0x0E68 + i * 0x40
            if not m.rb(b): continue
            a = m.rb(b + 0xA)
            if a == 0x57: seen['igloo'] += 1
            if a == 0x3A: seen['tombot'].add((i, m.rw(b + 5) // 64))
            if a == 0x54: seen['snowball'] += 1
    glide([(m.rw(P + 5), m.rw(P + 8)), (4700, 860), (5200, 660)], watch=wi)
    m.frames(40); m.shot('build/t.png'); im = Image.open('build/t.png')
    ImageDraw.Draw(im).text((30, 212), ('NORMAL' if mask == 0 else 'MELTDOWN') + ' Heart Tank igloo', fill=(255, 255, 0)); shots.append(im)
    # item actors: heart tank lives in the item/object pool; count any active slot near (5260,692) in all pools
    near = 0
    for base, n in ((0x0E68, 15), (0x1228, 8), (0x1428, 8), (0x1628, 12)):
        for i in range(n):
            b = base + i * 0x40
            if m.rb(b) and abs(m.rw(b + 5) - 5260) < 24 and abs(m.rw(b + 8) - 692) < 24: near += 1
    glide([(m.rw(P + 5), m.rw(P + 8)), (5700, 600), (6500, 600), (7300, 400)], watch=wi)
    print(f'mask {mask:02X}: cave bats seen {len(bats)} woke {len(woke)} | igloo-frames {seen["igloo"]} tombot slots {len(seen["tombot"])} '
          f'snowball-frames {seen["snowball"]} | objects at the Heart Tank spot {near}')
W = Image.new('RGB', (512, 224)); [W.paste(s, (256 * i, 0)) for i, s in enumerate(shots)]; W.save('build/meltdown_heart.png')
