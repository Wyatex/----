# -*- coding: utf-8 -*-
"""
Generate an animated ASS subtitle file with:
- Exact centered non-negative vector shapes (no libass negative-coord offset!)
- Character-by-character particle gather-in & wind-dissolve-out effects
- Fluttering butterflies, gliding whale + bubbles, and expanding water ripples
for 《蝴蝶与鲸》 (1344x768).
"""
import re
import random
from pathlib import Path

LRC_PATH = Path(r"D:\project\视频\蝴蝶与鲸\hdyj\歌词.lrc")
ASS_PATH = Path(r"D:\project\视频\蝴蝶与鲸\hdyj\蝴蝶与鲸_01-11.ass")
MAX_DURATION = 90.125

PLAY_RES_X = 1344
PLAY_RES_Y = 768

# ALL vector shapes use strictly NON-NEGATIVE coordinates so libass \an5 centers them accurately!

# 1) Delicate butterfly silhouette (48x38)
BUTTERFLY_SHAPE = (
    "m 24 16 "
    "b 20 4 2 0 0 12 "
    "b -2 20 10 24 18 22 "
    "b 8 26 4 36 14 38 "
    "b 20 39 23 30 24 24 "
    "b 25 30 28 39 34 38 "
    "b 44 36 40 26 30 22 "
    "b 38 24 50 20 48 12 "
    "b 46 0 28 4 24 16"
)

# 2) Cute dreamy whale silhouette facing right (68x28)
WHALE_SHAPE = (
    "m 18 16 "
    "b 18 4 32 0 48 2 "
    "b 60 4 68 12 68 20 "
    "b 68 26 60 28 48 27 "
    "b 36 26 26 24 18 21 "
    "b 12 24 6 28 2 26 "
    "b 6 20 8 17 11 16 "
    "b 7 14 2 10 0 4 "
    "b 6 5 12 11 18 16"
)

# 3) Four-point sparkle star (20x20)
STAR_SHAPE = (
    "m 10 0 "
    "b 11 7 13 9 20 10 "
    "b 13 11 11 13 10 20 "
    "b 9 13 7 11 0 10 "
    "b 7 9 9 7 10 0"
)

# 4) Soft glowing dust / particle orb (12x12)
ORB_SHAPE = (
    "m 6 0 "
    "b 9 0 12 3 12 6 "
    "b 12 9 9 12 6 12 "
    "b 3 12 0 9 0 6 "
    "b 0 3 3 0 6 0"
)

# 5) Elliptical water ripple ring (100x20, outline-only via \1a&HFF&)
RIPPLE_SHAPE = (
    "m 50 0 "
    "b 78 0 100 4 100 10 "
    "b 100 16 78 20 50 20 "
    "b 22 20 0 16 0 10 "
    "b 0 4 22 0 50 0"
)

# 6) Tapered glowing horizontal divider line (320x4, strictly non-negative -> exact center!)
LINE_SHAPE = "m 0 2 l 160 0 l 320 2 l 160 4"


def fmt_time(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def parse_lrc(path: Path):
    lines = []
    pat = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\](.*)")
    for raw in path.read_text(encoding="utf-8").splitlines():
        m = pat.match(raw.strip())
        if not m:
            continue
        t = int(m.group(1)) * 60 + float(m.group(2))
        text = m.group(3).strip()
        lines.append((t, text))
    return lines


def detect_theme(text: str, t: float) -> str:
    has_whale = any(k in text for k in ("鲸", "海", "游", "搁浅", "潮", "涟漪", "跃"))
    has_bfly = any(k in text for k in ("蝶", "夏", "宿命", "风", "梦", "约定", "频率"))
    if has_whale and has_bfly:
        return "dual"
    if has_whale:
        return "whale"
    if has_bfly:
        return "butterfly"
    return "dual" if t >= 50.0 else "butterfly"


def make_butterfly_events(start: float, end: float, x0: float, y0: float, x1: float, y1: float,
                          color_bgr: str, glow_bgr: str, scale: int = 85, layer: int = 4):
    dur_ms = max(600, int((end - start) * 1000))
    flap_step = 260
    flaps = []
    cur = 0
    narrow = True
    while cur < dur_ms:
        nxt = min(dur_ms, cur + flap_step)
        sx = int(scale * (0.35 if narrow else 1.05))
        flaps.append(f"\\t({cur},{nxt},\\fscx{sx})")
        narrow = not narrow
        cur = nxt
    flap_str = "".join(flaps)
    rot0 = random.randint(-20, 16)
    rot1 = rot0 + random.randint(-14, 14)
    tags = (
        f"{{\\an5\\p1\\bord2\\shad0\\blur4"
        f"\\1c&H{color_bgr}&\\3c&H{glow_bgr}&\\1a&H28&\\3a&H60&"
        f"\\fscx{scale}\\fscy{scale}\\frz{rot0}"
        f"\\move({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f},0,{dur_ms})"
        f"\\t(0,{dur_ms},\\frz{rot1})"
        f"\\fad(360,460){flap_str}}}"
    )
    return f"Dialogue: {layer},{fmt_time(start)},{fmt_time(end)},FX,,0,0,0,,{tags}{BUTTERFLY_SHAPE}"


