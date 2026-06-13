---
layout: post
title: "[ML Khmer] ជំពូក 1b: ម៉ាទ្រីសពិសេស, ការច្រាស, និងឌីទែរមីណង់"
date: 2026-06-16 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, math, linear-algebra]
---

មេរៀននេះបន្តពី​ពិជគណិត​លីនេអ៊ែរ​មូលដ្ឋាន។ យើង​ស្វែងយល់​អំពី **ម៉ាទ្រីស​ពិសេស** (special matrices), **ការច្រាស​ម៉ាទ្រីស** (matrix inverse), និង **ឌីទែរមីណង់** (determinant) — បី​ប្រធានបទ​ដែល​លេច​ឡើង​គ្រប់​ទីកន្លែង​ក្នុង ML។ យើង​នឹង​អនុវត្ត​វា​ដើម្បី​ព្យាករ​តម្លៃ​អាផាតមិន​នៅ BKK1 ភ្នំពេញ។

---

# សង្ខេប

- ម៉ាទ្រីសពិសេសសំខាន់ៗ៖ **ឯកតា** $\mathbf{I}$, **សូន្យ** $\mathbf{0}$, **អង្កត់ទ្រូង**, **ត្រីកោណ**, **ស៊ីមេទ្រី**
- **ការច្រាស** $\mathbf{A}^{-1}$ ដោះស្រាយសមីការ $\mathbf{Ax} = \mathbf{b}$ ដោយ $\mathbf{x} = \mathbf{A}^{-1}\mathbf{b}$
- **ឌីទែរមីណង់** $\det(\mathbf{A})$ ជា​លេខ​មួយ​ដែល​ប្រាប់​ថា​ម៉ាទ្រីសច្រាស​បាន​ឬ​អត់
- ច្បាប់​សំខាន់៖ $\mathbf{A}$ ច្រាស​បាន ⟺ $\det(\mathbf{A}) \neq 0$

---

# ហេតុអ្វីសំខាន់?

ក្នុង ML, យើង​តែង​តែ​ដោះ​ស្រាយ​សមីការ​លីនេអ៊ែរ​ដូចជា៖

$$
\mathbf{X}^\top \mathbf{X} \mathbf{w} = \mathbf{X}^\top \mathbf{y}
$$

នេះ​គឺ **សមីការ​ធម្មតា** (normal equation) សម្រាប់ linear regression — ស្នូល​នៃ​ការ​ព្យាករ​តម្លៃ​ផ្ទះ, ការ​ព្យាករ​ផល​រ៉ូងស្រូវ, ការ​ព្យាករ​ហានិភ័យ​ឥណទាន។ ដើម្បី​ដោះ​ស្រាយ​វា, យើង​ត្រូវ​ការ​ការច្រាស៖

$$
\mathbf{w} = (\mathbf{X}^\top \mathbf{X})^{-1} \mathbf{X}^\top \mathbf{y}
$$

ចែករំលែក​ជា​មួយ​នោះ៖
- **ម៉ាទ្រីស​ស៊ីមេទ្រី** លេច​ឡើង​គ្រប់​ទីកន្លែង (covariance matrix, Gram matrix $\mathbf{X}^\top\mathbf{X}$)
- **ម៉ាទ្រីស​អង្កត់​ទ្រូង** ប្រើ​សម្រាប់ normalization និង scaling នៃ​លក្ខណៈ
- **ឌីទែរមីណង់** លេច​ឡើង​ក្នុង​ការ​ប្រមាណ​ការ​ចែកចាយ​ហ្គោសុ៊ស (Gaussian distribution)

---

# ពាក្យបច្ចេកទេសថ្មី

