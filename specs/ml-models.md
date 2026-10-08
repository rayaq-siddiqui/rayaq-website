# rayaq.ca/ml-models — large model architecture reference

**Status:** approved for build · **Owner:** Rayaq Siddiqui · **Spec version:** 1 (2026-10-08)

This is the product and technical contract for `rayaq.ca/ml-models`. The daily
implementation Routine builds and maintains the section against it. Build progress lives in
`specs/ml-models-progress.md`. Don't edit this spec without the owner's say-so. If the code
and the spec disagree, fix the code or record a deliberate deviation in the progress file.

---

## 1. Goal and audience

`rayaq.ca/ml-models` is a static reference that explains the architecture of large machine
learning models, with hand-drawn diagrams and visualizations, where every code link points
into one pinned PyTorch release.

The reader is an engineer who knows Python well but not transformer internals. Someone who
has read it should be able to:

- draw the original encoder-decoder transformer and its decoder-only, encoder-only, vision,
  mixture-of-experts and diffusion descendants, and say what each block does;
- follow the shape of every tensor through a layer (`[batch, seq, d_model]` →
  `[batch, heads, seq, d_head]` and back);
- count a model's parameters from its configuration;
- find the PyTorch module or function that implements each piece, at the right lines.

It's a reference, not a course. Every page opens with a short plain-language summary.

## 2. Non-goals

- Tutorials on Python, tensors, autograd or gradient descent basics.
- Leaderboards, benchmarks, model comparisons or opinion on which model is best.
- Reproducing papers' experiments, or training anything at request time.
- Links into third-party model code (for example nanoGPT or Hugging Face `transformers`).
  The owner chose PyTorch-only links to keep a single pin (§3.4). Where PyTorch has no
  module for an idea (RoPE, a GPT block, a U-Net), the page's reference snippet shows it
  built from PyTorch primitives, and the primitives are what get linked.

## 3. Hard constraints

1. **Static content.** Pages are server-rendered from committed templates. No runtime call
   to GitHub or any other service, no client-side fetching, no JavaScript library or CDN.
2. **Small vanilla JS only.** `frontend/static/ml_models.js` may add interactivity (for
   example a slider that steps through attention heads or tokens). Every page must read
   fully without JS: the default, no-JS state shows a meaningful figure, and nothing is
   hidden behind a script.
3. **No torch on the server.** Never add `torch` (or numpy, or any ML package) to
   `backend/requirements.txt` or `requirements-dev.txt`, and never run it in CI or at request
   time. The server is an e2-micro VM. Data computed with PyTorch (real attention weights
   from a tiny model, positional-encoding curves) comes from an offline script in
   `tools/ml_models/`, and its output is committed as small JSON or SVG files under
   `frontend/static/ml_models/`. The progress file records the exact script, command,
   PyTorch version and seed for every committed output.
4. **Pinned to one PyTorch release.** The whole section describes exactly one PyTorch stable
   release tag, recorded in code (§7.3) and shown on every page. Every PyTorch link goes
   through `ml_models_docs.source_url(path, start, end)`, which pins it to the tag's commit
   SHA. Never link `blob/main` or a branch.
5. **Every claim is sourced.** Claims about how PyTorch behaves (defaults, argument order,
   tensor layouts, what a function computes) must match the pinned source and link to it
   with a line range. Claims that are convention rather than PyTorch code (paper formulas,
   typical hyperparameters, model configurations) cite the paper, by title, authors, year
   and an arXiv link.
6. **Never fabricate.** Class, function and argument names, defaults and shapes are copied
   from source, not recalled. When unsure, omit and log the gap in the progress file.
7. **Licensing.** PyTorch is BSD-3-Clause. Every page footer credits PyTorch and links its
   `LICENSE` at the pin. Code excerpts stay short.
8. **Section isolation.** Several Routines push to this repo. This section owns only its own
   files (§7). It never edits another section's files (`/jj*`, weather, resume, assembly),
   including `jj.css`, which it may link but not change. Shared registration points
   (`app.py`, `AGENTS.md`, `backend/tests/app_tests.py`) get additive edits only.
9. **No homepage card** until the owner decides to add one.
10. **House rules.** Everything in `AGENTS.md` applies.

