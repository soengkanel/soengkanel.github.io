---
layout: post
title: "[Math] Graphing Functions - Visualization and Analysis"
tags: [Calculus, Functions, Visualization, Plotly]
thumbnail: /images/thumbnails/2024-01-21-graphing-functions.png
---

Graphing transforms abstract equations into visual representations. Understanding how to sketch and interpret graphs is essential for analyzing function behavior.

## The Coordinate System

The Cartesian plane consists of two perpendicular axes:

- **x-axis**: horizontal, represents the independent variable
- **y-axis**: vertical, represents the dependent variable

A point $(a, b)$ means: move $a$ units horizontally, then $b$ units vertically from the origin.

## Key Features of Graphs

### Intercepts

**x-intercepts**: Where the graph crosses the x-axis. Set $y = 0$ and solve for $x$.

**y-intercept**: Where the graph crosses the y-axis. Set $x = 0$ and evaluate $f(0)$.

**Example**: For $f(x) = x^2 - 4$

- x-intercepts: $x^2 - 4 = 0 \Rightarrow x = \pm 2$
- y-intercept: $f(0) = -4$

### Domain and Range

**Domain**: All valid input values (x-values).

**Range**: All possible output values (y-values).

For $f(x) = \sqrt{x}$:
- Domain: $x \geq 0$ (can't take square root of negative)
- Range: $y \geq 0$ (square root is always non-negative)

### Symmetry

**Even functions**: Symmetric about the y-axis. $f(-x) = f(x)$

Examples: $x^2$, $\cos x$, $|x|$

**Odd functions**: Symmetric about the origin. $f(-x) = -f(x)$

Examples: $x^3$, $\sin x$, $\tan x$

## Common Function Types

### Linear Functions

$$f(x) = mx + b$$

- $m$ = slope (rise over run)
- $b$ = y-intercept
- Graph is always a straight line

**Slope formula** between two points $(x_1, y_1)$ and $(x_2, y_2)$:

$$m = \frac{y_2 - y_1}{x_2 - x_1}$$

<div id="linear-graph" style="width:100%;max-width:700px;height:400px;margin:20px auto;"></div>

<script>
(function() {
  var x = [];
  for (var i = -5; i <= 5; i += 0.1) { x.push(i); }

  var trace1 = {
    x: x,
    y: x.map(v => 2*v + 1),
    type: 'scatter',
    mode: 'lines',
    name: 'y = 2x + 1',
    line: { color: '#3b82f6', width: 2 }
  };

  var trace2 = {
    x: x,
    y: x.map(v => -0.5*v + 2),
    type: 'scatter',
    mode: 'lines',
    name: 'y = -0.5x + 2',
    line: { color: '#ef4444', width: 2 }
  };

  var trace3 = {
    x: x,
    y: x.map(v => v),
    type: 'scatter',
    mode: 'lines',
    name: 'y = x',
    line: { color: '#10b981', width: 2 }
  };

  var layout = {
    title: 'Linear Functions',
    xaxis: { title: 'x', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-5, 5] },
    yaxis: { title: 'y', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-5, 10] },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Source Sans 3, sans-serif' },
    legend: { x: 0.02, y: 0.98 }
  };

  Plotly.newPlot('linear-graph', [trace1, trace2, trace3], layout, {responsive: true});
})();
</script>

### Quadratic Functions

$$f(x) = ax^2 + bx + c$$

Graph is a parabola:
- Opens upward if $a > 0$
- Opens downward if $a < 0$

**Vertex form**: $f(x) = a(x - h)^2 + k$ where $(h, k)$ is the vertex.

**Vertex location**: $h = -\frac{b}{2a}$, then $k = f(h)$

<div id="quadratic-graph" style="width:100%;max-width:700px;height:400px;margin:20px auto;"></div>

