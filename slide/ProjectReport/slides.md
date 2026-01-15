---
theme: default
background: https://images.unsplash.com/photo-1500049222335-df47b1ddc5ee?auto=format&fit=crop&q=80&w=2000
class: text-center
highlighter: shiki
lineNumbers: true
drawings:
  persist: false
transition: slide-up
title: "Project Adventure 2026: The Big Update!"
mdc: true
---

<div class="h-full flex flex-row justify-center items-center gap-6 p-10">
<div class="flex-1 text-left">
<div class="bg-yellow-400 border-8 border-black rounded-[3rem] p-10 shadow-[15px_15px_0px_0px_rgba(33,33,33,1)] transform -rotate-2 hover:rotate-0 transition-transform duration-500 animate-bounce-in">
<h1 class="text-7xl font-black mb-4 tracking-tighter leading-none text-black font-draw">Hello, Team! <span class="inline-block animate-wiggle">✨</span></h1>
<h2 class="text-3xl font-bold text-black/70 font-draw uppercase">Our Epic Q1 Journey</h2>
</div>
<div class="mt-12 space-y-6">
<div class="flex items-center gap-6 animate-slide-in-left" style="animation-delay: 0.2s">
<div class="w-16 h-16 rounded-2xl bg-orange-500 border-4 border-black flex items-center justify-center text-4xl shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">🦸‍♂️</div>
<div><div class="text-sm uppercase font-black tracking-widest text-black/60">Lead Hero</div><div class="text-2xl font-black text-black font-draw">TC | Master Navigator</div></div>
</div>
<div class="flex items-center gap-6 animate-slide-in-left" style="animation-delay: 0.4s">
<div class="w-16 h-16 rounded-2xl bg-blue-400 border-4 border-black flex items-center justify-center text-4xl shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">🚀</div>
<div><div class="text-sm uppercase font-black tracking-widest text-black/60">Mission Hub</div><div class="text-2xl font-black text-black font-draw">Quarterly Quest Q1-26</div></div>
</div>
</div>
</div>
<div class="flex-none w-1/3 relative animate-float">
<div class="absolute -inset-4 bg-white rounded-full blur-2xl opacity-40"></div>
<img src="./assets/pm-character.png" class="w-full relative z-10 drop-shadow-2xl transform hover:scale-110 transition duration-500">
<div class="absolute -top-10 -right-10 bg-yellow-400 text-black px-6 py-3 rounded-full font-black text-sm uppercase tracking-widest border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] animate-pulse rotate-12">Let's Go!</div>
</div>
</div>
<div class="abs-br m-10 w-80 text-left animate-wiggle">
<div class="p-6 bg-white border-4 border-black rounded-[2rem] shadow-[10px_10px_0px_0px_rgba(0,0,0,1)]">
<div class="text-xs font-black uppercase tracking-widest text-orange-600 mb-4 flex justify-between items-center"><span>TOP MISSIONS</span><div class="h-3 w-3 rounded-full bg-red-500 animate-ping border-2 border-black"></div></div>
<div class="space-y-3">
<div class="text-sm font-black text-black/80 flex items-center gap-2"><span class="bg-red-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-[10px] border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">1</span>Budget Matrix</div>
<div class="text-sm font-black text-black/80 flex items-center gap-2"><span class="bg-blue-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-[10px] border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">2</span>Container Quest</div>
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
<div class="text-7xl animate-bounce drop-shadow-lg">🗺️</div>
<div><h1 class="text-5xl font-black text-black font-draw mb-1 stroke-white">Our Mission Map</h1><p class="text-black/60 font-bold italic text-lg">Tracking our progress across the kingdom!</p></div>
</div>
<div class="bg-orange-500 border-4 border-black px-4 py-2 rounded-xl text-white font-black uppercase tracking-tighter shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] -rotate-2">Q1 2026 Live</div>
</div>
<div class="mt-4 overflow-hidden bg-white border-4 border-black rounded-[2.5rem] text-left p-2 shadow-[12px_12px_0px_0px_rgba(0,0,0,0.15)]">
<table class="w-full text-xs border-collapse">
<thead class="bg-blue-50 uppercase font-black text-blue-900 border-b-4 border-black">
<tr><th class="p-4 text-left">Level Name</th><th class="p-4 text-center">Pri</th><th class="p-4 text-left">The Goal</th><th class="p-4 text-left">XP Progress</th><th class="p-4 text-center">Hero</th><th class="p-4 text-right">Status</th></tr>
</thead>
<tbody v-if="$clicks === 0" class="animate-fade-in font-draw">
<tr class="border-b-2 border-dashed border-gray-300 hover:bg-yellow-50 transition group">
<td class="p-4"><div class="flex items-center gap-3">🎯 <div><div class="text-[10px] font-black opacity-30">BC</div><div class="font-black text-lg text-black">Budget Control</div></div></div></td>
<td class="p-4 text-center"><span class="px-3 py-1 bg-red-500 text-white text-[10px] font-black rounded-lg border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">P1</span></td>
<td class="p-4 text-black/60 font-bold italic">Gathering Scrolls</td>
<td class="p-4"><div class="flex items-center gap-3"><div class="flex-grow bg-gray-200 h-6 rounded-full overflow-hidden border-2 border-black p-0.5"><div class="h-full bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full border-r-2 border-black" style="width: 20%"></div></div><span class="text-sm font-black text-black">20%</span></div></td>
<td class="p-4 text-center text-blue-600 font-black">Panha</td>
<td class="p-4 text-right"><span class="px-4 py-2 text-[10px] font-black rounded-full uppercase bg-blue-500 text-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">Adventuring</span></td>
</tr>
<tr class="border-b-2 border-dashed border-gray-300 hover:bg-yellow-50 transition">
<td class="p-4"><div class="flex items-center gap-3">📦 <div><div class="text-[10px] font-black opacity-30">BC</div><div class="font-black text-lg text-black">Container Capacity</div></div></div></td>
<td class="p-4 text-center"><span class="px-3 py-1 bg-red-500 text-white text-[10px] font-black rounded-lg border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">P1</span></td>
<td class="p-4 text-black/60 font-bold italic">Analyzing Gaps</td>
<td class="p-4"><div class="flex items-center gap-3"><div class="flex-grow bg-gray-200 h-6 rounded-full overflow-hidden border-2 border-black p-0.5"><div class="h-full bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full border-r-2 border-black" style="width: 10%"></div></div><span class="text-sm font-black text-black">10%</span></div></td>
<td class="p-4 text-center text-blue-600 font-black">Kanel</td>
<td class="p-4 text-right"><span class="px-4 py-2 text-[10px] font-black rounded-full uppercase bg-blue-500 text-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">Adventuring</span></td>
</tr>
<tr class="border-b-2 border-dashed border-gray-300 hover:bg-yellow-50 transition">
<td class="p-4"><div class="flex items-center gap-3">🧪 <div><div class="text-[10px] font-black opacity-30">HR</div><div class="font-black text-lg text-black">HR Lab Web</div></div></div></td>
<td class="p-4 text-center"><span class="px-3 py-1 bg-blue-500 text-white text-[10px] font-black rounded-lg border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">P2</span></td>
<td class="p-4 text-black/60 font-bold italic">Building the Base</td>
<td class="p-4"><div class="flex items-center gap-3"><div class="flex-grow bg-gray-200 h-6 rounded-full overflow-hidden border-2 border-black p-0.5"><div class="h-full bg-gradient-to-r from-blue-400 to-indigo-600 rounded-full border-r-2 border-black" style="width: 85%"></div></div><span class="text-sm font-black text-black">85%</span></div></td>
<td class="p-4 text-center text-blue-600 font-black">Monika</td>
<td class="p-4 text-right"><span class="px-4 py-2 text-[10px] font-black rounded-full uppercase bg-emerald-500 text-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] animate-pulse">Boss Battle</span></td>
</tr>
<tr class="hover:bg-yellow-50 transition">
<td class="p-4"><div class="flex items-center gap-3">📱 <div><div class="text-[10px] font-black opacity-30">HR</div><div class="font-black text-lg text-black">HR Lab Mobile</div></div></div></td>
<td class="p-4 text-center"><span class="px-3 py-1 bg-blue-500 text-white text-[10px] font-black rounded-lg border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">P2</span></td>
<td class="p-4 text-black/60 font-bold italic">Hooking up APIs</td>
<td class="p-4"><div class="flex items-center gap-3"><div class="flex-grow bg-gray-200 h-6 rounded-full overflow-hidden border-2 border-black p-0.5"><div class="h-full bg-gradient-to-r from-blue-400 to-indigo-600 rounded-full border-r-2 border-black" style="width: 50%"></div></div><span class="text-sm font-black text-black">50%</span></div></td>
<td class="p-4 text-center text-blue-600 font-black">Monika</td>
<td class="p-4 text-right"><span class="px-4 py-2 text-[10px] font-black rounded-full uppercase bg-emerald-500 text-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">Battling</span></td>
</tr>
</tbody>
<tbody v-if="$clicks === 1" class="animate-fade-in font-draw">
<tr class="border-b-2 border-dashed border-gray-300 hover:bg-yellow-50 transition">
<td class="p-4"><div class="flex items-center gap-3">🍔 <div><div class="text-[10px] font-black opacity-30">Retail</div><div class="font-black text-lg text-black">NGPOS (F&B)</div></div></div></td>
<td class="p-4 text-center"><span class="px-3 py-1 bg-cyan-500 text-white text-[10px] font-black rounded-lg border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">P3</span></td>
<td class="p-4 text-black/60 font-bold italic">Drawing the Screens</td>
<td class="p-4"><div class="flex items-center gap-3"><div class="flex-grow bg-gray-200 h-6 rounded-full overflow-hidden border-2 border-black p-0.5"><div class="h-full bg-cyan-400 rounded-full border-r-2 border-black" style="width: 30%"></div></div><span class="text-sm font-black text-black">30%</span></div></td>
<td class="p-4 text-center text-blue-600 font-black">Marchi</td>
<td class="p-4 text-right"><span class="px-4 py-2 text-[10px] font-black rounded-full uppercase bg-blue-500 text-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">Adventuring</span></td>
</tr>
<tr class="border-b-2 border-dashed border-gray-300 hover:bg-yellow-50 transition">
<td class="p-4"><div class="flex items-center gap-3">🎯 <div><div class="text-[10px] font-black opacity-30">CRM</div><div class="font-black text-lg text-black">Bullseye</div></div></div></td>
<td class="p-4 text-center"><span class="px-3 py-1 bg-gray-300 text-black text-[10px] font-black rounded-lg border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">P4</span></td>
<td class="p-4 text-black/60 font-bold italic">Planning the Route</td>
<td class="p-4"><div class="flex items-center gap-3"><div class="flex-grow bg-gray-200 h-6 rounded-full overflow-hidden border-2 border-black p-0.5"><div class="h-full bg-gray-400 rounded-full border-r-2 border-black" style="width: 5%"></div></div><span class="text-sm font-black text-black">5%</span></div></td>
<td class="p-4 text-center text-gray-500 font-black">CRM Team</td>
<td class="p-4 text-right"><span class="px-4 py-2 text-[10px] font-black rounded-full uppercase bg-gray-200 text-gray-500 border-2 border-black dashed">Resting</span></td>
</tr>
<tr class="hover:bg-yellow-50 transition">
<td class="p-4"><div class="flex items-center gap-3">💰 <div><div class="text-[10px] font-black opacity-30">Quick</div><div class="font-black text-lg text-black">CryptoTrading</div></div></div></td>
<td class="p-4 text-center"><span class="px-3 py-1 bg-gray-300 text-black text-[10px] font-black rounded-lg border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">P4</span></td>
<td class="p-4 text-black/60 font-bold italic">Studying the Map</td>
<td class="p-4"><div class="flex items-center gap-3"><div class="flex-grow bg-gray-200 h-6 rounded-full overflow-hidden border-2 border-black p-0.5"><div class="h-full bg-gray-400 rounded-full border-r-2 border-black" style="width: 0%"></div></div><span class="text-sm font-black text-black">0%</span></div></td>
<td class="p-4 text-center text-gray-500 font-black">Gordon</td>
<td class="p-4 text-right"><span class="px-4 py-2 text-[10px] font-black rounded-full uppercase bg-gray-200 text-gray-500 border-2 border-black">Resting</span></td>
</tr>
</tbody>
</table>
</div>
<div class="mt-8 flex gap-8 text-left">
<div class="p-6 bg-orange-500 border-4 border-black rounded-[2.5rem] flex items-center gap-8 flex-1 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"><div class="text-6xl font-black italic text-white font-draw">25%</div><div class="text-sm uppercase font-black leading-tight tracking-[0.1em] text-white">Adventure XP<br>Collected</div></div>
<div class="p-6 bg-yellow-400 border-4 border-black rounded-[2.5rem] flex items-center gap-4 flex-1 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"><div class="w-8 h-8 rounded-full bg-green-500 animate-ping border-2 border-black"></div><span class="text-lg font-black uppercase tracking-widest text-black/70 font-draw underline">All Systems GO!</span></div>
</div>

