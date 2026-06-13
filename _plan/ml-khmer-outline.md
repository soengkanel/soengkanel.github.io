# ML Khmer Series — Topic Coverage Outline

Internal planning doc. Not published. Source: canonical ML curriculum (general knowledge from Strang, Bishop, Goodfellow, Murphy, CS229, CS231n, MIT 6.036, etc.). Chapter ordering follows standard ML pedagogy.

**Lesson template (10 sections):** សង្ខេប • ហេតុអ្វីសំខាន់? • ពាក្យបច្ចេកទេសថ្មី • គំនិតវិចារណញ្ញាណ • និយមន័យ និងគណិតវិទ្យា • ឧទាហរណ៍ • កូដ Python • ការអនុវត្តន៍ជាក់ស្តែង • លំហាត់ • មេរៀនបន្ទាប់

**Terminology:** Use "lesson" / មេរៀន. Title: `[ML Khmer] ជំពូក N: <topic>` (split lessons use `Na`, `Nb`, etc.)

**Status legend:** ✅ deployed • 🟡 partial (needs gap-fill or rewrite) • ⬜ not started

---

## Part 0 — Introduction

### Ch 0 — បុព្វកថា (Preface) ✅ 1 lesson
*Deployed as Lesson 1.*

---

## Part I — គណិតវិទ្យាមូលដ្ឋាន (Math foundations)

### Ch 1 — ពិជគណិតលីនេអ៊ែរ (Linear algebra) 🟡 → 4 lessons
- **1a** (✅ partial deployed as Lesson 2): notation, vectors, dot product, matrix basics, transpose, matrix multiplication
- **1b** ⬜: identity, zero, diagonal, triangular, symmetric matrices • inverse • pseudo-inverse • determinant
- **1c** ⬜: linear independence, span, basis • rank • range, null space • orthogonality, orthogonal/orthonormal matrices • change of basis
- **1d** ⬜: eigenvalues, eigenvectors • eigendecomposition / diagonalization • positive (semi)definite matrices • vector norms ($\ell_1, \ell_2, \ell_\infty$) • Frobenius norm • trace

### Ch 2 — កាល់គុលម៉ាទ្រីស (Matrix calculus) 🟡 → 2 lessons
- **2a** (✅ partial deployed as Lesson 3): scalar derivative, partial derivative, gradient, Jacobian, key identity table, numerical gradient, autograd intro
- **2b** ⬜: chain rule (scalar, vector, matrix) • product rule • Hessian • more identity derivations ($\mathbf{x}^\top \mathbf{Ax}$, $\|\mathbf{Ax}-\mathbf{b}\|^2$, trace functions, Frobenius norm) • gradient checking proper

### Ch 3 — ប្រូបាប៊ីលីតេ (Probability) ⬜ → 2 lessons
- **3a**: sample space, axioms • conditional probability • independence • random variables • PMF/PDF/CDF • common distributions (Bernoulli, Binomial, Categorical, Multinomial, Uniform, Gaussian, Exponential, Poisson, Beta, Dirichlet)
- **3b**: joint, marginal, conditional distributions • expectation, variance, covariance, correlation • law of total probability • Bayes' theorem • information theory basics (entropy, KL divergence, cross-entropy)

### Ch 4 — MLE & MAP ⬜ → 1 lesson
Likelihood function • MLE definition • MLE for Gaussian (mean, variance) • MLE for Bernoulli, Multinomial • prior, posterior, evidence • MAP definition • MAP = MLE + regularization • intro to Bayesian inference • conjugate priors

---

## Part II — ទិដ្ឋភាពទូទៅនៃ ML (ML Overview)

### Ch 5 — ប្រភេទនៃ ML (Categories of ML) ⬜ → 1 lesson
Supervised vs unsupervised vs semi-supervised vs reinforcement • classification vs regression • generative vs discriminative • parametric vs non-parametric • online vs batch learning • overview of loss functions

### Ch 6 — Feature engineering ⬜ → 1-2 lessons
- **6a**: feature types (numeric, categorical, ordinal, text, image) • normalization & standardization • one-hot, label encoding • handling missing data • train/val/test split
- **6b** (optional): bag-of-words, TF-IDF, n-grams • image features (histograms, pixels) • feature selection • log transform, polynomial features

### Ch 7 — តំរែតំរង់លីនេអ៊ែរ (Linear regression) ⬜ → 1-2 lessons
- **7a**: problem formulation • hypothesis • MSE loss • normal equation (closed form) • gradient descent for LR • geometric interpretation (projection)
- **7b** (optional): polynomial regression • Ridge (L2) • Lasso (L1) • bias-variance tradeoff

### Ch 8 — Overfitting ⬜ → 1 lesson
Underfit vs overfit • train vs validation error curves • bias-variance decomposition • cross-validation (k-fold, LOO) • early stopping • regularization (L1, L2) • dropout • data augmentation

---

## Part III — Warmup ML

### Ch 9 — K-Nearest Neighbors (KNN) ⬜ → 1 lesson
Algorithm • distance metrics (Euclidean, Manhattan, cosine, Minkowski) • choice of K • KNN for classification & regression • weighted KNN • curse of dimensionality • KD-trees / Ball trees • sklearn example

### Ch 10 — K-Means ⬜ → 1 lesson
Clustering objective • algorithm (init, assign, update) • convergence • choosing K (elbow, silhouette) • K-Means++ • limitations • image segmentation example

### Ch 11 — Naive Bayes Classifier ⬜ → 1 lesson
Bayes refresher • naive independence assumption • Gaussian NB, Multinomial NB, Bernoulli NB • text classification (spam filter) • Laplace smoothing • log-probabilities for stability • sklearn example

---

## Part IV — Neural Networks

