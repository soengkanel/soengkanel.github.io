---
layout: post
title: "[ML Khmer] ជំពូក 1c: លំហវ៉ិចទ័រ — ឯករាជ្យ, មូលដ្ឋាន, និង orthogonality"
date: 2026-06-17 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, math, linear-algebra]
thumbnail: /images/ml-series/ch01c-vector-spaces.svg
---

មេរៀននេះស្វែងយល់​អំពី​រចនាសម្ព័ន្ធ​ខាងក្នុង​នៃ​លំហ​វ៉ិចទ័រ៖ **លីនេអ៊ែរ​ឯករាជ្យ** (linear independence), **លំហ​សាង** (span), **មូលដ្ឋាន** (basis), **rank**, **null space**, និង **orthogonality**។ យើង​នឹង​ប្រើ​បញ្ហា​ "​លក្ខណៈ​ស្ទួន" ក្នុង​ទិន្នន័យ​មីក្រូហិរញ្ញវត្ថុ​នៅ​កម្ពុជា​ដើម្បី​យល់​ពី​គំនិត​ទាំងនេះ​ឱ្យ​កាន់​តែ​ច្បាស់។

---

# សង្ខេប

- **លីនេអ៊ែរ​ឯករាជ្យ** ⟺ គ្មាន​វ៉ិចទ័រ​មួយ​ណា​ដែល​សរសេរ​ជា​ផល​បូក​លីនេអ៊ែរ​នៃ​វ៉ិចទ័រ​ដទៃ
- **មូលដ្ឋាន** = សំណុំ​ឯករាជ្យ​ដែល​សាង​លំហ​ទាំងមូល
- **Rank** នៃ​ម៉ាទ្រីស = ចំនួន​ជួរ​ឈរ​ឯករាជ្យ​អតិបរមា (ខ្លឹមសារ​ព័ត៌មាន​ពិត)
- **Null space** = សំណុំ​នៃ $\mathbf{x}$ ដែល $\mathbf{Ax} = \mathbf{0}$
- **វ៉ិចទ័រ orthogonal**៖ $\mathbf{a} \cdot \mathbf{b} = 0$ • **ម៉ាទ្រីស orthogonal**៖ $\mathbf{Q}^\top \mathbf{Q} = \mathbf{I}$

---

# ហេតុអ្វីសំខាន់?

នេះ​មិនមែន​ជា​គណិតវិទ្យា​ដែល​មិន​មាន​ប្រយោជន៍​ទេ — វា​ឆ្លុះ​បញ្ចាំង​ដោយ​ផ្ទាល់​ក្នុង ML៖

- **Rank** ប្រាប់​យើង​ថា​លក្ខណៈ​ប៉ុន្មាន​ដែល​ពិត​ជា​ផ្ដល់​ព័ត៌មាន​ឯករាជ្យ។ ឧទាហរណ៍​ខាង​ក្រោម​នឹង​បង្ហាញ​ថា​បើ​អ្នក​ដាក់​ទាំង "ប្រាក់​ចំណូល KHR" និង "ប្រាក់​ចំណូល USD" ក្នុង dataset, អ្នក​មិន​មាន​លក្ខណៈ​ពីរ​ឯករាជ្យ​ទេ
- **Null space** ប្រាប់​យើង​ថា​ហេតុ​អ្វី​សមីការ $\mathbf{Xw} = \mathbf{y}$ ច្រើន​តែ​មាន​ដំណោះ​ស្រាយ​ច្រើន — ច្រើន​នាំ​ឱ្យ​គំរូ​មិន​ស្ថេរ​ភាព
- **Orthogonality** គឺ​ស្នូល​នៃ PCA — components សំខាន់ៗ​ទាំង​អស់​ត្រូវ​ជា orthogonal គ្នា
- **ការ​ផ្លាស់​មូលដ្ឋាន** គឺ​ជា​អ្វី​ដែល autoencoder និង​ការ​បកប្រែ​លក្ខណៈ​ធ្វើ​ក្នុង​ស្នូល

