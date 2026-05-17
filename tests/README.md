# tests

Four lightweight integrity checks that run in CI on every push and PR. They guard the kinds of breakage that are easy to introduce and hard to spot visually: `vercel.json` schema drift, dangling service entrypoints, broken relative asset links, and absolute-path references that would break under a `routePrefix` change.

## Run locally

```
pip install -r tests/requirements.txt
python3 tests/validate_vercel_json.py
python3 tests/check_entrypoints.py
python3 tests/check_asset_links.py
python3 tests/check_no_absolute_paths.py
```

Or in one shot via the project slash command: `/vercel-preflight`.

## What CI runs

`.github/workflows/ci.yml` runs all four scripts on `push` and `pull_request`. Each script exits 0 on success, 1 on failure, and prints actionable diagnostics on stderr.
