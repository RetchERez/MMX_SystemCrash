"""Radar Down live checks: tower view in game, pause-menu palette survival, deck turrets (1 of 2 silent)."""
import sys; sys.path.insert(0,'tools')
from mmx import *
from PIL import Image, ImageDraw
ROM=ROOT/'build/radar_down_test.sfc'; rom=VANILLA.read_bytes(); P=0x0BA8
m=MMX(ROM, rt=ROOT/'build/rt_rdl'); pw=make_password_state(m)
def ww(a,v): m.wb(a,v&0xff); m.wb(a+1,(v>>8)&0xff)
shots=[]
for mask in (0x00,0x40):
    enter_stage_at_cp(m,5,mask,0,rom,pw); m.frames(30)
    row0=m.read(0x300,32)
    # move X toward the control tower (grid row 2, cols 5-7) with the camera border widened (TEST ONLY)
    for f in range(700):
        ww(0x1E58,0x0900); ww(0x1E5A,0x0000)
        m.fe.run_frames(1,['right'] if f%40<30 else ['right','b']); m.wb(0x0BCF,0x10)
    m.shot('build/t.png'); im=Image.open('build/t.png'); ImageDraw.Draw(im).text((30,212),f'mask {mask:02X} X={m.rw(P+5)},{m.rw(P+8)}',fill=(255,255,0)); shots.append(im)
    # pause menu open/close
    m.tap('start',hold=3,settle=60); m.tap('start',hold=3,settle=60)
    print(f'mask {mask:02X}: row0 unchanged across pause: {m.read(0x300,32)==row0}  map ptr ${m.rw(0x0B95)|m.rb(0x0B97)<<16:06X}')
W=Image.new('RGB',(512,224)); [W.paste(s,(256*i,0)) for i,s in enumerate(shots)]; W.save('build/rd_live_tower.png')
# deck turrets at checkpoint 2 (on Death Rogumer)
for mask in (0x00,0x40):
    enter_stage_at_cp(m,5,mask,2,rom,pw); m.frames(30)
    fired={}; prev=set(); turrets={}
    for f in range(1500):
        ww(0x1E58,0x1A00)
        m.fe.run_frames(1,['right'] if f%60<40 else []); m.wb(0x0BCF,0x10)
        for i in range(15):
            b=0x0E68+i*0x40
            if m.rb(b) and m.rb(b+0xA)==0x50: turrets[i]=m.rw(b+5)
        cur={(i,m.rb(0x1428+i*0x40+0xA)) for i in range(8) if m.rb(0x1428+i*0x40)}
        for i,pid in cur-prev:
            if pid==0x13:
                # attribute to nearest turret
                sx=m.rw(0x1428+i*0x40+5)
                if turrets:
                    t=min(turrets.values(),key=lambda tx:abs(tx-sx)); fired[t]=fired.get(t,0)+1
        prev=cur
    print(f'turrets mask {mask:02X}: X reached {m.rw(P+5)}; turret X positions {sorted(set(turrets.values()))}; shots per turret {fired}')
