"""Turn Cannon gating unit test: spawn actor $17 into a free enemy slot near X and let the game run it.
Expect: fires in Kuwanger normal, silent in Grid Down; always fires in Mandrill (gate is stage-scoped)."""
import sys; sys.path.insert(0,'tools')
from mmx import *
import os; ROM=Path(os.environ.get('CR_ROM', ROOT/'build/grid_down_test.sfc')); rom=VANILLA.read_bytes()
m=MMX(ROM, rt=ROOT/'build/runtime_test'); pw=make_password_state(m); P=0x0BA8
def ww(a,v): m.wb(a,v&0xff); m.wb(a+1,(v>>8)&0xff)
def spawn(aid,sub,dx,dy):
    for i in range(14,0,-1):
        b=0x0E68+i*0x40
        if not m.rb(b):
            for k in range(0x40): m.wb(b+k,0)
            m.wb(b,1); m.wb(b+0xA,aid); m.wb(b+0xB,sub)
            ww(b+5,m.rw(P+5)+dx); ww(b+8,m.rw(P+8)+dy)
            return i
def run(stage,mask):
    enter_stage(m,stage,1200) if False else None
    to_stage_select(m,mask,rom,pw); enter_stage(m,stage); m.frames(30)
    slot=spawn(0x17,0x01,-80,-8)
    shots=0; prev=set(); alive=0
    for f in range(600):
        m.frames(1); m.wb(0x0BCF,0x10)
        b=0x0E68+slot*0x40
        if m.rb(b) and m.rb(b+0xA)==0x17: alive+=1
        cur={i for i in range(8) if m.rb(0x1428+i*0x40)}
        shots+=len(cur-prev); prev=cur
    return alive,shots
for stage,mask,label in [(7,0x00,'Kuwanger normal'),(7,0x20,'Kuwanger Grid Down'),(6,0x00,'Mandrill, Mandrill alive'),(6,0xFF,'Mandrill, all beaten')]:
    a,s=run(stage,mask); print(f'{label:28s} cannon alive frames={a:4d} new enemy shots={s}',flush=True)
