---
theme: default
background: ./assets/title-bg.png
class: text-center
highlighter: shiki
lineNumbers: true
drawings:
  persist: false
transition: fade-out
title: TC's Awesome Project Adventure 2026
mdc: true
---

<div class="h-full flex flex-row justify-center items-center text-white gap-10">
  <div class="flex-1 text-left animate-bounce-in">
    <div class="relative group inline-block">
      <div class="absolute -inset-2 bg-gradient-to-r from-yellow-400 via-orange-500 to-red-600 rounded-3xl blur opacity-30 group-hover:opacity-100 transition duration-1000"></div>
      <div class="relative px-8 py-6 bg-black/50 backdrop-blur-2xl border-4 border-dashed border-white/20 rounded-3xl">
        <h1 class="text-7xl font-black mb-2 tracking-tighter leading-none">
          <span class="text-transparent bg-clip-text bg-gradient-to-br from-yellow-300 to-orange-500 animate-pulse">
            Hello, Team! 🚀
          </span>
        </h1>
        <h2 class="text-3xl font-black opacity-90 tracking-tight uppercase transform -rotate-1">
          Technical Adventure Hub 2026
        </h2>
      </div>
    </div>

    <div class="mt-10 space-y-4">
      <div class="flex items-center gap-4 animate-slide-in-left" style="animation-delay: 0.2s">
        <div class="w-12 h-12 rounded-full bg-cyan-400 flex items-center justify-center text-2xl shadow-lg shadow-cyan-400/50">👨‍💻</div>
        <div>
          <div class="text-[10px] uppercase font-black tracking-widest text-cyan-400">Chief Navigator</div>
          <div class="text-xl font-black italic">TC | Technical Lead</div>
        </div>
      </div>
      <div class="flex items-center gap-4 animate-slide-in-left" style="animation-delay: 0.4s">
        <div class="w-12 h-12 rounded-full bg-orange-400 flex items-center justify-center text-2xl shadow-lg shadow-orange-400/50">📅</div>
        <div>
          <div class="text-[10px] uppercase font-black tracking-widest text-orange-400">Quarterly Mission</div>
          <div class="text-xl font-black opacity-80">Cycle Q1 / FY-2026</div>
        </div>
      </div>
    </div>
  </div>

  <div class="flex-none w-1/3 relative animate-float">
    <img src="./assets/pm-character.png" class="w-full drop-shadow-[0_20px_50px_rgba(34,_211,_238,_0.5)] transform hover:scale-105 transition duration-500" />
    <div class="absolute -top-10 -right-10 bg-yellow-400 text-black px-6 py-2 rounded-full font-black text-xs uppercase tracking-widest transform rotate-12 shadow-xl border-4 border-black">
      Ready to Launch!
    </div>
  </div>
</div>

<!-- Priority Cloud -->
<div class="abs-br m-10 w-80 text-left animate-wiggle">
  <div class="px-6 py-4 bg-white/10 backdrop-blur-xl border-2 border-white/20 rounded-[2rem] shadow-2xl relative">
    <div class="absolute -top-5 -left-5 bg-indigo-500 text-white p-2 rounded-lg rotate-[-10deg] shadow-lg">⭐</div>
    <div class="text-xs font-black uppercase tracking-widest text-indigo-300 mb-4 flex justify-between">
      <span>Priority Mission Stack</span>
      <span class="animate-ping">🔥</span>
    </div>
    <div class="space-y-3">
      <div class="flex items-center gap-3 transform hover:translate-x-2 transition">
        <div class="text-xs font-black text-red-400">#1</div>
        <div class="text-xs font-bold text-white leading-tight">NGD Budget Control</div>
      </div>
      <div class="flex items-center gap-3 transform hover:translate-x-2 transition opacity-80">
        <div class="text-xs font-black text-orange-400">#2</div>
        <div class="text-xs font-bold leading-tight">NGD Container Mgmt</div>
      </div>
      <div class="flex items-center gap-3 transform hover:translate-x-2 transition opacity-60">
        <div class="text-xs font-black text-emerald-400">#3</div>
        <div class="text-xs font-bold leading-tight">HR Lab (All Screens)</div>
      </div>
    </div>
  </div>
