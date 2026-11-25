#!/usr/bin/env python3
"""Package CHAIN REACTION v1.0.
  python tools/release.py
1. rebuild from source (tools/build.py --name chain_reaction_v1.0), BPS roundtrip checked there
2. player ZIP: BPS + readme.txt (no ROM)
3. development ZIP: src/, tools/*.py, tests/, BUILD.md, docs/*.md, QA logs + matrix results
   (no ROM bytes, no build/gen data, no save states, no screenshots or renders: those derive from the ROM)
"""
import hashlib, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = ROOT / 'release'
NAME = 'chain_reaction_v1.0'


def sha1(p):
    return hashlib.sha1(Path(p).read_bytes()).hexdigest()


def main():
    r = subprocess.run([sys.executable, str(ROOT / 'tools/build.py'), '--name', NAME], capture_output=True, text=True)
    print(r.stdout[-600:], r.stderr[-600:])
    if r.returncode != 0 or 'BPS roundtrip: OK' not in r.stdout:
        sys.exit('STOP: build or roundtrip failed')
    bps = ROOT / 'build' / f'{NAME}.bps'
    v = REL / 'v1.0'
    (v / f'{NAME}.bps').write_bytes(bps.read_bytes())
    player = REL / 'MegaManX_ChainReaction_v1.0.zip'
    with zipfile.ZipFile(player, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(v / f'{NAME}.bps', f'{NAME}.bps')
        z.write(v / 'readme.txt', 'readme.txt')
    dev = REL / 'MegaManX_ChainReaction_v1.0_dev.zip'
    with zipfile.ZipFile(dev, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((ROOT / 'src').glob('*.asm')):
            z.write(p, f'src/{p.name}')
        for p in sorted((ROOT / 'tools').glob('*.py')):
            z.write(p, f'tools/{p.name}')
        for p in sorted((ROOT / 'tests').glob('*')):
            if p.suffix in ('.py', '.sh'):
                z.write(p, f'tests/{p.name}')
        for p in [ROOT / 'BUILD.md'] + sorted((ROOT / 'docs').glob('*.md')):
            z.write(p, f'docs/{p.name}' if p.parent.name == 'docs' else p.name)
        for p in sorted((ROOT / 'build/qa').glob('*.log')) + sorted((ROOT / 'build/matrix').glob('*.json')):
            z.write(p, f'qa/{p.name}')
    for p in (player, dev):
        with zipfile.ZipFile(p) as z:
            names = z.namelist()
            assert not any(n.lower().endswith(('.sfc', '.smc', '.state', '.png', '.bin')) for n in names), names
        print(p.name, p.stat().st_size, 'bytes', len(names), 'files', 'sha1', sha1(p))
    print('BPS sha1', sha1(bps), bps.stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
