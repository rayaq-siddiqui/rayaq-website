import functools
import hashlib
import heapq
import itertools
import math
import random
import re
import statistics
import struct

PINS = {
    "pytorch": {
        "name": "PyTorch",
        "repo": "https://github.com/pytorch/pytorch",
        "tag": "v2.14.1",
        "commit": "5c4886908584029761b579af026dcfb627c84070",
        "commit_date": "2026-09-29",
        "analyzed_on": "2026-10-08",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE",
    },
    "sklearn": {
        "name": "scikit-learn",
        "repo": "https://github.com/scikit-learn/scikit-learn",
        "tag": "1.9.1",
        "commit": "866c0f51e7560ef0303cbcc5f159df5382ea9e3f",
        "commit_date": "2026-09-10",
        "analyzed_on": "2026-10-08",
        "license": "BSD-3-Clause",
        "license_path": "COPYING",
    },
    "xgboost": {
        "name": "XGBoost",
        "repo": "https://github.com/dmlc/xgboost",
        "tag": "v3.4.2",
        "commit": "fdf0888bedddbd444d72994d845c59b3ca182c5b",
        "commit_date": "2026-09-15",
        "analyzed_on": "2026-10-08",
        "license": "Apache-2.0",
        "license_path": "LICENSE",
    },
}

UPSTREAM = PINS["pytorch"]

AREAS = [
    {
        "slug": "foundations",
        "title": "Mathematical foundations",
        "summary": "Vectors, matrices, dot products, gradients, the chain rule, probability, distributions, expectation, Bayes' rule, entropy.",
    },
    {
        "slug": "core-ml",
        "title": "Core ML concepts",
        "summary": "Supervised, unsupervised and self-supervised learning; losses; generalization; bias–variance; overfitting; regularization.",
    },
    {
        "slug": "data-evaluation",
        "title": "Data and evaluation",
        "summary": "Splits, leakage, preprocessing, missing data, imbalance, cross-validation, metrics, calibration, uncertainty.",
    },
    {
        "slug": "classical-ml",
        "title": "Classical ML",
        "summary": "Linear and logistic regression, decision trees, random forests, gradient boosting, SVMs, nearest neighbors, clustering, PCA.",
    },
    {
        "slug": "neural-networks",
        "title": "Neural network fundamentals",
        "summary": "Layers, activations, backprop, computation graphs, initialization, normalization, optimizers, LR schedules, the training loop.",
    },
    {
        "slug": "architectures",
        "title": "Model architectures",
        "summary": "CNNs, RNNs/LSTMs, Transformers, autoencoders, GNNs, mixture of experts, state-space models, vision transformers.",
    },
    {
        "slug": "generative",
        "title": "Generative modeling",
        "summary": "Autoregressive models, VAEs, GANs, diffusion, flow matching.",
    },
    {
        "slug": "language-models",
        "title": "Language models",
        "summary": "Tokenization, embeddings, positional encoding, attention, encoder and decoder LMs, pretraining, fine-tuning, preference optimization, decoding, KV caching.",
    },
    {
        "slug": "retrieval",
        "title": "Retrieval and recommendation",
        "summary": "Similarity search, vector indexes, ranking, collaborative filtering, two-tower models, RAG.",
    },
    {
        "slug": "training-systems",
        "title": "Training systems",
        "summary": "GPU execution, precision, batching, distributed training, gradient accumulation, checkpointing, profiling.",
    },
    {
        "slug": "inference",
        "title": "Inference and deployment",
        "summary": "Quantization, distillation, serving, latency and throughput, monitoring and drift, reproducibility.",
    },
    {
        "slug": "specialized",
        "title": "Specialized learning",
        "summary": "Reinforcement learning, time series, causal inference, online learning, multimodal models.",
    },
]

PAGES = [
    {
        "slug": "tensors-and-shapes",
        "title": "Tensors, shapes and broadcasting",
        "area": "foundations",
        "level": "intro",
        "summary": "What a tensor is, how shapes, strides and views work, and the broadcasting rules every model relies on.",
        "prerequisites": [],
        "sources": [
            "pytorch:torch/_tensor.py",
            "pytorch:torch/_torch_docs.py",
            "pytorch:torch/functional.py",
        ],
        "ready": True,
    },
    {
        "slug": "vectors-and-dot-products",
        "title": "Vectors and dot products",
        "area": "foundations",
        "level": "intro",
        "summary": "Vectors, norms and the dot product as similarity: the operation underneath attention and retrieval.",
        "prerequisites": ["tensors-and-shapes"],
        "sources": [
            "pytorch:torch/_torch_docs.py",
            "pytorch:torch/nn/modules/distance.py",
        ],
        "ready": True,
    },
    {
        "slug": "matrix-multiplication",
        "title": "Matrices and matrix multiplication",
        "area": "foundations",
        "level": "intro",
        "summary": "Matrix multiplication as many dot products, its shape rules, batched matmul, and how to count its FLOPs.",
        "prerequisites": ["vectors-and-dot-products"],
        "sources": [
            "pytorch:torch/_torch_docs.py",
            "pytorch:torch/functional.py",
            "pytorch:torch/nn/modules/linear.py",
        ],
        "ready": True,
    },
    {
        "slug": "linear-algebra-toolkit",
        "title": "Eigenvectors, SVD and low rank",
        "area": "foundations",
        "level": "core",
        "summary": "Eigenvectors, the SVD and low-rank approximation, and where they show up in ML.",
        "prerequisites": ["matrix-multiplication"],
        "sources": [
            "pytorch:torch/linalg/__init__.py",
            "pytorch:torch/_lowrank.py",
        ],
        "ready": True,
    },
    {
        "slug": "derivatives-and-gradients",
        "title": "Derivatives and gradients",
        "area": "foundations",
        "level": "intro",
        "summary": "Derivatives, partial derivatives and the gradient, with gradient descent worked step by step.",
        "prerequisites": ["vectors-and-dot-products"],
        "sources": [
            "pytorch:torch/autograd/__init__.py",
            "pytorch:torch/_tensor.py",
        ],
        "ready": True,
    },
    {
        "slug": "chain-rule",
        "title": "The chain rule",
        "area": "foundations",
        "level": "intro",
        "summary": "The chain rule from scalars to Jacobians, and why reverse mode is how ML computes gradients.",
        "prerequisites": ["derivatives-and-gradients", "matrix-multiplication"],
        "sources": [
            "pytorch:torch/autograd/function.py",
            "pytorch:torch/autograd/__init__.py",
        ],
        "ready": True,
    },
    {
        "slug": "probability-and-distributions",
        "title": "Probability and distributions",
        "area": "foundations",
        "level": "intro",
        "summary": "Random variables, the common distributions, and conditional and joint probability.",
        "prerequisites": [],
        "sources": [
            "pytorch:torch/distributions/normal.py",
            "pytorch:torch/distributions/categorical.py",
            "pytorch:torch/distributions/bernoulli.py",
        ],
        "ready": True,
    },
    {
        "slug": "expectation-and-variance",
        "title": "Expectation, variance and sampling",
        "area": "foundations",
        "level": "intro",
        "summary": "Expectation, variance and Monte Carlo estimates, and why minibatch gradients are noisy but unbiased.",
        "prerequisites": ["probability-and-distributions"],
        "sources": [
            "pytorch:torch/random.py",
            "pytorch:torch/distributions/normal.py",
        ],
        "ready": True,
    },
    {
        "slug": "bayes-rule",
        "title": "Bayes' rule and likelihood",
        "area": "foundations",
        "level": "core",
        "summary": "Bayes' rule, likelihood, maximum likelihood and MAP estimation, with priors as regularizers.",
        "prerequisites": ["probability-and-distributions"],
        "sources": [
            "pytorch:torch/distributions/distribution.py",
            "sklearn:sklearn/naive_bayes.py",
        ],
        "ready": True,
    },
    {
        "slug": "entropy-and-kl",
        "title": "Entropy, cross-entropy and KL divergence",
        "area": "foundations",
        "level": "core",
        "summary": "Entropy, cross-entropy, KL divergence and perplexity, and why cross-entropy is the classification loss.",
        "prerequisites": ["probability-and-distributions", "expectation-and-variance"],
        "sources": [
            "pytorch:torch/distributions/kl.py",
            "pytorch:torch/nn/modules/loss.py",
            "pytorch:torch/nn/functional.py",
        ],
        "ready": True,
    },
    {
        "slug": "learning-paradigms",
        "title": "Supervised, unsupervised and self-supervised learning",
        "area": "core-ml",
        "level": "intro",
        "summary": "Supervised, unsupervised and self-supervised learning, and what the label is in each.",
        "prerequisites": [],
        "sources": [
            "sklearn:sklearn/base.py",
            "sklearn:sklearn/cluster/_kmeans.py",
            "pytorch:torch/nn/modules/loss.py",
        ],
        "ready": True,
    },
    {
        "slug": "loss-functions",
        "title": "Loss functions",
        "area": "core-ml",
        "level": "intro",
        "summary": "The common losses as negative log-likelihoods, and how to choose one.",
        "prerequisites": ["entropy-and-kl"],
        "sources": [
            "pytorch:torch/nn/modules/loss.py",
            "pytorch:torch/nn/functional.py",
        ],
        "ready": True,
    },
    {
        "slug": "generalization",
        "title": "Generalization",
        "area": "core-ml",
        "level": "intro",
        "summary": "Why a model that fits its training data may still fail, and what makes it generalize.",
        "prerequisites": ["learning-paradigms", "loss-functions"],
        "sources": [
            "sklearn:sklearn/model_selection/_split.py",
            "sklearn:sklearn/model_selection/_validation.py",
        ],
        "ready": True,
    },
    {
        "slug": "bias-variance",
        "title": "The bias–variance tradeoff",
        "area": "core-ml",
        "level": "core",
        "summary": "The bias–variance decomposition, derived, with learning and validation curves.",
        "prerequisites": ["generalization", "expectation-and-variance"],
        "sources": [
            "sklearn:sklearn/model_selection/_validation.py",
        ],
        "ready": True,
    },
    {
        "slug": "overfitting",
        "title": "Overfitting and underfitting",
        "area": "core-ml",
        "level": "intro",
        "summary": "Diagnosing overfitting and underfitting from curves, and the remedies for each.",
        "prerequisites": ["generalization"],
        "sources": [
            "sklearn:sklearn/model_selection/_validation.py",
            "sklearn:sklearn/tree/_classes.py",
        ],
        "ready": True,
    },
    {
        "slug": "regularization",
        "title": "Regularization",
        "area": "core-ml",
        "level": "core",
        "summary": "L1, L2, dropout, early stopping and augmentation: the ways to trade fit for generalization.",
        "prerequisites": ["overfitting", "loss-functions"],
        "sources": [
            "sklearn:sklearn/linear_model/_ridge.py",
            "sklearn:sklearn/linear_model/_coordinate_descent.py",
            "pytorch:torch/nn/modules/dropout.py",
            "pytorch:torch/optim/adamw.py",
        ],
        "ready": True,
    },
    {
        "slug": "data-splits",
        "title": "Train, validation and test splits",
        "area": "data-evaluation",
        "level": "intro",
        "summary": "Train, validation and test splits, and when a random split gives the wrong answer.",
        "prerequisites": ["generalization"],
        "sources": [
            "sklearn:sklearn/model_selection/_split.py",
        ],
        "ready": True,
    },
    {
        "slug": "data-leakage",
        "title": "Data leakage",
        "area": "data-evaluation",
        "level": "core",
        "summary": "How information leaks from test to train, with concrete cases and a checklist to prevent it.",
        "prerequisites": ["data-splits", "preprocessing"],
        "sources": [
            "sklearn:sklearn/pipeline.py",
            "sklearn:sklearn/model_selection/_split.py",
        ],
        "ready": True,
    },
    {
        "slug": "preprocessing",
        "title": "Preprocessing and feature scaling",
        "area": "data-evaluation",
        "level": "intro",
        "summary": "Scaling, encoding and transforming features, and which models care.",
        "prerequisites": ["tensors-and-shapes"],
        "sources": [
            "sklearn:sklearn/preprocessing/_data.py",
            "sklearn:sklearn/preprocessing/_encoders.py",
        ],
        "ready": True,
    },
    {
        "slug": "missing-data",
        "title": "Missing data",
        "area": "data-evaluation",
        "level": "core",
        "summary": "Why values go missing, the imputation strategies, and how boosted trees handle missing values natively.",
        "prerequisites": ["preprocessing"],
        "sources": [
            "sklearn:sklearn/impute/_base.py",
            "sklearn:sklearn/impute/_iterative.py",
            "xgboost:src/tree/hist/evaluate_splits.h",
        ],
        "ready": True,
    },
    {
        "slug": "class-imbalance",
        "title": "Class imbalance",
        "area": "data-evaluation",
        "level": "core",
        "summary": "Why accuracy misleads on rare classes, and the weighting, resampling and threshold fixes.",
        "prerequisites": ["classification-metrics"],
        "sources": [
            "sklearn:sklearn/utils/class_weight.py",
            "pytorch:torch/nn/modules/loss.py",
        ],
        "ready": True,
    },
    {
        "slug": "cross-validation",
        "title": "Cross-validation",
        "area": "data-evaluation",
        "level": "core",
        "summary": "k-fold and its stratified, grouped and time-series variants, and nested CV for model selection.",
        "prerequisites": ["data-splits"],
        "sources": [
            "sklearn:sklearn/model_selection/_split.py",
            "sklearn:sklearn/model_selection/_validation.py",
        ],
        "ready": True,
    },
    {
        "slug": "classification-metrics",
        "title": "Classification metrics",
        "area": "data-evaluation",
        "level": "intro",
        "summary": "The confusion matrix, precision, recall, F1, ROC and PR curves, and choosing a threshold.",
        "prerequisites": ["data-splits"],
        "sources": [
            "sklearn:sklearn/metrics/_classification.py",
            "sklearn:sklearn/metrics/_ranking.py",
        ],
        "ready": True,
    },
    {
        "slug": "regression-metrics",
        "title": "Regression metrics",
        "area": "data-evaluation",
        "level": "intro",
        "summary": "MSE, MAE, R² and friends, and how to match the metric to the decision.",
        "prerequisites": ["loss-functions"],
        "sources": [
            "sklearn:sklearn/metrics/_regression.py",
        ],
        "ready": True,
    },
    {
        "slug": "calibration",
        "title": "Calibration",
        "area": "data-evaluation",
        "level": "core",
        "summary": "When a predicted probability means what it says, and how to fix it when it doesn't.",
        "prerequisites": ["classification-metrics"],
        "sources": [
            "sklearn:sklearn/calibration.py",
            "sklearn:sklearn/metrics/_classification.py",
        ],
        "ready": True,
    },
    {
        "slug": "uncertainty",
        "title": "Uncertainty",
        "area": "data-evaluation",
        "level": "advanced",
        "summary": "Aleatoric and epistemic uncertainty, ensembles, and conformal prediction with guaranteed coverage.",
        "prerequisites": ["calibration", "bayes-rule"],
        "sources": [
            "sklearn:sklearn/ensemble/_bagging.py",
            "pytorch:torch/nn/modules/dropout.py",
        ],
        "ready": True,
    },
    {
        "slug": "linear-regression",
        "title": "Linear regression",
        "area": "classical-ml",
        "level": "intro",
        "summary": "Least squares from the normal equations and from gradient descent, plus ridge and lasso.",
        "prerequisites": ["matrix-multiplication", "loss-functions"],
        "sources": [
            "sklearn:sklearn/linear_model/_base.py",
            "sklearn:sklearn/linear_model/_ridge.py",
        ],
        "ready": True,
    },
    {
        "slug": "logistic-regression",
        "title": "Logistic regression",
        "area": "classical-ml",
        "level": "intro",
        "summary": "Log-odds, the sigmoid and the cross-entropy loss: classification as one linear layer.",
        "prerequisites": ["linear-regression", "entropy-and-kl"],
        "sources": [
            "sklearn:sklearn/linear_model/_logistic.py",
            "pytorch:torch/nn/modules/linear.py",
        ],
        "ready": True,
    },
    {
        "slug": "decision-trees",
        "title": "Decision trees",
        "area": "classical-ml",
        "level": "intro",
        "summary": "Recursive splitting by Gini or entropy, worked on a toy dataset, and how to stop a tree overfitting.",
        "prerequisites": ["classification-metrics"],
        "sources": [
            "sklearn:sklearn/tree/_classes.py",
            "sklearn:sklearn/tree/_criterion.pyx",
            "sklearn:sklearn/tree/_splitter.pyx",
        ],
        "ready": True,
    },
    {
        "slug": "random-forests",
        "title": "Random forests",
        "area": "classical-ml",
        "level": "core",
        "summary": "Bagging and feature subsampling: many decorrelated trees averaged to cut variance.",
        "prerequisites": ["decision-trees", "bias-variance"],
        "sources": [
            "sklearn:sklearn/ensemble/_forest.py",
            "sklearn:sklearn/ensemble/_bagging.py",
        ],
        "ready": True,
    },
    {
        "slug": "gradient-boosting",
        "title": "Gradient boosting",
        "area": "classical-ml",
        "level": "core",
        "summary": "Boosting as gradient descent in function space, and XGBoost's second-order split gain, derived.",
        "prerequisites": ["decision-trees", "derivatives-and-gradients"],
        "sources": [
            "sklearn:sklearn/ensemble/_gb.py",
            "sklearn:sklearn/ensemble/_hist_gradient_boosting/gradient_boosting.py",
            "xgboost:src/tree/updater_quantile_hist.cc",
            "xgboost:src/tree/hist/evaluate_splits.h",
            "xgboost:python-package/xgboost/training.py",
        ],
        "ready": True,
    },
    {
        "slug": "support-vector-machines",
        "title": "Support vector machines",
        "area": "classical-ml",
        "level": "core",
        "summary": "The maximum-margin classifier, the hinge loss, and kernels.",
        "prerequisites": ["logistic-regression", "vectors-and-dot-products"],
        "sources": [
            "sklearn:sklearn/svm/_classes.py",
            "sklearn:sklearn/svm/_base.py",
        ],
        "ready": True,
    },
    {
        "slug": "nearest-neighbors",
        "title": "Nearest neighbors",
        "area": "classical-ml",
        "level": "intro",
        "summary": "Predicting from the closest training points, distance metrics, and the curse of dimensionality.",
        "prerequisites": ["vectors-and-dot-products", "preprocessing"],
        "sources": [
            "sklearn:sklearn/neighbors/_classification.py",
            "sklearn:sklearn/neighbors/_unsupervised.py",
            "sklearn:sklearn/neighbors/_ball_tree.pyx.tp",
        ],
        "ready": True,
    },
    {
        "slug": "clustering",
        "title": "Clustering",
        "area": "classical-ml",
        "level": "intro",
        "summary": "k-means, DBSCAN and Gaussian mixtures, and how to judge a clustering.",
        "prerequisites": ["nearest-neighbors"],
        "sources": [
            "sklearn:sklearn/cluster/_kmeans.py",
            "sklearn:sklearn/cluster/_dbscan.py",
            "sklearn:sklearn/mixture/_gaussian_mixture.py",
        ],
        "ready": True,
    },
    {
        "slug": "pca",
        "title": "Principal component analysis",
        "area": "classical-ml",
        "level": "core",
        "summary": "Principal components via the SVD, explained variance, and nonlinear alternatives.",
        "prerequisites": ["linear-algebra-toolkit", "preprocessing"],
        "sources": [
            "sklearn:sklearn/decomposition/_pca.py",
            "pytorch:torch/_lowrank.py",
        ],
        "ready": False,
    },
    {
        "slug": "neurons-and-layers",
        "title": "Neurons, layers and the MLP",
        "area": "neural-networks",
        "level": "intro",
        "summary": "From one neuron to a multilayer perceptron, and how nn.Module builds one.",
        "prerequisites": ["matrix-multiplication", "logistic-regression"],
        "sources": [
            "pytorch:torch/nn/modules/linear.py",
            "pytorch:torch/nn/modules/container.py",
            "pytorch:torch/nn/modules/module.py",
        ],
        "ready": True,
    },
    {
        "slug": "activation-functions",
        "title": "Activation functions",
        "area": "neural-networks",
        "level": "intro",
        "summary": "ReLU, GELU, SiLU, gated units and the rest, with their shapes and derivatives.",
        "prerequisites": ["neurons-and-layers"],
        "sources": [
            "pytorch:torch/nn/modules/activation.py",
            "pytorch:torch/nn/functional.py",
        ],
        "ready": True,
    },
    {
        "slug": "backpropagation",
        "title": "Backpropagation",
        "area": "neural-networks",
        "level": "core",
        "summary": "The backward pass through a two-layer network, with every number shown.",
        "prerequisites": ["chain-rule", "neurons-and-layers"],
        "sources": [
            "pytorch:torch/autograd/__init__.py",
            "pytorch:torch/autograd/function.py",
        ],
        "ready": True,
    },
    {
        "slug": "computation-graphs",
        "title": "Computation graphs and autograd",
        "area": "neural-networks",
        "level": "core",
        "summary": "The graph autograd records, how backward walks it, and how to control it.",
        "prerequisites": ["backpropagation"],
        "sources": [
            "pytorch:torch/autograd/graph.py",
            "pytorch:torch/autograd/function.py",
            "pytorch:torch/_tensor.py",
        ],
        "ready": True,
    },
    {
        "slug": "initialization",
        "title": "Weight initialization",
        "area": "neural-networks",
        "level": "core",
        "summary": "Why weight scale matters, derived, and the Xavier and Kaiming schemes PyTorch uses.",
        "prerequisites": ["backpropagation", "expectation-and-variance"],
        "sources": [
            "pytorch:torch/nn/init.py",
            "pytorch:torch/nn/modules/linear.py",
        ],
        "ready": True,
    },
    {
        "slug": "layernorm-and-residuals",
        "title": "Normalization and residual connections",
        "area": "neural-networks",
        "level": "core",
        "summary": "The residual stream, BatchNorm, LayerNorm and RMSNorm, pre-norm versus post-norm, and the feed-forward block.",
        "prerequisites": ["backpropagation"],
        "sources": [
            "pytorch:torch/nn/modules/normalization.py",
            "pytorch:torch/nn/modules/batchnorm.py",
            "pytorch:torch/nn/functional.py",
            "pytorch:torch/nn/modules/transformer.py",
        ],
        "ready": True,
    },
    {
        "slug": "optimizers",
        "title": "Optimizers: SGD to AdamW",
        "area": "neural-networks",
        "level": "core",
        "summary": "SGD, momentum, RMSProp, Adam and AdamW, with a worked Adam step.",
        "prerequisites": ["derivatives-and-gradients", "backpropagation"],
        "sources": [
            "pytorch:torch/optim/sgd.py",
            "pytorch:torch/optim/adam.py",
            "pytorch:torch/optim/adamw.py",
            "pytorch:torch/optim/optimizer.py",
        ],
        "ready": True,
    },
    {
        "slug": "learning-rate-schedules",
        "title": "Learning-rate schedules",
        "area": "neural-networks",
        "level": "core",
        "summary": "Warmup, step, cosine and one-cycle schedules, and why the learning rate matters most.",
        "prerequisites": ["optimizers"],
        "sources": [
            "pytorch:torch/optim/lr_scheduler.py",
        ],
        "ready": True,
    },
    {
        "slug": "training-loop",
        "title": "The training loop",
        "area": "neural-networks",
        "level": "intro",
        "summary": "Cross-entropy loss, AdamW, learning-rate warmup and decay, gradient clipping, and mixed precision.",
        "prerequisites": ["optimizers", "loss-functions"],
        "sources": [
            "pytorch:torch/nn/modules/loss.py",
            "pytorch:torch/optim/adamw.py",
            "pytorch:torch/optim/lr_scheduler.py",
            "pytorch:torch/amp/autocast_mode.py",
            "pytorch:torch/amp/grad_scaler.py",
            "pytorch:torch/nn/utils/clip_grad.py",
        ],
        "ready": True,
    },
    {
        "slug": "cnns",
        "title": "Convolutional networks",
        "area": "architectures",
        "level": "core",
        "summary": "Convolution as a sliding dot product, output-size arithmetic, pooling, and residual CNNs.",
        "prerequisites": ["neurons-and-layers"],
        "sources": [
            "pytorch:torch/nn/modules/conv.py",
            "pytorch:torch/nn/modules/pooling.py",
        ],
        "ready": True,
    },
    {
        "slug": "rnns-and-lstms",
        "title": "RNNs and LSTMs",
        "area": "architectures",
        "level": "core",
        "summary": "Recurrence, backprop through time, and the gates that let LSTMs remember.",
        "prerequisites": ["backpropagation"],
        "sources": [
            "pytorch:torch/nn/modules/rnn.py",
            "pytorch:torch/nn/utils/rnn.py",
        ],
        "ready": True,
    },
    {
        "slug": "transformer",
        "title": "The Transformer",
        "area": "architectures",
        "level": "core",
        "summary": "The full encoder-decoder from Attention Is All You Need, block by block, and how nn.Transformer implements it.",
        "prerequisites": ["attention", "layernorm-and-residuals"],
        "sources": [
            "pytorch:torch/nn/modules/transformer.py",
            "pytorch:torch/nn/modules/activation.py",
            "pytorch:torch/nn/modules/normalization.py",
            "pytorch:torch/nn/modules/sparse.py",
            "pytorch:torch/nn/modules/linear.py",
        ],
        "ready": True,
    },
    {
        "slug": "autoencoders",
        "title": "Autoencoders",
        "area": "architectures",
        "level": "core",
        "summary": "Compress, then reconstruct: bottlenecks, denoising, and the latent space.",
        "prerequisites": ["neurons-and-layers"],
        "sources": [
            "pytorch:torch/nn/modules/linear.py",
            "pytorch:torch/nn/modules/conv.py",
        ],
        "ready": True,
    },
    {
        "slug": "graph-neural-networks",
        "title": "Graph neural networks",
        "area": "architectures",
        "level": "advanced",
        "summary": "Message passing over graphs: GCN, GraphSAGE and GAT.",
        "prerequisites": ["neurons-and-layers", "matrix-multiplication"],
        "sources": [
            "pytorch:torch/_torch_docs.py",
            "pytorch:torch/_tensor.py",
        ],
        "ready": True,
    },
    {
        "slug": "vision-transformer",
        "title": "Vision Transformer",
        "area": "architectures",
        "level": "core",
        "summary": "ViT: images as sequences of patches, patch embedding as a strided convolution, and the class token.",
        "prerequisites": ["transformer", "cnns"],
        "sources": [
            "pytorch:torch/nn/modules/conv.py",
            "pytorch:torch/nn/modules/transformer.py",
            "pytorch:torch/nn/modules/flatten.py",
        ],
        "ready": True,
    },
    {
        "slug": "mixture-of-experts",
        "title": "Mixture of experts",
        "area": "architectures",
        "level": "advanced",
        "summary": "Routing each token to a few of many feed-forward experts: top-k gating, load balancing, total versus active parameters.",
        "prerequisites": ["transformer"],
        "sources": [
            "pytorch:torch/nn/modules/container.py",
            "pytorch:torch/nn/modules/linear.py",
            "pytorch:torch/nn/functional.py",
        ],
        "ready": False,
    },
    {
        "slug": "state-space-models",
        "title": "State-space models",
        "area": "architectures",
        "level": "advanced",
        "summary": "S4 and Mamba: recurrences that train like convolutions and run in linear time.",
        "prerequisites": ["rnns-and-lstms", "transformer"],
        "sources": [
            "pytorch:torch/nn/modules/conv.py",
            "pytorch:torch/functional.py",
        ],
        "ready": False,
    },
    {
        "slug": "autoregressive-models",
        "title": "Autoregressive models",
        "area": "generative",
        "level": "core",
        "summary": "Generating one piece at a time by the chain rule of probability, trained with teacher forcing.",
        "prerequisites": ["entropy-and-kl", "probability-and-distributions"],
        "sources": [
            "pytorch:torch/distributions/categorical.py",
            "pytorch:torch/nn/modules/loss.py",
            "pytorch:torch/nn/modules/conv.py",
        ],
        "ready": True,
    },
    {
        "slug": "variational-autoencoders",
        "title": "Variational autoencoders",
        "area": "generative",
        "level": "core",
        "summary": "The ELBO, derived, and the reparameterization trick that makes it trainable.",
        "prerequisites": [
            "autoencoders",
            "entropy-and-kl",
            "bayes-rule",
        ],
        "sources": [
            "pytorch:torch/distributions/normal.py",
            "pytorch:torch/distributions/kl.py",
        ],
        "ready": True,
    },
    {
        "slug": "gans",
        "title": "Generative adversarial networks",
        "area": "generative",
        "level": "core",
        "summary": "A generator and a discriminator trained against each other, and how to keep the game stable.",
        "prerequisites": ["neurons-and-layers", "loss-functions"],
        "sources": [
            "pytorch:torch/nn/modules/loss.py",
            "pytorch:torch/autograd/__init__.py",
        ],
        "ready": True,
    },
    {
        "slug": "diffusion-models",
        "title": "Diffusion models",
        "area": "generative",
        "level": "advanced",
        "summary": "Learning to undo noise: the forward process, the ε-prediction objective, and DDPM and DDIM sampling.",
        "prerequisites": ["variational-autoencoders", "expectation-and-variance"],
        "sources": [
            "pytorch:torch/nn/functional.py",
            "pytorch:torch/random.py",
        ],
        "ready": True,
    },
    {
        "slug": "diffusion-unet",
        "title": "Diffusion U-Net",
        "area": "generative",
        "level": "advanced",
        "summary": "Denoising diffusion and the U-Net that predicts the noise: down and up paths, skips, timestep embeddings and attention.",
        "prerequisites": [
            "diffusion-models",
            "cnns",
            "attention",
        ],
        "sources": [
            "pytorch:torch/nn/modules/conv.py",
            "pytorch:torch/nn/modules/normalization.py",
            "pytorch:torch/nn/modules/upsampling.py",
            "pytorch:torch/nn/modules/activation.py",
        ],
        "ready": False,
    },
    {
        "slug": "flow-matching",
        "title": "Normalizing flows and flow matching",
        "area": "generative",
        "level": "advanced",
        "summary": "Normalizing flows, continuous flows, and the flow-matching objective that trains them simply.",
        "prerequisites": ["diffusion-models"],
        "sources": [
            "pytorch:torch/distributions/transforms.py",
        ],
        "ready": False,
    },
    {
        "slug": "tokenization",
        "title": "Tokenization",
        "area": "language-models",
        "level": "intro",
        "summary": "How text becomes tokens: byte-pair encoding worked on a toy corpus, and why tokenization matters.",
        "prerequisites": [],
        "sources": [
            "pytorch:torch/nn/modules/sparse.py",
        ],
        "ready": True,
    },
    {
        "slug": "embeddings",
        "title": "Embeddings",
        "area": "language-models",
        "level": "intro",
        "summary": "Embedding tables as lookups, the geometry they learn, and contextual versus static embeddings.",
        "prerequisites": ["tensors-and-shapes", "vectors-and-dot-products"],
        "sources": [
            "pytorch:torch/nn/modules/sparse.py",
            "pytorch:torch/nn/functional.py",
        ],
        "ready": True,
    },
    {
        "slug": "positional-encoding",
        "title": "Positional encoding",
        "area": "language-models",
        "level": "core",
        "summary": "How a model that sees a set learns order: sinusoidal, learned and rotary (RoPE) positions.",
        "prerequisites": ["embeddings", "attention"],
        "sources": [
            "pytorch:torch/nn/modules/sparse.py",
            "pytorch:torch/nn/functional.py",
            "pytorch:torch/nn/modules/transformer.py",
        ],
        "ready": True,
    },
    {
        "slug": "attention",
        "title": "Attention",
        "area": "language-models",
        "level": "core",
        "summary": "Scaled dot-product and multi-head attention with a tiny numeric example, masks, and cross-attention.",
        "prerequisites": ["embeddings", "matrix-multiplication"],
        "sources": [
            "pytorch:torch/nn/functional.py",
            "pytorch:torch/nn/modules/activation.py",
            "pytorch:torch/nn/attention/__init__.py",
            "pytorch:torch/nn/attention/bias.py",
            "pytorch:torch/nn/attention/flex_attention.py",
        ],
        "ready": True,
    },
    {
        "slug": "encoder-only",
        "title": "Encoder-only models",
        "area": "language-models",
        "level": "core",
        "summary": "The BERT-style stack: bidirectional attention, padding masks, masked-language-model training and task heads.",
        "prerequisites": ["transformer"],
        "sources": [
            "pytorch:torch/nn/modules/transformer.py",
            "pytorch:torch/nn/modules/sparse.py",
            "pytorch:torch/nn/modules/loss.py",
        ],
        "ready": True,
    },
    {
        "slug": "decoder-only-llm",
        "title": "Decoder-only LLMs",
        "area": "language-models",
        "level": "core",
        "summary": "The GPT-style stack: causal self-attention blocks, the LM head, generation, and a GPT-2-small parameter count.",
        "prerequisites": ["transformer", "training-loop"],
        "sources": [
            "pytorch:torch/nn/modules/transformer.py",
            "pytorch:torch/nn/functional.py",
            "pytorch:torch/nn/modules/sparse.py",
            "pytorch:torch/nn/modules/loss.py",
        ],
        "ready": True,
    },
    {
        "slug": "pretraining",
        "title": "Pretraining and scaling laws",
        "area": "language-models",
        "level": "advanced",
        "summary": "Pretraining objectives, compute budgets, and the scaling laws that size a model.",
        "prerequisites": ["decoder-only-llm"],
        "sources": [
            "pytorch:torch/nn/modules/loss.py",
        ],
        "ready": True,
    },
    {
        "slug": "fine-tuning",
        "title": "Fine-tuning and LoRA",
        "area": "language-models",
        "level": "core",
        "summary": "Full fine-tuning, instruction tuning, and LoRA's low-rank update, derived.",
        "prerequisites": ["decoder-only-llm", "linear-algebra-toolkit"],
        "sources": [
            "pytorch:torch/nn/utils/parametrize.py",
            "pytorch:torch/nn/modules/linear.py",
        ],
        "ready": False,
    },
    {
        "slug": "preference-optimization",
        "title": "Preference optimization: RLHF and DPO",
        "area": "language-models",
        "level": "advanced",
        "summary": "Reward models, RLHF with PPO, and DPO's closed-form loss.",
        "prerequisites": ["fine-tuning", "reinforcement-learning"],
        "sources": [
            "pytorch:torch/nn/functional.py",
        ],
        "ready": False,
    },
    {
        "slug": "decoding",
        "title": "Decoding and sampling",
        "area": "language-models",
        "level": "core",
        "summary": "Greedy, beam, temperature, top-k and top-p sampling, and speculative decoding.",
        "prerequisites": ["decoder-only-llm", "probability-and-distributions"],
        "sources": [
            "pytorch:torch/distributions/categorical.py",
            "pytorch:torch/_torch_docs.py",
        ],
        "ready": True,
    },
    {
        "slug": "kv-cache",
        "title": "The KV cache",
        "area": "language-models",
        "level": "advanced",
        "summary": "Why generation caches keys and values, how big the cache gets, and how MQA and GQA shrink it.",
        "prerequisites": ["attention", "decoding"],
        "sources": [
            "pytorch:torch/nn/functional.py",
            "pytorch:torch/nn/modules/activation.py",
        ],
        "ready": True,
    },
    {
        "slug": "similarity-search",
        "title": "Similarity search",
        "area": "retrieval",
        "level": "intro",
        "summary": "Exact nearest-neighbor search over embeddings, the choice of metric, and lexical baselines.",
        "prerequisites": ["vectors-and-dot-products", "nearest-neighbors"],
        "sources": [
            "pytorch:torch/nn/modules/distance.py",
            "sklearn:sklearn/neighbors/_unsupervised.py",
        ],
        "ready": True,
    },
    {
        "slug": "vector-indexes",
        "title": "Vector indexes",
        "area": "retrieval",
        "level": "advanced",
        "summary": "Approximate nearest neighbors with IVF, product quantization and HNSW.",
        "prerequisites": ["similarity-search", "clustering"],
        "sources": [
            "sklearn:sklearn/cluster/_kmeans.py",
        ],
        "ready": True,
    },
    {
        "slug": "learning-to-rank",
        "title": "Learning to rank",
        "area": "retrieval",
        "level": "core",
        "summary": "Pointwise, pairwise and listwise ranking, NDCG, and LambdaMART.",
        "prerequisites": ["classification-metrics", "gradient-boosting"],
        "sources": [
            "xgboost:src/objective/lambdarank_obj.cc",
            "sklearn:sklearn/metrics/_ranking.py",
        ],
        "ready": True,
    },
    {
        "slug": "collaborative-filtering",
        "title": "Collaborative filtering",
        "area": "retrieval",
        "level": "core",
        "summary": "Recommending from the user–item matrix: neighborhoods and matrix factorization.",
        "prerequisites": ["linear-algebra-toolkit", "embeddings"],
        "sources": [
            "sklearn:sklearn/decomposition/_nmf.py",
            "pytorch:torch/nn/modules/sparse.py",
        ],
        "ready": True,
    },
    {
        "slug": "two-tower-models",
        "title": "Two-tower models",
        "area": "retrieval",
        "level": "core",
        "summary": "Separate query and item encoders trained with in-batch negatives, served with a vector index.",
        "prerequisites": ["collaborative-filtering", "similarity-search"],
        "sources": [
            "pytorch:torch/nn/modules/sparse.py",
            "pytorch:torch/nn/functional.py",
        ],
        "ready": False,
    },
    {
        "slug": "retrieval-augmented-generation",
        "title": "Retrieval-augmented generation",
        "area": "retrieval",
        "level": "advanced",
        "summary": "Retrieving passages and putting them in the prompt, and how to evaluate each half.",
        "prerequisites": ["two-tower-models", "decoder-only-llm"],
        "sources": [
            "pytorch:torch/nn/functional.py",
        ],
        "ready": False,
    },
    {
        "slug": "gpu-execution",
        "title": "How a GPU runs a model",
        "area": "training-systems",
        "level": "core",
        "summary": "Kernels, streams, memory bandwidth and the roofline: why some ops are fast and others aren't.",
        "prerequisites": ["matrix-multiplication"],
        "sources": [
            "pytorch:torch/cuda/__init__.py",
            "pytorch:torch/cuda/streams.py",
        ],
        "ready": True,
    },
    {
        "slug": "mixed-precision",
        "title": "Precision and mixed precision",
        "area": "training-systems",
        "level": "core",
        "summary": "fp32, bf16, fp16 and fp8, autocast, and loss scaling.",
        "prerequisites": ["gpu-execution"],
        "sources": [
            "pytorch:torch/amp/autocast_mode.py",
            "pytorch:torch/amp/grad_scaler.py",
        ],
        "ready": True,
    },
    {
        "slug": "data-loading-and-batching",
        "title": "Data loading and batching",
        "area": "training-systems",
        "level": "intro",
        "summary": "Datasets, DataLoaders, collation, padding and packing.",
        "prerequisites": ["tensors-and-shapes"],
        "sources": [
            "pytorch:torch/utils/data/dataloader.py",
            "pytorch:torch/utils/data/dataset.py",
            "pytorch:torch/utils/data/sampler.py",
        ],
        "ready": True,
    },
    {
        "slug": "gradient-accumulation",
        "title": "Gradient accumulation",
        "area": "training-systems",
        "level": "core",
        "summary": "Simulating a large batch with micro-batches, and the details that make it exact.",
        "prerequisites": ["training-loop"],
        "sources": [
            "pytorch:torch/optim/optimizer.py",
            "pytorch:torch/nn/parallel/distributed.py",
        ],
        "ready": True,
    },
    {
        "slug": "distributed-training",
        "title": "Distributed training",
        "area": "training-systems",
        "level": "advanced",
        "summary": "Data, sharded, tensor and pipeline parallelism, and memory per GPU worked through.",
        "prerequisites": ["gradient-accumulation", "gpu-execution"],
        "sources": [
            "pytorch:torch/nn/parallel/distributed.py",
            "pytorch:torch/distributed/fsdp/__init__.py",
        ],
        "ready": False,
    },
    {
        "slug": "checkpointing",
        "title": "Checkpointing",
        "area": "training-systems",
        "level": "core",
        "summary": "Saving and resuming every piece of training state, and activation checkpointing.",
        "prerequisites": ["training-loop"],
        "sources": [
            "pytorch:torch/serialization.py",
            "pytorch:torch/utils/checkpoint.py",
            "pytorch:torch/distributed/checkpoint/__init__.py",
        ],
        "ready": False,
    },
    {
        "slug": "profiling",
        "title": "Profiling",
        "area": "training-systems",
        "level": "core",
        "summary": "Measuring training correctly, reading a profiler trace, and computing MFU.",
        "prerequisites": ["gpu-execution"],
        "sources": [
            "pytorch:torch/profiler/profiler.py",
            "pytorch:torch/cuda/__init__.py",
        ],
        "ready": False,
    },
    {
        "slug": "quantization",
        "title": "Quantization",
        "area": "inference",
        "level": "core",
        "summary": "Scale and zero point, per-channel quantization, and int8 and int4 for LLMs.",
        "prerequisites": ["mixed-precision"],
        "sources": [
            "pytorch:torch/ao/quantization/quantize.py",
        ],
        "ready": True,
    },
    {
        "slug": "distillation",
        "title": "Knowledge distillation",
        "area": "inference",
        "level": "core",
        "summary": "Training a small student on a large teacher's soft targets.",
        "prerequisites": ["entropy-and-kl", "training-loop"],
        "sources": [
            "pytorch:torch/nn/modules/loss.py",
        ],
        "ready": True,
    },
    {
        "slug": "model-serving",
        "title": "Model serving",
        "area": "inference",
        "level": "core",
        "summary": "Exporting a model and serving it with batching on CPU or GPU.",
        "prerequisites": ["gpu-execution"],
        "sources": [
            "pytorch:torch/export/__init__.py",
            "pytorch:torch/serialization.py",
        ],
        "ready": True,
    },
    {
        "slug": "latency-and-throughput",
        "title": "Latency and throughput",
        "area": "inference",
        "level": "core",
        "summary": "Time to first token, tail latency, batching and Little's law.",
        "prerequisites": ["model-serving", "kv-cache"],
        "sources": [
            "pytorch:torch/profiler/profiler.py",
            "pytorch:torch/cuda/streams.py",
        ],
        "ready": True,
    },
    {
        "slug": "monitoring-and-drift",
        "title": "Monitoring and drift",
        "area": "inference",
        "level": "core",
        "summary": "Detecting drift in inputs, predictions and outcomes after deployment.",
        "prerequisites": ["classification-metrics", "calibration"],
        "sources": [
            "sklearn:sklearn/metrics/_classification.py",
            "sklearn:sklearn/calibration.py",
        ],
        "ready": False,
    },
    {
        "slug": "reproducibility",
        "title": "Reproducibility",
        "area": "inference",
        "level": "intro",
        "summary": "Seeds, deterministic kernels and versioning: getting the same result twice.",
        "prerequisites": ["training-loop"],
        "sources": [
            "pytorch:torch/random.py",
            "pytorch:torch/utils/data/dataloader.py",
            "sklearn:sklearn/utils/validation.py",
        ],
        "ready": False,
    },
    {
        "slug": "reinforcement-learning",
        "title": "Reinforcement learning",
        "area": "specialized",
        "level": "core",
        "summary": "MDPs, Q-learning, policy gradients and PPO.",
        "prerequisites": ["probability-and-distributions", "optimizers"],
        "sources": [
            "pytorch:torch/distributions/categorical.py",
        ],
        "ready": True,
    },
    {
        "slug": "time-series",
        "title": "Time series",
        "area": "specialized",
        "level": "core",
        "summary": "Trend, seasonality, lag features, time-ordered validation and forecasting models.",
        "prerequisites": ["cross-validation", "rnns-and-lstms"],
        "sources": [
            "sklearn:sklearn/model_selection/_split.py",
            "pytorch:torch/nn/modules/rnn.py",
        ],
        "ready": True,
    },
    {
        "slug": "causal-inference",
        "title": "Causal inference",
        "area": "specialized",
        "level": "advanced",
        "summary": "Confounding, potential outcomes, propensity scores and experiments.",
        "prerequisites": ["bayes-rule", "logistic-regression"],
        "sources": [
            "sklearn:sklearn/linear_model/_logistic.py",
        ],
        "ready": True,
    },
    {
        "slug": "online-learning",
        "title": "Online learning",
        "area": "specialized",
        "level": "core",
        "summary": "Learning from a stream, regret, and bandits.",
        "prerequisites": ["optimizers"],
        "sources": [
            "sklearn:sklearn/linear_model/_stochastic_gradient.py",
        ],
        "ready": True,
    },
    {
        "slug": "multimodal-models",
        "title": "Multimodal models",
        "area": "specialized",
        "level": "advanced",
        "summary": "Contrastive image–text pretraining and vision-language models.",
        "prerequisites": ["vision-transformer", "two-tower-models"],
        "sources": [
            "pytorch:torch/nn/functional.py",
        ],
        "ready": False,
    },
]

LEVELS = ["intro", "core", "advanced"]

LEARNING_PATH = [
    {"title": "Tensor shapes and matrix multiplication", "slugs": ["tensors-and-shapes", "matrix-multiplication"]},
    {"title": "Backpropagation and optimization", "slugs": ["derivatives-and-gradients", "chain-rule", "backpropagation", "optimizers"]},
    {"title": "Embeddings and attention", "slugs": ["embeddings", "attention"]},
    {"title": "The full Transformer block", "slugs": ["layernorm-and-residuals", "transformer"]},
    {"title": "Training versus inference", "slugs": ["training-loop", "decoder-only-llm", "decoding", "kv-cache"]},
    {"title": "Evaluation and data leakage", "slugs": ["data-splits", "data-leakage", "classification-metrics", "cross-validation"]},
    {"title": "Classical baselines", "slugs": ["linear-regression", "logistic-regression", "gradient-boosting"]},
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

MULTIHEAD_EXAMPLE = {
    "tokens": ["the", "cat", "sat", "<pad>"],
    "padding": [False, False, False, True],
    "embed_dim": 4,
    "heads": 2,
    "x": [[1, 0, 1, 0], [0, 1, 0, 1], [1, 1, 0, 0], [0, 0, 0, 0]],
    "in_proj_weight": [
        [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1],
        [1, 0, 1, 0], [0, 1, 0, 1], [1, 1, 0, 0], [0, 0, 1, 1],
        [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1], [1, 0, 0, 1],
    ],
    "out_proj_weight": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
}

TRANSFORMER_PRESETS = [
    {"name": "nn.Transformer() defaults", "d_model": 512, "nhead": 8, "encoder_layers": 6, "decoder_layers": 6, "dim_feedforward": 2048},
    {"name": "Paper, big", "d_model": 1024, "nhead": 16, "encoder_layers": 6, "decoder_layers": 6, "dim_feedforward": 4096},
    {"name": "Tiny (toy)", "d_model": 64, "nhead": 4, "encoder_layers": 2, "decoder_layers": 2, "dim_feedforward": 256},
]

SIMILARITY_EXAMPLE = {
    "query": [1, 2],
    "documents": {"d1": [2, 4], "d2": [2, 1], "d3": [-2, 1], "d4": [6, 0]},
}

PROJECTION_EXAMPLE = {"onto": [3, 1], "vector": [2, 2]}

MATMUL_EXAMPLE = {"a": [[1, 2, 3], [4, 5, 6]], "b": [[7, 8], [9, 10], [11, 12]]}

LINEAR_EXAMPLE = {
    "x": [[1, 2, 3], [4, 5, 6]],
    "weight": [[1, 0, -1], [0.5, 0.5, 0.5]],
    "bias": [0, 1],
}

INVERSE_EXAMPLE = [[2, 1], [1, 1]]

EIGEN_EXAMPLE = {"matrix": [[2, 1], [1, 2]], "start": [1, 0], "steps": 6}

SVD_EXAMPLE = [[3, 0], [4, 5]]

RATINGS_EXAMPLE = {
    "users": ["Ana", "Ben", "Cy", "Dee", "Eli"],
    "films": ["Alien", "Heat", "Up", "Coco"],
    "ratings": [[5, 4, 1, 1], [4, 5, 1, 2], [1, 1, 5, 4], [2, 1, 4, 5], [3, 3, 3, 3]],
}

RANK_EXAMPLE = [[1, 2, 3], [2, 4, 6], [1, 0, 1]]

CONDITION_EXAMPLE = {"a": [[1, 1], [1, 1.0001]], "b": [2, 2.0001], "nudged": [2, 2.0002]}

MISSING_EXAMPLE = {
    "columns": ["age", "income"],
    "rows": [
        [23, 38], [35, None], [None, 61], [41, 72],
        [29, None], [None, 45], [52, 90], [38, None],
    ],
}

ROUTING_EXAMPLE = {
    "x": [1, 2, 3, 4, 5, 9, None, None],
    "y": [1.0, 1.2, 0.8, 3.0, 3.2, 2.8, 1.1, 0.9],
    "reg_lambda": 1.0,
}

SLOPE_EXAMPLE = {"x": 3, "steps": [1, 0.1, 0.01, 0.001]}

BOWL_EXAMPLE = {"scale": [1, 3], "start": [3, 2], "lr": 0.1, "steps": 6, "unstable_lr": 0.4}

JACOBIAN_EXAMPLE = {"point": [2, 3]}

CHAIN_EXAMPLE = {"x": 1, "a": 3, "b": 1}

TWO_LAYER_EXAMPLE = {
    "x": [2, 1],
    "w1": [[1, -1], [-1, 1]],
    "b1": [1, 0],
    "w2": [2, 3],
    "b2": 0,
    "target": 3,
}

MODE_COST_EXAMPLE = {"widths": [1000, 1000, 1000, 1]}

BERNOULLI_EXAMPLE = {"p": 0.3}

CATEGORICAL_EXAMPLE = {
    "labels": ["cat", "dog", "bird"],
    "logits": [2.0, 1.0, 0.0],
    "uniforms": [0.10, 0.50, 0.70, 0.95],
}

JOINT_EXAMPLE = {
    "rows": ["rain", "sun"],
    "columns": ["umbrella", "no umbrella"],
    "counts": [[24, 6], [7, 63]],
}

DIE_EXAMPLE = {"values": [1, 2, 3, 4, 5, 6], "seed": 13, "checkpoints": [10, 100, 1000, 10000]}

COVARIANCE_EXAMPLE = {"pairs": [(1, 52), (2, 60), (3, 61), (4, 75), (5, 82)], "labels": ["hours studied", "score"]}

MINIBATCH_EXAMPLE = {"w": 1.0, "x": [1, 2, 3, 4, 5, 6], "y": [2, 3, 7, 8, 9, 13], "batch_sizes": [1, 2, 3, 6]}

ENTROPY_EXAMPLE = {
    "labels": ["sun", "cloud", "rain", "snow"],
    "p": [0.5, 0.25, 0.125, 0.125],
    "q": [0.25, 0.25, 0.25, 0.25],
}

ASYMMETRY_EXAMPLE = {"p": [0.9, 0.1], "q": [0.5, 0.5]}

PERPLEXITY_EXAMPLE = {"tokens": ["the", "cat", "sat", "down"], "probs": [0.4, 0.05, 0.2, 0.5]}

CONSTANT_FIT_EXAMPLE = {"targets": [2.0, 2.5, 3.0, 3.2, 3.6, 12.0], "delta": 2.0}

TRIPLET_EXAMPLE = {"anchor": [0.0, 0.0], "positive": [1.0, 0.0], "negative": [1.5, 1.0], "margin": 1.0}

INFONCE_EXAMPLE = {"labels": ["matching caption", "related caption", "unrelated caption"], "similarities": [0.9, 0.3, 0.1], "temperatures": [1.0, 0.1]}

REDUCTION_EXAMPLE = {"losses": [0.5, 1.2, 0.3, 2.0], "targets": [4, 7, -100, 2], "ignore_index": -100}

LINE_DESCENT_EXAMPLE = {"raw_lr": 0.04, "raw_steps": 300, "centered_lr": 0.2, "centered_steps": 20, "marks": [1, 10, 100, 300]}

REGULARIZATION_EXAMPLE = {
    "features": ["hours studied", "practice tests taken", "hours of sleep"],
    "x": [[1, 2, 7], [2, 1, 6], [3, 4, 5], [4, 3, 6], [5, 6, 9], [6, 5, 9], [7, 8, 4], [8, 7, 7]],
    "y": [49, 49, 59, 61, 71, 76, 83, 85],
    "ridge_alphas": [2 * i for i in range(41)],
    "lasso_alphas": [0.25 * i for i in range(57)],
}

LOGISTIC_EXAMPLE = {
    "hours": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0],
    "passed": [0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1],
    "newton_steps": 6,
    "gd_lr": 0.3,
    "gd_steps": 2000,
    "gd_marks": [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000],
}

BOUNDARY_EXAMPLE = {
    "rows": [[1, 2], [2, 1], [2, 3], [3, 1.5], [1.5, 4], [3, 3.5], [4, 5], [5, 4], [5, 6], [3.5, 5.5], [6, 5], [4.5, 2.5]],
    "labels": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0],
    "cs": [0.05, 1.0, 100.0],
    "unpenalized_steps": 12,
}

SOFTMAX_EXAMPLE = {"classes": ["cat", "dog", "bird"], "logits": [2.0, 1.0, -1.0], "target": 0}

XOR_EXAMPLE = {
    "inputs": [[0, 0], [0, 1], [1, 0], [1, 1]],
    "targets": [0, 1, 1, 0],
    "w1": [[1, 1], [1, 1]],
    "b1": [0, -1],
    "w2": [[1, -2]],
    "b2": [0],
}

APPROXIMATION_EXAMPLE = {"start": 0.0, "stop": 2 * math.pi, "units": [3, 8], "samples": 400}

MLP_EXAMPLE = {"sizes": [784, 256, 128, 10]}

BACKPROP_EXAMPLE = {
    "x": [1, 2],
    "w1": [[1, 0], [-1, 1], [0.5, -1]],
    "b1": [0, 0, 0.5],
    "w2": [[1, -1, 2], [0, 1, 1]],
    "b2": [0, 0],
    "target": 0,
    "lr": 0.1,
}

GRADIENT_CHECK_EXAMPLE = {"parameter": ("w1", 0, 0), "steps": [10.0 ** -k for k in range(1, 13)]}

DEPTH_EXAMPLE = {
    "width": 32,
    "depth": 30,
    "seed": 7,
    "cases": [
        {"label": "ReLU, gain 0.7", "activation": "relu", "gain": 0.7},
        {"label": "ReLU, He init", "activation": "relu", "gain": 1.0},
        {"label": "ReLU, gain 1.4", "activation": "relu", "gain": 1.4},
        {"label": "sigmoid, Xavier init", "activation": "sigmoid", "gain": 1.0},
    ],
}

OPTIMIZER_BOWL = {
    "curvatures": [1.0, 50.0],
    "start": [-4.0, 1.0],
    "steps": 30,
    "runs": [
        {"label": "SGD, lr 0.036", "kind": "sgd", "hyper": {"lr": 0.036}, "plot": True},
        {"label": "SGD, lr 0.042", "kind": "sgd", "hyper": {"lr": 0.042}, "plot": False},
        {"label": "momentum 0.7, lr 0.03", "kind": "momentum", "hyper": {"lr": 0.03, "momentum": 0.7}, "plot": True},
        {"label": "Nesterov 0.7, lr 0.02", "kind": "nesterov", "hyper": {"lr": 0.02, "momentum": 0.7}, "plot": False},
        {"label": "RMSProp, lr 0.05", "kind": "rmsprop", "hyper": {"lr": 0.05}, "plot": False},
        {"label": "Adam, lr 0.3", "kind": "adam", "hyper": {"lr": 0.3}, "plot": True},
    ],
}

ADAM_EXAMPLE = {
    "lr": 0.001,
    "betas": (0.9, 0.999),
    "eps": 1e-8,
    "start": [0.5, -0.3],
    "grads": [[0.02, -4.0], [0.01, -3.0], [0.03, -5.0]],
}

WEIGHT_DECAY_EXAMPLE = {"lr": 0.01, "weight_decay": 0.1, "steps": 1000, "scales": [1.0, 0.01]}

EMBEDDING_EXAMPLE = {
    "vocab": ["<pad>", "the", "cat", "sat", "on", "mat"],
    "table": [
        [0.0, 0.0, 0.0],
        [0.1, -0.2, 0.3],
        [0.9, 0.4, -0.5],
        [-0.3, 0.8, 0.2],
        [0.2, 0.1, -0.1],
        [0.7, -0.6, 0.5],
    ],
    "batch": [[1, 2, 3, 4, 1, 5], [1, 2, 3, 0, 0, 0]],
    "padding_idx": 0,
}

WORD2VEC_EXAMPLE = {
    "corpus": [
        "cat eats fish", "dog eats meat", "cat chases mouse", "dog chases cat",
        "mouse eats cheese", "cat drinks milk", "dog drinks water", "mouse drinks water",
        "car needs fuel", "truck needs fuel", "car drives road", "truck drives road",
        "bus drives road",
    ],
    "window": 2,
    "dim": 2,
    "epochs": 300,
    "lr": 0.05,
    "seed": 0,
}

_HEADING = re.compile(r'<h([23]) id="([^"]+)"[^>]*>(.*?)</h\1>', re.S)
_TAG = re.compile(r"<[^>]+>")


def pinned_url(key, path, start=None, end=None):
    pin = PINS[key]
    url = f"{pin['repo']}/blob/{pin['commit']}/{path}"
    if start is None:
        return url
    if end is None or end == start:
        return f"{url}#L{start}"
    return f"{url}#L{start}-L{end}"


def source_url(path, start=None, end=None):
    return pinned_url("pytorch", path, start, end)


def sklearn_url(path, start=None, end=None):
    return pinned_url("sklearn", path, start, end)


def xgboost_url(path, start=None, end=None):
    return pinned_url("xgboost", path, start, end)


def ready_pages():
    return [page for page in PAGES if page["ready"]]


def pages_by_area():
    return [
        {"area": area, "pages": [page for page in PAGES if page["area"] == area["slug"]]}
        for area in AREAS
    ]


def connections(slug):
    by_slug = {page["slug"]: page for page in PAGES}
    page = by_slug[slug]
    return {
        "prerequisites": [by_slug[prerequisite] for prerequisite in page["prerequisites"]],
        "leads_to": [entry for entry in PAGES if slug in entry["prerequisites"]],
    }


def learning_path():
    by_slug = {page["slug"]: page for page in PAGES}
    return [
        {"title": step["title"], "pages": [by_slug[slug] for slug in step["slugs"]]}
        for step in LEARNING_PATH
    ]


def find_area(slug):
    return next((area for area in AREAS if area["slug"] == slug), None)


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


def masked_softmax_row(scores):
    top = max(scores)
    if top == -math.inf:
        return [math.nan] * len(scores)
    exps = [math.exp(score - top) for score in scores]
    total = sum(exps)
    return [value / total for value in exps]


def scaled_attention(queries, keys, values, bias=None, scale=None):
    width = len(queries[0])
    scale = 1 / math.sqrt(width) if scale is None else scale
    scores, weights = [], []
    for i, query in enumerate(queries):
        row = [
            sum(q * k for q, k in zip(query, key)) * scale + (bias[i][j] if bias else 0.0)
            for j, key in enumerate(keys)
        ]
        scores.append(row)
        weights.append(masked_softmax_row(row))
    outputs = matmul(weights, values)
    return {"scores": scores, "weights": weights, "outputs": outputs}


def causal_allowed_mask(rows, columns, variant="upper_left"):
    offset = columns - rows if variant == "lower_right" else 0
    return [[column <= row + offset for column in range(columns)] for row in range(rows)]


def allowed_to_additive(mask):
    return [[0.0 if cell else -math.inf for cell in row] for row in mask]


def masked_out_to_additive(mask):
    return [[-math.inf if cell else 0.0 for cell in row] for row in mask]


def key_padding_additive(padding, rows):
    return [[-math.inf if flag else 0.0 for flag in padding] for _ in range(rows)]


def add_masks(first, second):
    return [[a + b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(first, second)]


def split_heads(matrix, heads):
    width = len(matrix[0]) // heads
    return [[row[h * width:(h + 1) * width] for row in matrix] for h in range(heads)]


def merge_heads(per_head):
    return [sum((head[i] for head in per_head), []) for i in range(len(per_head[0]))]


def packed_in_projection(x, in_proj_weight):
    embed_dim = len(x[0])
    projected = [
        matmul(x, transpose(in_proj_weight[part * embed_dim:(part + 1) * embed_dim]))
        for part in range(3)
    ]
    return {"q": projected[0], "k": projected[1], "v": projected[2]}


def multihead_attention(example, bias=None):
    heads = example["heads"]
    qkv = packed_in_projection(example["x"], example["in_proj_weight"])
    split = {name: split_heads(qkv[name], heads) for name in "qkv"}
    results = [
        scaled_attention(split["q"][h], split["k"][h], split["v"][h], bias)
        for h in range(heads)
    ]
    merged = merge_heads([result["outputs"] for result in results])
    output = matmul(merged, transpose(example["out_proj_weight"]))
    count = len(example["x"])
    averaged = [
        [sum(result["weights"][i][j] for result in results) / heads for j in range(count)]
        for i in range(count)
    ]
    return {
        "q": qkv["q"], "k": qkv["k"], "v": qkv["v"],
        "heads": results, "split": split, "merged": merged,
        "output": output, "average_weights": averaged,
    }


def gqa_groups(query_heads, kv_heads):
    if query_heads % kv_heads:
        raise ValueError("query heads must be a multiple of key/value heads")
    ratio = query_heads // kv_heads
    return [head // ratio for head in range(query_heads)]


def kv_cache_bytes_per_token(layers, kv_heads, head_dim, bytes_per_value):
    return 2 * layers * kv_heads * head_dim * bytes_per_value


def multihead_param_count(embed_dim, bias=True):
    weights = 3 * embed_dim * embed_dim + embed_dim * embed_dim
    biases = 3 * embed_dim + embed_dim if bias else 0
    return {"in_proj": 3 * embed_dim * embed_dim, "out_proj": embed_dim * embed_dim,
            "biases": biases, "total": weights + biases}


NORM_EXAMPLE = {
    "tokens": ["the", "cat", "sat"],
    "x": [[2.0, 4.0, 6.0, 8.0], [1.0, 1.0, 1.0, 5.0], [-3.0, 0.0, 3.0, 6.0]],
    "gamma": [1.0, 1.0, 1.0, 1.0],
    "beta": [0.0, 0.0, 0.0, 0.0],
    "eps": 1e-5,
}


def _mean(values):
    return sum(values) / len(values)


def _variance(values):
    centre = _mean(values)
    return sum((value - centre) ** 2 for value in values) / len(values)


def layer_norm_row(row, gamma=None, beta=None, eps=1e-5):
    centre = _mean(row)
    scale = 1.0 / math.sqrt(_variance(row) + eps)
    gamma = gamma or [1.0] * len(row)
    beta = beta or [0.0] * len(row)
    return [(value - centre) * scale * g + b for value, g, b in zip(row, gamma, beta)]


def rms_norm_row(row, gamma=None, eps=1e-5):
    scale = 1.0 / math.sqrt(_mean([value * value for value in row]) + eps)
    gamma = gamma or [1.0] * len(row)
    return [value * scale * g for value, g in zip(row, gamma)]


def batch_norm_columns(matrix, gamma=None, beta=None, eps=1e-5):
    columns = [list(column) for column in zip(*matrix)]
    gamma = gamma or [1.0] * len(columns)
    beta = beta or [0.0] * len(columns)
    normalised = []
    for column, g, b in zip(columns, gamma, beta):
        centre = _mean(column)
        scale = 1.0 / math.sqrt(_variance(column) + eps)
        normalised.append([(value - centre) * scale * g + b for value in column])
    return [list(row) for row in zip(*normalised)]


def group_norm_row(row, groups, eps=1e-5):
    if len(row) % groups:
        raise ValueError("channels must be a multiple of groups")
    size = len(row) // groups
    out = []
    for group in range(groups):
        out.extend(layer_norm_row(row[group * size:(group + 1) * size], eps=eps))
    return out


def running_stats_update(running_mean, running_var, batch, momentum=0.1):
    batch_mean = _mean(batch)
    unbiased = _variance(batch) * len(batch) / (len(batch) - 1)
    return (
        (1 - momentum) * running_mean + momentum * batch_mean,
        (1 - momentum) * running_var + momentum * unbiased,
    )


def batch_norm_eval(value, running_mean, running_var, gamma=1.0, beta=0.0, eps=1e-5):
    return (value - running_mean) / math.sqrt(running_var + eps) * gamma + beta


def residual_block(x, sublayer, norm, norm_first):
    if norm_first:
        return [a + b for a, b in zip(x, sublayer(norm(x)))]
    return norm([a + b for a, b in zip(x, sublayer(x))])


def residual_stream_norms(x, sublayers, norm, norm_first):
    norms = [math.sqrt(sum(value * value for value in x))]
    for sublayer in sublayers:
        x = residual_block(x, sublayer, norm, norm_first)
        norms.append(math.sqrt(sum(value * value for value in x)))
    return x, norms


def residual_demo(depth=6, gain=1.0):
    x = [1.0, -2.0, 3.0, -1.0]
    sublayer = lambda v: [gain * (value + 0.5 * v[(i + 1) % len(v)]) for i, value in enumerate(v)]
    sublayers = [sublayer] * depth
    pre = residual_stream_norms(x, sublayers, layer_norm_row, True)[1]
    post = residual_stream_norms(x, sublayers, layer_norm_row, False)[1]
    return {"pre": pre, "post": post}


def norm_param_count(kind, features, bias=True):
    if kind == "layer":
        return features * (2 if bias else 1)
    if kind == "rms":
        return features
    if kind == "batch":
        return 2 * features
    raise ValueError(kind)


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


def broadcast_steps(*shapes):
    rank = max(len(shape) for shape in shapes)
    padded = [(1,) * (rank - len(shape)) + tuple(shape) for shape in shapes]
    steps = []
    for position, sizes in enumerate(zip(*padded)):
        others = {size for size in sizes if size != 1}
        if len(others) > 1:
            raise ValueError(f"sizes {sizes} clash at dimension {position}")
        steps.append({"sizes": sizes, "result": others.pop() if others else 1})
    return {"padded": padded, "steps": steps, "shape": tuple(step["result"] for step in steps)}


def broadcast_shape(*shapes):
    return broadcast_steps(*shapes)["shape"]


def contiguous_strides(shape):
    strides = []
    step = 1
    for size in reversed(shape):
        strides.append(step)
        step *= size
    return tuple(reversed(strides))


def element_offset(index, strides):
    return sum(i * stride for i, stride in zip(index, strides))


def is_contiguous(shape, strides):
    return all(
        stride == expected
        for size, stride, expected in zip(shape, strides, contiguous_strides(shape))
        if size != 1
    )


def transpose_layout(shape, strides, first, second):
    shape, strides = list(shape), list(strides)
    shape[first], shape[second] = shape[second], shape[first]
    strides[first], strides[second] = strides[second], strides[first]
    return tuple(shape), tuple(strides)


def dot_product(u, v):
    if len(u) != len(v):
        raise ValueError("vectors must have the same length")
    return sum(a * b for a, b in zip(u, v))


def vector_norm(v, p=2):
    if p == math.inf:
        return max(abs(x) for x in v)
    return sum(abs(x) ** p for x in v) ** (1 / p)


def cosine_similarity(u, v, eps=1e-8):
    return dot_product(u, v) / (max(vector_norm(u), eps) * max(vector_norm(v), eps))


def angle_degrees(u, v):
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine_similarity(u, v)))))


def projection(vector, onto):
    scale = dot_product(vector, onto) / dot_product(onto, onto)
    along = [scale * x for x in onto]
    return {"scale": scale, "along": along, "residual": [a - b for a, b in zip(vector, along)]}


def transpose(matrix):
    return [list(column) for column in zip(*matrix)]


def identity(size):
    return [[1 if row == column else 0 for column in range(size)] for row in range(size)]


def matmul(a, b):
    if len(a[0]) != len(b):
        raise ValueError(f"inner sizes differ: [{len(a)}, {len(a[0])}] @ [{len(b)}, {len(b[0])}]")
    return [[dot_product(row, column) for column in transpose(b)] for row in a]


def matmul_shape(first, second):
    first, second = tuple(first), tuple(second)
    if not first or not second:
        raise ValueError("matmul needs at least one dimension on each side")
    if len(first) == 1 and len(second) == 1:
        if first != second:
            raise ValueError(f"vector lengths differ: {first[0]} and {second[0]}")
        return ()
    left = (1,) + first if len(first) == 1 else first
    right = second + (1,) if len(second) == 1 else second
    if left[-1] != right[-2]:
        raise ValueError(f"inner sizes differ: {left[-1]} and {right[-2]}")
    shape = broadcast_shape(left[:-2], right[:-2]) + (left[-2], right[-1])
    if len(first) == 1:
        shape = shape[:-2] + shape[-1:]
    if len(second) == 1:
        shape = shape[:-1]
    return shape


def matmul_flops(m, k, n, batch=1):
    return 2 * batch * m * k * n


def linear_layer(x, weight, bias=None):
    out = matmul(x, transpose(weight))
    if bias is None:
        return out
    return [[value + b for value, b in zip(row, bias)] for row in out]


def inverse_2x2(matrix):
    (a, b), (c, d) = matrix
    determinant = a * d - b * c
    if determinant == 0:
        raise ValueError("matrix is singular")
    return [[d / determinant, -b / determinant], [-c / determinant, a / determinant]]


def jacobi_eigh(matrix, tol=1e-12, sweeps=100):
    n = len(matrix)
    a = [list(map(float, row)) for row in matrix]
    v = [[float(i == j) for j in range(n)] for i in range(n)]
    for _ in range(sweeps):
        off = sum(a[i][j] ** 2 for i in range(n) for j in range(n) if i != j)
        if off < tol:
            break
        for p in range(n - 1):
            for q in range(p + 1, n):
                if abs(a[p][q]) < 1e-300:
                    continue
                theta = (a[q][q] - a[p][p]) / (2 * a[p][q])
                t = math.copysign(1.0, theta) / (abs(theta) + math.hypot(theta, 1.0))
                c = 1 / math.hypot(t, 1.0)
                s = t * c
                for k in range(n):
                    akp, akq = a[k][p], a[k][q]
                    a[k][p], a[k][q] = c * akp - s * akq, s * akp + c * akq
                for k in range(n):
                    apk, aqk = a[p][k], a[q][k]
                    a[p][k], a[q][k] = c * apk - s * aqk, s * apk + c * aqk
                for k in range(n):
                    vkp, vkq = v[k][p], v[k][q]
                    v[k][p], v[k][q] = c * vkp - s * vkq, s * vkp + c * vkq
    order = sorted(range(n), key=lambda i: a[i][i])
    values = [a[i][i] for i in order]
    vectors = [_sign_fixed([v[k][i] for k in range(n)]) for i in order]
    return {"values": values, "vectors": vectors}


def _sign_fixed(vector):
    pivot = max(vector, key=abs)
    return [-x for x in vector] if pivot < 0 else vector


def power_iteration(matrix, start, steps):
    vector = list(map(float, start))
    trace = []
    for _ in range(steps):
        image = [dot_product(row, vector) for row in matrix]
        length = vector_norm(image)
        vector = [x / length for x in image]
        rayleigh = dot_product(vector, [dot_product(row, vector) for row in matrix])
        trace.append({"vector": vector, "value": rayleigh})
    return trace


def svd(matrix, sweeps=60):
    rows, cols = len(matrix), len(matrix[0])
    if rows < cols:
        factors = svd(transpose(matrix), sweeps)
        return {"U": transpose(factors["Vh"]), "S": factors["S"], "Vh": transpose(factors["U"])}
    columns = [[float(matrix[i][j]) for i in range(rows)] for j in range(cols)]
    right = [[float(i == j) for i in range(cols)] for j in range(cols)]
    for _ in range(sweeps):
        rotated = False
        for p in range(cols - 1):
            for q in range(p + 1, cols):
                alpha = dot_product(columns[p], columns[p])
                beta = dot_product(columns[q], columns[q])
                gamma = dot_product(columns[p], columns[q])
                if abs(gamma) <= 1e-15 * math.sqrt(alpha * beta) or gamma == 0:
                    continue
                rotated = True
                zeta = (beta - alpha) / (2 * gamma)
                t = math.copysign(1.0, zeta) / (abs(zeta) + math.hypot(zeta, 1.0))
                c = 1 / math.hypot(t, 1.0)
                s = c * t
                for vectors in (columns, right):
                    vp, vq = vectors[p], vectors[q]
                    vectors[p] = [c * a - s * b for a, b in zip(vp, vq)]
                    vectors[q] = [s * a + c * b for a, b in zip(vp, vq)]
        if not rotated:
            break
    singular = [vector_norm(column) for column in columns]
    order = sorted(range(cols), key=lambda j: -singular[j])
    left, vh = [], []
    for j in order:
        u = [x / singular[j] for x in columns[j]] if singular[j] > 0 else [0.0] * rows
        v = right[j]
        if max(v, key=abs) < 0:
            u, v = [-x for x in u], [-x for x in v]
        left.append(u)
        vh.append(v)
    return {"U": transpose(left), "S": [singular[j] for j in order], "Vh": vh}


def from_svd(factors, k=None):
    k = len(factors["S"]) if k is None else k
    rows, cols = len(factors["U"]), len(factors["Vh"][0])
    out = [[0.0] * cols for _ in range(rows)]
    for r in range(k):
        sigma, v = factors["S"][r], factors["Vh"][r]
        for i in range(rows):
            u = factors["U"][i][r] * sigma
            for j in range(cols):
                out[i][j] += u * v[j]
    return out


def frobenius_norm(matrix):
    return math.sqrt(sum(x * x for row in matrix for x in row))


def low_rank_errors(matrix):
    factors = svd(matrix)
    total = frobenius_norm(matrix) ** 2
    out = []
    for k in range(len(factors["S"]) + 1):
        approx = from_svd(factors, k)
        residual = [[a - b for a, b in zip(r1, r2)] for r1, r2 in zip(matrix, approx)]
        error = frobenius_norm(residual) ** 2
        out.append({
            "k": k,
            "error": error,
            "dropped": sum(s * s for s in factors["S"][k:]),
            "kept_share": 1 - error / total,
        })
    return out


def rank_from_singular_values(singular, shape, rtol=None, atol=0.0):
    rtol = max(shape) * 2.0 ** -52 if rtol is None else rtol
    threshold = max(atol, singular[0] * rtol) if singular else atol
    return sum(1 for s in singular if s > threshold)


def matrix_rank(matrix, rtol=None, atol=0.0):
    return rank_from_singular_values(svd(matrix)["S"], (len(matrix), len(matrix[0])), rtol, atol)


def condition_number(matrix):
    singular = svd(matrix)["S"]
    return math.inf if singular[-1] == 0 else singular[0] / singular[-1]


def solve_2x2(matrix, rhs):
    inverse = inverse_2x2(matrix)
    return [dot_product(row, rhs) for row in inverse]


def perturbed_solve(example):
    a, b, nudged = example["a"], example["b"], example["nudged"]
    x, x_nudged = solve_2x2(a, b), solve_2x2(a, nudged)
    rhs_change = vector_norm([p - q for p, q in zip(nudged, b)]) / vector_norm(b)
    x_change = vector_norm([p - q for p, q in zip(x_nudged, x)]) / vector_norm(x)
    return {
        "x": x,
        "x_nudged": x_nudged,
        "rhs_change": rhs_change,
        "x_change": x_change,
        "amplification": x_change / rhs_change,
        "cond": condition_number(a),
    }


def unit_circle_image(matrix, count=72):
    points = []
    for k in range(count + 1):
        t = 2 * math.pi * k / count
        x = [math.cos(t), math.sin(t)]
        points.append({"in": x, "out": [dot_product(row, x) for row in matrix]})
    return points


def svd_stages(matrix, count=72):
    factors = svd(matrix)
    stages = {"circle": [], "rotated": [], "stretched": [], "image": []}
    for point in unit_circle_image(matrix, count):
        rotated = [dot_product(row, point["in"]) for row in factors["Vh"]]
        stages["circle"].append(point["in"])
        stages["rotated"].append(rotated)
        stages["stretched"].append([s * x for s, x in zip(factors["S"], rotated)])
        stages["image"].append(point["out"])
    return stages


def lora_param_counts(d_out, d_in, rank):
    full = d_out * d_in
    low = rank * (d_out + d_in)
    return {"full": full, "lora": low, "share": low / full}


def square(x):
    return x * x


def difference_quotient(f, x, h):
    return (f(x + h) - f(x)) / h


def slope_table(example):
    x = example["x"]
    exact = 2 * x
    rows = []
    for h in example["steps"]:
        secant = difference_quotient(square, x, h)
        rows.append({"h": h, "secant": secant, "error": secant - exact})
    return {"x": x, "value": square(x), "exact": exact, "rows": rows}


def numerical_gradient(f, point, h=1e-6):
    gradient = []
    for i in range(len(point)):
        up = list(point)
        down = list(point)
        up[i] += h
        down[i] -= h
        gradient.append((f(up) - f(down)) / (2 * h))
    return gradient


def numerical_jacobian(f, point, h=1e-6):
    columns = []
    for i in range(len(point)):
        up = list(point)
        down = list(point)
        up[i] += h
        down[i] -= h
        columns.append([(a - b) / (2 * h) for a, b in zip(f(up), f(down))])
    return [list(row) for row in zip(*columns)]


def jacobian_example_function(point):
    x, y = point
    return [x * y, x + y * y]


def jacobian_example_exact(point):
    x, y = point
    return [[y, x], [1, 2 * y]]


def bowl(point, scale):
    return sum(s * x * x for s, x in zip(scale, point))


def bowl_gradient(point, scale):
    return [2 * s * x for s, x in zip(scale, point)]


def gradient_descent(gradient, start, lr, steps):
    points = [list(start)]
    for _ in range(steps):
        current = points[-1]
        points.append([x - lr * g for x, g in zip(current, gradient(current))])
    return points


def bowl_descent(example, lr=None):
    scale = example["scale"]
    rate = example["lr"] if lr is None else lr
    points = gradient_descent(lambda p: bowl_gradient(p, scale), example["start"], rate, example["steps"])
    return [
        {"step": i, "point": point, "value": bowl(point, scale), "gradient": bowl_gradient(point, scale)}
        for i, point in enumerate(points)
    ]


def bowl_contours(scale, levels):
    return [
        {"level": level, "radii": [math.sqrt(level / s) for s in scale]}
        for level in levels
    ]


def stable_learning_rate(scale):
    return 1 / max(scale)


def scalar_chain(example):
    x, a, b = example["x"], example["a"], example["b"]
    u = a * x + b
    return {"x": x, "u": u, "f": u * u, "du_dx": a, "df_du": 2 * u, "df_dx": 2 * u * a}


def relu(values):
    return [max(0, v) for v in values]


def two_layer_loss(x, w1, b1, w2, b2, target):
    hidden = relu([dot_product(row, x) + b for row, b in zip(w1, b1)])
    y = dot_product(w2, hidden) + b2
    return 0.5 * (y - target) ** 2


def two_layer_pass(example):
    x, w1, b1 = example["x"], example["w1"], example["b1"]
    w2, b2, target = example["w2"], example["b2"], example["target"]
    z1 = [dot_product(row, x) + b for row, b in zip(w1, b1)]
    h = relu(z1)
    y = dot_product(w2, h) + b2
    dy = y - target
    dh = [dy * w for w in w2]
    dz1 = [g if z > 0 else 0 for g, z in zip(dh, z1)]
    return {
        "z1": z1,
        "h": h,
        "y": y,
        "loss": 0.5 * dy * dy,
        "dy": dy,
        "dw2": [dy * v for v in h],
        "db2": dy,
        "dh": dh,
        "dz1": dz1,
        "dw1": [[g * xi for xi in x] for g in dz1],
        "db1": dz1,
        "dx": [dot_product(column, dz1) for column in transpose(w1)],
    }


def mode_costs(widths):
    per_pass = sum(a * b for a, b in zip(widths, widths[1:]))
    inputs, outputs = widths[0], widths[-1]
    return {
        "inputs": inputs,
        "outputs": outputs,
        "per_pass": per_pass,
        "forward": inputs * per_pass,
        "reverse": outputs * per_pass,
    }


def bernoulli_pmf(k, p):
    return p if k == 1 else 1 - p


def categorical_from_logits(logits):
    top = max(logits)
    log_norm = top + math.log(sum(math.exp(v - top) for v in logits))
    log_probs = [v - log_norm for v in logits]
    return {"log_probs": log_probs, "probs": [math.exp(v) for v in log_probs]}


def inverse_cdf_sample(probs, u):
    total = 0.0
    for index, p in enumerate(probs):
        total += p
        if u < total:
            return index
    return len(probs) - 1


def normal_log_prob(x, loc, scale):
    return -((x - loc) ** 2) / (2 * scale**2) - math.log(scale) - math.log(math.sqrt(2 * math.pi))


def normal_pdf(x, loc, scale):
    return math.exp(normal_log_prob(x, loc, scale))


def normal_cdf(x, loc, scale):
    return 0.5 * (1 + math.erf((x - loc) / (scale * math.sqrt(2))))


def normal_band(k):
    return normal_cdf(k, 0.0, 1.0) - normal_cdf(-k, 0.0, 1.0)


def joint_table(example):
    counts = example["counts"]
    total = sum(sum(row) for row in counts)
    joint = [[c / total for c in row] for row in counts]
    row_marginal = [sum(row) for row in joint]
    column_marginal = [sum(column) for column in transpose(joint)]
    given_row = [[v / m for v in row] for row, m in zip(joint, row_marginal)]
    given_column = [[v / m for v, m in zip(row, column_marginal)] for row in joint]
    product = [[r * c for c in column_marginal] for r in row_marginal]
    independent = all(
        math.isclose(j, q) for joint_row, product_row in zip(joint, product) for j, q in zip(joint_row, product_row)
    )
    return {
        "total": total,
        "joint": joint,
        "row_marginal": row_marginal,
        "column_marginal": column_marginal,
        "given_row": given_row,
        "given_column": given_column,
        "product": product,
        "independent": independent,
    }


def expectation(values, probs):
    return sum(v * p for v, p in zip(values, probs))


def variance(values, probs):
    mean = expectation(values, probs)
    return sum(p * (v - mean) ** 2 for v, p in zip(values, probs))


def covariance(pairs):
    n = len(pairs)
    mean_x = sum(x for x, _ in pairs) / n
    mean_y = sum(y for _, y in pairs) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in pairs) / n
    var_x = sum((x - mean_x) ** 2 for x, _ in pairs) / n
    var_y = sum((y - mean_y) ** 2 for _, y in pairs) / n
    return {
        "mean_x": mean_x,
        "mean_y": mean_y,
        "cov": cov,
        "var_x": var_x,
        "var_y": var_y,
        "corr": cov / math.sqrt(var_x * var_y),
    }


def die_rolls(n, seed):
    rng = random.Random(seed)
    return [1 + int(rng.random() * 6) for _ in range(n)]


def running_means(samples, values, checkpoints):
    probs = [1 / len(values)] * len(values)
    mu = expectation(values, probs)
    sigma = math.sqrt(variance(values, probs))
    rows = []
    for n in checkpoints:
        mean = sum(samples[:n]) / n
        rows.append({"n": n, "mean": mean, "error": mean - mu, "standard_error": sigma / math.sqrt(n)})
    return rows


def sum_pmf(values, n):
    pmf = {0: 1.0}
    for _ in range(n):
        step = {}
        for total, p in pmf.items():
            for v in values:
                step[total + v] = step.get(total + v, 0.0) + p / len(values)
        pmf = step
    return dict(sorted(pmf.items()))


def minibatch_gradients(example):
    w, xs, ys = example["w"], example["x"], example["y"]
    per_example = [2 * x * (w * x - y) for x, y in zip(xs, ys)]
    full = sum(per_example) / len(per_example)
    sizes = []
    for b in example["batch_sizes"]:
        grads = [sum(batch) / b for batch in itertools.combinations(per_example, b)]
        mean = sum(grads) / len(grads)
        sizes.append(
            {
                "batch_size": b,
                "count": len(grads),
                "mean": mean,
                "variance": sum((g - mean) ** 2 for g in grads) / len(grads),
                "lowest": min(grads),
                "highest": max(grads),
                "grads": sorted(grads),
            }
        )
    return {"per_example": per_example, "full": full, "sizes": sizes}


def information_content(p, base=2):
    return -math.log(p, base)


def entropy(probs, base=2):
    return sum(-p * math.log(p, base) for p in probs if p > 0)


def cross_entropy(p, q, base=2):
    total = 0.0
    for p_i, q_i in zip(p, q):
        if p_i == 0:
            continue
        if q_i == 0:
            return math.inf
        total -= p_i * math.log(q_i, base)
    return total


def kl_divergence(p, q, base=2):
    return cross_entropy(p, q, base) - entropy(p, base)


def logits_cross_entropy(logits, target):
    log_probs = categorical_from_logits(logits)["log_probs"]
    probs = [math.exp(v) for v in log_probs]
    gradient = [prob - (1 if index == target else 0) for index, prob in enumerate(probs)]
    return {"loss": -log_probs[target], "probs": probs, "gradient": gradient}


def perplexity(example):
    nll = [-math.log(p) for p in example["probs"]]
    mean_nll = sum(nll) / len(nll)
    return {"nll": nll, "mean_nll": mean_nll, "perplexity": math.exp(mean_nll)}


def mutual_information(example, base=2):
    table = joint_table(example)
    joint = [v for row in table["joint"] for v in row]
    h_x = entropy(table["row_marginal"], base)
    h_y = entropy(table["column_marginal"], base)
    h_xy = entropy(joint, base)
    return {"h_x": h_x, "h_y": h_y, "h_xy": h_xy, "mutual": h_x + h_y - h_xy}


def huber(residual, delta=1.0):
    size = abs(residual)
    return 0.5 * residual * residual if size <= delta else delta * (size - 0.5 * delta)


def regression_losses(residual, delta=1.0):
    return {"mse": residual * residual, "mae": abs(residual), "huber": huber(residual, delta)}


def fit_constant(targets, delta=1.0):
    ordered = sorted(targets)
    middle = len(ordered) // 2
    median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2

    def slope(c):
        return sum(max(-delta, min(delta, c - y)) for y in targets)

    low, high = ordered[0], ordered[-1]
    for _ in range(100):
        mid = (low + high) / 2
        if slope(mid) < 0:
            low = mid
        else:
            high = mid
    return {"mse": sum(targets) / len(targets), "mae": median, "huber": (low + high) / 2}


def bce_with_logits(logit, target):
    return max(logit, 0) - logit * target + math.log1p(math.exp(-abs(logit)))


def margin_losses(margin):
    return {
        "zero_one": 1.0 if margin <= 0 else 0.0,
        "hinge": max(0.0, 1 - margin),
        "logistic": math.log1p(math.exp(-margin)),
    }


def triplet_loss(example):
    d_ap = math.dist(example["anchor"], example["positive"])
    d_an = math.dist(example["anchor"], example["negative"])
    return {"d_ap": d_ap, "d_an": d_an, "loss": max(d_ap - d_an + example["margin"], 0.0)}


def info_nce(similarities, temperature, target=0):
    return logits_cross_entropy([s / temperature for s in similarities], target)


def reduce_losses(example):
    kept = [loss for loss, target in zip(example["losses"], example["targets"]) if target != example["ignore_index"]]
    none = [0.0 if target == example["ignore_index"] else loss for loss, target in zip(example["losses"], example["targets"])]
    return {"none": none, "sum": sum(kept), "mean": sum(kept) / len(kept), "count": len(kept)}


def least_squares_line(pairs):
    stats = covariance(pairs)
    slope = stats["cov"] / stats["var_x"]
    intercept = stats["mean_y"] - slope * stats["mean_x"]
    fitted = [intercept + slope * x for x, _ in pairs]
    residuals = [y - f for (_, y), f in zip(pairs, fitted)]
    sse = sum(r * r for r in residuals)
    sst = sum((y - stats["mean_y"]) ** 2 for _, y in pairs)
    return {
        "slope": slope,
        "intercept": intercept,
        "fitted": fitted,
        "residuals": residuals,
        "sse": sse,
        "mse": sse / len(pairs),
        "sst": sst,
        "r2": 1 - sse / sst,
    }


def solve_linear(a, b):
    size = len(a)
    rows = [list(row) + [value] for row, value in zip(a, b)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda r: abs(rows[r][col]))
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for r in range(size):
            if r != col:
                factor = rows[r][col] / rows[col][col]
                rows[r] = [x - factor * y for x, y in zip(rows[r], rows[col])]
    return [rows[i][size] / rows[i][i] for i in range(size)]


def normal_equations(x, y):
    design = [list(row) + [1] for row in x]
    gram = matmul(transpose(design), design)
    moment = [sum(row[j] * t for row, t in zip(design, y)) for j in range(len(design[0]))]
    return {"gram": gram, "moment": moment, "solution": solve_linear(gram, moment)}


def standardize(x):
    n = len(x)
    means = [sum(col) / n for col in zip(*x)]
    stds = [math.sqrt(sum((v - m) ** 2 for v in col) / n) for col, m in zip(zip(*x), means)]
    return {
        "z": [[(v - m) / s for v, m, s in zip(row, means, stds)] for row in x],
        "means": means,
        "stds": stds,
    }


def ridge_coefficients(z, y, alpha):
    gram = matmul(transpose(z), z)
    for j in range(len(gram)):
        gram[j][j] += alpha
    moment = [sum(row[j] * t for row, t in zip(z, y)) for j in range(len(z[0]))]
    return solve_linear(gram, moment)


def soft_threshold(value, threshold):
    return math.copysign(max(abs(value) - threshold, 0.0), value)


def lasso_coefficients(z, y, alpha, sweeps=500):
    n, p = len(z), len(z[0])
    norms = [sum(row[j] ** 2 for row in z) / n for j in range(p)]
    weights = [0.0] * p
    residual = list(y)
    for _ in range(sweeps):
        for j in range(p):
            rho = sum(row[j] * r for row, r in zip(z, residual)) / n + norms[j] * weights[j]
            new = soft_threshold(rho, alpha) / norms[j]
            residual = [r - row[j] * (new - weights[j]) for row, r in zip(z, residual)]
            weights[j] = new
    return weights


def regularization_paths(example):
    scaled = standardize(example["x"])
    z = scaled["z"]
    mean_y = sum(example["y"]) / len(example["y"])
    centered = [t - mean_y for t in example["y"]]
    n = len(z)
    corr = [[sum(row[i] * row[j] for row in z) / n for j in range(len(z[0]))] for i in range(len(z[0]))]
    return {
        "corr": corr,
        "mean_y": mean_y,
        "ols": ridge_coefficients(z, centered, 0.0),
        "ridge": [{"alpha": a, "coef": ridge_coefficients(z, centered, a)} for a in example["ridge_alphas"]],
        "lasso": [{"alpha": a, "coef": lasso_coefficients(z, centered, a)} for a in example["lasso_alphas"]],
    }


def mse_hessian(pairs, centered=False):
    n = len(pairs)
    mean_x = sum(x for x, _ in pairs) / n
    xs = [x - mean_x if centered else x for x, _ in pairs]
    return [
        [2 * sum(x * x for x in xs) / n, 2 * sum(xs) / n],
        [2 * sum(xs) / n, 2.0],
    ]


def line_descent(pairs, lr, steps, centered=False):
    n = len(pairs)
    mean_x = sum(x for x, _ in pairs) / n
    data = [(x - mean_x if centered else x, y) for x, y in pairs]

    def gradient(point):
        w, b = point
        errors = [(w * x + b - y, x) for x, y in data]
        return [2 * sum(e * x for e, x in errors) / n, 2 * sum(e for e, _ in errors) / n]

    return gradient_descent(gradient, [0.0, 0.0], lr, steps)


def symmetric_eigen_2x2(matrix):
    (a, b), (_, d) = matrix
    mid, spread = (a + d) / 2, math.hypot((a - d) / 2, b)
    angle = 0.5 * math.atan2(2 * b, a - d)
    return {
        "values": [mid + spread, mid - spread],
        "vectors": [[math.cos(angle), math.sin(angle)], [-math.sin(angle), math.cos(angle)]],
    }


def quadratic_ellipse(matrix, center, excess, count=72):
    eigen = symmetric_eigen_2x2(matrix)
    radii = [math.sqrt(2 * excess / value) for value in eigen["values"]]
    (u1, u2), (v1, v2) = eigen["vectors"]
    points = []
    for k in range(count + 1):
        t = 2 * math.pi * k / count
        a, b = radii[0] * math.cos(t), radii[1] * math.sin(t)
        points.append([center[0] + a * u1 + b * v1, center[1] + a * u2 + b * v2])
    return points


def sigmoid(z):
    if z >= 0:
        return 1 / (1 + math.exp(-z))
    e = math.exp(z)
    return e / (1 + e)


def _with_intercept(rows):
    return [list(row) + [1.0] for row in rows]


def logistic_objective(rows, y, params, c=None):
    logits = [sum(a * b for a, b in zip(row, params)) for row in _with_intercept(rows)]
    total = sum(bce_with_logits(z, t) for z, t in zip(logits, y))
    if c is not None:
        total += sum(w * w for w in params[:-1]) / (2 * c)
    return total


def logistic_newton(rows, y, c=None, iterations=8):
    design = _with_intercept(rows)
    size = len(design[0])
    params = [0.0] * size
    history = []
    for step in range(iterations + 1):
        probs = [sigmoid(sum(a * b for a, b in zip(row, params))) for row in design]
        grad = [sum((p - t) * row[j] for p, t, row in zip(probs, y, design)) for j in range(size)]
        hess = [
            [sum(p * (1 - p) * row[j] * row[k] for p, row in zip(probs, design)) for k in range(size)]
            for j in range(size)
        ]
        if c is not None:
            for j in range(size - 1):
                grad[j] += params[j] / c
                hess[j][j] += 1 / c
        history.append({
            "params": list(params),
            "loss": logistic_objective(rows, y, params, c) / len(y),
            "grad_norm": math.sqrt(sum(g * g for g in grad)),
        })
        if step < iterations:
            params = [w - s for w, s in zip(params, solve_linear(hess, grad))]
    return history


def logistic_descent(rows, y, lr, steps):
    design = _with_intercept(rows)
    n = len(y)
    params = [0.0] * len(design[0])
    history = []
    for step in range(steps + 1):
        history.append({"params": list(params), "loss": logistic_objective(rows, y, params) / n})
        if step < steps:
            errors = [sigmoid(sum(a * b for a, b in zip(row, params))) - t for row, t in zip(design, y)]
            grad = [sum(e * row[j] for e, row in zip(errors, design)) / n for j in range(len(params))]
            params = [w - lr * g for w, g in zip(params, grad)]
    return history


def logistic_fit_1d(example):
    rows = [[h] for h in example["hours"]]
    newton = logistic_newton(rows, example["passed"], iterations=example["newton_steps"])
    w, b = newton[-1]["params"]
    best = newton[-1]["loss"]
    descent = logistic_descent(rows, example["passed"], example["gd_lr"], example["gd_steps"])
    return {
        "w": w,
        "b": b,
        "boundary": -b / w,
        "odds_ratio": math.exp(w),
        "loss": best,
        "probs": [sigmoid(w * h + b) for h in example["hours"]],
        "newton": newton,
        "newton_excess": [e["loss"] - best for e in newton],
        "descent_excess": {s: descent[s]["loss"] - best for s in example["gd_marks"]},
        "descent_final": descent[-1]["params"],
    }


def boundary_fits(example):
    fits = []
    for c in example["cs"]:
        params = logistic_newton(example["rows"], example["labels"], c, 20)[-1]["params"]
        probs = [sigmoid(params[0] * a + params[1] * b + params[2]) for a, b in example["rows"]]
        fits.append({"c": c, "params": params, "norm": math.hypot(params[0], params[1]), "probs": probs})
    unpenalized = logistic_newton(example["rows"], example["labels"], None, example["unpenalized_steps"])
    growth = [{"norm": math.hypot(*e["params"][:2]), "loss": e["loss"]} for e in unpenalized]
    return {"fits": fits, "unpenalized": growth}


def mlp_forward(x, layers):
    trace = []
    h = list(x)
    for index, (weight, bias) in enumerate(layers):
        z = [dot_product(row, h) + b for row, b in zip(weight, bias)]
        h = z if index == len(layers) - 1 else relu(z)
        trace.append({"z": z, "h": h})
    return trace


def collapse_linear(layers):
    weight, bias = layers[0]
    for next_weight, next_bias in layers[1:]:
        bias = [dot_product(row, bias) + b for row, b in zip(next_weight, next_bias)]
        weight = matmul(next_weight, weight)
    return weight, bias


def xor_network(example):
    layers = [(example["w1"], example["b1"]), (example["w2"], example["b2"])]
    rows = []
    for x, t in zip(example["inputs"], example["targets"]):
        hidden, output = mlp_forward(x, layers)
        rows.append({"x": x, "target": t, "z": hidden["z"], "h": hidden["h"], "y": output["h"][0]})
    weight, bias = collapse_linear(layers)
    linear = [dot_product(weight[0], x) + bias[0] for x in example["inputs"]]
    fit = normal_equations(example["inputs"], example["targets"])["solution"]
    best = [dot_product(fit[:-1], x) + fit[-1] for x in example["inputs"]]
    return {
        "rows": rows,
        "collapsed": {"weight": weight[0], "bias": bias[0], "outputs": linear},
        "best_linear": {"weight": fit[:-1], "bias": fit[-1], "outputs": best},
    }


def relu_interpolant(f, start, stop, units):
    knots = [start + (stop - start) * i / units for i in range(units + 1)]
    values = [f(k) for k in knots]
    slopes = [(values[i + 1] - values[i]) / (knots[i + 1] - knots[i]) for i in range(units)]
    coefficients = [slopes[0]] + [slopes[i] - slopes[i - 1] for i in range(1, units)]
    return {"knots": knots, "values": values, "bias": values[0], "coefficients": coefficients}


def evaluate_interpolant(net, x):
    return net["bias"] + sum(c * max(0.0, x - k) for c, k in zip(net["coefficients"], net["knots"]))


def approximation_fits(example):
    start, stop, samples = example["start"], example["stop"], example["samples"]
    xs = [start + (stop - start) * i / samples for i in range(samples + 1)]
    fits = []
    for units in example["units"]:
        net = relu_interpolant(math.sin, start, stop, units)
        errors = [abs(evaluate_interpolant(net, x) - math.sin(x)) for x in xs]
        fits.append({**net, "units": units, "params": 3 * units + 1, "max_error": max(errors)})
    return fits


def mlp_param_count(sizes):
    layers = [
        {"in": a, "out": b, "weights": a * b, "biases": b, "total": a * b + b}
        for a, b in zip(sizes, sizes[1:])
    ]
    return {"layers": layers, "total": sum(layer["total"] for layer in layers)}


def backprop_pass(x, w1, b1, w2, b2, target):
    z1 = [dot_product(row, x) + b for row, b in zip(w1, b1)]
    h = relu(z1)
    logits = [dot_product(row, h) + b for row, b in zip(w2, b2)]
    out = categorical_from_logits(logits)
    probs = out["probs"]
    dlogits = [p - (1 if k == target else 0) for k, p in enumerate(probs)]
    dh = [dot_product(column, dlogits) for column in transpose(w2)]
    dz1 = [g if z > 0 else 0 for g, z in zip(dh, z1)]
    return {
        "z1": z1,
        "h": h,
        "logits": logits,
        "probs": probs,
        "loss": -out["log_probs"][target],
        "dlogits": dlogits,
        "dw2": [[g * v + 0.0 for v in h] for g in dlogits],
        "db2": dlogits,
        "dh": dh,
        "dz1": dz1,
        "dw1": [[g * xi + 0.0 for xi in x] for g in dz1],
        "db1": dz1,
    }


def _backprop_params(example):
    return {name: example[name] for name in ("w1", "b1", "w2", "b2")}


def _sgd_update(params, grads, lr):
    def step(value, grad):
        if isinstance(value, list):
            return [step(v, g) for v, g in zip(value, grad)]
        return value - lr * grad

    return {name: step(params[name], grads["d" + name]) for name in params}


def backprop_example(example):
    params = _backprop_params(example)
    before = backprop_pass(example["x"], **params, target=example["target"])
    updated = _sgd_update(params, before, example["lr"])
    after = backprop_pass(example["x"], **updated, target=example["target"])
    return {"before": before, "updated": updated, "after": after}


def _perturbed_loss(example, parameter, delta):
    name, *index = parameter
    params = {key: [list(row) if isinstance(row, list) else row for row in value]
              for key, value in _backprop_params(example).items()}
    if len(index) == 2:
        params[name][index[0]][index[1]] += delta
    else:
        params[name][index[0]] += delta
    return backprop_pass(example["x"], **params, target=example["target"])["loss"]


def relative_error(exact, approximate):
    scale = max(abs(exact), abs(approximate))
    return 0.0 if scale == 0 else abs(exact - approximate) / scale


def gradient_check(example, check):
    parameter = check["parameter"]
    name, *index = parameter
    grads = backprop_pass(example["x"], **_backprop_params(example), target=example["target"])
    exact = grads["d" + name]
    for i in index:
        exact = exact[i]
    base = _perturbed_loss(example, parameter, 0.0)
    rows = []
    for h in check["steps"]:
        up = _perturbed_loss(example, parameter, h)
        down = _perturbed_loss(example, parameter, -h)
        forward = (up - base) / h
        central = (up - down) / (2 * h)
        rows.append({
            "h": h,
            "forward": forward,
            "central": central,
            "forward_error": relative_error(exact, forward),
            "central_error": relative_error(exact, central),
        })
    return {"exact": exact, "rows": rows}


def gradient_check_all(example, h=1e-6):
    grads = backprop_pass(example["x"], **_backprop_params(example), target=example["target"])
    results = []
    for name in ("w1", "b1", "w2", "b2"):
        value = example[name]
        indices = ([(i, j) for i in range(len(value)) for j in range(len(value[0]))]
                   if isinstance(value[0], list) else [(i,) for i in range(len(value))])
        for index in indices:
            exact = grads["d" + name]
            for i in index:
                exact = exact[i]
            parameter = (name, *index)
            numeric = (_perturbed_loss(example, parameter, h) - _perturbed_loss(example, parameter, -h)) / (2 * h)
            results.append({"parameter": parameter, "exact": exact, "numeric": numeric,
                            "error": relative_error(exact, numeric) if abs(exact) > 1e-12 else abs(numeric)})
    return results


def gradient_norms_by_depth(example):
    width, depth = example["width"], example["depth"]
    rng = random.Random(example["seed"])
    base = [[[rng.gauss(0, 1) / math.sqrt(width) for _ in range(width)] for _ in range(width)]
            for _ in range(depth)]
    x = [rng.gauss(0, 1) for _ in range(width)]
    upstream = [rng.gauss(0, 1) for _ in range(width)]
    activations = {
        "relu": (lambda z: max(0.0, z), lambda z: 1.0 if z > 0 else 0.0, math.sqrt(2)),
        "sigmoid": (sigmoid, lambda z: sigmoid(z) * (1 - sigmoid(z)), 1.0),
    }
    curves = []
    for case in example["cases"]:
        phi, dphi, init = activations[case["activation"]]
        scale = case["gain"] * init
        weights = [[[scale * w for w in row] for row in layer] for layer in base]
        h, pre = x, []
        for layer in weights:
            z = [dot_product(row, h) for row in layer]
            pre.append(z)
            h = [phi(v) for v in z]
        grad = upstream
        norms = [vector_norm(grad)]
        for layer, z in zip(reversed(weights), reversed(pre)):
            dz = [g * dphi(v) for g, v in zip(grad, z)]
            grad = [dot_product(column, dz) for column in transpose(layer)]
            norms.append(vector_norm(grad))
        top = norms[0]
        curves.append({**case, "norms": [n / top for n in reversed(norms)]})
    return curves


def optimizer_step(kind, params, grads, state, hyper):
    lr, decay = hyper["lr"], hyper.get("weight_decay", 0.0)
    beta1, beta2 = hyper.get("betas", (0.9, 0.999))
    eps = hyper.get("eps", 1e-8)
    state["step"] = state.get("step", 0) + 1
    t = state["step"]
    updated = []
    for i, (p, g) in enumerate(zip(params, grads)):
        if kind == "adamw":
            p *= 1 - lr * decay
        else:
            g += decay * p
        if kind == "sgd":
            p -= lr * g
        elif kind in ("momentum", "nesterov"):
            mu = hyper["momentum"]
            buf = state.setdefault("momentum_buffer", [None] * len(params))
            buf[i] = g if buf[i] is None else mu * buf[i] + g
            p -= lr * (g + mu * buf[i] if kind == "nesterov" else buf[i])
        elif kind == "rmsprop":
            alpha = hyper.get("alpha", 0.99)
            square = state.setdefault("square_avg", [0.0] * len(params))
            square[i] = alpha * square[i] + (1 - alpha) * g * g
            p -= lr * g / (math.sqrt(square[i]) + eps)
        else:
            m = state.setdefault("exp_avg", [0.0] * len(params))
            v = state.setdefault("exp_avg_sq", [0.0] * len(params))
            m[i] = beta1 * m[i] + (1 - beta1) * g
            v[i] = beta2 * v[i] + (1 - beta2) * g * g
            denom = math.sqrt(v[i]) / math.sqrt(1 - beta2**t) + eps
            p -= lr / (1 - beta1**t) * m[i] / denom
        updated.append(p)
    return updated


def optimizer_race(example):
    curvatures = example["curvatures"]

    def loss(point):
        return 0.5 * sum(a * x * x for a, x in zip(curvatures, point))

    runs = []
    for run in example["runs"]:
        point, state, path = list(example["start"]), {}, [list(example["start"])]
        for _ in range(example["steps"]):
            point = optimizer_step(run["kind"], point, [a * x for a, x in zip(curvatures, point)], state, run["hyper"])
            path.append(point)
        losses = [loss(q) for q in path]
        runs.append({**run, "path": path, "losses": losses, "final": losses[-1], "diverged": losses[-1] > losses[0]})
    return runs


def adam_trace(example):
    beta1, beta2 = example["betas"]
    hyper = {"lr": example["lr"], "betas": example["betas"], "eps": example["eps"]}
    params, state, rows = list(example["start"]), {}, []
    for t, grads in enumerate(example["grads"], start=1):
        params = optimizer_step("adam", params, grads, state, hyper)
        m, v = list(state["exp_avg"]), list(state["exp_avg_sq"])
        m_hat = [x / (1 - beta1**t) for x in m]
        v_hat = [x / (1 - beta2**t) for x in v]
        rows.append({
            "t": t, "grads": grads, "m": m, "v": v, "m_hat": m_hat, "v_hat": v_hat,
            "update": [-example["lr"] * a / (math.sqrt(b) + example["eps"]) for a, b in zip(m_hat, v_hat)],
            "params": params,
        })
    return rows


def uncorrected_step_ratio(betas, t):
    beta1, beta2 = betas
    return (1 - beta1**t) / math.sqrt(1 - beta2**t)


def weight_decay_paths(example):
    hyper = {"lr": example["lr"], "weight_decay": example["weight_decay"]}
    curves = []
    for kind in ("adam", "adamw"):
        for scale in example["scales"]:
            weight, state, values = [1.0], {}, [1.0]
            for k in range(example["steps"]):
                grad = scale if k % 2 == 0 else -scale
                weight = optimizer_step(kind, weight, [grad], state, hyper)
                values.append(weight[0])
            curves.append({"kind": kind, "scale": scale, "values": values})
    return curves


def optimizer_memory(parameters):
    rows = [
        ("SGD", 0, "none"),
        ("SGD with momentum", 1, "momentum_buffer"),
        ("RMSProp", 1, "square_avg"),
        ("Adam / AdamW", 2, "exp_avg, exp_avg_sq"),
    ]
    return [
        {"name": name, "tensors": tensors, "state": state, "bytes_per_param": 4 * tensors, "gigabytes": 4 * tensors * parameters / 1e9}
        for name, tensors, state in rows
    ]


def embedding_lookup(table, ids):
    if isinstance(ids, int):
        return list(table[ids])
    return [embedding_lookup(table, i) for i in ids]


def one_hot_rows(ids, size):
    return [[1 if i == j else 0 for j in range(size)] for i in ids]


def embedding_gradient(vocab_size, dim, ids, upstream, padding_idx=None, scale_grad_by_freq=False):
    flat_ids = [i for row in ids for i in row]
    flat_up = [u for row in upstream for u in row]
    grad = [[0.0] * dim for _ in range(vocab_size)]
    for i, u in zip(flat_ids, flat_up):
        if i == padding_idx:
            continue
        for d in range(dim):
            grad[i][d] += u[d]
    if scale_grad_by_freq:
        for i in set(flat_ids):
            count = flat_ids.count(i)
            grad[i] = [x / count for x in grad[i]]
    return grad


def skipgram_pairs(sentences, window):
    pairs = []
    for sentence in sentences:
        for i, center in enumerate(sentence):
            for j in range(max(0, i - window), min(len(sentence), i + window + 1)):
                if j != i:
                    pairs.append((center, sentence[j]))
    return pairs


def train_skipgram(example):
    sentences = [line.split() for line in example["corpus"]]
    vocab = sorted({word for sentence in sentences for word in sentence})
    index = {word: i for i, word in enumerate(vocab)}
    dim, lr = example["dim"], example["lr"]
    rng = random.Random(example["seed"])
    centers = [[rng.gauss(0, 0.5) for _ in range(dim)] for _ in vocab]
    contexts = [[rng.gauss(0, 0.5) for _ in range(dim)] for _ in vocab]
    pairs = [(index[a], index[b]) for a, b in skipgram_pairs(sentences, example["window"])]
    losses = []
    for _ in range(example["epochs"]):
        total = 0.0
        for center, target in pairs:
            v = centers[center]
            probs = categorical_from_logits([dot_product(v, u) for u in contexts])["probs"]
            total -= math.log(probs[target])
            grad_v = [0.0] * dim
            for k, u in enumerate(contexts):
                g = probs[k] - (1 if k == target else 0)
                for d in range(dim):
                    grad_v[d] += g * u[d]
                    u[d] -= lr * g * v[d]
            for d in range(dim):
                v[d] -= lr * grad_v[d]
        losses.append(total / len(pairs))
    return {
        "vocab": vocab,
        "vectors": dict(zip(vocab, centers)),
        "pairs": len(pairs),
        "losses": losses,
        "uniform_loss": math.log(len(vocab)),
    }


def nearest_words(vectors, word, count=3):
    scored = [(other, cosine_similarity(vectors[word], vec)) for other, vec in vectors.items() if other != word]
    return sorted(scored, key=lambda item: -item[1])[:count]


def tied_parameter_counts(vocab_size, dim, other_parameters):
    table = vocab_size * dim
    return {
        "table": table,
        "untied_total": 2 * table + other_parameters,
        "tied_total": table + other_parameters,
        "saved": table,
    }


def similarity_ranking(example):
    query = example["query"]
    rows = [
        {
            "name": name,
            "vector": vector,
            "dot": dot_product(query, vector),
            "norm": vector_norm(vector),
            "cosine": cosine_similarity(query, vector),
            "distance": vector_norm([a - b for a, b in zip(query, vector)]),
        }
        for name, vector in example["documents"].items()
    ]
    return {
        "rows": rows,
        "by_dot": [row["name"] for row in sorted(rows, key=lambda row: -row["dot"])],
        "by_cosine": [row["name"] for row in sorted(rows, key=lambda row: -row["cosine"])],
        "by_distance": [row["name"] for row in sorted(rows, key=lambda row: row["distance"])],
    }


TRAINING_EXAMPLE = {
    "vocab": ["a", "b", "c", "d"],
    "inputs": [0, 1, 2, 3, 1, 2],
    "targets": [1, 2, 3, -100, 2, 3],
    "ignore_index": -100,
    "lr": 0.2,
    "warmup": 2,
    "steps": 8,
    "min_lr": 0.02,
    "max_norm": 0.5,
    "weight_decay": 0.01,
}

SCALER_EXAMPLE = {"gradient": 1e-8, "scale": 2.0**16, "growth_interval": 3, "overflows": [False, False, False, True, False, False, False, False]}


def lr_at(step, base_lr, warmup, total, min_lr=0.0):
    if step < warmup:
        return base_lr * (step + 1) / warmup
    progress = (step - warmup) / (total - warmup)
    return min_lr + (base_lr - min_lr) * (1 + math.cos(math.pi * progress)) / 2


def lr_schedule(base_lr, warmup, total, min_lr=0.0):
    return [lr_at(step, base_lr, warmup, total, min_lr) for step in range(total)]


def smoothed_cross_entropy(logits, target, epsilon):
    log_probs = categorical_from_logits(logits)["log_probs"]
    nll = -log_probs[target]
    uniform = -sum(log_probs) / len(log_probs)
    return (1 - epsilon) * nll + epsilon * uniform


def masked_mean_loss(logit_rows, targets, ignore_index=-100):
    kept = [(row, t) for row, t in zip(logit_rows, targets) if t != ignore_index]
    losses = [logits_cross_entropy(row, t)["loss"] for row, t in kept]
    return {"losses": losses, "count": len(kept), "loss": sum(losses) / len(kept) if kept else math.nan}


def bigram_gradient(weights, inputs, targets, ignore_index=-100):
    count = sum(1 for t in targets if t != ignore_index)
    grad = [[0.0] * len(row) for row in weights]
    for x, t in zip(inputs, targets):
        if t == ignore_index:
            continue
        for j, g in enumerate(logits_cross_entropy(weights[x], t)["gradient"]):
            grad[x][j] += g / count
    return grad


def clip_by_global_norm(grads, max_norm):
    total = math.sqrt(sum(g * g for g in grads))
    coef = min(max_norm / (total + 1e-6), 1.0)
    return {"total_norm": total, "coef": coef, "grads": [g * coef for g in grads], "clipped": coef < 1.0}


def training_run(example):
    vocab = len(example["vocab"])
    flat = [0.0] * (vocab * vocab)
    state, rows = {}, []
    for step in range(example["steps"]):
        weights = [flat[i * vocab:(i + 1) * vocab] for i in range(vocab)]
        loss = masked_mean_loss([weights[x] for x in example["inputs"]], example["targets"], example["ignore_index"])
        grad = bigram_gradient(weights, example["inputs"], example["targets"], example["ignore_index"])
        clip = clip_by_global_norm([g for row in grad for g in row], example["max_norm"])
        lr = lr_at(step, example["lr"], example["warmup"], example["steps"], example["min_lr"])
        flat = optimizer_step("adamw", flat, clip["grads"], state, {"lr": lr, "weight_decay": example["weight_decay"]})
        rows.append({"step": step + 1, "loss": loss["loss"], "count": loss["count"], "grad_norm": clip["total_norm"], "coef": clip["coef"], "clipped": clip["clipped"], "lr": lr})
    final = [flat[i * vocab:(i + 1) * vocab] for i in range(vocab)]
    return {"rows": rows, "weights": final}


def accumulation_check(weights, micro_batches, ignore_index=-100):
    full_inputs = [x for inputs, _ in micro_batches for x in inputs]
    full_targets = [t for _, targets in micro_batches for t in targets]
    full = bigram_gradient(weights, full_inputs, full_targets, ignore_index)
    naive = [[0.0] * len(row) for row in weights]
    exact = [[0.0] * len(row) for row in weights]
    total = sum(1 for t in full_targets if t != ignore_index)
    for inputs, targets in micro_batches:
        kept = sum(1 for t in targets if t != ignore_index)
        grad = bigram_gradient(weights, inputs, targets, ignore_index)
        for i, row in enumerate(grad):
            for j, g in enumerate(row):
                naive[i][j] += g / len(micro_batches)
                exact[i][j] += g * kept / total
    flatten = lambda m: [v for row in m for v in row]
    return {"full": flatten(full), "naive": flatten(naive), "exact": flatten(exact)}


def to_float16(value):
    try:
        return struct.unpack("<e", struct.pack("<e", value))[0]
    except OverflowError:
        return math.inf


def scaled_gradient_roundtrip(gradient, scale):
    plain = to_float16(gradient)
    scaled = to_float16(gradient * scale)
    return {"plain": plain, "scaled": scaled, "recovered": scaled / scale}


def grad_scaler_trace(scale, growth_interval, overflows, growth_factor=2.0, backoff_factor=0.5):
    rows, good = [], 0
    for step, overflow in enumerate(overflows, start=1):
        used = scale
        if overflow:
            scale *= backoff_factor
            good = 0
        else:
            good += 1
            if good == growth_interval:
                scale *= growth_factor
                good = 0
        rows.append({"step": step, "scale": used, "overflow": overflow, "next_scale": scale})
    return rows


def training_memory(parameters, weight_bytes=4):
    rows = [
        ("Weights", weight_bytes),
        ("Gradients", weight_bytes),
        ("Adam exp_avg", 4),
        ("Adam exp_avg_sq", 4),
    ]
    out = [{"name": name, "bytes_per_param": b, "gigabytes": b * parameters / 1e9} for name, b in rows]
    total = sum(b for _, b in rows)
    out.append({"name": "Total, before activations", "bytes_per_param": total, "gigabytes": total * parameters / 1e9})
    return out


GPT2_SMALL = {"vocab": 50257, "context": 1024, "d_model": 768, "layers": 12, "heads": 12}

GENERATION_EXAMPLE = {"start": 0, "steps": 5}


def decoder_param_count(vocab, context, d_model, layers, d_ff=None, tied=True):
    d_ff = 4 * d_model if d_ff is None else d_ff
    token_table = vocab * d_model
    position_table = context * d_model
    block = transformer_param_count(d_model, 1, 0, d_ff)
    attention, feed_forward, layer_norm = block["attention"], block["feed_forward"], block["layer_norm"]
    per_block = attention + feed_forward + 2 * layer_norm
    blocks = layers * per_block
    head = 0 if tied else vocab * d_model
    return {
        "token_table": token_table,
        "position_table": position_table,
        "attention": attention,
        "feed_forward": feed_forward,
        "layer_norm": layer_norm,
        "per_block": per_block,
        "blocks": blocks,
        "final_norm": layer_norm,
        "head": head,
        "total": token_table + position_table + blocks + layer_norm + head,
    }


def next_token_pairs(tokens):
    return {"inputs": tokens[:-1], "targets": tokens[1:]}


def causal_prefix_check(example, keep):
    full = attention_weights(example, causal=True)
    cut = {key: value[:keep] for key, value in example.items() if key != "tokens"}
    short = attention_weights(cut, causal=True)
    bidirectional_full = attention_weights(example)
    bidirectional_short = attention_weights(cut)
    gap = lambda a, b: max(abs(x - y) for row_a, row_b in zip(a, b) for x, y in zip(row_a, row_b))
    return {
        "causal_gap": gap(full["outputs"][:keep], short["outputs"]),
        "bidirectional_gap": gap(bidirectional_full["outputs"][:keep], bidirectional_short["outputs"]),
    }


def sequence_nll(weights, tokens):
    pairs = next_token_pairs(tokens)
    losses = [logits_cross_entropy(weights[x], t)["loss"] for x, t in zip(pairs["inputs"], pairs["targets"])]
    mean = sum(losses) / len(losses)
    return {"losses": losses, "mean": mean, "perplexity": math.exp(mean)}


def greedy_generate(weights, start, steps):
    tokens = [start]
    for _ in range(steps):
        row = weights[tokens[-1]]
        tokens.append(max(range(len(row)), key=lambda j: row[j]))
    return tokens


def generation_positions(prompt_length, new_tokens, cached=False):
    if cached:
        return prompt_length + new_tokens - 1
    return sum(prompt_length + i for i in range(new_tokens))


DECODING_EXAMPLE = {
    "tokens": ["the", "a", "cat", "dog", "sat", "ran"],
    "logits": [3.0, 2.2, 1.6, 1.4, 0.2, -0.6],
}

SPECULATIVE_EXAMPLE = {
    "tokens": ["a", "b", "c", "d"],
    "target": [0.45, 0.30, 0.15, 0.10],
    "draft": [0.25, 0.40, 0.10, 0.25],
}

BEAM_STEP_PROBS = {
    "<s>": {"x": 0.5, "y": 0.4, "end": 0.1},
    "x": {"x": 0.3, "y": 0.3, "end": 0.4},
    "y": {"x": 0.0, "y": 0.0, "end": 1.0},
    "end": {},
}


def temperature_probs(logits, temperature):
    return categorical_from_logits([v / temperature for v in logits])["probs"]


def top_k_filter(probs, k):
    order = sorted(range(len(probs)), key=lambda i: (-probs[i], i))
    kept = sorted(order[:k])
    mass = sum(probs[i] for i in kept)
    return {
        "kept": kept,
        "mass": mass,
        "probs": [probs[i] / mass if i in kept else 0.0 for i in range(len(probs))],
    }


def top_p_filter(probs, p):
    order = sorted(range(len(probs)), key=lambda i: (-probs[i], i))
    kept = []
    cumulative = 0.0
    for index in order:
        if cumulative >= p:
            break
        kept.append(index)
        cumulative += probs[index]
    kept.sort()
    return {
        "kept": kept,
        "mass": cumulative,
        "probs": [probs[i] / cumulative if i in kept else 0.0 for i in range(len(probs))],
    }


def repeat_penalty(logits, seen, penalty):
    return [
        (v / penalty if v > 0 else v * penalty) if i in seen else v
        for i, v in enumerate(logits)
    ]


def constrained_probs(logits, allowed):
    masked = [v if i in allowed else -math.inf for i, v in enumerate(logits)]
    top = max(masked)
    weights = [math.exp(v - top) if v != -math.inf else 0.0 for v in masked]
    total = sum(weights)
    return [w / total for w in weights]


def sample_frequencies(probs, draws, seed):
    rng = random.Random(seed)
    counts = [0] * len(probs)
    for _ in range(draws):
        counts[inverse_cdf_sample(probs, rng.random())] += 1
    return [c / draws for c in counts]


def beam_search(step_probs, beam_width, max_len, start="<s>", end="end"):
    beams = [([start], 0.0)]
    finished = []
    for _ in range(max_len):
        candidates = []
        for tokens, score in beams:
            for token, p in step_probs[tokens[-1]].items():
                if p > 0:
                    candidates.append((tokens + [token], score + math.log(p)))
        candidates.sort(key=lambda c: -c[1])
        beams = []
        for tokens, score in candidates[:beam_width]:
            (finished if tokens[-1] == end else beams).append((tokens, score))
        if not beams:
            break
    return sorted(finished + beams, key=lambda c: -c[1])


def greedy_path(step_probs, max_len, start="<s>", end="end"):
    tokens, score = [start], 0.0
    for _ in range(max_len):
        token, p = max(step_probs[tokens[-1]].items(), key=lambda kv: kv[1])
        tokens.append(token)
        score += math.log(p)
        if token == end:
            break
    return tokens, score


def speculative_step(target, draft):
    overlap = [min(p, q) for p, q in zip(target, draft)]
    acceptance = sum(overlap)
    residual = [max(p - q, 0.0) for p, q in zip(target, draft)]
    norm = sum(residual)
    residual = [r / norm for r in residual]
    output = [o + (1 - acceptance) * r for o, r in zip(overlap, residual)]
    return {"acceptance": acceptance, "residual": residual, "output": output}


def speculative_tokens_per_pass(acceptance, draft_tokens):
    return sum(acceptance**i for i in range(draft_tokens + 1))


KV_CONFIG = {"layers": 32, "q_heads": 32, "kv_heads": 8, "head_dim": 128, "bytes_per_value": 2}

PAGED_EXAMPLE = {"lengths": [37, 120, 5, 64], "block_size": 16, "reserved": 128}


def cached_decode(example):
    keys, values, outputs = [], [], []
    cached_projections = uncached_projections = score_dots = 0
    for step, query in enumerate(example["queries"]):
        keys.append(example["keys"][step])
        values.append(example["values"][step])
        result = scaled_attention([query], keys, values)
        outputs.append(result["outputs"][0])
        cached_projections += 1
        uncached_projections += step + 1
        score_dots += step + 1
    full = attention_weights(example, causal=True)["outputs"]
    gap = max(abs(a - b) for row_a, row_b in zip(outputs, full) for a, b in zip(row_a, row_b))
    return {
        "outputs": outputs,
        "gap": gap,
        "cached_projections": cached_projections,
        "uncached_projections": uncached_projections,
        "score_dots": score_dots,
    }


def kv_cache_total_bytes(config, kv_heads, seq_len, batch=1):
    per_token = kv_cache_bytes_per_token(
        config["layers"], kv_heads, config["head_dim"], config["bytes_per_value"]
    )
    return per_token * seq_len * batch


def decode_attention_intensity(q_heads, kv_heads, bytes_per_value):
    return (4 * q_heads) / (2 * kv_heads * bytes_per_value)


def paged_allocation(lengths, block_size, reserved):
    blocks = [-(-length // block_size) for length in lengths]
    paged_slots = sum(blocks) * block_size
    used = sum(lengths)
    contiguous_slots = reserved * len(lengths)
    return {
        "blocks": blocks,
        "used": used,
        "paged_slots": paged_slots,
        "contiguous_slots": contiguous_slots,
        "paged_waste": paged_slots - used,
        "contiguous_waste": contiguous_slots - used,
    }


LEARNING_POINTS = [
    (0.5, 1.0), (1.0, 1.4), (1.4, 0.8), (1.8, 1.6), (2.4, 2.2),
    (3.6, 3.0), (4.0, 4.2), (4.6, 3.8), (5.0, 4.6),
]
LEARNING_TRUTH = [0, 0, 0, 0, 0, 1, 1, 1, 1]
LEARNING_LABELED = {0: 0, 5: 1}
LEARNING_TEXT = "the cat sat on the mat and the cat ran".split()


def _squared_distance(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def kmeans_run(points, centers, steps):
    centers = list(centers)
    history = []
    for _ in range(steps):
        assign = [
            min(range(len(centers)), key=lambda k: _squared_distance(p, centers[k])) for p in points
        ]
        inertia = sum(_squared_distance(p, centers[k]) for p, k in zip(points, assign))
        updated = []
        for k in range(len(centers)):
            members = [p for p, j in zip(points, assign) if j == k]
            updated.append(
                (sum(p[0] for p in members) / len(members), sum(p[1] for p in members) / len(members))
                if members
                else centers[k]
            )
        history.append({"assign": assign, "inertia": inertia, "centers": updated})
        if updated == centers:
            break
        centers = updated
    return history


def nearest_labeled(points, labeled):
    return [
        labeled[min(labeled, key=lambda i: _squared_distance(p, points[i]))] for p in points
    ]


def cluster_then_label(assign, labeled):
    names = {assign[i]: label for i, label in labeled.items()}
    return [names[a] for a in assign]


def prediction_accuracy(predicted, truth):
    return sum(p == t for p, t in zip(predicted, truth)) / len(truth)


def masked_pairs(tokens, positions):
    return [
        {"input": ["[MASK]" if j == i else t for j, t in enumerate(tokens)], "target": tokens[i]}
        for i in positions
    ]


def bigram_next_token_loss(tokens):
    pairs = next_token_pairs(tokens)
    counts = {}
    for before, after in zip(pairs["inputs"], pairs["targets"]):
        counts.setdefault(before, {}).setdefault(after, 0)
        counts[before][after] += 1
    losses = [
        -math.log(counts[b][a] / sum(counts[b].values()))
        for b, a in zip(pairs["inputs"], pairs["targets"])
    ]
    return {
        "pairs": len(losses),
        "mean_loss": sum(losses) / len(losses),
        "uniform_loss": math.log(len(set(tokens))),
    }


GENERALIZATION_X = [i / 9 for i in range(10)]
GENERALIZATION_NOISE = [0.25, -0.30, 0.15, 0.35, -0.20, -0.35, 0.25, 0.20, -0.30, 0.15]


def generalization_truth(x):
    return math.sin(2 * math.pi * x)


def generalization_train_targets():
    return [generalization_truth(x) + e for x, e in zip(GENERALIZATION_X, GENERALIZATION_NOISE)]


def _solve_linear(matrix, rhs):
    n = len(rhs)
    rows = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(rows[r][col]))
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for r in range(col + 1, n):
            factor = rows[r][col] / rows[col][col]
            for k in range(col, n + 1):
                rows[r][k] -= factor * rows[col][k]
    solution = [0.0] * n
    for i in range(n - 1, -1, -1):
        solution[i] = (rows[i][n] - sum(rows[i][j] * solution[j] for j in range(i + 1, n))) / rows[i][i]
    return solution


def polynomial_fit(xs, ys, degree):
    scaled = [2 * x - 1 for x in xs]
    design = [[u**k for k in range(degree + 1)] for u in scaled]
    gram = [
        [sum(row[i] * row[j] for row in design) for j in range(degree + 1)]
        for i in range(degree + 1)
    ]
    moments = [sum(row[i] * y for row, y in zip(design, ys)) for i in range(degree + 1)]
    return _solve_linear(gram, moments)


def polynomial_predict(weights, x):
    u = 2 * x - 1
    return sum(w * u**k for k, w in enumerate(weights))


def polynomial_mse(weights, xs, ys):
    return sum((polynomial_predict(weights, x) - y) ** 2 for x, y in zip(xs, ys)) / len(xs)


def generalization_rows(degrees):
    xs = GENERALIZATION_X
    ys = generalization_train_targets()
    heldout = [i / 49 for i in range(50)]
    shifted = [1 + i / 20 for i in range(11)]
    rows = []
    for degree in degrees:
        weights = polynomial_fit(xs, ys, degree)
        rows.append(
            {
                "degree": degree,
                "params": degree + 1,
                "train_mse": polynomial_mse(weights, xs, ys),
                "heldout_mse": polynomial_mse(weights, heldout, [generalization_truth(x) for x in heldout]),
                "shifted_mse": polynomial_mse(weights, shifted, [generalization_truth(x) for x in shifted]),
            }
        )
    return rows


SPLIT_LABELS = [1 if i in (3, 9, 14, 18) else 0 for i in range(20)]
SPLIT_UNLUCKY_ORDER = [0, 1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 19, 3, 9, 14, 18]
SPLIT_GROUPS = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5]
SPLIT_GROUP_ORDER = [0, 4, 7, 10, 13, 16, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17]
SPLIT_SERIES = [10.4, 12.1, 13.8, 16.2, 18.1, 19.7, 22.3, 23.8, 26.2, 28.1, 29.7, 32.2]
SPLIT_RANDOM_TEST_MONTHS = [1, 4, 6, 9]


def class_counts(labels, indices):
    counts = {}
    for i in indices:
        counts[labels[i]] = counts.get(labels[i], 0) + 1
    return counts


def stratified_allocation(labels, test_size):
    totals = class_counts(labels, range(len(labels)))
    exact = {c: n * test_size for c, n in totals.items()}
    allocation = {c: int(v) for c, v in exact.items()}
    missing = round(len(labels) * test_size) - sum(allocation.values())
    for c in sorted(exact, key=lambda c: exact[c] - allocation[c], reverse=True)[:missing]:
        allocation[c] += 1
    return allocation


def chance_test_misses_class(labels, test_count, label):
    others = sum(1 for y in labels if y != label)
    return math.comb(others, test_count) / math.comb(len(labels), test_count)


def leaked_group_records(groups, test_indices):
    test = set(test_indices)
    train_groups = {g for i, g in enumerate(groups) if i not in test}
    return sum(1 for i in test if groups[i] in train_groups)


def nearest_in_time_mse(series, train_indices, test_indices):
    errors = []
    for t in test_indices:
        nearest = min(train_indices, key=lambda u: (abs(u - t), u))
        errors.append((series[nearest] - series[t]) ** 2)
    return sum(errors) / len(errors)


def accuracy_standard_error(accuracy, count):
    return math.sqrt(accuracy * (1 - accuracy) / count)


PREPROCESS_AGE = [22, 35, 47, 51, 60]
PREPROCESS_INCOME = [30000, 52000, 61000, 90000, 250000]
PREPROCESS_COLORS = ["red", "green", "blue", "green", "red"]


def column_mean_std(values):
    mean = sum(values) / len(values)
    return mean, math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


def standardize_with(values, mean, std):
    return [(v - mean) / std for v in values]


def min_max_scale(values, low, high):
    return [(v - low) / (high - low) for v in values]


def median(values):
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2


def one_hot_encode(values):
    categories = sorted(set(values))
    return categories, [[1 if v == c else 0 for c in categories] for v in values]


def ordinal_encode(values):
    categories = sorted(set(values))
    return [categories.index(v) for v in values]


def log10_column(values):
    return [math.log10(v) for v in values]


def pair_distance(a, b):
    return math.dist(a, b)


LEAK_DUP_TRAIN = [("a", 1), ("b", 0), ("c", 0), ("d", 1), ("e", 0), ("f", 0), ("g", 1), ("h", 0)]
LEAK_DUP_TEST = [
    ("a", 1), ("d", 1), ("g", 1), ("b", 0),
    ("x1", 0), ("x2", 1), ("x3", 0), ("x4", 1), ("x5", 0), ("x6", 1),
]
LEAK_LOAN_DEFAULTED = [1, 0, 0, 1, 0, 1, 0, 0, 1, 0]
LEAK_LOAN_NOTICES = [3, 0, 0, 2, 0, 4, 0, 0, 1, 0]
LEAK_LOAN_DEBT_RATIO = [0.48, 0.52, 0.35, 0.55, 0.41, 0.43, 0.60, 0.30, 0.38, 0.45]


def noise_feature_table(rows, features, seed):
    rng = random.Random(seed)
    labels = [rng.random() < 0.5 for _ in range(rows)]
    table = [[rng.random() < 0.5 for _ in range(features)] for _ in range(rows)]
    return table, labels


def feature_accuracy(table, labels, feature, row_ids):
    return sum(1 for i in row_ids if table[i][feature] == labels[i]) / len(row_ids)


def best_noise_feature(table, labels, row_ids):
    best, best_hits = 0, -1
    for j in range(len(table[0])):
        hits = sum(1 for i in row_ids if table[i][j] == labels[i])
        if hits > best_hits:
            best, best_hits = j, hits
    return best, best_hits / len(row_ids)


def leaky_selection_demo(rows=40, features=500, seed=3):
    table, labels = noise_feature_table(rows, features, seed)
    train = list(range(rows // 2))
    test = list(range(rows // 2, rows))
    leaky, _ = best_noise_feature(table, labels, train + test)
    honest, honest_fit = best_noise_feature(table, labels, train)
    return {
        "leaky_feature": leaky,
        "leaky_test_accuracy": feature_accuracy(table, labels, leaky, test),
        "honest_feature": honest,
        "honest_train_accuracy": honest_fit,
        "honest_test_accuracy": feature_accuracy(table, labels, honest, test),
    }


def leaky_selection_average(trials=100, rows=40, features=500):
    runs = [leaky_selection_demo(rows, features, seed) for seed in range(trials)]
    return {
        key: sum(run[key] for run in runs) / trials
        for key in ("leaky_test_accuracy", "honest_train_accuracy", "honest_test_accuracy")
    }


def duplicate_overlap(train, test):
    seen = {key for key, _ in train}
    return sum(1 for key, _ in test if key in seen)


def lookup_accuracy(train, test, skip_seen=False):
    memory = dict(train)
    labels = [label for _, label in train]
    majority = 1 if sum(labels) * 2 > len(labels) else 0
    rows = [(key, label) for key, label in test if not (skip_seen and key in memory)]
    return sum(1 for key, label in rows if memory.get(key, majority) == label) / len(rows)


def best_threshold_rule(values, labels):
    best = (None, -1.0)
    for low, high in zip(sorted(set(values)), sorted(set(values))[1:]):
        cut = (low + high) / 2
        hits = sum(1 for v, y in zip(values, labels) if (v > cut) == bool(y))
        if hits / len(values) > best[1]:
            best = (cut, hits / len(values))
    return best


METRIC_LABELS = [1, 1, 0, 1, 0, 1, 0, 0, 0, 0]
METRIC_SCORES = [0.95, 0.85, 0.80, 0.65, 0.55, 0.45, 0.40, 0.30, 0.20, 0.10]
METRIC_CLASS_COUNTS = {"cat": (8, 2, 2), "dog": (1, 1, 4), "bird": (0, 0, 3)}


def confusion_counts(labels, scores, threshold):
    tp = sum(1 for y, s in zip(labels, scores) if y == 1 and s >= threshold)
    fp = sum(1 for y, s in zip(labels, scores) if y == 0 and s >= threshold)
    fn = sum(1 for y, s in zip(labels, scores) if y == 1 and s < threshold)
    tn = len(labels) - tp - fp - fn
    return tp, fp, fn, tn


def precision_recall_f1(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 0.0
    return precision, recall, f1


def roc_points(labels, scores):
    positives = sum(labels)
    negatives = len(labels) - positives
    points = [(0.0, 0.0)]
    for cut in sorted(set(scores), reverse=True):
        tp, fp, _, _ = confusion_counts(labels, scores, cut)
        points.append((fp / negatives, tp / positives))
    return points


def trapezoid_area(points):
    return sum((x1 - x0) * (y0 + y1) / 2 for (x0, y0), (x1, y1) in zip(points, points[1:]))


def rank_auc(labels, scores):
    pos = [s for y, s in zip(labels, scores) if y == 1]
    neg = [s for y, s in zip(labels, scores) if y == 0]
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def pr_points(labels, scores):
    positives = sum(labels)
    points = []
    for cut in sorted(set(scores), reverse=True):
        tp, fp, _, _ = confusion_counts(labels, scores, cut)
        points.append((tp / positives, tp / (tp + fp)))
    return points


def average_precision(labels, scores):
    previous_recall, total = 0.0, 0.0
    for recall, precision in pr_points(labels, scores):
        total += (recall - previous_recall) * precision
        previous_recall = recall
    return total


def binary_log_loss(labels, probabilities):
    return -sum(
        math.log(p) if y == 1 else math.log(1 - p) for y, p in zip(labels, probabilities)
    ) / len(labels)


def averaged_f1(class_counts):
    per_class = {name: precision_recall_f1(tp, fp, fn)[2] for name, (tp, fp, fn) in class_counts.items()}
    macro = sum(per_class.values()) / len(per_class)
    tp = sum(c[0] for c in class_counts.values())
    fp = sum(c[1] for c in class_counts.values())
    fn = sum(c[2] for c in class_counts.values())
    return per_class, macro, precision_recall_f1(tp, fp, fn)[2]


def kfold_splits(n, k):
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    splits = []
    start = 0
    for size in sizes:
        test = list(range(start, start + size))
        train = [i for i in range(n) if i < start or i >= start + size]
        splits.append((train, test))
        start += size
    return splits


def stratified_kfold_splits(labels, k):
    order = sorted(labels)
    classes = sorted(set(labels))
    allocation = [[order[i::k].count(c) for c in classes] for i in range(k)]
    tests = [[] for _ in range(k)]
    for ci, c in enumerate(classes):
        members = [i for i, y in enumerate(labels) if y == c]
        start = 0
        for fold in range(k):
            take = allocation[fold][ci]
            tests[fold].extend(members[start:start + take])
            start += take
    n = len(labels)
    return [([i for i in range(n) if i not in set(t)], sorted(t)) for t in tests]


def group_kfold_splits(groups, k):
    sizes = {}
    for g in groups:
        sizes[g] = sizes.get(g, 0) + 1
    order = sorted(sizes, key=lambda g: (-sizes[g], g))
    loads = [0] * k
    assigned = {}
    for g in order:
        fold = loads.index(min(loads))
        assigned[g] = fold
        loads[fold] += sizes[g]
    n = len(groups)
    return [
        ([i for i in range(n) if assigned[groups[i]] != f], [i for i in range(n) if assigned[groups[i]] == f])
        for f in range(k)
    ]


def time_series_splits(n, k):
    test_size = n // (k + 1)
    splits = []
    for start in range(n - k * test_size, n, test_size):
        splits.append((list(range(start)), list(range(start, start + test_size))))
    return splits


def cv_summary(scores):
    mean = sum(scores) / len(scores)
    spread = (sum((x - mean) ** 2 for x in scores) / (len(scores) - 1)) ** 0.5
    return mean, spread


def centroid_cv_data(rows=60, seed=4):
    rng = random.Random(seed)
    return [(rng.gauss(1.0 if i % 2 else -1.0, 1.4), i % 2) for i in range(rows)]


def centroid_fold_score(data, train, test):
    low = [data[i][0] for i in train if data[i][1] == 0]
    high = [data[i][0] for i in train if data[i][1] == 1]
    cut = (sum(low) / len(low) + sum(high) / len(high)) / 2
    return sum((data[i][0] > cut) == bool(data[i][1]) for i in test) / len(test)


def centroid_cv_scores(data, k, seed=None):
    order = list(range(len(data)))
    if seed is not None:
        random.Random(seed).shuffle(order)
    shuffled = [data[i] for i in order]
    return [centroid_fold_score(shuffled, tr, te) for tr, te in kfold_splits(len(shuffled), k)]


def repeated_cv_means(data, k, repeats=100):
    return [sum(s) / k for s in (centroid_cv_scores(data, k, seed=r) for r in range(repeats))]


def selection_bias_demo(rows=40, candidates=50, k=5, trials=200, seed=6):
    rng = random.Random(seed)
    best_total = nested_total = 0.0
    for _ in range(trials):
        truth = [rng.randint(0, 1) for _ in range(rows)]
        guesses = [[rng.randint(0, 1) for _ in range(rows)] for _ in range(candidates)]
        hits = [[int(g[i] == truth[i]) for i in range(rows)] for g in guesses]
        best_total += max(sum(h) for h in hits) / rows
        correct = 0
        for train, test in kfold_splits(rows, k):
            pick = max(range(candidates), key=lambda c: sum(hits[c][i] for i in train))
            correct += sum(hits[pick][i] for i in test)
        nested_total += correct / rows
    return best_total / trials, nested_total / trials


TREE_TOY_ROWS = [
    ((2.0, 7.0), 0), ((3.0, 8.0), 0), ((3.0, 3.0), 0), ((4.0, 5.0), 0),
    ((5.0, 2.0), 1), ((6.0, 6.0), 1), ((6.0, 1.0), 1), ((7.0, 4.0), 1),
    ((8.0, 8.0), 1), ((9.0, 3.0), 1), ((5.0, 9.0), 0), ((4.0, 8.0), 1),
]


def label_counts(labels, classes=(0, 1)):
    return [sum(1 for y in labels if y == c) for c in classes]


def gini_impurity(counts):
    n = sum(counts)
    return 1.0 - sum((c / n) ** 2 for c in counts)


def entropy_impurity(counts):
    n = sum(counts)
    return -sum((c / n) * math.log2(c / n) for c in counts if c > 0)


def split_candidates(rows, feature, criterion=gini_impurity):
    values = sorted({x[feature] for x, _ in rows})
    parent = criterion(label_counts([y for _, y in rows]))
    n = len(rows)
    out = []
    for lo, hi in zip(values, values[1:]):
        threshold = lo / 2.0 + hi / 2.0
        left = [y for x, y in rows if x[feature] <= threshold]
        right = [y for x, y in rows if x[feature] > threshold]
        li = criterion(label_counts(left))
        ri = criterion(label_counts(right))
        weighted = (len(left) * li + len(right) * ri) / n
        out.append({
            "feature": feature, "threshold": threshold, "n_left": len(left), "n_right": len(right),
            "left_impurity": li, "right_impurity": ri, "weighted": weighted, "gain": parent - weighted,
        })
    return out


def best_split(rows, criterion=gini_impurity, min_samples_leaf=1):
    best = None
    n_features = len(rows[0][0])
    for feature in range(n_features):
        for cand in split_candidates(rows, feature, criterion):
            if cand["n_left"] < min_samples_leaf or cand["n_right"] < min_samples_leaf:
                continue
            if best is None or cand["gain"] > best["gain"] + 1e-12:
                best = cand
    return best


def grow_tree(rows, criterion=gini_impurity, max_depth=None, min_samples_split=2,
              min_samples_leaf=1, total=None, depth=0):
    total = total if total is not None else len(rows)
    counts = label_counts([y for _, y in rows])
    node = {
        "n": len(rows), "counts": counts, "impurity": criterion(counts), "depth": depth,
        "total": total, "prediction": counts.index(max(counts)), "feature": None,
    }
    stop = (
        (max_depth is not None and depth >= max_depth)
        or len(rows) < min_samples_split
        or len(rows) < 2 * min_samples_leaf
        or node["impurity"] <= 1e-12
    )
    split = None if stop else best_split(rows, criterion, min_samples_leaf)
    if split is None:
        return node
    f, t = split["feature"], split["threshold"]
    node.update(feature=f, threshold=t)
    node["left"] = grow_tree([r for r in rows if r[0][f] <= t], criterion, max_depth,
                             min_samples_split, min_samples_leaf, total, depth + 1)
    node["right"] = grow_tree([r for r in rows if r[0][f] > t], criterion, max_depth,
                              min_samples_split, min_samples_leaf, total, depth + 1)
    return node


def tree_predict(node, x):
    while node["feature"] is not None:
        node = node["left"] if x[node["feature"]] <= node["threshold"] else node["right"]
    return node["prediction"]


def tree_accuracy(node, rows):
    return sum(tree_predict(node, x) == y for x, y in rows) / len(rows)


def tree_leaves(node):
    if node["feature"] is None:
        return [node]
    return tree_leaves(node["left"]) + tree_leaves(node["right"])


def tree_depth(node):
    if node["feature"] is None:
        return 0
    return 1 + max(tree_depth(node["left"]), tree_depth(node["right"]))


def tree_nodes(node):
    if node["feature"] is None:
        return [node]
    return [node] + tree_nodes(node["left"]) + tree_nodes(node["right"])


def tree_feature_importances(node, n_features):
    totals = [0.0] * n_features
    for nd in tree_nodes(node):
        if nd["feature"] is not None:
            totals[nd["feature"]] += (
                nd["n"] * nd["impurity"]
                - nd["left"]["n"] * nd["left"]["impurity"]
                - nd["right"]["n"] * nd["right"]["impurity"]
            ) / node["n"]
    norm = sum(totals)
    return [t / norm for t in totals] if norm > 0 else totals


def _subtree_r(node):
    if node["feature"] is None:
        return node["n"] * node["impurity"] / node["total"]
    return _subtree_r(node["left"]) + _subtree_r(node["right"])


def _copy_tree(node):
    out = dict(node)
    if "left" in node:
        out["left"] = _copy_tree(node["left"])
        out["right"] = _copy_tree(node["right"])
    return out


def cost_complexity_path(tree):
    work = _copy_tree(tree)
    path = [(0.0, len(tree_leaves(work)), _subtree_r(work))]
    while work["feature"] is not None:
        weakest = None
        for nd in tree_nodes(work):
            if nd["feature"] is None:
                continue
            r_node = nd["n"] * nd["impurity"] / nd["total"]
            alpha = (r_node - _subtree_r(nd)) / (len(tree_leaves(nd)) - 1)
            if weakest is None or alpha < weakest[0] - 1e-15:
                weakest = (alpha, nd)
        alpha, nd = weakest
        for key in ("threshold", "left", "right"):
            nd.pop(key, None)
        nd["feature"] = None
        path.append((alpha, len(tree_leaves(work)), _subtree_r(work)))
    return path


def prune_tree(tree, ccp_alpha):
    work = _copy_tree(tree)
    while work["feature"] is not None:
        weakest = None
        for nd in tree_nodes(work):
            if nd["feature"] is None:
                continue
            r_node = nd["n"] * nd["impurity"] / nd["total"]
            alpha = (r_node - _subtree_r(nd)) / (len(tree_leaves(nd)) - 1)
            if weakest is None or alpha < weakest[0] - 1e-15:
                weakest = (alpha, nd)
        if weakest[0] > ccp_alpha:
            break
        nd = weakest[1]
        for key in ("threshold", "left", "right"):
            nd.pop(key, None)
        nd["feature"] = None
    return work


def noisy_diagonal_rows(n, seed, flip=0.15, extra_noise_feature=False):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        a, b = rng.uniform(0, 10), rng.uniform(0, 10)
        y = int(a + b > 10)
        if rng.random() < flip:
            y = 1 - y
        x = (a, b, rng.random()) if extra_noise_feature else (a, b)
        rows.append((x, y))
    return rows


def depth_sweep(depths=(1, 2, 3, 4, 6, None), seed=3):
    train = noisy_diagonal_rows(60, seed)
    test = noisy_diagonal_rows(400, seed + 100)
    out = []
    for d in depths:
        t = grow_tree(train, max_depth=d)
        out.append((d, len(tree_leaves(t)), tree_accuracy(t, train), tree_accuracy(t, test)))
    return out


def importance_rows(n, seed, flip=0.2):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        signal = rng.uniform(0, 10)
        y = int(signal > 5)
        if rng.random() < flip:
            y = 1 - y
        rows.append(((signal, rng.uniform(0, 10), float(rng.randint(0, 1))), y))
    return rows


def importance_demo(seeds=20, n=80):
    totals = [0.0, 0.0, 0.0]
    for s in range(seeds):
        imp = tree_feature_importances(grow_tree(importance_rows(n, s)), 3)
        totals = [a + b for a, b in zip(totals, imp)]
    return [t / seeds for t in totals]


def regression_split_demo():
    xs = [1, 2, 3, 4, 5, 6, 7, 8]
    ys = [1.0, 1.4, 1.1, 1.3, 3.8, 4.2, 4.0, 4.4]
    n = len(ys)

    def sse(v):
        m = sum(v) / len(v)
        return sum((a - m) ** 2 for a in v)

    rows = []
    for i in range(1, n):
        left, right = ys[:i], ys[i:]
        rows.append({
            "threshold": (xs[i - 1] + xs[i]) / 2, "mean_left": sum(left) / len(left),
            "mean_right": sum(right) / len(right), "sse": sse(left) + sse(right),
        })
    return xs, ys, rows, sse(ys)


BOOST_XS = [1, 2, 3, 4, 5, 6, 7, 8]
BOOST_YS = [1.2, 1.9, 3.1, 3.8, 4.1, 3.4, 2.2, 1.5]
NEWTON_XS = [1, 2, 3, 4, 5, 6, 7, 8]
NEWTON_LABELS = [0, 0, 0, 1, 0, 1, 1, 1]


def _boost_mean(values):
    return sum(values) / len(values)


def best_regression_stump(xs, targets):
    pairs = sorted(zip(xs, targets))
    best = None
    for i in range(1, len(pairs)):
        if pairs[i - 1][0] == pairs[i][0]:
            continue
        left = [t for _, t in pairs[:i]]
        right = [t for _, t in pairs[i:]]
        ml, mr = _boost_mean(left), _boost_mean(right)
        sse = sum((t - ml) ** 2 for t in left) + sum((t - mr) ** 2 for t in right)
        threshold = pairs[i - 1][0] / 2 + pairs[i][0] / 2
        if best is None or sse < best["sse"] - 1e-12:
            best = {"threshold": threshold, "left": ml, "right": mr, "sse": sse}
    return best


def boost_stumps(xs, ys, rounds, learning_rate):
    init = _boost_mean(ys)
    preds = [init] * len(ys)
    history = []
    for _ in range(rounds):
        residuals = [y - p for y, p in zip(ys, preds)]
        stump = best_regression_stump(xs, residuals)
        preds = [
            p + learning_rate * (stump["left"] if x <= stump["threshold"] else stump["right"])
            for x, p in zip(xs, preds)
        ]
        history.append({
            "residuals": residuals, "threshold": stump["threshold"],
            "left": stump["left"], "right": stump["right"],
            "predictions": list(preds),
            "mse": _boost_mean([(y - p) ** 2 for y, p in zip(ys, preds)]),
        })
    return init, history


def grow_regression_tree(xs, ys, max_depth, depth=0):
    mean = _boost_mean(ys)
    if depth >= max_depth or len(ys) < 2 or max(ys) - min(ys) <= 1e-12:
        return {"value": mean}
    stump = best_regression_stump(xs, ys)
    if stump is None:
        return {"value": mean}
    pairs = list(zip(xs, ys))
    left = [(x, y) for x, y in pairs if x <= stump["threshold"]]
    right = [(x, y) for x, y in pairs if x > stump["threshold"]]
    return {
        "threshold": stump["threshold"],
        "left": grow_regression_tree([p[0] for p in left], [p[1] for p in left], max_depth, depth + 1),
        "right": grow_regression_tree([p[0] for p in right], [p[1] for p in right], max_depth, depth + 1),
    }


def regression_tree_predict(tree, x):
    while "value" not in tree:
        tree = tree["left"] if x <= tree["threshold"] else tree["right"]
    return tree["value"]


def wavy_rows(n, seed, noise=0.4):
    rng = random.Random(seed)
    xs = [rng.uniform(0, 10) for _ in range(n)]
    return xs, [math.sin(x) + rng.gauss(0, noise) for x in xs]


def boosting_curve(learning_rate, rounds, depth=2, seed=5, n_train=40, n_test=400):
    train_x, train_y = wavy_rows(n_train, seed)
    test_x, test_y = wavy_rows(n_test, seed + 100)
    init = _boost_mean(train_y)
    train_pred = [init] * n_train
    test_pred = [init] * n_test
    curve = []
    for _ in range(rounds):
        residuals = [y - p for y, p in zip(train_y, train_pred)]
        tree = grow_regression_tree(train_x, residuals, depth)
        train_pred = [p + learning_rate * regression_tree_predict(tree, x) for x, p in zip(train_x, train_pred)]
        test_pred = [p + learning_rate * regression_tree_predict(tree, x) for x, p in zip(test_x, test_pred)]
        curve.append((
            _boost_mean([(y - p) ** 2 for y, p in zip(train_y, train_pred)]),
            _boost_mean([(y - p) ** 2 for y, p in zip(test_y, test_pred)]),
        ))
    return curve


def newton_scan(xs, grads, hessians, reg_lambda=1.0, gamma=0.0, min_child_weight=0.0):
    total_g, total_h = sum(grads), sum(hessians)
    parent = total_g ** 2 / (total_h + reg_lambda)
    candidates = []
    for i in range(1, len(xs)):
        gl, hl = sum(grads[:i]), sum(hessians[:i])
        gr, hr = total_g - gl, total_h - hl
        valid = hl > 0 and hr > 0 and hl >= min_child_weight and hr >= min_child_weight
        loss_chg = gl ** 2 / (hl + reg_lambda) + gr ** 2 / (hr + reg_lambda) - parent
        candidates.append({
            "threshold": xs[i - 1] / 2 + xs[i] / 2, "g_left": gl, "h_left": hl,
            "g_right": gr, "h_right": hr, "loss_chg": loss_chg,
            "w_left": -gl / (hl + reg_lambda), "w_right": -gr / (hr + reg_lambda),
            "valid": valid, "kept": valid and loss_chg >= gamma,
        })
    return {"g": total_g, "h": total_h, "root_weight": -total_g / (total_h + reg_lambda),
            "root_gain": parent, "candidates": candidates}


def _median(values):
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2


def noisy_sine_rows(n, seed, noise=0.3):
    rng = random.Random(seed)
    xs = [rng.uniform(0, 1) for _ in range(n)]
    return xs, [math.sin(2 * math.pi * x) + rng.gauss(0, noise) for x in xs]


def poly_ridge_fit(xs, ys, degree, alpha=0.0):
    scaled = [2 * x - 1 for x in xs]
    design = [[u**k for k in range(degree + 1)] for u in scaled]
    gram = [
        [sum(row[i] * row[j] for row in design) + (alpha if i == j and i > 0 else 0.0)
         for j in range(degree + 1)]
        for i in range(degree + 1)
    ]
    moments = [sum(row[i] * y for row, y in zip(design, ys)) for i in range(degree + 1)]
    return _solve_linear(gram, moments)


def _poly_errors(degree, n, alpha, noise, seed, val_xs, val_ys):
    xs, ys = noisy_sine_rows(n, seed, noise)
    weights = poly_ridge_fit(xs, ys, degree, alpha)
    return polynomial_mse(weights, xs, ys), polynomial_mse(weights, val_xs, val_ys)


def polynomial_learning_curve(degree, sizes, alpha=0.0, noise=0.3, repeats=30):
    val_xs, val_ys = noisy_sine_rows(400, 10_000, noise)
    rows = []
    for n in sizes:
        pairs = [_poly_errors(degree, n, alpha, noise, 100 * n + r, val_xs, val_ys) for r in range(repeats)]
        rows.append((n, _median([p[0] for p in pairs]), _median([p[1] for p in pairs])))
    return rows


def ridge_strength_sweep(alphas, degree=9, n=15, noise=0.3, repeats=30):
    val_xs, val_ys = noisy_sine_rows(400, 10_000, noise)
    rows = []
    for alpha in alphas:
        pairs = [_poly_errors(degree, n, alpha, noise, 100 * n + r, val_xs, val_ys) for r in range(repeats)]
        rows.append((alpha, _median([p[0] for p in pairs]), _median([p[1] for p in pairs])))
    return rows


def memorization_demo(n_train=60, n_test=400, seed=3):
    rng = random.Random(seed)

    def draw(n):
        return [([rng.uniform(0, 10), rng.uniform(0, 10)], rng.randint(0, 1)) for _ in range(n)]

    train, test = draw(n_train), draw(n_test)
    tree = grow_tree(train)
    return {
        "train_accuracy": tree_accuracy(tree, train),
        "test_accuracy": tree_accuracy(tree, test),
        "leaves": len(tree_leaves(tree)),
        "majority_train": max(label_counts([y for _, y in train])) / n_train,
    }


def bias_variance_decomposition(degree, n=25, alpha=0.0, noise=0.3, repeats=200, bags=1, grid_size=40):
    grid = [(i + 0.5) / grid_size for i in range(grid_size)]
    truth = [generalization_truth(x) for x in grid]
    predictions = []
    for r in range(repeats):
        xs, ys = noisy_sine_rows(n, 7000 + r, noise)
        if bags == 1:
            members = [poly_ridge_fit(xs, ys, degree, alpha)]
        else:
            rng = random.Random(9000 + r)
            members = []
            for _ in range(bags):
                pick = [rng.randrange(n) for _ in range(n)]
                members.append(poly_ridge_fit([xs[i] for i in pick], [ys[i] for i in pick], degree, alpha))
        predictions.append([_boost_mean([polynomial_predict(w, x) for w in members]) for x in grid])
    per_x = []
    for g in range(grid_size):
        column = [row[g] for row in predictions]
        mean = _boost_mean(column)
        per_x.append({
            "x": grid[g], "mean": mean,
            "bias2": (mean - truth[g]) ** 2,
            "variance": _boost_mean([(v - mean) ** 2 for v in column]),
            "error": _boost_mean([(v - truth[g]) ** 2 for v in column]),
        })
    return {
        "bias2": _boost_mean([c["bias2"] for c in per_x]),
        "variance": _boost_mean([c["variance"] for c in per_x]),
        "noise": noise ** 2,
        "error": _boost_mean([c["error"] for c in per_x]),
        "per_x": per_x,
    }


SPARSE_TRUE_WEIGHTS = [3.0, -2.0, 1.5, 0.0, 0.0, 0.0, 0.0, 0.0]


def sparse_regression_data(n=40, seed=3, noise=1.0):
    rng = random.Random(seed)
    x = [[rng.gauss(0, 1) for _ in SPARSE_TRUE_WEIGHTS] for _ in range(n)]
    y = [sum(w * v for w, v in zip(SPARSE_TRUE_WEIGHTS, row)) + rng.gauss(0, noise) for row in x]
    return x, y


def penalized_fits(ridge_alpha, lasso_alpha, n=40, seed=3, noise=1.0):
    x, y = sparse_regression_data(n, seed, noise)
    z = standardize(x)["z"]
    mean_y = sum(y) / n
    centered = [t - mean_y for t in y]
    return {
        "ols": ridge_coefficients(z, centered, 0.0),
        "ridge": ridge_coefficients(z, centered, ridge_alpha),
        "lasso": lasso_coefficients(z, centered, lasso_alpha),
    }


def lasso_sparsity_path(alphas, n=40, seed=3, noise=1.0):
    x, y = sparse_regression_data(n, seed, noise)
    z = standardize(x)["z"]
    mean_y = sum(y) / n
    centered = [t - mean_y for t in y]
    rows = []
    for alpha in alphas:
        coef = lasso_coefficients(z, centered, alpha)
        rows.append((alpha, sum(1 for c in coef if c != 0.0), coef))
    return rows


def dropout_statistics(values, p, trials=4000, seed=0):
    rng = random.Random(seed)
    scale = 1.0 / (1.0 - p)
    sums = [0.0] * len(values)
    squares = [0.0] * len(values)
    kept = 0
    for _ in range(trials):
        for i, v in enumerate(values):
            out = v * scale if rng.random() >= p else 0.0
            kept += out != 0.0
            sums[i] += out
            squares[i] += out * out
    means = [t / trials for t in sums]
    variances = [q / trials - m * m for q, m in zip(squares, means)]
    return {
        "means": means,
        "variances": variances,
        "exact_variances": [v * v * p / (1.0 - p) for v in values],
        "kept_fraction": kept / (trials * len(values)),
        "scale": scale,
    }


def adam_weight_decay_comparison(grad, w0=5.0, lr=0.01, weight_decay=0.1, steps=300, beta1=0.9, beta2=0.999, eps=1e-8):
    def run(mode):
        w, m, v = w0, 0.0, 0.0
        for t in range(1, steps + 1):
            g = grad if t % 2 else -grad
            if mode == "l2":
                g += weight_decay * w
            elif mode == "decoupled":
                w *= 1.0 - lr * weight_decay
            m = beta1 * m + (1 - beta1) * g
            v = beta2 * v + (1 - beta2) * g * g
            w -= lr * (m / (1 - beta1**t)) / (math.sqrt(v / (1 - beta2**t)) + eps)
        return w

    plain = run("none")
    return {
        "none": plain,
        "l2": run("l2"),
        "decoupled": run("decoupled"),
        "l2_extra_shrink": plain - run("l2"),
        "decoupled_extra_shrink": plain - run("decoupled"),
    }


def gelu_exact(x):
    return 0.5 * x * (1.0 + math.erf(x / math.sqrt(2.0)))


def gelu_tanh(x):
    return 0.5 * x * (1.0 + math.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * x**3)))


def silu(x):
    return x * sigmoid(x)


def softplus(x):
    return max(x, 0.0) + math.log1p(math.exp(-abs(x)))


def _gelu_derivative(x):
    cdf = 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
    pdf = math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)
    return cdf + x * pdf


def _silu_derivative(x):
    s = sigmoid(x)
    return s * (1.0 + x * (1.0 - s))


ACTIVATIONS = [
    ("sigmoid", sigmoid, lambda x: sigmoid(x) * (1.0 - sigmoid(x))),
    ("tanh", math.tanh, lambda x: 1.0 - math.tanh(x) ** 2),
    ("relu", lambda x: max(0.0, x), lambda x: 1.0 if x > 0 else 0.0),
    ("leaky_relu", lambda x: x if x > 0 else 0.01 * x, lambda x: 1.0 if x > 0 else 0.01),
    ("gelu", gelu_exact, _gelu_derivative),
    ("silu", silu, _silu_derivative),
    ("softplus", softplus, sigmoid),
]


def activation_table(xs):
    return [
        {"name": name, "values": [f(x) for x in xs], "slopes": [d(x) for x in xs]}
        for name, f, d in ACTIVATIONS
    ]


def numeric_slope(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)


def gelu_tanh_max_error(low=-6.0, high=6.0, steps=1200):
    worst, at = 0.0, low
    for i in range(steps + 1):
        x = low + (high - low) * i / steps
        gap = abs(gelu_exact(x) - gelu_tanh(x))
        if gap > worst:
            worst, at = gap, x
    return worst, at


def chain_gradient(name, depth, z):
    derivative = next(d for n, _, d in ACTIVATIONS if n == name)
    return derivative(z) ** depth


def glu_variants(a, b):
    return {
        "glu": a * sigmoid(b),
        "swiglu": silu(a) * b,
        "geglu": gelu_exact(a) * b,
        "reglu": max(0.0, a) * b,
    }


def relu_active_fraction(bias, scale=1.0, n=4000, seed=0):
    rng = random.Random(seed)
    return sum(1 for _ in range(n) if rng.gauss(0.0, scale) + bias > 0) / n


def _observed(column):
    return [v for v in column if v is not None]


def column_fill_values(column, fill_value=0):
    seen = _observed(column)
    return {
        "missing": len(column) - len(seen),
        "mean": sum(seen) / len(seen) if seen else None,
        "median": _median(seen) if seen else None,
        "constant": fill_value,
    }


def impute_column(column, strategy, fill_value=0):
    value = column_fill_values(column, fill_value)[strategy]
    return [value if v is None else v for v in column]


def missing_indicator(column):
    return [1 if v is None else 0 for v in column]


def complete_rows(rows):
    return [row for row in rows if all(v is not None for v in row)]


def _ols(features, targets):
    design = [[1.0] + list(row) for row in features]
    cols = len(design[0])
    gram = [[sum(r[i] * r[j] for r in design) for j in range(cols)] for i in range(cols)]
    moments = [sum(r[i] * t for r, t in zip(design, targets)) for i in range(cols)]
    return _solve_linear(gram, moments)


def _ols_predict(weights, row):
    return weights[0] + sum(w * v for w, v in zip(weights[1:], row))


def _std(values):
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


def _correlation(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    return sxy / math.sqrt(sxx * syy)


def _missing_probability(mechanism, x, y):
    if mechanism == "MCAR":
        return 0.4
    if mechanism == "MAR":
        return 0.7 if x > 0 else 0.1
    return 0.7 if y > 50 else 0.1


def mechanism_rows(mechanism, n=4000, seed=11):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        z1, z2 = rng.gauss(0, 1), rng.gauss(0, 1)
        x = z1
        y = 50 + 10 * (0.8 * z1 + 0.6 * z2)
        missing = rng.random() < _missing_probability(mechanism, x, y)
        rows.append((x, y, missing))
    return rows


def mechanism_estimates(mechanism, n=4000, seed=11):
    rows = mechanism_rows(mechanism, n, seed)
    xs = [x for x, _, _ in rows]
    ys = [y for _, y, _ in rows]
    kept = [(x, y) for x, y, missing in rows if not missing]
    kept_ys = [y for _, y in kept]
    cc_mean = sum(kept_ys) / len(kept_ys)
    weights = _ols([[x] for x, _ in kept], kept_ys)
    regression = [y if not missing else _ols_predict(weights, [x]) for x, y, missing in rows]
    mean_filled = [y if not missing else cc_mean for _, y, missing in rows]
    return {
        "mechanism": mechanism,
        "missing_share": 1 - len(kept) / n,
        "true_mean": sum(ys) / n,
        "complete_case_mean": cc_mean,
        "regression_mean": sum(regression) / n,
        "true_std": _std(ys),
        "mean_imputed_std": _std(mean_filled),
        "true_corr": _correlation(xs, ys),
        "mean_imputed_corr": _correlation(xs, mean_filled),
    }


def iterative_rows(n=60, seed=4, missing_rate=0.25):
    rng = random.Random(seed)
    truth, observed = [], []
    for _ in range(n):
        z = rng.gauss(0, 1)
        row = [z + 0.3 * rng.gauss(0, 1), 2 * z + 0.3 * rng.gauss(0, 1), -z + 0.3 * rng.gauss(0, 1)]
        truth.append(row)
        observed.append([None if rng.random() < missing_rate else v for v in row])
    return truth, observed


def iterative_impute(observed, max_iter=10, tol=1e-3):
    n, d = len(observed), len(observed[0])
    columns = [[row[j] for row in observed] for j in range(d)]
    filled = [impute_column(column, "mean") for column in columns]
    missing_share = [sum(v is None for v in column) / n for column in columns]
    order = sorted(range(d), key=lambda j: missing_share[j])
    scale = max(abs(v) for column in columns for v in column if v is not None)
    rounds = []
    for round_number in range(1, max_iter + 1):
        previous = [list(column) for column in filled]
        for j in order:
            others = [k for k in range(d) if k != j]
            train = [i for i in range(n) if columns[j][i] is not None]
            weights = _ols([[filled[k][i] for k in others] for i in train], [columns[j][i] for i in train])
            for i in range(n):
                if columns[j][i] is None:
                    filled[j][i] = _ols_predict(weights, [filled[k][i] for k in others])
        change = max(abs(a - b) for new, old in zip(filled, previous) for a, b in zip(new, old))
        rounds.append({"round": round_number, "change": change, "converged": change < tol * scale})
        if change < tol * scale:
            break
    return {
        "rows": [[filled[j][i] for j in range(d)] for i in range(n)],
        "order": order,
        "rounds": rounds,
        "threshold": tol * scale,
    }


def imputation_rmse(truth, observed, imputed):
    errors = [
        (t - v) ** 2
        for t_row, o_row, i_row in zip(truth, observed, imputed)
        for t, o, v in zip(t_row, o_row, i_row)
        if o is None
    ]
    return math.sqrt(sum(errors) / len(errors))


def iterative_comparison(n=60, seed=4, missing_rate=0.25):
    truth, observed = iterative_rows(n, seed, missing_rate)
    d = len(observed[0])
    columns = [impute_column([row[j] for row in observed], "mean") for j in range(d)]
    mean_rows = [[columns[j][i] for j in range(d)] for i in range(n)]
    result = iterative_impute(observed)
    return {
        "missing_cells": sum(v is None for row in observed for v in row),
        "cells": n * d,
        "mean_rmse": imputation_rmse(truth, observed, mean_rows),
        "iterative_rmse": imputation_rmse(truth, observed, result["rows"]),
        "rounds": result["rounds"],
        "order": result["order"],
        "threshold": result["threshold"],
    }


def indicator_rows(n, seed):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        x = rng.gauss(0, 1)
        y = 2 * x + rng.gauss(0, 0.5)
        missing = rng.random() < (0.6 if y > 1 else 0.1)
        rows.append((None if missing else x, y))
    return rows


def indicator_comparison(n_train=400, n_test=4000, seed=8):
    train, test = indicator_rows(n_train, seed), indicator_rows(n_test, seed + 1)
    fill = sum(x for x, _ in train if x is not None) / sum(x is not None for x, _ in train)

    def features(x, with_indicator):
        value = fill if x is None else x
        return [value, 1.0 if x is None else 0.0] if with_indicator else [value]

    result = {"fill": fill}
    for name, flag in (("imputed", False), ("with_indicator", True)):
        weights = _ols([features(x, flag) for x, _ in train], [y for _, y in train])
        errors = [(_ols_predict(weights, features(x, flag)) - y) ** 2 for x, y in test]
        result[name] = {"weights": weights, "mse": sum(errors) / len(errors)}
    return result


def _leaf_gain(g, h, reg_lambda):
    return g * g / (h + reg_lambda)


def missing_split_scan(xs, grads, hessians, reg_lambda=1.0):
    present = sorted((x, g, h) for x, g, h in zip(xs, grads, hessians) if x is not None)
    total_g, total_h = sum(grads), sum(hessians)
    missing_g = total_g - sum(g for _, g, _ in present)
    missing_h = total_h - sum(h for _, _, h in present)
    parent = _leaf_gain(total_g, total_h, reg_lambda)
    candidates = []
    for i in range(1, len(present)):
        if present[i][0] == present[i - 1][0]:
            continue
        gl = sum(g for _, g, _ in present[:i])
        hl = sum(h for _, _, h in present[:i])
        threshold = (present[i - 1][0] + present[i][0]) / 2
        for direction, (lg, lh) in (("right", (gl, hl)), ("left", (gl + missing_g, hl + missing_h))):
            rg, rh = total_g - lg, total_h - lh
            candidates.append({
                "threshold": threshold, "missing_go": direction,
                "g_left": lg, "h_left": lh, "g_right": rg, "h_right": rh,
                "loss_chg": _leaf_gain(lg, lh, reg_lambda) + _leaf_gain(rg, rh, reg_lambda) - parent,
                "w_left": -lg / (lh + reg_lambda), "w_right": -rg / (rh + reg_lambda),
            })
    forward = [c for c in candidates if c["missing_go"] == "right"]
    backward = [c for c in candidates if c["missing_go"] == "left"] if missing_h > 0 else []
    best = None
    for candidate in forward + backward[::-1]:
        if best is None or candidate["loss_chg"] > best["loss_chg"]:
            best = candidate
    return {"parent": parent, "missing_g": missing_g, "missing_h": missing_h,
            "candidates": candidates, "best": best}


def routing_example(example=ROUTING_EXAMPLE):
    grads = [-y for y in example["y"]]
    hessians = [1.0] * len(grads)
    native = missing_split_scan(example["x"], grads, hessians, example["reg_lambda"])
    fill = column_fill_values(example["x"])["mean"]
    imputed_x = impute_column(example["x"], "mean")
    imputed = missing_split_scan(imputed_x, grads, hessians, example["reg_lambda"])
    return {"native": native, "fill": fill, "imputed": imputed}


BACKWARD_TWICE_ERROR = (
    "Trying to backward through the graph a second time (or directly access saved tensors after "
    "they have already been freed). Saved intermediate values of the graph are freed when you call "
    ".backward() or autograd.grad(). Specify retain_graph=True if you need to backward through the "
    "graph a second time or if you need to access saved tensors after calling backward."
)
ACCUMULATE_SEQUENCE_NR = 2**64 - 1
GRAPH_EXAMPLE = {"x": 2.0, "w": 3.0, "b": 1.0, "clamp_max": 5.0}


class GraphNode:
    def __init__(self, name, sequence_nr, next_functions, backward=None, saved=None, variable=None):
        self.name = name
        self.sequence_nr = sequence_nr
        self.next_functions = tuple(next_functions)
        self.backward = backward
        self.saved = saved or {}
        self.freed = False
        self.variable = variable
        self.prehooks = []


class GraphTensor:
    def __init__(self, value, requires_grad=False, grad_fn=None):
        self.value = value
        self.requires_grad = requires_grad
        self.grad_fn = grad_fn
        self.grad = None
        self.accumulator = None

    @property
    def is_leaf(self):
        return self.grad_fn is None


class Autograd:
    def __init__(self):
        self.sequence_nr = 0
        self.grad_enabled = True

    def tensor(self, value, requires_grad=False):
        return GraphTensor(value, requires_grad)

    def _edge(self, tensor):
        if not tensor.requires_grad:
            return (None, 0)
        if tensor.grad_fn is not None:
            return (tensor.grad_fn, 0)
        if tensor.accumulator is None:
            tensor.accumulator = GraphNode("AccumulateGrad", ACCUMULATE_SEQUENCE_NR, (), variable=tensor)
        return (tensor.accumulator, 0)

    def record(self, name, inputs, value, backward, saved=None):
        if not (self.grad_enabled and any(t.requires_grad for t in inputs)):
            return GraphTensor(value)
        node = GraphNode(name, self.sequence_nr, [self._edge(t) for t in inputs], backward, saved)
        self.sequence_nr += 1
        return GraphTensor(value, True, node)

    def mul(self, a, b):
        return self.record(
            "MulBackward0", (a, b), a.value * b.value,
            lambda g, s: (g * s["other"], g * s["self"]), {"self": a.value, "other": b.value},
        )

    def add(self, a, b):
        return self.record("AddBackward0", (a, b), a.value + b.value, lambda g, s: (g, g))

    def clamp(self, a, low, high):
        return self.record(
            "ClampBackward1", (a,), min(max(a.value, low), high),
            lambda g, s: (g if low <= s["self"] <= high else 0.0,), {"self": a.value},
        )

    def straight_through_clamp(self, a, low, high):
        return self.record("StraightThroughClampBackward", (a,), min(max(a.value, low), high), lambda g, s: (g,))

    def detach(self, a):
        return GraphTensor(a.value)

    def register_hook(self, tensor, hook):
        if not tensor.requires_grad:
            raise RuntimeError("cannot register a hook on a tensor that doesn't require gradient")
        node = tensor.grad_fn if tensor.grad_fn is not None else self._edge(tensor)[0]
        node.prehooks.append(hook)

    def backward(self, root, retain_graph=False):
        if root.grad_fn is None:
            raise RuntimeError("element 0 of tensors does not require grad and does not have a grad_fn")
        dependencies, stack, seen = {}, [root.grad_fn], {root.grad_fn}
        while stack:
            node = stack.pop()
            for following, _ in node.next_functions:
                if following is None:
                    continue
                dependencies[following] = dependencies.get(following, 0) + 1
                if following not in seen:
                    seen.add(following)
                    stack.append(following)
        buffers, ready, trace = {root.grad_fn: 1.0}, [root.grad_fn], []
        while ready:
            ready.sort(key=lambda n: n.sequence_nr)
            node = ready.pop()
            grad = buffers.pop(node)
            for hook in node.prehooks:
                result = hook(grad)
                grad = grad if result is None else result
            trace.append({"name": node.name, "sequence_nr": node.sequence_nr, "grad": grad})
            if node.variable is not None:
                node.variable.grad = grad if node.variable.grad is None else node.variable.grad + grad
                continue
            if node.freed and node.saved:
                raise RuntimeError(BACKWARD_TWICE_ERROR)
            grads = node.backward(grad, node.saved)
            if not retain_graph:
                node.freed = True
            for (following, _), g in zip(node.next_functions, grads):
                if following is None:
                    continue
                buffers[following] = buffers.get(following, 0.0) + g
                dependencies[following] -= 1
                if dependencies[following] == 0:
                    ready.append(following)
        return trace


def _example_graph(example=GRAPH_EXAMPLE):
    engine = Autograd()
    x = engine.tensor(example["x"])
    w = engine.tensor(example["w"], requires_grad=True)
    b = engine.tensor(example["b"], requires_grad=True)
    a = engine.mul(w, x)
    y = engine.add(a, b)
    loss = engine.mul(y, y)
    return engine, {"x": x, "w": w, "b": b, "a": a, "y": y, "loss": loss}


def _node_label(node):
    if node is None:
        return None
    if node.variable is not None:
        return "AccumulateGrad"
    return node.name


def graph_example(example=GRAPH_EXAMPLE):
    engine, t = _example_graph(example)
    nodes = []
    for key in ("a", "y", "loss"):
        node = t[key].grad_fn
        nodes.append({
            "tensor": key,
            "name": node.name,
            "sequence_nr": node.sequence_nr,
            "next": [_node_label(n) for n, _ in node.next_functions],
        })
    trace = engine.backward(t["loss"])
    try:
        engine.backward(t["loss"])
        second = None
    except RuntimeError as error:
        second = str(error)
    return {
        "values": {key: tensor.value for key, tensor in t.items()},
        "leaf": {key: tensor.is_leaf for key, tensor in t.items()},
        "requires_grad": {key: tensor.requires_grad for key, tensor in t.items()},
        "nodes": nodes,
        "trace": trace,
        "grads": {key: t[key].grad for key in ("x", "w", "b", "a", "y")},
        "second_backward": second,
    }


def graph_controls(example=GRAPH_EXAMPLE):
    engine, t = _example_graph(example)
    engine.backward(t["loss"], retain_graph=True)
    first = t["w"].grad
    engine.backward(t["loss"], retain_graph=True)
    retained = {"first": first, "second": t["w"].grad, "b": t["b"].grad}

    engine, t = _example_graph(example)
    engine.register_hook(t["y"], lambda g: g * 0.5)
    engine.backward(t["loss"])
    hooked = {"w": t["w"].grad, "b": t["b"].grad}

    engine, t = _example_graph(example)
    half = engine.mul(engine.detach(t["y"]), t["y"])
    engine.backward(half)
    detached = {"w": t["w"].grad, "b": t["b"].grad, "value": half.value}

    engine, t = _example_graph(example)
    engine.grad_enabled = False
    frozen = engine.mul(t["w"], t["x"])
    engine.grad_enabled = True
    no_grad = {"requires_grad": frozen.requires_grad, "grad_fn": frozen.grad_fn, "is_leaf": frozen.is_leaf}

    clamps = {}
    for kind in ("clamp", "straight_through_clamp"):
        engine, t = _example_graph(example)
        clamped = getattr(engine, kind)(t["y"], 0.0, example["clamp_max"])
        out = engine.mul(clamped, clamped)
        engine.backward(out)
        clamps[kind] = {"name": clamped.grad_fn.name, "value": out.value, "w": t["w"].grad, "b": t["b"].grad}

    return {"retained": retained, "hooked": hooked, "detached": detached, "no_grad": no_grad, "clamps": clamps}


CONV_IMAGE = [[3, 3, 3, 0, 0, 0] for _ in range(6)]
EDGE_KERNEL = [[1, 0, -1], [1, 0, -1], [1, 0, -1]]
POOL_MAP = [[1, 3, 2, 0], [4, 6, 1, 1], [0, 2, 5, 7], [1, 1, 3, 2]]


def conv_output_size(n, kernel, stride=1, padding=0, dilation=1):
    return (n + 2 * padding - dilation * (kernel - 1) - 1) // stride + 1


def pool_output_size(n, kernel, stride=None, padding=0, dilation=1, ceil_mode=False):
    stride = stride or kernel
    span = n + 2 * padding - dilation * (kernel - 1) - 1
    out = (span + (stride - 1 if ceil_mode else 0)) // stride + 1
    if ceil_mode and (out - 1) * stride >= n + padding:
        out -= 1
    return out


def pad2d(plane, padding):
    width = len(plane[0]) + 2 * padding
    rows = [[0] * width for _ in range(padding)]
    rows += [[0] * padding + list(row) + [0] * padding for row in plane]
    return rows + [[0] * width for _ in range(padding)]


def conv2d(x, weight, bias=None, stride=1, padding=0, dilation=1):
    planes = [pad2d(plane, padding) for plane in x]
    kh, kw = len(weight[0][0]), len(weight[0][0][0])
    out_h = conv_output_size(len(x[0]), kh, stride, padding, dilation)
    out_w = conv_output_size(len(x[0][0]), kw, stride, padding, dilation)
    out = []
    for o, kernels in enumerate(weight):
        start = bias[o] if bias else 0
        out.append([
            [
                start + sum(
                    kernels[c][a][b] * planes[c][i * stride + a * dilation][j * stride + b * dilation]
                    for c in range(len(x)) for a in range(kh) for b in range(kw)
                )
                for j in range(out_w)
            ]
            for i in range(out_h)
        ])
    return out


def pool2d(plane, kernel, stride=None, reduce=max):
    stride = stride or kernel
    out_h = pool_output_size(len(plane), kernel, stride)
    out_w = pool_output_size(len(plane[0]), kernel, stride)
    return [
        [
            reduce([plane[i * stride + a][j * stride + b] for a in range(kernel) for b in range(kernel)])
            for j in range(out_w)
        ]
        for i in range(out_h)
    ]


def _mean(values):
    return sum(values) / len(values)


def receptive_fields(layers):
    size, jump, rows = 1, 1, []
    for name, kernel, stride, dilation in layers:
        size += (kernel - 1) * dilation * jump
        jump *= stride
        rows.append({"layer": name, "size": size, "jump": jump})
    return rows


def conv_params(in_channels, out_channels, kernel, bias=True, groups=1):
    return out_channels * (in_channels // groups) * kernel * kernel + (out_channels if bias else 0)


def conv_example():
    image, kernel = CONV_IMAGE, EDGE_KERNEL
    terms = [(kernel[a][b], image[a][1 + b]) for a in range(3) for b in range(3)]
    return {
        "image": image,
        "kernel": kernel,
        "output": conv2d([image], [[kernel]])[0],
        "terms": terms,
        "term_sum": sum(k * v for k, v in terms),
        "padded": conv2d([image], [[kernel]], padding=1)[0],
        "strided": conv2d([image], [[kernel]], stride=2, padding=1)[0],
        "dilated": conv2d([image], [[kernel]], dilation=2)[0],
        "max_pool": pool2d(POOL_MAP, 2),
        "avg_pool": pool2d(POOL_MAP, 2, reduce=_mean),
        "pool_map": POOL_MAP,
    }


def output_size_rows():
    cases = [
        ("3×3, stride 1, no padding", 32, 3, 1, 0, 1),
        ("3×3, stride 1, padding 1", 32, 3, 1, 1, 1),
        ("3×3, stride 2, padding 1", 32, 3, 2, 1, 1),
        ("5×5, stride 1, no padding", 32, 5, 1, 0, 1),
        ("3×3, dilation 2, padding 2", 32, 3, 1, 2, 2),
        ("7×7, stride 2, padding 3", 224, 7, 2, 3, 1),
        ("1×1, stride 2", 56, 1, 2, 0, 1),
    ]
    return [
        {"label": label, "n": n, "out": conv_output_size(n, k, s, p, d), "kernel": k, "stride": s, "padding": p, "dilation": d}
        for label, n, k, s, p, d in cases
    ]


def lenet_stack(image=32):
    channels, size, rows = 1, image, [{"layer": "input", "shape": [1, image, image], "params": 0}]
    for out_channels in (6, 16):
        size = conv_output_size(size, 5)
        rows.append({"layer": f"Conv2d({channels}, {out_channels}, 5) + ReLU", "shape": [out_channels, size, size], "params": conv_params(channels, out_channels, 5)})
        size = pool_output_size(size, 2)
        rows.append({"layer": "MaxPool2d(2)", "shape": [out_channels, size, size], "params": 0})
        channels = out_channels
    features = channels * size * size
    rows.append({"layer": "Flatten", "shape": [features], "params": 0})
    for width in (120, 84, 10):
        rows.append({"layer": f"Linear({features}, {width})", "shape": [width], "params": features * width + width})
        features = width
    return {"rows": rows, "total": sum(row["params"] for row in rows)}


def _basic_block_params(in_channels, out_channels, downsample):
    params = conv_params(in_channels, out_channels, 3, bias=False)
    params += conv_params(out_channels, out_channels, 3, bias=False)
    params += 2 * (2 * out_channels)
    if downsample:
        params += conv_params(in_channels, out_channels, 1, bias=False) + 2 * out_channels
    return params


def resnet18_stack(image=224, classes=1000):
    size = conv_output_size(image, 7, 2, 3)
    rows = [{"layer": "conv1 7×7/2 + BN + ReLU", "shape": [64, size, size], "params": conv_params(3, 64, 7, bias=False) + 128}]
    size = pool_output_size(size, 3, 2, 1)
    rows.append({"layer": "maxpool 3×3/2", "shape": [64, size, size], "params": 0})
    channels = 64
    for stage, width in enumerate([64, 128, 256, 512], start=1):
        stride = 1 if stage == 1 else 2
        size = conv_output_size(size, 3, stride, 1)
        downsample = stride != 1 or channels != width
        params = _basic_block_params(channels, width, downsample) + _basic_block_params(width, width, False)
        rows.append({"layer": f"layer{stage}: 2 blocks", "shape": [width, size, size], "params": params, "downsample": downsample})
        channels = width
    rows.append({"layer": "adaptive avgpool → flatten", "shape": [channels], "params": 0})
    rows.append({"layer": f"fc {channels}→{classes}", "shape": [classes], "params": channels * classes + classes})
    return {"rows": rows, "total": sum(row["params"] for row in rows)}


def stacking_comparison(channels=64):
    stacked = receptive_fields([(f"3×3 #{i}", 3, 1, 1) for i in range(1, 4)])
    return {
        "stacked_rf": stacked[-1]["size"],
        "single_rf": receptive_fields([("7×7", 7, 1, 1)])[-1]["size"],
        "stacked_params": 3 * conv_params(channels, channels, 3, bias=False),
        "single_params": conv_params(channels, channels, 7, bias=False),
        "dense_params": (channels * 56 * 56) ** 2,
        "channels": channels,
    }


def resnet_receptive_fields():
    layers = [("conv1", 7, 2, 1), ("maxpool", 3, 2, 1)]
    for stage, stride in zip(range(1, 5), [1, 2, 2, 2]):
        layers += [
            (f"layer{stage}.0 conv1", 3, stride, 1), (f"layer{stage}.0 conv2", 3, 1, 1),
            (f"layer{stage}.1 conv1", 3, 1, 1), (f"layer{stage}.1 conv2", 3, 1, 1),
        ]
    return receptive_fields(layers)


AR_JOINT = {
    (0, 0, 0): 0.30, (0, 0, 1): 0.05, (0, 1, 0): 0.05, (0, 1, 1): 0.10,
    (1, 0, 0): 0.05, (1, 0, 1): 0.05, (1, 1, 0): 0.10, (1, 1, 1): 0.30,
}
AR_CORPUS = ["the cat sat .", "the cat ran .", "the dog sat ."]
AR_SENTENCE = "the cat ran ."
AR_CAUSAL_INPUT = [1, 2, 3, 4, 5, 6, 7, 8]
AR_CAUSAL_KERNEL = [0.5, 0.5]
AR_CAUSAL_DILATIONS = [1, 2, 4]


def _marginal(joint, positions, values):
    return sum(p for sequence, p in joint.items() if tuple(sequence[i] for i in positions) == values)


def chain_rule_factors(joint):
    length = len(next(iter(joint)))
    rows = []
    for sequence in sorted(joint):
        factors = []
        for t in range(length):
            prefix = tuple(range(t))
            factors.append(_marginal(joint, prefix + (t,), sequence[:t + 1]) / _marginal(joint, prefix, sequence[:t]))
        rows.append({"sequence": sequence, "joint": joint[sequence], "factors": factors, "product": math.prod(factors)})
    return rows


def markov_approximation(joint):
    approx = {}
    for s in joint:
        first = _marginal(joint, (0,), s[:1])
        second = _marginal(joint, (0, 1), s[:2]) / first
        third = _marginal(joint, (1, 2), s[1:]) / _marginal(joint, (1,), s[1:2])
        approx[s] = first * second * third
    kl = sum(p * math.log2(p / approx[s]) for s, p in joint.items() if p > 0)
    return {"approx": approx, "kl_bits": kl}


def ancestral_samples(joint, draws, seed):
    rng = random.Random(seed)
    counts = {s: 0 for s in joint}
    for _ in range(draws):
        prefix = ()
        for t in range(len(next(iter(joint)))):
            p_one = _marginal(joint, tuple(range(t + 1)), prefix + (1,)) / _marginal(joint, tuple(range(t)), prefix)
            prefix += (1 if rng.random() < p_one else 0,)
        counts[prefix] += 1
    return {s: c / draws for s, c in counts.items()}


def table_sizes(vocab, length):
    return {
        "joint": vocab ** length - 1,
        "chain": sum(vocab ** t * (vocab - 1) for t in range(length)),
        "markov": (vocab - 1) + (length - 1) * vocab * (vocab - 1),
    }


def teacher_forcing_example(corpus=AR_CORPUS, sentence=AR_SENTENCE):
    counts = {}
    for line in corpus:
        tokens = ["<s>"] + line.split()
        for before, after in zip(tokens, tokens[1:]):
            counts.setdefault(before, {}).setdefault(after, 0)
            counts[before][after] += 1
    model = {b: {a: c / sum(row.values()) for a, c in row.items()} for b, row in counts.items()}
    tokens = ["<s>"] + sentence.split()
    rows = [
        {"input": b, "target": a, "prob": model[b][a], "nll": -math.log(model[b][a])}
        for b, a in zip(tokens, tokens[1:])
    ]
    total = sum(row["nll"] for row in rows)
    gradient = {}
    for line in corpus:
        line_tokens = ["<s>"] + line.split()
        for before, after in zip(line_tokens, line_tokens[1:]):
            for token, p in model[before].items():
                key = (before, token)
                gradient[key] = gradient.get(key, 0.0) + p - (1 if token == after else 0)
    return {
        "model": model,
        "rows": rows,
        "inputs": tokens[:-1],
        "targets": tokens[1:],
        "total_nll": total,
        "mean_nll": total / len(rows),
        "perplexity": math.exp(total / len(rows)),
        "max_gradient": max(abs(g) for g in gradient.values()),
    }


def exposure_bias_curve(vocab=4, accuracy=0.9, length=12):
    offsets = [1.0] + [0.0] * (vocab - 1)
    rows = []
    for t in range(1, length + 1):
        slip = (1 - accuracy) / (vocab - 1)
        offsets = [
            sum(offsets[(k - e) % vocab] * (accuracy if e == 0 else slip) for e in range(vocab))
            for k in range(vocab)
        ]
        rows.append({"t": t, "teacher_forced": accuracy, "free_running": offsets[0], "all_correct": accuracy ** t})
    return rows


def causal_conv1d(x, kernel, dilation=1):
    width = len(kernel)
    padded = [0.0] * (dilation * (width - 1)) + list(x)
    return [sum(kernel[j] * padded[t + j * dilation] for j in range(width)) for t in range(len(x))]


def causal_stack(x, kernel=AR_CAUSAL_KERNEL, dilations=AR_CAUSAL_DILATIONS):
    layers = [list(x)]
    for dilation in dilations:
        layers.append(causal_conv1d(layers[-1], kernel, dilation))
    return layers


def causal_receptive_field(kernel_size, dilations):
    return 1 + sum((kernel_size - 1) * d for d in dilations)


def causality_check(x=AR_CAUSAL_INPUT, changed=5, delta=100):
    nudged = list(x)
    nudged[changed] += delta
    before, after = causal_stack(x)[-1], causal_stack(nudged)[-1]
    first_changed = next(t for t in range(len(x)) if before[t] != after[t])
    return {"before": before, "after": after, "changed": changed, "first_changed": first_changed}


def wavenet_receptive_fields():
    block = [2 ** i for i in range(10)]
    return [
        {"label": "one causal conv, kernel 2", "dilations": [1], "size": causal_receptive_field(2, [1])},
        {"label": "10 layers, no dilation", "dilations": [1] * 10, "size": causal_receptive_field(2, [1] * 10)},
        {"label": "10 layers, dilations 1, 2, …, 512", "dilations": block, "size": causal_receptive_field(2, block)},
        {"label": "3 such blocks", "dilations": block * 3, "size": causal_receptive_field(2, block * 3)},
    ]


def pixelcnn_mask(kernel, mask_type):
    centre = kernel // 2
    return [
        [1 if r < centre or (r == centre and (c < centre or (c == centre and mask_type == "B"))) else 0 for c in range(kernel)]
        for r in range(kernel)
    ]


def pixelcnn_dependencies(layers, size=7, kernel=3):
    target = (size - 2, size // 2)

    def offsets(mask_type):
        mask, centre = pixelcnn_mask(kernel, mask_type), kernel // 2
        return [(r - centre, c - centre) for r in range(kernel) for c in range(kernel) if mask[r][c]]

    seen = {target}
    for mask_type in ["B"] * (layers - 1) + ["A"]:
        seen = {
            (r + dr, c + dc) for r, c in seen for dr, dc in offsets(mask_type)
            if 0 <= r + dr < size and 0 <= c + dc < size
        }
    grid = []
    for r in range(size):
        row = []
        for c in range(size):
            if (r, c) == target:
                row.append("target")
            elif (r, c) in seen:
                row.append("seen")
            elif (r, c) > target:
                row.append("future")
            elif max(abs(r - target[0]), abs(c - target[1])) <= layers:
                row.append("blind")
            else:
                row.append("far")
        grid.append(row)
    return {"grid": grid, "target": target, "seen": len(seen), "blind": sum(row.count("blind") for row in grid)}


BPE_CORPUS = {"low": 5, "lower": 2, "newest": 6, "widest": 3}
BPE_END = "</w>"
TOKEN_TEXTS = ["cat", "café", "猫", "🐈"]
UNIGRAM_PIECES = {
    "l": 0.04, "o": 0.04, "w": 0.04, "e": 0.06, "s": 0.04, "t": 0.04,
    "lo": 0.05, "low": 0.12, "we": 0.03, "est": 0.10, "es": 0.05, "west": 0.02, "lowe": 0.01,
}


def _merge_word(word, pair):
    merged, i = [], 0
    while i < len(word):
        if i + 1 < len(word) and (word[i], word[i + 1]) == pair:
            merged.append(word[i] + word[i + 1])
            i += 2
        else:
            merged.append(word[i])
            i += 1
    return tuple(merged)


def _pair_counts(words):
    pairs = {}
    for word, count in words.items():
        for pair in zip(word, word[1:]):
            pairs[pair] = pairs.get(pair, 0) + count
    return pairs


def _bpe_words(word_counts):
    return {tuple(w) + (BPE_END,): c for w, c in word_counts.items()}


def bpe_train(word_counts=BPE_CORPUS, merges=10):
    words = _bpe_words(word_counts)
    vocab = sorted({s for w in words for s in w})
    steps = []
    for _ in range(merges):
        pairs = _pair_counts(words)
        if not pairs:
            break
        best = max(pairs, key=pairs.get)
        words = {_merge_word(w, best): c for w, c in words.items()}
        vocab.append(best[0] + best[1])
        steps.append({
            "pair": best,
            "count": pairs[best],
            "vocab_size": len(vocab),
            "tokens": sum(len(w) * c for w, c in words.items()),
        })
    start = _bpe_words(word_counts)
    return {
        "base": sorted({s for w in start for s in w}),
        "start_tokens": sum(len(w) * c for w, c in start.items()),
        "steps": steps,
        "words": words,
    }


def bpe_encode(word, merges):
    tokens = tuple(word) + (BPE_END,)
    for pair in merges:
        tokens = _merge_word(tokens, pair)
    return list(tokens)


def _unigram_log_likelihood(words):
    counts = {}
    for word, c in words.items():
        for unit in word:
            counts[unit] = counts.get(unit, 0) + c
    total = sum(counts.values())
    return sum(n * math.log(n / total) for n in counts.values())


def wordpiece_gains(word_counts=BPE_CORPUS):
    words = _bpe_words(word_counts)
    base = _unigram_log_likelihood(words)
    rows = []
    for pair, count in _pair_counts(words).items():
        merged = {_merge_word(w, pair): c for w, c in words.items()}
        rows.append({"pair": pair, "count": count, "gain": _unigram_log_likelihood(merged) - base})
    return sorted(rows, key=lambda r: -r["gain"])


def unigram_segmentations(word, pieces=UNIGRAM_PIECES):
    results = []

    def walk(start, path):
        if start == len(word):
            results.append(path)
            return
        for end in range(start + 1, len(word) + 1):
            if word[start:end] in pieces:
                walk(end, path + [word[start:end]])

    walk(0, [])
    rows = [{"pieces": p, "log_prob": sum(math.log(pieces[x]) for x in p)} for p in results]
    rows.sort(key=lambda r: -r["log_prob"])
    total = sum(math.exp(r["log_prob"]) for r in rows)
    for r in rows:
        r["share"] = math.exp(r["log_prob"]) / total
    return rows


def unigram_viterbi(word, pieces=UNIGRAM_PIECES):
    best = [(0.0, [])] + [(-math.inf, None)] * len(word)
    for end in range(1, len(word) + 1):
        for start in range(end):
            piece = word[start:end]
            if piece in pieces and best[start][1] is not None:
                score = best[start][0] + math.log(pieces[piece])
                if score > best[end][0]:
                    best[end] = (score, best[start][1] + [piece])
    return {"pieces": best[-1][1], "log_prob": best[-1][0]}


def utf8_lengths(texts=TOKEN_TEXTS):
    return [
        {"text": t, "chars": len(t), "bytes": list(t.encode("utf-8")), "byte_count": len(t.encode("utf-8"))}
        for t in texts
    ]


def digit_groups(number, group=3, from_right=False):
    digits = str(number)
    if not from_right:
        return [digits[i:i + group] for i in range(0, len(digits), group)]
    head = len(digits) % group
    return ([digits[:head]] if head else []) + [digits[i:i + group] for i in range(head, len(digits), group)]


def batch_ids(sentences, specials=("<pad>", "<bos>", "<eos>")):
    vocab = {s: i for i, s in enumerate(specials)}
    for sentence in sentences:
        for token in sentence.split():
            vocab.setdefault(token, len(vocab))
    pad, bos, eos = (vocab[s] for s in specials)
    rows = [[bos] + [vocab[t] for t in s.split()] + [eos] for s in sentences]
    width = max(len(r) for r in rows)
    return {
        "vocab": vocab,
        "ids": [r + [pad] * (width - len(r)) for r in rows],
        "mask": [[1] * len(r) + [0] * (width - len(r)) for r in rows],
        "targets": [r[1:] + [-100] * (width - len(r)) for r in rows],
    }


KNN_POINTS = [
    (1.0, 2.0, 0), (2.0, 1.0, 0), (2.0, 4.0, 0), (3.0, 3.0, 0),
    (1.0, 5.0, 0), (4.0, 2.0, 0), (3.0, 6.0, 0), (5.0, 4.0, 0),
    (6.0, 7.0, 1), (7.0, 5.0, 1), (8.0, 8.0, 1), (7.0, 9.0, 1),
    (9.0, 6.0, 1), (6.0, 4.5, 1), (8.0, 3.0, 1), (5.0, 8.0, 1),
]
KNN_QUERY = (4.8, 5.0)
KNN_DOC_X = [0.0, 1.0, 2.0, 3.0]
KNN_DOC_Y = [0, 0, 1, 1]


def minkowski(a, b, p=2):
    diffs = [abs(x - y) for x, y in zip(a, b)]
    if p == math.inf:
        return max(diffs)
    return sum(d**p for d in diffs) ** (1 / p)


def metric_table(a=(0.0, 0.0), b=(3.0, 4.0)):
    rows = [("manhattan", 1), ("euclidean", 2), ("minkowski", 3), ("chebyshev", math.inf)]
    return [{"name": name, "p": p, "distance": minkowski(a, b, p)} for name, p in rows]


def nearest(points, query, k, p=2):
    ranked = sorted(
        ({"index": i, "point": pt[:-1], "label": pt[-1], "distance": minkowski(pt[:-1], query, p)}
         for i, pt in enumerate(points)),
        key=lambda r: (r["distance"], r["index"]),
    )
    return ranked[:k]


def neighbor_weights(distances, weights="uniform"):
    if weights == "uniform":
        return [1.0] * len(distances)
    if any(d == 0 for d in distances):
        return [1.0 if d == 0 else 0.0 for d in distances]
    return [1 / d for d in distances]


def knn_classify(points=KNN_POINTS, query=KNN_QUERY, k=5, weights="uniform", p=2):
    neighbors = nearest(points, query, k, p)
    w = neighbor_weights([n["distance"] for n in neighbors], weights)
    labels = sorted({pt[-1] for pt in points})
    votes = {label: 0.0 for label in labels}
    for n, wi in zip(neighbors, w):
        votes[n["label"]] += wi
    total = sum(votes.values())
    prediction = max(labels, key=lambda label: (votes[label], -label))
    return {
        "neighbors": [dict(n, weight=wi) for n, wi in zip(neighbors, w)],
        "votes": votes,
        "proba": {label: votes[label] / total for label in labels},
        "prediction": prediction,
    }


def knn_regress(xs=KNN_DOC_X, ys=KNN_DOC_Y, query=1.5, k=2, weights="uniform"):
    points = [(x, y) for x, y in zip(xs, ys)]
    neighbors = nearest(points, (query,), k)
    w = neighbor_weights([n["distance"] for n in neighbors], weights)
    return sum(wi * n["label"] for n, wi in zip(neighbors, w)) / sum(w)


def docstring_examples():
    points = [(x, y) for x, y in zip(KNN_DOC_X, KNN_DOC_Y)]
    return {
        "predict_1_1": knn_classify(points, (1.1,), k=3)["prediction"],
        "proba_0_9": knn_classify(points, (0.9,), k=3)["proba"],
        "regress_1_5": knn_regress(query=1.5, k=2),
    }


def k_sweep(points=KNN_POINTS, query=KNN_QUERY, ks=(1, 3, 5, 7, 9)):
    rows = []
    for k in ks:
        result = knn_classify(points, query, k)
        rows.append({"k": k, "votes": result["votes"], "prediction": result["prediction"]})
    return rows


def leave_one_out(points=KNN_POINTS, ks=(1, 3, 5, 7, 9, 15)):
    rows = []
    for k in ks:
        errors = 0
        for i, pt in enumerate(points):
            rest = points[:i] + points[i + 1:]
            if knn_classify(rest, pt[:-1], k)["prediction"] != pt[-1]:
                errors += 1
        rows.append({"k": k, "errors": errors, "error_rate": errors / len(points)})
    return rows


def distance_concentration(dims=(1, 2, 10, 100, 1000), n=200, seed=0):
    rng = random.Random(seed)
    rows = []
    for d in dims:
        query = [rng.random() for _ in range(d)]
        dists = [minkowski([rng.random() for _ in range(d)], query) for _ in range(n)]
        near, far = min(dists), max(dists)
        rows.append({"dim": d, "nearest": near, "farthest": far, "ratio": near / far})
    return rows


def neighborhood_edge(dims=(1, 2, 10, 100), fraction=0.01):
    return [{"dim": d, "edge": fraction ** (1 / d)} for d in dims]


def tree_size(n_samples, leaf_size):
    n_levels = int(math.log2(max(1, (n_samples - 1) / leaf_size)) + 1)
    return {"n_levels": n_levels, "n_nodes": 2**n_levels - 1}


def kd_tree_build(points=KNN_POINTS, leaf_size=2):
    coords = [pt[:-1] for pt in points]
    n_nodes = tree_size(len(points), leaf_size)["n_nodes"]
    nodes = {}

    def build(i_node, idx):
        dims = len(coords[0])
        lower = [min(coords[i][j] for i in idx) for j in range(dims)]
        upper = [max(coords[i][j] for i in idx) for j in range(dims)]
        node = {"index": i_node, "points": list(idx), "lower": lower, "upper": upper}
        nodes[i_node] = node
        if 2 * i_node + 1 >= n_nodes:
            node["leaf"] = True
            return
        node["leaf"] = False
        spread = [upper[j] - lower[j] for j in range(dims)]
        split = spread.index(max(spread))
        ordered = sorted(idx, key=lambda i: (coords[i][split], i))
        mid = len(ordered) // 2
        node["split_dim"] = split
        node["split_value"] = coords[ordered[mid]][split]
        build(2 * i_node + 1, ordered[:mid])
        build(2 * i_node + 2, ordered[mid:])

    build(0, list(range(len(points))))
    return {"n_nodes": n_nodes, "nodes": [nodes[i] for i in sorted(nodes)]}


def box_min_dist(lower, upper, query):
    gaps = [max(lo - q, 0.0, q - hi) for lo, hi, q in zip(lower, upper, query)]
    return math.sqrt(sum(g * g for g in gaps))


def kd_tree_query(points=KNN_POINTS, query=KNN_QUERY, k=1, leaf_size=2):
    tree = kd_tree_build(points, leaf_size)
    nodes = {n["index"]: n for n in tree["nodes"]}
    coords = [pt[:-1] for pt in points]
    heap = []
    log = {"trimmed": [], "leaves": [], "scanned": 0}

    def largest():
        return heap[-1][0] if len(heap) == k else math.inf

    def visit(i_node, bound):
        node = nodes[i_node]
        if bound > largest():
            log["trimmed"].append(i_node)
        elif node["leaf"]:
            log["leaves"].append(i_node)
            for i in node["points"]:
                log["scanned"] += 1
                heap.append((minkowski(coords[i], query), i))
                heap.sort()
                del heap[k:]
        else:
            children = [2 * i_node + 1, 2 * i_node + 2]
            bounds = [box_min_dist(nodes[c]["lower"], nodes[c]["upper"], query) for c in children]
            order = [0, 1] if bounds[0] <= bounds[1] else [1, 0]
            for j in order:
                visit(children[j], bounds[j])

    visit(0, box_min_dist(nodes[0]["lower"], nodes[0]["upper"], query))
    return dict(log, neighbors=[{"index": i, "distance": d} for d, i in heap], n_points=len(points))


def ball_min_dist(query, centroid, radius):
    return max(0.0, minkowski(query, centroid) - radius)


def ball_bound_example(points=KNN_POINTS, query=KNN_QUERY, label=0):
    members = [pt[:-1] for pt in points if pt[-1] == label]
    centroid = tuple(sum(c[j] for c in members) / len(members) for j in range(2))
    radius = max(minkowski(c, centroid) for c in members)
    bound = ball_min_dist(query, centroid, radius)
    true_min = min(minkowski(c, query) for c in members)
    return {"centroid": centroid, "radius": radius, "bound": bound, "true_min": true_min}


SEARCH_EXAMPLE = {
    "query": [1.0, 0.5],
    "documents": {
        "A": [4.0, 1.0],
        "B": [1.0, 1.0],
        "C": [0.9, 0.3],
        "D": [2.0, 2.4],
        "E": [0.2, 1.0],
    },
}


def unit_vector(vector):
    norm = vector_norm(vector)
    return [x / norm for x in vector]


def metric_agreement(example=SEARCH_EXAMPLE):
    raw = similarity_ranking(example)
    unit = {
        "query": unit_vector(example["query"]),
        "documents": {name: unit_vector(v) for name, v in example["documents"].items()},
    }
    normalized = similarity_ranking(unit)
    identity = [
        {
            "name": row["name"],
            "squared_distance": row["distance"] ** 2,
            "two_minus_two_cos": 2 - 2 * row["cosine"],
        }
        for row in normalized["rows"]
    ]
    return {"raw": raw, "normalized": normalized, "identity": identity}


def brute_force_search_cost(n, dim, bytes_per_value=4, queries=1):
    flops = 2 * n * dim * queries
    return {
        "n": n,
        "dim": dim,
        "flops": flops,
        "index_bytes": n * dim * bytes_per_value,
        "intensity": flops / (n * dim * bytes_per_value),
    }


BM25_EXAMPLE = {
    "documents": {
        "d1": "the cat sat on the mat",
        "d2": "a dog chased the cat around the cat tree",
        "d3": "cats and dogs make good pets",
        "d4": "the market fell as investors sold shares and the dollar rose against the euro",
    },
    "query": "cat mat",
    "k1": 1.2,
    "b": 0.75,
}


def bm25_idf(n_docs, doc_freq):
    return math.log((n_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1)


def bm25_scores(example=BM25_EXAMPLE):
    docs = {name: text.split() for name, text in example["documents"].items()}
    terms = example["query"].split()
    n_docs = len(docs)
    avgdl = sum(len(tokens) for tokens in docs.values()) / n_docs
    k1, b = example["k1"], example["b"]
    idf = {t: bm25_idf(n_docs, sum(t in tokens for tokens in docs.values())) for t in terms}
    rows = []
    for name, tokens in docs.items():
        parts = {}
        for t in terms:
            tf = tokens.count(t)
            norm = k1 * (1 - b + b * len(tokens) / avgdl)
            parts[t] = idf[t] * tf * (k1 + 1) / (tf + norm) if tf else 0.0
        rows.append({"name": name, "length": len(tokens), "parts": parts, "score": sum(parts.values())})
    ranking = [row["name"] for row in sorted(rows, key=lambda row: (-row["score"], row["name"]))]
    return {"avgdl": avgdl, "idf": idf, "rows": rows, "ranking": ranking}


def bm25_saturation(k1=1.2, tfs=(1, 2, 3, 5, 10)):
    return [{"tf": tf, "weight": tf * (k1 + 1) / (tf + k1)} for tf in tfs]


def reciprocal_rank_fusion(rankings, k=60):
    scores = {}
    for ranking in rankings:
        for rank, name in enumerate(ranking, start=1):
            scores[name] = scores.get(name, 0.0) + 1 / (k + rank)
    fused = sorted(scores, key=lambda name: (-scores[name], name))
    return {"scores": scores, "ranking": fused}


HYBRID_DENSE_RANKING = ["d3", "d1", "d2", "d4"]


def hybrid_example(k=60):
    lexical = [row["name"] for row in sorted(bm25_scores()["rows"], key=lambda row: -row["score"]) if row["score"] > 0]
    fused = reciprocal_rank_fusion([lexical, HYBRID_DENSE_RANKING], k=k)
    return {"lexical": lexical, "dense": HYBRID_DENSE_RANKING, "k": k, **fused}


EXAMPLE_GPU = {"peak_flops": 100e12, "bandwidth": 2e12}


def roofline(flops, bytes_moved, gpu=EXAMPLE_GPU):
    compute_seconds = flops / gpu["peak_flops"]
    memory_seconds = bytes_moved / gpu["bandwidth"]
    intensity = flops / bytes_moved
    return {
        "flops": flops,
        "bytes": bytes_moved,
        "intensity": intensity,
        "ridge": gpu["peak_flops"] / gpu["bandwidth"],
        "compute_seconds": compute_seconds,
        "memory_seconds": memory_seconds,
        "seconds": max(compute_seconds, memory_seconds),
        "bound": "compute" if compute_seconds >= memory_seconds else "memory",
        "attainable_flops": min(gpu["peak_flops"], intensity * gpu["bandwidth"]),
    }


def matmul_roofline(m, n, k, bytes_per_value=4, gpu=EXAMPLE_GPU):
    flops = 2 * m * n * k
    bytes_moved = (m * k + k * n + m * n) * bytes_per_value
    return {"shape": (m, n, k), **roofline(flops, bytes_moved, gpu)}


def elementwise_roofline(numel, flops_per_element=1, tensors_read=1, tensors_written=1, bytes_per_value=4, gpu=EXAMPLE_GPU):
    flops = numel * flops_per_element
    bytes_moved = numel * (tensors_read + tensors_written) * bytes_per_value
    return {"numel": numel, **roofline(flops, bytes_moved, gpu)}


def gpu_op_examples(size=4096):
    return [
        {"name": f"matmul {size}×{size} by {size}×{size}", **matmul_roofline(size, size, size)},
        {"name": f"matrix-vector 1×{size} by {size}×{size}", **matmul_roofline(1, size, size)},
        {"name": f"ReLU over {size}×{size}", **elementwise_roofline(size * size)},
    ]


def fusion_example(numel=4096 * 4096, ops=3, bytes_per_value=4, gpu=EXAMPLE_GPU):
    unfused = roofline(ops * numel, ops * 2 * numel * bytes_per_value, gpu)
    fused = roofline(ops * numel, 2 * numel * bytes_per_value, gpu)
    return {"numel": numel, "ops": ops, "unfused": unfused, "fused": fused, "speedup": unfused["seconds"] / fused["seconds"]}


def tiled_matmul_traffic(n, tile, bytes_per_value=4):
    values_loaded = 2 * n**3 // tile
    return {
        "tile": tile,
        "bytes": values_loaded * bytes_per_value,
        "intensity": 2 * n**3 / (values_loaded * bytes_per_value),
    }


def roofline_xy(intensity, flops_per_second):
    return (
        60 + (math.log2(intensity) + 4) * 40,
        260 - (math.log10(flops_per_second / 1e12) + 1) * 70,
    )


def async_timeline(kernel_us, launch_us=5):
    rows = []
    cpu = 0
    gpu_end = 0
    for duration in kernel_us:
        issued = cpu + launch_us
        start = max(issued, gpu_end)
        rows.append({"issued": issued, "start": start, "end": start + duration})
        cpu = issued
        gpu_end = start + duration
    busy = sum(kernel_us)
    return {
        "rows": rows,
        "launch_us": launch_us,
        "cpu_done": cpu,
        "total": gpu_end,
        "busy": busy,
        "utilization": busy / gpu_end,
    }


FLOAT_FORMATS = [
    {"name": "fp32", "dtype": "torch.float32", "exponent": 8, "mantissa": 23, "bits": 32},
    {"name": "tf32", "dtype": None, "exponent": 8, "mantissa": 10, "bits": 19},
    {"name": "fp16", "dtype": "torch.float16", "exponent": 5, "mantissa": 10, "bits": 16},
    {"name": "bf16", "dtype": "torch.bfloat16", "exponent": 8, "mantissa": 7, "bits": 16},
    {
        "name": "fp8 e4m3",
        "dtype": "torch.float8_e4m3fn",
        "exponent": 4,
        "mantissa": 3,
        "bits": 8,
        "finite_only": True,
    },
    {"name": "fp8 e5m2", "dtype": "torch.float8_e5m2", "exponent": 5, "mantissa": 2, "bits": 8},
]


def find_float_format(name):
    return next(fmt for fmt in FLOAT_FORMATS if fmt["name"] == name)


def float_format_stats(fmt):
    e, m = fmt["exponent"], fmt["mantissa"]
    bias = 2 ** (e - 1) - 1
    if fmt.get("finite_only"):
        largest = (2 - 2 * 2.0**-m) * 2.0 ** (2**e - 1 - bias)
    else:
        largest = (2 - 2.0**-m) * 2.0 ** (2**e - 2 - bias)
    smallest_normal = 2.0 ** (1 - bias)
    return {
        "bias": bias,
        "max": largest,
        "smallest_normal": smallest_normal,
        "smallest_subnormal": smallest_normal * 2.0**-m,
        "epsilon": 2.0**-m,
        "digits": (m + 1) * math.log10(2),
    }


def round_to_format(x, fmt):
    if x == 0 or not math.isfinite(x):
        return x
    stats = float_format_stats(fmt)
    exponent = max(math.frexp(abs(x))[1] - 1, 1 - stats["bias"])
    quantum = 2.0 ** (exponent - fmt["mantissa"])
    rounded = round(abs(x) / quantum) * quantum
    if rounded > stats["max"]:
        rounded = stats["max"] if fmt.get("finite_only") else math.inf
    return math.copysign(rounded, x)


def float_bits(x, fmt):
    rounded = round_to_format(x, fmt)
    stats = float_format_stats(fmt)
    e, m = fmt["exponent"], fmt["mantissa"]
    sign = 1 if math.copysign(1, rounded) < 0 else 0
    a = abs(rounded)
    if a == 0:
        field, fraction = 0, 0
    elif a == math.inf:
        field, fraction = 2**e - 1, 0
    elif a < stats["smallest_normal"]:
        field, fraction = 0, round(a / stats["smallest_subnormal"])
    else:
        exponent = math.frexp(a)[1] - 1
        field = exponent + stats["bias"]
        fraction = round((a / 2.0**exponent - 1) * 2**m)
    return {
        "value": rounded,
        "sign": str(sign),
        "exponent": format(field, f"0{e}b"),
        "mantissa": format(fraction, f"0{m}b"),
    }


def bf16_round_bits(x):
    bits = struct.unpack("<I", struct.pack("<f", x))[0]
    rounding_bias = ((bits >> 16) & 1) + 0x7FFF
    return struct.unpack("<f", struct.pack("<I", ((bits + rounding_bias) >> 16) << 16))[0]


def fp16_struct_round(x):
    try:
        return struct.unpack("<e", struct.pack("<e", x))[0]
    except (OverflowError, struct.error):
        return math.copysign(math.inf, x)


PRECISION_EXAMPLE = {"value": 1 / 3, "big": 70000.0, "tiny": 1e-8}

GRADIENT_EXAMPLE = [3e-2, 4e-5, 2e-7, 5e-9, 1e-10]


def loss_scaling_example(grads=GRADIENT_EXAMPLE, scale=2.0**16, fmt_name="fp16"):
    fmt = find_float_format(fmt_name)
    rows = []
    for grad in grads:
        plain = round_to_format(grad, fmt)
        scaled = round_to_format(grad * scale, fmt)
        recovered = scaled / scale
        rows.append(
            {
                "grad": grad,
                "plain": plain,
                "plain_error": abs(plain - grad) / grad,
                "scaled": scaled,
                "recovered": recovered,
                "scaled_error": abs(recovered - grad) / grad,
            }
        )
    return {"scale": scale, "rows": rows}


def grad_scaler_run(
    max_grads,
    init_scale=2.0**16,
    growth_factor=2.0,
    backoff_factor=0.5,
    growth_interval=2000,
    fmt_name="fp16",
):
    fmt = find_float_format(fmt_name)
    scale = init_scale
    tracker = 0
    rows = []
    for step, grad in enumerate(max_grads, start=1):
        overflow = math.isinf(round_to_format(grad * scale, fmt))
        used = scale
        if overflow:
            scale *= backoff_factor
            tracker = 0
        else:
            tracker += 1
            if tracker == growth_interval:
                scale *= growth_factor
                tracker = 0
        rows.append({"step": step, "scale": used, "overflow": overflow, "next_scale": scale})
    skipped = sum(row["overflow"] for row in rows)
    return {"rows": rows, "skipped": skipped, "final_scale": scale}


def accumulate_updates(weight, update, steps, fmt_name):
    fmt = find_float_format(fmt_name)
    value = round_to_format(weight, fmt)
    for _ in range(steps):
        value = round_to_format(value + update, fmt)
    return value


def master_weight_example(weight=1.0, update=1e-4, steps=100):
    fp32 = accumulate_updates(weight, update, steps, "fp32")
    return {
        "weight": weight,
        "update": update,
        "steps": steps,
        "fp16": accumulate_updates(weight, update, steps, "fp16"),
        "bf16": accumulate_updates(weight, update, steps, "bf16"),
        "fp32": fp32,
        "fp32_cast_fp16": round_to_format(fp32, find_float_format("fp16")),
        "fp16_spacing": 2.0 ** -find_float_format("fp16")["mantissa"],
    }


QUANT_EPS = 2.0**-23

QUANT_RANGES = {
    "qint8": (-128, 127),
    "quint8": (0, 255),
    "qint8 reduce_range": (-64, 63),
    "quint8 reduce_range": (0, 127),
    "int4": (-8, 7),
}


def affine_qparams(min_val, max_val, quant_min, quant_max):
    min_neg = min(min_val, 0.0)
    max_pos = max(max_val, 0.0)
    scale = max((max_pos - min_neg) / (quant_max - quant_min), QUANT_EPS)
    zero_point = quant_min - round(min_neg / scale)
    return scale, min(max(zero_point, quant_min), quant_max)


def symmetric_qparams(min_val, max_val, quant_min, quant_max):
    bound = max(-min(min_val, 0.0), max(max_val, 0.0))
    scale = max(bound / ((quant_max - quant_min) / 2), QUANT_EPS)
    zero_point = 128 if (quant_min, quant_max) == (0, 255) else 0
    return scale, zero_point


def quantize_values(values, scale, zero_point, quant_min, quant_max):
    return [min(max(round(v / scale) + zero_point, quant_min), quant_max) for v in values]


def dequantize_values(codes, scale, zero_point):
    return [(q - zero_point) * scale for q in codes]


def fake_quantize(values, scale, zero_point, quant_min, quant_max):
    unclamped = [round(v / scale) + zero_point for v in values]
    codes = [min(max(q, quant_min), quant_max) for q in unclamped]
    return {
        "unclamped": unclamped,
        "codes": codes,
        "output": dequantize_values(codes, scale, zero_point),
        "mask": [quant_min <= q <= quant_max for q in unclamped],
    }


def straight_through_grad(upstream, mask):
    return [g if keep else 0.0 for g, keep in zip(upstream, mask)]


def quantize_roundtrip(values, scheme="affine", dtype="quint8"):
    quant_min, quant_max = QUANT_RANGES[dtype]
    qparams = affine_qparams if scheme == "affine" else symmetric_qparams
    scale, zero_point = qparams(min(values), max(values), quant_min, quant_max)
    codes = quantize_values(values, scale, zero_point, quant_min, quant_max)
    restored = dequantize_values(codes, scale, zero_point)
    return {
        "scale": scale,
        "zero_point": zero_point,
        "codes": codes,
        "restored": restored,
        "errors": [r - v for r, v in zip(restored, values)],
        "max_error": max(abs(r - v) for r, v in zip(restored, values)),
    }


AFFINE_EXAMPLE = [-1.0, 0.0, 1.0, 2.0]

ACTIVATION_EXAMPLE = [-0.62, 0.0, 0.35, 1.17, 2.48]

FAKE_QUANT_EXAMPLE = {
    "values": [0.0552, 0.9730, 0.3973, -1.0780],
    "scale": 0.1,
    "zero_point": 0,
    "quant_min": 0,
    "quant_max": 255,
}

CHANNEL_WEIGHTS = [
    [0.12, -0.08, 0.05, -0.11],
    [0.31, -0.27, 0.18, 0.02],
    [2.40, -1.10, 0.65, -0.30],
]


def _rows_error(rows, restored):
    return [
        sum(abs(r - w) for r, w in zip(rest, row)) / sum(abs(w) for w in row)
        for row, rest in zip(rows, restored)
    ]


def per_channel_example(weights=CHANNEL_WEIGHTS, dtype="qint8"):
    quant_min, quant_max = QUANT_RANGES[dtype]
    flat = [w for row in weights for w in row]
    tensor_scale, _ = symmetric_qparams(min(flat), max(flat), quant_min, quant_max)
    tensor_codes = [quantize_values(row, tensor_scale, 0, quant_min, quant_max) for row in weights]
    tensor_rest = [dequantize_values(codes, tensor_scale, 0) for codes in tensor_codes]
    channel_scales = [symmetric_qparams(min(row), max(row), quant_min, quant_max)[0] for row in weights]
    channel_codes = [
        quantize_values(row, s, 0, quant_min, quant_max) for row, s in zip(weights, channel_scales)
    ]
    channel_rest = [dequantize_values(c, s, 0) for c, s in zip(channel_codes, channel_scales)]
    return {
        "tensor_scale": tensor_scale,
        "tensor_codes": tensor_codes,
        "tensor_error": _rows_error(weights, tensor_rest),
        "channel_scales": channel_scales,
        "channel_codes": channel_codes,
        "channel_error": _rows_error(weights, channel_rest),
    }


GROUP_ROW = [0.21, -0.15, 0.08, -0.26, 0.19, 1.85, -0.12, 0.04]


def group_quantize(row, bits=4, group_size=None):
    quant_max = 2 ** (bits - 1) - 1
    group_size = group_size or len(row)
    scales, restored = [], []
    for start in range(0, len(row), group_size):
        group = row[start : start + group_size]
        scale = max(abs(v) for v in group) / quant_max
        scales.append(scale)
        codes = [min(max(round(v / scale), -quant_max - 1), quant_max) for v in group]
        restored.extend(q * scale for q in codes)
    error = sum(abs(r - v) for r, v in zip(restored, row)) / sum(abs(v) for v in row)
    return {"scales": scales, "restored": restored, "error": error}


def weight_bytes(params, bits, group_size=None, scale_bytes=2):
    groups = params // group_size if group_size else 0
    return params * bits / 8 + groups * scale_bytes


def weight_memory_example(params=8e9):
    rows = [
        {"name": "fp16", "bits": 16, "group": None},
        {"name": "int8, per channel", "bits": 8, "group": None},
        {"name": "int4, group 128", "bits": 4, "group": 128},
        {"name": "int4, group 32", "bits": 4, "group": 32},
    ]
    for row in rows:
        row["bytes"] = weight_bytes(int(params), row["bits"], row["group"])
        row["bits_per_weight"] = row["bytes"] * 8 / params
    return {"params": params, "rows": rows}


OUTLIER_ACTIVATIONS = [0.5, -0.3, 0.8, -0.6, 0.2, 60.0]
OUTLIER_WEIGHTS = [0.4, 0.7, -0.5, 0.3, 0.9, 0.02]


def absmax_quantize(values, quant_max=127):
    scale = max(abs(v) for v in values) / quant_max
    return [round(v / scale) * scale for v in values], scale


def outlier_example(x=OUTLIER_ACTIVATIONS, w=OUTLIER_WEIGHTS, threshold=6.0):
    exact = sum(a * b for a, b in zip(x, w))
    naive_x, naive_scale = absmax_quantize(x)
    naive = sum(a * b for a, b in zip(naive_x, w))
    keep = [abs(a) >= threshold for a in x]
    small = [a for a, k in zip(x, keep) if not k]
    small_q, small_scale = absmax_quantize(small)
    small_iter = iter(small_q)
    mixed_x = [a if k else next(small_iter) for a, k in zip(x, keep)]
    mixed = sum(a * b for a, b in zip(mixed_x, w))
    return {
        "exact": exact,
        "naive_x": naive_x,
        "naive_scale": naive_scale,
        "naive": naive,
        "mixed_x": mixed_x,
        "mixed_scale": small_scale,
        "mixed": mixed,
        "outliers": sum(keep),
    }


RL_GAMMA = 0.9
CHAIN_STATES = 4
CHAIN_SLIP = 0.2
CHAIN_ACTIONS = ("left", "right")


def discounted_returns(rewards, gamma=RL_GAMMA):
    returns = []
    running = 0.0
    for reward in reversed(rewards):
        running = reward + gamma * running
        returns.append(running)
    return returns[::-1]


def chain_transitions(state, action, slip=CHAIN_SLIP, states=CHAIN_STATES):
    goal = states - 1
    target = max(state - 1, 0) if action == "left" else state + 1
    outcomes = [(1 - slip, target), (slip, state)]
    return [(p, s, 1.0 if s == goal else 0.0) for p, s in outcomes if p > 0]


def chain_q_values(values, gamma=RL_GAMMA, slip=CHAIN_SLIP, states=CHAIN_STATES):
    goal = states - 1
    return [
        {
            action: sum(
                p * (r + gamma * (0.0 if s2 == goal else values[s2]))
                for p, s2, r in chain_transitions(s, action, slip, states)
            )
            for action in CHAIN_ACTIONS
        }
        for s in range(goal)
    ]


def value_iteration(gamma=RL_GAMMA, slip=CHAIN_SLIP, states=CHAIN_STATES, sweeps=60):
    values = [0.0] * states
    history = [list(values)]
    for _ in range(sweeps):
        values = [max(row.values()) for row in chain_q_values(values, gamma, slip, states)] + [0.0]
        history.append(list(values))
    return {"values": values, "q": chain_q_values(values, gamma, slip, states), "history": history}


def chain_values_closed_form(gamma=RL_GAMMA, slip=CHAIN_SLIP, states=CHAIN_STATES):
    stay = 1 / (1 - gamma * slip)
    values = [0.0] * states
    following = 1.0
    for s in range(states - 2, -1, -1):
        values[s] = (1 - slip) * following * stay
        following = gamma * values[s]
    return values


def q_update(q, reward, next_max, alpha, gamma=RL_GAMMA):
    target = reward + gamma * next_max
    return {"target": target, "td_error": target - q, "new": q + alpha * (target - q)}


def q_learning(episodes=500, alpha=0.1, epsilon=0.2, gamma=RL_GAMMA, slip=CHAIN_SLIP, states=CHAIN_STATES, seed=0):
    rng = random.Random(seed)
    goal = states - 1
    q = [{action: 0.0 for action in CHAIN_ACTIONS} for _ in range(goal)]
    steps = 0
    for _ in range(episodes):
        s = 0
        while s != goal:
            if rng.random() < epsilon:
                action = rng.choice(CHAIN_ACTIONS)
            else:
                action = max(CHAIN_ACTIONS, key=lambda name: q[s][name])
            u = rng.random()
            cumulative = 0.0
            for p, s2, r in chain_transitions(s, action, slip, states):
                cumulative += p
                if u < cumulative:
                    break
            next_max = 0.0 if s2 == goal else max(q[s2].values())
            q[s][action] = q_update(q[s][action], r, next_max, alpha, gamma)["new"]
            s = s2
            steps += 1
    optimal = value_iteration(gamma, slip, states)["q"]
    return {
        "q": q,
        "steps": steps,
        "greedy": [max(CHAIN_ACTIONS, key=lambda name: row[name]) for row in q],
        "max_error": max(abs(row[a] - best[a]) for row, best in zip(q, optimal) for a in CHAIN_ACTIONS),
    }


def chain_advantages(gamma=RL_GAMMA, slip=CHAIN_SLIP, states=CHAIN_STATES, state=1):
    values = value_iteration(gamma, slip, states)["values"]
    goal = states - 1
    rows = []
    for p, s2, r in chain_transitions(state, "right", slip, states):
        delta = r + (0.0 if s2 == goal else gamma * values[s2]) - values[state]
        rows.append({"probability": p, "next": s2, "reward": r, "td_error": delta})
    return {"value": values[state], "rows": rows, "mean": sum(row["probability"] * row["td_error"] for row in rows)}


BANDIT_REWARDS = [1.0, 2.0, 4.0]


def softmax_probs(logits):
    top = max(logits)
    exps = [math.exp(x - top) for x in logits]
    total = sum(exps)
    return [e / total for e in exps]


def score_function(probs, action):
    return [(1.0 if k == action else 0.0) - p for k, p in enumerate(probs)]


def reinforce_gradient(logits, rewards=BANDIT_REWARDS, baseline=0.0):
    probs = softmax_probs(logits)
    arms = range(len(probs))
    expected = sum(p * r for p, r in zip(probs, rewards))
    samples = [[(rewards[a] - baseline) * g for g in score_function(probs, a)] for a in arms]
    mean = [sum(probs[a] * samples[a][k] for a in arms) for k in arms]
    return {
        "probs": probs,
        "expected": expected,
        "exact": [p * (r - expected) for p, r in zip(probs, rewards)],
        "samples": samples,
        "mean": mean,
        "variance": sum(probs[a] * sum((samples[a][k] - mean[k]) ** 2 for k in arms) for a in arms),
    }


def bandit_training(steps=5, lr=1.0, rewards=BANDIT_REWARDS):
    logits = [0.0] * len(rewards)
    rows = []
    for _ in range(steps + 1):
        gradient = reinforce_gradient(logits, rewards)
        rows.append({"logits": list(logits), "probs": gradient["probs"], "expected": gradient["expected"]})
        logits = [x + lr * d for x, d in zip(logits, gradient["exact"])]
    return rows


PPO_EPSILON = 0.2
PPO_RATIOS = [0.5, 0.9, 1.1, 1.5]


def ppo_clip(ratio, advantage, epsilon=PPO_EPSILON):
    unclipped = ratio * advantage
    clipped = min(max(ratio, 1 - epsilon), 1 + epsilon) * advantage
    return {
        "unclipped": unclipped,
        "clipped": clipped,
        "objective": min(unclipped, clipped),
        "gradient": advantage if unclipped <= clipped else 0.0,
    }


DIAGNOSTIC_POPULATION = 10000


def diagnostic_test(prevalence=0.01, sensitivity=0.9, false_positive_rate=0.09, population=DIAGNOSTIC_POPULATION):
    sick = prevalence * population
    healthy = population - sick
    true_positives = sensitivity * sick
    false_positives = false_positive_rate * healthy
    evidence = sensitivity * prevalence + false_positive_rate * (1 - prevalence)
    return {
        "sick": sick,
        "healthy": healthy,
        "true_positives": true_positives,
        "false_negatives": sick - true_positives,
        "false_positives": false_positives,
        "true_negatives": healthy - false_positives,
        "evidence": evidence,
        "posterior": sensitivity * prevalence / evidence,
    }


def repeated_tests(prevalence=0.01, sensitivity=0.9, false_positive_rate=0.09, positives=3):
    beliefs = [prevalence]
    for _ in range(positives):
        beliefs.append(diagnostic_test(beliefs[-1], sensitivity, false_positive_rate)["posterior"])
    return beliefs


COIN_HEADS = 7
COIN_FLIPS = 10
COIN_PRIOR = (5, 5)


def binomial_likelihood(theta, heads=COIN_HEADS, flips=COIN_FLIPS):
    return math.comb(flips, heads) * theta**heads * (1 - theta) ** (flips - heads)


def beta_density(theta, a, b):
    return theta ** (a - 1) * (1 - theta) ** (b - 1) * math.gamma(a + b) / (math.gamma(a) * math.gamma(b))


def likelihood_area(heads=COIN_HEADS, flips=COIN_FLIPS, points=10000):
    width = 1 / points
    return sum(binomial_likelihood((i + 0.5) * width, heads, flips) for i in range(points)) * width


def coin_estimates(heads=COIN_HEADS, flips=COIN_FLIPS, prior=COIN_PRIOR):
    a, b = prior
    return {
        "mle": heads / flips,
        "map": (heads + a - 1) / (flips + a + b - 2),
        "posterior_mean": (heads + a) / (flips + a + b),
        "posterior": (heads + a, flips - heads + b),
    }


def coin_curves(heads=COIN_HEADS, flips=COIN_FLIPS, prior=COIN_PRIOR, points=51):
    a, b = prior
    post_a, post_b = heads + a, flips - heads + b
    grid = [i / (points - 1) for i in range(points)]
    curves = {
        "likelihood": [binomial_likelihood(t, heads, flips) for t in grid],
        "prior": [beta_density(t, a, b) for t in grid],
        "posterior": [beta_density(t, post_a, post_b) for t in grid],
    }
    scaled = {name: [v / max(values) for v in values] for name, values in curves.items()}
    return {"theta": grid, **scaled}


def ridge_map_1d(xs, ys, alpha):
    return sum(x * y for x, y in zip(xs, ys)) / (sum(x * x for x in xs) + alpha)


NB_VOCABULARY = ["free", "win", "meeting", "report"]
NB_CLASSES = ["spam", "ham"]
NB_DOCUMENTS = {"spam": 2, "ham": 3}
NB_WORD_COUNTS = {"spam": [3, 2, 0, 1], "ham": [1, 0, 3, 4]}
NB_MESSAGE = [1, 1, 1, 0]


def _log_sum_exp(values):
    finite = [v for v in values if v != -math.inf]
    if not finite:
        return -math.inf
    top = max(finite)
    return top + math.log(sum(math.exp(v - top) for v in finite))


def naive_bayes_posterior(message=NB_MESSAGE, alpha=1.0, counts=None, documents=None):
    counts = counts or NB_WORD_COUNTS
    documents = documents or NB_DOCUMENTS
    total_documents = sum(documents.values())
    rows = {}
    for name in NB_CLASSES:
        smoothed = [c + alpha for c in counts[name]]
        word_probs = [c / sum(smoothed) for c in smoothed]
        prior = documents[name] / total_documents
        joint = math.log(prior) + sum(
            n * (math.log(p) if p > 0 else -math.inf) for n, p in zip(message, word_probs) if n
        )
        rows[name] = {"prior": prior, "word_probs": word_probs, "joint_log": joint}
    evidence = _log_sum_exp([row["joint_log"] for row in rows.values()])
    for row in rows.values():
        row["posterior"] = None if evidence == -math.inf else math.exp(row["joint_log"] - evidence)
    return rows


IMBALANCE_POPULATION = {"negatives": 990, "positives": 10}
IMBALANCE_DATA = {"negatives": 180, "positives": 20, "negative_mean": 0.0, "positive_mean": 2.0, "keep_every": 9}


def balanced_class_weights(counts):
    total = sum(counts)
    return [total / (len(counts) * count) for count in counts]


def balanced_accuracy(tp, fp, fn, tn):
    return (tp / (tp + fn) + tn / (tn + fp)) / 2


def accuracy_paradox(population=IMBALANCE_POPULATION):
    negatives, positives = population["negatives"], population["positives"]
    tp, fp, fn, tn = 0, 0, positives, negatives
    weights = balanced_class_weights([negatives, positives])
    return {
        "accuracy": (tp + tn) / (negatives + positives),
        "recall": tp / (tp + fn),
        "balanced_accuracy": balanced_accuracy(tp, fp, fn, tn),
        "weights": weights,
        "weighted_totals": [weights[0] * negatives, weights[1] * positives],
        "pos_weight": negatives / positives,
        "sampler_positive_share": (positives * (1 / positives)) / (positives * (1 / positives) + negatives * (1 / negatives)),
    }


def imbalance_data(spec=IMBALANCE_DATA):
    unit = statistics.NormalDist()
    def quantiles(n, mean):
        return [mean + unit.inv_cdf((i + 0.5) / n) for i in range(n)]
    xs = quantiles(spec["negatives"], spec["negative_mean"]) + quantiles(spec["positives"], spec["positive_mean"])
    ys = [0] * spec["negatives"] + [1] * spec["positives"]
    return xs, ys


def weighted_logistic_1d(xs, ys, weights=None, iterations=30):
    weights = weights or [1.0] * len(xs)
    w, b = 0.0, 0.0
    for _ in range(iterations):
        probs = [sigmoid(w * x + b) for x in xs]
        g = [sum(s * (p - t) * x for s, p, t, x in zip(weights, probs, ys, xs)),
             sum(s * (p - t) for s, p, t in zip(weights, probs, ys))]
        h = [[sum(s * p * (1 - p) * x * x for s, p, x in zip(weights, probs, xs)),
              sum(s * p * (1 - p) * x for s, p, x in zip(weights, probs, xs))],
             [sum(s * p * (1 - p) * x for s, p, x in zip(weights, probs, xs)),
              sum(s * p * (1 - p) for s, p in zip(weights, probs))]]
        dw, db = solve_linear(h, g)
        w, b = w - dw, b - db
    return w, b


def _threshold_report(xs, ys, w, b, threshold):
    scores = [sigmoid(w * x + b) for x in xs]
    tp, fp, fn, tn = confusion_counts(ys, scores, threshold)
    precision, recall, f1 = precision_recall_f1(tp, fp, fn)
    return {
        "w": w,
        "b": b,
        "threshold": threshold,
        "cut": (math.log(threshold / (1 - threshold)) - b) / w,
        "counts": (tp, fp, fn, tn),
        "accuracy": (tp + tn) / len(ys),
        "balanced_accuracy": balanced_accuracy(tp, fp, fn, tn),
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def undersample_correction(p, kept_fraction):
    return kept_fraction * p / (kept_fraction * p - p + 1)


def imbalance_example(spec=IMBALANCE_DATA):
    xs, ys = imbalance_data(spec)
    negatives, positives = spec["negatives"], spec["positives"]
    weights = balanced_class_weights([negatives, positives])
    sample_weights = [weights[y] for y in ys]
    plain = weighted_logistic_1d(xs, ys)
    weighted = weighted_logistic_1d(xs, ys, sample_weights)
    oversampled_xs = xs + [x for x, y in zip(xs, ys) if y == 1] * (negatives // positives - 1)
    oversampled_ys = ys + [1] * (positives * (negatives // positives - 1))
    oversampled = weighted_logistic_1d(oversampled_xs, oversampled_ys)
    keep = spec["keep_every"]
    under_xs = [x for i, x in enumerate(xs[:negatives]) if i % keep == keep // 2] + xs[negatives:]
    under_ys = [0] * (len(under_xs) - positives) + [1] * positives
    under = weighted_logistic_1d(under_xs, under_ys)
    prior = positives / (negatives + positives)
    kept_fraction = (len(under_xs) - positives) / negatives
    probe = spec["positive_mean"] / 2
    under_p = sigmoid(under[0] * probe + under[1])
    return {
        "xs": xs,
        "ys": ys,
        "weights": weights,
        "plain": _threshold_report(xs, ys, *plain, 0.5),
        "weighted": _threshold_report(xs, ys, *weighted, 0.5),
        "oversampled": _threshold_report(xs, ys, *oversampled, 0.5),
        "undersampled": _threshold_report(xs, ys, *under, 0.5),
        "moved": _threshold_report(xs, ys, *plain, prior),
        "prior": prior,
        "intercept_shift": weighted[1] - plain[1],
        "log_weight_ratio": math.log(weights[1] / weights[0]),
        "average_precision": average_precision(ys, [sigmoid(plain[0] * x + plain[1]) for x in xs]),
        "kept_negatives": len(under_xs) - positives,
        "kept_fraction": kept_fraction,
        "probe": probe,
        "probe_plain": sigmoid(plain[0] * probe + plain[1]),
        "probe_under": under_p,
        "probe_corrected": undersample_correction(under_p, kept_fraction),
    }


FOCAL_PROBS = [0.1, 0.3, 0.5, 0.7, 0.9, 0.99]


def focal_loss(p_t, gamma=2.0, alpha_t=1.0):
    return -alpha_t * (1 - p_t) ** gamma * math.log(p_t)


def focal_table(probs=FOCAL_PROBS, gammas=(0.0, 0.5, 1.0, 2.0, 5.0)):
    return [
        {"p": p, "losses": [focal_loss(p, g) for g in gammas], "ratios": [focal_loss(p, g) / focal_loss(p, 0.0) for g in gammas]}
        for p in probs
    ]


FOREST_DATA = {"n_train": 100, "n_test": 400, "noise": 0.1, "train_seed": 11, "test_seed": 12}
FOREST_FEATURES = ["x₀", "x₁", "noise, continuous", "noise, binary"]
FOREST_METHODS = {
    "bagging": {"max_features": 4, "bootstrap": True, "random_thresholds": False},
    "forest": {"max_features": 2, "bootstrap": True, "random_thresholds": False},
    "extra": {"max_features": 2, "bootstrap": False, "random_thresholds": True},
}


def forest_rows(n, seed, noise=0.1):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        x = (rng.random(), rng.random(), rng.random(), float(rng.randint(0, 1)))
        y = int(x[0] + x[1] > 1.0)
        if rng.random() < noise:
            y = 1 - y
        rows.append((x, y))
    return rows


def _gini_two(n_pos, n):
    p = n_pos / n
    return 2.0 * p * (1.0 - p)


def _best_threshold(rows, feature):
    order = sorted(rows, key=lambda r: r[0][feature])
    n = len(order)
    total_pos = sum(y for _, y in order)
    left_pos = 0
    best = None
    for i in range(1, n):
        left_pos += order[i - 1][1]
        lo, hi = order[i - 1][0][feature], order[i][0][feature]
        if hi <= lo:
            continue
        weighted = (i * _gini_two(left_pos, i) + (n - i) * _gini_two(total_pos - left_pos, n - i)) / n
        if best is None or weighted < best[0] - 1e-12:
            best = (weighted, lo / 2.0 + hi / 2.0)
    return best


def _random_threshold(rows, feature, lo, hi, rng):
    threshold = rng.uniform(lo, hi)
    if threshold == hi:
        threshold = lo
    left = [y for x, y in rows if x[feature] <= threshold]
    n = len(rows)
    left_pos, right_pos = sum(left), sum(y for _, y in rows) - sum(left)
    n_left = len(left)
    weighted = (n_left * _gini_two(left_pos, n_left) + (n - n_left) * _gini_two(right_pos, n - n_left)) / n
    return weighted, threshold


def grow_forest_tree(rows, rng, max_features, random_thresholds=False):
    n = len(rows)
    n_pos = sum(y for _, y in rows)
    node = {"n": n, "value": n_pos / n, "impurity": _gini_two(n_pos, n), "feature": None}
    if n < 2 or n_pos in (0, n):
        return node
    best = None
    visited = 0
    for feature in rng.sample(range(len(rows[0][0])), len(rows[0][0])):
        if visited >= max_features and best is not None:
            break
        visited += 1
        values = [x[feature] for x, _ in rows]
        lo, hi = min(values), max(values)
        if hi <= lo:
            continue
        if random_thresholds:
            weighted, threshold = _random_threshold(rows, feature, lo, hi, rng)
        else:
            weighted, threshold = _best_threshold(rows, feature)
        if best is None or weighted < best[0] - 1e-12:
            best = (weighted, threshold, feature)
    if best is None:
        return node
    _, threshold, feature = best
    node.update(feature=feature, threshold=threshold)
    node["left"] = grow_forest_tree([r for r in rows if r[0][feature] <= threshold], rng, max_features, random_thresholds)
    node["right"] = grow_forest_tree([r for r in rows if r[0][feature] > threshold], rng, max_features, random_thresholds)
    return node


def forest_tree_predict(node, x):
    while node["feature"] is not None:
        node = node["left"] if x[node["feature"]] <= node["threshold"] else node["right"]
    return node["value"]


def forest_tree_importances(node, n_features):
    totals = [0.0] * n_features
    stack = [node]
    while stack:
        nd = stack.pop()
        if nd["feature"] is None:
            continue
        totals[nd["feature"]] += (
            nd["n"] * nd["impurity"] - nd["left"]["n"] * nd["left"]["impurity"] - nd["right"]["n"] * nd["right"]["impurity"]
        )
        stack += [nd["left"], nd["right"]]
    norm = sum(totals)
    return [t / norm for t in totals] if norm > 0 else totals


def fit_forest(rows, n_trees, max_features, bootstrap=True, random_thresholds=False, seed=0):
    rng = random.Random(seed)
    n = len(rows)
    trees = []
    for _ in range(n_trees):
        indices = [rng.randrange(n) for _ in range(n)] if bootstrap else list(range(n))
        tree = grow_forest_tree([rows[i] for i in indices], rng, max_features, random_thresholds)
        trees.append({"tree": tree, "in_bag": set(indices)})
    return trees


def forest_proba(trees, x):
    return sum(forest_tree_predict(t["tree"], x) for t in trees) / len(trees)


def forest_accuracy(trees, rows):
    return sum(int(forest_proba(trees, x) > 0.5) == y for x, y in rows) / len(rows)


def oob_accuracy(trees, rows):
    correct = scored = 0
    for i, (x, y) in enumerate(rows):
        votes = [forest_tree_predict(t["tree"], x) for t in trees if i not in t["in_bag"]]
        if votes:
            scored += 1
            correct += int(sum(votes) / len(votes) > 0.5) == y
    return correct / scored if scored else 0.0


def impurity_importances(trees, n_features):
    per_tree = [forest_tree_importances(t["tree"], n_features) for t in trees if t["tree"]["feature"] is not None]
    mean = [sum(col) / len(per_tree) for col in zip(*per_tree)]
    total = sum(mean)
    return [m / total for m in mean]


def permutation_importances(trees, rows, n_repeats=5, seed=0):
    rng = random.Random(seed)
    baseline = forest_accuracy(trees, rows)
    out = []
    for feature in range(len(rows[0][0])):
        drops = []
        for _ in range(n_repeats):
            column = [x[feature] for x, _ in rows]
            rng.shuffle(column)
            permuted = [(x[:feature] + (v,) + x[feature + 1:], y) for (x, y), v in zip(rows, column)]
            drops.append(baseline - forest_accuracy(trees, permuted))
        out.append({"mean": sum(drops) / n_repeats, "std": statistics.pstdev(drops)})
    return {"baseline": baseline, "features": out}


def bootstrap_oob_fraction(n):
    return (1.0 - 1.0 / n) ** n


def averaged_variance(rho, sigma2, n_trees):
    return rho * sigma2 + (1.0 - rho) * sigma2 / n_trees


def forest_example(spec=FOREST_DATA, n_trees=100):
    train = forest_rows(spec["n_train"], spec["train_seed"], spec["noise"])
    test = forest_rows(spec["n_test"], spec["test_seed"], spec["noise"])
    single = fit_forest(train, 1, 4, bootstrap=False, seed=1)
    out = {
        "train": train, "test": test,
        "single": {"train_accuracy": forest_accuracy(single, train), "test_accuracy": forest_accuracy(single, test)},
        "n_trees": n_trees,
    }
    for name, m in FOREST_METHODS.items():
        trees = fit_forest(train, n_trees, m["max_features"], m["bootstrap"], m["random_thresholds"], seed=2)
        curve = []
        sums = [0.0] * len(test)
        for b, t in enumerate(trees, 1):
            sums = [s + forest_tree_predict(t["tree"], x) for s, (x, _) in zip(sums, test)]
            curve.append(sum(int(s / b > 0.5) == y for s, (_, y) in zip(sums, test)) / len(test))
        out[name] = {
            "test_accuracy": curve[-1],
            "curve": curve,
            "train_accuracy": forest_accuracy(trees, train),
            "oob_accuracy": oob_accuracy(trees, train) if m["bootstrap"] else None,
            "mean_oob_fraction": sum(1 - len(t["in_bag"]) / len(train) for t in trees) / n_trees if m["bootstrap"] else None,
            "tree_accuracy": sum(forest_accuracy([t], test) for t in trees) / n_trees,
        }
        if name == "forest":
            out[name]["impurity"] = impurity_importances(trees, len(FOREST_FEATURES))
            out[name]["permutation"] = permutation_importances(trees, test)
    return out


def tree_correlation(max_features, bootstrap=True, random_thresholds=False, n_sets=20, n_trees=20, n_points=100):
    points = [x for x, _ in forest_rows(n_points, 99)]
    by_set = []
    for s in range(n_sets):
        train = forest_rows(FOREST_DATA["n_train"], 500 + s, FOREST_DATA["noise"])
        trees = fit_forest(train, n_trees, max_features, bootstrap, random_thresholds, seed=700 + s)
        by_set.append([[forest_tree_predict(t["tree"], x) for x in points] for t in trees])
    total = between = within = 0.0
    for j in range(n_points):
        all_preds = [tree[j] for trees in by_set for tree in trees]
        means = [sum(tree[j] for tree in trees) / n_trees for trees in by_set]
        within_j = sum(statistics.pvariance([tree[j] for tree in trees]) for trees in by_set) / n_sets
        total += statistics.pvariance(all_preds)
        within += within_j
        between += max(statistics.pvariance(means) - within_j / n_trees, 0.0)
    sigma2 = total / n_points
    return {"sigma2": sigma2, "rho": between / total, "within": within / n_points, "between": between / n_points}


def init_gain(nonlinearity, param=None):
    if nonlinearity in ("linear", "sigmoid"):
        return 1.0
    if nonlinearity == "tanh":
        return 5.0 / 3
    if nonlinearity == "relu":
        return math.sqrt(2.0)
    if nonlinearity == "leaky_relu":
        slope = 0.01 if param is None else param
        return math.sqrt(2.0 / (1 + slope ** 2))
    if nonlinearity == "selu":
        return 3.0 / 4
    raise ValueError(nonlinearity)


def fan_in_and_fan_out(shape):
    receptive = 1
    for s in shape[2:]:
        receptive *= s
    return shape[1] * receptive, shape[0] * receptive


def xavier_std(fan_in, fan_out, gain=1.0):
    return gain * math.sqrt(2.0 / (fan_in + fan_out))


def kaiming_std(fan, nonlinearity="leaky_relu", a=0):
    return init_gain(nonlinearity, a) / math.sqrt(fan)


def uniform_bound(std):
    return math.sqrt(3.0) * std


def linear_default_bound(fan_in):
    return uniform_bound(kaiming_std(fan_in, "leaky_relu", math.sqrt(5)))


def relu_moment_factor(fan_in, weight_var):
    return fan_in * weight_var / 2


INIT_SCHEMES = [
    {"key": "small", "label": "N(0, 0.01²)", "activation": "relu", "dist": "normal", "std": lambda n: 0.01},
    {"key": "pytorch", "label": "nn.Linear default, U(±1/√n)", "activation": "relu", "dist": "uniform", "std": lambda n: linear_default_bound(n) / math.sqrt(3.0)},
    {"key": "xavier", "label": "Xavier, gain 1", "activation": "relu", "dist": "normal", "std": lambda n: xavier_std(n, n)},
    {"key": "kaiming", "label": "Kaiming, gain √2", "activation": "relu", "dist": "normal", "std": lambda n: kaiming_std(n, "relu")},
    {"key": "large", "label": "N(0, 1)", "activation": "relu", "dist": "normal", "std": lambda n: 1.0},
    {"key": "tanh-xavier", "label": "tanh, Xavier gain 1", "activation": "tanh", "dist": "normal", "std": lambda n: xavier_std(n, n)},
    {"key": "tanh-gain", "label": "tanh, gain 5/3", "activation": "tanh", "dist": "normal", "std": lambda n: xavier_std(n, n, 5.0 / 3)},
]


def _rms(rows):
    total = sum(v * v for row in rows for v in row)
    return math.sqrt(total / sum(len(row) for row in rows))


def deep_signal(scheme, width=32, depth=20, batch=16, seed=0):
    rng = random.Random(seed)
    std = scheme["std"](width)
    bound = math.sqrt(3.0) * std

    def draw():
        return rng.uniform(-bound, bound) if scheme["dist"] == "uniform" else rng.gauss(0.0, std)

    weights = [[[draw() for _ in range(width)] for _ in range(width)] for _ in range(depth)]
    tanh = scheme["activation"] == "tanh"
    h = [[rng.gauss(0.0, 1.0) for _ in range(width)] for _ in range(batch)]
    forward = [_rms(h)]
    slopes = []
    for w in weights:
        z = [[sum(wi * xi for wi, xi in zip(row, x)) for row in w] for x in h]
        if tanh:
            h = [[math.tanh(v) for v in r] for r in z]
            slopes.append([[1 - math.tanh(v) ** 2 for v in r] for r in z])
        else:
            h = [[v if v > 0 else 0.0 for v in r] for r in z]
            slopes.append([[1.0 if v > 0 else 0.0 for v in r] for r in z])
        forward.append(_rms(h))
    g = [[rng.gauss(0.0, 1.0) for _ in range(width)] for _ in range(batch)]
    backward = [_rms(g)]
    for w, slope in zip(reversed(weights), reversed(slopes)):
        dz = [[gi * si for gi, si in zip(gr, sr)] for gr, sr in zip(g, slope)]
        g = [[sum(w[i][j] * d[i] for i in range(width)) for j in range(width)] for d in dz]
        backward.append(_rms(g))
    backward.reverse()
    return {"std": std, "forward": forward, "backward": backward}


def init_example(width=32, depth=20):
    return {
        "width": width,
        "depth": depth,
        "schemes": [dict(s, result=deep_signal(s, width, depth)) for s in INIT_SCHEMES],
    }


RNN_EXAMPLE = {
    "xs": [1.0, 0.5, -1.0],
    "w_ih": [[0.5], [-0.3]],
    "w_hh": [[0.8, -0.2], [0.4, 0.6]],
    "b": [0.0, 0.1],
}

LSTM_EXAMPLE = {
    "i": {"wx": 0.6, "wh": 0.2, "b": 0.0},
    "f": {"wx": 0.3, "wh": 0.1, "b": 1.0},
    "g": {"wx": 1.0, "wh": -0.5, "b": 0.0},
    "o": {"wx": 0.4, "wh": 0.3, "b": 0.0},
}

GRU_EXAMPLE = {
    "r": {"wx": 0.5, "wh": 0.4, "b": 0.0},
    "z": {"wx": 0.7, "wh": -0.3, "b": 0.0},
    "n": {"wx": 1.0, "wh": 0.6, "b": 0.0},
}


def rnn_forward(xs, w_ih, w_hh, b, h0=None):
    h = list(h0) if h0 is not None else [0.0] * len(w_hh)
    steps = []
    for x in xs:
        x = x if isinstance(x, list) else [x]
        from_x = [sum(w * v for w, v in zip(row, x)) for row in w_ih]
        from_h = [sum(w * v for w, v in zip(row, h)) for row in w_hh]
        pre = [a + c + bias for a, c, bias in zip(from_x, from_h, b)]
        h = [math.tanh(p) for p in pre]
        steps.append({"x": x, "from_x": from_x, "from_h": from_h, "pre": pre, "h": h})
    return steps


def lstm_step(x, h, c, weights):
    pre = {k: w["wx"] * x + w["wh"] * h + w["b"] for k, w in weights.items()}
    i, f, o = sigmoid(pre["i"]), sigmoid(pre["f"]), sigmoid(pre["o"])
    g = math.tanh(pre["g"])
    c_new = f * c + i * g
    h_new = o * math.tanh(c_new)
    return {"pre": pre, "i": i, "f": f, "g": g, "o": o, "c": c_new, "h": h_new}


def lstm_forward(xs, weights, h0=0.0, c0=0.0):
    h, c, steps = h0, c0, []
    for x in xs:
        s = lstm_step(x, h, c, weights)
        steps.append(dict(s, x=x, h_prev=h, c_prev=c))
        h, c = s["h"], s["c"]
    return steps


def gru_step(x, h, weights):
    r = sigmoid(weights["r"]["wx"] * x + weights["r"]["wh"] * h + weights["r"]["b"])
    z = sigmoid(weights["z"]["wx"] * x + weights["z"]["wh"] * h + weights["z"]["b"])
    n = math.tanh(weights["n"]["wx"] * x + r * (weights["n"]["wh"] * h) + weights["n"]["b"])
    return {"r": r, "z": z, "n": n, "h": (1 - z) * n + z * h}


def gru_forward(xs, weights, h0=0.0):
    h, steps = h0, []
    for x in xs:
        s = gru_step(x, h, weights)
        steps.append(dict(s, x=x, h_prev=h))
        h = s["h"]
    return steps


def rnn_memory_gradient(w, steps=30, u=1.0, b=0.0):
    h = math.tanh(u * 1.0 + b)
    dh = 1.0
    out = [{"t": 1, "h": h, "grad": dh}]
    for t in range(2, steps + 1):
        h = math.tanh(w * h + b)
        dh = (1 - h * h) * w * dh
        out.append({"t": t, "h": h, "grad": dh})
    return out


def lstm_memory_gradient(forget_bias, steps=30, weights=None):
    weights = {k: dict(v) for k, v in (weights or LSTM_EXAMPLE).items()}
    weights["f"]["b"] = forget_bias
    first = lstm_step(1.0, 0.0, 0.0, weights)
    h, c = first["h"], first["c"]
    dh, dc = 0.0, 1.0
    direct = 1.0
    out = [{"t": 1, "c": c, "grad": dc, "direct": direct, "f": first["f"]}]
    for t in range(2, steps + 1):
        s = lstm_step(0.0, h, c, weights)
        da = {k: weights[k]["wh"] * dh for k in weights}
        di = s["i"] * (1 - s["i"]) * da["i"]
        df = s["f"] * (1 - s["f"]) * da["f"]
        do = s["o"] * (1 - s["o"]) * da["o"]
        dg = (1 - s["g"] ** 2) * da["g"]
        dc_new = df * c + s["f"] * dc + di * s["g"] + s["i"] * dg
        tc = math.tanh(s["c"])
        dh = do * tc + s["o"] * (1 - tc * tc) * dc_new
        dc = dc_new
        direct *= s["f"]
        h, c = s["h"], s["c"]
        out.append({"t": t, "c": c, "grad": dc, "direct": direct, "f": s["f"]})
    return out


RNN_MEMORY_CASES = [
    {"key": "rnn-small", "label": "RNN, w = 0.5", "kind": "rnn", "value": 0.5},
    {"key": "rnn-near-one", "label": "RNN, w = 0.95", "kind": "rnn", "value": 0.95},
    {"key": "rnn-large", "label": "RNN, w = 2", "kind": "rnn", "value": 2.0},
    {"key": "lstm-0", "label": "LSTM, forget bias 0", "kind": "lstm", "value": 0.0},
    {"key": "lstm-3", "label": "LSTM, forget bias 3", "kind": "lstm", "value": 3.0},
]


def memory_gradient_example(steps=30):
    out = []
    for case in RNN_MEMORY_CASES:
        if case["kind"] == "rnn":
            trace = rnn_memory_gradient(case["value"], steps)
        else:
            trace = lstm_memory_gradient(case["value"], steps)
        out.append(dict(case, trace=trace))
    return out


def rnn_param_count(mode, input_size, hidden_size, num_layers=1, bias=True, bidirectional=False, proj_size=0):
    gate_size = {"LSTM": 4, "GRU": 3, "RNN_TANH": 1, "RNN_RELU": 1}[mode] * hidden_size
    directions = 2 if bidirectional else 1
    real_hidden = proj_size if proj_size > 0 else hidden_size
    total = 0
    for layer in range(num_layers):
        layer_input = input_size if layer == 0 else real_hidden * directions
        per_direction = gate_size * layer_input + gate_size * real_hidden
        if bias:
            per_direction += 2 * gate_size
        if proj_size > 0:
            per_direction += proj_size * hidden_size
        total += per_direction * directions
    return total


def pack_sequences(sequences, enforce_sorted=True):
    lengths = [len(s) for s in sequences]
    if enforce_sorted:
        if lengths != sorted(lengths, reverse=True):
            raise ValueError("sequences must be sorted by decreasing length")
        order = None
        ordered = list(sequences)
    else:
        order = sorted(range(len(sequences)), key=lambda k: -lengths[k])
        ordered = [sequences[k] for k in order]
    batch_sizes = [sum(1 for s in ordered if len(s) > t) for t in range(len(ordered[0]))]
    data = [s[t] for t in range(len(batch_sizes)) for s in ordered[: batch_sizes[t]]]
    unsorted = None
    if order is not None:
        unsorted = [0] * len(order)
        for position, k in enumerate(order):
            unsorted[k] = position
    return {"data": data, "batch_sizes": batch_sizes, "sorted_indices": order, "unsorted_indices": unsorted}


def padded_waste(lengths):
    return {"padded": len(lengths) * max(lengths), "packed": sum(lengths)}


def seq2seq_attention(encoder_states, query):
    scores = [sum(a * b for a, b in zip(s, query)) for s in encoder_states]
    weights = softmax_probs(scores)
    context = [sum(w * s[d] for w, s in zip(weights, encoder_states)) for d in range(len(query))]
    return {"scores": scores, "weights": weights, "context": context}


def rnn_example():
    e = RNN_EXAMPLE
    rnn = rnn_forward(e["xs"], e["w_ih"], e["w_hh"], e["b"])
    states = [s["h"] for s in rnn]
    return {
        "rnn": rnn,
        "lstm": lstm_forward(e["xs"], LSTM_EXAMPLE),
        "gru": gru_forward(e["xs"], GRU_EXAMPLE),
        "attention": seq2seq_attention(states, states[-1]),
        "memory": memory_gradient_example(),
    }


AUTOENCODER_EXAMPLE = {"count": 40, "seed": 7, "direction": [0.8, 0.6], "spread": 2.0, "noise": 0.4, "lr": 0.05, "steps": 1000, "noise_levels": [0.0, 0.5, 2.0]}


def autoencoder_points(count, seed, direction, spread, noise):
    rng = random.Random(seed)
    ux, uy = direction
    raw = []
    for _ in range(count):
        t = rng.gauss(0.0, spread)
        s = rng.gauss(0.0, noise)
        raw.append([t * ux - s * uy, t * uy + s * ux])
    mean = [sum(p[k] for p in raw) / count for k in range(2)]
    return [[p[0] - mean[0], p[1] - mean[1]] for p in raw]


def second_moment(points):
    n = len(points)
    return [[sum(p[i] * p[j] for p in points) / n for j in range(2)] for i in range(2)]


def reconstruction_mse(points, encoder, decoder):
    total = 0.0
    for p in points:
        z = encoder[0] * p[0] + encoder[1] * p[1]
        total += (p[0] - decoder[0] * z) ** 2 + (p[1] - decoder[1] * z) ** 2
    return total / (2 * len(points))


def train_linear_autoencoder(points, lr, steps, seed=0):
    rng = random.Random(seed)
    encoder = [rng.uniform(-0.5, 0.5) for _ in range(2)]
    decoder = [rng.uniform(-0.5, 0.5) for _ in range(2)]
    n = len(points)
    history = [reconstruction_mse(points, encoder, decoder)]
    start = (list(encoder), list(decoder))
    for _ in range(steps):
        grad_e = [0.0, 0.0]
        grad_d = [0.0, 0.0]
        for p in points:
            z = encoder[0] * p[0] + encoder[1] * p[1]
            r = [p[0] - decoder[0] * z, p[1] - decoder[1] * z]
            back = decoder[0] * r[0] + decoder[1] * r[1]
            for k in range(2):
                grad_d[k] -= z * r[k] / n
                grad_e[k] -= back * p[k] / n
        encoder = [w - lr * g for w, g in zip(encoder, grad_e)]
        decoder = [w - lr * g for w, g in zip(decoder, grad_d)]
        history.append(reconstruction_mse(points, encoder, decoder))
    return {"start": start, "encoder": encoder, "decoder": decoder, "history": history}


def denoising_linear_map(moment, noise_variance):
    shifted = [[moment[i][j] + (noise_variance if i == j else 0.0) for j in range(2)] for i in range(2)]
    return matmul(moment, inverse_2x2(shifted))


def conv_transpose_output_size(n, kernel, stride=1, padding=0, output_padding=0, dilation=1):
    return (n - 1) * stride - 2 * padding + dilation * (kernel - 1) + output_padding + 1


def conv_autoencoder_shapes(latent=16):
    rows = []
    c, h = 1, 28
    rows.append({"layer": "input", "shape": (c, h, h), "params": 0})
    for out in (16, 32):
        h = conv_output_size(h, 3, stride=2, padding=1)
        rows.append({"layer": f"Conv2d({c}, {out}, 3, stride=2, padding=1) + ReLU", "shape": (out, h, h), "params": conv_params(c, out, 3)})
        c = out
    flat = c * h * h
    rows.append({"layer": "Flatten", "shape": (flat,), "params": 0})
    rows.append({"layer": f"Linear({flat}, {latent})", "shape": (latent,), "params": flat * latent + latent, "code": True})
    rows.append({"layer": f"Linear({latent}, {flat}) + ReLU", "shape": (flat,), "params": latent * flat + flat})
    rows.append({"layer": f"Unflatten(1, ({c}, {h}, {h}))", "shape": (c, h, h), "params": 0})
    for out in (16, 1):
        h = conv_transpose_output_size(h, 3, stride=2, padding=1, output_padding=1)
        act = " + ReLU" if out > 1 else " + Sigmoid"
        rows.append({"layer": f"ConvTranspose2d({c}, {out}, 3, stride=2, padding=1, output_padding=1){act}", "shape": (out, h, h), "params": conv_params(c, out, 3)})
        c = out
    return rows


def autoencoder_example():
    e = AUTOENCODER_EXAMPLE
    points = autoencoder_points(e["count"], e["seed"], e["direction"], e["spread"], e["noise"])
    moment = second_moment(points)
    eig = jacobi_eigh(moment)
    top = eig["vectors"][1]
    trained = train_linear_autoencoder(points, e["lr"], e["steps"])
    enc, dec = trained["encoder"], trained["decoder"]
    dec_norm = math.hypot(*dec)
    product = [[dec[i] * enc[j] for j in range(2)] for i in range(2)]
    projections = []
    for p in points:
        z = enc[0] * p[0] + enc[1] * p[1]
        projections.append([dec[0] * z, dec[1] * z])
    denoise = []
    for sigma in e["noise_levels"]:
        var = sigma ** 2
        denoise.append({"sigma": sigma, "map": denoising_linear_map(moment, var), "shrink": [lam / (lam + var) for lam in eig["values"]]})
    return {
        "points": points,
        "projections": projections,
        "moment": moment,
        "eigenvalues": eig["values"],
        "top": top,
        "trained": trained,
        "product": product,
        "cosine": abs(dec[0] * top[0] + dec[1] * top[1]) / dec_norm,
        "pca_mse": eig["values"][0] / 2,
        "total_mse": (eig["values"][0] + eig["values"][1]) / 2,
        "denoise": denoise,
        "shapes": conv_autoencoder_shapes(),
    }


VAE_EXAMPLE = {
    "weight": 2.0,
    "noise": 1.0,
    "x": 3.0,
    "guesses": [(0.0, 1.0), (1.0, 0.5), (1.5, 0.2)],
    "target": 1.0,
    "mu": 0.5,
    "sigma": 0.8,
    "samples": 1000,
    "seed": 11,
    "code_mu": [1.2, -0.4, 0.0, 0.02],
    "code_logvar": [-2.0, -0.5, 0.0, -0.01],
    "betas": [0.5, 1.0, 4.0],
}


def normal_log_prob(value, loc, scale):
    return -((value - loc) ** 2) / (2 * scale ** 2) - math.log(scale) - math.log(math.sqrt(2 * math.pi))


def normal_kl(p_loc, p_scale, q_loc, q_scale):
    var_ratio = (p_scale / q_scale) ** 2
    t1 = ((p_loc - q_loc) / q_scale) ** 2
    return 0.5 * (var_ratio + t1 - 1 - math.log(var_ratio))


def standard_normal_kl(mu, logvar):
    return 0.5 * (math.exp(logvar) + mu ** 2 - 1 - logvar)


def linear_gaussian_evidence(x, weight, noise):
    return normal_log_prob(x, 0.0, math.sqrt(weight ** 2 + noise ** 2))


def linear_gaussian_posterior(x, weight, noise):
    total = weight ** 2 + noise ** 2
    return weight * x / total, math.sqrt(noise ** 2 / total)


def linear_gaussian_elbo(x, weight, noise, q_loc, q_scale):
    expected = -0.5 * math.log(2 * math.pi * noise ** 2) - ((x - weight * q_loc) ** 2 + weight ** 2 * q_scale ** 2) / (2 * noise ** 2)
    kl = normal_kl(q_loc, q_scale, 0.0, 1.0)
    return {"reconstruction": expected, "kl": kl, "elbo": expected - kl}


def gradient_estimators(mu, sigma, target, samples, seed):
    rng = random.Random(seed)
    reparam = []
    score = []
    for _ in range(samples):
        eps = rng.gauss(0.0, 1.0)
        z = mu + sigma * eps
        value = (z - target) ** 2
        reparam.append(2 * (z - target))
        score.append(value * eps / sigma)

    def summary(xs):
        mean = sum(xs) / len(xs)
        var = sum((x - mean) ** 2 for x in xs) / (len(xs) - 1)
        return {"mean": mean, "std": math.sqrt(var)}

    return {"exact": 2 * (mu - target), "reparam": summary(reparam), "score": summary(score)}


def normal_curve(loc, scale, low, high, steps=60):
    width = (high - low) / steps
    return [(low + i * width, math.exp(normal_log_prob(low + i * width, loc, scale))) for i in range(steps + 1)]


def vae_example():
    e = VAE_EXAMPLE
    w, s, x = e["weight"], e["noise"], e["x"]
    post_loc, post_scale = linear_gaussian_posterior(x, w, s)
    evidence = linear_gaussian_evidence(x, w, s)
    rows = []
    for loc, scale in list(e["guesses"]) + [(post_loc, post_scale)]:
        parts = linear_gaussian_elbo(x, w, s, loc, scale)
        rows.append({
            "loc": loc,
            "scale": scale,
            **parts,
            "gap": evidence - parts["elbo"],
            "posterior_kl": normal_kl(loc, scale, post_loc, post_scale),
        })
    code = []
    for mu, logvar in zip(e["code_mu"], e["code_logvar"]):
        code.append({"mu": mu, "logvar": logvar, "sigma": math.exp(0.5 * logvar), "kl": standard_normal_kl(mu, logvar)})
    code_kl = sum(c["kl"] for c in code)
    return {
        "posterior": (post_loc, post_scale),
        "evidence": evidence,
        "marginal_scale": math.sqrt(w ** 2 + s ** 2),
        "rows": rows,
        "gradients": gradient_estimators(e["mu"], e["sigma"], e["target"], e["samples"], e["seed"]),
        "code": code,
        "code_kl": code_kl,
        "betas": [{"beta": b, "penalty": b * code_kl} for b in e["betas"]],
        "curves": {
            "prior": normal_curve(0.0, 1.0, -3.0, 3.5),
            "posterior": normal_curve(post_loc, post_scale, -3.0, 3.5),
            "guess": normal_curve(e["guesses"][1][0], e["guesses"][1][1], -3.0, 3.5),
        },
    }



POSITION_EXAMPLE = {
    "d_model": 8,
    "base": 10000.0,
    "positions": [0, 1, 2, 5, 20],
    "offset": 3,
    "query": [1.0, 0.5, -0.5, 1.0],
    "key": [0.5, 1.0, 1.0, 0.5],
    "rope_base": 100.0,
    "pairs": [(0, 3), (2, 5), (10, 13), (40, 43)],
    "score_offsets": [0, 1, 2, 4, 8, 16],
    "alibi_heads": 8,
    "alibi_length": 6,
    "alibi_scores": [0.8, 0.1, 0.5, 0.9, 0.3, 0.6],
    "curve_dims": 64,
    "curve_pairs": [0, 2, 4, 8],
    "curve_positions": 40,
}


def sinusoidal_frequencies(d_model, base=10000.0):
    return [base ** (-2 * i / d_model) for i in range(d_model // 2)]


def sinusoidal_encoding(position, d_model, base=10000.0):
    out = []
    for w in sinusoidal_frequencies(d_model, base):
        out += [math.sin(position * w), math.cos(position * w)]
    return out


def rotate_pairs(vec, angles):
    out = []
    for i, a in enumerate(angles):
        x, y = vec[2 * i], vec[2 * i + 1]
        out += [x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)]
    return out


def shift_encoding(encoding, offset, d_model, base=10000.0):
    return rotate_pairs(encoding, [-offset * w for w in sinusoidal_frequencies(d_model, base)])


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def sinusoidal_similarity(p, q, d_model, base=10000.0):
    return _dot(sinusoidal_encoding(p, d_model, base), sinusoidal_encoding(q, d_model, base))


def rope(vec, position, base=10000.0):
    return rotate_pairs(vec, [position * w for w in sinusoidal_frequencies(len(vec), base)])


def rope_score(query, key, m, n, base=10000.0):
    return _dot(rope(query, m, base), rope(key, n, base))


def alibi_slopes(heads):
    start = 2 ** (-8 / heads)
    return [start ** (i + 1) for i in range(heads)]


def alibi_bias(length, slope):
    return [[-slope * (i - j) + 0.0 if j <= i else None for j in range(length)] for i in range(length)]


def alibi_weights(scores, slope):
    last = len(scores) - 1
    return softmax_probs([s - slope * (last - j) for j, s in enumerate(scores)])


def learned_position_params(max_positions, d_model):
    return max_positions * d_model


def position_example():
    e = POSITION_EXAMPLE
    d, base = e["d_model"], e["base"]
    freqs = sinusoidal_frequencies(d, base)
    table = [{"pos": p, "pe": sinusoidal_encoding(p, d, base)} for p in e["positions"]]
    shift_from = e["positions"][2]
    shifted = shift_encoding(sinusoidal_encoding(shift_from, d, base), e["offset"], d, base)
    direct = sinusoidal_encoding(shift_from + e["offset"], d, base)
    q, k, rb = e["query"], e["key"], e["rope_base"]
    rope_rows = []
    for m, n in e["pairs"]:
        rope_rows.append({
            "m": m, "n": n,
            "q": rope(q, m, rb), "k": rope(k, n, rb),
            "score": rope_score(q, k, m, n, rb),
            "absolute": _dot([a + b for a, b in zip(q, sinusoidal_encoding(m, 4, rb))],
                             [a + b for a, b in zip(k, sinusoidal_encoding(n, 4, rb))]),
        })
    slopes = alibi_slopes(e["alibi_heads"])
    scores = e["alibi_scores"]
    return {
        "freqs": freqs,
        "wavelengths": [2 * math.pi / w for w in freqs],
        "table": table,
        "shift_from": shift_from,
        "shifted": shifted,
        "direct": direct,
        "similarity": [{"offset": k, "value": sinusoidal_similarity(0, k, d, base)} for k in e["score_offsets"]],
        "rope_freqs": sinusoidal_frequencies(4, rb),
        "rope_rows": rope_rows,
        "rope_offsets": [{"offset": n, "score": rope_score(q, k, 0, n, rb)} for n in e["score_offsets"]],
        "plain_score": _dot(q, k),
        "slopes": slopes,
        "bias": alibi_bias(e["alibi_length"], slopes[0]),
        "alibi_rows": [
            {"head": None, "slope": 0.0, "weights": softmax_probs(scores)},
            {"head": 1, "slope": slopes[0], "weights": alibi_weights(scores, slopes[0])},
            {"head": 3, "slope": slopes[2], "weights": alibi_weights(scores, slopes[2])},
            {"head": e["alibi_heads"], "slope": slopes[-1], "weights": alibi_weights(scores, slopes[-1])},
        ],
        "curves": [
            {"pair": i, "freq": sinusoidal_frequencies(e["curve_dims"], base)[i],
             "points": [(p / 2, math.sin(p / 2 * sinusoidal_frequencies(e["curve_dims"], base)[i])) for p in range(2 * e["curve_positions"] + 1)]}
            for i in e["curve_pairs"]
        ],
        "gpt2_table": learned_position_params(1024, 768),
    }

CLUSTER_EXAMPLE = {
    "centers": [(2.0, 2.0), (7.0, 2.5), (4.5, 7.0)],
    "spread": 0.7,
    "per_blob": 12,
    "seed": 4,
    "outliers": [(9.2, 8.6), (0.6, 8.8)],
    "bad_init": [0, 25, 30],
    "plusplus_first": 0,
    "plusplus_draws": [0.62, 0.35],
    "k_range": [1, 2, 3, 4, 5],
    "seeds": 10,
    "eps": 1.0,
    "min_samples": 4,
    "moon_points": 10,
    "moons_eps": 1.0,
    "moons_min_samples": 3,
    "gmm_iterations": 100,
    "em_iterations": 8,
    "queries": [(2.5, 2.5), (4.1, 2.2), (3.5, 5.0)],
    "reg_covar": 1e-6,
}


def blob_points(centers, spread, per_blob, seed):
    rng = random.Random(seed)
    return [(round(rng.gauss(cx, spread), 1), round(rng.gauss(cy, spread), 1))
            for cx, cy in centers for _ in range(per_blob)]


def moon_points(n):
    upper = [(2 * math.cos(math.pi * i / (n - 1)), 2 * math.sin(math.pi * i / (n - 1))) for i in range(n)]
    lower = [(2 - 2 * math.cos(math.pi * i / (n - 1)), 1 - 2 * math.sin(math.pi * i / (n - 1))) for i in range(n)]
    return upper + lower


def _sq_dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def assign_labels(points, centers):
    return [min(range(len(centers)), key=lambda c: _sq_dist(p, centers[c])) for p in points]


def kmeans_inertia(points, centers, labels):
    return sum(_sq_dist(p, centers[c]) for p, c in zip(points, labels))


def lloyd(points, centers, max_iter=100):
    centers = [tuple(c) for c in centers]
    history = []
    for _ in range(max_iter):
        labels = assign_labels(points, centers)
        history.append({"centers": centers, "labels": labels, "inertia": kmeans_inertia(points, centers, labels)})
        new_centers = []
        for c in range(len(centers)):
            members = [p for p, l in zip(points, labels) if l == c]
            if members:
                new_centers.append(tuple(sum(v) / len(members) for v in zip(*members)))
            else:
                new_centers.append(centers[c])
        if new_centers == centers:
            break
        centers = new_centers
    return history


def kmeans_plusplus(points, k, first, draws):
    chosen = [first]
    steps = []
    for u in draws[: k - 1]:
        d2 = [min(_sq_dist(p, points[c]) for c in chosen) for p in points]
        total = sum(d2)
        target, running, pick = u * total, 0.0, len(points) - 1
        for i, d in enumerate(d2):
            running += d
            if running > target:
                pick = i
                break
        steps.append({"d2": d2, "probs": [d / total for d in d2], "pick": pick})
        chosen.append(pick)
    return chosen, steps


def best_of_kmeans(points, k, seeds):
    best = None
    for seed in range(seeds):
        rng = random.Random(seed)
        first = rng.randrange(len(points))
        chosen, _ = kmeans_plusplus(points, k, first, [rng.random() for _ in range(k - 1)])
        run = lloyd(points, [points[i] for i in chosen])[-1]
        if best is None or run["inertia"] < best["inertia"] - 1e-12:
            best = run
    return best


def silhouette_samples(points, labels):
    clusters = sorted(set(labels))
    if len(clusters) < 2:
        return [0.0] * len(points)
    scores = []
    for i, p in enumerate(points):
        mean_to = {}
        for c in clusters:
            others = [math.sqrt(_sq_dist(p, q)) for j, q in enumerate(points) if labels[j] == c and j != i]
            mean_to[c] = sum(others) / len(others) if others else 0.0
        own = [j for j in range(len(points)) if labels[j] == labels[i] and j != i]
        if not own:
            scores.append(0.0)
            continue
        a = mean_to[labels[i]]
        b = min(v for c, v in mean_to.items() if c != labels[i])
        scores.append((b - a) / max(a, b))
    return scores


def silhouette_score(points, labels):
    s = silhouette_samples(points, labels)
    return sum(s) / len(s)


def dbscan(points, eps, min_samples):
    n = len(points)
    neighborhoods = [[j for j in range(n) if _sq_dist(points[i], points[j]) <= eps ** 2] for i in range(n)]
    core = [len(nb) >= min_samples for nb in neighborhoods]
    labels = [-1] * n
    label = 0
    for i in range(n):
        if labels[i] != -1 or not core[i]:
            continue
        stack = [i]
        while stack:
            v = stack.pop()
            if labels[v] != -1:
                continue
            labels[v] = label
            if core[v]:
                stack.extend(w for w in neighborhoods[v] if labels[w] == -1)
        label += 1
    kinds = ["core" if core[i] else "border" if labels[i] != -1 else "noise" for i in range(n)]
    return {"labels": labels, "kinds": kinds, "neighbors": [len(nb) for nb in neighborhoods]}


def _gauss2_logpdf(x, mean, cov):
    a, b, d = cov[0][0], cov[0][1], cov[1][1]
    det = a * d - b * b
    dx, dy = x[0] - mean[0], x[1] - mean[1]
    maha = (d * dx * dx - 2 * b * dx * dy + a * dy * dy) / det
    return -0.5 * (maha + math.log(det) + 2 * math.log(2 * math.pi))


def gmm_e_step(points, weights, means, covs):
    resp, total = [], 0.0
    for p in points:
        logs = [math.log(w) + _gauss2_logpdf(p, m, c) for w, m, c in zip(weights, means, covs)]
        norm = _log_sum_exp(logs)
        total += norm
        resp.append([math.exp(l - norm) for l in logs])
    return resp, total / len(points)


def gmm_m_step(points, resp, reg_covar=1e-6):
    k, n = len(resp[0]), len(points)
    weights, means, covs = [], [], []
    for c in range(k):
        r = [row[c] for row in resp]
        nk = sum(r)
        mx = sum(ri * p[0] for ri, p in zip(r, points)) / nk
        my = sum(ri * p[1] for ri, p in zip(r, points)) / nk
        sxx = sum(ri * (p[0] - mx) ** 2 for ri, p in zip(r, points)) / nk + reg_covar
        syy = sum(ri * (p[1] - my) ** 2 for ri, p in zip(r, points)) / nk + reg_covar
        sxy = sum(ri * (p[0] - mx) * (p[1] - my) for ri, p in zip(r, points)) / nk
        weights.append(nk / n)
        means.append((mx, my))
        covs.append(((sxx, sxy), (sxy, syy)))
    return weights, means, covs


def gmm_fit(points, labels, iterations, reg_covar=1e-6):
    k = max(labels) + 1
    resp = [[1.0 if l == c else 0.0 for c in range(k)] for l in labels]
    weights, means, covs = gmm_m_step(points, resp, reg_covar)
    log_likelihoods = []
    for _ in range(iterations):
        resp, ll = gmm_e_step(points, weights, means, covs)
        log_likelihoods.append(ll)
        weights, means, covs = gmm_m_step(points, resp, reg_covar)
    resp, ll = gmm_e_step(points, weights, means, covs)
    return {"weights": weights, "means": means, "covs": covs, "resp": resp,
            "log_likelihoods": log_likelihoods, "log_likelihood": ll}


def gmm_predict_proba(model, point):
    logs = [math.log(w) + _gauss2_logpdf(point, m, c) for w, m, c in zip(model["weights"], model["means"], model["covs"])]
    norm = _log_sum_exp(logs)
    return [math.exp(l - norm) for l in logs]


def gmm_n_parameters(k, d=2):
    return int(k * d * (d + 1) / 2 + k * d + k - 1)


def gmm_bic(mean_log_likelihood, n, k, d=2):
    return -2 * mean_log_likelihood * n + gmm_n_parameters(k, d) * math.log(n)


def adjusted_rand_index(a, b):
    def comb2(x):
        return x * (x - 1) / 2
    n = len(a)
    pairs = {}
    for x, y in zip(a, b):
        pairs[(x, y)] = pairs.get((x, y), 0) + 1
    rows, cols = {}, {}
    for (x, y), v in pairs.items():
        rows[x] = rows.get(x, 0) + v
        cols[y] = cols.get(y, 0) + v
    index = sum(comb2(v) for v in pairs.values())
    sum_rows = sum(comb2(v) for v in rows.values())
    sum_cols = sum(comb2(v) for v in cols.values())
    expected = sum_rows * sum_cols / comb2(n)
    best = (sum_rows + sum_cols) / 2
    if best == expected:
        return 1.0
    return (index - expected) / (best - expected)


def cluster_example():
    e = CLUSTER_EXAMPLE
    pts = blob_points(e["centers"], e["spread"], e["per_blob"], e["seed"])
    truth = [i // e["per_blob"] for i in range(len(pts))]
    bad = lloyd(pts, [pts[i] for i in e["bad_init"]])
    chosen, pp_steps = kmeans_plusplus(pts, 3, e["plusplus_first"], e["plusplus_draws"])
    good = lloyd(pts, [pts[i] for i in chosen])
    final = good[-1]
    sweep = []
    for k in e["k_range"]:
        run = best_of_kmeans(pts, k, e["seeds"])
        fit = gmm_fit(pts, run["labels"], e["gmm_iterations"], e["reg_covar"])
        sweep.append({
            "k": k,
            "inertia": run["inertia"],
            "silhouette": silhouette_score(pts, run["labels"]) if k > 1 else None,
            "params": gmm_n_parameters(k),
            "log_likelihood": fit["log_likelihood"],
            "bic": gmm_bic(fit["log_likelihood"], len(pts), k),
        })
    with_outliers = pts + list(e["outliers"])
    db = dbscan(with_outliers, e["eps"], e["min_samples"])
    em = gmm_fit(pts, bad[-1]["labels"], e["em_iterations"], e["reg_covar"])
    gmm = gmm_fit(pts, final["labels"], e["gmm_iterations"], e["reg_covar"])
    moons = moon_points(e["moon_points"])
    moons_truth = [0] * e["moon_points"] + [1] * e["moon_points"]
    moons_km = best_of_kmeans(moons, 2, e["seeds"])
    moons_db = dbscan(moons, e["moons_eps"], e["moons_min_samples"])
    sil = silhouette_samples(pts, final["labels"])
    return {
        "points": pts,
        "ln_n": math.log(len(pts)),
        "truth": truth,
        "with_outliers": with_outliers,
        "bad": bad,
        "plusplus": {"chosen": chosen, "steps": pp_steps},
        "good": good,
        "final": final,
        "sweep": sweep,
        "best_k_silhouette": max((s for s in sweep if s["silhouette"] is not None), key=lambda s: s["silhouette"])["k"],
        "best_k_bic": min(sweep, key=lambda s: s["bic"])["k"],
        "dbscan": db,
        "ari_kmeans": adjusted_rand_index(truth, final["labels"]),
        "ari_bad": adjusted_rand_index(truth, bad[-1]["labels"]),
        "ari_dbscan": adjusted_rand_index(truth, db["labels"][: len(pts)]),
        "silhouette_samples": sil,
        "silhouette_by_cluster": [sum(v for v, l in zip(sil, final["labels"]) if l == c) / final["labels"].count(c) for c in range(3)],
        "em": em,
        "gmm": gmm,
        "queries": [{"point": q, "kmeans": assign_labels([q], final["centers"])[0], "proba": gmm_predict_proba(gmm, q)} for q in e["queries"]],
        "moons": moons,
        "moons_kmeans": {"labels": moons_km["labels"], "ari": adjusted_rand_index(moons_truth, moons_km["labels"])},
        "moons_dbscan": {"labels": moons_db["labels"], "kinds": moons_db["kinds"], "ari": adjusted_rand_index(moons_truth, moons_db["labels"])},
    }


VECTOR_INDEX_EXAMPLE = {
    "n": 800,
    "dim": 16,
    "groups": 16,
    "spread": 0.6,
    "seed": 7,
    "queries": 40,
    "k": 10,
    "nlist": 28,
    "nprobes": [1, 2, 4, 8, 28],
    "pq_m": [2, 4, 8],
    "pq_ks": 16,
    "rerank": [30, 100],
    "hnsw_m": 8,
    "ef_construction": 40,
    "efs": [10, 20, 40, 80],
    "kmeans_iterations": 15,
    "plane_points": 45,
    "plane_seed": 3,
    "plane_nlist": 5,
    "plane_hnsw_m": 3,
    "scale": {"n": 100_000_000, "dim": 768, "hnsw_m": 32, "pq_m": 96, "pq_bits": 8},
}


def _dist2(a, b):
    return math.dist(a, b) ** 2


def vector_dataset(n, dim, groups, spread, seed, queries):
    rng = random.Random(seed)
    centers = [[rng.uniform(-1, 1) for _ in range(dim)] for _ in range(groups)]

    def draw():
        c = centers[rng.randrange(groups)]
        return tuple(round(rng.gauss(x, spread), 3) for x in c)

    return [draw() for _ in range(n)], [draw() for _ in range(queries)]


def exact_knn(data, q, k):
    return sorted(range(len(data)), key=lambda i: (_dist2(q, data[i]), i))[:k]


def recall_at_k(found, truth):
    return len(set(found) & set(truth)) / len(truth)


def _nearest_center(p, centers):
    best, best_d = 0, None
    for c, center in enumerate(centers):
        d = _dist2(p, center)
        if best_d is None or d < best_d:
            best, best_d = c, d
    return best


def train_kmeans(points, k, seed, iterations):
    rng = random.Random(seed)
    centers = [points[rng.randrange(len(points))]]
    d2 = [_dist2(p, centers[0]) for p in points]
    while len(centers) < k:
        target, running, pick = rng.random() * sum(d2), 0.0, len(points) - 1
        for i, d in enumerate(d2):
            running += d
            if running > target:
                pick = i
                break
        centers.append(points[pick])
        d2 = [min(d, _dist2(p, points[pick])) for d, p in zip(d2, points)]
    labels = None
    for _ in range(iterations):
        new_labels = [_nearest_center(p, centers) for p in points]
        if new_labels == labels:
            break
        labels = new_labels
        for c in range(k):
            members = [p for p, l in zip(points, labels) if l == c]
            if members:
                centers[c] = tuple(sum(v) / len(members) for v in zip(*members))
    return centers


def ivf_build(data, nlist, seed, iterations):
    centroids = train_kmeans(data, nlist, seed, iterations)
    lists = [[] for _ in centroids]
    for i, v in enumerate(data):
        lists[_nearest_center(v, centroids)].append(i)
    return {"centroids": centroids, "lists": lists}


def ivf_search(index, data, q, k, nprobe):
    centroids = index["centroids"]
    probed = sorted(range(len(centroids)), key=lambda c: (_dist2(q, centroids[c]), c))[:nprobe]
    candidates = [i for c in probed for i in index["lists"][c]]
    ids = sorted(candidates, key=lambda i: (_dist2(q, data[i]), i))[:k]
    return {"ids": ids, "probed": probed, "distances": len(centroids) + len(candidates)}


def pq_train(data, m, ks, seed, iterations):
    sub = len(data[0]) // m
    books = [train_kmeans([v[j * sub:(j + 1) * sub] for v in data], ks, seed + j, iterations) for j in range(m)]
    return {"m": m, "sub": sub, "ks": ks, "codebooks": books}


def pq_encode(pq, v):
    s = pq["sub"]
    return tuple(_nearest_center(v[j * s:(j + 1) * s], pq["codebooks"][j]) for j in range(pq["m"]))


def pq_decode(pq, code):
    return tuple(x for j, c in enumerate(code) for x in pq["codebooks"][j][c])


def pq_tables(pq, q):
    s = pq["sub"]
    return [[_dist2(q[j * s:(j + 1) * s], word) for word in pq["codebooks"][j]] for j in range(pq["m"])]


def pq_search(pq, codes, data, q, k, rerank=0):
    tables = pq_tables(pq, q)
    approx = [sum(tables[j][c] for j, c in enumerate(code)) for code in codes]
    order = sorted(range(len(codes)), key=lambda i: (approx[i], i))
    if rerank:
        return sorted(order[:rerank], key=lambda i: (_dist2(q, data[i]), i))[:k]
    return order[:k]


def _hnsw_select(data, candidates, M):
    chosen = []
    for d, c in sorted(candidates):
        if all(_dist2(data[c], data[s]) > d for s in chosen):
            chosen.append(c)
            if len(chosen) == M:
                break
    return chosen


def _hnsw_layer_search(data, graph, q, entries, ef, counter, trace=None):
    visited = set(entries)
    candidates = [(_dist2(q, data[e]), e) for e in entries]
    counter[0] += len(entries)
    best = [(-d, e) for d, e in candidates]
    heapq.heapify(candidates)
    heapq.heapify(best)
    while candidates:
        d, c = heapq.heappop(candidates)
        if d > -best[0][0]:
            break
        if trace is not None:
            trace.append(c)
        for nb in graph[c]:
            if nb in visited:
                continue
            visited.add(nb)
            dn = _dist2(q, data[nb])
            counter[0] += 1
            if len(best) < ef or dn < -best[0][0]:
                heapq.heappush(candidates, (dn, nb))
                heapq.heappush(best, (-dn, nb))
                if len(best) > ef:
                    heapq.heappop(best)
    return sorted((-d, e) for d, e in best)


def hnsw_build(data, M, ef_construction, seed):
    rng = random.Random(seed)
    m_l = 1 / math.log(M)
    layers, levels, entry, counter = [], [], None, [0]
    for i, v in enumerate(data):
        level = int(-math.log(1 - rng.random()) * m_l)
        levels.append(level)
        while len(layers) <= level:
            layers.append({})
        for layer in layers[:level + 1]:
            layer[i] = []
        if entry is None:
            entry = i
            continue
        top = levels[entry]
        entries = [entry]
        for l in range(top, level, -1):
            entries = [_hnsw_layer_search(data, layers[l], v, entries, 1, counter)[0][1]]
        for l in range(min(level, top), -1, -1):
            found = _hnsw_layer_search(data, layers[l], v, entries, ef_construction, counter)
            cap = 2 * M if l == 0 else M
            layers[l][i] = _hnsw_select(data, found, M)
            for nb in layers[l][i]:
                links = layers[l][nb] + [i]
                if len(links) > cap:
                    links = _hnsw_select(data, [(_dist2(data[nb], data[x]), x) for x in links], cap)
                layers[l][nb] = links
            entries = [e for _, e in found]
        if level > top:
            entry = i
    return {"layers": layers, "levels": levels, "entry": entry, "M": M, "build_distances": counter[0]}


def hnsw_search(index, data, q, k, ef, trace=False):
    counter, entries, path = [0], [index["entry"]], []
    for layer in reversed(index["layers"][1:]):
        hops = [] if trace else None
        entries = [_hnsw_layer_search(data, layer, q, entries, 1, counter, hops)[0][1]]
        path.append(hops)
    hops = [] if trace else None
    found = _hnsw_layer_search(data, index["layers"][0], q, entries, max(ef, k), counter, hops)
    path.append(hops)
    return {"ids": [e for _, e in found[:k]], "distances": counter[0], "path": path}


def vector_index_memory(n, dim, hnsw_m, pq_m, pq_bits, id_bytes=8, float_bytes=4, link_bytes=4):
    vectors = n * dim * float_bytes
    code = n * pq_m * pq_bits // 8
    links = n * (2 * hnsw_m + hnsw_m / (hnsw_m - 1)) * link_bytes
    return {
        "flat": vectors,
        "ivf_flat": vectors + n * id_bytes,
        "ivf_pq": code + n * id_bytes,
        "hnsw_flat": vectors + links,
    }


def _mean(values):
    return sum(values) / len(values)


@functools.lru_cache(maxsize=1)
def vector_index_example():
    e = VECTOR_INDEX_EXAMPLE
    k, it = e["k"], e["kmeans_iterations"]
    data, queries = vector_dataset(e["n"], e["dim"], e["groups"], e["spread"], e["seed"], e["queries"])
    truth = [exact_knn(data, q, k) for q in queries]

    ivf = ivf_build(data, e["nlist"], e["seed"], it)
    ivf_rows = []
    for nprobe in e["nprobes"]:
        runs = [ivf_search(ivf, data, q, k, nprobe) for q in queries]
        ivf_rows.append({
            "nprobe": nprobe,
            "recall": _mean([recall_at_k(r["ids"], t) for r, t in zip(runs, truth)]),
            "distances": _mean([r["distances"] for r in runs]),
        })

    pq_rows, pq4 = [], None
    for m in e["pq_m"]:
        pq = pq_train(data, m, e["pq_ks"], e["seed"], it)
        codes = [pq_encode(pq, v) for v in data]
        if m == 4:
            pq4 = (pq, codes)
        error = _mean([_dist2(v, pq_decode(pq, c)) for v, c in zip(data, codes)])
        row = {"m": m, "sub": pq["sub"], "bytes": m * math.log2(e["pq_ks"]) / 8, "error": error, "recall": {}}
        for rerank in [0] + e["rerank"]:
            row["recall"][rerank] = _mean([recall_at_k(pq_search(pq, codes, data, q, k, rerank), t)
                                           for q, t in zip(queries, truth)])
        pq_rows.append(row)

    pq, codes = pq4
    q0, v0 = queries[0], data[truth[0][0]]
    tables = pq_tables(pq, q0)
    code0 = codes[truth[0][0]]
    pq_demo = {
        "vector": v0,
        "query": q0,
        "code": code0,
        "decoded": pq_decode(pq, code0),
        "terms": [tables[j][c] for j, c in enumerate(code0)],
        "approx": sum(tables[j][c] for j, c in enumerate(code0)),
        "exact": _dist2(q0, v0),
        "sub": pq["sub"],
        "ks": pq["ks"],
    }

    hnsw = hnsw_build(data, e["hnsw_m"], e["ef_construction"], e["seed"])
    hnsw_rows = []
    for ef in e["efs"]:
        runs = [hnsw_search(hnsw, data, q, k, ef) for q in queries]
        hnsw_rows.append({
            "ef": ef,
            "recall": _mean([recall_at_k(r["ids"], t) for r, t in zip(runs, truth)]),
            "distances": _mean([r["distances"] for r in runs]),
        })
    layer_sizes = [len(layer) for layer in hnsw["layers"]]
    links0 = _mean([len(v) for v in hnsw["layers"][0].values()])

    rng = random.Random(e["plane_seed"])
    plane = [(round(rng.uniform(0.5, 9.5), 1), round(rng.uniform(0.5, 9.5), 1)) for _ in range(e["plane_points"])]
    plane_ivf = ivf_build(plane, e["plane_nlist"], e["plane_seed"], it)
    plane_labels = [next(c for c, l in enumerate(plane_ivf["lists"]) if i in l) for i in range(len(plane))]
    plane_query = None
    for gx in range(4, 37):
        for gy in range(4, 37):
            q = (gx / 4, gy / 4)
            nn = exact_knn(plane, q, 1)
            if ivf_search(plane_ivf, plane, q, 1, 1)["ids"] != nn and ivf_search(plane_ivf, plane, q, 1, 2)["ids"] == nn:
                plane_query = q
                break
        if plane_query:
            break
    plane_hnsw = hnsw_build(plane, e["plane_hnsw_m"], 10, e["plane_seed"])
    plane_route = hnsw_search(plane_hnsw, plane, plane_query, 1, 1, trace=True)

    return {
        "n": len(data),
        "truth_distances": len(data),
        "ivf": {"rows": ivf_rows, "sizes": sorted(len(l) for l in ivf["lists"])},
        "pq": {"rows": pq_rows, "demo": pq_demo},
        "hnsw": {"rows": hnsw_rows, "layer_sizes": layer_sizes, "links0": links0,
                 "build_distances": hnsw["build_distances"]},
        "plane": {
            "points": plane,
            "labels": plane_labels,
            "centroids": plane_ivf["centroids"],
            "query": plane_query,
            "nearest": exact_knn(plane, plane_query, 1)[0],
            "probe1": ivf_search(plane_ivf, plane, plane_query, 1, 1),
            "probe2": ivf_search(plane_ivf, plane, plane_query, 1, 2),
            "levels": plane_hnsw["levels"],
            "layers": plane_hnsw["layers"],
            "entry": plane_hnsw["entry"],
            "route": plane_route,
        },
        "scale": vector_index_memory(**{
            "n": e["scale"]["n"], "dim": e["scale"]["dim"], "hnsw_m": e["scale"]["hnsw_m"],
            "pq_m": e["scale"]["pq_m"], "pq_bits": e["scale"]["pq_bits"],
        }),
    }


DISTILLATION_EXAMPLE = {
    "classes": ["cat", "dog", "fox", "car"],
    "teacher": [6.0, 3.5, 2.5, -2.0],
    "student": [2.0, 1.5, 0.0, 0.5],
    "label": 0,
    "temperatures": [1, 2, 4, 8],
    "alpha": 0.5,
    "kd_temperature": 4,
    "scaling_temperatures": [1, 2, 4, 8, 16, 32],
    "means": [(0.0, 1.2), (-1.0, -0.7), (1.0, -0.7)],
    "spreads": [0.6, 1.4, 1.0],
    "train": 15,
    "test": 3000,
    "seeds": [1, 2, 3, 4, 5],
    "lr": 0.5,
    "steps": 400,
    "students": [(1.0, 1), (0.0, 1), (0.5, 2), (0.0, 4)],
}


def temperature_softmax(logits, temperature):
    return softmax_probs([z / temperature for z in logits])


def kd_loss(student, teacher, label, temperature, alpha):
    q = softmax_probs(student)
    q_t = temperature_softmax(student, temperature)
    p_t = temperature_softmax(teacher, temperature)
    hard = -math.log(q[label])
    soft = sum(p * math.log(p / s) for p, s in zip(p_t, q_t))
    gradient = [alpha * (q[i] - (i == label)) + (1 - alpha) * temperature * (q_t[i] - p_t[i])
                for i in range(len(student))]
    return {
        "q": q, "q_t": q_t, "p_t": p_t, "hard": hard, "soft": soft,
        "loss": alpha * hard + (1 - alpha) * temperature ** 2 * soft,
        "hard_gradient": [q[i] - (i == label) for i in range(len(student))],
        "soft_gradient": [(q_t[i] - p_t[i]) / temperature for i in range(len(student))],
        "gradient": gradient,
    }


def _centred(values):
    mean = _mean(values)
    return [v - mean for v in values]


def kd_gradient_scaling(student, teacher, temperatures):
    student, teacher = _centred(student), _centred(teacher)
    n = len(student)
    rows = []
    for t in temperatures:
        raw = kd_loss(student, teacher, 0, t, 0.0)["soft_gradient"]
        rows.append({
            "temperature": t,
            "raw": raw,
            "raw_norm": math.sqrt(sum(g * g for g in raw)),
            "scaled": [g * t * t for g in raw],
        })
    return {"rows": rows, "limit": [(v - z) / n for v, z in zip(student, teacher)]}


def gaussian_teacher_logits(x, means, spreads):
    return [-((x[0] - m[0]) ** 2 + (x[1] - m[1]) ** 2) / (2 * s * s) - 2 * math.log(s)
            for m, s in zip(means, spreads)]


def draw_gaussian_classes(rng, n, means, spreads):
    points = []
    for _ in range(n):
        k = rng.randrange(len(means))
        points.append(((rng.gauss(means[k][0], spreads[k]), rng.gauss(means[k][1], spreads[k])), k))
    return points


def _linear_logits(weights, bias, x):
    return [w[0] * x[0] + w[1] * x[1] + b for w, b in zip(weights, bias)]


def train_kd_student(data, targets, alpha, temperature, lr, steps):
    k = len(targets[0])
    weights, bias = [[0.0, 0.0] for _ in range(k)], [0.0] * k
    for _ in range(steps):
        grad_w, grad_b = [[0.0, 0.0] for _ in range(k)], [0.0] * k
        for (x, y), teacher in zip(data, targets):
            g = kd_loss(_linear_logits(weights, bias, x), teacher, y, temperature, alpha)["gradient"]
            for i in range(k):
                grad_w[i][0] += g[i] * x[0]
                grad_w[i][1] += g[i] * x[1]
                grad_b[i] += g[i]
        for i in range(k):
            weights[i][0] -= lr * grad_w[i][0] / len(data)
            weights[i][1] -= lr * grad_w[i][1] / len(data)
            bias[i] -= lr * grad_b[i] / len(data)
    return weights, bias


def _argmax(values):
    return max(range(len(values)), key=values.__getitem__)


def evaluate_kd(logits_fn, test, teacher_fn):
    nll = correct = agree = kl = 0.0
    for x, y in test:
        q, p = softmax_probs(logits_fn(x)), softmax_probs(teacher_fn(x))
        nll -= math.log(q[y])
        correct += _argmax(q) == y
        agree += _argmax(q) == _argmax(p)
        kl += sum(a * math.log(a / b) for a, b in zip(p, q))
    n = len(test)
    return {"nll": nll / n, "accuracy": correct / n, "agreement": agree / n, "kl": kl / n}


@functools.lru_cache(maxsize=1)
def distillation_example():
    e = DISTILLATION_EXAMPLE
    teacher, student, label = e["teacher"], e["student"], e["label"]
    softened = [{"temperature": t, "probs": temperature_softmax(teacher, t),
                 "entropy": entropy(temperature_softmax(teacher, t))} for t in e["temperatures"]]
    loss = kd_loss(student, teacher, label, e["kd_temperature"], e["alpha"])

    def teacher_fn(x):
        return gaussian_teacher_logits(x, e["means"], e["spreads"])

    runs = []
    for seed in e["seeds"]:
        rng = random.Random(seed)
        train = draw_gaussian_classes(rng, e["train"], e["means"], e["spreads"])
        test = draw_gaussian_classes(rng, e["test"], e["means"], e["spreads"])
        targets = [teacher_fn(x) for x, _ in train]
        row = {"seed": seed, "counts": [sum(y == k for _, y in train) for k in range(len(e["means"]))],
               "teacher": evaluate_kd(teacher_fn, test, teacher_fn), "students": []}
        for alpha, t in e["students"]:
            w, b = train_kd_student(train, targets, alpha, t, e["lr"], e["steps"])
            scores = evaluate_kd(lambda x, w=w, b=b: _linear_logits(w, b, x), test, teacher_fn)
            scores["train_nll"] = evaluate_kd(lambda x, w=w, b=b: _linear_logits(w, b, x), train, teacher_fn)["nll"]
            row["students"].append(scores)
        runs.append(row)

    metrics = ["nll", "accuracy", "agreement", "kl", "train_nll"]
    summary = {
        "teacher": {m: _mean([r["teacher"][m] for r in runs]) for m in metrics[:-1]},
        "students": [{"alpha": a, "temperature": t,
                      **{m: _mean([r["students"][i][m] for r in runs]) for m in metrics}}
                     for i, (a, t) in enumerate(e["students"])],
    }
    return {
        "softened": softened,
        "loss": loss,
        "scaling": kd_gradient_scaling(student, teacher, e["scaling_temperatures"]),
        "runs": runs,
        "summary": summary,
    }


TIME_SERIES_EXAMPLE = {
    "n": 96,
    "period": 12,
    "level": 100.0,
    "slope": 0.5,
    "amplitude": 10.0,
    "phi": 0.6,
    "noise": 2.0,
    "seed": 7,
    "n_splits": 4,
    "test_size": 12,
    "harmonics": 2,
    "acf_lags": 24,
    "kfold": 5,
    "shuffle_seed": 3,
}


def seasonal_series(n, level, slope, amplitude, period, phi, noise, seed):
    rng = random.Random(seed)
    values = []
    ar = 0.0
    for t in range(n):
        ar = phi * ar + rng.gauss(0, noise)
        values.append(level + slope * t + amplitude * math.sin(2 * math.pi * t / period) + ar)
    return values


def centred_moving_average(values, period):
    half = period // 2
    out = [None] * len(values)
    for t in range(half, len(values) - half):
        if period % 2:
            window = values[t - half:t + half + 1]
        else:
            window = [0.5 * values[t - half]] + values[t - half + 1:t + half] + [0.5 * values[t + half]]
        out[t] = sum(window) / period
    return out


def classical_decomposition(values, period):
    trend = centred_moving_average(values, period)
    buckets = [[] for _ in range(period)]
    for t, (y, level) in enumerate(zip(values, trend)):
        if level is not None:
            buckets[t % period].append(y - level)
    raw = [sum(b) / len(b) for b in buckets]
    shift = sum(raw) / period
    indices = [r - shift for r in raw]
    residual = [None if level is None else y - level - indices[t % period]
                for t, (y, level) in enumerate(zip(values, trend))]
    return {"trend": trend, "indices": indices, "residual": residual}


def autocorrelation(values, lags):
    n = len(values)
    mean = sum(values) / n
    centred = [v - mean for v in values]
    denominator = sum(c * c for c in centred)
    return [sum(centred[t] * centred[t + k] for t in range(n - k)) / denominator for k in range(1, lags + 1)]


def time_series_split(n, n_splits, test_size=None, gap=0, max_train_size=None):
    if n_splits + 1 > n:
        raise ValueError("more folds than samples")
    test_size = test_size if test_size is not None else n // (n_splits + 1)
    if n - gap - test_size * n_splits <= 0:
        raise ValueError("too many splits for the number of samples")
    splits = []
    for start in range(n - n_splits * test_size, n, test_size):
        end = start - gap
        first = end - max_train_size if max_train_size and max_train_size < end else 0
        splits.append((list(range(first, end)), list(range(start, start + test_size))))
    return splits


def _least_squares(rows, targets):
    width = len(rows[0])
    gram = [[sum(r[i] * r[j] for r in rows) for j in range(width)] for i in range(width)]
    moments = [sum(r[i] * y for r, y in zip(rows, targets)) for i in range(width)]
    return _solve_linear(gram, moments)


def fourier_features(t, n, period, harmonics):
    row = [1.0, t / n]
    for k in range(1, harmonics + 1):
        angle = 2 * math.pi * k * t / period
        row += [math.sin(angle), math.cos(angle)]
    return row


def forecast_models(values, train, test, period, harmonics):
    n = len(values)
    last = train[-1]
    naive = [values[last]] * len(test)
    seasonal = [values[t - period * ((t - last - 1) // period + 1)] for t in test]
    weights = _least_squares([fourier_features(t, n, period, harmonics) for t in train], [values[t] for t in train])
    fourier = [sum(w * x for w, x in zip(weights, fourier_features(t, n, period, harmonics))) for t in test]
    lagged = [t for t in train if t >= period]
    lag_weights = _least_squares([[1.0, t / n, values[t - period]] for t in lagged], [values[t] for t in lagged])
    lag = [lag_weights[0] + lag_weights[1] * t / n + lag_weights[2] * values[t - period] for t in test]
    return [
        ("naive", naive),
        ("seasonal naive", seasonal),
        ("trend + Fourier", fourier),
        ("trend + lag 12", lag),
    ]


def forecast_errors(values, train, test, predictions):
    errors = [values[t] - p for t, p in zip(test, predictions)]
    mae = sum(abs(e) for e in errors) / len(errors)
    rmse = math.sqrt(sum(e * e for e in errors) / len(errors))
    scale = sum(abs(values[t] - values[t - 1]) for t in train[1:]) / (len(train) - 1)
    return {"mae": mae, "rmse": rmse, "mase": mae / scale, "scale": scale}


def nearest_time_prediction(values, train, t):
    return values[min(train, key=lambda s: (abs(s - t), s))]


def nearest_time_mae(values, splits):
    errors = [abs(values[t] - nearest_time_prediction(values, train, t)) for train, test in splits for t in test]
    return sum(errors) / len(errors)


@functools.lru_cache(maxsize=1)
def time_series_example():
    e = TIME_SERIES_EXAMPLE
    values = seasonal_series(e["n"], e["level"], e["slope"], e["amplitude"], e["period"],
                             e["phi"], e["noise"], e["seed"])
    parts = classical_decomposition(values, e["period"])
    residual = [r for r in parts["residual"] if r is not None]
    splits = time_series_split(e["n"], e["n_splits"], e["test_size"])
    folds = []
    for train, test in splits:
        models = forecast_models(values, train, test, e["period"], e["harmonics"])
        folds.append({
            "train": train,
            "test": test,
            "models": [{"name": name, "predictions": p, **forecast_errors(values, train, test, p)}
                       for name, p in models],
        })
    names = [m["name"] for m in folds[0]["models"]]
    summary = [{"name": name, **{key: sum(f["models"][i][key] for f in folds) / len(folds)
                                 for key in ("mae", "rmse", "mase")}}
               for i, name in enumerate(names)]
    order = list(range(e["n"]))
    random.Random(e["shuffle_seed"]).shuffle(order)
    shuffled = [([order[i] for i in train], [order[i] for i in test]) for train, test in kfold_splits(e["n"], e["kfold"])]
    return {
        "series": values,
        "trend": parts["trend"],
        "indices": parts["indices"],
        "residual": parts["residual"],
        "acf": autocorrelation(values, e["acf_lags"]),
        "residual_acf": autocorrelation(residual, e["acf_lags"]),
        "band": 1.96 / math.sqrt(e["n"]),
        "residual_band": 1.96 / math.sqrt(len(residual)),
        "folds": folds,
        "summary": summary,
        "true_indices": [e["amplitude"] * math.sin(2 * math.pi * k / e["period"]) for k in range(e["period"])],
        "shuffled_test": sorted(shuffled[0][1]),
        "leakage": {
            "shuffled": nearest_time_mae(values, shuffled),
            "ordered": nearest_time_mae(values, splits),
        },
    }


REGRESSION_METRICS_EXAMPLE = {
    "targets": [12, 14, 15, 15, 17, 18, 20, 22, 25, 31, 38, 55],
    "steady_errors": [3, -2, 4, -3, 2, -4, 3, -2, 4, -3, 2, -3],
    "spiky_errors": [0.5, -0.5, 0, 0.5, -0.5, 0, 0.5, -0.5, 0, 0.5, -0.5, -20],
    "bias": 5,
    "shrink": 0.5,
    "quantile": 0.9,
    "grid_step": 0.01,
}


def pinball_loss(targets, predictions, alpha):
    total = 0.0
    for y, p in zip(targets, predictions):
        diff = y - p
        total += alpha * diff if diff >= 0 else (alpha - 1) * diff
    return total / len(targets)


def regression_scores(targets, predictions):
    n = len(targets)
    errors = [y - p for y, p in zip(targets, predictions)]
    mean_y = sum(targets) / n
    mean_error = sum(errors) / n
    total = sum((y - mean_y) ** 2 for y in targets)
    sse = sum(e * e for e in errors)
    eps = 2.0 ** -52

    def fraction_explained(residual):
        if residual == 0:
            return 1.0
        return 0.0 if total == 0 else 1 - residual / total

    return {
        "mae": sum(abs(e) for e in errors) / n,
        "mse": sse / n,
        "rmse": math.sqrt(sse / n),
        "medae": median([abs(e) for e in errors]),
        "max_error": max(abs(e) for e in errors),
        "mape": sum(abs(e) / max(abs(y), eps) for e, y in zip(errors, targets)) / n,
        "r2": fraction_explained(sse),
        "explained_variance": fraction_explained(sum((e - mean_error) ** 2 for e in errors)),
        "mean_error": mean_error,
    }


def best_constant(targets, loss, step):
    lo, hi = min(targets), max(targets)
    count = int(round((hi - lo) / step))
    grid = [lo + i * step for i in range(count + 1)]
    values = [loss([c] * len(targets)) for c in grid]
    best = min(values)
    winners = [c for c, value in zip(grid, values) if value <= best + 1e-9]
    return {"low": winners[0], "high": winners[-1], "loss": best}


@functools.lru_cache(maxsize=1)
def regression_metrics_example():
    e = REGRESSION_METRICS_EXAMPLE
    y = e["targets"]
    n = len(y)
    mean_y = sum(y) / n
    steady = [t + err for t, err in zip(y, e["steady_errors"])]
    spiky = [t + err for t, err in zip(y, e["spiky_errors"])]
    biased = [t + e["bias"] for t in y]
    models = [
        ("steady", steady),
        ("spiky", spiky),
        ("biased +" + str(e["bias"]), biased),
        ("constant mean", [mean_y] * n),
        ("constant median", [median(y)] * n),
    ]
    rows = [{"name": name, "predictions": p, **regression_scores(y, p),
             "pinball": pinball_loss(y, p, e["quantile"])} for name, p in models]
    narrow = [mean_y + e["shrink"] * (t - mean_y) for t in y]
    narrow_steady = [t + err for t, err in zip(narrow, e["steady_errors"])]

    def squared(p):
        return sum((t - c) ** 2 for t, c in zip(y, p)) / n

    def absolute(p):
        return sum(abs(t - c) for t, c in zip(y, p)) / n

    def percentage(p):
        return sum(abs(t - c) / t for t, c in zip(y, p)) / n

    constants = [
        ("squared error (MSE)", best_constant(y, squared, e["grid_step"])),
        ("absolute error (MAE)", best_constant(y, absolute, e["grid_step"])),
        ("pinball, \u03b1 = " + str(e["quantile"]), best_constant(y, lambda p: pinball_loss(y, p, e["quantile"]), e["grid_step"])),
        ("percentage error (MAPE)", best_constant(y, percentage, e["grid_step"])),
    ]
    return {
        "mean": mean_y,
        "median": median(y),
        "models": rows,
        "narrow": narrow,
        "narrow_scores": regression_scores(narrow, narrow_steady),
        "constants": constants,
        "over_under": {
            "over": regression_scores([100], [150])["mape"],
            "under": regression_scores([150], [100])["mape"],
        },
    }


SVM_EXAMPLE = {
    "points": [(1.0, 1.0), (2.0, 1.0), (1.0, 2.5), (2.5, 2.0), (3.5, 3.0), (4.5, 3.0), (3.0, 4.5), (4.0, 4.5)],
    "labels": [-1, -1, -1, -1, 1, 1, 1, 1],
    "outlier": (2.0, 2.0),
    "c_values": [100.0, 0.5, 0.1],
    "ring": [-3.0, -2.5, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 2.5, 3.0],
    "ring_radius": 1.5,
    "gammas": [0.1, 1.0, 10.0],
    "far": 6.0,
    "ring_c": 10.0,
    "scaling_points": [(0.2, 1000.0), (0.8, 1000.0), (0.2, 3000.0)],
    "tol": 1e-9,
}


def linear_kernel(a, b):
    return sum(x * y for x, y in zip(a, b))


def rbf_kernel(a, b, gamma):
    return math.exp(-gamma * sum((x - y) ** 2 for x, y in zip(a, b)))


def poly_kernel(a, b, gamma=1.0, coef0=1.0, degree=2):
    return (gamma * linear_kernel(a, b) + coef0) ** degree


def svm_smo(points, labels, C, kernel, tol=1e-9, max_iter=100000):
    n = len(points)
    K = [[kernel(a, b) for b in points] for a in points]
    alpha = [0.0] * n
    grad = [-1.0] * n
    iterations = 0
    while iterations < max_iter:
        up = [t for t in range(n) if (labels[t] == 1 and alpha[t] < C) or (labels[t] == -1 and alpha[t] > 0)]
        low = [t for t in range(n) if (labels[t] == -1 and alpha[t] < C) or (labels[t] == 1 and alpha[t] > 0)]
        i = max(up, key=lambda t: -labels[t] * grad[t])
        j = min(low, key=lambda t: -labels[t] * grad[t])
        gap = -labels[i] * grad[i] + labels[j] * grad[j]
        if gap < tol:
            break
        eta = max(K[i][i] + K[j][j] - 2 * K[i][j], 1e-12)
        step = gap / eta
        for index, sign in ((i, labels[i]), (j, -labels[j])):
            room = C - alpha[index] if sign > 0 else alpha[index]
            step = min(step, room)
        alpha[i] += labels[i] * step
        alpha[j] -= labels[j] * step
        for k in range(n):
            grad[k] += step * labels[k] * (K[k][i] - K[k][j])
        iterations += 1
    free = [k for k in range(n) if 1e-9 < alpha[k] < C - 1e-9]
    if free:
        b = sum(-labels[k] * grad[k] for k in free) / len(free)
    else:
        b = (-labels[i] * grad[i] - labels[j] * grad[j]) / 2
    dual = sum(alpha) - 0.5 * sum(alpha[a] * alpha[c] * labels[a] * labels[c] * K[a][c]
                                  for a in range(n) for c in range(n))
    return {"alpha": alpha, "b": b, "iterations": iterations, "dual": dual, "gap": gap}


def svm_decision(points, labels, model, kernel, x):
    return sum(a * y * kernel(p, x) for a, y, p in zip(model["alpha"], labels, points) if a > 0) + model["b"]


def hinge(margin):
    return max(0.0, 1 - margin)


def svm_linear_fit(points, labels, C, tol=1e-9):
    model = svm_smo(points, labels, C, linear_kernel, tol)
    w = [sum(a * y * p[d] for a, y, p in zip(model["alpha"], labels, points)) for d in range(len(points[0]))]
    norm = math.sqrt(sum(v * v for v in w))
    margins = [y * (linear_kernel(w, p) + model["b"]) for p, y in zip(points, labels)]
    hinge_total = sum(hinge(m) for m in margins)
    return {
        **model,
        "C": C,
        "w": w,
        "width": 2 / norm,
        "margins": margins,
        "support": [k for k, a in enumerate(model["alpha"]) if a > 1e-7],
        "bounded": [k for k, a in enumerate(model["alpha"]) if a > C - 1e-7],
        "hinge_total": hinge_total,
        "primal": 0.5 * norm * norm + C * hinge_total,
    }


def gamma_scale(points):
    values = [v for p in points for v in p]
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return 1.0 / (len(points[0]) * variance) if variance != 0 else 1.0


@functools.lru_cache(maxsize=1)
def svm_example():
    e = SVM_EXAMPLE
    points, labels = e["points"], e["labels"]
    fits = [svm_linear_fit(points, labels, C, e["tol"]) for C in e["c_values"]]
    with_outlier = [svm_linear_fit(points + [e["outlier"]], labels + [1], C, e["tol"]) for C in e["c_values"]]
    ring = [(x,) for x in e["ring"]]
    ring_labels = [1 if abs(x) < e["ring_radius"] else -1 for x in e["ring"]]
    linear_ring = svm_linear_fit(ring, ring_labels, e["ring_c"], e["tol"])
    poly = svm_smo(ring, ring_labels, e["ring_c"], poly_kernel, e["tol"])
    rbf = []
    for gamma in e["gammas"]:
        kernel = functools.partial(rbf_kernel, gamma=gamma)
        model = svm_smo(ring, ring_labels, e["ring_c"], kernel, e["tol"])
        scores = [svm_decision(ring, ring_labels, model, kernel, p) for p in ring]
        rbf.append({
            "gamma": gamma,
            "model": model,
            "scores": scores,
            "accuracy": sum((s > 0) == (y > 0) for s, y in zip(scores, ring_labels)) / len(ring),
            "support": sum(1 for a in model["alpha"] if a > 1e-7),
            "far": svm_decision(ring, ring_labels, model, kernel, (e["far"],)),
            "curve": [(x / 10, svm_decision(ring, ring_labels, model, kernel, (x / 10,))) for x in range(-40, 41)],
        })
    poly_scores = [svm_decision(ring, ring_labels, poly, poly_kernel, p) for p in ring]
    a, b = (1.0,), (2.0,)
    lifted = lambda x: (x[0] ** 2, math.sqrt(2) * x[0], 1.0)
    scaled = e["scaling_points"]
    columns = list(zip(*scaled))
    stds = [statistics.pstdev(c) for c in columns]
    standardized = [tuple((v - statistics.fmean(c)) / s for v, c, s in zip(p, columns, stds)) for p in scaled]

    def distance_share(p, q):
        parts = [(x - y) ** 2 for x, y in zip(p, q)]
        return parts[0] / sum(parts)

    return {
        "fits": fits,
        "with_outlier": with_outlier,
        "ring_labels": ring_labels,
        "linear_ring": {**linear_ring, "accuracy": sum(m > 0 for m in linear_ring["margins"]) / len(ring)},
        "poly": {**poly, "scores": poly_scores,
                 "accuracy": sum((s > 0) == (y > 0) for s, y in zip(poly_scores, ring_labels)) / len(ring)},
        "rbf": rbf,
        "kernel_trick": {"kernel": poly_kernel(a, b), "explicit": linear_kernel(lifted(a), lifted(b)),
                         "lifted_a": lifted(a), "lifted_b": lifted(b)},
        "scaling": {
            "gamma_raw": gamma_scale(scaled),
            "gamma_standardized": gamma_scale(standardized),
            "standardized": standardized,
            "share_raw": distance_share(scaled[0], scaled[1]),
            "kernel_raw_near": rbf_kernel(scaled[0], scaled[1], gamma_scale(scaled)),
            "kernel_raw_far": rbf_kernel(scaled[0], scaled[2], gamma_scale(scaled)),
            "kernel_std_near": rbf_kernel(standardized[0], standardized[1], gamma_scale(standardized)),
            "kernel_std_far": rbf_kernel(standardized[0], standardized[2], gamma_scale(standardized)),
        },
    }


LR_SCHEDULE_EXAMPLE = {
    "base_lr": 0.1,
    "steps": 100,
    "step_size": 30,
    "step_gamma": 0.1,
    "exp_gamma": 0.96,
    "warmup": 10,
    "warmup_start": 0.01,
    "one_cycle": {"max_lr": 0.1, "pct_start": 0.3, "div_factor": 25.0, "final_div_factor": 1e4,
                  "base_momentum": 0.85, "max_momentum": 0.95},
    "curvature": 2.0,
    "noise": 1.0,
    "w0": 3.0,
    "slow_lr": 0.01,
    "gd_lrs": [0.05, 0.5, 0.9, 1.05],
    "gd_steps": 10,
    "range_curvatures": [0.5, 2.0, 8.0],
    "range_start": 1e-4,
    "range_end": 10.0,
    "range_steps": 51,
    "adam_grads": [1e-4, 10.0],
    "adam_lr": 1e-3,
}


def lr_step_decay(base_lr, t, step_size, gamma):
    return base_lr * gamma ** (t // step_size)


def lr_exponential(base_lr, t, gamma):
    return base_lr * gamma**t


def lr_cosine(base_lr, t, t_max, eta_min=0.0):
    return eta_min + (base_lr - eta_min) * (1 + math.cos(math.pi * t / t_max)) / 2


def lr_linear(base_lr, t, start_factor, end_factor, total_iters):
    return base_lr * (start_factor + (end_factor - start_factor) * min(total_iters, t) / total_iters)


def lr_warmup_cosine(base_lr, t, warmup, total, start_factor, eta_min=0.0):
    if t < warmup:
        return lr_linear(base_lr, t, start_factor, 1.0, warmup)
    return lr_cosine(base_lr, t - warmup, total - warmup, eta_min)


def lr_one_cycle(t, total_steps, max_lr, pct_start=0.3, div_factor=25.0, final_div_factor=1e4,
                 base_momentum=0.85, max_momentum=0.95):
    initial = max_lr / div_factor
    phases = [(pct_start * total_steps - 1, initial, max_lr, max_momentum, base_momentum),
              (total_steps - 1, max_lr, initial / final_div_factor, base_momentum, max_momentum)]
    start = 0.0
    for i, (end, lr0, lr1, m0, m1) in enumerate(phases):
        if t <= end or i == len(phases) - 1:
            pct = (t - start) / (end - start)
            anneal = lambda a, b: b + (a - b) / 2 * (math.cos(math.pi * pct) + 1)
            return anneal(lr0, lr1), anneal(m0, m1)
        start = end


def lr_recursive(kind, base_lr, steps, **kw):
    lrs = [base_lr * kw["start_factor"] if kind == "linear" else base_lr]
    for t in range(1, steps):
        lr = lrs[-1]
        if kind == "step":
            lr = lr * kw["gamma"] if t % kw["step_size"] == 0 else lr
        elif kind == "exponential":
            lr = lr * kw["gamma"]
        elif kind == "cosine":
            t_max, eta_min = kw["t_max"], kw.get("eta_min", 0.0)
            if (t - 1 - t_max) % (2 * t_max) == 0:
                lr = lr + (base_lr - eta_min) * (1 - math.cos(math.pi / t_max)) / 2
            else:
                lr = ((1 + math.cos(math.pi * t / t_max)) / (1 + math.cos(math.pi * (t - 1) / t_max))
                      * (lr - eta_min) + eta_min)
        elif kind == "linear":
            sf, ef, n = kw["start_factor"], kw["end_factor"], kw["total_iters"]
            if t <= n:
                lr = lr * (1.0 + (ef - sf) / (n * sf + (t - 1) * (ef - sf)))
        lrs.append(lr)
    return lrs


def noisy_quadratic_loss(lrs, curvature, noise, w0):
    second_moment = w0 * w0
    losses = [curvature * second_moment / 2]
    for lr in lrs:
        second_moment = (1 - lr * curvature) ** 2 * second_moment + (lr * noise) ** 2
        losses.append(curvature * second_moment / 2)
    return losses


def noise_floor(lr, curvature, noise):
    return lr * noise**2 / (2 * (2 - lr * curvature))


def gd_quadratic(lr, curvature, w0, steps):
    w = [w0]
    for _ in range(steps):
        w.append(w[-1] * (1 - lr * curvature))
    return w


def lr_range_test(curvatures, start, end, steps, w0=1.0):
    ratio = (end / start) ** (1 / (steps - 1))
    w = [w0] * len(curvatures)
    rows = []
    for i in range(steps):
        lr = start * ratio**i
        w = [x * (1 - lr * h) for x, h in zip(w, curvatures)]
        rows.append((lr, sum(h * x * x / 2 for h, x in zip(curvatures, w))))
    return rows


@functools.lru_cache(maxsize=None)
def lr_schedule_example():
    e = LR_SCHEDULE_EXAMPLE
    base, n = e["base_lr"], e["steps"]
    oc = e["one_cycle"]
    schedules = {
        "constant": [base] * n,
        "step": [lr_step_decay(base, t, e["step_size"], e["step_gamma"]) for t in range(n)],
        "exponential": [lr_exponential(base, t, e["exp_gamma"]) for t in range(n)],
        "cosine": [lr_cosine(base, t, n) for t in range(n)],
        "warmup_cosine": [lr_warmup_cosine(base, t, e["warmup"], n, e["warmup_start"]) for t in range(n)],
        "one_cycle": [lr_one_cycle(t, n, **oc)[0] for t in range(n)],
    }
    momentum = [lr_one_cycle(t, n, **oc)[1] for t in range(n)]
    recursion = {
        "step": lr_recursive("step", base, n, step_size=e["step_size"], gamma=e["step_gamma"]),
        "exponential": lr_recursive("exponential", base, n, gamma=e["exp_gamma"]),
        "cosine": lr_recursive("cosine", base, n, t_max=n),
        "linear": lr_recursive("linear", base, e["warmup"] + 5, start_factor=e["warmup_start"],
                               end_factor=1.0, total_iters=e["warmup"]),
    }
    closed_linear = [lr_linear(base, t, e["warmup_start"], 1.0, e["warmup"]) for t in range(e["warmup"] + 5)]
    recursion_error = max(
        max(abs(a - b) for a, b in zip(recursion[k], schedules[k])) for k in ("step", "exponential", "cosine"))
    recursion_error = max(recursion_error, max(abs(a - b) for a, b in zip(recursion["linear"], closed_linear)))
    past_end = lr_recursive("cosine", base, 2 * n + 1, t_max=n)
    h, sigma, w0 = e["curvature"], e["noise"], e["w0"]
    runs = {name: noisy_quadratic_loss(schedules[name], h, sigma, w0)
            for name in ("constant", "step", "cosine", "warmup_cosine", "one_cycle")}
    runs["slow"] = noisy_quadratic_loss([e["slow_lr"]] * n, h, sigma, w0)
    gd = [{"lr": lr, "factor": 1 - lr * h, "w": gd_quadratic(lr, h, w0, e["gd_steps"])} for lr in e["gd_lrs"]]
    rows = lr_range_test(e["range_curvatures"], e["range_start"], e["range_end"], e["range_steps"])
    best = min(range(len(rows)), key=lambda i: rows[i][1])
    blowup = next(i for i in range(best, len(rows)) if rows[i][1] > rows[0][1])
    adam = []
    for g in e["adam_grads"]:
        state, p, updates = {}, [0.0], []
        for _ in range(3):
            before = p[0]
            p = optimizer_step("adam", p, [g], state, {"lr": e["adam_lr"]})
            updates.append(before - p[0])
        adam.append({"grad": g, "updates": updates})
    return {
        "schedules": schedules,
        "momentum": momentum,
        "recursion_error": recursion_error,
        "linear": closed_linear,
        "cosine_past_end": {"at_end": past_end[n], "after": past_end[n + n // 2], "back": past_end[2 * n]},
        "runs": runs,
        "floors": {"constant": noise_floor(base, h, sigma), "slow": noise_floor(e["slow_lr"], h, sigma)},
        "gd": gd,
        "range": {"rows": rows, "best": best, "blowup": blowup, "stable_limit": 2 / max(e["range_curvatures"])},
        "adam": adam,
        "one_cycle": {"initial": oc["max_lr"] / oc["div_factor"],
                      "final": oc["max_lr"] / oc["div_factor"] / oc["final_div_factor"],
                      "peak_step": oc["pct_start"] * n - 1},
    }


GAN_EXAMPLE = {
    "data": [0.0, 0.1, 0.3, 0.1, 0.0, 0.1, 0.3, 0.1],
    "generators": [
        ("matched", [0.0, 0.1, 0.3, 0.1, 0.0, 0.1, 0.3, 0.1]),
        ("broad", [0.125] * 8),
        ("one mode", [0.0, 0.2, 0.6, 0.2, 0.0, 0.0, 0.0, 0.0]),
        ("shifted", [0.0, 0.0, 0.1, 0.3, 0.1, 0.0, 0.1, 0.4]),
    ],
    "logits": [-6.0, -3.0, 0.0, 3.0],
    "point_shifts": [0.5, 1.0, 2.0, 4.0],
    "dirac": {"theta": 1.0, "psi": 1.0, "lr": 0.1, "steps": 1000, "r1_gamma": 1.0},
    "dirac_marks": [0, 100, 300, 1000],
    "fid_cases": [
        ("identical", [0.0, 0.0], [[1.0, 0.0], [0.0, 1.0]]),
        ("mean shifted", [0.5, 0.0], [[1.0, 0.0], [0.0, 1.0]]),
        ("collapsed", [0.0, 0.0], [[0.25, 0.0], [0.0, 0.25]]),
        ("correlated", [0.0, 0.0], [[1.0, 0.8], [0.8, 1.0]]),
    ],
    "fid_sample_sizes": [20, 200, 2000],
    "fid_seed": 7,
    "dcgan": {"latent": 100, "layers": [(4, 1, 0), (4, 2, 1), (4, 2, 1), (4, 2, 1), (4, 2, 1)]},
}


def conv_transpose_out(size, kernel, stride=1, padding=0, output_padding=0, dilation=1):
    return (size - 1) * stride - 2 * padding + dilation * (kernel - 1) + output_padding + 1


def gan_optimal_discriminator(p_data, p_gen):
    return [d / (d + g) if d + g > 0 else None for d, g in zip(p_data, p_gen)]


def gan_value(p_data, p_gen, disc):
    total = 0.0
    for d, g, prob in zip(p_data, p_gen, disc):
        if d > 0:
            total += d * math.log(prob)
        if g > 0:
            total += g * math.log(1 - prob)
    return total


def js_divergence(p, q):
    m = [(a + b) / 2 for a, b in zip(p, q)]
    return (kl_divergence(p, m, math.e) + kl_divergence(q, m, math.e)) / 2


def wasserstein_1d(p, q, spacing=1.0):
    total, cdf_p, cdf_q = 0.0, 0.0, 0.0
    for a, b in zip(p[:-1], q[:-1]):
        cdf_p += a
        cdf_q += b
        total += abs(cdf_p - cdf_q) * spacing
    return total


def gan_generator_gradients(logit):
    d = sigmoid(logit)
    return {"logit": logit, "d": d, "minimax": -d, "non_saturating": d - 1}


def dirac_gan(theta, psi, lr, steps, generator="minimax", r1_gamma=0.0):
    path = [(theta, psi)]
    for _ in range(steps):
        grad_psi = theta * sigmoid(psi * theta) + r1_gamma * psi
        if generator == "minimax":
            grad_theta = -psi * sigmoid(psi * theta)
        else:
            grad_theta = -psi * sigmoid(-psi * theta)
        theta, psi = theta - lr * grad_theta, psi - lr * grad_psi
        path.append((theta, psi))
    return path


def frechet_distance_2d(mu1, cov1, mu2, cov2):
    product = [[sum(cov1[i][k] * cov2[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    det1 = cov1[0][0] * cov1[1][1] - cov1[0][1] * cov1[1][0]
    det2 = cov2[0][0] * cov2[1][1] - cov2[0][1] * cov2[1][0]
    trace_sqrt = math.sqrt(product[0][0] + product[1][1] + 2 * math.sqrt(det1 * det2))
    mean_term = sum((a - b) ** 2 for a, b in zip(mu1, mu2))
    return mean_term + cov1[0][0] + cov1[1][1] + cov2[0][0] + cov2[1][1] - 2 * trace_sqrt


def gan_mean_and_covariance(points):
    n = len(points)
    mu = [sum(p[i] for p in points) / n for i in range(2)]
    cov = [[sum((p[i] - mu[i]) * (p[j] - mu[j]) for p in points) / (n - 1) for j in range(2)]
           for i in range(2)]
    return mu, cov


@functools.lru_cache(maxsize=None)
def gan_example():
    e = GAN_EXAMPLE
    data = e["data"]
    generators = []
    for name, gen in e["generators"]:
        disc = gan_optimal_discriminator(data, gen)
        generators.append({
            "name": name,
            "p": gen,
            "disc": disc,
            "value": gan_value(data, gen, disc),
            "js": js_divergence(data, gen),
            "kl_forward": kl_divergence(data, gen, math.e),
            "kl_reverse": kl_divergence(gen, data, math.e),
            "w1": wasserstein_1d(data, gen),
        })
    points = [{"shift": s, "js": js_divergence([1.0, 0.0], [0.0, 1.0]), "w1": s} for s in e["point_shifts"]]
    d = e["dirac"]
    dirac = {}
    for kind, generator, gamma in (("minimax", "minimax", 0.0),
                                   ("non_saturating", "non_saturating", 0.0),
                                   ("r1", "minimax", d["r1_gamma"])):
        path = dirac_gan(d["theta"], d["psi"], d["lr"], d["steps"], generator, gamma)
        radius = [math.hypot(t, p) for t, p in path]
        dirac[kind] = {"path": path, "radius": radius, "marks": [radius[i] for i in e["dirac_marks"]]}
    rng = random.Random(e["fid_seed"])
    real_mu, real_cov = e["fid_cases"][0][1], e["fid_cases"][0][2]
    sampled = []
    for n in e["fid_sample_sizes"]:
        a = [(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(n)]
        b = [(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(n)]
        sampled.append({"n": n, "fid": frechet_distance_2d(*gan_mean_and_covariance(a),
                                                           *gan_mean_and_covariance(b))})
    return {
        "generators": generators,
        "points": points,
        "saturation": [gan_generator_gradients(a) for a in e["logits"]],
        "saturation_curve": [gan_generator_gradients(i / 4) for i in range(-24, 17)],
        "dcgan_sizes": list(itertools.accumulate(e["dcgan"]["layers"],
                                                 lambda size, layer: conv_transpose_out(size, *layer), initial=1)),
        "dirac": dirac,
        "fid": [{"name": name, "mu": mu, "cov": cov, "fid": frechet_distance_2d(real_mu, real_cov, mu, cov)}
                for name, mu, cov in e["fid_cases"]],
        "fid_sampled": sampled,
        "log4": math.log(4),
    }


BERT_CONFIGS = [
    {"name": "BERT-base", "vocab": 30000, "positions": 512, "segments": 2, "d_model": 768, "layers": 12, "heads": 12, "reported": "110M"},
    {"name": "BERT-large", "vocab": 30000, "positions": 512, "segments": 2, "d_model": 1024, "layers": 24, "heads": 16, "reported": "340M"},
]

ENCODER_EXAMPLE = {
    "sentence_a": ["the", "cat", "sat", "on", "the", "mat"],
    "sentence_b": ["it", "was", "warm"],
    "mask_rate": 0.15,
    "mask_split": (0.8, 0.1, 0.1),
    "mask_seed": 3,
    "mask_vocab": ["the", "cat", "sat", "on", "mat", "it", "was", "warm", "dog", "ran"],
    "mask_sample_tokens": 100000,
    "fill_corpus": [
        ("a", "p", "x"), ("a", "q", "y"), ("b", "q", "x"),
        ("b", "r", "y"), ("c", "p", "z"), ("c", "r", "z"),
    ],
    "fill_test": [("a", "p", "z"), ("a", "q", "y"), ("b", "q", "x"), ("b", "r", "z"), ("c", "p", "x"), ("c", "r", "y")],
    "fill_alpha": 0.5,
}

IGNORE_INDEX = -100


def encoder_param_count(vocab, positions, segments, d_model, layers, d_ff=None):
    d_ff = 4 * d_model if d_ff is None else d_ff
    block = transformer_param_count(d_model, 1, 0, d_ff)
    attention, feed_forward, layer_norm = block["attention"], block["feed_forward"], block["layer_norm"]
    token_table = vocab * d_model
    position_table = positions * d_model
    segment_table = segments * d_model
    embeddings = token_table + position_table + segment_table + layer_norm
    per_block = attention + feed_forward + 2 * layer_norm
    blocks = layers * per_block
    return {
        "d_ff": d_ff,
        "token_table": token_table,
        "position_table": position_table,
        "segment_table": segment_table,
        "embedding_norm": layer_norm,
        "embeddings": embeddings,
        "attention": attention,
        "feed_forward": feed_forward,
        "layer_norm": layer_norm,
        "per_block": per_block,
        "blocks": blocks,
        "total": embeddings + blocks,
    }


def bert_inputs(sentence_a, sentence_b=None, length=None):
    tokens = ["[CLS]"] + list(sentence_a) + ["[SEP]"]
    segments = [0] * len(tokens)
    if sentence_b:
        tokens += list(sentence_b) + ["[SEP]"]
        segments += [1] * (len(sentence_b) + 1)
    real = len(tokens)
    length = real if length is None else length
    if length < real:
        tokens, segments, real = tokens[:length - 1] + ["[SEP]"], segments[:length], length
    pad = length - real
    return {
        "tokens": tokens + ["[PAD]"] * pad,
        "segments": segments + [0] * pad,
        "positions": list(range(length)),
        "padding": [False] * real + [True] * pad,
        "real": real,
    }


def mlm_corrupt(tokens, rate, split, vocab, rng, special=("[CLS]", "[SEP]", "[PAD]")):
    candidates = [i for i, token in enumerate(tokens) if token not in special]
    count = max(1, round(rate * len(candidates)))
    chosen = sorted(rng.sample(candidates, count))
    inputs, labels, actions = list(tokens), [IGNORE_INDEX] * len(tokens), {}
    for i in chosen:
        labels[i] = tokens[i]
        draw = rng.random()
        if draw < split[0]:
            inputs[i], actions[i] = "[MASK]", "mask"
        elif draw < split[0] + split[1]:
            inputs[i], actions[i] = rng.choice(vocab), "random"
        else:
            actions[i] = "keep"
    return {"inputs": inputs, "labels": labels, "chosen": chosen, "actions": actions}


def mlm_corruption_rates(n, rate, split, vocab, seed):
    rng = random.Random(seed)
    tokens = [rng.choice(vocab) for _ in range(n)]
    result = mlm_corrupt(tokens, rate, split, vocab, rng)
    counts = {"mask": 0, "random": 0, "keep": 0}
    for action in result["actions"].values():
        counts[action] += 1
    changed = sum(a != b for a, b in zip(result["inputs"], tokens))
    return {
        "n": n,
        "selected": len(result["chosen"]),
        "fractions": {key: value / n for key, value in counts.items()},
        "unchanged_random": counts["random"] - sum(
            1 for i, a in result["actions"].items() if a == "random" and result["inputs"][i] != tokens[i]),
        "changed": changed / n,
    }


def masked_lm_loss(position_losses, labels):
    kept = [loss for loss, label in zip(position_losses, labels) if label != IGNORE_INDEX]
    return {"kept": len(kept), "loss": sum(kept) / len(kept)}


def padding_attention_check(example, keep, pad_key, pad_value):
    q, k, v = example["queries"][:keep], example["keys"][:keep], example["values"][:keep]
    alone = scaled_attention(q, k, v)
    pad_query = [0.0] * len(q[0])
    padded_q, padded_k, padded_v = q + [pad_query], k + [pad_key], v + [pad_value]
    mask = key_padding_additive([False] * keep + [True], keep + 1)
    masked = scaled_attention(padded_q, padded_k, padded_v, bias=mask)
    unmasked = scaled_attention(padded_q, padded_k, padded_v)
    gap = lambda a, b: max(abs(x - y) for row_a, row_b in zip(a, b) for x, y in zip(row_a, row_b))
    return {
        "alone": alone,
        "masked": masked,
        "unmasked": unmasked,
        "masked_gap": gap(alone["outputs"], masked["outputs"][:keep]),
        "unmasked_gap": gap(alone["outputs"], unmasked["outputs"][:keep]),
        "pad_weight": [row[keep] for row in unmasked["weights"][:keep]],
    }


def fill_in_model(corpus, alpha):
    middles = sorted({m for _, m, _ in corpus})
    rights = sorted({r for _, _, r in corpus} | {r for r, _, _ in corpus})
    left_counts, right_counts, middle_counts = {}, {}, {}
    for left, middle, right in corpus:
        left_counts[(left, middle)] = left_counts.get((left, middle), 0) + 1
        right_counts[(middle, right)] = right_counts.get((middle, right), 0) + 1
        middle_counts[middle] = middle_counts.get(middle, 0) + 1

    def given_left(left):
        raw = [left_counts.get((left, m), 0) + alpha for m in middles]
        total = sum(raw)
        return [value / total for value in raw]

    def right_given(middle, right):
        return (right_counts.get((middle, right), 0) + alpha) / (middle_counts[middle] + alpha * len(rights))

    def given_both(left, right):
        raw = [p * right_given(m, right) for p, m in zip(given_left(left), middles)]
        total = sum(raw)
        return [value / total for value in raw]

    def given_right(right):
        prior = [middle_counts[m] / len(corpus) for m in middles]
        raw = [p * right_given(m, right) for p, m in zip(prior, middles)]
        total = sum(raw)
        return [value / total for value in raw]

    return {"middles": middles, "left": given_left, "right": given_right, "both": given_both}


def fill_in_scores(corpus, test, alpha):
    model = fill_in_model(corpus, alpha)
    middles = model["middles"]
    rows, totals = [], {"left": 0.0, "right": 0.0, "both": 0.0}
    hits = {"left": 0, "right": 0, "both": 0}
    for left, middle, right in test:
        target = middles.index(middle)
        dists = {"left": model["left"](left), "right": model["right"](right), "both": model["both"](left, right)}
        row = {"sentence": (left, middle, right)}
        for key, dist in dists.items():
            row[key] = dist[target]
            row[key + "_guess"] = middles[max(range(len(dist)), key=lambda j: dist[j])]
            totals[key] += -math.log(dist[target])
            hits[key] += row[key + "_guess"] == middle
        rows.append(row)
    n = len(test)
    return {
        "middles": middles,
        "rows": rows,
        "nll": {key: value / n for key, value in totals.items()},
        "accuracy": {key: value / n for key, value in hits.items()},
    }


@functools.lru_cache(maxsize=None)
def encoder_example():
    e = ENCODER_EXAMPLE
    first = bert_inputs(e["sentence_a"], e["sentence_b"])
    second = bert_inputs(e["sentence_a"][:3], None)
    width = max(first["real"], second["real"])
    batch = [bert_inputs(e["sentence_a"], e["sentence_b"], width), bert_inputs(e["sentence_a"][:3], None, width)]
    corrupted = mlm_corrupt(first["tokens"], e["mask_rate"], e["mask_split"], e["mask_vocab"], random.Random(e["mask_seed"]))
    rates = mlm_corruption_rates(e["mask_sample_tokens"], e["mask_rate"], e["mask_split"], e["mask_vocab"], e["mask_seed"])
    attention = ATTENTION_EXAMPLE
    return {
        "configs": [dict(c, counts=encoder_param_count(c["vocab"], c["positions"], c["segments"], c["d_model"], c["layers"]))
                    for c in BERT_CONFIGS],
        "pair": first,
        "batch": batch,
        "corrupted": corrupted,
        "rates": rates,
        "bidirectional": attention_weights(attention),
        "causal": attention_weights(attention, causal=True),
        "prefix": causal_prefix_check(attention, 3),
        "padding": padding_attention_check(attention, 3, [0.0, 0.0], [0.0, 0.0]),
        "fill": fill_in_scores(tuple(e["fill_corpus"]), tuple(e["fill_test"]), e["fill_alpha"]),
    }


LTR_EXAMPLE = {
    "docs": ["d1", "d2", "d3", "d4", "d5"],
    "labels": [3, 2, 0, 1, 0],
    "scores": [0.2, 0.6, 0.9, -0.4, 0.1],
    "k": 3,
    "steps": 5,
    "learning_rate": 0.5,
    "pointwise_labels": [2, 1, 0],
    "pointwise_a": [1.1, 1.4, 0.0],
    "pointwise_b": [10.0, 5.0, 0.0],
}


def ltr_gain(label, exp_gain=True):
    return 2 ** label - 1 if exp_gain else label


def dcg_discount(position):
    return 1 / math.log2(position + 2)


def score_order(scores):
    return sorted(range(len(scores)), key=lambda i: -scores[i])


def dcg_at(ranked_labels, k=None, exp_gain=True):
    n = len(ranked_labels) if k is None else min(k, len(ranked_labels))
    return sum(ltr_gain(ranked_labels[i], exp_gain) * dcg_discount(i) for i in range(n))


def ndcg_at(labels, scores, k=None, exp_gain=True):
    ideal = dcg_at(sorted(labels, reverse=True), k, exp_gain)
    if ideal == 0:
        return 0.0
    return dcg_at([labels[i] for i in score_order(scores)], k, exp_gain) / ideal


def lambda_gradients(labels, scores, exp_gain=True, use_metric=True):
    order = score_order(scores)
    ideal = dcg_at(sorted(labels, reverse=True), None, exp_gain)
    inv_ideal = 0.0 if ideal == 0 else 1 / ideal
    n = len(labels)
    grad, hess, pairs = [0.0] * n, [0.0] * n, []
    for rank_i in range(n):
        for rank_j in range(rank_i + 1, n):
            high, low = rank_i, rank_j
            if labels[order[high]] == labels[order[low]]:
                continue
            if labels[order[high]] < labels[order[low]]:
                high, low = low, high
            i, j = order[high], order[low]
            if use_metric:
                g_i, g_j = ltr_gain(labels[i], exp_gain), ltr_gain(labels[j], exp_gain)
                kept = g_i * dcg_discount(high) + g_j * dcg_discount(low)
                swapped = g_j * dcg_discount(high) + g_i * dcg_discount(low)
                delta = abs((kept - swapped) * inv_ideal)
            else:
                delta = 1.0
            p = sigmoid(scores[i] - scores[j])
            g = (p - 1) * delta
            h = max(p * (1 - p), 1e-16) * delta * 2
            grad[i] += g
            grad[j] -= g
            hess[i] += h
            hess[j] += h
            pairs.append({"high": i, "low": j, "delta": delta, "grad": g})
    return {"grad": grad, "hess": hess, "pairs": pairs, "order": order}


def listnet_loss(labels, scores):
    def softmax(xs):
        top = max(xs)
        exps = [math.exp(x - top) for x in xs]
        total = sum(exps)
        return [e / total for e in exps]

    target, predicted = softmax(labels), softmax(scores)
    return -sum(t * math.log(q) for t, q in zip(target, predicted))


def ltr_newton_steps(labels, scores, steps, learning_rate, use_metric=True):
    history = [{"scores": list(scores), "ndcg": ndcg_at(labels, scores)}]
    current = list(scores)
    for _ in range(steps):
        lam = lambda_gradients(labels, current, use_metric=use_metric)
        current = [s - learning_rate * g / h if h > 0 else s
                   for s, g, h in zip(current, lam["grad"], lam["hess"])]
        history.append({"scores": list(current), "ndcg": ndcg_at(labels, current)})
    return history


@functools.lru_cache(maxsize=None)
def ltr_example():
    e = LTR_EXAMPLE
    labels, scores = e["labels"], e["scores"]
    order = score_order(scores)
    lam = lambda_gradients(labels, scores)
    ranknet = lambda_gradients(labels, scores, use_metric=False)
    pointwise = {}
    for name in ("a", "b"):
        guess = e["pointwise_" + name]
        truth = e["pointwise_labels"]
        pointwise[name] = {
            "scores": guess,
            "mse": sum((g - t) ** 2 for g, t in zip(guess, truth)) / len(truth),
            "ndcg": ndcg_at(truth, guess),
        }
    return {
        "example": e,
        "order": order,
        "ranked_labels": [labels[i] for i in order],
        "ideal_labels": sorted(labels, reverse=True),
        "discounts": [dcg_discount(i) for i in range(len(labels))],
        "dcg": dcg_at([labels[i] for i in order]),
        "idcg": dcg_at(sorted(labels, reverse=True)),
        "ndcg": ndcg_at(labels, scores),
        "ndcg_linear": ndcg_at(labels, scores, exp_gain=False),
        "ndcg_k": ndcg_at(labels, scores, k=e["k"]),
        "lambda": lam,
        "ranknet": ranknet,
        "listnet": {"start": listnet_loss(labels, scores), "ideal": listnet_loss(labels, labels)},
        "lambdamart": ltr_newton_steps(labels, scores, e["steps"], e["learning_rate"]),
        "ranknet_steps": ltr_newton_steps(labels, scores, e["steps"], e["learning_rate"], use_metric=False),
        "pointwise": pointwise,
    }


DATA_EXAMPLE = {
    "lengths": [5, 23, 9, 31, 14, 7, 18, 4, 27, 11, 16, 8],
    "batch_size": 4,
    "context": 32,
    "dataset_size": 10,
    "loader_batch_size": 3,
    "replicas": 4,
    "load_ms": 40,
    "compute_ms": 15,
    "workers": [0, 1, 2, 3, 4],
    "prefetch_factor": 2,
    "batches": 12,
    "grads": [0.9, -0.3, 1.6, 0.2, -1.1, 0.7, 2.0, 0.4],
    "grad_batch_sizes": [1, 2, 4, 8],
}


def padded_batches(lengths, batch_size):
    batches = []
    for start in range(0, len(lengths), batch_size):
        chunk = lengths[start:start + batch_size]
        batches.append({
            "lengths": chunk,
            "padded_to": max(chunk),
            "slots": max(chunk) * len(chunk),
            "real": sum(chunk),
        })
    slots = sum(b["slots"] for b in batches)
    return {"batches": batches, "slots": slots, "real": sum(lengths), "efficiency": sum(lengths) / slots}


def pack_into_rows(lengths, context):
    rows = []
    for length in sorted(lengths, reverse=True):
        for row in rows:
            if sum(row) + length <= context:
                row.append(length)
                break
        else:
            rows.append([length])
    slots = len(rows) * context
    return {"rows": rows, "slots": slots, "real": sum(lengths), "efficiency": sum(lengths) / slots}


def loader_length(n, batch_size, drop_last):
    return n // batch_size if drop_last else -(-n // batch_size)


def distributed_shards(n, replicas, drop_last=False):
    if drop_last and n % replicas:
        num_samples = math.ceil((n - replicas) / replicas)
    else:
        num_samples = math.ceil(n / replicas)
    total = num_samples * replicas
    indices = list(range(n))
    if drop_last:
        indices = indices[:total]
    else:
        padding = total - n
        indices += (indices * math.ceil(padding / n))[:padding] if padding else []
    return {
        "num_samples": num_samples,
        "indices": indices,
        "shards": [indices[rank:total:replicas] for rank in range(replicas)],
    }


def loader_pipeline(load_ms, compute_ms, workers, batches, prefetch_factor=2):
    if workers == 0:
        per_batch = load_ms + compute_ms
        return {"total_ms": per_batch * batches, "per_batch_ms": per_batch, "gpu_busy": compute_ms / per_batch, "timeline": []}
    limit = prefetch_factor * workers
    dispatch = [0.0] * batches
    worker_free = [0.0] * workers
    compute_end = 0.0
    timeline = []
    for i in range(batches):
        w = i % workers
        start = max(worker_free[w], dispatch[i])
        ready = start + load_ms
        worker_free[w] = ready
        take = max(ready, compute_end)
        compute_end = take + compute_ms
        if i + limit < batches:
            dispatch[i + limit] = take
        timeline.append({"worker": w, "load_start": start, "ready": ready, "compute_start": take, "compute_end": compute_end})
    return {
        "total_ms": compute_end,
        "per_batch_ms": compute_end / batches,
        "gpu_busy": compute_ms * batches / compute_end,
        "timeline": timeline,
    }


def minibatch_gradient_variance(grads, batch_size):
    n = len(grads)
    mean = sum(grads) / n
    population = sum((g - mean) ** 2 for g in grads) / n
    variance = population / batch_size * (n - batch_size) / (n - 1)
    return {"mean": mean, "variance": variance, "std": math.sqrt(variance)}


@functools.lru_cache(maxsize=None)
def data_example():
    e = DATA_EXAMPLE
    lengths = e["lengths"]
    return {
        "example": e,
        "shuffled": padded_batches(lengths, e["batch_size"]),
        "bucketed": padded_batches(sorted(lengths), e["batch_size"]),
        "packed": pack_into_rows(lengths, e["context"]),
        "lengths": {n: loader_length(e["dataset_size"], e["loader_batch_size"], d) for n, d in (("keep", False), ("drop", True))},
        "shards": distributed_shards(e["dataset_size"], e["replicas"]),
        "shards_drop": distributed_shards(e["dataset_size"], e["replicas"], drop_last=True),
        "pipelines": [
            dict(loader_pipeline(e["load_ms"], e["compute_ms"], w, e["batches"], e["prefetch_factor"]), workers=w)
            for w in e["workers"]
        ],
        "noise": [
            dict(minibatch_gradient_variance(e["grads"], b), batch_size=b)
            for b in e["grad_batch_sizes"]
        ],
    }


SERVING_EXAMPLE = {
    "arrivals": [0, 1, 2, 4, 5, 7, 8, 9, 12, 13, 15, 16, 18, 19, 21, 22],
    "fixed_ms": 5,
    "per_item_ms": 1,
    "policies": [
        {"name": "one at a time", "max_batch": 1, "max_wait_ms": 0},
        {"name": "batch of up to 4, no wait", "max_batch": 4, "max_wait_ms": 0},
        {"name": "batch of up to 4, wait 3 ms", "max_batch": 4, "max_wait_ms": 3},
        {"name": "batch of up to 8, wait 3 ms", "max_batch": 8, "max_wait_ms": 3},
    ],
    "devices": [
        {"name": "CPU", "fixed_ms": 0.5, "per_item_ms": 2.0},
        {"name": "GPU", "fixed_ms": 3.0, "per_item_ms": 0.05},
    ],
    "cost_sizes": [1, 4, 16, 64],
    "decode_requests": [(0, 3), (0, 9), (0, 4), (0, 2), (1, 5), (2, 3), (3, 6), (4, 2)],
    "decode_slots": 4,
}


def batch_cost(fixed_ms, per_item_ms, size):
    latency = fixed_ms + per_item_ms * size
    return {"size": size, "latency_ms": latency, "per_second": 1000 * size / latency}


def nearest_rank(values, q):
    ordered = sorted(values)
    return ordered[max(1, math.ceil(q * len(ordered))) - 1]


def dynamic_batching(arrivals, fixed_ms, per_item_ms, max_batch, max_wait_ms):
    queue = sorted(arrivals)
    free_at = 0
    i = 0
    batches = []
    finish = []
    while i < len(queue):
        deadline = queue[i] + max_wait_ms
        full = queue[i + max_batch - 1] if i + max_batch - 1 < len(queue) else math.inf
        start = max(free_at, min(deadline, full))
        size = 0
        while i + size < len(queue) and size < max_batch and queue[i + size] <= start:
            size += 1
        end = start + fixed_ms + per_item_ms * size
        batches.append({"start": start, "end": end, "size": size, "arrivals": queue[i:i + size]})
        finish.extend([end] * size)
        free_at = end
        i += size
    latencies = [f - a for f, a in zip(finish, queue)]
    busy = sum(b["end"] - b["start"] for b in batches)
    makespan = batches[-1]["end"] - queue[0]
    return {
        "batches": batches,
        "latencies": latencies,
        "mean_ms": sum(latencies) / len(latencies),
        "p50_ms": nearest_rank(latencies, 0.5),
        "p90_ms": nearest_rank(latencies, 0.9),
        "max_ms": max(latencies),
        "makespan_ms": makespan,
        "per_second": 1000 * len(queue) / makespan,
        "busy": busy / makespan,
        "mean_batch": len(queue) / len(batches),
    }


def decode_batching(requests, slots, continuous):
    waiting = sorted(range(len(requests)), key=lambda r: (requests[r][0], r))
    remaining = [tokens for _, tokens in requests]
    running = []
    finish = [None] * len(requests)
    step = 0
    busy_steps = 0
    timeline = []
    while waiting or running:
        if continuous or not running:
            while waiting and len(running) < slots and requests[waiting[0]][0] <= step:
                running.append(waiting.pop(0))
        if not running:
            step = requests[waiting[0]][0]
            continue
        active = [r for r in running if remaining[r] > 0]
        timeline.append({"step": step, "active": active, "idle": slots - len(active)})
        busy_steps += 1
        step += 1
        for r in active:
            remaining[r] -= 1
            if remaining[r] == 0:
                finish[r] = step
        if continuous or not any(remaining[r] for r in running):
            running = [r for r in running if remaining[r] > 0]
    tokens = sum(t for _, t in requests)
    latencies = [finish[r] - requests[r][0] for r in range(len(requests))]
    return {
        "finish": finish,
        "latencies": latencies,
        "mean_steps": sum(latencies) / len(latencies),
        "steps": step,
        "busy_steps": busy_steps,
        "tokens": tokens,
        "utilization": tokens / (busy_steps * slots),
        "timeline": timeline,
    }


@functools.lru_cache(maxsize=None)
def serving_example():
    e = SERVING_EXAMPLE
    return {
        "example": e,
        "policies": [
            dict(dynamic_batching(e["arrivals"], e["fixed_ms"], e["per_item_ms"], p["max_batch"], p["max_wait_ms"]), **p)
            for p in e["policies"]
        ],
        "devices": [
            dict(d, costs=[batch_cost(d["fixed_ms"], d["per_item_ms"], size) for size in e["cost_sizes"]])
            for d in e["devices"]
        ],
        "static": decode_batching(e["decode_requests"], e["decode_slots"], continuous=False),
        "continuous": decode_batching(e["decode_requests"], e["decode_slots"], continuous=True),
    }


CAUSAL_EXAMPLE = {
    "units": [
        {"z": 0, "y0": 8, "y1": 9, "t": 0},
        {"z": 0, "y0": 7, "y1": 9, "t": 0},
        {"z": 0, "y0": 9, "y1": 10, "t": 0},
        {"z": 0, "y0": 8, "y1": 10, "t": 1},
        {"z": 1, "y0": 3, "y1": 6, "t": 1},
        {"z": 1, "y0": 2, "y1": 5, "t": 1},
        {"z": 1, "y0": 4, "y1": 6, "t": 1},
        {"z": 1, "y0": 3, "y1": 5, "t": 0},
    ],
    "strata": [
        {"name": "mild", "z": 0, "treated": 200, "treated_recovered": 180, "control": 600, "control_recovered": 480},
        {"name": "severe", "z": 1, "treated": 300, "treated_recovered": 150, "control": 100, "control_recovered": 40},
    ],
    "did_treated": [48, 50, 62, 64],
    "did_control": [38, 40, 46, 48],
    "did_first_post": 2,
    "segments": [
        {"name": "A", "size": 1000, "treated_rate": 0.30, "control_rate": 0.10},
        {"name": "B", "size": 1000, "treated_rate": 0.60, "control_rate": 0.58},
        {"name": "C", "size": 1000, "treated_rate": 0.05, "control_rate": 0.04},
        {"name": "D", "size": 1000, "treated_rate": 0.35, "control_rate": 0.45},
    ],
    "target_segments": 2,
}


def potential_outcomes_summary(units):
    treated = [u["y1"] for u in units if u["t"] == 1]
    control = [u["y0"] for u in units if u["t"] == 0]
    effects = [u["y1"] - u["y0"] for u in units]
    ate = sum(effects) / len(units)
    naive = sum(treated) / len(treated) - sum(control) / len(control)
    treated_baseline = statistics.fmean(u["y0"] for u in units if u["t"] == 1)
    control_baseline = statistics.fmean(u["y0"] for u in units if u["t"] == 0)
    att = statistics.fmean(u["y1"] - u["y0"] for u in units if u["t"] == 1)
    return {
        "effects": effects,
        "ate": ate,
        "att": att,
        "naive": naive,
        "selection_bias": treated_baseline - control_baseline,
        "observed": [u["y1"] if u["t"] else u["y0"] for u in units],
    }


def randomized_assignments(units, treated_count):
    estimates = []
    for chosen in itertools.combinations(range(len(units)), treated_count):
        picked = set(chosen)
        treated = statistics.fmean(units[i]["y1"] for i in picked)
        control = statistics.fmean(units[i]["y0"] for i in range(len(units)) if i not in picked)
        estimates.append(treated - control)
    return {
        "count": len(estimates),
        "mean": statistics.fmean(estimates),
        "min": min(estimates),
        "max": max(estimates),
        "std": statistics.pstdev(estimates),
    }


def stratified_effect(strata):
    total = sum(s["treated"] + s["control"] for s in strata)
    rows = []
    for s in strata:
        size = s["treated"] + s["control"]
        treated_rate = s["treated_recovered"] / s["treated"]
        control_rate = s["control_recovered"] / s["control"]
        rows.append({
            "name": s["name"],
            "size": size,
            "share": size / total,
            "propensity": s["treated"] / size,
            "treated_rate": treated_rate,
            "control_rate": control_rate,
            "effect": treated_rate - control_rate,
        })
    treated_total = sum(s["treated"] for s in strata)
    control_total = sum(s["control"] for s in strata)
    naive_treated = sum(s["treated_recovered"] for s in strata) / treated_total
    naive_control = sum(s["control_recovered"] for s in strata) / control_total
    return {
        "rows": rows,
        "total": total,
        "naive_treated": naive_treated,
        "naive_control": naive_control,
        "naive": naive_treated - naive_control,
        "adjusted": sum(r["share"] * r["effect"] for r in rows),
    }


def ipw_effect(strata, propensities=None):
    total = sum(s["treated"] + s["control"] for s in strata)
    treated_sum = control_sum = treated_weight = control_weight = 0.0
    weights = []
    for i, s in enumerate(strata):
        e = propensities[i] if propensities else s["treated"] / (s["treated"] + s["control"])
        treated_sum += s["treated_recovered"] / e
        control_sum += s["control_recovered"] / (1 - e)
        treated_weight += s["treated"] / e
        control_weight += s["control"] / (1 - e)
        weights.append({"name": s["name"], "propensity": e, "treated": 1 / e, "control": 1 / (1 - e),
                        "pseudo_treated": s["treated"] / e, "pseudo_control": s["control"] / (1 - e)})
    return {
        "weights": weights,
        "horvitz_thompson": (treated_sum - control_sum) / total,
        "hajek": treated_sum / treated_weight - control_sum / control_weight,
    }


def propensity_fit(strata, c=None):
    rows, treated = [], []
    for s in strata:
        size = s["treated"] + s["control"]
        rows += [[s["z"]]] * size
        treated += [1] * s["treated"] + [0] * s["control"]
    weight, bias = logistic_newton(rows, treated, c=c)[-1]["params"]
    return {
        "weight": weight,
        "bias": bias,
        "propensities": [sigmoid(weight * s["z"] + bias) for s in strata],
    }


def diff_in_diff(treated, control, first_post):
    pre_t = statistics.fmean(treated[:first_post])
    post_t = statistics.fmean(treated[first_post:])
    pre_c = statistics.fmean(control[:first_post])
    post_c = statistics.fmean(control[first_post:])
    effect = (post_t - pre_t) - (post_c - pre_c)
    counterfactual = [t if i < first_post else pre_t + (c - pre_c) for i, (t, c) in enumerate(zip(treated, control))]
    return {
        "pre_treated": pre_t,
        "post_treated": post_t,
        "pre_control": pre_c,
        "post_control": post_c,
        "effect": effect,
        "before_after": post_t - pre_t,
        "post_gap": post_t - post_c,
        "pre_trend_gap": (treated[first_post - 1] - treated[0]) - (control[first_post - 1] - control[0]),
        "counterfactual": counterfactual,
    }


def uplift_targeting(segments, k):
    rows = [dict(s, uplift=s["treated_rate"] - s["control_rate"]) for s in segments]
    for r in rows:
        r["incremental"] = r["size"] * r["uplift"]

    def pick(key):
        chosen = sorted(rows, key=key, reverse=True)[:k]
        return {"names": [r["name"] for r in chosen], "incremental": sum(r["incremental"] for r in chosen)}

    return {
        "rows": rows,
        "by_response": pick(lambda r: r["treated_rate"]),
        "by_uplift": pick(lambda r: r["uplift"]),
        "everyone": sum(r["incremental"] for r in rows),
    }


@functools.lru_cache(maxsize=None)
def causal_example():
    e = CAUSAL_EXAMPLE
    strat = stratified_effect(e["strata"])
    fitted = propensity_fit(e["strata"])
    regularized = propensity_fit(e["strata"], c=1.0)
    return {
        "example": e,
        "po": potential_outcomes_summary(e["units"]),
        "randomized": randomized_assignments(e["units"], 4),
        "strat": strat,
        "ipw": ipw_effect(e["strata"]),
        "fit": fitted,
        "fit_ipw": ipw_effect(e["strata"], fitted["propensities"]),
        "regularized": regularized,
        "regularized_ipw": ipw_effect(e["strata"], regularized["propensities"]),
        "did": diff_in_diff(e["did_treated"], e["did_control"], e["did_first_post"]),
        "uplift": uplift_targeting(e["segments"], e["target_segments"]),
    }


CALIBRATION_EXAMPLE = {
    "probabilities": [
        0.05, 0.05, 0.10, 0.10, 0.15,
        0.30, 0.35,
        0.50, 0.55,
        0.65, 0.70, 0.75,
        0.85, 0.90, 0.90, 0.95, 0.95, 0.95, 0.99, 0.99,
    ],
    "labels": [
        0, 0, 1, 0, 0,
        1, 0,
        1, 0,
        1, 0, 1,
        1, 1, 0, 1, 1, 0, 1, 1,
    ],
    "n_bins": 5,
    "margin": 2.0,
    "scales": [1, 2, 4, 8],
}


def reliability_bins(probabilities, labels, n_bins):
    inner = [i / n_bins for i in range(1, n_bins)]
    bins = [{"lo": i / n_bins, "hi": (i + 1) / n_bins, "probs": [], "labels": []} for i in range(n_bins)]
    for p, y in zip(probabilities, labels):
        index = sum(1 for edge in inner if edge < p)
        bins[index]["probs"].append(p)
        bins[index]["labels"].append(y)
    total = len(probabilities)
    rows = []
    for b in bins:
        count = len(b["probs"])
        confidence = sum(b["probs"]) / count if count else None
        accuracy = sum(b["labels"]) / count if count else None
        rows.append({
            "lo": b["lo"],
            "hi": b["hi"],
            "count": count,
            "positives": sum(b["labels"]),
            "confidence": confidence,
            "accuracy": accuracy,
            "gap": abs(accuracy - confidence) if count else None,
            "share": count / total,
        })
    filled = [r for r in rows if r["count"]]
    return {
        "rows": rows,
        "ece": sum(r["share"] * r["gap"] for r in filled),
        "mce": max(r["gap"] for r in filled),
    }


def brier_score(labels, probabilities):
    return sum((p - y) ** 2 for y, p in zip(labels, probabilities)) / len(labels)


def calibration_report(labels, probabilities, n_bins):
    bins = reliability_bins(probabilities, labels, n_bins)
    return {
        "bins": bins["rows"],
        "ece": bins["ece"],
        "mce": bins["mce"],
        "brier": brier_score(labels, probabilities),
        "log_loss": binary_log_loss(labels, probabilities),
        "auc": rank_auc(labels, probabilities),
        "accuracy": sum((p > 0.5) == (y == 1) for y, p in zip(labels, probabilities)) / len(labels),
    }


def logit(p):
    return math.log(p / (1 - p))


def platt_scaling(scores, labels, iterations=25):
    positives = sum(labels)
    negatives = len(labels) - positives
    hi = (positives + 1) / (positives + 2)
    lo = 1 / (negatives + 2)
    targets = [hi if y == 1 else lo for y in labels]
    a, b = 1.0, 0.0
    for _ in range(iterations):
        ga = gb = haa = hab = hbb = 0.0
        for s, t in zip(scores, targets):
            p = sigmoid(a * s + b)
            r = p - t
            w = p * (1 - p)
            ga += r * s
            gb += r
            haa += w * s * s
            hab += w * s
            hbb += w
        det = haa * hbb - hab * hab
        a -= (hbb * ga - hab * gb) / det
        b -= (haa * gb - hab * ga) / det
    return {
        "a": a,
        "b": b,
        "target_positive": hi,
        "target_negative": lo,
        "probabilities": [sigmoid(a * s + b) for s in scores],
    }


def temperature_scaling(logits, labels, iterations=25):
    beta = 1.0
    for _ in range(iterations):
        grad = hess = 0.0
        for z, y in zip(logits, labels):
            p = sigmoid(beta * z)
            grad += (p - y) * z
            hess += p * (1 - p) * z * z
        beta -= grad / hess
    return {
        "beta": beta,
        "temperature": 1 / beta,
        "probabilities": [sigmoid(beta * z) for z in logits],
    }


def isotonic_pav(probabilities, labels):
    grouped = {}
    for p, y in zip(probabilities, labels):
        grouped.setdefault(p, []).append(y)
    blocks = [
        {"xs": [x], "total": sum(ys), "weight": len(ys)}
        for x, ys in sorted(grouped.items())
    ]
    merges = 0
    stack = []
    for block in blocks:
        stack.append(block)
        while len(stack) > 1 and stack[-2]["total"] / stack[-2]["weight"] >= stack[-1]["total"] / stack[-1]["weight"]:
            top = stack.pop()
            below = stack.pop()
            stack.append({
                "xs": below["xs"] + top["xs"],
                "total": below["total"] + top["total"],
                "weight": below["weight"] + top["weight"],
            })
            merges += 1
    steps = [
        {"lo": b["xs"][0], "hi": b["xs"][-1], "value": b["total"] / b["weight"], "weight": b["weight"]}
        for b in stack
    ]
    lookup = {x: s["value"] for s, b in zip(steps, stack) for x in b["xs"]}
    return {
        "unique": [
            {"x": x, "mean": sum(ys) / len(ys), "weight": len(ys)} for x, ys in sorted(grouped.items())
        ],
        "steps": steps,
        "merges": merges,
        "probabilities": [lookup[p] for p in probabilities],
    }


def overconfidence_losses(margin, scales):
    return [
        {"scale": k, "logit": margin * k, "correct": -math.log(sigmoid(margin * k)), "wrong": -math.log(sigmoid(-margin * k))}
        for k in scales
    ]


@functools.lru_cache(maxsize=None)
def calibration_example():
    e = CALIBRATION_EXAMPLE
    probs, labels, n_bins = e["probabilities"], e["labels"], e["n_bins"]
    logits = [logit(p) for p in probs]
    base_rate = sum(labels) / len(labels)
    platt = platt_scaling(logits, labels)
    temperature = temperature_scaling(logits, labels)
    isotonic = isotonic_pav(probs, labels)
    return {
        "example": e,
        "logits": logits,
        "base_rate": base_rate,
        "original": calibration_report(labels, probs, n_bins),
        "constant": calibration_report(labels, [base_rate] * len(labels), n_bins),
        "platt": platt,
        "platt_report": calibration_report(labels, platt["probabilities"], n_bins),
        "temperature": temperature,
        "temperature_report": calibration_report(labels, temperature["probabilities"], n_bins),
        "isotonic": isotonic,
        "isotonic_report": calibration_report(labels, isotonic["probabilities"], n_bins),
        "overconfidence": overconfidence_losses(e["margin"], e["scales"]),
        "maps": [
            {
                "p": p,
                "platt": sigmoid(platt["a"] * logit(p) + platt["b"]),
                "temperature": sigmoid(temperature["beta"] * logit(p)),
            }
            for p in [i / 40 for i in range(1, 40)]
        ],
    }


GNN_EXAMPLE = {
    "nodes": ["A", "B", "C", "D", "E"],
    "edges": [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4)],
    "features": [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 2.0], [2.0, 0.0]],
    "weight": [[0.5, -1.0], [1.0, 0.5]],
    "gat_weight": [[1.0, 0.0], [0.5, 1.0]],
    "gat_attention": [0.5, -1.0, 1.0, -1.0],
    "gat_slope": 0.2,
    "sage_weight": [[1.0, 0.0, 0.5, 0.5], [0.0, 1.0, -0.5, 1.0]],
    "focus": 2,
    "depths": [0, 1, 2, 4, 8, 16, 32],
    "second_graph": {"nodes": 3, "edges": [(0, 1), (1, 2), (0, 2)], "features": [[1.0, 1.0], [0.0, 3.0], [2.0, 2.0]]},
}


def adjacency_matrix(n, edges):
    a = [[0] * n for _ in range(n)]
    for i, j in edges:
        a[i][j] = a[j][i] = 1
    return a


def gcn_propagation(n, edges):
    a = adjacency_matrix(n, edges)
    a_tilde = [[a[i][j] + (1 if i == j else 0) for j in range(n)] for i in range(n)]
    degrees = [sum(row) for row in a_tilde]
    norm = [[a_tilde[i][j] / math.sqrt(degrees[i] * degrees[j]) for j in range(n)] for i in range(n)]
    return {"adjacency": a, "self_loops": a_tilde, "degrees": degrees, "normalized": norm}


def directed_edge_index(edges, self_loops=True, n=None):
    sources, targets = [], []
    for i, j in edges:
        sources += [i, j]
        targets += [j, i]
    if self_loops:
        for v in range(n):
            sources.append(v)
            targets.append(v)
    return sources, targets


def index_add_rows(n, index, rows):
    out = [[0.0] * len(rows[0]) for _ in range(n)]
    for target, row in zip(index, rows):
        out[target] = [o + r for o, r in zip(out[target], row)]
    return out


def gcn_message_passing(features, edges, weight):
    n = len(features)
    transformed = matmul(features, weight)
    sources, targets = directed_edge_index(edges, True, n)
    degrees = [0] * n
    for t in targets:
        degrees[t] += 1
    coefficients = [1 / math.sqrt(degrees[s] * degrees[t]) for s, t in zip(sources, targets)]
    messages = [[c * x for x in transformed[s]] for s, c in zip(sources, coefficients)]
    return {
        "transformed": transformed,
        "sources": sources,
        "targets": targets,
        "coefficients": coefficients,
        "aggregated": index_add_rows(n, targets, messages),
    }


def leaky_relu_scalar(x, slope):
    return x if x >= 0 else slope * x


def gat_node(features, edges, weight, attention, slope, node):
    n = len(features)
    z = matmul(features, weight)
    neighbours = sorted({node} | {j for i, j in edges if i == node} | {i for i, j in edges if j == node})
    half = len(z[0])
    scores = [
        leaky_relu_scalar(dot_product(attention[:half], z[node]) + dot_product(attention[half:], z[j]), slope)
        for j in neighbours
    ]
    alpha = softmax_probs(scores)
    out = [sum(a * z[j][k] for a, j in zip(alpha, neighbours)) for k in range(half)]
    return {"z": z, "neighbours": neighbours, "scores": scores, "alpha": alpha, "output": out, "n": n}


def sage_node(features, edges, weight, node):
    neighbours = sorted({j for i, j in edges if i == node} | {i for i, j in edges if j == node})
    mean = [sum(features[j][k] for j in neighbours) / len(neighbours) for k in range(len(features[0]))]
    concat = features[node] + mean
    pre = [dot_product(row, concat) for row in weight]
    activated = relu(pre)
    length = vector_norm(activated)
    return {
        "neighbours": neighbours,
        "mean": mean,
        "concat": concat,
        "pre": pre,
        "activated": activated,
        "output": [x / length for x in activated] if length else activated,
    }


def oversmoothing(features, edges, depths):
    n = len(features)
    prop = gcn_propagation(n, edges)
    limit = [math.sqrt(d) for d in prop["degrees"]]
    rows = []
    h, step = [list(r) for r in features], 0
    for depth in depths:
        while step < depth:
            h = matmul(prop["normalized"], h)
            step += 1
        cosines = [cosine_similarity(h[i], h[j]) for i in range(n) for j in range(i + 1, n)]
        scaled = [[x / s for x in row] for row, s in zip(h, limit)]
        spread = max(vector_norm([a - b for a, b in zip(scaled[i], scaled[j])]) for i in range(n) for j in range(i + 1, n))
        rows.append({"depth": depth, "features": h, "min_cosine": min(cosines), "spread": spread})
    return {"rows": rows, "limit_direction": limit}


def batch_graphs(graphs):
    features, sources, targets, batch, offsets = [], [], [], [], []
    for g, graph in enumerate(graphs):
        offset = len(features)
        offsets.append(offset)
        features += [list(r) for r in graph["features"]]
        for i, j in graph["edges"]:
            sources.append(i + offset)
            targets.append(j + offset)
        batch += [g] * len(graph["features"])
    sums = index_add_rows(len(graphs), batch, features)
    counts = [batch.count(g) for g in range(len(graphs))]
    return {
        "features": features,
        "sources": sources,
        "targets": targets,
        "batch": batch,
        "offsets": offsets,
        "sum_pool": sums,
        "mean_pool": [[x / c for x in row] for row, c in zip(sums, counts)],
    }


def gcn_layer_params(f_in, f_out, bias=True):
    return f_in * f_out + (f_out if bias else 0)


@functools.lru_cache(maxsize=None)
def gnn_example():
    e = GNN_EXAMPLE
    n, x = len(e["nodes"]), e["features"]
    prop = gcn_propagation(n, e["edges"])
    ax = matmul(prop["normalized"], x)
    axw = matmul(ax, e["weight"])
    mp = gcn_message_passing(x, e["edges"], e["weight"])
    second = e["second_graph"]
    return {
        "example": e,
        "prop": prop,
        "ax": ax,
        "axw": axw,
        "gcn": [relu(row) for row in axw],
        "mp": mp,
        "gat": gat_node(x, e["edges"], e["gat_weight"], e["gat_attention"], e["gat_slope"], e["focus"]),
        "sage": sage_node(x, e["edges"], e["sage_weight"], e["focus"]),
        "smooth": oversmoothing(x, e["edges"], tuple(e["depths"])),
        "batch": batch_graphs([
            {"features": x, "edges": e["edges"]},
            {"features": second["features"], "edges": second["edges"]},
        ]),
        "params": {
            "gcn": gcn_layer_params(2, 2),
            "sage": gcn_layer_params(4, 2, bias=False),
            "gat": gcn_layer_params(2, 2, bias=False) + len(e["gat_attention"]),
        },
    }


DIFFUSION_EXAMPLE = {
    "steps": 1000,
    "beta_start": 1e-4,
    "beta_end": 0.02,
    "cosine_offset": 0.008,
    "checkpoints": [1, 10, 50, 100, 250, 500, 750, 1000],
    "x0": 1.0,
    "eps": -0.5,
    "prior_plus": 0.7,
    "ddim_steps": [10, 50],
    "ddim_starts": [-1.5, -0.5, 0.0, 0.5, 1.5],
    "grid": 400,
    "guidance": [0.0, 1.0, 3.0],
    "ddpm_samples": 1000,
    "ddpm_seed": 0,
    "latent": {"height": 512, "width": 512, "channels": 3, "factor": 8, "latent_channels": 4},
}


def diffusion_linear_betas(steps, start, end):
    return [start + (end - start) * i / (steps - 1) for i in range(steps)]


def diffusion_cosine_betas(steps, offset=0.008, max_beta=0.999):
    def f(t):
        return math.cos((t / steps + offset) / (1 + offset) * math.pi / 2) ** 2
    return [min(1 - f(t + 1) / f(t), max_beta) for t in range(steps)]


def diffusion_alpha_bars(betas):
    out, running = [], 1.0
    for b in betas:
        running *= 1 - b
        out.append(running)
    return out


def diffusion_forward(x0, eps, alpha_bar):
    return math.sqrt(alpha_bar) * x0 + math.sqrt(1 - alpha_bar) * eps


def diffusion_iterated_moments(betas, x0):
    mean, var = x0, 0.0
    for b in betas:
        mean = math.sqrt(1 - b) * mean
        var = (1 - b) * var + b
    return mean, var


def diffusion_posterior(x0, xt, t, betas, alpha_bars):
    ab, ab_prev = alpha_bars[t], alpha_bars[t - 1] if t > 0 else 1.0
    beta = betas[t]
    coef_x0 = math.sqrt(ab_prev) * beta / (1 - ab)
    coef_xt = math.sqrt(1 - beta) * (1 - ab_prev) / (1 - ab)
    return {
        "coef_x0": coef_x0,
        "coef_xt": coef_xt,
        "mean": coef_x0 * x0 + coef_xt * xt,
        "variance": (1 - ab_prev) / (1 - ab) * beta,
    }


def diffusion_eps_mean(xt, eps, t, betas, alpha_bars):
    return (xt - betas[t] / math.sqrt(1 - alpha_bars[t]) * eps) / math.sqrt(1 - betas[t])


def diffusion_elbo_weight(t, betas, alpha_bars, variance):
    beta = betas[t]
    return beta * beta / (2 * variance * (1 - beta) * (1 - alpha_bars[t]))


def two_point_denoiser(xt, alpha_bar, prior_plus=0.5):
    shift = 0.5 * math.log(prior_plus / (1 - prior_plus))
    x0_hat = math.tanh(math.sqrt(alpha_bar) * xt / (1 - alpha_bar) + shift)
    eps_hat = (xt - math.sqrt(alpha_bar) * x0_hat) / math.sqrt(1 - alpha_bar)
    return x0_hat, eps_hat


def two_point_eps(xt, alpha_bar):
    return two_point_denoiser(xt, alpha_bar)[1]


def guided_eps(xt, alpha_bar, prior_plus, weight):
    cond = two_point_denoiser(xt, alpha_bar, prior_plus)[1]
    uncond = two_point_denoiser(xt, alpha_bar, 0.5)[1]
    return (1 + weight) * cond - weight * uncond


def guidance_tilt(prior_plus, uncond_plus, weight):
    plus = prior_plus ** (1 + weight) / uncond_plus ** weight
    minus = (1 - prior_plus) ** (1 + weight) / (1 - uncond_plus) ** weight
    return plus / (plus + minus)


def ddim_timesteps(steps, count):
    stride = steps // count
    return list(range(steps - 1, -1, -stride))[:count]


def ddim_sample(xt, alpha_bars, timesteps, eps_fn):
    path = [xt]
    for k, t in enumerate(timesteps):
        ab = alpha_bars[t]
        ab_next = alpha_bars[timesteps[k + 1]] if k + 1 < len(timesteps) else 1.0
        eps = eps_fn(xt, ab)
        x0_hat = (xt - math.sqrt(1 - ab) * eps) / math.sqrt(ab)
        xt = math.sqrt(ab_next) * x0_hat + math.sqrt(1 - ab_next) * eps
        path.append(xt)
    return path


def ddpm_sample(xt, betas, alpha_bars, eps_fn, rng):
    for t in range(len(betas) - 1, -1, -1):
        eps = eps_fn(xt, alpha_bars[t])
        mean = diffusion_eps_mean(xt, eps, t, betas, alpha_bars)
        xt = mean + (math.sqrt(betas[t]) * rng.gauss(0.0, 1.0) if t > 0 else 0.0)
    return xt


def normal_quantile_grid(count):
    dist = statistics.NormalDist()
    return [dist.inv_cdf((i + 0.5) / count) for i in range(count)]


def latent_compression(height, width, channels, factor, latent_channels):
    pixels = height * width * channels
    latents = (height // factor) * (width // factor) * latent_channels
    return {"pixels": pixels, "latents": latents, "ratio": pixels / latents,
            "latent_shape": [latent_channels, height // factor, width // factor]}


@functools.lru_cache(maxsize=None)
def diffusion_example():
    e = DIFFUSION_EXAMPLE
    T = e["steps"]
    linear = diffusion_linear_betas(T, e["beta_start"], e["beta_end"])
    cosine = diffusion_cosine_betas(T, e["cosine_offset"])
    ab_lin, ab_cos = diffusion_alpha_bars(linear), diffusion_alpha_bars(cosine)
    schedule = []
    for t in e["checkpoints"]:
        a, c = ab_lin[t - 1], ab_cos[t - 1]
        schedule.append({
            "t": t, "beta": linear[t - 1], "linear": a, "cosine": c,
            "snr_linear": a / (1 - a), "snr_cosine": c / (1 - c),
            "xt": diffusion_forward(e["x0"], e["eps"], a),
            "weight": diffusion_elbo_weight(t - 1, linear, ab_lin, linear[t - 1]) if t > 1 else None,
        })
    mean, var = diffusion_iterated_moments(linear, e["x0"])
    t_mid = 499
    xt_mid = diffusion_forward(e["x0"], e["eps"], ab_lin[t_mid])
    post = diffusion_posterior(e["x0"], xt_mid, t_mid, linear, ab_lin)
    eps_mean = diffusion_eps_mean(xt_mid, e["eps"], t_mid, linear, ab_lin)
    denoise = []
    for t in (999, 749, 499, 249, 99):
        x0_hat, eps_hat = two_point_denoiser(0.5, ab_lin[t])
        denoise.append({"t": t + 1, "alpha_bar": ab_lin[t], "x0_hat": x0_hat, "eps_hat": eps_hat})
    ddim = []
    for count in e["ddim_steps"]:
        ts = ddim_timesteps(T, count)
        paths = [ddim_sample(x, ab_lin, ts, two_point_eps) for x in e["ddim_starts"]]
        ddim.append({"count": count, "timesteps": ts, "paths": paths})
    grid = normal_quantile_grid(e["grid"])
    ts50 = ddim_timesteps(T, 50)
    guidance = []
    for w in e["guidance"]:
        finals = [ddim_sample(x, ab_lin, ts50, lambda xt, ab, w=w: guided_eps(xt, ab, e["prior_plus"], w))[-1] for x in grid]
        plus = sum(1 for v in finals if v > 0) / len(finals)
        guidance.append({"weight": w, "scale": 1 + w, "plus": plus, "mean": sum(finals) / len(finals),
                         "max_abs": max(abs(v) for v in finals),
                         "tilt": guidance_tilt(e["prior_plus"], 0.5, w)})
    rng = random.Random(e["ddpm_seed"])
    samples = [ddpm_sample(rng.gauss(0.0, 1.0), linear, ab_lin, two_point_eps, rng) for _ in range(e["ddpm_samples"])]
    plus = [v for v in samples if v > 0]
    ddpm = {"count": len(samples), "plus": len(plus) / len(samples),
            "max_error": max(abs(abs(v) - 1) for v in samples)}
    return {
        "example": e,
        "schedule": schedule,
        "curve": [{"t": t, "linear": ab_lin[t - 1] if t else 1.0, "cosine": ab_cos[t - 1] if t else 1.0}
                  for t in range(0, T + 1, 25)],
        "iterated": {"mean": mean, "variance": var, "closed_mean": math.sqrt(ab_lin[-1]) * e["x0"], "closed_variance": 1 - ab_lin[-1]},
        "posterior": {"t": t_mid + 1, "xt": xt_mid, "eps_mean": eps_mean, **post},
        "denoise": denoise,
        "ddim": ddim,
        "guidance": guidance,
        "ddpm": ddpm,
        "latent": latent_compression(**e["latent"]),
    }


PRETRAINING_EXAMPLE = {
    "sentence": "Thank you for inviting me to your party last week .",
    "spans": [[2, 4], [8, 9]],
    "sentinels": ["<X>", "<Y>", "<Z>"],
    "mlm": {"length": 512, "rate": 0.15, "split": [0.8, 0.1, 0.1]},
    "model": {"layers": 32, "d_model": 4096, "vocab": 32000, "context": 4096},
    "linear": {"tokens": 4096, "fan_in": 4096, "fan_out": 16384},
    "kaplan": {"alpha_n": 0.076, "n_c": 8.8e13, "alpha_d": 0.095, "d_c": 5.4e13, "n_exponent": 0.73},
    "chinchilla": {"e": 1.69, "a": 406.4, "b": 410.7, "alpha": 0.34, "beta": 0.28},
    "trained": [["Chinchilla", 70e9, 1.4e12], ["Gopher", 280e9, 300e9]],
    "budgets": [1e20, 1e21, 1e22, 1e23, 1e24, 1e25],
    "isoflop_budgets": [1e21, 1e22, 1e23, 1e24],
    "tokens_per_param": 20,
    "gpu": {"peak": 989e12, "mfu": 0.4, "count": 1000},
    "mixture": [["Web", 3.0e12, 0.70], ["Code", 4.0e11, 0.14], ["Books", 6.0e10, 0.06],
                ["Papers", 5.0e10, 0.05], ["Wikipedia", 2.0e10, 0.05]],
    "docs": [
        "the cat sat on the mat and looked out of the window at the rain",
        "the cat sat on the mat and looked out of the window at the snow",
        "a dog ran across the park chasing a red ball in the sun",
    ],
    "shingle": 3,
    "hashes": 128,
    "bands": 16,
    "similarities": [0.3, 0.5, 0.7, 0.8, 0.9],
    "per_token": [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99],
    "answer_tokens": 10,
}


def span_corrupt(tokens, spans, sentinels):
    inputs, targets, prev = [], [], 0
    for k, (start, end) in enumerate(spans):
        inputs += tokens[prev:start] + [sentinels[k]]
        targets += [sentinels[k]] + tokens[start:end]
        prev = end
    inputs += tokens[prev:]
    targets.append(sentinels[len(spans)])
    return inputs, targets


def mlm_counts(length, rate, split):
    chosen = length * rate
    return {"chosen": chosen, "mask": chosen * split[0], "random": chosen * split[1], "kept": chosen * split[2]}


def linear_layer_flops(tokens, fan_in, fan_out):
    mac = tokens * fan_in * fan_out
    return {"params": fan_in * fan_out, "forward": 2 * mac, "grad_input": 2 * mac, "grad_weight": 2 * mac,
            "total": 6 * mac, "per_param_token": 6 * mac / (tokens * fan_in * fan_out)}


def transformer_params(layers, d_model, vocab):
    return {"attention": 4 * d_model ** 2, "mlp": 8 * d_model ** 2, "per_layer": 12 * d_model ** 2,
            "non_embedding": 12 * layers * d_model ** 2, "embedding": vocab * d_model}


def kaplan_forward_flops(non_embedding, layers, context, d_model):
    weights, attention = 2 * non_embedding, 2 * layers * context * d_model
    return {"weights": weights, "attention": attention, "total": weights + attention,
            "attention_share": attention / (weights + attention)}


def kaplan_loss_n(n, k):
    return (k["n_c"] / n) ** k["alpha_n"]


def kaplan_loss_d(d, k):
    return (k["d_c"] / d) ** k["alpha_d"]


def chinchilla_loss(n, d, c):
    return c["e"] + c["a"] / n ** c["alpha"] + c["b"] / d ** c["beta"]


def chinchilla_optimal(compute, c):
    a = c["beta"] / (c["alpha"] + c["beta"])
    b = c["alpha"] / (c["alpha"] + c["beta"])
    g = (c["alpha"] * c["a"] / (c["beta"] * c["b"])) ** (1 / (c["alpha"] + c["beta"]))
    n = g * (compute / 6) ** a
    d = (compute / 6) ** b / g
    return {"n": n, "d": d, "a": a, "b": b, "ratio": d / n, "loss": chinchilla_loss(n, d, c)}


def tokens_per_param_split(compute, ratio):
    n = math.sqrt(compute / (6 * ratio))
    return {"n": n, "d": ratio * n}


def training_days(compute, peak, mfu, count):
    return compute / (peak * mfu * count) / 86400


def mixture_epochs(sources, budget):
    return [{"name": name, "size": size, "weight": weight, "tokens": weight * budget,
             "epochs": weight * budget / size} for name, size, weight in sources]


def word_shingles(text, k):
    words = text.split()
    return {" ".join(words[i:i + k]) for i in range(len(words) - k + 1)}


def jaccard(a, b):
    return len(a & b) / len(a | b)


def minhash_signature(shingles, count):
    return [min(int.from_bytes(hashlib.blake2b(f"{i}:{s}".encode(), digest_size=8).digest(), "big")
                for s in shingles) for i in range(count)]


def minhash_estimate(sig_a, sig_b):
    return sum(1 for x, y in zip(sig_a, sig_b) if x == y) / len(sig_a)


def lsh_candidate_probability(similarity, bands, rows):
    return 1 - (1 - similarity ** rows) ** bands


@functools.lru_cache(maxsize=None)
def pretraining_example():
    e = PRETRAINING_EXAMPLE
    tokens = e["sentence"].split()
    inputs, targets = span_corrupt(tokens, e["spans"], e["sentinels"])
    m = e["model"]
    params = transformer_params(m["layers"], m["d_model"], m["vocab"])
    forward = kaplan_forward_flops(params["non_embedding"], m["layers"], m["context"], m["d_model"])
    k, c = e["kaplan"], e["chinchilla"]
    trained = []
    for name, n, d in e["trained"]:
        compute = 6 * n * d
        trained.append({"name": name, "n": n, "log_n": math.log10(n), "d": d, "compute": compute, "ratio": d / n,
                        "loss": chinchilla_loss(n, d, c), "optimal": chinchilla_optimal(compute, c),
                        "rule": tokens_per_param_split(compute, e["tokens_per_param"])})
    budgets = [{"compute": b, "optimal": chinchilla_optimal(b, c),
                "rule": tokens_per_param_split(b, e["tokens_per_param"])} for b in e["budgets"]]
    shingles = [word_shingles(d, e["shingle"]) for d in e["docs"]]
    sigs = [minhash_signature(s, e["hashes"]) for s in shingles]
    rows = e["hashes"] // e["bands"]
    pairs = [{"pair": [i, j], "exact": jaccard(shingles[i], shingles[j]), "estimate": minhash_estimate(sigs[i], sigs[j]),
              "candidate": lsh_candidate_probability(jaccard(shingles[i], shingles[j]), e["bands"], rows)}
             for i, j in itertools.combinations(range(len(shingles)), 2)]
    g = e["gpu"]
    return {
        "example": e,
        "tokens": tokens,
        "span": {"inputs": inputs, "targets": targets, "corrupted": sum(b - a for a, b in e["spans"])},
        "causal_targets": len(tokens) - 1,
        "mlm": mlm_counts(**e["mlm"]),
        "linear": linear_layer_flops(**e["linear"]),
        "params": params,
        "forward": forward,
        "kaplan": {"double_n": 2 ** -k["alpha_n"], "double_d": 2 ** -k["alpha_d"],
                   "loss_n": kaplan_loss_n(params["non_embedding"], k),
                   "tenfold_n": 10 ** k["n_exponent"], "tenfold_d": 10 ** (1 - k["n_exponent"])},
        "chinchilla": {"tenfold_n": 10 ** (c["beta"] / (c["alpha"] + c["beta"])),
                       "tenfold_d": 10 ** (c["alpha"] / (c["alpha"] + c["beta"]))},
        "trained": trained,
        "budgets": budgets,
        "isoflop": [{"compute": b, "optimal": chinchilla_optimal(b, c),
                     "points": [{"n": n, "log_n": math.log10(n), "loss": chinchilla_loss(n, b / (6 * n), c)}
                                for n in (chinchilla_optimal(b, c)["n"] * 10 ** (x / 10) for x in range(-12, 13))]}
                    for b in e["isoflop_budgets"]],
        "days": training_days(trained[0]["compute"], g["peak"], g["mfu"], g["count"]),
        "mixture": mixture_epochs(e["mixture"], e["trained"][0][2]),
        "shingles": [len(s) for s in shingles],
        "rows": rows,
        "threshold": (1 / e["bands"]) ** (1 / rows),
        "pairs": pairs,
        "curve": [{"s": s, "p": lsh_candidate_probability(s, e["bands"], rows)} for s in e["similarities"]],
        "emergence": [{"per_token": p, "exact": p ** e["answer_tokens"]} for p in e["per_token"]],
    }


COLLAB_EXAMPLE = {
    "users": ["Ana", "Ben", "Cai", "Dee", "Eli"],
    "items": ["Heist", "Caper", "Sting", "Drift", "Haunt"],
    "ratings": (
        (5, 4, None, 1, 1),
        (4, None, 4, 1, 2),
        (1, 1, 2, 5, None),
        (None, 2, 1, 4, 5),
        (5, 5, 4, None, 1),
    ),
    "held_out": ((1, 1, 5), (3, 0, 1)),
    "neighbours": 2,
    "rank": 2,
    "l2": 0.1,
    "sweeps": 20,
    "seed": 0,
    "nmf_steps": 300,
    "implicit_counts": [0, 1, 3, 10],
    "implicit_alpha": 40,
    "scale": {"users": 1_000_000, "items": 100_000, "rank": 64},
}


def cf_observed(ratings):
    return [(u, i, r) for u, row in enumerate(ratings) for i, r in enumerate(row) if r is not None]


def cf_user_mean(ratings, u):
    values = [r for r in ratings[u] if r is not None]
    return sum(values) / len(values)


def cf_centered_cosine(ratings, u, v):
    mu, mv = cf_user_mean(ratings, u), cf_user_mean(ratings, v)
    common = [i for i, (a, b) in enumerate(zip(ratings[u], ratings[v])) if a is not None and b is not None]
    a = [ratings[u][i] - mu for i in common]
    b = [ratings[v][i] - mv for i in common]
    na, nb = math.sqrt(dot_product(a, a)), math.sqrt(dot_product(b, b))
    if na == 0 or nb == 0:
        return 0.0
    return dot_product(a, b) / (na * nb)


def cf_neighbour_predict(ratings, u, i, k):
    candidates = sorted(
        ((cf_centered_cosine(ratings, u, v), v) for v in range(len(ratings))
         if v != u and ratings[v][i] is not None),
        key=lambda t: -t[0],
    )
    top = [(s, v) for s, v in candidates if s > 0][:k]
    base = cf_user_mean(ratings, u)
    weight = sum(s for s, _ in top)
    if weight == 0:
        return {"prediction": base, "neighbours": top, "base": base}
    lift = sum(s * (ratings[v][i] - cf_user_mean(ratings, v)) for s, v in top) / weight
    return {"prediction": base + lift, "neighbours": top, "base": base}


def cf_baseline(ratings):
    observed = cf_observed(ratings)
    mu = sum(r for _, _, r in observed) / len(observed)
    user_bias = [cf_user_mean(ratings, u) - mu for u in range(len(ratings))]
    item_bias = []
    for i in range(len(ratings[0])):
        column = [row[i] for row in ratings if row[i] is not None]
        item_bias.append(sum(column) / len(column) - mu if column else 0.0)
    return {"mu": mu, "user_bias": user_bias, "item_bias": item_bias}


def cf_als(ratings, rank, l2, sweeps, seed):
    rng = random.Random(seed)
    users = [[rng.gauss(0, 0.5) for _ in range(rank)] for _ in ratings]
    items = [[rng.gauss(0, 0.5) for _ in range(rank)] for _ in ratings[0]]
    observed = cf_observed(ratings)
    history = []
    for _ in range(sweeps):
        for u in range(len(users)):
            seen = [(i, r) for v, i, r in observed if v == u]
            users[u] = ridge_coefficients([items[i] for i, _ in seen], [r for _, r in seen], l2)
        for i in range(len(items)):
            seen = [(u, r) for u, j, r in observed if j == i]
            items[i] = ridge_coefficients([users[u] for u, _ in seen], [r for _, r in seen], l2)
        sse = sum((dot_product(users[u], items[i]) - r) ** 2 for u, i, r in observed)
        penalty = l2 * sum(dot_product(x, x) for x in users + items)
        history.append({"rmse": math.sqrt(sse / len(observed)), "objective": sse + penalty})
    return {"users": users, "items": items, "history": history}


def cf_nmf_multiplicative(matrix, rank, steps, seed):
    rng = random.Random(seed)
    n, m = len(matrix), len(matrix[0])
    w = [[rng.random() for _ in range(rank)] for _ in range(n)]
    h = [[rng.random() for _ in range(m)] for _ in range(rank)]

    def product():
        return [[sum(w[a][k] * h[k][b] for k in range(rank)) for b in range(m)] for a in range(n)]

    for _ in range(steps):
        wh = product()
        for k in range(rank):
            for b in range(m):
                h[k][b] *= (sum(w[a][k] * matrix[a][b] for a in range(n))
                            / sum(w[a][k] * wh[a][b] for a in range(n)))
        wh = product()
        for a in range(n):
            for k in range(rank):
                w[a][k] *= (sum(matrix[a][b] * h[k][b] for b in range(m))
                            / sum(wh[a][b] * h[k][b] for b in range(m)))
    return {"w": w, "h": h, "reconstruction": product()}


def implicit_confidence(counts, alpha):
    return [{"count": c, "preference": 1 if c > 0 else 0, "confidence": 1 + alpha * c} for c in counts]


@functools.lru_cache(maxsize=None)
def collab_example():
    e = COLLAB_EXAMPLE
    ratings = e["ratings"]
    baseline = cf_baseline(ratings)
    als = cf_als(ratings, e["rank"], e["l2"], e["sweeps"], e["seed"])
    zero_filled = [[0 if r is None else r for r in row] for row in ratings]
    nmf = cf_nmf_multiplicative(zero_filled, e["rank"], e["nmf_steps"], e["seed"])
    targets = []
    for u, i, truth in e["held_out"]:
        neighbour = cf_neighbour_predict(ratings, u, i, e["neighbours"])
        targets.append({
            "user": u,
            "item": i,
            "truth": truth,
            "global": baseline["mu"],
            "baseline": baseline["mu"] + baseline["user_bias"][u] + baseline["item_bias"][i],
            "neighbour": neighbour,
            "als": dot_product(als["users"][u], als["items"][i]),
            "nmf": nmf["reconstruction"][u][i],
        })
    methods = ["global", "baseline", "neighbour", "als", "nmf"]
    heldout_rmse = {}
    for name in methods:
        errors = [(t[name]["prediction"] if name == "neighbour" else t[name]) - t["truth"] for t in targets]
        heldout_rmse[name] = math.sqrt(sum(x * x for x in errors) / len(errors))
    nmf_observed_rmse = math.sqrt(sum(
        (nmf["reconstruction"][u][i] - r) ** 2 for u, i, r in cf_observed(ratings)
    ) / len(cf_observed(ratings)))
    cold_order = sorted(range(len(ratings[0])), key=lambda i: -baseline["item_bias"][i])
    s = e["scale"]
    return {
        "names": e["users"],
        "titles": e["items"],
        "ratings": ratings,
        "observed": len(cf_observed(ratings)),
        "cells": len(ratings) * len(ratings[0]),
        "similarity": [[cf_centered_cosine(ratings, u, v) for v in range(len(ratings))]
                       for u in range(len(ratings))],
        "user_means": [cf_user_mean(ratings, u) for u in range(len(ratings))],
        "baseline": baseline,
        "als": als,
        "als_params": (len(ratings) + len(ratings[0])) * e["rank"],
        "nmf": nmf,
        "nmf_observed_rmse": nmf_observed_rmse,
        "targets": targets,
        "heldout_rmse": heldout_rmse,
        "implicit": implicit_confidence(e["implicit_counts"], e["implicit_alpha"]),
        "cold_order": cold_order,
        "scale_cells": s["users"] * s["items"],
        "scale_params": (s["users"] + s["items"]) * s["rank"],
        "scale_bytes": (s["users"] + s["items"]) * s["rank"] * 4,
    }


GRAD_ACCUM_EXAMPLE = {
    "params": (0.5, 0.0),
    "sequences": (
        ((1.0, 2.2), (2.0, 4.1)),
        ((3.0, 5.8), (1.0, 1.9), (2.0, 4.3), (4.0, 8.2), (0.5, 0.9), (3.0, 6.1)),
        ((2.0, 3.8),),
        ((1.0, 2.0), (4.0, 7.9), (2.5, 5.2)),
        ((3.5, 7.1), (1.5, 2.8), (2.0, 4.0), (0.5, 1.2), (3.0, 5.9)),
        ((1.0, 2.3), (2.0, 3.9)),
        ((4.0, 8.1), (2.0, 4.2), (1.0, 1.8), (3.0, 6.0)),
        ((2.5, 4.9),),
    ),
    "micro_batch": 2,
    "max_norm": 10.0,
    "bn_feature": (1.0, 3.0, 2.0, 6.0, 4.0, 0.0, 5.0, 3.0),
    "bn_momentum": 0.1,
    "ddp": {"params": 1.3e9, "bytes": 4, "world": 8, "accum": 8, "micro_batch": 4, "seq_len": 2048},
}


def ga_token_grad(params, token):
    w, b = params
    x, y = token
    err = w * x + b - y
    return 0.5 * err * err, (err * x, err)


def ga_sum(params, sequences):
    loss, gw, gb, count = 0.0, 0.0, 0.0, 0
    for seq in sequences:
        for token in seq:
            l, (dw, db) = ga_token_grad(params, token)
            loss, gw, gb, count = loss + l, gw + dw, gb + db, count + 1
    return {"loss": loss, "grad": (gw, gb), "tokens": count}


def ga_micro_batches(sequences, size):
    return [sequences[i:i + size] for i in range(0, len(sequences), size)]


def ga_accumulate(params, sequences, size, normalize):
    micro = ga_micro_batches(sequences, size)
    total_tokens = sum(len(seq) for seq in sequences)
    loss, gw, gb, rows = 0.0, 0.0, 0.0, []
    for batch in micro:
        part = ga_sum(params, batch)
        if normalize == "per_micro_mean":
            scale = 1 / (part["tokens"] * len(micro))
        elif normalize == "total_tokens":
            scale = 1 / total_tokens
        elif normalize == "none":
            scale = 1 / part["tokens"]
        else:
            raise ValueError(normalize)
        loss += part["loss"] * scale
        gw += part["grad"][0] * scale
        gb += part["grad"][1] * scale
        rows.append({"tokens": part["tokens"], "scale": scale,
                     "grad": (part["grad"][0] * scale, part["grad"][1] * scale)})
    return {"loss": loss, "grad": (gw, gb), "micro": rows}


def ga_clip_comparison(params, sequences, size, max_norm):
    acc = ga_accumulate(params, sequences, size, "total_tokens")
    after = clip_by_global_norm(list(acc["grad"]), max_norm)
    gw, gb = 0.0, 0.0
    each = []
    for row in acc["micro"]:
        k = len(acc["micro"])
        clipped = clip_by_global_norm([g * k for g in row["grad"]], max_norm)
        each.append(clipped)
        gw += clipped["grads"][0] / k
        gb += clipped["grads"][1] / k
    return {"after": after, "per_micro": each, "per_micro_grad": (gw, gb)}


def ga_batch_norm_stats(feature, size, momentum):
    full = {"mean": _mean(feature), "var": _variance(feature)}
    micro = []
    for i in range(0, len(feature), size):
        chunk = feature[i:i + size]
        micro.append({"values": list(chunk), "mean": _mean(chunk), "var": _variance(chunk)})
    running_once = running_stats_update(0.0, 1.0, list(feature), momentum)
    mean, var = 0.0, 1.0
    for row in micro:
        mean, var = running_stats_update(mean, var, row["values"], momentum)
    return {
        "full": full,
        "micro": micro,
        "running_once": running_once,
        "running_micro": (mean, var),
        "effective_momentum": 1 - (1 - momentum) ** len(micro),
    }


def ga_allreduce_bytes(params, bytes_per, world, accum, no_sync):
    payload = params * bytes_per
    per_reduce = 2 * (world - 1) / world * payload
    reduces = 1 if no_sync else accum
    return {"payload": payload, "per_reduce": per_reduce, "reduces": reduces, "total": per_reduce * reduces}


@functools.lru_cache(maxsize=None)
def accumulation_example():
    e = GRAD_ACCUM_EXAMPLE
    params, seqs, size = e["params"], e["sequences"], e["micro_batch"]
    full = ga_sum(params, seqs)
    full_mean = {"loss": full["loss"] / full["tokens"],
                 "grad": tuple(g / full["tokens"] for g in full["grad"]), "tokens": full["tokens"]}
    d = e["ddp"]
    return {
        "sequences": seqs,
        "lengths": [len(s) for s in seqs],
        "full": full_mean,
        "naive": ga_accumulate(params, seqs, size, "per_micro_mean"),
        "exact": ga_accumulate(params, seqs, size, "total_tokens"),
        "unscaled": ga_accumulate(params, seqs, size, "none"),
        "clip": ga_clip_comparison(params, seqs, size, e["max_norm"]),
        "bn": ga_batch_norm_stats(e["bn_feature"], size, e["bn_momentum"]),
        "ddp_every": ga_allreduce_bytes(d["params"], d["bytes"], d["world"], d["accum"], False),
        "ddp_no_sync": ga_allreduce_bytes(d["params"], d["bytes"], d["world"], d["accum"], True),
        "global_batch": d["micro_batch"] * d["accum"] * d["world"],
        "global_tokens": d["micro_batch"] * d["accum"] * d["world"] * d["seq_len"],
    }


LATENCY_EXAMPLE = {
    "params": 8e9,
    "bytes_per_param": 2,
    "d_model": 4096,
    "gpu": {"flops": 989e12, "bandwidth": 3.35e12, "memory": 80e9},
    "context": 2048,
    "prompt": 1024,
    "output": 256,
    "batches": (1, 8, 32, 64, 128, 192),
    "rates": (5, 10, 20, 30, 40),
    "queue": {"service_ms": 10.0, "utilizations": (0.5, 0.8, 0.9, 0.95), "requests": 20000, "seed": 7},
    "fanout": {"p_slow": 0.01, "widths": (1, 10, 100)},
}


def lt_kv_bytes_per_token():
    return kv_cache_bytes_per_token(KV_CONFIG["layers"], KV_CONFIG["kv_heads"], KV_CONFIG["head_dim"],
                                    KV_CONFIG["bytes_per_value"])


def lt_decode_step(batch, context):
    e, gpu = LATENCY_EXAMPLE, LATENCY_EXAMPLE["gpu"]
    weights = e["params"] * e["bytes_per_param"]
    kv = batch * context * lt_kv_bytes_per_token()
    flops = batch * (2 * e["params"] + 4 * KV_CONFIG["layers"] * e["d_model"] * context)
    memory_s = (weights + kv) / gpu["bandwidth"]
    compute_s = flops / gpu["flops"]
    seconds = max(memory_s, compute_s)
    return {
        "batch": batch,
        "weight_bytes": weights,
        "kv_bytes": kv,
        "flops": flops,
        "intensity": flops / (weights + kv),
        "memory_ms": 1000 * memory_s,
        "compute_ms": 1000 * compute_s,
        "itl_ms": 1000 * seconds,
        "bound": "memory" if memory_s >= compute_s else "compute",
        "tokens_per_s": batch / seconds,
        "fits": weights + kv <= gpu["memory"],
    }


def lt_prefill(prompt):
    e, gpu = LATENCY_EXAMPLE, LATENCY_EXAMPLE["gpu"]
    flops = 2 * e["params"] * prompt + 2 * KV_CONFIG["layers"] * e["d_model"] * prompt * prompt
    bytes_moved = e["params"] * e["bytes_per_param"] + prompt * lt_kv_bytes_per_token()
    memory_s = bytes_moved / gpu["bandwidth"]
    compute_s = flops / gpu["flops"]
    return {
        "flops": flops,
        "bytes": bytes_moved,
        "intensity": flops / bytes_moved,
        "memory_ms": 1000 * memory_s,
        "compute_ms": 1000 * compute_s,
        "ms": 1000 * max(memory_s, compute_s),
        "bound": "memory" if memory_s >= compute_s else "compute",
    }


def lt_max_batch(context):
    e, gpu = LATENCY_EXAMPLE, LATENCY_EXAMPLE["gpu"]
    return int((gpu["memory"] - e["params"] * e["bytes_per_param"]) // (context * lt_kv_bytes_per_token()))


def lt_little_fixed_point(rate, context, prompt, output, max_batch, rounds=200):
    prefill_s = lt_prefill(prompt)["ms"] / 1000
    decode_share = 1 - rate * prefill_s
    if decode_share <= 0:
        return {"rate": rate, "stable": False}
    concurrency = 1.0
    for _ in range(rounds):
        itl = lt_decode_step(concurrency, context)["itl_ms"] / 1000 / decode_share
        latency = prefill_s + (output - 1) * itl
        following = rate * latency
        if following > max_batch:
            return {"rate": rate, "stable": False}
        if abs(following - concurrency) < 1e-9:
            break
        concurrency = following
    return {
        "rate": rate,
        "stable": True,
        "concurrency": concurrency,
        "itl_ms": 1000 * itl,
        "latency_s": latency,
        "tokens_per_s": rate * output,
    }


def lt_queue_latencies(service_ms, utilization, requests, seed):
    rng = random.Random(seed)
    mean_gap = service_ms / utilization
    wait, latencies = 0.0, []
    for _ in range(requests):
        latencies.append(wait + service_ms)
        wait = max(0.0, wait + service_ms - rng.expovariate(1 / mean_gap))
    return latencies


def lt_queue_summary(service_ms, utilization, requests, seed):
    latencies = lt_queue_latencies(service_ms, utilization, requests, seed)
    return {
        "utilization": utilization,
        "mean_ms": sum(latencies) / len(latencies),
        "theory_mean_ms": service_ms + utilization * service_ms / (2 * (1 - utilization)),
        "p50_ms": nearest_rank(latencies, 0.5),
        "p99_ms": nearest_rank(latencies, 0.99),
    }


def lt_fanout_slow(p_slow, width):
    return 1 - (1 - p_slow) ** width


def lt_roofline_xy(intensity, flops_per_s, width=620, height=180, max_intensity=3000):
    x = 60 + width * math.log10(intensity) / math.log10(max_intensity)
    y = 200 - height * (math.log10(flops_per_s) - 12) / 3
    return round(x, 1), round(y, 1)


@functools.lru_cache(maxsize=None)
def latency_example():
    e = LATENCY_EXAMPLE
    q = e["queue"]
    max_batch = lt_max_batch(e["context"])
    prefill = lt_prefill(e["prompt"])
    decode = [lt_decode_step(b, e["context"]) for b in e["batches"]]
    single = decode[0]
    return {
        "example": e,
        "kv_bytes_per_token": lt_kv_bytes_per_token(),
        "ridge": e["gpu"]["flops"] / e["gpu"]["bandwidth"],
        "prefill": prefill,
        "decode": decode,
        "max_batch": max_batch,
        "single_request_s": (prefill["ms"] + (e["output"] - 1) * single["itl_ms"]) / 1000,
        "little": [lt_little_fixed_point(r, e["context"], e["prompt"], e["output"], max_batch) for r in e["rates"]],
        "queue": [lt_queue_summary(q["service_ms"], u, q["requests"], q["seed"]) for u in q["utilizations"]],
        "fanout": [{"width": w, "slow": lt_fanout_slow(e["fanout"]["p_slow"], w)} for w in e["fanout"]["widths"]],
        "roofline": [
            dict(zip(("x", "y"), lt_roofline_xy(p["intensity"], p["flops"] / (p["ms"] / 1000))),
                 label=p["label"], intensity=p["intensity"], tflops=p["flops"] / (p["ms"] / 1000) / 1e12)
            for p in [{"label": f"B={d['batch']}", "intensity": d["intensity"], "flops": d["flops"], "ms": d["itl_ms"]}
                      for d in decode] + [{"label": "prefill", "intensity": prefill["intensity"],
                                           "flops": prefill["flops"], "ms": prefill["ms"]}]
        ],
        "max_stable_rate": max(r for r in range(1, 60)
                               if lt_little_fixed_point(r, e["context"], e["prompt"], e["output"], max_batch)["stable"]),
    }


ONLINE_EXAMPLE = {
    "stream": {"n": 400, "drift_at": 200, "w_before": 2.0, "w_after": -1.0, "noise": 0.3, "seed": 11, "window": 50},
    "frozen_after": 100,
    "constant_eta": 0.1,
    "decay_eta0": 0.5,
    "regret": {"eta0": 0.5, "checkpoints": [10, 25, 50, 100, 200]},
    "bandit": {"probs": [0.25, 0.45, 0.55], "steps": 1000, "runs": 50, "seed": 5, "epsilon": 0.1,
               "checkpoints": [10, 50, 100, 250, 500, 1000], "every": 50},
}


def ol_stream(n, drift_at, w_before, w_after, noise, seed):
    rng = random.Random(seed)
    stream = []
    for t in range(n):
        x = rng.uniform(-1.0, 1.0)
        w = w_before if t < drift_at else w_after
        stream.append((x, w * x + rng.gauss(0.0, noise)))
    return stream


def ol_least_squares_weight(points):
    return sum(x * y for x, y in points) / sum(x * x for x, _ in points)


def ol_prequential(stream, eta, w=0.0, frozen=False):
    weights, losses, steps = [], [], []
    for t, (x, y) in enumerate(stream, start=1):
        prediction = w * x
        loss = (prediction - y) ** 2
        losses.append(loss)
        step = eta(t) if callable(eta) else eta
        if not frozen:
            gradient = 2 * (prediction - y) * x
            w = w - step * gradient
        weights.append(w)
        steps.append(step)
    return {"weights": weights, "losses": losses, "steps": steps}


def ol_window_means(values, window):
    return [sum(values[i:i + window]) / window for i in range(0, len(values) - window + 1, window)]


def ol_regret(stream, eta0, checkpoints):
    run = ol_prequential(stream, lambda t: eta0 / math.sqrt(t))
    rows = []
    for T in checkpoints:
        head = stream[:T]
        best = ol_least_squares_weight(head)
        best_loss = sum((best * x - y) ** 2 for x, y in head)
        learner_loss = sum(run["losses"][:T])
        regret = learner_loss - best_loss
        rows.append({"T": T, "best_w": best, "learner_loss": learner_loss, "best_loss": best_loss,
                     "regret": regret, "per_step": regret / T, "per_sqrt": regret / math.sqrt(T)})
    return rows


def ol_bandit_choose(policy, t, counts, successes, rng, epsilon):
    k = len(counts)
    if policy == "thompson":
        draws = [rng.betavariate(1 + successes[a], 1 + counts[a] - successes[a]) for a in range(k)]
        return max(range(k), key=lambda a: draws[a])
    for a in range(k):
        if counts[a] == 0:
            return a
    means = [successes[a] / counts[a] for a in range(k)]
    if policy == "epsilon" and rng.random() < epsilon:
        return rng.randrange(k)
    if policy == "ucb":
        scores = [means[a] + math.sqrt(2 * math.log(t) / counts[a]) for a in range(k)]
        return max(range(k), key=lambda a: scores[a])
    return max(range(k), key=lambda a: means[a])


def ol_bandit_run(policy, probs, steps, seed, epsilon, trace=0):
    reward_rng = random.Random(seed)
    rewards = [[reward_rng.random() < p for p in probs] for _ in range(steps)]
    rng = random.Random(seed * 7919 + 1)
    k = len(probs)
    counts, successes = [0] * k, [0] * k
    best = max(probs)
    regret, curve, rows = 0.0, [], []
    for t in range(1, steps + 1):
        before_counts, before_successes = counts[:], successes[:]
        arm = ol_bandit_choose(policy, t, counts, successes, rng, epsilon)
        reward = rewards[t - 1][arm]
        counts[arm] += 1
        successes[arm] += reward
        regret += best - probs[arm]
        curve.append(regret)
        if t <= trace:
            rows.append({"t": t, "counts": before_counts, "successes": before_successes, "arm": arm,
                         "reward": int(reward),
                         "ucb": [None if before_counts[a] == 0 else
                                 before_successes[a] / before_counts[a] + math.sqrt(2 * math.log(t) / before_counts[a])
                                 for a in range(k)]})
    return {"curve": curve, "counts": counts, "successes": successes, "trace": rows}


def ol_bandit_average(policy, probs, steps, runs, seed, epsilon):
    total = [0.0] * steps
    best_share = 0.0
    best_arm = probs.index(max(probs))
    for r in range(runs):
        run = ol_bandit_run(policy, probs, steps, seed + r, epsilon)
        for i, value in enumerate(run["curve"]):
            total[i] += value
        best_share += run["counts"][best_arm] / steps
    return {"curve": [value / runs for value in total], "best_share": best_share / runs}


def ol_curve_xy(step, value, steps, top, x0=60, width=600, y0=200, height=170):
    return round(x0 + width * step / steps, 1), round(y0 - height * min(value, top) / top, 1)


@functools.lru_cache(maxsize=None)
def online_example():
    e = ONLINE_EXAMPLE
    s = e["stream"]
    stream = ol_stream(s["n"], s["drift_at"], s["w_before"], s["w_after"], s["noise"], s["seed"])
    frozen_w = ol_least_squares_weight(stream[:e["frozen_after"]])
    learners = {
        "frozen": ol_prequential(stream, 0.0, w=frozen_w, frozen=True),
        "decay": ol_prequential(stream, lambda t: e["decay_eta0"] / t),
        "constant": ol_prequential(stream, e["constant_eta"]),
    }
    windows = {name: ol_window_means(run["losses"], s["window"]) for name, run in learners.items()}
    b = e["bandit"]
    policies = ["greedy", "epsilon", "ucb", "thompson"]
    bandits = {p: ol_bandit_average(p, b["probs"], b["steps"], b["runs"], b["seed"], b["epsilon"]) for p in policies}
    top = max(curve["curve"][-1] for curve in bandits.values())
    top = math.ceil(top / 10) * 10
    return {
        "example": e,
        "stream": stream,
        "frozen_w": frozen_w,
        "learners": learners,
        "windows": windows,
        "window_starts": list(range(0, s["n"], s["window"])),
        "first_steps": [{"t": t, "x": stream[t - 1][0], "y": stream[t - 1][1],
                         "w_before": 0.0 if t == 1 else learners["constant"]["weights"][t - 2],
                         "w_after": learners["constant"]["weights"][t - 1],
                         "loss": learners["constant"]["losses"][t - 1]} for t in (1, 2, 3)],
        "weights_at": {name: {t: run["weights"][t - 1] for t in (s["drift_at"], s["drift_at"] + 50, s["n"])}
                       for name, run in learners.items()},
        "regret": ol_regret(stream[:s["drift_at"]], e["regret"]["eta0"], e["regret"]["checkpoints"]),
        "bandits": bandits,
        "bandit_rows": [{"policy": p, "regret": {c: bandits[p]["curve"][c - 1] for c in b["checkpoints"]},
                         "best_share": bandits[p]["best_share"]} for p in policies],
        "bandit_top": top,
        "epsilon_floor": b["epsilon"] * sum(max(b["probs"]) - p for p in b["probs"]) / len(b["probs"]),
        "bandit_points": {p: [ol_curve_xy(t, bandits[p]["curve"][t - 1], b["steps"], top)
                              for t in [1] + list(range(b["every"], b["steps"] + 1, b["every"]))] for p in policies},
        "ucb_trace": ol_bandit_run("ucb", b["probs"], b["steps"], b["seed"], b["epsilon"], trace=7)["trace"],
        "thompson_run": ol_bandit_run("thompson", b["probs"], b["steps"], b["seed"], b["epsilon"]),
    }


UNCERTAINTY_EXAMPLE = {
    "data": {"n_train": 200, "n_cal": 200, "n_test": 2000, "lo": -3.0, "hi": 1.0,
             "noise_lo": 0.1, "noise_hi": 0.5, "seed": 3},
    "degree": 3,
    "members": 5,
    "probes": [-2.5, -1.0, 0.5, 2.0, 3.0],
    "plot": {"x_lo": -3.0, "x_hi": 3.0, "y_lo": -3.0, "y_hi": 2.0, "step": 0.1, "shown_points": 60},
    "bootstrap": {"n_test": 40, "resamples": 2000, "level": 0.95, "seed": 9},
    "dropout": {"hidden": [0.9, -0.4, 1.3, 0.2, -1.1, 0.7, 0.5, -0.8],
                "weights": [0.6, 0.3, -0.5, 0.8, 0.4, -0.7, 0.9, 0.2],
                "p": 0.2, "samples": [10, 100, 1000], "shown": 3, "seed": 4},
    "conformal": {"alpha": 0.1, "split_at": -1.0, "small_n": 9, "small_alpha": 0.2,
                  "repeats": 200, "repeat_test": 500, "seed": 21, "bins": [0.76 + 0.02 * i for i in range(10)]},
}


def unc_noise_sd(x, data):
    return data["noise_lo"] + (data["noise_hi"] - data["noise_lo"]) * (x - data["lo"]) / (data["hi"] - data["lo"])


def unc_sample(n, data, rng):
    points = []
    for _ in range(n):
        x = rng.uniform(data["lo"], data["hi"])
        points.append((x, math.sin(x) + rng.gauss(0.0, unc_noise_sd(x, data))))
    return points


def unc_poly(coef, x):
    return sum(c * x**k for k, c in enumerate(coef))


def unc_fit_member(points, degree):
    coef = _least_squares([[x**k for k in range(degree + 1)] for x, _ in points], [y for _, y in points])
    a, b = _least_squares([[1.0, x] for x, _ in points], [abs(y - unc_poly(coef, x)) for x, y in points])
    half_normal = math.sqrt(2 / math.pi)
    return {"mean": coef, "scale": (a / half_normal, b / half_normal)}


def unc_predict(member, x):
    a, b = member["scale"]
    return unc_poly(member["mean"], x), max(a + b * x, 1e-3)


def unc_ensemble(points, degree, members, rng):
    ensemble = []
    for _ in range(members):
        ensemble.append(unc_fit_member([points[rng.randrange(len(points))] for _ in points], degree))
    return ensemble


def unc_decompose(ensemble, x):
    predictions = [unc_predict(member, x) for member in ensemble]
    means = [mu for mu, _ in predictions]
    mean = sum(means) / len(means)
    aleatoric = sum(sd * sd for _, sd in predictions) / len(predictions)
    epistemic = sum((mu - mean) ** 2 for mu in means) / len(means)
    return {"x": x, "means": means, "sds": [sd for _, sd in predictions], "mean": mean, "truth": math.sin(x),
            "aleatoric": aleatoric, "epistemic": epistemic, "total": aleatoric + epistemic}


def unc_quantile(values, q):
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    lo = int(position)
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo)


def unc_bootstrap_ci(values, resamples, level, rng):
    n = len(values)
    stats = [sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(resamples)]
    mean = sum(values) / n
    se = math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1)) / math.sqrt(n)
    stats_mean = sum(stats) / resamples
    tail = (1 - level) / 2
    return {"mean": mean, "lo": unc_quantile(stats, tail), "hi": unc_quantile(stats, 1 - tail), "se": se,
            "boot_se": math.sqrt(sum((s - stats_mean) ** 2 for s in stats) / (resamples - 1)),
            "normal_lo": mean - 1.96 * se, "normal_hi": mean + 1.96 * se}


def unc_dropout_samples(hidden, weights, p, count, rng):
    outputs, masks = [], []
    for _ in range(count):
        mask = [0 if rng.random() < p else 1 for _ in hidden]
        masks.append(mask)
        outputs.append(sum(w * h * m / (1 - p) for w, h, m in zip(weights, hidden, mask)))
    return outputs, masks


def unc_dropout_variance(hidden, weights, p):
    return p / (1 - p) * sum((w * h) ** 2 for w, h in zip(weights, hidden))


def unc_conformal_rank(n, alpha):
    return math.ceil((n + 1) * (1 - alpha))


def unc_conformal_q(scores, alpha):
    k = unc_conformal_rank(len(scores), alpha)
    return sorted(scores)[k - 1] if k <= len(scores) else math.inf


def unc_coverage(model, points, q, normalized=False, split_at=None):
    hits = []
    for x, y in points:
        mu, sd = unc_predict(model, x)
        hits.append((x, abs(y - mu) <= q * (sd if normalized else 1.0)))
    result = {"all": sum(h for _, h in hits) / len(hits)}
    if split_at is not None:
        left = [h for x, h in hits if x < split_at]
        right = [h for x, h in hits if x >= split_at]
        result.update({"left": sum(left) / len(left), "right": sum(right) / len(right)})
    return result


def unc_xy(x, y, plot, x0=60, width=600, y0=200, height=170):
    y = min(max(y, plot["y_lo"]), plot["y_hi"])
    return (round(x0 + width * (x - plot["x_lo"]) / (plot["x_hi"] - plot["x_lo"]), 1),
            round(y0 - height * (y - plot["y_lo"]) / (plot["y_hi"] - plot["y_lo"]), 1))


@functools.lru_cache(maxsize=None)
def uncertainty_example():
    e = UNCERTAINTY_EXAMPLE
    data, plot, c, b, dr = e["data"], e["plot"], e["conformal"], e["bootstrap"], e["dropout"]
    rng = random.Random(data["seed"])
    train = unc_sample(data["n_train"], data, rng)
    cal = unc_sample(data["n_cal"], data, rng)
    test = unc_sample(data["n_test"], data, rng)
    model = unc_fit_member(train, e["degree"])
    ensemble = unc_ensemble(train, e["degree"], e["members"], random.Random(data["seed"] + 1))
    grid = [round(plot["x_lo"] + plot["step"] * i, 10)
            for i in range(int(round((plot["x_hi"] - plot["x_lo"]) / plot["step"])) + 1)]
    decomposed = [unc_decompose(ensemble, x) for x in grid]
    errors = [abs(y - unc_predict(model, x)[0]) for x, y in test[:b["n_test"]]]
    scores = [abs(y - unc_predict(model, x)[0]) for x, y in cal]
    q = unc_conformal_q(scores, c["alpha"])
    normalized_scores = [abs(y - unc_predict(model, x)[0]) / unc_predict(model, x)[1] for x, y in cal]
    q_normalized = unc_conformal_q(normalized_scores, c["alpha"])
    repeat_rng = random.Random(c["seed"])
    coverages = []
    for _ in range(c["repeats"]):
        cal_r = unc_sample(data["n_cal"], data, repeat_rng)
        test_r = unc_sample(c["repeat_test"], data, repeat_rng)
        q_r = unc_conformal_q([abs(y - unc_predict(model, x)[0]) for x, y in cal_r], c["alpha"])
        coverages.append(unc_coverage(model, test_r, q_r)["all"])
    coverage_mean = sum(coverages) / len(coverages)
    edges = c["bins"] + [c["bins"][-1] + 0.02]
    histogram = [sum(lo <= v < hi for v in coverages) for lo, hi in zip(edges, edges[1:])]
    small = scores[:c["small_n"]]
    outputs, masks = unc_dropout_samples(dr["hidden"], dr["weights"], dr["p"], max(dr["samples"]), random.Random(dr["seed"]))
    mc = []
    for count in dr["samples"]:
        head = outputs[:count]
        m = sum(head) / count
        mc.append({"samples": count, "mean": m, "sd": math.sqrt(sum((v - m) ** 2 for v in head) / (count - 1))})
    rank = unc_conformal_rank(data["n_cal"], c["alpha"])
    return {
        "example": e,
        "model": model,
        "ensemble": ensemble,
        "probes": [unc_decompose(ensemble, x) for x in e["probes"]],
        "points": [unc_xy(x, y, plot) for x, y in train[:plot["shown_points"]]],
        "truth_points": [unc_xy(x, math.sin(x), plot) for x in grid],
        "member_points": [[unc_xy(x, unc_predict(m, x)[0], plot) for x in grid] for m in ensemble],
        "band": [unc_xy(r["x"], r["mean"] + 2 * math.sqrt(r["total"]), plot) for r in decomposed]
                + [unc_xy(r["x"], r["mean"] - 2 * math.sqrt(r["total"]), plot) for r in reversed(decomposed)],
        "train_edge": unc_xy(data["hi"], 0.0, plot)[0],
        "bootstrap": unc_bootstrap_ci(errors, b["resamples"], b["level"], random.Random(b["seed"])),
        "dropout_deterministic": sum(w * h for w, h in zip(dr["weights"], dr["hidden"])),
        "dropout_sd": math.sqrt(unc_dropout_variance(dr["hidden"], dr["weights"], dr["p"])),
        "dropout_shown": [{"mask": m, "output": o} for m, o in zip(masks[:dr["shown"]], outputs[:dr["shown"]])],
        "mc": mc,
        "q": q,
        "rank": rank,
        "guarantee_hi": rank / (data["n_cal"] + 1),
        "coverage": unc_coverage(model, test, q, split_at=c["split_at"]),
        "q_normalized": q_normalized,
        "coverage_normalized": unc_coverage(model, test, q_normalized, normalized=True, split_at=c["split_at"]),
        "small_scores": small,
        "small_sorted": sorted(small),
        "small_rank": unc_conformal_rank(len(small), c["small_alpha"]),
        "small_q": unc_conformal_q(small, c["small_alpha"]),
        "repeat_mean": coverage_mean,
        "repeat_sd": math.sqrt(sum((v - coverage_mean) ** 2 for v in coverages) / (len(coverages) - 1)),
        "repeat_p05": unc_quantile(coverages, 0.05),
        "repeat_p95": unc_quantile(coverages, 0.95),
        "repeat_below": sum(v < 1 - c["alpha"] for v in coverages),
        "histogram": histogram,
        "histogram_edges": edges,
    }

VIT_EXAMPLE = {
    "configs": [
        {"name": "ViT-Ti/16", "image": 224, "patch": 16, "channels": 3, "dim": 192, "depth": 12, "heads": 3, "mlp": 768, "classes": 1000},
        {"name": "ViT-S/16", "image": 224, "patch": 16, "channels": 3, "dim": 384, "depth": 12, "heads": 6, "mlp": 1536, "classes": 1000},
        {"name": "ViT-B/16", "image": 224, "patch": 16, "channels": 3, "dim": 768, "depth": 12, "heads": 12, "mlp": 3072, "classes": 1000},
        {"name": "ViT-B/32", "image": 224, "patch": 32, "channels": 3, "dim": 768, "depth": 12, "heads": 12, "mlp": 3072, "classes": 1000},
        {"name": "ViT-L/16", "image": 224, "patch": 16, "channels": 3, "dim": 1024, "depth": 24, "heads": 16, "mlp": 4096, "classes": 1000},
        {"name": "ViT-H/14", "image": 224, "patch": 14, "channels": 3, "dim": 1280, "depth": 32, "heads": 16, "mlp": 5120, "classes": 1000},
    ],
    "main": "ViT-B/16",
    "batch": 8,
    "resolutions": [(224, 32), (224, 16), (224, 14), (384, 16), (512, 16)],
    "toy": {
        "image": [[1, 2, 0, 1], [3, 4, 1, 0], [0, 0, 2, 2], [1, 0, 2, 3]],
        "patch": 2,
        "weights": [[1, 0, 0, -1], [1, 1, 1, 1]],
        "bias": [1, 0],
    },
}


def vit_config(name):
    return next(c for c in VIT_EXAMPLE["configs"] if c["name"] == name)


def vit_tokens(image, patch):
    side = image // patch
    return {"side": side, "patches": side * side, "tokens": side * side + 1}


def vit_shape_walk(cfg, batch):
    t = vit_tokens(cfg["image"], cfg["patch"])
    b, c, d, s = batch, cfg["channels"], cfg["dim"], t["side"]
    return [
        {"stage": "image", "shape": [b, c, cfg["image"], cfg["image"]]},
        {"stage": "Conv2d(kernel = stride = %d)" % cfg["patch"], "shape": [b, d, s, s]},
        {"stage": "flatten(2)", "shape": [b, d, t["patches"]]},
        {"stage": "transpose(1, 2)", "shape": [b, t["patches"], d]},
        {"stage": "prepend class token", "shape": [b, t["tokens"], d]},
        {"stage": "add position embeddings", "shape": [b, t["tokens"], d]},
        {"stage": "per-head attention scores", "shape": [b, cfg["heads"], t["tokens"], t["tokens"]]},
        {"stage": "MLP hidden", "shape": [b, t["tokens"], cfg["mlp"]]},
        {"stage": "%d encoder layers" % cfg["depth"], "shape": [b, t["tokens"], d]},
        {"stage": "take token 0", "shape": [b, d]},
        {"stage": "head", "shape": [b, cfg["classes"]]},
    ]


def vit_params(cfg):
    d, m, c, p = cfg["dim"], cfg["mlp"], cfg["channels"], cfg["patch"]
    tokens = vit_tokens(cfg["image"], p)["tokens"]
    layer = {
        "attn_in": d * 3 * d + 3 * d,
        "attn_out": d * d + d,
        "norms": 2 * 2 * d,
        "mlp_up": d * m + m,
        "mlp_down": m * d + d,
    }
    layer_total = sum(layer.values())
    parts = {
        "patch_embed": c * p * p * d + d,
        "class_token": d,
        "position": tokens * d,
        "layers": cfg["depth"] * layer_total,
        "final_norm": 2 * d,
        "head": d * cfg["classes"] + cfg["classes"],
    }
    return {"layer": layer, "layer_total": layer_total, "parts": parts, "total": sum(parts.values())}


def vit_patchify(image, patch):
    side = len(image) // patch
    return [[image[pr * patch + i][pc * patch + j] for i in range(patch) for j in range(patch)]
            for pr in range(side) for pc in range(side)]


def vit_conv(image, weights, bias, patch, stride):
    size = len(image)
    out_side = (size - patch) // stride + 1
    return [[[bias[k] + sum(weights[k][i * patch + j] * image[r * stride + i][q * stride + j]
                            for i in range(patch) for j in range(patch))
              for q in range(out_side)] for r in range(out_side)] for k in range(len(weights))]


def vit_linear(patches, weights, bias):
    return [[bias[k] + sum(w * v for w, v in zip(weights[k], row)) for k in range(len(weights))] for row in patches]


@functools.lru_cache(maxsize=None)
def vit_example():
    e = VIT_EXAMPLE
    main = vit_config(e["main"])
    toy = e["toy"]
    patches = vit_patchify(toy["image"], toy["patch"])
    conv = vit_conv(toy["image"], toy["weights"], toy["bias"], toy["patch"], toy["patch"])
    linear = vit_linear(patches, toy["weights"], toy["bias"])
    side = len(conv[0])
    conv_tokens = [[conv[k][r][q] for k in range(len(conv))] for r in range(side) for q in range(side)]
    resolutions = []
    for image, patch in e["resolutions"]:
        t = vit_tokens(image, patch)
        resolutions.append({"image": image, "patch": patch, **t, "scores": t["tokens"] ** 2})
    base_scores = vit_tokens(main["image"], main["patch"])["tokens"] ** 2
    for r in resolutions:
        r["relative"] = r["scores"] / base_scores
    return {
        "example": e,
        "main": main,
        "tokens": vit_tokens(main["image"], main["patch"]),
        "walk": vit_shape_walk(main, e["batch"]),
        "params": vit_params(main),
        "models": [{"config": c, "tokens": vit_tokens(c["image"], c["patch"])["tokens"], "total": vit_params(c)["total"]}
                   for c in e["configs"]],
        "patches": patches,
        "conv": conv,
        "conv_tokens": conv_tokens,
        "linear": linear,
        "resolutions": resolutions,
        "overlap_side": len(vit_conv(toy["image"], toy["weights"], toy["bias"], toy["patch"], 1)[0]),
    }


UNET_EXAMPLE = {
    "sd": {"name": "Stable Diffusion v1", "in_channels": 4, "out_channels": 4, "model_channels": 320,
           "channel_mult": [1, 2, 4, 4], "num_res_blocks": 2, "attention_resolutions": [4, 2, 1],
           "num_heads": 8, "context_dim": 768, "context_tokens": 77, "latent": 64, "image": 512, "groups": 32},
    "dits": [
        {"name": "DiT-S/2", "dim": 384, "depth": 12, "heads": 6, "patch": 2},
        {"name": "DiT-B/2", "dim": 768, "depth": 12, "heads": 12, "patch": 2},
        {"name": "DiT-L/2", "dim": 1024, "depth": 24, "heads": 16, "patch": 2},
        {"name": "DiT-XL/2", "dim": 1152, "depth": 28, "heads": 16, "patch": 2},
        {"name": "DiT-XL/4", "dim": 1152, "depth": 28, "heads": 16, "patch": 4},
        {"name": "DiT-XL/8", "dim": 1152, "depth": 28, "heads": 16, "patch": 8},
    ],
    "dit_latent": 32,
    "dit_channels": 4,
    "dit_classes": 1000,
    "dit_frequency_dim": 256,
    "embed_dim": 8,
    "embed_steps": [0, 1, 10, 500, 999],
    "toy_groups": 2,
    "toy_x": [[1.0, 3.0], [2.0, 2.0], [10.0, 14.0], [12.0, 12.0]],
}


def _unet_conv(ci, co, k):
    return ci * co * k * k + co


def _unet_linear(i, o, bias=True):
    return i * o + (o if bias else 0)


def unet_resblock_params(ci, co, emb):
    skip = 0 if ci == co else _unet_conv(ci, co, 1)
    return 2 * ci + _unet_conv(ci, co, 3) + _unet_linear(emb, co) + 2 * co + _unet_conv(co, co, 3) + skip


def unet_transformer_params(c, ctx):
    self_attn = 3 * _unet_linear(c, c, False) + _unet_linear(c, c)
    cross_attn = _unet_linear(c, c, False) + 2 * _unet_linear(ctx, c, False) + _unet_linear(c, c)
    ff = _unet_linear(c, 8 * c) + _unet_linear(4 * c, c)
    return 2 * c + 2 * _unet_conv(c, c, 1) + self_attn + cross_attn + ff + 3 * 2 * c


def unet_walk(cfg):
    mc, emb, ctx = cfg["model_channels"], 4 * cfg["model_channels"], cfg["context_dim"]
    side, ch, ds = cfg["latent"], mc, 1
    parts = {"time": _unet_linear(mc, emb) + _unet_linear(emb, emb), "conv_in": _unet_conv(cfg["in_channels"], mc, 3),
             "res": 0, "attn": 0, "resample": 0, "out": 0}
    down = [{"name": "conv_in", "side": side, "channels": mc, "attn": False}]
    skips = [mc]
    last = len(cfg["channel_mult"]) - 1
    for level, mult in enumerate(cfg["channel_mult"]):
        for _ in range(cfg["num_res_blocks"]):
            parts["res"] += unet_resblock_params(ch, mult * mc, emb)
            ch = mult * mc
            attn = ds in cfg["attention_resolutions"]
            if attn:
                parts["attn"] += unet_transformer_params(ch, ctx)
            down.append({"name": "ResBlock" + (" + attention" if attn else ""), "side": side, "channels": ch, "attn": attn})
            skips.append(ch)
        if level != last:
            parts["resample"] += _unet_conv(ch, ch, 3)
            side //= 2
            ds *= 2
            down.append({"name": "Downsample", "side": side, "channels": ch, "attn": False})
            skips.append(ch)
    parts["res"] += 2 * unet_resblock_params(ch, ch, emb)
    parts["attn"] += unet_transformer_params(ch, ctx)
    middle = {"side": side, "channels": ch}
    up = []
    for level in range(last, -1, -1):
        mult = cfg["channel_mult"][level]
        for i in range(cfg["num_res_blocks"] + 1):
            skip = skips.pop()
            parts["res"] += unet_resblock_params(ch + skip, mult * mc, emb)
            row = {"side": side, "in": ch + skip, "skip": skip, "channels": mult * mc,
                   "attn": ds in cfg["attention_resolutions"], "upsample": bool(level and i == cfg["num_res_blocks"])}
            ch = mult * mc
            if row["attn"]:
                parts["attn"] += unet_transformer_params(ch, ctx)
            if row["upsample"]:
                parts["resample"] += _unet_conv(ch, ch, 3)
                side *= 2
                ds //= 2
            up.append(row)
    parts["out"] = 2 * ch + _unet_conv(mc, cfg["out_channels"], 3)
    return {"down": down, "middle": middle, "up": up, "parts": parts, "total": sum(parts.values()),
            "skips_left": len(skips)}


def dit_params(cfg, latent, channels, classes, freq_dim):
    d, p = cfg["dim"], cfg["patch"]
    out = 2 * channels
    block = _unet_linear(d, 3 * d) + _unet_linear(d, d) + _unet_linear(d, 4 * d) + _unet_linear(4 * d, d) + _unet_linear(d, 6 * d)
    parts = {"patchify": _unet_conv(channels, d, p),
             "conditioning": _unet_linear(freq_dim, d) + _unet_linear(d, d) + (classes + 1) * d,
             "blocks": cfg["depth"] * block,
             "final": _unet_linear(d, 2 * d) + _unet_linear(d, p * p * out)}
    tokens = (latent // p) ** 2
    return {"parts": parts, "block": block, "total": sum(parts.values()), "tokens": tokens,
            "pos_table": tokens * d, "out_channels": out}


def timestep_embedding_ldm(t, dim, max_period=10000.0):
    half = dim // 2
    freqs = [math.exp(-math.log(max_period) * i / half) for i in range(half)]
    return [math.cos(t * f) for f in freqs] + [math.sin(t * f) for f in freqs]


def timestep_embedding_ddpm(t, dim, max_period=10000.0):
    half = dim // 2
    freqs = [math.exp(-math.log(max_period) * i / (half - 1)) for i in range(half)]
    return [math.sin(t * f) for f in freqs] + [math.cos(t * f) for f in freqs]


def unet_group_norm(x, groups, eps=1e-5):
    size = len(x) // groups
    out, stats = [], []
    for g in range(groups):
        values = [v for channel in x[g * size:(g + 1) * size] for v in channel]
        mean = _mean(values)
        var = _variance(values)
        stats.append({"mean": mean, "var": var, "count": len(values)})
        out.extend([[(v - mean) / math.sqrt(var + eps) for v in channel] for channel in x[g * size:(g + 1) * size]])
    return {"out": out, "stats": stats}


@functools.lru_cache(maxsize=None)
def unet_example():
    e = UNET_EXAMPLE
    sd = e["sd"]
    walk = unet_walk(sd)
    dits = [dict(c, **dit_params(c, e["dit_latent"], e["dit_channels"], e["dit_classes"], e["dit_frequency_dim"]))
            for c in e["dits"]]
    attn_sides = sorted({r["side"] for r in walk["down"] if r["attn"]}, reverse=True)
    attention = [{"side": s, "tokens": s * s, "self_scores": (s * s) ** 2, "cross_scores": s * s * sd["context_tokens"]}
                 for s in [sd["latent"] // 2 ** k for k in range(len(sd["channel_mult"]))]]
    return {
        "example": e,
        "sd": sd,
        "walk": walk,
        "emb_dim": 4 * sd["model_channels"],
        "frequencies": [math.exp(-math.log(10000.0) * i / (e["embed_dim"] // 2)) for i in range(e["embed_dim"] // 2)],
        "embeddings": [{"t": t, "ldm": timestep_embedding_ldm(t, e["embed_dim"]),
                        "ddpm": timestep_embedding_ddpm(t, e["embed_dim"])} for t in e["embed_steps"]],
        "group_norm": unet_group_norm(e["toy_x"], e["toy_groups"]),
        "layer_norm_style": unet_group_norm(e["toy_x"], 1),
        "dits": dits,
        "dit_main": next(d for d in dits if d["name"] == "DiT-XL/2"),
        "attn_sides": attn_sides,
        "attention": attention,
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
        "areas": AREAS,
        "pages_by_area": pages_by_area(),
        "area": find_area(page["area"]) if page else None,
        "connections": connections(page["slug"]) if page else None,
        "learning_path": learning_path(),
        "ready_slugs": {entry["slug"] for entry in ready_pages()},
        "upstream": UPSTREAM,
        "pins": PINS,
        "src": source_url,
        "skl": sklearn_url,
        "xgb": xgboost_url,
        "pinned": pinned_url,
        "previous_page": previous,
        "next_page": following,
        "upcoming": UPCOMING_MODELS,
        "encoder_example": encoder_example,
        "ltr_example": ltr_example,
        "collab_example": collab_example,
        "accumulation_example": accumulation_example,
        "latency_example": latency_example,
        "online_example": online_example,
        "uncertainty_example": uncertainty_example,
        "vit_example": vit_example,
        "data_example": data_example,
        "serving_example": serving_example,
        "causal_example": causal_example,
        "calibration_example": calibration_example,
        "gnn_example": gnn_example,
        "diffusion_example": diffusion_example,
        "unet_example": unet_example,
        "pretraining_example": pretraining_example,
        "attention_example": ATTENTION_EXAMPLE,
        "attention_weights": attention_weights,
        "multihead_example": MULTIHEAD_EXAMPLE,
        "scaled_attention": scaled_attention,
        "multihead_attention": multihead_attention,
        "causal_allowed_mask": causal_allowed_mask,
        "allowed_to_additive": allowed_to_additive,
        "masked_out_to_additive": masked_out_to_additive,
        "key_padding_additive": key_padding_additive,
        "add_masks": add_masks,
        "split_heads": split_heads,
        "merge_heads": merge_heads,
        "packed_in_projection": packed_in_projection,
        "gqa_groups": gqa_groups,
        "kv_cache_bytes_per_token": kv_cache_bytes_per_token,
        "multihead_param_count": multihead_param_count,
        "norm_example": NORM_EXAMPLE,
        "layer_norm_row": layer_norm_row,
        "rms_norm_row": rms_norm_row,
        "batch_norm_columns": batch_norm_columns,
        "group_norm_row": group_norm_row,
        "running_stats_update": running_stats_update,
        "batch_norm_eval": batch_norm_eval,
        "residual_block": residual_block,
        "residual_stream_norms": residual_stream_norms,
        "norm_param_count": norm_param_count,
        "residual_demo": residual_demo,
        "presets": TRANSFORMER_PRESETS,
        "param_count": transformer_param_count,
        "broadcast_steps": broadcast_steps,
        "contiguous_strides": contiguous_strides,
        "element_offset": element_offset,
        "is_contiguous": is_contiguous,
        "transpose_layout": transpose_layout,
        "dot_product": dot_product,
        "vector_norm": vector_norm,
        "cosine_similarity": cosine_similarity,
        "angle_degrees": angle_degrees,
        "projection": projection,
        "similarity_example": SIMILARITY_EXAMPLE,
        "projection_example": PROJECTION_EXAMPLE,
        "similarity_ranking": similarity_ranking,
        "matmul_example": MATMUL_EXAMPLE,
        "linear_example": LINEAR_EXAMPLE,
        "inverse_example": INVERSE_EXAMPLE,
        "transpose": transpose,
        "identity": identity,
        "matmul": matmul,
        "matmul_shape": matmul_shape,
        "matmul_flops": matmul_flops,
        "linear_layer": linear_layer,
        "inverse_2x2": inverse_2x2,
        "slope_example": SLOPE_EXAMPLE,
        "slope_table": slope_table,
        "bowl_example": BOWL_EXAMPLE,
        "bowl": bowl,
        "bowl_gradient": bowl_gradient,
        "bowl_descent": bowl_descent,
        "bowl_contours": bowl_contours,
        "stable_learning_rate": stable_learning_rate,
        "jacobian_example": JACOBIAN_EXAMPLE,
        "jacobian_example_function": jacobian_example_function,
        "jacobian_example_exact": jacobian_example_exact,
        "numerical_jacobian": numerical_jacobian,
        "chain_example": CHAIN_EXAMPLE,
        "scalar_chain": scalar_chain,
        "two_layer_example": TWO_LAYER_EXAMPLE,
        "two_layer_pass": two_layer_pass,
        "mode_cost_example": MODE_COST_EXAMPLE,
        "mode_costs": mode_costs,
        "bernoulli_example": BERNOULLI_EXAMPLE,
        "bernoulli_pmf": bernoulli_pmf,
        "categorical_example": CATEGORICAL_EXAMPLE,
        "categorical_from_logits": categorical_from_logits,
        "inverse_cdf_sample": inverse_cdf_sample,
        "log": math.log,
        "normal_log_prob": normal_log_prob,
        "normal_pdf": normal_pdf,
        "normal_cdf": normal_cdf,
        "normal_band": normal_band,
        "joint_example": JOINT_EXAMPLE,
        "joint_table": joint_table,
        "die_example": DIE_EXAMPLE,
        "covariance_example": COVARIANCE_EXAMPLE,
        "minibatch_example": MINIBATCH_EXAMPLE,
        "expectation": expectation,
        "variance": variance,
        "covariance": covariance,
        "die_rolls": die_rolls,
        "running_means": running_means,
        "sum_pmf": sum_pmf,
        "minibatch_gradients": minibatch_gradients,
        "sqrt": math.sqrt,
        "log10": math.log10,
        "entropy_example": ENTROPY_EXAMPLE,
        "asymmetry_example": ASYMMETRY_EXAMPLE,
        "perplexity_example": PERPLEXITY_EXAMPLE,
        "information_content": information_content,
        "entropy": entropy,
        "cross_entropy": cross_entropy,
        "kl_divergence": kl_divergence,
        "logits_cross_entropy": logits_cross_entropy,
        "perplexity": perplexity,
        "mutual_information": mutual_information,
        "exp": math.exp,
        "sin": math.sin,
        "constant_fit_example": CONSTANT_FIT_EXAMPLE,
        "triplet_example": TRIPLET_EXAMPLE,
        "infonce_example": INFONCE_EXAMPLE,
        "reduction_example": REDUCTION_EXAMPLE,
        "huber": huber,
        "regression_losses": regression_losses,
        "fit_constant": fit_constant,
        "bce_with_logits": bce_with_logits,
        "margin_losses": margin_losses,
        "triplet_loss": triplet_loss,
        "info_nce": info_nce,
        "reduce_losses": reduce_losses,
        "line_descent_example": LINE_DESCENT_EXAMPLE,
        "regularization_example": REGULARIZATION_EXAMPLE,
        "least_squares_line": least_squares_line,
        "normal_equations": normal_equations,
        "regularization_paths": regularization_paths,
        "mse_hessian": mse_hessian,
        "line_descent": line_descent,
        "symmetric_eigen_2x2": symmetric_eigen_2x2,
        "quadratic_ellipse": quadratic_ellipse,
        "zip": zip,
        "gpt2_small": GPT2_SMALL,
        "generation_example": GENERATION_EXAMPLE,
        "decoder_param_count": decoder_param_count,
        "next_token_pairs": next_token_pairs,
        "causal_prefix_check": causal_prefix_check,
        "sequence_nll": sequence_nll,
        "greedy_generate": greedy_generate,
        "generation_positions": generation_positions,
        "decoding_example": DECODING_EXAMPLE,
        "kv_config": KV_CONFIG,
        "paged_example": PAGED_EXAMPLE,
        "cached_decode": cached_decode,
        "kv_cache_total_bytes": kv_cache_total_bytes,
        "decode_attention_intensity": decode_attention_intensity,
        "paged_allocation": paged_allocation,
        "learning_points": LEARNING_POINTS,
        "learning_truth": LEARNING_TRUTH,
        "learning_labeled": LEARNING_LABELED,
        "learning_text": LEARNING_TEXT,
        "generalization_rows": generalization_rows,
        "generalization_x": GENERALIZATION_X,
        "generalization_targets": generalization_train_targets,
        "generalization_truth": generalization_truth,
        "polynomial_fit": polynomial_fit,
        "polynomial_predict": polynomial_predict,
        "split_labels": SPLIT_LABELS,
        "split_unlucky_order": SPLIT_UNLUCKY_ORDER,
        "split_groups": SPLIT_GROUPS,
        "split_group_order": SPLIT_GROUP_ORDER,
        "split_series": SPLIT_SERIES,
        "split_random_test_months": SPLIT_RANDOM_TEST_MONTHS,
        "class_counts": class_counts,
        "stratified_allocation": stratified_allocation,
        "chance_test_misses_class": chance_test_misses_class,
        "leaked_group_records": leaked_group_records,
        "nearest_in_time_mse": nearest_in_time_mse,
        "accuracy_standard_error": accuracy_standard_error,
        "preprocess_age": PREPROCESS_AGE,
        "preprocess_income": PREPROCESS_INCOME,
        "preprocess_colors": PREPROCESS_COLORS,
        "column_mean_std": column_mean_std,
        "standardize_with": standardize_with,
        "min_max_scale": min_max_scale,
        "median": median,
        "one_hot_encode": one_hot_encode,
        "ordinal_encode": ordinal_encode,
        "pair_distance": pair_distance,
        "log10_column": log10_column,
        "leak_dup_train": LEAK_DUP_TRAIN,
        "leak_dup_test": LEAK_DUP_TEST,
        "leak_loan_defaulted": LEAK_LOAN_DEFAULTED,
        "leak_loan_notices": LEAK_LOAN_NOTICES,
        "leak_loan_debt_ratio": LEAK_LOAN_DEBT_RATIO,
        "leaky_selection_demo": leaky_selection_demo,
        "leaky_selection_average": leaky_selection_average,
        "duplicate_overlap": duplicate_overlap,
        "lookup_accuracy": lookup_accuracy,
        "best_threshold_rule": best_threshold_rule,
        "metric_labels": METRIC_LABELS,
        "metric_scores": METRIC_SCORES,
        "metric_class_counts": METRIC_CLASS_COUNTS,
        "confusion_counts": confusion_counts,
        "precision_recall_f1": precision_recall_f1,
        "roc_points": roc_points,
        "trapezoid_area": trapezoid_area,
        "rank_auc": rank_auc,
        "pr_points": pr_points,
        "average_precision": average_precision,
        "binary_log_loss": binary_log_loss,
        "averaged_f1": averaged_f1,
        "kfold_splits": kfold_splits,
        "stratified_kfold_splits": stratified_kfold_splits,
        "group_kfold_splits": group_kfold_splits,
        "time_series_splits": time_series_splits,
        "cv_summary": cv_summary,
        "best_regression_stump": best_regression_stump,
        "boost_stumps": boost_stumps,
        "grow_regression_tree": grow_regression_tree,
        "regression_tree_predict": regression_tree_predict,
        "wavy_rows": wavy_rows,
        "boosting_curve": boosting_curve,
        "newton_scan": newton_scan,
        "polynomial_learning_curve": polynomial_learning_curve,
        "ridge_strength_sweep": ridge_strength_sweep,
        "memorization_demo": memorization_demo,
        "bias_variance_decomposition": bias_variance_decomposition,
        "penalized_fits": penalized_fits,
        "activation_table": activation_table,
        "gelu_tanh_max_error": gelu_tanh_max_error,
        "chain_gradient": chain_gradient,
        "glu_variants": glu_variants,
        "relu_active_fraction": relu_active_fraction,
        "gelu_exact": gelu_exact,
        "gelu_tanh": gelu_tanh,
        "silu": silu,
        "softplus": softplus,
        "lasso_sparsity_path": lasso_sparsity_path,
        "dropout_statistics": dropout_statistics,
        "adam_weight_decay_comparison": adam_weight_decay_comparison,
        "BOOST_XS": BOOST_XS,
        "BOOST_YS": BOOST_YS,
        "NEWTON_XS": NEWTON_XS,
        "NEWTON_LABELS": NEWTON_LABELS,
        "label_counts": label_counts,
        "gini_impurity": gini_impurity,
        "entropy_impurity": entropy_impurity,
        "split_candidates": split_candidates,
        "best_split": best_split,
        "grow_tree": grow_tree,
        "tree_predict": tree_predict,
        "tree_accuracy": tree_accuracy,
        "tree_leaves": tree_leaves,
        "tree_depth": tree_depth,
        "tree_nodes": tree_nodes,
        "tree_feature_importances": tree_feature_importances,
        "cost_complexity_path": cost_complexity_path,
        "prune_tree": prune_tree,
        "noisy_diagonal_rows": noisy_diagonal_rows,
        "depth_sweep": depth_sweep,
        "importance_demo": importance_demo,
        "regression_split_demo": regression_split_demo,
        "TREE_TOY_ROWS": TREE_TOY_ROWS,
        "centroid_cv_data": centroid_cv_data,
        "centroid_fold_score": centroid_fold_score,
        "centroid_cv_scores": centroid_cv_scores,
        "repeated_cv_means": repeated_cv_means,
        "selection_bias_demo": selection_bias_demo,
        "kmeans_run": kmeans_run,
        "nearest_labeled": nearest_labeled,
        "cluster_then_label": cluster_then_label,
        "prediction_accuracy": prediction_accuracy,
        "masked_pairs": masked_pairs,
        "bigram_next_token_loss": bigram_next_token_loss,
        "beam_step_probs": BEAM_STEP_PROBS,
        "speculative_example": SPECULATIVE_EXAMPLE,
        "temperature_probs": temperature_probs,
        "top_k_filter": top_k_filter,
        "top_p_filter": top_p_filter,
        "repeat_penalty": repeat_penalty,
        "constrained_probs": constrained_probs,
        "sample_frequencies": sample_frequencies,
        "beam_search": beam_search,
        "greedy_path": greedy_path,
        "speculative_step": speculative_step,
        "speculative_tokens_per_pass": speculative_tokens_per_pass,
        "entropy": entropy,
        "logistic_example": LOGISTIC_EXAMPLE,
        "boundary_example": BOUNDARY_EXAMPLE,
        "softmax_example": SOFTMAX_EXAMPLE,
        "sigmoid": sigmoid,
        "logistic_fit_1d": logistic_fit_1d,
        "boundary_fits": boundary_fits,
        "xor_example": XOR_EXAMPLE,
        "approximation_example": APPROXIMATION_EXAMPLE,
        "mlp_example": MLP_EXAMPLE,
        "xor_network": xor_network,
        "approximation_fits": approximation_fits,
        "evaluate_interpolant": evaluate_interpolant,
        "mlp_param_count": mlp_param_count,
        "backprop_example": BACKPROP_EXAMPLE,
        "gradient_check_example": GRADIENT_CHECK_EXAMPLE,
        "depth_example": DEPTH_EXAMPLE,
        "run_backprop": backprop_example,
        "gradient_check": gradient_check,
        "gradient_check_all": gradient_check_all,
        "gradient_norms_by_depth": gradient_norms_by_depth,
        "optimizer_bowl": OPTIMIZER_BOWL,
        "adam_example": ADAM_EXAMPLE,
        "weight_decay_example": WEIGHT_DECAY_EXAMPLE,
        "optimizer_race": optimizer_race,
        "adam_trace": adam_trace,
        "uncorrected_step_ratio": uncorrected_step_ratio,
        "weight_decay_paths": weight_decay_paths,
        "optimizer_memory": optimizer_memory,
        "embedding_example": EMBEDDING_EXAMPLE,
        "word2vec_example": WORD2VEC_EXAMPLE,
        "embedding_lookup": embedding_lookup,
        "one_hot_rows": one_hot_rows,
        "embedding_gradient": embedding_gradient,
        "train_skipgram": train_skipgram,
        "nearest_words": nearest_words,
        "tied_parameter_counts": tied_parameter_counts,
        "training_example": TRAINING_EXAMPLE,
        "scaler_example": SCALER_EXAMPLE,
        "lr_at": lr_at,
        "lr_schedule": lr_schedule,
        "smoothed_cross_entropy": smoothed_cross_entropy,
        "masked_mean_loss": masked_mean_loss,
        "bigram_gradient": bigram_gradient,
        "clip_by_global_norm": clip_by_global_norm,
        "training_run": training_run,
        "accumulation_check": accumulation_check,
        "scaled_gradient_roundtrip": scaled_gradient_roundtrip,
        "grad_scaler_trace": grad_scaler_trace,
        "training_memory": training_memory,
        "eigen_example": EIGEN_EXAMPLE,
        "svd_example": SVD_EXAMPLE,
        "ratings_example": RATINGS_EXAMPLE,
        "rank_example": RANK_EXAMPLE,
        "condition_example": CONDITION_EXAMPLE,
        "jacobi_eigh": jacobi_eigh,
        "power_iteration": power_iteration,
        "svd": svd,
        "from_svd": from_svd,
        "low_rank_errors": low_rank_errors,
        "matrix_rank": matrix_rank,
        "condition_number": condition_number,
        "perturbed_solve": perturbed_solve,
        "unit_circle_image": unit_circle_image,
        "svd_stages": svd_stages,
        "lora_param_counts": lora_param_counts,
        "missing_example": MISSING_EXAMPLE,
        "routing_example_data": ROUTING_EXAMPLE,
        "column_fill_values": column_fill_values,
        "impute_column": impute_column,
        "missing_indicator": missing_indicator,
        "complete_rows": complete_rows,
        "mechanism_estimates": mechanism_estimates,
        "iterative_comparison": iterative_comparison,
        "indicator_comparison": indicator_comparison,
        "missing_split_scan": missing_split_scan,
        "routing_example": routing_example,
        "graph_example": graph_example,
        "graph_controls": graph_controls,
        "graph_example_data": GRAPH_EXAMPLE,
        "conv_example": conv_example,
        "output_size_rows": output_size_rows,
        "lenet_stack": lenet_stack,
        "resnet18_stack": resnet18_stack,
        "stacking_comparison": stacking_comparison,
        "resnet_receptive_fields": resnet_receptive_fields,
        "ar_joint": AR_JOINT,
        "ar_corpus": AR_CORPUS,
        "ar_causal_input": AR_CAUSAL_INPUT,
        "ar_causal_kernel": AR_CAUSAL_KERNEL,
        "ar_causal_dilations": AR_CAUSAL_DILATIONS,
        "chain_rule_factors": chain_rule_factors,
        "markov_approximation": markov_approximation,
        "ancestral_samples": ancestral_samples,
        "table_sizes": table_sizes,
        "teacher_forcing_example": teacher_forcing_example,
        "exposure_bias_curve": exposure_bias_curve,
        "causal_stack": causal_stack,
        "causal_receptive_field": causal_receptive_field,
        "causality_check": causality_check,
        "wavenet_receptive_fields": wavenet_receptive_fields,
        "pixelcnn_mask": pixelcnn_mask,
        "pixelcnn_dependencies": pixelcnn_dependencies,
        "bpe_corpus": BPE_CORPUS,
        "bpe_train": bpe_train,
        "bpe_encode": bpe_encode,
        "wordpiece_gains": wordpiece_gains,
        "unigram_pieces": UNIGRAM_PIECES,
        "unigram_segmentations": unigram_segmentations,
        "unigram_viterbi": unigram_viterbi,
        "utf8_lengths": utf8_lengths,
        "digit_groups": digit_groups,
        "batch_ids": batch_ids,
        "knn_points": KNN_POINTS,
        "knn_query": KNN_QUERY,
        "metric_table": metric_table,
        "knn_classify": knn_classify,
        "docstring_examples": docstring_examples,
        "k_sweep": k_sweep,
        "leave_one_out": leave_one_out,
        "distance_concentration": distance_concentration,
        "neighborhood_edge": neighborhood_edge,
        "tree_size": tree_size,
        "kd_tree_build": kd_tree_build,
        "kd_tree_query": kd_tree_query,
        "ball_bound_example": ball_bound_example,
        "search_example": SEARCH_EXAMPLE,
        "metric_agreement": metric_agreement,
        "brute_force_search_cost": brute_force_search_cost,
        "bm25_example": BM25_EXAMPLE,
        "bm25_scores": bm25_scores,
        "bm25_saturation": bm25_saturation,
        "hybrid_example": hybrid_example,
        "example_gpu": EXAMPLE_GPU,
        "gpu_op_examples": gpu_op_examples,
        "fusion_example": fusion_example,
        "tiled_matmul_traffic": tiled_matmul_traffic,
        "async_timeline": async_timeline,
        "roofline_xy": roofline_xy,
        "float_formats": FLOAT_FORMATS,
        "find_float_format": find_float_format,
        "float_format_stats": float_format_stats,
        "round_to_format": round_to_format,
        "float_bits": float_bits,
        "precision_example": PRECISION_EXAMPLE,
        "loss_scaling_example": loss_scaling_example,
        "grad_scaler_run": grad_scaler_run,
        "master_weight_example": master_weight_example,
        "log2": math.log2,
        "quantize_roundtrip": quantize_roundtrip,
        "affine_example": AFFINE_EXAMPLE,
        "activation_example": ACTIVATION_EXAMPLE,
        "fake_quant_example": FAKE_QUANT_EXAMPLE,
        "fake_quantize": fake_quantize,
        "straight_through_grad": straight_through_grad,
        "per_channel_example": per_channel_example,
        "channel_weights": CHANNEL_WEIGHTS,
        "group_row": GROUP_ROW,
        "group_quantize": group_quantize,
        "weight_memory_example": weight_memory_example,
        "outlier_example": outlier_example,
        "quant_ranges": QUANT_RANGES,
        "affine_qparams": affine_qparams,
        "symmetric_qparams": symmetric_qparams,
        "outlier_activations": OUTLIER_ACTIVATIONS,
        "outlier_weights": OUTLIER_WEIGHTS,
        "rl_gamma": RL_GAMMA,
        "chain_states": CHAIN_STATES,
        "chain_slip": CHAIN_SLIP,
        "discounted_returns": discounted_returns,
        "value_iteration": value_iteration,
        "chain_values_closed_form": chain_values_closed_form,
        "q_update": q_update,
        "q_learning": q_learning,
        "chain_advantages": chain_advantages,
        "bandit_rewards": BANDIT_REWARDS,
        "reinforce_gradient": reinforce_gradient,
        "bandit_training": bandit_training,
        "ppo_epsilon": PPO_EPSILON,
        "ppo_ratios": PPO_RATIOS,
        "ppo_clip": ppo_clip,
        "diagnostic_population": DIAGNOSTIC_POPULATION,
        "diagnostic_test": diagnostic_test,
        "repeated_tests": repeated_tests,
        "coin_heads": COIN_HEADS,
        "coin_flips": COIN_FLIPS,
        "coin_prior": COIN_PRIOR,
        "binomial_likelihood": binomial_likelihood,
        "likelihood_area": likelihood_area,
        "coin_estimates": coin_estimates,
        "coin_curves": coin_curves,
        "ridge_map_1d": ridge_map_1d,
        "nb_vocabulary": NB_VOCABULARY,
        "nb_classes": NB_CLASSES,
        "nb_documents": NB_DOCUMENTS,
        "nb_word_counts": NB_WORD_COUNTS,
        "nb_message": NB_MESSAGE,
        "naive_bayes_posterior": naive_bayes_posterior,
        "accuracy_paradox": accuracy_paradox,
        "imbalance_example": imbalance_example,
        "focal_table": focal_table,
        "focal_loss": focal_loss,
        "forest_example": forest_example,
        "tree_correlation": tree_correlation,
        "forest_methods": FOREST_METHODS,
        "forest_features": FOREST_FEATURES,
        "averaged_variance": averaged_variance,
        "bootstrap_oob_fraction": bootstrap_oob_fraction,
        "init_example": init_example,
        "init_gain": init_gain,
        "xavier_std": xavier_std,
        "kaiming_std": kaiming_std,
        "uniform_bound": uniform_bound,
        "linear_default_bound": linear_default_bound,
        "relu_moment_factor": relu_moment_factor,
        "rnn_example": rnn_example,
        "rnn_example_data": RNN_EXAMPLE,
        "lstm_example_weights": LSTM_EXAMPLE,
        "gru_example_weights": GRU_EXAMPLE,
        "rnn_param_count": rnn_param_count,
        "pack_sequences": pack_sequences,
        "padded_waste": padded_waste,
        "autoencoder_example": autoencoder_example,
        "autoencoder_settings": AUTOENCODER_EXAMPLE,
        "vae_example": vae_example,
        "vae_settings": VAE_EXAMPLE,
        "conv_transpose_output_size": conv_transpose_output_size,
        "position_example": position_example,
        "position_settings": POSITION_EXAMPLE,
        "cluster_example": cluster_example,
        "cluster_settings": CLUSTER_EXAMPLE,
        "vector_index_example": vector_index_example,
        "vector_index_settings": VECTOR_INDEX_EXAMPLE,
        "distillation_example": distillation_example,
        "distillation_settings": DISTILLATION_EXAMPLE,
        "time_series_example": time_series_example,
        "time_series_settings": TIME_SERIES_EXAMPLE,
        "time_series_split": time_series_split,
        "regression_metrics_example": regression_metrics_example,
        "pinball_loss": pinball_loss,
        "regression_metrics_settings": REGRESSION_METRICS_EXAMPLE,
        "svm_example": svm_example,
        "svm_settings": SVM_EXAMPLE,
        "hinge": hinge,
        "lr_example": lr_schedule_example,
        "lr_settings": LR_SCHEDULE_EXAMPLE,
        "gan_example": gan_example,
        "gan_settings": GAN_EXAMPLE,
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
