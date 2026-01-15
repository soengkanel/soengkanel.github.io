---
theme: default
background: https://images.unsplash.com/photo-1551288049-bbda38a5f94a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80
class: text-center
highlighter: shiki
lineNumbers: true
drawings:
  persist: false
transition: slide-left
title: Project Management Dashboard 2026
mdc: true
---

# <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">Executive Portfolio Report</span>
## PMO & Stakeholder Weekly Sync

<div class="pt-20 opacity-60">
  Soeng Kanel | Jan 15, 2026
</div>

<div class="abs-bl m-10 flex gap-2">
  <div class="px-3 py-1 bg-blue-500/20 border border-blue-500/30 rounded text-xs text-blue-400 font-bold uppercase tracking-widest">Data Source: projects.csv</div>
</div>

<script setup>
import { ref, onMounted } from 'vue'

const projects = ref([
  {
    "id": 1,
    "name": "Container Capacity Management",
    "category": "BC",
    "progress": 10,
    "status": "InProgress",
    "milestone": "Study Requirement",
    "owner": "TC",
    "note": "Study requirement",
    "color": "#22d3ee"
  },
  {
    "id": 2,
    "name": "Budget Control Extension",
    "category": "BC",
    "progress": 20,
    "status": "InProgress",
    "milestone": "Study Requirement",
    "owner": "TC",
    "note": "Study requirement  and gap analysis",
    "color": "#22d3ee"
  },
  {
    "id": 3,
    "name": "HR Lab",
    "category": "HRMS",
    "progress": 85,
    "status": "Coding",
    "milestone": "Development",
    "owner": "TC",
    "note": "Working on the Manpower budgeting",
    "color": "#34d399"
  },
  {
    "id": 4,
    "name": "HR Lab Mobile Apps",
    "category": "HRMS",
    "progress": 50,
    "status": "Coding",
    "milestone": "Development",
    "owner": "TC",
    "note": "",
    "color": "#34d399"
  },
  {
    "id": 4,
    "name": "Bullseye",
    "category": "CRM",
    "progress": 5,
    "status": "Todo",
    "milestone": "Initialized",
    "owner": "TC",
    "note": "Study requirement",
    "color": "#fb923c"
  },
  {
    "id": 5,
    "name": "CryptoTrading",
    "category": "QuantConnect",
    "progress": 0,
    "status": "Todo",
    "milestone": "R&D",
    "owner": "TC",
    "note": "Study QuantConnect",
    "color": "#fbbf24"
  },
  {
    "id": 6,
    "name": "Car Parking&Dorminitory",
    "category": "Custom",
    "progress": 3,
    "status": "Todo",
    "milestone": "Prospect",
    "owner": "TC",
    "note": "On bid",
    "color": "#94a3b8"
  }
])

const avgProgress = projects.value.reduce((acc, p) => acc + p.progress, 0) / projects.value.length
</script>

---
layout: default
---

# <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Portfolio Execution Dashboard</span>
<p class="opacity-50">Enterprise Project Tracking & Delivery Status</p>

<div class="mt-6 overflow-hidden bg-white/5 border border-white/10 rounded-2xl text-left">
  <table class="w-full text-sm border-collapse">
    <thead class="bg-white/10">
      <tr>
        <th class="p-3 text-xs font-bold uppercase opacity-50">Project Category & Name</th>
        <th class="p-3 text-xs font-bold uppercase opacity-50">Milestone</th>
        <th class="p-3 text-xs font-bold uppercase opacity-50">Execution Progress</th>
        <th class="p-3 text-xs font-bold uppercase opacity-50 text-right">Status</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="p in projects" :key="p.id" class="border-b border-white/5 hover:bg-white/5 transition-colors">
        <td class="p-3">
          <div class="flex items-center gap-3">
             <div class="w-1.5 h-6 rounded-full" :style="{ backgroundColor: p.color }"></div>
             <div>
               <div class="text-[10px] font-bold opacity-50 uppercase">{{ p.category }}</div>
               <div class="font-bold">{{ p.name }}</div>
             </div>
          </div>
        </td>
        <td class="p-3 text-xs opacity-70">{{ p.milestone }}</td>
        <td class="p-3 min-w-40">
          <div class="flex items-center gap-3">
            <div class="flex-grow bg-white/10 h-1.5 rounded-full overflow-hidden">
              <div class="h-full transition-all duration-1000" :style="{ width: p.progress + '%', backgroundColor: p.color }"></div>
            </div>
            <span class="text-[10px] font-mono opacity-50">{{ p.progress }}%</span>
          </div>
        </td>
        <td class="p-3 text-right">
          <span class="px-2 py-0.5 text-[9px] font-black rounded-full uppercase" 
                :class="p.status === 'Delay Risk' ? 'bg-red-500/20 text-red-500' : p.status === 'Todo' ? 'bg-white/10 text-white/50' : 'bg-emerald-400/20 text-emerald-400'">
            {{ p.status }}
          </span>
        </td>
      </tr>
    </tbody>
  </table>
</div>

<div class="mt-6 flex gap-4 text-left">
  <div class="p-3 bg-blue-600/20 border border-blue-400/30 rounded-xl flex items-center gap-4 flex-1">
    <div class="text-3xl font-black italic opacity-40">{{ Math.round(avgProgress) }}%</div>
    <div class="text-[10px] uppercase opacity-50 leading-tight">Average Portfolio<br>Completion</div>
  </div>
  <div class="p-3 bg-white/5 border border-white/10 rounded-xl flex items-center gap-3 flex-1">
    <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
    <span class="text-[10px] opacity-60">Source: <code>projects.csv</code> | Sync Active</span>
  </div>
</div>

