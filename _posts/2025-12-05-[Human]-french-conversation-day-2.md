---
layout: post
title: "[Human] French Conversation Day 2: Numbers & Café 🇫🇷☕"
tags: [French, Language, Khmer, Conversation, Beginner]
thumbnail: /images/french_day_2.svg
---

<style>
/* French Learning Styles */
.french-card {
  background: linear-gradient(135deg, #002654 0%, #1e3a5f 100%);
  border-radius: 16px;
  padding: 2rem;
  margin: 1.5rem 0;
  color: white;
  transition: all 0.4s ease;
  cursor: pointer;
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.french-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: 0.5s;
}

.french-card:hover::before {
  left: 100%;
}

.french-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 38, 84, 0.4);
  border-color: #ed2939;
}

.french-word {
  font-size: 2rem;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.french-pronunciation {
  font-size: 1.1rem;
  color: #87ceeb;
  font-style: italic;
  margin-bottom: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.french-meaning {
  color: #e0e0e0;
  margin-bottom: 0.8rem;
  font-size: 1.1rem;
}

.french-khmer {
  color: #ffd700;
  font-size: 1.3rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255,255,255,0.2);
}

.dialogue-box {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 2rem;
  margin: 2rem 0;
  color: white;
  border-left: 5px solid #ed2939;
}

.dialogue-line {
  display: flex;
  gap: 1rem;
  margin: 1.2rem 0;
  padding: 1rem;
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.dialogue-line:hover {
  background: rgba(255,255,255,0.1);
  transform: translateX(10px);
}

.speaker {
  font-weight: bold;
  min-width: 100px;
  color: #00d9ff;
}

.speaker.client {
  color: #ff6b9d;
}

.french-text {
  color: #ffffff;
  font-weight: 500;
}

.khmer-text {
  color: #ffd700;
  font-size: 0.95rem;
  margin-top: 0.3rem;
}

.section-header {
  background: linear-gradient(90deg, #002654, #ed2939, #ffffff);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.8rem;
  font-weight: bold;
  margin: 2rem 0 1rem 0;
}

.tip-box {
  background: rgba(237, 41, 57, 0.1);
  border: 2px solid #ed2939;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1.5rem 0;
}

.tip-box h4 {
  color: #ed2939;
  margin-top: 0;
}

.vocab-grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.audio-btn {
  background: linear-gradient(135deg, #ed2939, #c41e30);
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.audio-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 15px rgba(237, 41, 57, 0.4);
}

.practice-container {
  background: linear-gradient(135deg, #2d1b69 0%, #1a1a2e 100%);
  border-radius: 16px;
  padding: 2rem;
  margin: 2rem 0;
  color: white;
}

.quiz-option {
  background: rgba(255,255,255,0.1);
  padding: 1rem;
  margin: 0.5rem 0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.quiz-option:hover {
  background: rgba(255,255,255,0.2);
  border-color: rgba(255,255,255,0.3);
}

.quiz-option.correct {
  background: rgba(107, 203, 119, 0.4);
  border-color: #6bcb77;
}

.quiz-option.wrong {
  background: rgba(255, 107, 107, 0.4);
  border-color: #ff6b6b;
}

.flag-emoji {
  font-size: 3rem;
  text-align: center;
  margin: 1rem 0;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background: rgba(255,255,255,0.1);
  border-radius: 5px;
  overflow: hidden;
  margin: 1rem 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #002654, #ed2939);
  width: 28%;
  border-radius: 5px;
  transition: width 0.5s ease;
}

.number-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.8rem;
  margin: 1.5rem 0;
}

.number-card {
  background: linear-gradient(135deg, #002654, #1e3a5f);
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.number-card:hover {
  transform: scale(1.1);
  border-color: #ed2939;
  box-shadow: 0 5px 15px rgba(237, 41, 57, 0.3);
}

.number-card .num {
  font-size: 1.5rem;
  font-weight: bold;
  color: #00d9ff;
}

.number-card .french {
  font-size: 0.9rem;
  margin-top: 0.3rem;
}

.cafe-menu {
  background: linear-gradient(135deg, #3d2914 0%, #5c3d1e 100%);
  border-radius: 16px;
  padding: 2rem;
  margin: 2rem 0;
  color: white;
  border: 3px solid #8b6914;
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px dashed rgba(255,255,255,0.2);
  transition: all 0.3s ease;
}

.menu-item:hover {
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
}

.menu-item:last-child {
  border-bottom: none;
}

.item-name {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.item-emoji {
  font-size: 1.5rem;
}

.item-french {
  font-weight: bold;
  color: #ffd700;
}

.item-khmer {
  font-size: 0.85rem;
  color: #e0e0e0;
}

.item-price {
  color: #00d9ff;
  font-weight: bold;
}

@media (max-width: 600px) {
  .number-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>

<div class="flag-emoji">🇫🇷 ☕ 🥐</div>

Welcome to **Day 2** of your French learning journey! Today we'll learn **Numbers (0-20)** and how to **order at a café**. Essential for any trip to Paris! ☕

<div class="progress-bar">
  <div class="progress-fill"></div>
</div>
<p style="text-align: center; opacity: 0.7;">📚 Day 2 of 7 - Beginner Level</p>

---

## 🎯 Today's Goals

By the end of this lesson, you will be able to:
- ✅ Count from **0 to 20** in French
- ✅ Order **coffee, tea, and pastries** at a café
- ✅ Ask **"How much is it?"**
- ✅ Say **"I would like..."** politely

---

<h2 class="section-header">🔢 Numbers 0-20</h2>

Click on any number to hear it pronounced!

<div class="number-grid">
  <div class="number-card" onclick="speakFrench('zéro')">
    <div class="num">0</div>
    <div class="french">zéro</div>
  </div>
  <div class="number-card" onclick="speakFrench('un')">
    <div class="num">1</div>
    <div class="french">un</div>
  </div>
  <div class="number-card" onclick="speakFrench('deux')">
    <div class="num">2</div>
    <div class="french">deux</div>
  </div>
  <div class="number-card" onclick="speakFrench('trois')">
    <div class="num">3</div>
    <div class="french">trois</div>
  </div>
  <div class="number-card" onclick="speakFrench('quatre')">
    <div class="num">4</div>
    <div class="french">quatre</div>
  </div>
  <div class="number-card" onclick="speakFrench('cinq')">
    <div class="num">5</div>
    <div class="french">cinq</div>
  </div>
  <div class="number-card" onclick="speakFrench('six')">
    <div class="num">6</div>
    <div class="french">six</div>
  </div>
  <div class="number-card" onclick="speakFrench('sept')">
    <div class="num">7</div>
    <div class="french">sept</div>
  </div>
  <div class="number-card" onclick="speakFrench('huit')">
    <div class="num">8</div>
    <div class="french">huit</div>
  </div>
  <div class="number-card" onclick="speakFrench('neuf')">
    <div class="num">9</div>
    <div class="french">neuf</div>
  </div>
  <div class="number-card" onclick="speakFrench('dix')">
    <div class="num">10</div>
    <div class="french">dix</div>
  </div>
  <div class="number-card" onclick="speakFrench('onze')">
    <div class="num">11</div>
    <div class="french">onze</div>
  </div>
  <div class="number-card" onclick="speakFrench('douze')">
    <div class="num">12</div>
    <div class="french">douze</div>
  </div>
  <div class="number-card" onclick="speakFrench('treize')">
    <div class="num">13</div>
    <div class="french">treize</div>
  </div>
  <div class="number-card" onclick="speakFrench('quatorze')">
    <div class="num">14</div>
    <div class="french">quatorze</div>
  </div>
  <div class="number-card" onclick="speakFrench('quinze')">
    <div class="num">15</div>
    <div class="french">quinze</div>
  </div>
  <div class="number-card" onclick="speakFrench('seize')">
    <div class="num">16</div>
    <div class="french">seize</div>
  </div>
  <div class="number-card" onclick="speakFrench('dix-sept')">
    <div class="num">17</div>
    <div class="french">dix-sept</div>
  </div>
  <div class="number-card" onclick="speakFrench('dix-huit')">
    <div class="num">18</div>
    <div class="french">dix-huit</div>
  </div>
  <div class="number-card" onclick="speakFrench('dix-neuf')">
    <div class="num">19</div>
    <div class="french">dix-neuf</div>
  </div>
  <div class="number-card" onclick="speakFrench('vingt')" style="grid-column: span 5; max-width: 150px; margin: 0 auto;">
    <div class="num">20</div>
    <div class="french">vingt</div>
  </div>
</div>

---

<h2 class="section-header">☕ Café Menu</h2>

Learn these common café items:

<div class="cafe-menu">
  <h3 style="margin-top: 0; text-align: center; color: #ffd700;">🏪 Le Menu</h3>
  
  <div class="menu-item" onclick="speakFrench('un café')">
    <div class="item-name">
      <span class="item-emoji">☕</span>
      <div>
        <div class="item-french">Un café</div>
        <div class="item-khmer">កាហ្វេ (Kafei)</div>
      </div>
    </div>
    <div class="item-price">2€</div>
  </div>
  
  <div class="menu-item" onclick="speakFrench('un thé')">
    <div class="item-name">
      <span class="item-emoji">🍵</span>
      <div>
        <div class="item-french">Un thé</div>
        <div class="item-khmer">តែ (Tae)</div>
      </div>
    </div>
    <div class="item-price">3€</div>
  </div>
  
  <div class="menu-item" onclick="speakFrench('un croissant')">
    <div class="item-name">
      <span class="item-emoji">🥐</span>
      <div>
        <div class="item-french">Un croissant</div>
        <div class="item-khmer">នំក្រូសង់ (Num Krosang)</div>
      </div>
    </div>
    <div class="item-price">2€</div>
  </div>
  
  <div class="menu-item" onclick="speakFrench('une baguette')">
    <div class="item-name">
      <span class="item-emoji">🥖</span>
      <div>
        <div class="item-french">Une baguette</div>
        <div class="item-khmer">នំបាំងបារាំង (Num Bang Barang)</div>
      </div>
    </div>
    <div class="item-price">1€</div>
  </div>
  
  <div class="menu-item" onclick="speakFrench('un jus d\'orange')">
    <div class="item-name">
      <span class="item-emoji">🍊</span>
      <div>
        <div class="item-french">Un jus d'orange</div>
        <div class="item-khmer">ទឹកក្រូច (Tuk Krouch)</div>
      </div>
    </div>
    <div class="item-price">4€</div>
  </div>
  
  <div class="menu-item" onclick="speakFrench('de l\'eau')">
    <div class="item-name">
      <span class="item-emoji">💧</span>
      <div>
        <div class="item-french">De l'eau</div>
        <div class="item-khmer">ទឹក (Tuk)</div>
      </div>
    </div>
    <div class="item-price">1€</div>
  </div>
</div>

---

<h2 class="section-header">🗣️ The Dialogue: At the Café</h2>

<div class="dialogue-box">
  <h3 style="margin-top: 0; text-align: center;">☕ Ordering at a Parisian Café</h3>
  
  <div class="dialogue-line">
    <span class="speaker">Serveur:</span>
    <div>
      <div class="french-text">Bonjour ! Qu'est-ce que vous désirez ?</div>
      <div class="khmer-text">សួស្តី! តើអ្នកចង់បានអ្វី? (Suosdey! Ter neak chong ban avey?)</div>
    </div>
  </div>
  
  <div class="dialogue-line">
    <span class="speaker client">Client:</span>
    <div>
      <div class="french-text">Bonjour ! Je voudrais un café, s'il vous plaît.</div>
      <div class="khmer-text">សួស្តី! ខ្ញុំចង់បានកាហ្វេមួយ សូម។ (Suosdey! Knhom chong ban kafei muoy, soum.)</div>
    </div>
  </div>
  
  <div class="dialogue-line">
    <span class="speaker">Serveur:</span>
    <div>
      <div class="french-text">Très bien. Et avec ceci ?</div>
      <div class="khmer-text">បានហើយ។ ចុះមានអ្វីទៀតទេ? (Ban haey. Choh mean avey tiet te?)</div>
    </div>
  </div>
  
  <div class="dialogue-line">
    <span class="speaker client">Client:</span>
    <div>
      <div class="french-text">Un croissant aussi, s'il vous plaît.</div>
      <div class="khmer-text">ក្រូសង់មួយទៀតផង សូម។ (Krosang muoy tiet phong, soum.)</div>
    </div>
  </div>
  
  <div class="dialogue-line">
    <span class="speaker">Serveur:</span>
    <div>
      <div class="french-text">D'accord. Ce sera tout ?</div>
      <div class="khmer-text">បាន។ មានប៉ុណ្ណឹងទេ? (Ban. Mean ponneng te?)</div>
    </div>
  </div>
  
  <div class="dialogue-line">
    <span class="speaker client">Client:</span>
    <div>
      <div class="french-text">Oui, c'est tout. Ça fait combien ?</div>
      <div class="khmer-text">បាទ មានប៉ុណ្ណឹង។ តម្លៃប៉ុន្មាន? (Bat, mean ponneng. Tomlai ponman?)</div>
    </div>
  </div>
  
  <div class="dialogue-line">
    <span class="speaker">Serveur:</span>
    <div>
      <div class="french-text">Ça fait quatre euros.</div>
      <div class="khmer-text">តម្លៃបួនអឺរ៉ូ។ (Tomlai buon euro.)</div>
    </div>
  </div>
  
  <div class="dialogue-line">
    <span class="speaker client">Client:</span>
    <div>
      <div class="french-text">Voilà. Merci beaucoup !</div>
      <div class="khmer-text">នេះ។ អរគុណច្រើន! (Nis. Arkoun chraen!)</div>
    </div>
  </div>
  
  <div class="dialogue-line">
    <span class="speaker">Serveur:</span>
    <div>
      <div class="french-text">Merci à vous ! Bonne journée !</div>
      <div class="khmer-text">អរគុណអ្នកវិញ! សូមឱ្យមានថ្ងៃល្អ! (Arkoun neak vinh! Soum aoy mean thngai laor!)</div>
    </div>
  </div>
</div>

---

<h2 class="section-header">🔑 Key Phrases</h2>

<div class="vocab-grid">

  <div class="french-card">
    <div class="french-word">Je voudrais...</div>
    <div class="french-pronunciation">
      <button class="audio-btn" onclick="speakFrench('Je voudrais')">🔊 Listen</button>
      <span>zhuh voo-DREH</span>
    </div>
    <div class="french-meaning">I would like... (polite way to order)</div>
    <div class="french-khmer">🇰🇭 ខ្ញុំចង់បាន... (Knhom chong ban...)</div>
  </div>

  <div class="french-card">
    <div class="french-word">S'il vous plaît</div>
    <div class="french-pronunciation">
      <button class="audio-btn" onclick="speakFrench('S\'il vous plaît')">🔊 Listen</button>
      <span>seel voo PLEH</span>
    </div>
    <div class="french-meaning">Please (formal)</div>
    <div class="french-khmer">🇰🇭 សូម (Soum)</div>
  </div>

  <div class="french-card">
    <div class="french-word">Ça fait combien ?</div>
    <div class="french-pronunciation">
      <button class="audio-btn" onclick="speakFrench('Ça fait combien')">🔊 Listen</button>
      <span>sah fay kohm-BYEHN</span>
    </div>
    <div class="french-meaning">How much is it?</div>
    <div class="french-khmer">🇰🇭 តម្លៃប៉ុន្មាន? (Tomlai ponman?)</div>
  </div>

  <div class="french-card">
    <div class="french-word">L'addition, s'il vous plaît</div>
    <div class="french-pronunciation">
      <button class="audio-btn" onclick="speakFrench('L\'addition, s\'il vous plaît')">🔊 Listen</button>
      <span>lah-dee-SYOHN seel voo PLEH</span>
    </div>
    <div class="french-meaning">The check/bill, please</div>
    <div class="french-khmer">🇰🇭 សូមវិក្កយបត្រ (Soum vikkayabat)</div>
  </div>

  <div class="french-card">
    <div class="french-word">Merci beaucoup</div>
    <div class="french-pronunciation">
      <button class="audio-btn" onclick="speakFrench('Merci beaucoup')">🔊 Listen</button>
      <span>mehr-SEE boh-KOO</span>
    </div>
    <div class="french-meaning">Thank you very much</div>
    <div class="french-khmer">🇰🇭 អរគុណច្រើន (Arkoun chraen)</div>
  </div>

  <div class="french-card">
    <div class="french-word">Bonne journée</div>
    <div class="french-pronunciation">
      <button class="audio-btn" onclick="speakFrench('Bonne journée')">🔊 Listen</button>
      <span>bun zhoor-NAY</span>
    </div>
    <div class="french-meaning">Have a good day</div>
    <div class="french-khmer">🇰🇭 សូមឱ្យមានថ្ងៃល្អ (Soum aoy mean thngai laor)</div>
  </div>

</div>

<script>
// Text-to-Speech for French pronunciation
function speakFrench(text) {
  if ('speechSynthesis' in window) {
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'fr-FR';
    utterance.rate = 0.8; // Slower for learning
    utterance.pitch = 0.9; // Slightly lower pitch for male voice
    
    // Try to find a male French voice
    const voices = window.speechSynthesis.getVoices();
    const frenchVoices = voices.filter(voice => voice.lang.startsWith('fr'));
    
    // Prefer male voices (common male French voice names)
    const maleVoiceNames = ['thomas', 'paul', 'jacques', 'pierre', 'google français', 'microsoft paul', 'microsoft claude'];
    let selectedVoice = frenchVoices.find(voice => 
      maleVoiceNames.some(name => voice.name.toLowerCase().includes(name))
    );
    
    // If no male voice found, try to avoid female voice names
    if (!selectedVoice && frenchVoices.length > 0) {
      const femaleNames = ['amelie', 'marie', 'julie', 'céline', 'female', 'woman'];
      selectedVoice = frenchVoices.find(voice => 
        !femaleNames.some(name => voice.name.toLowerCase().includes(name))
      ) || frenchVoices[0];
    }
    
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }
    
    window.speechSynthesis.speak(utterance);
  } else {
    alert('Sorry, your browser does not support text-to-speech.');
  }
}

// Load voices (needed for some browsers)
if ('speechSynthesis' in window) {
  window.speechSynthesis.onvoiceschanged = function() {
    window.speechSynthesis.getVoices();
  };
}
</script>

---

<h2 class="section-header">💡 Grammar Tip</h2>

<div class="tip-box">
  <h4>🎯 Un vs. Une (Masculine & Feminine)</h4>
  
  <p>In French, every noun has a gender! You must use the correct article:</p>
  
  <table style="width: 100%; border-collapse: collapse; margin: 1rem 0; background: rgba(255,255,255,0.05); border-radius: 8px; overflow: hidden;">
    <thead>
      <tr style="background: rgba(237, 41, 57, 0.3);">
        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ed2939;">Article</th>
        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ed2939;">Gender</th>
        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ed2939;">Examples</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);"><strong style="color: #00d9ff;">Un</strong></td>
        <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">Masculine ♂️</td>
        <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">un café, un croissant, un thé</td>
      </tr>
      <tr>
        <td style="padding: 12px;"><strong style="color: #ff6b9d;">Une</strong></td>
        <td style="padding: 12px;">Feminine ♀️</td>
        <td style="padding: 12px;">une baguette, une eau, une orange</td>
      </tr>
    </tbody>
  </table>
  
  <div style="background: rgba(0, 217, 255, 0.1); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
    💡 <strong>Tip:</strong> You just have to memorize the gender of each noun. There are some patterns, but many exceptions!
  </div>
</div>

---

## 🎮 Practice Quiz

<div class="practice-container">
  <h3 style="margin-top: 0; text-align: center;">🏆 Test Your Knowledge!</h3>
  
  <div id="quiz-q1" style="margin-bottom: 2rem;">
    <p><strong>1. How do you say "15" in French?</strong></p>
    <div class="quiz-option" onclick="checkAnswer(1, 'a', this)">a) cinq</div>
    <div class="quiz-option" onclick="checkAnswer(1, 'b', this)">b) quinze</div>
    <div class="quiz-option" onclick="checkAnswer(1, 'c', this)">c) cinquante</div>
    <div id="feedback-1"></div>
  </div>

  <div id="quiz-q2" style="margin-bottom: 2rem;">
    <p><strong>2. How do you politely say "I would like a coffee"?</strong></p>
    <div class="quiz-option" onclick="checkAnswer(2, 'a', this)">a) Je veux un café</div>
    <div class="quiz-option" onclick="checkAnswer(2, 'b', this)">b) Je voudrais un café</div>
    <div class="quiz-option" onclick="checkAnswer(2, 'c', this)">c) Donne-moi un café</div>
    <div id="feedback-2"></div>
  </div>

  <div id="quiz-q3" style="margin-bottom: 2rem;">
    <p><strong>3. What does "Ça fait combien ?" mean?</strong></p>
    <div class="quiz-option" onclick="checkAnswer(3, 'a', this)">a) What time is it?</div>
    <div class="quiz-option" onclick="checkAnswer(3, 'b', this)">b) How much is it?</div>
    <div class="quiz-option" onclick="checkAnswer(3, 'c', this)">c) Where is it?</div>
    <div id="feedback-3"></div>
  </div>

  <div id="quiz-q4" style="margin-bottom: 2rem;">
    <p><strong>4. Which article do you use with "baguette"?</strong></p>
    <div class="quiz-option" onclick="checkAnswer(4, 'a', this)">a) Un (masculine)</div>
    <div class="quiz-option" onclick="checkAnswer(4, 'b', this)">b) Une (feminine)</div>
    <div class="quiz-option" onclick="checkAnswer(4, 'c', this)">c) Le (definite)</div>
    <div id="feedback-4"></div>
  </div>

  <div id="quiz-q5" style="margin-bottom: 1rem;">
    <p><strong>5. How do you say "7" in French?</strong></p>
    <div class="quiz-option" onclick="checkAnswer(5, 'a', this)">a) six</div>
    <div class="quiz-option" onclick="checkAnswer(5, 'b', this)">b) sept</div>
    <div class="quiz-option" onclick="checkAnswer(5, 'c', this)">c) huit</div>
    <div id="feedback-5"></div>
  </div>

  <div id="final-score" style="text-align: center; margin-top: 1.5rem;"></div>
