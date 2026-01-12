---
layout: post
title: "📊 22 Essential Technical Analysis Topics for Modern Traders"
tags: [Trading, Technical Analysis, Finance, Investing, Khmer]
thumbnail: /images/technical_analysis_mastery.png
---

<style>
/* Theme-Aware Mastery Layout */
.mastery-wrapper {
  --m-accent: #006aff;
  --m-bull: #10b981;
  --m-bear: #ef4444;
  --m-khmer: #eab308;
  max-width: 1000px;
  margin: 0 auto;
  font-family: 'Source Sans 3', sans-serif;
  color: var(--text-primary);
}

/* Hero Section */
.m-hero {
  padding: 4rem 0;
  border-bottom: 2px solid var(--border-color);
  margin-bottom: 4rem;
}

.m-hero h1 {
  font-size: clamp(2.5rem, 8vw, 4.5rem) !important;
  font-weight: 800;
  letter-spacing: -0.04em;
  line-height: 0.9 !important;
  margin-bottom: 1.5rem !important;
  color: var(--text-primary);
}

.m-hero p {
  font-size: 1.4rem;
  color: var(--text-secondary);
  max-width: 600px;
  line-height: 1.4;
}

/* Category Navigation */
.m-nav-sticky {
  position: sticky;
  top: 80px;
  background: var(--bg-primary);
  z-index: 90;
  padding: 1rem 0;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 3rem;
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  scrollbar-width: none;
}
.m-nav-sticky::-webkit-scrollbar { display: none; }

.m-nav-btn {
  white-space: nowrap;
  padding: 0.5rem 1.25rem;
  border-radius: 99px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  border: 1px solid var(--border-color);
  transition: all 0.2s;
}

.m-nav-btn:hover, .m-nav-btn.active {
  background: var(--m-accent);
  color: white;
  border-color: var(--m-accent);
}

/* Section Styling */
.m-section {
  margin-bottom: 6rem;
  scroll-margin-top: 160px;
}

.m-section-title {
  font-size: 0.8rem !important;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--m-accent);
  margin-bottom: 2rem !important;
  display: flex;
  align-items: center;
  gap: 1rem;
}
.m-section-title::after {
  content: '';
  flex-grow: 1;
  height: 1px;
  background: var(--border-color);
}

/* Topic Layout: Side-by-Side */
.m-topic {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  padding: 3rem 0;
  border-bottom: 1px solid var(--border-color);
  align-items: center;
}

@media (max-width: 768px) {
  .m-topic {
    grid-template-columns: 1fr;
    gap: 2rem;
    padding: 2rem 0;
  }
}

.m-topic-content {
  display: flex;
  flex-direction: column;
}

