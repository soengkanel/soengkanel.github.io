---
layout: post
title: "[Grade 9] មេរៀនទី ១៖ ស្វ័យគុណ (Exponents)"
date: 2026-08-17 09:00:00 +0700
categories: grade 9
tags: [math, grade-9, exponents, khmer, school-prep]
---

ស្វាគមន៍កូនៗ និងអាណាព្យាបាលមកកាន់មេរៀនគណិតវិទ្យាថ្នាក់ទី៩! មេរៀនដំបូងគេបង្អស់នេះ គឺនិយាយអំពី **"ស្វ័យគុណ" (Exponents)**។ នេះជាគ្រឹះដ៏សំខាន់បំផុតមួយសម្រាប់គណិតវិទ្យាថ្នាក់ខ្ពស់ៗ និងការប្រឡងផ្សេងៗ។

មេរៀននេះត្រូវបានរៀបចំឡើងយ៉ាងសាមញ្ញ ងាយយល់ មានឧទាហរណ៍ជាក់ស្តែងក្នុងជីវិតរស់នៅ និងមានលំហាត់ប្រឡងប្រជែង (Olympiad/Challenge) ដើម្បីឱ្យកូនៗបានហ្វឹកហាត់ខួរក្បាល និងត្រៀមខ្លួនសម្រាប់រាល់ការប្រឡងនានា។

---

# 1. គំនិតវិចារណញ្ញាណ៖ ស្វ័យគុណកើតចេញពីណា?

ស្រមៃថា កូនៗយកក្រដាសមួយសន្លឹកមកបត់ជាពីរដងហើយដងទៀត៖
* **បត់លើកទី១៖** យើងបានក្រដាសជា $2$ ស្រទាប់។
* **បត់លើកទី២៖** យើងបានក្រដាសជា $2 \times 2 = 4$ ស្រទាប់។
* **បត់លើកទី៣៖** យើងបានក្រដាសជា $2 \times 2 \times 2 = 8$ ស្រទាប់។
* **បត់លើកទី៤៖** យើងបានក្រដាសជា $2 \times 2 \times 2 \times 2 = 16$ ស្រទាប់។

ចុះបើបត់ដល់ទៅ ១០ ដង? តើយើងត្រូវសរសេរ $2 \times 2 \times 2 \times 2 \times 2 \times 2 \times 2 \times 2 \times 2 \times 2$ ចំនួន ១០ ដងមែនទេ? សរសេរបែបនេះគឺវែង និងពិបាកអានណាស់!

ដើម្បីសម្រួលដល់ការសរសេរវិធីគុណដដែលៗនេះ គណិតវិទូបានបង្កើតនិមិត្តសញ្ញាមួយហៅថា **ស្វ័យគុណ**៖

$$2 \times 2 \times 2 \times 2 \times 2 \times 2 \times 2 \times 2 \times 2 \times 2 = 2^{10}$$

អានថា៖ **ពីរ ស្វ័យគុណ ដប់** ឬ **ពីរ លើកជាស្វ័យគុណ ដប់**។

### 🎬 សាកល្បងអន្តរកម្ម៖ បត់ក្រដាសដល់ព្រះច័ន្ទ!

ប្តូរ​របារ​ខាង​ក្រោម​ដើម្បី​មើល​ថា ក្រដាស​មួយ​សន្លឹក (កម្រាស់ ០.១ មម) ក្លាយ​ជា​អ្វី​បន្ទាប់​ពី​បត់​ច្រើន​ដង។

