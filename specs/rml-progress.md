# rayaq.ca/rml — build progress

Running log for the rml build loop and the daily Routine. Read this first, update it last.
The contract is `specs/rml.md` (spec v2); this file records where the build actually stands.

**Last updated:** 2026-10-25 (daily run). Pin moved to `2b04eb6`; `data-metrics`, `classical` and `retrieval` shipped. The next run follows upstream, then builds `quantization`, `model-files`, `tokenizers`.

## Upstream pin

`rayaq-siddiqui/rml@2b04eb6a782de499de7865cefb7ccae7275acf24` (committed 2026-10-25,
"examples: tiny_models, a CNN, an LSTM and a transformer from PyTorch, JAX and TensorFlow run
in C++"), rml 0.1.0, Apache-2.0, analyzed 2026-10-25. Moved from `22c99d3` (11 commits: GEMM
column balancing, a blocked and threaded strided copy, the conv bias fold, a thread-pool
benchmark, every rml benchmark cell re-run, the `tiny_net` and `tiny_models` examples, and
`docs/kernels.md` / `docs/progress.md` updates). Held in `rml_docs.UPSTREAM`. The repository is
private, so pinned links 404 until it is public.

## §10 acceptance criteria

- [ ] `/rml` renders the §6 diagram and lists every §5 page.
- [ ] Every §5 page exists, meets its "Must cover" column, and is marked ready.
- [ ] `decoder` meets §8 with at least two SVG diagrams.
- [ ] Every Inference stack page is ready and `stack` has its layer diagram.
- [ ] Every source link is pinned; §7.5 tests exist and pass.
- [x] Homepage card links to `/rml`.
- [x] Mobile at 390px: no horizontal page scroll (`/rml`, `/rml/tensors`, `/rml/runtime`, `/rml/linalg`, `/rml/random`, `/rml/autograd`, `/rml/stack`, `/rml/exporters`, `/rml/graph-ir`, `/rml/executor`, `/rml/lowering`, `/rml/benchmarks`, `/rml/nn`, `/rml/training`, `/rml/data-metrics`, `/rml/classical`, `/rml/retrieval`; rerun per page).
- [x] The daily Routine has run at least once and cloned rml.

## Queue

Shipped before spec v2:

1. ~~Scaffold (module, routes, layout, index with §6 diagram, CSS, tests, homepage card,
   `AGENTS.md` notes)~~
2. ~~`tensors`~~
3. ~~`runtime`~~
4. ~~`linalg`~~
5. ~~`random`~~
6. ~~`autograd`~~

Spec v2 order, Inference stack first:

7. ~~`stack`~~
8. ~~`exporters`~~
9. ~~`graph-ir`~~
10. ~~`executor`~~
11. ~~`lowering`~~
12. ~~`benchmarks`~~
13. ~~`nn`~~
14. ~~`training`~~
15. ~~`data-metrics`~~
16. ~~`classical`~~
17. ~~`retrieval`~~
18. `quantization`
19. `model-files`
20. `tokenizers`
21. `decoder` (flagship, §8)
22. `generation`
23. `kernels`
24. `models-memory`
25. `examples`
26. `testing`

## Daily Routine

"rayaq.ca/rml — architecture reference agent" (`trig_01S4ui62EMp6wDGtW96h22La`), daily
12:44 UTC on Opus 5.5, fresh session per run (weekly on Saturdays until 2026-10-24). Each
run follows rml upstream first (re-checks ready pages, moves the pin), then builds up to
three queued pages; once the queue is empty it keeps following upstream daily. The
session-only `/loop` jobs that built pages earlier are retired.

## Log

- 2026-10-20 — `00e22a1` spec and progress log; `8242e96` scaffold; `3155c71` `AGENTS.md`
  notes; `d49afa8` `tensors` page, plus `rml_docs.page_link`, which renders plain text for
  pages not yet ready so cross-links never 404.
- 2026-10-20 — `032d685` `runtime` page (errors, allocation, arena, thread pool).
- 2026-10-20 — `9b1b305` `linalg` page (Matrix, MatMul, blocked GEMM and benchmark, LU, QR,
  Cholesky, Jacobi eigen and SVD, norms). No benchmark numbers are committed upstream, so none are quoted.
- 2026-10-21 — `d98c9e8` fixed clipped labels and black-filled accent boxes in the `linalg`
  diagrams; `b5ec1b2` `random` page (Philox, Generator, distributions, callers).
- 2026-10-21 — `b09ea6c`, `5cff680` homepage card first in the grid and rewritten for the
  new direction; `7775841` commits are authored by the owner (`AGENTS.md`).
- 2026-10-21 — `7fffc8a` `autograd` page. `346fedb` spec v2 (owner's redirect to the
  inference stack). Re-pin to `928a285` with the Inference stack group, `rml/graph` and
  `examples/graph_run` in the registry, the index rewritten, and the runtime page's arena
  citation corrected.
