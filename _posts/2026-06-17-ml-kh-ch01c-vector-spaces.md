---
layout: post
title: "[ML Khmer] ជំពូក 1c: លំហវ៉ិចទ័រ — ឯករាជ្យ, មូលដ្ឋាន, និង orthogonality"
date: 2026-06-17 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, math, linear-algebra]
---

មេរៀននេះស្វែងយល់​អំពី​រចនាសម្ព័ន្ធ​ខាងក្នុង​នៃ​លំហ​វ៉ិចទ័រ៖ **លីនេអ៊ែរ​ឯករាជ្យ** (linear independence), **លំហ​សាង** (span), **មូលដ្ឋាន** (basis), **rank**, **null space**, និង **orthogonality** — គំនិត​ដែល​ស្ថិត​នៅ​ពី​ក្រោម PCA, SVD, និង​គ្រប់​បច្ចេកទេស DR ក្នុង ML។

---

# សង្ខេប

- **លីនេអ៊ែរ​ឯករាជ្យ** ⟺ គ្មាន​វ៉ិចទ័រ​មួយ​ណា​ដែល​អាច​សរសេរ​ជា​ផល​បូក​លីនេអ៊ែរ​នៃ​វ៉ិចទ័រ​ដទៃ
- **មូលដ្ឋាន** = សំណុំ​ឯករាជ្យ​ដែល​សាង​លំហ​ទាំងមូល
- **Rank** នៃ​ម៉ាទ្រីស = ចំនួន​ជួរ​ឈរ​ឯករាជ្យ​អតិបរមា
- **Null space** = សំណុំ​នៃ $\mathbf{x}$ ដែល $\mathbf{Ax} = \mathbf{0}$
- **វ៉ិចទ័រ orthogonal**៖ $\mathbf{a} \cdot \mathbf{b} = 0$; **ម៉ាទ្រីស orthogonal**៖ $\mathbf{Q}^\top \mathbf{Q} = \mathbf{I}$

---

# ហេតុអ្វីសំខាន់?

នេះ​មិន​មែន​ជា​គណិតវិទ្យា​ដែល​មិន​មាន​ប្រយោជន៍​ទេ — វា​ឆ្លុះ​បញ្ចាំង​ដោយ​ផ្ទាល់​ក្នុង ML៖

- **Rank** ប្រាប់​យើង​ថា​លក្ខណៈ​ប៉ុន្មាន​ដែល​ពិត​ជា​ផ្ដល់​ព័ត៌មាន​ឯករាជ្យ — ប្រសិន​បើ​លក្ខណៈ​ពីរ​ជា​ផល​បូក​លីនេអ៊ែរ​នៃ​លក្ខណៈ​ដទៃ, វា​ត្រូវ​បាន​លុប
- **Null space** ប្រាប់​យើង​ថា​ហេតុ​អ្វី​សមីការ​ធម្មតា $\mathbf{X}^\top \mathbf{X} \mathbf{w} = \mathbf{X}^\top \mathbf{y}$ ច្រើន​តែ​មាន​ដំណោះ​ស្រាយ​ច្រើន
- **Orthogonality** គឺ​ស្នូល​នៃ PCA — components សំខាន់ៗ​ទាំងអស់​ត្រូវ​ជា orthogonal គ្នា
- **ការផ្លាស់​មូលដ្ឋាន** គឺ​ជា​អ្វី​ដែល autoencoder និង​ការ​បកប្រែ​លក្ខណៈ​ធ្វើ​ក្នុង​ស្នូល

---

# ពាក្យបច្ចេកទេសថ្មី

