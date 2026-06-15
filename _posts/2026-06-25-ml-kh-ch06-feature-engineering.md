---
layout: post
title: "[ML Khmer] ជំពូក 6: Feature Engineering"
date: 2026-06-25 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, feature-engineering, preprocessing, scaling, encoding, interactive]
thumbnail: /images/ml-series/ch06-feature-engineering.svg
---

ប្រសិន​បើ​អ្នក​សួរ data scientist ​ដែល​មាន​បទ​ពិសោធន៍​ច្រើន​ថា ​អ្វី​ដែល​​​​ធ្វើ​ឱ្យ​​លទ្ធផល​ ML ​ល្អ​បំផុត — ​ចម្លើយ​​ស្ទើរ​តែ​មិន​​មែន "​​algorithm ​ល្អ" ​ឬ​ "​ទិន្នន័យ​ច្រើន" ​ប៉ុណ្ណោះ​ទេ — ​​ច្បាស់​ជា ​"**feature engineering** ​ល្អ"។ Feature engineering ​ជា​ដំណើរ​ការ​បំប្លែង​ទិន្នន័យ​ដើម (raw) ​ទៅ​ជា​ feature ​ដែល​ algorithm ​ML យល់​បាន​ល្អ។ មេរៀន​នេះ​​បង្ហាញ​​ឧបករណ៍​ស្តង់​ដារ៖ scaling, encoding, log transform, cyclical features, ​និង missing data handling។ មាន **រូបភាព interactive ៣**៖ feature scaling ​លើ KNN classifier, log transform ​លើ​ទិន្នន័យ​​តម្លៃ​ផ្ទះ Phnom Penh, ​និង cyclical encoding សម្រាប់​ម៉ោង​ក្នុង​ថ្ងៃ។

---

# សង្ខេប

- **Scaling**៖ standardization ($z = (x-\mu)/\sigma$), min-max, robust scaling — ​សំខាន់​សម្រាប់ KNN, SVM, NN
- **Categorical encoding**៖ one-hot, ordinal, target encoding
- **Log/Box-Cox transform**៖ ​សម្រាប់​ទិន្នន័យ skewed (eg. ប្រាក់​ចំណូល, ​តម្លៃ​ផ្ទះ)
- **Cyclical encoding**៖ ​ប្រើ $(\sin, \cos)$ ​សម្រាប់ time-of-day, day-of-week, ​ខែ
- **Missing data**៖ ​លុប, impute (mean/median/KNN), ​ឬ​ flag indicator
- **Data leakage**៖ ​កុំ​ប្រើ​ test set ​ដើម្បី fit scaler/encoder

---

# ហេតុអ្វីសំខាន់?

**ច្បាប់​មាស​ Garbage in → Garbage out**៖ ​បើ​​អ្នក​ដាក់​ feature ​អន់​ឱ្យ​ algorithm — ​សូម្បី​​ deep learning​ មិន​ជួយ​អ្វី​បាន​ច្រើន​​ទេ។ ​ក្នុង​ឧស្សាហកម្ម​​នៅ​កម្ពុជា៖

| ​ស្ថានភាព | បញ្ហា​ | ​ដំណោះស្រាយ |
|---|---|---|
| AMK loan model — ​ចំណូល​ខ្ពស់​ច្រើន (top tier ​ឆ្ងាយ​ពី​មធ្យម) | Linear regression ​​ត្រូវ​ដាក់​​ផ្ដៅ​ដោយ​អតិថិជន​ច្រើន​លុយ | Log transform ​លើ income |
| Khmer NLP — ​ពាក្យ​ខ្មែរ​ច្រើន​មុខ​មាត់ | ​មិន​អាច​ដាក់​ string ​ផ្ទាល់​ឱ្យ model | Tokenization + embedding ​ឬ TF-IDF |
| ABA fraud detection — ​ម៉ោង​ប្រតិបត្តិការ | 23:00 ​​ខិត​ជិត 00:00 ​​​ប៉ុន្តែ​លេខ​​​​​ឆ្ងាយ​​ | Cyclical $(\sin, \cos)$ ​​​​ encoding |
| Wing customer — ​​ខណ្ឌ​ភ្នំ​ពេញ (Daun Penh, Toul Kork, ...) | ​មិន​មែន​លំដាប់ — ខណ្ឌ​មួយ "​ធំ​ជាង" ​ខណ្ឌ​មួយ​ទៀត​មិន​មែន​ន័យ​ | One-hot encoding |
| Crop yield — sensor ​បាត់​ទិន្នន័យ​​ខ្លះ | ​មិន​អាច​ដាក់ NaN ​​ឱ្យ algorithm ​ភាគ​ច្រើន | Imputation + missing indicator |

**ការ​ស្រាវ​ជ្រាវ​​ ​Kaggle** ​បង្ហាញ​​ថា​​ feature engineering ​​ល្អ​ច្រើន​​ជា​​​​​​​ហេតុ​នៃ​ការ​ឈ្នះ​ច្រើន​ជាង​ algorithm ​ល្អ — ​​ប៉ុន្តែ​​មាន​​​ការ​អនុវត្ត​យ៉ាង​សន្សឹមៗ​​ដោយ​ដៃ​ច្រើន​ជា​​ច្រើន​​ដង​ជាង​ការ​ប្រើ default។

---

# ពាក្យបច្ចេកទេសថ្មី

