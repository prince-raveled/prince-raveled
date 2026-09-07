"""The key visual: a cel-shaded anime meadow, drawn entirely from vector primitives.

Light theme renders the scene at golden hour; dark theme renders the same
composition at night. Nothing here is a raster image or a traced photograph --
every hill, cloud, leaf and silhouette is generated geometry.
"""
import math, os
from _core import DAY, NIGHT, text_path, letters, rng, write, HERE

W, H = 1200, 520
SUN = (992, 122, 52)          # cx, cy, r


# --------------------------------------------------------------- geometry
def smooth(points, close_to=None):
    """A path flowing through `points` via midpoint quadratics."""
    d = f"M{points[0][0]:.1f},{points[0][1]:.1f}"
    for i in range(1, len(points) - 1):
        x, y = points[i]
        mx, my = (x + points[i + 1][0]) / 2, (y + points[i + 1][1]) / 2
        d += f" Q{x:.1f},{y:.1f} {mx:.1f},{my:.1f}"
    d += f" T{points[-1][0]:.1f},{points[-1][1]:.1f}"
    if close_to is not None:
        d += f" L{points[-1][0]:.1f},{close_to} L{points[0][0]:.1f},{close_to} Z"
    return d


def ridge(seed, y, amp, n=8):
    r = rng(seed)
    return [(-40 + (W + 80) * (i / n),
             y + r.uniform(-amp, amp) * (0.45 + 0.55 * math.sin((i / n) * 5.3)))
            for i in range(n + 1)]


def blob(cs, fill, dx=0.0, dy=0.0, ks=1.0, extra=""):
    """Union of circles -- the only honest way to draw a cumulus."""
    o = "".join(f'<circle cx="{x+dx:.1f}" cy="{y+dy:.1f}" r="{rad*ks:.1f}"/>' for x, y, rad in cs)
    return f'<g fill="{fill}"{extra}>{o}{"" }</g>'


def clip_of(cid, cs, ks=1.0, dx=0.0, dy=0.0, base=None):
    o = "".join(f'<circle cx="{x+dx:.1f}" cy="{y+dy:.1f}" r="{rad*ks:.1f}"/>' for x, y, rad in cs)
    if base:
        o += base
    return f'<clipPath id="{cid}">{o}</clipPath>'


# ------------------------------------------------------------------ cloud
def cumulus(seed, w, h):
    """Densely overlapping circles + a flat base: a cumulus, not a bunch of grapes."""
    r, out = rng(seed), []
    k = 9
    for i in range(k):                       # base row, spacing well under the radius
        t = i / (k - 1)
        out.append((-w / 2 + w * t, r.uniform(-1, 3), h * r.uniform(0.52, 0.64)))
    for i in range(5):                       # bulging crowns
        t = (i + 0.5) / 5
        out.append((-w * 0.34 + w * 0.68 * t + r.uniform(-14, 14),
                    -h * r.uniform(0.34, 0.62), h * r.uniform(0.56, 0.82)))
    for i in range(3):                       # small tufts to break the outline
        out.append((r.uniform(-w * 0.45, w * 0.45), -h * r.uniform(0.05, 0.3),
                    h * r.uniform(0.4, 0.55)))
    return out


def cloud(p, cid, cx, cy, w, h, seed, dur, delay, op="1"):
    cs = cumulus(seed, w, h)
    base = (f'<rect x="{-w/2-h*0.5:.0f}" y="{-h*0.05:.0f}" width="{w+h:.0f}" '
            f'height="{h*0.5:.0f}" rx="{h*0.22:.0f}"/>')
    return (
        f'<g transform="translate({cx},{cy})" opacity="{op}">'
        f'<g class="cloud" style="animation-duration:{dur}s;animation-delay:{delay}s">'
        f'{clip_of(cid, cs, base=base)}'
        f'{blob(cs, p["cloud_rim"], 7, -7, 1.02)}'          # sunward edge catches light
        f'{blob(cs, p["cloud_sh"], -7, 9, 1.02)}'           # shaded underside
        f'<g fill="{p["cloud"]}" fill-opacity="{p["cloud_op"]}">'
        + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}"/>' for x, y, rad in cs)
        + base + '</g>'
        f'<g clip-path="url(#{cid})">{blob(cs, p["cloud_sh"], -14, 30, 0.96)}</g>'
        f'</g></g>')