# <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">Technical Deep Dive: Business Central</span>
<p class="opacity-50">NGD & Budget Control Implementation Progress</p>

<div class="mt-8 overflow-hidden bg-white/5 border border-white/10 rounded-2xl text-left">
  <table class="w-full text-sm">
    <thead class="bg-white/10">
      <tr>
        <th class="p-4 text-xs font-bold uppercase opacity-50">Functional Module</th>
        <th class="p-4 text-xs font-bold uppercase opacity-50">Technical Milestone</th>
        <th class="p-4 text-xs font-bold uppercase opacity-50">Progress</th>
        <th class="p-4 text-xs font-bold uppercase opacity-50">Note</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="p in projects.filter(p => p.category === 'BC')" :key="p.id" class="border-b border-white/5 hover:bg-white/5 transition-colors">
        <td class="p-4 font-bold">{{ p.name }}</td>
        <td class="p-4 text-xs">{{ p.milestone }}</td>
        <td class="p-4">
          <div class="flex items-center gap-3">
            <div class="flex-grow bg-white/10 h-1.5 rounded-full overflow-hidden">
              <div class="h-full bg-cyan-400" :style="{ width: p.progress + '%' }"></div>
            </div>
            <span class="text-[10px] opacity-50">{{ p.progress }}%</span>
          </div>
        </td>
        <td class="p-4 text-[10px] opacity-60 leading-tight">{{ p.note }}</td>
      </tr>
    </tbody>
  </table>
</div>

---
layout: default
---

# <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">Operations & CRM Execution</span>
<p class="opacity-50">HRMS & CRM Engagement Lifecycle</p>

<div class="mt-8 overflow-hidden bg-white/5 border border-white/10 rounded-2xl text-left">
  <table class="w-full text-sm">
    <thead class="bg-white/10 text-emerald-400">
      <tr>
        <th class="p-4 text-xs font-bold uppercase opacity-50">Project</th>
        <th class="p-4 text-xs font-bold uppercase opacity-50">Status</th>
        <th class="p-4 text-xs font-bold uppercase opacity-50">Progress</th>
        <th class="p-4 text-xs font-bold uppercase opacity-50 text-right">Owner</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="p in projects.filter(p => ['HRMS', 'CRM'].includes(p.category))" :key="p.id" class="border-b border-white/5 hover:bg-white/5 transition-colors">
        <td class="p-4 font-bold">{{ p.name }}</td>
        <td class="p-4"><span class="px-2 py-0.5 bg-white/5 rounded-full text-[10px] uppercase font-bold text-emerald-400/80">{{ p.status }}</span></td>
        <td class="p-4">
          <div class="flex items-center gap-3">
            <div class="flex-grow bg-white/10 h-1.5 rounded-full overflow-hidden">
              <div class="h-full bg-emerald-400" :style="{ width: p.progress + '%' }"></div>
            </div>
            <span class="text-[10px] opacity-50">{{ p.progress }}%</span>
          </div>
        </td>
        <td class="p-4 text-right text-xs opacity-60 font-mono">{{ p.owner }}</td>
      </tr>
    </tbody>
  </table>
</div>

---
layout: default
---

# <span class="text-transparent bg-clip-text bg-gradient-to-r from-gold-400 to-yellow-600">05. CryptoTrading Project</span>
<script setup>
const quantProj = projects.value.find(p => p.category === 'Quant')
</script>

<div class="mt-10 grid grid-cols-2 gap-10 text-left">
  <div class="space-y-8">
    <div class="flex items-start gap-4">
      <div class="p-2 bg-yellow-400/10 rounded-lg text-yellow-400 font-bold">Progress</div>
      <div>
        <div class="text-4xl font-black">{{ quantProj.progress }}%</div>
        <div class="text-[10px] opacity-50 uppercase">{{ quantProj.status }}</div>
      </div>
    </div>
    <div class="flex items-start gap-4">
      <div class="p-2 bg-blue-400/10 rounded-lg text-blue-400 font-bold">MIL</div>
      <div>
        <div class="text-xl font-bold">{{ quantProj.milestone }}</div>
        <div class="text-[10px] opacity-50 uppercase">Current Optimization Phase</div>
      </div>
    </div>
  </div>

  <div class="p-6 bg-white/5 border-l-4 border-yellow-500 rounded-r-2xl">
    <h3 class="text-sm font-bold mb-4">Business Value Analysis</h3>
    <p class="text-xs opacity-70 leading-relaxed">
      This model serves as a proof-of-concept for automated liquidity management. Success here will enable the architecture for the <strong>Institutional Trading Desk</strong> pilot in Q3.
    </p>
    <div class="mt-6 text-xl text-yellow-500 font-black tracking-tighter uppercase opacity-30">QuantConnect Engine</div>
  </div>
</div>

---
layout: center
class: text-center
---

# <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">Sync Complete</span>
<p class="opacity-50 -mt-2">Reporting via Dynamic Data Source</p>

<div class="mt-12 flex justify-center gap-10 opacity-30">
  <div class="flex flex-col items-center"><div class="i-carbon:report text-2xl" /><span class="text-[8px] mt-1 uppercase">Reports</span></div>
  <div class="flex flex-col items-center"><div class="i-carbon:milestone text-2xl" /><span class="text-[8px] mt-1 uppercase">Timeline</span></div>
  <div class="flex flex-col items-center"><div class="i-carbon:data-set text-2xl" /><span class="text-[8px] mt-1 uppercase">CSV Synced</span></div>
</div>

---
layout: default
---

<style>
h1 {
  font-weight: 900;
  letter-spacing: -0.05em;
}
.slidev-layout.default {
  padding: 3rem 4rem;
}
</style>