| ខ្មែរ | English | កំណត់សម្គាល់ |
|---|---|---|
| Feature engineering | feature engineering | ​ការ​បំប្លែង​ទិន្នន័យ​ដើម → feature |
| Standardization | standardization, z-score | $(x - \mu) / \sigma$ |
| Min-Max scaling | min-max scaling | $(x - x_{\min}) / (x_{\max} - x_{\min})$ |
| Robust scaling | robust scaling | $(x - \text{median}) / \text{IQR}$ |
| One-hot encoding | one-hot encoding | category → vector ​មួយ​ position |
| Ordinal encoding | ordinal encoding | category → integer (មាន​លំដាប់) |
| Target encoding | target encoding | category → mean of $y$ for that category |
| ​ការ​បំប្លែង​លោការីត | log transform | $x \to \log(1 + x)$ |
| Cyclical encoding | cyclical encoding | $t \to (\sin\theta, \cos\theta)$ |
| Imputation | imputation | ​បំពេញ​​​ NaN ​ដោយ​តម្លៃ |
| Data leakage | data leakage | ​ការ​ប្រើ​ព័ត៌មាន​ test ​ដោយ​ច្រឡំ​ក្នុង​ training |
| Feature crossing | feature crossing | ​បង្កើត feature ​ថ្មី​ដោយ​​ផ្គុំ​​ feature ច្រើន |

---

# គំនិតវិចារណញ្ញាណ

## ​​មុខ​មាត់ Feature ​សំខាន់​ជាង Algorithm

ឧបមា​អ្នក​ចង់​ព្យាករ​​ "​អ្នក​ឆ្លង COVID ​​​ឬ​ទេ" ​ដោយ​មាន feature ៖
- ​ប្រ​ភេទ A៖ ​លេខ​ទូរ​​ស័ព្ទ​អតិថិជន​
- ​ប្រ​ភេទ B៖ ​សីតុណ្ហភាព​​​​​រាង​កាយ, ​ការ​​ក្អក, ​ការ​ប៉ះ​ពាល់​អ្នក​ឆ្លង

​សូម្បី​ NN ​ខ្លាំង​បំផុត​​​​​ដាក់​លើ feature ប្រភេទ A — ​មិន​អាច​ព្យាករ​ឱ្យ​ត្រឹមត្រូវ​​បាន​ទេ។ ​​ប៉ុន្តែ​ logistic regression ​សាមញ្ញ​មួយ​​លើ​ប្រភេទ B → ​អាច​ឱ្យ​ accuracy ខ្ពស់។

> **ច្បាប់​មាស៖** **Feature ​ល្អ + algorithm ​សាមញ្ញ > Feature ​អន់ + algorithm ​ស្មុគ​ស្មាញ**

## Scaling — ​ហេតុ​ដែល​​សំខាន់​​​សម្រាប់ KNN/SVM/NN

ឧបមា​ feature 1 = income (\$1,000 ​ដល់ \$1,000,000) និង feature 2 = age (18 ​ដល់ 90)។ ​ដោយ​សារ income ​មាន scale ​ធំ​ច្រើន — ​​ការ​គណនា​ចម្ងាយ Euclidean ​​ស្ទើរ​​​តែ​​បាន​ឥទ្ធិពល​​ 99% ​ដោយ income, age ​ស្ទើរ​តែ​​​មិន​មាន​អ្វី​ឡើយ​!

​បន្ទាប់​ពី standardization — ​ទាំង​ពីរ​​ស្ថិត​ក្នុង scale ស្មើ​គ្នា ហើយ​ algorithm ​ប្រើ​ទាំង​ពីរ​ដោយ​ស្មើ​​​ភាព។

## Log transform — ​ការ​ "​ផ្គូផ្គង​​ដី"

ទិន្នន័យ​ជាក់​ស្ដែង​ច្រើន​ស្ថិត​ក្នុង​ scale ​​"power law" — ​មាន​អតិថិជន​ ​ច្រើន​ដែល​ប្រើ​លុយ​​តិច ហើយ​​​ច្រើន​​​ដែល​​ប្រើ​លុយ​ច្រើន​ដែល​មិន​មាន​ច្រើន។ ​​​​​លោការីត​​ "ផ្ទាល់​ដី​" ​​ផ្គូផ្គង​​ឱ្យ​មាន​​​ Gaussian shape — ​ងាយ​ស្រួល​សម្រាប់ linear model។

## Cyclical encoding — "23h ​ខិត​ជិត 0h ​ឬ​ឆ្ងាយ?"

​បើ​​អ្នក​ដាក់ hour ​ជា​លេខ​ត្រង់ (0-23) — model ​នឹង​យល់​ថា 23 ​ឆ្ងាយ​ពី 0 ​ច្រើន​ខ្លាំង (​ខុស​លេខ 23)។ ​​ប៉ុន្តែ​ការ​​លេង​ភ្នាល់​ ABA នៅ 23h ​ច្រើន​ស្រដៀង​នឹង 0h ​ច្រើន​ជាង​ឆ្ងាយ​ពី​វា។ ​សន្និធាន cyclical $(\sin, \cos)$ ​ដោះស្រាយ​បញ្ហា​នេះ — 23h និង 0h ​ស្ថិត​នៅ​ជិត​គ្នា​លើ​​​​​​​​​​​ unit circle។

---

# និយមន័យ និងគណិតវិទ្យា

## ១. Scaling សម្រាប់​ feature ​លេខ

### Standardization (z-score)

​សម្រាប់​​ feature $x$ ​ដែល​មាន mean $\mu$ និង​ std $\sigma$ ​ក្នុង​ training data៖

$$
x_{\text{std}} = \frac{x - \mu}{\sigma}
$$

​លទ្ធផល៖ mean = 0, std = 1។ ​ល្អ​​​ពេល​ feature ស្ទើរ Gaussian។

### Min-Max scaling

$$
x_{\text{mm}} = \frac{x - x_{\min}}{x_{\max} - x_{\min}}
$$

​លទ្ធផល៖ ក្នុង​ $[0, 1]$។ ​ល្អ​ពេល​អ្នក​ត្រូវ​ការ​ range កំណត់ (eg. image pixels, neural net activation)។

### Robust scaling

$$
x_{\text{rob}} = \frac{x - \text{median}(x)}{Q_3(x) - Q_1(x)}
$$

​ល្អ​ពេល​មាន outliers ​ច្រើន — median និង IQR ​មិន​អាស្រ័យ​លើ outliers។

