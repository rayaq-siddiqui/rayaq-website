# rayaq.ca/ml-models — build progress

This is the running log for the daily ml-models architecture Routine. Read it first and update it last.
The contract is `specs/ml-models.md` (spec v1, read-only without the owner's say-so). This file
records where the build actually stands.

**Last updated:** 2026-10-08 (first run, bootstrap). This run wrote the spec, set the pin and built
the section scaffold. No topic page is ready yet. The next run builds `transformer`.

## Upstream pin

`pytorch/pytorch` tag `v2.14.1` → commit `5c4886908584029761b579af026dcfb627c84070`
(committed 2026-09-29, `version.txt` `2.14.1a0`), analyzed 2026-10-08. The pin is held in
`ml_models_docs.UPSTREAM`. `v2.15.0` only had release candidates (rc2) on the analysis date, so
`v2.14.1` is the latest stable release.

To verify a line range, use a sparse, shallow clone at the tag. Clone with
`--depth 1 --branch v2.14.1 --filter=blob:none --sparse`, then sparse-checkout
`torch/nn torch/optim torch/amp`. That is enough for every file the spec lists.

## §9 acceptance criteria

- [x] `/ml-models` renders the model-family map. Each box links to its page once ready and to
      pinned source until then.
- [ ] Every §5 page exists, meets its "Must cover" column and §6, and is registered (0 of 10 ready).
- [x] Every PyTorch link is pinned to `UPSTREAM.commit` (tested).
- [x] §7.5 tests exist and pass.
- [x] No `torch` in requirements (tested). There is no offline data yet, so there is no
      script or seed to record.
- [x] Mobile at 390px: no horizontal page scroll on `/ml-models` (checked in headless Chromium).
- [ ] The Routine has run at least once in maintenance mode.

## Decisions

- **PyTorch-only links.** Sub-pages link only to the pinned PyTorch source. They don't link to
  a reference implementation such as nanoGPT or Hugging Face. The spec's non-goals record this.
  Where PyTorch has no module for an idea (a GPT block, RoPE, a U-Net), the page builds it from
  PyTorch primitives in a snippet and links those primitives. Papers are cited for conventions.
- **Homepage card.** At the owner's request (2026-10-08), `/` links to `/ml-models`, placed
  after the jj internals card and before jj-dojo (tested in `app_tests.py`).
- **Layout reuses `jj.css`.** It is linked, never edited. Section-specific styles live in
  `ml_models.css`.
- **`ml_models.js` is progressive enhancement only.** A figure marked `data-ml-steps`, with
  `data-ml-step` panels, becomes a one-at-a-time slider. Without JS, all panels stay visible.

## Offline data (`tools/ml_models/` → `frontend/static/ml_models/`)

None yet. Record each script here as script · output · seed · torch version used.

## Verified line ranges at the pin (for upcoming pages)

The paths below are relative to `torch/nn/modules/` unless they give a fuller path.

- `transformer.py`
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
  - Start lines only: `embedding` 2509, `layer_norm` 2972, `rms_norm` 2998, `cross_entropy` 3478.
- `normalization.py`
  - `LayerNorm` 105-236, with `__init__` from 188 and its params up to 216.
  - `GroupNorm` starts at 239.
  - `RMSNorm` 343-436.
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

## Known gaps and deviations

- Where the list above gives only a start line, the end line is unverified. Check the end
  before linking a range. A naive "next top-level line" scan gets fooled by unindented
  docstrings and comments; it gave a wrong end for `RMSNorm`, which was corrected by hand.
- On the index map, the boxes for `vision-transformer`, `mixture-of-experts` and
  `diffusion-unet` link to whole files (`conv.py`, `container.py`) until their pages exist.

## First run (2026-10-08) — bootstrap

| Commit | What |
|---|---|
| see `git log -- specs/ml-models.md` | Spec v1, pin, scaffold (`ml_models_docs.py`, routes, base/index templates, CSS, JS, tests, AGENTS.md entry, this file) |

## Queue

1. `transformer` ← next
2. `attention`
3. `positional-encoding`
4. `layernorm-and-residuals`
5. `decoder-only-llm`
6. `encoder-only`
7. `vision-transformer`
8. `mixture-of-experts`
9. `diffusion-unet`
10. `training-loop`

Once the queue is empty, the Routine runs maintenance only. In that mode it checks for a newer
stable PyTorch release (not an rc). If one exists, it diffs every linked file between the pin
and that tag, updates the affected line ranges and claims, and moves the pin.
