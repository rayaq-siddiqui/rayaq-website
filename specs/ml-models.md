# rayaq.ca/ml-models — a source-linked machine learning reference

**Status:** approved for build · **Owner:** Rayaq Siddiqui · **Spec version:** 2 (2026-10-08)

This is the product and technical contract for `rayaq.ca/ml-models`. The daily
implementation Routine builds and maintains the section against it. Build progress lives in
`specs/ml-models-progress.md`. Don't edit this spec without the owner's say-so. If the code
and the spec disagree, fix the code or record a deliberate deviation in the progress file.

**What changed from v1.** v1 covered ten pages about large-model architecture, all linked
only to PyTorch. On 2026-10-08 the owner widened the scope. The section now covers
everything in machine learning, organized around how someone gets from a problem and a
dataset to a model they can trust. Transformers become one model family among many. v2
adds:

- twelve subject areas (§4) and about ninety pages (§5);
- a learning path (§4.3);
- one fixed page format (§6);
- pins for scikit-learn and XGBoost beside PyTorch, plus primary papers (§3.4);
- a build order that builds the foundations, data and evaluation, and classical ML pages
  alongside the Transformer pages (§5.13).

The v1 pages keep their slugs and their "must cover" text.

---

## 1. Goal and audience

`rayaq.ca/ml-models` is where the owner goes to learn, or to refresh, anything in machine
learning. It is a static reference with hand-drawn diagrams, worked numbers and code links
pinned to exact releases. One question organizes it: *how do you get from a problem and a
dataset to a model you can trust?* The areas follow that question:

1. the math you need;
2. what learning is;
3. how you split and measure data;
4. the classical baselines;
5. how neural networks train;
6. the architectures;
7. generative models;
8. language models;
9. retrieval;
10. the systems that train and serve models;
11. the specialized settings.

The section serves two readers on the same pages:

- **A beginner** who knows Python but not ML enters through the learning path (§4.3) or any
  page marked *intro*. Every page opens with the problem it solves and an intuition, before
  any equation.
- **An expert** who needs depth skips to *Mechanics*, *Implementation* and *Tradeoffs*. They
  get exact equations, tensor shapes, parameter counts, and the lines of library code that
  implement each idea.

After reading the relevant pages, someone should be able to:

- explain each idea in plain language and then in equations;
- follow the shape of every tensor through a model;
- choose a sensible baseline and a sound evaluation for a new problem, and spot leakage;
- count a model's parameters and estimate its memory and compute cost;
- find the library code that implements each piece, at the right lines.

## 2. Non-goals

- Tutorials on Python itself, or on installing libraries.
- Leaderboards, benchmark tables, or opinions about which model or vendor is best. Tradeoff
  sections compare *approaches* on stated criteria, citing the evidence.
- Training anything at request time, or reproducing papers' experiments.
- Links into third-party *model zoo* code, for example nanoGPT or Hugging Face
  `transformers`. Code links go only to the pinned libraries in §3.4. Where none of them
  implements an idea (RoPE, a GPT block, a U-Net, HNSW), the page builds it from pinned
  primitives in a short snippet and links those primitives. It cites the paper for the idea.
- Exercises with grading, accounts, or progress tracking. "Check yourself" questions are
  allowed, as `<details>` that reveal the answer.

## 3. Hard constraints

1. **Static content.** Pages are server-rendered from committed templates. There are no
   runtime calls to GitHub, arXiv or any other service. There is no client-side fetching,
   and no JavaScript library or CDN.
2. **Small vanilla JS only.** `frontend/static/ml_models.js` may add interactivity, such as
   steppers, sliders, live tables or calculators. Every page must read fully without JS: the
   no-JS state shows a meaningful figure, and nothing is hidden behind a script.
3. **No ML packages on the server.** Never add `torch`, numpy, scikit-learn, xgboost or any
   other ML package to `backend/requirements.txt` or `requirements-dev.txt`. Never run them
   in CI or at request time; the server is an e2-micro VM. Small worked numbers, such as
   attention weights, a gradient step or a tree split, may be computed in pure Python in
   `ml_models_docs.py` and tested. Anything bigger comes from an offline script in
   `tools/ml_models/`, with its output committed as small JSON or SVG files under
   `frontend/static/ml_models/`. The progress file records the exact script, command,
   library version and seed for every committed output.
4. **Pinned sources.** The section describes exactly one stable release of each library
   below. Each pin is recorded in code (§7.3) and shown in the page footer.

   | Key | Library | Repository | Used for |
   |---|---|---|---|
   | `pytorch` | PyTorch | `pytorch/pytorch` | tensors, autograd, `nn`, optimizers, distributions, data loading, AMP, distributed, profiling, quantization, export |
   | `sklearn` | scikit-learn | `scikit-learn/scikit-learn` | classical models, preprocessing, imputation, splits, cross-validation, metrics, calibration, pipelines |
   | `xgboost` | XGBoost | `dmlc/xgboost` | gradient-boosted trees: histogram split finding, objectives, learning to rank |

   - **Links are pinned.** Every code link goes through `ml_models_docs.source_url` (PyTorch)
     or `ml_models_docs.pinned_url(key, path, start, end)` (any pin). Both pin the link to the
     tag's commit SHA. Never link `blob/main`, a branch or a bare tag.
   - **Adding a library.** A new pin (for example a vector-index library for §5.9) is an
     addition the Routine proposes in the progress file. The owner approves it before code
     links to it.
   - **Papers.** Primary papers are cited by title, authors, year and a stable URL: arXiv
     when one exists, otherwise a DOI or the publisher's page. They need no pin.
5. **Every claim is sourced.** Claims about how a library behaves must match the pinned
   source and link to it with a line range. That covers defaults, argument order, tensor
   layouts and what a function computes. Claims that are mathematics or convention cite a
   paper or a standard textbook, unless they are derivations shown in full on the page.
   Those claims include formulas, typical hyperparameters and model configurations.
6. **Never fabricate.** Copy class, function and argument names, defaults and shapes from
   source; never recall them. Every worked number is computed, in tested pure Python or by a
   recorded offline script, never estimated. When unsure, omit the claim and log the gap in
   the progress file.
7. **Licensing.**
   - Licenses: PyTorch and scikit-learn are BSD-3-Clause; XGBoost is Apache-2.0.
   - The footer credits each library a page links into and links its license file at the
     pin. The index credits all three.
   - Code excerpts stay short.
8. **Section isolation.**
   - Several Routines push to this repo. This section owns only its own files (§7.2).
   - It never edits another section's files (`/jj*`, weather, resume, assembly). That
     includes `jj.css`, which it may link but not change.
   - Shared registration points (`app.py`, `AGENTS.md`, `README.md`,
     `backend/tests/app_tests.py`, and the ml-models card in `home.html`) get additive edits
     only.
9. **Homepage card.** At the owner's request, `/` links to `/ml-models`. The card sits after
   the jj internals card and before jj-dojo. Keep it there.
10. **House rules.** Everything in `AGENTS.md` applies.

## 4. Information architecture

```
/ml-models               Index: the problem-to-model framing, the learning path, the area
                         map, the shared vocabulary, the pins, every page grouped by area
/ml-models/<slug>        One page per topic (§5), in the format of §6
```

- Every page shares one layout:
  - a section nav grouped by area;
  - a breadcrumb that names the area;
  - an on-page table of contents built from the page's `h2` and `h3` headings;
  - previous and next links;
  - a footer showing each pin the page links into: tag, commit, commit date and analysis
    date.
- Unknown slugs and pages not yet marked ready return 404. There is no catch-all.
  Headings have stable `id` anchors.

### 4.1 Areas

Areas group the pages in the nav and on the index, in this order. The order follows a
project, from the math through data and models to systems and specialized settings.

