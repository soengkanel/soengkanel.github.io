---
layout: post
title: "[ML Khmer] ជំពូក 2b: ច្បាប់​ខ្សែ​សង្វាក់, ហេស្យ៉ាន់, និង Gradient Checking"
date: 2026-06-18 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, math, calculus, backpropagation, interactive]
thumbnail: /images/ml-series/ch02b-chain-rule.svg
---

មេរៀននេះ​បន្ត​ពី​ជំពូក 2 ដោយ​ស្វែងយល់​អំពី **ច្បាប់​ខ្សែ​សង្វាក់** (chain rule), **ហេស្យ៉ាន់** (Hessian), និង **gradient checking** — ឧបករណ៍​ដែល​ធ្វើ​ឱ្យ backpropagation ក្នុង neural network ដំណើរ​ការ​បាន។ មេរៀន​នេះ​មាន **រូបភាព interactive ៣**៖ ការ​បំបែក chain rule, ហេស្យ៉ាន់​ជា curvature, និង​ការ​ប្រៀប​ធៀប​ក្រាដ្យង់​លេខ​នឹង​ក្រាដ្យង់​វិភាគ។

---

# សង្ខេប

- **Chain rule** ឱ្យ​យើង​គណនា​និស្សន្ទ​នៃ​អនុគមន៍​សមាស​ដោយ​បំបែក​ជា​ផល​គុណ៖ $(f \circ g)'(x) = f'(g(x)) \cdot g'(x)$
- នៅ​ក្នុង​វ៉ិចទ័រ, chain rule ក្លាយ​ជា​ផល​គុណ​ម៉ាទ្រីស​នៃ​យ៉ាក់ប៊ីយ៉ាន់
- **ហេស្យ៉ាន់** $\mathbf{H} = \nabla^2 f$ គឺ​ម៉ាទ្រីស​នៃ​និស្សន្ទ​លំដាប់​ទីពីរ — ប្រាប់​យើង​អំពី curvature នៃ loss surface
- **Gradient checking** ប្រៀប​ធៀប​ក្រាដ្យង់​វិភាគ​នឹង​ក្រាដ្យង់​លេខ​ដើម្បី​ផ្ទៀង​ផ្ទាត់​ការ​ implement
- ច្បាប់​ខ្សែ​សង្វាក់​គឺ​ជា​ស្នូល​នៃ **backpropagation** — algorithm ដែល​ធ្វើ​ឱ្យ deep learning ដំណើរ​ការ​បាន

---

# ហេតុអ្វីសំខាន់?

នៅ​ក្នុង neural network, ការ​ព្យាករ​ត្រូវ​ឆ្លង​កាត់​ស្រទាប់​ច្រើន (layers)៖

$$
\mathbf{x} \to \text{layer}_1 \to \text{layer}_2 \to \cdots \to \text{layer}_L \to \hat{y} \to \mathcal{L}
$$

ដើម្បី training, យើង​ត្រូវ​គណនា​ក្រាដ្យង់​នៃ​ loss ធៀប​ប៉ារ៉ាម៉ែត្រ​នៅ​ស្រទាប់​ទីមួយ — ប៉ុន្តែ loss អាស្រ័យ​លើ​ស្រទាប់​ទីមួយ​តាម​ខ្សែ​សង្វាក់​យូរ។ **Chain rule** គឺ​ឧបករណ៍​ដែល​អនុញ្ញាត​ឱ្យ​យើង​បំបែក​ការ​គណនា​នេះ​ជា​ផល​គុណ​នៃ​ក្រាដ្យង់​នីមួយៗ — នេះ​គឺ backpropagation។

**ឧទាហរណ៍កម្ពុជា៖** បើ​អ្នក training គំរូ​ដើម្បី​ស្គាល់​អក្សរ​ខ្មែរ​ដោយ​ស្កេន​ឯកសារ (Khmer OCR), គំរូ​អ្នក​មាន​ស្រទាប់​រាប់​សិប។ ដោយ​មិន​មាន chain rule, គ្មាន​ផ្លូវ​ណា​មួយ​ដែល​អាច training ប្រព័ន្ធ​នេះ​បាន​ឡើយ។

---

# ពាក្យបច្ចេកទេសថ្មី

