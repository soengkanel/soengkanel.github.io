---
layout: post
title: "[ML Khmer] ជំពូក 5: ប្រភេទ​នៃ Machine Learning"
date: 2026-06-24 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, overview, supervised, unsupervised, reinforcement, interactive]
thumbnail: /images/ml-series/ch05-ml-categories.svg
---

យើង​បាន​បញ្ចប់​ស្នូល​គណិតវិទ្យា — ​ពិជគណិត​លីនេអ៊ែរ, កាល់គុលម៉ាទ្រីស, ប្រូបាប៊ីលីតេ, និង MLE/MAP។ ​ឥឡូវ​នេះ​ជា​ការ​ចាប់​ផ្ដើម **ផ្នែក II** ​នៃ​សៀវភៅ៖ ​ការ​​ផ្ដោត​លើ algorithm និង​បញ្ហា ML ​ពិត​ប្រាកដ។ មុន​នឹង​ដោះស្រាយ​បញ្ហា​ណា​មួយ — ​អ្នក​​ត្រូវ​ដឹង​ថា​បញ្ហា​នោះ **ស្ថិត​ក្នុង​ប្រភេទ​ណា**៖ Supervised, Unsupervised, Reinforcement, ឬ Semi-supervised។ ​ការ​ជ្រើស​ប្រភេទ​ខុស — algorithm ​ខុស, ​ការ​វាយ​តម្លៃ​ខុស, ​លទ្ធផល​ខុស។ មាន **រូបភាព interactive ៣**​៖ supervised classification ​ដែល​អ្នក​ប្ដូរ decision boundary, K-means clustering លើ​​ទីតាំង​ខេត្ត​នៅ​កម្ពុជា, និង problem chooser ​ដែល​ណែ​នាំ​ប្រភេទ ML ​ត្រូវ​នឹង​បញ្ហា​អ្នក។

---

# សង្ខេប

- **Supervised learning**៖ ​មាន​ទាំង input $X$ ​និង label $y$ — រៀន​ផែនទី $f: X \to y$
- **Unsupervised learning**៖ ​មាន​តែ $X$ — រក​រចនាសម្ព័ន្ធ​ឬ​លំនាំ​ដោយ​មិន​មាន​ការ​ណែ​នាំ
- **Reinforcement learning**៖ agent ​អន្តរ​ប្រតិបត្តិ​ជាមួយ environment ​ដើម្បី​ទទួល​បាន​ reward ​ច្រើន​បំផុត
- **Semi-supervised**៖ ​មាន label ​តិច + ​ទិន្នន័យ​មិន​ដាក់ label ​ច្រើន — ​ប្រើ​ទាំង​ពីរ
- **Self-supervised**៖ ​ប្រើ​ទិន្នន័យ​ដោយ​ខ្លួន​ឯង​ដើម្បី​បង្កើត label (eg. GPT, BERT)
- ​ការ​ជ្រើស​ប្រភេទ​ត្រឹមត្រូវ ​ផ្តើម​ដោយ​សួរ​​​សំណួរ​មួយ៖ **"តើ​អ្នក​មាន​ទិន្នន័យ​អ្វី?"**

---

# ហេតុអ្វីសំខាន់?

ការ​ដាក់​ប្រភេទ​បញ្ហា​មិន​ត្រឹមត្រូវ​​ជា​បញ្ហា​ដ៏​ធំ​បំផុត​ដែល​អ្នក​ចាប់​ផ្ដើម ML ​ជួប​ប្រទះ៖

- ​អ្នក​ខ្លះ​ព្យាយាម​ប្រើ deep learning លើ​បញ្ហា​ដែល linear regression ​​គ្រប់​គ្រាន់ → ​ខ្ជះ​ខ្ជាយ​ពេល
- ​អ្នក​ខ្លះ​ប្រើ classification លើ​បញ្ហា​ដែល regression ​ត្រូវ → metrics ​ខុស​ទាំង​មូល
- ​អ្នក​ខ្លះ​ស្ទើរ​តែ​ដែល​ប្រើ supervised ​លើ​បញ្ហា​ដែល​មិន​មាន​ label → ​ខ្វល់​រក label ​ម៉ាន់ៗ
- ​អ្នក​ខ្លះ​ប្រើ RL ​លើ​បញ្ហា​ដែល supervised ​ល្អ​ជាង → ​ស្មុគស្មាញ​ហួស​ហេតុ

**ឧទាហរណ៍​ជាក់​ស្ដែង​នៅ​កម្ពុជា៖**

| បញ្ហា | ប្រភេទ​ត្រឹមត្រូវ | ​ប្រភេទ​ខុស​ដែល​មនុស្ស​ច្រើន​ជ្រើស |
|---|---|---|
| ​ព្យាករ​ការ default ឥណទាន (AMK) | Supervised classification | "Cluster អតិថិជន​" — ​ខុស​ដោយ​ឆ្លើយ​សំណួរ​ខុស |
| ​បែង​ចែក​អតិថិជន Wing ​ជា segment | Unsupervised clustering | "ព្យាករ segment" — ​មិន​មាន label segment ពិត |
| ​ណែ​នាំ​ភោជនីយ​ដ្ឋាន​ក្នុង Phnom Penh | Hybrid (collab + content) | "Classification ​ល្អ/​មិន​ល្អ" — ​បាត់​ការ​ផ្ទាល់​ខ្លួន |
| ​បង្កើន​ប្រសិទ្ធភាព tuktuk route | RL ឬ optimization | "Predict ​ល្បឿន" — ​មិន​ដោះស្រាយ​ការ​សម្រេច​ចិត្ត |

​ការ​ដឹង​ប្រភេទ​បាន​ឱ្យ​អ្នក៖
- ​ជ្រើស algorithm ​ត្រឹមត្រូវ​​មុន
- ​ដឹង metric ​ត្រឹមត្រូវ (accuracy, RMSE, silhouette score, reward)
- ​ដឹង​ទម្រង់​ទិន្នន័យ​ដែល​ត្រូវ​ប្រមូល

---

# ពាក្យបច្ចេកទេសថ្មី

| ខ្មែរ | English | កំណត់សម្គាល់ |
|---|---|---|
| ការ​រៀន​មាន​ការ​ត្រួត​ពិនិត្យ | supervised learning | $(x_i, y_i)$ pairs |
| ការ​រៀន​ឥត​ការ​ត្រួត​ពិនិត្យ | unsupervised learning | ​មាន​តែ $x_i$ |
| ការ​រៀន​ពង្រឹង | reinforcement learning (RL) | agent–environment–reward |
| ការ​រៀន​ពាក់​កណ្ដាល​ត្រួត​ពិនិត្យ | semi-supervised | label ​តិច + unlabeled ​ច្រើន |
| ការ​រៀន​ដោយ​ខ្លួន​ឯង​ត្រួត​ពិនិត្យ | self-supervised | label ​ពី​ទិន្នន័យ​ខ្លួន​ឯង |
| តំរែតំរង់ | regression | $y \in \mathbb{R}$ ​(តម្លៃ​បន្ត) |
| ការ​ចាត់​ថ្នាក់ | classification | $y \in \{1, \ldots, K\}$ |
| ការ​ដាក់​ក្រុម | clustering | រក​ក្រុម​ដោយ​មិន​មាន label |
| ​ការ​កាត់​បន្ថយ​វិមាត្រ | dimensionality reduction | $\mathbb{R}^d \to \mathbb{R}^k, k < d$ |
| Parametric | parametric model | ប៉ារ៉ាម៉ែត្រ​មាន​ចំនួន​កំណត់ |
| Non-parametric | non-parametric model | ប៉ារ៉ាម៉ែត្រ​ដុះ​តាម​ទិន្នន័យ |
| Online vs Batch | online vs batch | រៀន​ម្ដងៗ​ vs ​រៀន​ទាំង​មូល |

