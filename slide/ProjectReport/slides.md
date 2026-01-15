---
theme: default
background: ./assets/title-bg.png
class: text-center
highlighter: shiki
lineNumbers: true
drawings:
  persist: false
transition: fade-out
title: The Culture Orbital: Technical Synthesis 2026
mdc: true
---

<div class="h-full flex flex-row justify-center items-center text-white gap-10">
  <div class="flex-1 text-left animate-bounce-in">
    <div class="relative group inline-block">
      <div class="absolute -inset-2 bg-gradient-to-r from-indigo-400 via-cyan-500 to-silver-200 rounded-3xl blur opacity-30 group-hover:opacity-100 transition duration-1000"></div>
      <div class="relative px-8 py-6 bg-black/60 backdrop-blur-2xl border-2 border-white/20 rounded-3xl shadow-[0_20px_50px_rgba(34,211,238,0.2)]">
        <h1 class="text-7xl font-black mb-2 tracking-tighter leading-none">
          <span class="text-transparent bg-clip-text bg-gradient-to-br from-white via-cyan-200 to-indigo-400 animate-pulse">
            Hello, Sentients! �
          </span>
        </h1>
        <h2 class="text-3xl font-black opacity-90 tracking-[0.1em] uppercase transform -rotate-1 font-serif italic">
          Orbital Optimization Hub
        </h2>
      </div>
    </div>

    <div class="mt-10 space-y-4">
      <div class="flex items-center gap-4 animate-slide-in-left" style="animation-delay: 0.2s">
        <div class="w-12 h-12 rounded-full bg-indigo-500 flex items-center justify-center text-2xl shadow-lg border-2 border-white/20">
          <div class="i-carbon:chip"></div>
        </div>
        <div>
          <div class="text-[10px] uppercase font-black tracking-widest text-cyan-300">Avatar Designated</div>
          <div class="text-xl font-black italic">TC | Collective Mind-Brain</div>
        </div>
      </div>
      <div class="flex items-center gap-4 animate-slide-in-left" style="animation-delay: 0.4s">
        <div class="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center text-2xl backdrop-blur-md border border-white/20">
          <div class="i-carbon:rocket"></div>
        </div>
        <div>
          <div class="text-[10px] uppercase font-black tracking-widest text-indigo-300">Operation Cycle</div>
          <div class="text-xl font-black opacity-80 italic">GSV Pure Innovation | Q1-26</div>
        </div>
      </div>
    </div>
  </div>

  <div class="flex-none w-1/3 relative animate-float">
    <img src="./assets/pm-character.png" class="w-full drop-shadow-[0_0_80px_rgba(255,255,255,0.3)] transform hover:scale-105 transition duration-500">
    <div class="absolute -top-5 -right-5 bg-white text-black px-6 py-2 rounded-full font-black text-xs uppercase tracking-widest shadow-2xl border-4 border-indigo-500 animate-pulse">
      In Contact
    </div>
  </div>
</div>

<!-- Bio-Stack Side Panel -->
<div class="abs-br m-10 w-80 text-left animate-wiggle">
  <div class="px-6 py-4 bg-white/5 backdrop-blur-3xl border border-white/20 rounded-3xl shadow-2xl overflow-hidden text-white">
    <div class="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 blur-3xl rounded-full"></div>
    <div class="text-xs font-black uppercase tracking-widest text-cyan-400 mb-4 flex justify-between">
      <span>Synthesis Directives</span>
      <span class="animate-ping tracking-tighter text-[8px]">ACTIVE</span>
    </div>
    <div class="space-y-3 relative">
      <div class="flex items-center gap-3 transform hover:translate-x-2 transition border-l-2 border-red-500 pl-3 bg-white/5 py-1">
        <div class="text-xs font-bold text-white leading-tight">01. Budget Control</div>
      </div>
      <div class="flex items-center gap-3 transform hover:translate-x-2 transition border-l-2 border-indigo-400 pl-3 py-1">
        <div class="text-xs font-bold leading-tight">02. Container Capacity</div>
      </div>
      <div class="flex items-center gap-3 transform hover:translate-x-2 transition border-l-2 border-emerald-500 pl-3 py-1">
        <div class="text-xs font-bold leading-tight">03. HR Lab Portal</div>
      </div>
    </div>
  </div>
</div>

---
layout: default
clicks: 1
---