| ខ្មែរ | English | កំណត់សម្គាល់ |
|---|---|---|
| ច្បាប់ខ្សែសង្វាក់ | chain rule | និស្សន្ទ​នៃ​អនុគមន៍​សមាស |
| អនុគមន៍សមាស | composite function | $f \circ g$ — បន្តគ្នា​ដូចជា pipeline |
| ហេស្យ៉ាន់ | Hessian | ម៉ាទ្រីស​និស្សន្ទ​លំដាប់ ២ |
| Curvature | curvature | រាង​កោង​នៃ​អនុគមន៍ (ផ្ដិត​ឬ​ផើង) |
| ចំណុចសេន | saddle point | ចំណុច​មាន​ក្រាដ្យង់ = 0 ប៉ុន្តែ​មិនមែន min/max |
| Gradient checking | gradient checking | ផ្ទៀង​ផ្ទាត់​ការ​ implement |
| Backpropagation | backpropagation | algorithm ប្រើ chain rule ដើម្បី training NN |
| Convex / non-convex | convex / non-convex | មាន​អប្បបរមា​សកល​មួយ / មាន​ច្រើន |

---

# គំនិតវិចារណញ្ញាណ

## Chain rule

ស្រមៃ pipeline ផ្គត់​ផ្គង់​ទឹក​មាន​សន្ទះ ៣៖ ផ្លាស់​ប្ដូរ​សន្ទះ​ដំបូង​បន្តិច → លំហូរ​ក្នុង​បំពង់​ទី ២ ផ្លាស់​ប្ដូរ → លំហូរ​ក្នុង​បំពង់​ចុង​ផ្លាស់​ប្ដូរ។ **ការ​ប៉ះពាល់​សរុប = ផល​គុណ​នៃ​ឥទ្ធិពល​នៅ​សន្ទះ​នីមួយៗ។**

$$
\frac{dy}{dx} = \underbrace{\frac{dy}{du}}_{\text{outer}} \cdot \underbrace{\frac{du}{dx}}_{\text{inner}}
$$

## ហេស្យ៉ាន់

បើ​ក្រាដ្យង់​ប្រាប់​ថា​ផ្ទៃ **ឡើង​ខ្ពស់​ភាគ​ណា**, ហេស្យ៉ាន់​ប្រាប់​ថា​ផ្ទៃ​នោះ **កោង​យ៉ាង​ម៉េច**៖
- **ហេស្យ៉ាន់​វិជ្ជមាន​សុទ្ធ** → ចានផ្ដិត → អប្បបរមា
- **ហេស្យ៉ាន់​អវិជ្ជមាន​សុទ្ធ** → ផើង​ដួល​ក្បាល​ចុះ → អតិបរមា
- **មាន​ទាំង + និង −** → ចំណុច​សេន (saddle)

---

# និយមន័យ និងគណិតវិទ្យា

## ១. Chain rule (Scalar)

សម្រាប់ $y = f(g(x))$, ដោយ​កំណត់ $u = g(x)$៖

$$
\frac{dy}{dx} = \frac{dy}{du} \cdot \frac{du}{dx} = f'(u) \cdot g'(x)
$$

## 🎮 រូបភាព interactive ១៖ ការ​បំបែក chain rule

ពិចារណា $y = \sin(x^2)$ ដែល $g(x) = x^2$ និង $f(u) = \sin(u)$។ ផ្លាស់ slider ខាង​ក្រោម​ដើម្បី​មើល​ជម្រាល​នៅ​ចំណុច $x$ ត្រូវ​នឹង​ផល​គុណ​នៃ​ជម្រាល​ខាង​ក្នុង និង​ខាង​ក្រៅ៖

$$
\frac{dy}{dx} = \cos(x^2) \cdot 2x
$$

