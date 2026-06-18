---
layout: post
title: "[ML Khmer] ជំពូក 8: Overfitting និង Regularization"
date: 2026-06-27 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, overfitting, regularization, ridge, lasso, cross-validation, interactive]
thumbnail: /images/ml-series/ch08-overfitting.svg
---

មេរៀន​មុន​យើង​ដោះ​ស្រាយ linear regression — ​ស្អាត ​ហើយ​មាន closed-form។ ​ប៉ុន្តែ​​​ការ​ដោះ​ស្រាយ​​​ល្អ​បំផុត​លើ train data **​មិន​មែន​​ត្រូវ​ល្អ​ជាង​លើ​ data ​ថ្មី** ​ឡើយ។ ​មេរៀន​នេះ​ដោះ​ស្រាយ​បញ្ហា​ស្នូល​នៃ ML — **overfitting** — ​​ហើយ​បង្ហាញ​​ឧបករណ៍​មាស​បី​៖ **Ridge (L2)**, **Lasso (L1)**, ​និង **cross-validation**។ ​យើង​ភ្ជាប់​ Ridge ​ទៅ​នឹង **MAP** ​នៃ​មេរៀន 4 — Ridge = Gaussian prior លើ weights, Lasso = Laplace prior។ ​មាន **រូបភាព interactive ៣**៖ polynomial degree ​ដែល​​បង្ហាញ U-shape, Ridge λ ​ដែល​បង្ហាញ shrinkage, ​និង bias–variance decomposition។

---

# សង្ខេប

- **Overfitting**៖ model ​​សម train ​ល្អ​ខ្លាំង → ​ខ្សោយ​លើ test (memorize noise)
- **Underfitting**៖ model ​ងាយ​ខ្លាំង → ខ្សោយ​ទាំង train ​និង test
- **Bias–variance tradeoff**៖ $\mathbb{E}[\text{err}] = \text{bias}^2 + \text{variance} + \sigma^2$
- **Ridge (L2)**៖ $L(w) = \|y - Xw\|^2 + \lambda \|w\|_2^2$ → closed form $w^* = (X^\top X + \lambda I)^{-1} X^\top y$
- **Lasso (L1)**៖ $L(w) = \|y - Xw\|^2 + \lambda \|w\|_1$ → ​ដុះ​ sparsity (coefficient ​ខ្លះ = 0 ​ច្បាស់)
- **Elastic Net**៖ $\lambda_1 \|w\|_1 + \lambda_2 \|w\|_2^2$ — ​បញ្ចូល​​​ល្អ​បំផុត​ទាំង​ពីរ
- **K-fold CV**៖ ​​​ជ្រើស $\lambda$ ​​ដោយ​​​​មិន "​​មើល" test set
- **​ការ​ភ្ជាប់ MAP**៖ Ridge ↔ Gaussian prior; Lasso ↔ Laplace prior

---

# ហេតុ​អ្វី​សំខាន់?

ការ​មាន model ​ដែល​​​បង្ហាញ​ R² = 0.99 ​លើ train ​​​​​​ប៉ុន្តែ​ R² = 0.30 ​លើ​ test ​​​មាន​បញ្ហា​ស្នូល — model ​មិន​បាន "​​យល់" អ្វី​​​​​​​សោះ; ​ត្រឹម​តែ memorize។ Regularization ​ជា​​ **ច្បាប់​​ច្បាស់​​ដែល​សម្រួល​ឱ្យ​ model សា​មញ្ញ ​នៅ​ពេល​ត្រូវ​ការ**។

**ឧស្សាហកម្ម​នៅ​កម្ពុជា​ដែល​ប្រើ​ផ្ទាល់​៖**

- **PP house price** — ​ផ្ទះ​មាន feature ច្រើន (50+ ​ដូច​ជា​ខណ្ឌ, គ្រឿង​សង្ហារឹម, ​ឆ្នាំ) → multicollinearity → **Ridge** ​ស្ថិត​ស្ថេរ
- **AMK loan scoring** — ​​ឱ្យ feature 200+ ​ឯកសារ → ​ត្រូវ feature selection → **Lasso** ​​ដុះ​​ដែល​​ "សំខាន់" 20
- **Crop yield prediction** — ​​ទិន្នន័យ​​​​​ត្រឹម​ ​​80 farms → **K-fold CV** ​ត្រូវ​ខ្លាំង (មិន​អាច​បាត់​បង់ data ​ច្រើន)
- **Wing fraud detection** — feature 500+ behavioral signals → **Elastic Net** ​សម្រួល​​​ feature group
- **Mobile click-through prediction** — model ​ឆាប់​ overfit ​លើ user history → regularization ​ការ​ពារ

**ច្បាប់​​ស្នូល​នៃ ML**៖ "​​​​​​បំ​លែង model ​ល្អ​បំផុត​លើ data ​ដែល​អ្នក​​​មិន​ដែល​ឃើញ" — ​​មិន​​មែន "​​​លឿន​បំផុត​​ ​លើ data ​ដែល​​​អ្នក​មាន​"​​។ Regularization + CV ​ផ្ដល់​ឧបករណ៍​​​ដែល​​​​​ធ្វើ​ឱ្យ​ត្រូវ។

---

# ពាក្យ​បច្ចេកទេស​ថ្មី

| ខ្មែរ | English | កំណត់​សម្គាល់ |
|---|---|---|
| ​ការ​សម​ហួស | overfitting | ​សម train ​ល្អ, test ​អន់ |
| ការ​សម​មិន​គ្រប់​គ្រាន់ | underfitting | model ​​ងាយ​ខ្លាំង |
| ​ភាព​លំអៀង | bias | ​​ការ​ខុស​មាន​ប្រព័ន្ធ​​ |
| ​បំរែប​បំរួល | variance | ​ការ​ប្រែ​ប្រួល​ដោយ data |
| Regularization | regularization | ​បន្ថែម penalty លើ​​ coefficient |
| L2 norm | $\|w\|_2^2 = \sum w_j^2$ | ​យក weight ​លើ ២ |
| L1 norm | $\|w\|_1 = \sum \|w_j\|$ | ​យក absolute value |
| Ridge regression | Ridge | linear + L2 penalty |
| Lasso regression | Lasso | linear + L1 penalty |
| Elastic Net | Elastic Net | L1 + L2 |
| Hyperparameter | hyperparameter | $\lambda$ — ​​​ត្រូវ​ជ្រើស​មុន train |
| Cross-validation | CV | ​​បំ​បែក data ​ដើម្បី estimate generalization |
| K-fold | K-fold | ​បំ​បែក data ​ជា K ​ដុំ |
| Sparsity | sparsity | coefficient ​​ខ្លះ = 0 ​ច្បាស់ |
| Shrinkage | shrinkage | coefficient ​​ដែល​ត្រូវ​បង្ហាប់​ឆ្ពោះ​ទៅ 0 |
| Generalization | generalization | ​ដំណើរ​ការ​លើ data ​ថ្មី |
| Effective degrees of freedom | edf | "​ភាព​ស្មុគ​ស្មាញ" ​ពិត​ប្រាកដ​​នៃ model |

---

# គំនិត​វិចារណញ្ញាណ

## "​ស្ទេនត្​ memorize ​ឬ​ understand?"

ស្រមៃ​មាន​សិស្ស​ពីរ​​៖

- **សិស្ស A** — memorize ​មេរៀន​ដោយ​ខ្យល់​ ​ដោយ​ឥត​មាន​​​ការ​​យល់ → ​ឆ្លើយ​បាន​ល្អ​លើ​ exam ​ដែល​មាន​សំណួរ​ស្រដៀង; ​ប៉ុន្តែ​ ​សំណួរ​ថ្មី → ​ល្ងង់
- **សិស្ស B** — យល់​មូល​ដ្ឋាន → ​ចំណេញ​ចំណាយ​​​​ច្រើន​បន្តិច​​​លើ​ practice ​ប៉ុន្តែ​ ​សំណួរ​ថ្មី → ​ឆ្លើយ​បាន​ច្បាស់