| ខ្មែរ | English | កំណត់សម្គាល់ |
|---|---|---|
| ម៉ាទ្រីសឯកតា | identity matrix | $\mathbf{I}$ — អង្កត់​ទ្រូង​ជាលេខ ១, ធាតុ​ដទៃ​ជា​សូន្យ |
| ម៉ាទ្រីសសូន្យ | zero matrix | $\mathbf{0}$ — រាល់​ធាតុ​ជា​សូន្យ |
| ម៉ាទ្រីសអង្កត់ទ្រូង | diagonal matrix | ធាតុ​ខាង​ក្រៅ​អង្កត់​ទ្រូង​ជា​សូន្យ​ទាំង​អស់ |
| ម៉ាទ្រីសត្រីកោណ | triangular matrix | ខាង​លើ ឬ​ខាង​ក្រោម​អង្កត់​ទ្រូង​ជា​សូន្យ |
| ម៉ាទ្រីសស៊ីមេទ្រី | symmetric matrix | $\mathbf{A}^\top = \mathbf{A}$ |
| ការច្រាសម៉ាទ្រីស | matrix inverse | $\mathbf{A}^{-1}$ — សម្គាល់​ដោយ $\mathbf{A}\mathbf{A}^{-1} = \mathbf{I}$ |
| ច្រាសបាន | invertible / nonsingular | ម៉ាទ្រីស​មាន​ការច្រាស |
| ច្រាសមិនបាន | singular | ម៉ាទ្រីស​គ្មាន​ការច្រាស |
| ឌីទែរមីណង់ | determinant | $\det(\mathbf{A})$ — លេខ​ដែល​ប្រាប់​ច្រាសបាន/មិនបាន |
| ស្យូដូ-ច្រាស | pseudo-inverse | $\mathbf{A}^+$ — សម្រាប់​ម៉ាទ្រីស​មិន​ការេ |

---

# គំនិតវិចារណញ្ញាណ

## ម៉ាទ្រីសឯកតា

ដូច​លេខ $1$ ក្នុង​ការ​គុណ​ធម្មតា៖ $1 \cdot x = x$។ ម៉ាទ្រីស​ឯកតា​មាន​លក្ខណៈ​ដូច​គ្នា៖

$$\mathbf{I} \mathbf{A} = \mathbf{A} \mathbf{I} = \mathbf{A}$$

មិន​ផ្លាស់​ប្ដូរ​អ្វី​នៅ​ពេល​គុណ។

## ការច្រាស

ដូច​ការ​ច្រាស​លេខ​ធម្មតា៖ $5 \cdot \frac{1}{5} = 1$។ ម៉ាទ្រីស​ច្រាស​ធ្វើ​ដូចគ្នា៖

$$\mathbf{A} \mathbf{A}^{-1} = \mathbf{A}^{-1} \mathbf{A} = \mathbf{I}$$

ប៉ុន្តែ **មិនមែន​ម៉ាទ្រីស​ទាំងអស់​មាន​ការច្រាស​ទេ** — ដូច​ជា​លេខ $0$ មិន​មាន $\frac{1}{0}$។

## ឌីទែរមីណង់

លេខ​មួយ​ដែល​ប្រាប់​ភ្លាមៗ​ថា​ម៉ាទ្រីស​ច្រាស​បាន​ឬ​អត់៖
- $\det(\mathbf{A}) = 0$ ⟹ ម៉ាទ្រីស​ច្រាស​មិន​បាន (singular)
- $\det(\mathbf{A}) \neq 0$ ⟹ ម៉ាទ្រីស​ច្រាស​បាន (invertible)

តាម​ធរណីមាត្រ, $|\det(\mathbf{A})|$ គឺ​ជា **មាត្រដ្ឋាន​នៃ​មាឌ** (volume scaling factor) ដែល​ម៉ាទ្រីស​ផ្លាស់​ប្ដូរ។

---

# និយមន័យ និងគណិតវិទ្យា

## ១. ម៉ាទ្រីសឯកតា

$$
\mathbf{I}_3 = \begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}
$$

ធាតុ៖ $I_{ij} = 1$ បើ $i = j$, និង $0$ បើ​ផ្សេង។

## ២. ម៉ាទ្រីសសូន្យ

$$
\mathbf{0}_{2 \times 3} = \begin{bmatrix} 0 & 0 & 0 \\ 0 & 0 & 0 \end{bmatrix}
$$

## ៣. ម៉ាទ្រីសអង្កត់ទ្រូង

$$
\mathbf{D} = \begin{bmatrix} d_1 & 0 & 0 \\ 0 & d_2 & 0 \\ 0 & 0 & d_3 \end{bmatrix}
$$

ការ​គុណ​ម៉ាទ្រីស​អង្កត់​ទ្រូង​ងាយ​ស្រួល​ខ្លាំង៖ $\mathbf{D}\mathbf{x}$ គ្រាន់​តែ​គុណ​ធាតុ​នីមួយៗ​នៃ $\mathbf{x}$ ដោយ $d_i$ ដែល​ត្រូវ​គ្នា។