</div>

---
layout: default
clicks: 1
---

<div class="flex items-center gap-4 mb-2">
  <div class="text-5xl animate-bounce">📊</div>
  <div>
    <h1 class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
      Mission Status: Portfolio
    </h1>
    <p class="opacity-50 font-bold italic">The delivery roadmap in detail!</p>
  </div>
</div>

<div class="mt-4 overflow-hidden bg-white/5 border-2 border-dashed border-white/20 rounded-[2rem] text-left p-2 backdrop-blur-sm">
  <table class="w-full text-[11px] border-collapse">
    <thead class="bg-white/10 uppercase font-black opacity-60 text-cyan-300">
      <tr>
        <th class="p-3 text-left">The Mission (Project)</th>
        <th class="p-3 text-center w-8">Rank</th>
        <th class="p-3 text-left">Checkpoint</th>
        <th class="p-3 text-left">Level Progress</th>
        <th class="p-3 text-center">Hero</th>
        <th class="p-3 text-right">Status</th>
      </tr>
    </thead>
    <tbody v-if="$clicks === 0" class="animate-fade-in">
      <tr class="border-b border-white/5 group hover:bg-white/5 transition px-2">
        <td class="p-3"><div class="flex items-center gap-2">🕹️ <div><div class="text-[9px] font-bold opacity-40">BC</div><div class="font-black text-cyan-400">Budget Control Extension</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-red-500 text-white text-[8px] font-black rounded-lg shadow-lg animate-pulse">P1</span></td>
        <td class="p-3 opacity-70 italic font-bold">Requirement Hunt</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-3 rounded-full overflow-hidden border border-white/10"><div class="h-full bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full" style="width: 20%"></div></div><span class="text-[10px] font-black">20%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-cyan-400 underline decoration-dotted">Panha</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-emerald-400 text-black shadow-lg">In Flight</span></td>
      </tr>
      <tr class="border-b border-white/5 group hover:bg-white/5 transition">
        <td class="p-3"><div class="flex items-center gap-2">📦 <div><div class="text-[9px] font-bold opacity-40">BC</div><div class="font-black text-cyan-400">Container Capacity Management</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-red-500 text-white text-[8px] font-black rounded-lg shadow-lg">P1</span></td>
        <td class="p-3 opacity-70 italic font-bold">Requirement Hunt</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-3 rounded-full overflow-hidden border border-white/10"><div class="h-full bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full" style="width: 10%"></div></div><span class="text-[10px] font-black">10%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-cyan-400 underline decoration-dotted">Kanel</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-emerald-400 text-black">In Flight</span></td>
      </tr>
      <tr class="border-b border-white/5 group hover:bg-white/5 transition">
        <td class="p-3"><div class="flex items-center gap-2">🧬 <div><div class="text-[9px] font-bold opacity-40">HRMS</div><div class="font-black text-emerald-400">HR Lab</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-orange-400 text-white text-[8px] font-black rounded-lg shadow-lg">P2</span></td>
        <td class="p-3 opacity-70 italic font-bold">Code Crafting</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-3 rounded-full overflow-hidden border border-white/10"><div class="h-full bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full" style="width: 85%"></div></div><span class="text-[10px] font-black">85%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-emerald-400 underline decoration-dotted">Monika</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-blue-500 text-white animate-pulse">Coding</span></td>
      </tr>
      <tr class="border-b border-white/5 group hover:bg-white/5 transition">
        <td class="p-3"><div class="flex items-center gap-2">📱 <div><div class="text-[9px] font-bold opacity-40">HRMS</div><div class="font-black text-emerald-400">HR Lab Mobile Apps</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-orange-400 text-white text-[8px] font-black rounded-lg shadow-lg">P2</span></td>
        <td class="p-3 opacity-70 italic font-bold">Code Crafting</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-3 rounded-full overflow-hidden border border-white/10"><div class="h-full bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full" style="width: 50%"></div></div><span class="text-[10px] font-black">50%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-emerald-400 underline decoration-dotted">Monika</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-blue-500 text-white">Coding</span></td>
      </tr>
      <tr class="group hover:bg-white/5 transition">
        <td class="p-3"><div class="flex items-center gap-2">🛒 <div><div class="text-[9px] font-bold opacity-40">Retail</div><div class="font-black text-sky-400">NGPOS (F&B)</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-sky-400 text-white text-[8px] font-black rounded-lg shadow-lg">P3</span></td>
        <td class="p-3 opacity-70 italic font-bold">Exploration</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-3 rounded-full overflow-hidden border border-white/10"><div class="h-full bg-gradient-to-r from-sky-400 to-blue-500 rounded-full" style="width: 30%"></div></div><span class="text-[10px] font-black">30%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-sky-300 underline decoration-dotted">Marchi</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-emerald-400 text-black">In Flight</span></td>
      </tr>
    </tbody>
    <tbody v-if="$clicks === 1" class="animate-fade-in">
       <tr class="border-b border-white/5 group hover:bg-white/5 transition px-2">
        <td class="p-3"><div class="flex items-center gap-2">🎯 <div><div class="text-[9px] font-bold opacity-40">CRM</div><div class="font-black text-orange-400">Bullseye</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-white/20 text-white text-[8px] font-black rounded-lg">P4</span></td>
        <td class="p-3 opacity-70 italic font-bold">New Mission</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-3 rounded-full overflow-hidden border border-white/10"><div class="h-full bg-orange-400" style="width: 5%"></div></div><span class="text-[10px] font-black">5%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-orange-300 underline decoration-dotted">Team CRM</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-white/20 text-white/50">Resting</span></td>
      </tr>
      <tr class="border-b border-white/5 group hover:bg-white/5 transition">
        <td class="p-3"><div class="flex items-center gap-2">🪙 <div><div class="text-[9px] font-bold opacity-40">QC</div><div class="font-black text-yellow-400">CryptoTrading</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-white/20 text-white text-[8px] font-black rounded-lg">P4</span></td>
        <td class="p-3 opacity-70 italic font-bold">Laboratory R&D</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-3 rounded-full overflow-hidden border border-white/10"><div class="h-full bg-yellow-400" style="width: 0%"></div></div><span class="text-[10px] font-black">0%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-yellow-300 underline decoration-dotted">Gordon</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-white/20 text-white/50">Resting</span></td>
      </tr>
      <tr class="border-b border-white/5 group hover:bg-white/5 transition">
        <td class="p-3"><div class="flex items-center gap-2">🚗 <div><div class="text-[9px] font-bold opacity-40">Custom</div><div class="font-black text-purple-400">Car Parking & Dormitory</div></div></div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 bg-white/20 text-white text-[8px] font-black rounded-lg">P5</span></td>
        <td class="p-3 opacity-70 italic font-bold">The Horizon</td>
        <td class="p-3 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-3 rounded-full overflow-hidden border border-white/10"><div class="h-full bg-purple-400" style="width: 3%"></div></div><span class="text-[10px] font-black">3%</span></div></td>
        <td class="p-3 text-center text-[10px] font-black text-purple-300 underline decoration-dotted">Kanel</td>
        <td class="p-3 text-right"><span class="px-3 py-1 text-[8px] font-black rounded-full uppercase bg-white/20 text-white/50">Resting</span></td>
      </tr>
    </tbody>
  </table>
