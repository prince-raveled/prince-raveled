"""Self-hosted stats card.

The popular third-party stats services share one rate-limited instance and
routinely return 503, which puts a broken image on your profile. This reads the
GitHub API directly (with the Actions token, so no rate-limit roulette) and
draws the numbers in the same cel-shaded language as everything else.

    python tools/build_stats.py            # unauthenticated, 60 req/hr
    GITHUB_TOKEN=... python tools/build_stats.py   # + contribution totals
"""
import json, os, sys, urllib.request, urllib.error
from _core import DAY, NIGHT, text_path, write, HERE

USER = os.environ.get("GH_USER", "prince-raveled")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
W, H = 1200, 320
API = "https://api.github.com"


def get(url, data=None):
    req = urllib.request.Request(url, data=data)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "prince-raveled-profile")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    if data:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect():
    u = get(f"{API}/users/{USER}")
    repos = get(f"{API}/users/{USER}/repos?per_page=100&type=owner")
    stars = sum(r["stargazers_count"] for r in repos)
    langs = {}
    for r in repos:
        if r.get("fork"):
            continue
        try:
            for k, v in get(r["languages_url"]).items():
                langs[k] = langs.get(k, 0) + v
        except urllib.error.HTTPError:
            pass
    contrib = None
    if TOKEN:
        q = {"query": "query($u:String!){user(login:$u){contributionsCollection"
                      "{contributionCalendar{totalContributions}}}}",
             "variables": {"u": USER}}
        try:
            res = get("https://api.github.com/graphql", json.dumps(q).encode())
            contrib = (res["data"]["user"]["contributionsCollection"]
                          ["contributionCalendar"]["totalContributions"])
        except Exception as e:                      # noqa: BLE001 - stat is optional
            print(f"  (contributions unavailable: {e})", file=sys.stderr)
    return {
        "repos": u["public_repos"],
        "stars": stars,
        "followers": u["followers"],
        "contrib": contrib,
        "langs": sorted(langs.items(), key=lambda kv: -kv[1])[:6],
    }


def ramp(p):
    """On-palette language colours -- greens into gold, not GitHub's rainbow."""
    return ([p["tree_hi"], p["tree_mid"], p["card_gold"], p["tree_dark"],
             p["card_mute"], p["hill_mid"]] if not p["night"] else
            [p["tree_hi"], p["hill_mid"], p["card_gold"], p["tree_mid"],
             p["card_mute"], p["hill_far"]])


def build(p, d):
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
         f'height="{H}" role="img" aria-label="GitHub statistics for {USER}">']
    o.append('''<style>
.pop{animation:pop .9s cubic-bezier(.2,.9,.3,1.25) both}
@keyframes pop{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
.seg{animation:seg 1.1s cubic-bezier(.3,.7,.3,1) both;transform-box:fill-box;transform-origin:0 50%}
@keyframes seg{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
</style>''')
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22" fill="{p["card"]}" '
             f'stroke="{p["card_line"]}" stroke-width="1.6"/>')
    o.append(f'<rect x="1" y="1" width="6" height="{H-2}" fill="{p["card_gold"]}" '
             f'fill-opacity=".8"/>')

    tiles = [("REPOSITORIES", d["repos"]), ("STARS EARNED", d["stars"]),
             ("FOLLOWERS", d["followers"])]
    if d["contrib"] is not None:
        tiles.append(("CONTRIBUTIONS", d["contrib"]))

    for i, (label, val) in enumerate(tiles):
        x = 56 + (i % 2) * 250
        y = 108 + (i // 2) * 116
        nd, _ = text_path("display", f"{val:,}", 54, x, y, 0.04)
        ld, _ = text_path("serif", label, 14, x, y + 26, 0.26, wght=700)
        o.append(f'<g class="pop" style="animation-delay:{.15+i*.12:.2f}s">'
                 f'<path d="{nd}" fill="{p["card_ink"]}"/>'
                 f'<path d="{ld}" fill="{p["card_mute"]}"/></g>')

    o.append(f'<rect x="560" y="60" width="1" height="{H-120}" fill="{p["card_line"]}"/>')

    ld, lw = text_path("serif", "LANGUAGES", 15, 620, 92, 0.26, wght=700)
    jd, _ = text_path("jp", "言語", 13, 620, 114, 0.2, wght=500)
    o.append(f'<g class="pop"><path d="{ld}" fill="{p["card_ink"]}"/>'
             f'<path d="{jd}" fill="{p["card_mute"]}"/></g>')

    total = sum(v for _, v in d["langs"]) or 1
    cols, bx, bw = ramp(p), 620, 520
    x = bx
    o.append(f'<rect x="{bx}" y="140" width="{bw}" height="16" rx="8" '
             f'fill="{p["card_ink"]}" fill-opacity=".07"/>')
    for i, (name, val) in enumerate(d["langs"]):
        seg = bw * val / total
        o.append(f'<rect class="seg" x="{x:.1f}" y="140" width="{max(seg,2):.1f}" height="16" '
                 f'fill="{cols[i % len(cols)]}" style="animation-delay:{.4+i*.1:.2f}s"/>')
        x += seg
    o.append(f'<rect x="{bx}" y="140" width="{bw}" height="16" rx="8" fill="none" '
             f'stroke="{p["card"]}" stroke-width="0"/>')

    for i, (name, val) in enumerate(d["langs"]):
        cx = bx + (i % 2) * 264
        cy = 196 + (i // 2) * 34
        pct = 100.0 * val / total
        td, tw = text_path("serif", name, 20, cx + 20, cy + 6, 0.02, wght=600)
        pd, _ = text_path("serif", f"{pct:.1f}%", 18, cx + 30 + tw, cy + 6, 0.02, wght=500)
        o.append(f'<g class="pop" style="animation-delay:{.55+i*.08:.2f}s">'
                 f'<circle cx="{cx+6}" cy="{cy}" r="6" fill="{cols[i % len(cols)]}"/>'
                 f'<path d="{td}" fill="{p["card_ink"]}" fill-opacity=".9"/>'
                 f'<path d="{pd}" fill="{p["card_mute"]}"/></g>')

    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    d = collect()
    print(f"  {USER}: {d['repos']} repos, {d['stars']} stars, {d['followers']} followers, "
          f"contrib={d['contrib']}, langs={[k for k, _ in d['langs']]}")
    dest = os.path.join(HERE, "..", "assets")
    write(os.path.join(dest, "stats-light.svg"), build(DAY, d))
    write(os.path.join(dest, "stats-dark.svg"), build(NIGHT, d))
