---
theme: default
class: text-center
highlighter: shiki
lineNumbers: true
drawings:
  persist: false
transition: slide-up
title: "HR Lab Status Report"
mdc: true
---

<div class="h-full flex flex-col justify-center items-center p-4 relative">
<div class="max-w-5xl w-full z-10 space-y-4">
<!-- Main Title Card - Compact -->
<div class="bg-gradient-to-r from-amber-300 via-amber-400 to-yellow-500 border-4 border-black rounded-[1.5rem] p-6 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] animate-bounce-in flex justify-between items-center text-left">
<div>
<h1 class="text-5xl font-black text-black font-draw leading-none stroke-white">HR Lab Status 🚀</h1>
<div class="text-sm font-black uppercase tracking-widest mt-1 text-black">Business & Shareholder Update</div>
</div>
<div class="bg-black text-white px-4 py-2 rounded-lg transform rotate-2">
<h2 class="text-lg font-black font-draw">Jan 2026</h2>
</div>
</div>

<!-- Content Grid -->
<div class="grid grid-cols-2 gap-4">

<!-- Left Column: Metrics -->
<div class="space-y-4">
<!-- Progress Card -->
<div class="bg-gradient-to-br from-pink-400 to-pink-600 border-4 border-black rounded-xl p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex items-center gap-4 animate-slide-in-left" style="animation-delay: 0.1s">
<div class="text-4xl bg-white/20 w-12 h-12 flex items-center justify-center rounded-full border-2 border-black">📊</div>
<div>
<div class="text-[10px] uppercase font-black text-white tracking-widest">Overall Progress</div>
<div class="text-3xl font-black text-white font-draw leading-none">85% <span class="text-lg">Complete</span></div>
</div>
</div>

<!-- Launch Target -->
<div class="bg-gradient-to-br from-rose-400 to-rose-600 border-4 border-black rounded-xl p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex items-center gap-4 animate-slide-in-left" style="animation-delay: 0.2s">
<div class="text-4xl bg-white/20 w-12 h-12 flex items-center justify-center rounded-full border-2 border-black">🎯</div>
<div>
<div class="text-[10px] uppercase font-black text-white tracking-widest">Target Launch</div>
<div class="text-2xl font-black text-white font-draw leading-none">Q1 2026</div>
</div>
</div>
</div>

<!-- Right Column: Summary Context -->
<div class="bg-white border-4 border-black rounded-[1.5rem] p-5 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] animate-bounce-in flex flex-col justify-center h-full" style="animation-delay: 0.3s">
<div class="mb-3">
<span class="bg-gray-100 border-2 border-black px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest">Primary Customer</span>
<div class="font-black text-xl mt-1">NGD/NGT Group</div>
<div class="text-xs font-bold text-gray-500">Distribution / Consultant Service</div>
</div>
<div class="border-t-2 border-dashed border-gray-200 pt-3">
<span class="bg-gray-100 border-2 border-black px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest">Platform Goal</span>
<p class="font-bold text-sm text-gray-700 leading-tight mt-1">
Cloud-based HR platform specialized for large-scale manufacturing & construction workforces.
</p>
</div>
</div>

</div>
</div>
</div>

---
layout: default
---

<div class="h-full flex flex-col p-4">
<!-- Header -->
<div class="flex justify-between items-end mb-4 border-b-4 border-black pb-4">
<div>
<h1 class="text-5xl font-black text-black font-draw stroke-white mb-2">Progress Overview (1/2)</h1>
<p class="text-lg font-bold text-gray-600 italic">Completed Modules & Features</p>
</div>
<div class="bg-green-500 text-white border-4 border-black px-4 py-2 rounded-xl shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
<div class="text-xs font-black uppercase">Ready</div>
<div class="text-2xl font-black font-draw">12 Modules</div>
</div>
</div>

<!-- Ready Modules Grid -->
<div class="h-full flex flex-col justify-center">
<h3 class="font-black text-2xl font-draw text-green-600 flex items-center gap-2 mb-6">
<span class="bg-green-100 border-2 border-green-600 rounded-full w-8 h-8 flex items-center justify-center text-sm">✓</span> 
What's Ready Now
</h3>

