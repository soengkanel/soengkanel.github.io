---
layout: post
title: "[ML Khmer] ជំពូក 2: កាល់គុលម៉ាទ្រីស"
date: 2026-06-15 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, math, calculus]
---

មេរៀននេះស្វែងយល់អំពី **កាល់គុលម៉ាទ្រីស** (matrix calculus) — និស្សន្ទ និងក្រាដ្យង់សម្រាប់​អនុគមន៍​ដែលទទួលយក​វ៉ិចទ័រ និងម៉ាទ្រីសជាធាតុចូល។ នេះជា​ស្នូលនៃ​ការ training គំរូ ML។

---

# សង្ខេប

- **និស្សន្ទ** (derivative) ប្រាប់យើងពីរបៀបដែលអនុគមន៍មួយផ្លាស់ប្តូរនៅពេលធាតុចូល​ផ្លាស់​ប្តូរ​បន្តិច
- **ក្រាដ្យង់** (gradient) គឺជា​វ៉ិចទ័រ​នៃ​និស្សន្ទ​ផ្នែក​នីមួយៗ — ចង្អុលទៅទិសដែលអនុគមន៍កើនលឿនបំផុត
- ក្នុង ML, យើងបង្រួម​មិនត្រឹមត្រូវ (loss) ដោយ​ការ​ដើរ​បញ្ច្រាស​ទិស​ក្រាដ្យង់ — នេះគឺ **gradient descent**
- ច្បាប់សំខាន់៖ $\nabla_{\mathbf{x}} (\mathbf{a}^\top \mathbf{x}) = \mathbf{a}$, $\nabla_{\mathbf{x}} (\mathbf{x}^\top \mathbf{x}) = 2\mathbf{x}$

---

# ហេតុអ្វីសំខាន់?

គ្រប់គំរូ ML មានប៉ារ៉ាម៉ែត្រ (parameters) ដែលត្រូវ​រៀន — តម្លៃដែលធ្វើឱ្យគំរូព្យាករ​ត្រឹមត្រូវ​ជាង​មុន។ ដើម្បីរកប៉ារ៉ាម៉ែត្រ​ល្អបំផុត, យើងត្រូវ​ដោះស្រាយ​បញ្ហា​បង្កើនប្រសិទ្ធភាព៖

$$
\min_{\boldsymbol{\theta}} \; \mathcal{L}(\boldsymbol{\theta})
$$

ដែល $\mathcal{L}$ គឺ​អនុគមន៍​ខាតបង់ (loss function) និង $\boldsymbol{\theta}$ គឺ​វ៉ិចទ័រ​ប៉ារ៉ាម៉ែត្រ។

**ដើម្បីបង្រួម $\mathcal{L}$, យើងត្រូវដឹង​ទិសដែលត្រូវ​ផ្លាស់​ប្ដូរ $\boldsymbol{\theta}$។** ក្រាដ្យង់​ឱ្យចម្លើយនេះ។

---

# ពាក្យបច្ចេកទេសថ្មី

| ខ្មែរ | English | កំណត់សម្គាល់ |
|---|---|---|
| និស្សន្ទ | derivative | អត្រាផ្លាស់ប្តូរនៃអនុគមន៍ |
| និស្សន្ទផ្នែក | partial derivative | និស្សន្ទ​ធៀបនឹងអថេរមួយ​ (រក្សា​អថេរ​ដទៃ​ថេរ) |
| ក្រាដ្យង់ | gradient | វ៉ិចទ័រនៃ​និស្សន្ទ​ផ្នែក​ទាំងអស់ |
| យ៉ាក់ប៊ីយ៉ាន់ | Jacobian | ម៉ាទ្រីសនៃ​និស្សន្ទ​ផ្នែក​សម្រាប់​អនុគមន៍​វ៉ិចទ័រ |
| ហេស្យ៉ាន់ | Hessian | ម៉ាទ្រីសនៃ​និស្សន្ទ​លំដាប់​ទីពីរ |
| តង់សង់ | tangent | បន្ទាត់​ប៉ះ​ខ្សែ​ក្រាបនៅ​ចំណុចមួយ |

---

# គំនិតវិចារណញ្ញាណ

ស្រមៃថា​អ្នកឈរ​លើភ្នំ​អ័ព្ទ ហើយ​ចង់​ចុះ​ទៅ​ជ្រលង។ អ្នកមិនឃើញ​ផ្លូវទេ, ប៉ុន្តែ​អ្នកអាច​មាន​អារម្មណ៍​ពីជម្រាល​នៅ​ក្រោម​ជើង។

**ក្រាដ្យង់ = ទិសដែលជម្រាល​ឡើង​ខ្លាំង​បំផុត។**

