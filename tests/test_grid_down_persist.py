"""Persistence: Grid Down palette at every checkpoint, after death/respawn; vanilla parity when Mandrill alive."""
import sys; sys.path.insert(0,'tools')
from mmx import *
rom=VANILLA.read_bytes()
def pal(m): return m.read(0x0300,0x200)
vm=MMX(VANILLA, rt=ROOT/'build/rt_persist_v'); make_password_state(vm); vpw=vm.save()
vpal={}
for cp in range(3):
    enter_stage_at_cp(vm,7,0x00,cp,rom,vpw); vm.frames(30); vpal[cp]=pal(vm)
vm.close()
pm=MMX(Path(__import__('os').environ.get('CR_ROM', ROOT/'build/grid_down_test.sfc')), rt=ROOT/'build/rt_persist_p'); make_password_state(pm); ppw=pm.save()
ok=True
for cp in range(3):
    v=vpal[cp]
    enter_stage_at_cp(pm,7,0x00,cp,rom,ppw); pm.frames(30); pn=pal(pm)
    enter_stage_at_cp(pm,7,0x20,cp,rom,ppw); pm.frames(30); pa=pal(pm)
    print(f'cp{cp}: normal==vanilla {pn==v}  altered!=normal {pa!=pn}  1F0A={pm.rb(0x1F0A)}'); ok &= (pn==v) and (pa!=pn)
    if cp==0: alt_cp0=pa
# death + respawn in altered state: HP 1, Turn Cannon spawned on X (contact damage)
P=0x0BA8
def ww(a,v): pm.wb(a,v&0xff); pm.wb(a+1,(v>>8)&0xff)
enter_stage_at_cp(pm,7,0x20,0,rom,ppw); pm.frames(30)
lives=pm.rb(0x1F80); pm.wb(0x0BCF,1)
b=0x0E68+14*0x40
for k in range(0x40): pm.wb(b+k,0)
pm.wb(b,1); pm.wb(b+0xA,0x17); pm.wb(b+0xB,1); ww(b+5,pm.rw(P+5)); ww(b+8,pm.rw(P+8)-8)
died=False
for f in range(3000):
    pm.frames(1)
    if pm.rb(0x1F80)!=lives: died=True
    if died and f>400 and pm.rb(0xD2)==4 and pm.rb(0xD3) in (4,6): break
pm.frames(60)
after=pal(pm)
print('death: lives',lives,'->',pm.rb(0x1F80),' respawned palette altered:',after==alt_cp0)
ok &= died and after==alt_cp0
print('PERSISTENCE', 'PASS' if ok else 'FAIL')
