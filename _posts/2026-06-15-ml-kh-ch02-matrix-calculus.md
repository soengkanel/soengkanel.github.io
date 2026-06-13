---
layout: post
title: "[ML Khmer] ជំពូក 2: កាល់គុលម៉ាទ្រីស"
date: 2026-06-15 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, math, calculus, interactive]
---

មេរៀននេះស្វែងយល់​អំពី **កាល់គុលម៉ាទ្រីស** (matrix calculus) — និស្សន្ទ និងក្រាដ្យង់សម្រាប់​អនុគមន៍​ដែលទទួលយក​វ៉ិចទ័រ និងម៉ាទ្រីសជាធាតុចូល។ នេះជា​ស្នូល​នៃ​ការ training គំរូ ML។ មេរៀននេះមាន **រូបភាព interactive ៣** ដើម្បីឱ្យអ្នកចូលរួមលេងផ្ទាល់នឹង​គំនិត។

---

# សង្ខេប

- **និស្សន្ទ** (derivative) ប្រាប់​យើង​ថា​អនុគមន៍​ផ្លាស់​ប្ដូរ​យ៉ាង​ណា​នៅ​ពេល​ធាតុ​ចូល​ផ្លាស់​ប្ដូរ​បន្តិច
- **ក្រាដ្យង់** (gradient) គឺ​វ៉ិចទ័រ​នៃ​និស្សន្ទ​ផ្នែក​នីមួយៗ — ចង្អុល​ទៅ​ទិស​ដែល​អនុគមន៍​កើន​លឿន​បំផុត
- ក្នុង ML, យើង​បង្រួម loss ដោយ​ការ​ដើរ​បញ្ច្រាស​ទិស​ក្រាដ្យង់ — នេះ​គឺ **gradient descent**
- ច្បាប់​សំខាន់៖ $\nabla_{\mathbf{x}} (\mathbf{a}^\top \mathbf{x}) = \mathbf{a}$, $\nabla_{\mathbf{x}} (\mathbf{x}^\top \mathbf{x}) = 2\mathbf{x}$

---

# ហេតុអ្វីសំខាន់?

គ្រប់​គំរូ ML មាន​ប៉ារ៉ាម៉ែត្រ (parameters) ដែល​ត្រូវ​រៀន — តម្លៃ​ដែល​ធ្វើ​ឱ្យ​គំរូ​ព្យាករ​ត្រឹមត្រូវ​ជាង​មុន។ ដើម្បី​រក​ប៉ារ៉ាម៉ែត្រ​ល្អ​បំផុត, យើង​ត្រូវ​ដោះ​ស្រាយ​បញ្ហា​បង្កើន​ប្រសិទ្ធភាព៖

$$
\min_{\boldsymbol{\theta}} \; \mathcal{L}(\boldsymbol{\theta})
$$

ដែល $\mathcal{L}$ គឺ loss function និង $\boldsymbol{\theta}$ ជា​វ៉ិចទ័រ​ប៉ារ៉ាម៉ែត្រ។

**ដើម្បី​បង្រួម $\mathcal{L}$, យើង​ត្រូវ​ដឹង​ទិស​ដែល​ត្រូវ​ផ្លាស់​ប្ដូរ $\boldsymbol{\theta}$។** ក្រាដ្យង់​ឱ្យ​ចម្លើយ​នេះ។

**ឧទាហរណ៍កម្ពុជា៖** ការ​បង្កើត​គំរូ​ព្យាករ​តម្លៃ​អាផាតមិន BKK1 (ដែល​យើង​បាន​ដោះ​ស្រាយ​ដោយ​ការ​ច្រាស​ម៉ាទ្រីស​ក្នុង​ជំពូក 1b) ក៏​អាច​ដោះ​ស្រាយ​ដោយ gradient descent ផងដែរ — ដោយ​ប្រើ​ក្រាដ្យង់​នៃ MSE loss។

---

# ពាក្យបច្ចេកទេសថ្មី

