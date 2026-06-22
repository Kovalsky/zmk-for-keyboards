"""Generate the Lily58 keymap wallpaper from scratch.

Reads the physical layout and keymap directly (encoded below as data) and
renders all 54 keys for each of the 4 layers in their actual physical
positions. No reuse of any existing cheat-sheet PNG — every pixel is drawn
here. Output is sized for the laptop screen (1680x1050).
"""

import json
import math
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path.home() / "Pictures" / "lily58_wallpaper.png"
W, H = 1680, 1050

# === Palette ================================================================
# Editorial dark with amber accent — the original direction.
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

# Secondary-panel palette (LOWER / RAISE). Recessed: surface darker than page
# BG, keys blended toward BG so the bottom row reads as quiet reference, not
# co-equal focus with BASE EN/UA on top.
SECONDARY_PANEL_BG = (12, 14, 20)
SECONDARY_PANEL_BORDER = (32, 38, 50)
SECONDARY_KEY_BG = (38, 44, 56)
SECONDARY_KEY_BORDER = (58, 66, 82)
SECONDARY_KEY_TRANS = (22, 26, 34)
SECONDARY_KEY_TRANS_BORDER = (38, 44, 56)
SECONDARY_INK = (188, 196, 212)
SECONDARY_INK_TRANS = (70, 82, 100)

# === Fonts ==================================================================
DISPLAY = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MONO_BOLD = "/home/b_bondar/.local/share/fonts/NerdFonts/JetBrainsMonoNerdFont-Bold.ttf"
MONO = "/home/b_bondar/.local/share/fonts/NerdFonts/JetBrainsMonoNerdFont-Regular.ttf"


def F(p, s):
    return ImageFont.truetype(p, s)


def fetch_openrouter_usage():
    """Return (used, total) in USD, or None if the API is unreachable."""
    key_path = Path.home() / ".config" / "openrouter" / "key"
    if not key_path.exists():
        return None
    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/credits",
            headers={"Authorization": f"Bearer {key_path.read_text().strip()}"},
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.load(resp).get("data", {})
        return float(data["total_usage"]), float(data["total_credits"])
    except Exception:
        return None


# === Keymap data ============================================================
# 58 slots per layer in linear order (row 0 → row 3 → thumbs).
# Each entry: (label, kind). T = transparent (&trans), N = absent (&none).
T = ("·", "trans")
N = (None, "none")

BASE_EN = [
    # row 0: 12 keys
    ("ESC", "normal"), ("1", "normal"), ("2", "normal"), ("3", "normal"), ("4", "normal"), ("5", "normal"),
    ("6", "normal"), ("7", "normal"), ("8", "normal"), ("9", "normal"), ("0", "normal"), ("BSPC", "normal"),
    # row 1
    ("TAB", "normal"), ("Q", "normal"), ("W", "normal"), ("E", "normal"), ("R", "normal"), ("T", "normal"),
    ("Y", "normal"), ("U", "normal"), ("I", "normal"), ("O", "normal"), ("P", "normal"), ("-", "normal"),
    # row 2 — home-row mods: tap = letter, hold = amber modifier
    ("CTL\nESC", "mod"), ("A\nSUPER", "hrm"), ("S\nALT", "hrm"), ("D\nCTRL", "hrm"), ("F\nSHIFT", "hrm"), ("G", "normal"),
    ("H", "normal"), ("J\nSHIFT", "hrm"), ("K\nCTRL", "hrm"), ("L\nALT", "hrm"), (";\nSUPER", "hrm"), ("ENTER", "normal"),
    # row 3 (14 slots, &none at 42, 43)
    ("LSHFT", "mod"), ("Z", "combo"), ("X", "combo"), ("C", "combo"), ("V", "combo"), ("B", "normal"),
    N, N,
    ("N", "combo"), ("M", "combo"), (",", "normal"), (".", "combo"), ("/", "combo"), ("RSHFT", "mod"),
    # thumbs (8 slots, &none at 53, 54) — Miryoku-style right side
    ("LGUI", "thumb"), ("SPACE", "thumb"), ("LOWER", "thumb"),
    N, N,
    ("RAISE", "thumb"), ("BSPC", "thumb"), ("ENTER", "thumb"),
]

