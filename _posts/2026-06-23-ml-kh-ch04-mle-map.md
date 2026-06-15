---
layout: post
title: "[ML Khmer] ជំពូក 4: MLE និង MAP — ការ​ប៉ាន់​ប្រមាណ​ប៉ារ៉ាម៉ែត្រ"
date: 2026-06-23 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, math, probability, mle, map, bayesian, interactive]
thumbnail: /images/ml-series/ch04-mle-map.svg
---

នៅ​មេរៀន​មុន យើង​បាន​សិក្សា​ប្រូបាប៊ីលីតេ — ភាសា​នៃ​ភាព​មិន​ច្បាស់​លាស់។ ​មេរៀន​នេះ​យើង​ប្រើ​ភាសា​នោះ​ដើម្បី​ឆ្លើយ​សំណួរ​ស្នូល​នៃ ML ៖ **ឱ្យ​ទិន្នន័យ $D$ មក​ហើយ — តើ​ប៉ារ៉ាម៉ែត្រ $\theta$ ​ល្អ​បំផុត​មាន​តម្លៃ​ប៉ុនណា?** សំណួរ​នេះ​មាន​ចម្លើយ​ពីរ​ប្រភេទ​សំខាន់៖ **MLE** (Maximum Likelihood Estimation) និង **MAP** (Maximum A Posteriori)។ MLE មើល​តែ​ទិន្នន័យ; MAP បន្ថែម **prior** — ការ​ជឿ​ជាក់​មុន​មើល​ទិន្នន័យ។ មាន **រូបភាព interactive ៣**៖ MLE លើ​កាក់, MAP ​ជាមួយ Beta prior, ​និង Gaussian MLE​ ជាមួយ​ទិន្នន័យ​​កម្ពុជា។

---

# សង្ខេប

- **MLE**៖ $\theta_{\text{MLE}} = \arg\max_\theta P(D \mid \theta)$ — ជ្រើស $\theta$ ដែល​ធ្វើ​ឱ្យ​ទិន្នន័យ​ដែល​ឃើញ​មាន​ឱកាស​កើត​ច្រើន​បំផុត
- **MAP**៖ $\theta_{\text{MAP}} = \arg\max_\theta P(D \mid \theta) \, P(\theta)$ — បន្ថែម prior $P(\theta)$ លើ MLE
- ​សម្រាប់​ Bernoulli ៖ MLE $\hat{p} = k/n$ (ភាគ​រយ​មុខ); MAP ជាមួយ Beta(α, β) prior ៖ $\hat{p} = (k + \alpha - 1) / (n + \alpha + \beta - 2)$
- ​សម្រាប់ Gaussian ៖ MLE $\hat{\mu}$ = sample mean, $\hat{\sigma}^2$ = sample variance (mle ប្រើ $n$ មិន​មែន $n-1$)
- **Linear regression ↔ Gaussian MLE**; **Ridge regression ↔ Gaussian MAP** — ​យើង​នឹង​ឃើញ​ក្នុង​មេរៀន​ក្រោយ

---

# ហេតុអ្វីសំខាន់?

ML គឺ​ការ "**រៀន**" — តែ​ការ​រៀន​មាន​ន័យ​យ៉ាង​ណា? ​មាន​ន័យ​ថា៖ **ឱ្យ​ទិន្នន័យ​មក, រក​ប៉ារ៉ាម៉ែត្រ​ដែល​សម​បំផុត**។ ប៉ុន្តែ "សម​បំផុត" តាម​ស្តង់​ដារ​អ្វី?

- **MLE** ឆ្លើយ​ថា៖ ​សម​បំផុត = ធ្វើ​ឱ្យ​ទិន្នន័យ​ដែល​ឃើញ​ហើយ​មាន​ប្រូបាប៊ីលីតេ​ខ្ពស់​បំផុត
- **MAP** ឆ្លើយ​ថា៖ ​សម​បំផុត = ​ផ្គូផ្គង​ទាំង​ទិន្នន័យ និង​ការ​ជឿ​ជាក់​មុន​របស់​យើង

ហេតុ​ដែល​សំខាន់​ខ្លាំង​ខាង​ឧស្សាហកម្ម៖

- **Linear regression** ដែល​ដោះស្រាយ​ MSE — ​នោះ​គឺ​​ Gaussian MLE
- **Ridge regression** (L2 regularization) — នោះ​គឺ​ Gaussian MAP ជាមួយ Gaussian prior លើ weights
- **Lasso** (L1 regularization) — Gaussian MAP ជាមួយ Laplace prior
- **Naive Bayes ជាមួយ Laplace smoothing** — ​នោះ​គឺ MAP ជាមួយ Dirichlet prior
- **Logistic regression** — Bernoulli MLE លើ classification probability
- **Neural network training ដោយ cross-entropy** — Categorical MLE

ការ​យល់​ MLE/MAP ​ឱ្យ​អ្នក​ឃើញ​ថា **ស្ទើរ​តែ​គ្រប់ loss function** ​ដែល​អ្នក​ប្រើ​មាន​ឫស​ប្រូបាប៊ីលីតេ — មិន​មែន​គ្រាន់​តែ​ជា​រូប​មន្ត​អព្ភូត​ហេតុ​ទេ។

---

# ពាក្យបច្ចេកទេសថ្មី