| ខ្មែរ | English | កំណត់សម្គាល់ |
|---|---|---|
| និស្សន្ទ | derivative | អត្រា​ផ្លាស់​ប្ដូរ​នៃ​អនុគមន៍ |
| និស្សន្ទផ្នែក | partial derivative | និស្សន្ទ​ធៀប​អថេរ​មួយ (រក្សា​អថេរ​ដទៃ​ថេរ) |
| ក្រាដ្យង់ | gradient | វ៉ិចទ័រ​នៃ​និស្សន្ទ​ផ្នែក​ទាំង​អស់ |
| យ៉ាក់ប៊ីយ៉ាន់ | Jacobian | ម៉ាទ្រីស​នៃ​និស្សន្ទ​ផ្នែក​សម្រាប់​អនុគមន៍​វ៉ិចទ័រ |
| ហេស្យ៉ាន់ | Hessian | ម៉ាទ្រីស​នៃ​និស្សន្ទ​លំដាប់​ទីពីរ |
| តង់សង់ | tangent line | បន្ទាត់​ប៉ះ​ខ្សែ​ក្រាប​នៅ​ចំណុច​មួយ |
| Learning rate | learning rate | $\eta$ — ទំហំ​ជំហាន​ដើរ​ក្នុង gradient descent |
| Loss | loss / cost | កំហុស​នៃ​គំរូ (តូច = ល្អ) |

---

# គំនិតវិចារណញ្ញាណ

ស្រមៃ​ថា​អ្នក​ឈរ​លើ​ភ្នំ​អ័ព្ទ ហើយ​ចង់​ចុះ​ទៅ​ជ្រលង។ អ្នក​មិន​ឃើញ​ផ្លូវ​ទេ, ប៉ុន្តែ​អ្នក​អាច​មាន​អារម្មណ៍​ពី​ជម្រាល​នៅ​ក្រោម​ជើង។

**ក្រាដ្យង់ = ទិស​ដែល​ជម្រាល​ឡើង​ខ្លាំង​បំផុត។**

ដើម្បី​ចុះ​ទៅ​ជ្រលង (បង្រួម loss), អ្នក​ដើរ​បញ្ច្រាស​ទិស​ក្រាដ្យង់៖

$$
\boldsymbol{\theta}_{\text{new}} = \boldsymbol{\theta}_{\text{old}} - \eta \cdot \nabla \mathcal{L}(\boldsymbol{\theta}_{\text{old}})
$$

ដែល $\eta$ (eta) ជា **learning rate** — ទំហំ​ជំហាន​ដើរ។

## 🎮 រូបភាព interactive ១៖ និស្សន្ទ​ជា​ជម្រាល​នៃ​បន្ទាត់​ប៉ះ

សូម​ផ្លាស់ slider ខាង​ក្រោម​ដើម្បី​មើល​ថា​ជម្រាល​នៃ​បន្ទាត់​ប៉ះ (តង់សង់) ប្រែ​ប្រួល​យ៉ាង​ណា​នៅ​ពេល​អ្នក​ផ្លាស់​ចំណុច​ខ្លួន​ឯង។ ក្រាប​សម្រាប់ $f(x) = x^2 - 4$ និង $f'(x) = 2x$។

<div id="viz1" style="width:100%;max-width:760px;margin:0 auto;height:420px"></div>
<div style="max-width:760px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  <label>x = <span id="viz1-x" style="font-weight:bold">1.00</span> • slope f'(x) = <span id="viz1-slope" style="font-weight:bold;color:#dc2626">2.00</span></label><br>
  <input id="viz1-slider" type="range" min="-2.5" max="2.5" step="0.05" value="1" style="width:80%;max-width:600px">
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    var xs = [];
    for (var i = -3; i <= 3.0001; i += 0.05) xs.push(i);
    var f = function (x) { return x * x - 4; };
    var fp = function (x) { return 2 * x; };
    var ys = xs.map(f);
    function getData(x0) {
      var m = fp(x0), b = f(x0) - m * x0;
      return [
        { x: xs, y: ys, mode: 'lines', name: 'f(x) = x² − 4', line: { color: '#1e40af', width: 3 } },
        { x: [-3, 3], y: [m * -3 + b, m * 3 + b], mode: 'lines', name: 'tangent line', line: { color: '#dc2626', width: 2, dash: 'dot' } },
        { x: [x0], y: [f(x0)], mode: 'markers', marker: { color: '#dc2626', size: 14 }, showlegend: false }
      ];
    }
    var layout = {
      xaxis: { title: 'x', range: [-3, 3], zeroline: true, gridcolor: '#e5e7eb' },
      yaxis: { title: 'f(x)', range: [-6, 8], zeroline: true, gridcolor: '#e5e7eb' },
      margin: { t: 20, b: 50, l: 50, r: 20 },
      showlegend: true,
      legend: { x: 0.02, y: 0.98 },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    Plotly.newPlot('viz1', getData(1.0), layout, { responsive: true, displayModeBar: false });
    var s = document.getElementById('viz1-slider');
    s.addEventListener('input', function () {
      var x0 = parseFloat(s.value);
      document.getElementById('viz1-x').textContent = x0.toFixed(2);
      document.getElementById('viz1-slope').textContent = fp(x0).toFixed(2);
      Plotly.react('viz1', getData(x0), layout);
    });
  }
  init();
})();
</script>