### Ch 12 — Gradient descent ⬜ → 2 lessons
- **12a**: optimization setup • vanilla (batch) GD • learning rate, convergence • stochastic GD • mini-batch GD • momentum • Nesterov
- **12b**: AdaGrad • RMSProp • Adam • learning rate schedules (step, cosine, warmup) • visualization & comparison

### Ch 13 — Perceptron ⬜ → 1 lesson
Binary linear classifier • perceptron learning algorithm • convergence theorem (linear separability) • XOR limitation • interpretation as single-layer neural net

### Ch 14 — Logistic regression ⬜ → 1 lesson
Binary classification • sigmoid function • hypothesis as probability • cross-entropy loss • MLE derivation • gradient + GD update • decision boundary • regularization • multiclass via OVR • sklearn example

### Ch 15 — Softmax regression ⬜ → 1 lesson
Multiclass classification • softmax function • one-hot labels • categorical cross-entropy • relationship to logistic regression (K=2) • gradient derivation • log-sum-exp trick

### Ch 16 — MLP (Multi-layer perceptron) ⬜ → 3 lessons
- **16a**: motivation (nonlinear separation) • architecture (layers, neurons, weights, biases) • activation functions (ReLU, sigmoid, tanh, softmax) • forward propagation
- **16b**: loss functions • backpropagation derivation (chain rule application step-by-step)
- **16c**: weight initialization (Xavier, He) • vanishing/exploding gradients • universal approximation theorem • full Python example (NumPy + PyTorch)

---

## Part V — ប្រព័ន្ធណែនាំ (Recommendation Systems)

### Ch 17 — Content-based RS ⬜ → 1 lesson
Setup • user profile + item features • similarity measures • item representation (TF-IDF) • linear regression per user • cold start • pros/cons

### Ch 18 — Neighborhood-based RS ⬜ → 1 lesson
Collaborative filtering intuition • user-user vs item-item • similarity (Pearson, cosine) • prediction formula • mean centering • neighborhood size • limitations

### Ch 19 — Matrix factorization RS ⬜ → 1-2 lessons
- **19a**: user-item matrix • low-rank factorization • latent factors • objective function • gradient descent training
- **19b** (optional): regularization • bias terms • ALS (alternating least squares) • full example

---

## Part VI — ការកាត់បន្ថយវិមាត្រ (Dimensionality Reduction)

### Ch 20 — DR introduction ⬜ → 1 lesson
Curse of dimensionality • storage & computation • visualization motivation • linear vs nonlinear DR • overview of methods (PCA, LDA, t-SNE, UMAP teaser)

### Ch 21 — SVD ⬜ → 1 lesson
Definition • geometric interpretation • computation • truncated SVD • low-rank approximation • applications (LSA, image compression)

### Ch 22 — PCA ⬜ → 1-2 lessons
- **22a**: motivation (variance preservation) • mean centering • covariance matrix • eigendecomposition • principal components • variance explained
- **22b** (optional): PCA via SVD • reconstruction error • sklearn example • PCA on real datasets

### Ch 23 — LDA (Linear Discriminant Analysis) ⬜ → 1 lesson
Supervised DR for classification • between-class vs within-class scatter • Fisher's criterion • generalized eigenvalue problem • multiclass extension • LDA vs PCA • sklearn example

---

## Part VII — Convex Optimization

### Ch 24 — Convexity ⬜ → 1 lesson
Convex sets • convex functions (definition, first/second order conditions) • examples (linear, quadratic, log-sum-exp) • Jensen's inequality • operations preserving convexity • why convexity matters for optimization

### Ch 25 — Convex optimization ⬜ → 1-2 lessons
- **25a**: standard form • LP, QP, SOCP, SDP overview • Lagrangian
- **25b**: KKT conditions • solvers (CVXPY) • examples (LR as LS, SVM as QP)

### Ch 26 — Duality ⬜ → 1 lesson
Lagrange dual function • dual problem • weak vs strong duality • Slater's condition • KKT conditions revisited • sensitivity interpretation

---

## Part VIII — Support Vector Machines

### Ch 27 — SVM (linear, hard-margin) ⬜ → 1 lesson
Maximum margin classifier • geometric setup • primal optimization problem • dual formulation • support vectors • sklearn example

### Ch 28 — Soft-margin SVM ⬜ → 1 lesson
Non-separable data • slack variables • C hyperparameter • hinge loss interpretation • sklearn example

### Ch 29 — Kernel SVM ⬜ → 1 lesson
Kernel trick • common kernels (linear, polynomial, RBF, sigmoid) • Mercer's theorem (sketch) • kernel choice • hyperparameter tuning • sklearn example

### Ch 30 — Multiclass SVM ⬜ → 1 lesson
One-vs-Rest • One-vs-One • Crammer-Singer • sklearn handling

---

## Lesson count summary

| Part | Chapters | Lessons |
|---|---|---:|
| 0 — Intro | Ch 0 | 1 |
| I — Math | Ch 1–4 | 9 |
| II — Overview | Ch 5–8 | 4–5 |
| III — Warmup | Ch 9–11 | 3 |
| IV — Neural Nets | Ch 12–16 | 8 |
| V — Recsys | Ch 17–19 | 3–4 |
| VI — DimRed | Ch 20–23 | 4–5 |
| VII — Convex Opt | Ch 24–26 | 3–4 |
| VIII — SVM | Ch 27–30 | 4 |
| **Total** | **31 chapters** | **~40 lessons** |

---

## Writing order

1. Finish Part I gap-fill: Lesson 1b, 1c, 1d (LA), Lesson 2b (matrix calc)
2. Continue: Ch 3 (Probability) → Ch 4 (MLE/MAP) → Part II → … → Part VIII