<div id="fold-viz" style="max-width:820px;margin:0 auto;padding:18px;background:linear-gradient(180deg,#f0f9ff 0%,#fafafa 100%);border-radius:12px;border:1px solid #cbd5e1;font-family:system-ui,sans-serif">
  <div style="text-align:center">
    <label style="font-size:0.95em;color:#334155">ចំនួនបត់ (n) = <span id="fold-n" style="font-weight:bold;color:#1e40af;font-size:1.25em">10</span> ដង</label><br>
    <input id="fold-slider" type="range" min="0" max="42" step="1" value="10" style="width:85%;max-width:450px;margin-top:8px;accent-color:#1e40af">
    <div style="display:flex;justify-content:space-between;max-width:450px;margin:2px auto;font-size:0.75em;color:#64748b"><span>0</span><span>10</span><span>20</span><span>30</span><span>42 🌙</span></div>
  </div>
  <div style="margin:14px auto 0;padding:14px;background:white;border-radius:10px;border:2px solid #dbeafe;max-width:560px;text-align:center">
    <div style="font-size:0.95em;color:#475569">ចំនួនស្រទាប់ក្រដាស៖</div>
    <div style="font-size:1.9em;font-weight:bold;color:#1e40af;margin:4px 0">
      <span id="fold-formula">2<sup>10</sup></span> = <span id="fold-layers">1,024</span>
    </div>
    <div style="font-size:1.05em;color:#334155;margin-top:6px">
      កម្រាស់សរុប៖ <span id="fold-thick" style="font-weight:bold;color:#dc2626;font-size:1.15em">10.24 cm</span>
    </div>
    <div id="fold-compare" style="margin-top:10px;padding:8px;background:#faf5ff;border-radius:6px;font-size:0.98em;color:#7c3aed;font-weight:500;min-height:1.6em">
      ≈ កម្រាស់សៀវភៅមួយក្បាល
    </div>
  </div>
</div>

<script>
(function(){
  var slider = document.getElementById('fold-slider');
  var nEl = document.getElementById('fold-n');
  var formEl = document.getElementById('fold-formula');
  var layEl = document.getElementById('fold-layers');
  var thickEl = document.getElementById('fold-thick');
  var cmpEl = document.getElementById('fold-compare');
  var THICK_MM = 0.1;
  function fmt(n){ return n.toLocaleString('en-US', {maximumFractionDigits: 0}); }
  function formatThickness(mm){
    if (mm < 10) return mm.toFixed(2) + ' mm';
    if (mm < 1000) return (mm/10).toFixed(2) + ' cm';
    if (mm < 1e6) return (mm/1000).toFixed(2) + ' m';
    return (mm/1e6).toLocaleString('en-US', {maximumFractionDigits: 0}) + ' km';
  }
  function comparison(n){
    if (n <= 0) return 'ក្រដាសមួយសន្លឹកតែម្តង';
    if (n <= 4) return '≈ ស្តើងជាងស្លឹករូក';
    if (n <= 7) return '≈ កម្រាស់សៀវភៅតូច';
    if (n <= 10) return '≈ កម្រាស់សៀវភៅមួយក្បាល';
    if (n <= 13) return '≈ កម្ពស់តុសាលារៀន';
    if (n <= 14) return '≈ កម្ពស់មនុស្សពេញវ័យ 🧍';
    if (n <= 17) return '≈ ខ្ពស់ជាងផ្ទះ ៣ ជាន់ 🏠';
    if (n <= 20) return '≈ ខ្ពស់ជាងដើមឈើធំ ៗ 🌳';
    if (n <= 23) return '≈ ខ្ពស់ជាងអគារ Burj Khalifa (828 m) 🏙️';
    if (n <= 27) return '≈ ខ្ពស់ជាងភ្នំ Everest ច្រើនដង ⛰️';
    if (n <= 30) return '≈ ដល់ព្រំដែនអវកាស (Kármán line) 🚀';
    if (n <= 33) return '≈ ចម្ងាយកាត់ប្រទេសកម្ពុជា';
    if (n <= 37) return '≈ ព័ទ្ធជុំវិញផែនដីច្រើនជុំ 🌍';
    if (n <= 40) return '≈ រហូតដល់ផ្កាយរណប GPS';
    if (n <= 41) return '≈ ជិតដល់ព្រះច័ន្ទ!';
    return '🚀🌙 ដល់ព្រះច័ន្ទ! (384,000 km)';
  }
  function update(){
    var n = parseInt(slider.value);
    var layers = Math.pow(2, n);
    var thickMm = layers * THICK_MM;
    nEl.textContent = n;
    formEl.innerHTML = '2<sup>' + n + '</sup>';
    layEl.textContent = fmt(layers);
    thickEl.textContent = formatThickness(thickMm);
    cmpEl.textContent = comparison(n);
  }
  slider.addEventListener('input', update);
  update();
})();
</script>

