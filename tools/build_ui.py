"""Section furniture in the same cel-shaded language as the key visual:
episode-title headers, a treeline divider, a skill vine, a live terminal,
and the quote card. All vector, all generated.
"""
import math, os
from _core import DAY, NIGHT, text_path, rng, write, HERE
from build_scene import CANOPY, blob, smooth, ridge, clip_of

W = 1200

HEADERS = [
    ("about",   "ABOUT",   "私について"),
    ("toolkit", "TOOLKIT", "スキル"),
    ("work",    "WORK",    "作品"),
    ("journey", "JOURNEY", "経歴"),
    ("stats",   "STATS",   "記録"),
    ("connect", "CONNECT", "連絡"),
]


def svg(w, h, label, extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img" aria-label="{label}"{extra}>')


def tone(p, tid="tone", op=".16", step=7):
    return (f'<pattern id="{tid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<circle cx="{step/2:.1f}" cy="{step/2:.1f}" r="1.15" fill="{p["card_ink"]}" '
            f'fill-opacity="{op}"/></pattern>')


def cel_leaf(p, s=1.0, cls=""):
    """Flat top half, shadowed bottom half, midrib. The anime way to draw a leaf."""
    c = f' class="{cls}"' if cls else ""
    return (f'<g{c} transform="scale({s})">'
            f'<path d="M0,0 C6.2,-9.4 20,-11.6 26.4,-6.2 C18,-4 8,-1.9 0,0 Z" '
            f'fill="{p["ui_leaf_hi"]}"/>'
            f'<path d="M0,0 C8,-1.9 18,-4 26.4,-6.2 C20.4,3.4 6.4,7.4 0,0 Z" '
            f'fill="{p["ui_leaf_mid"]}"/>'
            f'<path d="M1,-0.2 C9,-2.4 18,-4.4 25.6,-6.2" fill="none" '
            f'stroke="{p["ui_leaf_dark"]}" stroke-opacity=".55" stroke-width="1.1"/></g>')


# ----------------------------------------------------------------- headers
def header(p, en, jp):
    H = 108
    o = [svg(W, H, f"{en} section")]
    o.append(f'''<style>
.sw{{animation:sw 5.5s ease-in-out infinite;transform-box:fill-box;transform-origin:0 50%}}
@keyframes sw{{0%,100%{{transform:rotate(-6deg)}}50%{{transform:rotate(6deg)}}}}
.dash{{stroke-dasharray:900;stroke-dashoffset:900;animation:dash 1.6s ease forwards}}
@keyframes dash{{to{{stroke-dashoffset:0}}}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}.dash{{stroke-dashoffset:0}}}}
</style><defs>{tone(p, "th", ".13")}</defs>''')

    # slanted accent block -- the anime episode-title cut
    o.append(f'<path d="M0,18 L26,18 L14,92 L0,92 Z" fill="{p["card_gold"]}"/>')
    o.append(f'<path d="M32,18 L44,18 L32,92 L20,92 Z" fill="{p["card_gold"]}" '
             f'fill-opacity=".45"/>')

    d, tw = text_path("display", en, 42, 62, 62, 0.09)
    o.append(f'<path d="{d}" fill="{p["card_ink"]}"/>')
    jd, jw = text_path("jp", jp, 16, 64, 90, 0.24, wght=500)
    o.append(f'<path d="{jd}" fill="{p["card_mute"]}"/>')

    x0 = 62 + max(tw, jw) + 34
    o.append(f'<path class="dash" d="M{x0},52 L{W-96},52" stroke="{p["card_line"]}" '
             f'stroke-width="1.6" fill="none"/>')
    o.append(f'<rect x="{x0}" y="66" width="{W-96-x0}" height="16" fill="url(#th)" '
             f'opacity=".7"/>')
    o.append(f'<g transform="translate({W-84},48)">{cel_leaf(p, .95, "sw")}</g>')
    o.append(f'<g transform="translate({W-46},64) scale(-1,1)">'
             f'{cel_leaf(p, .7, "sw")}</g>')
    o.append("</svg>")
    return "\n".join(o)


# ----------------------------------------------------------------- divider
def strip(p):
    H = 84
    o = [svg(W, H, "divider")]
    o.append('''<style>
.fly{animation-name:fl;animation-timing-function:linear;animation-iteration-count:infinite}
@keyframes fl{from{transform:translate(0,0)}to{transform:translate(-1320px,var(--dy))}}
.flap{animation-name:fp;animation-timing-function:ease-in-out;animation-iteration-count:infinite;
 transform-box:fill-box;transform-origin:50% 100%}
@keyframes fp{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.4)}}
.blade{animation-name:sw;animation-timing-function:ease-in-out;animation-iteration-count:infinite;
 transform-box:fill-box;transform-origin:50% 100%}
@keyframes sw{0%,100%{transform:rotate(-4deg)}50%{transform:rotate(4deg)}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
</style>''')
    r = rng(12)
    # a low ridge of silhouetted trees, fading at both ends
    o.append(f'<defs><linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0%" stop-color="{p["tree_dark"]}" stop-opacity="0"/>'
             f'<stop offset="18%" stop-color="{p["tree_dark"]}" stop-opacity=".55"/>'
             f'<stop offset="82%" stop-color="{p["tree_dark"]}" stop-opacity=".55"/>'
             f'<stop offset="100%" stop-color="{p["tree_dark"]}" stop-opacity="0"/>'
             f'</linearGradient>'
             f'<mask id="fm"><rect width="{W}" height="{H}" fill="url(#fadem)"/></mask>'
             f'<linearGradient id="fadem" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0%" stop-color="#000"/><stop offset="22%" stop-color="#fff"/>'
             f'<stop offset="78%" stop-color="#fff"/><stop offset="100%" stop-color="#000"/>'
             f'</linearGradient></defs>')
    g = ['<g mask="url(#fm)">']
    for i in range(30):
        x = -20 + (W + 40) * (i + r.random() * 0.75) / 30
        k = 0.13 * r.uniform(0.6, 1.5)
        g.append(f'<g transform="translate({x:.0f},{H - 6 + r.uniform(-3,3):.0f}) '
                 f'scale({k*r.choice([-1,1]):.2f},{k*r.uniform(.8,1.2):.2f})">'
                 + blob(CANOPY, p["ui_leaf_dark"], 0, 0, 1, ' fill-opacity=".6"')
                 + f'<rect x="-9" y="-10" width="18" height="46" fill="{p["ui_leaf_dark"]}" '
                   f'fill-opacity=".6"/></g>')
    for i in range(52):
        x = -10 + (W + 20) * (i + r.random()) / 52
        h = r.uniform(8, 20)
        lean = r.uniform(-.4, .4) * h
        g.append(f'<g transform="translate({x:.0f},{H-2})"><path class="blade" '
                 f'd="M-1.4,0 Q{lean*.2:.1f},{-h*.5:.1f} {lean:.1f},{-h:.1f} '
                 f'Q{lean*.05:.1f},{-h*.48:.1f} 1.4,0 Z" fill="{p["ui_leaf_dark"]}" '
                 f'fill-opacity=".7" style="animation-duration:{r.uniform(3,6):.1f}s;'
                 f'animation-delay:{-r.uniform(0,6):.1f}s"/></g>')
    g.append('</g>')
    o.append("".join(g))
    for i in range(3):
        y, dur = 18 + i * 13, r.uniform(28, 44)
        o.append(f'<g transform="translate({W+60},{y})"><g class="fly" '
                 f'style="animation-duration:{dur:.0f}s;animation-delay:{-r.uniform(0,dur):.0f}s;'
                 f'--dy:{r.uniform(-8,10):.0f}px"><g class="flap" '
                 f'style="animation-duration:{r.uniform(1,1.5):.2f}s" '
                 f'transform="scale({r.uniform(.5,.8):.2f})">'
                 f'<path d="M0,0 Q7,-8 14,-1 Q21,-8 28,0" fill="none" stroke="{p["card_mute"]}" '
                 f'stroke-opacity=".7" stroke-width="2.2" stroke-linecap="round"/>'
                 f'</g></g></g>')
    o.append("</svg>")
    return "\n".join(o)


# ----------------------------------------------------------------- toolkit
VINES = [
    ("LANGUAGES", "言語", 244, ["C / C++", "Python", "Bash", "Perl", "MySQL", "Linux CLI"]),
    ("TOOLS  &  CRAFT", "道具", 468,
     ["MetaPhlAn", "Bowtie2", "QIIME 2", "SparCC", "FASTQ", "PyMOL", "Blender"]),
]


def vine_pts(x0, x1, cy, amp, waves, n=200):
    pts = [(x0 + (x1 - x0) * i / n,
            cy + amp * math.sin(2 * math.pi * waves * i / n)) for i in range(n + 1)]
    ln = sum(math.dist(pts[i], pts[i + 1]) for i in range(n))
    return pts, ln


def toolkit(p):
    H = 568
    o = [svg(W, H, "Toolkit")]
    o.append(f'''<style>
.vine{{stroke-dasharray:var(--len);stroke-dashoffset:var(--len);
 animation:draw 2.8s cubic-bezier(.3,.7,.3,1) forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.sprout{{animation:sp .8s cubic-bezier(.2,.9,.3,1.35) both;
 transform-box:fill-box;transform-origin:0 50%}}
@keyframes sp{{from{{transform:scale(0) rotate(-45deg);opacity:0}}
 to{{transform:scale(1) rotate(0);opacity:1}}}}
.lbl{{animation:li .7s ease both}}
@keyframes li{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
.br{{animation-name:br;animation-timing-function:ease-in-out;animation-iteration-count:infinite;
 transform-box:fill-box;transform-origin:0 50%}}
@keyframes br{{0%,100%{{transform:rotate(-5deg)}}50%{{transform:rotate(5deg)}}}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}.vine{{stroke-dashoffset:0}}}}
</style><defs>{tone(p, "tk", ".10")}</defs>''')
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22" fill="{p["card"]}" '
             f'stroke="{p["card_line"]}" stroke-width="1.6"/>')
    o.append(f'<path d="M{W-2},1 L{W-2},170 L{W-330},1 Z" fill="url(#tk)"/>')

    r = rng(5)
    for vi, (name, jp, cy, items) in enumerate(VINES):
        d, lw = text_path("serif", name, 17, 62, cy - 104, 0.26, wght=700)
        jd, _ = text_path("jp", jp, 14, 62, cy - 82, 0.2, wght=500)
        o.append(f'<g class="lbl" style="animation-delay:{.25+vi*.2:.2f}s">'
                 f'<path d="{d}" fill="{p["card_ink"]}"/>'
                 f'<path d="{jd}" fill="{p["card_mute"]}"/>'
                 f'<rect x="{62+lw+22}" y="{cy-109}" width="{W-146-lw}" height="1" '
                 f'fill="{p["card_line"]}"/></g>')

        pts, ln = vine_pts(62, W - 62, cy, 22, 1.6 + vi * 0.4)
        vd = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        o.append(f'<path class="vine" d="{vd}" fill="none" stroke="{p["ui_leaf_mid"]}" '
                 f'stroke-opacity=".7" stroke-width="2.6" stroke-linecap="round" '
                 f'style="--len:{ln:.0f};animation-delay:{.3+vi*.25:.2f}s"/>')

        for i, item in enumerate(items):
            x, y = pts[int(((i + 0.5) / len(items)) * (len(pts) - 1))]
            up = i % 2 == 0
            sy = y - 34 if up else y + 34
            delay = 0.9 + vi * 0.25 + i * 0.15
            o.append(f'<g class="sprout" style="animation-delay:{delay:.2f}s">'
                     f'<path d="M{x:.1f},{y:.1f} Q{x+5:.1f},{(y+sy)/2:.1f} {x:.1f},{sy:.1f}" '
                     f'fill="none" stroke="{p["ui_leaf_mid"]}" stroke-opacity=".6" stroke-width="2"/>'
                     f'<g transform="translate({x:.1f},{sy:.1f}) rotate({r.uniform(-22,22):.0f})">'
                     f'<g class="br" style="animation-duration:{r.uniform(4,7):.1f}s;'
                     f'animation-delay:-{r.uniform(0,6):.1f}s">'
                     f'{cel_leaf(p, r.uniform(.7, .95))}</g></g></g>')

            tw = text_path("serif", item, 22, 0, 0, 0.03, wght=600)[1]
            td, _ = text_path("serif", item, 22, x - tw / 2, sy - 24 if up else sy + 38,
                              0.03, wght=600)
            o.append(f'<g class="lbl" style="animation-delay:{delay+.18:.2f}s">'
                     f'<path d="{td}" fill="{p["card_ink"]}" fill-opacity=".88"/></g>')
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- terminal
LINES = [
    ("p", "conda activate metagenome"),
    ("p", "fastqc raw/*.fastq.gz -t 8 -o qc/"),
    ("o", "24 samples  ·  mean Q30 94.1%  ·  adapters clean"),
    ("p", "bowtie2 --very-sensitive -x hg38 -U trim.fq --un-gz clean.fq.gz"),
    ("o", "97.3% non-host reads retained"),
    ("p", "metaphlan clean.fq.gz --input_type fastq --nproc 8 -o profile.tsv"),
    ("b", "profiling"),
    ("o", "1,284 clades  ·  312 species-level SGBs"),
    ("p", "Rscript sparcc_network.R --r 0.5 --p 0.01"),
    ("o", "network built  ·  87 nodes, 214 edges"),
]
PROMPT = "prince@sastra:~/gut-metagenome$ "
CW, FS, LH, PADX, TOP, T = 12.5, 20, 32, 36, 96, 22.0
MONO = 'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,DejaVu Sans Mono,monospace"'


