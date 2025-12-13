---
layout: post
title: "[Human] English Grammar Mastery: Learn with Fun Real-World Examples! 🌍📚"
tags: [English, Grammar, Learning, Business, Technology, Science, Daily Usage]
thumbnail: /images/english_grammar_thumbnail.png
---

<style>
/* Interactive Learning Styles */
.grammar-game {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 2rem;
  margin: 2rem 0;
  color: white;
}

.time-machine {
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin: 2rem 0;
  flex-wrap: wrap;
  gap: 1rem;
}

.time-zone {
  text-align: center;
  padding: 1.5rem;
  border-radius: 12px;
  min-width: 150px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.time-zone:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.time-zone.past {
  background: linear-gradient(135deg, #c79081 0%, #dfa579 100%);
}

.time-zone.present {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.time-zone.future {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.time-zone .emoji {
  font-size: 3rem;
  display: block;
  margin-bottom: 0.5rem;
}

.drag-zone {
  min-height: 60px;
  border: 2px dashed rgba(255,255,255,0.3);
  border-radius: 8px;
  padding: 1rem;
  margin: 0.5rem 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.drag-zone.highlight {
  border-color: #6bcb77;
  background: rgba(107, 203, 119, 0.1);
}

.draggable {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: grab;
  user-select: none;
  transition: all 0.2s ease;
}

.draggable:hover {
  transform: scale(1.05);
}

.draggable:active {
  cursor: grabbing;
  transform: scale(0.95);
}

.draggable.correct {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.draggable.incorrect {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

.strength-meter {
  width: 100%;
  height: 300px;
  background: linear-gradient(to top, #1a1a2e, #2d1b69);
  border-radius: 12px;
  position: relative;
  overflow: hidden;
}

.modal-level {
  position: absolute;
  left: 0;
  right: 0;
  padding: 0.8rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-level:hover {
  background: rgba(255,255,255,0.1);
}

.modal-level .bar {
  height: 8px;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.quiz-option {
  background: rgba(255,255,255,0.1);
  padding: 1rem;
  margin: 0.5rem 0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.quiz-option:hover {
  background: rgba(255,255,255,0.2);
  border-color: #667eea;
}

.quiz-option.selected {
  border-color: #ffd93d;
}

.quiz-option.correct {
  background: rgba(107, 203, 119, 0.3);
  border-color: #6bcb77;
}

.quiz-option.wrong {
  background: rgba(255, 107, 107, 0.3);
  border-color: #ff6b6b;
}

.sentence-builder {
  background: rgba(255,255,255,0.05);
  padding: 1.5rem;
  border-radius: 12px;
  margin: 1rem 0;
}

.word-bank {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
  min-height: 50px;
}

.sentence-area {
  min-height: 60px;
  border: 2px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.animated-example {
  overflow: hidden;
}

.typing-text {
  display: inline-block;
  border-right: 2px solid #00d9ff;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { border-color: #00d9ff; }
  50% { border-color: transparent; }
}

.flip-card {
  perspective: 1000px;
  cursor: pointer;
}

.flip-card-inner {
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flip-card.flipped .flip-card-inner {
  transform: rotateY(180deg);
}

.flip-card-front, .flip-card-back {
  backface-visibility: hidden;
  border-radius: 12px;
  padding: 1.5rem;
}

.flip-card-back {
  transform: rotateY(180deg);
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
}

.progress-bar {
  height: 8px;
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 1rem 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.5s ease;
}

.score-display {
  font-size: 2rem;
  text-align: center;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  margin: 1rem 0;
}

.celebration {
  animation: celebrate 0.5s ease;
}

@keyframes celebrate {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}
</style>

Ever felt confused about when to use **"has been"** vs **"was"**? Or wondered why Elon Musk says *"Tesla **has launched** a new product"* instead of *"Tesla **launched** a new product"*? 🤔

Welcome to your **fun grammar playground** where we learn English through real examples from the worlds of **Business, Policy, Science, and Technology**!

<div class="grammar-game">
  <h3 style="margin-top: 0; text-align: center; color: #00d9ff;">📊 Your Learning Progress</h3>
  <div class="progress-bar">
    <div class="progress-fill" id="mainProgress" style="width: 0%;"></div>
  </div>
  <div style="display: flex; justify-content: space-between; font-size: 0.9rem; opacity: 0.7;">
    <span>Beginner</span>
    <span>Intermediate</span>
    <span>Master!</span>
  </div>
</div>

---

## 🎯 Why Grammar Matters (Even for Geniuses!)

Even the smartest people need good grammar to communicate clearly:

<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; color: white; margin: 1.5rem 0;">
  <strong>🚀 Elon Musk (CEO of Tesla/SpaceX):</strong><br>
  "We <strong>have achieved</strong> full self-driving capability."<br>
  <small style="opacity: 0.8;">→ Uses Present Perfect because the achievement affects NOW</small>
</div>

<div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 12px; color: white; margin: 1.5rem 0;">
  <strong>💰 Warren Buffett (Investor):</strong><br>
  "If we <strong>had invested</strong> earlier, we <strong>would have</strong> made billions more."<br>
  <small style="opacity: 0.8;">→ Uses Third Conditional for past hypothetical situations</small>
</div>

---

## 📚 Topic 1: Tenses - The Time Machine of English! ⏰

Imagine tenses as a **time machine** that takes your sentences to different moments! Click on each time zone to see examples:

<!-- Interactive Time Machine -->
<div class="grammar-game">
  <h4 style="text-align: center; margin-top: 0; color: #00d9ff;">🚀 Click a Time Zone!</h4>
  
  <div class="time-machine">
    <div class="time-zone past" onclick="showTenseExample('past')">
      <span class="emoji">🏛️</span>
      <strong>PAST</strong><br>
      <small>Yesterday, in 2020, last week</small>
    </div>
    <div class="time-zone present" onclick="showTenseExample('present')">
      <span class="emoji">⚡</span>
      <strong>PRESENT</strong><br>
      <small>Now, already, just, ever</small>
    </div>
    <div class="time-zone future" onclick="showTenseExample('future')">
      <span class="emoji">🚀</span>
      <strong>FUTURE</strong><br>
      <small>Tomorrow, next week, will</small>
    </div>
  </div>
  
  <div id="tense-example" style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 12px; text-align: center; min-height: 80px;">
    <p style="margin: 0; opacity: 0.7;">👆 Click a time zone to see sentence examples!</p>
  </div>
</div>

<script>
function showTenseExample(tense) {
  const examples = {
    past: {
      business: '💼 "Apple <strong>launched</strong> the iPhone in 2007."',
      tech: '🤖 "OpenAI <strong>released</strong> GPT-3 in 2020."',
      policy: '🏛️ "The president <strong>signed</strong> the bill last March."',
      tip: '⏰ Use when the action is FINISHED and time is SPECIFIC!'
    },
    present: {
      business: '💼 "Apple <strong>has sold</strong> over 2 billion iPhones." (still selling!)',
      tech: '🤖 "OpenAI <strong>has just released</strong> a new model!" (breaking news!)',
      policy: '🏛️ "The government <strong>has implemented</strong> new regulations."',
      tip: '🔗 Use when the action CONNECTS to NOW or time is NOT important!'
    },
    future: {
      business: '💼 "Tesla <strong>will launch</strong> the Roadster next year."',
      tech: '🤖 "AI <strong>will transform</strong> every industry by 2030."',
      policy: '🏛️ "New laws <strong>will be passed</strong> next session."',
      tip: '🔮 Use for predictions, plans, and things that WILL happen!'
    }
  };
  
  const ex = examples[tense];
  document.getElementById('tense-example').innerHTML = `
    <div style="text-align: left;">
      <p style="margin: 0.5rem 0;">${ex.business}</p>
      <p style="margin: 0.5rem 0;">${ex.tech}</p>
      <p style="margin: 0.5rem 0;">${ex.policy}</p>
      <p style="margin: 1rem 0 0 0; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2); color: #6bcb77;">${ex.tip}</p>
    </div>
  `;
}
</script>

### 🔵 Present Perfect vs Simple Past

This is the **#1 confusion** for English learners! Let's master it:

<div style="background: #1a1a2e; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0; color: white;">
  <h4 style="margin-top: 0; color: #00d9ff;">📊 The Rule:</h4>
  <table style="width: 100%; color: white; border-collapse: collapse;">
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.2);">
      <td style="padding: 12px;"><strong>Simple Past</strong></td>
      <td style="padding: 12px;">Finished action, specific time mentioned</td>
      <td style="padding: 12px; color: #ffd93d;">Yesterday, in 2020, last week</td>
    </tr>
    <tr>
      <td style="padding: 12px;"><strong>Present Perfect</strong></td>
      <td style="padding: 12px;">Action connected to NOW, or time not important</td>
      <td style="padding: 12px; color: #6bcb77;">Ever, never, just, already, yet</td>
    </tr>
  </table>
</div>

### 🎮 Interactive Exercise: Build the Sentence!

<div class="grammar-game">
  <h4 style="margin-top: 0; color: #ffd93d;">📝 Drag words to complete the sentence correctly:</h4>
  
  <div class="sentence-builder">
    <p style="margin-bottom: 1rem;"><strong>Question:</strong> Tesla _____ electric vehicles since 2008.</p>
    
    <div class="word-bank" id="tenseWordBank">
      <span class="draggable" onclick="selectTenseWord(this, 'produces')">produces</span>
      <span class="draggable" onclick="selectTenseWord(this, 'has produced')">has produced ✓</span>
      <span class="draggable" onclick="selectTenseWord(this, 'produced')">produced</span>
    </div>
    
    <div class="sentence-area" id="tenseAnswer" style="min-height: 50px;">
      <span style="opacity: 0.5;">Click the correct answer above!</span>
    </div>
    
    <div id="tenseFeedback" style="margin-top: 1rem; text-align: center;"></div>
  </div>
</div>

<script>
function selectTenseWord(el, answer) {
  const correct = 'has produced';
  const answerArea = document.getElementById('tenseAnswer');
  const feedback = document.getElementById('tenseFeedback');
  
  // Reset all words
  document.querySelectorAll('#tenseWordBank .draggable').forEach(w => {
    w.classList.remove('correct', 'incorrect');
  });
  
  if (answer === correct) {
    el.classList.add('correct');
    answerArea.innerHTML = '<span class="draggable correct">has produced ✓</span>';
    feedback.innerHTML = '🎉 <strong style="color: #6bcb77;">Correct!</strong> "Since 2008" shows the action started in the past and continues to NOW!';
    updateProgress(20);
  } else {
    el.classList.add('incorrect');
    feedback.innerHTML = '❌ <strong style="color: #ff6b6b;">Try again!</strong> Look for the signal word "since" - it needs Present Perfect!';
  }
}
</script>

### 💼 Business Examples:

```
✅ SIMPLE PAST (Specific time):
"Apple launched the iPhone in 2007."
"We signed the contract last Tuesday."
"The company went public in 2019."

✅ PRESENT PERFECT (Connected to now):
"Apple has sold over 2 billion iPhones." (still selling!)
"We have already signed the contract." (it's done now!)
"The company has grown 300% since 2019." (still growing!)
```

### 🔬 Science & Technology Examples:

<div style="display: grid; gap: 1rem; margin: 2rem 0;">
  <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 12px; color: white;">
    <strong>🤖 AI News:</strong><br>
    "OpenAI <strong>has released</strong> GPT-5." (Breaking news - affects now!)<br>
    "OpenAI <strong>released</strong> GPT-3 in 2020." (Historical fact)
  </div>
  
  <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 1.5rem; border-radius: 12px; color: white;">
    <strong>🚀 SpaceX:</strong><br>
    "SpaceX <strong>has landed</strong> over 200 rockets successfully!" (Achievement!)<br>
    "SpaceX <strong>landed</strong> its first rocket in 2015." (Specific date)
  </div>
</div>

### 🏛️ Policy Examples:

```
✅ Government Announcement Today:
"The president HAS SIGNED the new climate bill."
→ Just happened, affects us now!

✅ History Textbook:
"The president SIGNED the climate bill on March 15, 2025."
→ Historical record, specific date
```

---

## 📚 Topic 2: Conditionals - The "What If" World! 🌈

Conditionals help us talk about possibilities, dreams, and regrets!

### 🎮 Interactive: Choose Your Path!

Click on different scenarios to see which conditional type to use:

<div class="grammar-game">
  <h4 style="margin-top: 0; color: #00d9ff; text-align: center;">🌳 The Conditional Decision Tree</h4>
  
  <div style="display: grid; gap: 1rem; margin: 1rem 0;">
    <button onclick="showConditional(0)" style="padding: 1rem; background: linear-gradient(135deg, #00d9ff 0%, #0099cc 100%); border: none; border-radius: 8px; color: white; cursor: pointer; font-size: 1rem;">
      🔬 "Water boils at 100°C" - Universal fact
    </button>
    <button onclick="showConditional(1)" style="padding: 1rem; background: linear-gradient(135deg, #6bcb77 0%, #38f9d7 100%); border: none; border-radius: 8px; color: white; cursor: pointer; font-size: 1rem;">
      📈 "If the market improves..." - Real possibility
    </button>
    <button onclick="showConditional(2)" style="padding: 1rem; background: linear-gradient(135deg, #ffd93d 0%, #ff9500 100%); border: none; border-radius: 8px; color: white; cursor: pointer; font-size: 1rem;">
      💭 "If I were a billionaire..." - Imaginary now
    </button>
    <button onclick="showConditional(3)" style="padding: 1rem; background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%); border: none; border-radius: 8px; color: white; cursor: pointer; font-size: 1rem;">
      😢 "If I had studied harder..." - Regret about past
    </button>
  </div>
  
  <div id="conditional-result" style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 12px; min-height: 100px;">
    <p style="text-align: center; opacity: 0.7; margin: 0;">👆 Click a scenario above to learn which conditional to use!</p>
  </div>
</div>

<script>
function showConditional(type) {
  const results = [
    {
      title: 'Type 0: Universal Truth',
      color: '#00d9ff',
      formula: 'If + present simple, ... present simple',
      example: 'If you heat water to 100°C, it <strong>boils</strong>.',
      business: '💼 "If you invest wisely, you <strong>make</strong> money."',
      tech: '🤖 "If you train a model longer, it <strong>performs</strong> better."'
    },
    {
      title: 'Type 1: Real Future Possibility',
      color: '#6bcb77',
      formula: 'If + present simple, ... will + verb',
      example: 'If it <strong>rains</strong> tomorrow, we <strong>will cancel</strong> the event.',
      business: '💼 "If the market <strong>recovers</strong>, our stocks <strong>will increase</strong>."',
      tech: '🤖 "If AI <strong>becomes</strong> more advanced, it <strong>will change</strong> everything."'
    },
    {
      title: 'Type 2: Unreal Present/Future (Hypothetical)',
      color: '#ffd93d',
      formula: 'If + past simple, ... would + verb',
      example: 'If I <strong>were</strong> rich, I <strong>would travel</strong> the world.',
      business: '💼 "If we <strong>had</strong> more budget, we <strong>would hire</strong> 10 more developers."',
      tech: '🤖 "If AI <strong>had</strong> consciousness, it <strong>would</strong> be scary!"'
    },
    {
      title: 'Type 3: Unreal Past (Regret)',
      color: '#ff6b6b',
      formula: 'If + had + past participle, ... would have + past participle',
      example: 'If I <strong>had studied</strong> harder, I <strong>would have passed</strong> the exam.',
      business: '💼 "If we <strong>had invested</strong> in Bitcoin in 2010, we <strong>would have become</strong> billionaires!"',
      tech: '🤖 "If researchers <strong>had anticipated</strong> this, they <strong>would have designed</strong> better safeguards."'
    }
  ];
  
  const r = results[type];
  document.getElementById('conditional-result').innerHTML = `
    <h4 style="margin-top: 0; color: ${r.color};">${r.title}</h4>
    <p><strong>Formula:</strong> <code>${r.formula}</code></p>
    <p><strong>Example:</strong> "${r.example}"</p>
    <hr style="border-color: rgba(255,255,255,0.2);">
    <p>${r.business}</p>
    <p>${r.tech}</p>
  `;
  updateProgress(40);
}
</script>

### 🔵 The 4 Types of Conditionals

<div style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); padding: 1.5rem; border-radius: 12px; margin: 2rem 0; color: white;">
  <div style="display: grid; gap: 1rem;">
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
      <strong style="color: #00d9ff;">Type 0: Universal Truth</strong><br>
      <code>If + present, ... present</code><br>
      "If you heat water to 100°C, it <strong>boils</strong>."
    </div>
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
      <strong style="color: #6bcb77;">Type 1: Real Future Possibility</strong><br>
      <code>If + present, ... will + verb</code><br>
      "If Tesla <strong>releases</strong> the Roadster, it <strong>will sell</strong> out in hours."
    </div>
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
      <strong style="color: #ffd93d;">Type 2: Unreal Present/Future</strong><br>
      <code>If + past, ... would + verb</code><br>
      "If I <strong>were</strong> the CEO, I <strong>would invest</strong> in AI."
    </div>
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
      <strong style="color: #ff6b6b;">Type 3: Unreal Past (Regret)</strong><br>
      <code>If + had + past participle, ... would have + past participle</code><br>
      "If I <strong>had bought</strong> Bitcoin in 2010, I <strong>would have become</strong> rich."
    </div>
  </div>
</div>

### 💼 Business Examples:

<div style="background: #1a1a2e; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0; color: white;">
  <h4 style="margin-top: 0; color: #ffd93d;">Real Business Scenarios:</h4>
  
  <p><strong>📈 Investment Meeting:</strong></p>
  <ul style="list-style: none; padding: 0;">
    <li>✅ "If the market <strong>recovers</strong>, our stocks <strong>will increase</strong>." (Type 1)</li>
    <li>✅ "If we <strong>had more funding</strong>, we <strong>would expand</strong> faster." (Type 2)</li>
    <li>✅ "If we <strong>had diversified</strong> earlier, we <strong>would have avoided</strong> losses." (Type 3)</li>
  </ul>
  
  <p><strong>🏢 Job Interview:</strong></p>
  <ul style="list-style: none; padding: 0;">
    <li>✅ "If you <strong>hire</strong> me, I <strong>will deliver</strong> results." (Type 1 - Confident!)</li>
    <li>✅ "If I <strong>were</strong> in that position, I <strong>would prioritize</strong> innovation." (Type 2 - Thoughtful)</li>
  </ul>
</div>

### 🔬 Technology Examples:

```
🤖 AI Ethics Discussion:
Type 1: "If AI becomes too powerful, it WILL change society."
Type 2: "If we HAD better regulations, AI WOULD be safer."
Type 3: "If researchers HAD anticipated this, they WOULD HAVE 
         designed better safeguards."

🚀 Space Exploration:
Type 1: "If SpaceX succeeds, humans WILL live on Mars."
Type 2: "If we COLONIZED Mars, we WOULD need new laws."
Type 3: "If we HAD started earlier, we WOULD HAVE reached 
         Mars by now."
```

---

## 📚 Topic 3: Passive Voice - When the Action Matters More! 🎭

### 🔵 When to Use Passive Voice

<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; color: white; margin: 1.5rem 0;">
  <h4 style="margin-top: 0;">🎯 Use Passive When:</h4>
  <ul>
    <li>The <strong>doer</strong> is unknown or unimportant</li>
    <li>The <strong>action or result</strong> is more important</li>
    <li>Writing <strong>formal or scientific</strong> documents</li>
    <li>Avoiding <strong>blame</strong> (corporate speak! 😅)</li>
  </ul>
</div>

### 🔬 Science & Research Examples:

```
❌ Active (Sounds personal):
"I conducted the experiment."
"We collected the data."

✅ Passive (More scientific):
"The experiment WAS CONDUCTED using standard protocols."
"The data WERE COLLECTED over a 6-month period."
"Three variables WERE ANALYZED in this study."
```

### 🏛️ Policy & Government Examples:

<div style="display: grid; gap: 1rem; margin: 2rem 0;">
  <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1.5rem; border-radius: 12px; color: white;">
    <strong>📜 Official Announcements:</strong><br>
    "New regulations <strong>have been implemented</strong>."<br>
    "The law <strong>was passed</strong> by Congress."<br>
    "Taxes <strong>will be reduced</strong> next year."<br>
    <small>→ Passive sounds more formal and authoritative!</small>
  </div>
  
  <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 12px; color: white;">
    <strong>🏢 Corporate "Mistakes Were Made" Language:</strong><br>
    "Mistakes <strong>were made</strong>." (Who made them? 🤔)<br>
    "The data <strong>was compromised</strong>." (Avoids blame!)<br>
    "Your account <strong>has been suspended</strong>." (Sounds official)
  </div>
</div>

### 💼 Business Email Examples:

```
❌ Too Direct (Might sound rude):
"You didn't send the report."
"You made an error in the invoice."

✅ Passive (More diplomatic):
"The report HAS NOT BEEN received yet."
"An error WAS FOUND in the invoice."

❌ Active:
"Our team will process your order."

✅ Passive (Customer-focused):
"Your order WILL BE PROCESSED within 24 hours."
```

---

## 📚 Topic 4: Modal Verbs - Expressing Possibility & Obligation! 💪

### 🎮 Interactive: Modal Verb Power Meter!

Click on each modal verb to see its power level and examples:

<div class="grammar-game">
  <h4 style="margin-top: 0; color: #00d9ff; text-align: center;">⚡ Modal Verb Strength Levels</h4>
  
  <div style="display: flex; flex-direction: column; gap: 0.5rem;">
    <div onclick="showModal('must')" style="cursor: pointer; display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: rgba(255,255,255,0.05); border-radius: 8px; transition: all 0.3s;">
      <span style="width: 80px; font-weight: bold; color: #ff6b6b;">MUST</span>
      <div style="flex: 1; height: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;">
        <div style="width: 100%; height: 100%; background: linear-gradient(90deg, #ff6b6b, #ee5a5a); border-radius: 10px;"></div>
      </div>
      <span style="width: 50px; text-align: right;">100%</span>
    </div>
    
    <div onclick="showModal('should')" style="cursor: pointer; display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: rgba(255,255,255,0.05); border-radius: 8px; transition: all 0.3s;">
      <span style="width: 80px; font-weight: bold; color: #ffd93d;">SHOULD</span>
      <div style="flex: 1; height: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;">
        <div style="width: 80%; height: 100%; background: linear-gradient(90deg, #ffd93d, #ff9500); border-radius: 10px;"></div>
      </div>
      <span style="width: 50px; text-align: right;">80%</span>
    </div>
    
    <div onclick="showModal('can')" style="cursor: pointer; display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: rgba(255,255,255,0.05); border-radius: 8px; transition: all 0.3s;">
      <span style="width: 80px; font-weight: bold; color: #6bcb77;">CAN</span>
      <div style="flex: 1; height: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;">
        <div style="width: 70%; height: 100%; background: linear-gradient(90deg, #6bcb77, #38f9d7); border-radius: 10px;"></div>
      </div>
      <span style="width: 50px; text-align: right;">70%</span>
    </div>
    
    <div onclick="showModal('could')" style="cursor: pointer; display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: rgba(255,255,255,0.05); border-radius: 8px; transition: all 0.3s;">
      <span style="width: 80px; font-weight: bold; color: #4facfe;">COULD</span>
      <div style="flex: 1; height: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;">
        <div style="width: 50%; height: 100%; background: linear-gradient(90deg, #4facfe, #00f2fe); border-radius: 10px;"></div>
      </div>
      <span style="width: 50px; text-align: right;">50%</span>
    </div>
    
    <div onclick="showModal('might')" style="cursor: pointer; display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: rgba(255,255,255,0.05); border-radius: 8px; transition: all 0.3s;">
      <span style="width: 80px; font-weight: bold; color: #ff9ff3;">MIGHT</span>
      <div style="flex: 1; height: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;">
        <div style="width: 30%; height: 100%; background: linear-gradient(90deg, #ff9ff3, #f093fb); border-radius: 10px;"></div>
      </div>
      <span style="width: 50px; text-align: right;">30%</span>
    </div>
  </div>
  
  <div id="modal-result" style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 12px; margin-top: 1rem; min-height: 100px;">
    <p style="text-align: center; opacity: 0.7; margin: 0;">👆 Click a modal verb to see examples!</p>
  </div>
</div>

<script>
function showModal(modal) {
  const modals = {
    must: {
      color: '#ff6b6b',
      meaning: 'Obligation/Necessity - No choice!',
      examples: [
        '💼 "You <strong>must</strong> submit the report by Friday." (Order)',
        '🏛️ "Citizens <strong>must</strong> pay taxes." (Law)',
        '🤖 "AI systems <strong>must</strong> be transparent." (Requirement)'
      ]
    },
    should: {
      color: '#ffd93d',
      meaning: 'Advice/Recommendation - Good idea!',
      examples: [
        '💼 "You <strong>should</strong> invest in index funds." (Advice)',
        '🏛️ "Governments <strong>should</strong> regulate AI." (Recommendation)',
        '🤖 "Developers <strong>should</strong> test their code." (Best practice)'
      ]
    },
    can: {
      color: '#6bcb77',
      meaning: 'Ability/General Possibility',
      examples: [
        '💼 "Our company <strong>can</strong> deliver worldwide." (Ability)',
        '🤖 "AI <strong>can</strong> process millions of data points." (Capability)',
        '🔬 "This technology <strong>can</strong> save lives." (Potential)'
      ]
    },
    could: {
      color: '#4facfe',
      meaning: 'Polite Request/Possibility/Past Ability',
      examples: [
        '💼 "<strong>Could</strong> you send me the report?" (Polite)',
        '🤖 "AI <strong>could</strong> replace some jobs." (Possibility)',
        '🔬 "We <strong>could</strong> try a different approach." (Suggestion)'
      ]
    },
    might: {
      color: '#ff9ff3',
      meaning: 'Uncertainty/Low Possibility',
      examples: [
        '💼 "The market <strong>might</strong> crash next year." (Uncertain)',
        '🤖 "AI <strong>might</strong> become sentient someday." (Speculation)',
        '🔬 "This experiment <strong>might</strong> fail." (Possibility)'
      ]
    }
  };
  
  const m = modals[modal];
  document.getElementById('modal-result').innerHTML = `
    <h4 style="margin-top: 0; color: ${m.color};">${modal.toUpperCase()}</h4>
    <p><strong>Meaning:</strong> ${m.meaning}</p>
    <hr style="border-color: rgba(255,255,255,0.2);">
    ${m.examples.map(e => `<p style="margin: 0.5rem 0;">${e}</p>`).join('')}
  `;
  updateProgress(60);
}
</script>

### 🔵 The Power of Modals

<div style="background: #1a1a2e; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0; color: white;">
  <table style="width: 100%; color: white; border-collapse: collapse;">
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.2);">
      <td style="padding: 12px;"><strong style="color: #ff6b6b;">MUST</strong></td>
      <td style="padding: 12px;">Obligation/Necessity (100%)</td>
      <td style="padding: 12px;">"You must wear a seatbelt."</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.2);">
      <td style="padding: 12px;"><strong style="color: #ffd93d;">SHOULD</strong></td>
      <td style="padding: 12px;">Advice/Recommendation (80%)</td>
      <td style="padding: 12px;">"You should invest in ETFs."</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.2);">
      <td style="padding: 12px;"><strong style="color: #6bcb77;">CAN</strong></td>
      <td style="padding: 12px;">Ability/Possibility</td>
      <td style="padding: 12px;">"AI can process data faster."</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.2);">
      <td style="padding: 12px;"><strong style="color: #4facfe;">COULD</strong></td>
      <td style="padding: 12px;">Polite/Past Ability/Possibility</td>
      <td style="padding: 12px;">"Could you send the report?"</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.2);">
      <td style="padding: 12px;"><strong style="color: #ff9ff3;">MIGHT/MAY</strong></td>
      <td style="padding: 12px;">Uncertainty (50%)</td>
      <td style="padding: 12px;">"It might rain tomorrow."</td>
    </tr>
    <tr>
      <td style="padding: 12px;"><strong style="color: #a29bfe;">WOULD</strong></td>
      <td style="padding: 12px;">Hypothetical/Polite Request</td>
      <td style="padding: 12px;">"I would recommend option A."</td>
    </tr>
  </table>
</div>

### 🔬 Technology Headlines:

```
🤖 AI News:
"AI COULD replace 40% of jobs by 2030." (Possibility)
"Governments SHOULD regulate AI development." (Recommendation)
"Tech companies MUST disclose AI training data." (Obligation)
"ChatGPT CAN write code, but it MIGHT make errors." (Ability + Uncertainty)

🚗 Self-Driving Cars:
"Autonomous vehicles WILL BE able to save lives." (Future ability)
"Drivers MIGHT NOT need licenses in the future." (Possibility)
"Cars SHOULD have backup safety systems." (Recommendation)
```

### 💼 Professional Email Politeness Scale:

<div style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); padding: 1.5rem; border-radius: 12px; margin: 2rem 0; color: white;">
  <h4 style="margin-top: 0; color: #00d9ff;">From Direct → Ultra Polite:</h4>
  <ol style="padding-left: 1.5rem;">
    <li>❌ "Send me the file." (Rude!)</li>
    <li>😐 "Can you send me the file?" (Okay)</li>
    <li>🙂 "Could you send me the file?" (Better)</li>
    <li>😊 "Would you be able to send me the file?" (Polite)</li>
    <li>✨ "Would you mind sending me the file?" (Very polite)</li>
    <li>👑 "I would greatly appreciate it if you could send me the file." (Ultra formal)</li>
  </ol>
</div>

---

## 📚 Topic 5: Articles (A, An, The) - The Tiny Words That Confuse Everyone! 😵

### 🔵 The Rules Made Simple

<div style="display: grid; gap: 1rem; margin: 2rem 0;">
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; color: white;">
    <strong>🔵 A/AN = First mention, not specific</strong><br>
    "I saw <strong>a</strong> self-driving car today." (Which one? Any one.)<br>
    "She works at <strong>an</strong> AI company." (One of many.)
  </div>
  
  <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 12px; color: white;">
    <strong>🔴 THE = Specific, known, unique</strong><br>
    "I saw <strong>the</strong> self-driving car that was on the news." (Specific one!)<br>
    "<strong>The</strong> CEO of Apple announced new products." (Only one CEO.)
  </div>
  
  <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 1.5rem; border-radius: 12px; color: white;">
    <strong>⚪ NO ARTICLE = General concepts, plurals</strong><br>
    "<strong>Technology</strong> is changing the world." (General concept)<br>
    "<strong>Computers</strong> are everywhere." (General plural)
  </div>
</div>

### 🔬 Science Examples:

```
✅ CORRECT:
"THE sun is 93 million miles away." (Only one sun!)
"Water boils at 100°C." (General fact - no article)
"A new study found that..." (Introducing a study)
"THE study published in Nature showed..." (Specific study)

❌ COMMON MISTAKES:
"The science is important." ❌
"Science is important." ✅

"I study the artificial intelligence." ❌
"I study artificial intelligence." ✅
```

### 💼 Business Usage:

```
✅ Introducing things:
"We need A new strategy."
"I have AN idea for the project."

✅ Referring back:
"We need a new strategy. THE strategy should focus on AI."
"I have an idea. THE idea came to me last night."

✅ Unique things:
"THE CEO will announce THE quarterly results."
"We need to talk to THE head of marketing."

✅ General concepts (NO article):
"Innovation is key to success."
"Business is about relationships."
```

---

## 🎮 Interactive Grammar Quiz!

Test your skills with this interactive quiz! Click on your answer and get instant feedback:

<div class="grammar-game">
  <h4 style="margin-top: 0; color: #00d9ff; text-align: center;">🏆 Grammar Challenge</h4>
  
  <div class="progress-bar" style="margin-bottom: 1.5rem;">
    <div id="quizProgress" class="progress-fill" style="width: 0%;"></div>
  </div>
  
  <div id="quiz-container">
    <!-- Question 1 -->
    <div id="q1" class="quiz-question" style="margin-bottom: 1.5rem;">
      <p><strong>1. Tesla _____ electric vehicles since 2008.</strong></p>
      <div class="quiz-option" onclick="checkAnswer(1, 'a', this)">a) produces</div>
      <div class="quiz-option" onclick="checkAnswer(1, 'b', this)">b) has produced ✓</div>
      <div class="quiz-option" onclick="checkAnswer(1, 'c', this)">c) produced</div>
      <div id="feedback1" style="margin-top: 0.5rem;"></div>
    </div>
    
    <!-- Question 2 -->
    <div id="q2" class="quiz-question" style="margin-bottom: 1.5rem;">
      <p><strong>2. If I _____ more time, I _____ learn Python.</strong></p>
      <div class="quiz-option" onclick="checkAnswer(2, 'a', this)">a) have / will</div>
      <div class="quiz-option" onclick="checkAnswer(2, 'b', this)">b) had / would ✓</div>
      <div class="quiz-option" onclick="checkAnswer(2, 'c', this)">c) had had / would have</div>
      <div id="feedback2" style="margin-top: 0.5rem;"></div>
    </div>
    
    <!-- Question 3 -->
    <div id="q3" class="quiz-question" style="margin-bottom: 1.5rem;">
      <p><strong>3. The experiment _____ using advanced equipment.</strong></p>
      <div class="quiz-option" onclick="checkAnswer(3, 'a', this)">a) conducted</div>
      <div class="quiz-option" onclick="checkAnswer(3, 'b', this)">b) was conducted ✓</div>
      <div class="quiz-option" onclick="checkAnswer(3, 'c', this)">c) has conducting</div>
      <div id="feedback3" style="margin-top: 0.5rem;"></div>
    </div>
    
    <!-- Question 4 -->
    <div id="q4" class="quiz-question" style="margin-bottom: 1.5rem;">
      <p><strong>4. You _____ backup your data regularly. It's important!</strong></p>
      <div class="quiz-option" onclick="checkAnswer(4, 'a', this)">a) could</div>
      <div class="quiz-option" onclick="checkAnswer(4, 'b', this)">b) might</div>
      <div class="quiz-option" onclick="checkAnswer(4, 'c', this)">c) should ✓</div>
      <div id="feedback4" style="margin-top: 0.5rem;"></div>
    </div>
    
    <!-- Question 5 -->
    <div id="q5" class="quiz-question" style="margin-bottom: 1.5rem;">
      <p><strong>5. _____ artificial intelligence is transforming _____ healthcare industry.</strong></p>
      <div class="quiz-option" onclick="checkAnswer(5, 'a', this)">a) The / the</div>
      <div class="quiz-option" onclick="checkAnswer(5, 'b', this)">b) An / a</div>
      <div class="quiz-option" onclick="checkAnswer(5, 'c', this)">c) ∅ / the ✓</div>
      <div id="feedback5" style="margin-top: 0.5rem;"></div>
    </div>
  </div>
  
  <div id="quiz-result" style="display: none; text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; margin-top: 1rem;">
    <h3 style="margin: 0; font-size: 2rem;">🎉</h3>
    <p id="score-text" style="font-size: 1.5rem; margin: 1rem 0;"></p>
    <button onclick="resetQuiz()" style="padding: 0.8rem 2rem; background: white; color: #667eea; border: none; border-radius: 25px; font-weight: bold; cursor: pointer;">Try Again</button>
  </div>
