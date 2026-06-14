---
layout: post
title: "[ML Khmer] ជំពូក 3: ប្រូបាប៊ីលីតេ​សម្រាប់ ML"
date: 2026-06-20 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, math, probability, bayes, interactive]
thumbnail: /images/ml-series/ch03-probability.svg
---

មេរៀន​នេះ​ចាប់​ផ្ដើម​ផ្នែក​មួយ​ថ្មី​នៃ​ស្នូល​គណិតវិទ្យា​សម្រាប់ ML — **ប្រូបាប៊ីលីតេ**។ យើង​នឹង​មើល​អថេរ​ចៃ​ដន្យ, ការ​ចែក​ចាយ​សំខាន់ៗ (Bernoulli, Gaussian), ប្រូបាប៊ីលីតេ​លក្ខខណ្ឌ, និង​ច្បាប់ Bayes — ឧបករណ៍​ដែល​ត្រូវ​ប្រើ​ក្នុង Naive Bayes, MLE/MAP, និង model probabilistic ផ្សេងៗ។ មាន **រូបភាព interactive ៣** ដើម្បី​ឱ្យ​អ្នក​លេង​ផ្ទាល់៖ sampling ពី Gaussian, ច្បាប់ Bayes ជាមួយ​ការ​ធ្វើ​តេស្ត COVID, និង​ការ​ចែក​ចាយ​សហ​ការ (joint distribution)។

---

# សង្ខេប

- **អថេរ​ចៃ​ដន្យ** (random variable) គឺ​អថេរ​ដែល​តម្លៃ​អាស្រ័យ​លើ​លទ្ធផល​ចៃ​ដន្យ
- **ការ​ចែក​ចាយ​ប្រូបាប៊ីលីតេ** (probability distribution) ប្រាប់​យើង​ថា​តម្លៃ​ណា​មាន​ឱកាស​កើត​មាន​ប៉ុនណា
- **Gaussian distribution** $\mathcal{N}(\mu, \sigma^2)$ — ការ​ចែក​ចាយ​សំខាន់​បំផុត​ក្នុង ML
- **ច្បាប់ Bayes**៖ $P(A \mid B) = \dfrac{P(B \mid A) P(A)}{P(B)}$ — ស្នូល​នៃ​ការ​យល់​ដឹង​ប្រូបាប៊ីលីតេ​បន្ទាប់ពី​ឃើញ​ទិន្នន័យ
- **ឯករាជ្យ** (independence): $P(A, B) = P(A) P(B)$ — ហេតុ​ដែល Naive Bayes ហៅ​ "naive"

---

# ហេតុអ្វីសំខាន់?

រាល់​គំរូ ML មាន **ភាព​មិន​ច្បាស់​លាស់** (uncertainty)៖
- ការ​ព្យាករ​អាច​ខុស
- ទិន្នន័យ​មាន noise
- ការ​សម្រេច​ចិត្ត​ត្រូវ​ធ្វើ​ដោយ​មាន​ព័ត៌មាន​មិន​ពេញ​លេញ

ប្រូបាប៊ីលីតេ​គឺ​ជា **ភាសា​នៃ​ភាព​មិន​ច្បាស់​លាស់**។ ដោយ​មិន​យល់​ប្រូបាប៊ីលីតេ, ការ implement Naive Bayes classifier, logistic regression, Gaussian Mixture Model, Bayesian neural network ទាំង​អស់​នឹង​ក្លាយ​ជា "magic" ដែល​មិន​អាច​ប្ដូរ​ឬ​យល់​បាន។

**ឧទាហរណ៍កម្ពុជា៖** នៅ​ឆ្នាំ 2020, ការ​ធ្វើ​តេស្ត COVID PCR មាន **sensitivity ≈ 95%** និង **specificity ≈ 99%**។ បើ​អ្នក​ធ្វើ​តេស្ត​ហើយ​បាន​លទ្ធផល​វិជ្ជមាន — តើ​អ្នក​ឆ្លង​មែន? **ច្បាប់ Bayes ជា​ឧបករណ៍​ត្រឹមត្រូវ​ដើម្បី​ឆ្លើយ​សំណួរ​នេះ** (ឆ្លើយ​នៅ​ខាង​ក្រោម)។

---

# ពាក្យបច្ចេកទេសថ្មី

