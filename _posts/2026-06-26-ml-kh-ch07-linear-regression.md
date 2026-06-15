---
layout: post
title: "[ML Khmer] ជំពូក 7: តំរែតំរង់​លីនេអ៊ែរ (Linear Regression)"
date: 2026-06-26 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, linear-regression, supervised, gradient-descent, interactive]
thumbnail: /images/ml-series/ch07-linear-regression.svg
---

ឥឡូវ​នេះ — យើង​ build algorithm ML ​​ដំបូង​ដោយ​ដៃ! **Linear regression** ​ជា​​​​​​មូលដ្ឋាន​​​​​​​​​សាមញ្ញ​បំផុត ​តែ​ស្ថិត​នៅ​ស្នូល​នៃ​អ្វី​ៗ​ច្រើន — Ridge, Lasso, logistic regression, neural network output layer, ​សូម្បី​​​ attention scores ​ក្នុង Transformer។ ​មេរៀន​នេះ​​បង្ហាញ​៖ ​សមីការ $\hat y = w^\top x + b$, MSE loss, ​ដំណោះ​ស្រាយ​ closed-form (normal equation), gradient descent, ​ការ​បកស្រាយ coefficients, ​និង​ R²។ មាន **រូបភាព interactive ៣**៖ ​អ្នក​​​ដោះ​ស្រាយ slope/intercept ​ដោយ​ដៃ, gradient descent ​​​លើ​ loss surface, ​​​​និង polynomial regression ​ដែល​​បង្ហាញ overfit។

---

# សង្ខេប

- **Model**៖ $\hat y = w^\top x + b$ — ​លីនេអ៊ែរ​ក្នុង parameters $(w, b)$
- **Loss**៖ $L = \frac{1}{n} \sum_i (y_i - \hat y_i)^2$ — Mean Squared Error
- **ដំណោះ​ស្រាយ​ closed-form** (normal equation)៖ $w^* = (X^\top X)^{-1} X^\top y$
- **ដំណោះ​ស្រាយ​ iterative** (gradient descent)៖ $w \leftarrow w - \alpha \nabla L$
- **Metric**៖ R² = $1 - \dfrac{\text{SS}_{\text{res}}}{\text{SS}_{\text{tot}}}$ — ​ភាគ​រយ​នៃ variance ​ដែល model ពន្យល់
- **​ការ​ភ្ជាប់​ MLE** (ពី​មេរៀន​ 4)៖ MSE = Gaussian MLE ​នៅ​ពេល noise ​ជា Gaussian

---

# ហេតុ​អ្វី​សំខាន់?

Linear regression ​មាន​ឫស​នៅ​ស្ទើរ​តែ​គ្រប់​​ប្រព័ន្ធ​​ ML៖

- **Neural network**៖ ​​​ layer ​​នីមួយ​ៗ​​ជា​ linear transformation $W x + b$ ​បន្ទាប់​ដោយ​ activation
- **Logistic regression**៖ linear regression ​បន្ទាប់​មក sigmoid
- **Softmax regression**៖ linear ​បន្ទាប់​មក softmax
- **Attention ​ក្នុង Transformer**៖ Q, K, V ជា linear projections
- **Time series forecasting**៖ ARIMA, exponential smoothing — linear ​ស្ទើរ​តែ​ទាំង​អស់

**ឧស្សាហកម្ម​នៅ​កម្ពុជា​ដែល​ប្រើ​ផ្ទាល់៖**

- **PP real estate** — ​ព្យាករ​តម្លៃ​ផ្ទះ​ពី sqm, ​ខណ្ឌ, ​ឆ្នាំ​សាង​សង់
- **AMK loan** — ​ព្យាករ loan amount ​​ដែល​​អតិថិជន​​​​​​អាច​​សង​​បាន
- **Crop yield** — ​ព្យាករ​ទិន្នផល kg/ha ​ពី rainfall, NDVI, temperature
- **Wing fees** — ​ព្យាករ commission ​ពី volume, ​ប្រភេទ​ប្រតិបត្តិការ
- **Khmer text length** — ​ព្យាករ​ការ​អាន​ពេល​​ ​ពី​ចំនួន​ពាក្យ, ភាព​ស្មុគ​ស្មាញ

​ការ​យល់​ linear regression ​ឱ្យ​អ្នក​ដឹង **ហេតុ​ដែល model ​ផ្សេងៗ​ដំណើរការ​ដូច​ច្នេះ** — មិន​មែន​​​ blindly call `model.fit()` ឡើយ។

---

# ពាក្យ​បច្ចេកទេស​ថ្មី

| ខ្មែរ | English | កំណត់​សម្គាល់ |
|---|---|---|
| តំរែតំរង់​លីនេអ៊ែរ | linear regression | $\hat y = w^\top x + b$ |
| ​ប៉ារ៉ាម៉ែត្រ​ទម្ងន់ | weight / coefficient | $w_j$ — ​ឥទ្ធិពល​នៃ feature $j$ |
| Intercept / bias | intercept / bias | $b$ — តម្លៃ​នៅ​ពេល $x = 0$ |
| Residual | residual | $y_i - \hat y_i$ — ​ភាព​ខុស​ឆ្គង |
| Mean Squared Error | MSE | មធ្យម​នៃ residual ​លើ​​ ២ |
| Normal equation | normal equation | $w^* = (X^\top X)^{-1} X^\top y$ |
| Design matrix | design matrix | $X \in \mathbb{R}^{n \times d}$ — ​ទិន្នន័យ​ទាំង​អស់​ជា​ matrix |
| Gradient descent | gradient descent | ​រត់​ឆ្ពោះ​ឆ្ងាយ​ពី gradient |
| Learning rate | learning rate | $\alpha$ — ​ទំហំ​នៃ step |
| R² (R-squared) | coefficient of determination | ​ភាគ​រយ​​ variance ​ដែល model ពន្យល់ |
| Multicollinearity | multicollinearity | feature ​ច្រើន​ស្រដៀង​គ្នា → $X^\top X$ ​ងងឹត |
| Homoscedasticity | homoscedasticity | variance ​នៃ noise ​​​ដូច​គ្នា​គ្រប់ $x$ |

---

# គំនិត​វិចារណញ្ញាណ

## "​គូ​សខ្សែ​ត្រង់​ឆ្លង​ចំណុច​"

ឱ្យ​ចំណុច​ ​មួយ​ចំនួន​លើ​ scatter plot — ​ស្វែង​រក​ "​ខ្សែ​ត្រង់​ល្អ​បំផុត" ​ដែល​ឆ្លង​ចំណុច​ទាំង​នោះ។

