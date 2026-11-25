"""Sigma firewall: select the fortress icon (Sigma 1 for real; 2-4 by stage number, set during the intro) with every
boss beaten, on vanilla and on the patch, run 600 frames of the same inputs, and compare all of WRAM
(stack zone and the header-checksum copy excluded, as in test_parity)."""
import sys, os, hashlib; sys.path.insert(0, 'tools')
from mmx import *
ROM = Path(os.environ.get('CR_ROM', ROOT / 'build/v10_rc3.sfc')); N = int(os.environ.get('CR_SIGMA_FRAMES', 2400)); rom = VANILLA.read_bytes()
def run(path, tag):
    m = MMX(path, rt=ROOT / f'build/rt_sig_{tag}'); pw = make_password_state(m); out = {}
    for sid in (9, 10, 11, 12):
        to_stage_select(m, 0xFF, rom, pw)
        m.frames(60); assert (m.rb(0x1E4C), m.rb(0x1E4F)) == (3, 3)  # the real fortress icon, offered once all 8 are beaten
        m.fe.run_frames(4, ['b']); m.fe.clear_buttons()
        for f in range(2400):
            if sid != 9: m.wb(0x1F7A, sid)   # Sigma 1 is entered for real; 2-4 by setting the stage number (TEST ONLY)
            m.frames(1)
            if m.rb(0xD2) == 4 and m.rb(0xD3) == 4: break
        snaps = []
        for f in range(N):
            m.fe.run_frames(1, ['right'] if f % 60 < 40 else ['right', 'b']); m.wb(0x0BCF, 0x10)
            if f % 60 == 0:
                w = bytearray(m.read(0, 0x20000)); w[0x100:0x300] = bytes(0x200); w[0xFFBC:0xFFC0] = bytes(4)
                snaps.append(hashlib.sha1(w).hexdigest())
        out[sid] = (m.rb(0x1F7A), snaps)
    m.close(); return out
v = run(VANILLA, 'v'); p = run(ROM, 'p')
for sid in (9, 10, 11, 12):
    print(f'Sigma stage id {sid:02X}: loaded id {p[sid][0]:02X}; WRAM identical to vanilla over {N} frames: {v[sid][1] == p[sid][1]}')