def make_whale_events(start: float, end: float, x0: float, y0: float, x1: float, y1: float,
                      scale: int = 85, layer: int = 4):
    dur_ms = max(800, int((end - start) * 1000))
    events = []
    tags = (
        f"{{\\an5\\p1\\bord2.5\\shad0\\blur5"
        f"\\1c&HFFE8B5&\\3c&HFF9E4A&\\1a&H35&\\3a&H55&"
        f"\\fscx{scale}\\fscy{scale}\\frz-4"
        f"\\move({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f},0,{dur_ms})"
        f"\\t(0,{dur_ms // 2},\\frz4)\\t({dur_ms // 2},{dur_ms},\\frz-3)"
        f"\\fad(420,480)}}"
    )
    events.append(f"Dialogue: {layer},{fmt_time(start)},{fmt_time(end)},FX,,0,0,0,,{tags}{WHALE_SHAPE}")

    for i in range(3):
        b_start = start + 0.15 + i * 0.35
        b_end = min(end + 0.2, b_start + 1.45)
        if b_start >= end:
            break
        bx = x0 + (x1 - x0) * (0.2 + i * 0.25) + random.randint(-10, 10)
        by = y0 + random.randint(-6, 6)
        b_scale = random.randint(40, 70)
        b_dur = int((b_end - b_start) * 1000)
        b_tags = (
            f"{{\\an5\\p1\\bord1.5\\shad0\\blur2"
            f"\\1c&HFFF6E0&\\3c&HFFCA7A&\\1a&H95&\\3a&H30&"
            f"\\fscx{b_scale}\\fscy{b_scale}"
            f"\\move({bx:.0f},{by:.0f},{bx + random.randint(-10, 14):.0f},{by - random.randint(35, 62):.0f},0,{b_dur})"
            f"\\fad(220,420)}}"
        )
        events.append(f"Dialogue: {layer},{fmt_time(b_start)},{fmt_time(b_end)},FX,,0,0,0,,{b_tags}{ORB_SHAPE}")
    return events


def make_ripple_event(start: float, cx: float, cy: float, color_bgr: str, dur: float = 1.6, layer: int = 2):
    end = min(MAX_DURATION, start + dur)
    dur_ms = max(400, int((end - start) * 1000))
    tags = (
        f"{{\\an5\\p1\\bord1.8\\shad0\\blur3"
        f"\\1a&HFF&\\3c&H{color_bgr}&\\3a&H45&"
        f"\\pos({cx:.0f},{cy:.0f})\\fscx50\\fscy50"
        f"\\t(0,{dur_ms},\\fscx230\\fscy230\\3a&HFF&)"
        f"\\fad(120,0)}}"
    )
    return f"Dialogue: {layer},{fmt_time(start)},{fmt_time(end)},FX,,0,0,0,,{tags}{RIPPLE_SHAPE}"


