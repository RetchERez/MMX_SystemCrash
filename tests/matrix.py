"""State matrix: for one stage, all 256 boss masks, patched vs vanilla.
Signature per load = palette buffer $0300-$04FF, screen grid $E800-$EBFF, live enemy IDs, after 30 frames.
Expectation: identical to vanilla unless this stage is a new altered target whose source bit is set."""
import sys, json, hashlib; sys.path.insert(0, 'tools')
from mmx import *
stage = int(sys.argv[1]); patched = Path(sys.argv[2]); out = Path(sys.argv[3])
rom = VANILLA.read_bytes()
SOURCE_BIT = {7: 0x20, 5: 0x40, 1: 0x04, 3: 0x02, 8: 0x08}   # all five new links (target stage: source boss bit)
def sigs(rompath, tag):
    m = MMX(rompath, rt=ROOT / f'build/rt_matrix_{tag}_{stage}')
    make_password_state(m); pw = m.save()
    res = {}
    for mask in range(256):
        to_stage_select(m, mask, rom, pw)
        enter_stage(m, stage)
        m.frames(30)
        probe = b''
        if stage == 3:   # Ambush Called Off changes nothing at load: glide a fixed path and record waking enemies
            P = 0x0BA8; x = m.rw(P + 5)
            for f in range(600):
                for a, v in ((0x1E56, 0), (0x1E58, 0x1F00), (0x1E5A, 0), (0x1E5C, 0x0F00)):
                    m.wb(a, v & 0xff); m.wb(a + 1, v >> 8)
                if f % 3 == 0: x += 1; m.wb(P + 5, x & 0xff); m.wb(P + 6, x >> 8)
                m.frames(1); m.wb(0x0BCF, 0x10)
                probe += bytes(m.rb(0x0E68 + i * 0x40 + 0xA) if m.rb(0x0E68 + i * 0x40) and m.rb(0x0E68 + i * 0x40 + 1) >= 2 else 0 for i in range(15))
        if stage == 8:   # Meltdown changes nothing at load: spawn an igloo and a snowball next to X and watch them
            P = 0x0BA8
            for aid in (0x57, 0x54):
                b = 0x0E68 + 14 * 0x40
                for k in range(0x40): m.wb(b + k, 0)
                x = m.rw(P + 5) + 96; y = m.rw(P + 8) - 8
                m.wb(b, 1); m.wb(b + 0xA, aid); m.wb(b + 5, x & 0xff); m.wb(b + 6, x >> 8); m.wb(b + 8, y & 0xff); m.wb(b + 9, y >> 8)
                alive = 0
                for f in range(20):
                    m.frames(1)
                    if m.rb(b) and m.rb(b + 0xA) == aid: alive += 1
                probe += bytes([aid, alive])
        h = hashlib.sha1(probe + m.read(0x0300, 0x200) + m.read(0x7EE800, 0x400) + m.read(0x0B92, 6) + m.read(0x7E2000, 0x8000) + bytes(sorted(enemy_ids(m)))).hexdigest()[:12]
        res[mask] = h
    m.close()
    return res
v = sigs(VANILLA, 'v'); p = sigs(patched, 'p')
fails = []; altered = 0
for mask in range(256):
    expect_alt = stage in SOURCE_BIT and bool(mask & SOURCE_BIT[stage])
    same = v[mask] == p[mask]
    if expect_alt:
        altered += 1
        if same: fails.append((mask, 'expected altered, got vanilla'))
    elif not same:
        fails.append((mask, 'expected vanilla, differs'))
# single-bit isolation: all altered masks share one signature, all non-altered match vanilla
alt_sigs = {p[mk] for mk in range(256) if stage in SOURCE_BIT and mk & SOURCE_BIT[stage]}
json.dump({'stage': stage, 'loads': 512, 'altered_masks': altered, 'altered_signatures': len(alt_sigs),
           'fails': fails}, open(out, 'w'), indent=1)
print(f'stage {stage}: fails={len(fails)} altered_masks={altered} distinct_altered_sigs={len(alt_sigs)}')
