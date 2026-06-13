---
layout: post
title: "[ML Khmer] ជំពូក 1b: ម៉ាទ្រីសពិសេស, ការច្រាស, និងឌីទែរមីណង់"
date: 2026-06-16 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, math, linear-algebra]
---

មេរៀននេះបន្តពីពិជគណិតលីនេអ៊ែរមូលដ្ឋាន។ យើងស្វែងយល់អំពី **ម៉ាទ្រីសពិសេស** (special matrices), **ការច្រាសម៉ាទ្រីស** (matrix inverse), និង **ឌីទែរមីណង់** (determinant) — បីប្រធានបទដែលលេចឡើងគ្រប់ទីកន្លែងក្នុង ML។

---

# សង្ខេប

- ម៉ាទ្រីសពិសេសសំខាន់ៗ៖ **ឯកតា** $\mathbf{I}$, **សូន្យ** $\mathbf{0}$, **អង្កត់ទ្រូង**, **ត្រីកោណ**, **ស៊ីមេទ្រី**
- **ការច្រាស** $\mathbf{A}^{-1}$ ដោះស្រាយសមីការ $\mathbf{Ax} = \mathbf{b}$ ដោយ $\mathbf{x} = \mathbf{A}^{-1}\mathbf{b}$
- **ឌីទែរមីណង់** $\det(\mathbf{A})$ ជាលេខមួយដែលប្រាប់ថា​ម៉ាទ្រីសមាន​ការច្រាស​ឬអត់
- ច្បាប់សំខាន់៖ $\mathbf{A}$ មាន​ការច្រាស ⟺ $\det(\mathbf{A}) \neq 0$

---

# ហេតុអ្វីសំខាន់?

ក្នុង ML, យើងតែងតែដោះស្រាយ​សមីការ​លីនេអ៊ែរ​ដូចជា៖

$$
\mathbf{X}^\top \mathbf{X} \mathbf{w} = \mathbf{X}^\top \mathbf{y}
$$

នេះគឺ **សមីការធម្មតា** (normal equation) សម្រាប់ linear regression។ ដើម្បីដោះស្រាយវា, យើងត្រូវការ​ការច្រាស៖

$$
\mathbf{w} = (\mathbf{X}^\top \mathbf{X})^{-1} \mathbf{X}^\top \mathbf{y}
$$

ចែករំលែកគ្នាជាមួយនោះ៖
- **ម៉ាទ្រីសស៊ីមេទ្រី** លេចឡើងគ្រប់ទីកន្លែង (covariance, Gram matrix $\mathbf{X}^\top\mathbf{X}$)
- **ម៉ាទ្រីសអង្កត់ទ្រូង** ប្រើសម្រាប់ normalization និង scaling
- **ឌីទែរមីណង់** លេចឡើងក្នុង​ការ​ប្រមាណ​អនុគមន៍​ហ្គោសុ៊ស (Gaussian density)

---

# ពាក្យបច្ចេកទេសថ្មី

| ខ្មែរ | English | កំណត់សម្គាល់ |
|---|---|---|
| ម៉ាទ្រីសឯកតា | identity matrix | $\mathbf{I}$ — អង្កត់ទ្រូងជាលេខ ១, រាល់ធាតុ​ដទៃ​ជា​សូន្យ |
| ម៉ាទ្រីសសូន្យ | zero matrix | $\mathbf{0}$ — រាល់ធាតុជាសូន្យ |
| ម៉ាទ្រីសអង្កត់ទ្រូង | diagonal matrix | ធាតុ​ខាង​ក្រៅ​អង្កត់ទ្រូង​ជា​សូន្យ​ទាំងអស់ |
| ម៉ាទ្រីសត្រីកោណ | triangular matrix | ខាងលើ ឬខាងក្រោម​អង្កត់ទ្រូង​ជា​សូន្យ |
| ម៉ាទ្រីសស៊ីមេទ្រី | symmetric matrix | $\mathbf{A}^\top = \mathbf{A}$ |
| ការច្រាសម៉ាទ្រីស | matrix inverse | $\mathbf{A}^{-1}$ — សម្គាល់ដោយ $\mathbf{A}\mathbf{A}^{-1} = \mathbf{I}$ |
| ច្រាសបាន | invertible / nonsingular | ម៉ាទ្រីសមាន​ការច្រាស |
| ច្រាសមិនបាន | singular | ម៉ាទ្រីសគ្មាន​ការច្រាស |
| ឌីទែរមីណង់ | determinant | $\det(\mathbf{A})$ ឬ $\|\mathbf{A}\|$ |
| ស្យូដូ-ច្រាស | pseudo-inverse | $\mathbf{A}^+$ — សម្រាប់ម៉ាទ្រីសមិនជាការេ |

