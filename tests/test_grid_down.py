"""Grid Down emulator checks: palette bank applied only for stage 07 with Mandrill beaten."""
import sys; sys.path.insert(0,'tools')
from mmx import *
from PIL import Image, ImageDraw
import os; ROM=Path(os.environ.get('CR_ROM', ROOT/'build/grid_down_test.sfc')); rom=VANILLA.read_bytes()
m=MMX(ROM, rt=ROOT/'build/runtime_test')
pw=make_password_state(m)   # password screen state from the PATCHED rom
def pal(): return m.read(0x0300,0x200)
res={}; shots=[]
for mask in (0x00,0x20,0xDF,0xFF):
    to_stage_select(m,mask,rom,pw); enter_stage(m,7); m.frames(30)
    res[mask]=pal(); m.shot('build/t.png'); im=Image.open('build/t.png'); ImageDraw.Draw(im).text((30,4),f'mask {mask:02X}',fill=(255,255,0)); shots.append(im)
W=Image.new('RGB',(1024,224)); [W.paste(s,(256*i,0)) for i,s in enumerate(shots)]; W.save('build/test_grid_down_pal.png')
ok_off = res[0x00]==res[0xDF]          # every boss except Mandrill: retail
ok_on  = res[0x20]==res[0xFF] and res[0x20]!=res[0x00]
print('normal (00 vs DF, Mandrill alive) identical:', ok_off)
print('altered (20 vs FF, Mandrill beaten) identical and different from normal:', ok_on)