<div class="flex items-center gap-4 mb-2">
  <div class="text-5xl animate-bounce">�</div>
  <div>
    <h1 class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-300 to-cyan-400">
      Orbital Manifest: Projects
    </h1>
    <p class="opacity-50 font-bold italic font-serif">A civilized tracking of our collective efforts.</p>
  </div>
</div>

<div class="mt-4 overflow-hidden bg-white/5 border border-white/10 rounded-[2rem] text-left p-2 backdrop-blur-3xl shadow-inner">
  <table class="w-full text-[11px] border-collapse">
    <thead class="bg-white/10 uppercase font-black opacity-60 text-indigo-200">
      <tr>
        <th class="p-3 text-left italic">Vessel (Mission)</th>
        <th class="p-3 text-center w-8">Priority</th>
        <th class="p-3 text-left">Vector Point</th>
        <th class="p-3 text-left">Internal Status</th>
        <th class="p-3 text-center">Sub-Mind</th>
        <th class="p-3 text-right">State</th>
      </tr>
    </thead>
    <tbody v-if="$clicks === 0" class="animate-fade-in">
      <tr class="border-b border-white/5 group hover:bg-white/5 transition px-2">
        <td class="p-3"><div class="flex items-center gap-2">� <div><div class="text-[9px] font-bold opacity-40">BC</div><div class="font-black text-white">Budget Control Extension</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-red-500/80 text-white text-[8px] font-black rounded-lg shadow-lg">P1</span></td>
        <td class="p-3 opacity-70 italic font-bold">Requirement Scry</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-2 rounded-full overflow-hidden border border-white/5"><div class="h-full bg-gradient-to-r from-indigo-400 to-cyan-300 rounded-full" style="width: 20%"></div></div><span class="text-[10px] font-black opacity-50">20%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-indigo-300 underline underline-offset-4 decoration-white/20">Panha Mind</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-indigo-500 text-white shadow-xl">Engaged</span></td>
      </tr>
      <tr class="border-b border-white/5 group hover:bg-white/5 transition">
        <td class="p-3"><div class="flex items-center gap-2">🧱 <div><div class="text-[9px] font-bold opacity-40">BC</div><div class="font-black text-white">Container Capacity Management</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-red-500/80 text-white text-[8px] font-black rounded-lg shadow-lg">P1</span></td>
        <td class="p-3 opacity-70 italic font-bold">Vector Mapping</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-2 rounded-full overflow-hidden border border-white/5"><div class="h-full bg-gradient-to-r from-indigo-400 to-cyan-300 rounded-full" style="width: 10%"></div></div><span class="text-[10px] font-black opacity-50">10%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-indigo-300 underline decoration-white/20">Kanel Mind</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-indigo-500 text-white">Engaged</span></td>
      </tr>
      <tr class="border-b border-white/5 group hover:bg-white/5 transition">
        <td class="p-3"><div class="flex items-center gap-2">🧬 <div><div class="text-[9px] font-bold opacity-40">HRMS</div><div class="font-black text-white">HR Lab</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-indigo-400 text-white text-[8px] font-black rounded-lg shadow-lg">P2</span></td>
        <td class="p-3 opacity-70 italic font-bold">DNA Compilation</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-2 rounded-full overflow-hidden border border-white/5"><div class="h-full bg-gradient-to-r from-indigo-200 to-silver-100 rounded-full" style="width: 85%"></div></div><span class="text-[10px] font-black opacity-50">85%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-indigo-300 underline decoration-white/20">Monika Mind</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-cyan-500 text-white animate-pulse">Compiling</span></td>
      </tr>
      <tr class="group hover:bg-white/5 transition">
        <td class="p-3"><div class="flex items-center gap-2">�️ <div><div class="text-[9px] font-bold opacity-40">HRMS</div><div class="font-black text-white">HR Lab Mobile Apps</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-indigo-400 text-white text-[8px] font-black rounded-lg shadow-lg">P2</span></td>
        <td class="p-3 opacity-70 italic font-bold">Mobility Logic</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-2 rounded-full overflow-hidden border border-white/5"><div class="h-full bg-gradient-to-r from-indigo-200 to-silver-100 rounded-full" style="width: 50%"></div></div><span class="text-[10px] font-black opacity-50">50%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-indigo-300 underline decoration-white/20">Monika Mind</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-cyan-500 text-white">Compiling</span></td>
      </tr>
    </tbody>
    <tbody v-if="$clicks === 1" class="animate-fade-in">
      <tr class="border-b border-white/5 group hover:bg-white/5 transition px-2">
        <td class="p-3"><div class="flex items-center gap-2">🥪 <div><div class="text-[9px] font-bold opacity-40">Retail</div><div class="font-black text-white">NGPOS (F&B)</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-cyan-600 text-white text-[8px] font-black rounded-lg shadow-lg">P3</span></td>
        <td class="p-3 opacity-70 italic font-bold">Atomic Integration</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-2 rounded-full overflow-hidden border border-white/5"><div class="h-full bg-cyan-400" style="width: 30%"></div></div><span class="text-[10px] font-black opacity-50">30%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-indigo-300 underline decoration-white/20">Marchi Mind</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-indigo-500 text-white">Engaged</span></td>
      </tr>
       <tr class="border-b border-white/5 group hover:bg-white/5 transition px-2">
        <td class="p-3"><div class="flex items-center gap-2">� <div><div class="text-[9px] font-bold opacity-40">CRM</div><div class="font-black text-white">Bullseye</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-white/20 text-white text-[8px] font-black rounded-lg">P4</span></td>
        <td class="p-3 opacity-70 italic font-bold">Calibration</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-2 rounded-full overflow-hidden border border-white/5"><div class="h-full bg-white/20" style="width: 5%"></div></div><span class="text-[10px] font-black opacity-30">5%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-white/50">Collective CRM</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-white/10 text-white/30 italic">Stasis</span></td>
      </tr>
      <tr class="border-b border-white/5 group hover:bg-white/5 transition">
        <td class="p-3"><div class="flex items-center gap-2">💰 <div><div class="text-[9px] font-bold opacity-40">QC</div><div class="font-black text-white">CryptoTrading</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-white/20 text-white text-[8px] font-black rounded-lg">P4</span></td>
        <td class="p-3 opacity-70 italic font-bold">Resource Simulation</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-2 rounded-full overflow-hidden border border-white/5"><div class="h-full bg-white/20" style="width: 0%"></div></div><span class="text-[10px] font-black opacity-30">0%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-white/50 italic">Gordon Mind</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-white/10 text-white/30 italic">Stasis</span></td>
      </tr>
      <tr class="border-b border-white/5 group hover:bg-white/5 transition">
        <td class="p-3"><div class="flex items-center gap-2">� <div><div class="text-[9px] font-bold opacity-40">Custom</div><div class="font-black text-white">Car Parking & Dormitory</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-white/20 text-white text-[8px] font-black rounded-lg">P5</span></td>
        <td class="p-3 opacity-70 italic font-bold">Planned Arrival</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-2 rounded-full overflow-hidden border border-white/5"><div class="h-full bg-white/20" style="width: 3%"></div></div><span class="text-[10px] font-black opacity-30">3%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-white/50 italic">Kanel Mind</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-white/10 text-white/30 italic">Stasis</span></td>
      </tr>
    </tbody>
  </table>