| # | Area slug | Title | Scope |
|---|---|---|---|
| 1 | `foundations` | Mathematical foundations | vectors, matrices, dot products, gradients, the chain rule, probability, distributions, expectation, Bayes' rule, entropy |
| 2 | `core-ml` | Core ML concepts | supervised, unsupervised and self-supervised learning; losses; generalization; bias–variance; overfitting; regularization |
| 3 | `data-evaluation` | Data and evaluation | splits, leakage, preprocessing, missing data, imbalance, cross-validation, metrics, calibration, uncertainty |
| 4 | `classical-ml` | Classical ML | linear and logistic regression, decision trees, random forests, gradient boosting, SVMs, nearest neighbors, clustering, PCA |
| 5 | `neural-networks` | Neural network fundamentals | layers, activations, backprop, computation graphs, initialization, normalization, optimizers, LR schedules, the training loop |
| 6 | `architectures` | Model architectures | CNNs, RNNs/LSTMs, Transformers, autoencoders, GNNs, mixture of experts, state-space models, vision transformers |
| 7 | `generative` | Generative modeling | autoregressive models, VAEs, GANs, diffusion, flow matching |
| 8 | `language-models` | Language models | tokenization, embeddings, positional encoding, attention, encoder and decoder LMs, pretraining, fine-tuning, preference optimization, decoding, KV caching |
| 9 | `retrieval` | Retrieval and recommendation | similarity search, vector indexes, ranking, collaborative filtering, two-tower models, RAG |
| 10 | `training-systems` | Training systems | GPU execution, precision, batching, distributed training, gradient accumulation, checkpointing, profiling |
| 11 | `inference` | Inference and deployment | quantization, distillation, serving, latency and throughput, monitoring and drift, reproducibility |
| 12 | `specialized` | Specialized learning | reinforcement learning, time series, causal inference, online learning, multimodal models |

### 4.2 Levels

Every page has a level, shown as a badge in the nav and on the index:

- **intro**: assumes only Python and high-school algebra, plus its listed prerequisites.
- **core**: the working knowledge an ML engineer uses daily.
- **advanced**: research-adjacent depth, such as systems internals or recent methods.

A level describes a page's entry point, not its ceiling. Even an intro page carries the
full *Mechanics* and *Implementation* sections that an expert would want.

### 4.3 The learning path

The index shows this seven-step path for someone starting from zero. Each step links to its
pages in order; a page that isn't ready yet shows as plain text.

| Step | Theme | Pages |
|---|---|---|
| 1 | Tensor shapes and matrix multiplication | `tensors-and-shapes`, `matrix-multiplication` |
| 2 | Backpropagation and optimization | `derivatives-and-gradients`, `chain-rule`, `backpropagation`, `optimizers` |
| 3 | Embeddings and attention: a tiny numeric Q/K/V example with masking | `embeddings`, `attention` |
| 4 | The full Transformer block | `layernorm-and-residuals`, `transformer` |
| 5 | Training versus inference: teacher forcing, next-token prediction, sampling, the KV cache | `training-loop`, `decoder-only-llm`, `decoding`, `kv-cache` |
| 6 | Evaluation and data leakage | `data-splits`, `data-leakage`, `classification-metrics`, `cross-validation` |
| 7 | Classical baselines | `linear-regression`, `logistic-regression`, `gradient-boosting` |

The registry stores the path as `LEARNING_PATH` (§7.4), and a test keeps it in step with
this table.

## 5. Page inventory

Every page belongs to exactly one area. The tables list pages in nav order within each
area; the build order is §5.13.

- **Source sets.** Entries name each repository by its pin key (§3.4) and give paths
  relative to that repository's root. Papers are named by short title and arXiv ID or DOI.
- **Prerequisites.** These are the slugs a reader should know first, and they drive the
  *Connections* section (§6).
- **Prerequisite cycles.** Prerequisites may point to any area. They must form no cycle,
  and a test enforces that (§7.5).

### 5.1 Mathematical foundations (`foundations`)

| Slug | Title | Level | Prerequisites | Must cover | Sources |
|---|---|---|---|---|---|
| `tensors-and-shapes` | Tensors, shapes and broadcasting | intro | — | Scalars to n-d tensors; shape, dtype, device; strides and views versus copies; reshape, transpose and permute; broadcasting rules, worked through; the batch dimension convention | `pytorch:torch/_tensor.py`, `pytorch:torch/_torch_docs.py`, `pytorch:torch/functional.py` |
| `vectors-and-dot-products` | Vectors and dot products | intro | `tensors-and-shapes` | Vectors as points and directions; norms; the dot product as projection and similarity; cosine similarity; orthogonality; why attention and retrieval both reduce to dot products | `pytorch:torch/_torch_docs.py`, `pytorch:torch/nn/modules/distance.py` |
| `matrix-multiplication` | Matrices and matrix multiplication | intro | `vectors-and-dot-products` | Matmul as many dot products; shape rules `[m,k]·[k,n]`; batched matmul and `einsum`; a linear layer as a matmul plus bias; FLOP counting (2·m·k·n); the identity, transpose and inverse | `pytorch:torch/_torch_docs.py`, `pytorch:torch/functional.py`, `pytorch:torch/nn/modules/linear.py` |
| `linear-algebra-toolkit` | Eigenvectors, SVD and low rank | core | `matrix-multiplication` | Eigen-decomposition; SVD and its geometry; rank and low-rank approximation (Eckart–Young); condition number; where they appear (PCA, LoRA, embeddings, initialization) | `pytorch:torch/linalg/__init__.py`, `pytorch:torch/_lowrank.py` |
| `derivatives-and-gradients` | Derivatives and gradients | intro | `vectors-and-dot-products` | The derivative as slope; partial derivatives; the gradient as the steepest-ascent direction; gradient descent on a 2-D bowl, worked step by step; Jacobians; `requires_grad` and `.grad` | `pytorch:torch/autograd/__init__.py`, `pytorch:torch/_tensor.py` |
| `chain-rule` | The chain rule | intro | `derivatives-and-gradients`, `matrix-multiplication` | Composing functions; the scalar chain rule, then its vector-Jacobian form; forward versus reverse mode and why ML uses reverse; a hand-differentiated two-layer example checked against autograd | `pytorch:torch/autograd/function.py`, `pytorch:torch/autograd/__init__.py` |
| `probability-and-distributions` | Probability and distributions | intro | — | Events, random variables, PMF and PDF; Bernoulli, categorical, Gaussian; joint, marginal and conditional; independence; sampling; `torch.distributions` | `pytorch:torch/distributions/normal.py`, `pytorch:torch/distributions/categorical.py`, `pytorch:torch/distributions/bernoulli.py` |
| `expectation-and-variance` | Expectation, variance and sampling | intro | `probability-and-distributions` | Expectation and linearity; variance and standard deviation; covariance; the law of large numbers and Monte Carlo estimates; the central limit theorem; why minibatch gradients are unbiased but noisy | `pytorch:torch/random.py`, `pytorch:torch/distributions/normal.py` |
| `bayes-rule` | Bayes' rule and likelihood | core | `probability-and-distributions` | Bayes' rule with a worked diagnostic-test example; likelihood versus probability; maximum likelihood; MAP estimation and priors as regularizers; naive Bayes | `pytorch:torch/distributions/distribution.py`, `sklearn:sklearn/naive_bayes.py` |
| `entropy-and-kl` | Entropy, cross-entropy and KL divergence | core | `probability-and-distributions`, `expectation-and-variance` | Information content; entropy; cross-entropy and why it is the classification loss; KL divergence and its asymmetry; perplexity; mutual information | `pytorch:torch/distributions/kl.py`, `pytorch:torch/nn/modules/loss.py`, `pytorch:torch/nn/functional.py` |

### 5.2 Core ML concepts (`core-ml`)