## 🎮 រូបភាព interactive ១៖ ​ហេតុ​ដែល scaling ​សំខាន់​សម្រាប់ KNN

​​​យើង​​​មាន​ទិន្នន័យ​ AMK loan៖ income (\$0–\$10,000) ​និង age (18–80) → ​ព្យាករ​ default (​ឆ្នោត​ដែល​អ្នក​ default ​ឬ​ទេ)។ ​ប្ដូរ​ slider ​សម្រាប់​​ feature 2 scale — ​មើល​ KNN decision boundary​ ​ផ្លាស់​ប្ដូរ​​ជា​មួយ ​និង​មិន​មាន scaling។

<div id="viz1" style="width:100%;max-width:800px;margin:0 auto;height:440px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  Scale ratio (feature1 ÷ feature2) = <span id="viz1-scale" style="font-weight:bold;color:#dc2626">100×</span>
  <input id="viz1-scale-slider" type="range" min="1" max="3" step="0.1" value="2" style="width:50%;max-width:400px"><br>
  <label style="font-weight:600">
    <input id="viz1-norm" type="checkbox" style="vertical-align:middle"> ​អនុវត្ត standardization
  </label>
  &nbsp;|&nbsp;
  <span style="font-size:1.05em">
    KNN accuracy = <span id="viz1-acc" style="font-weight:bold;color:#0f766e">--</span>
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
      var pts = [];
      for (var i = 0; i < 100; i++) {
        var label = i < 50 ? 0 : 1;
        var f1 = (label === 0 ? 0.3 : 0.7) + 0.15 * randn();
        var f2 = (label === 0 ? 0.7 : 0.3) + 0.15 * randn();
        pts.push([f1, f2, label]);
      }
      DATA = pts;
    }
    function knnPredict(train, x1, x2, k) {
      var dists = train.map(function (p) {
        var dx = p[0] - x1, dy = p[1] - x2;
        return { d: dx * dx + dy * dy, label: p[2] };
      });
      dists.sort(function (a, b) { return a.d - b.d; });
      var c0 = 0, c1 = 0;
      for (var i = 0; i < k; i++) (dists[i].label === 0 ? c0++ : c1++);
      return c1 > c0 ? 1 : 0;
    }
    function plot(scalePow, normalize) {
      var scale = Math.pow(10, scalePow);
      // Transform data: feature1 stays, feature2 is multiplied by scale
      var work = DATA.map(function (p) { return [p[0] * scale, p[1], p[2]]; });
      var x1Vals = work.map(function (p) { return p[0]; });
      var x2Vals = work.map(function (p) { return p[1]; });
      if (normalize) {
        var m1 = x1Vals.reduce(function (s, x) { return s + x; }, 0) / x1Vals.length;
        var m2 = x2Vals.reduce(function (s, x) { return s + x; }, 0) / x2Vals.length;
        var v1 = x1Vals.reduce(function (s, x) { return s + (x - m1) * (x - m1); }, 0) / x1Vals.length;
        var v2 = x2Vals.reduce(function (s, x) { return s + (x - m2) * (x - m2); }, 0) / x2Vals.length;
        var s1 = Math.sqrt(v1), s2 = Math.sqrt(v2);
        work = work.map(function (p) { return [(p[0] - m1) / s1, (p[1] - m2) / s2, p[2]]; });
      }
      // Compute decision boundary on grid
      var xs = work.map(function (p) { return p[0]; });
      var ys = work.map(function (p) { return p[1]; });
      var xMin = Math.min.apply(null, xs), xMax = Math.max.apply(null, xs);
      var yMin = Math.min.apply(null, ys), yMax = Math.max.apply(null, ys);
      var pad = 0.15;
      var xR = xMax - xMin, yR = yMax - yMin;
      xMin -= pad * xR; xMax += pad * xR;
      yMin -= pad * yR; yMax += pad * yR;
      var grid = 30, xGrid = [], yGrid = [], zGrid = [];
      for (var i = 0; i <= grid; i++) xGrid.push(xMin + (xMax - xMin) * i / grid);
      for (var j = 0; j <= grid; j++) yGrid.push(yMin + (yMax - yMin) * j / grid);
      for (var j2 = 0; j2 <= grid; j2++) {
        var row = [];
        for (var i2 = 0; i2 <= grid; i2++) row.push(knnPredict(work, xGrid[i2], yGrid[j2], 5));
        zGrid.push(row);
      }
      // Compute "accuracy" using leave-one-out on the data (cheap proxy)
      var correct = 0;
      for (var k = 0; k < work.length; k++) {
        var others = work.slice(0, k).concat(work.slice(k + 1));
        if (knnPredict(others, work[k][0], work[k][1], 5) === work[k][2]) correct++;
      }
      var acc = correct / work.length;
      var a = work.filter(function (p) { return p[2] === 0; });
      var b = work.filter(function (p) { return p[2] === 1; });
      return {
        traces: [
          { x: xGrid, y: yGrid, z: zGrid, type: 'contour',
            colorscale: [[0, '#dbeafe'], [0.5, '#ffffff'], [1, '#fee2e2']],
            contours: { start: 0, end: 1, size: 0.5, coloring: 'fill' },
            line: { width: 0 }, showscale: false, opacity: 0.85, hoverinfo: 'skip' },
          { x: a.map(function (p) { return p[0]; }), y: a.map(function (p) { return p[1]; }),
            mode: 'markers', name: 'ល្អ (y=0)',
            marker: { color: '#1e40af', size: 9, line: { color: '#fff', width: 1 } } },
          { x: b.map(function (p) { return p[0]; }), y: b.map(function (p) { return p[1]; }),
            mode: 'markers', name: 'default (y=1)',
            marker: { color: '#dc2626', size: 9, line: { color: '#fff', width: 1 } } }
        ],
        acc: acc
      };
    }
    var layout = {
      xaxis: { title: 'feature 1 (eg. income — scaled)' },
      yaxis: { title: 'feature 2 (eg. age)' },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    gen();
    var d = plot(2, false);
    Plotly.newPlot('viz1', d.traces, layout, { responsive: true, displayModeBar: false });
    document.getElementById('viz1-acc').textContent = (d.acc * 100).toFixed(1) + '%';
    function render() {
      var pow = parseFloat(document.getElementById('viz1-scale-slider').value);
      var norm = document.getElementById('viz1-norm').checked;
      document.getElementById('viz1-scale').textContent = Math.pow(10, pow).toFixed(0) + '×';
      var d = plot(pow, norm);
      document.getElementById('viz1-acc').textContent = (d.acc * 100).toFixed(1) + '%';
      Plotly.react('viz1', d.traces, layout);
    }
    document.getElementById('viz1-scale-slider').addEventListener('input', render);
    document.getElementById('viz1-norm').addEventListener('change', render);
  }
  init();
})();
</script>

