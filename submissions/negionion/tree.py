"""Neon Noel, a Christmas tree above a rain-slick city street."""

import math
import sys
import time
from itertools import groupby

WIDTH, HEIGHT = 73, 37
CENTER = WIDTH // 2
FRAME_COUNT, FRAME_DELAY = 56, 0.14
TREE_TOP = 8
BRANCH_WIDTHS = (
    0, 1, 2, 3, 4, 5, 6,
    4, 5, 6, 7, 8, 9, 10,
    8, 9, 10, 11, 12, 13, 14, 15,
)

PINE = ("204858", "24657a", "3c8fa6", "58c4d5")
VIOLET = ("35284f", "513972", "7952a8", "b077dd")
FROST = ("373858", "5c5c8b", "aa91d9", "e5c9ff")
AMBER = ("70405f", "ab6874", "ff9b88", "ffd1a2", "fff2d8")
PINK = ("633168", "a14295", "ed64ce", "ff9be5", "ffe0f8")
CYAN = ("255c72", "348ca7", "59dbea", "a0f7ff", "e4fdff")
BUILDINGS = (
    (1, 6, 16, VIOLET), (8, 6, 21, PINE), (15, 7, 19, VIOLET),
    (23, 5, 24, PINE), (45, 6, 23, VIOLET), (52, 7, 18, PINE),
    (60, 5, 22, VIOLET), (66, 6, 15, PINE),
)
LANTERN_PAIRS = (
    (1, 11, PINK), (3, 16, AMBER), (6, 21, PINK),
    (7, 24, AMBER), (5, 28, PINK), (11, 28, CYAN),
)

RESET = "\x1b[0m"
HOME = "\x1b[H"
EMPTY = (" ", None)


def pulse(phase, palette):
    """Pick a shade on a smooth, repeating rise and fall."""
    brightness = (1 - math.cos(math.tau * phase / FRAME_COUNT)) / 2
    return palette[round(brightness * (len(palette) - 1))]


def write_at(scene, x, y, text, color):
    for offset, char in enumerate(text):
        if char != " ":
            scene[y][x + offset] = (char, color)


def gift(scene, x, y, paper, ribbon):
    write_at(scene, x + 2, y, "╲╵╱", ribbon)
    write_at(scene, x, y + 1, "╭──┬──╮", paper)
    write_at(scene, x, y + 2, "│··│··│", paper)
    write_at(scene, x, y + 3, "╰──┴──╯", paper)
    for row, knot in enumerate("┬│┴", start=y + 1):
        scene[row][x + 3] = (knot, ribbon)


