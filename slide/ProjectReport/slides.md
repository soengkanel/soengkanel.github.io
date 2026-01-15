---
theme: default
background: https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&q=80&w=2072
class: text-center
highlighter: shiki
lineNumbers: true
drawings:
  persist: false
transition: slide-up
title: "Mission Control 2026: The Big Flight!"
mdc: true
---

<div class="h-full flex flex-row justify-center items-center gap-6 p-10">
<div class="flex-1 text-left">
<div class="bg-indigo-600 border-8 border-black rounded-[3rem] p-10 shadow-[15px_15px_0px_0px_rgba(33,33,33,1)] transform -rotate-2 hover:rotate-0 transition-transform duration-500 animate-bounce-in">
<h1 class="text-7xl font-black mb-4 tracking-tighter leading-none text-white font-draw">Hello, Crew! <span class="inline-block animate-float">🛸</span></h1>
<h2 class="text-3xl font-bold text-cyan-200 font-draw uppercase">Launching into Q1-26</h2>
</div>
<div class="mt-12 space-y-6">
<div class="flex items-center gap-6 animate-slide-in-left" style="animation-delay: 0.2s">
<div class="w-16 h-16 rounded-2xl bg-orange-500 border-4 border-black flex items-center justify-center text-4xl shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">👨‍🚀</div>
<div><div class="text-sm uppercase font-black tracking-widest text-white/60">Chief Pilot</div><div class="text-2xl font-black text-white font-draw">TC | Flight Commander</div></div>
</div>
<div class="flex items-center gap-6 animate-slide-in-left" style="animation-delay: 0.4s">
<div class="w-16 h-16 rounded-2xl bg-cyan-400 border-4 border-black flex items-center justify-center text-4xl shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">�️</div>
<div><div class="text-sm uppercase font-black tracking-widest text-white/60">Mission Hub</div><div class="text-2xl font-black text-white font-draw">Orbital Flight Q1-26</div></div>
</div>
</div>
</div>
<div class="flex-none w-1/3 relative animate-float">
<div class="absolute -inset-4 bg-cyan-400 rounded-full blur-2xl opacity-40 animate-pulse"></div>
<img src="./assets/pm-character.png" class="w-full relative z-10 drop-shadow-2xl transform hover:scale-110 transition duration-500">
<div class="absolute -top-10 -right-10 bg-indigo-500 text-white px-6 py-3 rounded-full font-black text-sm uppercase tracking-widest border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] animate-pulse rotate-12">LIFT OFF!</div>
</div>
</div>
<div class="abs-br m-10 w-80 text-left animate-wiggle">
<div class="p-6 bg-white border-4 border-black rounded-[2rem] shadow-[10px_10px_0px_0px_rgba(0,0,0,1)]">
<div class="text-xs font-black uppercase tracking-widest text-indigo-600 mb-4 flex justify-between items-center"><span>PRIORITY FLIGHTS</span><div class="h-3 w-3 rounded-full bg-cyan-500 animate-ping border-2 border-black"></div></div>
<div class="space-y-3">
<div class="text-sm font-black text-black/80 flex items-center gap-2"><span class="bg-red-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-[10px] border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">1</span>Budget Interface</div>
<div class="text-sm font-black text-black/80 flex items-center gap-2"><span class="bg-blue-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-[10px] border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">2</span>Container Pods</div>
<div class="text-sm font-black text-black/80 flex items-center gap-2"><span class="bg-emerald-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-[10px] border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">3</span>HR Neural Lab</div>
</div>
</div>
</div>

---
layout: default
clicks: 1
---