| ខ្មែរ | English | កំណត់សម្គាល់ |
|---|---|---|
| ការ​ប៉ាន់​ប្រមាណ | estimation | រក​តម្លៃ​ប៉ារ៉ាម៉ែត្រ​ពី​ទិន្នន័យ |
| តម្លៃ​ប៉ាន់ | estimator | មុខងារ​ដែល​យក​ទិន្នន័យ → ប៉ារ៉ាម៉ែត្រ ($\hat\theta$) |
| Likelihood | likelihood | $P(D \mid \theta)$ — ប្រូបាប៊ីលីតេ​នៃ​ទិន្នន័យ​ឱ្យ $\theta$ |
| Log-likelihood | log-likelihood | $\ell(\theta) = \log P(D \mid \theta)$ |
| MLE | Maximum Likelihood Estimation | $\arg\max_\theta P(D \mid \theta)$ |
| MAP | Maximum A Posteriori | $\arg\max_\theta P(\theta \mid D)$ |
| Prior | prior | $P(\theta)$ — ការ​ជឿ​ជាក់​មុន​មើល​ទិន្នន័យ |
| Posterior | posterior | $P(\theta \mid D)$ — ការ​ជឿ​ជាក់​បន្ទាប់​ពី​ឃើញ​ទិន្នន័យ |
| Conjugate prior | conjugate prior | prior ដែល​ផ្ដល់​ posterior ​ក្នុង​ត្រកូល​ដូច​គ្នា |
| i.i.d. | independent and identically distributed | ឯករាជ្យ ​និង​​មាន​ការ​ចែក​ចាយ​ដូច​គ្នា |
| Regularization | regularization | ការ​បន្ថែម​ការ​ឃុំ​ឃាំង​ដើម្បី​កុំ​ឱ្យ overfit |

---

# គំនិតវិចារណញ្ញាណ

## MLE = "ទិន្នន័យ​នេះ​ត្រូវ​ស្ថិត​នៅ​កណ្ដាល​នៃ​អ្វី​ដែល​យើង​រំពឹង"

ឧបមា​អ្នក​ឃើញ​មុខ​មាន់​សុំ​អ្នក​បោះ​កាក់ 10 ដង ហើយ​ឃើញ​មុខ 7 ដង។ តើ​​ប្រូបាប៊ីលីតេ​ឱ្យ​មុខ​ប៉ុនណា?

MLE ​ឆ្លើយ​ដោយ "សុភវិវេក"៖ $\hat p = 7/10 = 0.7$។ ហេតុ​អ្វី? **ដោយ​សារ​ក្នុង​ចំណោម​តម្លៃ​ទាំង​អស់​នៃ $p$, $p = 0.7$ គឺ​ជា​តម្លៃ​ដែល​ធ្វើ​ឱ្យ​ការ​ឃើញ "មុខ 7 ដង​ក្នុង 10 ដង" មាន​ឱកាស​កើត​ច្រើន​បំផុត។**

## MAP = "ខ្ញុំ​មាន​ការ​ជឿ​ជាក់​មុន — ហើយ​ទិន្នន័យ​អាច​ផ្លាស់​ប្ដូរ​វា"

ប៉ុន្តែ​ឧបមា​ខ្ញុំ​បាន​ឃើញ​កាក់​នោះ​ហើយ — វា​មាន​មុខ​មាន់​ខាង​នេះ, ខ្នង​ខាង​នោះ — មិន​ខុស​ពី​កាក់​ធម្មតា​ទេ។ ​ការ​ជឿ​ជាក់​មុន​របស់​ខ្ញុំ៖ $p \approx 0.5$។ ឥឡូវ​ឃើញ​មុខ 7 ដង — ​ខ្ញុំ​នឹង​ផ្លាស់​ប្ដូរ​ការ​ជឿ​ជាក់​ខ្លះ, ប៉ុន្តែ​មិន​ដល់ 0.7 ភ្លាម​ទេ។ MAP ​ឆ្លើយ​ជា ​ឧទាហរណ៍ $\hat p \approx 0.6$ — ​នៅ​ចន្លោះ​ prior និង MLE។

ការ​ប្រៀប​ធៀប​សំខាន់៖

| លក្ខណៈ | MLE | MAP |
|---|---|---|
| ប្រើ prior? | ❌ | ✅ |
| ងាយ​ overfit? | ​ងាយ (ពេល $n$ តូច) | តិច​ជាង |
| ​ពេល $n \to \infty$ | ​ត្រូវ​នឹង​តម្លៃ​ពិត | ​ត្រូវ​នឹង​តម្លៃ​ពិត (prior បាត់​ឥទ្ធិពល) |
| ​​ត្រូវ​ការ​ជ្រើស? | ​មិន​ត្រូវ​ (តែ model) | ​ត្រូវ​ជ្រើស prior |

> **ឧបមេយ្យ៖** MLE ដូច​ជា​នាយក​សាលា​ដែល​សម្រេច​ដោយ​ផ្អែក​លើ​ការ​សាកល្បង​ឆ្នាំ​នេះ​ប៉ុណ្ណោះ។ MAP ដូច​ជា​នាយក​សាលា​ដែល​ផ្គូផ្គង​ទាំង​ការ​សាកល្បង​ឆ្នាំ​នេះ និង​ប្រវត្តិ​សិស្ស​នៅ​ឆ្នាំ​មុនៗ។ ពេល​ទិន្នន័យ​ឆ្នាំ​នេះ​តិច — ប្រវត្តិ​ជួយ​បំពេញ; ពេល​ទិន្នន័យ​ច្រើន — ​ប្រវត្តិ​មាន​ឥទ្ធិពល​តិច​ទៅៗ។

---

# និយមន័យ និងគណិតវិទ្យា

## ១. MLE — និយមន័យ​ផ្លូវការ