## 4. Information architecture

```
/ml-models               Index: summary, the model-family map, page list
/ml-models/<slug>        One deep-dive page per topic (§5)
```

- Every page shares one layout: a section nav, a breadcrumb, an on-page table of contents
  built from its `h2`/`h3`, previous/next links, and a footer showing the pinned PyTorch
  tag, its commit, its date, and the date of the last analysis.
- Unknown slugs and pages not yet marked ready return 404. There is no catch-all.
  Headings have stable `id` anchors.

## 5. Page inventory

Build order is the table order. Paths are relative to the PyTorch repo root at the pin.

| Slug | Title | Must cover | PyTorch source set |
|---|---|---|---|
| *(index)* | ML model architectures | What the section is; a map of the model families and which page covers each block; the shared vocabulary (token, embedding, `d_model`, head, layer, logits); the pin; links to every page | `torch/nn/modules/transformer.py`, `torch/nn/modules/activation.py`, `torch/nn/functional.py` |
| `transformer` | The Transformer | The full encoder-decoder from *Attention Is All You Need* (Vaswani et al., 2017): embeddings and scaling by √d_model, positional encoding, encoder layer (self-attention, feed-forward, residual + LayerNorm), decoder layer (masked self-attention, cross-attention, feed-forward), the output projection and softmax; post-norm versus `norm_first`; how `nn.Transformer`, `TransformerEncoder(Layer)` and `TransformerDecoder(Layer)` map onto the paper, every constructor argument and default, `batch_first`, `generate_square_subsequent_mask`; the base-model parameter count | `torch/nn/modules/transformer.py`, `torch/nn/modules/activation.py` (`MultiheadAttention`), `torch/nn/modules/normalization.py` (`LayerNorm`), `torch/nn/modules/sparse.py` (`Embedding`), `torch/nn/modules/linear.py` |
| `attention` | Attention | Scaled dot-product attention step by step (QKᵀ, scaling, mask, softmax, ·V); multi-head attention and the head split/merge reshapes; padding, causal and additive versus boolean masks, and which way PyTorch's boolean masks point in each API; cross-attention; the KV cache for autoregressive decoding and its memory cost; grouped-query attention (`enable_gqa`); `MultiheadAttention`'s packed `in_proj_weight`, `need_weights`, and when it takes the fast path; `F.scaled_dot_product_attention` and its backends; FlexAttention's `score_mod`/`mask_mod` | `torch/nn/functional.py` (`scaled_dot_product_attention`, `multi_head_attention_forward`), `torch/nn/modules/activation.py`, `torch/nn/attention/__init__.py`, `torch/nn/attention/bias.py`, `torch/nn/attention/flex_attention.py` |
| `positional-encoding` | Positional encoding | Why attention needs position; sinusoidal encoding (formula, curves, the relative-offset property); learned absolute positions (`nn.Embedding`); rotary embeddings (RoPE): the 2-D rotation per frequency pair, why q·k then depends only on the offset, and a snippet built from tensor ops; a note on ALiBi as a bias, not an embedding | `torch/nn/modules/sparse.py`, `torch/nn/functional.py` (`embedding`), `torch/nn/modules/transformer.py` (where PyTorch leaves position to the caller) |
| `layernorm-and-residuals` | LayerNorm and residuals | What a residual stream is; LayerNorm's computation and its learned scale and bias; RMSNorm; pre-norm versus post-norm and why deep models prefer pre-norm; dropout placement; the feed-forward block and activations (ReLU, GELU, SwiGLU) | `torch/nn/modules/normalization.py` (`LayerNorm`, `RMSNorm`), `torch/nn/functional.py` (`layer_norm`, `rms_norm`), `torch/nn/modules/activation.py` (`GELU`, `SiLU`), `torch/nn/modules/dropout.py`, `torch/nn/modules/transformer.py` (`norm_first`) |
| `decoder-only-llm` | Decoder-only LLMs | The GPT-style stack: token and position embeddings, N pre-norm blocks with causal self-attention, final LayerNorm, the LM head and weight tying; next-token training versus autoregressive generation with a KV cache; sampling (temperature, top-k, top-p); the GPT-2-small parameter count worked through; how to build one from `TransformerEncoderLayer` with a causal mask, or from primitives | `torch/nn/modules/transformer.py`, `torch/nn/functional.py`, `torch/nn/modules/sparse.py`, `torch/nn/modules/linear.py`, `torch/nn/modules/loss.py` (`CrossEntropyLoss`) |
| `encoder-only` | Encoder-only models | The BERT-style stack: token, segment and position embeddings, bidirectional self-attention, the `[CLS]` token, masked-language-model and next-sentence objectives, padding masks, fine-tuning heads; the BERT-base parameter count | `torch/nn/modules/transformer.py` (`TransformerEncoder`, `src_key_padding_mask`, nested-tensor fast path), `torch/nn/modules/sparse.py`, `torch/nn/modules/loss.py` |
| `vision-transformer` | Vision Transformer | ViT: cutting an image into patches, patch embedding as a strided `Conv2d`, the class token, learned position embeddings, the encoder, the classification head; shapes from `[batch, 3, 224, 224]` to `[batch, 197, 768]`; ViT-B/16 parameter count | `torch/nn/modules/conv.py` (`Conv2d`), `torch/nn/modules/transformer.py`, `torch/nn/modules/flatten.py`, `torch/nn/modules/linear.py` |
| `mixture-of-experts` | Mixture of experts | Replacing the feed-forward block with E experts and a router; top-k gating, softmax over selected experts, load-balancing auxiliary loss, capacity and dropped tokens; total versus active parameters; a reference snippet from primitives (`topk`, `scatter`/index ops, `ModuleList`) | `torch/nn/modules/container.py` (`ModuleList`), `torch/nn/modules/linear.py`, `torch/nn/functional.py` (`softmax`) |
| `diffusion-unet` | Diffusion U-Net | The denoising objective (forward noising, predicting ε), the noise schedule, the U-Net: down and up paths, skip connections, ResNet blocks with GroupNorm, timestep embeddings, self- and cross-attention at low resolutions; sampling as repeated denoising; shapes at each resolution | `torch/nn/modules/conv.py` (`Conv2d`, `ConvTranspose2d`), `torch/nn/modules/normalization.py` (`GroupNorm`), `torch/nn/modules/upsampling.py`, `torch/nn/modules/activation.py` (`SiLU`, `MultiheadAttention`), `torch/nn/functional.py` |
| `training-loop` | The training loop | Cross-entropy loss over logits (shapes, `ignore_index`, label smoothing); the backward pass; gradient clipping; AdamW (the update rule, decoupled weight decay, which parameters get decay); learning-rate warmup and cosine decay with PyTorch's schedulers; mixed precision with `autocast` and `GradScaler` (and why bf16 needs no scaler); gradient accumulation; memory per parameter | `torch/nn/modules/loss.py`, `torch/nn/functional.py` (`cross_entropy`), `torch/optim/adamw.py`, `torch/optim/adam.py`, `torch/optim/optimizer.py`, `torch/optim/lr_scheduler.py`, `torch/amp/autocast_mode.py`, `torch/amp/grad_scaler.py`, `torch/nn/utils/clip_grad.py` |

