---
layout: post
title: "[AI] Flutter for Web Developers: Part 2 - State & Lifecycle"
date: 2026-01-23 09:00:00 +0700
categories: [AI]
tags: [Flutter, Dart, State Management, React, Web Development]
author: Soeng Kanel
thumbnail: /images/flutter_state_management_thumbnail.png
description: "In React, we use Hooks. In Flutter, we use State Objects. Learn how to manage the 'Rebuild' without losing your mind."
---

If you read [Part 1](/ai/2025/12/06/[AI]-flutter-for-web-developers/), you know that Flutter is about **Wrapping**. But once you wrap your Cat widget in a `Container`, how do you make it move?

In React, you have `useState`. In Flutter, things are a bit more... "Institutional."

## The Mental Shift: Functions vs. Instances

In React (Functional Components):
*   Your component is a **Function**.
*   When state changes, the **Function runs again**.
*   Variables inside are "re-calculated" every time.

In Flutter (`StatefulWidget`):
*   Your widget is a **Class**, but your State is **another Class**.
*   The Widget is immutable (it dies and is reborn).
*   The **State object** survives. It stays in memory while the widget tree rebuilds around it.

## Interactive: The "State Survival" Lab

Click the "Rebuild Widget" button. Notice how the **Widget Tree** flashes (indicating it was recreated), but the **Counter** inside the State Object remains the same. 

<div class="animation-container" style="border: 2px solid #0277BD; border-radius: 12px; padding: 20px; text-align: center; background: #e1f5fe; margin-bottom: 2rem; font-family: sans-serif;">
  <h3 style="margin-top: 0; color: #01579B;">Interactive: Widget vs State 🔬</h3>
  
  <div style="display: flex; gap: 10px; justify-content: center; margin-bottom: 15px;">
    <button id="incrementBtn" style="padding: 10px 20px; background: #0288D1; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">➕ setState(() => count++)</button>
    <button id="rebuildBtn" style="padding: 10px 20px; background: #FF9800; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">🔄 Rebuild Widget Tree</button>
  </div>

  <div style="display: flex; justify-content: space-around; align-items: stretch; gap: 20px;">
    <!-- Widget View -->
    <div style="flex: 1; background: white; padding: 15px; border-radius: 8px; border: 2px solid #ccc;">
      <h4 style="margin-top: 0;">UI (The Widget)</h4>
      <div id="widgetVisual" style="font-size: 32px; padding: 20px; background: #f5f5f5; border-radius: 50%; width: 60px; height: 60px; margin: 0 auto; display: flex; align-items: center; justify-content: center; transition: transform 0.1s;">0</div>
      <p style="font-size: 12px; color: #666; margin-top: 10px;">I am temporary.<br>I am recreated on every frame.</p>
    </div>

    <!-- State View -->
    <div style="flex: 1; background: #fff9c4; padding: 15px; border-radius: 8px; border: 2px solid #fbc02d;">
      <h4 style="margin-top: 0;">Memory (The State)</h4>
      <div id="stateVisual" style="font-size: 32px; font-weight: bold; color: #f57f17;">0</div>
      <p style="font-size: 12px; color: #666; margin-top: 10px;">I am persistent.<br>I hold the 'Source of Truth'.</p>
    </div>
  </div>

  <div id="logArea" style="margin-top: 15px; text-align: left; background: #263238; padding: 10px; border-radius: 8px; color: #80cbc4; font-family: monospace; font-size: 13px; height: 60px; overflow-y: hidden;">
    > System Ready...
  </div>
</div>

<script>
(function() {
    let count = 0;
    const widgetVisual = document.getElementById('widgetVisual');
    const stateVisual = document.getElementById('stateVisual');
    const logArea = document.getElementById('logArea');
    
    function log(msg) {
        logArea.innerHTML = `> ${msg}<br>` + logArea.innerHTML.split('<br>').slice(0, 2).join('<br>');
    }

    function updateUI() {
        widgetVisual.textContent = count;
        stateVisual.textContent = count;
    }

    document.getElementById('incrementBtn').onclick = () => {
        count++;
        log("setState() called. Marking dirty...");
        // Simulate Rebuild
        widgetVisual.style.transform = 'scale(1.2)';
        setTimeout(() => { 
            widgetVisual.style.transform = 'scale(1)';
            updateUI(); 
            log("Widget Rebuilt with new data.");
        }, 150);
    };

    document.getElementById('rebuildBtn').onclick = () => {
        log("Parent Rebuild! Widget is destroyed/recreated.");
        widgetVisual.style.opacity = '0';
        setTimeout(() => {
            widgetVisual.style.opacity = '1';
            updateUI();
            log("State object was preserved.");
        }, 200);
    };
})();
</script>

## Why Web Devs get confused

In React, you do this:
```javascript
function Counter() {
  const [count, setCount] = useState(0); 
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

In Flutter, you do this:
```dart
class Counter extends StatefulWidget {
  @override
  _CounterState createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  int count = 0; // Persistent variable

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: () => setState(() => count++),
      child: Text("$count"),
    );
  }
}
```

### The "Gotcha": `setState` isn't magic
In React, `setCount` updates the value and schedules a render.
In Flutter, `setState` does exactly **one** thing: It tells Flutter "This State object is dirty. Please run the `build` method again at the next frame."

If you forget to call `setState`, your variable `count` **will still increase** in memory, but your screen will stay at `0`.

## The Lifecycle Cheat Sheet

If you are coming from React Hooks, here is your translation guide:

| React Hook | Flutter Equivalent | When it runs |
| :--- | :--- | :--- |
| `useEffect(() => {}, [])` | `initState()` | Once, when the widget enters the tree. |
| `useEffect(() => {})` | `build()` | Every single time the UI needs updating. |
| `useMemo() / useCallback()` | *Not needed* | Flutter's `build` is highly optimized; just create objects. |
| `useEffect(() => { return () => ... }, [])` | `dispose()` | When the widget is removed (Unmount). |

---

## Conclusion

Mastering Flutter isn't about learning a new language (Dart is just Java-flavored JavaScript anyway). It's about accepting that **UI is a reflection of State**.

1.  **Widgets** are just blueprints. They are cheap and disposable.
2.  **State** is the brain. It lives outside the blueprint.
3.  **setState** is the bridge that tells the blueprint to update.

Next time, we'll look at **Flexbox vs. Row/Column**—and why your layout is probably overflowing.
