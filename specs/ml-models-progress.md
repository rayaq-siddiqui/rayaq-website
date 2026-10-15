# rayaq.ca/ml-models — build progress

This is the running log for the daily ml-models Routine. Read it first and update it last.
The contract is `specs/ml-models.md` (spec v2, read-only without the owner's say-so). This file
records where the build actually stands.

**Last updated:** 2026-10-15 (forty-third run). Spec v2 widens the section from model
architectures to all of machine learning: 12 areas, 93 pages, a seven-step learning path and a
fixed page format. Every queue item is ready (1-93, the last being `profiling`). The queue
is empty, so the next run is the first weekly audit (spec §8.1).

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
- [x] Every §5 page is ready and meets its "Must cover" column and §6 (93 of 93 ready, all
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

## First to forty-second runs (2026-10-08 to 2026-10-14) — condensed

Runs 1-3 wrote the spec (v1, then v2), the registry, `LEARNING_PATH`, the §6 and queue tests,
`check_mobile.js` and the Routine. Every run since adds, per page, a tested-helpers commit, a
page commit (page, `ready`, queue ✓) and a `docs:` commit, building queue items 1-84 in order
(three per run from run 28 to run 42, which built preference-optimization,
retrieval-augmented-generation and checkpointing). `6f0803f` fixed 13 templates that read a missing `pins.X.version` key.
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

## Forty-third run (2026-10-15) — reproducibility, state-space-models, profiling

| Commit | What |
|---|---|
| `02bde76` `ml-models: add tested reproducibility helpers` | A port of DataLoader's `_generate_state` worker NumPy seed, copied versus reseeded worker generators, shared versus per-purpose derived seed streams, float32 sums in eight orders, a `check_random_state` stand-in with KFold-like folds, a data/code/environment manifest |
| `af0dbcf` `ml-models: add the reproducibility page` | The page, `ready`, queue ✓ |
| `4c55a5b` `docs: record the reproducibility page in ml-models progress` | The reproducibility record |
| `51756e2` `ml-models: add tested state-space-model helpers` | Scalar Euler/bilinear/ZOH discretization, HiPPO-LegS and its NPLR split, recurrent versus convolutional evaluation, a gated selective scan against a fixed step, a Hillis-Steele scan, state versus KV-cache costs |
| `8b41fbc` `ml-models: add the state-space-models page` | The page, `ready`, queue ✓; links the SSM mentions on `rnns-and-lstms` and `attention` |
| `ad9d04a` `docs: record the state-space-models page in ml-models progress` | The state-space-models record |
| `aeac839` `ml-models: add tested profiling helpers` | A port of `torch.profiler.schedule`, step timing with and without sync and warmup (on `async_timeline`), a `key_averages`-style self/total split, MFU versus HFU, data-loader wait fractions (on `loader_pipeline`), a training-step memory timeline |
| `81c854a` `ml-models: add the profiling page` | The page, `ready`, queue ✓ (queue empty); links the profiling mentions on `gpu-execution` and `latency-and-throughput` |
| (this commit) `docs: record the forty-third ml-models run` | Profiling record, pin check; condenses run 42 |

Findings worth keeping:

- At the pin, DataLoader workers already reseed Python `random`, torch and NumPy's global
  generator (`seed = base_seed + worker_id`, NumPy from `_generate_state`). The remaining trap
  is a generator object built in `Dataset.__init__`, copied unchanged into every worker; the
  page shows four identical crop sequences versus four distinct ones.
- The pure-Python `_generate_state` port matches `np.random.SeedSequence([wid, lo, hi,
  0]).generate_state(4)` word for word (checked once in a scratch venv with NumPy, not in the
  repo); the tests pin the words.
- 4096 float32 normals (seed 11) summed in eight orders give 7 distinct results spread over
  39 ULPs; pairwise is 1.7 ULPs from the exact sum, left to right 4.3.
- `use_deterministic_algorithms`'s docstring at the pin does not mention
  `CUBLAS_WORKSPACE_CONFIG`; the page attributes that setting to NVIDIA's cuBLAS docs. At
  scikit-learn 1.9.1, `KFold(shuffle=False, random_state=...)` raises a `ValueError`.
- Ranges checked at the pins: `random.py` (`set_rng_state` 27-36, `get_rng_state` 39-46,
  `manual_seed` 49-59, `_manual_seed_impl` 62-86, `initial_seed` 144-150, `fork_rng`
  156-239), `_utils/worker.py` (`get_worker_info` 99-129, `_generate_state` 192-241, seeding
  274-282), `dataloader.py` (`worker_init_fn` doc 188-190, `_base_seed` 690-694),
  `RandomSampler.__iter__` 160-166, `torch/__init__.py` (`use_deterministic_algorithms`
  1756-1903, `set_deterministic_debug_mode` 1921-1962), `backends/cudnn/__init__.py` (flag
  defaults 192-194, `CudnnModule` props 221-229), `docs/source/notes/randomness.md` (1-272;
  benchmarking 73-92, uninitialized memory 235-249, DataLoader 251-272); scikit-learn
  `check_random_state` 1455-1485, `KFold._iter_test_indices` 516-521, the `shuffle=False`
  check 364-371.
- State-space models: the HiPPO-LegS SSM (N = 4, Δ = 0.1, bilinear) gives the same eight
  outputs as a recurrence and as a causal convolution to 1.1e-16, and A + ppᵀ is −½I plus a
  skew-symmetric matrix. The selective scan tracks the last flagged value with error 0.040;
  the same SSM with a fixed Δ = 0.5 misses by 1.81. A 48-layer, width-2048 Mamba-shaped
  model carries 7,471,104 bytes of state at any context, against 384 MiB of KV cache at
  1,024 tokens and 192 GiB at 524,288.
- Ranges checked at PyTorch v2.14.1: `nn/modules/conv.py` (`Conv1d` 225-385,
  `_conv_forward` 366-382, `forward` 384-385), `functional.py` (`einsum` 175-382),
  `nn/functional.py` (`conv1d` docstring 53-99, `softplus` 2115-2127, `silu` 2429-2451),
  `_torch_docs.py` (`cumprod` 3521-3558, `cumsum` 3560-3590).
- Profiling: a six-kernel step synced reads 7.005 ms, unsynced 0.03 ms; the 8-iteration mean
  with two warmup costs is 117.6 ms, 17× the median. Twenty 2 µs kernels launched 5 µs apart
  keep the GPU 39% busy. The schedule port (skip_first 2, wait 1, warmup 1, active 2,
  repeat 2) saves at steps 5 and 9 and is idle after. With 120 ms loads and 40 ms steps,
  two workers wait a third of each step; three remove the stall. Adam state makes step 1's
  peak (5,650 MiB) exceed step 0's (4,000); a 2× batch peaks at 8,050. A 1.3B model on 8
  GPUs at 1,048,576 tokens per 2.6 s is 45.9% MFU (61.2% HFU with full recompute).
- Ranges checked at PyTorch v2.14.1 for profiling (all linked from the page):
  `profiler/profiler.py` (`export_chrome_trace` 469-523, `export_stacks` 545-554,
  `key_averages` 589-614, `export_memory_timeline` 692-742, `ProfilerAction` 745-759,
  `schedule` 768-827, `_default_schedule_fn` 830-835, `tensorboard_trace_handler` 838-871,
  `profile` 874-1323, `action_map` 1088-1198, `step` 1236-1323, `_transit_action`
  1344-1349), `autograd/profiler.py` (`record_function` 868-1001), `autograd/profiler_util.py`
  (FLOP formulas 44-107, `table` 242-286), `cuda/__init__.py` (`synchronize` 1271-1281),
  `cuda/memory.py` (`memory_stats` 242-350, `reset_peak_memory_stats` 381-397,
  `memory_allocated` 525-539, `max_memory_allocated` 542-560, `memory_reserved` 563-575,
  `max_memory_reserved` 578-593, `memory_summary` 652-778, `_record_memory_history` 897-995,
  `_dump_snapshot` 1149-1168), `cuda/streams.py` (`Event` 159-243, `record` 199-209,
  `elapsed_time` 234-243), `utils/benchmark/utils/timer.py` (`timer` 17-20, `Timer` 66-382,
  `timeit` 259-273, `_estimate_block_size` 305-322, `blocked_autorange` 324-382),
  `docs/source/notes/cuda.md` (asynchronous execution 307-345, memory management 506-530).
  `self_cuda_time_total` is deprecated in favour of `self_device_time_total` on events but is
  still a `table` sort key.
- Pins checked with `git ls-remote --tags`: v2.14.1, 1.9.1 and v3.4.2 are still the newest
  stable PyTorch, scikit-learn and XGBoost releases; no pin moved.

Gaps:

- Reproducibility: the scikit-learn example uses `random.Random` as a labelled stand-in for
  `RandomState`, so the fold contents differ from scikit-learn's. Goldberg, O'Neill (PCG) and
  Bouthillier et al. are cited from memory. The snippet was not run under real PyTorch.
- State-space models: no pin implements an SSM, so S4, S4D, HiPPO, Mamba and Mamba-2 details
  (HiPPO-LegS formula, NPLR with p = √(n+½), S4D-real init, Mamba's B̄ = ΔB shortcut and
  block layout) follow the papers from memory, with arxiv.org unreachable from the Routine.
  The cost model counts only sequence mixing, with no grouped-query attention; the snippet
  was not run under real PyTorch.
- Profiling: the step kernels, warmup costs, trace spans, loader times and memory model are
  invented and labelled; the 989 TFLOP/s peak is the H100 SXM bf16 dense figure from general
  knowledge. PaLM's MFU definition, Korthikanti et al.'s HFU and Kaplan's 6N are cited from
  memory (arxiv.org unreachable). Nsight, Perfetto and pytorch.org/memory_viz are named, not
  pinned. The snippet was not run under real PyTorch.

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

The queue is empty since run 43. From now on the Routine runs the weekly audit (spec §8.1): for each pin it checks for a newer stable release (never an rc, beta or dev tag). When one
exists, it diffs every file the ready pages link to between the pin and that tag, updates the
affected line ranges and claims, and moves the pin.
