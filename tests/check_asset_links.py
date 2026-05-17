#!/usr/bin/env python3
"""Assert every relative asset reference under apps/ resolves to a real file.

Walks every .html for src=/href=/srcset= and every .css for url(...).
Skips external URLs, data: URIs, anchors, mailto:, tel:.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = REPO_ROOT / "apps"

SKIP_PREFIXES = ("http://", "https://", "//", "data:", "mailto:", "tel:", "#", "javascript:")
PATH_ATTRS = {"src", "href"}

CSS_URL_RE = re.compile(r"url\(\s*['\"]?([^'\")\s]+)")


class AssetExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.paths: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value is None:
                continue
            if name in PATH_ATTRS:
                self.paths.append(value)
            elif name == "srcset":
                for candidate in value.split(","):
                    url = candidate.strip().split()[0] if candidate.strip() else ""
                    if url:
                        self.paths.append(url)


def extract_from_html(path: Path) -> list[str]:
    parser = AssetExtractor()
    parser.feed(path.read_text())
    return parser.paths


def extract_from_css(path: Path) -> list[str]:
    return CSS_URL_RE.findall(path.read_text())


def is_external(path: str) -> bool:
    return path.startswith(SKIP_PREFIXES)


def main() -> int:
    if not APPS_DIR.exists():
        print(f"apps/ not found at {APPS_DIR}")
        return 0

    broken: list[tuple[str, str]] = []
    checked = 0

    for source in APPS_DIR.rglob("*.html"):
        for ref in extract_from_html(source):
            if is_external(ref) or ref.startswith("/"):
                continue
            checked += 1
            target = (source.parent / ref).resolve()
            if not target.exists():
                broken.append((str(source.relative_to(REPO_ROOT)), ref))

    for source in APPS_DIR.rglob("*.css"):
        for ref in extract_from_css(source):
            if is_external(ref) or ref.startswith("/"):
                continue
            checked += 1
            target = (source.parent / ref).resolve()
            if not target.exists():
                broken.append((str(source.relative_to(REPO_ROOT)), ref))

    if broken:
        print("broken asset references:", file=sys.stderr)
        for source, ref in broken:
            print(f"  {source} -> {ref}", file=sys.stderr)
        return 1

    print(f"asset links: {checked} OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