<script>
(function() {
  var x = [];
  for (var i = -4; i <= 4; i += 0.1) { x.push(i); }

  var trace1 = {
    x: x,
    y: x.map(v => v*v),
    type: 'scatter',
    mode: 'lines',
    name: 'y = x²',
    line: { color: '#3b82f6', width: 2 }
  };

  var trace2 = {
    x: x,
    y: x.map(v => -v*v + 4),
    type: 'scatter',
    mode: 'lines',
    name: 'y = -x² + 4',
    line: { color: '#ef4444', width: 2 }
  };

  var trace3 = {
    x: x,
    y: x.map(v => 0.5*(v-1)*(v-1) - 2),
    type: 'scatter',
    mode: 'lines',
    name: 'y = 0.5(x-1)² - 2',
    line: { color: '#10b981', width: 2 }
  };

  var layout = {
    title: 'Quadratic Functions (Parabolas)',
    xaxis: { title: 'x', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-4, 4] },
    yaxis: { title: 'y', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-5, 10] },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Source Sans 3, sans-serif' },
    legend: { x: 0.02, y: 0.98 }
  };

  Plotly.newPlot('quadratic-graph', [trace1, trace2, trace3], layout, {responsive: true});
})();
</script>

### Polynomial Functions

$$f(x) = a_nx^n + a_{n-1}x^{n-1} + \cdots + a_1x + a_0$$

Key behaviors:
- **End behavior** depends on leading term $a_nx^n$
- Maximum of $n$ x-intercepts (real roots)
- Maximum of $n-1$ turning points

| Degree | Leading Coefficient | Left End | Right End |
|--------|---------------------|----------|-----------|
| Even   | Positive            | $+\infty$ | $+\infty$ |
| Even   | Negative            | $-\infty$ | $-\infty$ |
| Odd    | Positive            | $-\infty$ | $+\infty$ |
| Odd    | Negative            | $+\infty$ | $-\infty$ |

<div id="polynomial-graph" style="width:100%;max-width:700px;height:400px;margin:20px auto;"></div>

<script>
(function() {
  var x = [];
  for (var i = -3; i <= 3; i += 0.05) { x.push(i); }

  var trace1 = {
    x: x,
    y: x.map(v => v*v*v),
    type: 'scatter',
    mode: 'lines',
    name: 'y = x³ (cubic)',
    line: { color: '#3b82f6', width: 2 }
  };

  var trace2 = {
    x: x,
    y: x.map(v => v*v*v*v - 2*v*v),
    type: 'scatter',
    mode: 'lines',
    name: 'y = x⁴ - 2x² (quartic)',
    line: { color: '#ef4444', width: 2 }
  };

  var trace3 = {
    x: x,
    y: x.map(v => -v*v*v + 3*v),
    type: 'scatter',
    mode: 'lines',
    name: 'y = -x³ + 3x',
    line: { color: '#10b981', width: 2 }
  };

  var layout = {
    title: 'Polynomial Functions',
    xaxis: { title: 'x', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-3, 3] },
    yaxis: { title: 'y', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-5, 5] },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Source Sans 3, sans-serif' },
    legend: { x: 0.02, y: 0.98 }
  };

  Plotly.newPlot('polynomial-graph', [trace1, trace2, trace3], layout, {responsive: true});
})();
</script>

### Rational Functions

$$f(x) = \frac{P(x)}{Q(x)}$$

**Vertical asymptotes**: Where $Q(x) = 0$ (denominator equals zero).

**Horizontal asymptotes**: Compare degrees of $P(x)$ and $Q(x)$.

**Example**: $f(x) = \frac{1}{x-2}$
- Vertical asymptote: $x = 2$
- Horizontal asymptote: $y = 0$

<div id="rational-graph" style="width:100%;max-width:700px;height:400px;margin:20px auto;"></div>