def terminal(p):
    H = TOP + LH * len(LINES) + 44
    css = ['.cur{animation:bl 1.05s steps(1) infinite}',
           '@keyframes bl{0%,49%{opacity:1}50%,100%{opacity:0}}',
           '.scan{animation:sc 9s linear infinite}',
           '@keyframes sc{from{transform:translateY(-100px)}to{transform:translateY(' + str(H + 100) + 'px)}}']
    b = []
    b.append(f'<rect width="{W}" height="{H}" rx="18" fill="{p["term_bg"]}"/>')
    b.append(f'<path d="M18,0 H{W-18} A18,18 0 0 1 {W},18 V58 H0 V18 A18,18 0 0 1 18,0Z" '
             f'fill="{p["term_glow"]}" fill-opacity=".08"/>')
    b.append(f'<rect y="58" width="{W}" height="1" fill="{p["term_glow"]}" fill-opacity=".2"/>')
    for i, c in enumerate(("#e0685f", "#e2b04a", "#71b85c")):
        b.append(f'<circle cx="{34+i*24}" cy="29" r="6.5" fill="{c}" fill-opacity=".9"/>')
    b.append(f'<text x="{W/2}" y="35" text-anchor="middle" font-size="16" {MONO} '
             f'fill="{p["term_dim"]}">gut-metagenome — bash — 120×32</text>')

    per = 0.86 / len(LINES)
    for i, (kind, txt) in enumerate(LINES):
        y = TOP + i * LH
        t0, t1 = 0.02 + i * per, 0.02 + i * per + per * 0.7
        row, x = [], PADX
        if kind == "p":
            row.append(f'<text x="{x}" y="{y}" font-size="{FS}" {MONO} '
                       f'xml:space="preserve">'
                       f'<tspan fill="{p["term_glow"]}" fill-opacity=".85">{PROMPT}</tspan>'
                       f'<tspan fill="{p["term_ink"]}">{txt}</tspan></text>')
            n = len(txt)
            width = (len(PROMPT) + n) * CW + 20
        elif kind == "b":
            row.append(f'<text x="{x+20}" y="{y}" font-size="{FS}" {MONO} '
                       f'fill="{p["term_dim"]}">{txt}</text>')
            bx, bw = x + 20 + (len(txt) + 2) * CW, 420
            row.append(f'<rect x="{bx}" y="{y-15}" width="{bw}" height="15" rx="7.5" '
                       f'fill="{p["term_glow"]}" fill-opacity=".14"/>')
            css.append('.bar{animation:bar ' + str(T) + 's linear infinite;'
                       'transform-box:fill-box;transform-origin:0 50%}')
            css.append(f'@keyframes bar{{0%,{t0*100:.1f}%{{transform:scaleX(0)}}'
                       f'{t1*100+7:.1f}%,96%{{transform:scaleX(1)}}'
                       f'97%,100%{{transform:scaleX(0)}}}}')
            row.append(f'<rect class="bar" x="{bx}" y="{y-15}" width="{bw}" height="15" rx="7.5" '
                       f'fill="{p["term_glow"]}" fill-opacity=".8"/>')
            n, width = len(txt), bx + bw + 16 - PADX
        else:
            row.append(f'<circle cx="{x+7}" cy="{y-7}" r="3.2" fill="{p["card_gold"]}"/>')
            row.append(f'<text x="{x+24}" y="{y}" font-size="{FS}" {MONO} '
                       f'fill="{p["term_dim"]}">{txt}</text>')
            n, width = len(txt), 28 + len(txt) * CW + 16
        b.append("".join(row))
        css.append(f'.w{i}{{animation:w{i} {T}s steps({max(4,n)}) infinite;'
                   f'transform-box:fill-box;transform-origin:0 50%}}')
        css.append(f'@keyframes w{i}{{0%,{t0*100:.2f}%{{transform:translateX(0)}}'
                   f'{t1*100:.2f}%,96%{{transform:translateX({width:.0f}px)}}'
                   f'97%,100%{{transform:translateX(0)}}}}')
        b.append(f'<rect class="w{i}" x="{PADX-6}" y="{y-FS-5}" width="{width:.0f}" '
                 f'height="{LH}" fill="{p["term_bg"]}"/>')

    cy = TOP + LH * len(LINES)
    b.append(f'<rect class="cur" x="{PADX}" y="{cy-FS+3}" width="10" height="{FS}" '
             f'fill="{p["term_glow"]}" fill-opacity=".9"/>')
    b.append(f'<rect width="{W}" height="{H}" fill="url(#scan)" opacity=".55"/>')
    b.append(f'<rect class="scan" width="{W}" height="60" fill="{p["term_glow"]}" '
             f'fill-opacity=".04"/>')
    b.append(f'<rect x=".9" y=".9" width="{W-1.8}" height="{H-1.8}" rx="18" fill="none" '
             f'stroke="{p["term_glow"]}" stroke-opacity=".28" stroke-width="1.8"/>')

    o = [svg(W, H, "A metagenomics pipeline, running")]
    o.append("<style>" + "\n".join(css) +
             "\n@media(prefers-reduced-motion:reduce){*{animation:none!important}}</style>")
    o.append(f'<defs><pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
             f'<rect width="4" height="1.2" fill="{p["term_glow"]}" fill-opacity=".05"/></pattern>'
             f'<clipPath id="win"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>')
    o.append('<g clip-path="url(#win)">' + "\n".join(b) + "</g></svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ quotes
QUOTES = [
    ("Always believe in yourself. Do this and no matter where you are,",
     "you will have nothing to fear.", "CASTLE IN THE SKY"),
    ("Nothing that happens is ever forgotten,",
     "even if you can't remember it.", "SPIRITED AWAY"),
    ("The wind is rising —", "we must try to live.", "THE WIND RISES"),
]


def quotes(p):
    H = 216
    n = len(QUOTES)
    css, seg = [], 100.0 / n
    for i in range(n):
        a, b = i * seg, (i + 1) * seg
        css.append(f'.q{i}{{animation:q{i} 27s ease-in-out infinite}}'
                   f'@keyframes q{i}{{0%,{max(0,a-1):.1f}%{{opacity:0;transform:translateY(12px)}}'
                   f'{a+3:.1f}%,{b-4:.1f}%{{opacity:1;transform:translateY(0)}}'
                   f'{min(100,b-1):.1f}%,100%{{opacity:0;transform:translateY(-10px)}}}}')
    o = [svg(W, H, "Quotes")]
    o.append("<style>" + "".join(css) +
             ".tw{animation-name:tw;animation-timing-function:ease-in-out;"
             "animation-iteration-count:infinite}"
             "@keyframes tw{0%,100%{opacity:.18}50%{opacity:.85}}"
             "@media(prefers-reduced-motion:reduce){*{animation:none!important}"
             ".q1,.q2{display:none}}</style>")
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22" fill="{p["card2"]}" '
             f'stroke="{p["card_line"]}" stroke-width="1.6"/>')
    r = rng(77)
    o.append(f'<clipPath id="qc"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22"/></clipPath>')
    st = ['<g clip-path="url(#qc)">']
    for _ in range(46):
        st.append(f'<circle class="tw" cx="{r.uniform(0,W):.0f}" cy="{r.uniform(0,H):.0f}" '
                  f'r="{r.uniform(.8,2):.1f}" fill="{p["card_gold"]}" '
                  f'style="animation-duration:{r.uniform(3,7):.1f}s;'
                  f'animation-delay:{-r.uniform(0,7):.1f}s"/>')
    st.append('</g>')
    o.append("".join(st))

    for i, (l1, l2, src) in enumerate(QUOTES):
        g = [f'<g class="q{i}">']
        for j, line in enumerate((l1, l2)):
            wpx = text_path("serif-italic", line, 35, 0, 0, 0.015, wght=500)[1]
            d, _ = text_path("serif-italic", line, 35, (W - wpx) / 2, 84 + j * 46,
                             0.015, wght=500)
            g.append(f'<path d="{d}" fill="{p["card_ink"]}" fill-opacity=".94"/>')
        sw = text_path("serif", src, 14, 0, 0, 0.3, wght=600)[1]
        d, _ = text_path("serif", src, 14, (W - sw) / 2, 170, 0.3, wght=600)
        g.append(f'<path d="{d}" fill="{p["card_gold"]}"/>')
        g.append(f'<rect x="{W/2-sw/2-76}" y="163" width="56" height="1" fill="{p["card_line"]}"/>')
        g.append(f'<rect x="{W/2+sw/2+20}" y="163" width="56" height="1" fill="{p["card_line"]}"/>')
        g.append("</g>")
        o.append("".join(g))
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    dest = os.path.join(HERE, "..", "assets")
    for p in (DAY, NIGHT):
        t = "light" if not p["night"] else "dark"
        for slug, en, jp in HEADERS:
            write(os.path.join(dest, f"h-{slug}-{t}.svg"), header(p, en, jp))
        write(os.path.join(dest, f"strip-{t}.svg"), strip(p))
        write(os.path.join(dest, f"toolkit-{t}.svg"), toolkit(p))
        write(os.path.join(dest, f"terminal-{t}.svg"), terminal(p))
        write(os.path.join(dest, f"quotes-{t}.svg"), quotes(p))