Overfitting = ​សិស្ស A។ Regularization = ​ច្បាប់​​​ដែល​​​​បំបង្ខំ​ឱ្យ model "​​យល់" ​ជំនួស "memorize"​​។

## "Bias = ​លំអៀង​មាន​ប្រព័ន្ធ; variance = ​ការ​​​ប្រែ​ប្រួល"

ស្រមៃ​​អ្នក​បាញ់​ព្រួញ​​ ​លើ target​៖

- **Bias ​ខ្ពស់, variance ​ទាប** — ​ព្រួញ​ទាំង​អស់​​​​​នៅ​ក្នុង​ដែន​តូច ​ប៉ុន្តែ​ឆ្ងាយ​ពី center → ​ស្ថិត​ស្ថេរ​​​​ ប៉ុន្តែ​ខុស​​​ច្បាស់
- **Bias ​ទាប, variance ​ខ្ពស់** — ​ព្រួញ​ចែក​ច្រើន​ជុំ​វិញ center → ​ល្អ​ជា​មធ្យម​ ​ប៉ុន្តែ​មិន​ស្ថិត​ស្ថេរ
- **​ល្អ​បំផុត​** — bias ​ទាប + variance ​ទាប → ​​​ ​ត្រូវ​ដោះ​ស្រាយ​ trade-off

**ច្បាប់​៖**
- Model ​សា​មញ្ញ​ខ្លាំង → bias ​ខ្ពស់, variance ​ទាប → underfit
- Model ស្មុគ​​ស្មាញ​ខ្លាំង → bias ​ទាប, variance ​ខ្ពស់ → overfit
- ​ល្អ​បំផុត​​នៅ​ចំ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ tradeoff sweet spot

## "Ridge = ​បង្រួម coefficient; Lasso = ​ដាក់ coefficient = 0"

​បើ​អ្នក​មាន 100 features ​​​ប៉ុន្តែ​ត្រឹម​ 5 ​​​សំខាន់​​៖

- **Ridge** — ​​ឱ្យ coefficient ​ទាំង 100 ​​ ​បន្ថយ​ឆ្ពោះ​ទៅ 0 (មិន​មែន​​​ត្រូវ 0)
- **Lasso** — ​ដាក់ coefficient ​​មិន​សំខាន់​ 95 ​​​ត្រូវ 0 ច្បាស់; ​​​ទុក​ត្រឹម​ 5 ​សំខាន់

ឧស្ស​ាហកម្ម​ច្រើន​ដង​​​​ត្រូវ​ការ Lasso ​សម្រាប់ **feature selection** — ​ឆ្លើយ​សំណួរ​ "​feature មួយ​ណា​សំខាន់​បំផុត?"

---

# និយមន័យ និង​គណិតវិទ្យា

## ១. Overfitting — ​​​និយមន័យ​ជា​លេខ

ឱ្យ​ true function $f(x)$ ​​​​​និង​ training set $\mathcal{D} = \{(x_i, y_i)\}$ ដែល $y_i = f(x_i) + \epsilon_i$, $\epsilon_i \sim \mathcal{N}(0, \sigma^2)$។

ឱ្យ $\hat f_\mathcal{D}$ ​​​ជា model ​ដែល​​​​​​​​ train ​លើ​ $\mathcal{D}$។

**Generalization error** ​លើ​ ​ចំណុច​​ថ្មី $x_0$៖

$$
\text{Err}(x_0) = \mathbb{E}_\mathcal{D, \epsilon} \left[ (y_0 - \hat f_\mathcal{D}(x_0))^2 \right]
$$

​ការ​បំ​បែក​ស្នូល (bias–variance decomposition)៖

$$
\boxed{\;\; \text{Err}(x_0) = \underbrace{(\mathbb{E}_\mathcal{D}[\hat f_\mathcal{D}(x_0)] - f(x_0))^2}_{\text{bias}^2} + \underbrace{\text{Var}_\mathcal{D}[\hat f_\mathcal{D}(x_0)]}_{\text{variance}} + \underbrace{\sigma^2}_{\text{noise irreducible}} \;\;}
$$

- **Bias²** — model ​ស្នូល​​​ខុស​ប៉ុនណា (​​ល្ងង់​ខ្លាំង​ឬ​ទេ?)
- **Variance** — model ​ផ្លាស់​ប្ដូរ​ប៉ុនណា​ពេល data ផ្លាស់​ប្ដូរ (​​ស្ថិត​ស្ថេរ​ឬ​ទេ?)
- **σ²** — noise ​ដែល​ឥត​អាច​លុប

## ២. Ridge Regression (L2 penalty)

​បន្ថែម​ penalty លើ​ norm ​នៃ weights៖

$$
L_\text{ridge}(w) = \|y - Xw\|_2^2 + \lambda \|w\|_2^2 = \sum_i (y_i - x_i^\top w)^2 + \lambda \sum_j w_j^2
$$

**$\lambda \ge 0$** ​ជា **regularization strength**​៖
- $\lambda = 0$ → linear regression ​ធម្មតា
- $\lambda \to \infty$ → $w \to 0$

​យក derivative ​ស្មើ​ 0៖

$$
\nabla_w L = -2 X^\top (y - Xw) + 2 \lambda w = 0
$$

​ដោះ​ស្រាយ៖

$$
\boxed{\;\; w_\text{ridge}^* = (X^\top X + \lambda I)^{-1} X^\top y \;\;}
$$

**គន្លឹះ​សំខាន់**៖ $X^\top X + \lambda I$ **ងងឹត​​ជានិច្ច** ​​នៅ​ពេល $\lambda > 0$ — ដោះ​ស្រាយ​​​ singular matrix ​ដែល​បាន​ពី multicollinearity ​​!

**ភាព​ស្មុគ​ស្មាញ​​​នៅ​ខាង​លេខ**៖ ​ដូច​ normal equation — $O(d^3)$ — ​ប៉ុន្តែ​ស្ថិត​ស្ថេរ​ខ្លាំង​ជាង។

## ៣. Lasso Regression (L1 penalty)

$$
L_\text{lasso}(w) = \|y - Xw\|_2^2 + \lambda \|w\|_1 = \sum_i (y_i - x_i^\top w)^2 + \lambda \sum_j |w_j|
$$

**​​មិន​មាន closed-form** ​ដោយ​សារ $|w_j|$ ​មិន differentiable ​​នៅ 0។ ​​ដោះ​ស្រាយ​ដោយ៖
- **Coordinate descent** (sklearn default)
- **Proximal gradient / ISTA**
- **LARS** (Least Angle Regression)

**​ហេតុ​អ្វី​ Lasso ​ផ្ដល់ sparsity?** L1 ​ball ​មាន **ច្រកាំងស្រួច** (corner) ​នៅ axes (eg. $w = (1, 0)$, $w = (0, 1)$)។ ​ការ​ស្វែង​រក minimum ​​​​​​​​នៃ​ loss + λ·L1 ​​​ច្រើន​ដង​ត្រូវ​ប៉ះ corner → coefficient ​​ខ្លះ = 0 ​​ច្បាស់។

L2 ​ball ​មាន **ផ្ទៃ​​ស្រួល​​​** ​​(​​​មូល) → ​មិន​ផ្ដល់​ sparsity, ​ត្រឹម​​ shrinkage។

## ៤. Elastic Net

​បញ្ចូល​ ល្អ​បំផុត​ទាំង​ពីរ​៖

$$
L_\text{enet}(w) = \|y - Xw\|^2 + \lambda \left[ \alpha \|w\|_1 + (1 - \alpha) \|w\|_2^2 \right]
$$

- $\alpha = 1$ → pure Lasso
- $\alpha = 0$ → pure Ridge
- $\alpha = 0.5$ → ​មធ្យម

**​​ជាក់​ស្តែង​៖** ​Lasso ​​ច្រើន​ដង​​ "​​ជ្រើស ​ច្រិត​ច្រិន" — ​​​ច្រើន​ correlated feature → ​ដាក់​មួយ​ត្រឹម 0; ​ឯ​ Elastic Net ​​​ ​​បំបែក​​​លាយ​លំ​ Ridge-style ​​​​​ដែល​ដោះ​ស្រាយ​ multicollinearity ​​​​​បាន​ល្អ​ជាង។