# Ukrainian system overlay (OS-level layout). Same firmware base layer — just
# what each scancode produces when the Ukrainian xkb layout is active.
# Mapping follows standard us+ua: Q→Й, W→Ц, … Z→Я, X→Ч, …
BASE_UA = [
    # row 0: digits and ESC/BSPC stay
    ("ESC", "normal"), ("1", "normal"), ("2", "normal"), ("3", "normal"), ("4", "normal"), ("5", "normal"),
    ("6", "normal"), ("7", "normal"), ("8", "normal"), ("9", "normal"), ("0", "normal"), ("BSPC", "normal"),
    # row 1: Q W E R T Y U I O P → Й Ц У К Е Н Г Ш Щ З
    ("TAB", "normal"), ("Й", "normal"), ("Ц", "normal"), ("У", "normal"), ("К", "normal"), ("Е", "normal"),
    ("Н", "normal"), ("Г", "normal"), ("Ш", "normal"), ("Щ", "normal"), ("З", "normal"), ("-", "normal"),
    # row 2: A S D F G H J K L ; → Ф І В А П Р О Л Д Ж — same HRM holds
    ("CTL\nESC", "mod"), ("Ф\nSUPER", "hrm"), ("І\nALT", "hrm"), ("В\nCTRL", "hrm"), ("А\nSHIFT", "hrm"), ("П", "normal"),
    ("Р", "normal"), ("О\nSHIFT", "hrm"), ("Л\nCTRL", "hrm"), ("Д\nALT", "hrm"), ("Ж\nSUPER", "hrm"), ("ENTER", "normal"),
    # row 3: Z X C V B → Я Ч С М И ; N M , . / → Т Ь Б Ю .
    ("LSHFT", "mod"), ("Я", "combo"), ("Ч", "combo"), ("С", "combo"), ("М", "combo"), ("И", "normal"),
    N, N,
    ("Т", "combo"), ("Ь", "combo"), ("Б", "normal"), ("Ю", "combo"), (".", "combo"), ("RSHFT", "mod"),
    # thumbs: same firmware bindings, no language transform
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
    ("`", "muted"), ("1", "muted"), ("2", "muted"), ("3", "muted"), ("4", "muted"), ("5", "muted"),
    ("6", "muted"), ("7", "muted"), ("8", "muted"), ("9", "muted"), ("0", "muted"), T,
    T, ("DICT", "combo"), ("CHAT", "combo"), ("PASTE", "combo"), T, T,
    ("←", "normal"), ("↓", "normal"), ("↑", "normal"), ("→", "normal"), ("'", "normal"), ('"', "normal"),
    T, T, ("REC", "combo"), ("MARK", "combo"), ("STOP", "combo"), T, N, N,
    ("+", "normal"), ("-", "normal"), ("=", "normal"), ("[", "normal"), ("]", "normal"), ("\\", "normal"),
    T, T, T, N, N, T, T, T,
]

LAYERS_DATA = [
    ("EN", "BASE",  "english · firmware default", BASE_EN),
    ("UA", "BASE",  "ukrainian · OS overlay",     BASE_UA),
    ("01", "LOWER", "hold left thumb",            LOWER),
    ("02", "RAISE", "hold right thumb",           RAISE),
]


# === Drawing primitives =====================================================