| Slug | Title | Level | Prerequisites | Must cover | Sources |
|---|---|---|---|---|---|
| `learning-paradigms` | Supervised, unsupervised and self-supervised learning | intro | — | The three setups with an example each; what the label is in each; semi-supervised and weak supervision; how self-supervision powers pretraining (masked and next-token objectives); the estimator API (`fit`/`predict`) | `sklearn:sklearn/base.py`, `sklearn:sklearn/cluster/_kmeans.py`, `pytorch:torch/nn/modules/loss.py` |
| `loss-functions` | Loss functions | intro | `entropy-and-kl` | Losses as negative log-likelihoods; MSE, MAE and Huber; binary and categorical cross-entropy over logits; hinge; ranking and contrastive losses; reduction and `ignore_index`; choosing a loss | `pytorch:torch/nn/modules/loss.py`, `pytorch:torch/nn/functional.py` |
| `generalization` | Generalization | intro | `learning-paradigms`, `loss-functions` | Empirical versus true risk; the i.i.d. assumption; the train/test gap; model capacity; distribution shift as the enemy of generalization; double descent | `sklearn:sklearn/model_selection/_split.py`, `sklearn:sklearn/model_selection/_validation.py` |
| `bias-variance` | The bias–variance tradeoff | core | `generalization`, `expectation-and-variance` | The decomposition of expected squared error, derived; a polynomial-fit worked example; learning and validation curves; how ensembles trade variance | `sklearn:sklearn/model_selection/_validation.py` |
| `overfitting` | Overfitting and underfitting | intro | `generalization` | Diagnosing each from training and validation curves; remedies (data, capacity, regularization, early stopping); memorization in deep nets | `sklearn:sklearn/model_selection/_validation.py`, `sklearn:sklearn/tree/_classes.py` |
| `regularization` | Regularization | core | `overfitting`, `loss-functions` | L2 (ridge, weight decay) and L1 (lasso, sparsity), geometrically; elastic net; dropout; early stopping; data augmentation; label smoothing; weight decay versus L2 under Adam | `sklearn:sklearn/linear_model/_ridge.py`, `sklearn:sklearn/linear_model/_coordinate_descent.py`, `pytorch:torch/nn/modules/dropout.py`, `pytorch:torch/optim/adamw.py` |

### 5.3 Data and evaluation (`data-evaluation`)

| Slug | Title | Level | Prerequisites | Must cover | Sources |
|---|---|---|---|---|---|
| `data-splits` | Train, validation and test splits | intro | `generalization` | Why three splits; split sizes; stratified, grouped and time-ordered splits; when a random split lies; `train_test_split` and its arguments | `sklearn:sklearn/model_selection/_split.py` |
| `data-leakage` | Data leakage | core | `data-splits`, `preprocessing` | Target leakage, train–test contamination and temporal leakage, each with a concrete example; fitting a preprocessor on all the data; duplicates across splits; using a `Pipeline` to prevent it; a leakage checklist | `sklearn:sklearn/pipeline.py`, `sklearn:sklearn/model_selection/_split.py` |
| `preprocessing` | Preprocessing and feature scaling | intro | `tensors-and-shapes` | Standardization and min-max scaling; one-hot and ordinal encoding; log transforms; why scale matters for gradient descent, k-NN and SVMs but not for trees; `fit` versus `transform` | `sklearn:sklearn/preprocessing/_data.py`, `sklearn:sklearn/preprocessing/_encoders.py` |
| `missing-data` | Missing data | core | `preprocessing` | MCAR, MAR and MNAR; deletion; mean, median and constant imputation; iterative imputation; missing-indicator features; how gradient-boosted trees route missing values natively | `sklearn:sklearn/impute/_base.py`, `sklearn:sklearn/impute/_iterative.py`, `xgboost:src/tree/hist/evaluate_splits.h` |
| `class-imbalance` | Class imbalance | core | `classification-metrics` | Why accuracy misleads; class weights; resampling; threshold moving; focal loss; which metrics to use instead | `sklearn:sklearn/utils/class_weight.py`, `pytorch:torch/nn/modules/loss.py` |
| `cross-validation` | Cross-validation | core | `data-splits` | k-fold, stratified, group and time-series splitters; nested CV for model selection; variance of CV estimates; `cross_validate` | `sklearn:sklearn/model_selection/_split.py`, `sklearn:sklearn/model_selection/_validation.py` |
| `classification-metrics` | Classification metrics | intro | `data-splits` | The confusion matrix; accuracy, precision, recall and F1; ROC and AUC; PR curves and average precision; log loss; choosing a threshold; micro versus macro averaging | `sklearn:sklearn/metrics/_classification.py`, `sklearn:sklearn/metrics/_ranking.py` |
| `regression-metrics` | Regression metrics | intro | `loss-functions` | MSE, RMSE, MAE, R² and MAPE; how outliers move each one; quantile (pinball) loss; matching the metric to the decision | `sklearn:sklearn/metrics/_regression.py` |
| `calibration` | Calibration | core | `classification-metrics` | What a calibrated probability is; reliability diagrams; ECE and Brier score; Platt scaling, isotonic regression and temperature scaling; why modern nets are overconfident | `sklearn:sklearn/calibration.py`, `sklearn:sklearn/metrics/_classification.py`, paper *On Calibration of Modern Neural Networks* (arXiv 1706.04599) |
| `uncertainty` | Uncertainty | advanced | `calibration`, `bayes-rule` | Aleatoric versus epistemic uncertainty; bootstrap confidence intervals; ensembles and MC dropout; conformal prediction with a worked coverage example | `sklearn:sklearn/ensemble/_bagging.py`, `pytorch:torch/nn/modules/dropout.py`, papers *Deep Ensembles* (arXiv 1612.01474) and *A Gentle Introduction to Conformal Prediction* (arXiv 2107.07511) |

### 5.4 Classical ML (`classical-ml`)