## ៥. K-fold Cross-Validation

​ដើម្បី​ជ្រើស $\lambda$ ​ត្រឹម​ត្រូវ — ​អ្នក​មិន​អាច​ "​​មើល" test set ​​​​​​នោះ​ឡើយ (​ការ​ធ្វើ​ច្នេះ → ​ការ​ "​លេច​​​​ឺ​​ leakage" → ​ការ​ ​បរ​ឯក​ឯករា​ជ្យ​ test estimate)។

**K-fold CV procedure**៖

1. ​បំ​បែក training data ​ជា $K$ ​ដុំ (folds)
2. ​សម្រាប់ $k = 1, \ldots, K$៖
   - Train ​លើ $K - 1$ folds
   - Evaluate ​លើ fold $k$ → $\text{err}_k(\lambda)$
3. **CV error**៖ $\text{CV}(\lambda) = \frac{1}{K} \sum_k \text{err}_k(\lambda)$
4. ​ជ្រើស $\lambda^* = \arg\min_\lambda \text{CV}(\lambda)$
5. Retrain ​លើ​​ training data ទាំង​មូល​​ ​ដោយ​ប្រើ $\lambda^*$
6. **​ឥឡូវ​នេះ** — test ​លើ test set (​​ មួយ​ដង)

**ច្បាប់​​ស្តង់​ដារ**៖
- $K = 5$ ​ឬ $K = 10$ — ​ការ​ចេញ​ចូល​​​ល្អ​បំផុត
- $K = n$ → **Leave-One-Out CV (LOOCV)** — variance ​ខ្ពស់, ​​​​​ចំណាយ​ច្រើន
- Stratified K-fold — ​សម្រាប់ classification (រក្សា class proportion)

## ៦. ​ការ​ភ្ជាប់ MAP

ត្រឡប់​ទៅ​មេរៀន 4 (MLE & MAP)៖

$$
w_\text{MAP} = \arg\max_w \left[ \log p(\mathcal{D} | w) + \log p(w) \right]
$$

ឱ្យ **Gaussian likelihood** (linear regression noise)៖

$$
\log p(\mathcal{D} | w) = -\frac{1}{2\sigma^2} \|y - Xw\|^2 + \text{const}
$$

**Case 1៖ Gaussian prior** $w \sim \mathcal{N}(0, \tau^2 I)$៖

$$
\log p(w) = -\frac{1}{2\tau^2} \|w\|_2^2 + \text{const}
$$

​បំ​លែង៖

$$
w_\text{MAP} = \arg\min_w \left[ \|y - Xw\|^2 + \frac{\sigma^2}{\tau^2} \|w\|_2^2 \right] = w_\text{ridge}^* \quad (\lambda = \sigma^2 / \tau^2)
$$

**Ridge = Gaussian prior!** ​​ការ​ភ្ជាប់​​ច្បាស់៖
- Prior tight ($\tau$ ​​តូច) → $\lambda$ ​ធំ → ​ការ​បង្ហាប់​​ខ្លាំង
- Prior loose ($\tau$ ​ធំ) → $\lambda$ ​​​​​តូច → linear regression ​ធម្មតា

**Case 2៖ Laplace prior** $w_j \sim \text{Laplace}(0, b)$ (independent ​​សម្រាប់ $j$)​៖

$$
\log p(w) = -\frac{1}{b} \sum_j |w_j| + \text{const} = -\frac{1}{b} \|w\|_1 + \text{const}
$$

→ **Lasso = Laplace prior!**

**ហេតុ​​អ្វី​ Laplace ​​​ផ្ដល់ sparsity?** Laplace ​​មាន **​ច្រកាំង​ស្រួច​ច្រាម​នៅ​ 0** — density ​ខ្ពស់​ខ្លាំង​នៅ $w_j = 0$ → Bayesian "ច្បាប់" ​ដែល​​​ច្រើន weight ​ជា 0 ​ច្បាស់។

## 🎮 ​រូបភាព interactive ១៖ Polynomial degree → U-shape

​ប្ដូរ degree ​នៃ polynomial — ​មើល​ train MSE ​ដួល​ឆ្ពោះ​ទៅ 0 ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ ​​ប៉ុន្តែ​ test MSE ​មាន​ U-shape — ​ដួល​​​​ដំបូង (underfit→good) ​បន្ទាប់​មក​ឡើង (good→overfit)។

<div id="viz1" style="width:100%;max-width:800px;margin:0 auto;height:440px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  Polynomial degree d = <span id="viz1-d" style="font-weight:bold;color:#dc2626">3</span>
  <input id="viz1-d-slider" type="range" min="1" max="15" step="1" value="3" style="width:40%;max-width:350px"><br>
  <button id="viz1-new" style="margin-top:6px;padding:5px 14px;cursor:pointer">🎲 ​ទិន្នន័យ​ថ្មី</button><br>
  <span style="font-size:1.05em;margin-top:6px;display:inline-block">
    Train MSE = <span id="viz1-train" style="font-weight:bold;color:#0f766e">--</span>
    &nbsp;|&nbsp;
    Test MSE = <span id="viz1-test" style="font-weight:bold;color:#dc2626">--</span>
  </span>
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    function randn() {
      var u = 0, v = 0;
      while (u === 0) u = Math.random();
      while (v === 0) v = Math.random();
      return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
    }
    var TRAIN = null, TEST = null;
    function f(x) { return Math.sin(1.5 * x) + 0.3 * x; }
    function gen() {
      TRAIN = []; TEST = [];
      for (var i = 0; i < 15; i++) {
        var x = -3 + 6 * Math.random();
        TRAIN.push([x, f(x) + 0.5 * randn()]);
      }
      for (var i = 0; i < 50; i++) {
        var x = -3 + 6 * Math.random();
        TEST.push([x, f(x) + 0.5 * randn()]);
      }
    }
    function design(pts, d) {
      var X = [];
      for (var i = 0; i < pts.length; i++) {
        var row = [];
        for (var j = 0; j <= d; j++) row.push(Math.pow(pts[i][0], j));
        X.push(row);
      }
      return X;
    }
    function transpose(M) {
      var R = M.length, C = M[0].length, T = [];
      for (var c = 0; c < C; c++) {
        var row = [];
        for (var r = 0; r < R; r++) row.push(M[r][c]);
        T.push(row);
      }
      return T;
    }
    function matmul(A, B) {
      var ra = A.length, ca = A[0].length, cb = B[0].length, C = [];
      for (var i = 0; i < ra; i++) {
        var row = [];
        for (var j = 0; j < cb; j++) {
          var s = 0;
          for (var k = 0; k < ca; k++) s += A[i][k] * B[k][j];
          row.push(s);
        }
        C.push(row);
      }
      return C;
    }
    function matvec(A, v) {
      var out = [];
      for (var i = 0; i < A.length; i++) {
        var s = 0;
        for (var j = 0; j < A[0].length; j++) s += A[i][j] * v[j];
        out.push(s);
      }
      return out;
    }
    function inv(M) {
      // Gauss-Jordan inversion with small ridge for stability
      var n = M.length, A = [];
      for (var i = 0; i < n; i++) {
        var row = [];
        for (var j = 0; j < n; j++) row.push(M[i][j] + (i === j ? 1e-8 : 0));
        for (var j = 0; j < n; j++) row.push(i === j ? 1 : 0);
        A.push(row);
      }
      for (var i = 0; i < n; i++) {
        var p = i;
        for (var k = i + 1; k < n; k++) if (Math.abs(A[k][i]) > Math.abs(A[p][i])) p = k;
        if (p !== i) { var t = A[i]; A[i] = A[p]; A[p] = t; }
        var piv = A[i][i];
        if (Math.abs(piv) < 1e-12) return null;
        for (var j = 0; j < 2 * n; j++) A[i][j] /= piv;
        for (var k = 0; k < n; k++) {
          if (k === i) continue;
          var f = A[k][i];
          for (var j = 0; j < 2 * n; j++) A[k][j] -= f * A[i][j];
        }
      }
      var inv = [];
      for (var i = 0; i < n; i++) inv.push(A[i].slice(n));
      return inv;
    }
    function fit(d) {
      var X = design(TRAIN, d);
      var Xt = transpose(X);
      var XtX = matmul(Xt, X);
      var XtXi = inv(XtX);
      if (XtXi === null) return null;
      var Xty = matvec(Xt, TRAIN.map(function (p) { return p[1]; }));
      return matvec(XtXi, Xty);
    }
    function predict(w, x) {
      var s = 0;
      for (var j = 0; j < w.length; j++) s += w[j] * Math.pow(x, j);
      return s;
    }
    function mse(w, pts) {
      var s = 0;
      for (var i = 0; i < pts.length; i++) {
        var err = pts[i][1] - predict(w, pts[i][0]);
        s += err * err;
      }
      return s / pts.length;
    }
    function plot(d) {
      var w = fit(d);
      var trainMSE = w ? mse(w, TRAIN) : NaN;
      var testMSE = w ? mse(w, TEST) : NaN;
      document.getElementById('viz1-train').textContent = isFinite(trainMSE) ? trainMSE.toFixed(3) : '--';
      document.getElementById('viz1-test').textContent = isFinite(testMSE) ? testMSE.toFixed(3) : '--';
      var lineX = [], lineY = [], trueY = [];
      for (var i = 0; i <= 200; i++) {
        var x = -3 + 6 * i / 200;
        lineX.push(x);
        lineY.push(w ? predict(w, x) : 0);
        trueY.push(f(x));
      }
      return [
        { x: lineX, y: trueY, mode: 'lines', name: 'true f(x)',
          line: { color: '#6b7280', width: 2, dash: 'dash' } },
        { x: lineX, y: lineY, mode: 'lines', name: 'polynomial fit',
          line: { color: '#dc2626', width: 3 } },
        { x: TRAIN.map(function (p) { return p[0]; }), y: TRAIN.map(function (p) { return p[1]; }),
          mode: 'markers', name: 'train',
          marker: { color: '#1e40af', size: 10, line: { color: '#fff', width: 1 } } },
        { x: TEST.map(function (p) { return p[0]; }), y: TEST.map(function (p) { return p[1]; }),
          mode: 'markers', name: 'test',
          marker: { color: '#10b981', size: 6, opacity: 0.55 } }
      ];
    }
    var layout = {
      xaxis: { title: 'x', range: [-3.3, 3.3] },
      yaxis: { title: 'y', range: [-4, 4] },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    gen();
    Plotly.newPlot('viz1', plot(3), layout, { responsive: true, displayModeBar: false });
    function render() {
      var d = parseInt(document.getElementById('viz1-d-slider').value);
      document.getElementById('viz1-d').textContent = d;
      Plotly.react('viz1', plot(d), layout);
    }
    document.getElementById('viz1-d-slider').addEventListener('input', render);
    document.getElementById('viz1-new').addEventListener('click', function () { gen(); render(); });
  }
  init();
})();
</script>

