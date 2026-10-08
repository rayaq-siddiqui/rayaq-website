# rayaq.ca/ml-models — build progress

This is the running log for the daily ml-models Routine. Read it first and update it last.
The contract is `specs/ml-models.md` (spec v2, read-only without the owner's say-so). This file
records where the build actually stands.

**Last updated:** 2026-10-08 (eighteenth run). Spec v2 widens the section from model architectures
to all of machine learning: 12 areas, 93 pages, a seven-step learning path and a fixed page
format. Ready pages: `transformer` and queue items 1-17, the last being `layernorm-and-residuals`.
The next run retrofits `transformer` to the §6 format (queue item 18).

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
- [ ] Every §5 page is ready and meets its "Must cover" column and §6 (1 of 93 ready:
      `transformer`, still in the v1 format).
- [x] Every link into a pinned repository uses that pin's commit (tested).
- [x] §7.5 tests exist and pass, including the §6 section order for every ready page except
      the v1 `transformer`.
- [x] No ML package in either requirements file (tested). There is no offline data yet.
- [x] Mobile at 390px: no horizontal page scroll on `/`, `/ml-models` or
      `/ml-models/transformer` (checked in headless Chromium).
- [ ] The Routine has run at least once in maintenance mode.

## Decisions

- **Spec v2 (2026-10-08).** At the owner's request, `/ml-models` became the place to learn or
  refresh anything in ML, for beginners and experts. The spec gained the 12 areas, levels, the
  learning path, the §6 page format (Problem · Intuition · Mechanics · Worked example ·
  Implementation · Tradeoffs · Connections · References) and a 93-page inventory.
- **Multiple pins (supersedes "PyTorch-only links").** Code links go to pinned PyTorch,
  scikit-learn and XGBoost releases, through `pinned_url` and the `src`/`skl`/`xgb`/`pinned`
  template helpers. Papers are cited for ideas no library implements. Reference repositories
  such as nanoGPT or Hugging Face are still not linked.
- **Prerequisite-first queue.** §5.13's order is expanded so every page's prerequisites come
  before it (inserted depth-first). `test_progress_queue_lists_every_page_after_its_prerequisites`
  checks the queue below.
- **Connections come from the registry.** Pages include `ml_models/_connections.html` in their
  `connections` section; it renders "Read first" and "Read next" from `connections(slug)`.
- **Navigation.** The nav groups pages by area in collapsible groups and opens the current
  page's area. The breadcrumb names the area and level. The footer credits every pin.
- **Homepage card.** At the owner's request (2026-10-08), `/` links to `/ml-models`, after the
  jj internals card and before jj-dojo (tested in `app_tests.py`).
- **Layout reuses `jj.css`.** It is linked, never edited. Section styles live in `ml_models.css`.
- **`ml_models.js` is progressive enhancement only.** `data-ml-steps` figures become
  one-at-a-time sliders, and the transformer page's attention table and parameter calculator
  are live. Every page reads in full without JS.
- **Upcoming models list.** The index keeps `UPCOMING_MODELS`, four tiers of notable models
  with their papers, marking the ones that map to a registered page.
- **Interactive transformer page.** Its worked numbers come from `attention_weights` and
  `transformer_param_count` in `ml_models_docs.py`, not from torch. Keep these when
  retrofitting it to §6.

## Offline data (`tools/ml_models/` → `frontend/static/ml_models/`)

None yet. Record each script here as script · command · output · seed · library version.

## Verified line ranges at the pins (for upcoming pages)

### PyTorch v2.14.1

The paths below are relative to `torch/nn/modules/` unless they give a fuller path.

- `transformer.py`
  - Used by the transformer page as well: `TransformerEncoder.forward` layer loop 541-555,
    encoder-layer fast path 917-942, `TransformerDecoderLayer.__init__` 1046-1061.
  - `Transformer` 58-317. Constructor defaults 102-119: d_model 512, nhead 8, 6+6 layers,
    dim_feedforward 2048, dropout 0.1, relu, eps 1e-5, `batch_first=False`, `norm_first=False`.
  - `TransformerEncoder` 320-555.
  - `TransformerDecoder` 558-660.
  - `TransformerEncoderLayer` 663-982.
  - `TransformerDecoderLayer` 985-1196.
- `activation.py`
  - `MultiheadAttention` 1090-1573, with `__init__` at 1163-1229.
  - `in_proj_weight` 1207-1213, `in_proj_bias` 1215-1218, `out_proj` 1219-1221.
  - `GELU` 778-823.
- `torch/nn/functional.py`
  - `scaled_dot_product_attention` docstring 6367-6540.
  - `multi_head_attention_forward` 6664-7120.
  - The head reshape in `multi_head_attention_forward` is at 6974; `relu` is at 1766.
  - Start lines only: `embedding` 2509, `layer_norm` 2972, `rms_norm` 2998, `cross_entropy` 3478.
- `normalization.py`
  - `LayerNorm` 105-236, with `__init__` from 188 and its params up to 216.
  - `GroupNorm` starts at 239.
  - `RMSNorm` 343-436.
- Attention ranges verified at the pin:
  - `activation.py`: `MultiheadAttention` 1090-1573, `__init__` 1163-1231, `_reset_parameters` 1233-1247, `forward` 1256-1523 (fast-path checks 1327-1395), `merge_masks` 1525-1573.
  - `functional.py`: `_in_projection_packed` 6217-6292, `_canonical_mask` 6612-6638, `multi_head_attention_forward` 6664-7120 (head reshape 6974-6991, need_weights branch 7050-7086, SDPA branch 7087-7120).
  - `torch/nn/attention/__init__.py`: `SDPBackend` doc 40-56, `sdpa_kernel` 114-166.
  - `bias.py`: `CausalVariant` 33-84, `CausalBias` 86-306, `causal_upper_left`/`causal_lower_right` 308-376.
  - `flex_attention.py`: `BlockMask` 855-1694, `or_masks`/`and_masks` 1759-1785, `create_block_mask` 1967-2088, `flex_attention` 2365-2640.
- Normalization ranges verified at the pin:
  - `normalization.py`: `LayerNorm` 105-236, `GroupNorm` 239-340, `RMSNorm` 343-436.
  - `batchnorm.py`: `_NormBase` 25-150, `_BatchNorm` 152-224.
  - `functional.py`: `batch_norm` 2865-2926, `layer_norm` 2972-2996, `rms_norm` 2998-3013.
  - `transformer.py`: `TransformerEncoderLayer` 663-982 (norm order 944-958, `_sa_block`/`_ff_block` 960-983); `dropout.py` `Dropout` 35-73.
- `sparse.py`: `Embedding` 14-264, weight 164-168.
- `linear.py`: `Linear` 53-147, weight and bias 104-114.
- `dropout.py`: `Dropout` 35-73.
- `loss.py`: `CrossEntropyLoss` 1200-1407.
- `torch/optim/adamw.py`: `AdamW` 19-56. The docstring starts at 59, and the `adamw` function at 129.
- `torch/optim/lr_scheduler.py`
  - `CosineAnnealingLR` 1338-1475.
  - Start lines only: `LambdaLR` 343, `LinearLR` 877, `SequentialLR` 1082, `OneCycleLR` 2285.
- `torch/amp/autocast_mode.py`: `autocast` starts at 52.
- `torch/amp/grad_scaler.py`: `GradScaler` starts at 53.
- `torch/nn/utils/clip_grad.py`: `clip_grad_norm_` starts at 185.
- `torch/nn/attention/bias.py`: start lines only for `CausalBias` 86, `causal_upper_left` 308 and
  `causal_lower_right` 342.
- `torch/nn/attention/flex_attention.py`: start lines only for `create_block_mask` 1967 and
  `flex_attention` 2365.
- `conv.py`: start lines only for `Conv2d` 388 and `ConvTranspose2d` 1012.
- `container.py`: start lines only for `Sequential` 59 and `ModuleList` 341.
- `torch/_tensor.py`: `Tensor` class starts at 102; `__len__` 1189-1203; `unflatten` 1353.
- `torch/functional.py`: `broadcast_tensors` 47-76, `broadcast_shapes` 79-117, `einsum` 175-382.
  Start lines only: `cdist` 1483, `norm` 1734.
- `distance.py` (100 lines): `PairwiseDistance` 10-61, with `forward` at 57; `CosineSimilarity`
  64-100. Its docstring clamps the product of the norms, while `F.cosine_similarity` (in
  `torch/nn/functional.py` 5895-5924) clamps each norm; the function is what runs.
  `pairwise_distance` starts at 5858 in `functional.py`.
- `torch/linalg/__init__.py`: `vector_norm` 1491-1568; `matrix_norm` starts at 1570.
- `torch/_torch_docs.py` (each range runs from `add_docstr(` to its closing `)`): `as_strided`
  1019-1060, `broadcast_to` 1896-1916, `stack` 1918-1976, `permute` 8953-8971, `reshape`
  9833-9863, `squeeze` 11063-11111, `transpose` 11942-11990, `unsqueeze` 12475-12504, `dot`
  4134-4162, `vdot` 4164-4211, `inner` 5093-5152, `outer` 5154-5182. Start
  lines of the `torch.X,` entry: `cat` 2532, `matmul` 7909, `tensor` 9583, `zeros` 12618.
  Matrix ops: `matmul` 7908-7990, `mm` 7831-7887, `bmm` 1706-1762, `addmm` 592-665, `baddbmm`
  1512-1581, `eye` 4380-4408, `inverse` 5606-5613 (an alias of `linalg.inv`), `t` 11507-11544.
- `torch/linalg/__init__.py`: `inv` 214-292.
- `torch/nn/functional.py`: `linear` 2382-2403 (docstring "y = xA^T + b").
- `torch/nn/modules/linear.py`: `Linear` 53-147; `__init__` 96, `weight`/`bias` 104-114,
  `reset_parameters` 117-128 (kaiming_uniform with a=√5, bias bound 1/√fan_in), `forward`
  130-134 (calls `F.linear`).
- `torch/_tensor_docs.py` (each range from `add_docstr_all(` to `)`): `contiguous` 1131-1144,
  `is_contiguous` 2702-2714, `stride` 4963-4989, `view` 6041-6180, `expand` 6198-6249.
  Autograd attributes: `grad` 6555-6563 ("accumulate (add)"), `retain_grad` 6595-6603,
  `requires_grad` 6613-6624, `is_leaf` 6626-6666, `requires_grad_` 4125-4161.
- `torch/autograd/__init__.py`: `backward` 255-403; `grad` 434-621 (its overloads start at 406).
- `torch/_tensor.py`: `Tensor.backward` 566-625 (calls `torch.autograd.backward`);
  `register_hook` starts at 655.
- `torch/autograd/functional.py`: `jacobian` 587-853; `hessian` starts at 856.
- `torch/autograd/grad_mode.py`: `no_grad` 22-86; `enable_grad` starts at 89.
- `torch/autograd/function.py`: `FunctionCtx.save_for_backward` 41-100, `backward` 473-505
  (ends with `vjp = backward`), `jvp` 531-553, `Function` 555-655 (docstring has the `Exp`
  example).
- `torch/autograd/functional.py`: `vjp` 271-363, `jvp` 366-476.
- `torch/autograd/forward_ad.py`: `make_dual` 77-138; `dual_level` starts at 185.
- `torch/distributions/normal.py`: `Normal` docstring 15-31; `__init__` 55-66; `sample` 77-80; `rsample` 82-85; `log_prob` 87-101; `cdf` 103-108; `icdf` 110-111; `entropy` starts at 113.
- `torch/distributions/categorical.py`: `Categorical` with docstring 13-50; `__init__` 56-85; `sample` 144-149; `log_prob` 151-157; `entropy` 159-163.
- `torch/distributions/bernoulli.py`: `Bernoulli` with docstring 20-40; `__init__` starts at 47; `sample` 116-119; `log_prob` 121-125; `entropy` 127-130.
- `torch/distributions/normal.py` properties: `mean` 39-41, `mode` 43-45, `stddev` 47-49, `variance` 51-53 (each `@property` on the line before).
- `torch/random.py`: `set_rng_state` 27-36; `get_rng_state` 39-46; `manual_seed` 49-59; `_manual_seed_impl` 62-86; `seed` starts at 89; `initial_seed` 144-150; `fork_rng` 156-239 (decorator at 156, def at 157).
- `torch/distributions/kl.py`: `register_kl` starts at 51; `kl_divergence` 165-193; `_kl_bernoulli_bernoulli` 203-216; `_kl_categorical_categorical` 247-252; `_kl_normal_normal` 467-471 (each with its `@register_kl` decorator on the first line).
- `torch/distributions/categorical.py`: `entropy` 159-163.
- `torch/nn/functional.py`: `kl_div` 3401-3475; `cross_entropy` 3478-3569.
- `torch/nn/modules/loss.py`: `KLDivLoss` 464-564; `CrossEntropyLoss` 1200-1407 (`forward` 1398-1407).
- `torch/nn/modules/loss.py` (loss-functions): `_Loss` 42-50; `L1Loss` 66-133; `NLLLoss` 136-266; `MSELoss` 567-630; `BCEWithLogitsLoss` 719-844; `HingeEmbeddingLoss` 847-922; `SmoothL1Loss` 988-1078; `HuberLoss` 1081-1150; `CosineEmbeddingLoss` 1671-1740; `MarginRankingLoss` 1743-1807; `MultiMarginLoss` 1810-1903; `TripletMarginLoss` 1906-2013.
- `torch/nn/functional.py` (loss-functions): `nll_loss` 3180-3244; `binary_cross_entropy_with_logits` 3634-3701; `huber_loss` 4107-4192; `l1_loss` 4195-4268; `mse_loss` 4271-4346; `margin_ranking_loss` 4349-4397; `multi_margin_loss` 4635-4696; `triplet_margin_loss` 5977-6016.
- `torch/nn/modules/module.py` (neurons-and-layers): `class Module` 407, `__init__` 482-525; `register_buffer` 528; `register_parameter` 592-641; `add_module` 642-669; `_wrapped_call_impl` 1779-1786; `_call_impl` 1787-1921 (no-hook fast path 1788-1794), `__call__` 1922; `__setattr__` 1976-2080; `state_dict` 2199; `parameters` 2670-2698; `named_parameters` 2699-2730; `train` 2894; `eval` 2916; `zero_grad` 2957.
- `torch/nn/modules/container.py` (neurons-and-layers): `Sequential` 59-339 (`__init__` 115-122, `forward` 254-260); `ModuleList` 341-510; `ModuleDict` 511.
- `torch/nn/modules/linear.py` (neurons-and-layers): `reset_parameters` 117-129, `forward` 130-135. `activation.py`: `ReLU` 104-152, `Sigmoid` 337, `Tanh` 407.
- `torch/autograd/__init__.py` (backpropagation): `backward` 255-403, `grad` 434-621. `graph.py`: `_engine_run_backward` 1059-1083, the handoff to the C++ engine. `function.py`: `FunctionCtx.save_for_backward` 41-100, `_SingleLevelFunction.backward` 473-505, `Function` 555-655. `torch/_tensor.py`: `Tensor.backward` 566-625.
- `torch/autograd/gradcheck.py`: `gradcheck` 1999-2105 (`eps=1e-6`, `atol=1e-5`, `rtol=1e-3`), `_compute_numerical_gradient` 358-394. `clip_grad.py`: `clip_grad_norm_` 185-232. `module.py`: `zero_grad` 2957-2985. `torch/utils/checkpoint.py`: `checkpoint` 423-619.
- `torch/optim/sgd.py` (optimizers): `SGD` 28-105, `_single_tensor_sgd` 322-380. `adam.py`: `Adam` 34-138, `_single_tensor_adam` 347-552 (decoupled decay 415-418, bias correction 528-546). `adamw.py`: `AdamW` 19-47. `rmsprop.py`: `_single_tensor_rmsprop` 265-341.
- `torch/optim/optimizer.py`: `Optimizer` starts at 358; `state_dict` 700-791, `zero_grad` 1048-1110, `step` 1117-1124, `add_param_group` 1127-1180.
- `torch/nn/modules/sparse.py` (embeddings): `Embedding` 14-264 (`__init__` 134-177, `reset_parameters` 179-181, `forward` 188-197, `from_pretrained` 213-264); `EmbeddingBag` starts at 267. `torch/nn/functional.py`: `embedding` 2509-2621.

### scikit-learn 1.9.1 (start lines; check the end before linking a range)

Paths are under `sklearn/`.

- `linear_model/_base.py`: `LinearRegression` 519 (verified range 519-765; `fit` 654-760,
  dense `linalg.lstsq` branch 751-755, `positive`/sparse branches 707-750),
  `_preprocess_data` 113-220, `_set_intercept` 318-334.
- `linear_model/_logistic.py`: `LogisticRegression` 974 (verified range 974-1637; `C` docstring
  1023-1029, `l1_ratio` 1031-1047, solver table 1096-1153, `fit` 1333-1572, `predict_proba`
  1573-1604), `_check_solver` 81-103, `_logistic_regression_path` 219-720 (lbfgs branch 580-606,
  `l2_reg_strength = 1 / (C * sw_sum)` at 580), `LogisticRegressionCV` 1638.
- `linear_model/_base.py` (classifiers): `LinearClassifierMixin` 360, `decision_function` 366-397,
  `predict` 398-428, `_predict_proba_lr` 429-452.
- `linear_model/_linear_loss.py`: `LinearModelLoss` 47 (`loss` 231-290), `l2_penalty` 226-229,
  `gradient_hessian` 454-710. `sklearn/_loss/` is not in the sparse clone; cite these instead.
- `linear_model/_glm/_newton_solver.py`: `NewtonSolver` 22-451, `NewtonCholeskySolver` 452-637.
- `linear_model/_ridge.py`: `Ridge` 1022 (verified range 1022-1287), `_solve_cholesky` 215-234,
  `_solve_svd` 299-309, `resolve_solver_for_numpy` 867-878.
- `linear_model/_coordinate_descent.py`: `Lasso` 1329 (verified range 1329-1517), `ElasticNet` 884.
- `linear_model/_cd_fast.pyx`: `enet_coordinate_descent` 243; soft-threshold update 439-452.
- `tree/_classes.py`: `DecisionTreeClassifier` 699, `DecisionTreeRegressor` 1097.
- `ensemble/_forest.py`: `RandomForestClassifier` 1174.
- `ensemble/_gb.py`: `GradientBoostingClassifier` 1145.
- `ensemble/_hist_gradient_boosting/gradient_boosting.py`: `HistGradientBoostingClassifier` 1762.
- `svm/_classes.py`: `SVC` 623.
- `neighbors/_classification.py`: `KNeighborsClassifier` 44.
- `cluster/_kmeans.py`: `KMeans` 1191.
- `decomposition/_pca.py`: `PCA` 113.
- `model_selection/_split.py`: `KFold` 437, `GroupKFold` 533, `StratifiedKFold` 687,
  `TimeSeriesSplit` 1116, `train_test_split` 2797.
- `model_selection/_validation.py`: `cross_validate` 101, `cross_val_score` 512,
  `learning_curve` 1776, `validation_curve` 2283.
- `preprocessing/_data.py`: `StandardScaler` 742.
- `impute/_base.py`: `SimpleImputer` 171.
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

## First run (2026-10-08) — bootstrap

| Commit | What |
|---|---|
| see `git log -- specs/ml-models.md` | Spec v1, pin, scaffold (`ml_models_docs.py`, routes, base/index templates, CSS, JS, tests, AGENTS.md entry, this file) |

## Second run (2026-10-08) — transformer and upcoming models

| Commit | What |
|---|---|
| `ml-models: add the upcoming models list data` | `UPCOMING_MODELS` with tests |
| `ml-models: list upcoming models on the index` | The tiered grid on `/ml-models` |
| `ml-models: compute the transformer page's worked numbers` | `attention_weights`, `transformer_param_count`, presets |
| `ml-models: add an interactive attention table` | The attention playground in `ml_models.js` |
| `ml-models: add a parameter calculator` | The calculator in `ml_models.js` |
| `ml-models: add the transformer page` | `transformer.html`, ready flag, CSS, test |

The README was refreshed in a separate `docs:` commit in the same run.

## Third run (2026-10-08) — spec v2

| Commit | What |
|---|---|
| `ml-models: widen the spec to a full ml reference` | Spec v2 |
| `ml-models: pin scikit-learn and xgboost beside pytorch` | `PINS`, `pinned_url`, template helpers, tests |
| `ml-models: register the twelve areas and every planned page` | `AREAS`, `PAGES` and spec-inventory tests |
| `ml-models: add the learning path and page connections` | `LEARNING_PATH`, `connections`, tests |
| `ml-models: group the nav by area and credit every pin` | `base.html` nav, breadcrumb, footer |
| `ml-models: show the learning path and every area on the index` | `index.html` |
| `ml-models: add the connections partial and the page format test` | `_connections.html`, §6 test |
| `ml-models: expand the build queue for spec v2` | This file, the §5.13 prerequisite rule, the queue test |
| `ml-models: add a 390px overflow checker for the routine` | `tools/ml_models/check_mobile.js` |
| `docs: record the ml-models routine` | The Routine section above, AGENTS.md |

The daily Routine was created at the end of this run.

## Fourth run (2026-10-08) — first page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested shape, stride and broadcasting helpers` | `broadcast_steps`, `contiguous_strides`, `element_offset`, `is_contiguous`, `transpose_layout` |
| `ml-models: build the tensors-and-shapes page` | The page, `ready`, queue ✓ |
| `docs: record the tensors-and-shapes run` | This table and the verified ranges above |

## Fifth run (2026-10-08) — second page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested dot product, norm and cosine helpers` | `dot_product`, `vector_norm`, `cosine_similarity`, `angle_degrees`, `projection`, `similarity_ranking` and the two worked-example constants |
| `ml-models: build the vectors-and-dot-products page` | The page, `ready`, queue ✓ |
| `docs: record the vectors-and-dot-products run` | This table and the verified ranges above |

Jinja constant-folds `"inf"|float` into a bare `inf` in compiled template code, which raises
`NameError` at render time. Compute such values in Python or with filters on lists instead.

## Sixth run (2026-10-08) — third page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested matmul, shape-rule and flop helpers` | `transpose`, `identity`, `matmul`, `matmul_shape` (torch.matmul's rank and broadcast rules), `matmul_flops`, `linear_layer`, `inverse_2x2` and three worked-example constants |
| `ml-models: build the matrix-multiplication page` | The page, `ready`, queue ✓ |
| `docs: record the matrix-multiplication run` | This table and the verified ranges above |

## Seventh run (2026-10-08) — fourth page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested slope, gradient and descent helpers` | `difference_quotient`, `slope_table`, `numerical_gradient`, `numerical_jacobian`, the bowl and its gradient, `gradient_descent`, `bowl_descent`, `bowl_contours`, `stable_learning_rate` and three worked-example constants |
| `ml-models: build the derivatives-and-gradients page` | The page, `ready`, queue ✓. Links to `chain-rule` and `optimizers` stay plain text until those pages are ready, since the link test rejects 404s |
| `docs: record the derivatives-and-gradients run` | This table and the verified autograd ranges above |

## Eighth run (2026-10-08) — fifth page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested chain-rule and backprop helpers` | `scalar_chain`, `relu`, `two_layer_pass` (every forward value and gradient of a Linear-ReLU-Linear network), `two_layer_loss` for the finite-difference tests, `mode_costs`, and three worked-example constants |
| `ml-models: build the chain-rule page` | The page, `ready`, queue ✓; the derivatives page's chain-rule mentions become links |
| `docs: record the chain-rule run` | This table and the verified `function.py`, `functional.py` and `forward_ad.py` ranges above |

## Ninth run (2026-10-08) — sixth page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested probability helpers` | `bernoulli_pmf`, `categorical_from_logits` (logsumexp-normalized, like `Categorical`), `inverse_cdf_sample`, `normal_log_prob`/`normal_pdf`/`normal_cdf`/`normal_band`, `joint_table`, and their example constants |
| `ml-models: build the probability-and-distributions page` | The page, `ready`, queue ✓; `math.log` exposed to templates |
| `docs: record the probability-and-distributions run` | This table and the verified `torch.distributions` ranges above |

## Tenth run (2026-10-08) — seventh page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested expectation and sampling helpers` | `expectation`, `variance`, `covariance`, `die_rolls` (seeded), `running_means`, `sum_pmf`, `minibatch_gradients` (every batch via `itertools.combinations`), and the die, covariance and minibatch example constants |
| `ml-models: build the expectation-and-variance page` | The page, `ready`, queue ✓; `sqrt` and `log10` exposed to templates; per-batch gradients kept for the dot-strip figure |
| `docs: record the expectation-and-variance run` | This table and the verified `torch/random.py` and `Normal` property ranges above |

## Eleventh run (2026-10-08) — eighth page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested entropy and divergence helpers` | `information_content`, `entropy`, `cross_entropy`, `kl_divergence` (bits by default, infinite where q has no mass), `logits_cross_entropy` (log-softmax loss and softmax-minus-one-hot gradient), `perplexity`, `mutual_information`, and the weather, asymmetry and perplexity example constants |
| `ml-models: build the entropy-and-kl page` | The page, `ready`, queue ✓; `math.exp` exposed to templates |
| `docs: record the entropy-and-kl run` | This table and the verified `kl.py`, `Categorical.entropy`, `functional.py` and `loss.py` ranges above |

## Twelfth run (2026-10-08) — ninth page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested loss-function helpers` | `huber`, `regression_losses`, `fit_constant` (mean, median, Huber by bisection), `bce_with_logits` (stable form), `margin_losses`, `triplet_loss`, `info_nce`, `reduce_losses`, and the outlier, triplet, InfoNCE and reduction example constants |
| `ml-models: build the loss-functions page` | The page, `ready`, queue ✓ |
| `docs: record the loss-functions run` | This table and the verified `loss.py` and `functional.py` loss ranges above |

## Thirteenth run (2026-10-08) — tenth page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested linear-regression helpers` | `least_squares_line`, `solve_linear`, `normal_equations`, `standardize`, `ridge_coefficients`, `soft_threshold`, `lasso_coefficients` (sklearn's objective), `regularization_paths`, `mse_hessian`, `line_descent`, `symmetric_eigen_2x2`, `quadratic_ellipse`, and the descent and three-feature regularization examples |
| `ml-models: build the linear-regression page` | The page, `ready`, queue ✓; also `torch.linalg.lstsq` 1078-1200 and `nn.Linear` 53-147 in PyTorch |
| `docs: record the linear-regression run` | This table and the verified scikit-learn linear-model ranges above |

## Fourteenth run (2026-10-08) — eleventh page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested logistic-regression helpers` | `sigmoid`, `logistic_objective` (sklearn's C-weighted objective, intercept unpenalized), `logistic_newton`, `logistic_descent`, `logistic_fit_1d`, `boundary_fits`, and the pass/fail, separable two-feature and softmax examples |
| `ml-models: build the logistic-regression page` | The page, `ready`, queue ✓; also `BCEWithLogitsLoss` 719-846 and `CrossEntropyLoss` 1200-1409 in PyTorch |
| `docs: record the logistic-regression run` | This table and the verified scikit-learn logistic ranges above |

## Fifteenth run (2026-10-08) — twelfth page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested neurons-and-layers helpers` | `mlp_forward`, `collapse_linear`, `xor_network`, `relu_interpolant`, `evaluate_interpolant`, `approximation_fits`, `mlp_param_count`, and the XOR, sin-approximation and MNIST-MLP examples |
| `ml-models: build the neurons-and-layers page` | The page, `ready`, queue ✓; adds `sin` to the template context |
| `docs: record the neurons-and-layers run` | This table and the verified `module.py`/`container.py` ranges above |

## Sixteenth run (2026-10-08) — thirteenth page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested backpropagation helpers` | `backprop_pass`, `backprop_example` (one SGD step), `relative_error`, `gradient_check`, `gradient_check_all`, `gradient_norms_by_depth`, and the 2-3-2 network, gradient-check and 30-layer depth examples |
| `ml-models: build the backpropagation page` | The page, `ready`, queue ✓ |
| `docs: record the backpropagation run` | This table and the verified autograd, gradcheck and clip_grad ranges above |

## Seventeenth run (2026-10-08) — fourteenth page of the 5-minute loop

| Commit | What |
|---|---|
| `ml-models: add tested optimizer helpers` | `optimizer_step`, `optimizer_race`, `adam_trace`, `uncorrected_step_ratio`, `weight_decay_paths`, `optimizer_memory`, and the bowl, Adam and weight-decay examples |
| `ml-models: draft the optimizers page template` | The work-in-progress page, not yet routable |
| `ml-models: build the optimizers page` | Template fixes, `ready`, queue ✓ |
| `docs: record the optimizers run` | This table and the verified `torch/optim` ranges above |

## Eighteenth run (2026-10-08) — fifteenth page onward

| Commit | What |
|---|---|
| `ml-models: add tested embedding helpers` | `embedding_lookup`, `one_hot_rows`, `embedding_gradient`, `skipgram_pairs`, `train_skipgram` (seed 0, pure Python), `nearest_words`, `tied_parameter_counts` |
| `ml-models: build the embeddings page` | The page, `ready`, queue ✓ |
| `ml-models: add tested attention helpers` | `scaled_attention`, `multihead_attention`, mask helpers, GQA and cache helpers |
| `ml-models: build the attention page` | The page, `ready`, queue ✓ |
| `ml-models: add tested normalization helpers` | `layer_norm_row`, `rms_norm_row`, `batch_norm_columns`, `group_norm_row`, running statistics, residual blocks, `residual_demo` |
| `ml-models: build the layernorm-and-residuals page` | The page, `ready`, queue ✓ |

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
18. `transformer` ✓ ← next (v1 format; retrofit it to §6 here, keeping its interactive pieces)
19. `training-loop`
20. `decoder-only-llm`
21. `decoding`
22. `kv-cache`
23. `learning-paradigms`
24. `generalization`
25. `data-splits`
26. `preprocessing`
27. `data-leakage`
28. `classification-metrics`
29. `cross-validation`
30. `decision-trees`
31. `gradient-boosting`
32. `overfitting`
33. `bias-variance`
34. `regularization`
35. `activation-functions`
36. `linear-algebra-toolkit`
37. `missing-data`
38. `computation-graphs`
39. `cnns`
40. `autoregressive-models`
41. `tokenization`
42. `nearest-neighbors`
43. `similarity-search`
44. `gpu-execution`
45. `mixed-precision`
46. `quantization`
47. `reinforcement-learning`
48. `bayes-rule`
49. `class-imbalance`
50. `random-forests`
51. `initialization`
52. `rnns-and-lstms`
53. `autoencoders`
54. `variational-autoencoders`
55. `positional-encoding`
56. `clustering`
57. `vector-indexes`
58. `distillation`
59. `time-series`
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