# -------------------------------------------------------------- sun / moon
def rays(p):
    cx, cy, _ = SUN
    r, wedges = rng(3), []
    for i in range(9):                       # a fan spilling down and to the left
        a = 96 + i * (112 / 8) + r.uniform(-4, 4)
        half, ln = r.uniform(1.4, 4.0), r.uniform(320, 560)
        a0, a1 = math.radians(a - half), math.radians(a + half)
        wedges.append(f'<path d="M0,0 L{ln*math.cos(a0):.0f},{ln*math.sin(a0):.0f} '
                      f'L{ln*math.cos(a1):.0f},{ln*math.sin(a1):.0f} Z"/>')
    return (f'<g transform="translate({cx},{cy})">'
            f'<g class="rays" fill="url(#rayg)">{"".join(wedges)}</g></g>')


def orb(p):
    cx, cy, rr = SUN
    o = [f'<circle class="glow" cx="{cx}" cy="{cy}" r="{rr*4.0:.0f}" fill="url(#halo)"/>']
    if p["night"]:
        o.append(f'<mask id="moonm"><circle cx="{cx}" cy="{cy}" r="{rr}" fill="#fff"/>'
                 f'<circle cx="{cx+rr*0.52:.0f}" cy="{cy-rr*0.34:.0f}" r="{rr*0.90:.0f}" '
                 f'fill="#000"/></mask>')
        o.append(f'<g mask="url(#moonm)"><circle cx="{cx}" cy="{cy}" r="{rr}" '
                 f'fill="{p["orb"]}"/>')
        for dx, dy, cr in ((-20, 14, 8), (-9, 27, 5), (-29, -10, 4)):
            o.append(f'<circle cx="{cx+dx}" cy="{cy+dy}" r="{cr}" fill="{p["sky_mid"]}" '
                     f'fill-opacity=".28"/>')
        o.append('</g>')
    else:
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="{p["orb"]}"/>')
    return "".join(o)


# ----------------------------------------------------------------- flyers
def birds(p, seed=17, n=8):
    r, out = rng(seed), []
    for _ in range(n):
        s, y = r.uniform(0.45, 1.1), r.uniform(90, 250)
        dur = r.uniform(26, 46)
        out.append(
            f'<g transform="translate({W + 90},{y:.0f})">'
            f'<g class="fly" style="animation-duration:{dur:.0f}s;'
            f'animation-delay:{-r.uniform(0, dur):.0f}s;--dy:{r.uniform(-40,52):.0f}px">'
            f'<g class="flap" style="animation-duration:{r.uniform(.9,1.5):.2f}s" '
            f'transform="scale({s:.2f})">'
            f'<path d="M0,0 Q7,-8 14,-1 Q21,-8 28,0" fill="none" '
            f'stroke="{p["figure"] if not p["night"] else p["rim"]}" stroke-opacity=".55" '
            f'stroke-width="2.2" stroke-linecap="round"/></g></g></g>')
    return "".join(out)


def stars(p, seed=91, n=110):
    r, out = rng(seed), []
    for _ in range(n):
        out.append(f'<circle class="tw" cx="{r.uniform(0,W):.0f}" cy="{r.uniform(4,350):.0f}" '
                   f'r="{r.uniform(.7,2.2):.1f}" fill="{p["spark"]}" '
                   f'style="animation-duration:{r.uniform(2.4,6):.1f}s;'
                   f'animation-delay:{-r.uniform(0,6):.1f}s"/>')
    for _ in range(8):
        x, y, k = r.uniform(40, W - 40), r.uniform(20, 300), r.uniform(5, 9)
        out.append(f'<path class="tw" d="M{x:.0f},{y-k:.0f} Q{x:.0f},{y:.0f} {x+k:.0f},{y:.0f} '
                   f'Q{x:.0f},{y:.0f} {x:.0f},{y+k:.0f} Q{x:.0f},{y:.0f} {x-k:.0f},{y:.0f} '
                   f'Q{x:.0f},{y:.0f} {x:.0f},{y-k:.0f}Z" fill="{p["spark"]}" '
                   f'style="animation-duration:{r.uniform(3,7):.1f}s;'
                   f'animation-delay:{-r.uniform(0,7):.1f}s"/>')
    return "".join(out)


def fireflies(p, seed=55, n=30):
    r, out = rng(seed), []
    for _ in range(n):
        out.append(
            f'<g transform="translate({r.uniform(20,W-20):.0f},{r.uniform(388,H-8):.0f})">'
            f'<g class="fly2" style="animation-duration:{r.uniform(7,16):.1f}s;'
            f'animation-delay:{-r.uniform(0,16):.1f}s;--fx:{r.uniform(-70,70):.0f}px;'
            f'--fy:{r.uniform(-52,-16):.0f}px">'
            f'<circle r="7" fill="{p["spark"]}" fill-opacity=".12"/>'
            f'<circle r="2.1" fill="{p["spark"]}"/></g></g>')
    return "".join(out)