| Slug | Title | Level | Prerequisites | Must cover | Sources |
|---|---|---|---|---|---|
| `linear-regression` | Linear regression | intro | `matrix-multiplication`, `loss-functions` | The model and squared loss; the normal equations, derived; gradient descent on the same problem; ridge and lasso; residual plots; interpreting coefficients; `LinearRegression`'s solver | `sklearn:sklearn/linear_model/_base.py`, `sklearn:sklearn/linear_model/_ridge.py` |
| `logistic-regression` | Logistic regression | intro | `linear-regression`, `entropy-and-kl` | The sigmoid and log-odds; the cross-entropy loss and its gradient; the decision boundary; multinomial softmax regression; regularization `C`; solvers; the neural-net view as one linear layer | `sklearn:sklearn/linear_model/_logistic.py`, `pytorch:torch/nn/modules/linear.py` |
| `decision-trees` | Decision trees | intro | `classification-metrics` | Recursive splitting; Gini and entropy, with a worked split; regression trees; stopping and pruning (`max_depth`, `min_samples_leaf`, cost-complexity); feature importance and its caveats | `sklearn:sklearn/tree/_classes.py`, `sklearn:sklearn/tree/_criterion.pyx`, `sklearn:sklearn/tree/_splitter.pyx` |
| `random-forests` | Random forests | core | `decision-trees`, `bias-variance` | Bagging and feature subsampling; why averaging reduces variance; out-of-bag error; permutation importance; extra trees | `sklearn:sklearn/ensemble/_forest.py`, `sklearn:sklearn/ensemble/_bagging.py` |
| `gradient-boosting` | Gradient boosting | core | `decision-trees`, `derivatives-and-gradients` | Boosting as gradient descent in function space; fitting residuals; shrinkage; second-order (Newton) boosting and XGBoost's split gain and regularized leaf weight, derived; histogram binning; missing-value routing; early stopping; the main hyperparameters | `sklearn:sklearn/ensemble/_gb.py`, `sklearn:sklearn/ensemble/_hist_gradient_boosting/gradient_boosting.py`, `xgboost:src/tree/updater_quantile_hist.cc`, `xgboost:src/tree/hist/evaluate_splits.h`, `xgboost:python-package/xgboost/training.py`, paper *XGBoost* (arXiv 1603.02754) |
| `support-vector-machines` | Support vector machines | core | `logistic-regression`, `vectors-and-dot-products` | The max-margin idea; hinge loss; soft margin `C`; the dual and support vectors; kernels and the kernel trick; RBF `gamma`; scaling needs | `sklearn:sklearn/svm/_classes.py`, `sklearn:sklearn/svm/_base.py` |
| `nearest-neighbors` | Nearest neighbors | intro | `vectors-and-dot-products`, `preprocessing` | k-NN classification and regression; distance metrics; choosing k; the curse of dimensionality; KD-trees and ball trees | `sklearn:sklearn/neighbors/_classification.py`, `sklearn:sklearn/neighbors/_unsupervised.py`, `sklearn:sklearn/neighbors/_ball_tree.pyx.tp` |
| `clustering` | Clustering | intro | `nearest-neighbors` | k-means (Lloyd's algorithm, k-means++, inertia); choosing k; DBSCAN; Gaussian mixtures; evaluating clusters | `sklearn:sklearn/cluster/_kmeans.py`, `sklearn:sklearn/cluster/_dbscan.py`, `sklearn:sklearn/mixture/_gaussian_mixture.py` |
| `pca` | Principal component analysis | core | `linear-algebra-toolkit`, `preprocessing` | Variance-maximizing directions; PCA via SVD; explained variance; whitening; reconstruction; t-SNE and UMAP as nonlinear alternatives, and their caveats | `sklearn:sklearn/decomposition/_pca.py`, `pytorch:torch/_lowrank.py` |

### 5.5 Neural network fundamentals (`neural-networks`)

| Slug | Title | Level | Prerequisites | Must cover | Sources |
|---|---|---|---|---|---|
| `neurons-and-layers` | Neurons, layers and the MLP | intro | `matrix-multiplication`, `logistic-regression` | A neuron as logistic regression; stacking layers; why nonlinearity is needed; universal approximation; `nn.Module`, `nn.Linear`, `nn.Sequential`; parameter counting for an MLP | `pytorch:torch/nn/modules/linear.py`, `pytorch:torch/nn/modules/container.py`, `pytorch:torch/nn/modules/module.py` |
| `activation-functions` | Activation functions | intro | `neurons-and-layers` | Sigmoid, tanh, ReLU, leaky ReLU, GELU, SiLU/Swish and gated variants (GLU, SwiGLU); saturation and dead units; plots of each function and its derivative | `pytorch:torch/nn/modules/activation.py`, `pytorch:torch/nn/functional.py` |
| `backpropagation` | Backpropagation | core | `chain-rule`, `neurons-and-layers` | Forward pass, loss, backward pass on a two-layer MLP with every number shown; local gradients per op; vanishing and exploding gradients; gradient checking | `pytorch:torch/autograd/__init__.py`, `pytorch:torch/autograd/function.py` |
| `computation-graphs` | Computation graphs and autograd | core | `backpropagation` | The dynamic graph PyTorch records; `grad_fn` and `next_functions`; leaf tensors; `retain_graph`, `no_grad` and `detach`; custom `autograd.Function`; hooks | `pytorch:torch/autograd/graph.py`, `pytorch:torch/autograd/function.py`, `pytorch:torch/_tensor.py` |
| `initialization` | Weight initialization | core | `backpropagation`, `expectation-and-variance` | Why scale matters (variance propagation, derived); Xavier/Glorot and Kaiming/He; PyTorch's default `Linear` init; orthogonal init; scaled residual init in deep transformers | `pytorch:torch/nn/init.py`, `pytorch:torch/nn/modules/linear.py` |
| `layernorm-and-residuals` | Normalization and residual connections | core | `backpropagation` | What a residual stream is; BatchNorm (train versus eval, running stats); LayerNorm's computation and its learned scale and bias; RMSNorm; GroupNorm; pre-norm versus post-norm and why deep models prefer pre-norm; dropout placement; the feed-forward block | `pytorch:torch/nn/modules/normalization.py`, `pytorch:torch/nn/modules/batchnorm.py`, `pytorch:torch/nn/functional.py`, `pytorch:torch/nn/modules/transformer.py` |
| `optimizers` | Optimizers: SGD to AdamW | core | `derivatives-and-gradients`, `backpropagation` | SGD and minibatches; momentum and Nesterov; RMSProp; Adam's moment estimates and bias correction, with a worked step; AdamW's decoupled weight decay; optimizer state memory; `Optimizer.step` and `zero_grad` | `pytorch:torch/optim/sgd.py`, `pytorch:torch/optim/adam.py`, `pytorch:torch/optim/adamw.py`, `pytorch:torch/optim/optimizer.py` |
| `learning-rate-schedules` | Learning-rate schedules | core | `optimizers` | Why the learning rate dominates; step, exponential and cosine decay; linear warmup and why transformers need it; one-cycle; LR range tests; composing schedulers | `pytorch:torch/optim/lr_scheduler.py` |
| `training-loop` | The training loop | intro | `optimizers`, `loss-functions` | Cross-entropy loss over logits (shapes, `ignore_index`, label smoothing); the backward pass; gradient clipping; AdamW (the update rule, decoupled weight decay, which parameters get decay); learning-rate warmup and cosine decay with PyTorch's schedulers; mixed precision with `autocast` and `GradScaler`; gradient accumulation; train versus eval mode; teacher forcing; memory per parameter | `pytorch:torch/nn/modules/loss.py`, `pytorch:torch/optim/adamw.py`, `pytorch:torch/optim/lr_scheduler.py`, `pytorch:torch/amp/autocast_mode.py`, `pytorch:torch/amp/grad_scaler.py`, `pytorch:torch/nn/utils/clip_grad.py` |

### 5.6 Model architectures (`architectures`)

| Slug | Title | Level | Prerequisites | Must cover | Sources |
|---|---|---|---|---|---|
| `cnns` | Convolutional networks | core | `neurons-and-layers` | Convolution as a sliding dot product; kernels, stride, padding, dilation and the output-size formula; channels; pooling; receptive fields; parameter sharing; a LeNet/ResNet-style stack with shapes; residual blocks | `pytorch:torch/nn/modules/conv.py`, `pytorch:torch/nn/modules/pooling.py`, papers *ResNet* (arXiv 1512.03385) |
| `rnns-and-lstms` | RNNs and LSTMs | core | `backpropagation` | The recurrence; backprop through time and vanishing gradients; LSTM gates, derived; GRU; sequence-to-sequence with attention as the bridge to Transformers; packed sequences | `pytorch:torch/nn/modules/rnn.py`, `pytorch:torch/nn/utils/rnn.py` |
| `transformer` | The Transformer | core | `attention`, `layernorm-and-residuals` | The full encoder-decoder from *Attention Is All You Need* (Vaswani et al., 2017): embeddings and scaling by √d_model, positional encoding, encoder layer (self-attention, feed-forward, residual + LayerNorm), decoder layer (masked self-attention, cross-attention, feed-forward), the output projection and softmax; post-norm versus `norm_first`; how `nn.Transformer`, `TransformerEncoder(Layer)` and `TransformerDecoder(Layer)` map onto the paper, every constructor argument and default, `batch_first`, `generate_square_subsequent_mask`; the base-model parameter count | `pytorch:torch/nn/modules/transformer.py`, `pytorch:torch/nn/modules/activation.py`, `pytorch:torch/nn/modules/normalization.py`, `pytorch:torch/nn/modules/sparse.py`, `pytorch:torch/nn/modules/linear.py` |
| `autoencoders` | Autoencoders | core | `neurons-and-layers` | Encoder, bottleneck, decoder; reconstruction loss; undercomplete, denoising and sparse variants; the latent space; the link to PCA and to VAEs | `pytorch:torch/nn/modules/linear.py`, `pytorch:torch/nn/modules/conv.py` |
| `graph-neural-networks` | Graph neural networks | advanced | `neurons-and-layers`, `matrix-multiplication` | Graphs as adjacency and feature matrices; message passing; GCN's normalized propagation, derived; GraphSAGE and GAT; over-smoothing; batching graphs; a snippet with `index_add_`/`scatter` | `pytorch:torch/_torch_docs.py`, `pytorch:torch/_tensor.py`, papers *GCN* (arXiv 1609.02907), *GAT* (arXiv 1710.10903) |
| `vision-transformer` | Vision Transformer | core | `transformer`, `cnns` | ViT: cutting an image into patches, patch embedding as a strided `Conv2d`, the class token, learned position embeddings, the encoder, the classification head; shapes from `[batch, 3, 224, 224]` to `[batch, 197, 768]`; ViT-B/16 parameter count | `pytorch:torch/nn/modules/conv.py`, `pytorch:torch/nn/modules/transformer.py`, `pytorch:torch/nn/modules/flatten.py`, paper *ViT* (arXiv 2010.11929) |
| `mixture-of-experts` | Mixture of experts | advanced | `transformer` | Replacing the feed-forward block with E experts and a router; top-k gating, softmax over selected experts, load-balancing auxiliary loss, capacity and dropped tokens; total versus active parameters; a reference snippet from primitives (`topk`, `scatter`/index ops, `ModuleList`) | `pytorch:torch/nn/modules/container.py`, `pytorch:torch/nn/modules/linear.py`, `pytorch:torch/nn/functional.py`, papers *Switch Transformers* (arXiv 2101.03961) |
| `state-space-models` | State-space models | advanced | `rnns-and-lstms`, `transformer` | Continuous state-space equations and discretization; the recurrence/convolution duality; S4's structured state matrix; Mamba's input-dependent selection and the parallel scan; linear-time inference versus attention's quadratic cost; a minimal snippet from primitives | `pytorch:torch/nn/modules/conv.py`, `pytorch:torch/functional.py`, papers *S4* (arXiv 2111.00396), *Mamba* (arXiv 2312.00752) |

### 5.7 Generative modeling (`generative`)

| Slug | Title | Level | Prerequisites | Must cover | Sources |
|---|---|---|---|---|---|
| `autoregressive-models` | Autoregressive models | core | `entropy-and-kl`, `probability-and-distributions` | Factorizing a joint distribution with the chain rule of probability; maximum likelihood by teacher forcing; exposure bias; PixelCNN and WaveNet-style causal convolutions; language models as the main case | `pytorch:torch/distributions/categorical.py`, `pytorch:torch/nn/modules/loss.py`, `pytorch:torch/nn/modules/conv.py` |
| `variational-autoencoders` | Variational autoencoders | core | `autoencoders`, `entropy-and-kl`, `bayes-rule` | The latent-variable model; the ELBO, derived; the reparameterization trick; the KL term in closed form for Gaussians; β-VAE; posterior collapse; latent diffusion's use of a VAE | `pytorch:torch/distributions/normal.py`, `pytorch:torch/distributions/kl.py`, paper *Auto-Encoding Variational Bayes* (arXiv 1312.6114) |
| `gans` | Generative adversarial networks | core | `neurons-and-layers`, `loss-functions` | The generator–discriminator game; the minimax and non-saturating losses; mode collapse; DCGAN conventions; Wasserstein loss and gradient penalty; evaluation (FID) | `pytorch:torch/nn/modules/loss.py`, `pytorch:torch/autograd/__init__.py`, papers *GAN* (arXiv 1406.2661), *WGAN-GP* (arXiv 1704.00028) |
| `diffusion-models` | Diffusion models | advanced | `variational-autoencoders`, `expectation-and-variance` | The forward noising process in closed form; the ε-prediction objective and its link to the ELBO; noise schedules; DDPM and DDIM sampling; classifier-free guidance; latent diffusion | `pytorch:torch/nn/functional.py`, `pytorch:torch/random.py`, papers *DDPM* (arXiv 2006.11239), *DDIM* (arXiv 2010.02502), *Classifier-Free Guidance* (arXiv 2207.12598) |
| `diffusion-unet` | Diffusion U-Net | advanced | `diffusion-models`, `cnns`, `attention` | The U-Net: down and up paths, skip connections, ResNet blocks with GroupNorm, timestep embeddings, self- and cross-attention at low resolutions; shapes at each resolution; DiT as the transformer alternative | `pytorch:torch/nn/modules/conv.py`, `pytorch:torch/nn/modules/normalization.py`, `pytorch:torch/nn/modules/upsampling.py`, `pytorch:torch/nn/modules/activation.py`, paper *Latent Diffusion* (arXiv 2112.10752) |
| `flow-matching` | Normalizing flows and flow matching | advanced | `diffusion-models` | Change of variables and normalizing flows; continuous-time flows and ODEs; flow matching and rectified flow objectives; how they relate to diffusion; sampling with an ODE solver | `pytorch:torch/distributions/transforms.py`, papers *Flow Matching* (arXiv 2210.02747), *Rectified Flow* (arXiv 2209.03003) |

### 5.8 Language models (`language-models`)

| Slug | Title | Level | Prerequisites | Must cover | Sources |
|---|---|---|---|---|---|
| `tokenization` | Tokenization | intro | — | Characters, words and subwords; byte-pair encoding worked on a toy corpus; WordPiece and unigram; byte-level BPE; special tokens; how tokenization affects cost, arithmetic and multilingual text | `pytorch:torch/nn/modules/sparse.py`, papers *BPE for NMT* (arXiv 1508.07909), *SentencePiece* (arXiv 1808.06226) |
| `embeddings` | Embeddings | intro | `tensors-and-shapes`, `vectors-and-dot-products` | An embedding as a lookup table and as a one-hot matmul; learned geometry; word2vec's objective; contextual versus static embeddings; weight tying; `nn.Embedding` and `padding_idx` | `pytorch:torch/nn/modules/sparse.py`, `pytorch:torch/nn/functional.py`, paper *word2vec* (arXiv 1301.3781) |
| `positional-encoding` | Positional encoding | core | `embeddings`, `attention` | Why attention needs position; sinusoidal encoding (formula, curves, the relative-offset property); learned absolute positions; rotary embeddings (RoPE): the 2-D rotation per frequency pair, why q·k then depends only on the offset, and a snippet built from tensor ops; ALiBi as a bias, not an embedding | `pytorch:torch/nn/modules/sparse.py`, `pytorch:torch/nn/functional.py`, `pytorch:torch/nn/modules/transformer.py`, paper *RoFormer* (arXiv 2104.09864) |
| `attention` | Attention | core | `embeddings`, `matrix-multiplication` | A tiny numeric Q/K/V example with every number shown; scaled dot-product attention step by step (QKᵀ, scaling, mask, softmax, ·V); multi-head attention and the head split/merge reshapes; padding, causal and additive versus boolean masks, and which way PyTorch's boolean masks point in each API; cross-attention; grouped-query attention; `MultiheadAttention`'s packed `in_proj_weight` and fast path; `F.scaled_dot_product_attention` and its backends; FlexAttention | `pytorch:torch/nn/functional.py`, `pytorch:torch/nn/modules/activation.py`, `pytorch:torch/nn/attention/__init__.py`, `pytorch:torch/nn/attention/bias.py`, `pytorch:torch/nn/attention/flex_attention.py` |
| `encoder-only` | Encoder-only models | core | `transformer` | The BERT-style stack: token, segment and position embeddings, bidirectional self-attention, the `[CLS]` token, masked-language-model and next-sentence objectives, padding masks, fine-tuning heads; the BERT-base parameter count | `pytorch:torch/nn/modules/transformer.py`, `pytorch:torch/nn/modules/sparse.py`, `pytorch:torch/nn/modules/loss.py`, paper *BERT* (arXiv 1810.04805) |
| `decoder-only-llm` | Decoder-only LLMs | core | `transformer`, `training-loop` | The GPT-style stack: token and position embeddings, N pre-norm blocks with causal self-attention, final LayerNorm, the LM head and weight tying; next-token training with teacher forcing versus autoregressive generation; the GPT-2-small parameter count worked through; building one from `TransformerEncoderLayer` with a causal mask, or from primitives | `pytorch:torch/nn/modules/transformer.py`, `pytorch:torch/nn/functional.py`, `pytorch:torch/nn/modules/sparse.py`, `pytorch:torch/nn/modules/loss.py`, paper *GPT-2* (OpenAI 2019) |
| `pretraining` | Pretraining and scaling laws | advanced | `decoder-only-llm` | Pretraining objectives (causal LM, masked LM, span corruption); data mixtures and deduplication; compute = 6·N·D, derived; Kaplan and Chinchilla scaling laws; compute-optimal model size, worked; emergent-ability caveats | `pytorch:torch/nn/modules/loss.py`, papers *Scaling Laws* (arXiv 2001.08361), *Chinchilla* (arXiv 2203.15556) |
| `fine-tuning` | Fine-tuning and LoRA | core | `decoder-only-llm`, `linear-algebra-toolkit` | Full fine-tuning versus feature extraction; instruction tuning; catastrophic forgetting; LoRA's low-rank update, derived, with a parameter count; QLoRA; adapters and prefix tuning; a LoRA snippet with `parametrize` | `pytorch:torch/nn/utils/parametrize.py`, `pytorch:torch/nn/modules/linear.py`, papers *LoRA* (arXiv 2106.09685), *QLoRA* (arXiv 2305.14314) |
| `preference-optimization` | Preference optimization: RLHF and DPO | advanced | `fine-tuning`, `reinforcement-learning` | Reward modeling from pairwise preferences (Bradley–Terry); RLHF with PPO and a KL penalty; DPO's closed-form loss, derived; variants (IPO, KTO, GRPO); reward hacking | `pytorch:torch/nn/functional.py`, papers *InstructGPT* (arXiv 2203.02155), *DPO* (arXiv 2305.18290) |
| `decoding` | Decoding and sampling | core | `decoder-only-llm`, `probability-and-distributions` | Greedy and beam search; temperature with a worked softmax; top-k and top-p (nucleus); repetition penalties; constrained decoding; speculative decoding | `pytorch:torch/distributions/categorical.py`, `pytorch:torch/_torch_docs.py`, papers *Nucleus Sampling* (arXiv 1904.09751), *Speculative Decoding* (arXiv 2211.17192) |
| `kv-cache` | The KV cache | advanced | `attention`, `decoding` | Why decoding recomputes keys and values without a cache; prefill versus decode; cache shape and memory per token, worked for a real configuration; multi-query and grouped-query attention as cache savers; paged attention | `pytorch:torch/nn/functional.py`, `pytorch:torch/nn/modules/activation.py`, papers *MQA* (arXiv 1911.02150), *GQA* (arXiv 2305.13245), *PagedAttention* (arXiv 2309.06180) |

### 5.9 Retrieval and recommendation (`retrieval`)

| Slug | Title | Level | Prerequisites | Must cover | Sources |
|---|---|---|---|---|---|
| `similarity-search` | Similarity search | intro | `vectors-and-dot-products`, `nearest-neighbors` | Exact k-NN search; cosine versus dot product versus L2 and when they agree; normalizing embeddings; brute-force cost; BM25 as the lexical baseline; hybrid search | `pytorch:torch/nn/modules/distance.py`, `sklearn:sklearn/neighbors/_unsupervised.py` |
| `vector-indexes` | Vector indexes | advanced | `similarity-search`, `clustering` | Approximate nearest neighbors; IVF (k-means partitions); product quantization; HNSW graphs; recall versus latency versus memory; tuning knobs | `sklearn:sklearn/cluster/_kmeans.py`, papers *HNSW* (arXiv 1603.09320), *Product Quantization* (DOI 10.1109/TPAMI.2010.57) |
| `learning-to-rank` | Learning to rank | core | `classification-metrics`, `gradient-boosting` | Pointwise, pairwise and listwise losses; NDCG and MRR; LambdaRank/LambdaMART; XGBoost's ranking objectives | `xgboost:src/objective/lambdarank_obj.cc`, `sklearn:sklearn/metrics/_ranking.py` |
| `collaborative-filtering` | Collaborative filtering | core | `linear-algebra-toolkit`, `embeddings` | The user–item matrix; neighborhood methods; matrix factorization and its loss; implicit feedback; cold start; NMF | `sklearn:sklearn/decomposition/_nmf.py`, `pytorch:torch/nn/modules/sparse.py` |
| `two-tower-models` | Two-tower models | core | `collaborative-filtering`, `similarity-search` | Separate query and item encoders; in-batch negatives and the sampled softmax; hard negatives; serving with a vector index; retrieval then ranking | `pytorch:torch/nn/modules/sparse.py`, `pytorch:torch/nn/functional.py` |
| `retrieval-augmented-generation` | Retrieval-augmented generation | advanced | `two-tower-models`, `decoder-only-llm` | Chunking; dense and hybrid retrieval; re-ranking; prompt assembly; evaluating retrieval and generation separately; failure modes | `pytorch:torch/nn/functional.py`, paper *RAG* (arXiv 2005.11401) |

### 5.10 Training systems (`training-systems`)

| Slug | Title | Level | Prerequisites | Must cover | Sources |
|---|---|---|---|---|---|
| `gpu-execution` | How a GPU runs a model | core | `matrix-multiplication` | Kernels, streams and asynchronous execution; memory hierarchy; arithmetic intensity and the roofline; why matmul is fast and elementwise ops are memory-bound; kernel fusion; `torch.compile` in one paragraph | `pytorch:torch/cuda/__init__.py`, `pytorch:torch/cuda/streams.py` |
| `mixed-precision` | Precision and mixed precision | core | `gpu-execution` | fp32, tf32, fp16, bf16 and fp8 bit layouts; range versus precision; autocast's op lists; loss scaling and why bf16 needs none; master weights | `pytorch:torch/amp/autocast_mode.py`, `pytorch:torch/amp/grad_scaler.py`, paper *Mixed Precision Training* (arXiv 1710.03740) |
| `data-loading-and-batching` | Data loading and batching | intro | `tensors-and-shapes` | `Dataset` and `DataLoader`; workers, pinning and prefetch; collation and padding; samplers; sequence packing and bucketing; batch size versus learning rate | `pytorch:torch/utils/data/dataloader.py`, `pytorch:torch/utils/data/dataset.py`, `pytorch:torch/utils/data/sampler.py` |
| `gradient-accumulation` | Gradient accumulation | core | `training-loop` | Simulating a large batch; loss normalization across micro-batches; interaction with normalization layers and clipping; `no_sync` under DDP | `pytorch:torch/optim/optimizer.py`, `pytorch:torch/nn/parallel/distributed.py` |
| `distributed-training` | Distributed training | advanced | `gradient-accumulation`, `gpu-execution` | Data parallelism and all-reduce; DDP's buckets; sharded data parallelism (ZeRO, FSDP); tensor and pipeline parallelism; memory per GPU, worked; communication cost | `pytorch:torch/nn/parallel/distributed.py`, `pytorch:torch/distributed/fsdp/__init__.py`, papers *ZeRO* (arXiv 1910.02054), *Megatron-LM* (arXiv 1909.08053) |
| `checkpointing` | Checkpointing | core | `training-loop` | Saving and resuming state (model, optimizer, scheduler, RNG, data position); `state_dict`; `weights_only` loading safety; distributed checkpoints; activation checkpointing as a memory-for-compute trade | `pytorch:torch/serialization.py`, `pytorch:torch/utils/checkpoint.py`, `pytorch:torch/distributed/checkpoint/__init__.py` |
| `profiling` | Profiling | core | `gpu-execution` | Measuring correctly (synchronization, warmup); the PyTorch profiler and traces; finding data-loader stalls, host overhead and memory spikes; MFU, worked | `pytorch:torch/profiler/profiler.py`, `pytorch:torch/cuda/__init__.py` |

### 5.11 Inference and deployment (`inference`)

| Slug | Title | Level | Prerequisites | Must cover | Sources |
|---|---|---|---|---|---|
| `quantization` | Quantization | core | `mixed-precision` | Affine quantization (scale and zero point), worked; per-tensor versus per-channel; post-training versus quantization-aware training; weight-only int8 and int4 for LLMs; outliers | `pytorch:torch/ao/quantization/quantize.py`, papers *LLM.int8()* (arXiv 2208.07339), *GPTQ* (arXiv 2210.17323) |
| `distillation` | Knowledge distillation | core | `entropy-and-kl`, `training-loop` | Soft targets and temperature; the distillation loss, derived; feature distillation; distilling LLMs on teacher outputs | `pytorch:torch/nn/modules/loss.py`, paper *Distilling the Knowledge in a Neural Network* (arXiv 1503.02531) |
| `model-serving` | Model serving | core | `gpu-execution` | Exporting a model; eager versus compiled versus exported graphs; dynamic and continuous batching; CPU versus GPU serving; a serving checklist | `pytorch:torch/export/__init__.py`, `pytorch:torch/serialization.py` |
| `latency-and-throughput` | Latency and throughput | core | `model-serving`, `kv-cache` | Time-to-first-token and inter-token latency; throughput versus latency under batching; tail latency; Little's law, worked; memory-bound decoding | `pytorch:torch/profiler/profiler.py`, `pytorch:torch/cuda/streams.py` |
| `monitoring-and-drift` | Monitoring and drift | core | `classification-metrics`, `calibration` | Covariate, label and concept drift; monitoring inputs, predictions and outcomes; PSI and KS tests, worked; delayed labels; retraining triggers | `sklearn:sklearn/metrics/_classification.py`, `sklearn:sklearn/calibration.py` |
| `reproducibility` | Reproducibility | intro | `training-loop` | Seeds (Python, NumPy, torch, data-loader workers); nondeterministic kernels and `use_deterministic_algorithms`; `random_state` in scikit-learn; versioning data, code and environment | `pytorch:torch/random.py`, `pytorch:torch/utils/data/dataloader.py`, `sklearn:sklearn/utils/validation.py` |

### 5.12 Specialized learning (`specialized`)

| Slug | Title | Level | Prerequisites | Must cover | Sources |
|---|---|---|---|---|---|
| `reinforcement-learning` | Reinforcement learning | core | `probability-and-distributions`, `optimizers` | MDPs, returns and discounting; value functions and the Bellman equation; Q-learning and DQN; policy gradients (REINFORCE, derived); actor–critic; PPO's clipped objective | `pytorch:torch/distributions/categorical.py`, papers *DQN* (arXiv 1312.5602), *PPO* (arXiv 1707.06347) |
| `time-series` | Time series | core | `cross-validation`, `rnns-and-lstms` | Trend, seasonality and autocorrelation; lag features; time-ordered validation (`TimeSeriesSplit`); classical baselines (naive, ARIMA in brief); gradient boosting on lags; sequence models; forecast metrics | `sklearn:sklearn/model_selection/_split.py`, `pytorch:torch/nn/modules/rnn.py` |
| `causal-inference` | Causal inference | advanced | `bayes-rule`, `logistic-regression` | Correlation versus causation; potential outcomes; confounding and DAGs; randomized experiments; propensity scores and inverse weighting, worked; difference-in-differences; uplift modeling | `sklearn:sklearn/linear_model/_logistic.py`, paper *Causal Inference in Statistics: An Overview* (Pearl 2009, DOI 10.1214/09-SS057) |
| `online-learning` | Online learning | core | `optimizers` | Learning from a stream; `partial_fit`; regret; concept drift; bandits (ε-greedy, UCB, Thompson sampling) | `sklearn:sklearn/linear_model/_stochastic_gradient.py` |
| `multimodal-models` | Multimodal models | advanced | `vision-transformer`, `two-tower-models` | Contrastive image–text pretraining (CLIP's loss, derived); vision-language models with an image encoder and an LLM; cross-attention versus token concatenation; audio tokens | `pytorch:torch/nn/functional.py`, papers *CLIP* (arXiv 2103.00020), *Flamingo* (arXiv 2204.14198) |

### 5.13 Build order

The Routine builds pages in this order. It follows the learning path first, so a beginner
has a complete route early. It then covers every area breadth-first.

1. **Learning path.** In this order:
   - math: `tensors-and-shapes`, `matrix-multiplication`, `derivatives-and-gradients`,
     `chain-rule`;
   - training: `backpropagation`, `optimizers`;
   - attention and the Transformer: `embeddings`, `attention`, `layernorm-and-residuals`,
     then retrofit `transformer` to §6;
   - training versus inference: `training-loop`, `decoder-only-llm`, `decoding`,
     `kv-cache`;
   - evaluation: `data-splits`, `data-leakage`, `classification-metrics`,
     `cross-validation`;
   - baselines: `linear-regression`, `logistic-regression`, `gradient-boosting`.
2. **Foundations and core ML.** The pages the path assumes:
   - `vectors-and-dot-products`, `probability-and-distributions`,
     `expectation-and-variance`, `entropy-and-kl`;
   - `learning-paradigms`, `loss-functions`, `generalization`, `overfitting`,
     `bias-variance`, `regularization`;
   - `preprocessing`, `neurons-and-layers`, `activation-functions`.
3. **Breadth.** One page per area, round-robin in §4.1 area order, taking each area's next
   unbuilt page in its table order, until every page is built.

The progress file holds the expanded queue. The Routine may swap two adjacent queue items
to satisfy a prerequisite and must log the swap.

**New pages.** The Routine may propose an addition, such as a page for a new method or a
new PyTorch API. It goes in the progress file as a queue row with a slug, title, area,
level, prerequisites, "must cover" and source set. It is recorded as a deliberate addition
until the owner folds it into these tables.

## 6. The page format

Every topic page has these `h2` sections, in this order, with these exact `id`s. Extra
`h2`s may sit between them, for example "Counting parameters" inside Mechanics.

| # | `id` | Heading | Contents |
|---|---|---|---|
| — | — | header | `<h1>` title and a plain-language summary, inside `<header>`, plus the level and area |
| 1 | `problem` | Problem | What problem this solves and what goes wrong without it, made concrete with an example |
| 2 | `intuition` | Intuition | The idea in plain language and pictures, before any equation |
| 3 | `mechanics` | Mechanics | The precise version: equations (in `.ml-formula` blocks), diagrams, and tensor shapes or data structures, with a component table |
| 4 | `worked-example` | Worked example | Small real numbers carried through every step. Computed by tested pure Python in `ml_models_docs.py` or a recorded offline script, never by hand |
| 5 | `implementation` | Implementation | A minimal snippet (`<pre><code>`, never executed by the site) plus links to the pinned library code that implements the idea, with line ranges |
| 6 | `tradeoffs` | Tradeoffs | When to use it, when not to, its costs, common pitfalls, and the alternatives compared on stated criteria |
| 7 | `connections` | Connections | Prerequisites, alternatives, and what to read next, rendered from the registry (§7.4) plus any prose links |
| 8 | `references` | References | Papers by title, authors, year and link; the pinned library docs used |

Every page also has these elements:

1. **Diagrams.** At least two hand-authored inline SVG diagrams. Each one:
   - has `role="img"`, a `<title>` and a `<desc>`;
   - uses the site's colour variables and works in light and dark mode;
   - scrolls sideways inside its own container on a phone instead of widening the page.
2. **Component tables.** At least one table with the columns
   **Component · Shape/Params · Meaning · Source**. Source cells link pinned code with line
   ranges. A purely mathematical page, such as `bayes-rule`, may use the column order
   **Term · Shape/Params · Meaning · Source**, linking the closest library code or the
   paper.
3. **Check yourself.** Optional `<details class="ml-quiz">` questions with revealed
   answers.
4. **Interactive figures.** Optional, using `ml_models.js`, with a static fallback (§3.2).

The v1 `transformer` page predates this format. It stays ready, and is retrofitted to these
section ids in §5.13 step 1.

## 7. Technical design

### 7.1 Routing

`app.py` gets `/ml-models` and `/ml-models/<slug>` and stays route-only. It asks
`ml_models_docs.render` for the page through `rendered_pages`, and returns 404 when it gets
`None`.

### 7.2 Files this section owns

```
backend/ml_models_docs.py              pins, URL helpers, AREAS, PAGES, LEARNING_PATH, render()
backend/tests/ml_models_docs_tests.py  section tests (§7.5)
frontend/templates/ml_models/          base.html, index.html, <slug>.html fragments
frontend/static/ml_models.css          section styles (layout reuses jj.css, linked not edited)
frontend/static/ml_models.js           optional progressive enhancement
frontend/static/ml_models/             committed offline-computed JSON/SVG
tools/ml_models/                       offline scripts that produce it (run by hand, never in CI)
specs/ml-models.md, specs/ml-models-progress.md
```

### 7.3 Upstream pins

```python
PINS = {
    "pytorch": {"name": "PyTorch", "repo": "https://github.com/pytorch/pytorch",
                "tag": "vX.Y.Z", "commit": "<40-hex sha>", "commit_date": "YYYY-MM-DD",
                "analyzed_on": "YYYY-MM-DD", "license": "BSD-3-Clause",
                "license_path": "LICENSE"},
    "sklearn": {...},   # scikit-learn, tag "X.Y.Z", license file "COPYING"
    "xgboost": {...},   # XGBoost, tag "vX.Y.Z", license Apache-2.0, file "LICENSE"
}
UPSTREAM = PINS["pytorch"]
```

- `pinned_url(key, path, start=None, end=None)` returns
  `<repo>/blob/<commit>/<path>#L<start>-L<end>`.
- `source_url(path, start, end)` stays as the PyTorch shorthand.
- Templates get `src` (PyTorch), `skl` (scikit-learn), `xgb` (XGBoost) and `pinned`.
- Each pin is the latest *stable* release on its analysis date. Release candidates, betas
  and dev tags never count.

### 7.4 Registry

- **`AREAS`** is an ordered list of `{slug, title, summary}`, as in §4.1.
- **`PAGES`** is an ordered list grouped by area, in §5 table order. Each entry has:
  - `slug`, `title`, `area`, `level` (`intro`, `core` or `advanced`) and `summary`;
  - `prerequisites`, a list of slugs;
  - `sources`, a list of `"<pin key>:<path>"`;
  - `ready`.
- **`LEARNING_PATH`** is a list of `{title, slugs}` steps, as in §4.3.

Derived from those three:

- **Navigation.** The nav, the index, the 404 allowlist and previous/next all follow
  `PAGES`. Previous/next follow `PAGES` order among ready pages.
- **Connections.** `connections(slug)` gives a page's prerequisites, and the pages that
  list it as a prerequisite ("leads to"). The *Connections* section renders them; slugs
  that aren't ready show as plain text.
- **Unready pages.** Pages not yet ready show in the nav and on the index without a link,
  marked "In progress".

### 7.5 Tests (`backend/tests/ml_models_docs_tests.py`, plus `app_tests.py` additions)

- **Pins.** Every pin is well formed: a known repository, a stable-release tag, a 40-hex
  commit, ISO dates with the commit date on or before the analysis date, and a license.
- **URL helpers.** `pinned_url` and `source_url` are pinned to the commit and format line
  ranges.
- **Registry.**
  - Every area has at least one page.
  - Every page's area exists, and its level is valid.
  - Every source names a known pin key.
  - Every prerequisite is a real slug, and prerequisites form no cycle.
  - Every learning-path slug is a real page.
- **Routes.** `/ml-models` and every ready page return 200. Unknown slugs and slugs not yet
  ready return 404.
- **Templates.** Every ready page has a template, a summary and at least one source.
- **Links.**
  - Every GitHub link into a pinned repository uses that pin's commit. There is no
    `blob/main`.
  - Every internal `/ml-models…` link resolves.
- **Page content.** Every ready topic page has:
  - the §6 section ids, in order (the v1 `transformer` page is exempt until it is
    retrofitted);
  - at least two inline SVGs with `<title>` and `<desc>`;
  - a §6 table;
  - a code snippet.
- **Index.** It shows every area, every page title and the learning path.
- **Static only.** No page loads a script or stylesheet from another origin.
- **No ML packages.** Neither requirements file names `torch` or any other ML package.

## 8. The daily Routine

A Routine ("rayaq.ca/ml-models — architecture reference agent") runs once a day. Each run:

1. **Starts clean.** It syncs with `origin/main` (`git pull`), then reads `AGENTS.md`, this
   spec and the progress file.
2. **Clones the pinned upstreams.** It makes shallow, sparse clones of each pin at its tag,
   in a scratch directory, and checks out only the paths the next page needs. It verifies
   every path and line range against those clones before linking.
3. **Builds.** It builds the next queued page completely, to §6, one page per run, in §5.13
   order. It adds any pure-Python worked-example helper, with tests, and marks the page
   `"ready": True`. If a run finishes its page with time to spare, it may start the next
   page, but it never pushes a half-built page as ready.
4. **Maintains.** It does this every run, after building, and as the whole run once the
   queue is empty:
   - It checks each pin for a newer stable release.
   - When one exists, it diffs every file the ready pages link to, between the old and new
     tag. It updates the line ranges and claims that changed, moves that pin, and records
     the change in the progress file. If nothing linked changed, it moves the pin and
     records "no relevant upstream change".
   - It also fixes any gap logged in the progress file that it can now close.
5. **Records.** It updates the progress file:
   - the queue and the pins;
   - each committed offline output, with its script, command, version and seed;
   - verified line ranges, deviations, open gaps, and a row for this run.
6. **Checks before every push.** It:
   - runs the full test suite;
   - starts the app and curls `/health`, `/ml-models` and every ready page;
   - checks for horizontal overflow at 390px in headless Chromium;
   - stops the app.
7. **Pushes.** It pushes straight to `main` in several small commits, each with an
   `ml-models: <lowercase imperative>` subject and a body explaining the change. It uses no
   branches, pull requests, force-pushes or history rewrites. If the push is rejected, it
   pulls with a rebase onto its own unpushed commits, re-runs the checks, and pushes again.

## 9. Acceptance criteria

- [ ] `/ml-models` renders the problem-to-model framing, the learning path, the area map and
      every page grouped by area.
- [ ] Every §5 page exists, meets its "Must cover" column and §6, and is registered.
- [ ] Every code link is pinned to its library's commit (tested).
- [ ] §7.5 tests exist and pass.
- [ ] No ML package in requirements; offline data has its script and seed recorded.
- [ ] Mobile at 390px: no horizontal page scroll; diagrams scroll inside their container.
- [ ] The Routine has run at least once in maintenance mode.