**New pages.** The Routine may propose an addition (for example a page for a new PyTorch
attention API) as a queue row in the progress file with a slug, title, "must cover" and
source set. It is recorded as a deliberate addition until the owner folds it into this table.

## 6. What every topic page contains

1. **Summary.** A short plain-language paragraph at the top, inside the page `<header>`.
2. **Diagrams.** At least two hand-authored inline SVG diagrams, for example the full block
   diagram, tensor shapes flowing through each layer, or an attention-matrix heatmap with the
   causal mask. Each has `role="img"`, a `<title>` and a `<desc>`, uses the site's colour
   variables, works in light and dark mode, and scrolls sideways inside its own container on
   a phone instead of widening the page.
3. **Component tables** with the columns **Component · Shape/Params · Meaning · Source**.
   Source cells link the matching PyTorch code through `source_url`, with line ranges.
4. **A reference snippet**: minimal PyTorch code for the page's core idea, shown as
   `<pre><code>`, never executed by the site.
5. **A worked numeric example** where it helps (for example the GPT-2-small parameter count
   from its configuration, or attention scores for a four-token sequence).
6. **Citations.** Papers cited by title, authors, year and arXiv link, in a "References"
   section at the end.

## 7. Technical design

### 7.1 Routing

`app.py` gets `/ml-models` and `/ml-models/<slug>` and stays route-only: it asks
`ml_models_docs.render` for the page through `rendered_pages`, and returns 404 when it gets
`None`.

