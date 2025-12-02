---
layout: post
title: "[ALGO] Big O Notation: The Speed of Code"
tags: [Algorithms, Computer Science, Big O, Optimization]
thumbnail: 
---

Imagine you are a librarian.

*   **Scenario A:** A reader asks for the first book on the shelf. You grab it instantly. **(Fast)**
*   **Scenario B:** A reader asks for a specific book, but the library is a mess. You have to check every single book until you find it. **(Slow)**
*   **Scenario C:** The library is perfectly sorted. You go to the middle, check if the title is before or after, and repeat. **(Very Fast)**

In programming, **Big O Notation** is how we measure this "speed". It doesn't measure seconds; it measures **how the number of operations grows** as the input size ($n$) grows.

## Visualizing the Speed

See how different algorithms perform as the data gets larger ($n$).

<div class="chart-container" style="position: relative; height:400px; width:100%; margin: 2rem 0; background: #1e1e1e; border-radius: 12px; padding: 1rem;">
  <canvas id="bigOChart"></canvas>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  const ctx = document.getElementById('bigOChart').getContext('2d');
  
  // Generate data points
  const labels = Array.from({length: 20}, (_, i) => i + 1);
  
  const dataO1 = labels.map(() => 1);
  const dataOlogN = labels.map(x => Math.log2(x));
  const dataOn = labels.map(x => x);
  const dataOn2 = labels.map(x => x * x);

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'O(1) - Constant',
          data: dataO1,
          borderColor: '#28a745', // Green
          borderWidth: 3,
          tension: 0.4
        },
        {
          label: 'O(log n) - Logarithmic',
          data: dataOlogN,
          borderColor: '#17a2b8', // Cyan
          borderWidth: 3,
          tension: 0.4
        },
        {
          label: 'O(n) - Linear',
          data: dataOn,
          borderColor: '#ffc107', // Yellow
          borderWidth: 3,
          tension: 0.4
        },
        {
          label: 'O(n²) - Quadratic',
          data: dataOn2,
          borderColor: '#dc3545', // Red
          borderWidth: 3,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: '#333' },
          ticks: { color: '#aaa' },
          title: { display: true, text: 'Operations', color: '#aaa' }
        },
        x: {
          grid: { color: '#333' },
          ticks: { color: '#aaa' },
          title: { display: true, text: 'Input Size (n)', color: '#aaa' }
        }
      },
      plugins: {
        legend: {
          labels: { color: '#fff' }
        }
      }
    }
  });
</script>

## 1. O(1) - Constant Time (The Best)

No matter how much data you have, the operation takes the same amount of time.

**Example:** Accessing an array by index.

```go
func getFirstItem(items []string) string {
    return items[0] // Always takes 1 step
}
```

## 2. O(log n) - Logarithmic Time (Great)

The time grows very slowly. Usually involves dividing the problem in half (like Binary Search).

**Example:** Finding a number in a sorted list.

```go
// See our Binary Search article for the full code!
// If you double the inputs, you only add ONE extra step.
```

## 3. O(n) - Linear Time (Okay)

If you double the data, you double the time. This happens when you have to loop through every item.

**Example:** Finding the maximum number in an unsorted list.

```go
func findMax(numbers []int) int {
    maxVal := numbers[0]
    for _, num := range numbers {
        if num > maxVal {
            maxVal = num
        }
    }
    return maxVal
}
```

## 4. O(n²) - Quadratic Time (Slow)

If you double the data, the time quadruples! This usually happens with "nested loops" (a loop inside a loop). Avoid this for large datasets.

**Example:** Checking for duplicates by comparing every number to every other number.

```go
func hasDuplicates(numbers []int) bool {
    for i := 0; i < len(numbers); i++ {
        for j := 0; j < len(numbers); j++ {
            if i != j && numbers[i] == numbers[j] {
                return true
            }
        }
    }
    return false
}
```

## Summary Cheat Sheet

| Notation | Name | Speed | Analogy |
| :--- | :--- | :--- | :--- |
| **O(1)** | Constant | ⚡ Instant | Knowing the first page of a book is page 1. |
| **O(log n)** | Logarithmic | 🚀 Fast | Finding a word in a dictionary. |
| **O(n)** | Linear | 🚶 Moderate | Reading a book page by page. |
| **O(n²)** | Quadratic | 🐢 Slow | Comparing every page to every other page. |

Always aim for **O(1)** or **O(log n)** when possible!
