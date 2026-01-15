---
theme: default
background: ./assets/title-bg.png
class: text-center
highlighter: shiki
lineNumbers: true
drawings:
  persist: false
transition: slide-left
title: TC Technical Portfolio 2026
mdc: true
---

<div class="h-full flex flex-col justify-center items-center text-white">
  <div class="relative group">
    <div class="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg blur opacity-25 group-hover:opacity-100 transition duration-1000 group-hover:duration-200"></div>
    <div class="relative px-8 py-4 bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl">
      <h1 class="text-7xl font-black mb-2 tracking-tighter">
        <span class="text-transparent bg-clip-text bg-gradient-to-br from-cyan-400 via-blue-500 to-indigo-600 animate-gradient-x">
          Strategic Technical Dashboard
        </span>
      </h1>
      <h2 class="text-2xl font-light opacity-80 tracking-[0.2em] uppercase">
        Solutions Architecture & Execution
      </h2>
    </div>
  </div>

  <div class="mt-20 flex gap-8 items-center">
    <div class="flex flex-col items-end border-r border-white/20 pr-8">
      <div class="text-xs uppercase font-black tracking-widest text-cyan-400 mb-1">Consultant Identity</div>
      <div class="text-2xl font-black italic">TC | Technical Lead</div>
    </div>
    <div class="flex flex-col items-start translate-y-1">
      <div class="text-xs uppercase font-black tracking-widest opacity-40 mb-1">Portfolio Lifecycle</div>
      <div class="text-lg font-bold opacity-80">Cycle Q1 / FY-2026</div>
    </div>
  </div>

  <div class="mt-12 flex gap-4">
    <div class="px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-black uppercase tracking-widest flex items-center gap-2">
      <div class="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></div>
      System Health: Optimized
    </div>
    <div class="px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-black uppercase tracking-widest flex items-center gap-2 opacity-40 italic">
      Confidential / Internal Use Only
    </div>
  </div>

  <div class="abs-br m-10 w-80 text-left">
    <div class="px-4 py-3 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl">
      <div class="text-[10px] font-black uppercase tracking-widest opacity-30 mb-3 flex justify-between">
        <span>Priority Delivery Stack</span>
        <span class="text-cyan-400">Q1-2026</span>
      </div>
      <div class="space-y-2">
        <div class="flex items-center gap-3">
          <div class="text-xs font-black opacity-20">01</div>
          <div class="text-[11px] font-bold text-white border-l-2 border-cyan-400 pl-2 leading-tight">NGD Budget Control Extension</div>
        </div>
        <div class="flex items-center gap-3">
          <div class="text-xs font-black opacity-20">02</div>
          <div class="text-[11px] font-bold opacity-80 border-l-2 border-white/20 pl-2 leading-tight">NGD Container Capacity Management</div>
        </div>
        <div class="flex items-center gap-3">
          <div class="text-xs font-black opacity-20">03</div>
          <div class="text-[11px] font-bold opacity-60 border-l-2 border-white/20 pl-2 leading-tight">HR Lab</div>
        </div>
        <div class="flex items-center gap-3">
          <div class="text-xs font-black opacity-20">04</div>
          <div class="text-[11px] font-bold opacity-40 border-l-2 border-white/20 pl-2 leading-tight">HR Lab Mobile Apps</div>
        </div>
        <div class="flex items-center gap-3">
          <div class="text-xs font-black opacity-20">05</div>
          <div class="text-[11px] font-bold opacity-20 border-l-2 border-white/20 pl-2 leading-tight">NGPOS (F&B)</div>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
.animate-gradient-x {
  background-size: 200% 200%;
  animation: gradient-x 15s ease infinite;
}