---

# ពាក្យបច្ចេកទេសថ្មី

| ខ្មែរ | English | កំណត់សម្គាល់ |
|---|---|---|
| ផលបូកលីនេអ៊ែរ | linear combination | $c_1 \mathbf{v}_1 + c_2 \mathbf{v}_2 + \cdots$ |
| លីនេអ៊ែរឯករាជ្យ | linearly independent | គ្មាន​វ៉ិចទ័រ​ជា​ផល​បូក​នៃ​ដទៃ |
| លីនេអ៊ែរអាស្រ័យ | linearly dependent | មាន​យ៉ាង​ហោច​មួយ​ជា​ផល​បូក​នៃ​ដទៃ (= ទិន្នន័យ​ស្ទួន) |
| លំហសាង | span | សំណុំ​នៃ​ផល​បូក​លីនេអ៊ែរ​ទាំង​អស់ |
| មូលដ្ឋាន | basis | សំណុំ​ឯករាជ្យ​ដែល​សាង​លំហ |
| វិមាត្រ | dimension | ចំនួន​វ៉ិចទ័រ​ក្នុង​មូលដ្ឋាន |
| Rank | rank | $\text{rank}(\mathbf{A})$ — ចំនួន​ជួរ​ឈរ​ឯករាជ្យ |
| លំហជួរឈរ | column space / range | លំហ​សាង​ដោយ​ជួរ​ឈរ​នៃ $\mathbf{A}$ |
| លំហសូន្យ | null space / kernel | $\{\mathbf{x} : \mathbf{Ax} = \mathbf{0}\}$ |
| Orthogonal | orthogonal | កែង​គ្នា ($\mathbf{a} \cdot \mathbf{b} = 0$) |
| Orthonormal | orthonormal | orthogonal + normalized ($\\|\mathbf{v}\\| = 1$) |
| ម៉ាទ្រីស orthogonal | orthogonal matrix | $\mathbf{Q}^\top \mathbf{Q} = \mathbf{I}$ |

---

# គំនិតវិចារណញ្ញាណ

## លីនេអ៊ែរឯករាជ្យ — តាមរយៈ​ទិន្នន័យ​មីក្រូហិរញ្ញវត្ថុ

ឧបមាថា Prasac មាន dataset កសិករ​ដែល​មាន​ជួរ​ឈរ​ដូច​ខាង​ក្រោម៖

- **ប្រាក់​ចំណូល KHR** (លាន​រៀល​ប្រចាំ​ខែ)
- **ប្រាក់​ចំណូល USD** (ដុល្លារ​ប្រចាំ​ខែ)

ដោយ​សារ 1 USD ≈ 4,100 KHR, ប្រាក់​ចំណូល USD គឺ​គ្រាន់​តែ​ជា ប្រាក់​ចំណូល KHR ÷ 4.1 (ក្នុង​លាន)។

មាន​ន័យ​ថា៖

$$
\text{income}_{\text{USD}} = \frac{1}{4.1} \cdot \text{income}_{\text{KHR}}
$$

ជួរ​ឈរ​មួយ​គឺ **គុណ​នៃ​ជួរ​ឈរ​ដទៃ** — នេះ​ជា **លីនេអ៊ែរ​អាស្រ័យ**។ ដាក់​លក្ខណៈ​នេះ​ទាំង​ពីរ​ក្នុង​គំរូ ML មិន​ផ្ដល់​ព័ត៌មាន​បន្ថែម​ទេ ហើយ​ជា​ការ​ពិត​បំផ្លាញ​ការ training (covariance matrix ច្រាស​មិន​បាន)។

## មូលដ្ឋាន

មូលដ្ឋាន = សំណុំ​អប្បបរមា​នៃ​ទិស​ដែល​អាច​ឱ្យ​អ្នក​ឈាន​ដល់​គ្រប់​ចំណុច​ក្នុង​លំហ។ សម្រាប់ $\mathbb{R}^2$, មូលដ្ឋាន​ស្ដង់​ដារ​គឺ៖