| ខ្មែរ | English | កំណត់សម្គាល់ |
|---|---|---|
| អថេរ​ចៃ​ដន្យ | random variable | អថេរ​ដែល​មាន​តម្លៃ​ចៃ​ដន្យ ($X, Y, \ldots$) |
| ការ​ចែក​ចាយ | distribution | មុខងារ​ប្រូបាប៊ីលីតេ |
| PMF | probability mass function | សម្រាប់​អថេរ discrete |
| PDF | probability density function | សម្រាប់​អថេរ continuous |
| CDF | cumulative distribution function | $F_X(x) = P(X \le x)$ |
| ប្រូបាប៊ីលីតេ​លក្ខខណ្ឌ | conditional probability | $P(A \mid B)$ |
| ឯករាជ្យ | independence | $P(A, B) = P(A) P(B)$ |
| តម្លៃ​សង្ឃឹម | expectation / mean | $\mathbb{E}[X] = \sum x P(x)$ ឬ $\int x f(x) dx$ |
| វ៉ារ្យង់ | variance | $\text{Var}(X) = \mathbb{E}[(X-\mu)^2]$ |
| ច្បាប់ Bayes | Bayes' theorem | $P(A \mid B) = P(B \mid A) P(A) / P(B)$ |
| Prior / Posterior | prior / posterior | មុន​/​ក្រោយ​ឃើញ​ទិន្នន័យ |

---

# គំនិតវិចារណញ្ញាណ

## ប្រូបាប៊ីលីតេ ≈ ភាគ​រយ​នៃ​ករណី

ឧបមា​អ្នក​បោះ​កាក់ 1,000 ដង — បាន​មុខ 503 ដង។ ប្រូបាប៊ីលីតេ​ដែល​បាន​មុខ​ប៉ាន់​ប្រមាណ​ប្រហែល $503/1000 = 0.503$។ **ប្រូបាប៊ីលីតេ​គឺ​ជា​ដែន​កំណត់​នៃ​ប្រេកង់​ដែល​បន្តរ​យូរ**៖

