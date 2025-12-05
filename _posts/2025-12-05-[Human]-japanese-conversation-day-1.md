---
layout: post
title: "[Human] Japanese Day 1: Your First Words 🇯🇵👶"
tags: [Japanese, Language, Khmer, Conversation, Beginner]
thumbnail: /images/japanese_day_1.svg
---

<style>
/* Japanese Learning Styles */
.jp-card {
  background: linear-gradient(135deg, #bc002d 0%, #1a1a2e 100%);
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

.jp-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: 0.5s;
}

.jp-card:hover::before {
  left: 100%;
}

.jp-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(188, 0, 45, 0.4);
  border-color: #ffd700;
}

.jp-word {
  font-size: 3rem;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.jp-romaji {
  font-size: 1.3rem;
  color: #87ceeb;
  font-style: italic;
  margin-bottom: 0.5rem;
}

.jp-pronunciation {
  font-size: 1.1rem;
  color: #ffd700;
  margin-bottom: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.jp-meaning {
  color: #e0e0e0;
  margin-bottom: 0.8rem;
  font-size: 1.1rem;
}

.jp-khmer {
  color: #ff9999;
  font-size: 1.2rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255,255,255,0.2);
}

.dialogue-box {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 2rem;
  margin: 2rem 0;
  color: white;
  border-left: 5px solid #bc002d;
}

.dialogue-line {
  display: flex;
  gap: 1rem;
  margin: 1.2rem 0;
  padding: 1rem;
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.dialogue-line:hover {
  background: rgba(255,255,255,0.1);
  transform: translateX(10px);
}

.speaker {
  font-weight: bold;
  min-width: 80px;
  color: #00d9ff;
}

.speaker.b {
  color: #ff6b9d;
}

.jp-text {
  color: #ffffff;
  font-weight: 500;
  font-size: 1.8rem;
}

.romaji-text {
  color: #87ceeb;
  font-size: 1rem;
  margin-top: 0.2rem;
}

.khmer-text {
  color: #ffd700;
  font-size: 0.95rem;
  margin-top: 0.3rem;
}

.section-header {
  background: linear-gradient(90deg, #bc002d, #ffffff, #bc002d);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.8rem;
  font-weight: bold;
  margin: 2rem 0 1rem 0;
}

.tip-box {
  background: rgba(188, 0, 45, 0.1);
  border: 2px solid #bc002d;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1.5rem 0;
}

.tip-box h4 {
  color: #bc002d;
  margin-top: 0;
}

.vocab-grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.audio-btn {
  background: linear-gradient(135deg, #bc002d, #8b0020);
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
  box-shadow: 0 5px 15px rgba(188, 0, 45, 0.4);
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
  background: linear-gradient(90deg, #bc002d, #ffd700);
  width: 14%;
  border-radius: 5px;
  transition: width 0.5s ease;
}

/* Hiragana Grid */
.hiragana-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1rem;
  margin: 2rem 0;
}

.hiragana-card {
  background: linear-gradient(135deg, #bc002d, #8b0020);
  border-radius: 16px;
  padding: 1.5rem;
  text-align: center;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 3px solid transparent;
}

.hiragana-card:hover {
  transform: scale(1.1) rotate(2deg);
  border-color: #ffd700;
  box-shadow: 0 10px 30px rgba(188, 0, 45, 0.5);
}

.hiragana-card .char {
  font-size: 3rem;
  font-weight: bold;
  display: block;
  margin-bottom: 0.5rem;
}

.hiragana-card .romaji {
  font-size: 1.2rem;
  color: #ffd700;
}

.hiragana-card .sound {
  font-size: 0.9rem;
  color: #87ceeb;
  margin-top: 0.3rem;
}

.baby-talk {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  border-radius: 20px;
  padding: 2rem;
  margin: 2rem 0;
  color: #333;
  text-align: center;
}

.baby-talk h3 {
  color: #bc002d;
  margin-top: 0;
}

.repeat-box {
  background: rgba(255,255,255,0.9);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1rem 0;
  font-size: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.repeat-box:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 20px rgba(0,0,0,0.2);
}

@media (max-width: 600px) {
  .hiragana-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .hiragana-card .char {
    font-size: 2rem;
  }
}
</style>

<div class="flag-emoji">🇯🇵 👶 🌸</div>

Welcome to **Day 1** of Japanese! Today, we learn like a baby - just **sounds** and **simple words**. No complicated grammar. Just listen, repeat, and have fun! 🎉

<div class="progress-bar">
  <div class="progress-fill"></div>
</div>
<p style="text-align: center; opacity: 0.7;">👶 Day 1 of 7 - Absolute Beginner</p>

---

## 🎯 Today's Simple Goals

Just like a baby, today you will:
- 👂 **Listen** to the 5 basic sounds (vowels)
- 🗣️ **Repeat** them out loud (many times!)
- 😊 **Learn 5 simple words** that every Japanese baby knows

**No reading. No writing. Just sounds!** 🔊

---

<h2 class="section-header">🔤 The 5 Magic Sounds</h2>

Japanese has only **5 vowel sounds**. Master these first! Click each one to hear it:

<div class="hiragana-grid">
  <div class="hiragana-card" onclick="speakJapanese('あ')">
    <span class="char">あ</span>
    <span class="romaji">a</span>
    <span class="sound">like "ah" in "father"</span>
  </div>
  
  <div class="hiragana-card" onclick="speakJapanese('い')">
    <span class="char">い</span>
    <span class="romaji">i</span>
    <span class="sound">like "ee" in "see"</span>
  </div>
  
  <div class="hiragana-card" onclick="speakJapanese('う')">
    <span class="char">う</span>
    <span class="romaji">u</span>
    <span class="sound">like "oo" in "food"</span>
  </div>
  
  <div class="hiragana-card" onclick="speakJapanese('え')">
    <span class="char">え</span>
    <span class="romaji">e</span>
    <span class="sound">like "e" in "bed"</span>
  </div>
  
  <div class="hiragana-card" onclick="speakJapanese('お')">
    <span class="char">お</span>
    <span class="romaji">o</span>
    <span class="sound">like "o" in "go"</span>
  </div>
</div>

<div class="baby-talk">
  <h3>👶 Baby Practice Time!</h3>
  <p>Say these sounds out loud, just like a baby babbling:</p>
  <div class="repeat-box" onclick="speakJapanese('あ い う え お')">
    あ → い → う → え → お
  </div>
  <p style="font-size: 1.2rem; margin-top: 1rem;">🔊 Click and repeat 10 times!</p>
</div>

---

<h2 class="section-header">👋 Your First 5 Words</h2>

These are words every Japanese child learns first. Super simple!

<div class="vocab-grid">

  <div class="jp-card" onclick="speakJapanese('おはよう')">
    <div class="jp-word">おはよう</div>
    <div class="jp-romaji">Ohayou</div>
    <div class="jp-pronunciation">
      <button class="audio-btn" onclick="event.stopPropagation(); speakJapanese('おはよう')">🔊 Listen</button>
      <span>oh-ha-yoh</span>
    </div>
    <div class="jp-meaning">Good morning! ☀️</div>
    <div class="jp-khmer">🇰🇭 អរុណសួស្តី (Arun suosdey)</div>
  </div>

  <div class="jp-card" onclick="speakJapanese('こんにちは')">
    <div class="jp-word">こんにちは</div>
    <div class="jp-romaji">Konnichiwa</div>
    <div class="jp-pronunciation">
      <button class="audio-btn" onclick="event.stopPropagation(); speakJapanese('こんにちは')">🔊 Listen</button>
      <span>kon-nee-chee-wah</span>
    </div>
    <div class="jp-meaning">Hello! (daytime) 👋</div>
    <div class="jp-khmer">🇰🇭 សួស្តី (Suosdey)</div>
  </div>

  <div class="jp-card" onclick="speakJapanese('ありがとう')">
    <div class="jp-word">ありがとう</div>
    <div class="jp-romaji">Arigatou</div>
    <div class="jp-pronunciation">
      <button class="audio-btn" onclick="event.stopPropagation(); speakJapanese('ありがとう')">🔊 Listen</button>
      <span>ah-ree-gah-toh</span>
    </div>
    <div class="jp-meaning">Thank you! 🙏</div>
    <div class="jp-khmer">🇰🇭 អរគុណ (Arkoun)</div>
  </div>

  <div class="jp-card" onclick="speakJapanese('ごめんなさい')">
    <div class="jp-word">ごめんなさい</div>
    <div class="jp-romaji">Gomen nasai</div>
    <div class="jp-pronunciation">
      <button class="audio-btn" onclick="event.stopPropagation(); speakJapanese('ごめんなさい')">🔊 Listen</button>
      <span>goh-men-nah-sigh</span>
    </div>
    <div class="jp-meaning">I'm sorry! 😔</div>
    <div class="jp-khmer">🇰🇭 សុំទោស (Som tos)</div>
  </div>

  <div class="jp-card" onclick="speakJapanese('はい')">
    <div class="jp-word">はい</div>
    <div class="jp-romaji">Hai</div>
    <div class="jp-pronunciation">
      <button class="audio-btn" onclick="event.stopPropagation(); speakJapanese('はい')">🔊 Listen</button>
      <span>high</span>
    </div>
    <div class="jp-meaning">Yes! ✓</div>
    <div class="jp-khmer">🇰🇭 បាទ/ចាស (Bat/Chas)</div>
  </div>

  <div class="jp-card" onclick="speakJapanese('いいえ')">
    <div class="jp-word">いいえ</div>
    <div class="jp-romaji">Iie</div>
    <div class="jp-pronunciation">
      <button class="audio-btn" onclick="event.stopPropagation(); speakJapanese('いいえ')">🔊 Listen</button>
      <span>ee-eh</span>
    </div>
    <div class="jp-meaning">No ✗</div>
    <div class="jp-khmer">🇰🇭 ទេ (Te)</div>
  </div>

</div>

<script>
// Text-to-Speech for Japanese pronunciation
function speakJapanese(text) {
  if ('speechSynthesis' in window) {
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ja-JP';
    utterance.rate = 0.7; // Slow for learning
    utterance.pitch = 1;
    
    // Try to find a Japanese voice
    const voices = window.speechSynthesis.getVoices();
    const japaneseVoices = voices.filter(voice => voice.lang.startsWith('ja'));
    
    if (japaneseVoices.length > 0) {
      utterance.voice = japaneseVoices[0];
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

<h2 class="section-header">🗣️ Baby's First Conversation</h2>

Just 3 lines! Super easy!

<div class="dialogue-box">
  <h3 style="margin-top: 0; text-align: center;">🌸 Meeting a Friend</h3>
  
  <div class="dialogue-line" onclick="speakJapanese('こんにちは')">
    <span class="speaker">You:</span>
    <div>
      <div class="jp-text">こんにちは！</div>
      <div class="romaji-text">Konnichiwa!</div>
      <div class="khmer-text">សួស្តី!</div>
    </div>
  </div>
  
  <div class="dialogue-line" onclick="speakJapanese('こんにちは')">
    <span class="speaker b">Friend:</span>
    <div>
      <div class="jp-text">こんにちは！</div>
      <div class="romaji-text">Konnichiwa!</div>
      <div class="khmer-text">សួស្តី!</div>
    </div>
  </div>
  
  <div class="dialogue-line" onclick="speakJapanese('ありがとう')">
    <span class="speaker">You:</span>
    <div>
      <div class="jp-text">ありがとう！</div>
      <div class="romaji-text">Arigatou!</div>
      <div class="khmer-text">អរគុណ!</div>
    </div>
  </div>
</div>

---

<h2 class="section-header">💡 Baby Tip</h2>

<div class="tip-box">
  <h4>👶 Learn Like a Baby!</h4>
  
  <p>Babies don't study grammar. They just:</p>
  
  <table style="width: 100%; border-collapse: collapse; margin: 1rem 0; background: rgba(255,255,255,0.05); border-radius: 8px; overflow: hidden;">
    <tbody>
      <tr>
        <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 2rem; text-align: center;">👂</td>
        <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);"><strong style="color: #00d9ff;">LISTEN</strong> - Hear the sounds many times</td>
      </tr>
      <tr>
        <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 2rem; text-align: center;">🗣️</td>
        <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);"><strong style="color: #ffd700;">REPEAT</strong> - Copy the sounds (don't be shy!)</td>
      </tr>
      <tr>
        <td style="padding: 12px; font-size: 2rem; text-align: center;">🔄</td>
        <td style="padding: 12px;"><strong style="color: #ff6b9d;">AGAIN</strong> - Do it many, many times!</td>
      </tr>
    </tbody>
  </table>
  
  <div style="background: rgba(0, 217, 255, 0.1); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
    💡 <strong>Secret:</strong> Babies hear "mama" 1000 times before saying it. Repeat each word at least 10 times today!
  </div>
</div>

---

## 🎮 Listen & Match Game

<div class="practice-container">
  <h3 style="margin-top: 0; text-align: center;">🏆 Can You Remember?</h3>
  
  <div id="quiz-q1" style="margin-bottom: 2rem;">
    <p><strong>1. What does こんにちは (Konnichiwa) mean?</strong></p>
    <div class="quiz-option" onclick="checkAnswer(1, 'a', this)">a) Thank you</div>
    <div class="quiz-option" onclick="checkAnswer(1, 'b', this)">b) Hello</div>
    <div class="quiz-option" onclick="checkAnswer(1, 'c', this)">c) Goodbye</div>
    <div id="feedback-1"></div>
  </div>

  <div id="quiz-q2" style="margin-bottom: 2rem;">
    <p><strong>2. How do you say "Thank you" in Japanese?</strong></p>
    <div class="quiz-option" onclick="checkAnswer(2, 'a', this)">a) はい (Hai)</div>
    <div class="quiz-option" onclick="checkAnswer(2, 'b', this)">b) ごめんなさい (Gomen nasai)</div>
    <div class="quiz-option" onclick="checkAnswer(2, 'c', this)">c) ありがとう (Arigatou)</div>
    <div id="feedback-2"></div>
  </div>

  <div id="quiz-q3" style="margin-bottom: 2rem;">
    <p><strong>3. What sound does あ make?</strong></p>
    <div class="quiz-option" onclick="checkAnswer(3, 'a', this)">a) "ah" like in "father"</div>
    <div class="quiz-option" onclick="checkAnswer(3, 'b', this)">b) "ee" like in "see"</div>
    <div class="quiz-option" onclick="checkAnswer(3, 'c', this)">c) "oo" like in "food"</div>
    <div id="feedback-3"></div>
  </div>

  <div id="quiz-q4" style="margin-bottom: 2rem;">
    <p><strong>4. はい (Hai) means:</strong></p>
    <div class="quiz-option" onclick="checkAnswer(4, 'a', this)">a) No</div>
    <div class="quiz-option" onclick="checkAnswer(4, 'b', this)">b) Yes</div>
    <div class="quiz-option" onclick="checkAnswer(4, 'c', this)">c) Maybe</div>
    <div id="feedback-4"></div>
  </div>

  <div id="quiz-q5" style="margin-bottom: 1rem;">
    <p><strong>5. How many vowel sounds does Japanese have?</strong></p>
    <div class="quiz-option" onclick="checkAnswer(5, 'a', this)">a) 3</div>
    <div class="quiz-option" onclick="checkAnswer(5, 'b', this)">b) 5</div>
    <div class="quiz-option" onclick="checkAnswer(5, 'c', this)">c) 10</div>
    <div id="feedback-5"></div>
  </div>

  <div id="final-score" style="text-align: center; margin-top: 1.5rem;"></div>