> **សាក​មើល៖** ​ប្ដូរ degree ​ពី 1 ​ទៅ 15 ​​​​ — ឃើញ​ថា degree = 1 → underfit (train + test ​ខ្ពស់​ទាំង​ពីរ​), degree ≈ 3 → ​ល្អ​បំផុត (train + test ​ទាប), degree = 15 → train ​​ស្ទើ 0 ​ប៉ុន្តែ test ​​​លោត​ឡើង → **overfit ច្បាស់​​​**​​!

## 🎮 ​រូបភាព interactive ២៖ Ridge λ → coefficient shrinkage

​ដាក់ Ridge ​លើ​ polynomial degree 10 (overfit ​ខ្លាំង)។ ​ប្ដូរ $\lambda$ ​ពី 0 ​ទៅ ​ធំ — ​មើល coefficient ​​ដែល​ត្រូវ​បង្ហាប់​ឆ្ពោះ​ទៅ 0 ​បន្តិច​ម្តង​ៗ។

<div id="viz2" style="width:100%;max-width:800px;margin:0 auto;height:480px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  log₁₀(λ) = <span id="viz2-lam" style="font-weight:bold;color:#7c3aed">-2.0</span> &nbsp;
  (λ = <span id="viz2-lamval" style="font-weight:bold;color:#7c3aed">0.0100</span>)
  <input id="viz2-lam-slider" type="range" min="-4" max="4" step="0.1" value="-2.0" style="width:40%;max-width:350px"><br>
  <button id="viz2-new" style="margin-top:6px;padding:5px 14px;cursor:pointer">🎲 ​ទិន្នន័យ​ថ្មី</button><br>
  <span style="font-size:1.05em;margin-top:6px;display:inline-block">
    Train MSE = <span id="viz2-train" style="font-weight:bold;color:#0f766e">--</span>
    &nbsp;|&nbsp;
    Test MSE = <span id="viz2-test" style="font-weight:bold;color:#dc2626">--</span>
  </span>
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    function randn() {
      var u = 0, v = 0;
      while (u === 0) u = Math.random();
      while (v === 0) v = Math.random();
      return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
    }
    var TRAIN = null, TEST = null, D = 10;
    function f(x) { return Math.sin(1.5 * x) + 0.3 * x; }
    function gen() {
      TRAIN = []; TEST = [];
      for (var i = 0; i < 15; i++) {
        var x = -3 + 6 * Math.random();
        TRAIN.push([x, f(x) + 0.5 * randn()]);
      }
      for (var i = 0; i < 50; i++) {
        var x = -3 + 6 * Math.random();
        TEST.push([x, f(x) + 0.5 * randn()]);
      }
    }
    function design(pts, d) {
      var X = [];
      for (var i = 0; i < pts.length; i++) {
        var row = [];
        for (var j = 0; j <= d; j++) row.push(Math.pow(pts[i][0], j));
        X.push(row);
      }
      return X;
    }
    function transpose(M) {
      var R = M.length, C = M[0].length, T = [];
      for (var c = 0; c < C; c++) {
        var row = [];
        for (var r = 0; r < R; r++) row.push(M[r][c]);
        T.push(row);
      }
      return T;
    }
    function matmul(A, B) {
      var ra = A.length, ca = A[0].length, cb = B[0].length, C = [];
      for (var i = 0; i < ra; i++) {
        var row = [];
        for (var j = 0; j < cb; j++) {
          var s = 0;
          for (var k = 0; k < ca; k++) s += A[i][k] * B[k][j];
          row.push(s);
        }
        C.push(row);
      }
      return C;
    }
    function matvec(A, v) {
      var out = [];
      for (var i = 0; i < A.length; i++) {
        var s = 0;
        for (var j = 0; j < A[0].length; j++) s += A[i][j] * v[j];
        out.push(s);
      }
      return out;
    }
    function inv(M) {
      var n = M.length, A = [];
      for (var i = 0; i < n; i++) {
        var row = [];
        for (var j = 0; j < n; j++) row.push(M[i][j]);
        for (var j = 0; j < n; j++) row.push(i === j ? 1 : 0);
        A.push(row);
      }
      for (var i = 0; i < n; i++) {
        var p = i;
        for (var k = i + 1; k < n; k++) if (Math.abs(A[k][i]) > Math.abs(A[p][i])) p = k;
        if (p !== i) { var t = A[i]; A[i] = A[p]; A[p] = t; }
        var piv = A[i][i];
        if (Math.abs(piv) < 1e-15) return null;
        for (var j = 0; j < 2 * n; j++) A[i][j] /= piv;
        for (var k = 0; k < n; k++) {
          if (k === i) continue;
          var f = A[k][i];
          for (var j = 0; j < 2 * n; j++) A[k][j] -= f * A[i][j];
        }
      }
      var inv = [];
      for (var i = 0; i < n; i++) inv.push(A[i].slice(n));
      return inv;
    }
    function fitRidge(d, lam) {
      var X = design(TRAIN, d);
      var Xt = transpose(X);
      var XtX = matmul(Xt, X);
      for (var i = 0; i < XtX.length; i++) XtX[i][i] += lam;
      var XtXi = inv(XtX);
      if (XtXi === null) return null;
      var Xty = matvec(Xt, TRAIN.map(function (p) { return p[1]; }));
      return matvec(XtXi, Xty);
    }
    function predict(w, x) {
      var s = 0;
      for (var j = 0; j < w.length; j++) s += w[j] * Math.pow(x, j);
      return s;
    }
    function mse(w, pts) {
      var s = 0;
      for (var i = 0; i < pts.length; i++) {
        var err = pts[i][1] - predict(w, pts[i][0]);
        s += err * err;
      }
      return s / pts.length;
    }
    function plot(lam) {
      var w = fitRidge(D, lam);
      var trainMSE = w ? mse(w, TRAIN) : NaN;
      var testMSE = w ? mse(w, TEST) : NaN;
      document.getElementById('viz2-train').textContent = isFinite(trainMSE) ? trainMSE.toFixed(3) : '--';
      document.getElementById('viz2-test').textContent = isFinite(testMSE) ? testMSE.toFixed(3) : '--';
      var lineX = [], lineY = [], trueY = [];
      for (var i = 0; i <= 200; i++) {
        var x = -3 + 6 * i / 200;
        lineX.push(x);
        lineY.push(w ? predict(w, x) : 0);
        trueY.push(f(x));
      }
      return [
        { x: lineX, y: trueY, mode: 'lines', name: 'true f(x)',
          line: { color: '#6b7280', width: 2, dash: 'dash' } },
        { x: lineX, y: lineY, mode: 'lines', name: 'Ridge fit (d=10)',
          line: { color: '#7c3aed', width: 3 } },
        { x: TRAIN.map(function (p) { return p[0]; }), y: TRAIN.map(function (p) { return p[1]; }),
          mode: 'markers', name: 'train',
          marker: { color: '#1e40af', size: 10, line: { color: '#fff', width: 1 } } },
        { x: TEST.map(function (p) { return p[0]; }), y: TEST.map(function (p) { return p[1]; }),
          mode: 'markers', name: 'test',
          marker: { color: '#10b981', size: 6, opacity: 0.55 } }
      ];
    }
    var layout = {
      xaxis: { title: 'x', range: [-3.3, 3.3] },
      yaxis: { title: 'y', range: [-4, 4] },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    gen();
    Plotly.newPlot('viz2', plot(0.01), layout, { responsive: true, displayModeBar: false });
    function render() {
      var l = parseFloat(document.getElementById('viz2-lam-slider').value);
      var lam = Math.pow(10, l);
      document.getElementById('viz2-lam').textContent = l.toFixed(1);
      document.getElementById('viz2-lamval').textContent = lam.toFixed(4);
      Plotly.react('viz2', plot(lam), layout);
    }
    document.getElementById('viz2-lam-slider').addEventListener('input', render);
    document.getElementById('viz2-new').addEventListener('click', function () { gen(); render(); });
  }
  init();
})();
</script>