<div class="flex justify-between items-start mb-6">
<div class="flex items-center gap-6">
<div class="text-7xl animate-float drop-shadow-lg">�</div>
<div><h1 class="text-5xl font-black text-white font-draw mb-1 stroke-black">Star Dash Dashboard</h1><p class="text-cyan-200 font-bold italic text-lg shadow-black">Tracking our flight path across the stars!</p></div>
</div>
<div class="bg-indigo-500 border-4 border-black px-4 py-2 rounded-xl text-white font-black uppercase tracking-tighter shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] -rotate-2">FLYING Q1-2026</div>
</div>
<div class="mt-4 overflow-hidden bg-white border-4 border-black rounded-[2.5rem] text-left p-2 shadow-[12px_12px_0px_0px_rgba(0,0,0,0.5)]">
<table class="w-full text-xs border-collapse">
<thead class="bg-indigo-50 uppercase font-black text-indigo-900 border-b-4 border-black">
<tr><th class="p-4 text-left">Vessel Name</th><th class="p-4 text-center">Fuel</th><th class="p-4 text-left">Objective</th><th class="p-4 text-left">Flight Progress</th><th class="p-4 text-center">Pilot</th><th class="p-4 text-right">State</th></tr>
</thead>
<tbody v-if="$clicks === 0" class="animate-fade-in font-draw">
<tr class="border-b-2 border-dashed border-gray-300 hover:bg-cyan-50 transition group">
<td class="p-4"><div class="flex items-center gap-3">🛰️ <div><div class="text-[10px] font-black opacity-30">BC</div><div class="font-black text-lg text-black">Budget Control</div></div></div></td>
<td class="p-4 text-center"><span class="px-3 py-1 bg-red-500 text-white text-[10px] font-black rounded-lg border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">P1</span></td>
<td class="p-4 text-black/60 font-bold italic">Gathering Data</td>
<td class="p-4"><div class="flex items-center gap-3"><div class="flex-grow bg-gray-200 h-6 rounded-full overflow-hidden border-2 border-black p-0.5"><div class="h-full bg-gradient-to-r from-cyan-400 to-indigo-500 rounded-full border-r-2 border-black" style="width: 20%"></div></div><span class="text-sm font-black text-black">20%</span></div></td>
<td class="p-4 text-center text-indigo-600 font-black">Panha</td>
<td class="p-4 text-right"><span class="px-4 py-2 text-[10px] font-black rounded-full uppercase bg-indigo-500 text-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">In Flight</span></td>
</tr>
<tr class="border-b-2 border-dashed border-gray-300 hover:bg-cyan-50 transition">
<td class="p-4"><div class="flex items-center gap-3">📦 <div><div class="text-[10px] font-black opacity-30">BC</div><div class="font-black text-lg text-black">Container Capacity</div></div></div></td>
<td class="p-4 text-center"><span class="px-3 py-1 bg-red-500 text-white text-[10px] font-black rounded-lg border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">P1</span></td>
<td class="p-4 text-black/60 font-bold italic">Mapping Pods</td>
<td class="p-4"><div class="flex items-center gap-3"><div class="flex-grow bg-gray-200 h-6 rounded-full overflow-hidden border-2 border-black p-0.5"><div class="h-full bg-gradient-to-r from-cyan-400 to-indigo-500 rounded-full border-r-2 border-black" style="width: 10%"></div></div><span class="text-sm font-black text-black">10%</span></div></td>
<td class="p-4 text-center text-indigo-600 font-black">Kanel</td>
<td class="p-4 text-right"><span class="px-4 py-2 text-[10px] font-black rounded-full uppercase bg-indigo-500 text-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">In Flight</span></td>
</tr>
<tr class="border-b-2 border-dashed border-gray-300 hover:bg-cyan-50 transition">
<td class="p-4"><div class="flex items-center gap-3">� <div><div class="text-[10px] font-black opacity-30">HR</div><div class="font-black text-lg text-black">HR Lab Web</div></div></div></td>
<td class="p-4 text-center"><span class="px-3 py-1 bg-blue-500 text-white text-[10px] font-black rounded-lg border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">P2</span></td>
<td class="p-4 text-black/60 font-bold italic">Interface Dev</td>
<td class="p-4"><div class="flex items-center gap-3"><div class="flex-grow bg-gray-200 h-6 rounded-full overflow-hidden border-2 border-black p-0.5"><div class="h-full bg-gradient-to-r from-blue-400 to-indigo-600 rounded-full border-r-2 border-black" style="width: 85%"></div></div><span class="text-sm font-black text-black">85%</span></div></td>
<td class="p-4 text-center text-indigo-600 font-black">Monika</td>
<td class="p-4 text-right"><span class="px-4 py-2 text-[10px] font-black rounded-full uppercase bg-emerald-500 text-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] animate-pulse">Docking</span></td>
</tr>
<tr class="hover:bg-cyan-50 transition">
<td class="p-4"><div class="flex items-center gap-3">📱 <div><div class="text-[10px] font-black opacity-30">HR</div><div class="font-black text-lg text-black">HR Lab Mobile</div></div></div></td>
<td class="p-4 text-center"><span class="px-3 py-1 bg-blue-500 text-white text-[10px] font-black rounded-lg border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">P2</span></td>
<td class="p-4 text-black/60 font-bold italic">Syncing APIs</td>
<td class="p-4"><div class="flex items-center gap-3"><div class="flex-grow bg-gray-200 h-6 rounded-full overflow-hidden border-2 border-black p-0.5"><div class="h-full bg-gradient-to-r from-blue-400 to-indigo-600 rounded-full border-r-2 border-black" style="width: 50%"></div></div><span class="text-sm font-black text-black">50%</span></div></td>
<td class="p-4 text-center text-indigo-600 font-black">Monika</td>
<td class="p-4 text-right"><span class="px-4 py-2 text-[10px] font-black rounded-full uppercase bg-emerald-500 text-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">Docking</span></td>
</tr>
</tbody>
</table>
</div>
<div class="mt-8 flex gap-8 text-left">
<div class="p-6 bg-indigo-600 border-4 border-black rounded-[2.5rem] flex items-center gap-8 flex-1 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"><div class="text-6xl font-black italic text-white font-draw">25%</div><div class="text-sm uppercase font-black leading-tight tracking-[0.1em] text-cyan-200">Flight XP<br>Reached</div></div>
<div class="p-6 bg-cyan-400 border-4 border-black rounded-[2.5rem] flex items-center gap-4 flex-1 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"><div class="w-8 h-8 rounded-full bg-white animate-ping border-2 border-black"></div><span class="text-lg font-black uppercase tracking-widest text-black/70 font-draw underline">Signals: Optimal</span></div>
</div>