def add_city(scene):
    for x, width, roof, palette in BUILDINGS:
        write_at(scene, x, roof, "╭" + "─" * (width - 2) + "╮", palette[1])
        write_at(scene, x + width // 2, roof - 1, "╵", palette[2])
        for y in range(roof + 1, 30):
            scene[y][x] = scene[y][x + width - 1] = ("│", palette[0])
            for column in range(x + 1, x + width - 1, 2):
                if (column * 9 + y * 5) % 11 < 4:
                    scene[y][column] = ("▪", palette[2])
        write_at(scene, x + 1, roof + 2, "═" * (width - 2), palette[2])

    # Broken reflections and widening edges give the street depth.
    for y in range(30, 36):
        edge = 20 + (y - 30) * 3
        scene[y][CENTER - edge] = ("╱", CYAN[0])
        scene[y][CENTER + edge] = ("╲", PINK[0])
        for x in range(CENTER - edge + 1, CENTER + edge):
            texture = (x * x + 9 * x + 13 * y) % 23
            if texture < 9:
                palette = CYAN if x < CENTER else PINK
                scene[y][x] = ("·" if texture < 7 else "─", palette[texture % 2])


def make_scene():
    scene = [[EMPTY] * WIDTH for _ in range(HEIGHT)]
    add_city(scene)

    for y in range(30, 34):
        write_at(scene, CENTER - 1, y, "│┆│", VIOLET[2])
        scene[y][CENTER] = ("┆", CYAN[1])

    for y, half_width in enumerate(BRANCH_WIDTHS, start=TREE_TOP):
        scene[y][CENTER - half_width : CENTER + half_width + 1] = [EMPTY] * (
            2 * half_width + 1
        )
        scene[y][CENTER] = ("╵" if half_width == 0 else "┆", FROST[1])
        for distance in range(1, half_width + 1):
            inset = half_width - distance
            if inset % 3 == 0:
                shade = 3 if inset == 0 else 1
                scene[y][CENTER - distance] = ("╱", PINE[shade])
                scene[y][CENTER + distance] = ("╲", VIOLET[shade])

    gift(scene, 15, 31, PINK[2], AMBER[3])
    gift(scene, 25, 31, CYAN[1], CYAN[3])
    gift(scene, 41, 31, VIOLET[3], PINK[3])
    gift(scene, 51, 31, CYAN[2], AMBER[3])
    greeting = "N E O N   N O E L"
    left = (WIDTH - len(greeting)) // 2
    write_at(scene, left - 7, 36, "────", PINE[2])
    write_at(scene, left, 36, greeting, CYAN[3])
    write_at(scene, left + len(greeting) + 3, 36, "────", PINK[1])
    return scene


def add_snow(scene, frame):
    for flake in range(64):
        start_x = (flake * flake * 41 + flake * 37) % WIDTH
        start_y = (flake * flake * 13 + 11 * flake) % HEIGHT
        close = flake % 5 == 0
        speed = 2 if close else 1
        y = (start_y + frame * HEIGHT * speed // FRAME_COUNT) % HEIGHT
        sway = round(2 * math.sin(math.tau * (frame / FRAME_COUNT + flake / 19)))
        x = (start_x + sway) % WIDTH
        tree_row = y - TREE_TOP
        if 0 <= tree_row < len(BRANCH_WIDTHS) and abs(x - CENTER) <= BRANCH_WIDTHS[tree_row]:
            continue
        if scene[y][x] == EMPTY:
            char = "✧" if close else "·"
            color = pulse(frame + flake * 11, FROST if close else FROST[:2])
            scene[y][x] = (char, color)


def add_lights(scene, frame):
    for y, half_width, palette in (
        (12, 3, CYAN), (18, 6, PINK), (25, 10, CYAN),
    ):
        for x in range(-half_width, half_width + 1):
            ratio = x / half_width
            row = y + round(1.8 * (1 - ratio * ratio))
            shade = pulse(frame * 2 - abs(x) * 3 + y, palette)
            scene[row][CENTER + x] = ("•" if x % 3 == 0 else "·", shade)

    for index, (distance, y, palette) in enumerate(LANTERN_PAIRS):
        color = pulse(frame + index * 11, palette)
        bulb = ("◆" if color == palette[-1] else "●", color)
        scene[y][CENTER - distance] = scene[y][CENTER + distance] = bulb

    for index, x in enumerate(range(-29, 30, 3)):
        y = 34 + index % 2
        if scene[y][CENTER + x] == EMPTY:
            palette = CYAN[:2] if x < 0 else PINK[:2]
            scene[y][CENTER + x] = ("─", pulse(frame + index * 5, palette))

    scene[5][CENTER] = ("✦", pulse(frame * 2, CYAN[3:]))
    for index, (distance, y, char) in enumerate(
        ((0, 3, "╵"), (0, 7, "╷"), (3, 5, "─"), (2, 3, "·"), (2, 7, "·"), (5, 2, "✧"))
    ):
        glint = (char, pulse(frame * 2 + index * 7, PINK))
        scene[y][CENTER - distance] = scene[y][CENTER + distance] = glint


def render_frame(background, frame):
    scene = [row.copy() for row in background]
    add_snow(scene, frame)
    add_lights(scene, frame)
    return scene


def paint(scene):
    lines = []
    active_color = None
    for row in scene:
        spans = []
        for color, cells in groupby(row, key=lambda cell: cell[1]):
            if color is not None and color != active_color:
                red, green, blue = bytes.fromhex(color)
                spans.append(f"\x1b[38;2;{red};{green};{blue}m")
                active_color = color
            spans.append("".join(char for char, _ in cells))
        lines.append("".join(spans))
    return "\n".join(lines) + RESET


def main():
    # Write UTF-8 and LF even when stdout is redirected on Windows.
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    background = make_scene()
    sys.stdout.write("\x1b[?25l\x1b[2J")
    try:
        for frame in range(FRAME_COUNT):
            sys.stdout.write(HOME + paint(render_frame(background, frame)))
            sys.stdout.flush()
            time.sleep(FRAME_DELAY)
    finally:
        sys.stdout.write(f"{RESET}\x1b[{HEIGHT + 1};1H\x1b[?25h")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