> **សាក​មើល៖** ​ដាក់ $\lambda$ ​​​តូច​ខ្លាំង (eg. $10^{-4}$) → overfit ​​​ច្បាស់ (wave ​ច្រើន​)។ ​ដាក់ $\lambda$ ​ធំ (eg. $10^{2}$) → underfit (line ​ស្ទើ​​ flat)។ ​ល្អ​បំផុត​នៅ $\lambda$ ​មធ្យម (~$10^{-1}$)។

## 🎮 ​រូបភាព interactive ៣៖ Bias–variance decomposition

​យក 30 ​ដង​សម្រាប់ training set ​ផ្សេង​ៗ (sample ​ផ្សេង​​)។ ​សម្រាប់​ degree នីមួយ​ៗ — គូ​ស fitted curve ​ទាំង 30 ​​លើ​ same plot​​។ Variance ​ឃើញ​ច្បាស់​ដោយ​ការ​ច្រឹប​នៃ​​ curve!

<div id="viz3" style="width:100%;max-width:800px;margin:0 auto;height:480px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  Polynomial degree d = <span id="viz3-d" style="font-weight:bold;color:#dc2626">3</span>
  <input id="viz3-d-slider" type="range" min="1" max="12" step="1" value="3" style="width:40%;max-width:350px"><br>
  <button id="viz3-new" style="margin-top:6px;padding:5px 14px;cursor:pointer">🎲 ​ទិន្នន័យ​ថ្មី</button><br>
  <span style="font-size:1.05em;margin-top:6px;display:inline-block">
    Bias² ≈ <span id="viz3-bias" style="font-weight:bold;color:#7c3aed">--</span>
    &nbsp;|&nbsp;
    Variance ≈ <span id="viz3-var" style="font-weight:bold;color:#dc2626">--</span>
  </span>
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    function randn() {
      var u = 0, v = 0;
      while (u === 0) u = Math.random();
      while (v === 0) v = Math.random();
      return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
    }
    var N_SETS = 30, N_PTS = 12, SEED_OFFSET = 0;
    function f(x) { return Math.sin(1.5 * x) + 0.3 * x; }
    function genSet() {
      var pts = [];
      for (var i = 0; i < N_PTS; i++) {
        var x = -3 + 6 * Math.random();
        pts.push([x, f(x) + 0.5 * randn()]);
      }
      return pts;
    }
    function transpose(M) {
      var R = M.length, C = M[0].length, T = [];
      for (var c = 0; c < C; c++) {
        var row = [];
        for (var r = 0; r < R; r++) row.push(M[r][c]);
        T.push(row);
      }
      return T;
    }
    function matmul(A, B) {
      var ra = A.length, ca = A[0].length, cb = B[0].length, C = [];
      for (var i = 0; i < ra; i++) {
        var row = [];
        for (var j = 0; j < cb; j++) {
          var s = 0;
          for (var k = 0; k < ca; k++) s += A[i][k] * B[k][j];
          row.push(s);
        }
        C.push(row);
      }
      return C;
    }
    function matvec(A, v) {
      var out = [];
      for (var i = 0; i < A.length; i++) {
        var s = 0;
        for (var j = 0; j < A[0].length; j++) s += A[i][j] * v[j];
        out.push(s);
      }
      return out;
    }
    function inv(M) {
      var n = M.length, A = [];
      for (var i = 0; i < n; i++) {
        var row = [];
        for (var j = 0; j < n; j++) row.push(M[i][j] + (i === j ? 1e-8 : 0));
        for (var j = 0; j < n; j++) row.push(i === j ? 1 : 0);
        A.push(row);
      }
      for (var i = 0; i < n; i++) {
        var p = i;
        for (var k = i + 1; k < n; k++) if (Math.abs(A[k][i]) > Math.abs(A[p][i])) p = k;
        if (p !== i) { var t = A[i]; A[i] = A[p]; A[p] = t; }
        var piv = A[i][i];
        if (Math.abs(piv) < 1e-12) return null;
        for (var j = 0; j < 2 * n; j++) A[i][j] /= piv;
        for (var k = 0; k < n; k++) {
          if (k === i) continue;
          var f = A[k][i];
          for (var j = 0; j < 2 * n; j++) A[k][j] -= f * A[i][j];
        }
      }
      var inv = [];
      for (var i = 0; i < n; i++) inv.push(A[i].slice(n));
      return inv;
    }
    function fit(pts, d) {
      var X = [];
      for (var i = 0; i < pts.length; i++) {
        var row = [];
        for (var j = 0; j <= d; j++) row.push(Math.pow(pts[i][0], j));
        X.push(row);
      }
      var Xt = transpose(X);
      var XtX = matmul(Xt, X);
      var XtXi = inv(XtX);
      if (XtXi === null) return null;
      var Xty = matvec(Xt, pts.map(function (p) { return p[1]; }));
      return matvec(XtXi, Xty);
    }
    function predict(w, x) {
      var s = 0;
      for (var j = 0; j < w.length; j++) s += w[j] * Math.pow(x, j);
      return s;
    }
    function plot(d) {
      var traces = [];
      var grid = [];
      for (var i = 0; i <= 200; i++) grid.push(-3 + 6 * i / 200);
      var trueY = grid.map(f);
      var allPreds = []; // [N_SETS][grid.length]
      for (var s = 0; s < N_SETS; s++) {
        var pts = genSet();
        var w = fit(pts, d);
        var pred = w ? grid.map(function (x) { return predict(w, x); }) : grid.map(function () { return NaN; });
        allPreds.push(pred);
        traces.push({
          x: grid, y: pred, mode: 'lines',
          line: { color: 'rgba(220, 38, 38, 0.18)', width: 1 },
          showlegend: false, hoverinfo: 'skip'
        });
      }
      // average curve
      var avg = grid.map(function (_, i) {
        var sum = 0, n = 0;
        for (var s = 0; s < N_SETS; s++) {
          if (isFinite(allPreds[s][i])) { sum += allPreds[s][i]; n++; }
        }
        return n > 0 ? sum / n : 0;
      });
      // bias² and variance averaged over grid
      var biasSq = 0, varSum = 0, count = 0;
      for (var i = 0; i < grid.length; i++) {
        biasSq += Math.pow(avg[i] - trueY[i], 2);
        var v = 0;
        for (var s = 0; s < N_SETS; s++) {
          if (isFinite(allPreds[s][i])) v += Math.pow(allPreds[s][i] - avg[i], 2);
        }
        varSum += v / N_SETS;
        count++;
      }
      var biasOut = biasSq / count;
      var varOut = varSum / count;
      document.getElementById('viz3-bias').textContent = biasOut.toFixed(3);
      document.getElementById('viz3-var').textContent = varOut.toFixed(3);
      traces.push({
        x: grid, y: trueY, mode: 'lines', name: 'true f(x)',
        line: { color: '#374151', width: 3, dash: 'dash' }
      });
      traces.push({
        x: grid, y: avg, mode: 'lines', name: 'mean prediction',
        line: { color: '#7c3aed', width: 3 }
      });
      return traces;
    }
    var layout = {
      xaxis: { title: 'x', range: [-3.3, 3.3] },
      yaxis: { title: 'y', range: [-4, 4] },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    Plotly.newPlot('viz3', plot(3), layout, { responsive: true, displayModeBar: false });
    function render() {
      var d = parseInt(document.getElementById('viz3-d-slider').value);
      document.getElementById('viz3-d').textContent = d;
      Plotly.react('viz3', plot(d), layout);
    }
    document.getElementById('viz3-d-slider').addEventListener('input', render);
    document.getElementById('viz3-new').addEventListener('click', render);
  }
  init();
})();
</script>

