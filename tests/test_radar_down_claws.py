"""Sky Claws: normal = all move; Radar Down = claws whose spawn X is in the dead list never move, the rest move."""
import sys, os; sys.path.insert(0,'tools')
from mmx import *
ROM=Path(os.environ.get('SC_ROM', ROOT/'build/test02b.sfc')); rom=VANILLA.read_bytes(); P=0x0BA8
_g=open(ROOT/'build/gen/halves.asm').read().split('SC_SkyClawDead:')[1].split(chr(10))[1]
DEAD={int(v.strip().strip('$'),16) for v in _g.replace('dw','').split(',') if v.strip()!='$FFFF'}
m=MMX(ROM, rt=ROOT/'build/rt_claw'); pw=make_password_state(m)
def ww(a,v): m.wb(a,v&0xff); m.wb(a+1,(v>>8)&0xff)
for mask in (0x00,0x40):
    enter_stage_at_cp(m,5,mask,0,rom,pw); m.frames(30)
    claws={}   # spawn X -> max displacement
    y0=m.rw(P+8); x=m.rw(P+5)
    for f in range(1400):
        # TEST ONLY: glide X along the start level (camera borders opened) so every early claw reacts
        ww(0x1E56,0); ww(0x1E58,0x1F00); ww(0x1E5A,0); ww(0x1E5C,0x0700)
        if f%3==0 and x<800: x+=1
        ww(P+5,x); ww(P+8,y0); m.frames(1); m.wb(0x0BCF,0x10)
        for i in range(15):
            b=0x0E68+i*0x40
            if m.rb(b) and m.rb(b+0xA)==0x49 and m.rb(b+1)>=2:
                sx=m.rw(b+0x37); d=abs(m.rw(b+5)-sx)+abs(m.rw(b+8)-m.rw(b+0x39) if False else 0)
                claws.setdefault(sx,[0,m.rw(b+8)])
                claws[sx][0]=max(claws[sx][0],abs(m.rw(b+5)-sx)); claws[sx][1]=min(claws[sx][1],m.rw(b+8))
    print(f'mask {mask:02X}: X reached {m.rw(P+5)}')
    for sx,(dx,miny) in sorted(claws.items()):
        print(f'   claw spawn x={sx:5d} {"DEAD-LISTED" if sx in DEAD else "live-listed"}  max horizontal travel={dx}')