@keyframes gradient-x {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
</style>

---
layout: default
clicks: 1
---

# <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Portfolio Execution Dashboard</span>
<p class="opacity-50">Enterprise Project Tracking & Delivery Status</p>

<div class="mt-4 overflow-hidden bg-white/5 border border-white/10 rounded-2xl text-left">
  <table class="w-full text-[11px] border-collapse">
    <thead class="bg-white/10 uppercase font-black opacity-60">
      <tr>
        <th class="p-2 text-left">Category & Project Name</th>
        <th class="p-2 text-left">Milestone</th>
        <th class="p-2 text-left">Progress</th>
        <th class="p-2 text-center">Lead</th>
        <th class="p-3 text-right">Status</th>
      </tr>
    </thead>
    <tbody v-if="$clicks === 0">
      <!-- 1 -->
      <tr class="border-b border-white/5">
        <td class="p-2"><div class="flex items-center gap-2"><div class="w-1 h-5 rounded-full bg-cyan-400"></div><div><div class="text-[9px] font-bold opacity-40 leading-none">BC</div><div class="font-bold leading-tight">Container Capacity Management</div></div></div></td>
        <td class="p-2 opacity-70">Study Requirement</td>
        <td class="p-2 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-1 rounded-full overflow-hidden"><div class="h-full bg-cyan-400" style="width: 10%"></div></div><span class="text-[10px] font-mono opacity-50">10%</span></div></td>
        <td class="p-2 text-center text-[10px] font-bold text-cyan-300">Kanel</td>
        <td class="p-2 text-right"><span class="px-2 py-0.5 text-[8px] font-black rounded-full uppercase bg-emerald-400/20 text-emerald-400">InProgress</span></td>
      </tr>
      <!-- 2 -->
      <tr class="border-b border-white/5">
        <td class="p-2"><div class="flex items-center gap-2"><div class="w-1 h-5 rounded-full bg-cyan-400"></div><div><div class="text-[9px] font-bold opacity-40 leading-none">BC</div><div class="font-bold leading-tight">Budget Control Extension</div></div></div></td>
        <td class="p-2 opacity-70">Study Requirement</td>
        <td class="p-2 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-1 rounded-full overflow-hidden"><div class="h-full bg-cyan-400" style="width: 20%"></div></div><span class="text-[10px] font-mono opacity-50">20%</span></div></td>
        <td class="p-2 text-center text-[10px] font-bold text-cyan-300">Panha</td>
        <td class="p-2 text-right"><span class="px-2 py-0.5 text-[8px] font-black rounded-full uppercase bg-emerald-400/20 text-emerald-400">InProgress</span></td>
      </tr>
      <!-- 3 -->
      <tr class="border-b border-white/5">
        <td class="p-2"><div class="flex items-center gap-2"><div class="w-1 h-5 rounded-full bg-emerald-400"></div><div><div class="text-[9px] font-bold opacity-40 leading-none">HRMS</div><div class="font-bold leading-tight">HR Lab</div></div></div></td>
        <td class="p-2 opacity-70">Development</td>
        <td class="p-2 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-1 rounded-full overflow-hidden"><div class="h-full bg-emerald-400" style="width: 85%"></div></div><span class="text-[10px] font-mono opacity-50">85%</span></div></td>
        <td class="p-2 text-center text-[10px] font-bold text-emerald-300">Monika</td>
        <td class="p-2 text-right"><span class="px-2 py-0.5 text-[8px] font-black rounded-full uppercase bg-blue-400/20 text-blue-400">Coding</span></td>
      </tr>
      <!-- 4 -->
      <tr class="border-b border-white/5">
        <td class="p-2"><div class="flex items-center gap-2"><div class="w-1 h-5 rounded-full bg-emerald-400"></div><div><div class="text-[9px] font-bold opacity-40 leading-none">HRMS</div><div class="font-bold leading-tight">HR Lab Mobile Apps</div></div></div></td>
        <td class="p-2 opacity-70">Development</td>
        <td class="p-2 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-1 rounded-full overflow-hidden"><div class="h-full bg-emerald-400" style="width: 50%"></div></div><span class="text-[10px] font-mono opacity-50">50%</span></div></td>
        <td class="p-2 text-center text-[10px] font-bold text-emerald-300">Monika</td>
        <td class="p-2 text-right"><span class="px-2 py-0.5 text-[8px] font-black rounded-full uppercase bg-blue-400/20 text-blue-400">Coding</span></td>
      </tr>
      <!-- 5 -->
      <tr class="border-b border-white/5">
        <td class="p-2"><div class="flex items-center gap-2"><div class="w-1 h-5 rounded-full bg-orange-400"></div><div><div class="text-[9px] font-bold opacity-40 leading-none">CRM</div><div class="font-bold leading-tight">Bullseye</div></div></div></td>
        <td class="p-2 opacity-70">Initialized</td>
        <td class="p-2 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-1 rounded-full overflow-hidden"><div class="h-full bg-orange-400" style="width: 5%"></div></div><span class="text-[10px] font-mono opacity-50">5%</span></div></td>
        <td class="p-2 text-center text-[10px] font-bold text-orange-300">Sreypich, Panha</td>
        <td class="p-2 text-right"><span class="px-2 py-0.5 text-[8px] font-black rounded-full uppercase bg-white/10 text-white/50">Todo</span></td>
      </tr>
    </tbody>
    <tbody v-if="$clicks === 1">
      <!-- 6 -->
      <tr class="border-b border-white/5">
        <td class="p-2"><div class="flex items-center gap-2"><div class="w-1 h-5 rounded-full bg-yellow-400"></div><div><div class="text-[9px] font-bold opacity-40 leading-none">QuantConnect</div><div class="font-bold leading-tight">CryptoTrading</div></div></div></td>
        <td class="p-2 opacity-70">R&D</td>
        <td class="p-2 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-1 rounded-full overflow-hidden"><div class="h-full bg-yellow-400" style="width: 0%"></div></div><span class="text-[10px] font-mono opacity-50">0%</span></div></td>
        <td class="p-2 text-center text-[10px] font-bold text-yellow-300">Gordon</td>
        <td class="p-2 text-right"><span class="px-2 py-0.5 text-[8px] font-black rounded-full uppercase bg-white/10 text-white/50">Todo</span></td>
      </tr>
      <!-- 7 -->
      <tr class="border-b border-white/5">
        <td class="p-2"><div class="flex items-center gap-2"><div class="w-1 h-5 rounded-full bg-purple-400"></div><div><div class="text-[9px] font-bold opacity-40 leading-none">Custom</div><div class="font-bold leading-tight">Car Parking & Dormitory</div></div></div></td>
        <td class="p-2 opacity-70">Prospect</td>
        <td class="p-2 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-1 rounded-full overflow-hidden"><div class="h-full bg-purple-400" style="width: 3%"></div></div><span class="text-[10px] font-mono opacity-50">3%</span></div></td>
        <td class="p-2 text-center text-[10px] font-bold text-purple-300">Kanel</td>
        <td class="p-2 text-right"><span class="px-2 py-0.5 text-[8px] font-black rounded-full uppercase bg-white/10 text-white/50">Todo</span></td>
      </tr>
      <!-- 8 -->
      <tr class="border-b border-white/5">
        <td class="p-2"><div class="flex items-center gap-2"><div class="w-1 h-5 rounded-full bg-sky-400"></div><div><div class="text-[9px] font-bold opacity-40 leading-none">Retail</div><div class="font-bold leading-tight">NGPOS</div></div></div></td>
        <td class="p-2 opacity-70">In Progress</td>
        <td class="p-2 min-w-28"><div class="flex items-center gap-2"><div class="flex-grow bg-white/10 h-1 rounded-full overflow-hidden"><div class="h-full bg-sky-400" style="width: 30%"></div></div><span class="text-[10px] font-mono opacity-50">30%</span></div></td>
        <td class="p-2 text-center text-[10px] font-bold text-sky-300">Marchi</td>
        <td class="p-2 text-right"><span class="px-2 py-0.5 text-[8px] font-black rounded-full uppercase bg-emerald-400/20 text-emerald-400">InProgress</span></td>
      </tr>
      <tr class="border-b border-white/5">
        <td colspan="5" class="p-1 opacity-0 text-[1px]">Buffer</td>
      </tr>
    </tbody>
  </table>
</div>

<div class="mt-4 flex gap-4 text-left">
  <div class="p-3 bg-blue-600/20 border border-blue-400/30 rounded-xl flex items-center gap-4 flex-1">
    <div class="text-3xl font-black italic opacity-40">25.5%</div>
    <div class="text-[10px] uppercase opacity-50 leading-tight font-bold">Average Portfolio<br>Completion</div>
  </div>
  <div class="p-3 bg-white/5 border border-white/10 rounded-xl flex items-center gap-3 flex-1">
    <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
    <span class="text-[10px] opacity-60 font-bold uppercase tracking-wider">Static Reporting Active</span>
  </div>
</div>

---
layout: default
---

# <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">In-Progress Tasks</span>
<p class="opacity-50 text-xs">Granular tracking of all active implementation stages</p>

<div class="mt-6">
  <div class="overflow-hidden bg-white/5 border border-white/10 rounded-2xl text-left">
    <table class="w-full text-[11px]">
      <thead class="bg-white/10 opacity-70 uppercase font-bold">
        <tr>
          <th class="p-3">Project</th>
          <th class="p-3">Active Identifiable Task</th>
          <th class="p-3 text-center">% Progress</th>
          <th class="p-3 text-right">PIC</th>
        </tr>
      </thead>
      <tbody>
        <tr class="border-b border-white/5">
          <td class="p-3 font-bold opacity-60">Container Mgmt</td>
          <td class="p-3 italic">Understand the requirements</td>
          <td class="p-3 text-center text-cyan-400 font-bold">15%</td>
          <td class="p-3 text-right font-black opacity-80">Kanel</td>
        </tr>
        <tr class="border-b border-white/5">
          <td class="p-3 font-bold opacity-60">Budget Extension</td>
          <td class="p-3 italic">Gap Analysis & Requirement Specs, man days est.</td>
          <td class="p-3 text-center text-cyan-400 font-bold">30%</td>
          <td class="p-3 text-right font-black opacity-80">Panha</td>
        </tr>
        <tr class="border-b border-white/5">
          <td class="p-3 font-bold opacity-60">HR Lab (Web)</td>
          <td class="p-3 italic">Manpower Budgeting Workflow Integration</td>
          <td class="p-3 text-center text-emerald-400 font-bold">85%</td>
          <td class="p-3 text-right font-black opacity-80">Monika</td>
        </tr>
        <tr class="border-b border-white/5">
          <td class="p-3 font-bold opacity-60">HR Mobile</td>
          <td class="p-3 italic">Login multitenant(NGD/T) & leave a half-day feature</td>
          <td class="p-3 text-center text-emerald-400 font-bold">50%</td>
          <td class="p-3 text-right font-black opacity-80">Monika</td>
        </tr>
        <tr class="border-b border-white/5">
          <td class="p-3 font-bold opacity-60">NGPOS</td>
          <td class="p-3 italic">Design User Interface & Database Schema</td>
          <td class="p-3 text-center text-sky-400 font-bold">30%</td>
          <td class="p-3 text-right font-black opacity-80">Marchi</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<div class="mt-4 p-3 border border-blue-500/20 rounded-xl bg-blue-500/5 text-[10px] opacity-60 text-center uppercase tracking-tighter">
  Cross-departmental resources are currently optimized for Q1 delivery cycle.
</div>

---
layout: default
---

# <span class="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-500">Blockers & Strategic Support</span>
<p class="opacity-50 text-xs">Critical challenges requiring executive intervention</p>

<div class="grid grid-cols-2 gap-6 mt-8">
  <div class="p-6 bg-red-500/5 border border-red-500/20 rounded-2xl">
    <div class="flex items-center gap-3 mb-4">
      <div class="i-carbon:warning-filled text-red-400 text-2xl" />
      <h3 class="text-lg font-black uppercase text-red-200">Facing Problems</h3>
    </div>
    <ul class="text-sm space-y-4 opacity-80">
      <li class="flex gap-2">
        <span class="text-red-400 font-black">01.</span>
        <span><b>Mobile Production Risk:</b> Currently utilizing 2 Junior Devs with AI assistance. While coding is fast, there are deep architectural concerns for Production stability.</span>
      </li>
      <li class="flex gap-2">
        <span class="text-red-400 font-black">02.</span>
        <span><b>Testing Gap:</b> Critical lack of <b>Domain Experts</b> for functional testing and product evaluation. Current testing is technical, not business-aligned.</span>
      </li>
    </ul>
  </div>

  <div class="p-6 bg-blue-500/5 border border-blue-500/20 rounded-2xl">
    <div class="flex items-center gap-3 mb-4">
      <div class="i-carbon:user-activity text-blue-400 text-2xl" />
      <h3 class="text-lg font-black uppercase text-blue-200">Support Action</h3>
    </div>
    <ul class="text-sm space-y-4 opacity-80">
      <li class="flex gap-2">
        <span class="text-blue-400 font-black">A.</span>
        <span><b>Project Prioritization:</b> Clearly define the delivery sequence to ensure resources are focused on high-impact projects.</span>
      </li>
      <li class="flex gap-2">
        <span class="text-blue-400 font-black">B.</span>
        <span><b>Domain Squad:</b> Direct assignment of 2 Business Power Users for a 1-week intensive evaluation sprint or by module.</span>
      </li>
    </ul>
  </div>
</div>

<div class="mt-8 flex justify-center">
  <div class="px-6 py-2 bg-white/5 border border-white/10 rounded-full text-[10px] uppercase font-bold tracking-widest opacity-40">
    Urgent Decision Required for Q1 Delivery Schedule
  </div>
</div>

---
layout: center
class: text-center
---

# <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">Strategic Performance Complete</span>
<p class="opacity-50 -mt-2 tracking-widest uppercase text-xs">Awaiting Executive Guidance</p>

<div class="mt-12 flex justify-center gap-10 opacity-20">
  <div class="flex flex-col items-center"><div class="i-carbon:report text-3xl" /></div>
  <div class="flex flex-col items-center"><div class="i-carbon:milestone text-3xl" /></div>
  <div class="flex flex-col items-center"><div class="i-carbon:dashboard text-3xl" /></div>
</div>

<style>
h1 {
  font-weight: 900;
  letter-spacing: -0.05em;
}
.slidev-layout.default {
  padding: 3rem 4rem;
}
table th { font-weight: 900 !important; }
</style>
