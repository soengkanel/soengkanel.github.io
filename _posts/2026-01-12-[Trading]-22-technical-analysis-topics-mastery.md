---
layout: post
title: "📊 22 Essential Technical Analysis Topics for Modern Traders"
tags: [Trading, Technical Analysis, Finance, Investing, Khmer]
thumbnail: /images/technical_analysis_mastery.png
---

<style>
:root {
  --trading-primary: #00d2ff;
  --trading-secondary: #3a7bd5;
  --trading-accent: #ffd700;
  --trading-bg: #0f172a;
  --trading-card: #1e293b;
  --bullish: #10b981;
  --bearish: #ef4444;
}

.trading-container {
  background: var(--trading-bg);
  color: #f8fafc;
  font-family: 'Source Sans 3', sans-serif;
  border-radius: 20px;
  padding: 2rem;
  line-height: 1.6;
}

.topic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.topic-card {
  background: var(--trading-card);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.topic-card:hover {
  transform: translateY(-5px);
  border-color: var(--trading-primary);
  box-shadow: 0 10px 30px -10px rgba(0, 210, 255, 0.3);
}

.topic-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, transparent 50%, rgba(0, 210, 255, 0.05) 50%);
  transition: all 0.3s ease;
}

.topic-card:hover::after {
  background: linear-gradient(135deg, transparent 50%, rgba(0, 210, 255, 0.1) 50%);
}

.topic-id {
  font-size: 0.8rem;
  font-weight: bold;
  color: var(--trading-primary);
  opacity: 0.8;
  margin-bottom: 0.5rem;
  display: block;
}

.topic-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.topic-desc {
  font-size: 0.95rem;
  color: #94a3b8;
  margin-bottom: 1.25rem;
}

.khmer-desc {
  font-family: 'Noto Sans Khmer', sans-serif;
  color: var(--trading-accent);
  font-size: 0.9rem;
  margin-bottom: 1rem;
  display: block;
}

.visual-box {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  position: relative;
  border: 1px dashed rgba(255,255,255,0.1);
}