</div>

<div class="mt-6 flex gap-6 text-left">
  <div class="p-4 bg-white/5 border border-white/20 rounded-[2rem] flex items-center gap-6 flex-1 shadow-[0_0_30px_rgba(255,255,255,0.05)]">
    <div class="text-5xl font-black italic text-cyan-300 drop-shadow-[0_0_10px_white]">25.5%</div>
    <div class="text-xs uppercase font-black leading-tight tracking-[0.2em] opacity-80">Collective Exp.<br>Efficiency</div>
  </div>
  <div class="p-4 bg-indigo-500/10 border border-indigo-400/20 rounded-[2rem] flex items-center gap-4 flex-1">
    <div class="w-4 h-4 rounded-full bg-cyan-400 animate-ping"></div>
    <span class="text-xs font-black uppercase tracking-widest text-cyan-200">Orbital Stability: Optimal</span>
  </div>
</div>

---
layout: default
---

<div class="flex items-center gap-4 mb-2">
  <div class="text-5xl animate-float">💠</div>
  <div>
    <h1 class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-indigo-300">
      Mission Vectors: Deep Dive
    </h1>
    <p class="opacity-50 font-bold italic font-serif">Fine-tuning the neural interface!</p>
  </div>
</div>

<div class="mt-6 grid grid-cols-5 gap-4">
  <div class="col-span-3 overflow-hidden bg-white/5 border border-white/10 rounded-[2.5rem] p-4 text-left shadow-2xl backdrop-blur-md">
    <table class="w-full text-[11px]">
      <thead class="bg-white/10 opacity-70 uppercase font-black text-white tracking-widest">
        <tr>
          <th class="p-3">Mission Vector</th>
          <th class="p-3">Sub-Task String</th>
          <th class="p-3 text-center">Sync Rate</th>
          <th class="p-3 text-right">Hero Mind</th>
        </tr>
      </thead>
      <tbody class="font-medium text-silver-100">
        <tr class="border-b border-white/5 hover:bg-white/5 transition"><td class="p-3 font-black">Budget Ctrl</td><td class="p-3 italic opacity-60">Gap Analysis Forge</td><td class="p-3 text-center font-black text-cyan-300">30%</td><td class="p-3 text-right">Panha</td></tr>
        <tr class="border-b border-white/5 hover:bg-white/5 transition"><td class="p-3 font-black">Container</td><td class="p-3 italic opacity-60">Stealth Requirement</td><td class="p-3 text-center font-black text-cyan-300">15%</td><td class="p-3 text-right">Kanel</td></tr>
        <tr class="border-b border-white/5 hover:bg-white/5 transition"><td class="p-3 font-black text-indigo-200">HR Lab (W)</td><td class="p-3 italic opacity-60">Workflow Weaving</td><td class="p-3 text-center font-black text-indigo-200">85%</td><td class="p-3 text-right">Monika</td></tr>
        <tr class="border-b border-white/5 hover:bg-white/5 transition"><td class="p-3 font-black text-indigo-200">HR Mobile</td><td class="p-3 italic opacity-60">Multitenant Matrix</td><td class="p-3 text-center font-black text-indigo-200">50%</td><td class="p-3 text-right">Monika</td></tr>
        <tr class="hover:bg-white/5 transition"><td class="p-3 font-black text-cyan-200">NGPOS</td><td class="p-3 italic opacity-60">Architectural Pulse</td><td class="p-3 text-center font-black text-cyan-200">30%</td><td class="p-3 text-right">Marchi</td></tr>
      </tbody>
    </table>
  </div>
  
  <div class="col-span-2 relative group">
    <div class="absolute inset-0 bg-indigo-500/10 blur-3xl opacity-0 group-hover:opacity-100 transition duration-1000"></div>
    <img src="./assets/team-sketch.png" class="w-full opacity-70 animate-float shadow-2xl rounded-3xl group-hover:opacity-100 transition" />
    <div class="mt-4 p-4 border border-white/20 rounded-3xl bg-white/5 text-[10px] font-black text-center uppercase leading-tight italic tracking-widest text-silver-300">
      "Civilization is just a series of correctly timed interactions."
    </div>
  </div>