<div id="viz1" style="width:100%;max-width:800px;margin:0 auto;height:480px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  <label>x = <span id="viz1-x" style="font-weight:bold">1.20</span></label>
  &nbsp;•&nbsp; g'(x) = 2x = <span id="viz1-gp" style="font-weight:bold;color:#7c3aed">2.40</span>
  &nbsp;•&nbsp; f'(u) = cos(u) = <span id="viz1-fp" style="font-weight:bold;color:#0f766e">-0.43</span>
  &nbsp;•&nbsp; <b>dy/dx</b> = <span id="viz1-dydx" style="font-weight:bold;color:#dc2626">-1.04</span><br>
  <input id="viz1-slider" type="range" min="-2.5" max="2.5" step="0.02" value="1.2" style="width:80%;max-width:600px">
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    var xs = [], gs = [], ys = [];
    for (var i = -2.6; i <= 2.6001; i += 0.02) {
      xs.push(i);
      gs.push(i * i);
      ys.push(Math.sin(i * i));
    }
    function plot(x0) {
      var u0 = x0 * x0;
      var y0 = Math.sin(u0);
      var gp = 2 * x0;
      var fp = Math.cos(u0);
      var dydx = fp * gp;
      var tangent_left = y0 + dydx * (-0.6);
      var tangent_right = y0 + dydx * (0.6);
      var traces = [
        { x: xs, y: gs, mode: 'lines', name: 'g(x) = x²',
          line: { color: '#7c3aed', width: 2.5 }, xaxis: 'x1', yaxis: 'y1' },
        { x: [x0], y: [u0], mode: 'markers', showlegend: false,
          marker: { color: '#7c3aed', size: 12 }, xaxis: 'x1', yaxis: 'y1' },

        { x: xs, y: xs.map(function (v) { return Math.sin(v); }),
          mode: 'lines', name: 'f(u) = sin(u)',
          line: { color: '#0f766e', width: 2.5 }, xaxis: 'x2', yaxis: 'y2' },
        { x: [u0], y: [Math.sin(u0)], mode: 'markers', showlegend: false,
          marker: { color: '#0f766e', size: 12 }, xaxis: 'x2', yaxis: 'y2' },

        { x: xs, y: ys, mode: 'lines', name: 'y = sin(x²)',
          line: { color: '#1e40af', width: 3 }, xaxis: 'x3', yaxis: 'y3' },
        { x: [x0 - 0.6, x0 + 0.6], y: [tangent_left, tangent_right],
          mode: 'lines', name: 'tangent (slope dy/dx)',
          line: { color: '#dc2626', width: 2.5, dash: 'dot' },
          xaxis: 'x3', yaxis: 'y3' },
        { x: [x0], y: [y0], mode: 'markers', showlegend: false,
          marker: { color: '#dc2626', size: 12 }, xaxis: 'x3', yaxis: 'y3' }
      ];
      return { traces: traces, gp: gp, fp: fp, dydx: dydx };
    }
    var layout = {
      grid: { rows: 1, columns: 3, pattern: 'independent' },
      xaxis:  { domain: [0.00, 0.30], title: 'x', range: [-2.6, 2.6] },
      yaxis:  { anchor: 'x1', title: 'u = g(x)', range: [-1, 7] },
      xaxis2: { domain: [0.36, 0.66], title: 'u', range: [-1, 7] },
      yaxis2: { anchor: 'x2', title: 'f(u)', range: [-1.2, 1.2] },
      xaxis3: { domain: [0.72, 1.00], title: 'x', range: [-2.6, 2.6] },
      yaxis3: { anchor: 'x3', title: 'y = f(g(x))', range: [-1.4, 1.4] },
      margin: { t: 30, b: 50, l: 50, r: 20 },
      showlegend: false,
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)',
      annotations: [
        { text: 'ខាង​ក្នុង g', xref: 'paper', yref: 'paper', x: 0.15, y: 1.05, showarrow: false, font: { color: '#7c3aed', size: 14, weight: 700 } },
        { text: 'ខាង​ក្រៅ f', xref: 'paper', yref: 'paper', x: 0.51, y: 1.05, showarrow: false, font: { color: '#0f766e', size: 14, weight: 700 } },
        { text: 'សមាស y = f(g(x))', xref: 'paper', yref: 'paper', x: 0.86, y: 1.05, showarrow: false, font: { color: '#1e40af', size: 14, weight: 700 } }
      ]
    };
    var d = plot(1.2);
    Plotly.newPlot('viz1', d.traces, layout, { responsive: true, displayModeBar: false });
    var s = document.getElementById('viz1-slider');
    s.addEventListener('input', function () {
      var x0 = parseFloat(s.value);
      var d = plot(x0);
      document.getElementById('viz1-x').textContent = x0.toFixed(2);
      document.getElementById('viz1-gp').textContent = d.gp.toFixed(2);
      document.getElementById('viz1-fp').textContent = d.fp.toFixed(2);
      document.getElementById('viz1-dydx').textContent = d.dydx.toFixed(2);
      Plotly.react('viz1', d.traces, layout);
    });
  }
  init();
})();
</script>

