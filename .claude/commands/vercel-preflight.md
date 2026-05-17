---
description: Validate vercel.json + apps/ integrity before pushing to avoid Vercel build failures
allowed-tools: Bash
---

Run the four integrity checks in `tests/` and then `npx vercel build` to mirror what Vercel CI does. Report a single pass/fail summary at the end.

Steps:

1. Run each check in order, capturing stdout+stderr+exit code:
   - `python3 tests/validate_vercel_json.py`
   - `python3 tests/check_entrypoints.py`
   - `python3 tests/check_asset_links.py`
   - `python3 tests/check_no_absolute_paths.py`
2. If any of the above failed, **stop here** — print the failing check's stderr and map it to the documented fix from the **Known deploy failures** table in `CLAUDE.md` (e.g. `framework should be string` → "Per-service `framework` must be a string slug; omit the field for static services and use a file entrypoint instead"). Do not run `vercel build`.
3. If all four passed, run `npx vercel build` in the repo root with a 120s timeout. This catches detection / framework errors the static checks can't see. If it fails, surface the verbatim error.
4. Final summary: one line per check (✓ / ✗), then "ready to push" or "blocked: <which check> — <one-line fix>".

Do not commit or push anything. This command only validates.