### 7.2 Files this section owns

```
backend/ml_models_docs.py              pin, source_url, PAGES, render()
backend/tests/ml_models_docs_tests.py  section tests (§7.5)
frontend/templates/ml_models/          base.html, index.html, <slug>.html fragments
frontend/static/ml_models.css          section styles (layout reuses jj.css, linked not edited)
frontend/static/ml_models.js           optional progressive enhancement
frontend/static/ml_models/             committed offline-computed JSON/SVG
tools/ml_models/                       offline scripts that produce it (run by hand, never in CI)
specs/ml-models.md, specs/ml-models-progress.md
```

### 7.3 Upstream pin

```python
UPSTREAM = {
    "repo": "https://github.com/pytorch/pytorch",
    "tag": "v<major>.<minor>.<patch>",
    "commit": "<40-char sha the tag points at>",
    "commit_date": "YYYY-MM-DD",
    "analyzed_on": "YYYY-MM-DD",
}
```

plus `source_url(path, start=None, end=None)`, which returns
`https://github.com/pytorch/pytorch/blob/<commit>/<path>#L<start>-L<end>`.

### 7.4 Page registry

An ordered `PAGES` list, each entry with `slug`, `title`, `summary`, `sources` and `ready`.
The nav, index list and slug allowlist derive from it. Pages not yet ready show in the nav
and on the index without a link, marked "In progress".

### 7.5 Tests (`backend/tests/ml_models_docs_tests.py`, plus `app_tests.py` additions)

- The pin is well formed: the PyTorch repo, a `vX.Y.Z` tag, a 40-hex commit, ISO dates.
- `source_url` is pinned to the commit and formats line ranges.
- `/ml-models` and every ready page return 200; unknown and not-ready slugs return 404.
- Every ready page has a template, a summary and at least one source.
- Every GitHub link is pinned to `UPSTREAM.commit`; no `blob/main`.
- Every internal `/ml-models…` link resolves.
- Every ready topic page has at least two inline SVGs with `<title>` and `<desc>`, a table
  with the §6 columns, and a code snippet.
- No page loads a script or stylesheet from another origin.
- `torch` is not in either requirements file.

## 8. The daily Routine

A Routine ("rayaq.ca/ml-models — architecture reference agent") runs once a day. Each run:

1. Reads this spec and the progress file.
2. **Build phase**: builds the next queued page completely (§6), one page per run, in §5
   order, marks it `"ready": True`, and updates the progress file (queue, pin, deviations,
   open gaps, and the script and seed of any committed data).
3. **Maintenance phase** (once the queue is empty): checks whether a newer stable PyTorch
   release changed any file the pages link to. If one did, it updates the pin and the
   affected pages (line ranges included) in one commit and records it in the progress file;
   if not, it records "no relevant upstream change".
4. Before every commit: runs the full test suite, starts the app and curls `/ml-models` and
   every ready page after `/health` answers, checks for horizontal overflow at 390px in
   headless Chromium, then stops the app.
5. Pushes straight to `main` with `ml-models: <lowercase imperative>` commit subjects. No
   branches, pull requests, force-pushes or history rewrites.

## 9. Acceptance criteria

- [ ] `/ml-models` renders the model-family map and links to every ready page.
- [ ] Every §5 page exists, meets its "Must cover" column and §6, and is registered.
- [ ] Every PyTorch link is pinned to `UPSTREAM.commit` (tested).
- [ ] §7.5 tests exist and pass.
- [ ] No `torch` in requirements; offline data has its script and seed recorded.
- [ ] Mobile at 390px: no horizontal page scroll; diagrams scroll inside their container.
- [ ] The Routine has run at least once in maintenance mode.
