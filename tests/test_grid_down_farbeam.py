"""Far-sensor check: when a beam from a live far sensor (x >= $0300) exists, place X inside it.
Expect Ray Trap shots in BOTH normal and Grid Down (far sensors stay on backup power)."""
import sys; sys.path.insert(0,'tools')
from mmx import *
import os; ROM=Path(os.environ.get('CR_ROM', ROOT/'build/grid_down_test.sfc')); rom=VANILLA.read_bytes()
m=MMX(ROM, rt=ROOT/'build/runtime_test'); pw=make_password_state(m); P=0x0BA8
def ww(a,v): m.wb(a,v&0xff); m.wb(a+1,(v>>8)&0xff)
for mask in (0x00,0x20):
    to_stage_select(m,mask,rom,pw); enter_stage(m,7); m.frames(20)
    for y in range(6040,5180,-16): ww(P+5,200); ww(P+8,y); m.wb(0x0BCF,0x10); m.frames(2)
    x=250
    while x<900:
        ww(0x1E58,0x0700); x+=2; ww(P+5,x); m.frames(1); m.wb(0x0BCF,0x10)
    shots=0; prev=set(); touched=0
    for f in range(900):
        ww(0x1E58,0x0700); m.wb(0x0BCF,0x10)
        for i in range(15):
            b=0x0E68+i*0x40
            if m.rb(b) and m.rb(b+0xA)==0x43 and m.rw(b+5)>=0x0340:
                ww(P+5,m.rw(b+5)); ww(P+8,m.rw(b+8)); touched+=1; break
        m.frames(1)
        cs={i for i in range(8) if m.rb(0x1428+i*0x40) and m.rb(0x1428+i*0x40+0xA)==0x1C}
        shots+=len(cs-prev); prev=cs
    print(f'mask {mask:02X}: frames X held inside a far beam={touched}  Ray Trap shots={shots}')