> **សង្កេត​ផ្ទាល់៖** ​នៅ scale ratio = 1000× **ដោយ​មិន​មាន** standardization — KNN accuracy ​ដួល​ចុះ​ខ្លាំង​ (boundary ​ស្ទើរ​​​តែ​ត្រង់​បញ្ឈរ — ​​​​​មិន​​ផ្ទេរ​ feature 2 សោះ)។ ​ដាក់ check standardization — accuracy ​លោត​ឡើង​ភ្លាមៗ! ​នេះ​ជា​ហេតុ​ដែល​ប្រើ KNN/SVM/NN ​**តែង​តែ**​​ត្រូវ scaling។

## ២. Categorical encoding

### One-hot encoding

​សម្រាប់​​ category មាន $K$ ​តម្លៃ → vector ​ប្រវែង $K$ ដែល​មាន 1 ​នៅ position ត្រូវ​នឹង category, 0 ​ផ្សេង​ៗ៖

$$
\text{Daun Penh} \to [1, 0, 0, 0, 0, 0, 0] \text{ (ខណ្ឌ 7 ​ប្រភេទ)}
$$

​ល្អ​ពេល​ category ​មិន​មាន​លំដាប់ (nominal) ​ហើយ $K$ ​មិន​ធំ​ខ្លាំង។

### Ordinal encoding

​ដាក់​ category ​ជា integer ​តាម​លំដាប់៖

$$
\{\text{Bachelor}, \text{Master}, \text{PhD}\} \to \{0, 1, 2\}
$$

​ល្អ​ពេល​ category មាន​លំដាប់​ធម្មជាតិ​ (education level, satisfaction rating)។

### Target encoding

ជំនួស​ category ​ដោយ mean of $y$ ​ក្នុង​ category នោះ៖

$$
\text{encode}(\text{Daun Penh}) = \frac{1}{n_{\text{DP}}} \sum_{i: x_i = \text{DP}} y_i
$$

​ល្អ​ពេល $K$ ​ធំ (high-cardinality categories) ​តែ​ត្រូវ​ប្រយ័ត្ន data leakage — ​ត្រូវ​​ប្រើ​ target ​​​ពី training set ​ប៉ុណ្ណោះ ​ឬ​ប្រើ K-fold mean។

## ៣. Log transform ​សម្រាប់​ skewed data

​ការ​បំប្លែង​លោការីត៖

$$
x' = \log(1 + x)
$$

​ (​ប្រើ $\log(1+x)$ ​ជំនួស $\log(x)$ ​ដើម្បី​អនុញ្ញាត $x = 0$)

​សម្រាប់​ Box-Cox ​ទូទៅ៖

$$
x'(\lambda) = \begin{cases} \dfrac{x^\lambda - 1}{\lambda}, & \lambda \neq 0 \\[6pt] \log(x), & \lambda = 0 \end{cases}
$$

ការ​បំប្លែង​ទាំង​ពីរ​នេះ​​​"ផ្ទុះ​​ភ្នំ" ​នៃ​ distribution ដែល​មាន long right tail ​ឱ្យ​ស្រដៀង​ Gaussian។

## 🎮 រូបភាព interactive ២៖ Log transform ​លើ​ Phnom Penh house prices

ទិន្នន័យ​ផ្ទះ Phnom Penh ​មាន long right tail — ​ផ្ទះ​ច្រើន​នៅ​ \$50K–\$200K តែ​ផ្ទះ​ luxury ​ឡើង​ដល់ \$2M។ ​សាក​មើល​មុន (raw) ​និង​បន្ទាប់ (log)។