---
layout: default
---

<div class="flex items-center gap-6 mb-8">
<div class="text-7xl animate-float drop-shadow-lg">🕵️‍♂️</div>
<div><h1 class="text-5xl font-black text-black font-draw stroke-white">The Quest Log</h1><p class="text-black/60 font-bold italic text-lg opacity-80">A closer look at our heroic deeds.</p></div>
</div>
<div class="mt-6 grid grid-cols-5 gap-8">
<div class="col-span-3 overflow-hidden bg-white border-4 border-black rounded-[3rem] p-6 text-left shadow-[15px_15px_0px_0px_rgba(0,0,0,0.1)]">
<table class="w-full text-xs">
<thead class="bg-blue-50 opacity-80 uppercase font-black text-blue-900 border-b-4 border-black font-draw">
<tr><th class="p-4">Level</th><th class="p-4">Current Task</th><th class="p-4 text-center">XP %</th><th class="p-4 text-right">Hero</th></tr>
</thead>
<tbody class="font-bold text-gray-800">
<tr class="border-b-2 border-dashed border-gray-200 hover:bg-blue-50 transition"><td class="p-4 font-black">Budget Ctrl</td><td class="p-4 italic text-blue-600">Checking the Treasures</td><td class="p-4 text-center font-black text-orange-500 text-lg">30%</td><td class="p-4 text-right">Panha</td></tr>
<tr class="border-b-2 border-dashed border-gray-200 hover:bg-blue-50 transition"><td class="p-4 font-black">Container</td><td class="p-4 italic text-blue-600">Measuring the Chests</td><td class="p-4 text-center font-black text-orange-500 text-lg">15%</td><td class="p-4 text-right">Kanel</td></tr>
<tr class="border-b-2 border-dashed border-gray-200 hover:bg-blue-50 transition"><td class="p-4 font-black">HR Lab Web</td><td class="p-4 italic text-blue-600">Building the Lab</td><td class="p-4 text-center font-black text-orange-500 text-lg">85%</td><td class="p-4 text-right">Monika</td></tr>
<tr class="hover:bg-blue-50 transition"><td class="p-4 font-black">HR Mobile</td><td class="p-4 italic text-blue-600">Making the App Magic</td><td class="p-4 text-center font-black text-orange-500 text-lg">50%</td><td class="p-4 text-right">Monika</td></tr>
</tbody>
</table>
</div>
<div class="col-span-2 flex flex-col gap-6">
<div class="relative group rounded-[3rem] overflow-hidden border-4 border-black shadow-[10px_10px_0px_0px_rgba(0,0,0,0.15)]">
<img src="./assets/team-sketch.png" class="w-full h-48 object-cover transform scale-110 group-hover:scale-125 transition duration-700 opacity-90 group-hover:opacity-100">
<div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent flex items-end p-6"><span class="text-sm font-black uppercase text-white tracking-widest italic font-draw">Our Brave Team!</span></div>
</div>
<div class="bg-white border-4 border-black rounded-[2rem] p-6 shadow-[10px_10px_0px_0px_rgba(0,0,0,1)] relative">
<div class="absolute -top-4 -left-4 text-4xl transform -rotate-12 drop-shadow-md">💬</div>
<div class="space-y-3 font-draw text-sm">
<div class="flex gap-2"><span class="text-orange-600 font-black">Panha:</span><span class="text-black/80 font-bold">"Almost found the golden ratio!"</span></div>
<div class="flex gap-2"><span class="text-blue-600 font-black">Monika:</span><span class="text-black/80 font-bold">"Lab is looking super cool!"</span></div>
<div class="flex gap-2"><span class="text-emerald-600 font-black">TC:</span><span class="text-emerald-600 font-black italic">"Great job! Keep going!"</span></div>
</div>
</div>
</div>
</div>

