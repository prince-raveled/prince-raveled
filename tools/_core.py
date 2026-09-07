"""Shared helpers: font -> SVG path, palettes, deterministic RNG."""
import os, math, random, urllib.request
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".fontcache")
GF = "https://github.com/google/fonts/raw/main/"

FONTS = {
    "display":      ("Italiana-Regular.ttf",            "ofl/italiana/Italiana-Regular.ttf"),
    "serif":        ("CormorantGaramond[wght].ttf",     "ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf"),
    "serif-italic": ("CormorantGaramond-Italic[wght].ttf","ofl/cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf"),
    "hand":         ("Caveat[wght].ttf",                "ofl/caveat/Caveat%5Bwght%5D.ttf"),
    "jp":           ("NotoSansJP[wght].ttf",            "ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf"),
}

def font_path(key):
    name, remote = FONTS[key]
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if not os.path.exists(p):
        print(f"  downloading {name} ...")
        urllib.request.urlretrieve(GF + remote, p)
    return p

_loaded = {}
def _font(key, wght):
    ck = (key, wght)
    if ck in _loaded:
        return _loaded[ck]
    f = TTFont(font_path(key))
    if wght is not None and "fvar" in f:
        from fontTools.varLib import instancer
        f = instancer.instantiateVariableFont(f, {"wght": wght})
    upem = f["head"].unitsPerEm
    _loaded[ck] = (f, f.getGlyphSet(), f.getBestCmap(), f["hmtx"], upem)
    return _loaded[ck]

def _num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")

def glyph(key, ch, size, x, y, wght=None):
    """Return (path_d, advance_without_tracking) for one character."""
    f, gs, cmap, hmtx, upem = _font(key, wght)
    gname = cmap.get(ord(ch)) or cmap.get(ord(" "))
    if gname is None:
        return "", size * 0.3
    adv = hmtx[gname][0] * size / upem
    if ch == " ":
        return "", adv
    spen = SVGPathPen(gs, ntos=_num)
    gs[gname].draw(TransformPen(spen, Transform().translate(x, y).scale(size / upem, -size / upem)))
    return spen.getCommands(), adv

def text_path(key, text, size, x=0.0, y=0.0, tracking=0.0, wght=None):
    """Whole string as one path. tracking is in em (like CSS letter-spacing/font-size)."""
    pen, parts = 0.0, []
    for ch in text:
        d, adv = glyph(key, ch, size, x + pen, y, wght)
        if d:
            parts.append(d)
        pen += adv + tracking * size
    return " ".join(parts), (pen - tracking * size if text else 0.0)

def text_width(key, text, size, tracking=0.0, wght=None):
    return text_path(key, text, size, 0, 0, tracking, wght)[1]

def letters(key, text, size, x=0.0, y=0.0, tracking=0.0, wght=None):
    """Per-character paths so each glyph can be animated on its own."""
    pen, out = 0.0, []
    for i, ch in enumerate(text):
        d, adv = glyph(key, ch, size, x + pen, y, wght)
        if d:
            out.append({"i": i, "ch": ch, "d": d, "x": x + pen, "w": adv})
        pen += adv + tracking * size
    return out, (pen - tracking * size if text else 0.0)

# ---------------------------------------------------------------- palettes
# Light values are lifted verbatim from the portfolio's CSS custom properties.
LIGHT = dict(
    name="light",
    sky_top="#f7f9ec", sky_mid="#eaf3d5", sky_low="#d7e6ad", ground="#cbdf9c",
    paper="#f7f9ec", panel="#eef4dd", panel2="#e6eece",
    ink="#1f6b26", ink2="#2f7d38", body="#3d5c38", mute="#6c8560",
    gold="#b8842c", gold_soft="rgba(184,132,44,.16)",
    line="rgba(31,107,38,.16)", line_soft="rgba(31,107,38,.08)",
    grass_a="#4f8f3e", grass_b="#3a7530", grass_c="#2b5f27",
    leaf_a="#6aa34a", leaf_b="#4d8a3a",
    glow="#f2e2a8", glow_op=".55",
    shadow="rgba(40,66,30,.16)",
    term_bg="#1d2a19", term_ink="#d7e6ad", term_dim="#8fae76",
)
DARK = dict(
    name="dark",
    sky_top="#0c1310", sky_mid="#101b13", sky_low="#152218", ground="#101a12",
    paper="#0f1711", panel="#152016", panel2="#18251a",
    ink="#8ad597", ink2="#6fbe7e", body="#a9c2a3", mute="#7c9478",
    gold="#dda85a", gold_soft="rgba(221,168,90,.14)",
    line="rgba(138,213,151,.18)", line_soft="rgba(138,213,151,.08)",
    grass_a="#2a5c31", grass_b="#1e4726", grass_c="#15331b",
    leaf_a="#3d7a44", leaf_b="#2c5f33",
    glow="#e8c98a", glow_op=".22",
    shadow="rgba(0,0,0,.5)",
    term_bg="#0a110c", term_ink="#8ad597", term_dim="#5d7d5c",
)

