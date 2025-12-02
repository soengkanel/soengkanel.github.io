---
layout: post
title: "[ALGO] Understanding Binary Search: A Simple Guide"
tags: [Algorithms, Computer Science, Binary Search, Visualization]
thumbnail: /images/binary_search_thumbnail.png
---

Have you ever played the "Guess the Number" game?

I pick a number between 1 and 100. You guess, and I tell you "Higher" or "Lower".

If you guess **1**, then **2**, then **3**... you are doing a **Linear Search**. It could take you 100 guesses!

But if you guess **50** (the middle), and I say "Lower", you instantly know the number is between 1 and 49. You just eliminated half the possibilities in one go! That is the power of **Binary Search**.

## What is Binary Search?

Binary Search is an efficient algorithm for finding an item from a **sorted list** of items. It works by repeatedly dividing in half the portion of the list that could contain the item, until you've narrowed down the possible locations to just one.

### The Rules
1. The list **MUST be sorted** (e.g., 1, 3, 5, 7, 9...).
2. You always check the **middle** element.
3. If the middle is too low, you discard the left half.
4. If the middle is too high, you discard the right half.

## Visualizing the Algorithm

Let's see it in action. Below is a sorted list of numbers. Click "Start Search" to find the number **37**.

<div class="algo-container" style="margin: 2rem 0; padding: 1.5rem; background: #1e1e1e; border-radius: 12px; color: white; text-align: center;">
  <div id="array-container" style="display: flex; justify-content: center; gap: 5px; margin-bottom: 20px; flex-wrap: wrap;">
    <!-- Array elements will be generated here -->
  </div>
  <div id="status-text" style="margin-bottom: 15px; font-family: monospace; font-size: 1.1rem; height: 1.5em;">Ready to search for 37...</div>
  <button id="start-btn" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem;">Start Search</button>
  <button id="reset-btn" style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; margin-left: 10px;">Reset</button>
</div>

<script>
(function() {
  const container = document.getElementById('array-container');
  const status = document.getElementById('status-text');
  const startBtn = document.getElementById('start-btn');
  const resetBtn = document.getElementById('reset-btn');
  
  // Sorted array
  const data = [2, 5, 8, 12, 16, 23, 37, 45, 56, 72, 91];
  const target = 37;
  let elements = [];
  let isSearching = false;

  function createArray() {
    container.innerHTML = '';
    elements = [];
    data.forEach((num, index) => {
      const el = document.createElement('div');
      el.textContent = num;
      el.style.width = '40px';
      el.style.height = '40px';
      el.style.display = 'flex';
      el.style.alignItems = 'center';
      el.style.justifyContent = 'center';
      el.style.background = '#333';
      el.style.border = '1px solid #555';
      el.style.borderRadius = '4px';
      el.style.transition = 'all 0.3s ease';
      container.appendChild(el);
      elements.push(el);
    });
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async function binarySearch() {
    if (isSearching) return;
    isSearching = true;
    startBtn.disabled = true;
    
    let left = 0;
    let right = data.length - 1;
    
    while (left <= right) {
      // Reset styles for current range
      elements.forEach((el, i) => {
        if (i < left || i > right) {
          el.style.opacity = '0.3'; // Dim ignored elements
          el.style.background = '#222';
        } else {
          el.style.opacity = '1';
          el.style.background = '#333';
        }
      });

      const mid = Math.floor((left + right) / 2);
      
      // Highlight Middle
      elements[mid].style.background = '#f39c12'; // Orange for current check
      elements[mid].style.transform = 'scale(1.1)';
      status.textContent = `Checking middle index ${mid} (Value: ${data[mid]})...`;
      
      await sleep(1500);

      if (data[mid] === target) {
        elements[mid].style.background = '#28a745'; // Green for found
        status.textContent = `Found ${target} at index ${mid}!`;
        isSearching = false;
        startBtn.disabled = false;
        return;
      } else if (data[mid] < target) {
        status.textContent = `${data[mid]} is too low. Ignoring left half.`;
        left = mid + 1;
      } else {
        status.textContent = `${data[mid]} is too high. Ignoring right half.`;
        right = mid - 1;
      }
      
      await sleep(1500);
      elements[mid].style.transform = 'scale(1)';
    }
    
    status.textContent = 'Not found.';
    isSearching = false;
    startBtn.disabled = false;
  }

  startBtn.addEventListener('click', binarySearch);
  resetBtn.addEventListener('click', () => {
    createArray();
    status.textContent = 'Ready to search for 37...';
    isSearching = false;
    startBtn.disabled = false;
  });

  createArray();
})();
</script>

## How it Works (The Code)

Here is how you would write this in Golang. It's clean and efficient!

```go
package main

import "fmt"

func binarySearch(arr []int, target int) int {
    left := 0
    right := len(arr) - 1

    for left <= right {
        mid := (left + right) / 2

        if arr[mid] == target {
            return mid // Found it!
        } else if arr[mid] < target {
            left = mid + 1 // Discard left half
        } else {
            right = mid - 1 // Discard right half
        }
    }

    return -1 // Not found
}

func main() {
    items := []int{2, 5, 8, 12, 16, 23, 37, 45, 56, 72, 91}
    fmt.Println(binarySearch(items, 37)) // Output: 6
}
```

## Why is it so fast?

In computer science, we measure speed using **Big O Notation**.

*   **Linear Search** is **O(n)**. If you have 1,000,000 items, you might have to check 1,000,000 times.
*   **Binary Search** is **O(log n)**. If you have 1,000,000 items, it takes **only 20 steps** to find any number!

Every time you make a check, you cut the problem size in half. This makes Binary Search incredibly powerful for large datasets.

### Summary
1.  **Divide** the search space in half.
2.  **Conquer** by checking the middle.
3.  **Repeat** until found.

Next time you look up a word in a dictionary, remember: you are running a Binary Search algorithm in your head!