> **សង្កេត៖** តង់សង់​ក្រហម​លើ​ក្រាប​ស្ដាំ​មាន​ជម្រាល​ស្មើ​ផល​គុណ​នៃ​ជម្រាល​នៅ​ក្រាប​ឆ្វេង (g'(x)) និង​ក្រាប​កណ្ដាល (f'(u))។ នេះ​គឺ chain rule។

## ២. Chain rule (Vector — យ៉ាក់ប៊ីយ៉ាន់)

សម្រាប់ $\mathbf{y} = \mathbf{f}(\mathbf{g}(\mathbf{x}))$ ដែល $\mathbf{x} \in \mathbb{R}^n$, $\mathbf{u} = \mathbf{g}(\mathbf{x}) \in \mathbb{R}^m$, $\mathbf{y} \in \mathbb{R}^p$៖

$$
\frac{\partial \mathbf{y}}{\partial \mathbf{x}} = \frac{\partial \mathbf{y}}{\partial \mathbf{u}} \cdot \frac{\partial \mathbf{u}}{\partial \mathbf{x}}
$$

នោះ​គឺ​ផល​គុណ​ម៉ាទ្រីស​យ៉ាក់ប៊ីយ៉ាន់​ដែល​មាន shape $(p \times m) \cdot (m \times n) = (p \times n)$។

## ៣. ច្បាប់ផលគុណ (Product Rule)

សម្រាប់ scalar៖

$$
(f \cdot g)' = f'g + fg'
$$

សម្រាប់​ម៉ាទ្រីស/វ៉ិចទ័រ៖

$$
\nabla_{\mathbf{x}} (\mathbf{u}^\top \mathbf{v}) = (\nabla_{\mathbf{x}} \mathbf{u})^\top \mathbf{v} + (\nabla_{\mathbf{x}} \mathbf{v})^\top \mathbf{u}
$$

## ៤. ហេស្យ៉ាន់ (Hessian Matrix)

សម្រាប់ $f: \mathbb{R}^n \to \mathbb{R}$, ហេស្យ៉ាន់​គឺ​ម៉ាទ្រីស $n \times n$ នៃ​និស្សន្ទ​លំដាប់​ទីពីរ៖

$$
\mathbf{H} = \nabla^2 f = \begin{bmatrix}
\dfrac{\partial^2 f}{\partial x_1^2} & \cdots & \dfrac{\partial^2 f}{\partial x_1 \partial x_n} \\
\vdots & \ddots & \vdots \\
\dfrac{\partial^2 f}{\partial x_n \partial x_1} & \cdots & \dfrac{\partial^2 f}{\partial x_n^2}
\end{bmatrix}
$$