**តើ​ខ្សែ​​ណា​ "​ល្អ​"?** ​ខ្សែ​ដែល​ **residual ​សរុប​​​ស្ថិត​ក្នុង​បរិមាណ​​តូច​បំផុត**។ ​ប៉ុន្តែ​យើង​ប្រើ​ residual លើ ២ (​មិន​មែន absolute) ​ដោយ​សារ៖

- ​ហ្គឺ​មណ៍​ងាយ​យក derivative ​ហើយ​ដោះ​ស្រាយ​ដោយ​ដៃ
- ​ហ្គឺ​មណ៍​ត្រូវ​នឹង Gaussian MLE (មេរៀន​ 4)
- ​ឱ្យ​ការ​ដាក់​ទម្ងន់​ច្រើន​លើ​ error ​ធំៗ (ភាគ​រយ​ច្រើន​ជាង​ error តូច)

## ​ឧបមេយ្យ​ស្នូល៖ "​​ល្បឿន + ល្បាក់​ហួស"

ឧបមា​អ្នក​បើក​ tuktuk ​ពី Toul Tom Pong ​ទៅ Phsar Thmey — ​អ្នក​មាន ៖
- $x$ = ​ល្បឿន​មធ្យម (km/h)
- $y$ = ​ពេល​ដែល​យក (minutes)

​អ្នក​មាន​ទិន្នន័យ​ប្រវត្តិ 30 ​ដង — ​ខ្សែ​ត្រង់​ $\hat y = w \cdot x + b$ ​ប្រាប់​អ្នក​ថា៖

- បើ $x = 20$ km/h → ប្រហែល $\hat y = 18$ ​នាទី
- ​បើ $x = 40$ km/h → ប្រហែល $\hat y = 9$ នាទី

$w$ ​ប្រាប់​អ្នក​ "​​​ល្បឿន​បន្ថែម 1 km/h ​បន្ថយ​ពេល​ប៉ុនណា"; $b$ ​ប្រាប់​​​​​អ្នក​ "​ពេល​មូល​ដ្ឋាន​​ដែល​មិន​អាស្រ័យ​ល្បឿន" (eg. ការ​ឈប់​ភ្លើង​ស្ទប់)។

## "​ការ​​​ស្វែង​រក​ខ្សែ​​ល្អ​បំផុត​​ = ​ការ​ចាក់​​​ស្នូរ​ Q ​ឆ្ពោះ​ទៅ​អប្បបរមា"

​លោក​ MSE ​បង្កើត **bowl-shaped surface** លើ space (w, b) — មាន​​អប្បបរមា **តែ​មួយ​ប៉ុណ្ណោះ**។ ​អ្នក​អាច​ដោះ​ស្រាយ​ដោយ​ផ្ទាល់ (normal equation) ​ឬ​ "​រត់​ចុះ​ភ្នំ" ​(gradient descent)។

---

# និយមន័យ និង​គណិតវិទ្យា

## ១. Model setup

​ឱ្យ training data $\{(x_i, y_i)\}_{i=1}^n$ ដែល $x_i \in \mathbb{R}^d$ ​និង $y_i \in \mathbb{R}$។ ​​Linear regression model៖

$$
\hat y_i = w^\top x_i + b = w_1 x_{i,1} + w_2 x_{i,2} + \cdots + w_d x_{i,d} + b
$$

​​​បំបារ៉ាមីត្រ​ដែល​​​ត្រូវ​រៀន៖ vector $w \in \mathbb{R}^d$ ​និង scalar $b$។

**គន្លឹះ​ជាក់​លាក់៖** ​បន្ថែម column ​ដែល​មាន 1 ​ទាំង​អស់​ទៅ $X$, ​បន្ទាប់​មក $b$ ​ក្លាយ​ជា $w_0$ ​នៃ vector w ​ដែល​ពង្រីក។ ​សរសេរ​​​ដ៏​សាមញ្ញ​ក្លាយ​ជា៖

$$
\hat y = X w
$$

## ២. Mean Squared Error

​​​បាត់​បង់​ ​​(loss) ​សម្រាប់​ training set ​ទាំង​មូល៖

$$
L(w) = \frac{1}{n} \sum_{i=1}^n (y_i - \hat y_i)^2 = \frac{1}{n} \| y - X w \|^2
$$

​គោល​ដៅ៖

$$
w^* = \arg\min_w L(w)
$$

## ៣. Normal equation — ដំណោះ​ស្រាយ​​​ closed-form

យក derivative ​នៃ $L$ ​តាម $w$ ​ស្មើ​នឹង 0៖

$$
\nabla_w L = -\frac{2}{n} X^\top (y - X w) = 0
$$

​ដោះ​ស្រាយ៖

$$
X^\top X \, w = X^\top y
$$

​បើ $X^\top X$ ​ងងឹត (invertible)៖

$$
\boxed{\;\; w^* = (X^\top X)^{-1} X^\top y \;\;}
$$

​នេះ​ជា **normal equation**។ ​ផ្ដល់​ដំណោះ​ស្រាយ​​ច្បាស់​​​ក្នុង​ one step!

**​ភាព​ស្មុគ​ស្មាញ​​​ខាង​លេខ៖** $X^\top X$ ​មាន size $d \times d$; matrix inversion ​មាន​ ​complexity $O(d^3)$។ ​ល្អ​ពេល $d \le 10{,}000$ ​; ​ពេល​ $d$ ធំ​ខ្លាំង — ​ប្រើ gradient descent។

## ៤. Gradient descent

ជំហាន​ update៖

$$
w \leftarrow w - \alpha \nabla_w L = w + \frac{2 \alpha}{n} X^\top (y - X w)
$$

​​ដោយ $\alpha$ ​ជា **learning rate**។ ​រត់​​ច្រើន​​ដង​​​​​​​រហូត​ដល់ convergence។

**ភាព​ជ្រើស​​ $\alpha$៖**
- ​ធំ​ពេក → ​ឆ្លង​ឆ្ងាយ​ពី​​ minimum, ប្រហែល​ diverge
- ​តូច​ពេក → ​​​​យឺត​ខ្លាំង​​
- ​ច្បាប់​ទូទៅ​ចាប់​ផ្ដើម​ដោយ $\alpha \in \{0.001, 0.01, 0.1\}$

## 🎮 ​រូប​ភាព​ interactive ១៖ ​ដោះ​ស្រាយ​ដោយ​ដៃ