/* Animations for Visuals */
.fibo-lines {
  width: 80%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.fibo-line {
  height: 1px;
  background: var(--trading-primary);
  opacity: 0.5;
  width: 100%;
}
.fibo-label {
  font-size: 8px;
  position: absolute;
  right: 5px;
  color: var(--trading-primary);
}

.breakout-path {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.candle-container {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}
.candle {
  width: 12px;
  border-radius: 2px;
  position: relative;
}
.candle.bull { background: var(--bullish); height: 40px; }
.candle.bear { background: var(--bearish); height: 60px; }
.candle::before, .candle::after {
  content: '';
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  background: inherit;
}
.candle::before { top: -10px; height: 10px; }
.candle::after { bottom: -10px; height: 10px; }

.section-header {
  border-left: 4px solid var(--trading-primary);
  padding-left: 1rem;
  margin: 3rem 0 1.5rem 0;
  background: linear-gradient(90deg, rgba(0, 210, 255, 0.1), transparent);
}

.badge {
  background: rgba(0, 210, 255, 0.1);
  color: var(--trading-primary);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  text-transform: uppercase;
  font-weight: bold;
}

.use-case {
  background: rgba(255, 215, 0, 0.05);
  border-left: 2px solid var(--trading-accent);
  padding: 1rem;
  margin-top: 1rem;
  border-radius: 0 8px 8px 0;
  font-size: 0.9rem;
}

.use-case-title {
  color: var(--trading-accent);
  font-weight: bold;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

@keyframes pulse {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s infinite;
}

</style>

<div class="trading-container">

# Technical Analysis Roadmap 📈
Mastering the markets requires a deep understanding of price action, patterns, and psychology. Below are 22 essential topics to master your trading journey.

---

<h2 class="section-header">1. Foundation & Charting</h2>

<div class="topic-grid">

  <!-- Topic 6: Candlesticks -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 01</span>
    <h3 class="topic-title">🕯️ Candlesticks</h3>
    <span class="khmer-desc">🇰🇭 បច្ចេកទេសទៀនជប៉ុន</span>
    <p class="topic-desc">The visual representation of price movement. Each candle tells a story of the battle between bulls and bears.</p>
    <div class="visual-box">
      <div class="candle-container">
        <div class="candle bear" style="height: 40px;"></div>
        <div class="candle bull" style="height: 70px;"></div>
        <div class="candle bull" style="height: 50px;"></div>
      </div>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Look for "Hammer" at support or "Shooting Star" at resistance to spot potential reversals.
    </div>
  </div>

  <!-- Topic 7: Heikin Ashi -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 02</span>
    <h3 class="topic-title">📉 Heikin Ashi</h3>
    <span class="khmer-desc">🇰🇭 ទៀនសម្រួលនិន្នាការ</span>
    <p class="topic-desc">A modified candlestick technique that filters out market noise, making trends easier to identify.</p>
    <div class="visual-box">
       <div class="candle-container" style="gap: 2px;">
         <div class="candle bull" style="height: 30px; width: 8px;"></div>
         <div class="candle bull" style="height: 35px; width: 8px;"></div>
         <div class="candle bull" style="height: 40px; width: 8px;"></div>
         <div class="candle bull" style="height: 45px; width: 8px;"></div>
       </div>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Stay in a trade as long as the Heikin Ashi candles remain the same color without lower/upper wicks.
    </div>
  </div>

  <!-- Topic 9: Renko -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 03</span>
    <h3 class="topic-title">🧱 Renko</h3>
    <span class="khmer-desc">🇰🇭 ក្រាហ្វិកឥដ្ឋ (គ្មានពេលវេលា)</span>
    <p class="topic-desc">Charts based solely on price movement rather than both price and time. Perfect for trend followers.</p>
    <div class="visual-box">
      <div style="display: flex; gap: 4px; align-items: flex-end;">
        <div style="width: 15px; height: 15px; background: var(--bullish); margin-bottom: 0;"></div>
        <div style="width: 15px; height: 15px; background: var(--bullish); margin-bottom: 15px;"></div>
        <div style="width: 15px; height: 15px; background: var(--bearish); margin-bottom: 15px;"></div>
      </div>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Used to remove "sideways" noise and focus only on significant price changes.
    </div>
  </div>

</div>

<h2 class="section-header">2. Market Geometry & Levels</h2>

<div class="topic-grid">

  <!-- Topic 11: Support and Resistance -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 04</span>
    <h3 class="topic-title">🧱 Support & Resistance</h3>
    <span class="khmer-desc">🇰🇭 តំបន់គាំទ្រ និងតំបន់តស៊ូ</span>
    <p class="topic-desc">Horizontal levels where price has historically struggled to break through.</p>
    <div class="visual-box">
      <div style="width:80%; height:1px; background:var(--trading-accent); position:absolute; top:20%;"></div>
      <div style="width:80%; height:1px; background:var(--trading-accent); position:absolute; bottom:20%;"></div>
      <svg width="100" height="60" viewBox="0 0 100 60">
        <path d="M10,40 L30,15 L50,45 L70,12 L90,48" fill="none" stroke="white" stroke-width="2"/>
      </svg>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Buy at Support (floor) and Sell at Resistance (ceiling).
    </div>
  </div>

  <!-- Topic 12: Dynamic Support and Resistance -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 05</span>
    <h3 class="topic-title">🌊 Dynamic S&R</h3>
    <span class="khmer-desc">🇰🇭 តំបន់គាំទ្រចល័ត</span>
    <p class="topic-desc">Using Moving Averages (EMA/SMA) as "invisible" support or resistance that moves with price.</p>
    <div class="visual-box">
      <svg width="140" height="80" viewBox="0 0 140 80">
        <path d="M10,70 Q40,40 70,50 T130,20" fill="none" stroke="var(--trading-primary)" stroke-width="2" class="animate-pulse"/>
        <path d="M5,75 Q35,45 65,55 T125,25" fill="none" stroke="white" stroke-width="1" stroke-dasharray="4"/>
      </svg>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      The 200 EMA often acts as a major dynamic floor in a bull market.
    </div>
  </div>

  <!-- Topic 13: Trend lines -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 06</span>
    <h3 class="topic-title">📈 Trend Lines</h3>
    <span class="khmer-desc">🇰🇭 ខ្សែបន្ទាត់និន្នាការ</span>
    <p class="topic-desc">Diagonal lines connecting troughs or peaks to define the direction of the trend.</p>
    <div class="visual-box">
       <svg width="100" height="60">
         <line x1="0" y1="60" x2="100" y2="0" stroke="var(--bullish)" stroke-width="2" />
         <circle cx="20" cy="48" r="3" fill="white" />
         <circle cx="50" cy="30" r="3" fill="white" />
         <circle cx="80" cy="12" r="3" fill="white" />
       </svg>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Wait for a 3rd touch on a trendline to confirm its validity before entering a trade.
    </div>
  </div>

</div>

<h2 class="section-header">3. Price Dynamics & Gaps</h2>

<div class="topic-grid">

  <!-- Topic 2: Breakouts -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 07</span>
    <h3 class="topic-title">🚀 Breakouts</h3>
    <span class="khmer-desc">🇰🇭 ការទម្លុះចេញ</span>
    <p class="topic-desc">When price moves significantly through a defined level of support or resistance.</p>
    <div class="visual-box">
      <svg width="120" height="60">
        <line x1="10" y1="30" x2="110" y2="30" stroke="var(--bearish)" stroke-width="1" stroke-dasharray="4"/>
        <path d="M10,50 L30,45 L50,55 L70,30 L90,10" fill="none" stroke="var(--bullish)" stroke-width="3" />
      </svg>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      A breakout with high volume confirms the move is likely to continue.
    </div>
  </div>

  <!-- Topic 5: Fair Value Gap -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 08</span>
    <h3 class="topic-title">🕳️ Fair Value Gap (FVG)</h3>
    <span class="khmer-desc">🇰🇭 ចន្លោះតម្លៃយុត្តិធម៌</span>
    <p class="topic-desc">Imbalance in price movement where only one side (buyers or sellers) was dominant, leaving a "gap".</p>
    <div class="visual-box">
      <div style="display: flex; gap: 5px; align-items: flex-end;">
        <div class="candle bear" style="height: 30px;"></div>
        <div class="candle bear" style="height: 80px; border: 1px solid var(--trading-primary);"></div>
        <div class="candle bear" style="height: 30px;"></div>
      </div>
      <div style="position: absolute; width: 40px; height: 10px; background: rgba(0,210,255,0.2); top: 50%; left: 50%; transform: translate(-50%, -50%);"></div>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Market often returns to fill these gaps before continuing the original move.
    </div>
  </div>

  <!-- Topic 3: Reversals -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 09</span>
    <h3 class="topic-title">🔄 Reversals</h3>
    <span class="khmer-desc">🇰🇭 ការបកត្រឡប់នៃនិន្នាការ</span>
    <p class="topic-desc">The moment a trend changes from Bullish to Bearish, or vice versa.</p>
    <div class="visual-box">
      <svg width="100" height="60">
        <path d="M0,50 L30,20 L50,10 L70,20 L100,60" fill="none" stroke="var(--bearish)" stroke-width="3" />
      </svg>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Identifying a "Double Top" is a classic sign of an upcoming bearish reversal.
    </div>
  </div>

</div>

<h2 class="section-header">4. Advanced Market Structure (SMC)</h2>

<div class="topic-grid">

  <!-- Topic 20: Market Structure -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 10</span>
    <h3 class="topic-title">🏛️ Market Structure</h3>
    <span class="khmer-desc">🇰🇭 រចនាសម្ព័ន្ធទីផ្សារ</span>
    <p class="topic-desc">Understanding the hierarchy of Highs and Lows (HH, HL, LH, LL).</p>
    <div class="visual-box">
      <div style="font-size: 10px; position: absolute; top: 10px; left: 20px;">HH</div>
      <div style="font-size: 10px; position: absolute; bottom: 10px; left: 40px;">HL</div>
       <svg width="120" height="80">
         <path d="M10,70 L30,20 L50,50 L80,10 L100,40" fill="none" stroke="white" stroke-width="2" />
       </svg>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      A break of a Higher Low (HL) is the first sign of structural weakness.
    </div>
  </div>

  <!-- Topic 21: BOS -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 11</span>
    <h3 class="topic-title">💥 BOS (Break of Structure)</h3>
    <span class="khmer-desc">🇰🇭 ការបំបែករចនាសម្ព័ន្ធ</span>
    <p class="topic-desc">When price continues the current trend by breaking the previous high (bullish) or low (bearish).</p>
    <div class="visual-box">
       <svg width="120" height="80">
         <path d="M10,50 L40,20 L60,40 L90,10" fill="none" stroke="var(--bullish)" stroke-width="2" />
         <line x1="30" y1="20" x2="110" y2="20" stroke="grey" stroke-dasharray="2" />
         <text x="75" y="15" fill="var(--bullish)" font-size="10">BOS</text>
       </svg>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Consistent BOS confirms you are in a strong, healthy trend.
    </div>
  </div>

  <!-- Topic 22: CHOCH -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 12</span>
    <h3 class="topic-title">⚡ CHOCH</h3>
    <span class="khmer-desc">🇰🇭 ការផ្លាស់ប្តូរលក្ខណៈ</span>
    <p class="topic-desc">Change of Character: The first signal that the market sentiment has shifted from bull to bear or vice versa.</p>
    <div class="visual-box">
       <svg width="120" height="80">
         <path d="M10,70 L30,40 L50,60 L80,30 L100,50 L110,80" fill="none" stroke="var(--bearish)" stroke-width="2" />
         <text x="80" y="70" fill="var(--bearish)" font-size="10">CHOCH</text>
       </svg>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      CHOCH often happens at major Supply or Demand zones before a big reversal.
    </div>
  </div>

  <!-- Topic 19: Supply & Demand -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 13</span>
    <h3 class="topic-title">⚖️ Supply & Demand</h3>
    <span class="khmer-desc">🇰🇭 ការផ្គត់ផ្គង់ និងតម្រូវការ</span>
    <p class="topic-desc">Zones where big institutions are likely buying (Demand) or selling (Supply).</p>
    <div class="visual-box">
      <div style="width: 100px; height: 30px; border: 1px solid var(--bearish); background: rgba(239, 68, 68, 0.1); position: absolute; top: 10px;">Supply</div>
      <div style="width: 100px; height: 30px; border: 1px solid var(--bullish); background: rgba(16, 185, 129, 0.1); position: absolute; bottom: 10px;">Demand</div>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Look for "Rally-Base-Rally" to identify strong institutional demand zones.
    </div>
  </div>

</div>

<h2 class="section-header">5. Indicators & Oscillators</h2>

<div class="topic-grid">

  <!-- Topic 18: Volume -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 14</span>
    <h3 class="topic-title">📊 Volume</h3>
    <span class="khmer-desc">🇰🇭 បរិមាណជួញដូរ</span>
    <p class="topic-desc">The number of shares or contracts traded. It validates the strength of price moves.</p>
    <div class="visual-box" style="align-items: flex-end; gap: 2px;">
      <div style="width: 6px; background: var(--bearish); height: 20px;"></div>
      <div style="width: 6px; background: var(--bullish); height: 50px;"></div>
      <div style="width: 6px; background: var(--bullish); height: 80px;"></div>
      <div style="width: 6px; background: var(--bearish); height: 30px;"></div>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Price rising on falling volume? Watch out—the trend might be exhausting.
    </div>
  </div>

  <!-- Topic 15: Momentum Indicators -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 15</span>
    <h3 class="topic-title">🚀 Momentum Indicators</h3>
    <span class="khmer-desc">🇰🇭 សន្ទស្សន៍សន្ទុះតម្លៃ</span>
    <p class="topic-desc">Indicators like MACD or ROC that measure the speed of price changes to confirm trend strength.</p>
    <div class="visual-box">
      <svg width="120" height="40">
        <path d="M0,35 L20,30 L40,25 L60,15 L80,10 L100,2" fill="none" stroke="var(--bullish)" stroke-width="3" />
      </svg>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      When MACD crosses above the signal line, it shows increasing bullish momentum.
    </div>
  </div>

  <!-- Topic 16: Oscillators -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 16</span>
    <h3 class="topic-title">⏲️ Oscillators (RSI/Stoch)</h3>
    <span class="khmer-desc">🇰🇭 សន្ទស្សន៍រំញ័រ</span>
    <p class="topic-desc">Tools like RSI or Stochastic that track overbought (>70) and oversold (<30) conditions.</p>
    <div class="visual-box">
      <svg width="120" height="60">
        <rect x="0" y="15" width="120" height="30" fill="rgba(255,255,255,0.05)" />
        <path d="M0,45 Q20,10 40,30 T80,50 T120,5" fill="none" stroke="var(--trading-primary)" stroke-width="2" />
      </svg>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      RSI above 70 indicates the market might be due for a correction.
    </div>
  </div>

  <!-- Topic 17: Divergence -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 17</span>
    <h3 class="topic-title">🔀 Divergence</h3>
    <span class="khmer-desc">🇰🇭 ការដើរចេញពីគ្នា</span>
    <p class="topic-desc">When price and an indicator move in opposite directions. A powerful reversal signal.</p>
    <div class="visual-box">
       <div style="position: absolute; top: 30px;">Price: HH 📈</div>
       <div style="position: absolute; bottom: 10px; color: var(--bearish);">RSI: LH 📉</div>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Bearish Divergence: Price makes a new high, but RSI makes a lower high.
    </div>
  </div>

</div>

<h2 class="section-header">6. Mathematical & Harmonic Patterns</h2>

<div class="topic-grid">

  <!-- Topic 18: Fibonacci Retracements -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 18</span>
    <h3 class="topic-title">🔢 Fibonacci Retracements</h3>
    <span class="khmer-desc">🇰🇭 កម្រិតហ្វីបូណាក់ឈី</span>
    <p class="topic-desc">Mathematical ratios (0.618, 0.5) used to predict where price might pull back.</p>
    <div class="visual-box">
      <div class="fibo-lines">
        <div class="fibo-line"><span class="fibo-label">0.0%</span></div>
        <div class="fibo-line" style="background: var(--trading-accent); opacity: 1;"><span class="fibo-label">61.8%</span></div>
        <div class="fibo-line"><span class="fibo-label">100.0%</span></div>
      </div>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      The "Golden Pocket" (61.8%) is where professional traders look for entries.
    </div>
  </div>

  <!-- Topic 19: Elliott Wave -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 19</span>
    <h3 class="topic-title">🌊 Elliott Wave</h3>
    <span class="khmer-desc">🇰🇭 ទ្រឹស្តីរលក Elliott</span>
    <p class="topic-desc">Theoretical framework where markets move in repetitive cycles of 5 impulse and 3 corrective waves.</p>
    <div class="visual-box">
      <svg width="120" height="80">
        <path d="M10,70 L30,40 L45,60 L75,20 L90,40 L115,5" fill="none" stroke="var(--trading-primary)" stroke-width="2" />
      </svg>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Wave 3 is usually the longest and strongest part of a trend.
    </div>
  </div>

  <!-- Topic 20: Harmonic Patterns -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 20</span>
    <h3 class="topic-title">🦋 Harmonic Patterns</h3>
    <span class="khmer-desc">🇰🇭 បំណិនរាងធរណីមាត្រ</span>
    <p class="topic-desc">Complex geometric patterns that use Fib ratios to predict turns.</p>
    <div class="visual-box">
      <svg width="100" height="60" viewBox="0 0 100 60">
        <path d="M10,50 L30,10 L50,40 L70,10 L90,50 Z" fill="rgba(0,210,255,0.1)" stroke="var(--trading-primary)" stroke-width="2" />
      </svg>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Patterns like "Bat" or "Gartley" indicate high-probability reversal points.
    </div>
  </div>

  <!-- Topic 21: Gann Angles -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 21</span>
    <h3 class="topic-title">📐 Gann Angles</h3>
    <span class="khmer-desc">🇰🇭 មុំ Gann</span>
    <p class="topic-desc">Relationship between time and price. The 45-degree angle (1x1) is key.</p>
    <div class="visual-box">
      <svg width="100" height="80">
        <line x1="10" y1="70" x2="90" y2="10" stroke="var(--trading-accent)" stroke-width="1" />
        <line x1="10" y1="70" x2="90" y2="30" stroke="grey" stroke-width="0.5" />
      </svg>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      If price stays above the 1x1 angle, it is extremely bullish.
    </div>
  </div>

</div>

<h2 class="section-header">7. Psychology & Final Steps</h2>

<div class="topic-grid">

  <!-- Topic 22: Moon Phases -->
  <div class="topic-card">
    <span class="topic-id">TOPIC 22</span>
    <h3 class="topic-title">🌑 Moon Phases</h3>
    <span class="khmer-desc">🇰🇭 វដ្តព្រះច័ន្ទ</span>
    <p class="topic-desc">An unconventional theory that lunar cycles affect volatility and psychology.</p>
    <div class="visual-box">
      <div style="width: 40px; height: 40px; border-radius: 50%; background: #fff; box-shadow: 0 0 20px #fff;"></div>
    </div>
    <div class="use-case">
      <div class="use-case-title">🔍 Example:</div>
      Some traders use full/new moons as secondary confirmation for trend turns.
    </div>
  </div>

  <!-- Final Wrap Up -->
  <div class="topic-card" style="background: linear-gradient(135deg, #1e293b, #0f172a); border: 2px solid var(--trading-primary);">
    <span class="topic-id">CRITICAL</span>
    <h3 class="topic-title">🎯 Risk Management</h3>
    <span class="khmer-desc">🇰🇭 ការគ្រប់គ្រងហានិភ័យ</span>
    <p class="topic-desc">The most important "topic" of all. Without risk management, TA is just gambling.</p>
    <div class="visual-box">
       <div style="font-size: 2rem;">🛡️</div>
    </div>
    <div class="use-case">
      <div class="use-case-title">💡 Pro Tip:</div>
      Never risk more than 1% of your account on a single trade, no matter how good the TA looks.
    </div>
  </div>

</div>

<div style="text-align: center; padding: 2rem; background: rgba(0, 210, 255, 0.05); border-radius: 16px; margin-top: 3rem;">
  <h3>🚀 Level Up Your Trading</h3>
  <p>Technical analysis is a language. The more you practice, the more fluent you become. Start by mastering one category at a time.</p>
  <p style="color: var(--trading-accent);">សូមសំណាងល្អក្នុងការជួញដូរ! (Good luck with your trading!)</p>
</div>

</div>