.m-num {
  font-family: inherit;
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.m-title {
  font-size: 2rem !important;
  font-weight: 700;
  margin-bottom: 0.5rem !important;
  color: var(--text-primary);
}

.m-khmer {
  font-family: 'Noto Sans Khmer', sans-serif;
  color: var(--m-khmer);
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}

.m-desc {
  font-size: 1.1rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 2rem;
}

.m-example {
  background: var(--bg-secondary);
  padding: 1.5rem;
  border-radius: 12px;
  font-size: 0.95rem;
  border-left: 4px solid var(--m-accent);
}

.m-example strong { color: var(--text-primary); }

/* Visual Components */
.m-visual {
  background: var(--bg-secondary);
  border-radius: 24px;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

/* Specific SVG stylings */
.candle-bull { fill: var(--m-bull); }
.candle-bear { fill: var(--m-bear); }
.path-main { stroke: var(--text-primary); stroke-width: 3; fill: none; }
.path-accent { stroke: var(--m-accent); stroke-width: 4; fill: none; }

/* Custom Animations */
@keyframes draw {
  from { stroke-dashoffset: 200; }
  to { stroke-dashoffset: 0; }
}
.animate-draw {
  stroke-dasharray: 200;
  animation: draw 2s ease-out forwards;
}

/* Risk Card Special styling */
.risk-card {
  background: var(--m-bear);
  color: white;
  padding: 4rem;
  border-radius: 32px;
  text-align: center;
  margin-top: 4rem;
}
.risk-card h2 { color: white !important; font-size: 3rem !important; }
.risk-card p { color: rgba(255,255,255,0.8); font-size: 1.2rem; }

</style>

<div class="mastery-wrapper">

  <!-- Hero Section -->
  <header class="m-hero">
    <p class="m-num">CURRICULUM 2026</p>
    <h1>Technical Analysis Mastery</h1>
    <p>A comprehensive roadmap of 22 essential concepts for the modern algorithmic and discretionary trader.</p>
  </header>

  <!-- Sticky Navigation -->
  <nav class="m-nav-sticky">
    <a href="#foundations" class="m-nav-btn">Foundations</a>
    <a href="#geometry" class="m-nav-btn">Geometry</a>
    <a href="#liquidity" class="m-nav-btn">Liquidity</a>
    <a href="#structure" class="m-nav-btn">Structure</a>
    <a href="#indicators" class="m-nav-btn">Indicators</a>
    <a href="#advanced" class="m-nav-btn">Advanced</a>
    <a href="#risk" class="m-nav-btn">Risk</a>
  </nav>

  <!-- Section: Foundations -->
  <section id="foundations" class="m-section">
    <div class="m-section-title">01 / Foundation & Charting</div>
    
    <!-- Topic 1 -->
    <article class="m-topic" id="candlesticks">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 01</span>
        <h3 class="m-title">Candlestick Patterns</h3>
        <p class="m-khmer">🇰🇭 ទម្រង់ក្រាហ្វិកទៀន</p>
        <p class="m-desc">The visual language of the market. Candlesticks represent price action over time, showing the open, high, low, and close levels.</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> Look for "Engulfing" patterns at key support levels to find high-probability reversal entries.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <rect x="60" y="40" width="20" height="60" class="candle-bull" />
          <line x1="70" y1="20" x2="70" y2="120" stroke="var(--m-bull)" stroke-width="2" />
          <rect x="100" y="30" width="20" height="90" class="candle-bull" />
          <line x1="110" y1="10" x2="110" y2="140" stroke="var(--m-bull)" stroke-width="2" />
        </svg>
      </div>
    </article>

    <!-- Topic 2 -->
    <article class="m-topic" id="heikin-ashi">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 02</span>
        <h3 class="m-title">Heikin Ashi</h3>
        <p class="m-khmer">🇰🇭 ទៀនសម្រួលនិន្នាការ</p>
        <p class="m-desc">A averaging technique that filters out market noise, making it significantly easier to identify the core trend.</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> Flat bottom candles in an uptrend indicate strong momentum. Stay in the trade until a wick appears.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <rect x="40" y="80" width="15" height="20" fill="var(--m-bull)" opacity="0.4" />
          <rect x="60" y="70" width="15" height="30" fill="var(--m-bull)" opacity="0.6" />
          <rect x="80" y="60" width="15" height="40" fill="var(--m-bull)" opacity="0.8" />
          <rect x="100" y="50" width="15" height="50" fill="var(--m-bull)" />
        </svg>
      </div>
    </article>

    <!-- Topic 3 -->
    <article class="m-topic" id="renko">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 03</span>
        <h3 class="m-title">Renko Bricks</h3>
        <p class="m-khmer">🇰🇭 ក្រាហ្វិកឥដ្ឋ (គ្មានពេលវេលា)</p>
        <p class="m-desc">Charts based solely on price movement. Time is ignored, allowing traders to focus purely on structural shifts.</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> Use Renko to avoid being "chopped out" during sideways consolidation periods.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <rect x="50" y="90" width="25" height="25" fill="var(--m-bull)" rx="4" />
          <rect x="75" y="65" width="25" height="25" fill="var(--m-bull)" rx="4" />
          <rect x="100" y="40" width="25" height="25" fill="var(--m-bull)" rx="4" />
        </svg>
      </div>
    </article>
  </section>

  <!-- Section: Geometry -->
  <section id="geometry" class="m-section">
    <div class="m-section-title">02 / Market Geometry</div>

    <!-- Topic 4 -->
    <article class="m-topic" id="support-resistance">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 04</span>
        <h3 class="m-title">Support & Resistance</h3>
        <p class="m-khmer">🇰🇭 តំបន់គាំទ្រ និងតំបន់តស៊ូ</p>
        <p class="m-desc">Foundational horizontal levels where supply meets demand. These act as psychological barriers for price.</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> Look for "Role Reversal"—when old resistance becomes new support after a breakout.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <line x1="20" y1="50" x2="180" y2="50" stroke="var(--m-bear)" stroke-dasharray="5,5" />
          <path d="M20,120 L50,50 L80,100 L110,50 L140,80 L170,30" class="path-main" />
        </svg>
      </div>
    </article>

    <!-- Topic 5 -->
    <article class="m-topic" id="trend-lines">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 05</span>
        <h3 class="m-title">Trend Lines</h3>
        <p class="m-khmer">🇰🇭 ខ្សែបន្ទាត់និន្នាការ</p>
        <p class="m-desc">Diagonal paths connecting price extremes. They define the slope and speed of the current market cycle.</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> A trend line needs at least 3 touches to be considered valid by major market participants.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <line x1="20" y1="130" x2="180" y2="30" stroke="var(--m-accent)" stroke-width="2" />
          <circle cx="40" cy="118.5" r="5" fill="var(--m-accent)" opacity="0.4" />
          <circle cx="100" cy="84.5" r="5" fill="var(--m-accent)" opacity="0.4" />
          <circle cx="150" cy="56" r="5" fill="var(--m-accent)" opacity="0.4" />
        </svg>
      </div>
    </article>

    <!-- Topic 6 -->
    <article class="m-topic" id="channels">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 06</span>
        <h3 class="m-title">Price Channels</h3>
        <p class="m-khmer">🇰🇭 ប៉ុស្តិ៍តម្លៃ</p>
        <p class="m-desc">Parallel trend lines that encapsulate price action, creating a visual corridor of movement.</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> Trading the "mid-line" of a channel can offer high R:R setups in trending markets.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <line x1="20" y1="110" x2="180" y2="30" stroke="var(--m-accent)" />
          <line x1="40" y1="130" x2="200" y2="50" stroke="var(--m-accent)" />
          <path d="M30,120 L70,80 L110,100 L150,60 L190,80" class="path-main" opacity="0.5" />
        </svg>
      </div>
    </article>
  </section>

  <!-- Section: Liquidity -->
  <section id="liquidity" class="m-section">
    <div class="m-section-title">03 / Liquidity & Efficiency</div>

    <!-- Topic 7 -->
    <article class="m-topic" id="fvg">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 07</span>
        <h3 class="m-title">Fair Value Gap (FVG)</h3>
        <p class="m-khmer">🇰🇭 ចន្លោះតម្លៃយុត្តិធម៌</p>
        <p class="m-desc">Price inefficiencies where liquidity was unbalanced, creating a vacuum that price often returns to "fill".</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> FVGs represent institutional urgency. They are often used as high-confluence entry zones.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <rect x="50" y="20" width="10" height="30" class="candle-bear" />
          <rect x="65" y="10" width="10" height="100" class="candle-bear" />
          <rect x="80" y="80" width="10" height="30" class="candle-bear" />
          <rect x="65" y="50" width="25" height="30" fill="var(--m-accent)" opacity="0.2" />
        </svg>
      </div>
    </article>

    <!-- Topic 8 -->
    <article class="m-topic" id="breakouts">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 08</span>
        <h3 class="m-title">Breakouts & Fakeouts</h3>
        <p class="m-khmer">🇰🇭 ការទម្លុះចេញ និងការបោកបញ្ឆោត</p>
        <p class="m-desc">The moment price escapes a range. Learn to distinguish between true momentum and liquidity traps.</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> Always wait for a high-volume candle close above the range to confirm a valid breakout.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <line x1="20" y1="80" x2="180" y2="80" stroke="var(--border-color)" />
          <polyline points="20,100 50,85 80,95 110,75 130,40 160,20" class="path-accent" />
        </svg>
      </div>
    </article>
  </section>

  <!-- Section: Structure -->
  <section id="structure" class="m-section">
    <div class="m-section-title">04 / Market Structure (SMC)</div>

    <!-- Topic 9 -->
    <article class="m-topic" id="market-structure">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 09</span>
        <h3 class="m-title">Market Structure</h3>
        <p class="m-khmer">🇰🇭 រចនាសម្ព័ន្ធទីផ្សារ</p>
        <p class="m-desc">The core hierarchy of price: Higher Highs (HH) and Higher Lows (HL). If you don't know structure, you don't know the trend.</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> Only trade in the direction of the High Timeframe (HTF) structure for the best win rates.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <polyline points="20,130 50,80 80,110 110,60 140,90 170,40" class="path-main" />
          <text x="50" y="70" fill="var(--m-bull)" font-size="10">HH</text>
          <text x="80" y="125" fill="var(--m-bull)" font-size="10">HL</text>
        </svg>
      </div>
    </article>

    <!-- Topic 10 -->
    <article class="m-topic" id="bos">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 10</span>
        <h3 class="m-title">Break of Structure (BOS)</h3>
        <p class="m-khmer">🇰🇭 ការបំបែករចនាសម្ព័ន្ធ</p>
        <p class="m-desc">Confirmation that the trend is continuing. A BOS occurs when price closes beyond the previous structural high or low.</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> A BOS on the monthly chart signals a multi-year shift in market regime.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <polyline points="20,100 60,40 90,70 150,10" class="path-main" />
          <line x1="50" y1="40" x2="160" y2="40" stroke="var(--border-color)" stroke-dasharray="2" />
          <circle cx="115" cy="40" r="5" fill="var(--m-bull)" />
        </svg>
      </div>
    </article>

    <!-- Topic 11 -->
    <article class="m-topic" id="choch">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 11</span>
        <h3 class="m-title">Change of Character (CHoCH)</h3>
        <p class="m-khmer">🇰🇭 ការផ្លាស់ប្តូរលក្ខណៈ</p>
        <p class="m-desc">The first aggressive sign of a trend reversal. CHoCH indicates early shifts in order flow before a BOS happens.</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> Use CHoCH on lower timeframes for "Sniper" entries within HTF supply/demand zones.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <polyline points="20,40 60,100 90,70 130,130" class="path-main" />
          <line x1="80" y1="70" x2="160" y2="70" stroke="var(--m-bear)" stroke-dasharray="2" />
          <text x="110" y="65" fill="var(--m-bear)" font-size="10">CHoCH</text>
        </svg>
      </div>
    </article>
  </section>

  <!-- Section: Indicators -->
  <section id="indicators" class="m-section">
    <div class="m-section-title">05 / The Quant Toolbox</div>

    <article class="m-topic" id="volume">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 12</span>
        <h3 class="m-title">Volume Profile</h3>
        <p class="m-khmer">🇰🇭 កម្រងបរិមាណជួញដូរ</p>
        <p class="m-desc">Visualizing where most trading activity happened at specific price levels, rather than just over time.</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> The "Point of Control" (POC) is where the most volume was traded—it acts as a magnet for price.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <rect x="150" y="20" width="30" height="10" fill="var(--m-accent)" opacity="0.2" />
          <rect x="130" y="30" width="50" height="10" fill="var(--m-accent)" opacity="0.4" />
          <rect x="100" y="40" width="80" height="10" fill="var(--m-accent)" />
          <rect x="140" y="50" width="40" height="10" fill="var(--m-accent)" opacity="0.3" />
        </svg>
      </div>
    </article>

    <article class="m-topic" id="rsi">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 13</span>
        <h3 class="m-title">The RSI Divergence</h3>
        <p class="m-khmer">🇰🇭 សន្ទស្សន៍បង្គែតរំញ័រ</p>
        <p class="m-desc">Identifying when price and momentum are disagreeing. A bearish divergence often precedes a major drop.</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> A "Hidden Bullish Divergence" is one of the strongest signals for trend continuation.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <path d="M20,60 L80,30 L160,20" class="path-main" />
          <path d="M20,130 L80,110 L160,125" stroke="var(--m-accent)" stroke-width="2" fill="none" />
          <text x="20" y="145" fill="var(--m-accent)" font-size="8">MOMENTUM DECLINING</text>
        </svg>
      </div>
    </article>
  </section>

  <!-- Section: Advanced -->
  <section id="advanced" class="m-section">
    <div class="m-section-title">06 / Mathematical Models</div>

    <article class="m-topic" id="fibonacci">
      <div class="m-topic-content">
        <span class="m-num">TOPIC 16</span>
        <h3 class="m-title">The Golden Ratio (Fib)</h3>
        <p class="m-khmer">🇰🇭 មធ្យោបាយហ្វីបូណាក់ឈី</p>
        <p class="m-desc">Using 0.618 and 0.786 retracements to find the "Ote" (Optimal Trade Entry) in any market.</p>
        <div class="m-example">
          <strong>Pro Insight:</strong> Fibonacci works best when aligned with previous structure or high-volume zones.
        </div>
      </div>
      <div class="m-visual">
        <svg width="200" height="150" viewBox="0 0 200 150">
          <line x1="20" y1="130" x2="180" y2="30" stroke="var(--border-color)" />
          <line x1="20" y1="68" x2="180" y2="68" stroke="var(--m-accent)" stroke-width="2" />
          <text x="185" y="72" fill="var(--m-accent)" font-size="10">0.618</text>
        </svg>
      </div>
    </article>

    <div style="padding: 4rem 0; border-top: 1px solid var(--border-color); display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem;">
      <div>
        <h4 style="color: var(--m-accent)">17. Elliott Wave Theory</h4>
        <p style="font-size: 0.9rem; color: var(--text-secondary)">Understanding the 5-wave impulse and 3-wave correction of human psychology.</p>
      </div>
      <div>
        <h4 style="color: var(--m-accent)">18. Wyckoff Schematics</h4>
        <p style="font-size: 0.9rem; color: var(--text-secondary)">Tracking Accumulation and Distribution phases by "The Composite Man".</p>
      </div>
      <div>
        <h4 style="color: var(--m-accent)">19. Bollinger Bands</h4>
        <p style="font-size: 0.9rem; color: var(--text-secondary)">Statistical volatility bands that indicate reversion to the mean.</p>
      </div>
      <div>
        <h4 style="color: var(--m-accent)">20. Ichimoku Cloud</h4>
        <p style="font-size: 0.9rem; color: var(--text-secondary)">Performance at a glance: Trend, support, and momentum in one indicator.</p>
      </div>
      <div>
        <h4 style="color: var(--m-accent)">21. Order Blocks (OB)</h4>
        <p style="font-size: 0.9rem; color: var(--text-secondary)">Specific candles where institutions placed massive buy/sell orders.</p>
      </div>
      <div>
        <h4 style="color: var(--m-accent)">22. Time & Price (Killzones)</h4>
        <p style="font-size: 0.9rem; color: var(--text-secondary)">Trading only during London/NY sessions when liquidity is highest.</p>
      </div>
    </div>
  </section>

  <!-- Section: Risk -->
  <section id="risk" class="m-section">
    <div class="risk-card">
      <span class="m-num" style="color: rgba(255,255,255,0.6)">THE BOTTOM LINE</span>
      <h2>Risk Management</h2>
      <p>Technical analysis gives you the "Odds", but Risk Management gives you the "Career". Without a stop loss and proper position sizing, your analysis is worthless in the long run.</p>
      <div style="margin-top: 2rem; display: flex; justify-content: center; gap: 1rem;">
        <span style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 8px;">1% Max Risk</span>
        <span style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 8px;">2:1 Min R:R</span>
      </div>
    </div>
  </section>

  <!-- Final Footer -->
  <footer style="margin-top: 6rem; padding: 4rem 0; border-top: 1px solid var(--border-color); text-align: center;">
    <p style="color: var(--text-muted); font-style: italic;">"The goal of a successful trader is to make the best trades. Money is secondary." — Alexander Elder</p>
    <div style="margin-top: 2rem; font-weight: 800; font-size: 1.2rem; color: var(--m-accent);">KEEP TRADING. KEEP LEARNING. 🚀</div>
  </footer>

</div>

<script>
// Simple Navigation Highlight Script
document.addEventListener('DOMContentLoaded', () => {
  const sections = document.querySelectorAll('.m-section');
  const navBtns = document.querySelectorAll('.m-nav-btn');

  window.addEventListener('scroll', () => {
    let current = "";
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      if (pageYOffset >= sectionTop - 200) {
        current = section.getAttribute('id');
      }
    });

    navBtns.forEach(btn => {
      btn.classList.remove('active');
      if (btn.getAttribute('href').includes(current)) {
        btn.classList.add('active');
      }
    });
  });
});
</script>
