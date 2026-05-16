# CLAUDE.md

Guidance for Claude Code (and other LLM-driven agents) working in this repository.

## Project overview

`drewdas/DeepDive` is a Vercel-hosted multi-service project, set up around the DeepDive paper (THUDM, arXiv 2509.10446). Today it ships a single static landing page at `apps/web/`; the structure is in place so additional services (FastAPI backend, TanStack Start dashboard, etc.) can be added as new `apps/<name>/` directories without restructuring.

**Hosting model:** Vercel's experimental Services feature — one Vercel project, multiple services declared in `vercel.json` under `experimentalServices`, routed by URL path prefix. The Vercel project's framework setting is **Services** (set in the dashboard); `vercel.json` must satisfy that.

The upstream paper repo (`THUDM/DeepDive`) lives unchanged at `references/DeepDive/` as a read-only reference — see `references/DeepDive/CLAUDE.md` for guidance about that subtree.

## Repository layout

```
.
├── CLAUDE.md            # this file
├── README.md            # public landing copy (stub)
├── vercel.json          # experimentalServices config — single source of truth for service routing
├── .mcp.json            # MCP server config (Supabase)
├── apps/
│   └── web/             # static landing page (the only service today)
│       ├── index.html
│       ├── styles.css
│       ├── script.js
│       ├── assets/      # SVG figures copied from references/DeepDive/assets/
│       └── .nojekyll
└── references/
    └── DeepDive/        # upstream THUDM/DeepDive paper repo (read-only reference)
```

## Vercel Services (experimentalServices)

