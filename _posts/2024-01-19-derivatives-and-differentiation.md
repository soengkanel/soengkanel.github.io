---
layout: post
title: "[Math] Derivatives and Differentiation Rules"
tags: [Calculus, Derivatives, Functions, Grade 12]
thumbnail: /images/thumbnails/2024-01-19-derivatives-and-differentiation.png
---

The derivative measures how a function changes as its input changes. It's the instantaneous rate of change—the slope of the tangent line at any point.

## Definition of the Derivative

The derivative of $f(x)$ is defined as:

$$f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}$$

This limit, when it exists, gives us a new function that tells us the slope at every point.

## Notation

Several notations mean the same thing:

$$f'(x) = \frac{df}{dx} = \frac{d}{dx}f(x) = Df(x)$$

For $y = f(x)$, we also write $\frac{dy}{dx}$ or $y'$.

## Basic Derivative Rules

### Constant Rule
$$\frac{d}{dx}(c) = 0$$

### Power Rule
$$\frac{d}{dx}(x^n) = nx^{n-1}$$

**Examples**:
- $\frac{d}{dx}(x^5) = 5x^4$
- $\frac{d}{dx}(x^{-2}) = -2x^{-3}$
- $\frac{d}{dx}(\sqrt{x}) = \frac{d}{dx}(x^{1/2}) = \frac{1}{2}x^{-1/2} = \frac{1}{2\sqrt{x}}$

### Constant Multiple Rule
$$\frac{d}{dx}[cf(x)] = c \cdot f'(x)$$

### Sum and Difference Rules
$$\frac{d}{dx}[f(x) \pm g(x)] = f'(x) \pm g'(x)$$

## Product Rule

For two functions multiplied together:

$$\frac{d}{dx}[f(x) \cdot g(x)] = f'(x) \cdot g(x) + f(x) \cdot g'(x)$$

**Example**: Find $\frac{d}{dx}[(x^2)(3x+1)]$

$$= (2x)(3x+1) + (x^2)(3) = 6x^2 + 2x + 3x^2 = 9x^2 + 2x$$

## Quotient Rule

For a fraction of functions:

$$\frac{d}{dx}\left[\frac{f(x)}{g(x)}\right] = \frac{f'(x) \cdot g(x) - f(x) \cdot g'(x)}{[g(x)]^2}$$

**Example**: Find $\frac{d}{dx}\left[\frac{x^2}{x+1}\right]$

$$= \frac{(2x)(x+1) - (x^2)(1)}{(x+1)^2} = \frac{2x^2 + 2x - x^2}{(x+1)^2} = \frac{x^2 + 2x}{(x+1)^2}$$

## Chain Rule

For composite functions $f(g(x))$:

$$\frac{d}{dx}[f(g(x))] = f'(g(x)) \cdot g'(x)$$

Think: "derivative of outside, times derivative of inside."

**Example**: Find $\frac{d}{dx}[(3x+2)^5]$

Let outer function be $u^5$ and inner be $3x+2$:

$$= 5(3x+2)^4 \cdot 3 = 15(3x+2)^4$$

## Derivatives of Trigonometric Functions

$$\frac{d}{dx}(\sin x) = \cos x$$

$$\frac{d}{dx}(\cos x) = -\sin x$$

$$\frac{d}{dx}(\tan x) = \sec^2 x$$

$$\frac{d}{dx}(\cot x) = -\csc^2 x$$

$$\frac{d}{dx}(\sec x) = \sec x \tan x$$

$$\frac{d}{dx}(\csc x) = -\csc x \cot x$$

## Derivatives of Exponential and Logarithmic Functions

$$\frac{d}{dx}(e^x) = e^x$$

$$\frac{d}{dx}(a^x) = a^x \ln a$$

$$\frac{d}{dx}(\ln x) = \frac{1}{x}$$

$$\frac{d}{dx}(\log_a x) = \frac{1}{x \ln a}$$

## Higher-Order Derivatives

The second derivative is the derivative of the derivative:

$$f''(x) = \frac{d^2f}{dx^2} = \frac{d}{dx}\left[\frac{df}{dx}\right]$$

**Example**: If $f(x) = x^4$, then:
- $f'(x) = 4x^3$
- $f''(x) = 12x^2$
- $f'''(x) = 24x$
- $f^{(4)}(x) = 24$

## Applications

### Finding Slope
The derivative $f'(a)$ gives the slope of the tangent line to $f(x)$ at $x = a$.

### Velocity and Acceleration
If $s(t)$ is position at time $t$:
- Velocity: $v(t) = s'(t)$
- Acceleration: $a(t) = v'(t) = s''(t)$

### Rate of Change
Derivatives model any rate: population growth, chemical reaction rates, profit margins.

## Practice Problems

1. Find $\frac{d}{dx}(4x^3 - 2x^2 + 7x - 5)$

2. Differentiate $f(x) = (2x-1)(x^2+3)$

3. Find $\frac{dy}{dx}$ if $y = \frac{x^3}{2x+1}$

4. Differentiate $g(x) = \sin(x^2)$

5. Find $f''(x)$ if $f(x) = e^{2x}$

## Key Takeaways

- The derivative is the instantaneous rate of change
- Power rule handles polynomials; chain rule handles compositions
- Memorize the trig and exponential derivatives
- Product and quotient rules follow predictable patterns
- Always simplify your answer when possible