| ខ្មែរ | English | កំណត់សម្គាល់ |
|---|---|---|
| ផលបូកលីនេអ៊ែរ | linear combination | $c_1 \mathbf{v}_1 + c_2 \mathbf{v}_2 + \cdots + c_k \mathbf{v}_k$ |
| លីនេអ៊ែរឯករាជ្យ | linearly independent | គ្មាន​វ៉ិចទ័រ​ជា​ផល​បូក​នៃ​អ្នក​ដទៃ |
| លីនេអ៊ែរអាស្រ័យ | linearly dependent | មាន​យ៉ាង​ហោច​មួយ​ជា​ផល​បូក​នៃ​អ្នក​ដទៃ |
| លំហសាង (span) | span | សំណុំ​នៃ​ផល​បូក​លីនេអ៊ែរ​ទាំងអស់ |
| មូលដ្ឋាន | basis | សំណុំ​ឯករាជ្យ​ដែល​សាង​លំហ |
| វិមាត្រ | dimension | ចំនួន​វ៉ិចទ័រ​ក្នុង​មូលដ្ឋាន |
| Rank | rank | $\text{rank}(\mathbf{A})$ — ចំនួន​ជួរ​ឈរ​ឯករាជ្យ |
| លំហជួរឈរ | column space / range | លំហ​សាង​ដោយ​ជួរ​ឈរ​នៃ $\mathbf{A}$ |
| លំហសូន្យ | null space / kernel | $\{\mathbf{x} : \mathbf{Ax} = \mathbf{0}\}$ |
| Orthogonal | orthogonal | កែង​គ្នា ($\mathbf{a} \cdot \mathbf{b} = 0$) |
| Orthonormal | orthonormal | orthogonal + normalized ($\|\mathbf{v}\| = 1$) |
| ម៉ាទ្រីស orthogonal | orthogonal matrix | $\mathbf{Q}^\top \mathbf{Q} = \mathbf{I}$ |

---

# គំនិតវិចារណញ្ញាណ

## លីនេអ៊ែរឯករាជ្យ

ស្រមៃ​ថា​អ្នក​មាន​ទិស​បី៖ ខាងជើង, ខាងកើត, និង **ឦសាន​** (NE)។ "ឦសាន" មិន​ឯករាជ្យ​ទេ — វា​ជា​ផល​បូក​នៃ "ខាងជើង" និង "ខាងកើត"។ ដូច្នេះ​អ្នក​មាន **ទិស​ឯករាជ្យ​ពីរ** ប៉ុណ្ណោះ។

## មូលដ្ឋាន

មូលដ្ឋាន = សំណុំ​អប្បបរមា​នៃ​ទិស​ដែល​អាច​ឱ្យ​អ្នក​ឈាន​ដល់​គ្រប់​ចំណុច​ក្នុង​លំហ។ សម្រាប់ $\mathbb{R}^2$, មូលដ្ឋាន​ស្ដង់ដារ​គឺ៖

$$
\mathbf{e}_1 = \begin{bmatrix} 1 \\ 0 \end{bmatrix}, \quad \mathbf{e}_2 = \begin{bmatrix} 0 \\ 1 \end{bmatrix}
$$

ប្រសិន​បើ​អ្នក​ដឹង "ខាង​ណា" និង​ "ប៉ុន្មាន​ដង" សម្រាប់​មូលដ្ឋាន​នីមួយៗ, អ្នក​ដឹង​ចំណុច។

## Rank

រាប់​ចំនួន​ជួរ​ឈរ​នៃ $\mathbf{A}$ ដែល​ឯករាជ្យ — នេះ​គឺ "ខ្លឹមសារ​ព័ត៌មាន​ពិត" នៃ​ម៉ាទ្រីស។

## Null space

ប្រសិន​បើ​អ្នក​ដឹង​ដំណោះស្រាយ​មួយ​នៃ $\mathbf{Ax} = \mathbf{b}$, គ្រប់​វ៉ិចទ័រ​ក្នុង null space​ បន្ថែម​ទៅ​នឹង​ដំណោះ​ស្រាយ​នោះ​ក៏​ជា​ដំណោះ​ស្រាយ​ផង​ដែរ។ Null space ​ច្រើន​ជាង​សូន្យ ⟺ ដំណោះ​ស្រាយ​ច្រើន។

---

# និយមន័យ និងគណិតវិទ្យា

## ១. ផលបូកលីនេអ៊ែរ និងលំហសាង

ផល​បូក​លីនេអ៊ែរ​នៃ $\mathbf{v}_1, \ldots, \mathbf{v}_k$៖

$$
c_1 \mathbf{v}_1 + c_2 \mathbf{v}_2 + \cdots + c_k \mathbf{v}_k \quad \text{ដែល } c_i \in \mathbb{R}
$$

**លំហសាង** (span)៖

