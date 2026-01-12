---
theme: seriph
title: AI + Human Collaboration
class: text-center
highlighter: shiki
transition: slide-left
mdc: true
css: unocss
fonts:
  sans: 'Inter'
  serif: 'Inter'
  mono: 'Inter'
---

<style>
@keyframes rocket-launch {
  /* Floating Cycle (0-70%) */
  0%   { transform: translate(0, 0) rotate(0deg); opacity: 1; }
  20%  { transform: translate(2px, -4px) rotate(2deg); opacity: 1; }
  40%  { transform: translate(-2px, -8px) rotate(-2deg); opacity: 1; }
  60%  { transform: translate(1px, -5px) rotate(1deg); opacity: 1; }
  75%  { transform: translate(0, -2px) scale(1.1); opacity: 1; }
  
  /* Slower Fly Out (75-100%) */
  100% { transform: translate(300px, -800px) scale(0); opacity: 0; }
}

@keyframes rocket-gas {
  0%, 60% { transform: scale(0); opacity: 0; }
  70% { transform: scale(1.5) translateY(5px); opacity: 0.8; filter: blur(2px); }
  85% { transform: scale(2.5) translateY(15px); opacity: 0; filter: blur(8px); }
  100% { transform: scale(3) translateY(20px); opacity: 0; }
}

.animate-rocket-fly {
  animation: rocket-launch 5s ease-in-out infinite;
  display: inline-block;
  position: relative;
}