</div>

<div class="mt-6 flex gap-6 text-left">
  <div class="p-4 bg-gradient-to-br from-blue-600/30 to-cyan-500/10 border-4 border-dashed border-blue-400/30 rounded-3xl flex items-center gap-6 flex-1 animate-wiggle">
    <div class="text-5xl font-black italic text-cyan-400 drop-shadow-lg">25.5%</div>
    <div class="text-xs uppercase font-black leading-tight">Team Adventure<br>Exp. Gained</div>
  </div>
  <div class="p-4 bg-white/5 border-4 border-dashed border-white/10 rounded-3xl flex items-center gap-4 flex-1">
    <div class="w-4 h-4 rounded-full bg-emerald-400 animate-ping" />
    <span class="text-xs font-black uppercase tracking-widest text-emerald-400">Leveling Up Q1!</span>
  </div>
</div>

---
layout: default
---

<div class="flex items-center gap-4 mb-2">
  <div class="text-5xl animate-bounce">⚔️</div>
  <div>
    <h1 class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
      Active Combat: In-Progress
    </h1>
    <p class="opacity-50 font-bold italic">Where the heroes are fighting right now!</p>
  </div>
</div>

<div class="mt-6 grid grid-cols-5 gap-4">
  <div class="col-span-3 overflow-hidden bg-white/5 border-2 border-white/10 rounded-[2rem] p-4 text-left backdrop-blur-md">
    <table class="w-full text-[11px]">
      <thead class="bg-white/10 opacity-70 uppercase font-black text-cyan-300">
        <tr>
          <th class="p-3">Mission</th>
          <th class="p-3">Active Quest</th>
          <th class="p-3 text-center">XP %</th>
          <th class="p-3 text-right">Hero</th>
        </tr>
      </thead>
      <tbody class="font-bold">
        <tr class="border-b border-white/5 hover:bg-white/5 transition"><td class="p-3 text-cyan-400">Budget Ctrl</td><td class="p-3 italic opacity-80">Gap Hunt & Specs</td><td class="p-3 text-center text-cyan-400">30%</td><td class="p-3 text-right">Panha</td></tr>
        <tr class="border-b border-white/5 hover:bg-white/5 transition"><td class="p-3 text-cyan-400">Container</td><td class="p-3 italic opacity-80">Requirement Stealth</td><td class="p-3 text-center text-cyan-400">15%</td><td class="p-3 text-right">Kanel</td></tr>
        <tr class="border-b border-white/5 hover:bg-white/5 transition"><td class="p-3 text-emerald-400">HR Lab (W)</td><td class="p-3 italic opacity-80">Workflow Forge</td><td class="p-3 text-center text-emerald-400">85%</td><td class="p-3 text-right">Monika</td></tr>
        <tr class="border-b border-white/5 hover:bg-white/5 transition"><td class="p-3 text-emerald-400">HR Mobile</td><td class="p-3 italic opacity-80">Multitenant Magic</td><td class="p-3 text-center text-emerald-400">50%</td><td class="p-3 text-right">Monika</td></tr>
        <tr class="hover:bg-white/5 transition"><td class="p-3 text-sky-400">NGPOS</td><td class="p-3 italic opacity-80">UI/DB Summoning</td><td class="p-3 text-center text-sky-400">30%</td><td class="p-3 text-right">Marchi</td></tr>
      </tbody>
    </table>
  </div>
  
  <div class="col-span-2 relative">
    <img src="./assets/team-sketch.png" class="w-full opacity-80 animate-float" />
    <div class="mt-4 p-4 border-2 border-dashed border-indigo-400/30 rounded-2xl bg-indigo-500/5 text-[10px] font-black text-center uppercase leading-tight italic">
      "Unity is the strongest buff in the guild!"
    </div>
  </div>