ដើម្បីចុះទៅជ្រលង (បង្រួម loss), អ្នកដើរ​បញ្ច្រាស​ទិស​ក្រាដ្យង់៖

$$
\boldsymbol{\theta}_{\text{new}} = \boldsymbol{\theta}_{\text{old}} - \eta \cdot \nabla \mathcal{L}(\boldsymbol{\theta}_{\text{old}})
$$

ដែល $\eta$ (eta) គឺ **learning rate** — ទំហំជំហានដើរ។

---

# និយមន័យ និងគណិតវិទ្យា

## ១. និស្សន្ទ (Scalar → Scalar)

សម្រាប់ $f: \mathbb{R} \to \mathbb{R}$៖

$$
f'(x) = \frac{df}{dx} = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}
$$

ឧទាហរណ៍៖ បើ $f(x) = 3x^2$, នោះ $f'(x) = 6x$។

## ២. និស្សន្ទផ្នែក (Multivariate → Scalar)

សម្រាប់ $f(x_1, x_2, \ldots, x_n)$, និស្សន្ទ​ផ្នែក​ធៀបនឹង $x_i$៖

$$
\frac{\partial f}{\partial x_i}
$$

មានន័យថា៖ ផ្លាស់ប្តូរ $x_i$ បន្តិច, រក្សា​អថេរ​ដទៃ​ថេរ, រួចមើល​ថា $f$ ផ្លាស់ប្តូរ​ប៉ុនណា។

ឧទាហរណ៍៖ $f(x, y) = x^2 y + 3y$

$$
\frac{\partial f}{\partial x} = 2xy, \quad \frac{\partial f}{\partial y} = x^2 + 3
$$

## ៣. ក្រាដ្យង់ (Gradient Vector)

ក្រាដ្យង់​នៃ $f: \mathbb{R}^n \to \mathbb{R}$ គឺ​វ៉ិចទ័រ​នៃ​និស្សន្ទ​ផ្នែក​ទាំងអស់៖

$$
\nabla f(\mathbf{x}) = \begin{bmatrix} \dfrac{\partial f}{\partial x_1} \\ \dfrac{\partial f}{\partial x_2} \\ \vdots \\ \dfrac{\partial f}{\partial x_n} \end{bmatrix}
$$

## ៤. យ៉ាក់ប៊ីយ៉ាន់ (Jacobian Matrix)

សម្រាប់​អនុគមន៍​វ៉ិចទ័រ $\mathbf{f}: \mathbb{R}^n \to \mathbb{R}^m$, យ៉ាក់ប៊ីយ៉ាន់​គឺ​ម៉ាទ្រីស​ $m \times n$៖

$$
\mathbf{J} = \begin{bmatrix} \dfrac{\partial f_1}{\partial x_1} & \cdots & \dfrac{\partial f_1}{\partial x_n} \\ \vdots & \ddots & \vdots \\ \dfrac{\partial f_m}{\partial x_1} & \cdots & \dfrac{\partial f_m}{\partial x_n} \end{bmatrix}
$$

## ច្បាប់សំខាន់ៗ (Identities)

នៅពេលគណនាក្រាដ្យង់ក្នុង ML, ច្បាប់ទាំងនេះ​ត្រូវ​ប្រើ​ញឹក​ញាប់៖

| អនុគមន៍ | ក្រាដ្យង់ធៀបនឹង $\mathbf{x}$ |
|---|---|
| $\mathbf{a}^\top \mathbf{x}$ | $\mathbf{a}$ |
| $\mathbf{x}^\top \mathbf{x}$ | $2\mathbf{x}$ |
| $\mathbf{x}^\top \mathbf{A} \mathbf{x}$ | $(\mathbf{A} + \mathbf{A}^\top)\mathbf{x}$ |
| $\\|\mathbf{x}\\|_2^2$ | $2\mathbf{x}$ |
| $\\|\mathbf{A}\mathbf{x} - \mathbf{b}\\|_2^2$ | $2\mathbf{A}^\top(\mathbf{A}\mathbf{x} - \mathbf{b})$ |

ច្បាប់​ចុង​ក្រោយ​សំខាន់​បំផុត — នេះគឺ​ក្រាដ្យង់​នៃ **linear regression loss**។

---

# ឧទាហរណ៍

គណនាក្រាដ្យង់​នៃ $f(\mathbf{x}) = \mathbf{x}^\top \mathbf{x}$ ដែល $\mathbf{x} = (x_1, x_2)^\top$។

យើងរក​មុនដោយផ្ទាល់៖

$$
f(\mathbf{x}) = x_1^2 + x_2^2
$$

និស្សន្ទ​ផ្នែក៖

$$
\frac{\partial f}{\partial x_1} = 2x_1, \quad \frac{\partial f}{\partial x_2} = 2x_2
$$

ដូច្នេះ៖