ឱ្យ​ទិន្នន័យ $D = \{x_1, x_2, \ldots, x_n\}$ ​ដែល i.i.d. ពី​ការ​ចែក​ចាយ​ដែល​មាន​ប៉ារ៉ាម៉ែត្រ $\theta$ ៖

$$
P(D \mid \theta) = \prod_{i=1}^n P(x_i \mid \theta)
$$

**MLE estimator**៖

$$
\boxed{\;\; \hat\theta_{\text{MLE}} = \arg\max_\theta \, \log P(D \mid \theta) = \arg\max_\theta \, \sum_{i=1}^n \log P(x_i \mid \theta) \;\;}
$$

ហេតុ​ដែល​ប្រើ log៖
- ​ផ្លាស់​ product → sum (មិន​ឱ្យ underflow ​ពេល $n$ ធំ)
- ​ងាយ​យក derivative
- ​ប្រូបាប៊ីលីតេ​អប្បបរមា​នៅ​តែ​ត្រូវ​នឹង log-likelihood អប្បបរមា (log គឺ monotonic)

## ២. MLE សម្រាប់ Bernoulli — ការ​បោះ​កាក់

ឱ្យ $x_i \in \{0, 1\}$ ជាមួយ $P(x = 1) = p$ ៖

$$
P(D \mid p) = \prod_{i=1}^n p^{x_i} (1-p)^{1-x_i} = p^k (1-p)^{n-k}
$$

ដោយ $k = \sum_i x_i$ = ចំនួន​មុខ។ យក log ៖

$$
\ell(p) = k \log p + (n-k) \log(1-p)
$$

យក derivative ​ស្មើ​នឹង 0 ៖

$$
\frac{d\ell}{dp} = \frac{k}{p} - \frac{n-k}{1-p} = 0
$$

​ដោះស្រាយ៖

$$
\boxed{\;\; \hat p_{\text{MLE}} = \frac{k}{n} \;\;}
$$

— ​ភាគ​រយ​មុខ​ជា​លំនាំ​ដ៏​សុភវិវេក!

## 🎮 រូបភាព interactive ១៖ Likelihood នៃ​កាក់

ប្ដូរ $n$ និង​ចំនួន​មុខ​ដែល​ឃើញ $k$ — ​ហើយ​មើល​ likelihood $L(p) = p^k(1-p)^{n-k}$ ជា​មុខងារ​នៃ $p$។ ចំណុច​ខ្ពស់​បំផុត​គឺ MLE។

<div id="viz1" style="width:100%;max-width:800px;margin:0 auto;height:420px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  n (ចំនួន​បោះ) = <span id="viz1-n" style="font-weight:bold;color:#1e40af">10</span>
  <input id="viz1-n-slider" type="range" min="2" max="200" step="1" value="10" style="width:40%;max-width:350px"><br>
  k (ចំនួន​មុខ) = <span id="viz1-k" style="font-weight:bold;color:#dc2626">7</span>
  <input id="viz1-k-slider" type="range" min="0" max="10" step="1" value="7" style="width:40%;max-width:350px"><br>
  <span style="font-size:1.1em">
    MLE: $\hat p$ = <span id="viz1-mle" style="font-weight:bold;color:#0f766e">0.700</span>
  </span>
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    function logLik(p, k, n) {
      if (p <= 0 || p >= 1) return -Infinity;
      return k * Math.log(p) + (n - k) * Math.log(1 - p);
    }
    function plot(n, k) {
      var ps = [];
      var lls = [];
      for (var p = 0.005; p <= 0.9951; p += 0.005) {
        ps.push(p);
        lls.push(logLik(p, k, n));
      }
      var maxLL = Math.max.apply(null, lls);
      var liks = lls.map(function (ll) { return Math.exp(ll - maxLL); });
      var mle = k / n;
      return [
        { x: ps, y: liks, mode: 'lines', name: 'normalized L(p)',
          fill: 'tozeroy', fillcolor: 'rgba(30, 64, 175, 0.18)',
          line: { color: '#1e40af', width: 3 } },
        { x: [mle, mle], y: [0, 1.05], mode: 'lines', name: 'MLE',
          line: { color: '#dc2626', width: 2.5, dash: 'dash' } },
        { x: [mle], y: [1.0], mode: 'markers+text', name: 'peak',
          marker: { color: '#dc2626', size: 14, line: { color: '#7f1d1d', width: 2 } },
          text: ['p̂ = ' + mle.toFixed(3)], textposition: 'top center',
          textfont: { size: 13, weight: 700, color: '#dc2626' } }
      ];
    }
    var layout = {
      xaxis: { title: 'p (true probability of heads)', range: [0, 1] },
      yaxis: { title: 'normalized likelihood', range: [0, 1.15] },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    Plotly.newPlot('viz1', plot(10, 7), layout, { responsive: true, displayModeBar: false });
    function render() {
      var n = parseInt(document.getElementById('viz1-n-slider').value);
      var kSlider = document.getElementById('viz1-k-slider');
      kSlider.max = n;
      var k = Math.min(parseInt(kSlider.value), n);
      kSlider.value = k;
      document.getElementById('viz1-n').textContent = n;
      document.getElementById('viz1-k').textContent = k;
      document.getElementById('viz1-mle').textContent = (k / n).toFixed(3);
      Plotly.react('viz1', plot(n, k), layout);
    }
    ['viz1-n-slider', 'viz1-k-slider'].forEach(function (id) {
      document.getElementById(id).addEventListener('input', render);
    });
  }
  init();
})();
</script>