​​​ប្ដូរ slider សម្រាប់ slope ($w$) និង intercept ($b$) — ​មើល​ MSE ​​​ដែល​​​ផ្លាស់​​ប្ដូរ។ ​ចុច "​ដំណោះ​ស្រាយ​​​ផ្ទាល់" ​​​ដើម្បី​​​​​បង្ហាញ normal equation solution។

<div id="viz1" style="width:100%;max-width:800px;margin:0 auto;height:440px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  w (slope) = <span id="viz1-w" style="font-weight:bold;color:#dc2626">1.00</span>
  <input id="viz1-w-slider" type="range" min="-2" max="4" step="0.05" value="1.0" style="width:40%;max-width:350px"><br>
  b (intercept) = <span id="viz1-b" style="font-weight:bold;color:#7c3aed">0.00</span>
  <input id="viz1-b-slider" type="range" min="-5" max="10" step="0.1" value="0.0" style="width:40%;max-width:350px"><br>
  <button id="viz1-solve" style="margin-top:6px;padding:5px 14px;font-weight:600;cursor:pointer">📐 ដំណោះ​ស្រាយ​ផ្ទាល់ (normal eq)</button>
  &nbsp;
  <button id="viz1-new" style="padding:5px 14px;cursor:pointer">🎲 ​ទិន្នន័យ​ថ្មី</button><br>
  <span style="font-size:1.05em;margin-top:6px;display:inline-block">
    MSE = <span id="viz1-mse" style="font-weight:bold;color:#0f766e">--</span>
    &nbsp;|&nbsp;
    R² = <span id="viz1-r2" style="font-weight:bold;color:#1e40af">--</span>
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
    var DATA = null;
    function gen() {
      var n = 30, pts = [];
      var trueW = 1.5 + 1.5 * Math.random();
      var trueB = -2 + 4 * Math.random();
      for (var i = 0; i < n; i++) {
        var x = 1 + 9 * Math.random();
        var y = trueW * x + trueB + 2 * randn();
        pts.push([x, y]);
      }
      DATA = pts;
    }
    function solve() {
      var n = DATA.length;
      var sx = 0, sy = 0, sxx = 0, sxy = 0;
      for (var i = 0; i < n; i++) {
        sx += DATA[i][0]; sy += DATA[i][1];
        sxx += DATA[i][0] * DATA[i][0];
        sxy += DATA[i][0] * DATA[i][1];
      }
      var w = (n * sxy - sx * sy) / (n * sxx - sx * sx);
      var b = (sy - w * sx) / n;
      return { w: w, b: b };
    }
    function metrics(w, b) {
      var n = DATA.length, ssr = 0, sst = 0;
      var meanY = DATA.reduce(function (s, p) { return s + p[1]; }, 0) / n;
      for (var i = 0; i < n; i++) {
        var pred = w * DATA[i][0] + b;
        ssr += (DATA[i][1] - pred) * (DATA[i][1] - pred);
        sst += (DATA[i][1] - meanY) * (DATA[i][1] - meanY);
      }
      return { mse: ssr / n, r2: 1 - ssr / sst };
    }
    function plot(w, b) {
      var lineX = [0, 11], lineY = [b, w * 11 + b];
      var residX = [], residY = [];
      for (var i = 0; i < DATA.length; i++) {
        residX.push(DATA[i][0], DATA[i][0], null);
        residY.push(DATA[i][1], w * DATA[i][0] + b, null);
      }
      return [
        { x: residX, y: residY, mode: 'lines', name: 'residuals',
          line: { color: '#dc2626', width: 1.5, dash: 'dot' }, showlegend: false,
          hoverinfo: 'skip' },
        { x: lineX, y: lineY, mode: 'lines', name: 'ŷ = w·x + b',
          line: { color: '#dc2626', width: 3 } },
        { x: DATA.map(function (p) { return p[0]; }),
          y: DATA.map(function (p) { return p[1]; }),
          mode: 'markers', name: 'data',
          marker: { color: '#1e40af', size: 9, line: { color: '#fff', width: 1 } } }
      ];
    }
    var layout = {
      xaxis: { title: 'x', range: [0, 11] },
      yaxis: { title: 'y', range: [-5, 30] },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    gen();
    Plotly.newPlot('viz1', plot(1, 0), layout, { responsive: true, displayModeBar: false });
    function render() {
      var w = parseFloat(document.getElementById('viz1-w-slider').value);
      var b = parseFloat(document.getElementById('viz1-b-slider').value);
      document.getElementById('viz1-w').textContent = w.toFixed(2);
      document.getElementById('viz1-b').textContent = b.toFixed(2);
      var m = metrics(w, b);
      document.getElementById('viz1-mse').textContent = m.mse.toFixed(2);
      document.getElementById('viz1-r2').textContent = m.r2.toFixed(3);
      Plotly.react('viz1', plot(w, b), layout);
    }
    document.getElementById('viz1-w-slider').addEventListener('input', render);
    document.getElementById('viz1-b-slider').addEventListener('input', render);
    document.getElementById('viz1-solve').addEventListener('click', function () {
      var s = solve();
      document.getElementById('viz1-w-slider').value = s.w;
      document.getElementById('viz1-b-slider').value = s.b;
      render();
    });
    document.getElementById('viz1-new').addEventListener('click', function () { gen(); render(); });
    render();
  }
  init();
})();
</script>

> **សាក​មើល៖** ​ប្ដូរ slider រហូត​ MSE ​ដួល​ឱ្យ​តូច​បំផុត។ ​បន្ទាប់​មក​ចុច "ដំណោះ​ស្រាយ​​​ផ្ទាល់" — ​ឃើញ​ថា​ការ​ដោះ​ស្រាយ closed-form ​ឱ្យ​អប្បបរមា​​​ច្បាស់ៗ ​ដោយ​មិន​ត្រូវ​ការ​ try-and-error។ R² ​ខ្ពស់​បំផុត​ត្រូវ​នឹង​ MSE ​ទាប​បំផុត។

## 🎮 ​រូប​ភាព​ interactive ២៖ Gradient descent លើ loss surface

Loss surface $L(w, b)$ ​ជា bowl (paraboloid)។ Gradient descent ​​​ចាប់​ផ្ដើម​ពី​​ចំណុច random ហើយ​ "​រត់​ចុះ​ភ្នំ"។ ​ប្ដូរ learning rate — ​មើល​​ផ្លូវ​ដែល​ផ្លាស់​ប្ដូរ។