def make_char_particle_lyric(t: float, end_t: float, text: str, cx: float, cy: float,
                             is_chorus: bool, glow_col: str, outline_col: str, fx_colors: list[str]):
    """
    Character-by-character particle gather-in + luminous dissolve-out:
    - Each char materializes from soft light while 3 micro-particles converge into it.
    - Before ending, each char dissolves into soft light while 3-4 glowing particles drift away on the wind.
    """
    events = []
    chars = list(text)
    n = len(chars)
    if n == 0:
        return events

    step = 55 if is_chorus else 48
    # Narrow spaces slightly
    widths = [step * 0.45 if ch == " " else step for ch in chars]
    total_w = sum(widths)
    x_cursor = cx - total_w / 2.0

    glow_style = "ChorusGlow" if is_chorus else "LyricGlow"
    main_style = "ChorusMain" if is_chorus else "LyricMain"

    line_dur = max(0.8, end_t - t)
    # Keep stagger tight so the whole sentence reads smoothly
    stagger_in = min(0.055, (line_dur * 0.28) / max(1, n))
    stagger_out = min(0.045, (line_dur * 0.22) / max(1, n))
    gather_dur = 0.42
    dissolve_dur = 0.46

    for i, ch in enumerate(chars):
        cw = widths[i]
        char_x = x_cursor + cw / 2.0
        x_cursor += cw
        if ch.strip() == "":
            continue

        c_in = t + i * stagger_in
        # Staggered dissolve-out starting slightly before end_t
        c_out_end = min(MAX_DURATION, end_t + 0.08)
        c_out_start = max(c_in + 0.35, end_t - dissolve_dur - (n - 1 - i) * stagger_out * 0.5)
        total_ms = max(450, int((c_out_end - c_in) * 1000))
        in_ms = min(int(gather_dur * 1000), total_ms // 2)
        out_start_ms = max(in_ms + 80, int((c_out_start - c_in) * 1000))

        # 1) Character glow layer (gather from blur16 -> blur8, dissolve to blur18 + transparent)
        g_tags = (
            f"{{\\an5\\pos({char_x:.0f},{cy:.0f})\\3c&H{glow_col}&"
            f"\\alpha&HFF&\\blur16\\fscx122\\fscy122"
            f"\\t(0,{in_ms},\\alpha&H38&\\blur8\\fscx100\\fscy100)"
            f"\\t({out_start_ms},{total_ms},\\alpha&HFF&\\blur18\\fscx112\\fscy90)}}"
        )
        events.append(f"Dialogue: 1,{fmt_time(c_in)},{fmt_time(c_out_end)},{glow_style},,0,0,0,,{g_tags}{ch}")

        # 2) Character crisp main layer (slight rise on gather, gentle dissolve on exit)
        m_tags = (
            f"{{\\an5\\move({char_x:.0f},{cy + 7:.0f},{char_x:.0f},{cy:.0f},0,{in_ms})"
            f"\\3c&H{outline_col}&\\alpha&HFF&\\blur10\\fscx112\\fscy112"
            f"\\t(0,{in_ms},\\alpha&H00&\\blur1.1\\fscx100\\fscy100)"
            f"\\t({out_start_ms},{total_ms},\\alpha&HFF&\\blur12\\fscx106\\fscy94)}}"
        )
        events.append(f"Dialogue: 2,{fmt_time(c_in)},{fmt_time(c_out_end)},{main_style},,0,0,0,,{m_tags}{ch}")

        # 3) Gather-in micro-particles converging INTO this character
        p_in_count = 3 if is_chorus else 2
        for _ in range(p_in_count):
            p_start = max(0.0, c_in - random.uniform(0.18, 0.34))
            p_end = min(MAX_DURATION, c_in + random.uniform(0.18, 0.32))
            p_ms = max(180, int((p_end - p_start) * 1000))
            sx = char_x + random.randint(-46, 46)
            sy = cy + random.randint(-34, 28)
            tx = char_x + random.randint(-10, 10)
            ty = cy + random.randint(-10, 10)
            col = random.choice(fx_colors)
            shape = STAR_SHAPE if random.random() < 0.45 else ORB_SHAPE
            sc0 = random.randint(28, 55) if shape == STAR_SHAPE else random.randint(35, 65)
            p_tags = (
                f"{{\\an5\\p1\\bord1.2\\shad0\\blur2.5"
                f"\\1c&HFFFFFF&\\3c&H{col}&\\1a&H15&\\3a&H35&"
                f"\\fscx{sc0}\\fscy{sc0}"
                f"\\move({sx:.0f},{sy:.0f},{tx:.0f},{ty:.0f},0,{p_ms})"
                f"\\t(0,{p_ms},\\fscx18\\fscy18\\frz{random.randint(45,120)})"
                f"\\fad(70,130)}}"
            )
            events.append(f"Dialogue: 3,{fmt_time(p_start)},{fmt_time(p_end)},FX,,0,0,0,,{p_tags}{shape}")

        # 4) Dissolve-out micro-particles drifting away on the sea breeze FROM this character
        p_out_count = 4 if is_chorus else 3
        for _ in range(p_out_count):
            p_start = max(c_in + 0.1, c_out_start - random.uniform(0.0, 0.08))
            p_end = min(MAX_DURATION, p_start + random.uniform(0.65, 1.15))
            if p_end - p_start < 0.25:
                continue
            p_ms = int((p_end - p_start) * 1000)
            sx = char_x + random.randint(-14, 14)
            sy = cy + random.randint(-12, 12)
            # Gentle rightward + upward breeze drift
            tx = sx + random.randint(20, 78)
            ty = sy - random.randint(22, 68)
            col = random.choice(fx_colors)
            shape = STAR_SHAPE if random.random() < 0.4 else ORB_SHAPE
            sc0 = random.randint(30, 58) if shape == STAR_SHAPE else random.randint(38, 68)
            p_tags = (
                f"{{\\an5\\p1\\bord1.2\\shad0\\blur2.5"
                f"\\1c&HFFFFFF&\\3c&H{col}&\\1a&H15&\\3a&H35&"
                f"\\fscx{sc0}\\fscy{sc0}"
                f"\\move({sx:.0f},{sy:.0f},{tx:.0f},{ty:.0f},0,{p_ms})"
                f"\\t(0,{p_ms},\\fscx14\\fscy14\\frz{random.randint(60,150)})"
                f"\\fad(80,420)}}"
            )
            events.append(f"Dialogue: 3,{fmt_time(p_start)},{fmt_time(p_end)},FX,,0,0,0,,{p_tags}{shape}")

    return events


def build_ass():
    random.seed(20261124)
    raw_lines = parse_lrc(LRC_PATH)

    segments = []
    for idx, (t, text) in enumerate(raw_lines):
        if t >= MAX_DURATION:
            break
        if not text:
            continue
        nxt_t = raw_lines[idx + 1][0] if idx + 1 < len(raw_lines) else MAX_DURATION
        end_t = min(nxt_t, MAX_DURATION)
        if end_t - t > 0.25 and idx + 1 < len(raw_lines) and raw_lines[idx + 1][1]:
            end_t -= 0.08
        segments.append((t, end_t, text))

    header = f"""[Script Info]
Title: 蝴蝶与鲸 - 浣语 (BGA 粒子特效字幕)
ScriptType: v4.00+
PlayResX: {PLAY_RES_X}
PlayResY: {PLAY_RES_Y}
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TitleMain,STXingkai,84,&H00FFFFFF,&H00FFE6FF,&H00A868B8,&H80301838,0,0,0,0,100,100,10,0,1,3,1.5,5,40,40,40,1
Style: TitleSub,STKaiti,30,&H00FFF4FF,&H00FFE6FF,&H007A4A8A,&H80201028,0,0,0,0,100,100,4,0,1,2,1,5,40,40,40,1
Style: LyricGlow,STKaiti,46,&H40FFFFFF,&H00FFFFFF,&H00E8A0FF,&H00000000,-1,0,0,0,100,100,0,0,1,6,0,5,0,0,0,1
Style: LyricMain,STKaiti,46,&H00FFFFFF,&H00FFFFFF,&H006A3E6E,&H70201028,-1,0,0,0,100,100,0,0,1,2.2,1.2,5,0,0,0,1
Style: ChorusGlow,STKaiti,52,&H35FFFFFF,&H00FFFFFF,&H00F0A8FF,&H00000000,-1,0,0,0,100,100,0,0,1,7,0,5,0,0,0,1
Style: ChorusMain,STKaiti,52,&H00FFFFFF,&H00FFFFFF,&H00583268,&H70180C24,-1,0,0,0,100,100,0,0,1,2.4,1.4,5,0,0,0,1
Style: FX,Arial,20,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    cx = PLAY_RES_X // 2  # 672

    # --- Intro Title Card (00:00.50 - 00:11.40) ---
    events.append(
        "Dialogue: 1,0:00:00.50,0:00:11.40,TitleMain,,0,0,0,,"
        f"{{\\pos({cx},330)\\bord9\\blur10\\1a&H60&\\3c&HFFA8D8&\\fad(900,1100)}}蝴蝶与鲸"
    )
    events.append(
        "Dialogue: 2,0:00:00.50,0:00:11.40,TitleMain,,0,0,0,,"
        f"{{\\move({cx},340,{cx},330,0,900)\\bord2.6\\blur1\\3c&H7A4585&\\fad(900,1100)}}蝴蝶与鲸"
    )
    # Centered glowing divider line (exact center at x=672!)
    events.append(
        "Dialogue: 2,0:00:01.00,0:00:11.20,FX,,0,0,0,,"
        f"{{\\an5\\p1\\pos({cx},386)\\bord1.5\\blur3\\1c&HFFF0FF&\\3c&HFFA8E0&\\1a&H20&"
        "\\fscx10\\fscy100\\t(0,900,\\fscx125)\\fad(700,1000)}" + LINE_SHAPE
    )
    events.append(
        "Dialogue: 2,0:00:01.40,0:00:11.20,TitleSub,,0,0,0,,"
        f"{{\\pos({cx},422)\\blur1\\fad(800,1000)}}演唱：浣语"
    )
    events.append(
        "Dialogue: 2,0:00:02.98,0:00:11.20,TitleSub,,0,0,0,,"
        f"{{\\pos({cx},462)\\fs24\\fsp3\\1c&HF5E8FF&\\blur1\\fad(800,1000)}}作词 / 作曲：牡丹亭"
    )
    events.append(make_butterfly_events(0.8, 6.2, 430, 355, 510, 265, "FFD2F8", "FF78E8", scale=105, layer=4))
    events.append(make_butterfly_events(2.2, 8.8, 910, 345, 845, 250, "FFE6B0", "FFAA50", scale=82, layer=4))
    events.extend(make_whale_events(3.5, 10.8, 455, 445, 585, 415, scale=108, layer=4))

    # --- Main Lyrics with Per-Character Particle Gather-In & Dissolve-Out ---
    lyric_y = PLAY_RES_Y - 58  # 710

    for t, end_t, text in segments:
        if t < 12.0:
            continue
        is_chorus = t >= 50.0
        theme = detect_theme(text, t)

        if theme == "whale":
            glow_col = "FFB86C"
            outline_col = "7A4E22"
            fx_colors = ["FFD888", "FFB060", "FFF0C8"]
        elif theme == "butterfly":
            glow_col = "F098FF"
            outline_col = "6E347A"
            fx_colors = ["F5A8FF", "FFD0F8", "A8E8FF"]
        else:
            glow_col = "FFA8D8"
            outline_col = "683A70"
            fx_colors = ["F5A8FF", "FFD888", "FFE8A8"]

        # Per-character particle text events
        events.extend(make_char_particle_lyric(t, end_t, text, cx, lyric_y, is_chorus, glow_col, outline_col, fx_colors))

        step = 55 if is_chorus else 48
        half_w = min(460, max(120, int(len(text) * step * 0.52)))

        # Perfectly centered glowing underline during chorus
        if is_chorus:
            line_scale = min(145, max(65, int(half_w * 0.62)))
            line_tags = (
                f"{{\\an5\\p1\\pos({cx},{lyric_y + 34})\\bord1.2\\blur2.5"
                f"\\1c&HFFFFFF&\\3c&H{glow_col}&\\1a&H40&\\3a&H50&"
                f"\\fscx8\\fscy85\\t(0,450,\\fscx{line_scale})"
                f"\\fad(320,380)}}"
            )
            events.append(f"Dialogue: 2,{fmt_time(t)},{fmt_time(end_t)},FX,,0,0,0,,{line_tags}{LINE_SHAPE}")

        # Theme-specific butterfly / whale / ripple accents
        if theme in ("butterfly", "dual"):
            bx0 = cx + half_w + 22
            by0 = lyric_y - 4
            bx1 = bx0 + random.randint(45, 92)
            by1 = by0 - random.randint(40, 82)
            b_col = "FFD4FA" if theme == "butterfly" else "FFE4B8"
            b_glow = "F080FF" if theme == "butterfly" else "FFA8E8"
            events.append(make_butterfly_events(t, min(end_t + 0.3, MAX_DURATION), bx0, by0, bx1, by1,
                                                b_col, b_glow, scale=86 if is_chorus else 74, layer=4))
            if is_chorus:
                lx0 = cx - half_w - 24
                ly0 = lyric_y + 4
                events.append(make_butterfly_events(t + 0.25, min(end_t + 0.3, MAX_DURATION),
                                                    lx0, ly0, lx0 - 52, ly0 - 52,
                                                    "C8F0FF", "FFAAFF", scale=64, layer=4))

        if theme in ("whale", "dual"):
            wx0 = cx - half_w - 72
            wy0 = lyric_y - 2
            wx1 = wx0 + 48
            wy1 = wy0 - 12
            events.extend(make_whale_events(t, min(end_t + 0.2, MAX_DURATION), wx0, wy0, wx1, wy1,
                                            scale=82 if is_chorus else 72, layer=4))
            events.append(make_ripple_event(t + 0.12, cx, lyric_y + 26, "FFD088", dur=1.8, layer=2))

    ASS_PATH.write_text(header + "\n".join(events) + "\n", encoding="utf-8-sig")
    print(f"Wrote {ASS_PATH} with {len(events)} dialogue/effect events.")


if __name__ == "__main__":
    build_ass()