$$
P(\text{head}) = \lim_{n \to \infty} \frac{\#\text{heads}}{n}
$$

## ការ​ចែក​ចាយ Gaussian = "សំណាង​បាន​មក​ដោយ​ឱកាស​ច្រើន"

ស្ទើរ​តែ​គ្រប់​អ្វី​ដែល​ជា​ផល​បូក​នៃ​បច្ច័យ​ផ្សេងៗ​ច្រើន​នឹង​មាន​រូបរាង **ស្តង់​ដារ​នៃ​អ័ក្ស​ក្បាល** (bell curve) — នេះ​ហើយ​ជា **central limit theorem**៖
- កម្ពស់​មនុស្ស​ខ្មែរ (បច្ច័យ​ហ្សែន + អាហារ + ...) → Gaussian
- ល្បឿន​ TukTuk នៅ​មហាវិថី​ព្រះ​នរោត្តម (ល្បឿន​ផ្ដាច់ + ការ​ឆ្លង​ភ្លើង​ស្ទប់ + ...) → ប្រហែល​ Gaussian
- ការ​បំប្លែង​ការ​ព្យាករ​នៃ neural network → ​ច្រើន​ដង​ Gaussian

## ច្បាប់ Bayes = "ផ្លាស់​ប្ដូរ​ការ​ជឿ​ជាក់​បន្ទាប់​ពី​ឃើញ​ភ័ស្តុតាង"

មុន​ឃើញ​ភ័ស្តុតាង → អ្នក​មាន **prior** $P(A)$។ ឃើញ​ភ័ស្តុតាង → អ្នក​ផ្លាស់​ប្ដូរ​ទៅ **posterior** $P(A \mid B)$។ ច្បាប់ Bayes ជា​រូបមន្ត​សម្រាប់​ការ​ផ្លាស់​ប្ដូរ​នេះ។

---

# និយមន័យ និងគណិតវិទ្យា

## ១. អថេរ​ចៃ​ដន្យ និង PMF/PDF

**Discrete** (តម្លៃ​រាប់​បាន — eg. លេខ​លើ​គ្រាប់​ឡុក​ឡាក់):

$$
P(X = x_i) = p_i, \quad \sum_i p_i = 1
$$

**Continuous** (តម្លៃ​បន្ត — eg. កម្ពស់):

$$
P(a \le X \le b) = \int_a^b f_X(x) \, dx, \quad \int_{-\infty}^{\infty} f_X(x) \, dx = 1
$$

## ២. ការ​ចែក​ចាយ​សំខាន់ៗ

### Bernoulli(p)
ករណី​មាន​ឬ​មិន​មាន — eg. ភ្លៀង​ឬ​មិន​ភ្លៀង​ថ្ងៃ​ស្អែក៖

$$
P(X = 1) = p, \quad P(X = 0) = 1 - p
$$

### Categorical(p_1, ..., p_K)
ករណី $K$ ​លទ្ធផល — eg. ប្រភេទ​ឧស្ម័ន​មួយ​ក្នុង 5 ប្រភេទ៖

$$
P(X = k) = p_k, \quad \sum_{k=1}^K p_k = 1
$$

### Gaussian / Normal $\mathcal{N}(\mu, \sigma^2)$

$$
f_X(x) = \frac{1}{\sqrt{2\pi \sigma^2}} \exp\!\left( -\frac{(x - \mu)^2}{2 \sigma^2} \right)
$$

ប៉ារ៉ាម៉ែត្រ៖
- $\mu$ = តម្លៃ​សង្ឃឹម (mean), ចំណុច​កណ្ដាល​នៃ​ខ្សែ
- $\sigma$ = standard deviation, ​ទទឹង​នៃ​ខ្សែ

## 🎮 រូបភាព interactive ១៖ Sampling ពី Gaussian

ផ្លាស់ slider សម្រាប់ $\mu$, $\sigma$, និង​ចំនួន samples $n$ — ហើយ​មើល​ histogram បំពេញ​បន្ទាប់ PDF។

<div id="viz1" style="width:100%;max-width:800px;margin:0 auto;height:420px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  μ = <span id="viz1-mu" style="font-weight:bold;color:#dc2626">0.0</span>
  <input id="viz1-mu-slider" type="range" min="-3" max="3" step="0.1" value="0" style="width:25%;max-width:200px">
  &nbsp;&nbsp;
  σ = <span id="viz1-sigma" style="font-weight:bold;color:#7c3aed">1.0</span>
  <input id="viz1-sigma-slider" type="range" min="0.3" max="2.5" step="0.05" value="1.0" style="width:25%;max-width:200px">
  &nbsp;&nbsp;
  n = <span id="viz1-n" style="font-weight:bold;color:#1e40af">500</span>
  <input id="viz1-n-slider" type="range" min="50" max="5000" step="50" value="500" style="width:25%;max-width:200px"><br>
  <button id="viz1-resample" style="margin-top:6px;padding:4px 14px;font-weight:600;cursor:pointer">🎲 Re-sample</button>
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
    function pdf(x, mu, sigma) {
      return Math.exp(-0.5 * Math.pow((x - mu) / sigma, 2)) / (sigma * Math.sqrt(2 * Math.PI));
    }
    var xs = [];
    for (var x = -6; x <= 6.001; x += 0.05) xs.push(x);
    function plot(mu, sigma, n) {
      var samples = [];
      for (var i = 0; i < n; i++) samples.push(mu + sigma * randn());
      var ys = xs.map(function (x) { return pdf(x, mu, sigma); });
      return [
        { x: samples, type: 'histogram', name: 'samples',
          histnorm: 'probability density',
          xbins: { start: -6, end: 6, size: 0.25 },
          marker: { color: '#1e40af', opacity: 0.55 } },
        { x: xs, y: ys, mode: 'lines', name: 'PDF (theory)',
          line: { color: '#dc2626', width: 3 } }
      ];
    }
    var layout = {
      xaxis: { title: 'x', range: [-6, 6] },
      yaxis: { title: 'density', range: [0, 1.4] },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      bargap: 0.05,
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    function render() {
      var mu = parseFloat(document.getElementById('viz1-mu-slider').value);
      var sigma = parseFloat(document.getElementById('viz1-sigma-slider').value);
      var n = parseInt(document.getElementById('viz1-n-slider').value);
      document.getElementById('viz1-mu').textContent = mu.toFixed(1);
      document.getElementById('viz1-sigma').textContent = sigma.toFixed(2);
      document.getElementById('viz1-n').textContent = n;
      Plotly.react('viz1', plot(mu, sigma, n), layout);
    }
    Plotly.newPlot('viz1', plot(0, 1, 500), layout, { responsive: true, displayModeBar: false });
    ['viz1-mu-slider', 'viz1-sigma-slider', 'viz1-n-slider'].forEach(function (id) {
      document.getElementById(id).addEventListener('input', render);
    });
    document.getElementById('viz1-resample').addEventListener('click', render);
  }
  init();
})();
</script>

