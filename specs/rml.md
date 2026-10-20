# rayaq.ca/rml — rml architecture reference

**Status:** approved for build · **Owner:** Rayaq Siddiqui · **Spec version:** 1 (2026-10-20)

This is the product and technical contract for `rayaq.ca/rml`. The build loop and the
weekly Routine build and maintain the section against it. Build progress lives in
`specs/rml-progress.md`. Don't edit this spec without the owner's say-so. If the code and
the spec disagree, fix the code or record a deliberate deviation in the progress file.

---

## 1. Goal

`rayaq-siddiqui/rml` is the owner's C++20/Bazel machine learning library: tensors, linear
algebra, autograd, neural network layers, optimizers, classical models, retrieval,
quantization, model file formats, tokenizers and an LLM runtime that runs real open-weight
decoder models. `/rml` is a source-linked architecture reference to it, in the style of
`/jj-vfs-poc`: a reader who knows C++ and some ML should be able to find where anything
lives, how the modules layer, and how one token of LLM decode actually happens, with every
claim one click from the pinned line that backs it.

Where a page explains a concept that `/ml-models` teaches, it links there rather than
re-teaching it.

## 2. Non-goals

- A tutorial on machine learning. `/ml-models` is that.
- API documentation for every function. Pages explain design and data flow, and link to
  headers for the full surface.
- Benchmarks run by this site. Numbers come only from rml's own docs or tests, cited.
- Anything about the Python reference tools beyond what they generate and why.

## 3. Hard constraints

1. **Static content.** Pages are server-rendered from committed templates. No runtime call
   to GitHub or any other service, no client-side fetching, no JavaScript framework.
2. **$0 incremental cost.** No new paid service, no new hosting, no new runtime dependency
   in `backend/requirements.txt`.
3. **Every claim is sourced.** Each type, function table, flow and algorithm links to the
   exact upstream file, pinned to the analyzed commit
   (`https://github.com/rayaq-siddiqui/rml/blob/<sha>/<path>#L<start>-L<end>`). Never
   `blob/main`. The repository is private for now, so these links 404 until it is public.
   That is expected; they are still written and tested.
4. **Pinned to one upstream commit.** The whole section describes exactly one rml commit,
   recorded in code (§7.3) and shown on every page.
5. **Never fabricate.** Type, function, file and option names, dtypes, block layouts,
   defaults and error behaviour are copied from source, not paraphrased from memory. When
   unsure, omit and log the gap in the progress file.
6. **Planned is not implemented.** Anything that appears only in rml's `docs/` and is
   missing from the source tree at the pin is marked *planned*, never described as working.
   At spec time that includes `rml/graph` and `tools/rml_export/` (`docs/graph_ir.md`), the
   `backend` and `profile` modules named in `docs/architecture.md`, and the kernels
   `docs/kernels.md` lists as planned. When a later pin adds them, the page flips them.
7. **Licensing.** rml is Apache-2.0. Every page footer says "Describes
   rayaq-siddiqui/rml at `<sha12>`, Apache-2.0". Code excerpts stay short.
8. **Section isolation.** Several Routines push to this repo. This section owns only its
   own files (§7). It never edits another section's module, templates, CSS or tests.
   Shared files (`app.py`, `home.html`, `app_tests.py`, `AGENTS.md`) get additive edits
   only.
9. **House rules.** Everything in `AGENTS.md` applies.

## 4. Information architecture

- `/rml` — overview, the library's two goals (a readable from-scratch ML library, and a
  fast CPU runtime for real open-weight LLMs), the module-layering diagram (§6), and the
  page index grouped as **Foundations**, **Learning**, **Classical & retrieval**,
  **LLM runtime** and **Project**.
- `/rml/<slug>` — one deep-dive page per §5 row. Each page starts with a `<header>` (title
  and tagline), has an on-page table of contents built from its `h2`/`h3` ids, and ends
  with previous/next links.
- The left nav lists every page; unbuilt pages show as pending, not as links.

## 5. Page inventory

Build order is the table order.