</div>

<script>
const quizAnswers = {
  1: { correct: 'b', explanation: '"Since 2008" shows continuing action → Present Perfect!' },
  2: { correct: 'b', explanation: 'Type 2 conditional for unreal present situations!' },
  3: { correct: 'b', explanation: 'Passive voice for scientific/formal writing!' },
  4: { correct: 'c', explanation: '"Should" gives advice/recommendation (80% strength)!' },
  5: { correct: 'c', explanation: 'No article for general concepts + THE for specific industry!' }
};

let quizScore = 0;
let answeredQuestions = new Set();

function checkAnswer(qNum, answer, element) {
  if (answeredQuestions.has(qNum)) return; // Already answered
  answeredQuestions.add(qNum);
  
  const correct = quizAnswers[qNum].correct;
  const feedback = document.getElementById(`feedback${qNum}`);
  const options = element.parentElement.querySelectorAll('.quiz-option');
  
  // Disable all options for this question
  options.forEach(opt => opt.style.pointerEvents = 'none');
  
  if (answer === correct) {
    element.classList.add('correct');
    feedback.innerHTML = `<span style="color: #6bcb77;">✅ Correct! ${quizAnswers[qNum].explanation}</span>`;
    quizScore++;
  } else {
    element.classList.add('wrong');
    // Highlight correct answer
    options.forEach(opt => {
      if (opt.textContent.includes('✓')) {
        opt.classList.add('correct');
      }
    });
    feedback.innerHTML = `<span style="color: #ff6b6b;">❌ ${quizAnswers[qNum].explanation}</span>`;
  }
  
  // Update progress
  const progress = (answeredQuestions.size / 5) * 100;
  document.getElementById('quizProgress').style.width = progress + '%';
  
  // Check if all questions answered
  if (answeredQuestions.size === 5) {
    setTimeout(showResult, 500);
    updateProgress(100);
  } else {
    updateProgress(80 + answeredQuestions.size * 4);
  }
}