---

# គំនិតវិចារណញ្ញាណ

## Supervised = "សិស្ស​ដែល​មាន​សៀវភៅ​ចម្លើយ"

គ្រូ​ឱ្យ​លំហាត់ និង​ចម្លើយ​ត្រឹមត្រូវ។ សិស្ស​រៀន​​ផែនទី​ "សំណួរ → ចម្លើយ"។ ​ដល់​ការ​សាកល្បង — សិស្ស​ឃើញ​សំណួរ​ថ្មី​ហើយ​ត្រូវ​​ឆ្លើយ​ដោយ​មិន​ឃើញ​ចម្លើយ។

​**ឧទាហរណ៍៖** ​បង្ហាញ​រូប 1,000 ​សន្លឹក ​មាន label "ឆ្កែ" ​ឬ "ឆ្មា" → model រៀន → ​បង្ហាញ​រូប​ថ្មី → model ​ព្យាករ "ឆ្កែ"។

## Unsupervised = "អ្នក​ស្រាវ​ជ្រាវ​ក្នុង​ដី​ថ្មី"

មិន​មាន​ផែនទី, មិន​មាន​អ្នក​ណែ​នាំ — អ្នក​ស្រាវ​ជ្រាវ​ស្វែង​រក​លំនាំ​ដោយ​ខ្លួន​ឯង។ "​មាន​ប្រភេទ​រូក្ខជាតិ​ប៉ុន្មាន​ក្នុង​តំបន់​នេះ? តើ​ពួក​វា​ប្រមូល​ផ្ដុំ​នៅ​ទីណា?"

**ឧទាហរណ៍៖** Wing ​មាន​ទិន្នន័យ​ការ​ប្រើ​ប្រាស់ 10,000 ​អតិថិជន — ​មិន​មាន label "premium" ឬ "casual" — ​តែ​ KMeans ​អាច​រក​ឃើញ​​ 3 ​ក្រុម​អតិថិជន​ដែល​មាន​លំនាំ​ស្រដៀង​គ្នា។

## Reinforcement = "​ការ​លេង​​ហ្គេម"

កុមារ​លេង Mario មិន​ស្គាល់​ច្បាប់ — ​សាក​​​​លោត, ​​ចា​យ, រត់; ​ពេល​ Mario ​ស្លាប់ → ​​ដឹង​ថា​អ្វី​ខុស; ​ពេល​ឈ្នះ​ stage → ​ដឹង​ថា​អ្វី​ត្រូវ។ បន្ទាប់​ពី​លេង​ច្រើន​ដង — ​កុមារ​ឆ្លាត​ឡើង​​។

**ឧទាហរណ៍៖** Smart Grab driver-routing ​​ប្រើ RL ​ដើម្បី​រៀន​ផ្លូវ​ដែល​ល្អ​បំផុត​ដោយ​ផ្អែក​លើ​ចរាចរណ៍​ពិត​ប្រាកដ​ និង​ការ​ទារ​លុយ​ពី​អតិថិជន។

## Semi/Self-supervised = "​សៀវភៅ​ចម្លើយ​​មាន​តែ​ខ្លះ"

គ្រូ​ឱ្យ​លំហាត់ 1,000 ​បញ្ហា — ​មាន​ចម្លើយ​តែ 50 ​ប៉ុណ្ណោះ។ ​សិស្ស​ត្រូវ​ប្រើ​ទាំង​ការ​ត្រួត​ពិនិត្យ និង​ការ​ស្រាវ​ជ្រាវ​ខ្លួន​ឯង។

**ឧទាហរណ៍៖** GPT ​រៀន​ភាសា​ដោយ​បំពេញ​ពាក្យ​ដែល​បាត់​ក្នុង​ប្រយោគ (self-supervised) — ​មិន​ត្រូវ​ការ label មនុស្ស​ដាក់​ឱ្យ​ផ្ទាល់។

---

# និយមន័យ និងគណិតវិទ្យា

## ១. Supervised Learning

**ការ​ដាក់​ឆ្នុក​ផ្លូវការ៖** ​ឱ្យ training set $D = \{(x_1, y_1), \ldots, (x_n, y_n)\}$ ​ដែល $x_i \in \mathcal{X}$ និង $y_i \in \mathcal{Y}$។ ​គោល​ដៅ៖ ​រៀន​មុខងារ $f: \mathcal{X} \to \mathcal{Y}$ ​ដែល​ប៉ាន់​ប្រមាណ $y$ ​សម្រាប់ $x$ ​ថ្មី។

​ផ្នែក​រង​ពីរ៖
- **Regression**៖ $\mathcal{Y} = \mathbb{R}$ — ​តម្លៃ​បន្ត (eg. តម្លៃ​ដី, ល្បឿន, ប្រាក់​ចំណូល)
- **Classification**៖ $\mathcal{Y} = \{1, 2, \ldots, K\}$ — ​ថ្នាក់​​​​​កំណត់ (eg. spam/ham, ​ឆ្កែ/ឆ្មា/ត្រី)

**Loss function** ​ស្តង់​ដារ៖

$$
\text{Regression: } L(f) = \frac{1}{n} \sum_{i=1}^n (y_i - f(x_i))^2 \quad (\text{MSE})
$$

$$
\text{Classification: } L(f) = -\frac{1}{n} \sum_{i=1}^n \log P(y_i \mid x_i; f) \quad (\text{cross-entropy})
$$

## 🎮 រូបភាព interactive ១៖ Supervised classification ​ដែល​អ្នក​គ្រប់​គ្រង

ផ្លាស់ slider សម្រាប់ **complexity** នៃ decision boundary — ពី​ linear (degree 1) ​ដល់ polynomial degree 8។ ​សង្កេត​ហេតុ​ដែល​ complexity ​ខ្ពស់​ពេក → **overfit** (ខ្សែ​​ដែល​​ឆ្លង​ទិន្នន័យ​ training ​ល្អ​តែ​អាក្រក់​លើ​ទិន្នន័យ​ថ្មី)។