> **គន្លឹះសម្រាប់ឪពុកម្តាយ៖** សូមឱ្យកូនៗទាយមុនពេលទាញរបារ — «ប្រសិនបើបត់ ២០ ដង តើនឹងកម្ពស់ដល់អ្វី?» លទ្ធផលនឹងធ្វើឱ្យពួកគេភ្ញាក់ផ្អើល ហើយចាប់ផ្តើមយល់ថា ស្វ័យគុណរីកមហិមាលឿនប៉ុណ្ណា។

---

# 2. និយមន័យគ្រឹះ

ជាទូទៅ បើ $a$ ជាចំនួនពិត និង $n$ ជាចំនួនគត់វិជ្ជមាន ($n \ge 1$) នោះ $a^n$ គឺជាផលគុណនៃ $n$ កត្តានៃចំនួន $a$៖

$$a^n = \underbrace{a \times a \times a \times \dots \times a}_{n \text{ ដង}}$$

ក្នុងនោះ៖
* **$a$** ហៅថា **គោល (Base)** (ចំនួនដែលត្រូវយកទៅគុណខ្លួនឯងដដែលៗ)
* **$n$** ហៅថា **និទស្សន្ត (Exponent / Index)** (ចំនួនដងដែលត្រូវយកទៅគុណ)

**ឧទាហរណ៍៖**
* $3^4 = 3 \times 3 \times 3 \times 3 = 81$ (គោលគឺ $3$, និទស្សន្តគឺ $4$)
* $(-5)^3 = (-5) \times (-5) \times (-5) = -125$ (គោលគឺ $-5$, និទស្សន្តគឺ $3$)
* $0.5^2 = 0.5 \times 0.5 = 0.25$

> [!IMPORTANT]
> **ចំណាំប្រយ័ត្នច្រឡំ៖**
> $-3^2 \neq (-3)^2$
> * $-3^2 = -(3 \times 3) = -9$ (ដកនៅក្រៅស្វ័យគុណ)
> * $(-3)^2 = (-3) \times (-3) = 9$ (ដកនៅក្នុងស្វ័យគុណ)

### 🎮 សាកល្បង៖ សាងស្វ័យគុណដោយខ្លួនឯង!

ជ្រើសរើស​គោល (a) និង​និទស្សន្ត (n) — មើល​ខ្សែ​គុណ​ដដែល​ៗ​សាង​ឡើង និង​តម្លៃ​រីក​ធំ​យ៉ាង​លឿន។

<div id="build-viz" style="max-width:820px;margin:0 auto;padding:18px;background:linear-gradient(180deg,#fef3c7 0%,#fafafa 100%);border-radius:12px;border:1px solid #fde68a;font-family:system-ui,sans-serif">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:12px">
    <div style="text-align:center">
      <label style="font-size:0.9em;color:#334155">គោល (Base) a = <span id="build-a" style="color:#dc2626;font-weight:bold;font-size:1.2em">3</span></label><br>
      <input id="build-a-slider" type="range" min="2" max="10" step="1" value="3" style="width:90%;accent-color:#dc2626;margin-top:4px">
    </div>
    <div style="text-align:center">
      <label style="font-size:0.9em;color:#334155">និទស្សន្ត (Exponent) n = <span id="build-n" style="color:#1e40af;font-weight:bold;font-size:1.2em">4</span></label><br>
      <input id="build-n-slider" type="range" min="0" max="8" step="1" value="4" style="width:90%;accent-color:#1e40af;margin-top:4px">
    </div>
  </div>
  <div style="padding:14px;background:white;border-radius:10px;border:2px solid #fbbf24;text-align:center">
    <div id="build-chain" style="font-size:1.3em;color:#1f2937;word-break:break-word">3 × 3 × 3 × 3</div>
    <div style="font-size:1.7em;font-weight:bold;color:#0f766e;margin-top:8px">
      <span id="build-formula">3<sup>4</sup></span> = <span id="build-result">81</span>
    </div>
  </div>
  <div id="build-chart" style="width:100%;height:280px;margin-top:8px"></div>
</div>