</div>

<script>
let score = 0;
let answered = 0;
const answers = {
  1: 'b',
  2: 'b',
  3: 'b',
  4: 'b',
  5: 'b'
};

const explanations = {
  1: '"Quinze" means 15. "Cinq" is 5, and "cinquante" is 50!',
  2: '"Je voudrais" is the polite conditional form. "Je veux" (I want) is too direct!',
  3: '"Ça fait combien?" literally means "That makes how much?" - used to ask for the price!',
  4: '"Baguette" is feminine, so we use "une baguette"!',
  5: '"Sept" is 7. Remember: six (6), sept (7), huit (8)!'
};

function checkAnswer(qNum, answer, el) {
  const feedback = document.getElementById('feedback-' + qNum);
  const options = el.parentElement.querySelectorAll('.quiz-option');
  
  // Disable clicks
  options.forEach(opt => opt.style.pointerEvents = 'none');
  
  answered++;
  
  if (answer === answers[qNum]) {
    el.classList.add('correct');
    score++;
    feedback.innerHTML = '<p style="color: #6bcb77; margin-top: 0.5rem;">✅ Correct! ' + explanations[qNum] + '</p>';
  } else {
    el.classList.add('wrong');
    // Highlight correct answer
    options.forEach(opt => {
      if (opt.textContent.startsWith(answers[qNum] + ')')) {
        opt.classList.add('correct');
      }
    });
    feedback.innerHTML = '<p style="color: #ff6b6b; margin-top: 0.5rem;">❌ ' + explanations[qNum] + '</p>';
  }
  
  // Show final score
  if (answered === 5) {
    const scoreDiv = document.getElementById('final-score');
    let emoji = score === 5 ? '🏆' : score >= 3 ? '👍' : '📚';
    scoreDiv.innerHTML = '<h3>' + emoji + ' Your Score: ' + score + '/5</h3><p>' + 
      (score === 5 ? 'Perfect! You\'re ready for Day 3!' : 
       score >= 3 ? 'Good job! Review the mistakes and try again!' : 
       'Keep practicing! Review the vocabulary above.') + '</p>';
  }
}
</script>

---

## 📖 Summary Table: Numbers

| Number | French | Pronunciation |
|--------|--------|---------------|
| 0 | zéro | ZAY-roh |
| 1 | un | uhn |
| 2 | deux | duh |
| 3 | trois | twah |
| 4 | quatre | KAH-truh |
| 5 | cinq | sank |
| 6 | six | sees |
| 7 | sept | set |
| 8 | huit | weet |
| 9 | neuf | nuhf |
| 10 | dix | dees |

---

## 🎯 Homework

Practice these scenarios:

1. **Count from 1 to 20** out loud three times
2. **Role-play**: Pretend to order at a café: "Je voudrais un café et un croissant, s'il vous plaît"
3. **Practice asking** "Ça fait combien ?" when shopping

---

<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #3d2914 0%, #5c3d1e 100%); border-radius: 16px; color: white; margin-top: 2rem; border: 3px solid #8b6914;">
  <h3>🇫🇷 Excellent travail ! (Excellent work!)</h3>
  <p>You've completed Day 2 of French Conversation! ☕🥐</p>
  <p style="font-size: 1.5rem;">À demain ! (See you tomorrow!)</p>
  <p style="color: #ffd700;">ជួបគ្នាថ្ងៃស្អែក!</p>
</div>