/* Engine Gas / Smoke Effect */
.animate-rocket-fly::after {
  content: '';
  position: absolute;
  top: 80%;
  left: 50%;
  width: 12px;
  height: 12px;
  background: radial-gradient(circle, #fff 0%, #00ffff 50%, transparent 70%);
  border-radius: 50%;
  transform: translateX(-50%);
  animation: rocket-gas 5s ease-in-out infinite;
  z-index: -1;
}
</style>

<img src="/futuristic_cambodia_business_park.png" class="absolute top-0 left-0 w-full h-full object-cover z-0" />
<div class="absolute top-0 left-0 w-full h-full bg-black/60 z-1"></div>

<div class="relative z-10 flex flex-col justify-center h-full items-center text-white">
  <div class="text-6xl font-extrabold tracking-widest mb-4 bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
    AI + HUMAN
  </div>
  <div class="text-2xl font-light tracking-wide opacity-90">
    COLLABORATIVE WORKFLOW
  </div>
  <div class="mt-12 text-sm opacity-80 border border-white/30 px-4 py-2 rounded-full uppercase">
    Next Generation Technology Co., Ltd.
  </div>
</div>

---
layout: default
transition: fade-out
class: bg-gray-900 text-white
background: ""
---

# <span class="text-cyan-500">The Lifecycle</span> Protocol

<div class="grid grid-cols-12 gap-4 h-[85%] mt-4">

<!-- Central Timeline Line -->
<div class="col-span-12 flex items-center justify-between relative px-2">
  
  <!-- The Line -->
  <div class="absolute left-10 right-10 top-1/2 h-1 bg-gray-700/50 -z-10 rounded-full"></div>
  <div class="absolute left-10 right-10 top-1/2 h-1 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 z-0 shadow-[0_0_15px_rgba(168,85,247,0.5)]"
       v-motion
       :initial="{ scaleX: 0, originX: 0 }"
       :enter="{ scaleX: 1, transition: { duration: 1500 } }">
  </div>

  <!-- Pipeline Flow Labels -->
  <div v-click="1" class="absolute top-[42%] left-[13%] text-[9px] text-cyan-400 tracking-widest uppercase opacity-70">Analysis</div>
  <div v-click="2" class="absolute top-[42%] left-[27%] text-[9px] text-purple-400 tracking-widest uppercase opacity-70">Spec</div>
  <div v-click="4" class="absolute top-[42%] left-[41%] text-[9px] text-yellow-400 tracking-widest uppercase opacity-70">Design</div>
  <div v-click="5" class="absolute top-[42%] left-[55%] text-[9px] text-green-400 tracking-widest uppercase opacity-70">Dev</div>
  <div v-click="6" class="absolute top-[42%] left-[70%] text-[9px] text-blue-400 tracking-widest uppercase opacity-70">Test</div>
  <div v-click="7" class="absolute top-[42%] left-[84%] text-[9px] text-pink-400 tracking-widest uppercase opacity-70">Deploy</div>

  <!-- Node 1: Idea -->
  <div v-click class="relative group cursor-pointer">
    <div class="w-14 h-14 bg-gray-900 border-2 border-cyan-500 rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(6,182,212,0.6)] z-10 transition-all duration-300 group-hover:scale-125 group-hover:shadow-[0_0_40px_rgba(6,182,212,0.9)]">
      <div class="i-carbon:idea text-2xl text-white"></div>
    </div>
    <div class="absolute top-16 left-1/2 -translate-x-1/2 w-32 text-center text-xs font-bold text-gray-300 opacity-80 group-hover:opacity-100 transition-opacity">
      Idea
    </div>
  </div>

  <!-- Node 2: BRS -->
  <div v-click="2" class="relative group cursor-pointer">
    <!-- Highlight Circle -->
    <div class="absolute -inset-3 border-2 border-dashed border-cyan-400 rounded-full animate-spin pointer-events-none shadow-[0_0_15px_rgba(34,211,238,0.6)]" style="animation-duration: 10s;"></div>
    <div class="w-10 h-10 bg-gray-800 border border-purple-500 rounded-full flex items-center justify-center z-10 transition-all duration-300 group-hover:scale-125 group-hover:bg-purple-900">
      <div class="i-carbon:document-requirements text-xl text-purple-300"></div>
    </div>
    <div class="absolute -top-10 left-1/2 -translate-x-1/2 w-32 text-center text-xs text-gray-400 opacity-80 group-hover:opacity-100 transition-opacity">
      BRS <span class="text-[10px] text-cyan-500 font-bold">(WHY)</span>
    </div>
  </div>

  <!-- Node 3: PRD -->
  <div v-click="3" class="relative group cursor-pointer">
     <div class="w-10 h-10 bg-gray-800 border border-purple-500 rounded-full flex items-center justify-center z-10 transition-all duration-300 group-hover:scale-125 group-hover:bg-purple-900">
      <div class="i-carbon:product text-xl text-purple-300"></div>
    </div>
    <div class="absolute top-16 left-1/2 -translate-x-1/2 w-32 text-center text-xs text-gray-400 opacity-80 group-hover:opacity-100 transition-opacity">
      PRD <span class="text-[10px] text-purple-500 font-bold">(WHAT)</span>
    </div>
  </div>

  <!-- Node 4: FRS (Functional Spec) -->
  <div v-click="4" class="relative group cursor-pointer">
     <!-- Highlight Circle -->
    <div class="absolute -inset-3 border-2 border-dashed border-cyan-400 rounded-full animate-spin pointer-events-none shadow-[0_0_15px_rgba(34,211,238,0.6)]" style="animation-duration: 10s;"></div>
     <div class="w-10 h-10 bg-gray-800 border border-purple-500 rounded-full flex items-center justify-center z-10 transition-all duration-300 group-hover:scale-125 group-hover:bg-purple-900">
      <div class="i-carbon:list-checked text-xl text-purple-300"></div>
    </div>
    <div class="absolute -top-10 left-1/2 -translate-x-1/2 w-32 text-center text-xs text-gray-400 opacity-80 group-hover:opacity-100 transition-opacity">
      FRS <span class="text-[10px] text-orange-500 font-bold">(HOW)</span>
    </div>
  </div>

  <!-- Node 5: Tech Design -->
  <div v-click="5" class="relative group cursor-pointer">
     <div class="w-10 h-10 bg-gray-800 border border-yellow-500 rounded-full flex items-center justify-center z-10 transition-all duration-300 group-hover:scale-125 group-hover:bg-yellow-900">
      <div class="i-carbon:model-alt text-xl text-yellow-300"></div>
    </div>
    <div class="absolute top-16 left-1/2 -translate-x-1/2 w-20 text-center text-xs text-gray-400 opacity-80 group-hover:opacity-100 transition-opacity">
      Tech Design
    </div>
  </div>

  <!-- Node 6: Implementation -->
  <div v-click="6" class="relative group cursor-pointer">
    <div class="w-14 h-14 bg-gray-900 border-2 border-green-500 rounded-xl rotate-45 flex items-center justify-center shadow-[0_0_20px_rgba(34,197,94,0.6)] z-10 transition-all duration-300 group-hover:scale-110 group-hover:rotate-0 group-hover:shadow-[0_0_40px_rgba(34,197,94,0.8)]">
      <div class="-rotate-45 group-hover:rotate-0 transition-transform duration-300 i-carbon:code text-2xl text-white"></div>
    </div>
    <div class="absolute top-16 left-1/2 -translate-x-1/2 w-32 text-center text-xs font-bold text-green-400 opacity-80 group-hover:opacity-100 transition-opacity">
      Implementation
    </div>
  </div>

  <!-- Node 7: QA -->
  <div v-click="7" class="relative group cursor-pointer">
     <div class="w-10 h-10 bg-gray-800 border border-blue-500 rounded-full flex items-center justify-center z-10 transition-all duration-300 group-hover:scale-125 group-hover:bg-blue-900">
      <div class="i-carbon:test-tool text-xl text-blue-300"></div>
    </div>
    <div class="absolute -top-10 left-1/2 -translate-x-1/2 w-32 text-center text-xs text-gray-400 opacity-80 group-hover:opacity-100 transition-opacity">
      QA
    </div>
  </div>

  <!-- Node 8: Release -->
  <div v-click="8" class="relative group cursor-pointer">
    <div class="w-14 h-14 bg-gradient-to-br from-pink-500 to-orange-500 rounded-full flex items-center justify-center shadow-[0_0_30px_rgba(236,72,153,0.8)] z-10 transition-all duration-300 group-hover:scale-125 group-hover:shadow-[0_0_60px_rgba(236,72,153,1)] overflow-visible">
      <div class="i-carbon:rocket text-2xl text-white animate-rocket-fly"></div>
    </div>
    <div class="absolute top-16 left-1/2 -translate-x-1/2 w-32 text-center text-xs font-bold text-pink-400 opacity-80 group-hover:opacity-100 transition-opacity">
      RELEASE
    </div>
  </div>

</div>

<!-- Loops descriptions -->
<div class="col-span-12 grid grid-cols-3 gap-4 text-center mt-10">
  
  <div v-click="3" class="p-4 bg-white/5 border border-white/10 rounded-xl backdrop-blur-sm hover:bg-white/10 transition-colors duration-300 relative group">
    <div class="text-purple-400 font-bold mb-2">Scope & Logic Context</div>
    <p class="text-[10px] text-gray-400 mb-2">Human defines / AI Refines <br> (BRS ⟲ PRD ⟲ FRS)</p>
    <div class="text-[10px] text-purple-300 border-t border-white/10 pt-2 font-semibold">
       FRS (HOW) is the anchor for AI Coding
    </div>
  </div>
  
  <div v-click="5" class="p-4 bg-white/5 border border-white/10 rounded-xl backdrop-blur-sm hover:bg-white/10 transition-colors duration-300">
    <div class="text-green-400 font-bold mb-2">Technical Constraints</div>
    <p class="text-[10px] text-gray-400">Implementation ⟲ Tech Design</p>
  </div>
  
  <div v-click="7" class="p-4 bg-white/5 border border-white/10 rounded-xl backdrop-blur-sm hover:bg-white/10 transition-colors duration-300">
    <div class="text-blue-400 font-bold mb-2">Defects / Gaps</div>
    <p class="text-[10px] text-gray-400">QA ⟲ Implementation</p>
  </div>

</div>

</div>

---
layout: default
transition: slide-up
class: bg-gray-900 text-white
background: ""
---

# <span class="text-orange-500">Phase 1:</span> Planning & Specs

<div class="grid grid-cols-2 gap-10 h-full items-center p-8">

<!-- AI CARD -->
<div 
  v-motion-slide-visible-left 
  class="h-[80%] relative bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-2xl p-6 shadow-2xl overflow-hidden group hover:border-cyan-500/50 transition-all duration-500"
>
  <div class="absolute -right-10 -top-10 w-32 h-32 bg-cyan-500/20 rounded-full blur-3xl group-hover:bg-cyan-500/30 transition-all"></div>
  
  <div class="flex items-center gap-4 mb-8">
    <div class="p-3 bg-cyan-900/30 rounded-lg text-cyan-400">
      <div class="i-carbon:machine-learning-model text-3xl"></div>
    </div>
    <div>
      <h2 class="text-2xl font-bold text-white">AI Agent</h2>
      <p class="text-xs text-cyan-400 uppercase tracking-widest">Execution Engine</p>
    </div>
  </div>

  <ul class="space-y-6">
    <li class="flex items-start gap-4">
      <div class="mt-1 i-carbon:document-import text-cyan-400"></div>
      <div>
        <span class="block text-gray-200 font-bold">Drafting Documents</span>
        <span class="text-sm text-gray-500">Generating BRS (Why), PRD (What), and FRS (How).</span>
      </div>
    </li>
    <li class="flex items-start gap-4">
      <div class="mt-1 i-carbon:list-checked text-cyan-400"></div>
      <div>
        <span class="block text-gray-200 font-bold">Functional Architecture</span>
        <span class="text-sm text-gray-500">Fleshing out the "How" (Functionally).</span>
      </div>
    </li>
    <li class="flex items-start gap-4">
      <div class="mt-1 i-carbon:flow-stream text-cyan-400"></div>
      <div>
        <span class="block text-gray-200 font-bold">Flow Expansion</span>
        <span class="text-sm text-gray-500">Creating diagrams and logic flows.</span>
      </div>
    </li>
  </ul>
</div>

<!-- HUMAN CARD -->
<div 
  v-motion-slide-visible-right
  class="h-[80%] relative bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-2xl p-6 shadow-2xl overflow-hidden group hover:border-orange-500/50 transition-all duration-500"
>
  <div class="absolute -left-10 -bottom-10 w-32 h-32 bg-orange-500/20 rounded-full blur-3xl group-hover:bg-orange-500/30 transition-all"></div>

  <div class="flex items-center gap-4 mb-8">
    <div class="p-3 bg-orange-900/30 rounded-lg text-orange-400">
      <div class="i-carbon:user-speaker text-3xl"></div>
    </div>
    <div>
      <h2 class="text-2xl font-bold text-white">Human Lead</h2>
      <p class="text-xs text-orange-400 uppercase tracking-widest">Vision & Validation</p>
    </div>
  </div>

  <ul class="space-y-6">
    <li class="flex items-start gap-4">
      <div class="mt-1 i-carbon:events text-orange-400"></div>
      <div>
        <span class="block text-gray-200 font-bold">The "Why" (BRS)</span>
        <span class="text-sm text-gray-500">Setting business goals and constraints.</span>
      </div>
    </li>
    <li class="flex items-start gap-4">
      <div class="mt-1 i-carbon:stamp text-orange-400"></div>
      <div>
        <span class="block text-gray-200 font-bold">The "What" & "How"</span>
        <span class="text-sm text-gray-500">Auditing PRD (What) and FRS (How) for alignment.</span>
      </div>
    </li>
  </ul>
</div>

</div>

---
layout: default
transition: slide-up
---

# <span class="text-green-500">Phase 2:</span> Build & Automate

<div class="grid grid-cols-2 gap-10 h-full items-center p-8">

<!-- AI CARD -->
<div 
  v-motion-slide-visible-left 
  class="h-[80%] relative bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-2xl p-6 shadow-2xl overflow-hidden group hover:border-purple-500/50 transition-all duration-500"
>
  <div class="absolute -right-10 -top-10 w-32 h-32 bg-purple-500/20 rounded-full blur-3xl group-hover:bg-purple-500/30 transition-all"></div>
  
  <div class="flex items-center gap-4 mb-8">
    <div class="p-3 bg-purple-900/30 rounded-lg text-purple-400">
      <div class="i-carbon:bot text-3xl"></div>
    </div>
    <div>
      <h2 class="text-2xl font-bold text-white">AI Coder</h2>
      <p class="text-xs text-purple-400 uppercase tracking-widest">High-Speed Implementation</p>
    </div>
  </div>

  <ul class="space-y-6">
    <li class="flex items-start gap-4">
      <div class="mt-1 i-carbon:code text-purple-400"></div>
      <div>
        <span class="block text-gray-200 font-bold">Code Generation</span>
        <span class="text-sm text-gray-500">Boilerplate to complex logic implementation.</span>
      </div>
    </li>
    <li class="flex items-start gap-4">
      <div class="mt-1 i-carbon:cogs text-purple-400"></div>
      <div>
        <span class="block text-gray-200 font-bold">Automation</span>
        <span class="text-sm text-gray-500">Writing unit tests, pipelines, and fixes.</span>
      </div>
    </li>
  </ul>
</div>

<!-- HUMAN CARD -->
<div 
  v-motion-slide-visible-right
  class="h-[80%] relative bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-2xl p-6 shadow-2xl overflow-hidden group hover:border-green-500/50 transition-all duration-500"
>
  <div class="absolute -left-10 -bottom-10 w-32 h-32 bg-green-500/20 rounded-full blur-3xl group-hover:bg-green-500/30 transition-all"></div>

  <div class="flex items-center gap-4 mb-8">
    <div class="p-3 bg-green-900/30 rounded-lg text-green-400">
      <div class="i-carbon:microscope text-3xl"></div>
    </div>
    <div>
      <h2 class="text-2xl font-bold text-white">Human Engineer</h2>
      <p class="text-xs text-green-400 uppercase tracking-widest">Architect & Auditor</p>
    </div>
  </div>

  <ul class="space-y-6">
    <li class="flex items-start gap-4">
      <div class="mt-1 i-carbon:construct text-green-400"></div>
      <div>
        <span class="block text-gray-200 font-bold">Architecture</span>
        <span class="text-sm text-gray-500">System design, security, and scalability.</span>
      </div>
    </li>
    <li class="flex items-start gap-4">
      <div class="mt-1 i-carbon:rule text-green-400"></div>
      <div>
        <span class="block text-gray-200 font-bold">Audit & QA</span>
        <span class="text-sm text-gray-500">Code review, edge-case testing, and approval.</span>
      </div>
    </li>
  </ul>
</div>

</div>

---
layout: default
transition: slide-up
class: bg-gray-900 text-white
---

# <span class="text-pink-500">The Core</span> Workflow

<div class="flex flex-col justify-center items-center h-[85%] w-full gap-8">

<!-- The Flow -->
<div class="w-full flex items-center justify-between px-2">
  <!-- Problem -->
  <div class="flex flex-col items-center gap-3">
    <div class="w-14 h-14 rounded-full bg-gray-800 border-2 border-red-500 flex items-center justify-center shadow-[0_0_20px_rgba(239,68,68,0.5)]">
      <div class="i-carbon:warning text-2xl text-red-500"></div>
    </div>
    <div class="text-xs font-bold text-gray-300 uppercase tracking-widest text-center">Problem</div>
  </div>
  
  <div class="i-carbon:arrow-right text-xl text-gray-600"></div>

  <!-- Human Validation 1 -->
  <div class="flex flex-col items-center gap-3 relative">
    <!-- Highlight Ring -->
    <div class="absolute -inset-2 border-2 border-dashed border-orange-400 rounded-full animate-spin pointer-events-none shadow-[0_0_15px_rgba(249,115,22,0.6)]" style="animation-duration: 10s;"></div>
    <div class="w-14 h-14 rounded-full bg-gray-800 border-2 border-orange-500 flex items-center justify-center shadow-[0_0_20px_rgba(249,115,22,0.5)] z-10">
      <div class="i-carbon:user-checkmark text-2xl text-orange-500"></div>
    </div>
    <div class="text-xs font-bold text-orange-400 uppercase tracking-widest text-center">Human<br>Audit</div>
  </div>

  <div class="i-carbon:arrow-right text-xl text-gray-600"></div>

  <!-- PRD -->
  <div class="flex flex-col items-center gap-3">
    <div class="w-14 h-14 rounded-full bg-gray-800 border-2 border-purple-500 flex items-center justify-center shadow-[0_0_20px_rgba(168,85,247,0.5)]">
      <div class="i-carbon:document text-2xl text-purple-500"></div>
    </div>
    <div class="text-xs font-bold text-gray-300 uppercase tracking-widest text-center">PRD</div>
  </div>

  <!-- FRS -->
  <div class="flex flex-col items-center gap-3 relative">
    <!-- Highlight Ring -->
    <div class="absolute -inset-2 border-2 border-dashed border-cyan-400 rounded-full animate-spin pointer-events-none shadow-[0_0_15px_rgba(34,211,238,0.6)]" style="animation-duration: 10s;"></div>
    <div class="w-14 h-14 rounded-full bg-gray-800 border-2 border-purple-500 flex items-center justify-center shadow-[0_0_20px_rgba(168,85,247,0.5)] z-10">
      <div class="i-carbon:list-checked text-2xl text-purple-500"></div>
    </div>
    <div class="text-xs font-bold text-gray-300 uppercase tracking-widest text-center">FRS (HOW)</div>
  </div>

  <div class="i-carbon:arrow-right text-xl text-gray-600"></div>

  <!-- AI Code -->
  <div class="flex flex-col items-center gap-3">
    <div class="w-14 h-14 rounded-full bg-gray-800 border-2 border-cyan-500 flex items-center justify-center shadow-[0_0_20px_rgba(6,182,212,0.5)]">
      <div class="i-carbon:bot text-2xl text-cyan-500"></div>
    </div>
    <div class="text-xs font-bold text-cyan-400 uppercase tracking-widest text-center italic">AI Code</div>
  </div>

  <div class="i-carbon:arrow-right text-xl text-gray-600"></div>

  <!-- Human Validation 2 -->
  <div class="flex flex-col items-center gap-3 relative">
    <!-- Highlight Ring -->
    <div class="absolute -inset-2 border-2 border-dashed border-green-400 rounded-full animate-spin pointer-events-none shadow-[0_0_15px_rgba(34,197,94,0.6)]" style="animation-duration: 10s;"></div>
    <div class="w-14 h-14 rounded-full bg-gray-800 border-2 border-green-500 flex items-center justify-center shadow-[0_0_20px_rgba(34,197,94,0.5)] z-10">
      <div class="i-carbon:checkmark-filled text-2xl text-green-500"></div>
    </div>
    <div class="text-xs font-bold text-green-400 uppercase tracking-widest text-center">Human<br>Review</div>
  </div>

  <div class="i-carbon:arrow-right text-xl text-gray-600"></div>

  <!-- RELEASE -->
  <div class="flex flex-col items-center gap-3">
     <div class="w-14 h-14 rounded-full bg-gradient-to-br from-pink-500 to-orange-500 flex items-center justify-center shadow-[0_0_30px_rgba(236,72,153,0.8)] z-10 overflow-visible">
      <div class="i-carbon:rocket text-2xl text-white animate-rocket-fly"></div>
    </div>
    <div class="text-xs font-bold text-pink-400 uppercase tracking-widest text-center">RELEASE</div>
  </div>
</div>


<!-- Quote/Validation Importance -->
<div v-click class="relative w-4/5 p-8 bg-white/5 border border-white/10 rounded-2xl text-center backdrop-blur-md">
  <div class="absolute -left-6 -top-6 text-6xl text-white/10 italic font-serif">"</div>
  <div class="text-3xl font-light text-gray-200 mb-6 leading-relaxed">
    AI can verify <span class="text-cyan-400 font-bold">correctness</span>.<br>
    Only humans can verify <span class="text-orange-400 font-bold">need</span>.
  </div>
  <div class="w-2/3 mx-auto h-px bg-gradient-to-r from-transparent via-gray-600 to-transparent mb-4"></div>
  <p class="text-sm text-gray-400">
    <span class="text-orange-400 font-bold">Key Insight:</span> Human testing determines value, usability, and strategic alignment—things AI cannot simulate.
  </p>
</div>

</div>

---
layout: default
transition: slide-up
class: bg-gray-900 text-white
---

# <span class="text-cyan-500">Collaborative</span> Roles & Responsibilities

<div class="grid grid-cols-5 gap-4 h-[80%] mt-8">

  <!-- SM -->
  <div v-click="1" class="flex flex-col items-center p-4 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/10 transition-all group">
    <div class="w-12 h-12 bg-pink-500/20 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
      <div class="i-carbon:user-activity text-2xl text-pink-400"></div>
    </div>
    <div class="text-lg font-bold text-pink-400 mb-1">SM</div>
    <div class="text-[10px] uppercase tracking-tighter text-gray-400 mb-4 text-center">Sales Manager</div>
    <div class="w-full h-px bg-white/10 mb-4"></div>
    <ul class="text-[10px] space-y-3 text-gray-300">
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-pink-500 text-xs"></div> Client Vision</li>
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-pink-500 text-xs"></div> High-level BRS</li>
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-pink-500 text-xs"></div> Scope Anchor</li>
    </ul>
  </div>

  <!-- PM -->
  <div v-click="2" class="flex flex-col items-center p-4 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/10 transition-all group">
    <div class="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
      <div class="i-carbon:event-schedule text-2xl text-blue-400"></div>
    </div>
    <div class="text-lg font-bold text-blue-400 mb-1">PM</div>
    <div class="text-[10px] uppercase tracking-tighter text-gray-400 mb-4 text-center">Project Manager</div>
    <div class="w-full h-px bg-white/10 mb-4"></div>
    <ul class="text-[10px] space-y-3 text-gray-300">
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-blue-500 text-xs"></div> Resource Sync</li>
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-blue-500 text-xs"></div> PRD Ownership</li>
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-blue-500 text-xs"></div> Mile-stone Mgmt</li>
    </ul>
  </div>

  <!-- FC -->
  <div v-click="3" class="flex flex-col items-center p-4 bg-white/5 border border-white/20 rounded-2xl bg-gradient-to-b from-purple-500/10 to-transparent hover:bg-white/10 transition-all group shadow-[0_0_20px_rgba(168,85,247,0.2)]">
    <div class="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-[0_0_15px_rgba(168,85,247,0.4)]">
      <div class="i-carbon:flow-data text-2xl text-purple-400"></div>
    </div>
    <div class="text-lg font-bold text-purple-400 mb-1">FC</div>
    <div class="text-[10px] uppercase tracking-tighter text-gray-400 mb-4 text-center font-bold">Functional Consultant</div>
    <div class="w-full h-px bg-white/10 mb-4"></div>
    <ul class="text-[10px] space-y-3 text-gray-300">
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-purple-500 text-xs"></div> Process Design</li>
      <li class="flex gap-2 font-bold text-white"><div class="i-carbon:checkmark-filled text-purple-500 text-xs"></div> FRS Mastery</li>
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-purple-500 text-xs"></div> Logic Audit</li>
    </ul>
  </div>

  <!-- TC -->
  <div v-click="4" class="flex flex-col items-center p-4 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/10 transition-all group">
    <div class="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
      <div class="i-carbon:terminal text-2xl text-green-400"></div>
    </div>
    <div class="text-lg font-bold text-green-400 mb-1">TC</div>
    <div class="text-[10px] uppercase tracking-tighter text-gray-400 mb-4 text-center">Technical Consultant</div>
    <div class="w-full h-px bg-white/10 mb-4"></div>
    <ul class="text-[10px] space-y-3 text-gray-300">
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-green-500 text-xs"></div> AI Orchestration</li>
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-green-500 text-xs"></div> System Arch</li>
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-green-500 text-xs"></div> Code Quality</li>
    </ul>
  </div>

  <!-- SS -->
  <div v-click="5" class="flex flex-col items-center p-4 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/10 transition-all group">
    <div class="w-12 h-12 bg-yellow-500/20 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
      <div class="i-carbon:cloud-service-management text-2xl text-yellow-400"></div>
    </div>
    <div class="text-lg font-bold text-yellow-400 mb-1">SS</div>
    <div class="text-[10px] uppercase tracking-tighter text-gray-400 mb-4 text-center">Shared Service</div>
    <div class="w-full h-px bg-white/10 mb-4"></div>
    <ul class="text-[10px] space-y-3 text-gray-300">
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-yellow-500 text-xs"></div> Cross-Dept Sync</li>
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-yellow-500 text-xs"></div> Security Stds</li>
      <li class="flex gap-2"><div class="i-carbon:checkmark-filled text-yellow-500 text-xs"></div> Infrastructure</li>
    </ul>
  </div>

</div>

<div v-click="6" class="mt-8 text-center text-xs text-gray-500 italic">
  * All roles interact with AI to accelerate their specific domain deliverables.
</div>