function showResult() {
  document.getElementById('quiz-result').style.display = 'block';
  const messages = {
    5: '🏆 PERFECT! You\'re a Grammar Master!',
    4: '🌟 Excellent! Almost perfect!',
    3: '👍 Good job! Keep practicing!',
    2: '📚 Not bad! Review the topics above!',
    1: '💪 Keep learning! You\'ll get there!',
    0: '🎯 Time to review! Try the interactive exercises above!'
  };
  document.getElementById('score-text').textContent = `${quizScore}/5 - ${messages[quizScore]}`;
  document.getElementById('quiz-result').classList.add('celebration');
}

function resetQuiz() {
  quizScore = 0;
  answeredQuestions.clear();
  document.getElementById('quizProgress').style.width = '0%';
  document.getElementById('quiz-result').style.display = 'none';
  
  // Reset all questions
  for (let i = 1; i <= 5; i++) {
    document.getElementById(`feedback${i}`).innerHTML = '';
    document.querySelectorAll(`#q${i} .quiz-option`).forEach(opt => {
      opt.classList.remove('correct', 'wrong');
      opt.style.pointerEvents = 'auto';
    });
  }
}
</script>

---

## 📱 Daily Usage Cheat Sheet

<div style="display: grid; gap: 1rem; margin: 2rem 0;">
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; color: white;">
    <strong>📧 Email Starters:</strong><br>
    "I <strong>would like to</strong> discuss..." (Polite)<br>
    "I <strong>am writing to</strong> inform you..." (Formal)<br>
    "<strong>Could you</strong> please send me..." (Requesting)
  </div>
  
  <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 12px; color: white;">
    <strong>🗣️ Meeting Phrases:</strong><br>
    "I <strong>would suggest</strong> that we..." (Recommending)<br>
    "<strong>Have you considered</strong>..." (Questioning politely)<br>
    "We <strong>should probably</strong>..." (Soft recommendation)
  </div>
  
  <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 12px; color: white;">
    <strong>📊 Presentation Phrases:</strong><br>
    "This chart <strong>shows</strong> that..." (Present simple for facts)<br>
    "Sales <strong>have increased</strong> by 20%." (Present perfect for results)<br>
    "If we <strong>continue</strong> this trend, we <strong>will achieve</strong>..." (Type 1 conditional)
  </div>