def rng(seed):
    return random.Random(seed)

def write(path, svg):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"  wrote {os.path.relpath(path)}  ({len(svg.encode('utf-8'))/1024:.1f} KB)")


# ---------------------------------------------------- anime scene palettes
# Cel-shaded: every surface is a flat fill plus a hard-edged shadow shape.
DAY = dict(
    name="day", night=False,
    sky_hi="#6fb7dd", sky_mid="#b7dcea", sky_low="#f2f1ce",
    orb="#fff8d8", orb_glow="#ffe9a0", orb_glow_op=".55", ray_op=".12",
    cloud="#ffffff", cloud_sh="#cfe0ec", cloud_rim="#fff3d0", cloud_op="1",
    hill_far="#a9cf83", hill_far_sh="#8fbe6b",
    hill_mid="#74b055", hill_mid_sh="#5d9c44",
    hill_near="#569338", hill_near_sh="#437c2c",
    meadow="#3f7f2d", meadow_sh="#316a24", meadow_lite="#6aa844",
    tree_hi="#67a64c", tree_mid="#4a8639", tree_dark="#356428", trunk="#5a452f",
    figure="#24301f", rim="#ffeab0",
    title="#ffffff", title_sh="rgba(24,48,24,.55)", kicker="#ffe6a2",
    accent="#b8842c", spark="#ffffff", spark_op=".9",
    band="rgba(20,44,20,.30)", band_ink="#f4f8e6", scrim="#16331a", scrim_op=".34",
    card="#f5faea", card2="#e7f1d4", card_line="rgba(31,77,34,.20)",
    card_ink="#1f4d22", card_mute="#5f7d57", card_gold="#a9761f",
    ui_leaf_hi="#67a64c", ui_leaf_mid="#4a8639", ui_leaf_dark="#356428",
    term_bg="#16240f", term_ink="#d9ecb4", term_dim="#8aa974", term_glow="#9fe07a",
)
NIGHT = dict(
    name="night", night=True,
    sky_hi="#101a3c", sky_mid="#1e2c56", sky_low="#3a4570",
    orb="#f6f2dc", orb_glow="#cfd9ff", orb_glow_op=".30", ray_op=".05",
    cloud="#39456f", cloud_sh="#2a3459", cloud_rim="#8f9ac4", cloud_op=".92",
    hill_far="#2c3a52", hill_far_sh="#253145",
    hill_mid="#223634", hill_mid_sh="#1b2a29",
    hill_near="#16281f", hill_near_sh="#101f18",
    meadow="#0f1d16", meadow_sh="#0a1610", meadow_lite="#1d3527",
    tree_hi="#1f3a29", tree_mid="#172d20", tree_dark="#102018", trunk="#20180f",
    figure="#080d0a", rim="#9fd8ff",
    title="#eef6ea", title_sh="rgba(0,0,0,.55)", kicker="#ffd98f",
    accent="#dda85a", spark="#fff3c4", spark_op="1",
    band="rgba(0,0,0,.34)", band_ink="#dfeadb", scrim="#040a16", scrim_op=".40",
    card="#101a2c", card2="#17243a", card_line="rgba(163,196,255,.18)",
    card_ink="#e7eefa", card_mute="#93a8c8", card_gold="#e8b866",
    ui_leaf_hi="#63b378", ui_leaf_mid="#458a58", ui_leaf_dark="#2b6140",
    term_bg="#080f1c", term_ink="#bfe4ff", term_dim="#6b86a8", term_glow="#7fd2ff",
)