$$
\mathbf{e}_1 = \begin{bmatrix} 1 \\ 0 \end{bmatrix}, \quad \mathbf{e}_2 = \begin{bmatrix} 0 \\ 1 \end{bmatrix}
$$

ប្រសិន​បើ​អ្នក​ដឹង "ខាង​ណា" និង "ប៉ុន្មាន​ដង" សម្រាប់​មូលដ្ឋាន​នីមួយៗ, អ្នក​ដឹង​ចំណុច។

## Rank

រាប់​ចំនួន​ជួរ​ឈរ​នៃ $\mathbf{A}$ ដែល​ឯករាជ្យ​ — នេះ​គឺ **ខ្លឹមសារ​ព័ត៌មាន​ពិត** នៃ​ម៉ាទ្រីស។ ប្រសិន​បើ​អ្នក​មាន 10 លក្ខណៈ​ប៉ុន្តែ rank = 7, នោះ​មាន 3 លក្ខណៈ​ស្ទួន​ — អាច​យក​ចេញ​ដោយ​មិន​បាត់​បង់​ព័ត៌មាន។

## Null space

ប្រសិន​បើ​អ្នក​ដឹង​ដំណោះ​ស្រាយ​មួយ​នៃ $\mathbf{Ax} = \mathbf{b}$, គ្រប់​វ៉ិចទ័រ​ក្នុង null space​ បន្ថែម​ទៅ​នឹង​ដំណោះ​ស្រាយ​នោះ​ក៏​ជា​ដំណោះ​ស្រាយ​ផង​ដែរ។ Null space ​ច្រើន​ជាង​សូន្យ ⟺ ដំណោះ​ស្រាយ​ច្រើន — នេះ​ជា​ភាព​មិន​កំណត់​ដែល​ធ្វើ​ឱ្យ​គំរូ ML មិន​ស្ថេរ​ភាព។

---

# និយមន័យ និងគណិតវិទ្យា

## ១. ផលបូកលីនេអ៊ែរ និងលំហសាង

ផល​បូក​លីនេអ៊ែរ​នៃ $\mathbf{v}_1, \ldots, \mathbf{v}_k$៖

$$
c_1 \mathbf{v}_1 + c_2 \mathbf{v}_2 + \cdots + c_k \mathbf{v}_k \quad \text{where } c_i \in \mathbb{R}
$$

**លំហ​សាង** (span)៖

$$
\text{span}(\mathbf{v}_1, \ldots, \mathbf{v}_k) = \left\{ \sum_{i=1}^k c_i \mathbf{v}_i : c_i \in \mathbb{R} \right\}
$$

## ២. លីនេអ៊ែរ​ឯករាជ្យ

$\{\mathbf{v}_1, \ldots, \mathbf{v}_k\}$ **ឯករាជ្យ** ⟺ សមីការ​ខាង​ក្រោម​មាន​តែ​ដំណោះ​ស្រាយ​សូន្យ៖

$$
c_1 \mathbf{v}_1 + c_2 \mathbf{v}_2 + \cdots + c_k \mathbf{v}_k = \mathbf{0} \implies c_1 = c_2 = \cdots = c_k = 0
$$

បើ​មាន​ដំណោះ​ស្រាយ​មិន​សូន្យ, វា **អាស្រ័យ**។

## ៣. មូលដ្ឋាន និង វិមាត្រ

**មូលដ្ឋាន** នៃ​លំហ $V$ = សំណុំ​នៃ​វ៉ិចទ័រ​ដែល៖
1. ឯករាជ្យ
2. សាង $V$ (i.e., $\text{span} = V$)

**វិមាត្រ** $\dim(V)$ = ចំនួន​វ៉ិចទ័រ​ក្នុង​មូលដ្ឋាន (ដូច​គ្នា​សម្រាប់​មូលដ្ឋាន​ទាំង​អស់​នៃ​លំហ​នោះ)។

