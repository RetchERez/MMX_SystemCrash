"""SYSTEM CRASH title subtitle: bold italic letters in the gold gradient of the title logo's X, dark outline.
Strip 112x16 = seven 16x16 sprites (OBJ palette 7). Colours sampled from the title screen's X."""
GRAD = [(255, 255, 165), (255, 239, 132), (247, 223, 58), (239, 198, 0), (230, 174, 0),
        (222, 142, 0), (206, 113, 0), (181, 105, 0), (156, 89, 0), (123, 73, 0)]   # rows 0-9, top to bottom
OUTLINE = (57, 33, 0)
PAL = [(0, 0, 0), OUTLINE] + GRAD + [(0, 0, 0)] * 4
G = {
    'S': [".######.", "##....##", "##......", "##......", ".######.", "......##", "......##", "##....##", "##....##", ".######."],
    'Y': ["##....##", "##....##", "##....##", ".##..##.", "..####..", "...##...", "...##...", "...##...", "...##...", "...##..."],
    'T': ["########", "########", "...##...", "...##...", "...##...", "...##...", "...##...", "...##...", "...##...", "...##..."],
    'E': ["########", "##......", "##......", "##......", "#######.", "##......", "##......", "##......", "##......", "########"],
    'M': ["##....##", "###..###", "########", "##.##.##", "##.##.##", "##....##", "##....##", "##....##", "##....##", "##....##"],
    'C': [".######.", "##....##", "##......", "##......", "##......", "##......", "##......", "##......", "##....##", ".######."],
    'R': ["#######.", "##....##", "##....##", "##....##", "#######.", "##..##..", "##...##.", "##...##.", "##....##", "##....##"],
    'A': ["..####..", ".##..##.", "##....##", "##....##", "##....##", "########", "##....##", "##....##", "##....##", "##....##"],
    'H': ["##....##"] * 4 + ["########"] + ["##....##"] * 5,
}
WORD = 'SYSTEM CRASH'
W, H = 112, 16
SHEAR = [3, 3, 2, 2, 2, 1, 1, 1, 0, 0]   # italic, like the logo


def pixels():
    lit = {}
    x = 0
    for ch in WORD:
        if ch == ' ':
            x += 5; continue
        for r, row in enumerate(G[ch]):
            for c, v in enumerate(row):
                if v == '#': lit[(x + c + SHEAR[r], r)] = 2 + r
        x += 9
    width = max(p[0] for p in lit) + 1
    ox, oy = (W - width - 2) // 2 + 1, 3          # centred, room for the outline
    g = [[0] * W for _ in range(H)]
    for (px, py), col in lit.items():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                X, Y = px + ox + dx, py + oy + dy
                if 0 <= X < W and 0 <= Y < H and g[Y][X] == 0: g[Y][X] = 1
    for (px, py), col in lit.items(): g[py + oy][px + ox] = col
    return g


def to_bgr15(rgb):
    r, g_, b = (v >> 3 for v in rgb); return r | g_ << 5 | b << 10


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
    """top tile row (14 tiles) then bottom tile row (14 tiles): uploads to tiles n.. and n+16.."""
    px = pixels()
    return b''.join(tile4bpp(px, t, 0) for t in range(14)), b''.join(tile4bpp(px, t, 1) for t in range(14))


def image(scale=1):
    from PIL import Image
    im = Image.new('RGBA', (W, H))
    for y, row in enumerate(pixels()):
        for x, v in enumerate(row):
            if v: im.putpixel((x, y), PAL[v] + (255,))
    return im.resize((W * scale, H * scale), Image.NEAREST)


if __name__ == '__main__':
    image(8).save('art/title_preview.png')