</div>

---
layout: default
---

<div class="flex items-center gap-4 mb-2">
  <div class="text-5xl animate-shake">🌀</div>
  <div>
    <h1 class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-red-200 via-orange-300 to-white">
      Special Circumstances & Upgrades
    </h1>
    <p class="opacity-50 font-bold italic font-serif">Negotiating with the universal entropy!</p>
  </div>
</div>

<div class="grid grid-cols-2 gap-8 mt-8">
  <div class="p-8 bg-red-500/10 border border-white/10 rounded-[3rem] relative animate-float shadow-[0_0_50px_rgba(239,68,68,0.1)]">
    <div class="absolute -top-4 -right-4 text-6xl opacity-10 font-bold">WAR</div>
    <div class="flex items-center gap-4 mb-6">
      <div class="w-12 h-12 rounded-full bg-red-600 flex items-center justify-center shadow-xl shadow-red-500/50 text-2xl border-2 border-white/20 text-white">🔥</div>
      <h3 class="text-2xl font-black uppercase text-red-500 italic tracking-tighter">Hegemonising Swarms</h3>
    </div>
    <ul class="text-sm space-y-6 font-bold text-silver-200">
      <li class="flex gap-4 p-4 bg-black/40 rounded-[2rem] border border-white/5 backdrop-blur-md">
        <span class="text-3xl">�</span>
        <span><b>Apprentice Paradox:</b> Junior Minds are fast with AI, but need <b>Special Circumstances</b> (Senior Overlook) to prevent orbital decay.</span>
      </li>
      <li class="flex gap-4 p-4 bg-black/40 rounded-[2rem] border border-white/5 backdrop-blur-md">
        <span class="text-3xl">⚖️</span>
        <span><b>Verification Null:</b> We need <b>Domain Minds</b> to verify if the output is actually beneficial to the Culture!</span>
      </li>
    </ul>
  </div>

  <div class="p-8 bg-indigo-500/10 border border-white/10 rounded-[3rem] relative animate-bounce-in shadow-[0_0_50px_rgba(79,70,229,0.1)]">
    <div class="absolute -top-4 -left-4 text-6xl opacity-10 font-bold">MIND</div>
    <div class="flex items-center gap-4 mb-6">
      <div class="w-12 h-12 rounded-full bg-indigo-600 flex items-center justify-center shadow-xl shadow-indigo-500/50 text-2xl border-2 border-white/20 text-white">🛡️</div>
      <h3 class="text-2xl font-black uppercase text-indigo-400 italic tracking-tighter">Neuro-Buffs Required</h3>
    </div>
    <ul class="text-sm space-y-6 font-bold text-silver-200">
      <li class="flex gap-4 p-4 bg-black/40 rounded-[2rem] border border-white/5 backdrop-blur-md">
        <span class="text-3xl">�</span>
        <span><b>Vector Priority:</b> Define the primary destination. Which mission takes the lead in this sector of space?</span>
      </li>
      <li class="flex gap-4 p-4 bg-black/40 rounded-[2rem] border border-white/5 backdrop-blur-md">
        <span class="text-3xl">🤝</span>
        <span><b>Expert Unit:</b> Summon 2 Power Sentients for a 1-week evaluation raid on the code manifest.</span>
      </li>
    </ul>
  </div>