**ការ​ប្រើ​ក្នុង ML៖** ការ​ធ្វើ​មាត្រ​ដ្ឋាន​លក្ខណៈ (feature scaling)។ ប្រសិន​បើ​ "ផ្ទៃ​ដី" មាន​តម្លៃ 0.5–5 និង "ប្រាក់​ចំណូល" មាន​តម្លៃ 600,000–1,500,000, យើង​ប្រើ​ម៉ាទ្រីស​អង្កត់​ទ្រូង​ដើម្បី​នាំ​ពួក​វា​មក​ស្ថិត​នៅ​លំដាប់​ដូច​គ្នា។

## ៤. ម៉ាទ្រីសត្រីកោណ

**ត្រីកោណលើ** (upper triangular)៖ ធាតុ​ខាង​ក្រោម​អង្កត់​ទ្រូង​សុទ្ធ​តែ​សូន្យ៖

$$
\mathbf{U} = \begin{bmatrix} 1 & 2 & 3 \\ 0 & 4 & 5 \\ 0 & 0 & 6 \end{bmatrix}
$$

**ត្រីកោណក្រោម** (lower triangular)៖ ខាង​លើ​សូន្យ​វិញ។

## ៥. ម៉ាទ្រីសស៊ីមេទ្រី

$$\mathbf{A}^\top = \mathbf{A} \quad \text{or} \quad A_{ij} = A_{ji}$$

ឧទាហរណ៍៖

$$
\begin{bmatrix} 1 & 7 & 3 \\ 7 & 5 & 2 \\ 3 & 2 & 9 \end{bmatrix}
$$

ម៉ាទ្រីស​ស៊ីមេទ្រី​មាន​លក្ខណៈ​ល្អ​ច្រើន — តម្លៃ​ផ្ទាល់​ខ្លួន (eigenvalue) ទាំង​អស់​ជា​លេខ​ពិត, និង​មាន​ការ​បំបែក​អង្កត់​ទ្រូង។ ម៉ាទ្រីស covariance ក្នុង​ស្ថិតិ​ និង Gram matrix $\mathbf{X}^\top\mathbf{X}$ ក្នុង ML — សុទ្ធ​តែ​ស៊ីមេទ្រី។

## ៦. ការច្រាសម៉ាទ្រីស

$\mathbf{A}^{-1}$ មាន​ប្រសិន​បើ៖

$$\mathbf{A}\mathbf{A}^{-1} = \mathbf{A}^{-1}\mathbf{A} = \mathbf{I}$$

**លក្ខខណ្ឌ៖**
1. $\mathbf{A}$ ត្រូវ​តែ​ជា​ម៉ាទ្រីស​ការ៉េ ($n \times n$)
2. $\det(\mathbf{A}) \neq 0$

### រូបមន្តសម្រាប់ $2 \times 2$

$$
\mathbf{A} = \begin{bmatrix} a & b \\ c & d \end{bmatrix}, \quad \mathbf{A}^{-1} = \frac{1}{ad - bc} \begin{bmatrix} d & -b \\ -c & a \end{bmatrix}
$$

### លក្ខណៈសំខាន់ៗ

| លក្ខណៈ | រូបមន្ត |
|---|---|
| ការច្រាសនៃផលគុណ | $(\mathbf{AB})^{-1} = \mathbf{B}^{-1}\mathbf{A}^{-1}$ |
| ការច្រាសនៃការផ្ទេរ | $(\mathbf{A}^\top)^{-1} = (\mathbf{A}^{-1})^\top$ |
| ការច្រាសពីរដង | $(\mathbf{A}^{-1})^{-1} = \mathbf{A}$ |
| ឌីទែរមីណង់នៃការច្រាស | $\det(\mathbf{A}^{-1}) = 1/\det(\mathbf{A})$ |

## ៧. ស្យូដូ-ច្រាស (Pseudo-inverse)

នៅ​ពេល​ដែល $\mathbf{A}$ មិន​ជា​ការ៉េ ឬ​ច្រាស​មិន​បាន, យើង​ប្រើ **Moore-Penrose pseudo-inverse**៖

$$
\mathbf{A}^{+} = (\mathbf{A}^\top \mathbf{A})^{-1} \mathbf{A}^\top \quad \text{(if } \mathbf{A}^\top\mathbf{A} \text{ is invertible)}
$$