<div id="viz2" style="width:100%;max-width:800px;margin:0 auto;height:440px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  <label style="font-weight:600">
    <input id="viz2-log" type="checkbox" style="vertical-align:middle" checked> ​​អនុវត្ត log transform
  </label>
  &nbsp;&nbsp;
  <span style="font-size:1.05em">
    Skewness = <span id="viz2-skew" style="font-weight:bold;color:#dc2626">--</span>
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
    // Generate lognormal-ish PP house prices in $K
    var PRICES = [];
    for (var i = 0; i < 800; i++) {
      // log-mean=11.6 (~$110K median), log-std=0.7
      PRICES.push(Math.exp(11.6 + 0.7 * randn()) / 1000);
    }
    function skewness(arr) {
      var n = arr.length;
      var m = arr.reduce(function (s, x) { return s + x; }, 0) / n;
      var s2 = arr.reduce(function (s, x) { return s + (x - m) * (x - m); }, 0) / n;
      var s3 = arr.reduce(function (s, x) { return s + Math.pow(x - m, 3); }, 0) / n;
      return s3 / Math.pow(s2, 1.5);
    }
    function pdfGauss(x, mu, sigma) {
      return Math.exp(-0.5 * Math.pow((x - mu) / sigma, 2)) / (sigma * Math.sqrt(2 * Math.PI));
    }
    function plot(useLog) {
      var data = useLog ? PRICES.map(function (p) { return Math.log(p); }) : PRICES.slice();
      var skew = skewness(data);
      var m = data.reduce(function (s, x) { return s + x; }, 0) / data.length;
      var s2 = data.reduce(function (s, x) { return s + (x - m) * (x - m); }, 0) / data.length;
      var sigma = Math.sqrt(s2);
      var xMin = Math.min.apply(null, data), xMax = Math.max.apply(null, data);
      var step = (xMax - xMin) / 100;
      var xs = [], ys = [];
      for (var x = xMin; x <= xMax; x += step) { xs.push(x); ys.push(pdfGauss(x, m, sigma)); }
      return {
        traces: [
          { x: data, type: 'histogram', name: 'data',
            histnorm: 'probability density',
            xbins: { start: xMin, end: xMax, size: (xMax - xMin) / 35 },
            marker: { color: useLog ? '#0f766e' : '#dc2626', opacity: 0.6 } },
          { x: xs, y: ys, mode: 'lines', name: 'Gaussian fit',
            line: { color: '#0f172a', width: 3 } }
        ],
        skew: skew
      };
    }
    var layoutRaw = {
      xaxis: { title: 'Phnom Penh house price ($K)' },
      yaxis: { title: 'density' },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.6, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      bargap: 0.03,
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    var layoutLog = {
      xaxis: { title: 'log(house price)' },
      yaxis: { title: 'density' },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.6, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      bargap: 0.03,
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    var d = plot(true);
    Plotly.newPlot('viz2', d.traces, layoutLog, { responsive: true, displayModeBar: false });
    document.getElementById('viz2-skew').textContent = d.skew.toFixed(2);
    function render() {
      var useLog = document.getElementById('viz2-log').checked;
      var d = plot(useLog);
      document.getElementById('viz2-skew').textContent = d.skew.toFixed(2);
      Plotly.react('viz2', d.traces, useLog ? layoutLog : layoutRaw);
    }
    document.getElementById('viz2-log').addEventListener('change', render);
  }
  init();
})();
</script>

> **សង្កេត៖** ​​បើ​​មិន​មាន​ log — skewness ខ្ពស់ (~2–3), histogram មាន long right tail — Gaussian fit ​ខុស​ខ្លាំង។ ​ប្ដូរ​ទៅ log — skewness ​​​ស្ទើរ 0, histogram ស្តង់​ដារ​ Gaussian — linear model ​​ដំណើរ​ការ​ល្អ​​ខ្លាំង។

## ៤. Cyclical encoding ​សម្រាប់​​ time features

​សម្រាប់​ feature ​​ដែល​មាន period $T$ (eg. hour ​មាន period 24, day-of-week មាន period 7)៖

$$
x_{\sin} = \sin\!\left(\frac{2\pi \, t}{T}\right), \quad x_{\cos} = \cos\!\left(\frac{2\pi \, t}{T}\right)
$$

​លទ្ធផល៖ ​ចំណុច $(x_\sin, x_\cos)$ ​​​ស្ថិត​​លើ​​​​​ unit circle។ ​ចំណុច​​នៅ $t = 23$ ​ខិត​ជិត $t = 0$ ខ្លាំង — ​ដូច​ដែល​​​យើង​ចង់​បាន!

## 🎮 រូបភាព interactive ៣៖ Cyclical encoding សម្រាប់​ម៉ោង​ក្នុង​ថ្ងៃ

ឧបមា fraud detection ABA ​ត្រូវ​​ដឹង​ហេតុ​ដែល​ការ​​​ប្រតិបត្តិការ​​​ ​​ស្ថិត​នៅ​​​ម៉ោង​ណា។ ​ប្ដូរ​​​ slider សម្រាប់​ម៉ោង — ​មើល​​​ representation 1D ​(linear) ​និង 2D ​(cyclical) ​ដែល​មាន​សភាព​ខុស​គ្នា​យ៉ាង​ខ្លាំង។

<div id="viz3" style="width:100%;max-width:800px;margin:0 auto;height:440px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  ​ម៉ោង (0–23) = <span id="viz3-hour" style="font-weight:bold;color:#1e40af">14</span>
  <input id="viz3-hour-slider" type="range" min="0" max="23" step="1" value="14" style="width:50%;max-width:400px"><br>
  <span style="font-size:1.0em">
    Linear value = <span id="viz3-lin" style="font-weight:bold;color:#dc2626">14</span>
    &nbsp;|&nbsp;
    sin = <span id="viz3-sin" style="font-weight:bold;color:#0f766e">-0.50</span>
    &nbsp;|&nbsp;
    cos = <span id="viz3-cos" style="font-weight:bold;color:#7c3aed">-0.87</span>
  </span>
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    function plot(hour) {
      var sins = [], coss = [], labels = [];
      for (var h = 0; h < 24; h++) {
        sins.push(Math.sin(2 * Math.PI * h / 24));
        coss.push(Math.cos(2 * Math.PI * h / 24));
        labels.push(h + 'h');
      }
      var hSin = Math.sin(2 * Math.PI * hour / 24);
      var hCos = Math.cos(2 * Math.PI * hour / 24);
      return [
        // Linear line, full row
        { x: Array.from({length: 24}, function (_, i) { return i; }),
          y: Array.from({length: 24}, function () { return 0; }),
          mode: 'markers+lines', name: 'Linear (0–23)',
          marker: { color: '#94a3b8', size: 8 },
          line: { color: '#94a3b8', width: 2 },
          xaxis: 'x', yaxis: 'y' },
        { x: [hour], y: [0], mode: 'markers',
          marker: { color: '#dc2626', size: 22, line: { color: '#7f1d1d', width: 3 } },
          name: 'current', xaxis: 'x', yaxis: 'y', showlegend: false },
        // Circle
        { x: coss, y: sins, mode: 'markers+text', name: 'Cyclical (sin, cos)',
          marker: { color: '#0f766e', size: 8 },
          text: labels, textposition: 'top center',
          textfont: { size: 9 },
          xaxis: 'x2', yaxis: 'y2' },
        { x: [hCos], y: [hSin], mode: 'markers',
          marker: { color: '#dc2626', size: 22, line: { color: '#7f1d1d', width: 3 } },
          name: 'current', xaxis: 'x2', yaxis: 'y2', showlegend: false }
      ];
    }
    var layout = {
      grid: { rows: 1, columns: 2, pattern: 'independent' },
      xaxis: { title: 'hour (linear)', range: [-1, 24], domain: [0, 0.45] },
      yaxis: { range: [-0.3, 0.3], showticklabels: false, zeroline: false, fixedrange: true,
               domain: [0, 1] },
      xaxis2: { title: 'cos(2π·h/24)', range: [-1.4, 1.4], domain: [0.55, 1] },
      yaxis2: { title: 'sin(2π·h/24)', range: [-1.4, 1.4], scaleanchor: 'x2', scaleratio: 1,
                domain: [0, 1] },
      margin: { t: 30, b: 50, l: 50, r: 30 },
      showlegend: false,
      annotations: [
        { text: 'Linear: 23 ឆ្ងាយ​ពី 0 ច្រើន ❌', xref: 'paper', yref: 'paper',
          x: 0.22, y: 1.06, showarrow: false,
          font: { size: 12, weight: 700, color: '#dc2626' } },
        { text: 'Cyclical: 23 ខិត​ជិត 0 ✓', xref: 'paper', yref: 'paper',
          x: 0.78, y: 1.06, showarrow: false,
          font: { size: 12, weight: 700, color: '#0f766e' } }
      ],
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    Plotly.newPlot('viz3', plot(14), layout, { responsive: true, displayModeBar: false });
    function render() {
      var h = parseInt(document.getElementById('viz3-hour-slider').value);
      var hSin = Math.sin(2 * Math.PI * h / 24);
      var hCos = Math.cos(2 * Math.PI * h / 24);
      document.getElementById('viz3-hour').textContent = h;
      document.getElementById('viz3-lin').textContent = h;
      document.getElementById('viz3-sin').textContent = hSin.toFixed(2);
      document.getElementById('viz3-cos').textContent = hCos.toFixed(2);
      Plotly.react('viz3', plot(h), layout);
    }
    document.getElementById('viz3-hour-slider').addEventListener('input', render);
  }
  init();
})();
</script>