# ------------------------------------------------------------------- tree
CANOPY = [(0, -112, 46), (-44, -100, 36), (46, -102, 35), (-24, -150, 38),
          (28, -146, 35), (0, -176, 29), (-70, -80, 27), (70, -82, 26),
          (0, -86, 44), (-52, -132, 25), (54, -130, 24)]


def tree(p, x, ybase, s=1.0, tag="t1"):
    g = [f'<g transform="translate({x},{ybase}) scale({s})">']
    g.append(f'<ellipse cx="-6" cy="2" rx="54" ry="8" fill="{p["hill_near_sh"]}" '
             f'fill-opacity=".45"/>')
    g.append(f'<path d="M-11,0 C-9,-26 -10,-44 -15,-62 L-6,-66 C-3,-52 -2,-40 -2,-28 '
             f'L3,-28 C3,-42 5,-56 11,-70 L18,-64 C12,-48 10,-30 11,0 Z" fill="{p["trunk"]}"/>')
    g.append(f'<path d="M-5,-52 C-18,-62 -30,-72 -40,-84 L-34,-89 C-24,-77 -13,-66 -3,-58 Z" '
             f'fill="{p["trunk"]}"/>')
    g.append(f'<path d="M5,-58 C16,-70 28,-80 39,-88 L43,-82 C32,-74 20,-64 10,-54 Z" '
             f'fill="{p["trunk"]}"/>')
    g.append(clip_of(f"cnp{tag}", CANOPY))
    g.append(blob(CANOPY, p["tree_mid"]))
    g.append(f'<g clip-path="url(#cnp{tag})">'
             + blob(CANOPY, p["tree_dark"], -22, 30, 0.98)
             + blob(CANOPY, p["tree_hi"], 20, -22, 0.60) + '</g>')
    for cx, cy, cr in CANOPY:                # scalloped leaf edge, the Ghibli tell
        g.append(f'<circle cx="{cx}" cy="{cy}" r="{cr}" fill="none" '
                 f'stroke="{p["tree_dark"]}" stroke-opacity=".22" stroke-width="1.6"/>')
    g.append("</g>")
    return "".join(g)


def far_trees(p, seed, ybase, n, fill, op, x0, x1, s=0.16):
    """Distant tree line -- reads as depth, costs almost nothing."""
    r, out = rng(seed), []
    for i in range(n):
        x = x0 + (x1 - x0) * (i + r.random() * 0.8) / n
        k = s * r.uniform(0.75, 1.35)
        out.append(f'<g transform="translate({x:.0f},{ybase + r.uniform(-5,5):.0f}) scale({k:.2f})">'
                   + blob(CANOPY, fill, 0, 0, 1, f' fill-opacity="{op}"')
                   + f'<rect x="-9" y="-10" width="18" height="34" fill="{fill}" '
                     f'fill-opacity="{op}"/></g>')
    return "".join(out)