def soft_glow(base, cx, cy, radius, color, alpha):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(*color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=radius // 2))
    return Image.alpha_composite(base, layer)


def draw_key(d, x, y, w, h, label, kind, secondary=False):
    if kind == "none":
        return
    if kind == "trans":
        if secondary:
            bg, border, text_color = SECONDARY_KEY_TRANS, SECONDARY_KEY_TRANS_BORDER, SECONDARY_INK_TRANS
        else:
            bg, border, text_color = KEY_TRANS, KEY_TRANS_BORDER, INK_TRANS
    elif kind == "mod":
        bg, border, text_color = MOD_BG, MOD_BORDER, INK
    elif kind == "thumb":
        bg, border, text_color = THUMB_BG, THUMB_BORDER, INK
    elif kind == "combo":
        bg, border, text_color = COMBO_BG, COMBO_BORDER, INK
    elif kind == "muted":
        # Rarely-used keys (F-row on LOWER). Visible if needed, never shouts.
        if secondary:
            bg, border = SECONDARY_KEY_TRANS, SECONDARY_KEY_TRANS_BORDER
        else:
            bg, border = KEY_TRANS, KEY_TRANS_BORDER
        text_color = (105, 118, 140)
    elif secondary:
        bg, border, text_color = SECONDARY_KEY_BG, SECONDARY_KEY_BORDER, SECONDARY_INK
    else:
        bg, border, text_color = KEY_BG, KEY_BORDER, INK

    d.rounded_rectangle([x, y, x + w, y + h], radius=7, fill=bg, outline=border, width=1)

    if not label:
        return

    if kind == "hrm":
        # Home-row mod: tap-identity (letter) in ink, hold-identity
        # (modifier word) in amber below it.
        letter, mod = label.split("\n")
        lf = F(MONO_BOLD, 17)
        mf = F(MONO_BOLD, 10)
        tw = d.textlength(letter, font=lf)
        d.text((x + (w - tw) / 2, y + 5), letter, font=lf, fill=INK)
        tw = d.textlength(mod, font=mf)
        d.text((x + (w - tw) / 2, y + h - 17), mod, font=mf, fill=AMBER)
        return

    lines = label.split("\n")
    base_size = 20 if len(lines) == 1 else 16
    if any(len(line) > 4 for line in lines):
        base_size = 14
    if any(len(line) > 5 for line in lines):
        base_size = 12
    # Combo-trigger keys get a chunkier label so the chord letters
    # (Z, X, ., /, N, M) read from across the room.
    if kind == "combo" and len(lines) == 1 and len(lines[0]) <= 2:
        base_size = 26
    fnt = F(MONO_BOLD, base_size)

    line_h = base_size + 2
    total_h = line_h * len(lines)
    start_y = y + (h - total_h) / 2 - 1
    for i, line in enumerate(lines):
        tw = d.textlength(line, font=fnt)
        d.text((x + (w - tw) / 2, start_y + i * line_h), line, font=fnt, fill=text_color)


def draw_layer_panel(canvas, x, y, w, h, num, name, desc, bindings, secondary=False):
    d = ImageDraw.Draw(canvas)

    # Panel surface — secondary panels recess (darker than page BG).
    panel_bg = SECONDARY_PANEL_BG if secondary else PANEL_BG
    panel_border = SECONDARY_PANEL_BORDER if secondary else PANEL_BORDER
    num_color = AMBER_DIM if secondary else AMBER
    name_color = INK_DIM if secondary else INK

    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=panel_bg, outline=panel_border, width=1)

    # Header
    pad = 18
    num_font = F(SANS_BOLD, 24)
    name_font = F(SANS_BOLD, 18)
    desc_font = F(MONO, 11)
    inline_desc_font = F(MONO_BOLD, 13)

    if secondary:
        # Skip the meaningless "01"/"02" tag. Render "LOWER · hold left thumb"
        # as a single compound title so the thumb-side cue lives next to the
        # layer name instead of buried in the corner.
        d.text((x + pad, y + pad), name, font=name_font, fill=name_color)
        name_w = d.textlength(name, font=name_font)
        d.text((x + pad + name_w + 10, y + pad + 4),
               "·  " + desc, font=inline_desc_font, fill=MUTED)
    else:
        d.text((x + pad, y + pad - 6), num, font=num_font, fill=num_color)
        num_w = d.textlength(num, font=num_font)
        name_x = x + pad + num_w + 14
        d.text((name_x, y + pad), name, font=name_font, fill=name_color)

        desc_w = d.textlength(desc, font=desc_font)
        d.text((x + w - pad - desc_w, y + pad + 6), desc, font=desc_font, fill=MUTED)

    # Hairline beneath header
    sep_y = y + pad + 34
    d.line([(x + pad, sep_y), (x + w - pad, sep_y)], fill=panel_border, width=1)

    # Keys area
    keys_top = sep_y + 14
    keys_bottom = y + h - 16
    keys_h = keys_bottom - keys_top

    KEY_W = 60
    KEY_H = 50
    GAP = 3
    SPLIT_GAP = 18
    THUMB_VERT_GAP = 8

    # Column stagger so panels read like an actual Lily58 (middle finger
    # column raised most, ring next, pinky/index closer to baseline).
    # Negative values move the column UP. Values are in pixels.
    COL_STAGGER_LEFT  = [0, -2, -6, -9, -3, 0]   # outer pinky → inner index
    COL_STAGGER_RIGHT = [0, -3, -9, -6, -2, 0]   # mirror

    half_w = 6 * KEY_W + 5 * GAP
    total_w = 2 * half_w + SPLIT_GAP
    keys_x = x + (w - total_w) // 2

    rows_total_h = 4 * KEY_H + 3 * GAP + THUMB_VERT_GAP + KEY_H
    keys_y = keys_top + (keys_h - rows_total_h) // 2

    def get(slot):
        return bindings[slot]

    # Rows 0-2 (12 keys each, no &none in middle) — with column stagger
    for row in range(3):
        ry = keys_y + row * (KEY_H + GAP)
        for i in range(6):
            slot = row * 12 + i
            label, kind = get(slot)
            kx = keys_x + i * (KEY_W + GAP)
            draw_key(d, kx, ry + COL_STAGGER_LEFT[i], KEY_W, KEY_H, label, kind, secondary=secondary)
        for i in range(6):
            slot = row * 12 + 6 + i
            label, kind = get(slot)
            kx = keys_x + half_w + SPLIT_GAP + i * (KEY_W + GAP)
            draw_key(d, kx, ry + COL_STAGGER_RIGHT[i], KEY_W, KEY_H, label, kind, secondary=secondary)

    # Row 3 (skip slots 42, 43 — &none) — with column stagger
    ry = keys_y + 3 * (KEY_H + GAP)
    for i in range(6):
        slot = 36 + i
        label, kind = get(slot)
        kx = keys_x + i * (KEY_W + GAP)
        draw_key(d, kx, ry + COL_STAGGER_LEFT[i], KEY_W, KEY_H, label, kind)
    for i in range(6):
        slot = 44 + i
        label, kind = get(slot)
        kx = keys_x + half_w + SPLIT_GAP + i * (KEY_W + GAP)
        draw_key(d, kx, ry + COL_STAGGER_RIGHT[i], KEY_W, KEY_H, label, kind)

    # Thumb cluster: 3 left + 3 right, positioned at the inner edges
    ty = keys_y + 4 * (KEY_H + GAP) + THUMB_VERT_GAP
    left_thumb_x = keys_x + 3 * (KEY_W + GAP)
    for i, slot in enumerate([50, 51, 52]):
        label, kind = get(slot)
        kx = left_thumb_x + i * (KEY_W + GAP)
        draw_key(d, kx, ty, KEY_W, KEY_H, label, kind, secondary=secondary)
    right_thumb_x = keys_x + half_w + SPLIT_GAP
    for i, slot in enumerate([55, 56, 57]):
        label, kind = get(slot)
        kx = right_thumb_x + i * (KEY_W + GAP)
        draw_key(d, kx, ty, KEY_W, KEY_H, label, kind, secondary=secondary)


