import math
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
        "ready": True,
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


def _arxiv(paper_id):
    return f"https://arxiv.org/abs/{paper_id}"


UPCOMING_MODELS = [
    {
        "tier": "Classic machine learning",
        "blurb": "Small, fast, interpretable. Still the right first answer for most tabular data.",
        "models": [
            {"name": "Linear regression", "year": "1805", "idea": "Fit y = Xw + b by least squares; the closed form and gradient descent agree.", "paper": "Legendre, 1805 (least squares)", "url": None},
            {"name": "Logistic regression", "year": "1958", "idea": "A linear score through a sigmoid, trained with cross-entropy: a one-layer neural network.", "paper": "Cox, The Regression Analysis of Binary Sequences, 1958", "url": None},
            {"name": "Naive Bayes", "year": "1960s", "idea": "Bayes' rule with features assumed independent given the class; a strong text baseline.", "paper": "Maron, Automatic Indexing, 1961", "url": None},
            {"name": "k-nearest neighbours", "year": "1967", "idea": "Predict from the k closest training points; no training, all cost at query time.", "paper": "Cover and Hart, Nearest Neighbor Pattern Classification, 1967", "url": None},
            {"name": "k-means and PCA", "year": "1901/1982", "idea": "Unsupervised workhorses: cluster by nearest centroid; project onto directions of most variance.", "paper": "Lloyd, Least Squares Quantization in PCM, 1982; Pearson, 1901", "url": None},
            {"name": "Support vector machines", "year": "1995", "idea": "The maximum-margin separator, with kernels for non-linear boundaries.", "paper": "Cortes and Vapnik, Support-Vector Networks, 1995", "url": None},
            {"name": "Decision trees and random forests", "year": "1984/2001", "idea": "Recursive splits on features; average many decorrelated trees to cut variance.", "paper": "Breiman, Random Forests, 2001", "url": None},
            {"name": "Gradient-boosted trees (XGBoost, LightGBM)", "year": "2016", "idea": "Add trees one at a time, each fitting the previous ensemble's gradient. Still state of the art on tabular data.", "paper": "Chen and Guestrin, XGBoost, 2016", "url": _arxiv("1603.02754")},
        ],
    },
    {
        "tier": "Deep learning foundations",
        "blurb": "The building blocks every modern model is assembled from.",
        "models": [
            {"name": "Multilayer perceptron", "year": "1986", "idea": "Stacked linear layers with non-linearities, trained by backpropagation.", "paper": "Rumelhart, Hinton and Williams, Learning Representations by Back-Propagating Errors, 1986", "url": None},
            {"name": "CNNs: LeNet, AlexNet, ResNet", "year": "1998-2015", "idea": "Convolutions share weights across space; residual connections make very deep networks trainable.", "paper": "He et al., Deep Residual Learning for Image Recognition, 2015", "url": _arxiv("1512.03385")},
            {"name": "RNN, LSTM and GRU", "year": "1997/2014", "idea": "Read a sequence one step at a time, carrying a hidden state; gates fix vanishing gradients.", "paper": "Hochreiter and Schmidhuber, Long Short-Term Memory, 1997", "url": None},
            {"name": "word2vec", "year": "2013", "idea": "Learn word vectors by predicting neighbours; the ancestor of every embedding table.", "paper": "Mikolov et al., Efficient Estimation of Word Representations in Vector Space, 2013", "url": _arxiv("1301.3781")},
            {"name": "Seq2seq with attention", "year": "2014", "idea": "An encoder RNN, a decoder RNN, and attention over the encoder states: the Transformer's direct ancestor.", "paper": "Bahdanau, Cho and Bengio, Neural Machine Translation by Jointly Learning to Align and Translate, 2014", "url": _arxiv("1409.0473")},
            {"name": "Autoencoders and VAEs", "year": "2013", "idea": "Compress to a latent code and reconstruct; the VAE makes the latent space a distribution you can sample.", "paper": "Kingma and Welling, Auto-Encoding Variational Bayes, 2013", "url": _arxiv("1312.6114")},
            {"name": "GANs", "year": "2014", "idea": "A generator and a discriminator trained against each other.", "paper": "Goodfellow et al., Generative Adversarial Networks, 2014", "url": _arxiv("1406.2661")},
            {"name": "U-Net", "year": "2015", "idea": "A convolutional encoder-decoder with skip connections at every resolution; later the backbone of diffusion.", "paper": "Ronneberger, Fischer and Brox, U-Net, 2015", "url": _arxiv("1505.04597"), "slug": "diffusion-unet"},
        ],
    },
    {
        "tier": "The transformer era",
        "blurb": "Attention replaces recurrence, and scale becomes the main lever.",
        "models": [
            {"name": "Transformer", "year": "2017", "idea": "Encoder-decoder built only from attention and feed-forward blocks.", "paper": "Vaswani et al., Attention Is All You Need, 2017", "url": _arxiv("1706.03762"), "slug": "transformer"},
            {"name": "BERT", "year": "2018", "idea": "Encoder-only, bidirectional, pre-trained by filling in masked tokens.", "paper": "Devlin et al., BERT, 2018", "url": _arxiv("1810.04805"), "slug": "encoder-only"},
            {"name": "GPT-2 and GPT-3", "year": "2019/2020", "idea": "Decoder-only next-token prediction; at scale it learns tasks from the prompt alone.", "paper": "Brown et al., Language Models are Few-Shot Learners, 2020", "url": _arxiv("2005.14165"), "slug": "decoder-only-llm"},
            {"name": "T5", "year": "2019", "idea": "Every NLP task cast as text-to-text on one encoder-decoder.", "paper": "Raffel et al., Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer, 2019", "url": _arxiv("1910.10683")},
            {"name": "Vision Transformer (ViT)", "year": "2020", "idea": "An image is a sequence of 16x16 patches fed to a plain encoder.", "paper": "Dosovitskiy et al., An Image is Worth 16x16 Words, 2020", "url": _arxiv("2010.11929"), "slug": "vision-transformer"},
            {"name": "DDPM and latent diffusion", "year": "2020/2021", "idea": "Generate by learning to undo noise step by step; do it in a VAE's latent space to make it cheap.", "paper": "Rombach et al., High-Resolution Image Synthesis with Latent Diffusion Models, 2021", "url": _arxiv("2112.10752"), "slug": "diffusion-unet"},
            {"name": "CLIP", "year": "2021", "idea": "An image encoder and a text encoder trained so matching pairs have similar embeddings.", "paper": "Radford et al., Learning Transferable Visual Models From Natural Language Supervision, 2021", "url": _arxiv("2103.00020")},
            {"name": "Chinchilla scaling", "year": "2022", "idea": "For a fixed compute budget, grow parameters and training tokens together (about 20 tokens per parameter).", "paper": "Hoffmann et al., Training Compute-Optimal Large Language Models, 2022", "url": _arxiv("2203.15556")},
            {"name": "InstructGPT (RLHF)", "year": "2022", "idea": "Fine-tune on demonstrations, then on human preference rankings through a reward model.", "paper": "Ouyang et al., Training Language Models to Follow Instructions with Human Feedback, 2022", "url": _arxiv("2203.02155")},
            {"name": "Whisper", "year": "2022", "idea": "An encoder-decoder transformer over log-Mel spectrograms, trained on 680,000 hours of audio.", "paper": "Radford et al., Robust Speech Recognition via Large-Scale Weak Supervision, 2022", "url": _arxiv("2212.04356")},
        ],
    },
    {
        "tier": "Current state of the art",
        "blurb": "Open-weight models with published architectures. Closed frontier models don't publish theirs, so these pages don't guess at them.",
        "models": [
            {"name": "Llama 3", "year": "2024", "idea": "The reference dense decoder: RMSNorm, SwiGLU, rotary positions, grouped-query attention.", "paper": "Llama Team, The Llama 3 Herd of Models, 2024", "url": _arxiv("2407.21783"), "slug": "decoder-only-llm"},
            {"name": "Mixtral 8x7B", "year": "2024", "idea": "Sparse mixture of experts: each token goes to 2 of 8 feed-forward experts.", "paper": "Jiang et al., Mixtral of Experts, 2024", "url": _arxiv("2401.04088"), "slug": "mixture-of-experts"},
            {"name": "DeepSeek-V3", "year": "2024", "idea": "671B total, 37B active parameters per token; multi-head latent attention shrinks the KV cache.", "paper": "DeepSeek-AI, DeepSeek-V3 Technical Report, 2024", "url": _arxiv("2412.19437"), "slug": "mixture-of-experts"},
            {"name": "DeepSeek-R1", "year": "2025", "idea": "Reasoning learned with large-scale reinforcement learning on verifiable rewards.", "paper": "DeepSeek-AI, DeepSeek-R1, 2025", "url": _arxiv("2501.12948")},
            {"name": "Qwen3", "year": "2025", "idea": "Dense and MoE models with switchable thinking and non-thinking modes.", "paper": "Qwen Team, Qwen3 Technical Report, 2025", "url": _arxiv("2505.09388")},
            {"name": "Gemma 3", "year": "2025", "idea": "Interleaves local sliding-window and global attention layers to keep long-context memory small.", "paper": "Gemma Team, Gemma 3 Technical Report, 2025", "url": _arxiv("2503.19786")},
            {"name": "Diffusion transformers (DiT, SD3)", "year": "2022/2024", "idea": "Replace the U-Net with a transformer over latent patches; SD3 trains it with rectified flow.", "paper": "Esser et al., Scaling Rectified Flow Transformers for High-Resolution Image Synthesis, 2024", "url": _arxiv("2403.03206")},
            {"name": "Segment Anything (SAM)", "year": "2023", "idea": "A promptable segmentation model: ViT image encoder, prompt encoder, light mask decoder.", "paper": "Kirillov et al., Segment Anything, 2023", "url": _arxiv("2304.02643")},
            {"name": "Mamba", "year": "2023", "idea": "A selective state-space model: linear-time sequence mixing, the main alternative to attention.", "paper": "Gu and Dao, Mamba, 2023", "url": _arxiv("2312.00752")},
        ],
    },
]