<script>
(function() {
  var x1 = [], x2 = [], x3 = [], x4 = [];
  for (var i = -5; i < 0; i += 0.05) { x1.push(i); }
  for (var i = 0.05; i <= 5; i += 0.05) { x2.push(i); }
  for (var i = -5; i < 2; i += 0.05) { x3.push(i); }
  for (var i = 2.05; i <= 5; i += 0.05) { x4.push(i); }

  var trace1a = {
    x: x1,
    y: x1.map(v => 1/v),
    type: 'scatter',
    mode: 'lines',
    name: 'y = 1/x',
    line: { color: '#3b82f6', width: 2 },
    legendgroup: 'group1'
  };

  var trace1b = {
    x: x2,
    y: x2.map(v => 1/v),
    type: 'scatter',
    mode: 'lines',
    line: { color: '#3b82f6', width: 2 },
    legendgroup: 'group1',
    showlegend: false
  };

  var trace2a = {
    x: x3,
    y: x3.map(v => 1/(v-2)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = 1/(x-2)',
    line: { color: '#ef4444', width: 2 },
    legendgroup: 'group2'
  };

  var trace2b = {
    x: x4,
    y: x4.map(v => 1/(v-2)),
    type: 'scatter',
    mode: 'lines',
    line: { color: '#ef4444', width: 2 },
    legendgroup: 'group2',
    showlegend: false
  };

  var layout = {
    title: 'Rational Functions with Asymptotes',
    xaxis: { title: 'x', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-5, 5] },
    yaxis: { title: 'y', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-10, 10] },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Source Sans 3, sans-serif' },
    legend: { x: 0.02, y: 0.98 },
    shapes: [
      { type: 'line', x0: 0, x1: 0, y0: -10, y1: 10, line: { color: '#3b82f6', width: 1, dash: 'dash' } },
      { type: 'line', x0: 2, x1: 2, y0: -10, y1: 10, line: { color: '#ef4444', width: 1, dash: 'dash' } }
    ]
  };

  Plotly.newPlot('rational-graph', [trace1a, trace1b, trace2a, trace2b], layout, {responsive: true});
})();
</script>

### Exponential Functions

$$f(x) = a \cdot b^x$$

- Always positive (if $a > 0$)
- Horizontal asymptote at $y = 0$
- Growth if $b > 1$, decay if $0 < b < 1$

<div id="exponential-graph" style="width:100%;max-width:700px;height:400px;margin:20px auto;"></div>