def draw_header(canvas):
    d = ImageDraw.Draw(canvas)

    title_font = F(DISPLAY, 92)
    eyebrow_font = F(MONO_BOLD, 12)
    tag_font = F(SANS, 16)
    meta_label = F(MONO, 11)
    meta_value = F(MONO_BOLD, 14)

    PAD_X = 80
    bar_x = PAD_X - 22
    d.rectangle([bar_x, 50, bar_x + 4, 162], fill=AMBER)

    d.text((PAD_X, 48),
           "Z M K   ·   S P L I T   K E Y B O A R D",
           font=eyebrow_font, fill=AMBER_DIM)

    title_y = 64
    d.text((PAD_X, title_y), "LILY58", font=title_font, fill=INK)
    title_w = d.textlength("LILY58", font=title_font)
    d.text((PAD_X + title_w - 8, title_y), ".", font=title_font, fill=AMBER)

    d.text((PAD_X, title_y + 110),
           "Keymap reference  ·  ENG + UKR  ·  54 keys",
           font=tag_font, fill=DIM)

    right_x = W - PAD_X
    items = [
        ("BUILD",   "zmk-for-lily"),
        ("LAYOUT",  "lily58 · split"),
        ("VERSION", "v03 · 2026"),
    ]
    block_top = 64
    line_h = 28
    values_w = [d.textlength(v, font=meta_value) for _, v in items]
    max_val_w = max(values_w)
    label_x = right_x - max_val_w - 130

    for i, (lab, val) in enumerate(items):
        ty = block_top + i * line_h
        vw = d.textlength(val, font=meta_value)
        d.text((right_x - vw, ty), val, font=meta_value, fill=INK)
        d.text((label_x, ty + 3), lab, font=meta_label, fill=MUTED)

    sep_x = right_x - max_val_w - 36
    d.line(
        [(sep_x, block_top + 2), (sep_x, block_top + line_h * len(items) - 6)],
        fill=PANEL_BORDER, width=1,
    )


