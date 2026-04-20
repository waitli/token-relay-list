#!/usr/bin/env python3
"""Generate SEO assets for the static site."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
DATA_PATH = ROOT / "data" / "checked.json"

DEFAULT_SITE_URL = "https://token.waitli.top"


def normalize_site_url(raw: str | None) -> str:
    site_url = (raw or DEFAULT_SITE_URL).strip()
    if not site_url:
        site_url = DEFAULT_SITE_URL
    return site_url.rstrip("/")


def load_lastmod() -> str:
    try:
        with DATA_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        value = str(data.get("last_updated", "")).strip()
        if value:
            return datetime.strptime(value, "%Y-%m-%d %H:%M").date().isoformat()
    except Exception:
        pass
    return datetime.utcnow().date().isoformat()


def build_sitemap(site_url: str, lastmod: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url>\n'
        f'    <loc>{escape(site_url)}/</loc>\n'
        f'    <lastmod>{lastmod}</lastmod>\n'
        '    <changefreq>daily</changefreq>\n'
        '    <priority>1.0</priority>\n'
        '  </url>\n'
        '</urlset>\n'
    )


def build_robots(site_url: str) -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {site_url}/sitemap.xml\n"
    )


def main() -> None:
    site_url = normalize_site_url(os.environ.get("SITE_URL"))
    lastmod = load_lastmod()

    SRC_DIR.mkdir(parents=True, exist_ok=True)
    (SRC_DIR / "sitemap.xml").write_text(build_sitemap(site_url, lastmod), encoding="utf-8")
    (SRC_DIR / "robots.txt").write_text(build_robots(site_url), encoding="utf-8")


if __name__ == "__main__":
    main()
