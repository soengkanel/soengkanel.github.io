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
    "name": "NGD Container Capacity Management",
    "category": "BC",
    "progress": 65,
    "status": "In Progress",
    "milestone": "Core Table Refactoring",
    "owner": "Soeng Kanel",
    "note": "Optimizing 48 core financial tables.",
    "color": "#22d3ee"
  },
  {
    "id": 2,
    "name": "NGT Budget Control Extension",
    "category": "BC",
    "progress": 45,
    "status": "Development",
    "milestone": "Purchase Header Logic",
    "owner": "Soeng Kanel",
    "note": "Implementing hard-blocks on over-budget lines.",
    "color": "#22d3ee"
  },
  {
    "id": 3,
    "name": "HR Lab",
    "category": "HRMS",
    "progress": 85,
    "status": "On Track",
    "milestone": "Pilot Pre-launch",
    "owner": "HR Dept",
    "note": "Attendance API Sync completed.",
    "color": "#34d399"
  },
  {
    "id": 4,
    "name": "Bullseye CRM",
    "category": "CRM",
    "progress": 25,
    "status": "Delay Risk",
    "milestone": "Funnel Strategy Map",
    "owner": "Sales Op",
    "note": "Stakeholder feedback loop delay.",
    "color": "#fb923c"
  },
  {
    "id": 5,
    "name": "CryptoTrading",
    "category": "QuantConnect",
    "progress": 55,
    "status": "Active Research",
    "milestone": "Momentum Engine",
    "owner": "Quant Team",
    "note": "Simulating against 2024-2025 volatility.",
    "color": "#fbbf24"
  }
])

const avgProgress = projects.value.reduce((acc, p) => acc + p.progress, 0) / projects.value.length
</script>

---
layout: default
---

# <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Portfolio Health Dashboard</span>
<p class="opacity-50">High-level progress tracking for Product Owners & Business Stakeholders</p>

<div class="grid grid-cols-3 gap-4 mt-8">
  
  <div v-for="p in projects" :key="p.id" class="p-4 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-md">
    <div class="flex justify-between items-start mb-2 text-left">
      <div class="text-[10px] font-bold uppercase" :style="{ color: p.color }">{{ p.category }}: {{ p.name }}</div>
      <div class="text-xl font-black italic opacity-20">{{ p.progress }}%</div>
    </div>
    <div class="h-1.5 w-full bg-white/10 rounded-full mb-3 overflow-hidden">
      <div class="h-full transition-all duration-1000" :style="{ width: p.progress + '%', backgroundColor: p.color }"></div>
    </div>
    <div class="text-[10px] opacity-60 text-left">Milestone: {{ p.milestone }}</div>
  </div>

  <div class="p-4 bg-blue-600/20 border border-blue-400/30 rounded-2xl flex flex-col justify-center">
    <div class="text-2xl font-bold flex items-center gap-2">
      <div class="i-carbon:analytics text-blue-400" /> {{ Math.round(avgProgress) }}%
    </div>
    <div class="text-[10px] uppercase opacity-50 tracking-tighter">Avg Portfolio CompletionRatio</div>
  </div>

</div>

<div class="mt-8 flex gap-4 text-left">
  <div class="flex-1 p-3 bg-white/5 border border-white/10 rounded-xl text-[10px] flex items-center gap-3">
    <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
    <span>Resource Allocation: 92% Utilization</span>
  </div>
  <div class="flex-1 p-3 bg-white/5 border border-white/10 rounded-xl text-[10px] flex items-center gap-3">
    <div class="w-2 h-2 rounded-full bg-blue-400" />
    <span>Data synced from <code>projects.csv</code></span>
  </div>
</div>

---
layout: default
---

# <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">Deep Dive: Business Central</span>
<p class="opacity-50">NGD & Budget Control Status</p>

<div class="grid grid-cols-2 gap-6 mt-10 text-left">
  <div v-for="p in projects.filter(p => p.category === 'BC')" :key="p.id" class="p-6 bg-white/5 border border-white/10 rounded-2xl">
    <h3 class="flex items-center gap-2 mb-4">
      <div :class="p.id === 1 ? 'i-carbon:chart-relationship text-cyan-400' : 'i-carbon:security text-blue-400'" /> {{ p.name }}
    </h3>
    <p class="text-sm opacity-80 mb-6">Current Progress: {{ p.progress }}%. Target: Completion of {{ p.milestone }}.</p>
    <div class="text-[10px] flex gap-2">
      <span class="px-2 py-0.5 bg-white/10 rounded">{{ p.status }}</span>
      <span v-if="p.progress < 50" class="px-2 py-0.5 bg-yellow-400/10 text-yellow-400 rounded">In Development</span>
      <span v-else class="px-2 py-0.5 bg-emerald-400/10 text-emerald-400 rounded">Optimizing</span>
    </div>
  </div>
</div>

---
layout: default
---

# <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">Operations & CRM Tracking</span>
<p class="opacity-50">HR Lab & Bullseye Engagement</p>

<div class="mt-10 overflow-hidden bg-white/5 border border-white/10 rounded-3xl text-left">
  <div class="grid grid-cols-4 border-b border-white/10 bg-white/5">
    <div class="p-4 text-xs font-bold uppercase opacity-50">Product</div>
    <div class="p-4 text-xs font-bold uppercase opacity-50">Milestone</div>
    <div class="p-4 text-xs font-bold uppercase opacity-50">Progress</div>
    <div class="p-4 text-xs font-bold uppercase opacity-50 text-right">Status</div>
  </div>
  <div v-for="p in projects.filter(p => ['HRMS', 'CRM'].includes(p.category))" :key="p.id" class="grid grid-cols-4 border-b border-white/5">
    <div class="p-4 text-sm font-bold">{{ p.name }}</div>
    <div class="p-4 text-sm opacity-70">{{ p.milestone }}</div>
    <div class="p-4">
       <div class="w-full bg-white/10 h-1 rounded-full mt-2 overflow-hidden"><div class="h-full bg-emerald-400" :style="{ width: p.progress + '%' }"></div></div>
    </div>
    <div class="p-4 flex items-center justify-end">
      <div class="px-2 py-0.5 text-[10px] rounded-full font-bold" :class="p.status === 'Delay Risk' ? 'bg-red-500/20 text-red-500' : 'bg-emerald-400/20 text-emerald-400'">
        {{ p.status.toUpperCase() }}
      </div>
    </div>
  </div>
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
