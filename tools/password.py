#!/usr/bin/env python3
"""MMX (USA Rev 1) password encoder/decoder, ported from $80:F18C..$80:F31F.

The password routines run with DB=$86, DP=$1E48, so the tables are $86:BD24
(5x12 bit masks) and $86:BD6F (12x8 digit permutation). Tables are read from
the user's ROM at runtime; nothing from the ROM is stored here.

Decoded fields (from $80:F234..$80:F2A7):
  b24 -> $1F99 (high nibble: Sub Tanks $1F83..), b25 -> $1F9C (Heart Tanks),
  b26 -> boss mask: bit7 Penguin($1F96) bit6 Kuwanger bit5 Mandrill bit4 Eagle
         bit3 Mammoth bit2 Armadillo bit1 Chameleon bit0 Octopus($1F88)
  b27 bit0 -> $1F7E=$80, bit4 -> $1F9B (intro stage cleared); high nibble = XOR key
Digits are the cell values stored at $1E60..$1E6B (0..7; shown on screen as 1..8).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dis65 as d

def tables(rom):
    bd24 = rom[d.pc(0x86BD24):d.pc(0x86BD24) + 60]
    bd6f = rom[d.pc(0x86BD6F):d.pc(0x86BD6F) + 96]
    return bd24, bd6f

def _bitmap(bd24):
    """for digit position x, list of (byte_index, mask) consumed MSB-first"""
    out = []
    for x in range(12):
        out.append([(y, bd24[y * 12 + x]) for y in range(5) if bd24[y * 12 + x]])
        assert len(out[-1]) == 3, (x, out[-1])
    return out

def parity(v):
    return bin(v).count('1') & 1

def decode(rom, cells):
    bd24, bd6f = tables(rom)
    bm = _bitmap(bd24)
    b = [0] * 6
    for x in range(12):
        idx = [y for y in range(8) if bd6f[x * 8 + y] == cells[x]]
        assert len(idx) == 1
        v = idx[-1]
        for k, (y, mask) in enumerate(bm[x]):
            if v & (4 >> k):
                b[y] |= mask
    key = (b[3] & 0xF0) | (b[3] >> 4)
    b[0] ^= key; b[1] ^= key; b[2] ^= key
    ok = True
    if not (b[3] & 0x10) and (b[0] or b[1] or b[2]):
        ok = False
    x = b[0] ^ b[1] ^ b[2] ^ b[3]
    if ((x >> 4) ^ x) & 0xF != b[4]:
        ok = False
    for byte, bit in ((b[0], 3), (b[1], 2), (b[2], 1)):
        if parity(byte) != (b[3] >> bit) & 1:
            ok = False
    return ok, b[:5]

def encode(rom, bosses, hearts=0, subtanks_armor=0, extra_bit0=0, key=0x1):
    bd24, bd6f = tables(rom)
    bm = _bitmap(bd24)
    b24, b25, b26 = subtanks_armor & 0xff, hearts & 0xff, bosses & 0xff
    b27 = ((key & 0xF) << 4) | 0x10 | (parity(b24) << 3) | (parity(b25) << 2) | (parity(b26) << 1) | (extra_bit0 & 1)
    chk = b24 ^ b25 ^ b26 ^ b27
    b28 = ((chk >> 4) ^ chk) & 0xF
    k = (b27 & 0xF0) | (b27 >> 4)
    raw = [b24 ^ k, b25 ^ k, b26 ^ k, b27, b28]
    cells = []
    for x in range(12):
        v = 0
        for n, (y, mask) in enumerate(bm[x]):
            if raw[y] & mask:
                v |= 4 >> n
        cells.append(bd6f[x * 8 + v])
    ok, dec = decode(rom, cells)
    assert ok and dec[2] == b26 and dec[3] == b27, (cells, dec)
    return cells

if __name__ == '__main__':
    rom = Path(sys.argv[1]).read_bytes()
    for mask in (0x00, 0x08, 0x80, 0xFF):
        c = encode(rom, mask)
        print(f'{mask:02X}', ''.join(str(v + 1) for v in c), decode(rom, c))