<script>
(function(){
  function init(){
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    var aSlider = document.getElementById('build-a-slider');
    var nSlider = document.getElementById('build-n-slider');
    var aEl = document.getElementById('build-a');
    var nEl = document.getElementById('build-n');
    var chainEl = document.getElementById('build-chain');
    var formEl = document.getElementById('build-formula');
    var resEl = document.getElementById('build-result');
    function fmt(v){
      if (v < 1e7) return v.toLocaleString('en-US');
      return v.toExponential(3).replace('+', '');
    }
    function chain(a, n){
      if (n === 0) return '(គ្មានតួគុណ) = 1';
      var arr = [];
      for (var i = 0; i < n; i++) arr.push(a);
      return arr.join(' × ');
    }
    function bars(a, n){
      var xs = [], ys = [], colors = [], txt = [];
      for (var k = 0; k <= Math.max(n, 4); k++){
        var v = Math.pow(a, k);
        xs.push('n=' + k);
        ys.push(v);
        colors.push(k === n ? '#dc2626' : (k < n ? '#60a5fa' : '#e5e7eb'));
        txt.push(fmt(v));
      }
      return [{
        x: xs, y: ys, type: 'bar', marker: {color: colors},
        text: txt, textposition: 'outside', textfont: {size: 11},
        hovertemplate: '%{x}: %{text}<extra></extra>'
      }];
    }
    var layout = {
      margin: {t: 24, b: 40, l: 60, r: 20},
      xaxis: {title: ''},
      yaxis: {title: 'តម្លៃ a^n', automargin: true},
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)',
      showlegend: false
    };
    function render(){
      var a = parseInt(aSlider.value);
      var n = parseInt(nSlider.value);
      aEl.textContent = a;
      nEl.textContent = n;
      chainEl.textContent = chain(a, n);
      formEl.innerHTML = a + '<sup>' + n + '</sup>';
      resEl.textContent = fmt(Math.pow(a, n));
      Plotly.react('build-chart', bars(a, n), layout, {responsive: true, displayModeBar: false});
    }
    aSlider.addEventListener('input', render);
    nSlider.addEventListener('input', render);
    render();
  }
  init();
})();
</script>

---

# 3. លក្ខណៈសំខាន់ៗទាំង ៧ នៃស្វ័យគុណ

ដើម្បីដោះស្រាយលំហាត់ស្វ័យគុណបានលឿន និងត្រឹមត្រូវ កូនៗត្រូវចាំលក្ខណៈគ្រឹះទាំង ៧ នេះ៖

### លក្ខណៈទី ១៖ ផលគុណស្វ័យគុណដែលមានគោលដូចគ្នា
$$a^m \times a^n = a^{m+n}$$
*ច្បាប់៖ គោលដូចគ្នាគុណគ្នា យកនិទស្សន្តបូកគ្នា។*
* **ឧទាហរណ៍៖** $2^3 \times 2^4 = 2^{3+4} = 2^7 = 128$

### លក្ខណៈទី ២៖ ផលចែកស្វ័យគុណដែលមានគោលដូចគ្នា
$$\frac{a^m}{a^n} = a^{m-n} \quad (a \neq 0)$$
*ច្បាប់៖ គោលដូចគ្នាចែកគ្នា យកនិទស្សន្តដកគ្នា។*
* **ឧទាហរណ៍៖** $\frac{5^6}{5^4} = 5^{6-4} = 5^2 = 25$

### លក្ខណៈទី ៣៖ ស្វ័យគុណនៃស្វ័យគុណ
$$(a^m)^n = a^{m \times n}$$
*ច្បាប់៖ ស្វ័យគុណជាន់គ្នា យកនិទស្សន្តគុណគ្នា។*
* **ឧទាហរណ៍៖** $(3^2)^3 = 3^{2 \times 3} = 3^6 = 729$

### លក្ខណៈទី ៤៖ ស្វ័យគុណនៃផលគុណ
$$(a \times b)^n = a^n \times b^n$$
*ច្បាប់៖ ចែករំលែកនិទស្សន្តទៅកាន់គ្រប់តួគុណខាងក្នុងវង់ក្រចក។*
* **ឧទាហរណ៍៖** $(2 \times 5)^3 = 2^3 \times 5^3 = 8 \times 125 = 1000$ (ស្មើនឹង $10^3$)

### លក្ខណៈទី ៥៖ ស្វ័យគុណនៃផលចែក
$$\left(\frac{a}{b}\right)^n = \frac{a^n}{b^n} \quad (b \neq 0)$$
*ច្បាប់៖ ចែករំលែកនិទស្សន្តទៅភាគយក និងភាគបែង។*
* **ឧទាហរណ៍៖** $\left(\frac{2}{3}\right)^3 = \frac{2^3}{3^3} = \frac{8}{27}$

