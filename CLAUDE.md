# CLAUDE.md

Guidance for Claude Code (and other LLM-driven agents) working in this repository.

## Project overview

DeepDive is the public artifact repository for the paper *"DeepDive: Advancing Deep Search Agents with Knowledge Graphs and Multi-Turn RL"* (arXiv 2509.10446, THUDM / z-ai). The paper presents a pipeline that synthesizes hard multi-hop QA pairs from knowledge-graph random walks and then trains deep-search agents with multi-turn GRPO on those pairs.

This repo is primarily a **dataset + documentation release**. The QA dataset itself lives on Hugging Face (`zai-org/DeepDive`); the model weights are listed as "coming soon" and are not in this repo. The only executable code shipped here is the synthetic QA generation pipeline under `qa_synthetic/`. The root `README.md` is the authoritative paper-level reference (results tables, citation, methodology figures).

## Repository layout

```
.
├── README.md            # Paper overview, results tables, BibTeX — public landing page
├── assets/              # 8 SVG figures referenced from README.md
└── qa_synthetic/        # Python pipeline (the only executable code in the repo)
    ├── README.md        # Canonical setup + run instructions
    ├── requirements.txt
    ├── kilt_query.py
    ├── random_walk_kilt.py
    ├── generate_qa.py
    └── prompt.py
```

There is no package manifest at the repo root, no `setup.py`/`pyproject.toml`, and no top-level `tests/`. Everything Python lives inside `qa_synthetic/`.

## qa_synthetic pipeline

The four modules form a linear pipeline:

- `qa_synthetic/kilt_query.py` — `KiltClient` wraps MongoDB collection `kilt.knowledgesource` (the imported KILT Wikipedia snapshot). Exposes `query_text(title)`, `query_relations(title)`, and `kilt_search(query)` with exact → text-index → regex fallbacks. Running this file directly executes `run_smoke_tests()` against a local MongoDB.
- `qa_synthetic/random_walk_kilt.py` — multi-threaded random walks over KILT via `KiltClient`. At each step, an OpenAI model (default `gpt-4.1-2025-04-14`) ranks up to 5 unvisited anchor candidates and picks the most logically connected next node. Sub-paths of length `--save-every-k` (default 8) with ≥7 unique nodes are appended to `./random_walk_outputs/random_walk_<topic>.jsonl` and merged at the end.
- `qa_synthetic/generate_qa.py` — feeds each walk path into an LLM via OpenRouter (default `gemini-2.5-pro`) using the template in `prompt.py`, then parses `<question>:` / `<answer>:` out of the response. Resumable: on restart it reads existing output ids (keyed by `--id-key`, default `id`) and skips them.
- `qa_synthetic/prompt.py` — single `GENERATE_QUESTION_KILT` template that drives the QA generation; it instructs the LLM to obscure all names/places/dates/events along the path so the answer can't be matched by keyword.

## Running the pipeline

The canonical step-by-step (MongoDB install, KILT download, indexing) lives in `qa_synthetic/README.md`. Short reference:

```bash
pip install -r qa_synthetic/requirements.txt   # fastapi, uvicorn, pymongo, openai, python-dotenv

# Prereqs:
#   - MongoDB on localhost:27017 with the KILT knowledgesource collection imported (~35 GB JSON)
#   - qa_synthetic/.env with OPENAI_API_KEY, OPENAI_BASE_URL, OPENROUTER_API_KEY, OPENROUTER_BASE_URL

python3 qa_synthetic/kilt_query.py              # smoke-test MongoDB connection + text index

python3 qa_synthetic/random_walk_kilt.py        # produces ./random_walk_outputs/random_walk_*.jsonl

python3 qa_synthetic/generate_qa.py \
  --input  ./random_walk_outputs/random_walk_architecture.jsonl \
  --output ./random_walk_outputs/random_walk_architecture_qa.jsonl
```

Note that `tqdm` is imported by both `random_walk_kilt.py` and `generate_qa.py` but is **not** listed in `requirements.txt` — install it explicitly when rebuilding the env.

## Conventions & gotchas

- **Style**: 4-space indent, selective `typing` hints. Both CLI scripts use `argparse` with env-var defaults (e.g. `default=os.getenv("OPENAI_API_KEY")`); preserve that pattern when adding flags so configuration can come from either CLI or `.env`.
- **LLM retry shape**: both scripts implement their own retry-with-backoff loops — see `call_llm` in `qa_synthetic/generate_qa.py:43` and `query_llm` in `qa_synthetic/random_walk_kilt.py:65`. Follow the same pattern for new model calls rather than introducing a new abstraction.
- **Resumability**: `generate_qa.py` resumes off `--id-key` in the existing output JSONL (`parse_jsonl_ids` at `qa_synthetic/generate_qa.py:66`). `random_walk_kilt.py` appends to its per-topic JSONL with `a+`. Don't delete partial outputs to "start clean" — re-running will pick up where it left off.
- **Two different LLM providers**: `random_walk_kilt.py` reads `OPENAI_*` env vars; `generate_qa.py` reads `OPENROUTER_*`. Keep them separate when editing.
- **.gitignore** excludes `/data` and `/website` only. Generated walks/QA JSONLs under `qa_synthetic/random_walk_outputs/` are **not** ignored — do not commit large generated files; add them to `.gitignore` first if needed.

## What's not in this repo

- No tests, linter config, formatter config, or CI workflows. Do not claim to "run tests" before completing tasks — smoke-test scripts manually instead (e.g. `python3 qa_synthetic/kilt_query.py`).
- No training, RL, or inference code. The paper covers SFT + multi-turn GRPO, but only the data-synthesis half is open-sourced here. Model weights are listed in `README.md` as "coming soon".
- No top-level dependency manifest. `qa_synthetic/requirements.txt` is the only dependency list.

## Editing README.md

The root `README.md` is the public-facing paper landing page. The numeric results tables (BrowseComp / BrowseComp-ZH / Xbench-DeepSearch / SEAL-0) and the BibTeX citation block are authoritative — do not paraphrase, restructure, or "tidy up" numbers when making edits. Asset references (`./assets/*.svg`) must keep matching the files in `assets/`.