---

# គំនិតវិចារណញ្ញាណ

## ម៉ាទ្រីសឯកតា

ដូច​លេខ $1$ ក្នុង​ការគុណធម្មតា៖ $1 \cdot x = x$។ ម៉ាទ្រីស​ឯកតា​មាន​លក្ខណៈ​ដូច​គ្នា៖

$$\mathbf{I} \mathbf{A} = \mathbf{A} \mathbf{I} = \mathbf{A}$$

## ការច្រាស

ដូច​ការ​ច្រាសលេខ៖ $5 \cdot \frac{1}{5} = 1$។ ម៉ាទ្រីសច្រាសធ្វើ​ដូចគ្នា៖

$$\mathbf{A} \mathbf{A}^{-1} = \mathbf{A}^{-1} \mathbf{A} = \mathbf{I}$$

ប៉ុន្តែ​**មិនមែន​ម៉ាទ្រីសទាំងអស់​មាន​ការច្រាស​ទេ** — ដូច $0$ មិនមាន $\frac{1}{0}$។

## ឌីទែរមីណង់

លេខមួយដែលប្រាប់ថា​ម៉ាទ្រីសច្រាសបាន​ឬអត់៖
- $\det(\mathbf{A}) = 0$ ⟹ ម៉ាទ្រីសច្រាសមិនបាន (singular)
- $\det(\mathbf{A}) \neq 0$ ⟹ ម៉ាទ្រីសច្រាសបាន (invertible)

តាមធរណីមាត្រ, $|\det(\mathbf{A})|$ គឺជា​មាត្រដ្ឋាន (scaling factor) នៃ​មាឌ​ដែល​ម៉ាទ្រីសផ្លាស់ប្តូរ។

---

# និយមន័យ និងគណិតវិទ្យា

## ១. ម៉ាទ្រីសឯកតា

$$
\mathbf{I}_3 = \begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}
$$

ធាតុ៖ $I_{ij} = 1$ បើ $i = j$, និង $0$ បើដទៃ។

## ២. ម៉ាទ្រីសសូន្យ

$$
\mathbf{0}_{2 \times 3} = \begin{bmatrix} 0 & 0 & 0 \\ 0 & 0 & 0 \end{bmatrix}
$$

## ៣. ម៉ាទ្រីសអង្កត់ទ្រូង

$$
\mathbf{D} = \begin{bmatrix} d_1 & 0 & 0 \\ 0 & d_2 & 0 \\ 0 & 0 & d_3 \end{bmatrix}
$$

ការគុណ​ម៉ាទ្រីសអង្កត់ទ្រូង​ងាយ​ស្រួល​ខ្លាំង៖ $\mathbf{D}\mathbf{x}$ គ្រាន់​តែ​គុណ​ធាតុ​នីមួយៗ​នៃ $\mathbf{x}$ ដោយ $d_i$ ដែល​ត្រូវ​គ្នា។

## ៤. ម៉ាទ្រីសត្រីកោណ

**ត្រីកោណលើ** (upper triangular)៖ ធាតុ​ខាង​ក្រោម​អង្កត់ទ្រូង​សុទ្ធ​តែ​សូន្យ៖

$$
\mathbf{U} = \begin{bmatrix} 1 & 2 & 3 \\ 0 & 4 & 5 \\ 0 & 0 & 6 \end{bmatrix}
$$

**ត្រីកោណក្រោម** (lower triangular)៖ ខាង​លើ​សូន្យ​វិញ។