---
layout: default
---

<div class="flex items-center gap-6 mb-8">
<div class="text-7xl animate-shake drop-shadow-lg">🐉</div>
<div><h1 class="text-5xl font-black text-black font-draw stroke-white">Monster Watch</h1><p class="text-black/60 font-bold italic text-lg opacity-80">Beware of the tricky path ahead!</p></div>
</div>
<div class="grid grid-cols-2 gap-10 mt-8">
<div class="p-8 bg-white border-8 border-red-500 rounded-[3rem] relative animate-float shadow-[20px_20px_0px_0px_rgba(239,68,68,0.3)]">
<div class="absolute -top-10 -right-6 text-8xl opacity-10 font-bold -rotate-12">HELP!</div>
<div class="flex items-center gap-6 mb-8"><div class="w-20 h-20 rounded-full bg-red-600 border-4 border-black flex items-center justify-center text-4xl shadow-xl">👿</div><h3 class="text-4xl font-black uppercase text-black font-draw italic tracking-tighter stroke-red-500">Big Monsters</h3></div>
<ul class="text-lg space-y-6 font-bold text-black">
<li class="flex gap-6 p-6 bg-red-100 rounded-[2.5rem] border-4 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]"><div class="text-4xl animate-bounce">🆘</div><span class="font-draw uppercase leading-tight">Need <b>SENIOR WISDOM</b> to review the apprentice spells!</span></li>
<li class="flex gap-6 p-6 bg-red-100 rounded-[2.5rem] border-4 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]"><div class="text-4xl animate-wiggle">🧐</div><span class="font-draw uppercase leading-tight">Need <b>DOMAIN PROS</b> to test our magic potions!</span></li>
</ul>
</div>
<div class="p-8 bg-white border-8 border-blue-400 rounded-[3rem] relative animate-bounce-in shadow-[20px_20px_0px_0px_rgba(96,165,250,0.3)]">
<div class="absolute -top-10 -left-6 text-8xl opacity-10 font-bold rotate-12 text-blue-400">BUFF!</div>
<div class="flex items-center gap-6 mb-8"><div class="w-20 h-20 rounded-full bg-blue-400 border-4 border-black flex items-center justify-center text-4xl shadow-xl text-black">🛡️</div><h3 class="text-4xl font-black uppercase text-black font-draw italic tracking-tighter stroke-blue-400">Hero Buffs</h3></div>
<ul class="text-lg space-y-6 font-bold text-black">
<li class="flex gap-6 p-6 bg-blue-100 rounded-[2.5rem] border-4 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]"><div class="text-4xl animate-float">🧭</div><span class="font-draw uppercase leading-tight">Pick the <b>MAIN QUEST</b> for the final battle!</span></li>
<li class="flex gap-6 p-6 bg-blue-100 rounded-[2.5rem] border-4 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]"><div class="text-4xl animate-bounce">⚔️</div><span class="font-draw uppercase leading-tight">Summon <b>2 CHAMPIONS</b> for a 1-week testing raid!</span></li>
</ul>
</div>
</div>