> **គន្លឹះ​សំខាន់៖** ​ប្ដូរ slider ​ទៅ 23, ​បន្ទាប់​មក 0 — ​មើល​​លើ​​​​​​​ linear line ​ខ្ញុំ​លោត​ដោយ 23 unit; ​​លើ​ ​circle ​ខ្ញុំ​លោត​​បន្តិច​​ប៉ុណ្ណោះ។ ​​សម្រាប់​ NN ​ឬ KNN ​ដែល​ប្រើ ​Euclidean distance — ​​នេះ​មាន​ឥទ្ធិពល​ច្រើន​ខ្លាំង!

## ៥. Missing data handling

​ជម្រើស៖

| ​យុទ្ធសាស្ត្រ | ​ពេល​ប្រើ | កំណត់​សម្គាល់ |
|---|---|---|
| **​លុប row** | ​បាត់​បន្តិច (< 5%) ​ហើយ​ random | ​ងាយ​​​​​បំផុត |
| **​លុប column** | ​បាត់​ច្រើន (> 70%) | ​ហ្គឺមណ៍​ feature ​មិន​មាន​ប្រយោជន៍ |
| **Mean/Median imputation** | numeric, random | ​សាមញ្ញ ​តែ​បន្ថយ variance |
| **Mode imputation** | categorical | ​ងាយ |
| **KNN imputation** | ​មាន feature ស្រដៀង​គ្នា​ច្រើន | ​​​មាន​ប្រសិទ្ធភាព​ច្រើន ​តែ​យឺត |
| **Model-based** | ​មាន pattern ច្បាស់ | ​ប្រើ regression/classifier ​ដោយ​ស្វ័យ​ប្រវត្តិ |
| **Indicator column** | "​បាត់" ​ខ្លួន​ឯង​មាន​​​​ព័ត៌មាន | ​ដែរ​ឱ្យ​​ model ​ដឹង​ថា​​​ value ​បាន​ missing |

## ៦. Data leakage — ​​សត្រូវ​​ដ៏​លាក់​កំបាំង

**Data leakage** = ​ការ​ប្រើ​ព័ត៌មាន​ដែល​មិន​មាន​ក្នុង​ training time ​ក្នុង feature engineering។ ​លទ្ធផល៖ test accuracy ​ល្អ​ខ្លាំង​​ ​តែ production accuracy ​អន់​ខ្លាំង។

**​ឧទាហរណ៍​ខុស​​​ដែល​មនុស្ស​ច្រើន​ធ្វើ៖**

```python
# ❌ ខុស! mean/std ប្រើ​​ទាំង train + test
mu = X_all.mean(); sigma = X_all.std()
X_train_scaled = (X_train - mu) / sigma
X_test_scaled  = (X_test - mu) / sigma
```

**​ត្រឹមត្រូវ៖**

```python
# ✓ Fit scaler លើ train ​​ប៉ុណ្ណោះ
scaler = StandardScaler().fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled  = scaler.transform(X_test)
```

​ច្បាប់​មាស៖ ​អ្វី​ដែល​ fit នឹង training set; transform នឹង​ទាំង training និង test។

---

# ឧទាហរណ៍

**ឧទាហរណ៍ ១៖ AMK loan feature engineering**

ទិន្នន័យ​ដើម៖

```
age=32, income=850, district="Daun Penh", apply_time="14:30",
prev_loans=3, defaults_history=NaN
```

​ក្រោយ feature engineering៖

```
age_std=-0.3, log_income=6.74,
district_DP=1, district_TK=0, district_BK=0, ...,
sin_hour=0.97, cos_hour=-0.26,
prev_loans_log=1.39,
defaults_imputed=0.0, defaults_was_missing=1
```

**ឧទាហរណ៍ ២៖ Khmer text feature**

