# Putting this live

## 1. Create the repo

The profile README only works from a repo named **exactly** your username.

- Go to <https://github.com/new>
- Repository name: **`prince-raveled`**
- **Public**
- Do **not** tick "Add a README" — this folder already has one

GitHub will show a "✨ You found a secret!" banner when the name matches. That's the one.

## 2. Push

From this folder:

```bash
git init -b main
git add .
git commit -m "anime profile"
git remote add origin https://github.com/prince-raveled/prince-raveled.git
git push -u origin main
```

Open <https://github.com/prince-raveled> — the scene should be there.

## 3. Let the Actions write back

Both workflows commit to the repo, so they need write access:

**Settings → Actions → General → Workflow permissions → "Read and write permissions" → Save**

Then run each once by hand (**Actions** tab → pick the workflow → *Run workflow*):

| Workflow | What it does | How often |
| :-- | :-- | :-- |
| `refresh stats card` | Re-renders `assets/stats-*.svg` from the GitHub API | daily, 04:17 UTC |
| `generate snake` | Builds the snake animation onto an `output` branch | every 12 h |

**The snake image will show as broken until that workflow finishes the first time** — it points at
a branch that doesn't exist yet. Give it a minute, then reload.

---

## Changing things

Regenerate every illustration:

```bash
pip install fonttools brotli
python tools/build_all.py
```

Fonts download to `tools/.fontcache/` on first run (gitignored). Then commit `assets/`.

| File | What lives there |
| :-- | :-- |
| `tools/_core.py` | Colour palettes (`DAY` / `NIGHT`) and the font→path converter |
| `tools/build_scene.py` | The hero: sky, clouds, hills, tree, the figure, weather |
| `tools/build_ui.py` | Section headers, treeline divider, skill vines, terminal, quotes |
| `tools/build_stats.py` | The stats card (talks to the GitHub API) |

Common edits:

- **Your name / tagline** → `build_scene.py`, the `# ---- title card` block
- **Skills** → `VINES` in `build_ui.py`
- **The terminal session** → `LINES` in `build_ui.py`
- **Quotes** → `QUOTES` in `build_ui.py`
- **Colours** → `DAY` and `NIGHT` in `_core.py`

Preview locally without pushing:

```bash
python -m http.server 8777
```

then open <http://localhost:8777/preview.html> (renders the real README) or
`preview-assets.html` (every asset on a dark background).

## A caching gotcha

GitHub proxies README images through its own cache. After you push new art, the profile can keep
showing the old version for a while. Force it by bumping a version query on the URLs in
`README.md` — `...scene-light.svg` → `...scene-light.svg?v=2`.

## Two things I left for you to decide

- **Your phone number** is on your portfolio but I kept it out of the README — a GitHub profile is
  crawled far more aggressively than a personal site. Add it under CONNECT if you want it there.
- **The LinkedIn URL** is the one linked from your portfolio
  (`linkedin.com/in/prince-kumar-392b28353`). Swap it if you have a vanity URL now.