> **សាក​មើល៖** Degree = 1 → curves ​​​ស្រដៀង​គ្នា​ច្បាស់ (variance ​ទាប) ​​​​ប៉ុន្តែ​ឆ្ងាយ​ពី true f(x) (bias ​ខ្ពស់)។ Degree = 12 → ​curves ​ចែក​​​ច្រើន​ (variance ​ខ្ពស់) ​​ប៉ុន្តែ​ mean prediction ​នៅ​​​​​​​​ច្បាស់ (bias ​ទាប)។ Trade-off ច្បាស់ៗ ​!

---

# ឧទាហរណ៍

## ឧទាហរណ៍ 1៖ Ridge ​ដោះ​ស្រាយ multicollinearity

ឱ្យ data ​ដែល​មាន feature ស្រដៀង​គ្នា​ខ្លាំង​​៖

$$
X = \begin{pmatrix} 1 & 1.001 \\ 2 & 2.002 \\ 3 & 3.003 \end{pmatrix}, \quad y = \begin{pmatrix} 2 \\ 4 \\ 6 \end{pmatrix}
$$

​គណនា $X^\top X$៖

$$
X^\top X = \begin{pmatrix} 14 & 14.014 \\ 14.014 & 14.028 \end{pmatrix}
$$

Determinant: $14 \cdot 14.028 - 14.014^2 = 196.392 - 196.392 \approx 0.0003$ → **ស្ទើ singular**!

​​​យក normal equation ​ធម្មតា → coefficient ​​អស្ថេរ​​ខ្លាំង (មិន​​ល្អ)។

​​ដាក់ Ridge ($\lambda = 0.1$)៖

$$
X^\top X + \lambda I = \begin{pmatrix} 14.1 & 14.014 \\ 14.014 & 14.128 \end{pmatrix}
$$

Determinant: $14.1 \cdot 14.128 - 14.014^2 = 199.205 - 196.392 = 2.813$ — **ស្ថិត​ស្ថេរ​ច្បាស់**!

→ Ridge ​សុំ​​ឱ្យ $w$ ​​​ស្ថិត​ ​ស្ថេរ + ​​​បំ​បែក​ បន្ទុក​​ ​​​​​​​​​លើ feature ​ទាំង​​ពីរ​ ​ស្ទើ​​​ស្មើ​គ្នា​ (eg. $w_1 \approx w_2 \approx 1$) ​​​​​​​​​ជំនួស​លាមកធ្ងន់​មួយ​ក្នុង​​​ខ្លះ ឯ​មួយ​ខ្លះ​ឥត​មាន។

## ឧទាហរណ៍ 2៖ Lasso ​ផ្តល់​ sparsity

ឱ្យ data ​​​មាន 100 features ​ប៉ុន្តែ​ត្រឹម​ 3 ​សំខាន់​៖

```
y = 2*x_1 + 3*x_5 - 1*x_{20} + noise
```

​បន្ទាប់​ពី Lasso ($\lambda = 0.1$)៖

| Feature | Coefficient |
|---|---|
| $x_1$ | 1.94 |
| $x_5$ | 2.87 |
| $x_{20}$ | -0.92 |
| All other 97 features | 0.00 |

→ Lasso ​ដោះ​ស្រាយ feature selection ​ដោយ​ផ្ទាល់ — ​​មិន​ត្រូវ​​​ការ​ p-value test ​​​ ​​​ឬ​ stepwise selection!

## ឧទាហរណ៍ 3៖ K-fold CV ​ដើម្បី​ជ្រើស $\lambda$

ឱ្យ $\lambda \in \{0.001, 0.01, 0.1, 1, 10, 100\}$, K = 5៖

| λ | Fold 1 | Fold 2 | Fold 3 | Fold 4 | Fold 5 | **CV mean** |
|---|---|---|---|---|---|---|
| 0.001 | 0.45 | 0.51 | 0.48 | 0.62 | 0.49 | 0.51 |
| 0.01 | 0.32 | 0.36 | 0.30 | 0.41 | 0.34 | 0.346 |
| **0.1** | **0.24** | **0.28** | **0.26** | **0.30** | **0.27** | **0.27** ⭐ |
| 1 | 0.31 | 0.34 | 0.33 | 0.36 | 0.32 | 0.332 |
| 10 | 0.58 | 0.61 | 0.60 | 0.63 | 0.59 | 0.602 |
| 100 | 0.95 | 0.97 | 0.96 | 0.98 | 0.96 | 0.964 |

→ ​​ជ្រើស $\lambda^* = 0.1$ ​ដែល​ផ្ដល់ CV ​ទាប​បំផុត។ ​បន្ទាប់​មក retrain ​លើ​​ training data ​ទាំង​មូល​ដោយ​ប្រើ $\lambda = 0.1$, ​​​បន្ទាប់​មក​​​​​មើល test set ​​មួយ​ដង។

---

# កូដ Python

## Ridge & Lasso ​ដោយ sklearn

