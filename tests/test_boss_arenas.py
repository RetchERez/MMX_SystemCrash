"""Boss arenas must be untouched: walk into Kuwanger's and Storm Eagle's fights in normal and altered states.
Reports: boss actor seen, palette buffer during the fight (normal vs altered), deck turrets alive / firing during
the Storm Eagle fight."""
import sys, os, hashlib; sys.path.insert(0, 'tools')
from mmx import *
from PIL import Image, ImageDraw
ROM = Path(os.environ.get('CR_ROM', ROOT / 'build/v10_rc3.sfc')); rom = VANILLA.read_bytes(); P = 0x0BA8
m = MMX(ROM, rt=ROOT / 'build/rt_ba'); pw = make_password_state(m)
def ww(a, v): m.wb(a, v & 0xff); m.wb(a + 1, (v >> 8) & 0xff)
shots = []
for stage, boss, bit in ((7, 0x05, 0x20), (5, 0x52, 0x40)):
    res = {}
    for mask in (0x00, bit):
        enter_stage_at_cp(m, stage, mask, 2, rom, pw); m.frames(30)
        boss_frames = 0; pal = None; turret_alive = 0; turret_shots = 0; prev = set()
        for f in range(3000):
            m.fe.run_frames(1, ['right'] if f % 50 < 38 else ['right', 'b']); m.wb(0x0BCF, 0x10)
            ids = enemy_ids(m)
            if boss in ids:
                boss_frames += 1
                if boss_frames == 330:   # after the door transition and boss intro: the fight itself
                    pal = m.read(0x300, 0x100); m.shot('build/t.png'); im = Image.open('build/t.png')
                    ImageDraw.Draw(im).text((30, 212), f'stage {stage:02X} mask {mask:02X} boss fight', fill=(255, 255, 0)); shots.append(im)
                if 0x50 in ids: turret_alive += 1
                cur = {i for i in range(8) if m.rb(0x1428 + i * 0x40) and m.rb(0x1428 + i * 0x40 + 0xA) == 0x13}
                turret_shots += len(cur - prev); prev = cur
            if boss_frames > 700: break
        res[mask] = (boss_frames, pal, turret_alive, turret_shots, m.rw(P + 5))
        print(f'stage {stage:02X} mask {mask:02X}: boss frames {boss_frames}, X {m.rw(P + 5)}, deck turrets alive during fight {turret_alive} frames, turret shots {turret_shots}', flush=True)
    a, b = res[0x00][1], res[bit][1]
    if a and b:
        rows = [r for r in range(8) if a[r*32:r*32+32] != b[r*32:r*32+32]]
        print(f'   during the fight, BG palette rows differing normal vs altered: {rows}'
              + ('  (row 0 = spare dark-glass row, not displayed in this stage)' if rows == [0] else ''))
    else:
        print('   (boss not reached in one of the states)')
W = Image.new('RGB', (256 * len(shots), 224)); [W.paste(s, (256 * i, 0)) for i, s in enumerate(shots)]; W.save('build/boss_arenas.png')
