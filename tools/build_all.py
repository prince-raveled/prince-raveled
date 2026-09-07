"""Regenerate every SVG in assets/. Fonts download into tools/.fontcache on first run."""
import build_scene, build_ui, os
from _core import DAY, NIGHT, write, HERE

dest = os.path.join(HERE, "..", "assets")
os.makedirs(dest, exist_ok=True)

write(os.path.join(dest, "scene-light.svg"), build_scene.build(DAY))
write(os.path.join(dest, "scene-dark.svg"), build_scene.build(NIGHT))
for p in (DAY, NIGHT):
    t = "light" if not p["night"] else "dark"
    for slug, en, jp in build_ui.HEADERS:
        write(os.path.join(dest, f"h-{slug}-{t}.svg"), build_ui.header(p, en, jp))
    write(os.path.join(dest, f"strip-{t}.svg"), build_ui.strip(p))
    write(os.path.join(dest, f"toolkit-{t}.svg"), build_ui.toolkit(p))
    write(os.path.join(dest, f"terminal-{t}.svg"), build_ui.terminal(p))
    write(os.path.join(dest, f"quotes-{t}.svg"), build_ui.quotes(p))
print("\ndone — commit assets/ and push.")