## ៥. ម៉ាទ្រីសស៊ីមេទ្រី

$$\mathbf{A}^\top = \mathbf{A} \quad \text{ឬ} \quad A_{ij} = A_{ji}$$

ឧទាហរណ៍៖

$$
\begin{bmatrix} 1 & 7 & 3 \\ 7 & 5 & 2 \\ 3 & 2 & 9 \end{bmatrix}
$$

ម៉ាទ្រីស​ស៊ីមេទ្រី​មាន​លក្ខណៈ​ល្អ​ជាច្រើន — តម្លៃ​ផ្ទាល់ខ្លួន​ទាំងអស់​ជា​លេខ​ពិត, និង​មាន​អង្គ​បង្ហាញ​អង្កត់​ទ្រូង។

## ៦. ការច្រាសម៉ាទ្រីស

$\mathbf{A}^{-1}$ មាន​ប្រសិន​បើ៖

$$\mathbf{A}\mathbf{A}^{-1} = \mathbf{A}^{-1}\mathbf{A} = \mathbf{I}$$

**លក្ខខណ្ឌ៖**
1. $\mathbf{A}$ ត្រូវតែ​ជា​ម៉ាទ្រីសការ៉េ ($n \times n$)
2. $\det(\mathbf{A}) \neq 0$

### រូបមន្តសម្រាប់ $2 \times 2$

$$
\mathbf{A} = \begin{bmatrix} a & b \\ c & d \end{bmatrix}, \quad \mathbf{A}^{-1} = \frac{1}{ad - bc} \begin{bmatrix} d & -b \\ -c & a \end{bmatrix}
$$

### លក្ខណៈសំខាន់ៗ

| លក្ខណៈ | រូបមន្ត |
|---|---|
| ការច្រាសនៃ​ផល​គុណ | $(\mathbf{AB})^{-1} = \mathbf{B}^{-1}\mathbf{A}^{-1}$ |
| ការច្រាសនៃ​ការ​ផ្ទេរ | $(\mathbf{A}^\top)^{-1} = (\mathbf{A}^{-1})^\top$ |
| ការច្រាស​ពីរ​ដង | $(\mathbf{A}^{-1})^{-1} = \mathbf{A}$ |
| ឌីទែរមីណង់​នៃ​ការច្រាស | $\det(\mathbf{A}^{-1}) = 1/\det(\mathbf{A})$ |

## ៧. ស្យូដូ-ច្រាស (Pseudo-inverse)

នៅពេលដែល $\mathbf{A}$ មិន​ជា​ការេ ឬ​ច្រាស​មិន​បាន, យើង​ប្រើ **ស្យូដូ-ច្រាស​មូ៉-ផេនរូស** (Moore-Penrose pseudo-inverse)៖

$$
\mathbf{A}^{+} = (\mathbf{A}^\top \mathbf{A})^{-1} \mathbf{A}^\top \quad \text{(បើ } \mathbf{A}^\top\mathbf{A} \text{ ច្រាស​បាន)}
$$

នេះ​ត្រូវ​ប្រើ​ច្រើន​ក្នុង **least squares** និង **linear regression** នៅពេលដែល​ចំនួន​សមីការ​ច្រើន​ជាង​អថេរ។

## ៨. ឌីទែរមីណង់ (Determinant)

### សម្រាប់ $2 \times 2$

$$
\det\begin{bmatrix} a & b \\ c & d \end{bmatrix} = ad - bc
$$

### សម្រាប់ $3 \times 3$ (Cofactor expansion)

$$
\det\begin{bmatrix} a & b & c \\ d & e & f \\ g & h & i \end{bmatrix} = a(ei - fh) - b(di - fg) + c(dh - eg)
$$

### លក្ខណៈសំខាន់ៗ