# ----------------------------------------------------------------- figure
def figure(p, x, ybase, s=1.0):
    """Someone standing in the wind with a camera. Read as a silhouette, so the
    outline does all the work: hair off the shoulder, coat hem lifting, feet apart."""
    body = (
        # head + neck
        '<path d="M-8.4,-92.5 C-8.4,-101 -1.6,-105.5 3.4,-104.5 C9,-103.4 11.6,-98.4 11,-92 '
        'C10.6,-87.6 9,-84.4 6.6,-82.4 L7,-77 L-3,-77 L-2.6,-83 C-6,-85 -8.4,-88 -8.4,-92.5 Z"/>'
        # hair: mass over the crown, streaming to the right on the wind
        '<path d="M-10,-95 C-11.6,-105.6 -2.6,-112 5,-110.6 C13.6,-109 17,-101.6 15.4,-94 '
        'C21,-95.6 27,-94.4 33,-91 C25,-90.6 18.6,-88.4 13.4,-84.6 C15,-90 14,-94.6 11.4,-97 '
        'C9,-99.2 4,-100 -0.6,-98.6 C-4.4,-97.4 -7.4,-96 -10,-95 Z"/>'
        '<path d="M-9,-94 C-12.6,-88 -13.6,-82 -12.6,-76 L-7,-79 C-8.4,-84 -8.6,-89 -7.4,-93 Z"/>'
        # torso / coat, hem flaring downwind
        '<path d="M-9,-79 C-13,-70 -14.4,-58 -13.6,-45 C-6,-42.4 4,-42.4 12,-45 '
        'C13,-58 11.6,-70 8,-79 Z"/>'
        '<path d="M11,-53 C19,-51.6 26,-48 32,-42.6 C23,-45 16,-45.6 11.6,-45.4 Z"/>'
        # arms
        '<path d="M-9.4,-76 C-14.6,-66 -16.4,-56 -15.4,-46.6 L-10.6,-47.6 '
        'C-11.4,-56.4 -10.4,-65 -7.4,-73 Z"/>'
        '<path d="M8,-76 C13.4,-67 15.4,-58.6 14.6,-50.6 L9.6,-51.6 '
        'C10.2,-59 9,-66.4 6.4,-73.4 Z"/>'
        # legs
        '<path d="M-11.6,-45 C-12.6,-30 -11.6,-14 -10.4,0 L-2.6,0 C-2.6,-15 -2.4,-30 -3,-45 Z"/>'
        '<path d="M2,-45 C1.6,-30 2.6,-14 4,0 L11.4,0 C11.6,-15 11,-30 10,-45 Z"/>'
        '<path d="M-12.6,0 L-1.4,0 L-1.4,3 L-13.6,3 Z"/>'
        '<path d="M3,0 L12.6,0 L13.6,3 L2.6,3 Z"/>'
        # camera at the hip + strap across the chest
        '<path d="M12,-60 L24,-60 L25,-51 L11,-51 Z"/>'
        '<circle cx="18" cy="-55.5" r="3.4"/>'
        '<path d="M-8,-76 C0,-71 8,-70 14,-61" fill="none" stroke-width="2.6"/>'
    )
    return (f'<g transform="translate({x},{ybase}) scale({s})">'
            f'<g fill="{p["rim"]}" stroke="{p["rim"]}" fill-opacity=".9" '
            f'transform="translate(3,-3)">{body}</g>'
            f'<g fill="{p["figure"]}" stroke="{p["figure"]}">{body}</g></g>')


# --------------------------------------------------------------- ground fx
def tufts(p, seed, ybase, count, hmin, hmax, fill, op, x0=-20, x1=W + 20):
    r, out = rng(seed), []
    for i in range(count):
        x = x0 + (x1 - x0) * (i + r.random() * 0.9) / count
        h = r.uniform(hmin, hmax)
        lean = r.uniform(-0.45, 0.45) * h
        w = max(1.2, h * 0.05)
        out.append(
            f'<g transform="translate({x:.0f},{ybase + r.uniform(-4,8):.0f})">'
            f'<path class="blade" d="M{-w:.1f},0 Q{lean*0.2:.1f},{-h*0.5:.1f} '
            f'{lean:.1f},{-h:.1f} Q{lean*0.05:.1f},{-h*0.48:.1f} {w:.1f},0 Z" '
            f'fill="{fill}" fill-opacity="{op}" '
            f'style="animation-duration:{r.uniform(3.2,6.4):.1f}s;'
            f'animation-delay:{-r.uniform(0,7):.1f}s"/></g>')
    return "".join(out)


def wind(p, seed=8, n=10):
    r, out = rng(seed), []
    for _ in range(n):
        y, ln = r.uniform(398, H - 10), r.uniform(130, 320)
        dur = r.uniform(6, 13)
        out.append(
            f'<g transform="translate(-{ln+90:.0f},{y:.0f})">'
            f'<g class="gust" style="animation-duration:{dur:.1f}s;'
            f'animation-delay:{-r.uniform(0,dur):.1f}s">'
            f'<path d="M0,0 Q{ln*0.5:.0f},-8 {ln:.0f},0" fill="none" '
            f'stroke="{p["meadow_lite"]}" stroke-opacity=".5" stroke-width="2.6" '
            f'stroke-linecap="round"/></g></g>')
    return "".join(out)


def petals(p, seed=61, n=18):
    r, out = rng(seed), []
    col = p["spark"] if p["night"] else p["cloud"]
    for _ in range(n):
        y, dur, sc = r.uniform(60, 480), r.uniform(16, 34), r.uniform(0.5, 1.2)
        out.append(
            f'<g transform="translate({W+50},{y:.0f})">'
            f'<g class="drift" style="animation-duration:{dur:.0f}s;'
            f'animation-delay:{-r.uniform(0,dur):.0f}s;--dy:{r.uniform(60,190):.0f}px;'
            f'--sp:{r.choice([-1,1])*r.uniform(240,620):.0f}deg">'
            f'<ellipse rx="{5.4*sc:.1f}" ry="{2.6*sc:.1f}" fill="{col}" '
            f'fill-opacity="{r.uniform(.35,.8):.2f}"/></g></g>')
    return "".join(out)


