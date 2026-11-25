"""Render a full MMX stage map (BG1 layer) from ROM level data + live VRAM/palette.

Format (from MegaED X source, X1): layout grid in WRAM $7E:E800 (32 screens/row),
scene = 8x8 block words (0x80 bytes), block = 4 map words (8 bytes),
map = 4 SNES tilemap words (TL,TR,BL,BR), collision = 1 byte per map.
Pointer tables (24-bit, stage*3): scenes $86:8D93, blocks $86:8E02, maps $86:8E71,
collision $86:8EE0. Tiles from VRAM (char base 0), palettes from WRAM $0300.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dis65 as d


def ptr24(rom, a):
    o = d.pc(a)
    return rom[o] | rom[o + 1] << 8 | rom[o + 2] << 16


def w(rom, off):
    return rom[off] | rom[off + 1] << 8


def decode_tile(vram, n):
    base = 0x2000 + (n & 0x3FF) * 32  # BG char base verified against live frame
    px = []
    for y in range(8):
        b0, b1, b2, b3 = vram[(base + 2 * y) & 0xFFFF], vram[(base + 2 * y + 1) & 0xFFFF], vram[(base + 16 + 2 * y) & 0xFFFF], vram[(base + 17 + 2 * y) & 0xFFFF]
        row = []
        for x in range(8):
            s = 7 - x
            row.append(((b0 >> s) & 1) | ((b1 >> s) & 1) << 1 | ((b2 >> s) & 1) << 2 | ((b3 >> s) & 1) << 3)
        px.append(row)
    return px


def render(rom, stage, grid, vram, pal, out, collision_overlay=False, scale=1, labels=True):
    ps = d.pc(ptr24(rom, 0x868D93 + stage * 3))
    pb = d.pc(ptr24(rom, 0x868E02 + stage * 3))
    pm = d.pc(ptr24(rom, 0x868E71 + stage * 3))
    pcol = d.pc(ptr24(rom, 0x868EE0 + stage * 3))
    cols = [((c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31) for c in
            (pal[2 * i] | pal[2 * i + 1] << 8 for i in range(128))]
    rows_used = [r for r in range(32) if any(grid[r * 32:r * 32 + 32])]
    cols_used = [c for c in range(32) if any(grid[r * 32 + c] for r in range(32))]
    if not rows_used:
        return None
    r0, r1, c0, c1 = min(rows_used), max(rows_used), min(cols_used), max(cols_used)
    W, H = (c1 - c0 + 1) * 256, (r1 - r0 + 1) * 256
    img = Image.new('RGB', (W, H), (0, 0, 0))
    px = img.load()
    tcache, mcache = {}, {}
    draw = ImageDraw.Draw(img)

    def map_img(mi):
        if mi in mcache:
            return mcache[mi]
        tile_words = [w(rom, pm + mi * 8 + 2 * k) for k in range(4)]
        m = [[(0, 0, 0)] * 16 for _ in range(16)]
        for k, tw in enumerate(tile_words):
            tn = tw & 0x3FF; p = (tw >> 10) & 7; hf = tw & 0x4000; vf = tw & 0x8000
            if tn not in tcache:
                tcache[tn] = decode_tile(vram, tn)
            t = tcache[tn]
            ox, oy = (k & 1) * 8, (k >> 1) * 8
            for y in range(8):
                for x in range(8):
                    sx = 7 - x if hf else x; sy = 7 - y if vf else y
                    v = t[sy][sx]
                    m[oy + y][ox + x] = cols[p * 16 + v] if v else (20, 20, 30)
        mcache[mi] = m
        return m

    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            sc = grid[r * 32 + c]
            if not sc:
                continue
            sx0, sy0 = (c - c0) * 256, (r - r0) * 256
            for by in range(8):
                for bx in range(8):
                    blk = w(rom, ps + sc * 0x80 + by * 0x10 + bx * 2)
                    for k in range(4):
                        mi = w(rom, pb + blk * 8 + 2 * k)
                        m = map_img(mi)
                        ox = sx0 + bx * 32 + (k & 1) * 16; oy = sy0 + by * 32 + (k >> 1) * 16
                        for y in range(16):
                            row = m[y]
                            for x in range(16):
                                px[ox + x, oy + y] = row[x]
                        if collision_overlay:
                            cv = rom[pcol + mi]
                            if cv:
                                draw.text((ox + 2, oy + 2), f'{cv:02X}', fill=(255, 0, 255))
            if labels:
                draw.rectangle([sx0, sy0, sx0 + 255, sy0 + 255], outline=(255, 255, 0))
                draw.text((sx0 + 4, sy0 + 4), f'r{r}c{c} s{sc:02X}', fill=(255, 255, 0))
    if scale != 1:
        img = img.resize((int(W * scale), int(H * scale)))
    img.save(out)
    return (r0, c0, W, H)