> **សង្កេត៖** ពេល $n$ តូច (eg. 4) និង​អ្នក​ឃើញ 3 មុខ — MLE = 0.75, ​តែ​ខ្សែ​ likelihood ធំ​ទូលាយ — មាន​ភាព​មិន​ច្បាស់​លាស់​ច្រើន។ ពេល $n = 200$ ហើយ $k = 140$ — MLE = 0.7 ​ហើយ​ខ្សែ​ស្រួច​ខ្លាំង — យើង​ច្បាស់​ខ្លាំង។ ​នេះ​ហើយ​ហេតុ​ដែល​ទិន្នន័យ​ច្រើន​សំខាន់!

## ៣. MLE សម្រាប់ Gaussian

ឱ្យ $x_i \sim \mathcal{N}(\mu, \sigma^2)$ i.i.d. ៖

$$
\log P(D \mid \mu, \sigma^2) = -\frac{n}{2} \log(2\pi\sigma^2) - \frac{1}{2\sigma^2} \sum_{i=1}^n (x_i - \mu)^2
$$

យក derivative ​តាម $\mu$ ​ស្មើ​នឹង 0 ៖

$$
\hat\mu_{\text{MLE}} = \frac{1}{n} \sum_{i=1}^n x_i \quad (\text{sample mean})
$$

យក derivative ​តាម $\sigma^2$ ៖

$$
\hat\sigma^2_{\text{MLE}} = \frac{1}{n} \sum_{i=1}^n (x_i - \hat\mu)^2
$$

> **កំណត់​សម្គាល់៖** sample variance ដែល​យើង​ស្គាល់​នៅ​សាលា​ប្រើ $n-1$ (Bessel's correction) ​ដើម្បី​ឱ្យ unbiased។ MLE estimator ប្រើ $n$ ហើយ​ជា​ **biased** តិច​​បន្តិច — ប៉ុន្តែ​ផ្គូផ្គង likelihood ​ត្រឹមត្រូវ។

## ៤. MAP — និយមន័យ​ផ្លូវការ

ច្បាប់​ Bayes ​លើ $\theta$ ៖

$$
P(\theta \mid D) = \frac{P(D \mid \theta) \, P(\theta)}{P(D)}
$$

ដោយ $P(D)$ មិន​អាស្រ័យ​លើ $\theta$ ៖

$$
\boxed{\;\; \hat\theta_{\text{MAP}} = \arg\max_\theta \big[ \log P(D \mid \theta) + \log P(\theta) \big] \;\;}
$$

ផ្លាស់​ MLE មក​ MAP = **បន្ថែម​ពាក្យ​ regularization $\log P(\theta)$**​!

## ៥. MAP សម្រាប់ Bernoulli ​ជាមួយ Beta prior

ឧបមា​យើង​ប្រើ prior $p \sim \text{Beta}(\alpha, \beta)$ ៖

$$
P(p) \propto p^{\alpha - 1} (1 - p)^{\beta - 1}
$$

Posterior ៖

$$
P(p \mid D) \propto p^{k + \alpha - 1} (1 - p)^{n - k + \beta - 1}
$$

​នេះ​នៅ​តែ Beta — ​ដូច្នេះ Beta គឺ **conjugate prior** សម្រាប់ Bernoulli! យក​ argmax ៖

$$
\boxed{\;\; \hat p_{\text{MAP}} = \frac{k + \alpha - 1}{n + \alpha + \beta - 2} \;\;}
$$

ករណី​ដែល​​សំខាន់៖
- $\alpha = \beta = 1$ (uniform prior) → MAP = MLE = $k/n$ — prior មិន​មាន​ឥទ្ធិពល
- $\alpha = \beta = 2$ → MAP = $(k + 1)/(n + 2)$ — **Laplace smoothing**! (ច្បាប់​ដែល Naive Bayes ​ប្រើ)
- $\alpha = \beta$ ធំ → ​ផ្ដោត​ច្រើន​លើ 0.5 — ​ត្រូវ​ការ​ទិន្នន័យ​ច្រើន​ដើម្បី​ផ្លាស់​ប្ដូរ

## 🎮 រូបភាព interactive ២៖ MAP ជាមួយ Beta prior

ឧបមា​យើង​ប៉ាន់​ប្រូបាប៊ីលីតេ​ដែល​អ្នក​បើក​​ TukTuk នៅ Phnom Penh ​យល់​ព្រម​ទទួល​យក Bakong (mobile payment)។ យើង​សួរ $n$ នាក់ ហើយ $k$ នាក់​យល់​ព្រម។ Slider ​សម្រាប់​ $\alpha, \beta$ ​ឱ្យ​អ្នក​ឃើញ​ MAP ​ផ្លាស់​ប្ដូរ។

<div id="viz2" style="width:100%;max-width:800px;margin:0 auto;height:420px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  n = <span id="viz2-n" style="font-weight:bold;color:#1e40af">12</span>
  <input id="viz2-n-slider" type="range" min="2" max="100" step="1" value="12" style="width:40%;max-width:350px">
  &nbsp;&nbsp;
  k = <span id="viz2-k" style="font-weight:bold;color:#dc2626">8</span>
  <input id="viz2-k-slider" type="range" min="0" max="12" step="1" value="8" style="width:40%;max-width:350px"><br>
  α = <span id="viz2-alpha" style="font-weight:bold;color:#7c3aed">5</span>
  <input id="viz2-alpha-slider" type="range" min="1" max="30" step="0.5" value="5" style="width:40%;max-width:350px">
  &nbsp;&nbsp;
  β = <span id="viz2-beta" style="font-weight:bold;color:#0f766e">5</span>
  <input id="viz2-beta-slider" type="range" min="1" max="30" step="0.5" value="5" style="width:40%;max-width:350px"><br>
  <span style="font-size:1.05em">
    MLE = <span id="viz2-mle" style="font-weight:bold;color:#1e40af">0.667</span>
    &nbsp;|&nbsp;
    MAP = <span id="viz2-map" style="font-weight:bold;color:#dc2626">0.600</span>
  </span>
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    function logBetaPdf(p, a, b) {
      if (p <= 0 || p >= 1) return -Infinity;
      return (a - 1) * Math.log(p) + (b - 1) * Math.log(1 - p);
    }
    function plot(n, k, alpha, beta) {
      var ps = [];
      var prior = [];
      var lik = [];
      var post = [];
      for (var p = 0.005; p <= 0.9951; p += 0.005) {
        ps.push(p);
        prior.push(logBetaPdf(p, alpha, beta));
        lik.push(k * Math.log(p) + (n - k) * Math.log(1 - p));
        post.push(logBetaPdf(p, k + alpha, n - k + beta));
      }
      function normalize(arr) {
        var m = Math.max.apply(null, arr);
        return arr.map(function (v) { return Math.exp(v - m); });
      }
      var priorN = normalize(prior);
      var likN = normalize(lik);
      var postN = normalize(post);
      var mle = k / n;
      var map = (k + alpha - 1) / (n + alpha + beta - 2);
      return [
        { x: ps, y: priorN, mode: 'lines', name: 'prior',
          line: { color: '#7c3aed', width: 2.5, dash: 'dot' } },
        { x: ps, y: likN, mode: 'lines', name: 'likelihood',
          line: { color: '#1e40af', width: 2.5 } },
        { x: ps, y: postN, mode: 'lines', name: 'posterior',
          fill: 'tozeroy', fillcolor: 'rgba(220, 38, 38, 0.15)',
          line: { color: '#dc2626', width: 3 } },
        { x: [mle, mle], y: [0, 1.05], mode: 'lines', name: 'MLE',
          line: { color: '#1e40af', width: 2, dash: 'dash' }, showlegend: false },
        { x: [map, map], y: [0, 1.05], mode: 'lines', name: 'MAP',
          line: { color: '#dc2626', width: 2, dash: 'dash' }, showlegend: false }
      ];
    }
    var layout = {
      xaxis: { title: 'p', range: [0, 1] },
      yaxis: { title: 'normalized density', range: [0, 1.15] },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    Plotly.newPlot('viz2', plot(12, 8, 5, 5), layout, { responsive: true, displayModeBar: false });
    function render() {
      var n = parseInt(document.getElementById('viz2-n-slider').value);
      var kSlider = document.getElementById('viz2-k-slider');
      kSlider.max = n;
      var k = Math.min(parseInt(kSlider.value), n);
      kSlider.value = k;
      var alpha = parseFloat(document.getElementById('viz2-alpha-slider').value);
      var beta = parseFloat(document.getElementById('viz2-beta-slider').value);
      document.getElementById('viz2-n').textContent = n;
      document.getElementById('viz2-k').textContent = k;
      document.getElementById('viz2-alpha').textContent = alpha;
      document.getElementById('viz2-beta').textContent = beta;
      var mle = k / n;
      var map = (k + alpha - 1) / (n + alpha + beta - 2);
      document.getElementById('viz2-mle').textContent = mle.toFixed(3);
      document.getElementById('viz2-map').textContent = map.toFixed(3);
      Plotly.react('viz2', plot(n, k, alpha, beta), layout);
    }
    ['viz2-n-slider', 'viz2-k-slider', 'viz2-alpha-slider', 'viz2-beta-slider'].forEach(function (id) {
      document.getElementById(id).addEventListener('input', render);
    });
  }
  init();
})();
</script>

