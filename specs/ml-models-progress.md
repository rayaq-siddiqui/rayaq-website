# rayaq.ca/ml-models — build progress

This is the running log for the daily ml-models Routine. Read it first and update it last.
The contract is `specs/ml-models.md` (spec v2, read-only without the owner's say-so). This file
records where the build actually stands.

**Last updated:** 2026-10-13 (thirty-seventh run). Spec v2 widens the section from model
architectures to all of machine learning: 12 areas, 93 pages, a seven-step learning path and a
fixed page format. Ready pages: queue items 1-75, the last being `latency-and-throughput`.
The next page is `online-learning` (queue item 76).

## Pins

| Key | Library | Tag | Commit | Committed | License (file) | Analyzed |
|---|---|---|---|---|---|---|
| `pytorch` | PyTorch | `v2.14.1` | `5c4886908584029761b579af026dcfb627c84070` | 2026-09-29 | BSD-3-Clause (`LICENSE`) | 2026-10-08 |
| `sklearn` | scikit-learn | `1.9.1` | `866c0f51e7560ef0303cbcc5f159df5382ea9e3f` | 2026-09-10 | BSD-3-Clause (`COPYING`) | 2026-10-08 |
| `xgboost` | XGBoost | `v3.4.2` | `fdf0888bedddbd444d72994d845c59b3ca182c5b` | 2026-09-15 | Apache-2.0 (`LICENSE`) | 2026-10-08 |

The pins live in `ml_models_docs.PINS`. Each tag was the latest stable release on the analysis
date; PyTorch `v2.15.0` only had release candidates then. Every `pin:path` source in the spec's
page tables was checked to exist at its pin with `git cat-file -e`.

To verify line ranges, clone each pin shallow and sparse at its tag, in a scratch directory:

```bash
git clone --depth 1 --branch v2.14.1 --filter=blob:none --sparse https://github.com/pytorch/pytorch pt
git clone --depth 1 --branch 1.9.1 --filter=blob:none --sparse https://github.com/scikit-learn/scikit-learn skl
git clone --depth 1 --branch v3.4.2 --filter=blob:none --sparse https://github.com/dmlc/xgboost xgb
git -C pt sparse-checkout set --no-cone torch/nn torch/optim torch/amp   # plus what the page needs
```

Use `--no-cone` when the sparse-checkout list includes single files.

## The Routine

"rayaq.ca/ml-models — architecture reference agent" (`trig_01VAVRGkmCoUyweU2zQNd9m6`) runs
every 5 hours (at :44 America/Vancouver) while the queue has unbuilt pages. Once the queue is
empty it becomes the weekly audit in spec §8.1: pins, new open-weight models, and deeper
foundations such as linear algebra. Each firing starts a fresh session that follows spec §8:
pull, clone the pins, build the `← next` page to §6, maintain the pins, record here, check,
and push small commits to `main`. The phone check before each push is
`NODE_PATH=$(npm root -g) node tools/ml_models/check_mobile.js / /ml-models <ready pages>`.

## §9 acceptance criteria

- [x] The index shows the framing, the learning path, the map, the vocabulary, the pins and
      every page grouped by area with its level (tested).
- [ ] Every §5 page is ready and meets its "Must cover" column and §6 (75 of 93 ready, all
      in the §6 format).
- [x] Every link into a pinned repository uses that pin's commit (tested).
- [x] §7.5 tests exist and pass, including the §6 section order for every ready page.
- [x] No ML package in either requirements file (tested). There is no offline data yet.
- [x] Mobile at 390px: no horizontal page scroll on `/`, `/ml-models` or any ready page
      (`check_mobile.js` in headless Chromium, every run).
- [ ] The Routine has run at least once in maintenance mode.

## Decisions

- **Spec v2 (2026-10-08).** At the owner's request `/ml-models` became the place to learn or
  refresh anything in ML: 12 areas, levels, the learning path, the §6 page format and a
  93-page inventory.
- **Multiple pins.** Code links go to pinned PyTorch, scikit-learn and XGBoost releases through
  `pinned_url` and the `src`/`skl`/`xgb`/`pinned` helpers; papers are cited for ideas no library
  implements. Reference repositories (nanoGPT, Hugging Face) are not linked.
- **Prerequisite-first queue**, checked by `test_progress_queue_lists_every_page_after_its_prerequisites`.
- **Connections** come from the registry via `ml_models/_connections.html` (`connections(slug)`).
- **Navigation** groups pages by area in collapsible groups; the breadcrumb names area and
  level; the footer credits every pin. `/` links to `/ml-models` after the jj internals card
  (owner's request, tested in `app_tests.py`).
- **Layout reuses `jj.css`**, linked and never edited; section styles live in `ml_models.css`.
  `ml_models.js` is progressive enhancement only (`data-ml-steps` sliders, the transformer
  page's live table and calculator).
- **`UPCOMING_MODELS`** on the index lists four tiers of notable models with their papers.
- **The transformer page's** numbers come from `attention_weights` and
  `transformer_param_count`, not torch.

## Offline data (`tools/ml_models/` → `frontend/static/ml_models/`)

None yet. Record each script here as script · command · output · seed · library version.

## Verified line ranges at the pins (for upcoming pages)

### PyTorch v2.14.1

Ranges already cited by built pages live in their templates (and in `git log -p` on this
file); this list keeps only what queued pages still need.

- `torch/nn/utils/clip_grad.py`: `clip_grad_norm_` starts at 185.
- `torch/nn/attention/bias.py`: `CausalBias` 86-306, `causal_upper_left`/`causal_lower_right`
  308-376.
- `torch/nn/attention/flex_attention.py`: `BlockMask` 855-1694, `create_block_mask` 1967-2088,
  `flex_attention` starts at 2365.
- `conv.py`: `Conv1d` 225-385 (`ConvTranspose2d` is cited in `autoencoders` and `gans`).
- `torch/linalg/__init__.py`: `inv` 214-292, `vector_norm` 1491-1568; `matrix_norm` starts at 1570.
- `torch/_torch_docs.py` (from `add_docstr(` to `)`): `matmul` 7908-7990, `mm` 7831-7887,
  `bmm` 1706-1762, `addmm` 592-665, `baddbmm` 1512-1581.
- `torch/random.py`: `manual_seed` 49-59; `get_rng_state` 39-46; `set_rng_state` 27-36.
- `torch/optim/optimizer.py`: `Optimizer` starts at 358; `state_dict` 700-791, `zero_grad`
  1048-1110.
- `torch/nn/modules/module.py`: `class Module` 407; `register_buffer` 528.
- Mixed precision, quantization, GPU execution and initialization: ranges live in their
  templates.

### scikit-learn 1.9.1 (start lines; check the end before linking a range)

Paths are under `sklearn/`.

- Linear models, `neighbors/`, `cluster/`, similarity search,
  `metrics/_regression.py` and `impute/`: ranges live in the templates that use them.
- `tree/_classes.py`: `DecisionTreeClassifier` 699, `DecisionTreeRegressor` 1097.
- `ensemble/_forest.py`, `_bagging.py`, `inspection/_permutation_importance.py`,
  `tree/_splitter.pyx`: ranges live in the `random-forests` template.
- `ensemble/_gb.py`: `GradientBoostingClassifier` 1145.
- `ensemble/_hist_gradient_boosting/gradient_boosting.py`: `HistGradientBoostingClassifier` 1762.
- `svm/` and `metrics/pairwise.py` kernels: ranges live in the `support-vector-machines`
  template.
- `decomposition/_pca.py`: `PCA` 113.
- `model_selection/_split.py`: `KFold` 437, `GroupKFold` 533, `StratifiedKFold` 687,
  `TimeSeriesSplit` 1116, `train_test_split` 2797.
- `model_selection/_validation.py`: `cross_validate` 101, `cross_val_score` 512,
  `learning_curve` 1776, `validation_curve` 2283.
- `preprocessing/_data.py`: `StandardScaler` 742 (verified range 742-1189), `MinMaxScaler` 305, `RobustScaler` 1552.
- `preprocessing/_encoders.py`: `OneHotEncoder` 474, `OrdinalEncoder` 1263.
- `pipeline.py`: `Pipeline` 93.
- `calibration.py`: `CalibratedClassifierCV` 74, `calibration_curve` 1227.
- `metrics/_ranking.py`: `roc_auc_score` 511, `precision_recall_curve` 1059.
- `metrics/_classification.py`: `f1_score` 1448, `log_loss` 3321, `brier_score_loss` 3713.

### XGBoost v3.4.2 (start lines)

- `python-package/xgboost/training.py`: `train` 53.
- `python-package/xgboost/sklearn.py`: `XGBModel` 866, `XGBClassifier` 1759.

## Known gaps and deviations

- Where a list above gives only a start line, the end line is unverified. Check the end
  before linking a range. A naive "next top-level line" scan gets fooled by unindented
  docstrings and comments; it gave a wrong end for `RMSNorm`, which was corrected by hand.
- On the index map, the boxes for `vision-transformer`, `mixture-of-experts` and
  `diffusion-unet` link to whole files (`conv.py`, `container.py`) until their pages exist.
- The index map still covers only the architecture area. Widen it to all 12 areas once a
  page in each of the first few areas is ready.
- `transformer` uses the v1 section layout and is exempt from the §6 order test until its
  retrofit (queue item 18).

## First to thirty-sixth runs (2026-10-08 to 2026-10-13) — condensed

Runs 1-3 wrote the spec (v1, then v2), the registry, `LEARNING_PATH`, the §6 and queue tests,
`check_mobile.js` and the Routine. Every run since adds, per page, a tested-helpers commit, a
page commit (page, `ready`, queue ✓) and usually a `docs:` commit; items 1-69 were built in
queue order (run 28: quantization, reinforcement-learning, bayes-rule; run 29:
class-imbalance, random-forests, initialization; run 30: rnns-and-lstms, autoencoders,
variational-autoencoders; run 31: positional-encoding, clustering, vector-indexes; run 32:
distillation, time-series, regression-metrics; run 33: support-vector-machines,
learning-rate-schedules, gans; run 34: encoder-only, learning-to-rank,
data-loading-and-batching; run 35: model-serving, causal-inference, calibration; run 36:
graph-neural-networks, diffusion-models, pretraining). `6f0803f` fixed 13 templates that read a
missing `pins.X.version` key. Pins never moved. The ranges each page links live in its template
(grep `src(`, `skl(`, `xgb(`); `git log -p` on this file has every old commit table and range list.

Findings worth keeping (details in each page and in `git log -p` on this file):

- sklearn's `Entropy` criterion is in bits; XGBoost's `loss_chg` has no ½. `AdamW` is `Adam`
  with `decoupled_weight_decay=True`. `nn.Linear` uses `kaiming_uniform_(a=math.sqrt(5))`,
  a bound of exactly 1/√fan_in.
- Cross-checks ran in scratch venvs, never in requirements: scikit-learn 1.9.1, torch 2.14.1,
  XGBoost 3.2.0 (3.4.2 is not on the mirror; the formulas used are unchanged).
- Use the one-sided Jacobi SVD (eigenvalues of AᵀA squared the condition number).
- `.jj-diagram svg text { fill: var(--jj-text) }` beats an SVG `fill=` attribute, so coloured
  diagram text must use `style="fill: ..."`.
- `ml_models_docs.py` is one ~10,000-line namespace: grep for a helper name before adding it,
  and read the pytest result before committing (run 34 pushed one red commit, `b333b79`, when
  a new `pack_sequences` shadowed the RNN page's helper; `a6aae02` renamed it).
- Jinja: a context dict key named `values`, `items` or `keys` resolves to the dict method;
  macros return Markup, so do arithmetic before calling them, never on their output.

- sklearn's `_SigmoidCalibration` predicts `expit(-(a_*T + b_))` (negative stored slope);
  `_TemperatureScaling` optimizes log β in [−10, 10].
- Chinchilla's Approach 3 constants in the closed form give about 32B params / 3.0T tokens at
  Chinchilla's budget, not 70B; the isoFLOP valley is flat and the 20-tokens rule recovers
  70B / 1.4T. The pretraining page says all three.

Open gaps from these runs:

- Every paper reference so far was cited from memory (arxiv.org is unreachable through the
  proxy); pre-arXiv papers and the GPT-2 report have no link. Each page's references list
  is the full set to re-check once arxiv is reachable.
- No pin implements WordPiece training, BM25, GPTQ, LLM.int8() or any RL algorithm; those pages
  follow the papers. `gpu-execution`'s hardware remarks (on an invented, labelled example GPU),
  `mixed-precision`'s fp8 recipes and the SwiGLU "2/3 hidden size" remark are general knowledge.
- The end lines of the HistGradientBoosting regressor `__init__`, `_incremental_fit_estimator`
  and `Lasso` were inferred.
- `kv-cache` (quantization) and `reinforcement-learning` (preference optimization) name those
  pages in plain text until they are ready.
- No pin implements IVF, PQ or HNSW; those follow the papers. `pca` appears as plain text on
  `clustering` until it is ready.
- Page commits exceed 400 lines because each template is one file.
- Run 33: no pin implements a GAN, a Wasserstein critic, R1 or FID; the schedulers were held
  equal to a simulator of the pinned recursions, not cross-checked in torch. SVM helpers match
  `SVC` (scratch venv). Dirac-GAN: minimax spirals out, non-saturating orbits, R1 converges.
- Run 32: Hinton–Vinyals–Dean's T² remark was confirmed only through secondary quotes;
  Gneiting 2011 is cited only for consistent scoring functions. No pin implements ARIMA, STL
  or MASE; those follow the papers and FPP3.
- Run 34: no pin implements sequence packing with masks or a bucketing sampler; the
  data-loading worker timeline is an idealized model, labelled as such.
- Run 35: no pin implements a serving system, ECE, propensity weighting, DiD or uplift;
  `model-serving`'s figures come from an invented, labelled model. Its references (Rubin,
  Rosenbaum & Rubin, Guo et al., Platt, Zadrozny & Elkan, …) were cited from memory.
- Run 36: no pin implements a GNN library, a diffusion sampler, MinHash or a scaling-law fit;
  those follow the papers. The H100 peak and Llama 3 8B's 15T tokens are general knowledge.

## Thirty-seventh run (2026-10-13) — collaborative-filtering, gradient-accumulation, latency-and-throughput

| Commit | What |
|---|---|
| `cbce53e` `ml-models: add tested collaborative-filtering helpers` | Toy 5×5 rating matrix with two held-out cells, centred-cosine neighbours, bias baseline, rank-2 ALS on observed cells (each solve is `ridge_coefficients`), zero-filled NMF multiplicative updates, implicit confidence, factor-table size |
| `f283b1f` `ml-models: add the collaborative-filtering page` | The page, `ready`, queue ✓ |
| `b6b4393` `ml-models: add tested gradient-accumulation helpers` | 24-token linear toy in 8 variable-length sequences: full-batch vs per-micro mean ÷ k vs ÷ global tokens vs unscaled; clip-after vs per-micro clip; BN micro-batch stats and effective momentum; ring all-reduce bytes with and without `no_sync` |
| `492f50e` `ml-models: add the gradient-accumulation page` | The page, `ready`, queue ✓ |
| `44712dd` `ml-models: add tested latency-and-throughput helpers` | 8B bf16 model on an H100-class part (989 TFLOP/s, 3.35 TB/s, 80 GB): decode-step roofline per batch (KV 131,072 B/token at 2,048 context), prefill, memory batch cap, Little's-law fixed point with prefill stealing decode time, seeded M/D/1 Lindley queue with percentiles, fan-out tail |
| `a261b7b` `ml-models: add roofline points for the latency page` | Log-log roofline coordinates for the diagram, tested to sit under the roof |
| `077666b` `ml-models: add the latency-and-throughput page` | The page, `ready`, queue ✓ |
| (this commit) `docs: record the thirty-seventh ml-models run` | Commit SHAs, pin check, gaps; condenses run 36 |

Findings worth keeping:

- scikit-learn's `NMF` puts every cell in its loss, so blanks act as observed zeros. On the
  example it predicts 2.57 for a held-out 5 (ALS on observed cells: 4.01), and fits the real
  ratings worse too (RMSE 0.87 vs 0.29).
- Decode at 2,048 context never becomes compute-bound: the per-sequence KV read grows with
  the batch, so intensity tops out near 49 FLOP/byte at the 238-sequence memory cap, against a
  ridge of 295. Little's law with prefill stealing decode time has no fixed point above 23 req/s.
- The simulated M/D/1 means track Pollaczek–Khinchine within 1% up to ρ = 0.8; at ρ = 0.95 the
  20,000-request run under-reads the theory (94 vs 105 ms), as a finite run near saturation does.
- Pins checked with `git ls-remote --tags`: v2.14.1, 1.9.1 and v3.4.2 are still the newest
  stable releases; no pin moved.
- The bias baseline μ + b_u + b_i is worse than the global mean on the held-out cells: offsets
  cannot see interaction. The page says so.
- ALS's objective falls every sweep, but RMSE on observed cells can tick up, because ALS
  minimizes the penalized loss. The test checks the objective.

Gaps:

- References cited from memory (arxiv unreachable): GroupLens 1994, Sarwar 2001, Koren–Bell–
  Volinsky 2009, Hu–Koren–Volinsky 2008 (α = 40), Lee–Seung 2000. No pin implements ALS or
  implicit-feedback MF; those follow the papers.
- `two-tower-models` is named in plain text until it is ready.
- gradient-accumulation: `distributed-training` and `contrastive-learning` are named in plain
  text until ready. Goyal 2017, McCandlish 2018, Li 2020 (DDP), gradient cache (Gao 2021) cited
  from memory. DDP's `bucket_cap_mb` defaults to `None` meaning 25 MiB (doc 713-718), and the
  sync flag is read in `_pre_forward` (1745-1770), which is why forward must be inside `no_sync`.
- latency-and-throughput: `speculative-decoding` and `profiling` are named in plain text until
  ready. Little 1961, Williams–Waterman–Patterson 2009, Dean–Barroso 2013, Pope 2023, Kwon 2023,
  Sarathi-Serve 2024 cited from memory. The hardware is round numbers, not a vendor spec sheet;
  the numbers are roofline lower bounds, not measurements.

## Queue

1. `tensors-and-shapes` ✓
2. `vectors-and-dot-products` ✓
3. `matrix-multiplication` ✓
4. `derivatives-and-gradients` ✓
5. `chain-rule` ✓
6. `probability-and-distributions` ✓
7. `expectation-and-variance` ✓
8. `entropy-and-kl` ✓
9. `loss-functions` ✓
10. `linear-regression` ✓
11. `logistic-regression` ✓
12. `neurons-and-layers` ✓
13. `backpropagation` ✓
14. `optimizers` ✓
15. `embeddings` ✓
16. `attention` ✓
17. `layernorm-and-residuals` ✓
18. `transformer` ✓
19. `training-loop` ✓
20. `decoder-only-llm` ✓
21. `decoding` ✓
22. `kv-cache` ✓
23. `learning-paradigms` ✓
24. `generalization` ✓
25. `data-splits` ✓
26. `preprocessing` ✓
27. `data-leakage` ✓
28. `classification-metrics` ✓
29. `cross-validation` ✓
30. `decision-trees` ✓
31. `gradient-boosting` ✓
32. `overfitting` ✓
33. `bias-variance` ✓
34. `regularization` ✓
35. `activation-functions` ✓
36. `linear-algebra-toolkit` ✓
37. `missing-data` ✓
38. `computation-graphs` ✓
39. `cnns` ✓
40. `autoregressive-models` ✓
41. `tokenization` ✓
42. `nearest-neighbors` ✓
43. `similarity-search` ✓
44. `gpu-execution` ✓
45. `mixed-precision` ✓
46. `quantization` ✓
47. `reinforcement-learning` ✓
48. `bayes-rule` ✓
49. `class-imbalance` ✓
50. `random-forests` ✓
51. `initialization` ✓
52. `rnns-and-lstms` ✓
53. `autoencoders` ✓
54. `variational-autoencoders` ✓
55. `positional-encoding` ✓
56. `clustering` ✓
57. `vector-indexes` ✓
58. `distillation` ✓
59. `time-series` ✓
60. `regression-metrics` ✓
61. `support-vector-machines` ✓
62. `learning-rate-schedules` ✓
63. `gans` ✓
64. `encoder-only` ✓
65. `learning-to-rank` ✓
66. `data-loading-and-batching` ✓
67. `model-serving` ✓
68. `causal-inference` ✓
69. `calibration` ✓
70. `graph-neural-networks` ✓
71. `diffusion-models` ✓
72. `pretraining` ✓
73. `collaborative-filtering` ✓
74. `gradient-accumulation` ✓
75. `latency-and-throughput` ✓
76. `online-learning` ← next
77. `uncertainty`
78. `vision-transformer`
79. `diffusion-unet`
80. `fine-tuning`
81. `two-tower-models`
82. `distributed-training`
83. `monitoring-and-drift`
84. `multimodal-models`
85. `pca`
86. `mixture-of-experts`
87. `flow-matching`
88. `preference-optimization`
89. `retrieval-augmented-generation`
90. `checkpointing`
91. `reproducibility`
92. `state-space-models`
93. `profiling`

Build three pages per run, top to bottom, pushing each as it is finished. Once the queue is empty, the Routine runs maintenance
only: for each pin it checks for a newer stable release (never an rc, beta or dev tag). When one
exists, it diffs every file the ready pages link to between the pin and that tag, updates the
affected line ranges and claims, and moves the pin.
