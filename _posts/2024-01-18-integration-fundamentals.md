---
layout: post
title: "[Math] Integration and Antiderivatives"
tags: [Calculus, Integration, Antiderivatives, Grade 12]
thumbnail: /images/science_research_thumbnail.png
---

Integration is the reverse of differentiation. Where derivatives find rates of change, integrals find accumulated quantities—areas, volumes, total distance.

## Antiderivatives

An **antiderivative** of $f(x)$ is a function $F(x)$ such that $F'(x) = f(x)$.

Since the derivative of a constant is zero, antiderivatives include an arbitrary constant $C$:

$$\int f(x)\,dx = F(x) + C$$

This is the **indefinite integral**.

## Basic Integration Rules

### Power Rule for Integration

$$\int x^n\,dx = \frac{x^{n+1}}{n+1} + C \quad (n \neq -1)$$

**Examples**:
- $\int x^4\,dx = \frac{x^5}{5} + C$
- $\int x^{-3}\,dx = \frac{x^{-2}}{-2} + C = -\frac{1}{2x^2} + C$
- $\int \sqrt{x}\,dx = \int x^{1/2}\,dx = \frac{x^{3/2}}{3/2} + C = \frac{2}{3}x^{3/2} + C$

### Constant Multiple Rule

$$\int cf(x)\,dx = c\int f(x)\,dx$$

### Sum and Difference Rule

$$\int [f(x) \pm g(x)]\,dx = \int f(x)\,dx \pm \int g(x)\,dx$$

## Essential Integrals to Know

$$\int 1\,dx = x + C$$

$$\int e^x\,dx = e^x + C$$

$$\int \frac{1}{x}\,dx = \ln|x| + C$$

$$\int a^x\,dx = \frac{a^x}{\ln a} + C$$

$$\int \sin x\,dx = -\cos x + C$$

$$\int \cos x\,dx = \sin x + C$$

$$\int \sec^2 x\,dx = \tan x + C$$

$$\int \csc^2 x\,dx = -\cot x + C$$

$$\int \sec x \tan x\,dx = \sec x + C$$

$$\int \csc x \cot x\,dx = -\csc x + C$$

## Definite Integrals

The **definite integral** has limits of integration and gives a number:

$$\int_a^b f(x)\,dx = F(b) - F(a)$$

This is the **Fundamental Theorem of Calculus**.

**Example**: Evaluate $\int_1^3 x^2\,dx$

$$= \left[\frac{x^3}{3}\right]_1^3 = \frac{3^3}{3} - \frac{1^3}{3} = \frac{27}{3} - \frac{1}{3} = \frac{26}{3}$$

## Properties of Definite Integrals

$$\int_a^a f(x)\,dx = 0$$

$$\int_a^b f(x)\,dx = -\int_b^a f(x)\,dx$$

$$\int_a^b f(x)\,dx + \int_b^c f(x)\,dx = \int_a^c f(x)\,dx$$

$$\int_a^b cf(x)\,dx = c\int_a^b f(x)\,dx$$

## Integration by Substitution

When the integrand contains a composite function, use **u-substitution**.

**Method**:
1. Choose $u = g(x)$ (usually the inner function)
2. Find $du = g'(x)\,dx$
3. Substitute and integrate
4. Replace $u$ with the original expression

**Example**: $\int 2x(x^2+1)^3\,dx$

Let $u = x^2 + 1$, then $du = 2x\,dx$

$$= \int u^3\,du = \frac{u^4}{4} + C = \frac{(x^2+1)^4}{4} + C$$

**Example with adjustment**: $\int x\sin(x^2)\,dx$

Let $u = x^2$, then $du = 2x\,dx$, so $x\,dx = \frac{1}{2}du$

$$= \int \sin(u) \cdot \frac{1}{2}\,du = -\frac{1}{2}\cos u + C = -\frac{1}{2}\cos(x^2) + C$$

## Integration with Definite Integrals and Substitution

Change the limits when substituting:

**Example**: $\int_0^2 x(x^2+1)^2\,dx$

Let $u = x^2 + 1$. When $x = 0$, $u = 1$. When $x = 2$, $u = 5$.

$$= \frac{1}{2}\int_1^5 u^2\,du = \frac{1}{2}\left[\frac{u^3}{3}\right]_1^5 = \frac{1}{6}(125 - 1) = \frac{124}{6} = \frac{62}{3}$$

## Area Under a Curve

The definite integral $\int_a^b f(x)\,dx$ represents the **signed area** between $f(x)$ and the x-axis from $x = a$ to $x = b$.

- Area above x-axis: positive
- Area below x-axis: negative

For **total area** (unsigned), use:
$$\int_a^b |f(x)|\,dx$$

## Average Value of a Function

The average value of $f(x)$ on $[a, b]$ is:

$$f_{avg} = \frac{1}{b-a}\int_a^b f(x)\,dx$$

## Practice Problems

1. Find $\int (3x^2 - 4x + 5)\,dx$

2. Evaluate $\int_0^{\pi} \sin x\,dx$

3. Use substitution: $\int e^{3x}\,dx$

4. Evaluate $\int_1^4 \frac{1}{\sqrt{x}}\,dx$

5. Find $\int \cos(2x+1)\,dx$

## Key Takeaways

- Integration reverses differentiation
- Always include $+C$ for indefinite integrals
- The Fundamental Theorem connects derivatives and integrals
- U-substitution handles composite functions
- Definite integrals give signed areas; take absolute values for total area