> **សង្កេត៖** ពេល $n$ តូច (eg. 50), histogram លំអៀង​ខ្លាំង​ពី PDF។ ពេល $n$ ធំ (eg. 5000), histogram ចូល​ជិត PDF ល្អ — នេះ​ជា **law of large numbers**។

## ៣. តម្លៃ​សង្ឃឹម និង​វ៉ារ្យង់

$$
\mathbb{E}[X] = \mu = \sum_i x_i P(x_i) \quad \text{or} \quad \int x f(x) \, dx
$$

$$
\text{Var}(X) = \sigma^2 = \mathbb{E}\!\left[(X - \mu)^2\right] = \mathbb{E}[X^2] - \mu^2
$$

លក្ខណៈ​សំខាន់ៗ៖
- **Linearity**: $\mathbb{E}[aX + bY] = a \mathbb{E}[X] + b \mathbb{E}[Y]$ (តែង​តែ​ពិត)
- **Variance**: $\text{Var}(aX) = a^2 \text{Var}(X)$
- បើ $X, Y$ ឯករាជ្យ៖ $\text{Var}(X + Y) = \text{Var}(X) + \text{Var}(Y)$

## ៤. ប្រូបាប៊ីលីតេ​លក្ខខណ្ឌ និង​ច្បាប់ Bayes

**ប្រូបាប៊ីលីតេ​លក្ខខណ្ឌ**៖

$$
P(A \mid B) = \frac{P(A, B)}{P(B)} \quad (P(B) > 0)
$$

ពី​នេះ​ទាញ​បាន **ច្បាប់ Bayes**៖

$$
\boxed{\;\; P(A \mid B) = \frac{P(B \mid A) \, P(A)}{P(B)} \;\;}
$$

ឈ្មោះ​ផ្នែក​ផ្សេងៗ៖
- $P(A)$ = **prior** (ការ​ជឿ​ជាក់​មុន)
- $P(B \mid A)$ = **likelihood** (ភ័ស្តុតាង​ស្ថិត​ក្នុង model)
- $P(A \mid B)$ = **posterior** (ការ​ជឿ​ជាក់​បន្ទាប់​ពី​ឃើញ​ភ័ស្តុតាង)
- $P(B)$ = **evidence** (សម្រាប់ normalization)

## 🎮 រូបភាព interactive ២៖ ច្បាប់ Bayes ជាមួយ​តេស្ត COVID

ស្ថានភាព៖ អ្នក​ធ្វើ​តេស្ត COVID ហើយ​បាន​លទ្ធផល **វិជ្ជមាន**។ តើ​ប្រូបាប៊ីលីតេ​ដែល​អ្នក​ឆ្លង​ពិត​ប្រាកដ​មាន​ប៉ុនណា?

ផ្លាស់ slider ​សម្រាប់៖
- **Prior** = ប្រូបាប៊ីលីតេ​នៃ​ការ​ឆ្លង​មុន​តេស្ត (eg. 1% ក្នុង​សហគមន៍​ធម្មតា, 30% ក្នុង​ករណី​មាន​រោគ​សញ្ញា)
- **Sensitivity** = $P(\text{positive} \mid \text{infected})$
- **Specificity** = $P(\text{negative} \mid \text{healthy})$