នេះ​ត្រូវ​ប្រើ​ច្រើន​ក្នុង **least squares** និង **linear regression** នៅ​ពេល​ដែល​ចំនួន​សមីការ​ច្រើន​ជាង​អថេរ — ឧ. ទិន្នន័យ​អាផាតមិន 100 ឯកតា ដើម្បី​រក​ទម្ងន់ 3 (sqm, bedrooms, floor)។

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
| ឌីទែរមីណង់នៃផលគុណ | $\det(\mathbf{AB}) = \det(\mathbf{A})\det(\mathbf{B})$ |
| ឌីទែរមីណង់នៃការផ្ទេរ | $\det(\mathbf{A}^\top) = \det(\mathbf{A})$ |
| ឌីទែរមីណង់នៃការច្រាស | $\det(\mathbf{A}^{-1}) = 1/\det(\mathbf{A})$ |
| ឯកតា និងសូន្យ | $\det(\mathbf{I}) = 1$, $\det(\mathbf{0}) = 0$ |
| ម៉ាទ្រីសត្រីកោណ | $\det(\mathbf{T}) = \prod_i T_{ii}$ (ផលគុណអង្កត់ទ្រូង) |

---

# ឧទាហរណ៍

## ឧទាហរណ៍ ១៖ ការច្រាសនៃម៉ាទ្រីស $2 \times 2$

រក $\mathbf{A}^{-1}$ ដែល $\mathbf{A} = \begin{bmatrix} 4 & 7 \\ 2 & 6 \end{bmatrix}$។

**គណនា​ឌីទែរមីណង់​មុន៖**

$$\det(\mathbf{A}) = (4)(6) - (7)(2) = 24 - 14 = 10$$

ដោយ $\det(\mathbf{A}) = 10 \neq 0$, ការច្រាស​មាន។

$$
\mathbf{A}^{-1} = \frac{1}{10} \begin{bmatrix} 6 & -7 \\ -2 & 4 \end{bmatrix} = \begin{bmatrix} 0.6 & -0.7 \\ -0.2 & 0.4 \end{bmatrix}
$$

**ផ្ទៀង​ផ្ទាត់៖** $\mathbf{A}\mathbf{A}^{-1} = \mathbf{I}$? បាទ ✓

## ឧទាហរណ៍ ២៖ ដោះ​ស្រាយ​សមីការ​ព្យាករ​តម្លៃ​អាផាតមិន BKK1

ឧបមា​ថា​អ្នក​អ្នក​មាន​ទិន្នន័យ​អាផាតមិន 2 ឯកតា​នៅ BKK1៖

| អាផាតមិន | ផ្ទៃ (sqm) | តម្លៃ (ពាន់ USD) |
|---|---:|---:|
| Unit A | 40 | 160 |
| Unit B | 80 | 280 |

យើង​ឧបមា​គំរូ​លីនេអ៊ែរ​សាមញ្ញ​មួយ៖

$$
\text{price} = w_0 + w_1 \cdot \text{sqm}
$$

ដែល $w_0$ = តម្លៃ​មូលដ្ឋាន (base price) និង $w_1$ = តម្លៃ​ក្នុង​មួយ sqm។

តំណាង​ជា​សមីការ​ម៉ាទ្រីស៖

$$
\begin{bmatrix} 1 & 40 \\ 1 & 80 \end{bmatrix} \begin{bmatrix} w_0 \\ w_1 \end{bmatrix} = \begin{bmatrix} 160 \\ 280 \end{bmatrix}
$$

$$\mathbf{X} \mathbf{w} = \mathbf{y}$$

**ដំណាក់​កាល ១៖ ឌីទែរមីណង់**

$$\det(\mathbf{X}) = (1)(80) - (40)(1) = 40 \neq 0 \quad \checkmark$$

**ដំណាក់​កាល ២៖ ការច្រាស**

$$
\mathbf{X}^{-1} = \frac{1}{40}\begin{bmatrix} 80 & -40 \\ -1 & 1 \end{bmatrix} = \begin{bmatrix} 2 & -1 \\ -0.025 & 0.025 \end{bmatrix}
$$

**ដំណាក់​កាល ៣៖ ដោះ​ស្រាយ**