$$
\text{span}(\mathbf{v}_1, \ldots, \mathbf{v}_k) = \left\{ \sum_{i=1}^k c_i \mathbf{v}_i : c_i \in \mathbb{R} \right\}
$$

## ២. លីនេអ៊ែរឯករាជ្យ

$\{\mathbf{v}_1, \ldots, \mathbf{v}_k\}$ **ឯករាជ្យ** ⟺ សមីការ​ខាង​ក្រោម​មាន​តែ​ដំណោះ​ស្រាយ​សូន្យ៖

$$
c_1 \mathbf{v}_1 + c_2 \mathbf{v}_2 + \cdots + c_k \mathbf{v}_k = \mathbf{0} \implies c_1 = c_2 = \cdots = c_k = 0
$$

បើ​មាន​ដំណោះ​ស្រាយ​មិន​សូន្យ, វា **អាស្រ័យ**។

## ៣. មូលដ្ឋាន និង វិមាត្រ

**មូលដ្ឋាន** នៃ​លំហ $V$ = សំណុំ​នៃ​វ៉ិចទ័រ​ដែល៖
1. ឯករាជ្យ
2. សាង $V$ (i.e., $\text{span} = V$)

**វិមាត្រ** $\dim(V)$ = ចំនួន​វ៉ិចទ័រ​ក្នុង​មូលដ្ឋាន (ដូច​គ្នា​សម្រាប់​មូលដ្ឋាន​ទាំងអស់)។

## ៤. Rank, លំហ​ជួរ​ឈរ, និង null space

សម្រាប់ $\mathbf{A} \in \mathbb{R}^{m \times n}$៖

- **លំហ​ជួរ​ឈរ** (column space, range)៖
$$\text{col}(\mathbf{A}) = \text{span}(\text{columns of } \mathbf{A}) \subseteq \mathbb{R}^m$$

- **Rank**៖
$$\text{rank}(\mathbf{A}) = \dim(\text{col}(\mathbf{A}))$$

- **Null space** (kernel)៖
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
| Full rank (ស្តូប) | $\text{rank}(\mathbf{A}) = n$ ⟺ ជួរ​ឈរ​ឯករាជ្យ |
| Rank នៃ​ការ​ផ្ទេរ | $\text{rank}(\mathbf{A}^\top) = \text{rank}(\mathbf{A})$ |
| Rank នៃ​ផល​គុណ | $\text{rank}(\mathbf{AB}) \leq \min(\text{rank}(\mathbf{A}), \text{rank}(\mathbf{B}))$ |

## ៥. Orthogonality

វ៉ិចទ័រ $\mathbf{a}, \mathbf{b}$ **orthogonal** ⟺

$$\mathbf{a} \cdot \mathbf{b} = \mathbf{a}^\top \mathbf{b} = 0$$

សំណុំ **orthonormal** $\{\mathbf{q}_1, \ldots, \mathbf{q}_k\}$៖

$$
\mathbf{q}_i^\top \mathbf{q}_j = \begin{cases} 1 & \text{បើ } i = j \\ 0 & \text{បើ } i \neq j \end{cases}
$$

## ៦. ម៉ាទ្រីស orthogonal

$\mathbf{Q} \in \mathbb{R}^{n \times n}$ **orthogonal** ⟺ ជួរ​ឈរ​នៃ​វា​បង្កើត​ជា​សំណុំ orthonormal។ ស្មើ​នឹង៖

$$\mathbf{Q}^\top \mathbf{Q} = \mathbf{Q} \mathbf{Q}^\top = \mathbf{I}$$

ដូច្នេះ $\mathbf{Q}^{-1} = \mathbf{Q}^\top$ — **ការច្រាស​គ្រាន់​តែ​ជា​ការ​ផ្ទេរ!**

### លក្ខណៈរបស់ម៉ាទ្រីស orthogonal

| លក្ខណៈ | ហេតុ​អ្វី​សំខាន់ |
|---|---|
| រក្សា​ប្រវែង៖ $\\|\mathbf{Qx}\\| = \\|\mathbf{x}\\|$ | គឺ​ការ​បង្វិល ឬ​ឆ្លុះ |
| រក្សា​ផល​គុណ​ចំណុច៖ $(\mathbf{Qx})^\top(\mathbf{Qy}) = \mathbf{x}^\top \mathbf{y}$ | រក្សា​មុំ |
| $\det(\mathbf{Q}) = \pm 1$ | មិន​ផ្លាស់​មាឌ |