## ៤. Rank, លំហ​ជួរ​ឈរ, និង null space

សម្រាប់ $\mathbf{A} \in \mathbb{R}^{m \times n}$៖

**លំហ​ជួរ​ឈរ** (column space, range)៖
$$\text{col}(\mathbf{A}) = \text{span}(\text{columns of } \mathbf{A}) \subseteq \mathbb{R}^m$$

**Rank**៖
$$\text{rank}(\mathbf{A}) = \dim(\text{col}(\mathbf{A}))$$

**Null space** (kernel)៖
$$\text{null}(\mathbf{A}) = \{\mathbf{x} \in \mathbb{R}^n : \mathbf{Ax} = \mathbf{0}\}$$

### ទ្រឹស្តីបទ rank-nullity

$$
\text{rank}(\mathbf{A}) + \dim(\text{null}(\mathbf{A})) = n
$$

ដែល $n$ ​= ចំនួន​ជួរ​ឈរ​នៃ $\mathbf{A}$។

### លក្ខណៈរបស់ rank

| លក្ខណៈ | រូបមន្ត |
|---|---|
| Bound លើ | $\text{rank}(\mathbf{A}) \leq \min(m, n)$ |
| Full rank (ស្ដូប) | $\text{rank}(\mathbf{A}) = n$ ⟺ ជួរ​ឈរ​ឯករាជ្យ |
| Rank នៃ​ការ​ផ្ទេរ | $\text{rank}(\mathbf{A}^\top) = \text{rank}(\mathbf{A})$ |
| Rank នៃ​ផល​គុណ | $\text{rank}(\mathbf{AB}) \leq \min(\text{rank}(\mathbf{A}), \text{rank}(\mathbf{B}))$ |

## ៥. Orthogonality

វ៉ិចទ័រ $\mathbf{a}, \mathbf{b}$ **orthogonal** ⟺

$$\mathbf{a} \cdot \mathbf{b} = \mathbf{a}^\top \mathbf{b} = 0$$

ក្នុង​ធរណីមាត្រ៖ កែង​គ្នា 90°។

សំណុំ **orthonormal** $\{\mathbf{q}_1, \ldots, \mathbf{q}_k\}$៖

$$
\mathbf{q}_i^\top \mathbf{q}_j = \begin{cases} 1 & \text{if } i = j \\ 0 & \text{if } i \neq j \end{cases} = \delta_{ij}
$$

(orthogonal + ប្រវែង​ 1)

## ៦. ម៉ាទ្រីស orthogonal

$\mathbf{Q} \in \mathbb{R}^{n \times n}$ **orthogonal** ⟺ ជួរ​ឈរ​នៃ​វា​បង្កើត​ជា​សំណុំ orthonormal។ ស្មើ​នឹង៖

$$\mathbf{Q}^\top \mathbf{Q} = \mathbf{Q} \mathbf{Q}^\top = \mathbf{I}$$

ដូច្នេះ $\mathbf{Q}^{-1} = \mathbf{Q}^\top$ — **ការច្រាស​គ្រាន់​តែ​ជា​ការ​ផ្ទេរ!** (លឿន, ស្ថេរភាព​ខ្ពស់)

### លក្ខណៈរបស់ម៉ាទ្រីស orthogonal

| លក្ខណៈ | ហេតុអ្វីសំខាន់ |
|---|---|
| រក្សា​ប្រវែង៖ $\\|\mathbf{Qx}\\| = \\|\mathbf{x}\\|$ | គឺ​ការ​បង្វិល ឬ​ឆ្លុះ |
| រក្សា​ផល​គុណ​ចំណុច៖ $(\mathbf{Qx})^\top(\mathbf{Qy}) = \mathbf{x}^\top \mathbf{y}$ | រក្សា​មុំ |
| $\det(\mathbf{Q}) = \pm 1$ | មិន​ផ្លាស់​មាឌ |

## ៧. ការផ្លាស់មូលដ្ឋាន