ATTENTION_EXAMPLE = {
    "tokens": ["the", "cat", "sat", "down"],
    "queries": [[0, 1], [1, 1], [2, 0], [1, 2]],
    "keys": [[0, 1], [2, 0], [1, 1], [0, 2]],
    "values": [[1, 0], [0, 1], [1, 1], [0, 0]],
}

TRANSFORMER_PRESETS = [
    {"name": "nn.Transformer() defaults", "d_model": 512, "nhead": 8, "encoder_layers": 6, "decoder_layers": 6, "dim_feedforward": 2048},
    {"name": "Paper, big", "d_model": 1024, "nhead": 16, "encoder_layers": 6, "decoder_layers": 6, "dim_feedforward": 4096},
    {"name": "Tiny (toy)", "d_model": 64, "nhead": 4, "encoder_layers": 2, "decoder_layers": 2, "dim_feedforward": 256},
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


def attention_weights(example, causal=False, scaled=True):
    width = len(example["queries"][0])
    scale = 1 / math.sqrt(width) if scaled else 1
    scores, weights, outputs = [], [], []
    for row, query in enumerate(example["queries"]):
        row_scores = [
            None if causal and column > row else sum(q * k for q, k in zip(query, key)) * scale
            for column, key in enumerate(example["keys"])
        ]
        allowed = [score for score in row_scores if score is not None]
        top = max(allowed)
        exps = [0.0 if score is None else math.exp(score - top) for score in row_scores]
        total = sum(exps)
        row_weights = [value / total for value in exps]
        scores.append(row_scores)
        weights.append(row_weights)
        outputs.append([
            sum(weight * value[i] for weight, value in zip(row_weights, example["values"]))
            for i in range(len(example["values"][0]))
        ])
    return {"scores": scores, "weights": weights, "outputs": outputs}


def transformer_param_count(d_model, encoder_layers, decoder_layers, dim_feedforward, nhead=None):
    attention = 4 * d_model * d_model + 4 * d_model
    feed_forward = 2 * d_model * dim_feedforward + dim_feedforward + d_model
    layer_norm = 2 * d_model
    encoder_layer = attention + feed_forward + 2 * layer_norm
    decoder_layer = 2 * attention + feed_forward + 3 * layer_norm
    encoder = encoder_layers * encoder_layer + layer_norm
    decoder = decoder_layers * decoder_layer + layer_norm
    return {
        "attention": attention,
        "feed_forward": feed_forward,
        "layer_norm": layer_norm,
        "encoder_layer": encoder_layer,
        "decoder_layer": decoder_layer,
        "encoder": encoder,
        "decoder": decoder,
        "total": encoder + decoder,
    }


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
        "upcoming": UPCOMING_MODELS,
        "attention_example": ATTENTION_EXAMPLE,
        "attention_weights": attention_weights,
        "presets": TRANSFORMER_PRESETS,
        "param_count": transformer_param_count,
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