</div>

---
layout: default
---

<div class="flex items-center gap-4 mb-2">
  <div class="text-5xl animate-wiggle">🛡️</div>
  <div>
    <h1 class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-500">
      Boss Battles & Buffs Needed
    </h1>
    <p class="opacity-50 font-bold italic">Strategy for overcoming current obstacles</p>
  </div>
</div>

<div class="grid grid-cols-2 gap-8 mt-8">
  <div class="p-8 bg-red-500/10 border-4 border-dashed border-red-500/30 rounded-[3rem] relative animate-shake overflow-hidden">
    <div class="absolute -top-4 -right-4 text-6xl opacity-10">👿</div>
    <div class="flex items-center gap-4 mb-6">
      <div class="w-12 h-12 rounded-full bg-red-500 flex items-center justify-center shadow-xl shadow-red-500/50 text-2xl">🔥</div>
      <h3 class="text-2xl font-black uppercase text-red-100 italic">Boss Monsters</h3>
    </div>
    <ul class="text-sm space-y-6 font-bold">
      <li class="flex gap-4 p-3 bg-black/20 rounded-2xl">
        <span class="text-3xl">📱</span>
        <span><b>Mobile Production Risk:</b> Our apprentices (Junior Devs) are using powerful AI tools, but we need high-level mages (Architects) to check the spells for stability!</span>
      </li>
      <li class="flex gap-4 p-3 bg-black/20 rounded-2xl">
        <span class="text-3xl">🔍</span>
        <span><b>Testing Gap:</b> We have enough logic, but we need <b>Domain Experts</b> to verify if the treasure (Product) is what the guild actually needs.</span>
      </li>
    </ul>
  </div>

  <div class="p-8 bg-indigo-500/10 border-4 border-double border-indigo-500/30 rounded-[3rem] relative animate-float">
    <div class="absolute -top-4 -left-4 text-6xl opacity-10">✨</div>
    <div class="flex items-center gap-4 mb-6">
      <div class="w-12 h-12 rounded-full bg-indigo-500 flex items-center justify-center shadow-xl shadow-indigo-500/50 text-2xl">🪄</div>
      <h3 class="text-2xl font-black uppercase text-indigo-100 italic">Guild Buffs</h3>
    </div>
    <ul class="text-sm space-y-6 font-bold">
      <li class="flex gap-4 p-3 bg-black/20 rounded-2xl">
        <span class="text-3xl">🗺️</span>
        <span><b>Project Priority:</b> We need a clear map! Which dungeon should we clear first to maximize our Q1 loot?</span>
      </li>
      <li class="flex gap-4 p-3 bg-black/20 rounded-2xl">
        <span class="text-3xl">🤝</span>
        <span><b>Domain Squad:</b> Summon 2 Power Users for a 1-week intensive evaluation raid or module-by-module check.</span>
      </li>
    </ul>
  </div>
