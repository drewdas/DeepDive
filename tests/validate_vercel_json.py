#!/usr/bin/env python3
"""Validate vercel.json against the schema declared in its $schema field.

Catches the class of failures we've actually hit (e.g.
experimentalServices.web.framework should be string) before pushing.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_SCHEMA_URL = "https://openapi.vercel.sh/vercel.json"
CACHE_PATH = Path.home() / ".cache" / "deepdive-vercel-schema.json"
CACHE_TTL_SECONDS = 7 * 24 * 3600
FETCH_TIMEOUT = 10
REPO_ROOT = Path(__file__).resolve().parent.parent
VERCEL_JSON = REPO_ROOT / "vercel.json"


def load_schema(url: str) -> dict | None:
    if CACHE_PATH.exists() and (time.time() - CACHE_PATH.stat().st_mtime) < CACHE_TTL_SECONDS:
        return json.loads(CACHE_PATH.read_text())
    try:
        with urllib.request.urlopen(url, timeout=FETCH_TIMEOUT) as resp:
            body = resp.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError):
        if CACHE_PATH.exists():
            return json.loads(CACHE_PATH.read_text())
        return None
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(body)
    return json.loads(body)


def main() -> int:
    if not VERCEL_JSON.exists():
        print(f"vercel.json not found at {VERCEL_JSON}", file=sys.stderr)
        return 1

    config = json.loads(VERCEL_JSON.read_text())
    schema_url = config.get("$schema", DEFAULT_SCHEMA_URL)
    schema = load_schema(schema_url)
    if schema is None:
        print("skipping schema check (no network, no cache)")
        return 0

    import jsonschema

    try:
        jsonschema.validate(instance=config, schema=schema)
    except jsonschema.ValidationError as err:
        location = "/".join(str(p) for p in err.absolute_path) or "<root>"
        print(f"vercel.json schema validation failed at {location}: {err.message}", file=sys.stderr)
        return 1

    print("vercel.json: schema OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