<div id="viz1" style="width:100%;max-width:800px;margin:0 auto;height:440px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  Polynomial degree = <span id="viz1-deg" style="font-weight:bold;color:#dc2626">3</span>
  <input id="viz1-deg-slider" type="range" min="1" max="8" step="1" value="3" style="width:50%;max-width:400px"><br>
  <button id="viz1-resample" style="margin-top:6px;padding:4px 14px;font-weight:600;cursor:pointer">🎲 ទិន្នន័យ​ថ្មី</button>
  &nbsp;&nbsp;
  <span style="font-size:1.05em">
    Train acc = <span id="viz1-train" style="font-weight:bold;color:#0f766e">--</span>
    &nbsp;|&nbsp;
    Test acc = <span id="viz1-test" style="font-weight:bold;color:#7c3aed">--</span>
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
      var n = 50, train = [], test = [];
      for (var i = 0; i < n; i++) {
        var r = 1.5 + 1.4 * Math.random();
        var t = 2 * Math.PI * Math.random();
        var label = Math.random() < 0.5 ? 0 : 1;
        var cx = label === 0 ? -1 : 1;
        var cy = label === 0 ? -0.5 : 0.5;
        var x = cx + r * Math.cos(t) * 0.8 + 0.4 * randn();
        var y = cy + r * Math.sin(t) * 0.8 + 0.4 * randn();
        train.push([x, y, label]);
      }
      for (var j = 0; j < 50; j++) {
        var r2 = 1.5 + 1.4 * Math.random();
        var t2 = 2 * Math.PI * Math.random();
        var label2 = Math.random() < 0.5 ? 0 : 1;
        var cx2 = label2 === 0 ? -1 : 1;
        var cy2 = label2 === 0 ? -0.5 : 0.5;
        var x2 = cx2 + r2 * Math.cos(t2) * 0.8 + 0.4 * randn();
        var y2 = cy2 + r2 * Math.sin(t2) * 0.8 + 0.4 * randn();
        test.push([x2, y2, label2]);
      }
      DATA = { train: train, test: test };
    }
    function features(x, y, deg) {
      var f = [1];
      for (var i = 1; i <= deg; i++)
        for (var j = 0; j <= i; j++)
          f.push(Math.pow(x, i - j) * Math.pow(y, j));
      return f;
    }
    function fit(train, deg) {
      // Logistic regression by gradient descent
      var d = features(0, 0, deg).length;
      var w = new Array(d).fill(0);
      var lr = 0.05;
      for (var it = 0; it < 800; it++) {
        var grad = new Array(d).fill(0);
        for (var k = 0; k < train.length; k++) {
          var f = features(train[k][0], train[k][1], deg);
          var z = 0;
          for (var p = 0; p < d; p++) z += w[p] * f[p];
          var pHat = 1 / (1 + Math.exp(-z));
          var err = pHat - train[k][2];
          for (var p2 = 0; p2 < d; p2++) grad[p2] += err * f[p2];
        }
        for (var p3 = 0; p3 < d; p3++) w[p3] -= lr * grad[p3] / train.length;
      }
      return w;
    }
    function predict(w, x, y, deg) {
      var f = features(x, y, deg);
      var z = 0;
      for (var p = 0; p < w.length; p++) z += w[p] * f[p];
      return 1 / (1 + Math.exp(-z));
    }
    function acc(w, data, deg) {
      var c = 0;
      for (var i = 0; i < data.length; i++) {
        var p = predict(w, data[i][0], data[i][1], deg) > 0.5 ? 1 : 0;
        if (p === data[i][2]) c++;
      }
      return c / data.length;
    }
    function plot(deg) {
      var w = fit(DATA.train, deg);
      var nGrid = 50;
      var xs = [], ys = [], zs = [];
      for (var i = 0; i <= nGrid; i++) xs.push(-4 + 8 * i / nGrid);
      for (var j = 0; j <= nGrid; j++) ys.push(-3 + 6 * j / nGrid);
      for (var j2 = 0; j2 <= nGrid; j2++) {
        var row = [];
        for (var i2 = 0; i2 <= nGrid; i2++) row.push(predict(w, xs[i2], ys[j2], deg));
        zs.push(row);
      }
      var trA = DATA.train.filter(function (p) { return p[2] === 0; });
      var trB = DATA.train.filter(function (p) { return p[2] === 1; });
      return {
        traces: [
          { x: xs, y: ys, z: zs, type: 'contour', name: 'P(class=1)',
            colorscale: [[0, '#dbeafe'], [0.5, '#ffffff'], [1, '#fee2e2']],
            contours: { start: 0, end: 1, size: 0.1, coloring: 'fill' },
            line: { width: 0 }, showscale: false, opacity: 0.85,
            hoverinfo: 'skip' },
          { x: xs, y: ys, z: zs, type: 'contour',
            contours: { start: 0.5, end: 0.5, coloring: 'lines' },
            line: { color: '#0f172a', width: 3 }, showscale: false,
            hoverinfo: 'skip', showlegend: false },
          { x: trA.map(function (p) { return p[0]; }),
            y: trA.map(function (p) { return p[1]; }),
            mode: 'markers', name: 'class 0',
            marker: { color: '#1e40af', size: 9, line: { color: '#fff', width: 1 } } },
          { x: trB.map(function (p) { return p[0]; }),
            y: trB.map(function (p) { return p[1]; }),
            mode: 'markers', name: 'class 1',
            marker: { color: '#dc2626', size: 9, line: { color: '#fff', width: 1 } } }
        ],
        train: acc(w, DATA.train, deg),
        test: acc(w, DATA.test, deg)
      };
    }
    var layout = {
      xaxis: { title: 'feature 1', range: [-4, 4] },
      yaxis: { title: 'feature 2', range: [-3, 3] },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    gen();
    var d = plot(3);
    Plotly.newPlot('viz1', d.traces, layout, { responsive: true, displayModeBar: false });
    document.getElementById('viz1-train').textContent = (d.train * 100).toFixed(1) + '%';
    document.getElementById('viz1-test').textContent = (d.test * 100).toFixed(1) + '%';
    function render() {
      var deg = parseInt(document.getElementById('viz1-deg-slider').value);
      document.getElementById('viz1-deg').textContent = deg;
      var d = plot(deg);
      document.getElementById('viz1-train').textContent = (d.train * 100).toFixed(1) + '%';
      document.getElementById('viz1-test').textContent = (d.test * 100).toFixed(1) + '%';
      Plotly.react('viz1', d.traces, layout);
    }
    document.getElementById('viz1-deg-slider').addEventListener('input', render);
    document.getElementById('viz1-resample').addEventListener('click', function () { gen(); render(); });
  }
  init();
})();
</script>

> **សង្កេត​សំខាន់៖** ​នៅ degree 1 (linear) — boundary ​ត្រង់, ​train acc ≈ test acc — ​ប្រហែល​ល្អ​បំផុត​ហើយ​សម្រាប់​ទិន្នន័យ​នេះ។ ​នៅ degree 8 — boundary ​​​បត់​ច្រើន, train acc ឡើង​​ខ្ពស់ ​ប៉ុន្តែ test acc ​ច្រើន​ដួល​ចុះ → **overfit**!

## ២. Unsupervised Learning

**ការ​ដាក់​ឆ្នុក៖** ​ឱ្យ $D = \{x_1, \ldots, x_n\}$ ​ដោយ​មិន​មាន labels។ ​គោល​ដៅ​ខុស​ៗ​គ្នា៖