## ៧. ការផ្លាស់មូលដ្ឋាន

ប្រសិន​បើ $\mathbf{B}$ មាន​ជួរ​ឈរ​ជា​មូលដ្ឋាន​ថ្មី, គ្រប់​វ៉ិចទ័រ $\mathbf{x}$ ក្នុង​មូលដ្ឋាន​ស្ដង់ដារ​មាន​កូអរដោនេ​ថ្មី៖

$$\mathbf{x}_{\text{new}} = \mathbf{B}^{-1} \mathbf{x}$$

ប្រសិន​បើ $\mathbf{B}$ ជា orthogonal, នេះ​ជា​ការ​បង្វិល​ប្រព័ន្ធ​អ័ក្ស​ដ៏​សាមញ្ញ៖ $\mathbf{x}_{\text{new}} = \mathbf{Q}^\top \mathbf{x}$។ នេះ​ជា​អ្វី​ដែល **PCA** ធ្វើ។

---

# ឧទាហរណ៍

## ឧទាហរណ៍ ១៖ ឯករាជ្យ ឬ​អាស្រ័យ?

តើ $\mathbf{v}_1 = (1, 2)^\top$, $\mathbf{v}_2 = (2, 4)^\top$ ឯករាជ្យ​ឬទេ?

ចំណាំ​ថា $\mathbf{v}_2 = 2 \mathbf{v}_1$, ដូច្នេះ $2\mathbf{v}_1 - \mathbf{v}_2 = \mathbf{0}$ ជា​មួយ​មេគុណ​មិន​សូន្យ ⟹ **អាស្រ័យ**។

## ឧទាហរណ៍ ២៖ Rank

រក $\text{rank}(\mathbf{A})$ ដែល៖

$$
\mathbf{A} = \begin{bmatrix} 1 & 2 & 3 \\ 2 & 4 & 6 \\ 1 & 1 & 1 \end{bmatrix}
$$

ជួរ​ទីពីរ = ២ × ជួរ​ទីមួយ, ដូច្នេះ​ជួរ​ឯករាជ្យ​មាន​តែ​ពីរ ⟹ $\text{rank}(\mathbf{A}) = 2$។

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

# ឧទាហរណ៍ ២ ដែលនិយាយខាងលើ
A = np.array([[1, 2, 3],
              [2, 4, 6],
              [1, 1, 1]], dtype=float)

print(matrix_rank(A))      # 2

# រក null space ដោយ SVD
def null_space(A, tol=1e-10):
    U, s, Vt = np.linalg.svd(A)
    null_mask = s < tol
    null_dim = A.shape[1] - matrix_rank(A)
    return Vt[-null_dim:].T

N = null_space(A)
print(N)                   # ជួរ​ឈរ​ផ្ដល់​មូលដ្ឋាន​នៃ null space
print(A @ N)               # ≈ 0  ✓ ផ្ទៀង​ផ្ទាត់

# ផ្ទៀង​ផ្ទាត់ orthogonality
q1 = np.array([1, 0, 0])
q2 = np.array([0, 1, 0])
print(q1 @ q2)             # 0  →  orthogonal

# QR decomposition — សាង​ម៉ាទ្រីស orthogonal
A = np.random.randn(4, 4)
Q, R = qr(A)
print(np.allclose(Q.T @ Q, np.eye(4)))   # True  →  Q ជា orthogonal

# ផ្ទៀង​ផ្ទាត់​ការ​រក្សា​ប្រវែង
x = np.random.randn(4)
print(np.allclose(np.linalg.norm(Q @ x),
                  np.linalg.norm(x)))      # True