</div>

---

## 🧠 TL;DR - Quick Summary

| Topic | Key Rule | Example |
|-------|----------|---------|
| **Present Perfect** | Connected to NOW | "I have finished the report." |
| **Simple Past** | Specific time, finished | "I finished it yesterday." |
| **Type 2 Conditional** | Unreal present/future | "If I were you, I would..." |
| **Passive Voice** | Action > doer | "The study was conducted." |
| **Modal: Should** | Advice (80%) | "You should try this method." |
| **Modal: Must** | Obligation (100%) | "You must submit by Friday." |
| **THE** | Specific/unique | "The CEO announced..." |
| **A/AN** | First mention, one of many | "I met a new client." |

---

## 🎯 Next Steps for Your English Journey!

<div class="grammar-game">
  <h4 style="margin-top: 0; color: #00d9ff; text-align: center;">🌟 Your Achievement Summary</h4>
  
  <div class="progress-bar" style="margin: 1rem 0;">
    <div id="finalProgress" class="progress-fill" style="width: 0%;"></div>
  </div>
  
  <div id="achievement-text" style="text-align: center; font-size: 1.2rem; margin-bottom: 1rem;">
    Complete the interactive exercises above to fill your progress bar!
  </div>
  
  <div style="display: grid; gap: 0.5rem;">
    <div style="display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
      <span style="font-size: 1.5rem;">📰</span>
      <span><strong>Read tech news</strong> and notice the tenses used</span>
    </div>
    <div style="display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
      <span style="font-size: 1.5rem;">💬</span>
      <span><strong>Practice conditionals</strong> when discussing possibilities</span>
    </div>
    <div style="display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
      <span style="font-size: 1.5rem;">✍️</span>
      <span><strong>Write formal emails</strong> using passive voice</span>
    </div>
    <div style="display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
      <span style="font-size: 1.5rem;">🎧</span>
      <span><strong>Listen to podcasts</strong> and identify modal verbs</span>
    </div>
    <div style="display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
      <span style="font-size: 1.5rem;">📝</span>
      <span><strong>Keep a grammar journal</strong> with examples you find</span>
    </div>
  </div>