$$
\mathbf{w} = \mathbf{X}^{-1} \mathbf{y} = \begin{bmatrix} 2 & -1 \\ -0.025 & 0.025 \end{bmatrix} \begin{bmatrix} 160 \\ 280 \end{bmatrix} = \begin{bmatrix} 320 - 280 \\ -4 + 7 \end{bmatrix} = \begin{bmatrix} 40 \\ 3 \end{bmatrix}
$$

**លទ្ធផល៖**

$$
\text{price} = 40 + 3 \cdot \text{sqm} \quad (\text{ពាន់ USD})
$$

**ការ​ព្យាករ​សម្រាប់​អាផាតមិន​ថ្មី​ទំហំ 60 sqm៖**

$$
\text{price} = 40 + 3(60) = 220 \text{ ពាន់ USD} \approx \$220{,}000
$$

នេះ​ជា **closed-form solution** នៃ linear regression — បាន​មក​ដោយ​ការ​ច្រាស​ម៉ាទ្រីស​ដោយ​ផ្ទាល់។

---

# កូដ Python

```python
import numpy as np

# ===== ម៉ាទ្រីសពិសេស =====
I = np.eye(3)                        # ម៉ាទ្រីសឯកតា 3×3
Z = np.zeros((2, 3))                 # ម៉ាទ្រីសសូន្យ
D = np.diag([2, 5, 7])               # ម៉ាទ្រីសអង្កត់ទ្រូង
U = np.triu([[1, 2, 3],              # ត្រីកោណលើ
             [4, 5, 6],
             [7, 8, 9]])

# ម៉ាទ្រីសស៊ីមេទ្រី — A + A.T តែងតែស៊ីមេទ្រី
A = np.array([[1, 2], [3, 4]], dtype=float)
S = A + A.T
print(np.allclose(S, S.T))           # True

# ===== ឌីទែរមីណង់ និងការច្រាស =====
A = np.array([[4, 7], [2, 6]], dtype=float)
print(np.linalg.det(A))              # 10.0
A_inv = np.linalg.inv(A)
print(A_inv)
# [[ 0.6 -0.7]
#  [-0.2  0.4]]

# ផ្ទៀងផ្ទាត់៖ A @ A_inv ≈ I
print(np.allclose(A @ A_inv, np.eye(2)))   # True

# ===== ព្យាករតម្លៃអាផាតមិន BKK1 =====
# Data: [intercept_col, sqm]
X = np.array([[1, 40],
              [1, 80]], dtype=float)
y = np.array([160, 280], dtype=float)   # ពាន់ USD

# វិធីល្អ៖ ប្រើ np.linalg.solve (លឿន+ស្ថេរភាពលេខច្រើនជាង)
w = np.linalg.solve(X, y)
print(f"w = {w}")                       # [40.  3.]
print(f"price = {w[0]} + {w[1]} * sqm")

# ការព្យាករសម្រាប់ 60 sqm
new_apartment = np.array([1, 60])
price = new_apartment @ w
print(f"60 sqm → ${price*1000:,.0f}")   # $220,000

# ===== ស្យូដូ-ច្រាស (សម្រាប់ dataset ធំ) =====
# 10 apartments
np.random.seed(42)
sqm = np.random.uniform(30, 120, 10)
prices = 40 + 3*sqm + np.random.randn(10)*5   # +noise
X_big = np.column_stack([np.ones(10), sqm])
w_hat = np.linalg.pinv(X_big) @ prices
print(f"រកមកវិញ៖ {w_hat}")               # ≈ [40, 3]
```

> **គន្លឹះ៖** ប្រើ `np.linalg.solve(A, b)` ជា​ជាង `np.linalg.inv(A) @ b` — លឿន​ជាង​និង​មាន​ភាព​ត្រឹមត្រូវ​ខាង​លេខ​ច្រើន​ជាង។

---

# ការអនុវត្តន៍ជាក់ស្ដែង

## ១. ការវាយតម្លៃអចលនទ្រព្យនៅភ្នំពេញ

ក្រុមហ៊ុន​អចលនទ្រព្យ​ដូចជា **Knight Frank Cambodia**, **CBRE Cambodia**, ឬ​ស្ថាប័ន​ស្រាវ​ជ្រាវ​ក្នុងស្រុក​ប្រើ linear regression ជាមួយ​លក្ខណៈ​ច្រើន​ដើម្បី​ព្យាករ​តម្លៃ៖

