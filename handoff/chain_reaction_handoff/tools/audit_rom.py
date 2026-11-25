#!/usr/bin/env python3
"""Read-only X1 Rev 1 ROM audit; no ROM bytes written to output."""
import argparse, csv, hashlib, json, struct, zlib, zipfile
from pathlib import Path
EXPECTED={'crc32':'DED53C64','md5':'DF1CC0C8C8C4B61E3B834CC03366611C','sha1':'C65216760BA99178100A10D98457CF11496C2097','sha256':'B8F70A6E7FB93819F79693578887E2C11E196BDF1AC6DDC7CB924B1AD0BE2D32'}
STAGES=['Highway','Launch Octopus','Sting Chameleon','Armored Armadillo','Flame Mammoth','Storm Eagle','Spark Mandrill','Boomer Kuwanger','Chill Penguin','Sigma 1','Sigma 2','Sigma 3','Sigma 4']
NATIVE={'Penguin':[0x3c72,0x3509,0x17a38,0x218a2,0x39e97,0x3bd76],'Eagle':[0x3c84,0x34fd,0xb4cd,0xb4f0,0x17a2c,0x2311b,0x3fced,0x3f6de,0x3f66d,0x3f715],'Octopus':[0x3c96]}
ACTORS={0x03:'Thunder Slimer',0x20:'Amenhopper',0x2b:'Minecart',0x2c:'Mole Borer',0x44:'Ray Trap',0x49:'Sky Claw',0x50:'Death Rogumer cannon',0x57:'Bunker',0x59:'Lift Cannon',0x5b:'Mega Tortoise'}
def pc(addr):
    assert addr & 0x8000
    return ((addr>>16)&0x7f)*0x8000+(addr&0x7fff)
def read_rom(path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            names=[n for n in z.namelist() if not n.endswith('/') and Path(n).suffix.lower() in ('.sfc','.smc','.fig','.bin')]
            if len(names)!=1: raise ValueError(f'Expected one ROM in ZIP, found {names}')
            raw=z.read(names[0])
    else: raw=path.read_bytes()
    header=512 if len(raw)==0x180200 else 0
    return raw[header:], header

def parse_events(rom, stage):
    ptr=struct.unpack_from('<H',rom,pc(0x8582c2)+stage*2)[0]
    if ptr<0x8000: raise ValueError(f'invalid stage {stage} pointer {ptr:04X}')
    pos=pc(0x850000|ptr); start=pos; prev=255; rows=[]
    block=rom[pos]; pos+=1
    while prev!=block:
        if len(rows)>2048 or pos>=min(start+0x2000,pc(0x85ffff)+1): raise ValueError('unterminated event stream')
        prev=block
        while True:
            if pos+7>min(start+0x2000,pc(0x85ffff)+1): raise ValueError('record beyond expected bounds')
            t,y,actor,sub,xf=struct.unpack_from('<BHBBH',rom,pos)
            rows.append([stage,STAGES[stage],f'{pos:06X}',block,t&3,t>>2,y,f'{actor:02X}',f'{sub:02X}',xf&0x1fff,xf>>13,ACTORS.get(actor,'') if t&3==3 else ''])
            pos+=7
            if xf&0x8000: break
        block=rom[pos]; pos+=1
    return rows, {'stage':stage,'pointer':f'85:{ptr:04X}','length':pos-start,'records':len(rows)}

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('rom',type=Path); ap.add_argument('--out',type=Path,default=Path('audit_output')); a=ap.parse_args()
    rom,header=read_rom(a.rom)
    hashes={'crc32':f'{zlib.crc32(rom):08X}',**{n:hashlib.new(n,rom).hexdigest().upper() for n in ['md5','sha1','sha256']}}
    print('Header removed:',header,'Normalized bytes:',len(rom)); print(json.dumps(hashes,indent=2))
    if len(rom)!=0x180000 or hashes!=EXPECTED: raise SystemExit('STOP: source does not match expected USA Rev 1; investigate locally before edits.')
    a.out.mkdir(parents=True,exist_ok=True)
    result={'source_size':len(rom),'copier_header_bytes':header,'hashes':hashes,'revision_byte':rom[0x7fdb],'event_streams':[],'native_check_operands':{},'event_parse_errors':[]}
    for boss,offs in NATIVE.items():
        result['native_check_operands'][boss]=[{'pc':f'{o:06X}','byte':f'{rom[o]:02X}'} for o in offs]
    rows=[]
    for stage in range(len(STAGES)):
        try:
            r,meta=parse_events(rom,stage); rows+=r; result['event_streams'].append(meta)
        except (ValueError,IndexError,struct.error) as ex: result['event_parse_errors'].append({'stage':stage,'error':str(ex)})
    (a.out/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    with (a.out/'events.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['stage_id','stage','pc_offset','block','type','match','y','actor_id_hex','sub_id_hex','x','flags','candidate_actor_name']); w.writerows(rows)
    print('Audit written:',a.out,'Event records:',len(rows),'Parse errors:',len(result['event_parse_errors']))
    if result['event_parse_errors']: raise SystemExit('Inspect event parser failures before relying on exported data.')
if __name__=='__main__': main()
