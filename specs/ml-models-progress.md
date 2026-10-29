# rayaq.ca/ml-models — build progress

This is the running log for the daily ml-models Routine. Read it first and update it last.
The contract is `specs/ml-models.md` (spec v2, read-only without the owner's say-so). This file
records where the build actually stands.

**Last updated:** 2026-10-29 (third weekly audit). Spec v2 widens the section from model
architectures to all of machine learning: 12 areas, 96 pages, a seven-step learning path and a
fixed page format. Every queue item is ready (1-96; audits added `matrix-decompositions`,
`iterative-solvers` and `numerical-stability`).
Nothing is queued, so the next run is the next weekly audit (spec §8.1).

## Pins

| Key | Library | Tag | Commit | Committed | License (file) | Analyzed |
|---|---|---|---|---|---|---|
| `pytorch` | PyTorch | `v2.15.0` | `31a77fc9c0a7c6fff15a1ff58c743f53b1a9d457` | 2026-10-27 | BSD-3-Clause (`LICENSE`) | 2026-10-29 |
| `sklearn` | scikit-learn | `1.9.1` | `866c0f51e7560ef0303cbcc5f159df5382ea9e3f` | 2026-09-10 | BSD-3-Clause (`COPYING`) | 2026-10-08 |
| `xgboost` | XGBoost | `v3.4.2` | `fdf0888bedddbd444d72994d845c59b3ca182c5b` | 2026-09-15 | Apache-2.0 (`LICENSE`) | 2026-10-08 |

The pins live in `ml_models_docs.PINS`. Each tag was the latest stable release on the analysis
date. PyTorch moved from `v2.14.1` to `v2.15.0` in the 2026-10-29 audit (`361aea4`). Every `pin:path` source in the spec's
page tables was checked to exist at its pin with `git cat-file -e`.

To verify line ranges, clone each pin shallow and sparse at its tag, in a scratch directory:

```bash
git clone --depth 1 --branch v2.15.0 --filter=blob:none --sparse https://github.com/pytorch/pytorch pt
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

No audit so far (2026-10-15, 2026-10-22, 2026-10-29) had a tool to change a trigger's schedule, so
the trigger still fires every 5 hours. Until the owner switches it to weekly, a run that finds the last audit row less than
seven days old should record nothing and stop.

## §9 acceptance criteria

- [x] The index shows the framing, the learning path, the map, the vocabulary, the pins and
      every page grouped by area with its level (tested).
- [x] Every §5 page is ready and meets its "Must cover" column and §6 (96 of 96 ready, all
      in the §6 format).
- [x] Every link into a pinned repository uses that pin's commit (tested).
- [x] §7.5 tests exist and pass, including the §6 section order for every ready page.
- [x] No ML package in either requirements file (tested). There is no offline data yet.
- [x] Mobile at 390px: no horizontal page scroll on `/`, `/ml-models` or any ready page
      (`check_mobile.js` in headless Chromium, every run).
- [x] The Routine has run at least once in maintenance mode (the 2026-10-15 audit).

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

### PyTorch v2.14.1 (recheck at v2.15.0 before linking)

Ranges already cited by built pages live in their templates (and in `git log -p` on this
file); this list keeps ranges checked but not yet linked, for audits and new §5 rows.

- `torch/nn/utils/clip_grad.py`: `clip_grad_norm_` starts at 185.
- `torch/nn/attention/bias.py`: `CausalBias` 86-306, `causal_upper_left`/`causal_lower_right`
  308-376.
- `torch/nn/attention/flex_attention.py`: `BlockMask` 855-1694, `create_block_mask` 1967-2088,
  `flex_attention` starts at 2365.
- `torch/linalg/__init__.py`: `inv` 214-292, `vector_norm` 1491-1568; `matrix_norm` starts at 1570.
- `torch/_torch_docs.py` (from `add_docstr(` to `)`): `matmul` 7908-7990, `mm` 7831-7887,
  `bmm` 1706-1762, `addmm` 592-665, `baddbmm` 1512-1581.
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
- Every index map box links to its page.
- The index map still covers only the architecture area. Widen it to all 12 areas once a
  page in each of the first few areas is ready.
- `transformer` uses the v1 section layout and is exempt from the §6 order test until its
  retrofit (queue item 18).

## First to forty-third runs (2026-10-08 to 2026-10-15) — condensed

Runs 1-3 wrote the spec (v1, then v2), the registry, `LEARNING_PATH`, the §6 and queue tests,
`check_mobile.js` and the Routine. Every run since adds, per page, a tested-helpers commit, a
page commit (page, `ready`, queue ✓) and a `docs:` commit, building queue items 1-84 in order
(three per run from run 28 to run 42, which built preference-optimization,
retrieval-augmented-generation and checkpointing; run 43 built reproducibility,
state-space-models and profiling and emptied the queue). `6f0803f` fixed 13 templates that read a missing `pins.X.version` key.
Pins never moved. The ranges each page links live in its template (grep `src(`, `skl(`,
`xgb(`); `git log -p` on this file has every old commit table, range list and run detail.

Findings worth keeping:

- sklearn's `Entropy` criterion is in bits; XGBoost's `loss_chg` has no ½. `AdamW` is `Adam`
  with `decoupled_weight_decay=True`. `nn.Linear` uses `kaiming_uniform_(a=math.sqrt(5))`,
  a bound of exactly 1/√fan_in. `_SigmoidCalibration` predicts `expit(-(a_*T + b_))`.
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
- Chinchilla's Approach 3 constants give about 32B params / 3.0T tokens at its budget, not
  70B; the 20-tokens rule recovers 70B / 1.4T. scikit-learn's `NMF` treats blanks as zeros.
  Decode at 2,048 context tops out near 49 FLOP/byte against a ridge of 295. ViT's counter
  matches torchvision exactly; split conformal coverage is marginal, not per-group.
- Counters that match published totals: SD v1 UNet 859,520,964, DiT-XL/2 674,834,720,
  Llama 2 7B 6,738,415,616, PEFT's LoRA r=8 on q,v 4,194,304.
- PCA's float `n_components` keeps the smallest k whose cumulative ratio is strictly above t
  (`searchsorted(..., side="right") + 1`). Mixtral 8x7B counts 46.70B total, 12.88B active.
  On ±1 data one flow-matching Euler step sends every sample to the data mean.
- Tabular DPO lands on the closed-form optimum π_ref·exp(r/β)/Z to 1.5e-6; on a unanimous
  pair DPO's margin keeps growing while IPO settles at 1/(2τ). A full checkpoint resume
  replays steps bit for bit, and forgetting any one piece (scheduler, optimizer, RNG, data
  position) gives a different run, often with a lower loss. Young's T* = √(2CM).
- DataLoader workers reseed `random`, torch and NumPy at the pin; the trap is a generator
  built in `Dataset.__init__`. A HiPPO-LegS SSM gives the same outputs as a recurrence and
  a convolution to 1e-16. A six-kernel step reads 7.0 ms synced, 0.03 ms unsynced.
- The CLIP logit gradient is (P_row + P_colᵀ − 2I)/(2N). `cross_entropy` ends at 3569 and
  `F.scaled_dot_product_attention` is 6367-6540 at the PyTorch pin.

Open gaps from these runs:

- Every paper reference so far was cited from memory (arxiv.org is unreachable through the
  proxy); pre-arXiv papers and the GPT-2 report have no link. Each page's references list
  is the full set to re-check once arxiv is reachable.
- Run 42's invented examples are labelled on their pages: the preference counts and "true"
  reward, the RAG manual and its trigram/soft-match stand-ins for trained encoders, and the
  checkpointing failure rate, save times and 7B size. KTO is prose only (exact loss not
  checked); selective activation checkpointing and stateful data loaders are not covered.
- Ideas no pin implements follow their papers: WordPiece training, BM25, GPTQ, LLM.int8(), RL,
  IVF/PQ/HNSW, GANs, R1, FID, ARIMA/STL/MASE, sequence packing, serving systems, ECE,
  propensity weighting, DiD, uplift, GNNs, diffusion samplers, MinHash, scaling-law fits, ALS,
  gradient caching, bandits, drift detectors and conformal prediction.
- Invented, labelled examples: `gpu-execution`'s GPU, `model-serving`'s model, the
  data-loading worker timeline and the latency page's round-number hardware (roofline bounds,
  not measurements). `mixed-precision`'s fp8 recipes, the SwiGLU "2/3 hidden size" remark,
  the H100 peak and Llama 3 8B's 15T tokens are general knowledge; Hinton–Vinyals–Dean's T²
  remark was confirmed only through secondary quotes.
- The end lines of the HistGradientBoosting regressor `__init__`, `_incremental_fit_estimator`
  and `Lasso` were inferred.
- Topics named in plain text with no page: `contrastive-learning` and `speculative-decoding`
  (run 37 pages); candidates for §5 rows in an audit.
- No pin implements a UNet, LoRA/PEFT, NF4, an ANN index or logQ correction; the two-tower
  serving numbers are an invented, labelled configuration.
- PSI's 0.1/0.25 thresholds are an industry convention; Whisper, EnCodec, Flamingo and LLaVA
  details follow the papers from memory, and the fusion model is invented and labelled.
- UMAP is in no pin. Since run 41 the PyTorch wheel download is blocked, so page snippets
  are checked against the stdlib helpers (and NumPy mirrors), not run under torch.
- Page commits exceed 400 lines because each template is one file.

## Weekly audits

| Date | Checked | Found | Added |
|---|---|---|---|
| 2026-10-29 | Pins (`git ls-remote --tags`); Hugging Face model cards and reports for recent open-weight releases; the foundations area for floating point and conditioning | PyTorch `v2.15.0` is final (2026-10-27); scikit-learn 1.9.1 and XGBoost v3.4.2 are still the latest stable. No open-weight release qualified: Reflection Beam 1.0's report is still "coming", Muse Spark Open has only an evaluation-methodology note, Mistral Large 4 weights are due 2026-10-31, MiniMax M3.1-Flash could not be verified. Foundations had no page on rounding error, conditioning or stable rewrites | `361aea4` the PyTorch pin to v2.15.0 (every linked range rechecked); `bfc791c` the `numerical-stability` page (§5 row, registry, queue 96) |
| 2026-10-22 | Pins (`git ls-remote --tags`); Hugging Face model cards and reports for recent open-weight releases; the foundations area for numerical linear algebra beyond factorizations | No pin moved (PyTorch v2.15.0 is still rc7). DeepSeek-V4.1-Flash has weights and a report (cross-layer KV sharing, FP4 KV cache); Muse Spark Open, Reflection Beam and Mistral Large 4 have no report or open weights yet, so they were skipped. Foundations had no iterative solvers (CG, Krylov, preconditioning) | `15c05d9` a cross-layer sharing and FP4 section on `kv-cache` plus its `UPCOMING_MODELS` entry; `ab96a0f` the `iterative-solvers` page (§5 row, registry, queue 95) |
| 2026-10-15 | Pins (`git ls-remote --tags`); the Kimi K2, DeepSeek-V3.2-Exp and MiMo-V2-Flash reports; `torch/optim/_muon.py`; the foundations area against `torch.linalg` | No pin moved (PyTorch v2.15.0 is still rc only). Muon and QK-Clip had no coverage; foundations stopped at eigen/SVD with no LU, QR, Cholesky, least squares or matrix norms | `063d6ab` three `UPCOMING_MODELS` entries; `045a59f` a Muon/QK-Clip section on `optimizers`; `736023a` the `matrix-decompositions` page (§5 row, registry, queue 94) |

Notes from the 2026-10-29 audit:

- The v2.15.0 diff over the linked files moved line ranges only, plus new APIs not yet
  described: FSDP2 `MixedPrecisionPolicy.param_dtype_override_fn` and
  `set_manual_backward_finalization`, DDP `lazy_bucket_allocation`, `aoti_load_package`
  `num_runners`/`use_stream_affinity`, profiler `export_chrome_trace`
  `cuda_graph_annotations`/`graph_lanes`, more MPS deterministic-algorithm entries and an
  MI300 TF32 note. Candidates for a later audit.
- Linked at the pins for `numerical-stability`: PyTorch `_refs/__init__.py` `log_softmax`
  909-919, `logsumexp` 922-942, `logaddexp` 1711-1737; `_decomp/decompositions.py`
  `_softmax` 1302-1321, `_log_softmax` 1345-1365, `log_sigmoid_forward` 3591-3602,
  `binary_cross_entropy_with_logits` 5231-5248; `SumKernel.cpp` `multi_row_sum` 312-409,
  `cascade_sum` 568-645; `testing/_comparison.py` `_DTYPE_PRECISIONS` 96-104. scikit-learn
  `_loss/_loss.pyx.tp` `log1pexp` 250-267, `sum_exp_minus_max` 269-303;
  `utils/extmath.py` `_safe_accumulator_op` 1063-1115, `_incremental_mean_and_var`
  1118-1264, `stable_cumsum` 1289-1334 (deprecated in 1.8).
- research.meta.ai was unreachable. Recheck Mistral Large 4 next audit.
- Gaps: Goldberg, Higham, Trefethen–Bau, Kahan, Welford, Chan–Golub–LeVeque, Mächler,
  Blanchard–Higham–Higham and IEEE 754 are cited from memory without links; the PyTorch
  snippet was not run under real PyTorch.

Notes from the 2026-10-22 audit (condensed):

- WebFetch could not reach most domains, so reports were read through Hugging Face. The
  DeepSeek-V4.1-Flash report link is pinned to HF commit `314113f8`, not `blob/main`.
- Linked at the pins: scikit-learn `utils/optimize.py` `_cg` 173-259 and `_newton_cg`
  262-403, `linear_model/_ridge.py` `_solve_sparse_cg` 86-156 and `_solve_lsqr` 159-212;
  PyTorch `_lobpcg.py` `lobpcg` 343-580 and `_lobpcg` 583-697, `autograd/functional.py`
  `vhp` 997-1093 and `hvp` 1098-1210.
- Gaps: Hestenes–Stiefel, Shewchuk, Saad, Paige–Saunders, Knyazev, Pearlmutter, Martens and
  GPyTorch are cited from memory without links (the GPyTorch arXiv id could not be verified).
  The FP4 layout (E2M1 values, one E4M3 scale per 16) follows the DeepSeek report.

Notes from the 2026-10-15 audit (condensed):

- arxiv.org is unreachable, so model reports were read as PDFs in their GitHub repositories.
- Muon at the pin: `_zeropower_via_newtonschulz` 31-70, `_adjust_lr` 73-86, `Muon` 89-205,
  `_single_tensor_muon` 318-351.
- `torch/linalg/__init__.py` docstring ranges at v2.14.1: `cholesky` 71-146, `cholesky_ex`
  148-212, `eigh` 642-763, `lstsq` 1078-1200, `norm` 1353-1489, `matrix_norm` 1570-1644, `svd`
  1734-1886, `cond` 1938-2054, `solve` 2260-2363, `solve_triangular` 2365-2443, `lu_factor`
  2445-2529, `lu` 2641-2729, `qr` 2865-2966; `nn/init.py` `orthogonal_` 672-720.
- On the Läuchli matrix the normal equations lose accuracy as κ² (error 1.1e-3 at ε = 1e-7)
  and fail at ε = 1e-8, where 1 + ε² rounds to 1; Householder QR stays at or below 2.5e-16.
  Classical Gram–Schmidt on the 6 × 6 Hilbert matrix loses orthogonality to 7.1e-5, modified
  to 2.7e-10.
- Gaps: the Muon post, Moonshot's scaling paper, *Deriving Muon*, Trefethen–Bau, Golub–Van
  Loan, Higham, Läuchli and Rasmussen–Williams are cited from memory. Neither the Muon nor the
  decompositions snippet was run under real PyTorch (the wheel download is still blocked).

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
76. `online-learning` ✓
77. `uncertainty` ✓
78. `vision-transformer` ✓
79. `diffusion-unet` ✓
80. `fine-tuning` ✓
81. `two-tower-models` ✓
82. `distributed-training` ✓
83. `monitoring-and-drift` ✓
84. `multimodal-models` ✓
85. `pca` ✓
86. `mixture-of-experts` ✓
87. `flow-matching` ✓
88. `preference-optimization` ✓
89. `retrieval-augmented-generation` ✓
90. `checkpointing` ✓
91. `reproducibility` ✓
92. `state-space-models` ✓
93. `profiling` ✓
94. `matrix-decompositions` ✓
95. `iterative-solvers` ✓
96. `numerical-stability` ✓

Nothing is queued. Each audit appends at most two pages here. From now on the Routine runs the weekly audit (spec §8.1): for each pin it checks for a newer stable release (never an rc, beta or dev tag). When one
exists, it diffs every file the ready pages link to between the pin and that tag, updates the
affected line ranges and claims, and moves the pin.