| # | Slug | Group | Must cover | Source set |
|---|---|---|---|---|
| 1 | `tensors` | Foundations | dtypes and their storage (f16/bf16 rounding, Q8_0/Q4_0 blocks), `Shape`/`Strides`, broadcasting, `ForEachRow`, `Storage` and `Tensor`, views vs copies, the f32 reference ops, `RML_CHECK` | `rml/core` dtype, shape, strided, tensor, ops, check |
| 2 | `runtime` | Foundations | `Status`/`Expected`, the no-throw error model, aligned allocation and its counters, `ThreadPool`/`ParallelFor` chunking and determinism | `rml/core` status, allocator, thread_pool; `docs/architecture.md` Errors, Memory, Threads |
| 3 | `linalg` | Foundations | `Matrix`, matmul and the blocked GEMM (with its benchmark), LU, QR, Cholesky, eigen, SVD, norms | `rml/linalg` |
| 4 | `random` | Foundations | the Philox counter-based generator and the distributions built on it | `rml/random` |
| 5 | `autograd` | Learning | `Variable`, `Function`, the graph and backward pass, the differentiable ops, gradient checking | `rml/autograd` |
| 6 | `nn` | Learning | `Module`, every layer (linear, activation, init, conv, embedding, normalization, dropout, recurrent, attention, transformer) | `rml/nn` |
| 7 | `training` | Learning | losses (classification, regression, contrastive, variational, reductions) and optimizers (SGD, Adam, RMSprop, schedules, clipping, accumulation) | `rml/losses`, `rml/optim` |
| 8 | `data-metrics` | Learning | datasets, preprocessing, splits; classification, regression, ranking and calibration metrics | `rml/data`, `rml/metrics` |
| 9 | `classical` | Classical & retrieval | all 11 classical models, their shared helpers, and the scikit-learn fixture tests | `rml/classical`, `tools/make_sklearn_fixtures.py` |
| 10 | `retrieval` | Classical & retrieval | similarity functions and the IVF index | `rml/retrieval` |
| 11 | `quantization` | LLM runtime | GGML types, block layouts, dequantization, quantized dot products (with benchmark), fixtures | `rml/quant`, `tools/make_quant_fixtures.py` |
| 12 | `model-files` | LLM runtime | memory-mapped files, safetensors, GGUF, checkpoints, and how weights stay mmapped | `rml/io` |
| 13 | `tokenizers` | LLM runtime | the tokenizer interface, pretokenizer, Unicode tables, Hugging Face and GGUF tokenizers, chat templates | `rml/llm` tokenizer, pretokenizer, unicode, unicode_tables, hf_tokenizer, gguf_tokenizer, chat_template |
| 14 | `decoder` | LLM runtime | the flagship (§8) | `rml/llm` config, weight_source, decoder, attention, rope, kv_cache, kernels |
| 15 | `generation` | LLM runtime | samplers, the generation loop, speculative decoding, `examples/rml_chat`, the decode loop in `docs/architecture.md` | `rml/llm` sampler, generation, speculative; `examples/rml_chat` |
| 16 | `kernels` | Project | `docs/kernels.md`: which kernels exist and which are planned | `docs/kernels.md`, `rml/llm/kernels` |
| 17 | `models-memory` | Project | `docs/models.md`: supported model families, memory budgets, status per model | `docs/models.md`, `README.md` |
| 18 | `examples` | Project | every directory in `examples/`, what it builds, and the `/ml-models` concept it demonstrates | `examples/` |
| 19 | `testing` | Project | Bazel module and copts, GoogleTest and Google Benchmark, death tests, golden LLM tests and the tools that make them, CI | `MODULE.bazel`, `rml/copts/rml.bzl`, `tools/`, `.github/workflows/ci.yml` |
| 20 | `graph-ir` | Project | `docs/graph_ir.md`; the whole page is *planned* until the code lands | `docs/graph_ir.md` |

**New code upstream.** When the pin moves and a new module under `rml/` or a new
directory under `examples/` appears, it is added to `MODULES`/`EXAMPLES` and claimed by a
page's source set (an existing page, or a new queued row recorded in the progress file).

## 6. The architecture diagram

The index carries one inline SVG of the module layering from `docs/architecture.md`:
`core` at the bottom, then `linalg`, `random`, `autograd`, `nn`/`losses`/`optim`,
`data`/`metrics`/`classical`, `retrieval`, `quant`, `io`, `llm` at the top, with `backend`
and `profile` drawn dashed as *planned*. Every box links to its page when ready, otherwise
to the module's pinned source tree. The SVG has `role="img"`, a `<title>` and a `<desc>`.

## 7. Technical design

### 7.1 Routing

- `app.py` gets `/rml` and `/rml/<slug>` and stays route-only: it asks `rml_docs` for the
  page (through `rendered_pages`) and returns 404 for unknown or unbuilt slugs.
- `backend/rml_docs.py` owns the pin, registry and rendering and is unit-testable without
  Flask.