| ​ផ្នែក​រង | គោល​ដៅ | ​​ឧទាហរណ៍ algorithm |
|---|---|---|
| Clustering | រក​ក្រុម​ស្រដៀង​គ្នា | K-Means, DBSCAN, GMM |
| ​ការ​កាត់​បន្ថយ​វិមាត្រ | ​សង្ខេប $x \in \mathbb{R}^d$ ​ទៅ $\mathbb{R}^k$ | PCA, t-SNE, UMAP |
| Density estimation | រៀន $P(x)$ | KDE, GMM, normalizing flow |
| Anomaly detection | រក​ចំណុច​ "ខុស​ធម្មតា" | Isolation Forest, Autoencoder |

## 🎮 រូបភាព interactive ២៖ K-Means clustering ​លើ​​ទីតាំង​ប្រទេស​កម្ពុជា

​ឧបមា​យើង​មាន​ទីតាំង​ខេត្ត​ចម្បង​ៗ​នៅ​កម្ពុជា និង​ចង់​បែង​ចែក​ជា​ $K$ "​តំបន់​ប្រតិបត្តិការ" សម្រាប់​ការ​ដឹក​ជញ្ជូន។ ​ប្ដូរ slider សម្រាប់ $K$ — ​មើល​ centroids ​ផ្លាស់​ប្ដូរ។

<div id="viz2" style="width:100%;max-width:800px;margin:0 auto;height:480px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  K (ចំនួន​តំបន់) = <span id="viz2-k" style="font-weight:bold;color:#0f766e">3</span>
  <input id="viz2-k-slider" type="range" min="1" max="7" step="1" value="3" style="width:50%;max-width:400px"><br>
  <button id="viz2-rerun" style="margin-top:6px;padding:4px 14px;font-weight:600;cursor:pointer">🔁 រត់​ KMeans ​ម្តង​ទៀត</button>
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    // Approx (lon, lat) of major Cambodian provinces
    var PROVINCES = [
      { name: 'Phnom Penh', x: 104.92, y: 11.55 },
      { name: 'Siem Reap', x: 103.85, y: 13.36 },
      { name: 'Battambang', x: 103.20, y: 13.10 },
      { name: 'Sihanoukville', x: 103.52, y: 10.63 },
      { name: 'Kampong Cham', x: 105.45, y: 11.99 },
      { name: 'Kampot', x: 104.18, y: 10.62 },
      { name: 'Kandal', x: 104.95, y: 11.40 },
      { name: 'Pursat', x: 103.92, y: 12.53 },
      { name: 'Takeo', x: 104.78, y: 10.99 },
      { name: 'Banteay Meanchey', x: 103.00, y: 13.59 },
      { name: 'Kratie', x: 106.02, y: 12.48 },
      { name: 'Stung Treng', x: 105.97, y: 13.52 },
      { name: 'Ratanakiri', x: 106.99, y: 13.74 },
      { name: 'Mondulkiri', x: 107.20, y: 12.79 },
      { name: 'Kampong Speu', x: 104.54, y: 11.45 },
      { name: 'Kampong Thom', x: 104.89, y: 12.71 },
      { name: 'Preah Vihear', x: 104.98, y: 13.81 },
      { name: 'Svay Rieng', x: 105.80, y: 11.09 },
      { name: 'Prey Veng', x: 105.32, y: 11.49 },
      { name: 'Kep', x: 104.32, y: 10.48 },
      { name: 'Koh Kong', x: 103.50, y: 11.62 },
      { name: 'Oddar Meanchey', x: 103.55, y: 14.16 },
      { name: 'Tboung Khmum', x: 105.84, y: 11.89 }
    ];
    function kmeans(pts, K, maxIter) {
      // init: K-means++ style
      var centroids = [];
      centroids.push(pts[Math.floor(Math.random() * pts.length)]);
      while (centroids.length < K) {
        var dists = pts.map(function (p) {
          var min = Infinity;
          for (var c = 0; c < centroids.length; c++) {
            var d = (p.x - centroids[c].x) * (p.x - centroids[c].x) + (p.y - centroids[c].y) * (p.y - centroids[c].y);
            if (d < min) min = d;
          }
          return min;
        });
        var sum = dists.reduce(function (s, d) { return s + d; }, 0);
        var r = Math.random() * sum, acc = 0;
        for (var ii = 0; ii < pts.length; ii++) {
          acc += dists[ii];
          if (acc >= r) { centroids.push({ x: pts[ii].x, y: pts[ii].y }); break; }
        }
      }
      centroids = centroids.map(function (c) { return { x: c.x, y: c.y }; });
      var assign = new Array(pts.length).fill(0);
      for (var it = 0; it < maxIter; it++) {
        for (var i = 0; i < pts.length; i++) {
          var best = 0, bd = Infinity;
          for (var k = 0; k < K; k++) {
            var dd = (pts[i].x - centroids[k].x) * (pts[i].x - centroids[k].x) +
                     (pts[i].y - centroids[k].y) * (pts[i].y - centroids[k].y);
            if (dd < bd) { bd = dd; best = k; }
          }
          assign[i] = best;
        }
        var sums = [], counts = [];
        for (var k2 = 0; k2 < K; k2++) { sums.push({ x: 0, y: 0 }); counts.push(0); }
        for (var i2 = 0; i2 < pts.length; i2++) {
          sums[assign[i2]].x += pts[i2].x;
          sums[assign[i2]].y += pts[i2].y;
          counts[assign[i2]]++;
        }
        for (var k3 = 0; k3 < K; k3++) {
          if (counts[k3] > 0) {
            centroids[k3].x = sums[k3].x / counts[k3];
            centroids[k3].y = sums[k3].y / counts[k3];
          }
        }
      }
      return { centroids: centroids, assign: assign };
    }
    var palette = ['#1e40af', '#dc2626', '#0f766e', '#7c3aed', '#ea580c', '#be185d', '#0891b2'];
    function plot(K) {
      var res = kmeans(PROVINCES, K, 25);
      var traces = [];
      for (var k = 0; k < K; k++) {
        var xs = [], ys = [], txt = [];
        for (var i = 0; i < PROVINCES.length; i++) {
          if (res.assign[i] === k) {
            xs.push(PROVINCES[i].x); ys.push(PROVINCES[i].y); txt.push(PROVINCES[i].name);
          }
        }
        traces.push({
          x: xs, y: ys, mode: 'markers+text', name: 'តំបន់ ' + (k + 1),
          marker: { color: palette[k % palette.length], size: 14, line: { color: '#fff', width: 1.5 } },
          text: txt, textposition: 'top center',
          textfont: { size: 10, color: '#0f172a' }
        });
      }
      traces.push({
        x: res.centroids.map(function (c) { return c.x; }),
        y: res.centroids.map(function (c) { return c.y; }),
        mode: 'markers', name: 'centroid',
        marker: { color: '#0f172a', size: 22, symbol: 'x-thin', line: { color: '#0f172a', width: 4 } }
      });
      return traces;
    }
    var layout = {
      xaxis: { title: 'longitude', range: [102.5, 107.8] },
      yaxis: { title: 'latitude', range: [10.0, 14.5], scaleanchor: 'x', scaleratio: 1 },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 1.02, y: 1, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#f1f5f9', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    Plotly.newPlot('viz2', plot(3), layout, { responsive: true, displayModeBar: false });
    function render() {
      var K = parseInt(document.getElementById('viz2-k-slider').value);
      document.getElementById('viz2-k').textContent = K;
      Plotly.react('viz2', plot(K), layout);
    }
    document.getElementById('viz2-k-slider').addEventListener('input', render);
    document.getElementById('viz2-rerun').addEventListener('click', render);
  }
  init();
})();
</script>

