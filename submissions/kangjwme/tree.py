import sys, time

W, H, CX, TOP, ROWS, N = 60, 25, 30, 3, 14, 30
TW = ["    .##", "   ####", "   ####", "  #####", "  #####", "  ####.", "  ###", "  ##", "   #"]
ORN = [91, 93, 94, 95, 96]

def h(a, b):
    return ((((a * 73856093 ^ b * 19349663) & 0xFFFFFFFF) * 1103515245 + 12345) & 0x7FFFFFFF) >> 8

def lcg(s):
    return (s * 1103515245 + 12345) & 0x7FFFFFFF

flakes, s = [], 2025
for _ in range(46):
    v = []
    for _ in range(3):
        s = lcg(s)
        v.append(s >> 8)
    flakes.append((v[0] % W, v[1] % H, 1 + v[2] % 2))

def text(g, y, t, col):
    x = CX - sum(1 + (ord(c) > 0x2E80) for c in t) // 2
    g[y] = [(" ", 0)] * W
    for c in t:
        g[y][x] = (c, col)
        x += 1
        if ord(c) > 0x2E80:
            g[y][x] = ("", col)
            x += 1

def frame(f):
    g = [[(" ", 0)] * W for _ in range(H)]
    for x, y, sp in flakes:
        g[(y + f * sp) % H][(x + f // 3 * (1 if sp == 1 else -1)) % W] = ("*." [sp == 1], 97)
    for r in range(min(ROWS, f + 1)):
        for i in range(2 * r + 1):
            k = h(r, i)
            if i in (0, 2 * r):
                c = ("/\\"[i > 0], 32)
            elif r > 1 and k % 6 == 0:
                c = ("o", ORN[(k + f // 2) % 5])
            elif r > 1 and k % 11 == 1 and (f + k) % 4 < 2:
                c = ("+", 93)
            else:
                c = ("^", 92 if r % 2 else 32)
            g[TOP + r][CX - r + i] = c
    if f >= ROWS:
        for k, row in enumerate(TW):
            for j, c in enumerate(row):
                if c != " ":
                    g[TOP + 5 + k][CX - 3 + j] = (c, 93 if c == "#" else 91)
        g[TOP - 1][CX] = ("*+"[f % 2], 93)
        for j in range(3):
            for i in (-1, 0, 1):
                g[TOP + ROWS + j][CX + i] = ("|", 33)
        for i in range(-12, 13):
            g[TOP + ROWS + 3][CX + i] = ("~", 97)
        for i, col in ((-9, 91), (-6, 94), (6, 95), (9, 93)):
            g[TOP + ROWS + 2][CX + i] = g[TOP + ROWS + 2][CX + i + 1] = ("#", col)
    if f >= ROWS + 3:
        text(g, H - 2, "Merry Christmas", 93 if f % 2 == 0 else 91)
        text(g, H - 1, "聖誕快樂", 32)
    return g

def render(g):
    out, cur = [], 0
    for row in g:
        while row and row[-1][0] == " ":
            row = row[:-1]
        for c, col in row:
            if c and col != cur:
                out.append(f"\x1b[{col}m" if col else "\x1b[0m")
                cur = col
            out.append(c)
        out.append("\n")
    return "".join(out).rstrip("\n")

sys.stdout.write("\x1b[?25l\x1b[2J")
for f in range(N):
    sys.stdout.write("\x1b[H" + render(frame(f)))
    sys.stdout.flush()
    if f < N - 1:
        time.sleep(0.3)
sys.stdout.write("\x1b[0m\x1b[?25h\n")