<div id="viz2" style="width:100%;max-width:800px;margin:0 auto;height:500px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  Learning rate α = <span id="viz2-lr" style="font-weight:bold;color:#dc2626">0.020</span>
  <input id="viz2-lr-slider" type="range" min="-3" max="-0.3" step="0.05" value="-1.7" style="width:40%;max-width:350px"><br>
  Steps = <span id="viz2-steps" style="font-weight:bold;color:#1e40af">30</span>
  <input id="viz2-steps-slider" type="range" min="1" max="100" step="1" value="30" style="width:40%;max-width:350px"><br>
  <button id="viz2-restart" style="padding:5px 14px;cursor:pointer">🔁 ​ចាប់​ផ្ដើម​ឡើង​វិញ</button>
  &nbsp;
  <span style="font-size:1.05em;margin-left:10px">
    Final MSE = <span id="viz2-mse" style="font-weight:bold;color:#0f766e">--</span>
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
    var TRUE_W = 2.0, TRUE_B = 1.0;
    var DATA = [];
    for (var i = 0; i < 40; i++) {
      var x = -3 + 6 * Math.random();
      DATA.push([x, TRUE_W * x + TRUE_B + 1.0 * randn()]);
    }
    function loss(w, b) {
      var s = 0;
      for (var i = 0; i < DATA.length; i++) {
        var r = DATA[i][1] - (w * DATA[i][0] + b);
        s += r * r;
      }
      return s / DATA.length;
    }
    function grad(w, b) {
      var gw = 0, gb = 0;
      for (var i = 0; i < DATA.length; i++) {
        var r = DATA[i][1] - (w * DATA[i][0] + b);
        gw += -2 * DATA[i][0] * r;
        gb += -2 * r;
      }
      return [gw / DATA.length, gb / DATA.length];
    }
    var START = { w: -3.5, b: -5 };
    function runGD(lr, steps) {
      var w = START.w, b = START.b;
      var path = [[w, b, loss(w, b)]];
      for (var t = 0; t < steps; t++) {
        var g = grad(w, b);
        w -= lr * g[0];
        b -= lr * g[1];
        if (!isFinite(w) || !isFinite(b)) break;
        path.push([w, b, loss(w, b)]);
      }
      return path;
    }
    function plot(lr, steps) {
      var ws = [], bs = [], zs = [];
      var grid = 40;
      for (var i = 0; i <= grid; i++) ws.push(-4 + 8 * i / grid);
      for (var j = 0; j <= grid; j++) bs.push(-6 + 12 * j / grid);
      for (var j2 = 0; j2 <= grid; j2++) {
        var row = [];
        for (var i2 = 0; i2 <= grid; i2++) row.push(loss(ws[i2], bs[j2]));
        zs.push(row);
      }
      var path = runGD(lr, steps);
      var pw = path.map(function (p) { return p[0]; });
      var pb = path.map(function (p) { return p[1]; });
      return {
        traces: [
          { x: ws, y: bs, z: zs, type: 'contour',
            colorscale: 'Viridis', contours: { coloring: 'fill' },
            line: { width: 0.5, color: 'rgba(255,255,255,0.3)' },
            colorbar: { title: 'L(w, b)' }, opacity: 0.9 },
          { x: pw, y: pb, mode: 'lines+markers', name: 'GD path',
            line: { color: '#dc2626', width: 3 },
            marker: { color: '#dc2626', size: 7, line: { color: '#fff', width: 1 } } },
          { x: [TRUE_W], y: [TRUE_B], mode: 'markers', name: 'optimum (w*, b*)',
            marker: { color: '#facc15', size: 18, symbol: 'star', line: { color: '#0f172a', width: 2 } } },
          { x: [START.w], y: [START.b], mode: 'markers', name: 'start',
            marker: { color: '#0f172a', size: 14, symbol: 'circle-open', line: { width: 3 } } }
        ],
        finalLoss: path[path.length - 1][2]
      };
    }
    var layout = {
      xaxis: { title: 'w' },
      yaxis: { title: 'b' },
      margin: { t: 20, b: 50, l: 60, r: 80 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    var d = plot(0.02, 30);
    Plotly.newPlot('viz2', d.traces, layout, { responsive: true, displayModeBar: false });
    document.getElementById('viz2-mse').textContent = d.finalLoss.toFixed(3);
    function render() {
      var lr = Math.pow(10, parseFloat(document.getElementById('viz2-lr-slider').value));
      var steps = parseInt(document.getElementById('viz2-steps-slider').value);
      document.getElementById('viz2-lr').textContent = lr.toFixed(3);
      document.getElementById('viz2-steps').textContent = steps;
      var d = plot(lr, steps);
      document.getElementById('viz2-mse').textContent = isFinite(d.finalLoss) ? d.finalLoss.toFixed(3) : '∞ (diverged!)';
      Plotly.react('viz2', d.traces, layout);
    }
    document.getElementById('viz2-lr-slider').addEventListener('input', render);
    document.getElementById('viz2-steps-slider').addEventListener('input', render);
    document.getElementById('viz2-restart').addEventListener('click', render);
  }
  init();
})();
</script>

> **​សង្កេត​ត្រាប់៖**
> - **α = 0.001 (តូច​ខ្លាំង)** — ​​ផ្លូវ​​​​​លំ​ហើយ​​​​​​យឺត — មិន​ដល់​ optimum
> - **α = 0.02 (ល្អ)** — ​​​ផ្លូវ​​​​​​​​​បត់​​​ឆ្ពោះ​​​​ទៅ optimum
> - **α = 0.3 (ធំ​​ខ្លាំង)** — ​បោះ​ឆ្លង​ optimum, oscillate ​ឬ diverge
> - **​ដាក់​ Steps ​ច្រើន (eg. 100) ហើយ α ​ល្អ** — convergence ​ច្បាស់ៗ​​​ដល់​ star

## ៥. R² — ​ការ​វាយ​តម្លៃ regression model

$$
R^2 = 1 - \frac{\text{SS}_{\text{res}}}{\text{SS}_{\text{tot}}} = 1 - \frac{\sum_i (y_i - \hat y_i)^2}{\sum_i (y_i - \bar y)^2}
$$

​ការ​បកស្រាយ៖
- $R^2 = 1$ → model ពន្យល់ variance ​ទាំង​មូល​ (ល្អ​​​ឥត​ខ្ចោះ)
- $R^2 = 0$ → model ​ដូច​ប្រាប់ $\bar y$ ​ត្រឹមៗ
- $R^2 < 0$ → model ​អន់​ជាង "​ឆ្លើយ mean ​គ្រប់​ពេល"!

**ច្បាប់​​ផ្ទាល់​មាត់៖**