> **សង្កេត៖** ​នៅ $K=3$ — ​ច្រើន​ឃើញ​ "​ភ្នំ​ពេញ + តំបន់​ខាង​ត្បូង", "​​ភាគ​ខាង​ជើង", "​ខាង​កើត"។ ​ប្ដូរ $K = 5, 6$ — ​ឃើញ​ភាព​លម្អិត​ច្រើន​ជាង​នេះ។ ​ការ​ "រត់​​ម្តង​ទៀត" ​អាច​ឱ្យ​លទ្ធផល​ខុស​បន្តិច — KMeans ​អាស្រ័យ​លើ​ការ​ផ្ដើម​ centroid (random init)។

## ៣. Reinforcement Learning

**ការ​ដាក់​ឆ្នុក៖** Markov Decision Process (MDP) ​ដែល​មាន៖
- State $s_t \in \mathcal{S}$
- Action $a_t \in \mathcal{A}$
- Reward $r_t \in \mathbb{R}$
- Transition $P(s_{t+1} \mid s_t, a_t)$

**គោល​ដៅ៖** ​រក policy $\pi: \mathcal{S} \to \mathcal{A}$ ​ដែល​ធ្វើ​ឱ្យ expected cumulative reward ​អតិបរមា៖

$$
\pi^* = \arg\max_\pi \mathbb{E}\!\left[\sum_{t=0}^{\infty} \gamma^t r_t \,\middle|\, \pi \right]
$$

ដោយ $\gamma \in [0, 1)$ ​ជា discount factor។

**ឧទាហរណ៍​ឧស្សាហកម្ម៖** AlphaGo, ChatGPT (RLHF), Smart Grab routing, Tesla autopilot។

## ៤. Semi-supervised & Self-supervised

**Semi-supervised**៖ ​ឱ្យ labeled set ​តូច $D_L$ + unlabeled set ​ធំ $D_U$:
- ​ប្រើ $D_U$ ​ដើម្បី​រៀន​រចនាសម្ព័ន្ធ​ទិន្នន័យ
- ​ប្រើ $D_L$ ​ដើម្បី​ កំណត់​​​ខ្សែ​ដែល​បំបែក​ថ្នាក់

**Self-supervised** (សំខាន់​បំផុត​ក្នុង​ LLM ​សម័យ​ថ្មី)៖
- ​បង្កើត label ​ពី​ទិន្នន័យ​ខ្លួន​ឯង
- ​ឧទាហរណ៍ Masked Language Model (BERT)៖ "​ខ្ញុំ​ស្រឡាញ់ [MASK]" → ​ព្យាករ "​អ្នក"
- ​ឧទាហរណ៍ Next-token prediction (GPT)៖ ​យក​ប្រយោគ → ​ព្យាករ​ពាក្យ​បន្ទាប់

## ៥. Parametric vs Non-parametric

| លក្ខណៈ | Parametric | Non-parametric |
|---|---|---|
| ​ចំនួន​ប៉ារ៉ាម៉ែត្រ | កំណត់ (មិន​ដុះ​តាម $n$) | ​ដុះ​តាម $n$ |
| ​ឧទាហរណ៍ | Linear regression, NN ​មាន​​ architecture ​កំណត់ | KNN, Decision Tree, Gaussian Process |
| ​​ហ្វឹក​ហាត់ | លឿន​ + memory ​តិច | ស្ទើរ​តែ​​ "​មិន​​ហ្វឹក​" — ​តែ inference យឺត |
| ​ការ​ផ្គូផ្គង​ទិន្នន័យ​ស្មុគស្មាញ | ​អាស្រ័យ​លើ​ architecture | ស្វ័យ​ប្រវត្តិ​ច្រើន​ជាង |

## ៦. Batch vs Online Learning

- **Batch**៖ ​ហ្វឹក​ហាត់​នៅ​ពេល​មាន​ទិន្នន័យ​ទាំង​អស់​ (sklearn ​ភាគ​ច្រើន)
- **Online / Streaming**៖ ​ទទួល​ទិន្នន័យ​ម្ដងៗ ​ហើយ​ update model ​ភ្លាមៗ (SGD, online K-Means, online RL)

​ឧស្សាហកម្ម​នៅ​កម្ពុជា ​ដែល​ត្រូវ online: ​fraud detection ABA (millisecond response), recommendation Wing, sensor monitoring ​​នៅ​​​សួន​ឧស្សាហកម្ម។

---

# ឧទាហរណ៍

## 🎮 រូបភាព interactive ៣៖ Problem chooser

ជ្រើស​បញ្ហា​ ML ​នៅ​កម្ពុជា​ — ​ឃើញ​ប្រភេទ​ត្រឹមត្រូវ​ និង​ហេតុ​ផល​ដែល​ផ្ដល់​អនុសាសន៍។

<div style="max-width:800px;margin:0 auto;font-family:system-ui,sans-serif">
  <select id="viz3-problem" style="width:100%;padding:10px;font-size:1em;border-radius:8px;border:2px solid #0f766e;font-weight:600">
    <option value="0">— ​ជ្រើស​បញ្ហា​ ML —</option>
    <option value="1">AMK ​ចង់​​ព្យាករ​ថា​អតិថិជន​នឹង default ឥណទាន​ឬ​ទេ</option>
    <option value="2">Wing ​ចង់​ដឹង​ថា​អតិថិជន​មាន​ប៉ុន្មាន​ប្រភេទ ​(មិន​ដឹង​ចំនួន)</option>
    <option value="3">Real-estate startup ​ចង់​ព្យាករ​តម្លៃ​ផ្ទះ​ក្នុង Phnom Penh</option>
    <option value="4">Khmer chatbot ​ចង់​រៀន​ឆ្លើយ​សំណួរ​ដោយ​មិន​មាន​ការ​សន្ទនា​ដាក់​​ស្លាក​​ច្រើន</option>
    <option value="5">Grab driver routing ​ដែល​ត្រូវ​បង្កើន​​ប្រាក់​ចំណូល​រយៈ​ពេល​យូរ</option>
    <option value="6">Khmer OCR ​ចង់​ស្គាល់​អក្សរ​ខ្មែរ​ក្នុង​រូប</option>
    <option value="7">​ការ​​​រក​អោយ​ឃើញ​ការ​បន្លំ ABA ​​​​​​ដែល​​មិន​ធ្លាប់​ឃើញ​ពី​មុន</option>
    <option value="8">Crop yield ​ព្យាករ​ពី​ផ្កាយ​រណប</option>
  </select>
  <div id="viz3-result" style="margin-top:14px;padding:18px;border-radius:10px;background:#f8fafc;border:2px solid #cbd5e1;min-height:120px">
    <em style="color:#64748b">ជ្រើស​បញ្ហា​ខាង​លើ ​ដើម្បី​ឃើញ​ការ​វិភាគ...</em>
  </div>