</div>

---
layout: center
class: text-center
---

<div class="animate-bounce-in">
  <div class="text-8xl mb-8">🏆</div>
  <h1 class="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-600 animate-pulse">
    Mission Complete!
  </h1>
  <p class="text-xl font-bold opacity-60 mt-4 tracking-[0.3em] uppercase">Ready for the Next Level?</p>
  
  <div class="mt-12 flex justify-center gap-10 opacity-40">
    <div class="animate-float" style="animation-delay: 0.1s text-4xl">🕹️</div>
    <div class="animate-float" style="animation-delay: 0.3s text-4xl">🚀</div>
    <div class="animate-float" style="animation-delay: 0.5s text-4xl">✨</div>
  </div>
</div>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;700;900&family=DynaPuff:wght@400;700&display=swap');

h1, h2, h3, .font-black {
  font-family: 'DynaPuff', cursive;
  letter-spacing: -0.02em;
}

body {
  font-family: 'Outfit', sans-serif;
  background: #0f172a;
}

.animate-float {
  animation: float 6s ease-in-out infinite;
}

.animate-wiggle {
  animation: wiggle 3s ease-in-out infinite;
}

.animate-bounce-in {
  animation: bounce-in 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.animate-shake {
  animation: shake 2s cubic-bezier(.36,.07,.19,.97) alternate infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

@keyframes wiggle {
  0%, 100% { transform: rotate(-1deg); }
  50% { transform: rotate(1deg); }
}

@keyframes bounce-in {
  0% { transform: scale(0.3); opacity: 0; }
  50% { transform: scale(1.05); opacity: 1; }
  70% { transform: scale(0.9); }
  100% { transform: scale(1); }
}

@keyframes shake {
  0% { transform: translateX(0); }
  25% { transform: translateX(-2px); }
  50% { transform: translateX(2px); }
  75% { transform: translateX(-1px); }
  100% { transform: translateX(0); }
}

.animate-slide-in-left {
  animation: slide-in-left 0.8s ease-out forwards;
  opacity: 0;
}

@keyframes slide-in-left {
  0% { transform: translateX(-50px); opacity: 0; }
  100% { transform: translateX(0); opacity: 1; }
}

table th { font-family: 'DynaPuff', cursive; text-transform: uppercase; letter-spacing: 0.1em; }
</style>