</div>

<script>
let score = 0;
let answered = 0;
const answers = {
  1: 'b',
  2: 'c',
  3: 'a',
  4: 'b',
  5: 'b'
};

const explanations = {
  1: 'こんにちは (Konnichiwa) means "Hello"! 👋',
  2: 'ありがとう (Arigatou) means "Thank you"! 🙏',
  3: 'あ (a) sounds like "ah" in "father"! Try saying it!',
  4: 'はい (Hai) means "Yes"! いいえ (Iie) means "No"!',
  5: 'Japanese has 5 vowels: あ(a) い(i) う(u) え(e) お(o)!'
};

function checkAnswer(qNum, answer, el) {
  const feedback = document.getElementById('feedback-' + qNum);
  const options = el.parentElement.querySelectorAll('.quiz-option');
  
  options.forEach(opt => opt.style.pointerEvents = 'none');
  
  answered++;
  
  if (answer === answers[qNum]) {
    el.classList.add('correct');
    score++;
    feedback.innerHTML = '<p style="color: #6bcb77; margin-top: 0.5rem;">✅ すごい! (Sugoi - Amazing!) ' + explanations[qNum] + '</p>';
  } else {
    el.classList.add('wrong');
    options.forEach(opt => {
      if (opt.textContent.startsWith(answers[qNum] + ')')) {
        opt.classList.add('correct');
      }
    });
    feedback.innerHTML = '<p style="color: #ff6b6b; margin-top: 0.5rem;">❌ ' + explanations[qNum] + '</p>';
  }
  
  if (answered === 5) {
    const scoreDiv = document.getElementById('final-score');
    let emoji = score === 5 ? '🏆' : score >= 3 ? '👍' : '📚';
    let message = score === 5 ? 'すごい! (Sugoi!) Perfect! You\'re ready for Day 2!' : 
                  score >= 3 ? 'いいね! (Iine!) Good job! Practice more!' : 
                  'がんばれ! (Ganbare!) Keep trying!';
    scoreDiv.innerHTML = '<h3>' + emoji + ' Your Score: ' + score + '/5</h3><p>' + message + '</p>';
  }
}
</script>