</div>

<script>
(function () {
  var answers = {
    '1': {
      type: 'Supervised — Classification',
      color: '#1e40af',
      data: 'ប្រវត្តិ​អតិថិជន (income, loan amount, repayment history) + label (default = 0/1)',
      why: '​អ្នក​មាន label ច្បាស់ ($y$ = default ​ឬ​មិន default) ហើយ $y \\in \\{0, 1\\}$ → classification។',
      algos: 'Logistic Regression, Random Forest, XGBoost',
      metric: 'AUC-ROC, Precision/Recall (default ​ជា rare class)'
    },
    '2': {
      type: 'Unsupervised — Clustering',
      color: '#7c3aed',
      data: 'លក្ខណៈ​ការ​ប្រើ​ប្រាស់ (avg amount, frequency, time of day, location) — គ្មាន label',
      why: '​មិន​មាន​ "ប្រភេទ​ត្រឹមត្រូវ" ​ដែល​បាន​ដឹង​​មុន។ ​ត្រូវ​រក​ក្រុម​ដោយ​ខ្លួន​ឯង → clustering។',
      algos: 'K-Means, GMM, DBSCAN',
      metric: 'Silhouette score, ​ការ​បកស្រាយ​អាជីវកម្ម (interpretability)'
    },
    '3': {
      type: 'Supervised — Regression',
      color: '#1e40af',
      data: 'លក្ខណៈ​ផ្ទះ (sqm, ​ខណ្ឌ, room count, ឆ្នាំ​សាង​សង់) + label (តម្លៃ​ជា​ដុល្លារ)',
      why: '$y$ ​ជា​តម្លៃ​បន្ត ($y \\in \\mathbb{R}^+$) → regression។',
      algos: 'Linear Regression, Gradient Boosting, Neural Net',
      metric: 'RMSE, MAE, MAPE'
    },
    '4': {
      type: 'Self-supervised + Fine-tuning',
      color: '#ea580c',
      data: 'Khmer text corpus ​ធំ (មិន​មាន label) + ​​​សន្ទនា​ខ្លះ​ដែល​មាន label',
      why: '​ការ​ដាក់ label ​សន្ទនា​ច្រើន​ខ្លាំង = ​ថ្លៃ​ខ្ពស់។ self-supervised pretraining លើ Khmer corpus ហើយ fine-tune​ លើ​​សន្ទនា​ដែល​មាន label។',
      algos: 'BERT/GPT pretraining → supervised fine-tuning',
      metric: 'BLEU, Perplexity, ​ការ​វាយ​តម្លៃ​មនុស្ស'
    },
    '5': {
      type: 'Reinforcement Learning',
      color: '#dc2626',
      data: 'State (location, time, traffic), Action (which trip to accept), Reward (income per hour)',
      why: '​ការ​សម្រេច​ចិត្ត​ជា sequence; reward មក​យឺត; ​បរិស្ថាន​ផ្លាស់​ប្ដូរ​ — supervised មិន​សម។',
      algos: 'Q-learning, PPO, ​Actor-Critic',
      metric: 'Cumulative reward, average income/hour'
    },
    '6': {
      type: 'Supervised — Classification',
      color: '#1e40af',
      data: 'រូប​អក្សរ ($x$) + label អក្សរ​ខ្មែរ ($y \\in \\{\\text{ក}, \\text{ខ}, \\text{គ}, \\ldots\\}$)',
      why: '$y$ ​ជា label ​​ដាច់​ខាត​ច្រើន​ថ្នាក់ → multi-class classification។',
      algos: 'CNN (ResNet, EfficientNet), Vision Transformer',
      metric: 'Accuracy, F1 per character, character error rate'
    },
    '7': {
      type: 'Unsupervised — Anomaly Detection',
      color: '#7c3aed',
      data: 'ការ​ប្រតិបត្តិការ ABA ​ធម្មតា​ (មិន​មាន label សម្រាប់​ការ​បន្លំ​ថ្មី)',
      why: '​ការ​បន្លំ​​ថ្មី​ៗ​មិន​ដែល​ឃើញ → ​មិន​អាច​បង្ហាត់​ supervised បាន។ ​ត្រូវ​រក​អ្វី​ "ខុស​ធម្មតា"។',
      algos: 'Isolation Forest, Autoencoder, One-Class SVM',
      metric: 'AUC, Precision@K (top K most-anomalous)'
    },
    '8': {
      type: 'Supervised — Regression',
      color: '#1e40af',
      data: 'រូប​ផ្កាយ​រណប (NDVI, ​អាកាស​ធាតុ) + label (ទិន្នផល​ស្រូវ ​kg/ha)',
      why: 'Yield ​​ជា​​តម្លៃ​បន្ត → regression។ ​ប្រសិន​បើ​ចង់​ព្យាករ "ល្អ/​មធ្យម/​អន់" → classification។',
      algos: 'CNN + tabular features → Gradient Boosting, U-Net',
      metric: 'RMSE, R²'
    }
  };
  document.getElementById('viz3-problem').addEventListener('change', function (e) {
    var v = e.target.value;
    var box = document.getElementById('viz3-result');
    if (v === '0') {
      box.innerHTML = '<em style="color:#64748b">​ជ្រើស​បញ្ហា​ខាង​លើ ​ដើម្បី​ឃើញ​ការ​វិភាគ...</em>';
      return;
    }
    var a = answers[v];
    box.innerHTML =
      '<div style="font-size:1.2em;font-weight:800;color:' + a.color + ';margin-bottom:10px">' + a.type + '</div>' +
      '<div style="margin:6px 0"><strong>ទិន្នន័យ​ដែល​ត្រូវ៖</strong> ' + a.data + '</div>' +
      '<div style="margin:6px 0"><strong>ហេតុ​ផល៖</strong> ' + a.why + '</div>' +
      '<div style="margin:6px 0"><strong>Algorithm ​ដែល​ស្នើ៖</strong> ' + a.algos + '</div>' +
      '<div style="margin:6px 0"><strong>Metric ត្រឹមត្រូវ៖</strong> ' + a.metric + '</div>';
    if (window.MathJax && window.MathJax.typesetPromise) window.MathJax.typesetPromise([box]);
  });
})();
</script>

> **គន្លឹះ៖** ​សួរ​ខ្លួន​ឯង​​​មុន​ជ្រើស algorithm — ​​​“តើ​ខ្ញុំ​មាន​​​​ label ឬ​ទេ?” → ​​បើ​មាន → supervised; ​បើ​មិន​​មាន → unsupervised ​ឬ self-supervised; ​បើ​ការ​សម្រេច​ចិត្ត​ឆ្លុះ​បញ្ចាំង reward → RL។

---

# កូដ Python

## Supervised classification