<div class="grid grid-cols-3 gap-4">
<div class="bg-white border-2 border-black rounded-xl p-4 shadow-[3px_3px_0px_0px_rgba(0,0,0,0.1)] hover:scale-105 transition-transform flex items-center gap-3" v-for="item in ['Company Mgmt', 'User Access', 'ID Cards', 'Leave Mgmt', 'Billing', 'Activity Logs', 'Approvals', 'Locations', 'Employees', 'Projects', 'Procurement', 'Schedule Mgmt']" :key="item">
<div class="w-4 h-4 rounded-full bg-green-500 border-2 border-black flex-shrink-0"></div>
<span class="font-bold text-lg leading-tight">{{ item }}</span>
</div>
</div>
</div>
</div>

---
layout: default
---

<div class="h-full flex flex-col p-4">
<!-- Header -->
<div class="flex justify-between items-end mb-4 border-b-4 border-black pb-4">
<div>
<h1 class="text-5xl font-black text-black font-draw stroke-white mb-2">Progress Overview (2/2)</h1>
<p class="text-lg font-bold text-gray-600 italic">Active Development & Targets</p>
</div>
<div class="bg-yellow-400 text-black border-4 border-black px-4 py-2 rounded-xl shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
<div class="text-xs font-black uppercase">In Dev</div>
<div class="text-2xl font-black font-draw">8 Modules</div>
</div>
</div>

<!-- In Progress Content -->
<div class="h-full flex flex-col justify-center">
<h3 class="font-black text-2xl font-draw text-orange-600 flex items-center gap-2 mb-6">
<span class="bg-orange-100 border-2 border-orange-600 rounded-full w-8 h-8 flex items-center justify-center text-sm">⚙️</span>
In Progress
</h3>

<div class="bg-white border-4 border-black rounded-[2rem] overflow-hidden shadow-[8px_8px_0px_0px_rgba(0,0,0,0.1)]">
<table class="w-full text-base">
<thead class="bg-gray-100 border-b-2 border-black font-black uppercase text-gray-700">
<tr><th class="p-4 text-left">Feature</th><th class="p-4 text-center">Completion</th><th class="p-4 text-right">Target Date</th></tr>
</thead>
<tbody>
<tr class="border-b border-gray-200 hover:bg-orange-50 transition-colors">
<td class="p-4 font-bold text-lg">Payroll Processing<br><span class="text-xs text-red-500 font-black uppercase border border-red-500 px-1 rounded bg-red-50">Critical</span></td>
<td class="p-4 text-center"><div class="inline-block bg-orange-100 text-orange-600 px-3 py-1 rounded-lg font-black border border-orange-200">80%</div></td>
<td class="p-4 text-right font-mono text-gray-600 font-bold">Feb 2026</td>
</tr>
<tr class="border-b border-gray-200 hover:bg-orange-50 transition-colors">
<td class="p-4 font-bold text-lg">Time & Attendance<br><span class="text-xs text-red-500 font-black uppercase border border-red-500 px-1 rounded bg-red-50">Critical</span></td>
<td class="p-4 text-center"><div class="inline-block bg-orange-100 text-orange-600 px-3 py-1 rounded-lg font-black border border-orange-200">75%</div></td>
<td class="p-4 text-right font-mono text-gray-600 font-bold">Feb 2026</td>
</tr>
<tr class="border-b border-gray-200 hover:bg-yellow-50 transition-colors">
<td class="p-4 font-bold text-lg">Overtime Management</td>
<td class="p-4 text-center"><div class="inline-block bg-yellow-100 text-yellow-600 px-3 py-1 rounded-lg font-black border border-yellow-200">75%</div></td>
<td class="p-4 text-right font-mono text-gray-600 font-bold">Feb 2026</td>
</tr>
<tr class="hover:bg-yellow-50 transition-colors">
<td class="p-4 font-bold text-lg">Reports & Dashboards</td>
<td class="p-4 text-center"><div class="inline-block bg-yellow-100 text-yellow-600 px-3 py-1 rounded-lg font-black border border-yellow-200">60%</div></td>
<td class="p-4 text-right font-mono text-gray-600 font-bold">Mar 2026</td>
</tr>
</tbody>
</table>
</div>
</div>
</div>

