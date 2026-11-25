"""Render the Eagle control tower + booth from the RUNTIME data (WRAM blockMap, map/collision pointers
the game holds at $0B95/$0B92, live VRAM and palette) in normal and Radar Down states."""
import sys, ctypes; sys.path.insert(0,'tools')
from mmx import *
import render_stage as R
from PIL import Image, ImageDraw
ROM=ROOT/'build/radar_down_test.sfc'; rom=VANILLA.read_bytes(); prom=ROM.read_bytes()
def pc(a): return ((a>>16)&0x7F)*0x8000+(a&0x7FFF)
m=MMX(ROM, rt=ROOT/'build/rt_rd'); pw=make_password_state(m)
def render(scenes, out):
    vram=ctypes.string_at(m.fe.lib.retro_get_memory_data(3),0x10000); pal=m.read(0x300,0x200)
    pm=m.rw(0x0B95)|m.rb(0x0B97)<<16; pcl=m.rw(0x0B92)|m.rb(0x0B94)<<16
    bm=m.read(0x7E2000,0x8000)
    cols=[((c&31)*255//31,((c>>5)&31)*255//31,((c>>10)&31)*255//31) for c in (pal[2*i]|pal[2*i+1]<<8 for i in range(128))]
    img=Image.new('RGB',(256*len(scenes),256)); px=img.load(); tc={}
    for si,sc in enumerate(scenes):
        for slot in range(256):
            mi=bm[sc*0x200+slot*2]|bm[sc*0x200+slot*2+1]<<8
            o=pc(pm)+mi*8
            for t in range(4):
                tw=prom[o+2*t]|prom[o+2*t+1]<<8; tn=tw&0x3FF; p=(tw>>10)&7
                if tn not in tc: tc[tn]=R.decode_tile(vram,tn)
                tile=tc[tn]
                ox=si*256+(slot%16)*16+(t&1)*8; oy=(slot//16)*16+(t>>1)*8
                for y in range(8):
                    for x in range(8):
                        sx=7-x if tw&0x4000 else x; sy=7-y if tw&0x8000 else y; v=tile[sy][sx]
                        px[ox+x,oy+y]=cols[p*16+v] if v else (20,20,30)
    img.save(out); return pm,pcl
res={}
for mask in (0x00,0x40):
    enter_stage_at_cp(m,5,mask,0,rom,pw); m.frames(30)
    pm,pcl=render((0x1C,0x1D,0x1E,0x2A),f'build/rd_tower_{mask:02X}.png')
    print(f'mask {mask:02X}: map table ${pm:06X} collision ${pcl:06X}  row0 colours {m.read(0x300,8).hex()}')
a=Image.open('build/rd_tower_00.png'); b=Image.open('build/rd_tower_40.png')
W=Image.new('RGB',(a.width,512)); W.paste(a,(0,0)); W.paste(b,(0,256)); W.resize((a.width//2,256)).save('build/rd_tower_cmp.png')