</div>

<div style="text-align: center; margin: 2rem 0; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; color: white;">
  <h3 style="margin: 0;">🚀 Remember</h3>
  <p style="font-size: 1.2rem; margin: 1rem 0;">The best way to learn grammar is through <strong>real exposure and practice</strong>, not just memorizing rules!</p>
  <p style="font-size: 2rem; margin: 0;">Happy learning! 🌟📚✨</p>
</div>

<!-- Global Progress Tracking Script -->
<script>
let currentProgress = 0;

function updateProgress(value) {
  if (value > currentProgress) {
    currentProgress = value;
    const progressBars = document.querySelectorAll('#mainProgress, #finalProgress');
    progressBars.forEach(bar => {
      if (bar) bar.style.width = currentProgress + '%';
    });
    
    // Update achievement text
    const achievementText = document.getElementById('achievement-text');
    if (achievementText) {
      if (currentProgress >= 100) {
        achievementText.innerHTML = '🏆 <strong>Congratulations!</strong> You\'ve completed all exercises!';
      } else if (currentProgress >= 60) {
        achievementText.innerHTML = '🌟 <strong>Great progress!</strong> Keep going!';
      } else if (currentProgress >= 30) {
        achievementText.innerHTML = '� <strong>Good start!</strong> Try more exercises!';
      }
    }
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  // Welcome animation
  setTimeout(() => {
    const mainProgress = document.getElementById('mainProgress');
    if (mainProgress) {
      mainProgress.style.width = '5%';
      currentProgress = 5;
    }
  }, 1000);
});
</script>
