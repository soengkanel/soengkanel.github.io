---
layout: post
title: "[Math] Trigonometry - Functions, Identities, and Applications"
---

Trigonometry studies relationships between angles and sides of triangles. It extends to circular functions essential for modeling periodic phenomena.

## The Unit Circle

The unit circle has radius 1 centered at the origin. For angle $\theta$:

$$\cos\theta = x\text{-coordinate}$$
$$\sin\theta = y\text{-coordinate}$$

This definition works for all angles, not just acute ones.

### Key Angles

| Degrees | Radians | $\sin\theta$ | $\cos\theta$ | $\tan\theta$ |
|---------|---------|--------------|--------------|--------------|
| 0° | 0 | 0 | 1 | 0 |
| 30° | $\frac{\pi}{6}$ | $\frac{1}{2}$ | $\frac{\sqrt{3}}{2}$ | $\frac{\sqrt{3}}{3}$ |
| 45° | $\frac{\pi}{4}$ | $\frac{\sqrt{2}}{2}$ | $\frac{\sqrt{2}}{2}$ | 1 |
| 60° | $\frac{\pi}{3}$ | $\frac{\sqrt{3}}{2}$ | $\frac{1}{2}$ | $\sqrt{3}$ |
| 90° | $\frac{\pi}{2}$ | 1 | 0 | undefined |

## Six Trigonometric Functions

$$\sin\theta = \frac{\text{opposite}}{\text{hypotenuse}} \qquad \csc\theta = \frac{1}{\sin\theta}$$

$$\cos\theta = \frac{\text{adjacent}}{\text{hypotenuse}} \qquad \sec\theta = \frac{1}{\cos\theta}$$

$$\tan\theta = \frac{\text{opposite}}{\text{adjacent}} = \frac{\sin\theta}{\cos\theta} \qquad \cot\theta = \frac{1}{\tan\theta} = \frac{\cos\theta}{\sin\theta}$$

## Fundamental Identities

### Pythagorean Identities

$$\sin^2\theta + \cos^2\theta = 1$$

$$1 + \tan^2\theta = \sec^2\theta$$

$$1 + \cot^2\theta = \csc^2\theta$$

### Reciprocal Identities

$$\csc\theta = \frac{1}{\sin\theta}, \quad \sec\theta = \frac{1}{\cos\theta}, \quad \cot\theta = \frac{1}{\tan\theta}$$

### Quotient Identities

$$\tan\theta = \frac{\sin\theta}{\cos\theta}, \quad \cot\theta = \frac{\cos\theta}{\sin\theta}$$

### Even-Odd Identities

$$\sin(-\theta) = -\sin\theta \quad \text{(odd)}$$
$$\cos(-\theta) = \cos\theta \quad \text{(even)}$$
$$\tan(-\theta) = -\tan\theta \quad \text{(odd)}$$

## Sum and Difference Formulas

$$\sin(A \pm B) = \sin A \cos B \pm \cos A \sin B$$

$$\cos(A \pm B) = \cos A \cos B \mp \sin A \sin B$$

$$\tan(A \pm B) = \frac{\tan A \pm \tan B}{1 \mp \tan A \tan B}$$

**Example**: Find exact value of $\sin 75°$

$$\sin 75° = \sin(45° + 30°) = \sin 45°\cos 30° + \cos 45°\sin 30°$$

$$= \frac{\sqrt{2}}{2} \cdot \frac{\sqrt{3}}{2} + \frac{\sqrt{2}}{2} \cdot \frac{1}{2} = \frac{\sqrt{6} + \sqrt{2}}{4}$$

## Double Angle Formulas

$$\sin 2\theta = 2\sin\theta\cos\theta$$

$$\cos 2\theta = \cos^2\theta - \sin^2\theta = 2\cos^2\theta - 1 = 1 - 2\sin^2\theta$$