This feature is officially experimental — schema details can change. The authoritative reference is [vercel.com/docs/services](https://vercel.com/docs/services); confirm anything non-obvious there before assuming current behavior.

### Per-service configuration fields

Documented in [Services > Configuration fields](https://vercel.com/docs/services):

| Field           | Required | Notes                                                                                       |
| --------------- | -------- | ------------------------------------------------------------------------------------------- |
| `entrypoint`    | yes      | Path to a file or directory. Directory entrypoints require framework auto-detection.        |
| `routePrefix`   | web only | URL prefix this service handles. Vercel **strips it before handing off** to the service.    |
| `framework`     | no       | Framework slug to pin (`"nextjs"`, `"vite"`, `"astro"`, `"tanstack"`, etc.).                |
| `memory`        | no       | 128–10240 MB.                                                                               |
| `maxDuration`   | no       | 1–900 s.                                                                                    |
| `includeFiles`  | no       | Glob to include files outside the entrypoint dir.                                           |
| `excludeFiles`  | no       | Glob to exclude files.                                                                      |
| `type`          | no       | `"worker"` for background services (e.g. workflows). Omit for web services.                 |

### Routing rules

- Vercel evaluates `routePrefix` values **longest-to-shortest**, so more specific prefixes win.
- The service mounted at `/` is the catch-all for unmatched requests.
- Backend services are auto-mounted at the prefix — handlers should define their internal routes **without** the prefix (`/items`, not `/api/items`).
- Frontend frameworks (Next.js, TanStack Start, etc.) **must set their own `basePath`** to match `routePrefix` or generated links/assets break.

### Inter-service environment variables

Vercel auto-injects:

- `{SERVICENAME}_URL` — server-side requests between services
- `NEXT_PUBLIC_{SERVICENAME}_URL` — client-side (Next.js), relative paths so CORS is a non-issue

Service names follow the keys in `experimentalServices`. Env vars defined in Project Settings with the same name override the injected ones.

### Local development

```
vercel dev -L         # short for --local; runs all services together, no Cloud auth required
```

Without `-L`, `vercel dev` proxies through Vercel Cloud and needs authentication.

## Current `vercel.json`

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "experimentalServices": {
    "web": {
      "entrypoint": "apps/web",
      "routePrefix": "/",
      "framework": null
    }
  }
}
```

### Why `framework: null`

Top-level `framework: null` is documented as "select Other / no framework." Per-service `framework: null` is **not explicitly documented** — it's the natural extension of the same convention, and it's the minimal change that should let a directory entrypoint deploy without auto-detection.

If a future Vercel build rejects `null` per-service, the **documented fallback** (from the error message itself) is a **file entrypoint**:

```json
"web": {
  "entrypoint": "apps/web/index.html",
  "routePrefix": "/"
}
```

Don't switch preemptively — only if `framework: null` stops working.

## Adding a new service

1. Create `apps/<name>/` with the service code.
2. Add an entry to `experimentalServices` with a unique `routePrefix`.
3. If it's a frontend framework, set the framework's own `basePath` config to match `routePrefix`.
4. If it's a backend service, define routes without the `routePrefix` baked in.

### Planned services (reference shapes — do not commit until the code exists)

**FastAPI backend** (mounts at `/api`):

```jsonc
"api": {
  "entrypoint": "apps/api/main.py",
  "routePrefix": "/api"
}
```

Vercel auto-detects FastAPI when the entrypoint exposes `app = FastAPI()` in `app.py`, `index.py`, `server.py`, or `main.py`. Routes inside that app should be defined as `/items`, not `/api/items` — Vercel strips the prefix.

**TanStack Start dashboard** (mounts at `/dashboard`):

```jsonc
"dashboard": {
  "entrypoint": "apps/dashboard",
  "routePrefix": "/dashboard",
  "framework": "tanstack"
}
```

TanStack Start on Vercel requires the [Nitro Vite plugin](https://vercel.com/docs/frameworks/full-stack/tanstack-start) — add `nitro/vite` to `vite.config.ts` plugins, alongside `tanstackStart()` and `viteReact()`. Also set the router's `basePath: "/dashboard"` so links and asset URLs match the prefix.

**Background worker** (no `routePrefix`):

```jsonc
"jobs": {
  "type": "worker",
  "entrypoint": "apps/jobs/main.py",
  "topics": ["__wkf_*"]
}
```

## Things this stack does NOT support natively

- **Streamlit.** Long-running stateful WebSocket server — incompatible with Vercel's serverless / Fluid Compute runtime. **Host externally** (Fly, Railway, Render, Streamlit Cloud) and either:
  - rewrite to it from `vercel.json` (`routes` / `rewrites`), or
  - put it on a separate subdomain via DNS (no Vercel involvement).
- **Long-running background processes.** Use `type: "worker"` (queue/topic-driven) or external infra.
- **Subdomain-based service routing** *inside one Vercel project.* `experimentalServices` is path-based. For real subdomains you have three options:
  1. **Separate Vercel projects** per subdomain (recommended for full isolation, per-app preview URLs).
  2. **Wildcard domain on one project** (`*.example.com`) + middleware/rewrites that map subdomain → internal path. Multi-tenant pattern.
  3. **Apex + named subdomain** (`example.com`, `app.example.com`) added to the same project — both point at the same service set.

## Conventions & gotchas

- **One service per directory under `apps/`.** Don't co-locate services. Vercel resolves each service's entrypoint independently.
- **Asset paths in `apps/web/index.html` are relative** (`assets/...`). They work because `apps/web/` is served at `/`. If the prefix or directory ever changes, keep the paths relative — don't hardcode an absolute prefix.
- **Equations in `index.html`** render via MathJax from jsDelivr. Dark mode uses `prefers-color-scheme` only — no JS toggle.
- **BibTeX copy button** is the only client-side JS (`apps/web/script.js`). Keep `apps/web/` dependency-free; introducing a bundler would defeat the static deployment.
- **MCP servers** are configured in `.mcp.json` at the repo root. Treat project refs in those URLs as project-scoped infra config, not user-specific.
- **Don't edit `references/DeepDive/`** to change the landing page — it's a snapshot of the upstream paper repo. Change `apps/web/` instead.
- **Don't fabricate test results.** There's no test suite. Verify changes by opening the Vercel preview URL for the branch.

## Common tasks

| Task                          | Where to work                                                    |
| ----------------------------- | ---------------------------------------------------------------- |
| Tweak landing page content    | `apps/web/index.html`                                            |
| Tweak landing page styling    | `apps/web/styles.css`                                            |
| Update figures                | Replace files in `apps/web/assets/` (keep SVG, keep names)       |
| Add a new service             | New `apps/<name>/` + entry in `vercel.json`                      |
| Change service routing        | `vercel.json` only — do not move directories                     |
| Debug deployment failure      | Read the Vercel build log error verbatim; check `framework` slug |
| Run everything locally        | `vercel dev -L` from repo root                                   |

## Git workflow

Feature branches per change; PRs into `main`. The Vercel project is wired to the repo, so every branch gets a preview URL automatically. Don't push to `main` directly — let preview deploys verify the build first.
