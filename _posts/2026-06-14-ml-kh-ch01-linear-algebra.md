---
layout: post
title: "[ML Khmer] ជំពូក 1: ពិជគណិតលីនេអ៊ែរសម្រាប់ ML"
date: 2026-06-14 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, math, linear-algebra]
---

មេរៀនទី 2 — ការរំឭកគណិតវិទ្យាជាមូលដ្ឋានសម្រាប់ ML។ ក្នុងមេរៀននេះយើងនឹងស្វែងយល់អំពី **វ៉ិចទ័រ** (vector) និង **ម៉ាទ្រីស** (matrix) — ឧបករណ៍គណិតវិទ្យាដ៏សំខាន់បំផុតនៅពីក្រោយគ្រប់គំរូ ML។

---

# ហេតុអ្វីពិជគណិតលីនេអ៊ែរសំខាន់សម្រាប់ ML?

ទិន្នន័យក្នុង ML មិនមែនជាលេខតែមួយទេ — វាគឺជា **ការប្រមូលផ្តុំនៃលេខ**៖

- រូបភាពមួយ = ម៉ាទ្រីសនៃ pixel
- ឯកសារអក្សរមួយ = វ៉ិចទ័រនៃប្រេកង់ពាក្យ
- ទិន្នន័យអ្នកប្រើ ១០០០នាក់ × ២០លក្ខណៈ = ម៉ាទ្រីស ១០០០×២០

ប្រសិនបើយើងមិនអាចគណនាជាមួយវ៉ិចទ័រ និងម៉ាទ្រីសបានទេ, យើងមិនអាចសរសេរ ML បានឡើយ។

---

# វ៉ិចទ័រ (Vector)

**វ៉ិចទ័រ** គឺជាជួរនៃលេខ។ យើងសរសេរវាក្នុងទម្រង់នេះ៖

$$
\mathbf{x} = \begin{bmatrix} 2 \\ 5 \\ 1 \end{bmatrix}
$$

វ៉ិចទ័រនេះមាន **វិមាត្រ ៣** (3-dimensional)។ យើងអាចសរសេរថា $\mathbf{x} \in \mathbb{R}^3$ — មានន័យថា $\mathbf{x}$ គឺជាវ៉ិចទ័រនៃលេខពិតបី។

## ឧទាហរណ៍ក្នុង ML

ឧបមាថាយើងមានទិន្នន័យអ្នកប្រើម្នាក់៖

- អាយុ៖ ២៥
- ប្រាក់ចំណូល (USD)៖ ៣០០០
- ចំនួនថ្ងៃចូលគេហទំព័រ៖ ១៥

យើងតំណាងអ្នកប្រើនេះដោយវ៉ិចទ័រ៖

$$
\mathbf{u} = \begin{bmatrix} 25 \\ 3000 \\ 15 \end{bmatrix}
$$

នេះហៅថា **វ៉ិចទ័រលក្ខណៈ** (feature vector) — ផ្ទុកលក្ខណៈទាំងអស់នៃវត្ថុមួយ។

---

# ប្រមាណវិធីលើវ៉ិចទ័រ

## ១. បូក និងដក

បូកវ៉ិចទ័រពីរ — បូកធាតុនីមួយៗ៖

$$
\begin{bmatrix} 1 \\ 2 \end{bmatrix} + \begin{bmatrix} 3 \\ 4 \end{bmatrix} = \begin{bmatrix} 4 \\ 6 \end{bmatrix}
$$

> **ចំណាំ៖** វ៉ិចទ័រត្រូវតែមានវិមាត្រដូចគ្នាដើម្បីបូកគ្នាបាន។

## ២. គុណនឹងលេខ (scalar multiplication)

$$
3 \cdot \begin{bmatrix} 2 \\ -1 \end{bmatrix} = \begin{bmatrix} 6 \\ -3 \end{bmatrix}
$$

## ៣. ផលគុណចំណុច (Dot Product)

ផលគុណចំណុចជាប្រមាណវិធីសំខាន់បំផុតក្នុង ML។ សម្រាប់វ៉ិចទ័រ $\mathbf{a}, \mathbf{b} \in \mathbb{R}^n$៖

$$
\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^{n} a_i b_i = a_1 b_1 + a_2 b_2 + \cdots + a_n b_n
$$

ឧទាហរណ៍៖

$$
\begin{bmatrix} 1 \\ 2 \\ 3 \end{bmatrix} \cdot \begin{bmatrix} 4 \\ 5 \\ 6 \end{bmatrix} = 1(4) + 2(5) + 3(6) = 32
$$

> **ហេតុអ្វីសំខាន់?** គំរូ ML ភាគច្រើន (linear regression, logistic regression, neural networks) ប្រើផលគុណចំណុចដើម្បីផ្សំ​លក្ខណៈ​ជាមួយ **ទម្ងន់** (weights)៖
>
> $$y = w_1 x_1 + w_2 x_2 + \cdots + w_n x_n = \mathbf{w} \cdot \mathbf{x}$$

---

# ម៉ាទ្រីស (Matrix)

**ម៉ាទ្រីស** គឺជាតារាងលេខពីរវិមាត្រ — មានជួរ និងជួរឈរ៖

$$
\mathbf{A} = \begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \end{bmatrix}
$$

$\mathbf{A}$ មានទំហំ $2 \times 3$ — ២ ជួរ (row), ៣ ជួរឈរ (column)។ យើងសរសេរ $\mathbf{A} \in \mathbb{R}^{2 \times 3}$។

## ឧទាហរណ៍ក្នុង ML

**Dataset** ជាធម្មតាតំណាងដោយម៉ាទ្រីស៖

