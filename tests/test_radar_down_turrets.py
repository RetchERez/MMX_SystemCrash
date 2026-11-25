"""Death Rogumer deck turrets: normal = both fire; Radar Down = the turret at x 6086 fires, the one at x 6190 is silent.
Also the Mandrill parity case: turrets only exist in stage 05, gate is stage-scoped."""
import sys; sys.path.insert(0,'tools')
from mmx import *
import os; ROM=Path(os.environ.get('SC_ROM', ROOT/'build/v10_rc1.sfc')); rom=VANILLA.read_bytes(); P=0x0BA8
m=MMX(ROM, rt=ROOT/'build/rt_rdt'); pw=make_password_state(m)
def ww(a,v): m.wb(a,v&0xff); m.wb(a+1,(v>>8)&0xff)
def openb(): ww(0x1E56,0); ww(0x1E58,0x1F00); ww(0x1E5A,0); ww(0x1E5C,0x0700)
for mask in (0x00,0x40,0xFF,0xBF):
    enter_stage_at_cp(m,5,mask,2,rom,pw); m.frames(30)
    x0,y0=m.rw(P+5),m.rw(P+8)
    for i in range(200):
        openb(); ww(P+5,x0+(6138-x0)*i//200); ww(P+8,y0+(150-y0)*i//200); m.wb(0x0BCF,0x10); m.frames(1)
    turrets={}; shots={}; prev=set()
    for f in range(1200):
        openb(); ww(P+5,6138); m.wb(0x0BCF,0x10); m.frames(1)
        for i in range(15):
            b=0x0E68+i*0x40
            if m.rb(b) and m.rb(b+0xA)==0x50: turrets[i]=m.rw(b+5)
        cur={i for i in range(8) if m.rb(0x1428+i*0x40) and m.rb(0x1428+i*0x40+0xA)==0x13}
        for i in cur-prev:
            sx=m.rw(0x1428+i*0x40+5)
            if turrets:
                t=min(turrets.values(),key=lambda tx:abs(tx-sx)); shots[t]=shots.get(t,0)+1
        prev=cur
    print(f'mask {mask:02X} (Kuwanger {"beaten" if mask&0x40 else "alive"}): turrets at {sorted(set(turrets.values()))} shots per turret {dict(sorted(shots.items()))}')