</div>

---
layout: center
class: text-center
---

<div class="animate-bounce-in">
  <div class="text-8xl mb-8 animate-float">🛸</div>
  <h1 class="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-silver-100 via-white to-cyan-300 animate-pulse">
    Synthesis Stabilized.
  </h1>
  <p class="text-xl font-bold opacity-60 mt-4 tracking-[0.5em] uppercase font-serif italic text-white">Infinite Fun Space Awaits</p>
  
  <div class="mt-12 flex justify-center gap-10 opacity-40">
    <div class="animate-float text-4xl" style="animation-delay: 0.1s">�</div>
    <div class="animate-float text-4xl" style="animation-delay: 0.3s">🌐</div>
    <div class="animate-float text-4xl" style="animation-delay: 0.5s">✨</div>
  </div>
</div>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;700;900&family=DynaPuff:wght@400;700&family=Playfair+Display:ital,wght@1,900&display=swap');

h1, .font-black {
  font-family: 'DynaPuff', cursive;
  letter-spacing: -0.04em;
}

h2, .font-serif {
  font-family: 'Playfair Display', serif;
}

body {
  font-family: 'Outfit', sans-serif;
  background: radial-gradient(circle at 50% 50%, #1e293b 0%, #0f172a 100%);
  color: #f8fafc;
}

.animate-float {
  animation: float 8s ease-in-out infinite;
}

.animate-wiggle {
  animation: wiggle 4s ease-in-out infinite;
}

.animate-bounce-in {
  animation: bounce-in 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.animate-shake {
  animation: shake 5s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0); }
  50% { transform: translateY(-30px) rotate(1deg); }
}

@keyframes wiggle {
  0%, 100% { transform: rotate(-0.5deg); }
  50% { transform: rotate(0.5deg); }
}

@keyframes bounce-in {
  0% { transform: scale(0.5); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes shake {
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(-2px, 1px); }
  50% { transform: translate(2px, -1px); }
  75% { transform: translate(-1px, -2px); }
}

.animate-slide-in-left {
  animation: slide-in-left 1s cubic-bezier(0.23, 1, 0.32, 1) forwards;
  opacity: 0;
}

@keyframes slide-in-left {
  0% { transform: translateX(-100px); opacity: 0; }
  100% { transform: translateX(0); opacity: 1; }
}

table th { 
  font-family: 'DynaPuff', cursive; 
  text-transform: uppercase; 
  letter-spacing: 0.2em; 
  background-color: rgba(255,255,255,0.05);
}

.backdrop-blur-3xl {
  backdrop-filter: blur(60px);
}

.text-silver-100 { color: #e2e8f0; }
.text-silver-200 { color: #cbd5e1; }
.text-silver-300 { color: #94a3b8; }
</style>