​អត្ថបទ​ Khmer "ផលិតផល​នេះ​ល្អ​ខ្លាំង" → feature ​ត្រូវ​បំប្លែង​ដោយ៖

1. **Tokenization** (Khmer ​មិន​មាន​​ដក​ឃ្លា — ​ត្រូវ Khmer word segmenter)
2. **TF-IDF** ​ឬ​ **embedding** (eg. XLM-RoBERTa multilingual)
3. ​​ឬ​ tokenize ដោយ​​​​​ subword (BPE) — ​​ប្រើ​ច្រើន​ក្នុង Khmer LLM ​សម័យ​ថ្មី

---

# កូដ Python

## Scaling

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # fit + transform
X_test_scaled  = scaler.transform(X_test)        # transform only!
```

## One-hot encoding

```python
import pandas as pd

df = pd.DataFrame({'district': ['Daun Penh', 'Toul Kork', 'BKK1', 'Daun Penh']})
X = pd.get_dummies(df, columns=['district'], drop_first=True)
print(X)
#    district_Daun Penh  district_Toul Kork
# 0                   1                   0
# 1                   0                   1
# 2                   0                   0   <- reference (BKK1)
# 3                   1                   0
```

## Log transform + cyclical encoding

```python
import numpy as np

df['log_income']  = np.log1p(df['income'])
df['hour_sin']    = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos']    = np.cos(2 * np.pi * df['hour'] / 24)
df['dow_sin']     = np.sin(2 * np.pi * df['day_of_week'] / 7)
df['dow_cos']     = np.cos(2 * np.pi * df['day_of_week'] / 7)
```

## Imputation

```python
from sklearn.impute import SimpleImputer, KNNImputer

# Simple mean imputation
imp = SimpleImputer(strategy='mean')
X_imp = imp.fit_transform(X)

# KNN imputation (slower but better)
imp_knn = KNNImputer(n_neighbors=5)
X_imp_knn = imp_knn.fit_transform(X)
```

## ​បំពេញ pipeline (​ច្បាប់​​មាស​​ៗ​ដោយ​ស្វ័យ​ប្រវត្តិ)

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression

num_features = ['age', 'log_income']
cat_features = ['district']

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), num_features),
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features),
])

pipeline = Pipeline([
    ('prep', preprocessor),
    ('clf', LogisticRegression()),
])

pipeline.fit(X_train, y_train)   # ឥឡូវ scaler+encoder+model ហ្វឹក​ហាត់​ត្រឹមត្រូវ
print(pipeline.score(X_test, y_test))   # no leakage!
```

​**ហេតុ​ដែល​ Pipeline ​សំខាន់៖** ​​ការ​ fit ​​ដោយ​ស្វ័យ​ប្រវត្តិ​លើ training ​ប៉ុណ្ណោះ; ​ការ​ដាក់​ scaler/encoder ​មុន​ model ​ដោយ​ស្វ័យ​ប្រវត្តិ; ​អាច dump ​ដាក់​ production ​ឯ​​ឯង​ដោយ​មិន​បាត់​ steps។

---

# ការអនុវត្តន៍ជាក់ស្ដែង

## ​ច្បាប់​ស្នូល​ច្រើន​ឆ្នាំ​ដែល​បង្ហាញ​ខ្លួន​​ឥត​ខូច

1. ​**​​​​មើល​​​ histogram ​មុន**​ — ​ឱ្យ​ដឹង scale, skew, outliers, missing
2. **Scaling សម្រាប់​​ distance-based** — KNN, SVM, NN ត្រូវ​​; Tree-based ​មិន​ត្រូវ
3. **One-hot ​សម្រាប់ category ​មិន​មាន​លំដាប់** — ​ហើយ drop_first ​ដើម្បី​ជៀស​វាង collinearity
4. **Log transform** សម្រាប់​ feature ​មាន long right tail (income, price, count)
5. **Cyclical** សម្រាប់ time features
6. **ប្រើ Pipeline** ​សម្រាប់​ leakage prevention
7. **Imputation + indicator** — "​​missing" ​ខ្លួន​ឯង​​មាន​ព័ត៌មាន
8. **​សាក​ច្រើន​ rule, ​​​​មើល​ការ​ផ្លាស់​ប្ដូរ metric** — Empirical ​សំខាន់​ជាង theory

## Feature engineering ​​​ល្អ​សម្រាប់​ឧស្សាហកម្ម​នៅ​កម្ពុជា

| ​ឧស្សាហកម្ម | Feature ​​ស្នូល​ ​​​ដែល​​​​សំខាន់ |
|---|---|
| AMK loan | log_income, debt_to_income, prev_default_rate, day-of-month effect |
| ABA fraud | log_amount, hour_sin/cos, days_since_last_tx, merchant_category_target_enc |
| Wing churn | days_since_last_tx, frequency_log, decline_rate, account_age |
| Khmer NLP | subword tokens, character-level features, POS tags (​ពេល​មាន) |
| Crop yield | NDVI mean/std/min, rainfall_log, temperature_cyclical, soil_type one-hot |
| PP house price | log_price, sqm_log, district_target_enc, year_built, has_pool |

---

# លំហាត់

### លំហាត់ 1 — ​ការ​​ជ្រើស​ encoding

​ផ្តល់ feature ​ខាង​ក្រោម — ​ជ្រើស encoding ​ត្រឹមត្រូវ៖

a) Education ​ : Primary / Secondary / Bachelor / Master / PhD<br>
b) ​ខណ្ឌ​ភ្នំ​ពេញ​ : 7 ​ខណ្ឌ​ (Daun Penh, Toul Kork, Chamkar Mon, ...)<br>
c) Customer satisfaction ​ : 1, 2, 3, 4, 5 stars<br>
d) Day of week<br>
e) Postal code (1000 ​លេខ​ផ្សេង​ៗ)

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

