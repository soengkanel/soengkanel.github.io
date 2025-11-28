---
layout: post
title: "[Math] Understanding Limits and Continuity"
tags: [Calculus, Limits, Continuity, Grade 12]
---

Limits form the foundation of calculus. Before you can understand derivatives or integrals, you must master limits.

## What Is a Limit?

A limit describes what value a function approaches as the input approaches some value. We write:

$$\lim_{x \to a} f(x) = L$$

This means: as $x$ gets closer to $a$, $f(x)$ gets closer to $L$.

## Evaluating Limits

### Direct Substitution

The simplest method. If $f(x)$ is continuous at $x = a$, just plug in the value:

$$\lim_{x \to 3} (2x + 1) = 2(3) + 1 = 7$$

### Factoring

When direct substitution gives $\frac{0}{0}$, factor and simplify:

$$\lim_{x \to 2} \frac{x^2 - 4}{x - 2} = \lim_{x \to 2} \frac{(x+2)(x-2)}{x-2} = \lim_{x \to 2} (x + 2) = 4$$

### Rationalization

For expressions with radicals:

$$\lim_{x \to 0} \frac{\sqrt{x+1} - 1}{x}$$

Multiply by the conjugate:

$$= \lim_{x \to 0} \frac{(\sqrt{x+1} - 1)(\sqrt{x+1} + 1)}{x(\sqrt{x+1} + 1)} = \lim_{x \to 0} \frac{x}{x(\sqrt{x+1} + 1)} = \frac{1}{2}$$

## Important Limit Laws

For limits that exist:

1. **Sum Rule**: $\lim_{x \to a} [f(x) + g(x)] = \lim_{x \to a} f(x) + \lim_{x \to a} g(x)$

2. **Product Rule**: $\lim_{x \to a} [f(x) \cdot g(x)] = \lim_{x \to a} f(x) \cdot \lim_{x \to a} g(x)$

3. **Quotient Rule**: $\lim_{x \to a} \frac{f(x)}{g(x)} = \frac{\lim_{x \to a} f(x)}{\lim_{x \to a} g(x)}$ (if denominator $\neq 0$)

4. **Power Rule**: $\lim_{x \to a} [f(x)]^n = \left[\lim_{x \to a} f(x)\right]^n$

## Special Limits to Memorize

These appear frequently:

$$\lim_{x \to 0} \frac{\sin x}{x} = 1$$

$$\lim_{x \to 0} \frac{1 - \cos x}{x} = 0$$

$$\lim_{x \to \infty} \left(1 + \frac{1}{x}\right)^x = e$$

## One-Sided Limits

Sometimes we need limits from one direction only:

- **Left-hand limit**: $\lim_{x \to a^-} f(x)$ (approaching from values less than $a$)
- **Right-hand limit**: $\lim_{x \to a^+} f(x)$ (approaching from values greater than $a$)

A two-sided limit exists only if both one-sided limits exist and are equal.

## Continuity

A function $f$ is **continuous** at $x = a$ if three conditions hold:

1. $f(a)$ is defined
2. $\lim_{x \to a} f(x)$ exists
3. $\lim_{x \to a} f(x) = f(a)$

### Types of Discontinuities

**Removable**: The limit exists but doesn't equal $f(a)$. Can be "fixed" by redefining $f(a)$.

**Jump**: Left and right limits exist but aren't equal.

**Infinite**: The function approaches $\pm\infty$.

## Limits at Infinity

For rational functions, compare the degrees of numerator and denominator:

- If degree of numerator < degree of denominator: limit is $0$
- If degrees are equal: limit is ratio of leading coefficients
- If degree of numerator > degree of denominator: limit is $\pm\infty$

**Example**:
$$\lim_{x \to \infty} \frac{3x^2 + 2x}{5x^2 - 1} = \frac{3}{5}$$

## Practice Problems

1. Evaluate $\lim_{x \to 1} \frac{x^3 - 1}{x - 1}$

2. Find $\lim_{x \to 0} \frac{\sin(3x)}{x}$

3. Determine if $f(x) = \frac{|x|}{x}$ is continuous at $x = 0$

4. Evaluate $\lim_{x \to \infty} \frac{2x^3 - x}{4x^3 + 5}$

## Key Takeaways

- Limits describe the behavior of functions near a point, not at the point
- Always try direct substitution first
- Use algebraic manipulation when you get indeterminate forms
- Continuity requires the limit to equal the function value
- Master limits before moving to derivatives—they're the same concept applied differently
