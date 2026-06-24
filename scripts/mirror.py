#!/usr/bin/env python3
"""Mirror salesken.ai pages locally — preserves exact content and absolute paths."""

import json
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE_URL = "https://www.salesken.ai"
ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
SITEMAP_URL = f"{BASE_URL}/sitemap.xml"
USER_AGENT = "SaleskenCloneMirror/1.0"

MENU_PATHS = [
    "/",
    "/product/quality-assurance",
    "/product/ai-sales-assistant",
    "/product/revenue-intelligence",
    "/use-cases/revops",
    "/use-cases/sales-team",
    "/use-cases/compliance",
    "/pricing",
    "/blog",
    "/book-a-demo",
    "/legal/privacy-policy",
    "/legal/terms-conditions",
    "/legal/data-processing-addendum",
    "/blog-categories/blogs",
    "/blog-categories/templates",
    "/sales-percentage-calculator",
    "/sales-lift-calculator",
    "/revenue-projection-calculator",
    "/sales-forecast-calculator",
    "/sales-mix-calculator",
    "/profit-to-sales-ratio-calculator",
]


def fetch(url: str, retries: int = 3) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
            print(f"  retry {attempt + 1} for {url}: {exc}")
    return b""


def get_sitemap_paths() -> list[str]:
    paths = set(MENU_PATHS)
    try:
        raw = fetch(SITEMAP_URL)
        root = ET.fromstring(raw)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        for loc in root.findall(".//sm:loc", ns):
            url = loc.text.strip()
            if url.startswith(BASE_URL):
                paths.add(url[len(BASE_URL) :] or "/")
    except Exception as exc:
        print(f"Warning: could not parse sitemap: {exc}")
    return sorted(paths, key=lambda p: (p.count("/"), p))


def path_to_file(path: str) -> Path:
    if path == "/":
        return SITE_DIR / "index.html"
    clean = path.strip("/")
    return SITE_DIR / clean / "index.html"


def clean_html(html: str) -> str:
    """Strip analytics; keep layout/assets from Webflow CDN."""
    html = re.sub(
        r"<!-- Google Tag Manager -->.*?<!-- End Google Tag Manager -->",
        "",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'<noscript>.*?googletagmanager.*?</noscript>',
        "",
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    html = re.sub(
        r'<script[^>]*googletagmanager[^>]*>.*?</script>',
        "",
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    html = re.sub(
        r'<script async="" src="https://www\.googletagmanager\.com/gtag/js[^"]*"></script>',
        "",
        html,
    )
    html = re.sub(
        r"<script type=\"text/javascript\">\s*window\.dataLayer.*?</script>",
        "",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'<script type="text/javascript">\s*\(function\(c,l,a,r,i,t,y\).*?</script>',
        "",
        html,
        flags=re.DOTALL,
    )
    banner = "<!-- Local mirror of www.salesken.ai -->\n"
    if banner not in html:
        html = html.replace("<head>", f"<head>\n{banner}", 1)
    return html


def mirror_path(path: str) -> dict:
    url = BASE_URL if path == "/" else f"{BASE_URL}{path}"
    try:
        raw = fetch(url)
    except Exception as exc:
        return {"path": path, "ok": False, "error": str(exc)}

    html = clean_html(raw.decode("utf-8", errors="replace"))
    out = path_to_file(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return {"path": path, "ok": True, "file": str(out.relative_to(ROOT))}


def main() -> int:
    menu_only = "--menu-only" in sys.argv
    paths = get_sitemap_paths()
    if menu_only:
        paths = [p for p in paths if p in MENU_PATHS or (p.startswith("/blog") and p == "/blog")]

    print(f"Mirroring {len(paths)} pages to {SITE_DIR}...")
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    for i, path in enumerate(paths, 1):
        result = mirror_path(path)
        results.append(result)
        status = "OK" if result["ok"] else f"FAIL: {result.get('error')}"
        print(f"[{i}/{len(paths)}] {path} -> {status}")
        time.sleep(0.25)

    manifest = {
        "source": BASE_URL,
        "mirrored_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total": len(results),
        "success": sum(1 for r in results if r["ok"]),
        "pages": results,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nDone: {manifest['success']}/{manifest['total']} pages")
    return 0 if manifest["success"] == manifest["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