```python
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=200, n_features=4, n_classes=2)
clf = LogisticRegression().fit(X, y)
print('Accuracy:', clf.score(X, y))
print('P(class=1 | x):', clf.predict_proba(X[:3]))
```

## Supervised regression

```python
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression

X, y = make_regression(n_samples=200, n_features=4, noise=5)
reg = LinearRegression().fit(X, y)
print('R²:', reg.score(X, y))
```

## Unsupervised clustering

```python
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

X, _ = make_blobs(n_samples=300, centers=4)   # _: មិន​ប្រើ label
km = KMeans(n_clusters=4, n_init=10).fit(X)
print('Cluster assignments:', km.labels_[:10])
print('Centroids:', km.cluster_centers_)
```

## Dimensionality reduction

```python
from sklearn.decomposition import PCA

X_high = make_classification(n_samples=200, n_features=50)[0]
pca = PCA(n_components=2).fit(X_high)
X_2d = pca.transform(X_high)
print('Explained variance:', pca.explained_variance_ratio_)
```

## Reinforcement learning (minimal Q-learning)

```python
import numpy as np

# Tiny gridworld: 4 states (0,1,2,3), 2 actions (left, right)
# Reward only at state 3
Q = np.zeros((4, 2))
alpha, gamma, eps = 0.1, 0.9, 0.1

for episode in range(500):
    s = 0
    while s != 3:
        a = np.random.randint(2) if np.random.random() < eps else Q[s].argmax()
        s_next = max(0, min(3, s + (1 if a == 1 else -1)))
        r = 1.0 if s_next == 3 else 0.0
        Q[s, a] += alpha * (r + gamma * Q[s_next].max() - Q[s, a])
        s = s_next

print('Learned Q-table:'); print(Q)
```

---

# ការអនុវត្តន៍ជាក់ស្ដែង

## ​ផែនទី​ជ្រើស​ប្រភេទ​ ML

ស្ទើរ​តែ​គ្រប់​បញ្ហា​ ML ​ក្នុង​ឧស្សាហកម្ម​អាច​​ត្រូវ​បាន​​ជ្រើស​​ដោយ​ការ​សួរ​សំណួរ​ 3 ​ប៉ុណ្ណោះ៖

1. **​អ្នក​មាន label ​ច្បាស់?** → ​បើ​បាទ → ​សួរ ​សំណួរ 2; ​បើ​ទេ → ​សួរ ​សំណួរ 3
2. **Label ​ជា​លេខ​បន្ត ឬ​ប្រភេទ?** → ​បន្ត → **regression**; ប្រភេទ → **classification**
3. **​មាន​ការ​សម្រេច​ចិត្ត​​ដែល​ផ្ដល់ reward ឆ្ពោះ​អនាគត?** → ​បាទ → **RL**; ​ទេ → **clustering** ​ឬ **anomaly detection**

​ករណី​ពិសេស៖
- ​មាន label ​តិច + unlabeled ​ច្រើន → **semi-supervised**
- ​ទិន្នន័យ ​text/image/audio ​ធំ​ដោយ​មិន​មាន label → **self-supervised pretraining** ​​បន្ទាប់​មក fine-tune

## Metrics ​ដែល​ត្រូវ​​​ប្រើ​​​​ត្រូវ​នឹង​ប្រភេទ

| ប្រភេទ | Metrics ​ចម្បង |
|---|---|
| Regression | MSE, RMSE, MAE, R² |
| Binary classification | Accuracy, Precision, Recall, F1, AUC-ROC |
| Multi-class classification | Accuracy, Macro-F1, Confusion matrix |
| Clustering | Silhouette, Davies-Bouldin, ​ការ​បកស្រាយ​អាជីវកម្ម |
| Anomaly detection | Precision@K, AUC |
| RL | Cumulative reward, regret |

​ការ​​​ ​ដាក់​ metric ​ខុស = ​បាន​លេខ​ល្អ​តែ model ​មិន​ដោះស្រាយ​បញ្ហា​ពិត​ប្រាកដ។ ​ឧទាហរណ៍ accuracy ​លើ fraud detection ​ដែល 99.9% ​ប្រតិបត្តិការ​មិន​ជា fraud — ​​​model ​ដែល​ឆ្លើយ "​មិន​ជា fraud" ​ស្ទើរ​តែ 100% បាន​ 99.9% accuracy ​តែ​មិន​មាន​ប្រយោជន៍​ដាច់​ខាត។

---

# លំហាត់

### លំហាត់ 1 — ​ការ​បែង​ចែក​ប្រភេទ

​ដាក់​បញ្ហា​ខាង​ក្រោម​ទៅ​ប្រភេទ​ ML ​ត្រឹមត្រូវ៖

a) ​ព្យាករ​ល្បឿន​ខ្យល់​​ផ្ដោះ​ផ្ដាច់​នៅ Sihanoukville ​សម្រាប់​ការ​បិទ​ផ្លូវ<br>
b) រក​ក្រុម​​អ្នក​ប្រើ Telegram channel ​យក​​ការ​ផ្សាយ​ពាណិជ្ជកម្ម​ត្រូវ​ក្រុម<br>
c) Bonsai growth optimizer — ​ត្រូវ​​ស្រោច​ទឹក​ប៉ុនណា​ប្រ​ចាំ​ថ្ងៃ​ដើម្បី​​ការ​ដុះ​​ល្អ​បំផុត<br>
d) ​​ស្គាល់​ស្លាក​លេខ​ឡាន​ ​សម្រាប់​ប័ណ្ណ​ប្រាក់​ផ្លូវ<br>
e) Cambodia News Khmer chatbot — ​បាន​ corpus ​អត្ថបទ​ច្រើន​​​មិន​មាន label

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

| លំហាត់ | ប្រភេទ | ហេតុ​ផល |
|---|---|---|
| a | **Supervised regression** | $y$ = ល្បឿន (បន្ត, $\in \mathbb{R}^+$) |
| b | **Unsupervised clustering** | មិន​មាន​ "​ក្រុម​ត្រឹមត្រូវ" — រក​ដោយ​ខ្លួន​ឯង |
| c | **Reinforcement learning** | ​ការ​សម្រេច​ចិត្ត​ប្រ​ចាំ​ថ្ងៃ + reward (​ដុះ) មក​យឺត |
| d | **Supervised classification** | $y$ = តួ​អក្សរ ឬ​លេខ​ (កំណត់) |
| e | **Self-supervised** ​+ ​បន្ទាប់​​ដោយ task-specific fine-tuning | corpus ​ធំ​មិន​មាន label → pretraining ​ល្អ​បំផុត |

</details>

### លំហាត់ 2 — ​ការ​ជ្រើស metric

​អ្នក​បាន train classifier សម្រាប់​ការ​ស្គាល់​ COVID PCR ​ដែល​ 0.5% ​នៃ​អ្នក​ធ្វើ​តេស្ត​ឆ្លង​ពិត​ប្រាកដ។ Model A ​បាន accuracy 99.5%; Model B ​បាន accuracy 95% ​ប៉ុន្តែ recall លើ​ "ឆ្លង" = 95%។