ប្រសិន​បើ $\mathbf{B}$ មាន​ជួរ​ឈរ​ជា​មូលដ្ឋាន​ថ្មី, គ្រប់​វ៉ិចទ័រ $\mathbf{x}$ ក្នុង​មូលដ្ឋាន​ស្ដង់​ដារ​មាន​កូអរដោនេ​ថ្មី៖

$$\mathbf{x}_{\text{new}} = \mathbf{B}^{-1} \mathbf{x}$$

ប្រសិន​បើ $\mathbf{B}$ ជា orthogonal, នេះ​ជា​ការ​បង្វិល​ប្រព័ន្ធ​អ័ក្ស​ដ៏​សាមញ្ញ៖ $\mathbf{x}_{\text{new}} = \mathbf{Q}^\top \mathbf{x}$។ នេះ​ជា​អ្វី​ដែល **PCA** ធ្វើ។

---

# ឧទាហរណ៍

## ឧទាហរណ៍ ១៖ លក្ខណៈ​ស្ទួន​ក្នុង​ទិន្នន័យ Prasac

ឧបមា​ថា dataset មាន​ជួរ​ឈរ៖

| កសិករ | ចំណូល KHR (លាន) | ចំណូល USD |
|---|---:|---:|
| សុខា | 1.2 | 293 |
| ច័ន្ទថា | 0.8 | 195 |
| ដារ៉ា | 1.5 | 366 |

តើ​ជួរ​ឈរ "KHR" និង "USD" ឯករាជ្យ​ឬ​អត់?

ចំណាំ​ថា $\text{USD} = \text{KHR} / 0.0041 \cdot 10^{-6}$ (ត្រូវ​នឹង 1 USD = 4,100 KHR)។ ដូច្នេះ៖

$$
\text{column}_{\text{USD}} = \frac{1{,}000{,}000}{4{,}100} \cdot \text{column}_{\text{KHR}} \approx 244 \cdot \text{column}_{\text{KHR}}
$$

ជួរ​ឈរ​មួយ​ជា​គុណ​នៃ​ដទៃ ⟹ **លីនេអ៊ែរ​អាស្រ័យ**, ហើយ $\text{rank}(\mathbf{X}) = 1$ (មិន​មែន 2)។

**ការ​ដោះស្រាយ៖** យក​ជួរ​ឈរ​មួយ​ចេញ​មុន​ការ training។

## ឧទាហរណ៍ ២៖ Rank

រក $\text{rank}(\mathbf{A})$ ដែល៖

$$
\mathbf{A} = \begin{bmatrix} 1 & 2 & 3 \\ 2 & 4 & 6 \\ 1 & 1 & 1 \end{bmatrix}
$$

ជួរ​ទីពីរ = 2 × ជួរ​ទីមួយ, ដូច្នេះ​ជួរ​ឯករាជ្យ​មាន​តែ​ពីរ ⟹ $\text{rank}(\mathbf{A}) = 2$។

តាម rank-nullity, $\dim(\text{null}(\mathbf{A})) = 3 - 2 = 1$។

## ឧទាហរណ៍ ៣៖ Null space

រក null space នៃ $\mathbf{A} = \begin{bmatrix} 1 & 2 \\ 2 & 4 \end{bmatrix}$។

យើង​ដោះ​ស្រាយ $\mathbf{Ax} = \mathbf{0}$៖ $x_1 + 2x_2 = 0 \Rightarrow x_1 = -2x_2$។

ដូច្នេះ $\text{null}(\mathbf{A}) = \left\{ t \begin{bmatrix} -2 \\ 1 \end{bmatrix} : t \in \mathbb{R} \right\}$ — បន្ទាត់​មួយ​ឆ្លង​កាត់​សូន្យ។

---

# កូដ Python