| | អាយុ | ប្រាក់ចំណូល | ថ្ងៃចូល |
|---|---|---|---|
| អ្នកប្រើ ១ | 25 | 3000 | 15 |
| អ្នកប្រើ ២ | 32 | 5000 | 22 |
| អ្នកប្រើ ៣ | 19 | 1200 | 8 |

ជា​ម៉ាទ្រីស៖

$$
\mathbf{X} = \begin{bmatrix} 25 & 3000 & 15 \\ 32 & 5000 & 22 \\ 19 & 1200 & 8 \end{bmatrix}
$$

ជួរនីមួយៗ = អ្នកប្រើម្នាក់ (មួយឧទាហរណ៍)។ ជួរឈរនីមួយៗ = លក្ខណៈមួយ។

---

# ប្រមាណវិធីលើម៉ាទ្រីស

## ១. ការផ្ទេរ (Transpose)

ការផ្ទេរផ្លាស់ប្តូរជួរទៅជួរឈរ៖

$$
\mathbf{A} = \begin{bmatrix} 1 & 2 \\ 3 & 4 \\ 5 & 6 \end{bmatrix}, \quad \mathbf{A}^\top = \begin{bmatrix} 1 & 3 & 5 \\ 2 & 4 & 6 \end{bmatrix}
$$

## ២. គុណម៉ាទ្រីស (Matrix Multiplication)

នេះគឺជាប្រមាណវិធីសំខាន់បំផុតក្នុង ML។ ប្រសិនបើ $\mathbf{A} \in \mathbb{R}^{m \times n}$ និង $\mathbf{B} \in \mathbb{R}^{n \times p}$, នោះ $\mathbf{C} = \mathbf{A}\mathbf{B} \in \mathbb{R}^{m \times p}$ ដែល៖

$$
C_{ij} = \sum_{k=1}^{n} A_{ik} B_{kj}
$$

> **ច្បាប់សំខាន់៖** ចំនួនជួរឈរនៃ $\mathbf{A}$ ត្រូវតែ​ស្មើ​ចំនួនជួរ​នៃ $\mathbf{B}$។

ឧទាហរណ៍៖

$$
\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix} \begin{bmatrix} 5 \\ 6 \end{bmatrix} = \begin{bmatrix} 1(5) + 2(6) \\ 3(5) + 4(6) \end{bmatrix} = \begin{bmatrix} 17 \\ 39 \end{bmatrix}
$$

---

# Python ជាមួយ NumPy

NumPy គឺជាបណ្ណាល័យ Python ស្តង់ដារសម្រាប់ពិជគណិតលីនេអ៊ែរ៖

```python
import numpy as np

# វ៉ិចទ័រ
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# ផលគុណចំណុច
print(a @ b)        # 32
print(np.dot(a, b)) # 32

# ម៉ាទ្រីស
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# គុណម៉ាទ្រីស
print(A @ B)
# [[19 22]
#  [43 50]]

# ការផ្ទេរ
print(A.T)
# [[1 3]
#  [2 4]]

# ទំហំ
print(A.shape)  # (2, 2)
```

> **គន្លឹះ៖** ប្រើ​សញ្ញា `@` សម្រាប់គុណម៉ាទ្រីស — ច្បាស់ជាង `np.dot()`។

---

# ការអនុវត្ត ML ដ៏សាមញ្ញ

ឧបមាថាយើងមាន​គំរូ​លីនេអ៊ែរ (linear model) ដែលព្យាករពិន្ទុ​អ្នកប្រើ​ពីលក្ខណៈរបស់គាត់៖

$$
\hat{y} = w_1 \cdot \text{អាយុ} + w_2 \cdot \text{ប្រាក់ចំណូល} + w_3 \cdot \text{ថ្ងៃចូល} + b
$$

ជា​ផល​គុណចំណុច៖

$$
\hat{y} = \mathbf{w} \cdot \mathbf{x} + b
$$

ក្នុង Python៖

```python
import numpy as np

# លក្ខណៈអ្នកប្រើ
x = np.array([25, 3000, 15])

# ទម្ងន់ដែលរៀនបាន (ឧទាហរណ៍)
w = np.array([0.1, 0.001, 0.5])
b = 1.0

# ការព្យាករ
y_hat = w @ x + b
print(y_hat)  # 1.0 + 2.5 + 3.0 + 7.5 = 14.0
```

នេះគឺជា​ស្នូលនៃ **linear regression** — យើងនឹង​ស្វែងយល់​ច្បាស់​ក្នុង​មេរៀន​បន្ទាប់ៗ។

---

# លំហាត់

ដើម្បីពង្រឹងការយល់ដឹង, សូមសាកល្បង៖

1. គណនា $\begin{bmatrix} 2 \\ -1 \\ 4 \end{bmatrix} \cdot \begin{bmatrix} 3 \\ 0 \\ 1 \end{bmatrix}$
2. ប្រសិនបើ $\mathbf{A} \in \mathbb{R}^{3 \times 4}$ និង $\mathbf{B} \in \mathbb{R}^{4 \times 2}$, តើ $\mathbf{AB}$ មានទំហំប៉ុន្មាន?
3. សរសេរកូដ NumPy ដើម្បីបង្កើតម៉ាទ្រីសឯកតា (identity matrix) ទំហំ $5 \times 5$។

> **ចម្លើយ៖** (1) $10$ &nbsp;•&nbsp; (2) $3 \times 2$ &nbsp;•&nbsp; (3) `np.eye(5)`

---

**មេរៀនបន្ទាប់ (ជំពូក 2):** កាល់គុលម៉ាទ្រីស (matrix calculus) — និស្សន្ទ និងក្រាដ្យង់ (derivatives and gradients) សម្រាប់ training គំរូ ML។