| R² | ​ការ​អោះអាង |
|---|---|
| > 0.9 | ​ល្អ​​​​​​ខ្ពស់ |
| 0.7 – 0.9 | ​ល្អ |
| 0.5 – 0.7 | ​មធ្យម |
| < 0.5 | ​ប្រហែល​ត្រូវ​ feature engineering ​ឬ algorithm ​ស្មុគ​ស្មាញ​ជាង |

## ៦. ​ការ​ភ្ជាប់​ MLE (មេរៀន 4)

​ឧបមា $y_i = w^\top x_i + \varepsilon_i$ ​ដែល $\varepsilon_i \sim \mathcal{N}(0, \sigma^2)$ i.i.d.។ Log-likelihood៖

$$
\log P(D \mid w) = -\frac{1}{2\sigma^2} \sum_i (y_i - w^\top x_i)^2 + C
$$

**Maximize log-likelihood = minimize SSE = minimize MSE!**

​ដូច្នេះ **MSE loss = Gaussian noise assumption**។ ​បើ noise ​មិន​មែន​ Gaussian (eg. heavy-tailed, outliers ច្រើន) — ​ត្រូវ​ប្រើ Huber loss ​ឬ MAE ​ជំនួស។

## ៧. Polynomial regression = ​linear regression ​លើ features ​ដែល​បាន engineer

​បន្ថែម polynomial features៖

$$
\phi(x) = [1, x, x^2, x^3, \ldots, x^p]
$$

​បន្ទាប់​មក​​ដាក់ linear regression ​លើ $\phi(x)$ — model ​នៅ​តែ "linear in parameters" ​​ប៉ុន្តែ​​​​អាច​ផ្គូផ្គង​ curve ​ស្មុគ​ស្មាញ។

​បញ្ហា៖ ​ពេល degree $p$ ​ធំ​​ខ្លាំង → **overfit** (mention នៅ​មេរៀន​ 8 ​ដែល​នឹង​មក)។

## 🎮 ​រូប​ភាព​ interactive ៣៖ Polynomial overfit demo

​ប្ដូរ degree នៃ polynomial — ​មើល​ train R² ​ឡើង​​ខ្ពស់​​​ប៉ុន្តែ test R² ​ដួល​ចុះ។

<div id="viz3" style="width:100%;max-width:800px;margin:0 auto;height:440px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  Polynomial degree = <span id="viz3-d" style="font-weight:bold;color:#dc2626">3</span>
  <input id="viz3-d-slider" type="range" min="1" max="15" step="1" value="3" style="width:50%;max-width:400px"><br>
  <button id="viz3-new" style="padding:5px 14px;cursor:pointer">🎲 ​ទិន្នន័យ​ថ្មី</button>
  &nbsp;
  <span style="font-size:1.05em;margin-left:10px">
    Train R² = <span id="viz3-tr" style="font-weight:bold;color:#0f766e">--</span>
    &nbsp;|&nbsp;
    Test R² = <span id="viz3-te" style="font-weight:bold;color:#dc2626">--</span>
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
    var TRAIN = [], TEST = [];
    function gen() {
      TRAIN = []; TEST = [];
      function f(x) { return Math.sin(1.2 * x) + 0.3 * x; }
      for (var i = 0; i < 20; i++) {
        var x = -3 + 6 * Math.random();
        TRAIN.push([x, f(x) + 0.35 * randn()]);
      }
      for (var j = 0; j < 100; j++) {
        var x2 = -3 + 6 * Math.random();
        TEST.push([x2, f(x2) + 0.35 * randn()]);
      }
    }
    gen();
    // Polynomial fit via normal equation
    function fit(data, deg) {
      var n = data.length, p = deg + 1;
      // Build X (n x p) and y (n)
      var XtX = [];
      for (var i = 0; i < p; i++) { var row = []; for (var j = 0; j < p; j++) row.push(0); XtX.push(row); }
      var Xty = []; for (var k = 0; k < p; k++) Xty.push(0);
      for (var d = 0; d < n; d++) {
        var feat = [];
        for (var e = 0; e < p; e++) feat.push(Math.pow(data[d][0], e));
        for (var a = 0; a < p; a++) {
          for (var b = 0; b < p; b++) XtX[a][b] += feat[a] * feat[b];
          Xty[a] += feat[a] * data[d][1];
        }
      }
      // Add tiny regularization for numerical stability (very small)
      for (var r = 0; r < p; r++) XtX[r][r] += 1e-8;
      // Solve via Gaussian elimination
      for (var col = 0; col < p; col++) {
        var maxRow = col;
        for (var rr = col + 1; rr < p; rr++)
          if (Math.abs(XtX[rr][col]) > Math.abs(XtX[maxRow][col])) maxRow = rr;
        var tmp = XtX[col]; XtX[col] = XtX[maxRow]; XtX[maxRow] = tmp;
        var tmp2 = Xty[col]; Xty[col] = Xty[maxRow]; Xty[maxRow] = tmp2;
        for (var rr2 = col + 1; rr2 < p; rr2++) {
          var factor = XtX[rr2][col] / XtX[col][col];
          for (var cc = col; cc < p; cc++) XtX[rr2][cc] -= factor * XtX[col][cc];
          Xty[rr2] -= factor * Xty[col];
        }
      }
      var w = new Array(p).fill(0);
      for (var i2 = p - 1; i2 >= 0; i2--) {
        var sum = Xty[i2];
        for (var j2 = i2 + 1; j2 < p; j2++) sum -= XtX[i2][j2] * w[j2];
        w[i2] = sum / XtX[i2][i2];
      }
      return w;
    }
    function pred(w, x) {
      var s = 0;
      for (var i = 0; i < w.length; i++) s += w[i] * Math.pow(x, i);
      return s;
    }
    function r2(w, data) {
      var meanY = data.reduce(function (s, p) { return s + p[1]; }, 0) / data.length;
      var ssr = 0, sst = 0;
      for (var i = 0; i < data.length; i++) {
        var pr = pred(w, data[i][0]);
        ssr += (data[i][1] - pr) * (data[i][1] - pr);
        sst += (data[i][1] - meanY) * (data[i][1] - meanY);
      }
      return 1 - ssr / sst;
    }
    function plot(deg) {
      var w = fit(TRAIN, deg);
      var xs = [], ys = [];
      for (var x = -3.5; x <= 3.5; x += 0.05) { xs.push(x); ys.push(pred(w, x)); }
      return {
        traces: [
          { x: xs, y: ys, mode: 'lines', name: 'fitted polynomial',
            line: { color: '#dc2626', width: 3 } },
          { x: TRAIN.map(function (p) { return p[0]; }),
            y: TRAIN.map(function (p) { return p[1]; }),
            mode: 'markers', name: 'train',
            marker: { color: '#1e40af', size: 10, line: { color: '#fff', width: 1 } } },
          { x: TEST.map(function (p) { return p[0]; }),
            y: TEST.map(function (p) { return p[1]; }),
            mode: 'markers', name: 'test',
            marker: { color: '#0f766e', size: 5, opacity: 0.45 } }
        ],
        trainR2: r2(w, TRAIN),
        testR2: r2(w, TEST)
      };
    }
    var layout = {
      xaxis: { title: 'x', range: [-3.5, 3.5] },
      yaxis: { title: 'y', range: [-3, 4] },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    var d = plot(3);
    Plotly.newPlot('viz3', d.traces, layout, { responsive: true, displayModeBar: false });
    document.getElementById('viz3-tr').textContent = d.trainR2.toFixed(3);
    document.getElementById('viz3-te').textContent = d.testR2.toFixed(3);
    function render() {
      var deg = parseInt(document.getElementById('viz3-d-slider').value);
      document.getElementById('viz3-d').textContent = deg;
      var d = plot(deg);
      document.getElementById('viz3-tr').textContent = d.trainR2.toFixed(3);
      document.getElementById('viz3-te').textContent = d.testR2.toFixed(3);
      Plotly.react('viz3', d.traces, layout);
    }
    document.getElementById('viz3-d-slider').addEventListener('input', render);
    document.getElementById('viz3-new').addEventListener('click', function () { gen(); render(); });
  }
  init();
})();
</script>