```python
import numpy as np
from sklearn.linear_model import Ridge, Lasso, ElasticNet, LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, KFold

# ​បង្កើត data ​ដែល​ overfit ​បាន
np.random.seed(0)
X_train = np.random.uniform(-3, 3, (15, 1))
y_train = np.sin(1.5 * X_train).ravel() + 0.3 * X_train.ravel() + 0.5 * np.random.randn(15)

# Pipeline: poly degree 10 → standardize → fit
def make(model):
    return Pipeline([
        ('poly', PolynomialFeatures(degree=10, include_bias=False)),
        ('scale', StandardScaler()),
        ('reg', model)
    ])

linear = make(LinearRegression())
ridge  = make(Ridge(alpha=1.0))
lasso  = make(Lasso(alpha=0.1, max_iter=10000))
enet   = make(ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=10000))

for name, m in [('linear', linear), ('ridge', ridge), ('lasso', lasso), ('enet', enet)]:
    m.fit(X_train, y_train)
    coef = m.named_steps['reg'].coef_
    print(f'{name:8s}  ‖w‖₂² = {np.sum(coef**2):.3f}   nonzero = {np.sum(np.abs(coef) > 1e-4):2d}/10')
```

## K-fold CV ​ដើម្បី​ជ្រើស $\lambda$

```python
from sklearn.model_selection import GridSearchCV

# Grid search: 5-fold CV, log-scale lambda
param_grid = {'reg__alpha': np.logspace(-4, 2, 30)}
grid = GridSearchCV(ridge, param_grid, cv=5,
                    scoring='neg_mean_squared_error', n_jobs=-1)
grid.fit(X_train, y_train)

print(f'Best λ = {grid.best_params_["reg__alpha"]:.4f}')
print(f'Best CV MSE = {-grid.best_score_:.4f}')

# ​ឥឡូវ​ — best_model ​ដែល​ trained ​ដោយ best λ
best_model = grid.best_estimator_
```

## Plot CV error curve

```python
import matplotlib.pyplot as plt

results = grid.cv_results_
alphas = param_grid['reg__alpha']
cv_means = -results['mean_test_score']
cv_stds  = results['std_test_score']

plt.figure(figsize=(8, 5))
plt.semilogx(alphas, cv_means, 'b-', lw=2)
plt.fill_between(alphas, cv_means - cv_stds, cv_means + cv_stds, alpha=0.2)
plt.axvline(grid.best_params_['reg__alpha'], color='red', ls='--', label='best λ')
plt.xlabel('λ (log scale)'); plt.ylabel('CV MSE'); plt.legend()
plt.title('5-fold CV: ​ជ្រើស​ λ ​ល្អ​បំផុត')
plt.show()
```

## ​ការ​ផ្ទៀង​ផ្ទាត់​ bias–variance

```python
from sklearn.model_selection import learning_curve

train_sizes = np.linspace(0.1, 1.0, 10)
sizes, train_scores, test_scores = learning_curve(
    ridge, X_train, y_train, train_sizes=train_sizes,
    cv=5, scoring='neg_mean_squared_error', n_jobs=-1)

train_mse = -train_scores.mean(axis=1)
test_mse  = -test_scores.mean(axis=1)

# Gap ​ធំ → variance ​ខ្ពស់ (overfit)
# train_mse ​ខ្ពស់ + close to test_mse → bias ​ខ្ពស់ (underfit)
```

---

# ​ការ​អនុវត្តន៍​ជាក់​ស្តែង

## PP house price + Ridge

ឧស្សាហកម្ម real estate ​ក្នុង PP — feature 50+ ​​ច្រើន​ correlated (eg. floor area + bedroom count, ​ខណ្ឌ​ + lat/long)។

**Workflow​៖**

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ct = ColumnTransformer([
    ('num', StandardScaler(), ['floor_sqm', 'bedrooms', 'bathrooms', 'age']),
    ('cat', OneHotEncoder(sparse_output=False), ['khan', 'building_type'])
])

pipeline = Pipeline([('ct', ct), ('ridge', Ridge())])
grid = GridSearchCV(pipeline, {'ridge__alpha': np.logspace(-2, 4, 20)},
                    cv=5, scoring='neg_mean_squared_error')
grid.fit(X, y)
```

**លទ្ធផល​​ច្រើន​ដង​​៖** Ridge ​ផ្ដល់​​ R² ​​ខ្ពស់​ជាង linear regression 5-10% ​ លើ test set ​​ ហើយ coefficient ​ស្ថិត​ស្ថេរ​ច្បាស់ — ​ភ្ញាស់​ត្រួត​ពិនិត្យ​ច្បាស់​​​​​ជាង។

## AMK loan scoring + Lasso

​ឱ្យ feature 200+ (transaction patterns, demographic, behavioral) — ​ត្រូវ​​ feature ​ត្រឹម 20 ​ដែល​ explainable ​ដល់​ regulators។

**Workflow៖**

```python
lasso_grid = GridSearchCV(
    Pipeline([('scale', StandardScaler()), ('lasso', Lasso(max_iter=20000))]),
    {'lasso__alpha': np.logspace(-3, 1, 30)},
    cv=5, scoring='neg_mean_squared_error'
)
lasso_grid.fit(X, y)

# Inspect ​feature ​​ដែល​​​​​នៅ​​​សល់
best = lasso_grid.best_estimator_.named_steps['lasso']
nonzero = np.where(np.abs(best.coef_) > 1e-4)[0]
print(f'Kept {len(nonzero)} / {len(best.coef_)} features')
print(f'Top: {feature_names[nonzero][np.argsort(-np.abs(best.coef_[nonzero]))[:10]]}')
```

**លទ្ធផល​​ច្រើន​ដង​៖** Lasso ​​​លុប 180 feature ​​​​អស់ → ​ទុក​ត្រឹម 20 ​​​សំខាន់​ — model ​​​​ស្តង់​ដារ + ​​​​ហ្គឺមណ៍​ explainable + ​ដំណើរ​ការ​ inference លឿន​បំផុត។

## Crop yield + K-fold CV

ទិន្នន័យ 80 farms ​ត្រឹម — ​មិន​អាច​ "splits 70/15/15" → ​បាត់​​ test set ​សំខាន់។ → **Nested CV**៖

```python
from sklearn.model_selection import cross_val_score

outer_cv = KFold(n_splits=5, shuffle=True, random_state=42)
inner_cv = KFold(n_splits=4, shuffle=True, random_state=0)