> **សង្កេត​សំខាន់៖**
> - តម្លៃ​ default ($n=12, k=8, \alpha=\beta=5$): MLE = 0.667 តែ MAP = 0.6 — ​prior ទាញ​ឆ្ពោះ​ទៅ 0.5
> - ​ប្រសិន​បើ​ប្ដូរ $n = 100, k = 67$ (ត្រូវ​ប្ដូរ​ slider សម្រាប់ $k$ ផង): MLE = 0.67 ហើយ MAP ≈ 0.65 — prior ​មាន​ឥទ្ធិពល​តិច​ទៅៗ​ពេល​ទិន្នន័យ​ច្រើន
> - ​ប្ដូរ $\alpha = 30, \beta = 30$ (prior​ខ្លាំង) ហើយ $n=12$ — MAP ≈ 0.55, ​ខិត​ជិត 0.5 ​ច្រើន
> - ​ប្ដូរ $\alpha = 1, \beta = 1$ (uniform) — MAP = MLE ច្បាស់ៗ!

## ៦. ការ​ភ្ជាប់​ MLE/MAP ជាមួយ Loss Function (preview)

នៅ​មេរៀន​ក្រោយ យើង​នឹង​បាន​ឃើញ៖

**Linear regression** ដែល​ឧបមា $y_i = w^\top x_i + \varepsilon_i$ ដែល $\varepsilon_i \sim \mathcal{N}(0, \sigma^2)$ — MLE ​លើ $w$ ​ផ្ដល់​៖

$$
\hat w_{\text{MLE}} = \arg\min_w \sum_i (y_i - w^\top x_i)^2 \quad (\text{MSE!})
$$

**Ridge regression** ដែល​បន្ថែម prior $w \sim \mathcal{N}(0, \tau^2 I)$ — MAP ​ផ្ដល់​៖