---
layout: default
---

<div class="h-full flex flex-col p-4">
<!-- Header -->
<div class="flex justify-between items-end mb-4 border-b-4 border-black pb-4">
<div>
<h1 class="text-5xl font-black text-black font-draw stroke-white mb-2">Resource Request 🆘</h1>
</div>
<div class="bg-red-500 text-white border-4 border-black px-4 py-2 rounded-xl shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
<div class="text-xs font-black uppercase">Priority</div>
<div class="text-2xl font-black font-draw">High</div>
</div>
</div>

<div class="grid grid-cols-5 gap-6 h-full">

<!-- Left: Needs (3 cols) -->
<div class="col-span-3 space-y-4">
<h3 class="font-black text-xl font-draw text-black flex items-center gap-2">
<span class="bg-black text-white rounded-full w-8 h-8 flex items-center justify-center text-sm">1</span> 
Immediate Team Needs
</h3>

<div class="bg-white border-4 border-black rounded-2xl p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex items-center gap-4 hover:translate-x-1 transition-transform">
<div class="text-3xl bg-red-100 w-12 h-12 flex items-center justify-center rounded-xl border-2 border-black">🧪</div>
<div class="flex-grow">
<div class="font-black text-lg">QA Testers (2-3)</div>
<div class="text-xs font-bold text-gray-500">End-to-end testing execution</div>
</div>
</div>

<div class="bg-white border-4 border-black rounded-2xl p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex items-center gap-4 hover:translate-x-1 transition-transform">
<div class="text-3xl bg-orange-100 w-12 h-12 flex items-center justify-center rounded-xl border-2 border-black">📋</div>
<div class="flex-grow">
<div class="font-black text-lg">Business Analyst</div>
<div class="text-xs font-bold text-gray-500">Verify workflows vs MEC reqs</div>
</div>
</div>

<div class="bg-white border-4 border-black rounded-2xl p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex items-center gap-4 hover:translate-x-1 transition-transform">
<div class="text-3xl bg-blue-100 w-12 h-12 flex items-center justify-center rounded-xl border-2 border-black">👥</div>
<div class="flex-grow">
<div class="font-black text-lg">UAT Users</div>
<div class="text-xs font-bold text-gray-500">Real-world scenario validation</div>
</div>
</div>
</div>

<!-- Right: Context (2 cols) -->
<div class="col-span-2 flex flex-col gap-4">
<!-- Risk Card -->
<div class="bg-yellow-400 border-4 border-black rounded-2xl p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex-grow">
<h4 class="font-black text-lg mb-2 border-b-2 border-black pb-1">⚠️ The Risk</h4>
<p class="font-bold text-sm leading-tight">
"Without testing resources, we risk launching with undetected issues impacting daily operations."
</p>
</div>

<!-- Priorities Card -->
<div class="bg-white border-4 border-black rounded-2xl p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex-grow">
<h4 class="font-black text-lg mb-2 border-b-2 border-gray-200 pb-1">🎯 Priorities</h4>
<ul class="space-y-2">
<li class="flex items-center gap-2 font-bold text-sm"><span class="w-2 h-2 bg-red-500 rounded-full border border-black"></span>Payroll Calc</li>
<li class="flex items-center gap-2 font-bold text-sm"><span class="w-2 h-2 bg-orange-500 rounded-full border border-black"></span>Attendance Flow</li>
<li class="flex items-center gap-2 font-bold text-sm"><span class="w-2 h-2 bg-blue-500 rounded-full border border-black"></span>Approvals</li>
</ul>
</div>
</div>

</div>
</div>

---
layout: center
class: text-center
---