```python
import numpy as np
from numpy.linalg import matrix_rank, qr

# ===== ឧទាហរណ៍ ១៖ ស្វែងរកលក្ខណៈស្ទួននៅក្នុង Prasac dataset =====
# 3 farmers, 2 features: [income_KHR_million, income_USD]
X = np.array([
    [1.2, 293],
    [0.8, 195],
    [1.5, 366],
])

print(f"rank = {matrix_rank(X)}")   # 1 — មិនមែន 2!
print(f"shape = {X.shape}")
# ⚠️  Warning: linearly dependent features

# យកជួរឈរ USD ចេញដោយសារវាស្ទួន
X_clean = X[:, [0]]
print(f"clean rank = {matrix_rank(X_clean)}")   # 1 — តាមការរំពឹង

# ===== ឧទាហរណ៍ ២៖ Rank ឯករាជ្យ​ពេញ =====
A = np.array([[1, 2, 3],
              [2, 4, 6],
              [1, 1, 1]], dtype=float)
print(matrix_rank(A))      # 2 — មិនពេញ

# ===== ឧទាហរណ៍ ៣៖ រក null space ដោយ SVD =====
def null_space(A, tol=1e-10):
    U, s, Vt = np.linalg.svd(A)
    null_dim = A.shape[1] - matrix_rank(A)
    return Vt[-null_dim:].T

N = null_space(A)
print(N)                   # មូលដ្ឋាននៃ null space
print(A @ N)               # ≈ 0  ✓

# ===== ឧទាហរណ៍ ៤៖ Orthogonality និង QR =====
q1 = np.array([1, 0, 0])
q2 = np.array([0, 1, 0])
print(q1 @ q2)             # 0  →  orthogonal

# QR decomposition — សាងម៉ាទ្រីស orthogonal
A = np.random.randn(4, 4)
Q, R = qr(A)
print(np.allclose(Q.T @ Q, np.eye(4)))   # True

# ការរក្សាប្រវែង (isometry)
x = np.random.randn(4)
print(np.allclose(np.linalg.norm(Q @ x),
                  np.linalg.norm(x)))      # True
```

> **គន្លឹះ៖** `numpy.linalg.matrix_rank` ឬ `scipy.linalg.null_space` គឺ​ឧបករណ៍​ស្ដង់ដារ​សម្រាប់​ការ​វិភាគ​នេះ។

---

# ការអនុវត្តន៍ជាក់ស្ដែង

## ១. ការ​សម្អាត​លក្ខណៈ​ស្ទួន​ក្នុង​ទិន្នន័យ​មីក្រូហិរញ្ញវត្ថុ

មុន​ការ training គំរូ ML នៅ Prasac/AMK/LOLC, អ្នក​វិទ្យាសាស្ត្រ​ទិន្នន័យ​ត្រូវ​ពិនិត្យ​មើល rank ដើម្បី​ស្វែងរក​៖

| លក្ខណៈ​ស្ទួន​ដែល​អាច​លេច​ឡើង​ក្នុង dataset​មីក្រូហិរញ្ញវត្ថុ​ខ្មែរ | មូលហេតុ |
|---|---|
| income_KHR និង income_USD | ឯកតា​ខុស​គ្នា​នៃ​លេខ​ដូច​គ្នា |
| land_hectare និង land_sqm | 1 ha = 10,000 sqm |
| total_loan_amount និង monthly_installment × duration | ជា​ផល​គុណ​លីនេអ៊ែរ |
| household_size និង num_children + num_adults | ផល​បូក​ល្អៗ |

**វិធី​ដោះ​ស្រាយ៖**
- ប្រើ `matrix_rank` ឬ correlation matrix ដើម្បី​រក
- យក​ជួរ​ឈរ​ស្ទួន​ចេញ
- ឬ​ប្រើ **Ridge regression** ($\mathbf{X}^\top \mathbf{X} + \lambda \mathbf{I}$ តែង​តែ​ច្រាស​បាន)
- ឬ​ប្រើ **pseudo-inverse** (ស្ថេរ​ភាព​ខ្ពស់​ជាង)

## ២. PCA = ការ​ផ្លាស់​ទៅ​មូលដ្ឋាន orthonormal

