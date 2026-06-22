"""Generate lily58_keymap_cheatsheet.png — second-screen reference card.

Matches the existing visual style of the project's cheat-sheet PNG: dark
panel grid showing all four firmware layers, no UA overlay, no wallpaper
header. Bottom of the card is a kitty keybindings reference (the legend
section that used to live here was retired — the colour coding is obvious
enough at a glance that the room was better spent on actual cheats).

Run:  python3 make_cheatsheet.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "lily58_keymap_cheatsheet.png"
W, H = 1696, 938

# === Palette ================================================================
BG = (16, 19, 26)
PANEL_BG = (24, 28, 38)
PANEL_BORDER = (44, 50, 64)

KEY_BG = (54, 62, 78)
KEY_BORDER = (78, 88, 108)
KEY_TRANS = (32, 38, 50)
KEY_TRANS_BORDER = (54, 60, 76)

MOD_BG = (60, 100, 175)
MOD_BORDER = (95, 140, 215)
THUMB_BG = (70, 130, 90)
THUMB_BORDER = (110, 175, 130)
COMBO_BG = (148, 96, 165)
COMBO_BORDER = (190, 130, 210)

INK = (240, 242, 248)
INK_DIM = (180, 188, 205)
INK_TRANS = (90, 102, 122)
DIM = (140, 150, 170)
MUTED = (84, 92, 110)

AMBER = (245, 175, 75)
AMBER_DIM = (200, 140, 60)

# === Fonts ==================================================================
DISPLAY = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MONO_BOLD = "/home/b_bondar/.local/share/fonts/NerdFonts/JetBrainsMonoNerdFont-Bold.ttf"
MONO = "/home/b_bondar/.local/share/fonts/NerdFonts/JetBrainsMonoNerdFont-Regular.ttf"


def F(p, s):
    return ImageFont.truetype(p, s)


# === Keymap data ============================================================
T = ("·", "trans")
N = (None, "none")

BASE = [
    ("ESC", "normal"), ("1", "normal"), ("2", "normal"), ("3", "normal"), ("4", "normal"), ("5", "normal"),
    ("6", "normal"), ("7", "normal"), ("8", "normal"), ("9", "normal"), ("0", "normal"), ("BSPC", "normal"),

    ("TAB", "normal"), ("Q", "normal"), ("W", "normal"), ("E", "normal"), ("R", "normal"), ("T", "normal"),
    ("Y", "normal"), ("U", "normal"), ("I", "normal"), ("O", "normal"), ("P", "normal"), ("-", "normal"),

    ("CTL\nESC", "mod"), ("A\nSUPER", "hrm"), ("S\nALT", "hrm"), ("D\nCTRL", "hrm"), ("F\nSHIFT", "hrm"), ("G", "normal"),
    ("H", "normal"), ("J\nSHIFT", "hrm"), ("K\nCTRL", "hrm"), ("L\nALT", "hrm"), (";\nSUPER", "hrm"), ("ENTER", "normal"),

    ("LSHFT", "mod"), ("Z", "combo"), ("X", "combo"), ("C", "combo"), ("V", "combo"), ("B", "normal"),
    N, N,
    ("N", "combo"), ("M", "combo"), (",", "normal"), (".", "combo"), ("/", "combo"), ("RSHFT", "mod"),

    ("LGUI", "thumb"), ("SPACE", "thumb"), ("LOWER", "thumb"),
    N, N,
    ("RAISE", "thumb"), ("BSPC", "thumb"), ("ENTER", "thumb"),
]

LOWER = [
    T, T, T, T, T, T, T, T, T, T, T, ("F13", "muted"),
    ("F1", "muted"), ("F2", "muted"), ("F3", "muted"), ("F4", "muted"), ("F5", "muted"), ("F6", "muted"),
    ("F7", "muted"), ("F8", "muted"), ("F9", "muted"), ("F10", "muted"), ("F11", "muted"), ("F12", "muted"),
    ("`", "normal"), ("!", "normal"), ("@", "normal"), ("#", "normal"), ("$", "normal"), ("%", "normal"),
    ("^", "normal"), ("&", "normal"), ("*", "normal"), ("(", "normal"), (")", "normal"), ("~", "normal"),
    T, ("1", "normal"), ("2", "normal"), ("3", "normal"), ("4", "normal"), ("5", "normal"),
    N, N,
    ("6", "normal"), ("7", "normal"), ("8", "normal"), ("9", "normal"), ("0", "normal"), T,
    T, T, T, N, N, T, T, T,
]

RAISE = [
    T, T, T, T, T, T, T, T, T, T, T, T,
    ("`", "normal"), ("1", "normal"), ("2", "normal"), ("3", "normal"), ("4", "normal"), ("5", "normal"),
    ("6", "normal"), ("7", "normal"), ("8", "normal"), ("9", "normal"), ("0", "normal"), T,
    T, ("DICT", "combo"), ("CHAT", "combo"), ("PASTE", "combo"), T, T,
    ("←", "normal"), ("↓", "normal"), ("↑", "normal"), ("→", "normal"), ("'", "normal"), ('"', "normal"),
    T, T, ("REC", "combo"), ("MARK", "combo"), ("STOP", "combo"), T, N, N,
    ("+", "normal"), ("-", "normal"), ("=", "normal"), ("[", "normal"), ("]", "normal"), ("\\", "normal"),
    T, T, T, N, N, T, T, T,
]

ADJUST = [
    ("BTCLR", "mod"), ("BT1", "mod"), ("BT2", "mod"), ("BT3", "mod"), ("BT4", "mod"), ("BT5", "mod"),
    T, T, T, T, T, T,
    ("EXTPWR", "mod"), ("RGB\nHUD", "mod"), ("RGB\nHUI", "mod"), ("RGB\nSAD", "mod"), ("RGB\nSAI", "mod"), ("RGB\nEFF", "mod"),
    T, T, T, T, T, T,
    T, ("RGB\nBRD", "mod"), ("RGB\nBRI", "mod"), T, T, T,
    T, T, T, T, T, T,
    T, T, T, T, T, T, N, N, T, T, T, T, T, T,
    T, T, T, N, N, T, T, T,
]

LAYERS_DATA = [
    ("Layer 0", "BASE",   "combos: Z+X→[  C+V→'  .+/→]  N+M→_  ·  lang: LSHFT+LOWER ←  RSHFT+RAISE →  ·  amber word = hold for mod (opposite hand)", BASE),
    ("Layer 1", "LOWER",  "hold left thumb (LOWER)",                                LOWER),
    ("Layer 2", "RAISE",  "hold right thumb (RAISE)",                               RAISE),
    ("Layer 3", "ADJUST", "hold LOWER + RAISE together",                            ADJUST),
]


# === Drawing ================================================================

def draw_key(d, x, y, w, h, label, kind):
    if kind == "none":
        return
    if kind == "trans":
        bg, border, text_color = KEY_TRANS, KEY_TRANS_BORDER, INK_TRANS
    elif kind == "mod":
        bg, border, text_color = MOD_BG, MOD_BORDER, INK
    elif kind == "thumb":
        bg, border, text_color = THUMB_BG, THUMB_BORDER, INK
    elif kind == "combo":
        bg, border, text_color = COMBO_BG, COMBO_BORDER, INK
    elif kind == "muted":
        bg, border, text_color = KEY_TRANS, KEY_TRANS_BORDER, (105, 118, 140)
    else:
        bg, border, text_color = KEY_BG, KEY_BORDER, INK

    d.rounded_rectangle([x, y, x + w, y + h], radius=7, fill=bg, outline=border, width=1)
    if not label:
        return

    if kind == "hrm":
        # Home-row mod: tap-identity (letter) in ink on top, hold-identity
        # (modifier word) in amber below.
        letter, mod = label.split("\n")
        lf = F(MONO_BOLD, 15)
        mf = F(MONO_BOLD, 9)
        tw = d.textlength(letter, font=lf)
        d.text((x + (w - tw) / 2, y + 4), letter, font=lf, fill=INK)
        tw = d.textlength(mod, font=mf)
        d.text((x + (w - tw) / 2, y + h - 14), mod, font=mf, fill=AMBER)
        return

    lines = label.split("\n")
    base_size = 18 if len(lines) == 1 else 13
    if any(len(line) > 4 for line in lines):
        base_size = 12
    if any(len(line) > 5 for line in lines):
        base_size = 11
    if kind == "combo" and len(lines) == 1 and len(lines[0]) <= 2:
        base_size = 22
    fnt = F(MONO_BOLD, base_size)

    line_h = base_size + 2
    total_h = line_h * len(lines)
    start_y = y + (h - total_h) / 2 - 1
    for i, line in enumerate(lines):
        tw = d.textlength(line, font=fnt)
        d.text((x + (w - tw) / 2, start_y + i * line_h), line, font=fnt, fill=text_color)


def draw_layer_panel(canvas, x, y, w, h, num, name, desc, bindings):
    d = ImageDraw.Draw(canvas)

    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=PANEL_BG, outline=PANEL_BORDER, width=1)

    pad = 18
    head_font = F(SANS_BOLD, 22)
    desc_font = F(MONO, 11)

    # "Layer N · NAME"  — number in amber, name in ink
    d.text((x + pad, y + pad), num, font=head_font, fill=AMBER)
    num_w = d.textlength(num, font=head_font)
    sep = "  ·  "
    d.text((x + pad + num_w, y + pad), sep, font=head_font, fill=MUTED)
    sep_w = d.textlength(sep, font=head_font)
    d.text((x + pad + num_w + sep_w, y + pad), name, font=head_font, fill=AMBER)

    d.text((x + pad, y + pad + 30), desc, font=desc_font, fill=DIM)

    # Keys area
    keys_top = y + pad + 56
    keys_bottom = y + h - 16

    KEY_W = 52
    KEY_H = 42
    GAP = 3
    SPLIT_GAP = 16
    THUMB_VERT_GAP = 6

    half_w = 6 * KEY_W + 5 * GAP
    total_w = 2 * half_w + SPLIT_GAP
    keys_x = x + (w - total_w) // 2

    rows_total_h = 4 * KEY_H + 3 * GAP + THUMB_VERT_GAP + KEY_H
    keys_y = keys_top + ((keys_bottom - keys_top) - rows_total_h) // 2

    def get(slot):
        return bindings[slot]

    for row in range(3):
        ry = keys_y + row * (KEY_H + GAP)
        for i in range(6):
            slot = row * 12 + i
            label, kind = get(slot)
            kx = keys_x + i * (KEY_W + GAP)
            draw_key(d, kx, ry, KEY_W, KEY_H, label, kind)
        for i in range(6):
            slot = row * 12 + 6 + i
            label, kind = get(slot)
            kx = keys_x + half_w + SPLIT_GAP + i * (KEY_W + GAP)
            draw_key(d, kx, ry, KEY_W, KEY_H, label, kind)

    ry = keys_y + 3 * (KEY_H + GAP)
    for i in range(6):
        slot = 36 + i
        label, kind = get(slot)
        kx = keys_x + i * (KEY_W + GAP)
        draw_key(d, kx, ry, KEY_W, KEY_H, label, kind)
    for i in range(6):
        slot = 44 + i
        label, kind = get(slot)
        kx = keys_x + half_w + SPLIT_GAP + i * (KEY_W + GAP)
        draw_key(d, kx, ry, KEY_W, KEY_H, label, kind)

    ty = keys_y + 4 * (KEY_H + GAP) + THUMB_VERT_GAP
    left_thumb_x = keys_x + 3 * (KEY_W + GAP)
    for i, slot in enumerate([50, 51, 52]):
        label, kind = get(slot)
        kx = left_thumb_x + i * (KEY_W + GAP)
        draw_key(d, kx, ty, KEY_W, KEY_H, label, kind)
    right_thumb_x = keys_x + half_w + SPLIT_GAP
    for i, slot in enumerate([55, 56, 57]):
        label, kind = get(slot)
        kx = right_thumb_x + i * (KEY_W + GAP)
        draw_key(d, kx, ty, KEY_W, KEY_H, label, kind)


def draw_header(canvas):
    d = ImageDraw.Draw(canvas)
    title_font = F(DISPLAY, 32)
    sub_font = F(MONO, 12)

    title = "Lily58 · Keymap Cheat Sheet"
    tw = d.textlength(title, font=title_font)
    d.text(((W - tw) / 2, 18), title, font=title_font, fill=INK)

    sub = "54-key build  ·  branch zmk-for-lily  ·  slot 24 = tap ESC / hold LCTRL  ·  grey = transparent (falls through)"
    sw = d.textlength(sub, font=sub_font)
    d.text(((W - sw) / 2, 60), sub, font=sub_font, fill=DIM)


def draw_kitty_footer(canvas, footer_top):
    """Replaces the old colour-swatch legend with a kitty keybindings card.

    Three columns — windows, tabs, clipboard/misc — laid out across the full
    footer width. ⌘ is the user-visible cmd glyph; on the lily58 it's LGUI.
    """
    d = ImageDraw.Draw(canvas)
    PAD_X = 40

    h_font = F(MONO_BOLD, 12)
    label_font = F(MONO_BOLD, 13)
    desc_font = F(MONO, 12)
    tail_font = F(MONO, 11)

    d.text((PAD_X, footer_top - 16),
           "KITTY  ·  Super = left thumb (LGUI)",
           font=h_font, fill=AMBER_DIM)

    section_line_y = footer_top - 2
    d.line([(PAD_X, section_line_y), (W - PAD_X, section_line_y)],
           fill=PANEL_BORDER, width=1)

    # Anchor each column at a hand-picked x so wide key labels in the rightmost
    # column don't run off the right edge of the canvas.
    col1_x = PAD_X
    col2_x = 600
    col3_x = 1170

    body_y = footer_top + 12
    row_h = 19

    def column(x, header, rows):
        d.text((x, body_y), header, font=h_font, fill=AMBER_DIM)
        key_col_w = max(d.textlength(k, font=label_font) for k, _ in rows) + 14
        for i, (key, desc) in enumerate(rows):
            ly = body_y + 22 + i * row_h
            d.text((x, ly), key, font=label_font, fill=INK)
            d.text((x + key_col_w, ly + 1), desc, font=desc_font, fill=MUTED)

    column(col1_x, "WINDOWS", [
        ("Super Enter",        "new window (cwd)"),
        ("Super Q",            "close window"),
        ("Super L",            "next layout"),
        ("Super Shift ←→↑↓",   "focus neighbour"),
        ("Super R",            "resize mode (arrows, Esc ends)"),
    ])

    column(col2_x, "TABS", [
        ("Super T",            "new tab (cwd)"),
        ("Super Shift Q",      "close tab"),
        ("Super ← / →",        "prev / next tab"),
        ("Super Shift , / .",  "move tab back / fwd"),
        ("Super 1 – 9",        "jump to tab N"),
    ])

    column(col3_x, "CLIPBOARD  ·  HINTS", [
        ("Super C / V",        "copy / paste"),
        ("Ctrl Shift C / V",   "copy / paste (alt)"),
        ("Super E",            "open URL with hints"),
        ("UA dupes",           "Super + с м й е д у к all work"),
    ])


def main():
    canvas = Image.new("RGB", (W, H), BG)

    draw_header(canvas)

    # 2x2 grid of layer panels
    panels_top = 92
    panels_bottom = 760
    panel_gap_x = 22
    panel_gap_y = 18
    PAD_X = 24
    panel_w = (W - 2 * PAD_X - panel_gap_x) // 2
    panel_h = (panels_bottom - panels_top - panel_gap_y) // 2

    for i, (num, name, desc, bindings) in enumerate(LAYERS_DATA):
        col = i % 2
        row = i // 2
        px = PAD_X + col * (panel_w + panel_gap_x)
        py = panels_top + row * (panel_h + panel_gap_y)
        draw_layer_panel(canvas, px, py, panel_w, panel_h, num, name, desc, bindings)

    draw_kitty_footer(canvas, panels_bottom + 36)

    canvas.save(OUT, "PNG", optimize=True)
    print(f"Saved: {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