<div id="viz2" style="width:100%;max-width:800px;margin:0 auto;height:380px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  Prior P(ឆ្លង) = <span id="viz2-prior" style="font-weight:bold;color:#dc2626">1.0%</span>
  <input id="viz2-prior-slider" type="range" min="0.001" max="0.5" step="0.001" value="0.01" style="width:60%;max-width:500px"><br>
  Sensitivity = <span id="viz2-sens" style="font-weight:bold;color:#0f766e">95.0%</span>
  <input id="viz2-sens-slider" type="range" min="0.5" max="1" step="0.005" value="0.95" style="width:60%;max-width:500px"><br>
  Specificity = <span id="viz2-spec" style="font-weight:bold;color:#7c3aed">99.0%</span>
  <input id="viz2-spec-slider" type="range" min="0.5" max="1" step="0.005" value="0.99" style="width:60%;max-width:500px"><br>
  <span style="font-size:1.15em;font-weight:bold">
    P(ឆ្លង | positive) = <span id="viz2-post" style="color:#dc2626">48.7%</span>
  </span>
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    function bayes(prior, sens, spec) {
      var p_pos = sens * prior + (1 - spec) * (1 - prior);
      return sens * prior / p_pos;
    }
    function plot(prior, sens, spec) {
      var priors = [];
      for (var p = 0.001; p <= 0.501; p += 0.005) priors.push(p);
      var posteriors = priors.map(function (p) { return bayes(p, sens, spec); });
      var current = bayes(prior, sens, spec);
      return [
        { x: priors.map(function (p) { return p * 100; }),
          y: posteriors.map(function (p) { return p * 100; }),
          mode: 'lines', name: 'P(infected | positive)',
          line: { color: '#1e40af', width: 3 } },
        { x: [prior * 100], y: [current * 100],
          mode: 'markers', name: 'current',
          marker: { color: '#dc2626', size: 16, line: { color: '#7f1d1d', width: 2 } } },
        { x: priors.map(function (p) { return p * 100; }),
          y: priors.map(function (p) { return p * 100; }),
          mode: 'lines', name: 'y = x (no info)',
          line: { color: '#9ca3af', width: 1.5, dash: 'dot' } }
      ];
    }
    var layout = {
      xaxis: { title: 'Prior P(infected) %', range: [0, 50] },
      yaxis: { title: 'Posterior P(infected | positive) %', range: [0, 100] },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    Plotly.newPlot('viz2', plot(0.01, 0.95, 0.99), layout, { responsive: true, displayModeBar: false });
    function render() {
      var prior = parseFloat(document.getElementById('viz2-prior-slider').value);
      var sens = parseFloat(document.getElementById('viz2-sens-slider').value);
      var spec = parseFloat(document.getElementById('viz2-spec-slider').value);
      document.getElementById('viz2-prior').textContent = (prior * 100).toFixed(1) + '%';
      document.getElementById('viz2-sens').textContent = (sens * 100).toFixed(1) + '%';
      document.getElementById('viz2-spec').textContent = (spec * 100).toFixed(1) + '%';
      var post = bayes(prior, sens, spec);
      document.getElementById('viz2-post').textContent = (post * 100).toFixed(1) + '%';
      Plotly.react('viz2', plot(prior, sens, spec), layout);
    }
    ['viz2-prior-slider', 'viz2-sens-slider', 'viz2-spec-slider'].forEach(function (id) {
      document.getElementById(id).addEventListener('input', render);
    });
  }
  init();
})();
</script>

> **លទ្ធផល​គួរ​ឱ្យ​ភ្ញាក់​ផ្អើល៖** ទោះ​បី​ជា​តេស្ត​មាន sensitivity 95% និង specificity 99%, បើ prior តូច (1%), posterior មាន​តែ ≈ 49% ប៉ុណ្ណោះ! សូម្បី​តែ​លទ្ធផល​វិជ្ជមាន​មិន​មាន​ន័យ​ថា​អ្នក​ឆ្លង​ច្បាស់​ទេ — ប្រាប់​ហេតុ​ដែល​ត្រូវ​ធ្វើ​តេស្ត​លើក​ទីពីរ។

## ៥. ឯករាជ្យ និង​ការ​ចែក​ចាយ​សហ​ការ

$X, Y$ **ឯករាជ្យ** បើ៖

$$
P(X = x, Y = y) = P(X = x) \cdot P(Y = y) \quad \forall x, y
$$

ឬ​ដូច​គ្នា៖ $P(X \mid Y) = P(X)$ — ​ការ​ដឹង $Y$ មិន​ផ្លាស់​ប្ដូរ​ការ​ជឿ​ជាក់​លើ $X$។

**ឯករាជ្យ​លក្ខខណ្ឌ** (conditional independence)៖

$$
P(X, Y \mid Z) = P(X \mid Z) P(Y \mid Z)
$$

នេះ​ជា​មូលដ្ឋាន​នៃ **Naive Bayes** (មេរៀន​ជំពូក 11) ដែល​ឧបមា​ថា​ feature ទាំង​អស់​ឯករាជ្យ​លក្ខខណ្ឌ​លើ class។

## 🎮 រូបភាព interactive ៣៖ ការ​ចែក​ចាយ​សហ​ការ និង marginal

ឧបមា​យើង​មាន​ទិន្នន័យ​អ្នក​ដំណើរ​ Phnom Penh៖ $X$ = ​មធ្យោបាយ​ (TukTuk, Moto, Car), $Y$ = ​អាកាស​ធាតុ (ភ្លៀង, មិន​ភ្លៀង)។ Slider ផ្ដល់​ឱ្យ​អ្នក​នូវ joint table; មើល marginal និង conditional។