| លំហាត់ | Encoding | ហេតុ​ផល |
|---|---|---|
| a | **Ordinal** | មាន​លំដាប់​ច្បាស់: Primary < ... < PhD |
| b | **One-hot** | ​មិន​មាន​លំដាប់ (nominal), K=7 មិន​ធំ |
| c | **Ordinal** ​​ឬ​ **as-is integer** | មាន​លំដាប់​ច្បាស់ |
| d | **Cyclical** (sin/cos) | Period 7, Sunday ​ខិត​ជិត Monday |
| e | **Target encoding** ​ឬ **embedding** | K=1000 ​ធំ​ខ្លាំង → one-hot ​នឹង​បង្កើត 1000 columns; target encoding ​​​ល្អ​ប៉ុន្តែ​​ត្រូវ​ប្រយ័ត្ន leakage |

</details>

### លំហាត់ 2 — Scaling

​សម្រាប់​​ feature ​ខាង​ក្រោម — ​ជ្រើស​ scaling ​ត្រឹមត្រូវ៖

a) Income ​ : \$300 ​ដល់ \$50,000 (​មាន outliers ​ច្រើន)<br>
b) Age ​ : 18 ​ដល់ 80 (​ស្ទើរ Gaussian)<br>
c) Image pixel ​ : 0 ​ដល់ 255<br>
d) Square meters ​ : 20 ​ដល់ 500

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

| លំហាត់ | Scaling | ហេតុ​ផល |
|---|---|---|
| a | **Log + Standardization** ​ឬ **Robust scaling** | Long tail + outliers; ​log ​ជួយ​​បង្រួម tail |
| b | **Standardization** | Gaussian-ish, ​ស្តង់​ដារ​ល្អ​បំផុត |
| c | **Min-Max ​ដោយ​​ /255** | Range ​ត្រូវ [0, 1] ​សម្រាប់ NN |
| d | **Standardization** ​ឬ **Log + Std** | ​បើ skewed → log ​ល្អ​ជាង |

</details>

### លំហាត់ 3 — Data leakage detection

​សួរ​ខ្លួន​ឯង — តើ​កូដ​ខាង​ក្រោម​មាន leakage ​ឬ​ទេ? ​​បើ​មាន — ​​​​​សរសេរ​ឡើង​​​វិញ​ឱ្យ​ត្រឹមត្រូវ៖

```python
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Scale everything first
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Then split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)

model.fit(X_train, y_train)
print(model.score(X_test, y_test))
```

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**មាន leakage ច្បាស់ៗ!** scaler ​បាន fit លើ​ទាំង training + test → mean និង std ​ប៉ះ​ពាល់​ដោយ test data → test set ​មិន​មាន "​មិន​ដែល​ឃើញ"​ ​លែង​ច្បាស់​ហើយ។

**ការ​សរសេរ​ឡើង​វិញ​ត្រឹមត្រូវ៖**

```python
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Split FIRST
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Then fit scaler on train only
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # fit + transform train
X_test_scaled  = scaler.transform(X_test)         # transform test (no fit!)

model.fit(X_train_scaled, y_train)
print(model.score(X_test_scaled, y_test))
```

**ដំណោះស្រាយ​ល្អ​ជាង​នេះ** — ​​ប្រើ Pipeline ​ដែល​ស្វ័យ​ប្រវត្តិ​ការ​នេះ៖

```python
from sklearn.pipeline import Pipeline

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', model),
])
pipe.fit(X_train, y_train)
print(pipe.score(X_test, y_test))
```

</details>

### លំហាត់ 4 — Cyclical encoding ដោយ​ដៃ

គណនា $(\sin, \cos)$ ​សម្រាប់​​ feature day-of-week (Mon=0, Sun=6) ​សម្រាប់៖

a) Monday (day = 0)<br>
b) Thursday (day = 3)<br>
c) Sunday (day = 6)

ហើយ​​ផ្ទៀង​ផ្ទាត់​ថា Sunday ​ខិត​ជិត Monday ​ក្នុង representation ​នោះ។

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

​រូបមន្ត៖ $\theta = 2\pi \cdot d / 7$, $\sin\theta$, $\cos\theta$

| ​ថ្ងៃ | $\theta$ | $\sin$ | $\cos$ |
|---|:-:|:-:|:-:|
| Mon (0) | 0 | 0.00 | 1.00 |
| Thu (3) | $6\pi/7 \approx 2.69$ | 0.43 | -0.90 |
| Sun (6) | $12\pi/7 \approx 5.39$ | -0.78 | 0.62 |

**ផ្ទៀង​ផ្ទាត់ Sun ↔ Mon ​ខិត​ជិត​៖**

​ចម្ងាយ​ Euclidean រវាង Sun និង Mon៖

$$
d = \sqrt{(0 - (-0.78))^2 + (1 - 0.62)^2} = \sqrt{0.609 + 0.144} = \sqrt{0.753} \approx 0.868
$$

​ចម្ងាយ​ Mon ↔ Thu៖

$$
d = \sqrt{(0 - 0.43)^2 + (1 - (-0.90))^2} = \sqrt{0.185 + 3.61} \approx 1.95
$$

**សេចក្តី​សន្និដ្ឋាន៖** Sun-Mon ​ចម្ងាយ ≈ 0.87, Mon-Thu ​ចម្ងាយ ≈ 1.95 — Sun ​ខិត​ជិត Mon ​ច្រើន​ជាង Thu។ ​​ដូច​ដែល​យើង​​​ចង់​បាន!

</details>

---

**មេរៀន​បន្ទាប់ (ជំពូក 7):** Linear regression — algorithm ​ML ​ដំបូង​ដែល​យើង​នឹង​ build ​ផ្ទាល់​ដោយ​ដៃ។ យើង​នឹង​មើល normal equation, gradient descent, ការ​បកស្រាយ coefficient, R², ​ដើម្បី​ព្យាករ​តម្លៃ​ផ្ទះ​ Phnom Penh ​ដោយ​ប្រើ feature ​ដែល​យើង engineer ​ក្នុង​មេរៀន​នេះ។