> **សង្កេត​ស្នូល៖**
> - **degree 1** — underfit (R² ​​ទាប​​​ទាំង train ​​ហើយ test)
> - **degree 3–5** — sweet spot, ​​R² ​ល្អ​​ទាំង​ពីរ
> - **degree 12+** — **overfit**: train R² → 1.0 ​តែ test R² ​ដួល​ខ្លាំង (ខ្លះ​ជា​​ slope ច្រាស​​!)
>
> ​នេះ​​​ជា​​ motivation ​សម្រាប់ Ridge regression (មេរៀន​ 8) ​ដែល​​ប្រើ regularization (= MAP, ​មេរៀន​ 4) ​ដើម្បី​ការ​ពារ overfit។

---

# ឧទាហរណ៍

**ឧទាហរណ៍ ១៖ ​ដោះ​ស្រាយ​ដោយ​ដៃ​ (1D)**

ឱ្យ​ទិន្នន័យ៖

| $x$ | 1 | 2 | 3 | 4 | 5 |
| $y$ | 2 | 4 | 5 | 4 | 5 |

​គណនា slope ​និង intercept ​តាម​រូបមន្ត​ស្តង់​ដារ៖

$$
w = \frac{n \sum x_i y_i - (\sum x_i)(\sum y_i)}{n \sum x_i^2 - (\sum x_i)^2}, \quad b = \bar y - w \bar x
$$

​គណនា៖
- $\sum x = 15, \sum y = 20, \sum xy = 65, \sum x^2 = 55, n = 5$
- $w = (5 \cdot 65 - 15 \cdot 20) / (5 \cdot 55 - 225) = (325 - 300) / (275 - 225) = 25 / 50 = 0.5$
- $b = 4 - 0.5 \cdot 3 = 2.5$

**Model៖** $\hat y = 0.5 x + 2.5$

**ឧទាហរណ៍ ២៖ PP house price (multi-feature)**

​ឧបមា​យើង​​មាន features៖
- $x_1$ = sqm (square meters)
- $x_2$ = age (​ឆ្នាំ)
- $x_3$ = ​ខណ្ឌ Daun Penh (1 ​ឬ 0)

​ក្រោយ​ training ​លើ 500 ​ផ្ទះ​៖

$$
\hat y = 1{,}200 \cdot \text{sqm} - 800 \cdot \text{age} + 25{,}000 \cdot \text{DP} + 15{,}000
$$

​ការ​បកស្រាយ៖
- ​បន្ថែម 1 sqm → តម្លៃ​ឡើង \$1,200
- ​បន្ថែម 1 ​ឆ្នាំ​អាយុ → តម្លៃ​ដួល \$800
- ​នៅ Daun Penh → តម្លៃ​ឡើង \$25,000 ​​​ប្រសើរ​​​​ជាង​ខណ្ឌ baseline
- ​ផ្ទះ​ 0 sqm, 0 ឆ្នាំ, ​មិន​នៅ DP → \$15,000 (មិន​មាន​ន័យ​ផ្ទាល់ — ​​​ត្រូវ​ប្រើ​ការ​បកស្រាយ​ក្នុង range ​ទិន្នន័យ)

---

# កូដ Python

## Implementation ​ដោយ​ដៃ​ (normal equation)

```python
import numpy as np

# Generate data
np.random.seed(42)
n = 100
X = np.random.randn(n, 3)
true_w = np.array([1.5, -2.0, 0.8])
y = X @ true_w + 1.0 + 0.5 * np.random.randn(n)

# Add bias column (intercept absorbed into w)
X_aug = np.hstack([np.ones((n, 1)), X])

# Normal equation: w = (X^T X)^-1 X^T y
w = np.linalg.inv(X_aug.T @ X_aug) @ X_aug.T @ y
print('Intercept:', w[0])     # ≈ 1.0
print('Weights  :', w[1:])    # ≈ [1.5, -2.0, 0.8]
```

## Implementation ​ដោយ Gradient descent

```python
def gradient_descent(X, y, lr=0.01, n_iter=1000):
    n, d = X.shape
    w = np.zeros(d)
    history = []
    for t in range(n_iter):
        y_hat = X @ w
        grad = -2/n * X.T @ (y - y_hat)
        w -= lr * grad
        history.append(np.mean((y - y_hat) ** 2))
    return w, history

w_gd, losses = gradient_descent(X_aug, y, lr=0.05, n_iter=500)
print('GD result:', w_gd)
```

## ​ប្រើ scikit-learn

```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

model = LinearRegression().fit(X, y)
y_pred = model.predict(X)

print('Intercept :', model.intercept_)
print('Coef      :', model.coef_)
print('R²        :', r2_score(y, y_pred))
print('RMSE      :', np.sqrt(mean_squared_error(y, y_pred)))
```

## Polynomial regression

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline

poly = PolynomialFeatures(degree=3, include_bias=False)
pipe = Pipeline([
    ('poly', poly),
    ('linreg', LinearRegression()),
])
pipe.fit(X, y)
print('Train R²:', pipe.score(X, y))
```

## PP house price ​ឧទាហរណ៍​

```python
import pandas as pd

# Synthetic Phnom Penh house dataset
n = 500
sqm = np.random.uniform(40, 300, n)
age = np.random.randint(0, 30, n)
is_dp = np.random.binomial(1, 0.3, n)
price = 1200 * sqm - 800 * age + 25000 * is_dp + 15000 + 8000 * np.random.randn(n)

df = pd.DataFrame({'sqm': sqm, 'age': age, 'is_dp': is_dp, 'price': price})

X = df[['sqm', 'age', 'is_dp']]
y = df['price']
model = LinearRegression().fit(X, y)

print(f'Intercept: \${model.intercept_:,.0f}')
for name, coef in zip(X.columns, model.coef_):
    print(f'{name}: \${coef:,.2f}')
print(f'R²: {model.score(X, y):.3f}')
```

---

# ការ​អនុវត្តន៍​ជាក់​ស្ដែង

## ​ការ​បកស្រាយ coefficients

​ក្នុង​ប្រព័ន្ធ​ប្រាក់/​ការ​ងារ — ​ច្រើន​ដង​ការ​បកស្រាយ​សំខាន់​ជាង​ការ​ព្យាករ៖

- **AMK loan**៖ "ពិន្ទុ​ប្រវត្តិ​ឥណទាន​បន្ថែម 100 ​ផ្ដល់ chance approval ​បន្ថែម​ 12%" — អាច​ប្រាប់​អតិថិជន​ច្បាស់
- **PP house price**៖ "​នៅ​ខណ្ឌ Daun Penh ​​បន្ថែម \$25,000" — ​ផ្តល់​អនុសាសន៍​​ ​ដល់​អ្នក​ទិញ​ផ្ទះ
- **Crop yield**៖ "1 mm rainfall ​បន្ថែម → 0.3 kg/ha yield" — ​ដាក់​ផែន​ការ​ឱ្យ​​​សត្វ​ស្រែ
- **Wing churn**៖ "​ការ​ការ​ប្រតិបត្តិការ​លើ 30 ​ថ្ងៃ​មុន ​បន្ថយ chance churn 8%" — ​ផ្ដោត retention campaign

​**ច្បាប់​​ ត្រូវ​​ប្រយ័ត្ន​៖**

1. **Coefficient​ ​អាស្រ័យ​លើ scale នៃ feature** — ​បើ standardize ​មុន ​coefficient ​មាន scale ​ដូច​គ្នា ​ហើយ​អាច​ប្រៀប​ធៀប​ជា​ "សារៈ​សំខាន់"
2. **Multicollinearity** ​ធ្វើ​ឱ្យ coefficient ​មិន​ស្ថិត​ស្ថេរ — ​សាក assess `np.linalg.cond(X.T @ X)` ​មុន
3. **​ការ​បកស្រាយ ​"causal" ត្រូវ​ការ​ការ​សិក្សា​ផ្សេង** — linear regression ​បាន​ correlation, ​មិន​មែន causation
4. **​ត្រូវ​ផ្ទៀង​ផ្ទាត់​ assumptions**: linearity, ​noise Gaussian, ​​homoscedasticity, independence

## ​ការ​ផ្ទៀង​ផ្ទាត់ assumptions

​មាន 4 ​ឧបករណ៍​មាស៖

1. **Residual plot** ($\hat y$ vs $y - \hat y$) — ​ត្រូវ​ random scatter ជុំ​វិញ 0; ​​​មាន pattern → linearity ​ខូច
2. **Q-Q plot** — ​ត្រូវ​ near-diagonal; ​មាន curve → ​noise ​​មិន Gaussian
3. **Scale-location plot** — ​ត្រូវ horizontal; ​មាន​ funnel → heteroscedasticity
4. **Variance Inflation Factor (VIF)** — VIF > 10 → multicollinearity ​ខ្លាំង

---

# លំហាត់

### លំហាត់ 1 — ​ដោះ​ស្រាយ​ ​1D ​ដោយ​ដៃ

​ឱ្យ​ទិន្នន័យ៖

| $x$ | 0 | 1 | 2 | 3 | 4 |
| $y$ | 1 | 3 | 7 | 13 | 21 |

(a) ​គណនា $w$ និង $b$ ​ដោយ​ប្រើ formula 1D<br>
(b) ​គណនា R²<br>
(c) ​តើ linear regression ​សម​ឬ​ទេ​សម្រាប់​ទិន្នន័យ​នេះ?

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**(a)** គណនា៖
- $n = 5, \sum x = 10, \sum y = 45, \sum xy = 130, \sum x^2 = 30$
- $\bar x = 2, \bar y = 9$

$$
w = \frac{n \sum xy - \sum x \sum y}{n \sum x^2 - (\sum x)^2} = \frac{5 \cdot 130 - 10 \cdot 45}{5 \cdot 30 - 100} = \frac{200}{50} = 5
$$

$$
b = \bar y - w \bar x = 9 - 5 \cdot 2 = -1
$$

**Model៖** $\hat y = 5x - 1$

**(b)** ​គណនា SS:
- ​​​ការ​ព្យាករ​៖ $\hat y = \{-1, 4, 9, 14, 19\}$
- Residual²: $\{4, 1, 4, 1, 4\}$ → $\text{SS}_{\text{res}} = 14$
- $\text{SS}_{\text{tot}} = \sum (y - 9)^2 = 64 + 36 + 4 + 16 + 144 = 264$

$$
R^2 = 1 - \frac{14}{264} \approx 0.947
$$

**(c)** R² = 0.947 ​​ខ្ពស់​ — ​​​ប៉ុន្តែ​ residual pattern ​មាន​ V-shape (4, 1, 4, 1, 4)​ → ​​ទិន្នន័យ​ពិត​​​ប្រាហែល​ quadratic ($y = x^2 + 1$)។ Linear ​ប្រហែល​ "​​​​ប្រ​សើរ​​បាន" ​​ប៉ុន្តែ polynomial degree 2 ​​​​​​នឹង​​ល្អ​ជាង — sample size តូច (n=5) ​ត្រូវ​ប្រយ័ត្ន overfit។

</details>

### លំហាត់ 2 — ​​​ការ​​ដោះ​ស្រាយ Gradient descent

ឱ្យ loss $L(w) = (w - 3)^2$. ​ចាប់​ផ្តើម $w = 0$, $\alpha = 0.2$. ​​​​​​​​​គណនា $w$ ​បន្ទាប់​ 3 steps។

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

Gradient: $\dfrac{dL}{dw} = 2(w - 3)$

**Step 1:** $w_0 = 0$, $\nabla = 2(0 - 3) = -6$

$$
w_1 = 0 - 0.2 \cdot (-6) = 1.2
$$

**Step 2:** $\nabla = 2(1.2 - 3) = -3.6$

$$
w_2 = 1.2 - 0.2 \cdot (-3.6) = 1.92
$$

**Step 3:** $\nabla = 2(1.92 - 3) = -2.16$

$$
w_3 = 1.92 - 0.2 \cdot (-2.16) = 2.352
$$

**សេចក្តី​សន្និដ្ឋាន​៖** $w$ ​​ត្រូវ​ខិត​ជិត $w^* = 3$ ​​​​​​​​​​បន្តិច​ម្តង​ៗ​​ — convergence ​​ច្បាស់​​ ​ប៉ុន្តែ​យឺត។ ​បើ $\alpha = 1$ ​​​​​​​​​​នោះ $w_1 = 6$ → $w_2 = 0$ → oscillate ​ឥត​ឈប់!

</details>

### លំហាត់ 3 — ​ការ​បកស្រាយ R²

​អ្នក​ ​ដាក់​ linear regression ​​​​លើ​ ​​PP house price ​​​​បាន R² = 0.45 ​លើ test set។ ​​​ដៃ​ ​ស្នាក់​​អ្នក​​​អោះអាង​ថា "model ​នេះ​​​​​អន់​ខ្លាំង" ​ហើយ​​​​​ត្រូវ​បោះ​បង់ — តើ​អ្នក​យល់​​ស្រប?

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**​ការ​ឆ្លើយ​​ល្អ​ៗ​៖ ​មិន​អាស្រ័យ​ — ត្រូវ​មាន​​ បរិបទ​​ច្រើន**

1. **R² = 0.45 ​មាន​ន័យ​ថា 45% ​នៃ variance ​ក្នុង price ​ត្រូវ​​ ​ពន្យល់​ដោយ feature** — ​នៅ​សល់ 55% ​ដោយ​​​​​ហេតុ​មិន​មាន​ក្នុង feature
2. **​ដៃ​ ​មិន​ដឹង​ហេតុ​មិន​មាន​​​​​ក្នុង feature​​:** ​​​​​ការ​ឆ្ងាយ​ពី​ផ្សារ, ​ការ​មាន garage, ​​​​​​ការ​​ផ្តល់​ amenities, ​​​​លក្ខណៈ​ខាង​ក្នុង ... → ​ត្រូវ​ feature engineering ​ច្រើន​ជាង​នេះ
3. **​ការ​​​​​​​​​​បកស្រាយ R² ​អាស្រ័យ​លើ domain:**
   - Physics (lab measurements): R² < 0.95 ​​អន់
   - Economics/social: R² 0.3–0.5 ​​​​​​​​​​​​​​​​ល្មម​ល្អ
   - Real estate: R² 0.5–0.7 ​​​​​​​​ស្ដង់​ដារ​ល្អ
4. **ការ​ស្នើ:**
   - ​ប្រមូល features ​បន្ថែម​​ (location detail, building condition)
   - ​សាក polynomial/interaction features
   - ​សាក tree-based model (Random Forest, XGBoost) — ​​ច្រើន​ដង​ល្អ​ជាង​ linear ​លើ tabular data
   - ​ផ្ទៀង​ផ្ទាត់​ assumptions (residual plot, Q-Q plot)

**សេចក្តី​សន្និដ្ឋាន​៖** R² = 0.45 មិន​​មែន​​ "​​អន់" — ​​ត្រូវ​បន្ត feature engineering ​​ឬ​សាក algorithm ​ស្មុគ​ស្មាញ​ជាង។

</details>

### លំហាត់ 4 — Multicollinearity

​​​អ្នក​​​ដាក់ feature ខាង​ក្រោម​​​លើ AMK loan model៖

- $x_1$ = monthly income (USD)
- $x_2$ = annual income (USD) = $12 \cdot x_1$
- $x_3$ = years at current job

​តើ​មាន​បញ្ហា​ឬ​ទេ? ​​សរសេរ $X^\top X$ ​​​​​មាន​បញ្ហា​យ៉ាង​ណា?

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**មាន​បញ្ហា perfect multicollinearity​!**

$x_2 = 12 x_1$ → ​​​មាន​ linear dependence ​​​ត្រឹមត្រូវ​​​​​​​​​​​​​​​​​​​​​​​​​រវាង $x_1$ ​​និង $x_2$។

​លទ្ធផល៖
- column $x_1$ ​និង $x_2$ ​ក្នុង​ $X$ ​មាន linear dependence
- $X^\top X$ ​​​សារ​​ singular (determinant = 0)
- $(X^\top X)^{-1}$ ​​ មិន​មាន — normal equation ​​​បាក់
- ​​សូម្បី sklearn ​នឹង​​​បោះ warning ​ឬ​ ​ឆ្លើយ coefficient ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​មិន​ស្ថិត​ស្ថេរ

**ដំណោះស្រាយ​៖**

1. **​លុប feature ​មួយ** — ​​យក​តែ $x_1$ ​ឬ​តែ $x_2$ ​(ហ្គឺ​មណ៍​​ដ៏​សាមញ្ញ​បំផុត)
2. **Ridge regression** (មេរៀន 8) — ​​បន្ថែម regularization ​ដោះ​ស្រាយ singular matrix
3. **PCA** — ​​​​ផ្ដៅ​​ ​feature ​ដែល​ផ្ដោត​ direction ​ឯករាជ្យ

**​ឧទាហរណ៍​ច្រើន​ដង​ក្នុង​ឧស្សាហកម្ម​​​៖** "income/month" + "income/year", "height_cm" + "height_inch", "​​សីតុណ្ហភាព °C" + "°F" — ​ត្រូវ​លុប​មួយ​​ ​មុន​បំពេញ model។

</details>

---

**​មេរៀន​​​​​​​​​បន្ទាប់ (ជំពូក 8):** Overfitting and Regularization — ​​​​​​យើង​​​ឃើញ​ overfit ​ហើយ​ក្នុង​ viz 3 ​នៃ​មេរៀន​នេះ​​។ មេរៀន​ក្រោយ​​​បង្ហាញ​ Ridge (L2), Lasso (L1), Elastic Net, ​ការ cross-validation, ​​​ការ​​ភ្ជាប់​ MAP, ​និង bias-variance tradeoff។