---
layout: default
---

<div class="flex items-center gap-6 mb-8">
<div class="text-7xl animate-float drop-shadow-lg">�</div>
<div><h1 class="text-5xl font-black text-white font-draw stroke-black">Flight Navigation Log</h1><p class="text-cyan-200 font-bold italic text-lg opacity-80">Scanning our technical coordinates.</p></div>
</div>
<div class="mt-6 grid grid-cols-5 gap-8">
<div class="col-span-3 overflow-hidden bg-white border-4 border-black rounded-[3rem] p-6 text-left shadow-[15px_15px_0px_0px_rgba(0,0,0,0.4)]">
<table class="w-full text-xs">
<thead class="bg-indigo-50 opacity-80 uppercase font-black text-indigo-900 border-b-4 border-black font-draw">
<tr><th class="p-4">Pod</th><th class="p-4">Active Task</th><th class="p-4 text-center">Fuel %</th><th class="p-4 text-right">Pilot</th></tr>
</thead>
<tbody class="font-bold text-gray-800">
<tr class="border-b-2 border-dashed border-gray-200 hover:bg-cyan-50 transition"><td class="p-4 font-black">Budget Ctrl</td><td class="p-4 italic text-indigo-600">Simulating Currency</td><td class="p-4 text-center font-black text-orange-500 text-lg">30%</td><td class="p-4 text-right">Panha</td></tr>
<tr class="border-b-2 border-dashed border-gray-200 hover:bg-cyan-50 transition"><td class="p-4 font-black">Container</td><td class="p-4 italic text-indigo-600">Spatial Planning</td><td class="p-4 text-center font-black text-orange-500 text-lg">15%</td><td class="p-4 text-right">Kanel</td></tr>
<tr class="border-b-2 border-dashed border-gray-200 hover:bg-cyan-50 transition"><td class="p-4 font-black">HR Lab Web</td><td class="p-4 italic text-indigo-600">Logic Compilation</td><td class="p-4 text-center font-black text-orange-500 text-lg">85%</td><td class="p-4 text-right">Monika</td></tr>
<tr class="hover:bg-cyan-50 transition"><td class="p-4 font-black">HR Mobile</td><td class="p-4 italic text-indigo-600">Interface Weaving</td><td class="p-4 text-center font-black text-orange-500 text-lg">50%</td><td class="p-4 text-right">Monika</td></tr>
</tbody>
</table>
</div>
<div class="col-span-2 flex flex-col gap-6">
<div class="relative group rounded-[3rem] overflow-hidden border-4 border-black shadow-[10px_10px_0px_0px_rgba(0,0,0,0.3)]">
<img src="./assets/team-sketch.png" class="w-full h-48 object-cover opacity-90 group-hover:opacity-100 transition duration-500">
<div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent flex items-end p-6"><span class="text-sm font-black uppercase text-white tracking-widest italic font-draw">Our Brave Crew!</span></div>
</div>
<div class="bg-indigo-900/40 border-4 border-black rounded-[2rem] p-6 shadow-[10px_10px_0px_0px_rgba(0,0,0,1)] relative text-white">
<div class="absolute -top-4 -left-4 text-4xl animate-bounce">💬</div>
<div class="space-y-3 font-draw text-sm">
<div class="flex gap-2"><span class="text-orange-400 font-black">Panha:</span><span class="text-white/80 font-bold">"Coordinates locked!"</span></div>
<div class="flex gap-2"><span class="text-cyan-400 font-black">Monika:</span><span class="text-white/80 font-bold">"Engines at 85%!"</span></div>
<div class="flex gap-2"><span class="text-emerald-400 font-black">Commander:</span><span class="text-emerald-400 font-black italic">"Full speed ahead!"</span></div>
</div>
</div>
</div>
</div>

