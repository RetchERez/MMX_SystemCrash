"""Kuwanger Ray Trap hall, normal vs Grid Down. X is stepped through the whole hall (x 260-1100).
Logs which sensors spawn beams (by sensor X position) and how many trap shots fire.
Expect: normal = all five sensors beam; Grid Down = only the two far sensors (x >= $0300) beam,
and traps still fire when a live beam is touched."""
import sys, collections; sys.path.insert(0,'tools')
from mmx import *
import os; ROM=Path(os.environ.get('CR_ROM', ROOT/'build/grid_down_test.sfc')); rom=VANILLA.read_bytes()
m=MMX(ROM, rt=ROOT/'build/runtime_test'); pw=make_password_state(m); P=0x0BA8
def ww(a,v): m.wb(a,v&0xff); m.wb(a+1,(v>>8)&0xff)
for mask in (0x00,0x20):
    to_stage_select(m,mask,rom,pw); enter_stage(m,7); m.frames(20)
    for y in range(6040,5180,-16): ww(P+5,200); ww(P+8,y); m.wb(0x0BCF,0x10); m.frames(2)
    beams=collections.Counter(); sensors=set(); shots=0; prev=set(); prevshots=set(); shotx=[]
    x=250
    for f in range(1700):
        ww(0x1E58,0x0700)   # TEST ONLY: widen camera border
        if f%2==0 and x<1100: x+=1; ww(P+5,x)
        m.frames(1); m.wb(0x0BCF,0x10)
        for i in range(15):
            b=0x0E68+i*0x40
            if not m.rb(b): continue
            if m.rb(b+0xA)==0x42: sensors.add(m.rw(b+5))
            if m.rb(b+0xA)==0x43 and m.rb(b+1)==0 and m.rb(b+2)==0: pass
        # beams: count newly allocated $43 by nearest sensor
        cur={(i,m.rw(0x0E68+i*0x40+5)) for i in range(15) if m.rb(0x0E68+i*0x40) and m.rb(0x0E68+i*0x40+0xA)==0x43}
        for i,bx in cur-prev:
            s=min(sensors,key=lambda sx:abs(sx-bx)) if sensors else None
            beams[s]+=1
        prev=cur
        cs={i for i in range(8) if m.rb(0x1428+i*0x40) and m.rb(0x1428+i*0x40+0xA)==0x1C}
        new=cs-prevshots; shots+=len(new); prevshots=cs
        if new: shotx.append(m.rw(P+5))
    print(f'mask {mask:02X}: X reached {m.rw(P+5)}; sensors seen at {sorted(hex(s) for s in sensors)}')
    print('   beams spawned per sensor:',{hex(k):v for k,v in sorted(beams.items())})
    print('   Ray Trap shots (projectile $1C):',shots,' X position at each shot:',shotx)
