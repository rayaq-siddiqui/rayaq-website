import re

UPSTREAM = {
    "repo": "https://github.com/pytorch/pytorch",
    "tag": "v2.14.1",
    "commit": "5c4886908584029761b579af026dcfb627c84070",
    "commit_date": "2026-09-29",
    "analyzed_on": "2026-10-08",
}

PAGES = [
    {
        "slug": "transformer",
        "title": "The Transformer",
        "summary": "The full encoder-decoder from Attention Is All You Need, block by block, and how nn.Transformer implements it.",
        "sources": [
            "torch/nn/modules/transformer.py",
            "torch/nn/modules/activation.py",
            "torch/nn/modules/normalization.py",
            "torch/nn/modules/sparse.py",
            "torch/nn/modules/linear.py",
        ],
        "ready": False,
    },
    {
        "slug": "attention",
        "title": "Attention",
        "summary": "Scaled dot-product and multi-head attention, masking, cross-attention, and the KV cache.",
        "sources": [
            "torch/nn/functional.py",
            "torch/nn/modules/activation.py",
            "torch/nn/attention/__init__.py",
            "torch/nn/attention/bias.py",
            "torch/nn/attention/flex_attention.py",
        ],
        "ready": False,
    },
    {
        "slug": "positional-encoding",
        "title": "Positional encoding",
        "summary": "How a model that sees a set learns order: sinusoidal, learned and rotary (RoPE) positions.",
        "sources": [
            "torch/nn/modules/sparse.py",
            "torch/nn/functional.py",
            "torch/nn/modules/transformer.py",
        ],
        "ready": False,
    },
    {
        "slug": "layernorm-and-residuals",
        "title": "LayerNorm and residuals",
        "summary": "The residual stream, LayerNorm and RMSNorm, pre-norm versus post-norm, and the feed-forward block.",
        "sources": [
            "torch/nn/modules/normalization.py",
            "torch/nn/functional.py",
            "torch/nn/modules/activation.py",
            "torch/nn/modules/dropout.py",
            "torch/nn/modules/transformer.py",
        ],
        "ready": False,
    },
    {
        "slug": "decoder-only-llm",
        "title": "Decoder-only LLMs",
        "summary": "The GPT-style stack: causal self-attention blocks, the LM head, generation, and a GPT-2-small parameter count.",
        "sources": [
            "torch/nn/modules/transformer.py",
            "torch/nn/functional.py",
            "torch/nn/modules/sparse.py",
            "torch/nn/modules/linear.py",
            "torch/nn/modules/loss.py",
        ],
        "ready": False,
    },
    {
        "slug": "encoder-only",
        "title": "Encoder-only models",
        "summary": "The BERT-style stack: bidirectional attention, padding masks, masked-language-model training and task heads.",
        "sources": [
            "torch/nn/modules/transformer.py",
            "torch/nn/modules/sparse.py",
            "torch/nn/modules/loss.py",
        ],
        "ready": False,
    },
    {
        "slug": "vision-transformer",
        "title": "Vision Transformer",
        "summary": "ViT: images as sequences of patches, patch embedding as a strided convolution, and the class token.",
        "sources": [
            "torch/nn/modules/conv.py",
            "torch/nn/modules/transformer.py",
            "torch/nn/modules/flatten.py",
            "torch/nn/modules/linear.py",
        ],
        "ready": False,
    },
    {
        "slug": "mixture-of-experts",
        "title": "Mixture of experts",
        "summary": "Routing each token to a few of many feed-forward experts: top-k gating, load balancing, total versus active parameters.",
        "sources": [
            "torch/nn/modules/container.py",
            "torch/nn/modules/linear.py",
            "torch/nn/functional.py",
        ],
        "ready": False,
    },
    {
        "slug": "diffusion-unet",
        "title": "Diffusion U-Net",
        "summary": "Denoising diffusion and the U-Net that predicts the noise: down and up paths, skips, timestep embeddings and attention.",
        "sources": [
            "torch/nn/modules/conv.py",
            "torch/nn/modules/normalization.py",
            "torch/nn/modules/upsampling.py",
            "torch/nn/modules/activation.py",
            "torch/nn/functional.py",
        ],
        "ready": False,
    },
    {
        "slug": "training-loop",
        "title": "The training loop",
        "summary": "Cross-entropy loss, AdamW, learning-rate warmup and decay, gradient clipping, and mixed precision.",
        "sources": [
            "torch/nn/modules/loss.py",
            "torch/nn/functional.py",
            "torch/optim/adamw.py",
            "torch/optim/adam.py",
            "torch/optim/optimizer.py",
            "torch/optim/lr_scheduler.py",
            "torch/amp/autocast_mode.py",
            "torch/amp/grad_scaler.py",
            "torch/nn/utils/clip_grad.py",
        ],
        "ready": False,
    },
]

_HEADING = re.compile(r'<h([23]) id="([^"]+)"[^>]*>(.*?)</h\1>', re.S)
_TAG = re.compile(r"<[^>]+>")


def source_url(path, start=None, end=None):
    url = f"{UPSTREAM['repo']}/blob/{UPSTREAM['commit']}/{path}"
    if start is None:
        return url
    if end is None or end == start:
        return f"{url}#L{start}"
    return f"{url}#L{start}-L{end}"


def ready_pages():
    return [page for page in PAGES if page["ready"]]


def find_page(slug):
    return next((page for page in ready_pages() if page["slug"] == slug), None)


def table_of_contents(html):
    return [
        {"level": int(level), "id": anchor, "text": _TAG.sub("", text).strip()}
        for level, anchor, text in _HEADING.findall(html)
    ]


def _neighbours(slug):
    pages = ready_pages()
    slugs = [page["slug"] for page in pages]
    if slug not in slugs:
        return None, None
    position = slugs.index(slug)
    previous = pages[position - 1] if position > 0 else None
    following = pages[position + 1] if position + 1 < len(pages) else None
    return previous, following


def render(slug, render_template):
    if slug is None:
        page = None
        template = "ml_models/index.html"
    else:
        page = find_page(slug)
        if page is None:
            return None
        template = f"ml_models/{slug}.html"

    previous, following = _neighbours(slug)
    context = {
        "page": page,
        "pages": PAGES,
        "ready_slugs": {entry["slug"] for entry in ready_pages()},
        "upstream": UPSTREAM,
        "src": source_url,
        "previous_page": previous,
        "next_page": following,
    }
    content = render_template(template, **context)
    intro, separator, body = content.partition("</header>")
    if not separator:
        intro, body = "", content
    else:
        intro += separator
    return render_template(
        "ml_models/base.html",
        intro=intro,
        content=body,
        toc=table_of_contents(body),
        **context,
    )
