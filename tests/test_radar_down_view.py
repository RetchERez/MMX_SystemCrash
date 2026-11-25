"""In-game view of the Eagle control tower: normal, Radar Down, and Radar Down with the pause menu open."""
import sys; sys.path.insert(0,'tools')
from mmx import *
from PIL import Image, ImageDraw
ROM=ROOT/'build/radar_down_test.sfc'; rom=VANILLA.read_bytes(); P=0x0BA8
m=MMX(ROM, rt=ROOT/'build/rt_rdv'); pw=make_password_state(m)
def ww(a,v): m.wb(a,v&0xff); m.wb(a+1,(v>>8)&0xff)
ims=[]
def label(t):
    m.shot('build/t.png'); im=Image.open('build/t.png'); ImageDraw.Draw(im).text((30,212),t,fill=(255,255,0)); ims.append(im)
for mask in (0x00,0x40):
    enter_stage_at_cp(m,5,mask,0,rom,pw); m.frames(30)
    x0,y0=m.rw(P+5),m.rw(P+8)
    # TEST ONLY: open camera borders, then glide X to the girders under the control tower
    for i in range(240):
        ww(0x1E56,0); ww(0x1E58,0x1F00); ww(0x1E5A,0); ww(0x1E5C,0x0700)
        ww(P+5,x0+(1530-x0)*i//240); ww(P+8,y0+(700-y0)*i//240); m.wb(0x0BCF,0x10); m.frames(1)
    for i in range(90):
        ww(0x1E56,0); ww(0x1E58,0x1F00); ww(0x1E5A,0); ww(0x1E5C,0x0700); m.frames(1)
    label(f'{"NORMAL" if mask==0 else "RADAR DOWN"}  X={m.rw(P+5)},{m.rw(P+8)}')
    if mask==0x40:
        m.tap('start',hold=3,settle=40); label('RADAR DOWN, pause menu open')
W=Image.new('RGB',(256*len(ims),224)); [W.paste(s,(256*i,0)) for i,s in enumerate(ims)]; W.save('build/rd_view.png')