STYLE = """<style>
.cloud{animation-name:cl;animation-timing-function:linear;animation-iteration-count:infinite}
@keyframes cl{from{transform:translateX(0)}to{transform:translateX(-1500px)}}
.rays{animation:ray 11s ease-in-out infinite}
@keyframes ray{0%,100%{opacity:.75;transform:rotate(-1.6deg)}50%{opacity:1;transform:rotate(1.6deg)}}
.glow{animation:gl 8s ease-in-out infinite;transform-box:fill-box;transform-origin:50% 50%}
@keyframes gl{0%,100%{opacity:.82;transform:scale(1)}50%{opacity:1;transform:scale(1.06)}}
.blade{animation-name:sway;animation-timing-function:ease-in-out;
 animation-iteration-count:infinite;transform-box:fill-box;transform-origin:50% 100%}
@keyframes sway{0%,100%{transform:rotate(-3deg)}50%{transform:rotate(3.6deg)}}
.fly{animation-name:fl;animation-timing-function:linear;animation-iteration-count:infinite}
@keyframes fl{from{transform:translate(0,0)}to{transform:translate(-1380px,var(--dy))}}
.flap{animation-name:fp;animation-timing-function:ease-in-out;animation-iteration-count:infinite;
 transform-box:fill-box;transform-origin:50% 100%}
@keyframes fp{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.45)}}
.tw{animation-name:tw;animation-timing-function:ease-in-out;animation-iteration-count:infinite}
@keyframes tw{0%,100%{opacity:.2}50%{opacity:1}}
.fly2{animation-name:ff;animation-timing-function:ease-in-out;animation-iteration-count:infinite}
@keyframes ff{0%{transform:translate(0,0);opacity:0}
 20%,70%{opacity:1}100%{transform:translate(var(--fx),var(--fy));opacity:0}}
.gust{animation-name:gu;animation-timing-function:ease-in;animation-iteration-count:infinite}
@keyframes gu{0%{transform:translateX(0);opacity:0}
 15%,60%{opacity:.85}100%{transform:translateX(1560px);opacity:0}}
.drift{animation-name:dr;animation-timing-function:linear;animation-iteration-count:infinite}
@keyframes dr{from{transform:translate(0,0) rotate(0)}
 to{transform:translate(-1330px,var(--dy)) rotate(var(--sp))}}
.ltr{animation:rise 1s cubic-bezier(.22,.68,.28,1) both}
@keyframes rise{from{opacity:0;transform:translateY(28px)}to{opacity:1;transform:translateY(0)}}
.fade{animation:fin 1.2s ease both}
@keyframes fin{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
</style>"""


