"""Stage-select label for SYSTEM CRASH: OFFLINE in the green of the stage select's STAGE/MAP/SPEC panels.
A 32x8 strip (four 8x8 sprites, tiles $C0-$C3, OBJ palette 7): navy panel background, 3x5 letters in the panels'
bright green with their dark green as a drop shadow."""
PAL = [(0, 0, 0), (25, 40, 58), (115, 223, 115), (41, 113, 41)] + [(0, 0, 0)] * 12
GLYPH = {
    'O': ["111", "101", "101", "101", "111"],
    'F': ["111", "100", "111", "100", "100"],
    'L': ["100", "100", "100", "100", "111"],
    'I': ["111", "010", "010", "010", "111"],
    'N': ["1001", "1101", "1011", "1001", "1001"],
    'E': ["111", "100", "111", "100", "111"],
}
WORD = 'OFFLINE'
W, H = 32, 8


def pixels():
    g = [[1] * W for _ in range(7)] + [[0] * W]            # navy strip, 7 rows; row 8 transparent
    lit = set()
    x = (W - (sum(len(GLYPH[c][0]) for c in WORD) + len(WORD) - 1)) // 2
    for c in WORD:
        for r, row in enumerate(GLYPH[c]):
            for dx, v in enumerate(row):
                if v == '1': lit.add((x + dx, 1 + r))
        x += len(GLYPH[c][0]) + 1
    for (x, y) in lit:
        if (x + 1, y + 1) not in lit and y + 1 < 7: g[y + 1][x + 1] = 3
    for (x, y) in lit: g[y][x] = 2
    return g


def to_bgr15(rgb):
    r, g, b = (v >> 3 for v in rgb); return r | g << 5 | b << 10


def palette_bytes():
    return b''.join(to_bgr15(c).to_bytes(2, 'little') for c in PAL)


def tile4bpp(px, tx, ty):
    out = bytearray(32)
    for r in range(8):
        row = px[ty * 8 + r][tx * 8: tx * 8 + 8]
        for bit in range(4):
            v = 0
            for c in range(8): v |= ((row[c] >> bit) & 1) << (7 - c)
            out[(bit // 2) * 16 + r * 2 + (bit & 1)] = v
    return bytes(out)


def tiles():
    """tiles $C0-$C3 in order: one 128-byte upload"""
    px = pixels(); return b''.join(tile4bpp(px, t, 0) for t in range(4))


def preview(path, scale=8):
    from PIL import Image
    im = Image.new('RGBA', (W, H))
    for y, row in enumerate(pixels()):
        for x, v in enumerate(row):
            if v: im.putpixel((x, y), PAL[v] + (255,))
    im.resize((W * scale, H * scale), Image.NEAREST).save(path)


if __name__ == '__main__':
    preview('art/badge_preview.png')