PCA រក orthonormal basis ដែល​អ័ក្ស​នីមួយៗ​ចង្អុល​ទៅ​ទិស​នៃ​ការ​ប្រែប្រួល​ខ្ពស់​បំផុត។ ការ​បកប្រែ​ទិន្នន័យ​ទៅ​មូលដ្ឋាន​នេះ​គឺ​គ្រាន់​តែ​ការ​គុណ​ដោយ​ម៉ាទ្រីស orthogonal — ដោយ​សារ $\mathbf{Q}^\top \mathbf{Q} = \mathbf{I}$, គ្មាន​ព័ត៌មាន​ត្រូវ​បាន​បាត់​បង់​នៅ​ពេល​ផ្លាស់​ទៅ​មក​វិញ​ឡើយ។

ក្នុង​ប្រទេស​កម្ពុជា, PCA អាច​ប្រើ​ដើម្បី៖
- កាត់​បន្ថយ​លក្ខណៈ 30+ ​នៃ​អតិថិជន​ Wing/ABA សម្រាប់​ការ visualization
- បំបែក "Phnom Penh customer profile" vs "rural customer profile" ដោយ​ស្វ័យ​ប្រវត្តិ

## ៣. QR decomposition

រាល់​ម៉ាទ្រីស $\mathbf{A}$ អាច​បំ​បែក​ជា $\mathbf{A} = \mathbf{QR}$ ដែល $\mathbf{Q}$ orthogonal និង $\mathbf{R}$ ត្រីកោណ​លើ។ នេះ​ជា​មូលដ្ឋាន​នៃ​ការ​ដោះ​ស្រាយ least squares យ៉ាង​មាន​ស្ថេរ​ភាព​ខាង​លេខ — ប្រើ​ច្រើន​ជាង​សមីការ​ធម្មតា​ផ្ទាល់​ក្នុង​ការ​ងារ​ផលិតផល (ឧ. `sklearn.linear_model.LinearRegression` ប្រើ QR ខាង​ក្នុង)។

---

# លំហាត់

1. តើ $\mathbf{v}_1 = (1, 0, 1)^\top$, $\mathbf{v}_2 = (1, 1, 0)^\top$, $\mathbf{v}_3 = (0, 1, 1)^\top$ ឯករាជ្យ​ឬ​អត់?
2. ប្រសិន​បើ $\mathbf{A} \in \mathbb{R}^{5 \times 3}$ និង $\text{rank}(\mathbf{A}) = 2$, តើ $\dim(\text{null}(\mathbf{A})) = ?$
3. អ្នក​មាន dataset ឥណទាន​ដែល​មាន​លក្ខណៈ​៖ `monthly_income_KHR`, `monthly_income_USD`, `age`, `hectares`, `family_size`។ តើ rank អតិបរមា​ដែល​អាច​មាន​គឺ​ប៉ុន្មាន?

> **ចម្លើយ៖**
> (1) គណនា $\det\begin{bmatrix} 1 & 1 & 0 \\ 0 & 1 & 1 \\ 1 & 0 & 1 \end{bmatrix} = 1(1) - 1(-1) + 0 = 2 \neq 0$ ⟹ **ឯករាជ្យ**
> (2) $\dim(\text{null}(\mathbf{A})) = n - \text{rank} = 3 - 2 = 1$
> (3) **4** — ដោយ​សារ KHR និង USD ស្ទួន​គ្នា, លក្ខណៈ​ឯករាជ្យ​ពិត​ប្រាកដ​មាន​តែ 4 ($\{$income, age, hectares, family$\}$)

---

**មេរៀនបន្ទាប់ (ជំពូក 1d):** តម្លៃ​ផ្ទាល់​ខ្លួន (eigenvalues), វ៉ិចទ័រ​ផ្ទាល់​ខ្លួន (eigenvectors), diagonalization, positive (semi)definite matrices, norms, និង trace — មេរៀន​ចុង​ក្រោយ​បំផុត​នៃ​ពិជគណិត​លីនេអ៊ែរ។