scores = cross_val_score(
    GridSearchCV(ridge, {'reg__alpha': np.logspace(-2, 2, 10)},
                 cv=inner_cv, scoring='neg_mean_squared_error'),
    X, y, cv=outer_cv, scoring='neg_mean_squared_error'
)
print(f'Outer CV MSE: {-scores.mean():.3f} ± {scores.std():.3f}')
```

**ហេតុ​​អ្វី nested?** Inner CV ​ជ្រើស $\lambda$, outer CV ​​estimates ​​​ដំណើរ​ការ​លើ data ​ថ្មី។ ​ច្បាប់​មាស​​​នៅ​ពេល​ data ​ល្ងាច។

## Wing fraud detection + Elastic Net

500+ behavioral features ​ច្រើន​​ correlated → Lasso ​​"​ ​ច្រឹប" ​ច្រិត​ច្រិន (drop ​ groups ​ច្រើន​ដង​មិន​ត្រឹម​ត្រូវ)។ → Elastic Net ​ផ្ដល់​ smooth shrinkage + group selection។

---

# លំហាត់

### លំហាត់ 1 — Ridge solution ​ដោយ​ដៃ

ឱ្យ $X = \begin{pmatrix} 1 \\ 2 \\ 3 \end{pmatrix}, y = \begin{pmatrix} 2 \\ 5 \\ 7 \end{pmatrix}, \lambda = 1$.

(a) ​គណនា linear regression solution $w_\text{OLS}$<br>
(b) ​គណនា Ridge solution $w_\text{ridge}$<br>
(c) ​បកស្រាយ​ភាព​ខុស​គ្នា

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**(a) OLS៖**

$X^\top X = 1^2 + 2^2 + 3^2 = 14$, $X^\top y = 1 \cdot 2 + 2 \cdot 5 + 3 \cdot 7 = 33$

$$
w_\text{OLS} = \frac{X^\top y}{X^\top X} = \frac{33}{14} \approx 2.357
$$

**(b) Ridge ($\lambda = 1$)៖**

$$
w_\text{ridge} = \frac{X^\top y}{X^\top X + \lambda} = \frac{33}{14 + 1} = \frac{33}{15} = 2.2
$$

**(c) ​ភាព​ខុស​គ្នា៖**

- $w_\text{OLS} = 2.357$ — ​ដោះ​ស្រាយ​ residual ​ឱ្យ​​​នៅ​ត្រឹម 0 ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ល្អ​បំផុត
- $w_\text{ridge} = 2.2$ — ​ត្រូវ​បង្ហាប់​ឆ្ពោះ​ទៅ 0 ​ដោយ​ការ​ "​​ចុះ​បន្ថយ" ​​​​ដោយ factor $\frac{14}{15} \approx 0.933$
- Shrinkage factor = $\frac{X^\top X}{X^\top X + \lambda}$ — ​ច្បាស់​ច្នេះ $\lambda \to 0 \Rightarrow$ factor $\to 1$ (no shrinkage); $\lambda \to \infty \Rightarrow$ factor $\to 0$ ($w \to 0$)

</details>

### លំហាត់ 2 — Bias–variance: ​​​​​​ករណី​ណា?

​សម្រាប់ scenarios ​នី​មួយ​ៗ — តើ bias ​ខ្ពស់, variance ​ខ្ពស់, ​ឬ​​ល្អ​បំផុត?

(a) Train MSE = 5, Test MSE = 5.2<br>
(b) Train MSE = 0.01, Test MSE = 8.0<br>
(c) Train MSE = 10, Test MSE = 11<br>
(d) Train MSE = 0.5, Test MSE = 2.0

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**ច្បាប់​ស្នូល​៖**
- Train + Test ​ខ្ពស់​ទាំង​ពីរ + ​ស្ទើ​ស្មើ → **bias ​ខ្ពស់** (underfit) — model ​ងាយ​ខ្លាំង
- Train ​ទាប + Test ​ខ្ពស់ → **variance ​ខ្ពស់** (overfit) — model ​ស្មុគ​ស្មាញ​ខ្លាំង
- Train + Test ​ទាប​ទាំង​ពីរ + close → **​ល្អ​បំផុត**

**(a)** Train = 5, Test = 5.2 → ​ខ្ពស់​ទាំង​ពីរ + close → **bias ​ខ្ពស់ (underfit)** → ​ដាក់ feature ​បន្ថែម ​ឬ model ​ស្មុគ​ស្មាញ​ជាង

**(b)** Train = 0.01, Test = 8.0 → ​ទាប/ខ្ពស់, gap ​ធំ → **variance ​ខ្ពស់ (overfit)** → ​ដាក់ regularization ​ឬ​​​ collect data ​​​​​បន្ថែម

**(c)** Train = 10, Test = 11 → ​ខ្ពស់​ទាំង​ពីរ + close → **bias ​ខ្ពស់ (underfit)** → model ​ងាយ​ខ្លាំង

**(d)** Train = 0.5, Test = 2.0 → ​ទាប/​មធ្យម, gap ​មាន → **variance ​ខ្ពស់​បន្តិច (overfit ​បន្តិច)** → ​ដាក់ Ridge ​បន្តិច

</details>

### លំហាត់ 3 — K-fold CV ​​​​បំ​បែក

​ឱ្យ data 100 ​ចំណុច, $K = 5$ folds, stratified ​ដោយ class។

(a) ​​​​ដុំ​នី​មួយ​ៗ​មាន​ប៉ុនមាន​ចំណុច?<br>
(b) ​​​​ដុំ​នី​មួយ​ៗ​​ ​ត្រូវ​ train ​លើ​ចំណុច​ប៉ុនមាន?<br>
(c) ​បើ training time = 2s ​ដោយ data 80 ​ចំណុច — តើ full CV ​ប្រើ​ប៉ុនមាន​សរុប?<br>
(d) ​បើ​ប្រើ $K = 10$, ​​​ការ​ប្រែ​ប្រួល​ប៉ុនមាន?

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**(a)** ​​​ដុំ​នី​មួយ​ៗ = $100 / 5 = 20$ ​ចំណុច

**(b)** ​​​ដុំ​នី​មួយ​ៗ — train ​លើ $100 - 20 = 80$ ​ចំណុច (folds ​ដែល​​សល់)

**(c)** Total = $5 \times 2\text{s} = 10$s (sequential)។ ​បើ parallelize → $\sim 2\text{s} + $ overhead.

**(d)** $K = 10$ → ​​​ដុំ​នី​មួយ​ៗ = 10 ​ចំណុច, train ​លើ​ 90 → Cost: $10 \times \text{train\_time}(90)$ ​​​​ច្រើន​ជាង​ ​​​​ប្រហែល​ 2x។ Trade-off ៖
- $K$ ​ធំ → bias ​ទាប (training set ​ធំ​ជាង​​​ច្បាស់) + variance ​ខ្ពស់ (folds ​​ស្រដៀង​គ្នា) + ​ចំណាយ​ខ្ពស់
- $K = 5$ ​ឬ $K = 10$ — sweet spot ​ឧស្សាហកម្ម

</details>

### លំហាត់ 4 — MAP ↔ Regularization

​បង្ហាញ​ថា Gaussian likelihood + Gaussian prior → Ridge.

​ឱ្យ $p(y_i | w, x_i) = \mathcal{N}(x_i^\top w, \sigma^2)$ ​និង $p(w) = \mathcal{N}(0, \tau^2 I)$. ​​បាន $w_\text{MAP}$ = Ridge solution ​ដែល $\lambda = ?$

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

​យក $-\log$ ​នៃ posterior៖

$$
-\log p(w | \mathcal{D}) = -\log p(\mathcal{D} | w) - \log p(w) + \text{const}
$$

**Likelihood term​៖**

$$
-\log p(\mathcal{D} | w) = \frac{1}{2\sigma^2} \sum_i (y_i - x_i^\top w)^2 + \text{const} = \frac{1}{2\sigma^2} \|y - Xw\|^2 + \text{const}
$$

**Prior term​៖**

$$
-\log p(w) = \frac{1}{2\tau^2} \|w\|^2 + \text{const}
$$

**​​​​​បំ​លែង​សរុប៖**

$$
w_\text{MAP} = \arg\min_w \left[ \frac{1}{2\sigma^2} \|y - Xw\|^2 + \frac{1}{2\tau^2} \|w\|^2 \right]
$$

​​​​​​​​​​​​បំ​លែង​ត្រូវ $2\sigma^2$៖

$$
= \arg\min_w \left[ \|y - Xw\|^2 + \frac{\sigma^2}{\tau^2} \|w\|^2 \right]
$$

→ **Ridge ​ដែល $\lambda = \dfrac{\sigma^2}{\tau^2}$** ✓

**ការ​បកស្រាយ​៖**
- Noise ​ខ្ពស់ (large $\sigma^2$) → $\lambda$ ​ធំ → ​​​​ការ​បង្ហាប់​ខ្លាំង (ច្បាស់​មិន​​ ​ត្រូវ believe data ​ច្រើន)
- Prior tight (small $\tau^2$) → $\lambda$ ​ធំ → ​​ការ​​​បង្ហាប់​ខ្លាំង (believe prior ​ច្រើន​ជាង)
- ​បើ​ uniform prior ($\tau \to \infty$) → $\lambda \to 0$ → MLE = OLS

</details>

---

**​មេរៀន​បន្ទាប់ (ជំពូក 9):** K-Nearest Neighbors (KNN) — model ​ដំបូង​ដែល **​មិន​មាន train** ​ច្បាស់ — non-parametric ​ស្នូល។ យើង​ឃើញ​ថា bias–variance ​លេច​ច្បាស់​ដោយ $k$ — ​តូច​ខ្លាំង → overfit, ​ធំ​ខ្លាំង → underfit. គន្លឹះ​​ដែល​ត្រូវ​យក​មក​បន្ត​៖ ​ឧបករណ៍​មាស regularization + CV ​​ ​​ ​សម្រាប់​ tuning hyperparameter ​នៃ​ model ​ផ្សេងៗ​​ទាំង​អស់​ដែរ។
