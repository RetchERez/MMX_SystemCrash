"""Empty Arsenal: silos render empty from runtime data; Mega Tortoise bombs per volley (2 normal, 1 altered);
Kuwanger's Mega Tortoises unaffected (stage-scoped)."""
import sys, os, ctypes; sys.path.insert(0,'tools')
from mmx import *
import render_stage as R
from PIL import Image
ROM=Path(os.environ.get('SC_ROM', ROOT/'build/v10_rc1.sfc')); rom=VANILLA.read_bytes(); prom=ROM.read_bytes(); P=0x0BA8
def pc(a): return ((a>>16)&0x7F)*0x8000+(a&0x7FFF)
m=MMX(ROM, rt=ROOT/'build/rt_ea'); pw=make_password_state(m)
def ww(a,v): m.wb(a,v&0xff); m.wb(a+1,(v>>8)&0xff)
def render_scenes(scenes,out):
    vram=ctypes.string_at(m.fe.lib.retro_get_memory_data(3),0x10000); pal=m.read(0x300,0x200)
    pm=m.rw(0x0B95)|m.rb(0x0B97)<<16; bm=m.read(0x7E2000,0x8000)
    cols=[((c&31)*255//31,((c>>5)&31)*255//31,((c>>10)&31)*255//31) for c in (pal[2*i]|pal[2*i+1]<<8 for i in range(128))]
    img=Image.new('RGB',(256*len(scenes),256)); px=img.load(); tc={}
    for si,sc in enumerate(scenes):
        for slot in range(256):
            mi=bm[sc*0x200+slot*2]|bm[sc*0x200+slot*2+1]<<8; o=pc(pm)+mi*8
            for t in range(4):
                tw=prom[o+2*t]|prom[o+2*t+1]<<8; tn=tw&0x3FF; p=(tw>>10)&7
                if tn not in tc: tc[tn]=R.decode_tile(vram,tn)
                ox=si*256+(slot%16)*16+(t&1)*8; oy=(slot//16)*16+(t>>1)*8
                for y in range(8):
                    for x in range(8):
                        v=tc[tn][7-y if tw&0x8000 else y][7-x if tw&0x4000 else x]
                        px[ox+x,oy+y]=cols[p*16+v] if v else (20,20,30)
    img.save(out)
ims=[]
for mask in (0x00,0x04):
    enter_stage_at_cp(m,1,mask,0,rom,pw); m.frames(30)
    grid=m.read(0x7EE800,0x400); scs=[grid[2*32+c] for c in (12,18,19)]
    render_scenes(scs,f'build/ea_silos_{mask:02X}.png'); ims.append(Image.open(f'build/ea_silos_{mask:02X}.png'))
    # bombs: stand near the start, count projectile $25 spawns and group into volleys
    bombs=[]; prev=set()
    for f in range(1800):
        m.fe.run_frames(1,['right'] if m.rw(P+5)<330 else []); m.wb(0x0BCF,0x10)
        cur={i for i in range(8) if m.rb(0x1428+i*0x40) and m.rb(0x1428+i*0x40+0xA)==0x25}
        for i in cur-prev: bombs.append(f)
        prev=cur
    vol=[]; 
    for t in bombs:
        if vol and t-vol[-1][-1]<20: vol[-1].append(t)
        else: vol.append([t])
    print(f'Octopus mask {mask:02X}: bombs={len(bombs)} volleys={len(vol)} bombs per volley={[len(v) for v in vol]}  map ptr ${m.rw(0x0B95)|m.rb(0x0B97)<<16:06X}')
W=Image.new('RGB',(ims[0].width,512)); W.paste(ims[0],(0,0)); W.paste(ims[1],(0,256)); W.resize((W.width//2,256)).save('build/ea_silos_cmp.png')
# Kuwanger tortoises with both Grid Down and Armadillo beaten: must still fire two per volley (stage-scoped)