### លក្ខណៈទី ៦៖ ស្វ័យគុណសូន្យ
$$a^0 = 1 \quad (a \neq 0)$$
*ច្បាប់៖ គ្រប់ចំនួនពិតខុសពីសូន្យ លើកជាស្វ័យគុណ ០ គឺតែងតែស្មើ ១។*

**តើហេតុអ្វីបានជា $a^0 = 1$? (គន្លឹះយល់ដឹង!)**
យើងដឹងថា $\frac{5^3}{5^3} = 1$ (ព្រោះចំនួនដដែលចែកខ្លួនឯង)។
តែបើតាមលក្ខណៈទី ២ យើងក៏អាចគណនាបាន៖ $\frac{5^3}{5^3} = 5^{3-3} = 5^0$។
ដូចនេះ យើងអាចសន្និដ្ឋានបានថា $5^0 = 1$។ ពិតជាងាយស្រួលយល់មែនទេ!

### លក្ខណៈទី ៧៖ និទស្សន្តអវិជ្ជមាន
$$a^{-n} = \frac{1}{a^n} \quad (a \neq 0)$$
*ច្បាប់៖ និទស្សន្តដក ប្តូរទៅជាភាគបែងដើម្បីក្លាយជាបូក។*

**តើហេតុអ្វីបានជាមានច្បាប់នេះ? (ចូរមើលលំនាំ Pattern ខាងក្រោម)៖**
* $2^3 = 8$
* $2^2 = 4$  *(ចែកនឹង ២)*
* $2^1 = 2$  *(ចែកនឹង ២)*
* $2^0 = 1$  *(ចែកនឹង ២)*
* $2^{-1} = \frac{1}{2}$ *(ចែកនឹង ២)*
* $2^{-2} = \frac{1}{4} = \frac{1}{2^2}$ *(ចែកនឹង ២)*

ដូចនេះ $a^{-n} = \frac{1}{a^n}$ គឺពិតជាត្រឹមត្រូវតាមលំនាំគណិតវិទ្យា។

### 🔍 សាកល្បង៖ ជណ្តើរចែក — ស្វ័យគុណអវិជ្ជមានចេញពីណា?

រាល់​ជំហាន​ទៅ​ស្តាំ = ចែក​នឹង a មួយ​ដង។ សូម​សង្កេត​ថា​តម្លៃ​ $a^0$ តែង​តែ​ស្មើ ១ ហើយ​ស្វ័យ​គុណ​អវិជ្ជមាន​គ្រាន់​តែ​ជា «ភាគ​ដាច់​១​លើ...»។

<div id="halve-viz" style="max-width:820px;margin:0 auto;padding:18px;background:linear-gradient(180deg,#f0fdf4 0%,#fafafa 100%);border-radius:12px;border:1px solid #bbf7d0;font-family:system-ui,sans-serif">
  <div style="text-align:center;margin-bottom:14px">
    <label style="font-size:0.95em;color:#334155">ជ្រើសរើសគោល a៖</label>
    <select id="halve-base" style="padding:6px 10px;font-size:1em;margin-left:6px;border-radius:6px;border:1px solid #cbd5e1;background:white;font-weight:bold;color:#0f766e">
      <option value="2">2</option>
      <option value="3">3</option>
      <option value="5">5</option>
      <option value="10">10</option>
    </select>
  </div>
  <div id="halve-table" style="display:flex;justify-content:center;gap:6px;flex-wrap:wrap"></div>
  <div style="text-align:center;margin-top:14px;padding:10px;background:white;border-radius:8px;border:1px dashed #86efac;color:#334155;font-size:0.95em">
    <span style="color:#dc2626;font-weight:bold">←</span> ជំហានឆ្វេង​មួយ​ = <b>គុណ​នឹង <span id="halve-b1">2</span></b>
    &nbsp;&nbsp;|&nbsp;&nbsp;
    ជំហានស្តាំ​មួយ​ = <b>ចែក​នឹង <span id="halve-b2">2</span></b> <span style="color:#dc2626;font-weight:bold">→</span>
  </div>
</div>