<div id="viz3" style="width:100%;max-width:800px;margin:0 auto;height:380px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  P(ភ្លៀង) = <span id="viz3-rain" style="font-weight:bold;color:#1e40af">30%</span>
  <input id="viz3-rain-slider" type="range" min="0.05" max="0.7" step="0.01" value="0.3" style="width:50%;max-width:400px"><br>
  P(TukTuk | ភ្លៀង) = <span id="viz3-tuk-rain" style="font-weight:bold;color:#dc2626">15%</span>
  <input id="viz3-tukrain-slider" type="range" min="0.05" max="0.6" step="0.01" value="0.15" style="width:50%;max-width:400px"><br>
  P(TukTuk | មិន​ភ្លៀង) = <span id="viz3-tuk-norain" style="font-weight:bold;color:#0f766e">40%</span>
  <input id="viz3-tuknorain-slider" type="range" min="0.05" max="0.7" step="0.01" value="0.4" style="width:50%;max-width:400px">
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    function plot(pRain, pTukGivenRain, pTukGivenNoRain) {
      // assume P(Moto | rain) = 0.6 * (1 - P(Tuk|rain)), rest is Car
      var pNoRain = 1 - pRain;
      var pMotoGivenRain = 0.6 * (1 - pTukGivenRain);
      var pCarGivenRain  = 1 - pTukGivenRain - pMotoGivenRain;
      var pMotoGivenNoRain = 0.6 * (1 - pTukGivenNoRain);
      var pCarGivenNoRain  = 1 - pTukGivenNoRain - pMotoGivenNoRain;
      var joint = [
        [pTukGivenRain * pRain,   pMotoGivenRain * pRain,   pCarGivenRain * pRain],
        [pTukGivenNoRain * pNoRain, pMotoGivenNoRain * pNoRain, pCarGivenNoRain * pNoRain]
      ];
      var modes = ['TukTuk', 'Moto', 'Car'];
      var weather = ['ភ្លៀង', 'មិន​ភ្លៀង'];
      var text = joint.map(function (row) {
        return row.map(function (v) { return (v * 100).toFixed(1) + '%'; });
      });
      return {
        traces: [{
          type: 'heatmap',
          x: modes, y: weather, z: joint,
          colorscale: 'Purples', showscale: true,
          text: text, texttemplate: '%{text}',
          textfont: { size: 16, weight: 700, color: '#0f172a' },
          hovertemplate: 'P(%{x}, %{y}) = %{z:.3f}<extra></extra>'
        }],
        marginalTuk: joint[0][0] + joint[1][0],
        marginalRain: joint[0][0] + joint[0][1] + joint[0][2]
      };
    }
    var layout = {
      xaxis: { title: 'មធ្យោបាយ X' },
      yaxis: { title: 'អាកាស​ធាតុ Y' },
      margin: { t: 30, b: 60, l: 90, r: 60 },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)',
      annotations: [
        { text: 'Joint distribution P(X, Y) — sum = 1', xref: 'paper', yref: 'paper',
          x: 0.5, y: 1.08, showarrow: false, font: { size: 14, weight: 700 } }
      ]
    };
    var d = plot(0.3, 0.15, 0.4);
    Plotly.newPlot('viz3', d.traces, layout, { responsive: true, displayModeBar: false });
    function render() {
      var pRain = parseFloat(document.getElementById('viz3-rain-slider').value);
      var pTukRain = parseFloat(document.getElementById('viz3-tukrain-slider').value);
      var pTukNoRain = parseFloat(document.getElementById('viz3-tuknorain-slider').value);
      document.getElementById('viz3-rain').textContent = (pRain * 100).toFixed(0) + '%';
      document.getElementById('viz3-tuk-rain').textContent = (pTukRain * 100).toFixed(0) + '%';
      document.getElementById('viz3-tuk-norain').textContent = (pTukNoRain * 100).toFixed(0) + '%';
      var d = plot(pRain, pTukRain, pTukNoRain);
      Plotly.react('viz3', d.traces, layout);
    }
    ['viz3-rain-slider', 'viz3-tukrain-slider', 'viz3-tuknorain-slider'].forEach(function (id) {
      document.getElementById(id).addEventListener('input', render);
    });
  }
  init();
})();
</script>

> **សង្កេត៖**
> - **Marginal** P(TukTuk) = ផល​បូក​ជួរ​ដេក = P(TukTuk, ភ្លៀង) + P(TukTuk, មិន​ភ្លៀង)
> - **Conditional** P(TukTuk | ភ្លៀង) = P(TukTuk, ភ្លៀង) / P(ភ្លៀង)
> - បើ P(TukTuk | ភ្លៀង) = P(TukTuk | មិន​ភ្លៀង), នោះ **X និង Y ឯករាជ្យ**