ហេស្យ៉ាន់​**ឆ្លាស់** (symmetric) ក្នុង​ករណី​ធម្មតា (Schwarz's theorem)។

### លក្ខណៈ​ហេស្យ៉ាន់​បង្ហាញ​ប្រភេទ​ចំណុច​ស្ថានី

នៅ​ចំណុច​ដែល $\nabla f = 0$៖

| លក្ខណៈ $\mathbf{H}$ | ប្រភេទ​ចំណុច |
|---|---|
| Positive definite (all $\lambda_i > 0$) | អប្បបរមា​មូលដ្ឋាន |
| Negative definite (all $\lambda_i < 0$) | អតិបរមា​មូលដ្ឋាន |
| លាយ​សញ្ញា (mixed signs) | ចំណុច​សេន (saddle) |
| Semi-definite (មាន $\lambda_i = 0$) | មិន​ច្បាស់ — ត្រូវ​ពិនិត្យ​បន្ថែម |

## 🎮 រូបភាព interactive ២៖ ហេស្យ៉ាន់​ជា Curvature

ផ្លាស់ slider ដើម្បី​ផ្លាស់ប្ដូរ​មេគុណ​ហេស្យ៉ាន់៖

$$
f(x, y) = \tfrac{1}{2}(a \cdot x^2 + b \cdot y^2), \quad \mathbf{H} = \begin{bmatrix} a & 0 \\ 0 & b \end{bmatrix}
$$

<div id="viz2" style="width:100%;max-width:800px;margin:0 auto;height:450px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  a = <span id="viz2-a" style="font-weight:bold;color:#1e40af">1.0</span>
  &nbsp;<input id="viz2-a-slider" type="range" min="-2" max="2" step="0.1" value="1.0" style="width:35%;max-width:280px">
  &nbsp;&nbsp;
  b = <span id="viz2-b" style="font-weight:bold;color:#1e40af">1.0</span>
  &nbsp;<input id="viz2-b-slider" type="range" min="-2" max="2" step="0.1" value="1.0" style="width:35%;max-width:280px"><br>
  <span id="viz2-type" style="font-weight:bold;font-size:1.1em;color:#0f766e">→ Positive definite · អប្បបរមា</span>
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    var N = 30;
    var xs = [], ys = [];
    for (var i = 0; i < N; i++) {
      var t = -2 + 4 * i / (N - 1);
      xs.push(t); ys.push(t);
    }
    function buildZ(a, b) {
      var z = [];
      for (var i = 0; i < N; i++) {
        var row = [];
        for (var j = 0; j < N; j++) {
          row.push(0.5 * (a * xs[j] * xs[j] + b * ys[i] * ys[i]));
        }
        z.push(row);
      }
      return z;
    }
    function describe(a, b) {
      if (a > 0.05 && b > 0.05) return { t: '→ Positive definite · អប្បបរមា', c: '#10b981' };
      if (a < -0.05 && b < -0.05) return { t: '→ Negative definite · អតិបរមា', c: '#dc2626' };
      if (a * b < 0) return { t: '→ Indefinite · ចំណុច​សេន (saddle)', c: '#f59e0b' };
      return { t: '→ Semi-definite · មិន​ច្បាស់', c: '#6b7280' };
    }
    var layout = {
      scene: {
        xaxis: { title: 'x', range: [-2, 2] },
        yaxis: { title: 'y', range: [-2, 2] },
        zaxis: { title: 'f(x,y)', range: [-5, 5] },
        camera: { eye: { x: 1.6, y: 1.6, z: 0.9 } }
      },
      margin: { t: 10, b: 0, l: 0, r: 0 },
      paper_bgcolor: 'rgba(0,0,0,0)'
    };
    function render(a, b) {
      Plotly.react('viz2', [{
        type: 'surface', x: xs, y: ys, z: buildZ(a, b),
        colorscale: 'RdBu', reversescale: true, showscale: false,
        contours: { z: { show: true, usecolormap: true, project: { z: true } } }
      }], layout, { responsive: true, displayModeBar: false });
      var d = describe(a, b);
      var el = document.getElementById('viz2-type');
      el.textContent = d.t;
      el.style.color = d.c;
    }
    Plotly.newPlot('viz2', [{
      type: 'surface', x: xs, y: ys, z: buildZ(1, 1),
      colorscale: 'RdBu', reversescale: true, showscale: false,
      contours: { z: { show: true, usecolormap: true, project: { z: true } } }
    }], layout, { responsive: true, displayModeBar: false });

    function onChange() {
      var a = parseFloat(document.getElementById('viz2-a-slider').value);
      var b = parseFloat(document.getElementById('viz2-b-slider').value);
      document.getElementById('viz2-a').textContent = a.toFixed(1);
      document.getElementById('viz2-b').textContent = b.toFixed(1);
      render(a, b);
    }
    document.getElementById('viz2-a-slider').addEventListener('input', onChange);
    document.getElementById('viz2-b-slider').addEventListener('input', onChange);
  }
  init();
})();
</script>

> **សាកល្បង​លេង​៖**
> - **a > 0, b > 0** → ចានផ្ដិត (minimum)
> - **a < 0, b < 0** → ផើង​ដួល​ក្បាល​ចុះ (maximum)
> - **a > 0, b < 0** ឬ​ផ្ទុយ → ចំណុច​សេន — ខ្ពស់​ខាង​មួយ, ទាប​ខាង​មួយ

ក្នុង deep learning, ភាគ​ច្រើន​នៃ​ចំណុច​ដែល​ក្រាដ្យង់ = 0 គឺ **ចំណុច​សេន** មិន​មែន​អប្បបរមា — នេះ​ជា​មូលហេតុ​ដែល​ការ​យល់​ហេស្យ៉ាន់​សំខាន់។

---

# ឧទាហរណ៍

**ឧទាហរណ៍ ១៖ Chain rule** — គណនា $\dfrac{dy}{dx}$ បើ $y = (3x^2 + 1)^4$។

កំណត់ $u = 3x^2 + 1$, $y = u^4$។

$$
\frac{du}{dx} = 6x, \quad \frac{dy}{du} = 4u^3
$$

$$
\frac{dy}{dx} = 4u^3 \cdot 6x = 24x \cdot (3x^2 + 1)^3
$$