<script>
(function() {
  var x = [];
  for (var i = -3; i <= 3; i += 0.1) { x.push(i); }

  var trace1 = {
    x: x,
    y: x.map(v => Math.pow(2, v)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = 2ˣ (growth)',
    line: { color: '#3b82f6', width: 2 }
  };

  var trace2 = {
    x: x,
    y: x.map(v => Math.pow(0.5, v)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = (1/2)ˣ (decay)',
    line: { color: '#ef4444', width: 2 }
  };

  var trace3 = {
    x: x,
    y: x.map(v => Math.exp(v)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = eˣ',
    line: { color: '#10b981', width: 2 }
  };

  var layout = {
    title: 'Exponential Functions',
    xaxis: { title: 'x', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-3, 3] },
    yaxis: { title: 'y', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [0, 10] },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Source Sans 3, sans-serif' },
    legend: { x: 0.02, y: 0.98 }
  };

  Plotly.newPlot('exponential-graph', [trace1, trace2, trace3], layout, {responsive: true});
})();
</script>

### Logarithmic Functions

$$f(x) = \log_b(x)$$

- Inverse of exponential
- Domain: $x > 0$
- Vertical asymptote at $x = 0$
- Passes through $(1, 0)$

<div id="logarithmic-graph" style="width:100%;max-width:700px;height:400px;margin:20px auto;"></div>

<script>
(function() {
  var x = [];
  for (var i = 0.1; i <= 10; i += 0.1) { x.push(i); }

  var trace1 = {
    x: x,
    y: x.map(v => Math.log2(v)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = log₂(x)',
    line: { color: '#3b82f6', width: 2 }
  };

  var trace2 = {
    x: x,
    y: x.map(v => Math.log(v)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = ln(x)',
    line: { color: '#ef4444', width: 2 }
  };

  var trace3 = {
    x: x,
    y: x.map(v => Math.log10(v)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = log₁₀(x)',
    line: { color: '#10b981', width: 2 }
  };

  var layout = {
    title: 'Logarithmic Functions',
    xaxis: { title: 'x', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [0, 10] },
    yaxis: { title: 'y', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-4, 4] },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Source Sans 3, sans-serif' },
    legend: { x: 0.7, y: 0.98 },
    shapes: [
      { type: 'line', x0: 0, x1: 0, y0: -4, y1: 4, line: { color: '#888', width: 1, dash: 'dash' } }
    ]
  };

  Plotly.newPlot('logarithmic-graph', [trace1, trace2, trace3], layout, {responsive: true});
})();
</script>

### Trigonometric Functions

**Sine and Cosine**:

$$y = A\sin(Bx + C) + D$$

- Amplitude: $|A|$
- Period: $\frac{2\pi}{|B|}$
- Phase shift: $-\frac{C}{B}$
- Vertical shift: $D$

<div id="trig-graph" style="width:100%;max-width:700px;height:400px;margin:20px auto;"></div>

<script>
(function() {
  var x = [];
  for (var i = -2*Math.PI; i <= 2*Math.PI; i += 0.05) { x.push(i); }

  var trace1 = {
    x: x,
    y: x.map(v => Math.sin(v)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = sin(x)',
    line: { color: '#3b82f6', width: 2 }
  };

  var trace2 = {
    x: x,
    y: x.map(v => Math.cos(v)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = cos(x)',
    line: { color: '#ef4444', width: 2 }
  };

  var trace3 = {
    x: x,
    y: x.map(v => 2*Math.sin(2*v)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = 2sin(2x)',
    line: { color: '#10b981', width: 2 }
  };

  var layout = {
    title: 'Trigonometric Functions',
    xaxis: {
      title: 'x',
      zeroline: true,
      zerolinecolor: '#888',
      gridcolor: '#ddd',
      range: [-2*Math.PI, 2*Math.PI],
      tickvals: [-2*Math.PI, -Math.PI, 0, Math.PI, 2*Math.PI],
      ticktext: ['-2π', '-π', '0', 'π', '2π']
    },
    yaxis: { title: 'y', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-3, 3] },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Source Sans 3, sans-serif' },
    legend: { x: 0.02, y: 0.98 }
  };

  Plotly.newPlot('trig-graph', [trace1, trace2, trace3], layout, {responsive: true});
})();
</script>

## Graph Transformations

Starting from $y = f(x)$:

| Transformation | Effect on Graph |
|----------------|-----------------|
| $f(x) + k$ | Shift up by $k$ |
| $f(x) - k$ | Shift down by $k$ |
| $f(x + h)$ | Shift left by $h$ |
| $f(x - h)$ | Shift right by $h$ |
| $-f(x)$ | Reflect over x-axis |
| $f(-x)$ | Reflect over y-axis |
| $af(x)$, $a > 1$ | Vertical stretch |
| $af(x)$, $0 < a < 1$ | Vertical compression |
| $f(bx)$, $b > 1$ | Horizontal compression |
| $f(bx)$, $0 < b < 1$ | Horizontal stretch |

<div id="transform-graph" style="width:100%;max-width:700px;height:400px;margin:20px auto;"></div>

<script>
(function() {
  var x = [];
  for (var i = -4; i <= 6; i += 0.1) { x.push(i); }

  var trace1 = {
    x: x,
    y: x.map(v => v*v),
    type: 'scatter',
    mode: 'lines',
    name: 'y = x² (original)',
    line: { color: '#3b82f6', width: 2 }
  };

  var trace2 = {
    x: x,
    y: x.map(v => (v-2)*(v-2)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = (x-2)² (right 2)',
    line: { color: '#ef4444', width: 2 }
  };

  var trace3 = {
    x: x,
    y: x.map(v => v*v + 3),
    type: 'scatter',
    mode: 'lines',
    name: 'y = x² + 3 (up 3)',
    line: { color: '#10b981', width: 2 }
  };

  var trace4 = {
    x: x,
    y: x.map(v => -v*v),
    type: 'scatter',
    mode: 'lines',
    name: 'y = -x² (reflect)',
    line: { color: '#f59e0b', width: 2 }
  };

  var layout = {
    title: 'Graph Transformations of y = x²',
    xaxis: { title: 'x', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-4, 6] },
    yaxis: { title: 'y', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-10, 15] },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Source Sans 3, sans-serif' },
    legend: { x: 0.02, y: 0.98 }
  };

  Plotly.newPlot('transform-graph', [trace1, trace2, trace3, trace4], layout, {responsive: true});
})();
</script>

**Order matters**: Apply transformations in this order:
1. Horizontal shifts and stretches
2. Reflections
3. Vertical stretches and shifts

## Analyzing Function Behavior

### Increasing and Decreasing

- **Increasing**: As $x$ increases, $y$ increases. Graph goes uphill left to right.
- **Decreasing**: As $x$ increases, $y$ decreases. Graph goes downhill.

Using calculus: $f'(x) > 0$ means increasing, $f'(x) < 0$ means decreasing.

### Local Extrema

**Local maximum**: Highest point in a neighborhood.

**Local minimum**: Lowest point in a neighborhood.

These occur where the graph changes from increasing to decreasing (or vice versa).

### Concavity

**Concave up**: Graph curves upward like a cup. $f''(x) > 0$

**Concave down**: Graph curves downward like a frown. $f''(x) < 0$

**Inflection point**: Where concavity changes.

<div id="analysis-graph" style="width:100%;max-width:700px;height:400px;margin:20px auto;"></div>

<script>
(function() {
  var x = [];
  for (var i = -2; i <= 4; i += 0.05) { x.push(i); }

  var f = function(v) { return v*v*v - 3*v*v + 2; };

  var trace1 = {
    x: x,
    y: x.map(f),
    type: 'scatter',
    mode: 'lines',
    name: 'f(x) = x³ - 3x² + 2',
    line: { color: '#3b82f6', width: 2 }
  };

  // Mark critical points
  var trace2 = {
    x: [0, 2],
    y: [f(0), f(2)],
    type: 'scatter',
    mode: 'markers',
    name: 'Critical points',
    marker: { color: '#ef4444', size: 10, symbol: 'circle' }
  };

  // Mark inflection point
  var trace3 = {
    x: [1],
    y: [f(1)],
    type: 'scatter',
    mode: 'markers',
    name: 'Inflection point',
    marker: { color: '#10b981', size: 10, symbol: 'diamond' }
  };

  var layout = {
    title: 'Function Analysis: f(x) = x³ - 3x² + 2',
    xaxis: { title: 'x', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-2, 4] },
    yaxis: { title: 'y', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-5, 5] },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Source Sans 3, sans-serif' },
    legend: { x: 0.02, y: 0.98 },
    annotations: [
      { x: 0, y: f(0), text: 'Local max', showarrow: true, arrowhead: 2, ax: -40, ay: -30 },
      { x: 2, y: f(2), text: 'Local min', showarrow: true, arrowhead: 2, ax: 40, ay: 30 },
      { x: 1, y: f(1), text: 'Inflection', showarrow: true, arrowhead: 2, ax: 50, ay: -20 }
    ]
  };

  Plotly.newPlot('analysis-graph', [trace1, trace2, trace3], layout, {responsive: true});
})();
</script>

## Sketching Strategy

1. **Find the domain** (where is the function defined?)
2. **Find intercepts** (where does it cross the axes?)
3. **Check symmetry** (even, odd, or neither?)
4. **Find asymptotes** (vertical, horizontal, oblique?)
5. **Determine intervals of increase/decrease**
6. **Find local maxima and minima**
7. **Determine concavity and inflection points**
8. **Plot key points and sketch**

## Piecewise Functions

Functions defined by different rules on different intervals:

$$f(x) = \begin{cases} x^2 & \text{if } x < 0 \\ 2x + 1 & \text{if } x \geq 0 \end{cases}$$

Graph each piece on its interval. Check for continuity at boundary points.

<div id="piecewise-graph" style="width:100%;max-width:700px;height:400px;margin:20px auto;"></div>

<script>
(function() {
  var x1 = [], x2 = [];
  for (var i = -4; i < 0; i += 0.1) { x1.push(i); }
  for (var i = 0; i <= 4; i += 0.1) { x2.push(i); }

  var trace1 = {
    x: x1,
    y: x1.map(v => v*v),
    type: 'scatter',
    mode: 'lines',
    name: 'x² (x < 0)',
    line: { color: '#3b82f6', width: 2 }
  };

  var trace2 = {
    x: x2,
    y: x2.map(v => 2*v + 1),
    type: 'scatter',
    mode: 'lines',
    name: '2x + 1 (x ≥ 0)',
    line: { color: '#ef4444', width: 2 }
  };

  // Open and closed circle markers
  var trace3 = {
    x: [0],
    y: [0],
    type: 'scatter',
    mode: 'markers',
    name: 'Open point',
    marker: { color: 'white', size: 10, line: { color: '#3b82f6', width: 2 } }
  };

  var trace4 = {
    x: [0],
    y: [1],
    type: 'scatter',
    mode: 'markers',
    name: 'Closed point',
    marker: { color: '#ef4444', size: 10 }
  };

  var layout = {
    title: 'Piecewise Function',
    xaxis: { title: 'x', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-4, 4] },
    yaxis: { title: 'y', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-2, 10] },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Source Sans 3, sans-serif' },
    legend: { x: 0.02, y: 0.98 }
  };

  Plotly.newPlot('piecewise-graph', [trace1, trace2, trace3, trace4], layout, {responsive: true});
})();
</script>

## Absolute Value Functions

$$f(x) = |g(x)|$$

The graph of $|g(x)|$ takes the graph of $g(x)$ and reflects any portion below the x-axis above it.

**Example**: $y = |x - 2|$ is a V-shape with vertex at $(2, 0)$.

<div id="absolute-graph" style="width:100%;max-width:700px;height:400px;margin:20px auto;"></div>

<script>
(function() {
  var x = [];
  for (var i = -4; i <= 6; i += 0.1) { x.push(i); }

  var trace1 = {
    x: x,
    y: x.map(v => Math.abs(v)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = |x|',
    line: { color: '#3b82f6', width: 2 }
  };

  var trace2 = {
    x: x,
    y: x.map(v => Math.abs(v - 2)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = |x - 2|',
    line: { color: '#ef4444', width: 2 }
  };

  var trace3 = {
    x: x,
    y: x.map(v => Math.abs(v*v - 4)),
    type: 'scatter',
    mode: 'lines',
    name: 'y = |x² - 4|',
    line: { color: '#10b981', width: 2 }
  };

  var layout = {
    title: 'Absolute Value Functions',
    xaxis: { title: 'x', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [-4, 6] },
    yaxis: { title: 'y', zeroline: true, zerolinecolor: '#888', gridcolor: '#ddd', range: [0, 10] },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Source Sans 3, sans-serif' },
    legend: { x: 0.02, y: 0.98 }
  };

  Plotly.newPlot('absolute-graph', [trace1, trace2, trace3], layout, {responsive: true});
})();
</script>

## Practice Problems

1. Sketch the graph of $f(x) = -2(x + 1)^2 + 3$. Identify the vertex, axis of symmetry, and direction of opening.

2. Find all asymptotes of $f(x) = \frac{2x^2 - 1}{x^2 - 4}$.

3. Describe the transformations applied to $y = \sin x$ to obtain $y = 3\sin(2x - \pi) + 1$.

4. Determine the end behavior of $f(x) = -x^5 + 2x^3 - x$.

5. Graph the piecewise function:
$$g(x) = \begin{cases} -x - 1 & \text{if } x < -1 \\ x^2 & \text{if } -1 \leq x \leq 1 \\ 2 & \text{if } x > 1 \end{cases}$$

## Key Takeaways

- Every algebraic manipulation has a geometric interpretation on the graph
- Master the basic function shapes before applying transformations
- Asymptotes describe behavior at boundaries and infinity
- Calculus tools (derivatives) reveal increasing/decreasing intervals and extrema
- Sketching is about identifying key features, not plotting every point
- Understanding transformations lets you graph complex functions from simple ones
- Interactive visualization helps build intuition for function behavior