---

# ឧទាហរណ៍

**ឧទាហរណ៍ ១៖ ច្បាប់ Bayes ដោយ​ដៃ** — តេស្ត COVID

ឱ្យ:
- $P(\text{infected}) = 0.01$ (1% prior)
- $P(\text{positive} \mid \text{infected}) = 0.95$ (sensitivity)
- $P(\text{negative} \mid \text{healthy}) = 0.99 \Rightarrow P(\text{positive} \mid \text{healthy}) = 0.01$

គណនា $P(\text{positive})$ ដោយ​ច្បាប់ total probability៖

$$
P(\text{positive}) = P(\text{pos} \mid \text{inf}) P(\text{inf}) + P(\text{pos} \mid \text{healthy}) P(\text{healthy})
$$

$$
= 0.95 \cdot 0.01 + 0.01 \cdot 0.99 = 0.0095 + 0.0099 = 0.0194
$$

ច្បាប់ Bayes៖

$$
P(\text{infected} \mid \text{positive}) = \frac{0.95 \cdot 0.01}{0.0194} = \frac{0.0095}{0.0194} \approx 0.4897
$$

ដូច្នេះ ≈ **49% ប៉ុណ្ណោះ** — ​មិន​មែន 95% ឡើយ!

**ឧទាហរណ៍ ២៖ តម្លៃ​សង្ឃឹម​នៃ​គ្រាប់​ឡុក​ឡាក់**

$$
\mathbb{E}[X] = \sum_{x=1}^{6} x \cdot \frac{1}{6} = \frac{1+2+3+4+5+6}{6} = \frac{21}{6} = 3.5
$$

---

# កូដ Python

## Sample និង​គណនា​លក្ខណៈ​ស្ថិតិ

```python
import numpy as np

# Gaussian samples
np.random.seed(42)
samples = np.random.normal(loc=170, scale=8, size=10000)  # height in cm

print('Sample mean    :', samples.mean())     # ≈ 170
print('Sample std     :', samples.std())      # ≈ 8
print('P(height > 180):', np.mean(samples > 180))  # ≈ 0.106
```

## ច្បាប់ Bayes ដោយ​ផ្ទាល់

```python
def bayes(prior, likelihood, false_positive_rate):
    """
    prior              = P(A)
    likelihood         = P(B | A)         e.g. sensitivity
    false_positive_rate = P(B | not A)    e.g. 1 - specificity
    Returns posterior  = P(A | B)
    """
    evidence = likelihood * prior + false_positive_rate * (1 - prior)
    return likelihood * prior / evidence

# COVID test, sensitivity 95%, specificity 99%
print(bayes(prior=0.01, likelihood=0.95, false_positive_rate=0.01))
# ≈ 0.4897
```

## Bernoulli, Categorical, Gaussian ជា​ស្តង់​ដារ

```python
from scipy import stats

# Bernoulli (coin)
coin = stats.bernoulli(0.7)
print(coin.rvs(size=10))   # samples [1 1 0 1 1 1 0 1 1 1]
print(coin.pmf(1))         # 0.7

# Categorical (dice with biased weights)
probs = [0.1, 0.1, 0.2, 0.2, 0.2, 0.2]
print(np.random.choice([1,2,3,4,5,6], p=probs, size=5))

# Gaussian
gauss = stats.norm(loc=170, scale=8)
print(gauss.pdf(180))      # density at 180
print(gauss.cdf(180))      # P(X <= 180) ≈ 0.894
```

---

# ការអនុវត្តន៍ជាក់ស្ដែង

**ច្បាប់ Bayes ​ក្នុង​ឧស្សាហកម្ម​នៅ​កម្ពុជា៖**