| លក្ខណៈ | រូបមន្ត |
|---|---|
| ឌីទែរមីណង់​នៃ​ផល​គុណ | $\det(\mathbf{AB}) = \det(\mathbf{A})\det(\mathbf{B})$ |
| ឌីទែរមីណង់​នៃ​ការ​ផ្ទេរ | $\det(\mathbf{A}^\top) = \det(\mathbf{A})$ |
| ឌីទែរមីណង់​នៃ​ការច្រាស | $\det(\mathbf{A}^{-1}) = 1/\det(\mathbf{A})$ |
| ឯកតា​ និង​សូន្យ | $\det(\mathbf{I}) = 1$, $\det(\mathbf{0}) = 0$ |
| ម៉ាទ្រីសត្រីកោណ | $\det(\mathbf{T}) = \prod_i T_{ii}$ (ផល​គុណ​អង្កត់​ទ្រូង) |

---

# ឧទាហរណ៍

## ឧទាហរណ៍ ១៖ ការច្រាសនៃម៉ាទ្រីស $2 \times 2$

រក $\mathbf{A}^{-1}$ ដែល $\mathbf{A} = \begin{bmatrix} 4 & 7 \\ 2 & 6 \end{bmatrix}$។

**គណនា​ឌីទែរមីណង់​មុន​៖**

$$\det(\mathbf{A}) = (4)(6) - (7)(2) = 24 - 14 = 10$$

ដោយ $\det(\mathbf{A}) = 10 \neq 0$, ការច្រាស​មាន។

$$
\mathbf{A}^{-1} = \frac{1}{10} \begin{bmatrix} 6 & -7 \\ -2 & 4 \end{bmatrix} = \begin{bmatrix} 0.6 & -0.7 \\ -0.2 & 0.4 \end{bmatrix}
$$

**ផ្ទៀង​ផ្ទាត់៖** $\mathbf{A}\mathbf{A}^{-1} = \mathbf{I}$? បាទ ✓

## ឧទាហរណ៍ ២៖ ដោះស្រាយ $\mathbf{Ax} = \mathbf{b}$

ដោះស្រាយ៖

$$
\begin{bmatrix} 4 & 7 \\ 2 & 6 \end{bmatrix} \mathbf{x} = \begin{bmatrix} 18 \\ 14 \end{bmatrix}
$$

$$
\mathbf{x} = \mathbf{A}^{-1}\mathbf{b} = \begin{bmatrix} 0.6 & -0.7 \\ -0.2 & 0.4 \end{bmatrix} \begin{bmatrix} 18 \\ 14 \end{bmatrix} = \begin{bmatrix} 10.8 - 9.8 \\ -3.6 + 5.6 \end{bmatrix} = \begin{bmatrix} 1 \\ 2 \end{bmatrix}
$$

---

# កូដ Python

```python
import numpy as np

# សាងម៉ាទ្រីសពិសេស
I = np.eye(3)                        # ម៉ាទ្រីសឯកតា
Z = np.zeros((2, 3))                 # ម៉ាទ្រីសសូន្យ
D = np.diag([2, 5, 7])               # ម៉ាទ្រីសអង្កត់ទ្រូង
U = np.triu([[1, 2, 3],              # ត្រីកោណលើ
             [4, 5, 6],
             [7, 8, 9]])

# សាងម៉ាទ្រីសស៊ីមេទ្រី
A = np.array([[1, 2], [3, 4]], dtype=float)
S = A + A.T                          # រាល់ A + A.T ជាស៊ីមេទ្រី

# ឌីទែរមីណង់
A = np.array([[4, 7], [2, 6]], dtype=float)
det_A = np.linalg.det(A)             # 10.0

# ការច្រាស
A_inv = np.linalg.inv(A)
print(A_inv)
# [[ 0.6 -0.7]
#  [-0.2  0.4]]

# ផ្ទៀងផ្ទាត់៖ A @ A_inv ≈ I
print(np.allclose(A @ A_inv, np.eye(2)))  # True

# ដោះស្រាយ Ax = b — វិធីល្អជាងការច្រាសផ្ទាល់
b = np.array([18, 14], dtype=float)
x = np.linalg.solve(A, b)            # [1. 2.]

# ស្យូដូ-ច្រាសសម្រាប់ម៉ាទ្រីសមិនជាការេ
M = np.array([[1, 2], [3, 4], [5, 6]], dtype=float)  # 3 × 2
M_plus = np.linalg.pinv(M)
print(M_plus.shape)                  # (2, 3)
```