<script>
(function(){
  var box = document.getElementById('halve-table');
  var sel = document.getElementById('halve-base');
  var b1 = document.getElementById('halve-b1');
  var b2 = document.getElementById('halve-b2');
  function fmtVal(a, n){
    if (n >= 0) return String(Math.pow(a, n));
    var d = Math.pow(a, -n);
    return '1/' + d.toLocaleString('en-US');
  }
  function render(){
    var a = parseInt(sel.value);
    b1.textContent = a; b2.textContent = a;
    box.innerHTML = '';
    for (var n = 4; n >= -4; n--){
      var isZero = (n === 0);
      var cell = document.createElement('div');
      cell.style.cssText = 'padding:10px 8px;background:' + (isZero ? '#fef2f2' : 'white') + ';border:2px solid ' + (isZero ? '#dc2626' : '#d1fae5') + ';border-radius:8px;min-width:78px;text-align:center;transition:transform .15s;box-shadow:0 1px 3px rgba(0,0,0,.05)';
      cell.innerHTML =
        '<div style="color:#1e40af;font-size:1.05em;font-weight:bold">' + a + '<sup>' + n + '</sup></div>' +
        '<div style="color:#0f766e;margin-top:4px;font-size:0.95em;word-break:break-word">' + fmtVal(a, n) + '</div>';
      if (isZero) cell.innerHTML += '<div style="color:#dc2626;font-size:0.72em;margin-top:2px;font-weight:bold">= 1 ✨</div>';
      box.appendChild(cell);
    }
  }
  sel.addEventListener('change', render);
  render();
})();
</script>

---

# 4. ទម្រង់វិទ្យាសាស្ត្រ (Scientific Notation)

ទម្រង់វិទ្យាសាស្ត្រ ត្រូវបានប្រើដើម្បីសរសេរចំនួនដែលធំខ្លាំង ឬតូចខ្លាំង ឱ្យមានរបៀប និងងាយស្រួលអាន។
ទម្រង់ទូទៅ៖

$$A \times 10^n$$

ដែល $1 \le A < 10$ និង $n$ ជាចំនួនគត់។

* **ឧទាហរណ៍ ១ (ចំនួនធំខ្លាំង)៖** ចម្ងាយពីផែនដីទៅព្រះអាទិត្យគឺប្រហែល $150,000,000 \text{ km}$។
  សរសេរជាទម្រង់វិទ្យាសាស្ត្រ៖ $1.5 \times 10^8 \text{ km}$។
* **ឧទាហរណ៍ ២ (ចំនួនតូចខ្លាំង)៖** ទំហំនៃបាក់តេរីមួយប្រភេទគឺ $0.000003 \text{ m}$។
  សរសេរជាទម្រង់វិទ្យាសាស្ត្រ៖ $3 \times 10^{-6} \text{ m}$។

---

# 5. ផ្នែកហ្វឹកហាត់៖ លំហាត់អនុវត្តពីងាយទៅពិបាក

ដើម្បីត្រៀមខ្លួនសម្រាប់ភាពប្រកួតប្រជែង ចូរឱ្យកូនៗសាកល្បងដោះស្រាយលំហាត់ទាំងនេះជាជំហានៗ។

### កម្រិត ១៖ មូលដ្ឋានគ្រឹះ (Easy)
គណនាតម្លៃលេខ៖
1. $2^5 - 3^3$
2. $(-2)^4 \times 5^0$
3. $\left(\frac{1}{3}\right)^{-2} + 4^{-1}$

**ដំណោះស្រាយ៖**
1. យើងមាន $2^5 = 32$ និង $3^3 = 27$។
   ដូចនេះ៖ $32 - 27 = 5$។
2. យើងមាន $(-2)^4 = 16$ (ព្រោះនិទស្សន្តគូ លទ្ធផលវិជ្ជមាន) និង $5^0 = 1$。
   ដូចនេះ៖ $16 \times 1 = 16$។
3. យើងមាន $\left(\frac{1}{3}\right)^{-2} = 3^2 = 9$ និង $4^{-1} = \frac{1}{4} = 0.25$។
   ដូចនេះ៖ $9 + 0.25 = 9.25$ ឬ $\frac{37}{4}$។

---

### កម្រិត ២៖ សម្រួលកន្សោម (Medium)
សម្រួលកន្សោមខាងក្រោមឱ្យទៅជាទម្រង់សាមញ្ញបំផុត៖

$$A = \frac{x^5 \cdot y^{-2} \cdot (z^2)^3}{x^2 \cdot y^3 \cdot z^{-4}}$$

