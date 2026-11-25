"""Normal-state parity: identical inputs on vanilla and patched ROM (Mandrill alive) must give identical WRAM.
Compares all 128 KiB of WRAM every 30 frames through the Kuwanger trap hall, excluding two documented
expected differences: the stack zone $0100-$02FF (hooks push a little deeper; an interrupt inside a hook leaves
different residue below the stack pointer - observed only at $0117-$0135 and $02FD) and $7E:FFBC-FFBF
(boot-time copy of the ROM header checksum, which differs for any patched ROM)."""
import sys, hashlib; sys.path.insert(0,'tools')
from mmx import *
rom=VANILLA.read_bytes(); P=0x0BA8
def run(path,tag,mask,stage=7):
    m=MMX(path, rt=ROOT/f'build/rt_parity_{tag}'); make_password_state(m); pw=m.save()
    def ww(a,v): m.wb(a,v&0xff); m.wb(a+1,(v>>8)&0xff)
    to_stage_select(m,mask,rom,pw); enter_stage(m,stage); m.frames(20)
    for y in range(6040,5180,-16): ww(P+5,200); ww(P+8,y); m.wb(0x0BCF,0x10); m.frames(2)
    for x in range(200,300,4): ww(P+5,x); ww(P+8,5180); m.frames(2)
    snaps=[]
    for f in range(900):
        ww(0x1E58,0x0700); m.fe.run_frames(1,['right'] if f%90<70 else ['right','b']); m.wb(0x0BCF,0x10)
        if f%30==0:
            w=bytearray(m.read(0,0x20000)); w[0x100:0x300]=bytes(0x200); w[0xFFBC:0xFFC0]=bytes(4)
            snaps.append(hashlib.sha1(w).hexdigest())
    m.close(); return snaps
for stage,mask in ((7,0x00),(7,0xDF),(5,0x00),(5,0xBF),(1,0x00),(1,0xFB),(3,0x00),(3,0xFD),(8,0x00),(8,0xF7)):
    v=run(VANILLA,'v',mask,stage); p=run(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build/grid_down_test.sfc','p',mask,stage)
    first=next((i for i,(a,b) in enumerate(zip(v,p)) if a!=b),None)
    print(f'stage {stage} mask {mask:02X}: {len(v)} WRAM snapshots, identical={v==p}, first difference at snapshot {first}')