- **Acleda / ABA Mobile fraud detection** — តើ​ការ​ប្រតិបត្តិការ $T$ គឺ fraud ដោយ​ឱ្យ pattern ដែល​ឃើញ? $P(\text{fraud} \mid T) = P(T \mid \text{fraud}) P(\text{fraud}) / P(T)$
- **Spam filter ក្នុង email Khmer NGO** — Naive Bayes ប្រើ​ជាមួយ keyword: $P(\text{spam} \mid \text{words}) \propto P(\text{words} \mid \text{spam}) P(\text{spam})$
- **Khmer OCR confidence** — តើ​ឆ្នាំ​ផ្ទាំង​ដែល​ស្កេន​ហើយ​ស្គាល់​ថា "ក" ត្រឹមត្រូវ​ប៉ុនណា? Bayes ផ្ដល់​ posterior លើ​អក្សរ​នីមួយៗ
- **Khmer NLP language model** — GPT/transformer ត្រូវ​ប៉ាន់ $P(\text{next word} \mid \text{previous words})$ — នេះ​គឺ​ការ​ចែក​ចាយ​លក្ខខណ្ឌ​ដ៏​ធំ
- **AMK loan default prediction** — $P(\text{default} \mid \text{features})$ មាន​ Bayes នៅ​ក្នុង logistic regression (មេរៀន​ជំពូក 14)

**ហេតុ​អ្វី​បាន​ជា Gaussian ច្រើន?**

Gaussian មាន​លក្ខណៈ​សំខាន់​បំផុត​មួយ​ដែល​ការ​ចែក​ចាយ​ផ្សេង​ៗ​មិន​មាន៖
- **Sum នៃ​អថេរ​ Gaussian នៅ​តែ​ជា Gaussian**
- **Conditional នៃ Gaussian នៅ​តែ Gaussian**
- **Maximum entropy distribution សម្រាប់ mean និង variance ឱ្យ**

នេះ​ហើយ​ជា​ហេតុ​ដែល Gaussian ស្ថិត​នៅ​គ្រប់​ទីកន្លែង​ក្នុង ML៖ Gaussian Mixture Model, Gaussian Process, Variational Autoencoder, Diffusion Model។

---

# លំហាត់

1. គ្រាប់​ឡុក​ឡាក់​ដែល​មិន​យុត្តិធម៌​មួយ​មាន $P(1) = 0.4$ និង​​លេខ​ផ្សេងៗ​មាន​ប្រូបាប៊ីលីតេ​ស្មើ​គ្នា។ គណនា $P(2)$ និង $\mathbb{E}[X]$។
2. **Bayes**៖ ប្រអប់​ A មាន​ប៊ូល​ក្រហម 3 និង​ខៀវ 2។ ប្រអប់ B មាន​ប៊ូល​ក្រហម 1 និង​ខៀវ 4។ អ្នក​ជ្រើស​ប្រអប់​ដោយ​ចៃ​ដន្យ (50/50) រួច​ហូត​ប៊ូល 1 — ចេញ​ក្រហម។ តើ $P(\text{box A} \mid \text{red})$ ប៉ុនណា?
3. **ប្រើ​រូបភាព interactive ២**៖ រក prior ដែល​ធ្វើ​ឱ្យ posterior ≥ 95% (ដោយ​ប្រើ sensitivity = 95%, specificity = 99%)។ តើ​ការ​ធ្វើ​តេស្ត​លើក​ទីពីរ (ឱ្យ posterior ដំបូង​ជា prior ថ្មី) ​ឱ្យ​ posterior ប៉ុនណា?

> **ចម្លើយ៖**
> (1) លេខ 2-6 មាន $P = (1 - 0.4)/5 = 0.12$ ​ដូច​គ្នា។ $\mathbb{E}[X] = 0.4 \cdot 1 + 0.12 \cdot (2+3+4+5+6) = 0.4 + 2.4 = 2.8$
> (2) $P(\text{red} \mid A) = 3/5$, $P(\text{red} \mid B) = 1/5$, $P(\text{red}) = 0.5 \cdot 0.6 + 0.5 \cdot 0.2 = 0.4$។ Bayes: $P(A \mid \text{red}) = 0.5 \cdot 0.6 / 0.4 = \mathbf{0.75}$
> (3) Prior ≈ 17% → posterior 95%។ ការ​តេស្ត​លើក​ទីពីរ (prior = 0.487 → posterior) ≈ **99%** — ​នេះ​ជា​ហេតុ​ដែល​ត្រូវ​ធ្វើ​តេស្ត​ច្រើន​លើក

---

**មេរៀន​បន្ទាប់ (ជំពូក 4):** MLE និង MAP — ការ​ប្រើ​ប្រូបាប៊ីលីតេ​ដើម្បី​ "រៀន" ប៉ារ៉ាម៉ែត្រ​ពី​ទិន្នន័យ។ យើង​នឹង​ឃើញ​ហេតុ​ដែល linear regression ដោះស្រាយ​ MSE ត្រូវ​នឹង Gaussian MLE, ហើយ regularization ត្រូវ​នឹង MAP។