(a) ​តើ Model ​មួយ​ណា​ល្អ​ជាង?<br>
(b) ​ហេតុ​អ្វី​ accuracy ​ខុស​សម្រាប់​បញ្ហា​នេះ?<br>
(c) Metric ​ណា​មួយ​ល្អ​ជាង​សម្រាប់​បរិបទ​នេះ?

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**(a)** **Model B** — ​សូម្បី​តែ accuracy ទាប​​ប៉ុន្តែ​​​​ catch ​អ្នក​ឆ្លង​ពិត​ប្រាកដ 95%។ Model A ​ប្រហែល​​​ "​ឆ្លើយ​មិន​ឆ្លង​គ្រប់​គ្នា" → 99.5% accuracy ​ដោយ​ "​សំណាង" ​ដោយ​សារ class imbalance។

**(b)** Class imbalance៖ ​បើ 99.5% ​នៃ​ករណី​ជា​ "​មិន​ឆ្លង" — model ​ដែល​ឆ្លើយ "​មិន​ឆ្លង" ​សម្រាប់​ទាំង​អស់​នឹង​បាន 99.5% accuracy ​ដោយ​មិន​ដឹង​អ្វី​សោះ។

**(c)** Metrics ​ល្អ​ជាង៖
- **Recall** ​លើ class "​ឆ្លង" — តើ​យើង​ catch ​អ្នក​ឆ្លង​ប៉ុនណា?
- **Precision** ​លើ​ class "​ឆ្លង" — ពេល​ model ​និយាយ "​ឆ្លង" — ​ត្រឹមត្រូវ​ប៉ុនណា?
- **F1** — balance ​រវាង recall ​និង precision
- **AUC-ROC** — independent ​ពី threshold ​ជ្រើស

**សេចក្តី​សន្និដ្ឋាន៖** ​នៅ​ medical screening — recall ​សំខាន់​ខ្លាំង​ (false negative ​ខ្លាំង​ហានិភ័យ​ជាង false positive)។

</details>

### លំហាត់ 3 — ​ការ​បកស្រាយ

​អ្នក​​ដែល​ចាប់​ផ្ដើម ML ​ប្រាប់​ថា​ "ខ្ញុំ​ចង់​ប្រើ KMeans ​ដើម្បី​​ព្យាករ​​​​ថា​​​អតិថិជន​ Wing ​ណា​​ខ្លះ​នឹង churn"។ ​អ្នក​ជា mentor — ​ស្នើ​ឱ្យ​គាត់​ផ្លាស់​ប្ដូរ​អ្វី? ​ហេតុ​អ្វី?

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**បញ្ហា៖** KMeans ​ជា unsupervised clustering — ​មិន​មែន​ supervised prediction។ ​ពាក្យ "​ព្យាករ churn" ​មាន​ន័យ​ថា​មាន label ​នៃ​ "​អតិថិជន​បាន churn / ​មិន​បាន churn"។

**ការ​​ស្នើ៖**

1. ​សួរ៖ "តើ​អ្នក​មាន​ទិន្នន័យ​ប្រវត្តិ​ដែល​ដឹង​ថា​អតិថិជន​មួយ​នោះ​បាន churn ​ឬ​ទេ?"
2. ​បើ​មាន → **Supervised classification** (Logistic Regression, Random Forest, XGBoost) ​ដោយ $y$ = churn (0/1)
3. ​បើ​មិន​មាន → ​ត្រូវ​បង្កើត label ​ដំបូង (eg. "​មិន​មាន​ការ​ប្រតិបត្តិការ > 30 ​ថ្ងៃ" = churn)
4. KMeans **អាច​នៅ​មាន​ប្រយោជន៍** ​ដើម្បី​​ដឹង​ប្រភេទ​អតិថិជន​ផ្សេងៗ​មុន​ build classifier — ​តែ​មិន​មែន​ជា​ឧបករណ៍​​​ព្យាករ​ដោយ​ផ្ទាល់

**មេរៀន​ស្នូល៖** ​អ្នក​ដែល​ចាប់​ផ្ដើម​ ML ​ច្រើន​ច្រឡំ "Clustering = ការ​បែង​ចែក​អតិថិជន​ជា​ប្រភេទ" ​ជាមួយ "Classification = ​ការ​ព្យាករ​ប្រភេទ​​​ដែល​ដឹង​ហើយ"។ ​ការ​ជ្រើស​ប្រភេទ​ត្រឹមត្រូវ​ជា​ជំហាន​ដំបូង​សំខាន់​បំផុត។

</details>

### លំហាត់ 4 — Parametric vs Non-parametric

ជ្រើស​ algorithm ​សម​បំផុត​ (parametric ​ឬ non-parametric) សម្រាប់​ស្ថានភាព​ខាង​ក្រោម៖

a) Real-time fraud detection — ​​​ត្រូវ​ inference < 10ms<br>
b) Medical diagnosis ​​ដែល​ត្រូវ​ការ​ការ​បកស្រាយ​ច្បាស់ៗ<br>
c) Small dataset (n = 50)<br>
d) Very large dataset (n = 10 million) ​​ដែល​ត្រូវ​ការ retrain ​ច្រើន​ដង

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

| លំហាត់ | ​ការ​ស្នើ | ​ហេតុ​ផល |
|---|---|---|
| a | **Parametric** (Logistic Regression, NN ​តូច) | Inference លឿន, memory ​តិច; KNN ​ត្រូវ​​ផ្ដៅ​ដោយ training set ​ទាំង​មូល → យឺត |
| b | ​មាន​ trade-off — **Decision Tree** (non-parametric, ​បកស្រាយ​ងាយ) ​ឬ **Linear Regression** (parametric, ​​ស្រួល​បកស្រាយ​​​​​​​​​​​​​​​coefficients) | ​ដឹង​ថា Random Forest ​ច្បាស់​ខ្លាំង​ប៉ុន្តែ​​​ harder to interpret |
| c | **Parametric** ​ឬ **simple non-parametric** (eg. KNN) | ​ទិន្នន័យ​តិច → ​ខ្លាច overfit; ​ប្រើ​ model ​សាមញ្ញ |
| d | **Parametric** (NN, Linear models) | ​ហ្វឹក​​​ច្រើន​ដង​លឿន; non-parametric ​​​ស្ទើរ​តែ "​មិន​ហ្វឹក" ​ប៉ុន្តែ inference ​ឡើង​ដោយ​ size | 

**ច្បាប់​​ផ្ទាល់​មាត់៖** Parametric = "​ហ្វឹក​យូរ, inference លឿន"; Non-parametric = "​ហ្វឹក​លឿន, inference យឺត"។

</details>

---

**មេរៀន​បន្ទាប់ (ជំពូក 6):** Feature engineering — ​​ការ​បំប្លែង​ទិន្នន័យ​ដើម​ទៅ​ feature ​ដែល​ algorithm ​យល់​បាន​ល្អ។ យើង​នឹង​មើល one-hot encoding, scaling, log transformation, polynomial features, ​និង feature crosses — ​ដោយ​ឧទាហរណ៍​ពី Khmer text, ​តម្លៃ​ផ្ទះ Phnom Penh, និង AMK loan data។