> **គន្លឹះ៖** ប្រើ `np.linalg.solve(A, b)` ជាជាង `np.linalg.inv(A) @ b` — លឿនជាង និងមាន​ភាព​ត្រឹមត្រូវ​ខាងលេខ​ច្រើនជាង។

---

# ការអនុវត្តន៍ជាក់ស្តែង

**Linear regression closed-form solution.** ដើម្បីរក​ទម្ងន់​ល្អបំផុត $\mathbf{w}^*$ សម្រាប់ $\mathbf{y} \approx \mathbf{Xw}$, យើង​ដោះស្រាយ​សមីការ​ធម្មតា៖

$$
\mathbf{w}^* = (\mathbf{X}^\top \mathbf{X})^{-1} \mathbf{X}^\top \mathbf{y} = \mathbf{X}^+ \mathbf{y}
$$

ដែល $\mathbf{X}^+$ គឺ​ស្យូដូ-ច្រាស។ កូដ៖

```python
import numpy as np

# សាងទិន្នន័យសាក
np.random.seed(0)
X = np.random.randn(100, 3)
true_w = np.array([1.5, -2.0, 0.5])
y = X @ true_w + np.random.randn(100) * 0.1

# ដោះស្រាយដោយ pseudo-inverse
w_hat = np.linalg.pinv(X) @ y
print(w_hat)  # [ 1.50  -2.00  0.50] ≈ true_w  ✓
```

នេះ​ជា​មូលដ្ឋាន​នៃ linear regression — យើង​នឹង​ស៊ីជម្រៅ​ក្នុង​ជំពូក 7។

**ក្នុង Gaussian distribution:** ឌីទែរមីណង់​នៃ​ម៉ាទ្រីស covariance លេចឡើង​ក្នុង​អនុគមន៍​ដង់ស៊ីតេ​នៃ​ការ​ចែកចាយ​ហ្គោសុ៊ស​ច្រើនវិមាត្រ៖

$$
p(\mathbf{x}) = \frac{1}{\sqrt{(2\pi)^d \det(\boldsymbol{\Sigma})}} \exp\left(-\frac{1}{2}(\mathbf{x} - \boldsymbol{\mu})^\top \boldsymbol{\Sigma}^{-1} (\mathbf{x} - \boldsymbol{\mu})\right)
$$

ដោយគ្មាន​ឌីទែរមីណង់ និង​ការច្រាស, យើង​មិន​អាច​ប្រើ​ការ​ចែកចាយ​ហ្គោសុ៊ស​ក្នុង ML បាន​ឡើយ។

---

# លំហាត់

1. គណនា​ឌីទែរមីណង់​នៃ $\mathbf{A} = \begin{bmatrix} 3 & 1 \\ 5 & 2 \end{bmatrix}$ និង​រក $\mathbf{A}^{-1}$ ប្រសិន​បើ​មាន។
2. បញ្ជាក់​ថា $\mathbf{B} = \begin{bmatrix} 2 & 4 \\ 1 & 2 \end{bmatrix}$ ច្រាស​មិន​បាន។
3. សរសេរ​កូដ NumPy ដើម្បី (a) សាង​ម៉ាទ្រីស​ស៊ីមេទ្រី​ $5 \times 5$ ដោយ​ចៃ​ដន្យ និង (b) ផ្ទៀង​ផ្ទាត់​ថា​វា​ស៊ីមេទ្រី។

> **ចម្លើយ៖**
> (1) $\det(\mathbf{A}) = 6 - 5 = 1$, $\mathbf{A}^{-1} = \begin{bmatrix} 2 & -1 \\ -5 & 3 \end{bmatrix}$
> (2) $\det(\mathbf{B}) = 4 - 4 = 0 \Rightarrow$ ច្រាស​មិន​បាន
> (3) `A = np.random.randn(5, 5); S = A + A.T; np.allclose(S, S.T)` → `True`

---

**មេរៀនបន្ទាប់ (ជំពូក 1c):** លីនេអ៊ែរ independence, span, basis, rank, range, null space, និង​ម៉ាទ្រីស​ orthogonal។