$$
\hat w_{\text{MAP}} = \arg\min_w \sum_i (y_i - w^\top x_i)^2 + \lambda \|w\|^2 \quad (\text{L2 regularization!})
$$

ដោយ $\lambda = \sigma^2/\tau^2$។ **Regularization មាន​ឫស​ជា prior!**

---

# ឧទាហរណ៍

**ឧទាហរណ៍ ១៖ Bakong adoption** — អ្នក​ស្ទង់ tuktuk driver 10 នាក់; 8 នាក់​យល់​ព្រម​ទទួល Bakong។ ប៉ាន់ p (ភាគ​រយ​​យល់​ព្រម​ទាំង​មូល)។

- **MLE**៖ $\hat p = 8/10 = 0.80$
- **MAP​ ជាមួយ Beta(2, 2)** (Laplace smoothing): $\hat p = (8 + 1) / (10 + 2) = 9/12 = 0.75$
- **MAP​ ជាមួយ Beta(10, 10)** (prior ខ្លាំង​ផ្ដោត​លើ 0.5): $\hat p = (8 + 9) / (10 + 18) = 17/28 \approx 0.61$

ការ​ជ្រើស prior ​ជា **ការ​សម្រេច​ចិត្ត​ខាង​ស្ថាបនិក** — តើ​អ្នក​ជឿ​ជាក់​ខ្លាំង​ប៉ុនណា​មុន​ឃើញ​ទិន្នន័យ?

**ឧទាហរណ៍ ២៖ Gaussian MLE** — ​អ្នក​វាស់​កម្ពស់​សិស្ស 5 នាក់​នៅ​សាលា​មួយ​​ ​បាន (in cm): 162, 168, 170, 173, 167។

- $\hat\mu = (162+168+170+173+167)/5 = 168.0$
- $\hat\sigma^2_{\text{MLE}} = ((162-168)^2 + (168-168)^2 + (170-168)^2 + (173-168)^2 + (167-168)^2)/5 = (36+0+4+25+1)/5 = 13.2$
- $\hat\sigma_{\text{MLE}} \approx 3.63$ cm

---

# កូដ Python

## MLE សម្រាប់ Bernoulli

```python
import numpy as np

def bernoulli_mle(data):
    """data: array of 0s and 1s"""
    return data.mean()

# 10 tuktuk drivers, 8 say yes to Bakong
data = np.array([1,1,1,1,1,1,1,1,0,0])
print('MLE p =', bernoulli_mle(data))   # 0.8
```

## MAP សម្រាប់ Bernoulli ​ជាមួយ Beta prior

```python
def bernoulli_map(data, alpha, beta):
    k = data.sum()
    n = len(data)
    return (k + alpha - 1) / (n + alpha + beta - 2)

# Strong prior centered at 0.5 (Beta(10, 10))
print('MAP p (strong prior) =', bernoulli_map(data, 10, 10))  # ~0.607
# Weak prior (Laplace smoothing, Beta(2, 2))
print('MAP p (Laplace)      =', bernoulli_map(data, 2, 2))    # 0.75
```

## Gaussian MLE

```python
heights = np.array([162, 168, 170, 173, 167])

mu_mle = heights.mean()
var_mle = ((heights - mu_mle) ** 2).mean()   # divide by n, not n-1
sigma_mle = np.sqrt(var_mle)

print(f'mu_mle    = {mu_mle:.2f}')        # 168.00
print(f'sigma_mle = {sigma_mle:.2f}')     # 3.63
```

## ការ​ភ្ជាប់ ​Ridge regression ↔ Gaussian MAP

```python
from sklearn.linear_model import LinearRegression, Ridge

X = np.random.randn(50, 3)
true_w = np.array([1.5, -2.0, 0.5])
y = X @ true_w + 0.5 * np.random.randn(50)

# MLE (no regularization)
print('MLE w:', LinearRegression().fit(X, y).coef_)

# MAP with Gaussian prior (Ridge)
print('MAP w (lambda=1.0):', Ridge(alpha=1.0).fit(X, y).coef_)
print('MAP w (lambda=10) :', Ridge(alpha=10).fit(X, y).coef_)   # shrunk
```

---

# ការអនុវត្តន៍ជាក់ស្ដែង

## 🎮 រូបភាព interactive ៣៖ Sample mean និង Sample size

ឧបមា​ល្បឿន​ខ្យល់​នៅ Phnom Penh ​ពេល​យប់​​មាន​ការ​ចែក​ចាយ $\mathcal{N}(\mu_{\text{true}}, 4^2)$ km/h។ Slider ​ឱ្យ​អ្នក​ប្ដូរ $\mu_{\text{true}}$ និង​ចំនួន​សំណាក $n$ — មើល​ MLE ($\hat\mu$ = sample mean) ផ្លាស់​ប្ដូរ​ប៉ុនណា។