```

> **គន្លឹះ៖** `numpy.linalg.matrix_rank` និង `scipy.linalg.null_space` គឺ​ឧបករណ៍​ស្ដង់ដារ។

---

# ការអនុវត្តន៍ជាក់ស្តែង

## ១. ការ​លុប​លក្ខណៈ​លីនេអ៊ែរ​អាស្រ័យ

នៅ​ពេល $\mathbf{X}^\top \mathbf{X}$ ច្រាស​មិន​បាន ​(rank ​មិន​ពេញ), linear regression​ មាន​ដំណោះ​ស្រាយ​ច្រើន​ឬ​ច្រាសវាត់​មិន​ស្ថិត​ស្ថេរ។ វិធី​ដោះ​ស្រាយ៖
- លុប​លក្ខណៈ​ដែល​ជា​ផល​បូក​លីនេអ៊ែរ​នៃ​លក្ខណៈ​ដទៃ
- ប្រើ Ridge regression ($\mathbf{X}^\top \mathbf{X} + \lambda \mathbf{I}$ ​តែង​តែ​ច្រាស​បាន)
- ប្រើ pseudo-inverse

## ២. PCA = ការ​ផ្លាស់​ទៅ​មូលដ្ឋាន orthonormal

PCA រក orthonormal basis ដែល​អ័ក្ស​នីមួយៗ​ចង្អុល​ទៅ​ទិស​នៃ​ការ​ប្រែប្រួល​ខ្ពស់​បំផុត។ ការ​បកប្រែ​ទិន្នន័យ​ទៅ​មូលដ្ឋាន​នេះ​គឺ​គ្រាន់​តែ​ជា​ការ​គុណ​ដោយ​ម៉ាទ្រីស orthogonal — ដោយ​សារ​តែ $\mathbf{Q}^\top \mathbf{Q} = \mathbf{I}$, គ្មាន​ព័ត៌មាន​ត្រូវ​បាន​បាត់​បង់​ទេ ​នៅ​ពេល​ផ្លាស់​ទៅ​មកវិញ​ឡើយ។

## ៣. QR decomposition

រាល់​ម៉ាទ្រីស $\mathbf{A}$ អាច​បំ​បែក​ជា $\mathbf{A} = \mathbf{QR}$ ដែល $\mathbf{Q}$ orthogonal និង $\mathbf{R}$ ត្រីកោណ​លើ។ នេះ​ជា​មូលដ្ឋាន​នៃ​ការ​ដោះ​ស្រាយ​ least squares យ៉ាង​មាន​ស្ថេរ​ភាព​ខាង​លេខ — ប្រើ​ច្រើន​ជាង​សមីការ​ធម្មតា​ផ្ទាល់​ក្នុង​ការ​ងារ​ផលិតផល។

---

# លំហាត់

1. តើ $\mathbf{v}_1 = (1, 0, 1)^\top$, $\mathbf{v}_2 = (1, 1, 0)^\top$, $\mathbf{v}_3 = (0, 1, 1)^\top$ ឯករាជ្យ​ឬ​អត់?
2. ប្រសិន​បើ $\mathbf{A} \in \mathbb{R}^{5 \times 3}$ និង $\text{rank}(\mathbf{A}) = 2$, តើ $\dim(\text{null}(\mathbf{A})) = ?$
3. សរសេរ​កូដ NumPy ដើម្បី (a) សាង​ម៉ាទ្រីស orthogonal $3 \times 3$ ដោយ​ចៃ​ដន្យ និង (b) ផ្ទៀង​ផ្ទាត់​ថា $\mathbf{Q}^\top \mathbf{Q} = \mathbf{I}$។

> **ចម្លើយ៖**
> (1) គណនា $\det\begin{bmatrix} 1 & 1 & 0 \\ 0 & 1 & 1 \\ 1 & 0 & 1 \end{bmatrix} = 1(1) - 1(-1) + 0 = 2 \neq 0$ ⟹ **ឯករាជ្យ**
> (2) $\dim(\text{null}(\mathbf{A})) = n - \text{rank} = 3 - 2 = 1$
> (3) `Q, _ = np.linalg.qr(np.random.randn(3, 3)); np.allclose(Q.T @ Q, np.eye(3))` → `True`

---

**មេរៀនបន្ទាប់ (ជំពូក 1d):** តម្លៃ​ផ្ទាល់​ខ្លួន (eigenvalues), វ៉ិចទ័រ​ផ្ទាល់​ខ្លួន (eigenvectors), diagonalization, positive (semi)definite matrices, norms, និង trace — ជា​មេរៀន​ចុង​ក្រោយ​បំផុត​នៃ​ពិជគណិត​លីនេអ៊ែរ។