$$
\nabla f(\mathbf{x}) = \begin{bmatrix} 2x_1 \\ 2x_2 \end{bmatrix} = 2\mathbf{x}
$$

ត្រូវ​នឹង​ច្បាប់​ក្នុង​តារាង​ខាងលើ។ ✓

---

# កូដ Python

## និស្សន្ទ​លេខ (Numerical gradient) ជាមួយ NumPy

```python
import numpy as np

def f(x):
    """f(x) = x^T x"""
    return x @ x

def numerical_grad(f, x, h=1e-5):
    """ប៉ាន់ប្រមាណ​ក្រាដ្យង់​ដោយ​ផ្លាស់ប្តូរ​អថេរ​នីមួយៗ​បន្តិច"""
    grad = np.zeros_like(x, dtype=float)
    for i in range(len(x)):
        x_plus = x.copy().astype(float)
        x_minus = x.copy().astype(float)
        x_plus[i] += h
        x_minus[i] -= h
        grad[i] = (f(x_plus) - f(x_minus)) / (2 * h)
    return grad

x = np.array([3.0, 4.0])
print(numerical_grad(f, x))  # [6. 8.]  ≈ 2x ✓
```

## ក្រាដ្យង់​ស្វ័យប្រវត្តិ (Autograd) ជាមួយ PyTorch

```python
import torch

x = torch.tensor([3.0, 4.0], requires_grad=True)
f = x @ x
f.backward()
print(x.grad)  # tensor([6., 8.])
```

PyTorch គណនា​ក្រាដ្យង់​ដោយ​ស្វ័យប្រវត្តិ — នេះ​ជាមូលដ្ឋាន​នៃ​ការ training neural networks។

---

# ការអនុវត្តន៍ជាក់ស្តែង

**ការ training neural network** ប្រើ​ក្រាដ្យង់​លើ​ប៉ារ៉ាម៉ែត្ររាប់​លាន (ហើយ​ខ្លះ​រាប់​ប៊ីលាន)។

ឧទាហរណ៍ ChatGPT (GPT-3.5) មាន​ប្រហែល 175 ប៊ីលាន​ប៉ារ៉ាម៉ែត្រ។ ការ training គឺ​ការ​អនុវត្ត​លំដាប់​នេះ​ដដែលៗ​រាប់​លានដង៖

1. ផ្ទុក​ឧទាហរណ៍​មួយ​ចំនួន (batch) ពី​ទិន្នន័យ
2. ដំណើរការ​ឆ្ពោះ​ទៅ​មុខ (forward pass) — គណនា​ការ​ព្យាករ
3. គណនា loss
4. **គណនា​ក្រាដ្យង់** (backpropagation) — backward pass
5. ធ្វើ​បច្ចុប្បន្នភាព​ប៉ារ៉ាម៉ែត្រ៖ $\boldsymbol{\theta} \leftarrow \boldsymbol{\theta} - \eta \nabla \mathcal{L}$

ដោយគ្មាន​កាល់គុលម៉ាទ្រីស, deep learning ទំនើបនឹង​មិន​អាច​មាន​បាន។

---

# លំហាត់

1. គណនា​ក្រាដ្យង់​នៃ $f(\mathbf{x}) = \mathbf{a}^\top \mathbf{x}$ ដែល $\mathbf{a} = (2, -1, 3)^\top$ និង $\mathbf{x} \in \mathbb{R}^3$។
2. បើ $g(x, y) = x^2 + 3xy + y^2$, គណនា $\nabla g$ នៅចំណុច $(1, 2)$។
3. សរសេរ​កូដ NumPy ដើម្បី​ប៉ាន់ប្រមាណ​ក្រាដ្យង់​នៃ $f(\mathbf{x}) = \\|\mathbf{x}\\|_2^2 + 5$ នៅ $\mathbf{x} = (1, 2, 3)$ និង​ផ្ទៀង​ផ្ទាត់​ជាមួយ​ច្បាប់​ក្នុង​តារាង។

> **ចម្លើយ៖**
> (1) $\nabla f = \mathbf{a} = (2, -1, 3)^\top$
> (2) $\nabla g = (2x + 3y, 3x + 2y)^\top \Rightarrow \nabla g(1, 2) = (8, 7)^\top$
> (3) ក្រាដ្យង់​ជា​ការ​ប៉ាន់​ប្រមាណ ≈ $(2, 4, 6)$, ត្រូវ​នឹង $2\mathbf{x}$ ✓

---

**មេរៀនបន្ទាប់ (ជំពូក 3):** ប្រូបាប៊ីលីតេ​មូលដ្ឋាន (probability) — ការចែកចាយ (distributions), ការរំពឹង (expectation), variance, និង Bayes' theorem សម្រាប់ ML។