<div class="h-full flex flex-col justify-center items-center p-4">
<!-- Main Card -->
<div class="bg-white border-[6px] border-black rounded-[2.5rem] p-10 shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] w-full max-w-4xl relative">
<!-- Decoration -->
<div class="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-black text-white px-6 py-2 rounded-xl rotate-1 shadow-[4px_4px_0px_0px_rgba(255,255,255,0)] border-2 border-white">
<span class="font-black uppercase tracking-[0.2em] text-sm">Next Quarter</span>
</div>

<h1 class="text-6xl font-black text-black font-draw mb-8 mt-4">Q1 2026 Priorities 🏁</h1>

<div class="grid grid-cols-2 gap-4 text-left">
<div class="bg-gray-50 border-2 border-black p-4 rounded-xl flex items-center gap-4 hover:scale-105 transition-transform cursor-default group">
<span class="bg-black text-white w-10 h-10 flex items-center justify-center rounded-xl font-black text-xl border-2 border-transparent group-hover:border-black group-hover:bg-white group-hover:text-black transition-colors">1</span>
<div>
<div class="font-black text-lg leading-none">Payroll System</div>
<div class="text-xs font-bold text-gray-500 mt-1">Complete salaries & slips</div>
</div>
</div>

<div class="bg-gray-50 border-2 border-black p-4 rounded-xl flex items-center gap-4 hover:scale-105 transition-transform cursor-default group">
<span class="bg-black text-white w-10 h-10 flex items-center justify-center rounded-xl font-black text-xl border-2 border-transparent group-hover:border-black group-hover:bg-white group-hover:text-black transition-colors">2</span>
<div>
<div class="font-black text-lg leading-none">Attendance</div>
<div class="text-xs font-bold text-gray-500 mt-1">Finish module & device logic</div>
</div>
</div>

<div class="bg-gray-50 border-2 border-black p-4 rounded-xl flex items-center gap-4 hover:scale-105 transition-transform cursor-default group">
<span class="bg-black text-white w-10 h-10 flex items-center justify-center rounded-xl font-black text-xl border-2 border-transparent group-hover:border-black group-hover:bg-white group-hover:text-black transition-colors">3</span>
<div>
<div class="font-black text-lg leading-none">MEC Reqs</div>
<div class="text-xs font-bold text-gray-500 mt-1">Finalize all specific needs</div>
</div>
</div>

<div class="bg-gray-50 border-2 border-black p-4 rounded-xl flex items-center gap-4 hover:scale-105 transition-transform cursor-default group">
<span class="bg-black text-white w-10 h-10 flex items-center justify-center rounded-xl font-black text-xl border-2 border-transparent group-hover:border-black group-hover:bg-white group-hover:text-black transition-colors">4</span>
<div>
<div class="font-black text-lg leading-none">Go-Live Prep</div>
<div class="text-xs font-bold text-gray-500 mt-1">Deployment readiness</div>
</div>
</div>
</div>

<div class="mt-8 flex items-center justify-center gap-2 opacity-50">
<span class="text-2xl">📅</span>
<span class="font-black text-sm uppercase tracking-widest">Next Update: February 2026</span>
</div>
</div>
</div>

<style>
@import url('https://fonts.googleapis.com/css2?family=DynaPuff:wght@400;700;900&family=Outfit:wght@300;700;900&display=swap');

.font-draw { font-family: 'DynaPuff', cursive; }
body { font-family: 'Outfit', sans-serif; background-color: #fff7ed; color: #1f2937; }
.slidev-layout { background-size: cover !important; background-position: center !important; }

.stroke-white { -webkit-text-stroke: 4px white; }
.border-black { border-color: #000000 !important; }

.animate-bounce-in { animation: bounce-in 1s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
.animate-slide-in-left { animation: slide-in-left 0.8s cubic-bezier(0.23, 1, 0.32, 1) forwards; opacity: 0; }

@keyframes bounce-in { 0% { transform: scale(0.3); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
@keyframes slide-in-left { 0% { transform: translateX(-150px) rotate(-10deg); opacity: 0; } 100% { transform: translateX(0) rotate(0); opacity: 1; } }

/* Scrollbar for ready list */
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #000; border-radius: 4px; }
</style>