**ឧទាហរណ៍ ២៖ ហេស្យ៉ាន់** — រក​ហេស្យ៉ាន់​នៃ $f(x, y) = x^2 + xy + y^2$។

និស្សន្ទ​ផ្នែក​លំដាប់​ទីមួយ៖

$$
\frac{\partial f}{\partial x} = 2x + y, \quad \frac{\partial f}{\partial y} = x + 2y
$$

លំដាប់​ទីពីរ៖

$$
\frac{\partial^2 f}{\partial x^2} = 2, \quad \frac{\partial^2 f}{\partial y^2} = 2, \quad \frac{\partial^2 f}{\partial x \partial y} = 1
$$

ដូច្នេះ៖

$$
\mathbf{H} = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}
$$

តម្លៃ​ផ្ទាល់ $\lambda_1 = 3, \lambda_2 = 1$ — ទាំង​ពីរ​វិជ្ជមាន → positive definite → អនុគមន៍​នេះ​មាន​អប្បបរមា​សកល។

---

# កូដ Python

## Chain rule និង​ Hessian ដោយ​ដៃ (NumPy)

```python
import numpy as np

# f(x) = sin(x^2)
def f(x): return np.sin(x ** 2)
def f_grad(x): return np.cos(x ** 2) * 2 * x   # chain rule

x = np.array([1.2])
print(f_grad(x))   # ≈ -1.04

# Hessian សម្រាប់ f(x, y) = x^2 + xy + y^2
def hessian_numerical(f, x, h=1e-4):
    n = len(x)
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            xpp = x.copy(); xpp[i] += h; xpp[j] += h
            xpm = x.copy(); xpm[i] += h; xpm[j] -= h
            xmp = x.copy(); xmp[i] -= h; xmp[j] += h
            xmm = x.copy(); xmm[i] -= h; xmm[j] -= h
            H[i, j] = (f(xpp) - f(xpm) - f(xmp) + f(xmm)) / (4 * h * h)
    return H

g = lambda v: v[0]**2 + v[0]*v[1] + v[1]**2
print(hessian_numerical(g, np.array([1.0, 1.0])))
# [[2. 1.]
#  [1. 2.]]   ✓
```

## Gradient checking — ផ្ទៀង​ផ្ទាត់​ការ implement

នៅ​ពេល​អ្នក implement backpropagation ដោយ​ដៃ, **bug ក្នុង​ការ​គណនា​ក្រាដ្យង់​ពិបាក​រក​ឃើញ​បំផុត** — model នៅ​តែ "train" ប៉ុន្តែ​មិន​ដល់​ដំណោះ​ស្រាយ​ល្អ។ Gradient checking ប្រៀប​ធៀប​ក្រាដ្យង់​វិភាគ​នឹង​ក្រាដ្យង់​លេខ៖

$$
\text{rel\_error} = \frac{\|\nabla_{\text{analytic}} - \nabla_{\text{numerical}}\|_2}{\|\nabla_{\text{analytic}}\|_2 + \|\nabla_{\text{numerical}}\|_2}
$$

- rel_error < $10^{-7}$ → ល្អ​ឥត​ខ្ចោះ
- rel_error < $10^{-4}$ → អាច​មាន bug តូច
- rel_error > $10^{-2}$ → មាន bug ច្បាស់

```python
def numerical_grad(f, x, h=1e-5):
    grad = np.zeros_like(x, dtype=float)
    for i in range(len(x)):
        xp = x.copy().astype(float); xp[i] += h
        xm = x.copy().astype(float); xm[i] -= h
        grad[i] = (f(xp) - f(xm)) / (2 * h)
    return grad

def gradient_check(f, analytic_grad, x):
    num = numerical_grad(f, x)
    ana = analytic_grad(x)
    rel = np.linalg.norm(num - ana) / (np.linalg.norm(num) + np.linalg.norm(ana))
    return rel, num, ana

# សាក​លើ f(x) = x^T x
f_test  = lambda v: v @ v
grad_ok = lambda v: 2 * v
grad_bug = lambda v: 2 * v + 0.01   # មាន bug បន្តិច

x = np.array([3.0, 4.0])
print('ok  :', gradient_check(f_test, grad_ok,  x)[0])   # ≈ 1e-11
print('bug :', gradient_check(f_test, grad_bug, x)[0])   # ≈ 1e-3
```

---