<div id="viz3" style="width:100%;max-width:800px;margin:0 auto;height:420px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  μ_true = <span id="viz3-mu" style="font-weight:bold;color:#dc2626">15.0</span>
  <input id="viz3-mu-slider" type="range" min="5" max="30" step="0.5" value="15" style="width:40%;max-width:350px">
  &nbsp;&nbsp;
  n = <span id="viz3-n" style="font-weight:bold;color:#1e40af">20</span>
  <input id="viz3-n-slider" type="range" min="3" max="500" step="1" value="20" style="width:40%;max-width:350px"><br>
  <button id="viz3-resample" style="margin-top:6px;padding:4px 14px;font-weight:600;cursor:pointer">🎲 Re-sample</button><br>
  <span style="font-size:1.05em">
    μ_MLE (sample mean) = <span id="viz3-mle" style="font-weight:bold;color:#0f766e">15.00</span>
    &nbsp;|&nbsp;
    error = <span id="viz3-err" style="font-weight:bold;color:#7c3aed">0.00</span>
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
    function pdf(x, mu, sigma) {
      return Math.exp(-0.5 * Math.pow((x - mu) / sigma, 2)) / (sigma * Math.sqrt(2 * Math.PI));
    }
    var SIGMA = 4;
    function plot(muTrue, n) {
      var samples = [];
      for (var i = 0; i < n; i++) samples.push(muTrue + SIGMA * randn());
      var muMle = samples.reduce(function (s, x) { return s + x; }, 0) / n;
      var xs = [];
      for (var x = -5; x <= 45; x += 0.2) xs.push(x);
      var ysTrue = xs.map(function (x) { return pdf(x, muTrue, SIGMA); });
      return {
        traces: [
          { x: samples, type: 'histogram', name: 'samples',
            histnorm: 'probability density',
            xbins: { start: -5, end: 45, size: 1.0 },
            marker: { color: '#1e40af', opacity: 0.5 } },
          { x: xs, y: ysTrue, mode: 'lines', name: 'true N(μ, 16)',
            line: { color: '#dc2626', width: 3 } },
          { x: [muTrue, muTrue], y: [0, 0.15], mode: 'lines',
            line: { color: '#dc2626', width: 2.5, dash: 'dot' },
            name: 'μ_true' },
          { x: [muMle, muMle], y: [0, 0.15], mode: 'lines',
            line: { color: '#0f766e', width: 2.5, dash: 'dash' },
            name: 'μ_MLE' }
        ],
        mle: muMle
      };
    }
    var layout = {
      xaxis: { title: 'wind speed (km/h)', range: [-5, 45] },
      yaxis: { title: 'density', range: [0, 0.18] },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      bargap: 0.05,
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    var d = plot(15, 20);
    Plotly.newPlot('viz3', d.traces, layout, { responsive: true, displayModeBar: false });
    function render() {
      var mu = parseFloat(document.getElementById('viz3-mu-slider').value);
      var n = parseInt(document.getElementById('viz3-n-slider').value);
      document.getElementById('viz3-mu').textContent = mu.toFixed(1);
      document.getElementById('viz3-n').textContent = n;
      var d = plot(mu, n);
      document.getElementById('viz3-mle').textContent = d.mle.toFixed(2);
      document.getElementById('viz3-err').textContent = (d.mle - mu).toFixed(2);
      Plotly.react('viz3', d.traces, layout);
    }
    ['viz3-mu-slider', 'viz3-n-slider'].forEach(function (id) {
      document.getElementById(id).addEventListener('input', render);
    });
    document.getElementById('viz3-resample').addEventListener('click', render);
  }
  init();
})();
</script>

> **សង្កេត​៖** ពេល $n = 3$ — error អាច​ខ្ពស់​ដល់ $\pm 3$ km/h ងាយ; ពេល $n = 500$ — error ស្ទើរ​តែ​តែង​តែ​នៅ​ក្រោម $\pm 0.3$ km/h។ ​នេះ​ឆ្លុះ​បញ្ចាំង​ច្បាប់​ស្ថិតិ​ដ៏​សំខាន់៖ standard error of mean = $\sigma / \sqrt{n}$ — ​មាន​ន័យ​ថា​ដើម្បី​បន្ថយ error ​ពាក់​កណ្ដាល, ​ត្រូវ​ការ​ទិន្នន័យ​បួន​ដង​ច្រើន​ជាង។

## ​​ការ​ប្រើ​នៅ​​ឧស្សាហកម្ម​នៅ​កម្ពុជា

- **ABA / Acleda credit scoring** — MAP estimator ​លើ default probability, ប្រើ prior ​ពី​​ប្រវត្តិ​សិក្ស​ឆ្នាំ​មុនៗ ​ដើម្បី​បន្ថយ overfitting ពេល​ទិន្នន័យ​អតិថិជន​ថ្មី​មាន​តិច
- **Khmer language model fine-tuning** — pretrained model ​ដើរ​តួ​ជា prior; data ​ខ្មែរ​ថ្មី​​ដើរ​តួ​ជា likelihood; weighted MAP = ​ការ fine-tune
- **AMK microloan ​សម្រាប់​ឃុំ​ថ្មី** — ពេល​មាន​ទិន្នន័យ​តិច​ពី​ឃុំ​ថ្មី (eg. $n = 30$), MAP ​ដែល​ប្រើ prior ​ពី​ឃុំ​ស្រដៀង​គ្នា​ផ្ដល់​ការ​ប៉ាន់​ប្រសើរ​ជាង MLE
- **Cambodia COVID test calibration** — sensitivity និង specificity ​ត្រូវ​ប៉ាន់​ប្រមាណ​ពី​ការ​សាកល្បង​ខ្នាត​តូច; ​Beta prior ​ផ្ដល់​ឱ្យ​អ្នក​ ​ការ​ប៉ាន់​ដែល​មិន​ស្ថិត​នៅ 0 ឬ 1 ​ដាច់​ខាត
- **Khmer OCR character probabilities** — Naive Bayes ​ប្រើ Laplace smoothing (= MAP ​ជាមួយ Dirichlet prior) ​ដើម្បី​ជៀស​វាង $P(\text{char}) = 0$ ​សម្រាប់​អក្សរ​ដែល​មិន​ឃើញ​ក្នុង training set

