#!/usr/bin/env python3
"""Assert every experimentalServices entrypoint resolves to a real file or directory.

Catches the case where someone renames an apps/ directory but forgets to
update vercel.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERCEL_JSON = REPO_ROOT / "vercel.json"


def main() -> int:
    if not VERCEL_JSON.exists():
        print(f"vercel.json not found at {VERCEL_JSON}", file=sys.stderr)
        return 1

    config = json.loads(VERCEL_JSON.read_text())
    services = config.get("experimentalServices", {})
    if not services:
        print("no services declared in experimentalServices")
        return 0

    missing: list[tuple[str, str]] = []
    for name, service in services.items():
        entrypoint = service.get("entrypoint")
        if entrypoint is None:
            missing.append((name, "<no entrypoint field>"))
            continue
        path = REPO_ROOT / entrypoint
        if not path.exists():
            missing.append((name, entrypoint))

    if missing:
        print("missing entrypoints:", file=sys.stderr)
        for name, ep in missing:
            print(f"  {name}: {ep}", file=sys.stderr)
        return 1

    print(f"entrypoints: {len(services)} OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