> **សង្កេត៖**
> - នៅ $x = 0$: ជម្រាល = 0 (តង់សង់​ផ្ដេក) → ចំណុច​អប្បបរមា
> - នៅ $x > 0$: ជម្រាល > 0 (តង់សង់​ឡើង​ខាង​ស្ដាំ) → ត្រូវ​ដើរ​ខាង​ឆ្វេង​ដើម្បី​ចុះ
> - នៅ $x < 0$: ជម្រាល < 0 → ត្រូវ​ដើរ​ខាង​ស្ដាំ

នេះ​ហើយ​ជា​ហេតុ​ដែល gradient descent ប្រើ **−η · gradient**៖ បញ្ច្រាស​ទិស​ឡើង → ដើរ​ចុះ។

---

# និយមន័យ និងគណិតវិទ្យា

## ១. និស្សន្ទ (Scalar → Scalar)

សម្រាប់ $f: \mathbb{R} \to \mathbb{R}$៖

$$
f'(x) = \frac{df}{dx} = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}
$$

ឧទាហរណ៍៖ បើ $f(x) = 3x^2$, នោះ $f'(x) = 6x$។

## ២. និស្សន្ទផ្នែក (Multivariate → Scalar)

សម្រាប់ $f(x_1, x_2, \ldots, x_n)$, និស្សន្ទ​ផ្នែក​ធៀប $x_i$៖

$$
\frac{\partial f}{\partial x_i}
$$

មាន​ន័យ​ថា៖ ផ្លាស់ $x_i$ បន្តិច, រក្សា​អថេរ​ដទៃ​ថេរ, រួច​មើល​ថា $f$ ផ្លាស់​ប៉ុនណា។

ឧទាហរណ៍៖ $f(x, y) = x^2 y + 3y$

$$
\frac{\partial f}{\partial x} = 2xy, \quad \frac{\partial f}{\partial y} = x^2 + 3
$$

## ៣. ក្រាដ្យង់ (Gradient Vector)

ក្រាដ្យង់​នៃ $f: \mathbb{R}^n \to \mathbb{R}$ គឺ​វ៉ិចទ័រ​នៃ​និស្សន្ទ​ផ្នែក​ទាំង​អស់៖

$$
\nabla f(\mathbf{x}) = \begin{bmatrix} \dfrac{\partial f}{\partial x_1} \\ \dfrac{\partial f}{\partial x_2} \\ \vdots \\ \dfrac{\partial f}{\partial x_n} \end{bmatrix}
$$

## 🎮 រូបភាព interactive ២៖ ផ្ទៃ​នៃ​អនុគមន៍ និង​ទិស​ក្រាដ្យង់

ក្រាប​ខាង​ឆ្វេង​បង្ហាញ​ផ្ទៃ 3D នៃ $f(x, y) = x^2 + y^2$ (រង្វង់​ស្រដៀង​ចាន)។ អ្នក​អាច​**អូស​ដើម្បី​បង្វិល​ផ្ទៃ** និង **rotate ផ្តូរ​មុំ​មើល**។ ក្រាប​ខាង​ស្ដាំ​បង្ហាញ​ contour view ដែល​ព្រួញ​ក្រហម​ចង្អុល​ទៅ​ទិស​ក្រាដ្យង់ (កើន​ខ្ពស់​បំផុត) នៅ​ចំណុច​ផ្សេងៗ។

