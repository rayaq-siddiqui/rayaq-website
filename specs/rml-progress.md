# rayaq.ca/rml — build progress

Running log for the rml build loop and the weekly Routine. Read this first, update it last.
The contract is `specs/rml.md` (spec v1); this file records where the build actually stands.

**Last updated:** 2026-10-21. Spec v2: the Inference stack group leads the queue. Scaffold, `tensors`, `runtime`, `linalg`, `random` and `autograd` shipped; `stack` is next.

## Upstream pin

`rayaq-siddiqui/rml@928a285de296cded11d01266b334b02a56e4375e` (committed 2026-10-21,
"docs: StableHLO import and a kernel-level IR in the plan"), rml 0.1.0, Apache-2.0,
analyzed 2026-10-21. Moved from `927e190` for spec v2; the shipped pages' sources did not
change between the two, apart from one added row in `docs/architecture.md`. Held in `rml_docs.UPSTREAM`. The repository is private, so pinned
links 404 until it is public.

## §10 acceptance criteria

- [ ] `/rml` renders the §6 diagram and lists every §5 page.
- [ ] Every §5 page exists, meets its "Must cover" column, and is marked ready.
- [ ] `decoder` meets §8 with at least two SVG diagrams.
- [ ] Every Inference stack page is ready and `stack` has its layer diagram.
- [ ] Every source link is pinned; §7.5 tests exist and pass.
- [x] Homepage card links to `/rml`.
- [x] Mobile at 390px: no horizontal page scroll (`/rml`, `/rml/tensors`, `/rml/runtime`, `/rml/linalg`, `/rml/random`, `/rml/autograd`; rerun per page).
- [ ] The weekly Routine has run at least once and cloned rml.

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

7. `stack`
8. `exporters`
9. `graph-ir`
10. `executor`
11. `lowering`
12. `benchmarks`
13. `nn`
14. `training`
15. `data-metrics`
16. `classical`
17. `retrieval`
18. `quantization`
19. `model-files`
20. `tokenizers`
21. `decoder` (flagship, §8)
22. `generation`
23. `kernels`
24. `models-memory`
25. `examples`
26. `testing`

## Weekly Routine

"rayaq.ca/rml — architecture reference agent" (`trig_01S4ui62EMp6wDGtW96h22La`), Saturdays
12:44 UTC, fresh session per run: builds up to three queued pages, then maintains the pin.

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

## Deliberate deviations

- **29 examples, not 30.** The plan counted 30 directories under `examples/`; the pin has
  29. `EXAMPLES` lists what is in the tree.

## Open gaps / questions for the owner

- **Arena is unused outside `rml/core`.** `docs/architecture.md` says per-step scratch
  comes from an arena reset each step, but no code outside `rml/core` uses `Arena` at the
  pin. The `runtime` page presents it as available, not wired into decoding. Revisit when
  the pin moves.
