"""Re-render the post's chart images from the running app.

The images carry live numbers, so they go stale whenever the data is refreshed.
Start the app, then:  python scripts/capture_assets.py [port]

Needs `pip install playwright`. It drives the system Chrome, so there's no
browser download.
"""
import os
import subprocess
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

PORT = sys.argv[1] if len(sys.argv) > 1 else "8501"
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
BG = (251, 249, 245)  # must match SURFACE in ui.py, or the padding shows as a seam

# chart order is the order they appear on the page, so this breaks if sections move
CHARTS = {"colour": 0, "scatter": 1, "trend": 2, "survival": 3}
BLOCKS = {"groups": ".grp", "dogs": ".dogs"}


def chrome():
    for p in ("/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"):
        if os.path.exists(p):
            return p
    raise SystemExit("no chrome found, set the path by hand")


def pad(path, m=40):
    im = Image.open(path).convert("RGB")
    canvas = Image.new("RGB", (im.width + m * 2, im.height + m * 2), BG)
    canvas.paste(im, (m, m))
    canvas.save(path, optimize=True)
    return canvas.size


def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=chrome(), args=["--no-sandbox", "--disable-gpu"])
        pg = b.new_page(viewport={"width": 1500, "height": 3000}, device_scale_factor=2)
        pg.goto(f"http://localhost:{PORT}/", wait_until="domcontentloaded", timeout=120_000)
        pg.wait_for_selector(".dog", timeout=180_000)
        pg.wait_for_timeout(9000)  # altair finishes drawing after streamlit says it's done

        charts = pg.locator('[data-testid="stVegaLiteChart"]')
        if charts.count() < max(CHARTS.values()) + 1:
            raise SystemExit(f"expected {max(CHARTS.values()) + 1} charts, found {charts.count()}")

        targets = [(n, charts.nth(i)) for n, i in CHARTS.items()]
        targets += [(n, pg.locator(s)) for n, s in BLOCKS.items()]
        for name, loc in targets:
            loc.scroll_into_view_if_needed()
            pg.wait_for_timeout(700)
            path = os.path.join(OUT, f"{name}.png")
            loc.screenshot(path=path)
            print(f"{name}.png {pad(path)}")
        b.close()

    changed = subprocess.run(["git", "status", "--porcelain", "assets"],
                             capture_output=True, text=True).stdout.strip()
    print("\nchanged:\n" + (changed or "  nothing"))


if __name__ == "__main__":
    main()
