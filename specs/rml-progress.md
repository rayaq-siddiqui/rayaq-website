# rayaq.ca/rml — build progress

Running log for the rml build loop and the weekly Routine. Read this first, update it last.
The contract is `specs/rml.md` (spec v1); this file records where the build actually stands.

**Last updated:** 2026-10-20 (first run). Scaffold and `tensors` shipped; `runtime` is next.

## Upstream pin

`rayaq-siddiqui/rml@927e1904d2d01c0317fb810b08c0815503fed7e8` (committed 2026-10-20,
"docs: rml-graph IR for models exported from Python frameworks"), rml 0.1.0, Apache-2.0,
analyzed 2026-10-20. Held in `rml_docs.UPSTREAM`. The repository is private, so pinned
links 404 until it is public.

## §10 acceptance criteria

- [ ] `/rml` renders the §6 diagram and lists every §5 page.
- [ ] Every §5 page exists, meets its "Must cover" column, and is marked ready.
- [ ] `decoder` meets §8 with at least two SVG diagrams.
- [ ] Every source link is pinned; §7.5 tests exist and pass.
- [x] Homepage card links to `/rml`.
- [x] Mobile at 390px: no horizontal page scroll (`/rml`, `/rml/tensors`; rerun per page).
- [ ] The weekly Routine has run at least once and cloned rml.

## Queue

1. ~~Scaffold (module, routes, layout, index with §6 diagram, CSS, tests, homepage card,
   `AGENTS.md` notes)~~
2. ~~`tensors`~~
3. `runtime`
4. `linalg`
5. `random`
6. `autograd`
7. `nn`
8. `training`
9. `data-metrics`
10. `classical`
11. `retrieval`
12. `quantization`
13. `model-files`
14. `tokenizers`
15. `decoder` (flagship, §8)
16. `generation`
17. `kernels`
18. `models-memory`
19. `examples`
20. `testing`
21. `graph-ir`

## Log

- 2026-10-20 — `00e22a1` spec and progress log; `8242e96` scaffold; `3155c71` `AGENTS.md`
  notes; `d49afa8` `tensors` page, plus `rml_docs.page_link`, which renders plain text for
  pages not yet ready so cross-links never 404.

## Deliberate deviations

- **29 examples, not 30.** The plan counted 30 directories under `examples/`; the pin has
  29. `EXAMPLES` lists what is in the tree.

## Open gaps / questions for the owner

- None yet.
