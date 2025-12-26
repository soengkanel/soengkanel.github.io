---
theme: default
background: https://images.unsplash.com/photo-1557683316-973673baf926?q=80&w=2029&auto=format&fit=crop
class: text-center
highlighter: shiki
lineNumbers: false
info: |
  ## SharePoint WordPress Integration
  Secure Product Catalog for BRED Bank Cambodia.
drawings:
  persist: false
transition: slide-left
title: Secure SharePoint Product Catalog
css: unocss
---

<style>
/* Using Open Sans as it is the closest free Google Font to BRED's "Myriad Pro" */
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,600;0,700;0,800;1,400&display=swap');

:root {
  --bred-red: #D71920;
  --bred-blue: #0047BB;
  --bred-grad-red: linear-gradient(135deg, #D71920 0%, #a61218 100%);
  --bred-grad-blue: linear-gradient(135deg, #0047BB 0%, #002a70 100%);
  --glass-bg: rgba(255, 255, 255, 0.95);
  --glass-border: 1px solid rgba(255, 255, 255, 0.8);
}

body {
  font-family: 'Open Sans', sans-serif; /* Corporate Standard look-alike */
  color: #334155;
  background-image: radial-gradient(#0047BB 0.5px, transparent 0.5px), radial-gradient(#D71920 0.5px, transparent 0.5px);
  background-size: 20px 20px;
  background-position: 0 0, 10px 10px;
  background-color: #f8fafc;
}

h1, h2, h3, h4 {
  font-family: 'Open Sans', sans-serif;
  color: var(--bred-blue);
  letter-spacing: -0.02em; /* Tighter tracking for Myriad Pro feel */
}

.fusion-line {
  height: 4px;
  background: linear-gradient(90deg, 
    #0047BB 0%, #0047BB 40%, 
    transparent 40%, transparent 60%, 
    #D71920 60%, #D71920 100%);
  position: relative;
  margin: 20px 0;
}

/* Abstract interpretation of Khmer Kbach (Lotus) + French Art Deco (Geo) */
.fusion-line::after {
  content: "✦"; 
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -55%);
  color: #334155;
  font-size: 20px;
  background: #f8fafc;
  padding: 0 10px;
}

.text-gradient-blue {
  background: var(--bred-grad-blue);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.text-gradient-red {
  background: var(--bred-grad-red);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.card-prem {
  background: var(--glass-bg);
  border: var(--glass-border);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(12px);
  border-radius: 8px; /* Sharper French corners, slightly rounded for friendliness */
}
</style>

<div class="absolute inset-0 bg-white/90 backdrop-blur-sm z-0"></div>

<div class="relative z-10 h-full flex flex-col justify-center items-center">
  
  <!-- Brand Identity -->
  <div class="mb-2">
    <span class="text-7xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-[#0047BB] to-[#00338d] drop-shadow-sm">We BRED</span>
  </div>

  <!-- Primary Title -->
  <h1 class="text-5xl font-extrabold mb-6 leading-tight">
    <span class="text-slate-600 font-light">Intranet SharePoint</span> <br> 
    <span class="text-gradient-red">Proposed Solution Architecture</span>
  </h1>

  <!-- Subtitle -->
  <div class="text-lg text-slate-400 font-medium tracking-[0.2em] uppercase border-t border-slate-200 pt-6 mt-2 inline-block px-12">
    Product Catalog Integration
  </div>



  <div class="fusion-line w-1/2 mt-12"></div>

</div>

<!-- 
SPEAKER NOTES:
Welcome everyone. Today we are presenting the architecture for the new Internal Product Catalog. 
This solution bridges Marketing's need for autonomy with the Bank's strict security compliance.
-->

---
layout: default
---

# ⚠️ The Problem Statement

<div class="fusion-line"></div>

<div class="text-center mb-8">
  <p class="text-lg text-slate-500 italic">Why we need a creative approach to solve this challenge</p>
</div>

<div class="grid grid-cols-3 gap-6 mt-4">

  <!-- Global Regulation -->
  <div v-click class="card-prem p-6 border-t-0 border-l-8 border-[#D71920] hover:shadow-xl transition-all duration-300">
    <div class="flex items-center gap-3 mb-4">
      <div class="text-3xl bg-red-100 p-3 rounded-xl">🌍</div>
      <h3 class="text-xl font-bold text-[#D71920]">Global Regulation</h3>
    </div>
    <p class="text-sm leading-relaxed text-slate-600 mb-4">
      BRED Bank Cambodia operates under <b>strict governance policies</b> from headquarters.
    </p>
    <div class="bg-red-50 p-4 rounded-lg border border-red-100">
      <div class="text-xs uppercase font-bold text-[#D71920] mb-2">⛔ Limitation</div>
      <p class="text-sm text-slate-700 font-medium">Only <span class="text-[#D71920] font-bold">Site Owner</span> permission granted — <b>No Global Admin</b> or <b>Tenant Admin</b> access available.</p>
    </div>
  </div>

  <!-- Internal Compliance -->
  <div v-click class="card-prem p-6 border-t-0 border-l-8 border-[#0047BB] hover:shadow-xl transition-all duration-300">
    <div class="flex items-center gap-3 mb-4">
      <div class="text-3xl bg-blue-100 p-3 rounded-xl">📋</div>
      <h3 class="text-xl font-bold text-[#0047BB]">Internal Compliance</h3>
    </div>
    <p class="text-sm leading-relaxed text-slate-600 mb-4">
      Standard SharePoint Framework (SPFx) solutions require <b>elevated privileges</b>.
    </p>
    <div class="bg-blue-50 p-4 rounded-lg border border-blue-100">
      <div class="text-xs uppercase font-bold text-[#0047BB] mb-2">🚫 Blocker</div>
      <p class="text-sm text-slate-700 font-medium"><span class="text-[#0047BB] font-bold">SPFx</span> requires Global Admin to create and deploy to the <b>App Catalog</b> — not feasible.</p>
    </div>
  </div>

  <!-- Security Solution -->
  <div v-click class="card-prem p-6 border-t-0 border-l-8 border-emerald-600 hover:shadow-xl transition-all duration-300">
    <div class="flex items-center gap-3 mb-4">
      <div class="text-3xl bg-emerald-100 p-3 rounded-xl">✅</div>
      <h3 class="text-xl font-bold text-emerald-600">Available Solution</h3>
    </div>
    <p class="text-sm leading-relaxed text-slate-600 mb-3">
      We leverage <b>existing infrastructure</b> that's already in place and approved.
    </p>
    <div class="bg-emerald-80 p-4 rounded-lg border border-emerald-100 mb-3">
      <div class="text-xs uppercase font-bold text-emerald-600 mb-2">⚡Automation&bredcambodia</div>
      <p class="text-sm text-slate-700 font-small">- is available to Site Owners.</p>
      <p class="text-sm text-slate-700 font-small">- WordPress with <span class="text-purple-600 font-bold">JavaScript</span>, <span class="text-purple-600 font-bold">Bootstrap</span>&<span class="text-purple-600 font-bold">jQuery</span> already loaded.</p>
    </div>
    
  </div>

</div>

<div v-click class="mt-6 mx-auto max-w-5xl bg-gradient-to-r from-slate-50 via-emerald-50 to-purple-50 border border-slate-200 p-5 rounded-xl shadow-sm">
  <div class="flex items-center justify-center gap-4 text-center">
    <div class="flex flex-col items-center">
      <span class="text-2xl mb-1">🔒</span>
      <span class="text-[10px] font-bold text-slate-500 uppercase">Restricted</span>
    </div>
    <div class="text-2xl text-slate-300">→</div>
    <div class="flex flex-col items-center">
      <span class="text-2xl mb-1">❌</span>
      <span class="text-[10px] font-bold text-slate-500 uppercase">No SPFx</span>
    </div>
    <div class="text-2xl text-slate-300">→</div>
    <div class="flex flex-col items-center px-3 py-2 bg-emerald-100 rounded-lg border border-emerald-200">
      <span class="text-2xl mb-1">⚡</span>
      <span class="text-[10px] font-bold text-emerald-600 uppercase">Power Automate</span>
    </div>
    <div class="text-2xl text-emerald-400 font-bold">+</div>
    <div class="flex flex-col items-center px-3 py-2 bg-purple-100 rounded-lg border border-purple-200">
      <span class="text-2xl mb-1">🌐</span>
      <span class="text-[10px] font-bold text-purple-600 uppercase">WordPress</span>
    </div>
    <div class="text-2xl text-slate-300">→</div>
    <div class="flex flex-col items-center">
      <span class="text-2xl mb-1">🎯</span>
      <span class="text-[10px] font-bold text-[#0047BB] uppercase">Solution</span>
    </div>
  </div>
</div>

<!-- 
SPEAKER NOTES:
Before we present the solution, let's understand why we need a creative approach:

1. GLOBAL REGULATION: BRED Bank Cambodia operates under strict oversight from headquarters. 
   We only have Site Owner permissions - no Global Admin or Tenant Admin access.

2. INTERNAL COMPLIANCE: The standard approach would be to use SPFx (SharePoint Framework).
   However, SPFx requires Global Admin to create and deploy solutions to the App Catalog.
   This path is blocked for us.

3. SECURITY-APPROVED SOLUTION: The good news? Site Owners DO have access to Power Automate.
   This gives us a compliant path to build secure integrations without requiring elevated permissions.

This is why we've designed a Power Automate + WordPress approach instead of traditional SPFx.
-->

---
layout: default
title: Solution Architecture
---

# ⚡ Solution Architecture

<div class="flex items-center justify-center h-96 gap-8 mt-4">
  
  <div v-click class="relative group">
    <div class="bg-white p-6 rounded-2xl shadow-xl border-t-8 border-[#0047BB] w-56 flex flex-col items-center z-10 relative">
        <div class="text-5xl mb-4">🏢</div>
        <div class="font-bold text-[#0047BB] text-xl">SharePoint</div>
        <div class="text-xs text-center text-slate-500 mt-2 font-medium uppercase tracking-wide">Marketing Interface</div>
    </div>
    <!-- Decor element -->
    <div class="absolute -inset-2 bg-blue-200 rounded-2xl blur-lg opacity-40 group-hover:opacity-70 transition duration-500"></div>
  </div>

  <div v-click class="text-3xl text-gray-300 animate-pulse">➡️</div>

  <div v-click class="relative group">
    <div class="bg-white p-6 rounded-2xl shadow-xl border-t-8 border-purple-600 w-56 flex flex-col items-center z-10 relative">
        <div class="text-5xl mb-4">⚡</div>
        <div class="font-bold text-purple-700 text-xl">Power Automate</div>
        <div class="text-xs text-center text-slate-500 mt-2 font-medium uppercase tracking-wide">Logic Engine</div>
    </div>
    <div class="absolute -inset-2 bg-purple-200 rounded-2xl blur-lg opacity-40 group-hover:opacity-70 transition duration-500"></div>
  </div>

  <div v-click class="text-3xl text-gray-300 animate-pulse">➡️</div>

  <div v-click class="relative group">
    <div class="bg-white p-6 rounded-2xl shadow-xl border-t-8 border-emerald-600 w-64 flex flex-col items-center z-10 relative">
        <div class="text-5xl mb-4">📦</div>
        <div class="font-bold text-emerald-700 text-lg leading-tight text-center">bredcambodia.com.kh<br>(WP)</div>
        <div class="text-xs text-center text-slate-500 mt-2 font-medium uppercase tracking-wide">Encrypted Product Store</div>
    </div>
    <div class="absolute -inset-2 bg-emerald-200 rounded-2xl blur-lg opacity-40 group-hover:opacity-70 transition duration-500"></div>
  </div>

</div>

<div v-click class="text-center -mt-2 mx-auto max-w-2xl bg-slate-50 border border-slate-200 p-4 rounded-full shadow-sm text-sm text-slate-600">
    <span class="font-bold text-[#D71920]">Data Flow:</span> 
    Intranet Only 🔒 No Public Access 🚫
</div>

<!-- 
SPEAKER NOTES:
Before we get technical, here is the big picture.
Structure is simple:
1. Input starts in SharePoint (Marketing).
2. Automation picks it up (Power Automate).
3. Data lands in our Secure Database (WordPress/DB).
Crucially, this entire flow happens INSIDE our private network.
-->

---
layout: default
---

# 🗺️ Implementation Map

<div class="grid grid-cols-3 gap-8 mt-10 h-96">

  <!-- SharePoint Column -->
  <div v-click class="relative group">
    <div class="h-full flex flex-col bg-gradient-to-b from-blue-50 to-white border-t-8 border-[#0ea5e9] rounded-2xl shadow-lg p-1 group-hover:shadow-2xl transition-all duration-300">
      <div class="p-6 text-center border-b border-blue-100">
        <div class="text-4xl mb-3 drop-shadow-sm">🏢</div>
        <h3 class="font-extrabold text-[#0ea5e9] tracking-wide">SHAREPOINT</h3>
        <p class="text-xs uppercase font-semibold text-blue-400 mt-1">Configuration</p>
      </div>
      <div class="p-6 flex-grow space-y-4">
          <div class="text-sm bg-white p-3 rounded-lg shadow-sm border border-blue-100 font-medium text-slate-600">📋 Lists Setup</div>
          <div class="text-sm bg-white p-3 rounded-lg shadow-sm border border-blue-100 font-medium text-slate-600">📄 Site Page</div>
          <div class="text-sm bg-white p-3 rounded-lg shadow-sm border border-blue-100 font-medium text-slate-600">🔌 Embed Web Part</div>
      </div>
    </div>
  </div>

  <!-- Power Automate Column -->
  <div v-click class="relative group">
    <div class="h-full flex flex-col bg-gradient-to-b from-purple-50 to-white border-t-8 border-[#8b5cf6] rounded-2xl shadow-lg p-1 group-hover:shadow-2xl transition-all duration-300">
      <div class="p-6 text-center border-b border-purple-100">
        <div class="text-4xl mb-3 drop-shadow-sm">⚡</div>
        <h3 class="font-extrabold text-[#8b5cf6] tracking-wide">AUTOMATE</h3>
        <p class="text-xs uppercase font-semibold text-purple-400 mt-1">Logic</p>
      </div>
      <div class="p-6 flex-grow space-y-4">
          <div class="text-sm bg-white p-3 rounded-lg shadow-sm border border-purple-100 font-medium text-slate-600">🔔 Trigger Logic</div>
          <div class="text-sm bg-white p-3 rounded-lg shadow-sm border border-purple-100 font-medium text-slate-600">🔄 JSON Mapping</div>
          <div class="text-sm bg-white p-3 rounded-lg shadow-sm border border-purple-100 font-medium text-slate-600">🌐 HTTP Connector</div>
      </div>
    </div>
  </div>

  <!-- WordPress Column -->
  <div v-click class="relative group">
    <div class="h-full flex flex-col bg-gradient-to-b from-slate-50 to-white border-t-8 border-[#334155] rounded-2xl shadow-lg p-1 group-hover:shadow-2xl transition-all duration-300">
      <div class="p-6 text-center border-b border-slate-200">
        <div class="text-4xl mb-3 drop-shadow-sm">🌐</div>
        <h3 class="font-extrabold text-[#334155] tracking-wide">WORDPRESS</h3>
        <p class="text-xs uppercase font-semibold text-slate-400 mt-1">Code</p>
      </div>
      <div class="p-6 flex-grow space-y-4">
          <div class="text-sm bg-white p-3 rounded-lg shadow-sm border border-slate-200 font-medium text-slate-600">🔧 Plugin (PHP)</div>
          <div class="text-sm bg-white p-3 rounded-lg shadow-sm border border-slate-200 font-medium text-slate-600">📦 Database</div>
          <div class="text-sm bg-white p-3 rounded-lg shadow-sm border border-slate-200 font-medium text-slate-600">🛡️ Security (CSP)</div>
      </div>
    </div>
  </div>

</div>

<!-- 
SPEAKER NOTES:
So, where does everything live?
SharePoint holds the config.
Power Automate holds the logic.
WordPress holds the code.
Clear separation of concerns.
-->

---
layout: default
---

# 🤖 Automation Workflow

<div class="grid grid-cols-3 gap-6 mt-10">
    <div class="col-span-1 p-6 bg-white rounded-xl shadow-lg border border-gray-100 hover:shadow-xl transition-all">
        <h3 class="font-bold text-[#0047BB] text-lg mb-2">1. Trigger</h3>
        <p class="text-sm text-slate-500 leading-relaxed">Marketing creates a new item in the <b>SharePoint List</b>.</p>
    </div>
    <div class="col-span-1 p-6 bg-white rounded-xl shadow-lg border border-gray-100 hover:shadow-xl transition-all">
        <h3 class="font-bold text-[#0047BB] text-lg mb-2">2. Action</h3>
        <p class="text-sm text-slate-500 leading-relaxed"><b>Power Automate</b> transforms data & POSTs to WordPress API.</p>
    </div>
    <div class="col-span-1 p-6 bg-white rounded-xl shadow-lg border border-gray-100 hover:shadow-xl transition-all">
        <h3 class="font-bold text-[#0047BB] text-lg mb-2">3. View</h3>
        <p class="text-sm text-slate-500 leading-relaxed">Site Owner views result via <b>Embed Web Part</b>.</p>
    </div>
</div>

<div class="mt-10 relative max-w-3xl mx-auto shadow-2xl rounded-lg overflow-hidden text-left">
  
  <!-- Custom Code Block for Precision Targeting -->
  <div class="bg-[#0d1117] text-[#e6edf3] p-6 rounded-lg font-mono text-sm leading-7 border border-slate-700">
    <div class="text-slate-500">&lt;!-- Embed Code for SharePoint --&gt;</div>
    <div><span class="text-blue-400">&lt;iframe</span></div>
    <div class="pl-4">
      <span class="text-purple-400">src</span>=<span class="text-green-400">"https://bredcambodia.com.kh/product-catalog-embed/</span><span v-mark.circle.red="1" class="text-red-400 font-bold px-1">?token=[SECURE]</span><span class="text-green-400">"</span>
    </div>
    <div class="pl-4">
      <span class="text-purple-400">width</span>=<span class="text-blue-400">"100%"</span>
    </div>
    <div class="pl-4">
      <span class="text-purple-400">style</span>=<span class="text-blue-400">"border:none;"</span><span class="text-blue-400">&gt;</span>
    </div>
    <div><span class="text-blue-400">&lt;/iframe&gt;</span></div>
  </div>

</div>

<!-- 
SPEAKER NOTES:
Let's see how a user interacts with this.
They just add an item to a list. That's it.
Behind the scenes, we use an embedded iframe to display the result back to them.
Note the 'token=[SECURE]' part - this is key.
-->

---
layout: default
---

# 🛡️ "Defense in Depth" Strategy

<div class="mt-4 text-slate-500">Four concentric layers of security ensuring zero leakage.</div>

<div class="mt-10 grid grid-cols-2 gap-6">

<v-clicks>

<div class="card-prem p-5 flex items-start gap-4">
  <div class="text-3xl bg-blue-100 p-2 rounded-lg">🔒</div>
  <div>
    <h4 class="text-[#0047BB] font-bold">1. Strict CSP & Origin Locking</h4>
    <p class="text-sm text-slate-600 mt-1">`frame-ancestors` prevents rendering unless parent is `...sharepoint.com`.</p>
  </div>
</div>

<div class="card-prem p-5 flex items-start gap-4">
  <div class="text-3xl bg-amber-100 p-2 rounded-lg">🕵️</div>
  <div>
    <h4 class="text-amber-600 font-bold">2. Server-Side Referrer Check</h4>
    <p class="text-sm text-slate-600 mt-1">Rejects any request without verifiable Intranet referrer header.</p>
  </div>
</div>

<div class="card-prem p-5 flex items-start gap-4">
  <div class="text-3xl bg-emerald-100 p-2 rounded-lg">🔑</div>
  <div>
    <h4 class="text-emerald-600 font-bold">3. Security Boundary</h4>
    Embed access is protected by: <br>
     <p class="text-sm text-slate-600 mt-1">🔑 Token </p>
     <p class="text-sm text-slate-600 mt-1">🌐 IP Whitelisting Prevents unauthorized iframe or API access</p>
  </div>
</div>

<div class="card-prem p-5 flex items-start gap-4">
  <div class="text-3xl bg-slate-100 p-2 rounded-lg flex items-center justify-center">
    <!-- Inline SVG for absolute reliability -->
    <svg viewBox="0 0 24 24" class="text-3xl text-slate-600 h-[1em] w-[1em]" xmlns="http://www.w3.org/2000/svg">
      <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
        <line x1="1" y1="1" x2="23" y2="23"/>
      </g>
    </svg>
  </div>
  <div>
    <h4 class="text-slate-600 font-bold">4. Public Invisibility</h4>
    <p class="text-sm text-slate-600 mt-1">Post Type: `public => false`. Excluded from search & archives.</p>
  </div>
</div>

</v-clicks>

</div>

<!-- 
SPEAKER NOTES:
Now, you might ask: "Is it safe?"
Yes. We use Defense in Depth.
Even if someone guesses the URL, the CSP blocks them.
Even if they spoof the CSP, the Referrer check blocks them.
Even if they bypass that, the Token rotates.
And finally, the content is just INVISIBLE to the public internet.
-->

---
layout: two-cols
---

# 🔧 Technical Implementation

### WordPress Plugin Strategy

<div class="mt-6 space-y-4">
<v-clicks>

  <div class="bg-blue-50 p-3 rounded-lg border-l-4 border-blue-500">
    <strong class="block text-blue-800">Hidden Post Type</strong>
    <span class="text-sm text-blue-600">`sp_product`: No frontend presence, no indexing.</span>
  </div>

  <div class="bg-purple-50 p-3 rounded-lg border-l-4 border-purple-500">
    <strong class="block text-purple-800">API Connectivity</strong>
    <span class="text-sm text-purple-600">Custom REST Endpoint with Key Validation.</span>
  </div>

  <div class="bg-red-50 p-3 rounded-lg border-l-4 border-red-500">
    <strong class="block text-red-800">Display Interception</strong>
    <span class="text-sm text-red-600">Hook `send_headers` (CSP) & `template_redirect` (Referrer).</span>
  </div>

</v-clicks>
</div>

::right::

<div class="mt-14 shadow-2xl rounded-lg overflow-hidden border border-gray-200">

```php {all|2-4|6-9|all}
// Security Enforcement
add_action('send_headers', function() {
    $allowed = 'https://demo...sharepoint.com';
    header("Content-Security-Policy: ... $allowed");
});

// Access Control
if (strpos($referer, 'sharepoint.com') === false) {
    wp_die('403 Forbidden', 'Access Denied');
}
```

</div>

<!-- 
SPEAKER NOTES:
Here is the code that enforces those rules.
Simple, robust PHP hooks that run before any content is served.
-->

---
layout: center
class: text-center
---

# 👥 Operational Governance

<div class="overflow-x-auto mt-10 w-full max-w-5xl">
  <table class="w-full text-sm text-left border-separate border-spacing-y-3">
    <thead class="bg-slate-100 text-[#0047BB] uppercase font-bold tracking-wider">
      <tr>
        <th class="px-6 py-4 rounded-l-lg">Role</th>
        <th class="px-6 py-4">Scope</th>
        <th class="px-6 py-4 rounded-r-lg">Capabilities</th>
      </tr>
    </thead>
    <tbody class="">
      <tr v-click class="bg-white shadow-sm hover:transform hover:scale-[1.01] transition-all duration-200">
        <td class="px-6 py-5 font-bold text-[#0047BB] border-l-4 border-[#0047BB] rounded-l-lg">Site Owner</td>
        <td class="px-6 py-5">🏢 Intranet (WeBred)</td>
        <td class="px-6 py-5 rounded-r-lg">
          <div class="flex flex-col gap-1 text-slate-700">
            <span>✅ Add/Edit Products</span>
            <span>✅ Manage Automations</span>
          </div>
        </td>
      </tr>
      <tr v-click class="bg-white shadow-sm mt-4 hover:transform hover:scale-[1.01] transition-all duration-200">
        <td class="px-6 py-5 font-medium text-slate-700 border-l-4 border-slate-300 rounded-l-lg">Site Member</td>
        <td class="px-6 py-5">🏢 Intranet (WeBred)</td>
        <td class="px-6 py-5 rounded-r-lg">
          <div class="flex flex-col gap-1 text-slate-700">
            <span>✅ Edit Products</span>
            <span class="text-red-500 font-bold bg-red-50 px-2 py-0.5 rounded w-max">🚫 No Auto Config</span>
          </div>
        </td>
      </tr>
      <tr v-click class="bg-red-50 shadow-sm mt-4 hover:transform hover:scale-[1.01] transition-all duration-200">
        <td class="px-6 py-5 font-bold text-[#D71920] border-l-4 border-[#D71920] rounded-l-lg">Public User</td>
        <td class="px-6 py-5">🌍 Public Internet</td>
        <td class="px-6 py-5 rounded-r-lg font-bold text-[#D71920]">
           ⛔ STRICTLY BLOCKED
        </td>
      </tr>
    </tbody>
  </table>
</div>

<!-- 
SPEAKER NOTES:
And finally, who controls what?
Marketing (Site Owners) fully control the content.
Staff (Members) can edit but not break the logic.
The Public gets nothing.
-->

---
layout: default
---

# 🔄 Full-Cycle Data Simulation

<div class="grid grid-cols-5 gap-4 items-center mt-12 px-8">

<!-- Node 1: SharePoint -->
<div class="flex flex-col items-center">
<div v-click="1" class="text-xs font-bold text-[#0047BB] mb-2 animate-pulse">📝 NEW</div>
<div class="w-20 h-20 bg-white border-4 border-[#0047BB] rounded-xl flex items-center justify-center text-3xl shadow-lg">
🏢
</div>
<div class="text-sm font-bold text-[#0047BB] mt-2">SharePoint</div>
</div>

<!-- Arrow 1 + Data Packet -->
<div class="relative h-20 flex items-center justify-center">
<div class="absolute w-full h-1 bg-slate-200 rounded"></div>
<div v-click="2" v-motion :initial="{ x: -60, opacity: 0 }" :enter="{ x: 60, opacity: 1, transition: { duration: 800 } }" class="absolute bg-[#0047BB] text-white text-[10px] font-mono font-bold px-3 py-1 rounded-full shadow-lg z-10">
0101...
</div>
</div>

<!-- Node 2: Automate -->
<div class="flex flex-col items-center">
<div v-click="3" class="text-xs font-bold text-purple-600 mb-2 animate-pulse">⚙️ PROCESS</div>
<div class="w-20 h-20 bg-white border-4 border-purple-600 rounded-xl flex items-center justify-center text-3xl shadow-lg">
⚡
</div>
<div class="text-sm font-bold text-purple-600 mt-2">Automate</div>
</div>

<!-- Arrow 2 + Data Packet -->
<div class="relative h-20 flex items-center justify-center">
<div class="absolute w-full h-1 bg-slate-200 rounded"></div>
<div v-click="4" v-motion :initial="{ x: -60, opacity: 0 }" :enter="{ x: 60, opacity: 1, transition: { duration: 800 } }" class="absolute bg-purple-600 text-white text-[10px] font-mono font-bold px-3 py-1 rounded-full shadow-lg z-10">
{JSON}
</div>
</div>

<!-- Node 3: WordPress -->
<div class="flex flex-col items-center">
<div v-click="5" class="text-xs font-bold text-emerald-600 mb-2 animate-pulse">💾 SAVED</div>
<div class="w-20 h-20 bg-white border-4 border-emerald-600 rounded-xl flex items-center justify-center text-3xl shadow-lg">
🌐
</div>
<div class="text-sm font-bold text-emerald-600 mt-2">WordPress</div>
</div>

</div>

<!-- Return Path -->
<div class="relative h-16 mx-8 mt-4">
<div v-click="6" class="absolute inset-x-0 top-1/2 border-t-2 border-dashed border-[#D71920] opacity-30"></div>
<div v-click="7" v-motion :initial="{ x: '100%', opacity: 0 }" :enter="{ x: '0%', opacity: 1, transition: { duration: 1200 } }" class="absolute right-0 top-1/2 -translate-y-1/2 bg-[#D71920] text-white text-[10px] font-mono font-bold px-3 py-1 rounded-full shadow-lg flex items-center gap-1">
🔑 TOKEN/🌐 IP Whitelisting
</div>
<div v-click="8" class="absolute left-8 top-1/2 -translate-y-1/2 bg-white border-2 border-[#D71920] px-3 py-1 rounded-lg shadow-md">
<span class="text-xs font-bold text-[#D71920]">🖼️ Embed Loaded</span>
</div>
</div>

<!-- Terminal Log -->
<div class="mx-8 mt-6 bg-[#0d1117] rounded-lg border border-slate-700 p-4 font-mono text-[11px] text-green-400 shadow-xl">
<div class="flex gap-1 mb-3">
<div class="w-2.5 h-2.5 rounded-full bg-red-500"></div>
<div class="w-2.5 h-2.5 rounded-full bg-yellow-500"></div>
<div class="w-2.5 h-2.5 rounded-full bg-green-500"></div>
</div>
<div class="space-y-1">
<div v-click="1"><span class="text-blue-400">[SP]</span> Item Created: "Promo Q1"</div>
<div v-click="2"><span class="text-blue-400">[TX]</span> Binary → Automate <span class="text-slate-500">████████</span></div>
<div v-click="4"><span class="text-purple-400">[TX]</span> JSON → WordPress <span class="text-slate-500">████████</span></div>
<div v-click="5"><span class="text-emerald-400">[WP]</span> 200 OK - Data Persisted</div>
<div v-click="7"><span class="text-red-400">[RX]</span> Token/IP Whitelisting → SharePoint Embed</div>
<div v-click="8"><span class="text-green-400">[OK]</span> iFrame Rendered ✓</div>
</div>
</div>

<!-- 
SPEAKER NOTES:
1. Write Path: Data moves left to right (SharePoint -> Automation -> WP).
2. Read Path: Data moves right to left (WP -> SharePoint Embed), but ONLY via the secure channel.
-->

---
layout: default
background: https://images.unsplash.com/photo-1557683316-973673baf926?q=80&w=2029&auto=format&fit=crop
class: text-center text-white
---

<div class="absolute inset-0 bg-[#0047BB]/80 backdrop-blur-sm z-0"></div>

<div class="relative z-10 flex flex-col justify-center items-center h-full">

  <h1 class="text-6xl font-extrabold mb-8 tracking-tight text-white drop-shadow-md">
    Ready for Deployment
  </h1>
  
  <div class="text-2xl mt-4 max-w-3xl mx-auto font-light leading-relaxed opacity-90">
    <span class="block mb-2 font-bold text-white">Compliance by Design.</span>
  </div>

  <div class="mt-16">
    <a href="https://demo081225.sharepoint.com/sites/WeBred/" target="_blank" class="px-8 py-4 bg-white text-[#0047BB] rounded-full font-bold text-xl shadow-2xl hover:scale-105 transition-transform cursor-pointer border-4 border-blue-300/50 inline-block no-underline">
      🚀 Launch Demo
    </a>
    <div class="mt-4 text-sm text-blue-200 font-mono opacity-80">
      https://demo081225.sharepoint.com/sites/WeBred/
    </div>
  </div>

</div>