---
layout: default
---

<div class="flex items-center gap-6 mb-8">
<div class="text-7xl animate-shake drop-shadow-lg">�</div>
<div><h1 class="text-5xl font-black text-white font-draw stroke-black">Deep Space Hazards</h1><p class="text-cyan-200 font-bold italic text-lg opacity-80">Asteroids and interference detected!</p></div>
</div>
<div class="grid grid-cols-2 gap-10 mt-8">
<div class="p-8 bg-black/60 border-8 border-orange-500 rounded-[3rem] relative animate-float shadow-[20px_20px_0px_0px_rgba(249,115,22,0.3)]">
<div class="absolute -top-10 -right-6 text-8xl opacity-10 font-bold -rotate-12 text-orange-500">SIGNAL!</div>
<div class="flex items-center gap-6 mb-8"><div class="w-20 h-20 rounded-full bg-orange-600 border-4 border-black flex items-center justify-center text-4xl shadow-xl">⚠️</div><h3 class="text-4xl font-black uppercase text-white font-draw italic tracking-tighter stroke-orange-500">Interference</h3></div>
<ul class="text-lg space-y-6 font-bold text-white">
<li class="flex gap-6 p-6 bg-orange-500/10 rounded-[2.5rem] border-4 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]"><div class="text-4xl animate-bounce">📡</div><span class="font-draw uppercase leading-tight text-sm">Need <b>SIGNAL STABILITY</b> (Review) from Senior Pilots!</span></li>
<li class="flex gap-6 p-6 bg-orange-500/10 rounded-[2.5rem] border-4 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]"><div class="text-4xl animate-wiggle">🛸</div><span class="font-draw uppercase leading-tight text-sm">Need <b>DOMAIN EXPERTS</b> to verify our flight logic!</span></li>
</ul>
</div>
<div class="p-8 bg-black/60 border-8 border-cyan-400 rounded-[3rem] relative animate-bounce-in shadow-[20px_20px_0px_0px_rgba(34,211,238,0.3)]">
<div class="absolute -top-10 -left-6 text-8xl opacity-10 font-bold rotate-12 text-cyan-400">BOOST!</div>
<div class="flex items-center gap-6 mb-8"><div class="w-20 h-20 rounded-full bg-cyan-400 border-4 border-black flex items-center justify-center text-4xl shadow-xl text-black">�</div><h3 class="text-4xl font-black uppercase text-white font-draw italic tracking-tighter stroke-cyan-400">Energy Boost</h3></div>
<ul class="text-lg space-y-6 font-bold text-white">
<li class="flex gap-6 p-6 bg-cyan-400/10 rounded-[2.5rem] border-4 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]"><div class="text-4xl animate-float">🧭</div><span class="font-draw uppercase leading-tight text-sm">Target the <b>PRIMARY STAR</b> for this quarter!</span></li>
<li class="flex gap-6 p-6 bg-cyan-400/10 rounded-[2.5rem] border-4 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]"><div class="text-4xl animate-bounce">🔭</div><span class="font-draw uppercase leading-tight text-sm">Summon <b>2 SCOUTS</b> for a 1-week navigation raid!</span></li>
</ul>
</div>
</div>