### 7.2 Templates and assets

- `frontend/templates/rml/base.html` is the layout; each page is a fragment
  `frontend/templates/rml/<slug>.html` beginning with a `<header>`; the index is
  `rml/index.html`.
- `frontend/static/rml.css` holds this section's styles. Pages also link `jj.css` for the
  shared reference layout, which this section never edits.
- Code blocks are plain `<pre><code>`. Tables: **Item · Type/Signature · Meaning · Source**.

### 7.3 Upstream pin

```python
UPSTREAM = {
    "repo": "https://github.com/rayaq-siddiqui/rml",
    "commit": "<40-char sha>",
    "commit_date": "YYYY-MM-DD",
    "version": "<version from MODULE.bazel>",
    "license": "Apache-2.0",
    "analyzed_on": "YYYY-MM-DD",
}
```

plus `source_url(path, start=None, end=None)` and `tree_url(path)`. Every rml link goes
through them. `ml_models_link(slug, text)` links `/ml-models/<slug>` only when
`ml_models_docs.find_page` says that page is ready, and is plain text otherwise.

### 7.4 Registry

- `PAGES`: ordered, each entry with `slug`, `title`, `group`, `summary`, `sources`, `ready`.
- `MODULES`: every directory under `rml/` at the pin with its source files.
- `EXAMPLES`: every directory under `examples/` at the pin.

### 7.5 Tests (`backend/tests/rml_docs_tests.py`, plus `app_tests.py` additions)

- The pin is well-formed: 40 hex chars, ISO dates, semver version, license `Apache-2.0`.
- Slugs, titles and summaries are unique and non-empty; every page has sources.
- Every ready page has a template; only ready pages route; unknown slugs 404.
- Every rml link is pinned to `UPSTREAM.commit`; no `blob/main`.
- Every internal `/rml` and `/ml-models` link on a rendered page resolves to 200.
- The index lists every page; every page shows `commit[:12]` and "Apache-2.0".
- Every `MODULES` and `EXAMPLES` entry is claimed by some page's sources.
- `decoder`, once ready, has the §8 `h2` anchors and at least two `<svg viewBox`.
- The index SVG has `role="img"`, `<title>` and `<desc>`.
- The homepage links to `/rml`.

## 8. `decoder` deep dive — requirements

The flagship page. `h2` sections with these ids, in order, all sourced:

1. `config` — the model config: fields, how they are read from safetensors/GGUF metadata,
   and per-family differences.
2. `weights` — `WeightSource`: how tensors are named, found and kept mmapped.
3. `forward-pass` — one layer's dataflow (norm, attention, residual, MLP or MoE, residual),
   drawn as an SVG.
4. `attention-kv-cache` — the attention kernel and the KV-cache layout (dtype, shape,
   growth), drawn as an SVG.
5. `rope` — rotary embeddings: frequencies, scaling variants, which family uses which.
6. `moe` — expert routing for Mixtral, Qwen3-MoE and OLMoE.
7. `families` — Llama, Mistral, Mixtral, Qwen2, Qwen3, Qwen3-MoE, Gemma 3 and OLMoE: what
   differs, and which golden tests pin each.

## 9. Keeping it current

- **Build loop** (an interactive session's `/loop`): each iteration builds the first unbuilt
  queued page, sets `"ready": True`, runs the tests, checks the 200s and 390px, updates the
  progress file and pushes `rml: <page>` to `main`. When nothing is queued it prints
  "rml build complete" and stops.
- **Weekly Routine** ("rayaq.ca/rml — architecture reference agent", Saturdays 13:00 UTC):
  pulls, runs the tests, builds the next queued page if any; otherwise diffs upstream
  `HEAD` against the pin over each page's source set, updates affected pages, queues pages
  for new modules or examples, flips *planned* items that have landed, and bumps `UPSTREAM`
  in the same commit. It pushes small commits straight to `main` (merge, never rebase or
  force) and finishes with an `rml: record progress` commit.

## 10. Acceptance criteria

- [ ] `/rml` renders the §6 diagram and lists every §5 page.
- [ ] Every §5 page exists, meets its "Must cover" column, and is marked ready.
- [ ] `decoder` meets §8 with at least two SVG diagrams.
- [ ] Every source link is pinned; §7.5 tests exist and pass.
- [ ] Homepage card links to `/rml`.
- [ ] Mobile at 390px: no horizontal page scroll (`tools/rml/check_mobile.js`).
- [ ] The weekly Routine has run at least once and cloned rml.