<div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center">
  <div id="viz2-3d" style="width:48%;min-width:300px;height:400px"></div>
  <div id="viz2-contour" style="width:48%;min-width:300px;height:400px"></div>
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    var N = 30;
    var xs = [], ys = [], zs = [];
    for (var i = 0; i < N; i++) {
      var t = -2 + 4 * i / (N - 1);
      xs.push(t); ys.push(t);
    }
    for (var i = 0; i < N; i++) {
      var row = [];
      for (var j = 0; j < N; j++) row.push(xs[j] * xs[j] + ys[i] * ys[i]);
      zs.push(row);
    }
    Plotly.newPlot('viz2-3d', [{
      type: 'surface', x: xs, y: ys, z: zs,
      colorscale: 'Blues', showscale: false
    }], {
      scene: {
        xaxis: { title: 'x' }, yaxis: { title: 'y' }, zaxis: { title: 'f(x,y)' },
        camera: { eye: { x: 1.6, y: 1.6, z: 0.9 } }
      },
      margin: { t: 10, b: 0, l: 0, r: 0 },
      paper_bgcolor: 'rgba(0,0,0,0)'
    }, { responsive: true, displayModeBar: false });
    var traces = [{
      type: 'contour', x: xs, y: ys, z: zs,
      colorscale: 'Blues', contours: { coloring: 'heatmap' }, showscale: false, opacity: 0.85
    }];
    var pts = [-1.5, -0.5, 0.5, 1.5];
    for (var i = 0; i < pts.length; i++) {
      for (var j = 0; j < pts.length; j++) {
        var xp = pts[i], yp = pts[j];
        var gx = 2 * xp, gy = 2 * yp;
        var norm = Math.sqrt(gx * gx + gy * gy);
        if (norm < 1e-6) continue;
        var dx = gx * 0.3 / norm, dy = gy * 0.3 / norm;
        traces.push({
          x: [xp, xp + dx], y: [yp, yp + dy],
          mode: 'lines+markers',
          line: { color: '#dc2626', width: 3 },
          marker: { size: [0, 8], symbol: 'arrow', angleref: 'previous', color: '#dc2626' },
          showlegend: false, hoverinfo: 'skip'
        });
      }
    }
    Plotly.newPlot('viz2-contour', traces, {
      xaxis: { title: 'x', range: [-2, 2] },
      yaxis: { title: 'y', range: [-2, 2], scaleanchor: 'x' },
      margin: { t: 10, b: 50, l: 50, r: 20 },
      showlegend: false,
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    }, { responsive: true, displayModeBar: false });
  }
  init();
})();
</script>

> **សង្កេត៖** ក្រាដ្យង់​នៅ​គ្រប់​ចំណុច​ចង្អុល​ចេញ​ពី​អប្បបរមា (origin)។ ការ​ដើរ​បញ្ច្រាស​ទិស (−gradient) នាំ​យើង​ត្រលប់​ទៅ​អប្បបរមា — នេះ​គឺ gradient descent។

## ៤. យ៉ាក់ប៊ីយ៉ាន់ (Jacobian Matrix)

សម្រាប់​អនុគមន៍​វ៉ិចទ័រ $\mathbf{f}: \mathbb{R}^n \to \mathbb{R}^m$, យ៉ាក់ប៊ីយ៉ាន់​គឺ​ម៉ាទ្រីស $m \times n$៖

$$
\mathbf{J} = \begin{bmatrix} \dfrac{\partial f_1}{\partial x_1} & \cdots & \dfrac{\partial f_1}{\partial x_n} \\ \vdots & \ddots & \vdots \\ \dfrac{\partial f_m}{\partial x_1} & \cdots & \dfrac{\partial f_m}{\partial x_n} \end{bmatrix}
$$

## ច្បាប់សំខាន់ៗ (Identities)

នៅ​ពេល​គណនា​ក្រាដ្យង់​ក្នុង ML, ច្បាប់​ទាំង​នេះ​ត្រូវ​ប្រើ​ញឹក​ញាប់៖

| អនុគមន៍ | ក្រាដ្យង់ធៀប $\mathbf{x}$ |
|---|---|
| $\mathbf{a}^\top \mathbf{x}$ | $\mathbf{a}$ |
| $\mathbf{x}^\top \mathbf{x}$ | $2\mathbf{x}$ |
| $\mathbf{x}^\top \mathbf{A} \mathbf{x}$ | $(\mathbf{A} + \mathbf{A}^\top)\mathbf{x}$ |
| $\\|\mathbf{x}\\|_2^2$ | $2\mathbf{x}$ |
| $\\|\mathbf{A}\mathbf{x} - \mathbf{b}\\|_2^2$ | $2\mathbf{A}^\top(\mathbf{A}\mathbf{x} - \mathbf{b})$ |