---
layout: center
class: text-center
---

<div class="bg-indigo-600 border-[10px] border-black p-20 rounded-[4rem] shadow-[25px_25px_0px_0px_rgba(34,211,238,1)] transform hover:scale-105 transition-transform duration-700 animate-bounce-in">
<div class="text-[12rem] mb-12 animate-float filter drop-shadow-2xl">🚀</div>
<h1 class="text-8xl font-black text-white font-draw tracking-tighter mb-4 animate-pulse">MISSION SUCCESS!</h1>
<p class="text-3xl font-black text-cyan-300 tracking-[0.2em] uppercase font-draw italic">Infinite Space Awaits!</p>
<div class="mt-16 flex justify-center gap-16">
<div class="animate-bounce text-7xl" style="animation-delay: 0.1s">🛰️</div>
<div class="animate-bounce text-7xl" style="animation-delay: 0.3s">🛸</div>
<div class="animate-bounce text-7xl" style="animation-delay: 0.5s">�</div>
</div>
</div>

<style>
@import url('https://fonts.googleapis.com/css2?family=DynaPuff:wght@400;700;900&family=Outfit:wght@300;700;900&display=swap');
.font-draw { font-family: 'DynaPuff', cursive; }
body { font-family: 'Outfit', sans-serif; background-color: #0f172a; color: #f8fafc; }
.slidev-layout { background-size: cover !important; background-position: center !important; }
.stroke-black { -webkit-text-stroke: 3px black; }
.stroke-orange-500 { -webkit-text-stroke: 1.5px #f97316; }
.stroke-cyan-400 { -webkit-text-stroke: 1.5px #22d3ee; }
.animate-float { animation: float 4s ease-in-out infinite; }
.animate-wiggle { animation: wiggle 0.5s ease-in-out infinite; }
.animate-shake { animation: shake 2s ease-in-out infinite; }
.animate-bounce-in { animation: bounce-in 1s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
.animate-slide-in-left { animation: slide-in-left 0.8s cubic-bezier(0.23, 1, 0.32, 1) forwards; opacity: 0; }
@keyframes float { 0%, 100% { transform: translateY(0) rotate(0); } 50% { transform: translateY(-30px) rotate(2deg); } }
@keyframes wiggle { 0%, 100% { transform: rotate(-5deg); } 50% { transform: rotate(5deg); } }
@keyframes shake { 0%, 100% { transform: translate(0, 0); } 10%, 30%, 50%, 70%, 90% { transform: translate(-5px, 0); } 20%, 40%, 60%, 80% { transform: translate(5px, 0); } }
@keyframes bounce-in { 0% { transform: scale(0.3); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
@keyframes slide-in-left { 0% { transform: translateX(-150px) rotate(-10deg); opacity: 0; } 100% { transform: translateX(0) rotate(0); opacity: 1; } }
table th { font-family: 'DynaPuff', cursive; text-transform: uppercase; letter-spacing: 0.1em; }
.border-black { border-color: #000000 !important; }
</style>