def draw_footer(canvas, footer_top, openrouter_usage=None):
    d = ImageDraw.Draw(canvas)
    PAD_X = 40

    h_font = F(MONO_BOLD, 12)
    label_font = F(MONO, 11)
    body_font = F(MONO_BOLD, 15)
    cmd_font = F(MONO_BOLD, 14)
    desc_font = F(MONO, 13)
    mini_font = F(MONO_BOLD, 8)
    stats_font = F(MONO, 12)

    # Five-column footer. Left side (COMBOS, MEETING TOOLS) is foreground —
    # full-voice headers and labels. Right side (MODELS, ADJUST, LEGEND) is
    # a quiet metadata zone — muted headers, dimmer text, packed tighter.
    col1_x = PAD_X            # COMBOS         — foreground
    col2_x = PAD_X + 290      # MEETING TOOLS  — foreground
    col3_x = PAD_X + 790      # MODELS         — metadata zone start
    col4_x = PAD_X + 1090     # ADJUST mini-grid
    col5_x = PAD_X + 1320     # LEGEND single-column

    section_line_y = footer_top + 14
    body_y = footer_top + 22

    def section_header(text, x, color=AMBER_DIM):
        d.text((x, footer_top), text, font=h_font, fill=color)
        tw = d.textlength(text, font=h_font)
        d.line([(x, section_line_y), (x + min(tw, 60), section_line_y)],
               fill=color, width=1)

    # Column 1: Combos — emit firmware keycode; OS layout decides what prints.
    section_header("COMBOS  · BASE LAYER", col1_x)
    combos_lines = [
        ("Z + X", "[", "х"),
        ("C + V", "'", "є"),
        (". + /", "]", "ї"),
        ("N + M", "_", "_"),
    ]
    for i, (trig, en, ua) in enumerate(combos_lines):
        ly = body_y + i * 22
        d.text((col1_x, ly), trig, font=body_font, fill=INK_DIM)
        arrow_x = col1_x + 78
        d.text((arrow_x, ly), "→", font=body_font, fill=MUTED)
        d.text((arrow_x + 22, ly), en, font=body_font, fill=INK)
        d.text((arrow_x + 50, ly + 1), "/", font=desc_font, fill=MUTED)
        d.text((arrow_x + 62, ly), ua, font=body_font, fill=INK)

    # Column 2: Meeting tools — record/mark/stop live on RAISE + the left-hand
    # bottom row (X/C/V); the zsh transcribe aliases (which now also auto-extract
    # on-screen frames from the recorded video) round it out.
    section_header("MEETING TOOLS  · KEYS + ZSH", col2_x)
    meeting = [
        ("RAISE+X",                  "start recording"),
        ("RAISE+C",                  "mark — grab screenshot"),
        ("RAISE+V",                  "stop recording"),
        ("meeting-transcribe-last",  "transcribe · auto-frames"),
        ("meeting-transcribe-video", "transcribe a video file"),
    ]
    cmd_col_w = max(d.textlength(c, font=cmd_font) for c, _ in meeting) + 16
    for i, (cmd, desc) in enumerate(meeting):
        ly = body_y + i * 20
        d.text((col2_x, ly), cmd, font=cmd_font, fill=INK)
        d.text((col2_x + cmd_col_w, ly + 1), desc, font=desc_font, fill=MUTED)

    # Column 3: MODELS · OPENROUTER — quiet metadata. Smaller fonts, dim ink.
    section_header("MODELS  · OPENROUTER", col3_x, color=MUTED)
    models = [
        ("meeting  ", "gemini-3.1-pro-preview"),
        ("dictation", "gemini-3-flash-preview"),
    ]
    quiet_label_font = F(MONO_BOLD, 12)
    quiet_desc_font = F(MONO, 11)
    for i, (label, model) in enumerate(models):
        ly = body_y + i * 18
        d.text((col3_x, ly), label, font=quiet_label_font, fill=INK_DIM)
        label_w = d.textlength(label, font=quiet_label_font)
        d.text((col3_x + label_w + 8, ly + 1), "·  " + model, font=quiet_desc_font, fill=MUTED)

    if openrouter_usage is not None:
        used, total = openrouter_usage
        spend_y = body_y + len(models) * 18 + 4
        d.text((col3_x, spend_y),
               f"${used:.2f} used  ·  ${total - used:.2f} left",
               font=quiet_desc_font, fill=MUTED)

    # Column 4: ADJUST mini-grid — quiet metadata. Keys use the secondary
    # palette (recessed slate) instead of bright cobalt; labels in dim ink.
    section_header("ADJUST  · L+R", col4_x, color=MUTED)
    adj_keys = [
        ("CLR", "mod"), ("1", "mod"),   ("2", "mod"),   ("3", "mod"),   ("4", "mod"),   ("5", "mod"),
        ("PWR", "mod"), ("HUD", "mod"), ("HUI", "mod"), ("SAD", "mod"), ("SAI", "mod"), ("EFF", "mod"),
        (None, "trans"),("BRD", "mod"), ("BRI", "mod"), (None, "trans"),(None, "trans"),(None, "trans"),
    ]
    mw, mh, mg = 28, 18, 2
    grid_y = body_y + 2
    for i, (lab, kind) in enumerate(adj_keys):
        row, col = i // 6, i % 6
        kx = col4_x + col * (mw + mg)
        ky = grid_y + row * (mh + mg)
        if kind == "mod":
            # Quieter than MOD_BG cobalt — recessed slate so the grid reads
            # as a pictogram, not as bright primary keys.
            bg, border, text_color = SECONDARY_KEY_BG, SECONDARY_KEY_BORDER, INK_DIM
        else:
            bg, border, text_color = KEY_TRANS, KEY_TRANS_BORDER, INK_TRANS
        d.rounded_rectangle([kx, ky, kx + mw, ky + mh], radius=3,
                            fill=bg, outline=border, width=1)
        if lab:
            tw = d.textlength(lab, font=mini_font)
            d.text((kx + (mw - tw) / 2, ky + 4), lab, font=mini_font, fill=text_color)

    # Column 5: Legend — single skinny column on the far right.
    section_header("LEGEND", col5_x, color=MUTED)
    swatches = [
        ("Normal", KEY_BG, KEY_BORDER),
        ("Mod",    MOD_BG, MOD_BORDER),
        ("Thumb",  THUMB_BG, THUMB_BORDER),
        ("Combo",  COMBO_BG, COMBO_BORDER),
        ("Trans",  KEY_TRANS, KEY_TRANS_BORDER),
    ]
    sw = 12
    for i, (name, bg, border) in enumerate(swatches):
        sy = body_y + i * 17
        d.rounded_rectangle([col5_x, sy, col5_x + sw, sy + sw], radius=3,
                            fill=bg, outline=border, width=1)
        d.text((col5_x + sw + 6, sy - 1), name, font=label_font, fill=INK_DIM)
    # Hold-word entry — amber sample word instead of a colour swatch.
    hy = body_y + len(swatches) * 17
    sample = "ALT"
    sample_font = F(MONO_BOLD, 9)
    d.text((col5_x, hy), sample, font=sample_font, fill=AMBER)
    sample_w = d.textlength(sample, font=sample_font)
    d.text((col5_x + sample_w + 6, hy - 1), "= hold for mod", font=label_font, fill=INK_DIM)


