#!/usr/bin/env python3
"""Flag absolute-path asset references under apps/.

Absolute paths (href="/foo", src="/foo", url("/foo")) silently break if
a service's routePrefix changes. Relative paths survive prefix changes.
External URLs (https://...) are fine.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = REPO_ROOT / "apps"

EXTERNAL_PREFIXES = ("http://", "https://", "//", "data:", "mailto:", "tel:", "#", "javascript:")
PATH_ATTRS = {"src", "href"}
CSS_URL_RE = re.compile(r"url\(\s*['\"]?([^'\")\s]+)")

ALLOWLIST: set[str] = set()  # add paths here if a future case genuinely needs an absolute path


class AbsPathExtractor(HTMLParser):
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


def extract_html(path: Path) -> list[str]:
    parser = AbsPathExtractor()
    parser.feed(path.read_text())
    return parser.paths


def extract_css(path: Path) -> list[str]:
    return CSS_URL_RE.findall(path.read_text())


def is_absolute_local(ref: str) -> bool:
    if ref.startswith(EXTERNAL_PREFIXES):
        return False
    return ref.startswith("/")


def main() -> int:
    if not APPS_DIR.exists():
        print(f"apps/ not found at {APPS_DIR}")
        return 0

    findings: list[tuple[str, str]] = []

    for source in APPS_DIR.rglob("*.html"):
        for ref in extract_html(source):
            if is_absolute_local(ref) and ref not in ALLOWLIST:
                findings.append((str(source.relative_to(REPO_ROOT)), ref))

    for source in APPS_DIR.rglob("*.css"):
        for ref in extract_css(source):
            if is_absolute_local(ref) and ref not in ALLOWLIST:
                findings.append((str(source.relative_to(REPO_ROOT)), ref))

    if findings:
        print("absolute-path references (would break under routePrefix change):", file=sys.stderr)
        for source, ref in findings:
            print(f"  {source} -> {ref}", file=sys.stderr)
        print("Use relative paths, or add to ALLOWLIST in this script if intentional.", file=sys.stderr)
        return 1

    print("absolute paths: none found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
