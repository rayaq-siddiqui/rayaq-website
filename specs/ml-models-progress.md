# rayaq.ca/ml-models — build progress

This is the running log for the daily ml-models Routine. Read it first and update it last.
The contract is `specs/ml-models.md` (spec v2, read-only without the owner's say-so). This file
records where the build actually stands.

**Last updated:** 2026-10-12 (thirty-first run). Spec v2 widens the section from model
architectures to all of machine learning: 12 areas, 93 pages, a seven-step learning path and a
fixed page format. Ready pages: queue items 1-57, the last being `vector-indexes`. The
next page is `distillation` (queue item 58).

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
- [ ] Every §5 page is ready and meets its "Must cover" column and §6 (54 of 93 ready, all
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

- `torch/optim/lr_scheduler.py`: `CosineAnnealingLR` 1338-1475. Start lines only: `LambdaLR`
  343, `LinearLR` 877, `SequentialLR` 1082, `OneCycleLR` 2285.
- `torch/nn/utils/clip_grad.py`: `clip_grad_norm_` starts at 185.
- `torch/nn/attention/bias.py`: `CausalBias` 86-306, `causal_upper_left`/`causal_lower_right`
  308-376.
- `torch/nn/attention/flex_attention.py`: `BlockMask` 855-1694, `create_block_mask` 1967-2088,
  `flex_attention` starts at 2365.
- `conv.py`: `Conv1d` 225-385 (`ConvTranspose2d` is cited in `autoencoders`).
- `torch/linalg/__init__.py`: `inv` 214-292, `vector_norm` 1491-1568; `matrix_norm` starts at 1570.
- `torch/_torch_docs.py` (from `add_docstr(` to `)`): `matmul` 7908-7990, `mm` 7831-7887,
  `bmm` 1706-1762, `addmm` 592-665, `baddbmm` 1512-1581.
- `torch/random.py`: `manual_seed` 49-59; `get_rng_state` 39-46; `set_rng_state` 27-36.
- `torch/optim/optimizer.py`: `Optimizer` starts at 358; `state_dict` 700-791, `zero_grad`
  1048-1110.
- `torch/nn/modules/module.py`: `class Module` 407; `register_buffer` 528.
- Mixed precision, quantization, GPU execution and initialization: ranges live in their
  templates.
- Similarity search: `distance.py` `PairwiseDistance` 10-61, `CosineSimilarity` 64-100;
  `torch/nn/functional.py` `pairwise_distance` 5858-5865, `cosine_similarity` 5895-5924,
  `normalize` 6096-6130; `torch/functional.py` `cdist` 1483-1541.

### scikit-learn 1.9.1 (start lines; check the end before linking a range)

Paths are under `sklearn/`.

- Linear models (`linear_model/`), used by the regression, classifier and regularization pages:
  ranges live in those templates.
- `tree/_classes.py`: `DecisionTreeClassifier` 699, `DecisionTreeRegressor` 1097.
- `ensemble/_forest.py`, `_bagging.py`, `inspection/_permutation_importance.py`,
  `tree/_splitter.pyx`: ranges live in the `random-forests` template.
- `ensemble/_gb.py`: `GradientBoostingClassifier` 1145.
- `ensemble/_hist_gradient_boosting/gradient_boosting.py`: `HistGradientBoostingClassifier` 1762.
- `svm/_classes.py`: `SVC` 623.
- `neighbors/`: all ranges live in the `nearest-neighbors` template.
- Similarity search: `metrics/pairwise.py` `euclidean_distances` 268-373,
  `_euclidean_distances` 376-427, `cosine_similarity` 1703-1758; `preprocessing/_data.py`
  `normalize` 1978-2089; `feature_extraction/text.py` `TfidfTransformer` 1506, idf in `fit`
  1675-1695.
- `cluster/_kmeans.py`: `_kmeans_plusplus` 180-283, `_labels_inertia` 761-832,
  `KMeans.predict` 1071-1104, `KMeans` 1191-1561 (`fit` 1432-1561), `MiniBatchKMeans`
  1680-2320 (end of file). DBSCAN, GaussianMixture and metrics ranges live in the
  `clustering` template.
- `neighbors/_unsupervised.py` `NearestNeighbors` 10-179; `neighbors/_base.py` `kneighbors`
  756-959.
- `decomposition/_pca.py`: `PCA` 113.
- `model_selection/_split.py`: `KFold` 437, `GroupKFold` 533, `StratifiedKFold` 687,
  `TimeSeriesSplit` 1116, `train_test_split` 2797.
- `model_selection/_validation.py`: `cross_validate` 101, `cross_val_score` 512,
  `learning_curve` 1776, `validation_curve` 2283.
- `preprocessing/_data.py`: `StandardScaler` 742 (verified range 742-1189), `MinMaxScaler` 305, `RobustScaler` 1552.
- `preprocessing/_encoders.py`: `OneHotEncoder` 474, `OrdinalEncoder` 1263.
- `impute/`: ranges live in the `missing-data` template.
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

## First to thirtieth runs (2026-10-08 to 2026-10-12) — condensed

Runs 1-3 wrote the spec (v1, then v2), the registry, `LEARNING_PATH`, the §6 and queue tests,
`check_mobile.js` and the Routine. Every run since adds, per page, a tested-helpers commit, a
page commit (page, `ready`, queue ✓) and usually a `docs:` commit; items 1-51 were built in
queue order (run 28: quantization, reinforcement-learning, bayes-rule; run 29:
class-imbalance, random-forests, initialization; run 30: rnns-and-lstms, autoencoders,
variational-autoencoders). `6f0803f` fixed 13 templates that read a
missing `pins.X.version` key. Pins never moved. The ranges each page links live in its template
(grep `src(`, `skl(`, `xgb(`); `git log -p` on this file has every old commit table and range list.

Findings worth keeping (details in each page and in `git log -p` on this file):

- sklearn's `Entropy` criterion is in bits; XGBoost's `loss_chg` has no ½. `AdamW` is `Adam`
  with `decoupled_weight_decay=True`. `nn.Linear` uses `kaiming_uniform_(a=math.sqrt(5))`,
  a bound of exactly 1/√fan_in.
- Cross-checks ran in scratch venvs, never in requirements: scikit-learn 1.9.1, torch 2.14.1,
  XGBoost 3.2.0 (3.4.2 is not on the mirror; the formulas used are unchanged).
- Use the one-sided Jacobi SVD (eigenvalues of AᵀA squared the condition number).
- A linear autoencoder's encoder·decoder product matches PCA's projection uuᵀ; only
  `Normal.rsample` carries gradients (`sample` runs under `no_grad`).
- `.jj-diagram svg text { fill: var(--jj-text) }` beats an SVG `fill=` attribute, so coloured
  diagram text must use `style="fill: ..."`.

Open gaps from these runs:

- Every paper reference so far was cited from memory (arxiv.org is unreachable through the
  proxy); pre-arXiv papers and the GPT-2 report have no link. Each page's references list
  is the full set to re-check once arxiv is reachable.
- No pin implements WordPiece training, BM25, GPTQ, LLM.int8() or any RL algorithm; those pages
  follow the papers. `gpu-execution`'s hardware remarks (on an invented, labelled example GPU),
  `mixed-precision`'s fp8 recipes and the SwiGLU "2/3 hidden size" remark are general knowledge.
- The end lines of the HistGradientBoosting regressor `__init__`, `_incremental_fit_estimator`
  and `Lasso` were inferred.
- `kv-cache` (quantization), `reinforcement-learning` (preference optimization) and
  `class-imbalance` (calibration) name those pages in plain text until they are ready.
- Page commits exceed 400 lines because each template is one file.

## Thirty-first run (2026-10-12) — positional-encoding, clustering, vector-indexes

| Commit | What |
|---|---|
| `31314b5` `ml-models: add tested positional encoding helpers` | Sinusoidal encoding and its shift rotation, RoPE pair by pair with offset-only scores, ALiBi slopes and biases, learned-table size, with tests |
| `c42adca` `ml-models: add the positional encoding page` | The page, the transformer link, `ready`, queue ✓ |
| `e1c1ebe` `ml-models: add tested clustering helpers` | Lloyd's algorithm, k-means++, silhouette, DBSCAN as sklearn labels it, 2-D Gaussian mixture EM with BIC, adjusted Rand index, with tests |
| `ba25dc9` `ml-models: add the clustering page` | The page, `ln_n` for the BIC text, `ready`, queue ✓ |
| `9967d96` `ml-models: add tested vector index helpers` | IVF, PQ with ADC and re-ranking, HNSW with the selection heuristic, recall@k and a memory model on 800 clustered 16-d vectors, with tests |
| `902218c` `ml-models: add the vector indexes page` | The page, clustering links to it, `ready`, queue ✓ |

Findings worth keeping:

- The vector-index example is cached with `lru_cache` (about 1.7 s); the O(n·k²) k-means++
  seeding was rewritten incrementally and distances use `math.dist`.
- PQ re-ranking only helps when R > k: re-ranking the top 10 for k = 10 changes nothing.
- On the example, HNSW at ef = 20 reaches recall 0.98 at about the same cost as IVF at
  nprobe = 4 (0.915); probing all IVF lists costs more than brute force.
- Pins checked with `git ls-remote --tags`: v2.14.1, 1.9.1 and v3.4.2 are still the newest
  stable releases; no pin moved.

Gaps:

- References on all three pages were cited from memory (arxiv still unreachable): Vaswani,
  Su (RoPE), Press (ALiBi), Lloyd, Arthur–Vassilvitskii, Ester (DBSCAN), Jégou (PQ),
  Malkov–Yashunin (HNSW), Johnson (Faiss GPU), DiskANN and ANN-Benchmarks.
- No pin implements IVF, PQ or HNSW; those follow the papers. FAISS and hnswlib are named in
  prose only. `pca` appears as plain text on `clustering` until it is ready.
- The page commits exceed 400 lines.

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
59. `time-series` ← next
60. `regression-metrics`
61. `support-vector-machines`
62. `learning-rate-schedules`
63. `gans`
64. `encoder-only`
65. `learning-to-rank`
66. `data-loading-and-batching`
67. `model-serving`
68. `causal-inference`
69. `calibration`
70. `graph-neural-networks`
71. `diffusion-models`
72. `pretraining`
73. `collaborative-filtering`
74. `gradient-accumulation`
75. `latency-and-throughput`
76. `online-learning`
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