def draw_signature(canvas):
    d = ImageDraw.Draw(canvas)
    f = F(MONO, 10)
    text = "lily58 · zmk · 2026"
    tw = d.textlength(text, font=f)
    d.text((W - tw - 30, H - 22), text, font=f, fill=MUTED)


def main():
    canvas = Image.new("RGB", (W, H), BG)

    # Subtle directional lighting
    rgba = canvas.convert("RGBA")
    rgba = soft_glow(rgba, -100, -60, 760, AMBER, 30)
    rgba = soft_glow(rgba, W + 200, H + 100, 850, (90, 130, 220), 24)
    canvas = rgba.convert("RGB")

    draw_header(canvas)

    # 2x2 grid of layer panels — slightly shorter to leave room for richer footer
    panels_top = 168
    panels_bottom = 884
    panel_gap_x = 22
    panel_gap_y = 22
    PAD_X = 40
    panel_w = (W - 2 * PAD_X - panel_gap_x) // 2
    panel_h = (panels_bottom - panels_top - panel_gap_y) // 2

    for i, (num, name, desc, bindings) in enumerate(LAYERS_DATA):
        col = i % 2
        row = i // 2
        # Bottom row (LOWER, RAISE) renders as visually recessed reference,
        # letting BASE EN/UA on top read as the primary focus.
        px = PAD_X + col * (panel_w + panel_gap_x)
        py = panels_top + row * (panel_h + panel_gap_y)
        draw_layer_panel(canvas, px, py, panel_w, panel_h, num, name, desc, bindings,
                         secondary=(row == 1))

    draw_footer(canvas, panels_bottom + 22, openrouter_usage=fetch_openrouter_usage())
    draw_signature(canvas)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT, "PNG", optimize=True)
    print(f"Saved: {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