ច្បាប់​ចុង​ក្រោយ​សំខាន់​បំផុត — នេះ​គឺ​ក្រាដ្យង់​នៃ **linear regression loss**។

---

# ឧទាហរណ៍

គណនា​ក្រាដ្យង់​នៃ $f(\mathbf{x}) = \mathbf{x}^\top \mathbf{x}$ ដែល $\mathbf{x} = (x_1, x_2)^\top$។

យើង​បំបែក​មុន​ដោយ​ផ្ទាល់៖

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

ត្រូវ​នឹង​ច្បាប់​ក្នុង​តារាង​ខាង​លើ។ ✓

---

# កូដ Python

## និស្សន្ទ​លេខ (Numerical gradient) ជាមួយ NumPy

```python
import numpy as np

def f(x):
    """f(x) = x^T x"""
    return x @ x

def numerical_grad(f, x, h=1e-5):
    """ប៉ាន់ប្រមាណក្រាដ្យង់ដោយផ្លាស់អថេរនីមួយៗបន្តិច"""
    grad = np.zeros_like(x, dtype=float)
    for i in range(len(x)):
        x_plus = x.copy().astype(float)
        x_minus = x.copy().astype(float)
        x_plus[i] += h
        x_minus[i] -= h
        grad[i] = (f(x_plus) - f(x_minus)) / (2 * h)
    return grad

x = np.array([3.0, 4.0])
print(numerical_grad(f, x))   # [6. 8.]  ≈ 2x ✓
```

## ក្រាដ្យង់​ស្វ័យប្រវត្តិ (Autograd) ជាមួយ PyTorch

```python
import torch

x = torch.tensor([3.0, 4.0], requires_grad=True)
f = x @ x
f.backward()
print(x.grad)   # tensor([6., 8.])
```

PyTorch គណនា​ក្រាដ្យង់​ស្វ័យ​ប្រវត្តិ — នេះ​ជា​មូលដ្ឋាន​នៃ​ការ training neural networks។

---

# ការអនុវត្តន៍ជាក់ស្ដែង

## 🎮 រូបភាព interactive ៣៖ Gradient descent លើ BKK1 MSE loss

ចូរ​យើង​ត្រឡប់​មកការ​ព្យាករ​តម្លៃ​អាផាតមិន BKK1 ពី​ជំពូក 1b៖

| អាផាតមិន | sqm | តម្លៃ (ពាន់ USD) |
|---|---:|---:|
| Unit A | 40 | 160 |
| Unit B | 80 | 280 |

គំរូ៖ $\hat{y} = w_0 + w_1 \cdot \text{sqm}$, MSE loss៖

$$
\mathcal{L}(w_0, w_1) = \frac{1}{2}\big[(w_0 + 40 w_1 - 160)^2 + (w_0 + 80 w_1 - 280)^2\big]
$$

ក្រាដ្យង់៖

$$
\nabla \mathcal{L} = \begin{bmatrix} (w_0 + 40 w_1 - 160) + (w_0 + 80 w_1 - 280) \\ 40(w_0 + 40 w_1 - 160) + 80(w_0 + 80 w_1 - 280) \end{bmatrix}
$$

ក្នុង​ជំពូក 1b យើង​បាន​រក​ឃើញ​ដំណោះ​ស្រាយ​ដោយ​ផ្ទាល់​ដោយ​ការ​ច្រាស​ម៉ាទ្រីស៖ $w_0^* = 40$, $w_1^* = 3$។ **ឥឡូវ​នេះ​យើង​នឹង​រក​ដំណោះ​ស្រាយ​ដូច​គ្នា​ដោយ gradient descent។**

ផ្លាស់ slider learning rate ($\eta$) ខាង​ក្រោម​ហើយ​មើល​ផ្លូវ​ដែល GD ដើរ​ទៅ​រក​ដំណោះ​ស្រាយ​ (⭐ ពណ៌​បៃ​តង)។