$$\tan 2\theta = \frac{2\tan\theta}{1 - \tan^2\theta}$$

## Half Angle Formulas

$$\sin\frac{\theta}{2} = \pm\sqrt{\frac{1 - \cos\theta}{2}}$$

$$\cos\frac{\theta}{2} = \pm\sqrt{\frac{1 + \cos\theta}{2}}$$

$$\tan\frac{\theta}{2} = \frac{\sin\theta}{1 + \cos\theta} = \frac{1 - \cos\theta}{\sin\theta}$$

## Law of Sines

For any triangle with sides $a$, $b$, $c$ opposite angles $A$, $B$, $C$:

$$\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C}$$

**Use when**: You know two angles and one side (AAS, ASA) or two sides and an angle opposite one of them (SSA).

## Law of Cosines

$$c^2 = a^2 + b^2 - 2ab\cos C$$

**Use when**: You know two sides and the included angle (SAS) or all three sides (SSS).

**Example**: Find side $c$ if $a = 5$, $b = 7$, and $C = 60°$

$$c^2 = 25 + 49 - 2(5)(7)\cos 60° = 74 - 70(0.5) = 74 - 35 = 39$$

$$c = \sqrt{39} \approx 6.24$$

## Solving Trigonometric Equations

### General Solutions

$$\sin\theta = k \implies \theta = \arcsin(k) + 2\pi n \text{ or } \theta = \pi - \arcsin(k) + 2\pi n$$

$$\cos\theta = k \implies \theta = \pm\arccos(k) + 2\pi n$$

$$\tan\theta = k \implies \theta = \arctan(k) + \pi n$$

### Example

Solve $2\sin^2\theta - \sin\theta - 1 = 0$ for $\theta \in [0, 2\pi)$

Factor: $(2\sin\theta + 1)(\sin\theta - 1) = 0$

$\sin\theta = -\frac{1}{2}$ or $\sin\theta = 1$

$\theta = \frac{7\pi}{6}, \frac{11\pi}{6}, \frac{\pi}{2}$

## Graphing Trigonometric Functions

For $y = A\sin(Bx - C) + D$ or $y = A\cos(Bx - C) + D$:

- **Amplitude**: $|A|$ (height from midline to peak)
- **Period**: $\frac{2\pi}{|B|}$ (length of one cycle)
- **Phase Shift**: $\frac{C}{B}$ (horizontal shift)
- **Vertical Shift**: $D$ (midline)

**Example**: $y = 3\sin(2x - \pi) + 1$

- Amplitude: 3
- Period: $\frac{2\pi}{2} = \pi$
- Phase shift: $\frac{\pi}{2}$ (right)
- Vertical shift: 1 (up)

## Inverse Trigonometric Functions

$$y = \arcsin x \iff x = \sin y, \quad y \in \left[-\frac{\pi}{2}, \frac{\pi}{2}\right]$$

$$y = \arccos x \iff x = \cos y, \quad y \in [0, \pi]$$

$$y = \arctan x \iff x = \tan y, \quad y \in \left(-\frac{\pi}{2}, \frac{\pi}{2}\right)$$

## Practice Problems

1. Simplify: $\frac{\sin^2\theta}{1 - \cos\theta}$

2. Find the exact value of $\cos 15°$

3. Solve $\cos 2\theta = \cos\theta$ for $\theta \in [0, 2\pi)$

4. In triangle ABC, $a = 8$, $b = 5$, $C = 120°$. Find $c$.

5. Graph $y = 2\cos(3x + \frac{\pi}{2})$ and identify amplitude, period, and phase shift.

## Key Takeaways

- The unit circle defines trig functions for all angles
- Pythagorean identity $\sin^2 + \cos^2 = 1$ is fundamental
- Law of Sines for AAS/ASA/SSA; Law of Cosines for SAS/SSS
- Know the sum, double, and half angle formulas
- Inverse functions have restricted domains to be one-to-one