**ដំណោះស្រាយ៖**
យើងអនុវត្តលក្ខណៈស្វ័យគុណម្តងមួយៗចំពោះអក្សរនីមួយៗ៖
* **ចំពោះ $x$៖** $\frac{x^5}{x^2} = x^{5-2} = x^3$
* **ចំពោះ $y$៖** $\frac{y^{-2}}{y^3} = y^{-2-3} = y^{-5}$
* **ចំពោះ $z$៖** ភាគយកមាន $(z^2)^3 = z^{2 \times 3} = z^6$។
  នាំឱ្យការសម្រួលចំពោះ $z$ គឺ $\frac{z^6}{z^{-4}} = z^{6 - (-4)} = z^{6+4} = z^{10}$

រួមបញ្ចូលគ្នា យើងបាន៖

$$A = x^3 \cdot y^{-5} \cdot z^{10} = \frac{x^3 z^{10}}{y^5}$$

---

### កម្រិត ៣៖ ប្រកួតប្រជែងខួរក្បាល (Challenging Brain Teaser 🧠)
*លំហាត់នេះជាប្រភេទលំហាត់សិស្សពូកែ ឬលំហាត់ត្រៀមប្រឡងប្រជែង។ ព្យាយាមឱ្យកូនៗគិតរកវិធីមុនពេលមើលដំណោះស្រាយ!*

**សំណួរ៖** ចូរប្រៀបធៀបចំនួនទាំងពីរខាងក្រោម តើមួយណាធំជាង?

$$2^{300} \quad \text{និង} \quad 3^{200}$$

**ដំណោះស្រាយ៖**
យើងមិនអាចគណនាតម្លៃផ្ទាល់នៃ $2^{300}$ ឬ $3^{200}$ ដោយការគុណដោយដៃបានឡើយ ព្រោះពួកវាមានទំហំធំមហិមាណាស់។ ប៉ុន្តែយើងអាចប្រើ **លក្ខណៈស្វ័យគុណ** ដើម្បីប្រៀបធៀបវាបានយ៉ាងងាយស្រួល!

ចូរក្រឡេកមើលនិទស្សន្ត $300$ និង $200$។ តួចែករួមធំបំផុត (GCD) របស់វាគឺ $100$។
យើងអាចបំបែកនិទស្សន្តទាំងពីរនេះជាផលគុណដែលមានលេខ $100$៖
* $2^{300} = 2^{3 \times 100} = (2^3)^{100}$
* $3^{200} = 3^{2 \times 100} = (3^2)^{100}$

ឥឡូវ យើងគណនាតម្លៃលេខដែលនៅក្នុងវង់ក្រចក៖
* $2^3 = 8$ នាំឱ្យ $(2^3)^{100} = 8^{100}$
* $3^2 = 9$ នាំឱ្យ $(3^2)^{100} = 9^{100}$

ដោយសារតែ $9 > 8$ នាំឱ្យយើងអាចសន្និដ្ឋានបានយ៉ាងច្បាស់ថា $9^{100} > 8^{100}$។
ដូចនេះ៖

$$3^{200} > 2^{300}$$

---

# 6. ប័ណ្ណសង្ខេបមេរៀន (Formula Sheet សម្រាប់កូនៗ)
ចូរកូនៗកត់ត្រារូបមន្តទាំងនេះទុកក្នុងសៀវភៅមេរៀនសង្ខេប៖
1. **គុណគោលដូចគ្នា៖** $a^m \times a^n = a^{m+n}$
2. **ចែកគោលដូចគ្នា៖** $a^m / a^n = a^{m-n}$
3. **ស្វ័យគុណជាន់គ្នា៖** $(a^m)^n = a^{mn}$
4. **ស្វ័យគុណផលគុណ៖** $(ab)^n = a^n b^n$
5. **ស្វ័យគុណផលចែក៖** $(a/b)^n = a^n / b^n$
6. **ស្វ័យគុណសូន្យ៖** $a^0 = 1$
7. **ស្វ័យគុណអវិជ្ជមាន៖** $a^{-n} = 1/a^n$

*ប្រសិនបើកូនៗមានចម្ងល់ ឬចង់បានលំហាត់បន្ថែមទៀត អាចសួរនៅក្នុងប្រអប់មតិយោបល់ (Comments) ខាងក្រោមបានណា!*