<div id="viz3" style="width:100%;max-width:760px;margin:0 auto;height:450px"></div>
<div style="max-width:760px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  <label>Learning rate η = <span id="viz3-lr" style="font-weight:bold;color:#1e40af">2.00e-4</span></label><br>
  <input id="viz3-slider" type="range" min="0" max="100" step="1" value="50" style="width:80%;max-width:600px"><br>
  <span id="viz3-info" style="font-size:0.9em;color:#6b7280">iterations: -, final loss: -</span>
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    var X = [[1, 40], [1, 80]];
    var y = [160, 280];
    function mse(w0, w1) {
      var t = 0;
      for (var i = 0; i < X.length; i++) {
        var p = w0 * X[i][0] + w1 * X[i][1];
        t += (p - y[i]) * (p - y[i]);
      }
      return t / 2;
    }
    function grad(w0, w1) {
      var g0 = 0, g1 = 0;
      for (var i = 0; i < X.length; i++) {
        var e = w0 * X[i][0] + w1 * X[i][1] - y[i];
        g0 += e * X[i][0]; g1 += e * X[i][1];
      }
      return [g0, g1];
    }
    function gd(lr) {
      var w0 = 0, w1 = 0;
      var traj = [[w0, w1]];
      for (var it = 0; it < 300; it++) {
        var g = grad(w0, w1);
        w0 -= lr * g[0]; w1 -= lr * g[1];
        traj.push([w0, w1]);
        if (Math.abs(g[0]) + Math.abs(g[1]) < 1e-3) break;
        if (Math.abs(w0) > 500 || Math.abs(w1) > 50) break;
      }
      return traj;
    }
    var N = 40;
    var w0s = [], w1s = [];
    for (var i = 0; i < N; i++) {
      w0s.push(-20 + 120 * i / (N - 1));
      w1s.push(-2 + 10 * i / (N - 1));
    }
    var Lvals = [];
    for (var i = 0; i < N; i++) {
      var row = [];
      for (var j = 0; j < N; j++) row.push(Math.log10(mse(w0s[j], w1s[i]) + 1));
      Lvals.push(row);
    }
    function plotData(lr) {
      var traj = gd(lr);
      var last = traj[traj.length - 1];
      var fl = mse(last[0], last[1]);
      return {
        traces: [
          { type: 'contour', x: w0s, y: w1s, z: Lvals, colorscale: 'Blues',
            contours: { coloring: 'heatmap' }, showscale: false, opacity: 0.75,
            hovertemplate: 'w₀=%{x:.1f}<br>w₁=%{y:.2f}<extra></extra>' },
          { x: traj.map(function (p) { return p[0]; }),
            y: traj.map(function (p) { return p[1]; }),
            mode: 'lines+markers', name: 'GD trajectory',
            line: { color: '#dc2626', width: 2 }, marker: { size: 4, color: '#dc2626' } },
          { x: [40], y: [3], mode: 'markers', name: 'optimal (40, 3)',
            marker: { color: '#10b981', size: 18, symbol: 'star',
                      line: { color: '#065f46', width: 2 } } }
        ],
        info: 'iterations: ' + traj.length + ', final loss: ' + fl.toFixed(2)
      };
    }
    var layout = {
      xaxis: { title: 'w₀ (intercept)', range: [-20, 100] },
      yaxis: { title: 'w₁ (slope per sqm)', range: [-2, 8] },
      margin: { t: 10, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    function lrFromSlider(v) { return Math.pow(10, -6 + 3 * v / 100); }
    var initLr = lrFromSlider(50);
    var d = plotData(initLr);
    Plotly.newPlot('viz3', d.traces, layout, { responsive: true, displayModeBar: false });
    document.getElementById('viz3-info').textContent = d.info;
    document.getElementById('viz3-lr').textContent = initLr.toExponential(2);
    document.getElementById('viz3-slider').addEventListener('input', function (e) {
      var lr = lrFromSlider(parseFloat(e.target.value));
      document.getElementById('viz3-lr').textContent = lr.toExponential(2);
      var d = plotData(lr);
      Plotly.react('viz3', d.traces, layout);
      document.getElementById('viz3-info').textContent = d.info;
    });
  }
  init();
})();
</script>

> **សាកល្បង​លេង​៖**
> - **η តូច​ខ្លាំង** (eg $10^{-6}$) → ដើរ​យឺត​ខ្លាំង, មិន​ឈាន​ដល់​ដំណោះ​ស្រាយ​ក្នុង 300 ជំហាន
> - **η ល្អ** (eg $10^{-4}$) → ដើរ​ត្រង់​ទៅ​រក ⭐
> - **η ធំ​ខ្លាំង** (eg $10^{-3}$) → លោត​ឆ្លង, ខាត​បង់​បំប្លែង (diverge)

