import re

from markupsafe import Markup, escape

import ml_models_docs

UPSTREAM = {
    "repo": "https://github.com/rayaq-siddiqui/rml",
    "commit": "13234ae977ad00839b7f68f919fd81540247fa7f",
    "commit_date": "2026-10-25",
    "version": "0.1.0",
    "license": "Apache-2.0",
    "analyzed_on": "2026-10-28",
}

GROUPS = [
    "Inference stack",
    "Foundations",
    "Learning",
    "Classical & retrieval",
    "LLM runtime",
    "Project",
]

MODULES = {
    "rml/core": [
        "allocator", "buffer_pool", "check", "dtype", "ops", "shape", "status", "strided",
        "tensor", "thread_pool",
    ],
    "rml/linalg": [
        "cholesky", "eigen", "gemm", "lu", "matmul", "matrix", "norms", "qr", "svd",
    ],
    "rml/random": ["distributions", "philox"],
    "rml/autograd": ["function", "grad_check", "ops", "variable"],
    "rml/nn": [
        "activation", "attention", "conv", "dropout", "embedding", "init", "linear", "module",
        "normalization", "recurrent", "transformer",
    ],
    "rml/losses": ["classification", "contrastive", "reduction", "regression", "variational"],
    "rml/optim": ["accumulation", "adam", "clip", "optimizer", "rmsprop", "schedule", "sgd"],
    "rml/data": ["dataset", "preprocessing", "split"],
    "rml/metrics": ["calibration", "classification", "inputs", "ranking", "regression"],
    "rml/classical": [
        "common", "decision_tree", "gradient_boosting", "kmeans", "knn", "linear_regression",
        "logistic_regression", "naive_bayes", "pca", "random_forest", "svm",
    ],
    "rml/retrieval": ["ivf", "similarity"],
    "rml/quant": ["blocks", "dequantize", "dot", "ggml_type"],
    "rml/io": ["checkpoint", "gguf", "mapped_file", "safetensors", "safetensors_model"],
    "rml/llm": [
        "attention", "chat_template", "config", "decoder", "generation", "gguf_tokenizer",
        "hf_tokenizer", "kernels", "kv_cache", "pretokenizer", "rope", "sampler", "speculative",
        "tokenizer", "unicode", "unicode_tables", "weight_source",
    ],
    "rml/graph": ["executor", "fusion", "graph", "kernels", "ops", "shape_inference"],
    "rml/copts": ["rml"],
}

EXAMPLES = [
    "causal_inference", "char_gpt", "cnn", "collaborative_filtering", "diffusion",
    "diffusion_unet", "distillation", "distributed", "dpo", "drift", "encoder", "finetune",
    "flow_matching", "gan", "gnn", "graph_run", "learning_to_rank", "mlp", "multimodal", "online_learning",
    "rag", "rl", "rml_chat", "rnn", "serving", "ssm", "time_series", "tiny_models", "tiny_net",
    "two_tower", "vae", "vit",
]