---
layout: center
class: text-center
---

<div class="bg-white border-[10px] border-black p-20 rounded-[4rem] shadow-[25px_25px_0px_0px_rgba(251,191,36,1)] transform hover:scale-105 transition-transform duration-700 animate-bounce-in">
<div class="text-[12rem] mb-12 animate-float filter drop-shadow-2xl">🏆</div>
<h1 class="text-8xl font-black text-black font-draw tracking-tighter mb-4 animate-pulse">QUEST COMPLETE!</h1>
<p class="text-3xl font-black text-orange-600 tracking-[0.2em] uppercase font-draw italic">Level Up Incoming!</p>
<div class="mt-16 flex justify-center gap-16">
<div class="animate-bounce text-7xl" style="animation-delay: 0.1s">🌟</div>
<div class="animate-bounce text-7xl" style="animation-delay: 0.3s">🎉</div>
<div class="animate-bounce text-7xl" style="animation-delay: 0.5s">🔥</div>
</div>
</div>

<style>
@import url('https://fonts.googleapis.com/css2?family=DynaPuff:wght@400;700;900&family=Outfit:wght@300;700;900&display=swap');
.font-draw { font-family: 'DynaPuff', cursive; }
body { font-family: 'Outfit', sans-serif; background-color: #fffbeb; color: #1f2937; }
.slidev-layout { background-size: cover !important; background-position: center !important; }
.stroke-white { -webkit-text-stroke: 4px white; }
.stroke-red-500 { -webkit-text-stroke: 1.5px #ef4444; }
.stroke-blue-400 { -webkit-text-stroke: 1.5px #60a5fa; }
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