# ការអនុវត្តន៍ជាក់ស្ដែង

## 🎮 រូបភាព interactive ៣៖ Gradient checking ដោយ​ឯង

ខាង​ក្រោម​នេះ, យើង training គំរូ MSE តូច​មួយ​ដោយ gradient descent។ អ្នក​អាច "បំផ្លាញ" ក្រាដ្យង់​វិភាគ​ដោយ​បន្ថែម bias bug ហើយ​មើល​ relative error ក្នុង​ gradient check។

<div id="viz3" style="width:100%;max-width:800px;margin:0 auto;height:380px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  Analytic gradient bug (bias added): <span id="viz3-bug" style="font-weight:bold">0.000</span><br>
  <input id="viz3-slider" type="range" min="-1" max="1" step="0.01" value="0" style="width:80%;max-width:600px"><br>
  <span style="font-size:0.95em">
    Numerical: <span id="viz3-num" style="color:#1e40af;font-weight:bold">-</span> &nbsp;|&nbsp;
    Analytic: <span id="viz3-ana" style="color:#7c3aed;font-weight:bold">-</span> &nbsp;|&nbsp;
    Relative error: <span id="viz3-err" style="color:#dc2626;font-weight:bold">-</span>
  </span>
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    // f(w) = (w-3)^2,  true grad = 2(w-3),  buggy grad = 2(w-3) + bug
    function f(w) { return (w - 3) * (w - 3); }
    function analytic(w, bug) { return 2 * (w - 3) + bug; }
    function numerical(w, h) {
      h = h || 1e-5;
      return (f(w + h) - f(w - h)) / (2 * h);
    }
    function trainGD(bug, lr, steps) {
      var w = 0, hist = [w];
      for (var i = 0; i < steps; i++) { w = w - lr * analytic(w, bug); hist.push(w); }
      return hist;
    }
    var ws = [];
    for (var i = -1; i <= 6.01; i += 0.05) ws.push(i);
    var fs = ws.map(f);
    function plot(bug) {
      var hist = trainGD(bug, 0.1, 30);
      var fh = hist.map(f);
      var w_probe = 0.0;
      var ana = analytic(w_probe, bug);
      var num = numerical(w_probe);
      var err = Math.abs(ana - num) / (Math.abs(ana) + Math.abs(num) + 1e-12);
      return {
        traces: [
          { x: ws, y: fs, mode: 'lines', name: 'f(w) = (w−3)²',
            line: { color: '#1e40af', width: 3 } },
          { x: hist, y: fh, mode: 'lines+markers', name: 'GD trajectory',
            line: { color: '#dc2626', width: 2 },
            marker: { size: 6, color: '#dc2626' } },
          { x: [3], y: [0], mode: 'markers', name: 'true min (w=3)',
            marker: { color: '#10b981', size: 14, symbol: 'star',
                      line: { color: '#065f46', width: 2 } } }
        ],
        ana: ana, num: num, err: err
      };
    }
    var layout = {
      xaxis: { title: 'w', range: [-1, 6] },
      yaxis: { title: 'f(w)', range: [-1, 18] },
      margin: { t: 20, b: 50, l: 50, r: 20 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    var d = plot(0);
    Plotly.newPlot('viz3', d.traces, layout, { responsive: true, displayModeBar: false });
    document.getElementById('viz3-num').textContent = d.num.toFixed(3);
    document.getElementById('viz3-ana').textContent = d.ana.toFixed(3);
    document.getElementById('viz3-err').textContent = d.err.toExponential(2);
    document.getElementById('viz3-slider').addEventListener('input', function (e) {
      var bug = parseFloat(e.target.value);
      document.getElementById('viz3-bug').textContent = bug.toFixed(3);
      var d = plot(bug);
      Plotly.react('viz3', d.traces, layout);
      document.getElementById('viz3-num').textContent = d.num.toFixed(3);
      document.getElementById('viz3-ana').textContent = d.ana.toFixed(3);
      document.getElementById('viz3-err').textContent = d.err.toExponential(2);
    });
  }
  init();
})();
</script>

> **សង្កេត៖**
> - **bug = 0** → relative error ≈ $10^{-11}$ → ការ implement ត្រឹមត្រូវ, GD ដល់​ដំណោះ​ស្រាយ $w = 3$
> - **bug ≠ 0** → relative error ធំ​ឡើង, GD ឈប់​នៅ​ចំណុច​ខុស (bias offset)
> - នេះ​បង្ហាញ​ហេតុ​ដែល​អ្នក​ស្រាវ​ជ្រាវ ML ត្រូវ​ធ្វើ gradient check **មុន​ training**