def build(p):
    o = []
    A = o.append
    n = p["night"]
    cx, cy, _ = SUN

    A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
      f'role="img" aria-label="Prince Kumar — an illustrated meadow at '
      f'{"night" if n else "golden hour"}">')
    A(f'''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0%" stop-color="{p['sky_hi']}"/><stop offset="52%" stop-color="{p['sky_mid']}"/>
 <stop offset="100%" stop-color="{p['sky_low']}"/></linearGradient>
<radialGradient id="halo"><stop offset="0%" stop-color="{p['orb_glow']}" stop-opacity="{p['orb_glow_op']}"/>
 <stop offset="55%" stop-color="{p['orb_glow']}" stop-opacity="{float(p['orb_glow_op'])*.34:.2f}"/>
 <stop offset="100%" stop-color="{p['orb_glow']}" stop-opacity="0"/></radialGradient>
<radialGradient id="rayg" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="540">
 <stop offset="0%" stop-color="{p['orb']}" stop-opacity="{float(p['ray_op'])*1.7:.3f}"/>
 <stop offset="52%" stop-color="{p['orb']}" stop-opacity="{float(p['ray_op'])*.85:.3f}"/>
 <stop offset="100%" stop-color="{p['orb']}" stop-opacity="0"/></radialGradient>
<filter id="ts" x="-25%" y="-25%" width="150%" height="150%">
 <feDropShadow dx="0" dy="3" stdDeviation="6" flood-color="{p['title_sh']}"/></filter>
<linearGradient id="scrim" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0%" stop-color="{p['scrim']}" stop-opacity="{p['scrim_op']}"/>
 <stop offset="58%" stop-color="{p['scrim']}" stop-opacity="{float(p['scrim_op'])*.45:.3f}"/>
 <stop offset="100%" stop-color="{p['scrim']}" stop-opacity="0"/></linearGradient>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>''')
    A(STYLE)
    A('<g clip-path="url(#frame)">')

    A(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    if n:
        A(stars(p))
    A(orb(p))
    A(rays(p))

    # clouds kept clear of the title block on the left
    A(cloud(p, "cA", 322, 44, 168, 34, 21, 165, -40, ".78"))
    A(cloud(p, "cB", 1070, 58, 250, 52, 33, 130, -20))
    A(cloud(p, "cC", 660, 112, 320, 76, 42, 200, -80))
    A(cloud(p, "cD", 830, 244, 230, 34, 57, 118, -34, ".72"))
    A(cloud(p, "cE", 1150, 206, 160, 26, 66, 145, -100, ".62"))

    if not n:
        A(birds(p))

    # ---- land: cel-shaded bands, each with a fold shadow under its crest
    for seed, y, amp, fill, sh, sy in (
            (101, 366, 12, p["hill_far"], p["hill_far_sh"], 26),
            (202, 402, 16, p["hill_mid"], p["hill_mid_sh"], 32),
            (303, 444, 14, p["hill_near"], p["hill_near_sh"], 28)):
        A(f'<path d="{smooth(ridge(seed, y, amp), H + 10)}" fill="{fill}"/>')
        if seed == 101:
            A(far_trees(p, 71, y + 10, 26, p["hill_far_sh"], ".85", -20, W + 20, 0.15))
        if seed == 202:
            A(far_trees(p, 72, y + 12, 14, p["hill_mid_sh"], ".9", 60, W - 40, 0.24))
        A(f'<path d="{smooth([(x, yy + sy) for x, yy in ridge(seed + 7, y, amp * .7)], H + 10)}" '
          f'fill="{sh}"/>')
        if seed == 303:
            A(tree(p, 1020, 448, 1.05))
            A(figure(p, 852, 452, 1.22))

    A(tufts(p, 404, 450, 74, 8, 20, p["hill_near_sh"], ".7"))

    A(f'<path d="{smooth(ridge(404, 478, 11), H + 10)}" fill="{p["meadow"]}"/>')
    A(wind(p))
    A(tufts(p, 505, H + 2, 96, 20, 54, p["meadow_sh"], ".85"))
    A(tufts(p, 606, H + 6, 48, 34, 80, p["meadow_sh"], "1"))
    if n:
        A(fireflies(p))
    A(petals(p))

    A(f'<rect width="640" height="{H}" fill="url(#scrim)"/>')

    # ---- title card
    d, _ = text_path("serif-italic", "Bioinformatics  ·  Data  ·  Visual Craft",
                     27, 76, 122, 0.05, wght=600)
    A(f'<g class="fade" style="animation-delay:.2s" filter="url(#ts)">'
      f'<path d="{d}" fill="{p["kicker"]}"/></g>')

    for row, (word, base) in enumerate((("PRINCE", 214), ("KUMAR", 300))):
        gl, _ = letters("display", word, 92, 76, base, 0.062)
        for j, g in enumerate(gl):
            A(f'<g class="ltr" style="animation-delay:{.4 + row*.3 + j*.055:.2f}s" '
              f'filter="url(#ts)"><path d="{g["d"]}" fill="{p["title"]}"/></g>')

    jd, jw = text_path("jp", "プリンス・クマール", 20, 78, 340, 0.2, wght=500)
    A(f'<g class="fade" style="animation-delay:1.5s" filter="url(#ts)">'
      f'<path d="{jd}" fill="{p["title"]}" fill-opacity=".8"/>'
      f'<rect x="{78+jw+16}" y="333" width="132" height="1.4" fill="{p["title"]}" '
      f'fill-opacity=".45"/></g>')

    A('</g>')
    A(f'<rect x=".8" y=".8" width="{W-1.6}" height="{H-1.6}" rx="16" fill="none" '
      f'stroke="{p["figure"] if not n else p["rim"]}" stroke-opacity=".2" stroke-width="1.6"/>')
    A("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    dest = os.path.join(HERE, "..", "assets")
    write(os.path.join(dest, "scene-light.svg"), build(DAY))
    write(os.path.join(dest, "scene-dark.svg"), build(NIGHT))
