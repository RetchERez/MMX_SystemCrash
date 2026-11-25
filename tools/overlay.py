import csv,json,re,sys
from PIL import Image, ImageDraw
src=open('research_repos/sharivan_XSharp/ROMExporter/MegaEDX/MMXCoreLoader.cs').read()
names={int(a,16):b.replace('enemy_','').replace('boss_','BOSS ') for a,b in re.findall(r'case 0x([0-9A-F]{2})(?: when Type == 0)?:\s*writer\.AddEntity\("([a-z0-9_]+)"',src[src.find('case 0x03:\n'):])}
items={4:'1UP',5:'SUBTANK',7:'door',0x0B:'HEART'}
grids=json.load(open('build/grids_normal.json'))
rows=list(csv.DictReader(open('audit_output/events.csv')))
NM={1:'Octopus',2:'Chameleon',3:'Armadillo',4:'Mammoth',5:'Eagle',6:'Mandrill',7:'Kuwanger',8:'Penguin'}
for st in range(1,9):
    g=grids[str(st)]; rs=[r for r,h in g]
    cols=[c for r,h in g for c,v in enumerate(h.split()) if v!='00']
    r0,c0=min(rs),min(cols)
    for cp in range(3):
        im=Image.open(f'build/maps/{NM[st]}_normal_cp{cp}.png').convert('RGB'); dr=ImageDraw.Draw(im); s=0.5
        for r in rows:
            if r['stage_id']!=str(st): continue
            t=int(r['type']); a=int(r['actor_id_hex'],16)
            x=(int(r['x'])-c0*256)*s; y=(int(r['y'])-r0*256)*s
            if t==3: col=(255,80,80); lab=names.get(a,f'{a:02X}')
            elif t==0 and a in items: col=(80,255,80); lab=items[a]
            elif t==2 and a==0x0B: col=(80,160,255); lab='CHECKPOINT'
            else: continue
            dr.ellipse([x-4,y-4,x+4,y+4],outline=col,width=2); dr.text((x+5,y-6),lab,fill=col)
        im.save(f'build/maps/{NM[st]}_annot_cp{cp}.png')
    print(st,im.size)