## ការ​អនុវត្ត​នៅ​ក្នុង​ឧស្សាហកម្ម

**Backpropagation = Chain rule × Gradient computation** — នេះ​គឺ algorithm មូលដ្ឋាន​នៃ deep learning។ នៅ​ក្នុង neural network មាន​ស្រទាប់ $L$៖

$$
\frac{\partial \mathcal{L}}{\partial \mathbf{W}^{(1)}} = \frac{\partial \mathcal{L}}{\partial \mathbf{a}^{(L)}} \cdot \frac{\partial \mathbf{a}^{(L)}}{\partial \mathbf{a}^{(L-1)}} \cdots \frac{\partial \mathbf{a}^{(2)}}{\partial \mathbf{W}^{(1)}}
$$

PyTorch និង TensorFlow អនុវត្ត chain rule ដោយ​ស្វ័យ​ប្រវត្តិ​តាមរយៈ **autograd** — អ្នក​ប្រកាស forward pass, ហើយ framework គណនា backward pass ដោយ​ឯង។

**ការ​ប្រើ​ប្រាស់​នៅ​កម្ពុជា និង​តំបន់៖**
- **Khmer NLP** — Hugging Face transformer for Khmer (Sealang, KhmerST) training ដោយ backprop លើ chain rule
- **Acleda AI fraud detection** — neural network training ដោយ Adam optimizer (ប្រើ​ទាំង​ក្រាដ្យង់​និង Hessian-like adaptive step)
- **Image OCR for Khmer documents** — CNN training ដោយ backprop ក្នុង​ស្រទាប់​រាប់​ដប់

**ហេតុ​ដែល​ត្រូវ​យល់ Hessian៖** ក្នុង Newton's method, យើង​ប្រើ $\mathbf{H}^{-1}$ ដើម្បី​បង្ហើយ​ការ training លឿន​ជាង gradient descent — ប៉ុន្តែ​ការ​ច្រាស​ម៉ាទ្រីស $n \times n$ ថ្លៃ​ខ្លាំង។ ដូច្នេះ​ក្នុង​ deep learning, យើង​ប្រើ **quasi-Newton methods** ដូចជា L-BFGS, ឬ **adaptive optimizers** ដូចជា Adam, RMSprop ដែល​ប៉ាន់​ប្រមាណ​ឥទ្ធិពល​នៃ Hessian ដោយ​មាន cost ទាប។

---

# លំហាត់

1. គណនា $\dfrac{dy}{dx}$ បើ $y = e^{\sin(2x)}$។
2. រក​ហេស្យ៉ាន់​នៃ $f(x, y) = x^3 - 3xy + y^3$ នៅ​ចំណុច $(1, 1)$ ហើយ​ប្រាប់​ប្រភេទ​ចំណុច (min / max / saddle)។
3. **ប្រើ​រូបភាព interactive ៣**៖ រក​តម្លៃ​ bug អប្បបរមា​ដែល​ធ្វើ​ឱ្យ relative error លើស $10^{-2}$ (ដែល​ត្រូវ​ចាត់​ទុក​ថា​មាន bug ច្បាស់)។

> **ចម្លើយ៖**
> (1) $\dfrac{dy}{dx} = e^{\sin(2x)} \cdot \cos(2x) \cdot 2 = 2\cos(2x) \cdot e^{\sin(2x)}$
> (2) $\mathbf{H}(1,1) = \begin{bmatrix} 6 & -3 \\ -3 & 6 \end{bmatrix}$ → $\lambda = 3, 9$ → ទាំង​ពីរ​វិជ្ជមាន → **អប្បបរមា​មូលដ្ឋាន**
> (3) ប្រហែល $|\text{bug}| \approx 0.12$ ឡើង​ទៅ (សាក​លេង​ផ្ទាល់!)

---

**មេរៀន​បន្ទាប់ (ជំពូក 3):** ប្រូបាប៊ីលីតេ​សម្រាប់ ML — distribution, conditional probability, Bayes' theorem, និង intuition សម្រាប់​មាតិកា​ដែល​នឹង​មាន​ក្នុង MLE/MAP, Naive Bayes, និង​គំរូ probabilistic ផ្សេងៗ។