---

## 📖 Today's Summary

| Japanese | Romaji | Meaning | Khmer |
|----------|--------|---------|-------|
| あ い う え お | a i u e o | 5 vowel sounds | ស្រៈ ៥ |
| おはよう | Ohayou | Good morning | អរុណសួស្តី |
| こんにちは | Konnichiwa | Hello | សួស្តី |
| ありがとう | Arigatou | Thank you | អរគុណ |
| ごめんなさい | Gomen nasai | I'm sorry | សុំទោស |
| はい | Hai | Yes | បាទ/ចាស |
| いいえ | Iie | No | ទេ |

---

## 🎯 Baby Homework

Do these 3 things today:

1. **🔊 Listen** to あ い う え お 20 times (click the cards!)
2. **🗣️ Say** こんにちは (Konnichiwa) 10 times out loud
3. **🙏 Say** ありがとう (Arigatou) every time you thank someone today!

---

<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #bc002d 0%, #1a1a2e 100%); border-radius: 16px; color: white; margin-top: 2rem;">
  <h3>🇯🇵 がんばったね！(Ganbatta ne!)</h3>
  <p>You did great!</p>
  <p style="font-size: 2rem;">おつかれさま！</p>
  <p style="font-size: 1.2rem; color: #87ceeb;">(Otsukaresama - Good work!)</p>
  <p style="color: #ffd700;">ជួបគ្នាថ្ងៃស្អែក! (See you tomorrow!)</p>
</div>