PAGES = [
    {
        "slug": "stack",
        "title": "The inference stack",
        "group": "Inference stack",
        "summary": "Where rml is headed: framework models exported into rml-graph, lowered to a "
        "fused kernel plan and benchmarked against PyTorch, JAX and TensorFlow, level by level.",
        "sources": [
            "docs/progress.md", "docs/graph_ir.md", "README.md", "docs/bench/frameworks.md",
            "rml/graph/fusion.h",
        ],
        "ready": True,
    },
    {
        "slug": "exporters",
        "title": "Exporters and the model zoo",
        "group": "Inference stack",
        "summary": "How tools/rml_export traces PyTorch, JAX and TensorFlow models into "
        "rml-graph, the passes it runs, the shared zoo, and the golden fixtures.",
        "sources": [
            "tools/rml_export", "tools/make_graph_fixtures.py", "rml/graph/golden_test.cc",
            "rml/graph/testdata", "rml/graph/cross_framework_test.cc",
            "tools/cross_framework_test.py", "tools/rml_infer_example.py",
            "tools/requirements-export.txt", "examples/tiny_net", "examples/tiny_models",
            "tools/make_tiny_net.py", "tools/make_tiny_models.py",
        ],
        "ready": True,
    },
    {
        "slug": "graph-ir",
        "title": "The rml-graph IR",
        "group": "Inference stack",
        "summary": "The exported model format: JSON values, constants and nodes over mmapped "
        "safetensors, the op set, loader validation and shape inference.",
        "sources": [
            "docs/graph_ir.md", "rml/graph/graph.h", "rml/graph/graph.cc",
            "rml/graph/shape_inference.h", "rml/graph/shape_inference.cc",
        ],
        "ready": True,
    },
    {
        "slug": "executor",
        "title": "Executing a graph",
        "group": "Inference stack",
        "summary": "The executor's order and value lifetimes, how each op maps onto rml "
        "kernels, the rml-graph-run tool, and the executor benchmark.",
        "sources": [
            "rml/graph/executor.h", "rml/graph/executor.cc", "rml/graph/ops.h",
            "rml/graph/ops.cc", "rml/graph/executor_benchmark.cc", "examples/graph_run",
        ],
        "ready": True,
    },
    {
        "slug": "lowering",
        "title": "Lowering and fast CPU",
        "group": "Inference stack",
        "summary": "The kernel-level layer below rml-graph: fused elementwise programs, "
        "threaded vectorized kernels, buffer reuse and SIMD GEMM, each tied to the gap it targets.",
        "sources": [
            "docs/progress.md", "docs/bench/frameworks.md", "rml/graph/fusion.h",
            "rml/graph/fusion.cc", "rml/graph/kernels.h", "rml/graph/kernels.cc",
            "rml/graph/kernels_benchmark.cc", "docs/kernels.md",
        ],
        "ready": True,
    },
    {
        "slug": "benchmarks",
        "title": "Benchmarks against the frameworks",
        "group": "Inference stack",
        "summary": "How each model is timed in PyTorch, JAX and TensorFlow, eager and "
        "compiled, and in rml, and what the published results show.",
        "sources": ["tools/bench_frameworks.py", "docs/bench/frameworks.md"],
        "ready": True,
    },
    {
        "slug": "tensors",
        "title": "Tensors and dtypes",
        "group": "Foundations",
        "summary": "DTypes and their storage, shapes and strides, broadcasting, the strided row "
        "walker, Tensor views versus copies, the f32 reference ops, and RML_CHECK.",
        "sources": [
            "rml/core/dtype.h", "rml/core/dtype.cc", "rml/core/shape.h", "rml/core/shape.cc",
            "rml/core/strided.h", "rml/core/tensor.h", "rml/core/tensor.cc", "rml/core/ops.h",
            "rml/core/ops.cc", "rml/core/check.h", "rml/core/check.cc",
        ],
        "ready": True,
    },
    {
        "slug": "runtime",
        "title": "Errors, memory and threads",
        "group": "Foundations",
        "summary": "Status and Expected instead of exceptions, aligned allocation with its "
        "counters, and the ThreadPool whose ParallelFor gives reproducible results.",
        "sources": [
            "rml/core/status.h", "rml/core/status.cc", "rml/core/allocator.h",
            "rml/core/allocator.cc", "rml/core/buffer_pool.h", "rml/core/buffer_pool.cc",
            "rml/core/thread_pool.h", "rml/core/thread_pool.cc", "docs/architecture.md",
        ],
        "ready": True,
    },
    {
        "slug": "linalg",
        "title": "Linear algebra",
        "group": "Foundations",
        "summary": "Matrix, matmul and the blocked GEMM kernel, and the LU, QR, Cholesky, "
        "eigen and SVD decompositions plus norms.",
        "sources": ["rml/linalg", "docs/kernels.md"],
        "ready": True,
    },
    {
        "slug": "random",
        "title": "Random numbers",
        "group": "Foundations",
        "summary": "The Philox counter-based generator and the distributions sampled from it.",
        "sources": ["rml/random"],
        "ready": True,
    },
    {
        "slug": "autograd",
        "title": "Autograd",
        "group": "Learning",
        "summary": "Variables, functions and the backward pass over a dynamic graph, the "
        "differentiable ops, and numerical gradient checking.",
        "sources": ["rml/autograd"],
        "ready": True,
    },
    {
        "slug": "nn",
        "title": "Neural network layers",
        "group": "Learning",
        "summary": "Module and every layer: linear, activations, initialization, convolution, "
        "embedding, normalization, dropout, recurrent, attention and transformer blocks.",
        "sources": ["rml/nn"],
        "ready": True,
    },
    {
        "slug": "training",
        "title": "Losses and optimizers",
        "group": "Learning",
        "summary": "Classification, regression, contrastive and variational losses, and SGD, "
        "Adam, RMSprop, schedules, clipping and gradient accumulation.",
        "sources": ["rml/losses", "rml/optim"],
        "ready": True,
    },
    {
        "slug": "data-metrics",
        "title": "Data and metrics",
        "group": "Learning",
        "summary": "Datasets, preprocessing and splits, and the classification, regression, "
        "ranking and calibration metrics.",
        "sources": ["rml/data", "rml/metrics"],
        "ready": True,
    },
    {
        "slug": "classical",
        "title": "Classical models",
        "group": "Classical & retrieval",
        "summary": "The fifteen classical estimators, from linear regression to gradient "
        "boosting, and the tests that hold them to scikit-learn fixtures.",
        "sources": ["rml/classical", "tools/make_sklearn_fixtures.py"],
        "ready": True,
    },
    {
        "slug": "retrieval",
        "title": "Retrieval",
        "group": "Classical & retrieval",
        "summary": "Similarity functions and the inverted-file (IVF) vector index.",
        "sources": ["rml/retrieval"],
        "ready": True,
    },
    {
        "slug": "quantization",
        "title": "Quantization",
        "group": "LLM runtime",
        "summary": "GGML block types, dequantization, and the quantized dot products the "
        "decoder runs on.",
        "sources": ["rml/quant", "tools/make_quant_fixtures.py"],
        "ready": True,
    },
    {
        "slug": "model-files",
        "title": "Model files",
        "group": "LLM runtime",
        "summary": "Memory-mapped files, safetensors, GGUF and checkpoints, and how weights "
        "stay mapped rather than copied.",
        "sources": ["rml/io"],
        "ready": True,
    },
    {
        "slug": "tokenizers",
        "title": "Tokenizers",
        "group": "LLM runtime",
        "summary": "The tokenizer interface, pretokenization and Unicode tables, Hugging Face "
        "and GGUF tokenizers, and chat templates.",
        "sources": [
            "rml/llm/tokenizer.h", "rml/llm/pretokenizer.h", "rml/llm/unicode.h",
            "rml/llm/unicode_tables.cc", "rml/llm/hf_tokenizer.h", "rml/llm/gguf_tokenizer.h",
            "rml/llm/chat_template.h", "tools/make_tokenizer_fixtures.py",
            "tools/make_pretokenizer_fixtures.py", "tools/make_unicode_tables.py",
        ],
        "ready": True,
    },
    {
        "slug": "decoder",
        "title": "The decoder",
        "group": "LLM runtime",
        "summary": "Config, weights, one layer's forward pass, attention and the KV cache, "
        "RoPE, mixture of experts, and the eight model families.",
        "sources": [
            "rml/llm/config.h", "rml/llm/weight_source.h", "rml/llm/decoder.h",
            "rml/llm/decoder.cc", "rml/llm/attention.h", "rml/llm/rope.h",
            "rml/llm/kv_cache.h", "rml/llm/kernels.h", "rml/llm/attention_benchmark.cc",
            "rml/llm/decoder_alloc_test.cc", "rml/llm/decoder_benchmark.cc",
            "rml/llm/real_model_test.cc", "rml/llm/config.cc", "rml/llm/weight_source.cc",
            "rml/llm/attention.cc", "rml/llm/rope.cc", "rml/llm/kv_cache.cc", "rml/llm/kernels.cc",
            "tools/make_llm_fixtures.py",
        ],
        "ready": True,
    },
    {
        "slug": "generation",
        "title": "Generation",
        "group": "LLM runtime",
        "summary": "Samplers, the generation loop, speculative decoding, the rml_chat example "
        "and the decode loop end to end.",
        "sources": [
            "rml/llm/sampler.h", "rml/llm/generation.h", "rml/llm/speculative.h",
            "examples/rml_chat", "docs/architecture.md", "rml/llm/sampler.cc",
            "rml/llm/generation.cc", "rml/llm/speculative.cc",
        ],
        "ready": True,
    },
    {
        "slug": "kernels",
        "title": "Kernels",
        "group": "Project",
        "summary": "What docs/kernels.md describes: the GEMM, quantized dot, attention and "
        "fused decoder kernels that exist, and the ones still planned.",
        "sources": [
            "docs/kernels.md", "rml/llm/kernels.h", "rml/linalg/gemm.h", "rml/quant/dot.h",
            "rml/llm/attention.h", "rml/graph/kernels.h", "rml/core/tensor.cc",
        ],
        "ready": True,
    },
    {
        "slug": "models-memory",
        "title": "Models and memory",
        "group": "Project",
        "summary": "Target models and the memory math behind them, and the status of each "
        "model family.",
        "sources": ["docs/models.md", "README.md", "tools/download_model.py"],
        "ready": True,
    },
    {
        "slug": "examples",
        "title": "Examples",
        "group": "Project",
        "summary": "Every example program, what it builds from the library, and the concept "
        "it demonstrates.",
        "sources": ["examples"],
        "ready": True,
    },
    {
        "slug": "testing",
        "title": "Build and testing",
        "group": "Project",
        "summary": "Bazel modules and copts, GoogleTest and Google Benchmark, golden LLM "
        "tests, the fixture tools, and CI.",
        "sources": [
            "MODULE.bazel", "rml/copts/rml.bzl", ".github/workflows/ci.yml",
            "tools/llm_reference.py", "tools/make_llm_fixtures.py",
            "tools/make_real_model_goldens.py",
        ],
        "ready": False,
    },
]

