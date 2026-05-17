---
description: Scaffold a new apps/<name>/ service and append its experimentalServices entry to vercel.json
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion
---

Scaffold a new service in this monorepo. Drive the user through the choices, create the files, edit `vercel.json`, then run `/vercel-preflight`. Do not commit.

## Step 1 — ground in current patterns

Read `CLAUDE.md` first. Pay attention to:

- The **Planned services** section (reference shapes for static / FastAPI / TanStack / worker).
- The **Known deploy failures** table — in particular: per-service `framework` **must be a string slug**; never set it to `null`. For static services, omit the `framework` field entirely and use a **file entrypoint**.
- Routing rules: Vercel strips `routePrefix` before handoff to the service. Frontend frameworks must set their own `basePath` to match `routePrefix`.

## Step 2 — collect inputs

Use `AskUserQuestion` to collect:

1. **Service name** (single word, lowercase, used as the key in `experimentalServices` and the directory name under `apps/`).
2. **Service type**: `static`, `fastapi`, `tanstack`, or `worker`.
3. **`routePrefix`** (e.g. `/api`, `/dashboard`). For `worker`, no prefix is needed — skip this question.

## Step 3 — scaffold files

Create `apps/<name>/`. The starter file depends on type:

- **static** — `apps/<name>/index.html` with a minimal `<!doctype html>` page that names the service. Entrypoint will be the file (`apps/<name>/index.html`); do NOT add a `framework` field.
- **fastapi** — `apps/<name>/main.py` with `from fastapi import FastAPI`, `app = FastAPI()`, and one `@app.get("/")` returning `{"service": "<name>"}`. **Routes inside this app must not include the `routePrefix`** — Vercel strips it. Entrypoint will be the file (`apps/<name>/main.py`).
- **tanstack** — do NOT half-scaffold this. Create only `apps/<name>/README.md` listing the remaining manual steps: `npm create @tanstack/start`, add `nitro/vite` to `vite.config.ts` plugins next to `tanstackStart()` and `viteReact()`, set the router's `basePath: "<routePrefix>"`, then come back and add the service block to `vercel.json` with `entrypoint: "apps/<name>"` and `framework: "tanstack"`. Skip Step 4 below for tanstack and tell the user to re-run this command after running the setup.
- **worker** — `apps/<name>/main.py` with a minimal worker stub. Entrypoint will be the file. Service block uses `type: "worker"` and **no `routePrefix`**.

## Step 4 — edit vercel.json

Read `vercel.json`. Append a new key under `experimentalServices` preserving existing services. Shape by type:

```jsonc
// static
"<name>": { "entrypoint": "apps/<name>/index.html", "routePrefix": "<routePrefix>" }

// fastapi
"<name>": { "entrypoint": "apps/<name>/main.py", "routePrefix": "<routePrefix>" }

// worker
"<name>": { "type": "worker", "entrypoint": "apps/<name>/main.py" }
```

Use `Edit`, not `Write` — don't risk clobbering the existing file. Verify the result parses by running `python3 -c "import json; json.load(open('vercel.json'))"`.

## Step 5 — validate

Run the preflight checks:

```
python3 tests/validate_vercel_json.py
python3 tests/check_entrypoints.py
python3 tests/check_asset_links.py
python3 tests/check_no_absolute_paths.py
```

If anything fails, surface the error and stop. Do not commit.

## Step 6 — report

Summarize: which files were created, what was added to `vercel.json`, and the next manual step (e.g. for TanStack: install deps + set basePath; for FastAPI: define your real routes). Tell the user to review and commit themselves.