**នេះ​បង្ហាញ​ថា​ហេតុ​អ្វី learning rate សំខាន់​បំផុត​ក្នុង deep learning** — រាល់​អ្នក​ស្រាវ​ជ្រាវ​ ML ត្រូវ​ចំណាយ​ពេល​ច្រើន​លើ​ការ tune learning rate។

## ការ​អនុវត្ត​នៅ​ក្នុង​ឧស្សាហកម្ម

**ការ training neural network** ប្រើ​ក្រាដ្យង់​លើ​ប៉ារ៉ាម៉ែត្រ​រាប់​លាន (ហើយ​ខ្លះ​រាប់​ប៊ីលាន)។

ឧទាហរណ៍ ChatGPT (GPT-3.5) មាន​ប្រហែល 175 ប៊ីលាន​ប៉ារ៉ាម៉ែត្រ។ ការ training គឺ​ការ​អនុវត្ត​លំដាប់​នេះ​ដដែលៗ​រាប់​លាន​ដង៖

1. ផ្ទុក​ឧទាហរណ៍​មួយ​ចំនួន (batch) ពី​ទិន្នន័យ
2. ដំណើរ​ការ​ឆ្ពោះ​ទៅ​មុខ (forward pass) — គណនា​ការ​ព្យាករ
3. គណនា loss
4. **គណនា​ក្រាដ្យង់** (backpropagation) — backward pass
5. ធ្វើ​បច្ចុប្បន្នភាព​ប៉ារ៉ាម៉ែត្រ៖ $\boldsymbol{\theta} \leftarrow \boldsymbol{\theta} - \eta \nabla \mathcal{L}$

ស្ថាប័ន​ខ្មែរ​ដែល​ប្រើ gradient descent ផ្ទាល់៖
- **ABA Mobile fraud detection** — រៀន​គំរូ​ការ​ប្រតិបត្តិការ​ "ធម្មតា" ដោយ training neural network
- **Khmer NLP (Google Translate, Khmer OCR)** — រៀន​ការ​បក​ប្រែ​ភាសា​ដោយ​ training transformers (ដែល​ប្រើ​ Adam optimizer, រឺ adaptive form នៃ GD)
- **AMK/Prasac credit scoring** — រៀន​គំរូ​ឥណទាន​ដោយ logistic regression + GD

ដោយ​គ្មាន​កាល់គុលម៉ាទ្រីស, deep learning ទំនើប​នឹង​មិន​អាច​មាន​បាន​ឡើយ។

---

# លំហាត់

1. គណនា​ក្រាដ្យង់​នៃ $f(\mathbf{x}) = \mathbf{a}^\top \mathbf{x}$ ដែល $\mathbf{a} = (2, -1, 3)^\top$ និង $\mathbf{x} \in \mathbb{R}^3$។
2. បើ $g(x, y) = x^2 + 3xy + y^2$, គណនា $\nabla g$ នៅ​ចំណុច $(1, 2)$។
3. **ប្រើ​រូបភាព interactive ៣**៖ រក​ learning rate តូច​បំផុត​ដែល​ GD ឈាន​ដល់​ដំណោះ​ស្រាយ ($w_0 = 40, w_1 = 3$) ក្នុង​រយៈ​ពេល​មិន​លើស 100 iterations។

> **ចម្លើយ៖**
> (1) $\nabla f = \mathbf{a} = (2, -1, 3)^\top$
> (2) $\nabla g = (2x + 3y, 3x + 2y)^\top \Rightarrow \nabla g(1, 2) = (8, 7)^\top$
> (3) ប្រហែល $\eta \approx 2 \times 10^{-4}$ (សាក​លេង​ផ្ទាល់!)

---

**មេរៀន​បន្ទាប់ (ជំពូក 2b):** ច្បាប់​ខ្សែ​សង្វាក់ (chain rule), ច្បាប់​ផល​គុណ (product rule), ហេស្យ៉ាន់, និង gradient checking — និង​ការ​ត្រៀម​ឱ្យ​អ្នក​យល់ backpropagation ក្នុង neural networks។
