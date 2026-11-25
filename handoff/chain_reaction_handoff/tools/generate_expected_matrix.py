#!/usr/bin/env python3
"""Generate design oracle, not actual ROM validation."""
import csv, itertools
from pathlib import Path
NAMES=['Launch Octopus','Sting Chameleon','Armored Armadillo','Flame Mammoth','Storm Eagle','Spark Mandrill','Boomer Kuwanger','Chill Penguin']
SOURCE=[2,0,6,7,1,4,5,3] # zero-based source for each target
assert sorted(SOURCE)==list(range(8)) and all(i!=s for i,s in enumerate(SOURCE))
def states(mask): return [(mask>>i)&1 for i in SOURCE]
def main():
    for m,i in itertools.product(range(256),range(8)):
        assert sum(a!=b for a,b in zip(states(m),states(m^(1<<i))))==1
    out=Path(__file__).resolve().parent.parent/'tests'/'expected_256_states.csv'
    with out.open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['mask_hex']+['defeated: '+n for n in NAMES]+['altered: '+n for n in NAMES]);
        for m in range(256): w.writerow([f'{m:02X}']+[(m>>i)&1 for i in range(8)]+states(m))
    print('Generated 256 rows / 2048 expected stage-state selections. Design oracle only.')
if __name__=='__main__': main()
