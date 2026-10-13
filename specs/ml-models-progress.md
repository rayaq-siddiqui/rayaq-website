# rayaq.ca/ml-models — build progress

This is the running log for the daily ml-models Routine. Read it first and update it last.
The contract is `specs/ml-models.md` (spec v2, read-only without the owner's say-so). This file
records where the build actually stands.

**Last updated:** 2026-10-12 (thirty-third run). Spec v2 widens the section from model
architectures to all of machine learning: 12 areas, 93 pages, a seven-step learning path and a
fixed page format. Ready pages: queue items 1-63, the last being `gans`. The next page is
`encoder-only` (queue item 64).

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
- [ ] Every §5 page is ready and meets its "Must cover" column and §6 (60 of 93 ready, all
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

## First to thirty-second runs (2026-10-08 to 2026-10-12) — condensed

Runs 1-3 wrote the spec (v1, then v2), the registry, `LEARNING_PATH`, the §6 and queue tests,
`check_mobile.js` and the Routine. Every run since adds, per page, a tested-helpers commit, a
page commit (page, `ready`, queue ✓) and usually a `docs:` commit; items 1-51 were built in
queue order (run 28: quantization, reinforcement-learning, bayes-rule; run 29:
class-imbalance, random-forests, initialization; run 30: rnns-and-lstms, autoencoders,
variational-autoencoders; run 31: positional-encoding, clustering, vector-indexes; run 32:
distillation, time-series, regression-metrics). `6f0803f` fixed 13 templates that read a
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
- The vector-index example is `lru_cache`d (about 1.7 s); PQ re-ranking only helps when R > k.
- `.jj-diagram svg text { fill: var(--jj-text) }` beats an SVG `fill=` attribute, so coloured
  diagram text must use `style="fill: ..."`.
- Jinja: a context dict key named `values`, `items` or `keys` resolves to the dict method;
  macros return Markup, so do arithmetic before calling them, never on their output.
- Time series: trend + Fourier wins (MASE 0.73); shuffled K-fold flatters a 1-NN-in-time model
  (3.53 vs 8.21). Regression metrics: the spiky model wins MAE and loses RMSE; MAPE's best
  constant sits below the median.

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
- No pin implements IVF, PQ or HNSW; those follow the papers. `pca` appears as plain text on
  `clustering` until it is ready.
- Page commits exceed 400 lines because each template is one file.
- Run 32: Hinton–Vinyals–Dean's T² remark was confirmed only through secondary quotes;
  Gneiting 2011 is cited only for consistent scoring functions. No pin implements ARIMA, STL
  or MASE; those follow the papers and FPP3.

## Thirty-third run (2026-10-12) — support-vector-machines, learning-rate-schedules, gans

| Commit | What |
|---|---|
| `4038256` `ml-models: add tested support vector machine helpers` | A deterministic SMO solver (maximal-violating-pair working set, as in libsvm), linear/RBF/polynomial kernels, hinge loss, `gamma='scale'`, hard and soft margins, an outlier at three C, a 1-D ring, a scaling demo, with tests |
| `d4603af` `ml-models: build the support vector machines page` | The page, `ready`, queue ✓ |
| `7696dbf` `ml-models: add tested learning rate schedule helpers` | Closed-form step/exponential/cosine/warmup/one-cycle schedules, a recursive `get_lr` simulator the tests hold equal to them, noisy-SGD expected loss on a quadratic, GD at four rates, an LR range test, Adam's first steps |
| `ec993db` `ml-models: build the learning rate schedules page` | The page, `ready`, queue ✓ |
| `c289d64` `ml-models: add gan worked-example helpers` | Optimal discriminator and value on an eight-bin two-mode distribution, JS, both KLs and W1 for four generators, disjoint supports, minimax vs non-saturating gradients, Dirac-GAN runs, the 2×2 Fréchet distance and its sample-size bias, ConvTranspose2d sizes, with tests |
| `ae3cbd5` `ml-models: add generative adversarial networks page` | The page, `ready`, queue ✓ |

Ranges verified this run are linked from the three templates: scikit-learn `svm/_base.py`,
`svm/_classes.py`, `svm/src/libsvm/svm.cpp`, `metrics/pairwise.py` kernels and the SGD hinge
loss; PyTorch `torch/optim/lr_scheduler.py` (every scheduler in the component table);
`BCELoss` 633-716, `BCEWithLogitsLoss` 719-844, `autograd.grad` 434-621, `ConvTranspose2d`
1012-1207, `LeakyReLU` 875-930, `Tanh` 407-433, `init.normal_` 274-298, `spectral_norm`
535-636 and `_SpectralNorm` 403-532.

Findings worth keeping:

- The SVM helpers' coefficients, intercepts and support sets match scikit-learn 1.9.1 `SVC`
  (scratch venv); the tests pin those values and check primal = dual.
- Learning rates: cosine beats step decay on the noisy quadratic; the range test's best rate is
  1.0 on curvatures 0.5/2/8 and blows up three steps later; Adam's first steps move by
  ≈ lr whatever the gradient scale, which is the case for warmup.
- Dirac-GAN at step 0.1 from (1, 1): minimax simultaneous GD spirals out (radius 2.76 at
  step 1000); the non-saturating loss shrinks, then orbits at ≈ 0.44 (checked to 10,000
  steps); R1 with γ = 1 converges. A first WGAN-GP simulation with a linear critic stalled at
  a spurious point created by the kink of |ψ| at 0, so the page states WGAN-GP's
  non-convergence only as Mescheder et al.'s result.
- FID helper cross-checked against `scipy.linalg.sqrtm` in the scratch venv.
- `rendered_pages` caches each page for the life of the process: restart the app before
  re-screenshotting an edited template.
- Pins checked with `git ls-remote --tags`: v2.14.1, 1.9.1 and v3.4.2 are still the newest
  stable releases; no pin moved.

Gaps:

- References cited from memory (arxiv unreachable): Platt (SMO), Cortes–Vapnik, Fan–Chen–Lin,
  Smith, SGDR, Goyal et al., Smith–Topin, RAdam, Xiong et al., Goodfellow et al., DCGAN,
  Arjovsky–Bottou (including the KL(p_g‖p_data) − 2·JS gradient result), WGAN, WGAN-GP,
  Heusel et al., Miyato et al., Mescheder et al. and Chong–Forsyth.
- No torch cross-check was run for the schedulers; the closed forms are held equal to a
  simulator of the pinned recursions instead.
- No pin implements a GAN, a Wasserstein critic, R1 or FID; those follow the papers. The
  "diffusion models largely replaced GANs" remark is general knowledge; `diffusion-models` is
  not linked until it is ready.

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
67. `model-serving` ← next
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
