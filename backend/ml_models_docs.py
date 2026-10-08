import itertools
import math
import random
import re

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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "ready": False,
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
        "attention_example": ATTENTION_EXAMPLE,
        "attention_weights": attention_weights,
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
        "logistic_example": LOGISTIC_EXAMPLE,
        "boundary_example": BOUNDARY_EXAMPLE,
        "softmax_example": SOFTMAX_EXAMPLE,
        "sigmoid": sigmoid,
        "logistic_fit_1d": logistic_fit_1d,
        "boundary_fits": boundary_fits,
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