## ​ហេតុ​ដែល​ MAP បាន​ក្លាយ​ជា regularization

ការ​ដឹង​នេះ​ផ្លាស់​ប្ដូរ​មុំ​មើល​របស់​អ្នក៖

| Loss / Method | ​ការ​ឆ្លុះ​បញ្ចាំង​ប្រូបាប៊ីលីតេ |
|---|---|
| MSE (linear regression) | Gaussian noise MLE |
| Cross-entropy (classifier) | Categorical MLE |
| L2 regularization (Ridge) | Gaussian prior MAP |
| L1 regularization (Lasso) | Laplace prior MAP |
| Early stopping | implicit regularization ≈ ​limited MAP |
| Dropout | approximate Bayesian model averaging |

​ស្ទើរ​តែ​គ្រប់ ML technique ​ដែល​អ្នក​ស្គាល់​មាន​ការ​បកស្រាយ​ប្រូបាប៊ីលីតេ។

---

# លំហាត់

1. **Bernoulli MLE**: អ្នក​បោះ​កាក់ 20 ​ដង — បាន​ខ្នង 13 ដង។ គណនា $\hat p_{\text{MLE}}$ សម្រាប់​ប្រូបាប៊ីលីតេ​នៃ "ខ្នង" (ខ្នង = 1)។
2. **MAP**: ​ដោយ​ប្រើ​​ទិន្នន័យ​ដូច​គ្នា​នឹង​លំហាត់ 1, គណនា $\hat p_{\text{MAP}}$ ជាមួយ Beta(3, 3) prior និង Beta(5, 1) prior។ ​ប្រៀប​ធៀប​លទ្ធផល​ទាំង​បី (MLE, MAP ជាមួយ​ prior ស្មើ​គ្នា, MAP ​ជាមួយ prior លំអៀង​ទៅ​មុខ)។
3. **Gaussian MLE​ ដោយ​ដៃ**: កម្ពស់​សិស្ស 4 នាក់ = 165, 170, 168, 172 cm។ គណនា $\hat\mu_{\text{MLE}}$ និង $\hat\sigma^2_{\text{MLE}}$។ ​បន្ទាប់​មក​គណនា​ sample variance unbiased (បែង​ដោយ $n-1$)។ ​តើ​លទ្ធផល​ខុស​គ្នា​យ៉ាង​ម៉េច​ដែរ?
4. **(ប្រឹង​ប្រែង)** ​ភ័ស្តុតាង​មើល​ការ​ភ្ជាប់ Ridge ↔ Gaussian MAP៖ ​ឧបមា $y_i = w^\top x_i + \varepsilon_i$ ដែល $\varepsilon \sim \mathcal{N}(0, \sigma^2)$ និង $w \sim \mathcal{N}(0, \tau^2 I)$។ បង្ហាញ​ថា $\hat w_{\text{MAP}} = \arg\min_w \sum_i (y_i - w^\top x_i)^2 + \lambda \|w\|^2$ ​ដោយ $\lambda = \sigma^2/\tau^2$។

> **ចម្លើយ៖**
> (1) $\hat p_{\text{MLE}} = 13/20 = 0.65$
> (2) MAP Beta(3,3): $(13+2)/(20+4) = 15/24 = 0.625$ — ​ស្ទើរ​តែ​ដូច MLE ដោយ prior បាន​​​សន្មត​​ជ្រើស​ស្មើ​គ្នា។ MAP Beta(5,1): $(13+4)/(20+4) = 17/24 \approx 0.708$ — ​prior លំអៀង​ទៅ "ខ្នង​ច្រើន" ​ទាញ MAP ​ឡើង​ខ្ពស់
> (3) $\hat\mu = (165+170+168+172)/4 = 168.75$; $\hat\sigma^2_{\text{MLE}} = ((-3.75)^2 + 1.25^2 + (-0.75)^2 + 3.25^2)/4 = (14.0625+1.5625+0.5625+10.5625)/4 = 6.6875$ → $\sigma_{\text{MLE}} \approx 2.59$ cm។ Unbiased: ​បែង​ដោយ 3 ​វិញ ​ផ្ដល់ $6.6875 \times 4 / 3 \approx 8.917$ → $\sigma \approx 2.99$ cm — ធំ​ជាង​បន្តិច (MLE ​មាន​លំអៀង​ទាប)
> (4) Log-posterior: $\log P(D \mid w) + \log P(w) = -\frac{1}{2\sigma^2}\sum (y_i - w^\top x_i)^2 - \frac{1}{2\tau^2}\|w\|^2 + \text{const}$។ ​គុណ​ដោយ $-2\sigma^2$ ​ប្តូរ argmax → argmin: $\sum (y_i - w^\top x_i)^2 + \frac{\sigma^2}{\tau^2}\|w\|^2$ — នេះ​គឺ Ridge ​ដោយ $\lambda = \sigma^2/\tau^2$ ∎

---

**មេរៀន​បន្ទាប់ (ជំពូក 5):** ប្រភេទ​នៃ ML — supervised, unsupervised, reinforcement, semi-supervised។ យើង​បាន​ឃើញ​ស្នូល​គណិតវិទ្យា​រួច​ហើយ (ពិជគណិត​លីនេអ៊ែរ, កាល់គុលម៉ាទ្រីស, ប្រូបាប៊ីលីតេ, MLE/MAP) — ឥឡូវ​យើង​ចាប់​ផ្ដើម​ប្រើ​ឧបករណ៍​ទាំង​នេះ​ដើម្បី​ស្ថាបនា​ algorithm ​ML ពិត​ប្រាកដ។
