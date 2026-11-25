"""Per-stage survey on the user's ROM (vanilla): visible BG1 pixels per palette row at every checkpoint,
and map entries whose tiles carry >= N pixels of given colour indices in a given row.
usage: stage_survey.py <stage> [row idx,idx,.. minpix]"""
import sys, ctypes, collections; sys.path.insert(0,'tools')
from mmx import *
import render_stage as R, dis65 as d
ST=int(sys.argv[1]); rom=VANILLA.read_bytes()
m=MMX(VANILLA, rt=ROOT/f'build/rt_sv{ST}'); pw=make_password_state(m)
ps=d.pc(R.ptr24(rom,0x868D93+ST*3)); pb=d.pc(R.ptr24(rom,0x868E02+ST*3)); pm=d.pc(R.ptr24(rom,0x868E71+ST*3))
rowpix=collections.Counter(); hits=collections.Counter()
want=None
if len(sys.argv)>2:
    want=(int(sys.argv[2]), {int(x) for x in sys.argv[3].split(',')}, int(sys.argv[4]))
for cp in range(3):
    enter_stage_at_cp(m,ST,0,cp,rom,pw); m.frames(30)
    vram=ctypes.string_at(m.fe.lib.retro_get_memory_data(3),0x10000); grid=m.read(0x7EE800,0x400); tc={}
    seen=set()
    for r in range(32):
        for c in range(32):
            sc=grid[r*32+c]
            if not sc: continue
            for i in range(64):
                blk=R.w(rom,ps+sc*0x80+2*i)
                for k in range(4):
                    mi=R.w(rom,pb+blk*8+2*k)
                    cnt=0
                    for t in range(4):
                        tw=R.w(rom,pm+mi*8+2*t); row=(tw>>10)&7; tn=tw&0x3FF
                        if tn not in tc: tc[tn]=R.decode_tile(vram,tn)
                        n=sum(1 for rr in tc[tn] for v in rr if v); rowpix[(cp,row)]+=n
                        if want and row==want[0]: cnt+=sum(1 for rr in tc[tn] for v in rr if v in want[1])
                    if want and cnt>=want[2] and mi not in seen: hits[mi]+=1; seen.add(mi)
for cp in range(3): print('cp',cp,'visible BG1 pixels per row',{r:rowpix[(cp,r)] for r in range(8)})
if want: print('maps with >=',want[2],'pixels of',sorted(want[1]),'in row',want[0],':',sorted(hex(x) for x in hits))