$$
\text{price} = w_0 + w_1(\text{sqm}) + w_2(\text{bedrooms}) + w_3(\text{floor}) + w_4(\text{distance to BKK1}) + \cdots
$$

ដោះ​ស្រាយ​ដោយ៖

$$
\mathbf{w}^* = (\mathbf{X}^\top \mathbf{X})^{-1} \mathbf{X}^\top \mathbf{y} = \mathbf{X}^+ \mathbf{y}
$$

```python
# ឧទាហរណ៍ជាមួយ 100 apartments នៅ BKK1
np.random.seed(0)
n = 100
sqm = np.random.uniform(30, 150, n)
bedrooms = np.random.choice([1, 2, 3], n)
floor = np.random.randint(1, 30, n)

# តម្លៃ "ពិត" (ដើម្បីបង្ហាញ)
true_w = np.array([20, 2.5, 15, 1.0])
X = np.column_stack([np.ones(n), sqm, bedrooms, floor])
y = X @ true_w + np.random.randn(n)*5

# ដោះស្រាយ
w_hat = np.linalg.pinv(X) @ y
print(w_hat)   # ≈ [20, 2.5, 15, 1.0]
```

## ២. ការ​ចែកចាយ​ហ្គោសុ៊ស​ច្រើន​វិមាត្រ

ឌីទែរមីណង់​នៃ​ម៉ាទ្រីស covariance លេច​ឡើង​ក្នុង​អនុគមន៍​ដង់ស៊ីតេ​នៃ Gaussian distribution ច្រើន​វិមាត្រ៖

$$
p(\mathbf{x}) = \frac{1}{\sqrt{(2\pi)^d \det(\boldsymbol{\Sigma})}} \exp\left(-\frac{1}{2}(\mathbf{x} - \boldsymbol{\mu})^\top \boldsymbol{\Sigma}^{-1} (\mathbf{x} - \boldsymbol{\mu})\right)
$$

នេះ​ប្រើ​ច្រើន​ក្នុង​ Naive Bayes (សម្រាប់ Khmer text classification, spam filter ភាសា​ខ្មែរ), Anomaly Detection (រក​ប្រតិបត្តិការ​ Wing/ABA ដែល​គួរ​សង្ស័យ), និង Gaussian Mixture Models។

---

# លំហាត់

1. គណនា​ឌីទែរមីណង់​នៃ $\mathbf{A} = \begin{bmatrix} 3 & 1 \\ 5 & 2 \end{bmatrix}$ និង​រក $\mathbf{A}^{-1}$ ប្រសិន​បើ​មាន។
2. បញ្ជាក់​ថា $\mathbf{B} = \begin{bmatrix} 2 & 4 \\ 1 & 2 \end{bmatrix}$ ច្រាស​មិន​បាន។
3. ឧបមា​ថា​អ្នក​មាន​ទិន្នន័យ​អាផាតមិន​បន្ថែម​មួយ​នៅ BKK1៖ Unit C ទំហំ 100 sqm តម្លៃ $340,000។ ប្រើ​គំរូ $\text{price} = 40 + 3 \cdot \text{sqm}$ ដែល​យើង​ទទួល​បាន​ខាង​លើ — តើ​ការ​ព្យាករ​មាន​កំហុស​ប៉ុន្មាន?

> **ចម្លើយ៖**
> (1) $\det(\mathbf{A}) = 6 - 5 = 1$, $\mathbf{A}^{-1} = \begin{bmatrix} 2 & -1 \\ -5 & 3 \end{bmatrix}$
> (2) $\det(\mathbf{B}) = 4 - 4 = 0 \Rightarrow$ ច្រាស​មិន​បាន
> (3) ការ​ព្យាករ: $40 + 3(100) = 340$ ($340,000$) → កំហុស 0 — គំរូ​ត្រូវ​ល្អ ✓

---

**មេរៀនបន្ទាប់ (ជំពូក 1c):** លំហ​វ៉ិចទ័រ — លីនេអ៊ែរ​ឯករាជ្យ, span, basis, rank, null space, និង orthogonality — និង​ប្រើ​ដើម្បី​យល់​បញ្ហា​ លក្ខណៈ​ស្ទួន (redundant features) ក្នុង dataset។