_HEADING = re.compile(r'<h([23]) id="([^"]+)"[^>]*>(.*?)</h\1>', re.S)
_TAG = re.compile(r"<[^>]+>")


def _pinned(url, start, end):
    if start is None:
        return url
    if end is None or end == start:
        return f"{url}#L{start}"
    return f"{url}#L{start}-L{end}"


def source_url(path, start=None, end=None):
    return _pinned(f"{UPSTREAM['repo']}/blob/{UPSTREAM['commit']}/{path}", start, end)


def tree_url(path=""):
    return f"{UPSTREAM['repo']}/tree/{UPSTREAM['commit']}/{path}".rstrip("/")


def ml_models_link(slug, text):
    if ml_models_docs.find_page(slug) is None:
        return escape(text)
    return Markup('<a href="/ml-models/{}">{}</a>').format(slug, text)


def page_link(slug, text, anchor=""):
    if find_page(slug) is None:
        return escape(text)
    return Markup('<a href="/rml/{}{}">{}</a>').format(slug, anchor, text)


def pages_for(module):
    return [
        page
        for page in PAGES
        if any(source == module or source.startswith(f"{module}/") for source in page["sources"])
    ]


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
        template = "rml/index.html"
    else:
        page = find_page(slug)
        if page is None:
            return None
        template = f"rml/{slug}.html"

    previous, following = _neighbours(slug)
    context = {
        "page": page,
        "pages": PAGES,
        "groups": GROUPS,
        "ready_slugs": {entry["slug"] for entry in ready_pages()},
        "upstream": UPSTREAM,
        "src": source_url,
        "tree": tree_url,
        "ml": ml_models_link,
        "link": page_link,
        "modules": MODULES,
        "pages_for": pages_for,
        "examples": EXAMPLES,
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
        "rml/base.html",
        intro=intro,
        content=body,
        toc=table_of_contents(body),
        **context,
    )