- 2026-10-22 — `e0c793d` `stack` page (levels diagram, scope, zoo plan, first results).
- 2026-10-24 — `2daeab6` `exporters` page (builder, three exporters, passes, zoo, golden fixtures).
- 2026-10-24 — first daily scheduled run: blocked. The session had no access to
  `rayaq-siddiqui/rml` (git clone asked for credentials; GitHub access was scoped to
  `rayaq-website` only, and no `add_repo` tool was available). Pin unchanged, no pages built;
  all 1066 tests passed.
- 2026-10-24 — daily run, rml readable. `7142b9c` follow upstream to `a948ac7`: stack (every
  level built, 19-model table, new benchmark status), exporters (StableHLO route, new passes,
  zoo, six fixture routes, agreement tests), linalg (dispatch, GEMV and few-row paths,
  `PackedB`, `docs/kernels.md` numbers), runtime (`BufferPool`, spinning pool, grains),
  tensors (line ranges, pooled storage), index; `buffer_pool`, `fusion`, `kernels` added to
  `MODULES`. `3b6553e` `graph-ir` page; `f782b89` `executor` page; `628e0ac` `lowering`
  page; `a81aba6` AGENTS.md note. All 1066 tests pass; mobile check passes on every ready page.
- 2026-10-24 — second daily run. `6b5ef5c` follow upstream to `22c99d3`: lowering (grouping
  rules, `FusedGroup` outputs, row-strided inputs, new "An LSTM step" section, packed-weight
  timings, line ranges), executor and stack (multi-output groups), linalg (packed-weight
  timings), exporters (Python 3.12 venv), runtime, index; `docs/progress.md` and
  `docs/kernels.md` line ranges moved everywhere. `3abe91e` `benchmarks` page; `ff29950` `nn`
  page; `c81dae4` `training` page. All 1066 tests pass; mobile check passes on every ready page.

- 2026-10-25 — daily run. `849a599` follow upstream to `2b04eb6`: benchmarks (results rewritten
  from the re-run report), lowering (GEMM column balancing, dropped recurrence fold, new conv bias
  section, strided copy, results), executor (conv2d+add fold), linalg (`UnitColumns`,
  `BM_GemmPackedB`), tensors (`StridedCopy`), runtime, exporters (new "Exact tiny examples"
  section; `tiny_net` and `tiny_models` added to `EXAMPLES`), stack, index; moved line ranges
  everywhere. `61efbeb` `data-metrics` page; `0e12d60` `classical` page (registry summary now
  says fifteen estimators); `1790c62` `retrieval` page. All 1067 tests pass; mobile check passes
  on every ready page.

## Deliberate deviations

- **Commit-message numbers are not quoted.** Several upstream commits carry timings in their
  messages (for example the small-ops grain change); pages quote only `docs/progress.md`,
  `docs/kernels.md` and `docs/bench/frameworks.md`.

## Open gaps / questions for the owner

- **`docs/graph_ir.md` lags the executor.** At `2b04eb6` its Execution section still says ops
  call `rml/nn`'s conv and pool and that the loader rejects unknown ops; the pages describe the
  code (direct conv, op checks in `Executor::Create`). (The checklist lag logged earlier is
  resolved: L163 and L170 are now checked and L169 quotes the report's 38 of 171.)
- **Spec §3.6 lists landed work as planned.** It names the StableHLO route, the kernel-level
  IR and the fast-CPU items as planned at spec v2; all have landed. The section follows
  §3.6's rule (flip when landed); the owner may want to refresh that sentence.
- **`rml/nn/attention.h` names a module that does not exist.** Its L9–10 say the inference
  engine's fused attention kernel in `rml/backend` is tested against the readable version;
  there is no `rml/backend` at the pin and `rml/llm` includes nothing from `rml/nn`. The `nn`
  page marks it planned. Likewise `conv.h` describes Conv2d as unfold plus a product while the
  code builds patch rows (`PatchRowsFunction`); the page describes the code.
- **Spec §5 says "all 11 classical models".** `rml/classical` has fifteen public estimator
  classes in ten model headers (eleven headers counting `common.h`). The page and the registry
  summary say fifteen; the owner may want to update the spec row.
- **`gradient_boosting.h` and its code differ by a factor.** Its L13–15 give the split gain "up
  to a factor 1/2", and `Score` leaves the ½ out; the best split is the same. The `classical` page
  notes it. Random forest, gradient boosting and the decision-tree classifier have no
  scikit-learn fixture, and the k-means test checks only inertia.
- **`rml/data` preprocessing and splits and all of `rml/metrics` have no callers outside their
  tests.** Only `TensorDataset` and `DataLoader` are used (by 13 examples); `data-metrics` says so.
- **Arena is unused outside `rml/core`.** `docs/architecture.md` says per-step scratch
  comes from an arena reset each step, but no code outside `rml/core` uses `Arena` at the
  pin (re-checked at `a948ac7`; the graph executor uses a `BufferPool` instead). The
  `runtime` page presents it as available, not wired into decoding.
