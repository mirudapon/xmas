import math
import sys
import time

W, H = 72, 34
CX = W // 2
TOP = 3
STAR = ["O"]
LAYERS = [(1, 5), (3, 6), (5, 7)] 
FRAMES = 36
DELAY = 0.1

RESET = "\033[0m"
C = {
    "leaf": "\033[32m",
    "leaf2": "\033[92m",
    "trunk": "\033[33m",
    "star": "\033[1;93m",
    "snow": "\033[97m",
    "ground": "\033[37m",
    "dirt": "\033[90m",
    "text": "\033[1;93m",
    " ": "",
}
LIGHTS = ["\033[1;91m", "\033[1;93m", "\033[1;94m", "\033[1;95m", "\033[1;96m"]
GIFTS = ["\033[91m", "\033[94m", "\033[95m"]


def lcg(n):
    return (n * 1103515245 + 12345) & 0x7FFFFFFF


FLAKES = []
for i in range(55):
    r = lcg(i + 7)
    FLAKES.append((r % W, lcg(r) % H, 1 + lcg(r + 3) % 2, ".'`"[lcg(r + 5) % 3]))


def build_tree():
    cells = {}
    y = TOP + len(STAR)
    for start, rows in LAYERS:
        for k in range(rows):
            half = start + k * 2
            for x in range(CX - half, CX + half + 1):
                cells[(x, y)] = "edge" if abs(x - CX) == half else "leaf"
            y += 1
    trunk_top = y
    for ty in range(trunk_top, trunk_top + 3):
        for x in range(CX - 2, CX + 3):
            cells[(x, ty)] = "trunk"
    return cells, trunk_top + 3


TREE, GROUND = build_tree()
SNOW_DEPTH = [max(1, min(4, round(2.5 + math.sin(x / 4.5) * 1.2 + math.sin(x / 1.7) * 0.5))) for x in range(W)]
SNOW_PHASE = [lcg(x + 99) % FRAMES for x in range(W)]


def snow_height(x, f):
    final = SNOW_DEPTH[x]
    return min(final, (f * (final + 1) + SNOW_PHASE[x]) // FRAMES)
BULBS = [p for p in TREE if TREE[p] == "leaf" and (p[0] * 5 + p[1] * 3) % 7 == 0]


def frame(f):
    grid = [[(" ", " ") for _ in range(W)] for _ in range(H)]

    def put(x, y, ch, color):
        if 0 <= x < W and 0 <= y < H:
            grid[y][x] = (ch, color)

    for fx, fy, speed, ch in FLAKES:
        y = (fy + f * speed // 2) % GROUND
        x = (fx + (f + fy) // 6) % W
        put(x, y, ch, "snow")

    for (x, y), kind in TREE.items():
        if kind == "trunk":
            put(x, y, "#", "trunk")
        else:
            put(x, y, "*", "leaf2" if (x + y) % 3 == 0 else "leaf")
    for i, (x, y) in enumerate(BULBS):
        on = (i + f) % 4 != 0
        put(x, y, "o" if on else ".", f"L{(i + f // 2) % len(LIGHTS)}" if on else "leaf")

    put(CX, TOP, "o", "star")

    gy = GROUND - 2
    for i, gx in enumerate([CX - 13, CX + 7]):
        col = f"G{i}"
        for dy, row in enumerate(["+-+-+", "| | |", "+-+-+"]):
            for dx, ch in enumerate(row):
                put(gx + dx, gy - 1 + dy, ch, col)

    bottom = GROUND + 3
    heights = [snow_height(x, f) for x in range(W)]
    for x in range(W):
        h = heights[x]
        if h == 0:
            put(x, bottom, "_", "dirt")
        for k in range(h):
            y = bottom - k
            if k == h - 1:
                ch = "_" if h < heights[x - 1] or h < heights[(x + 1) % W] else "~"
            else:
                ch = ":" if (x * 7 + y * 3 + f // 3) % 9 == 0 else "."
            put(x, y, ch, "ground")

    msg = "Merry Christmas & Happy New Year!"
    shown = msg[: max(0, min(len(msg), (f - 4) * 2))]
    mx = CX - len(msg) // 2
    for i, ch in enumerate(shown):
        put(mx + i, bottom + 2, ch, "text")

    out = []
    for row in grid[: bottom + 3]:
        cur = None
        line = []
        for ch, col in row:
            if ch != " " and col != cur:
                if col.startswith("L"):
                    line.append(LIGHTS[int(col[1:])])
                elif col.startswith("G"):
                    line.append(GIFTS[int(col[1:])])
                else:
                    line.append(RESET + C[col])
                cur = col
            line.append(ch)
        out.append("".join(line).rstrip() + RESET + "\033[K")

    return "\n".join(out)


def main():
    w = sys.stdout.write
    w("\033[?25l\033[2J")
    for f in range(FRAMES):
        w("\033[H" + frame(f) + "\n")
        sys.stdout.flush()
        if f < FRAMES - 1:
            time.sleep(DELAY)
    w(RESET + "\033[?25h")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
