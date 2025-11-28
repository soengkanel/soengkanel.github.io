---
layout: post
title: "[Math] Probability and Statistics Essentials"
tags: [Probability, Statistics, Data Analysis, Grade 12]
thumbnail: /images/science_research_thumbnail.png
---

Probability quantifies uncertainty. Statistics uses data to draw conclusions. Together, they form the mathematical foundation for making decisions under uncertainty.

## Basic Probability

The probability of event $A$ is:

$$P(A) = \frac{\text{number of favorable outcomes}}{\text{total number of outcomes}}$$

Probability always satisfies: $0 \leq P(A) \leq 1$

### Complement Rule

The probability that $A$ does NOT occur:

$$P(A') = 1 - P(A)$$

### Addition Rule

For any two events:

$$P(A \cup B) = P(A) + P(B) - P(A \cap B)$$

For **mutually exclusive** events (can't both occur):

$$P(A \cup B) = P(A) + P(B)$$

### Multiplication Rule

For **independent** events:

$$P(A \cap B) = P(A) \cdot P(B)$$

For **dependent** events:

$$P(A \cap B) = P(A) \cdot P(B|A)$$

where $P(B|A)$ is the probability of $B$ given that $A$ occurred.

## Conditional Probability

$$P(B|A) = \frac{P(A \cap B)}{P(A)}$$

**Example**: A bag has 3 red and 2 blue balls. You draw two without replacement. What's the probability the second is red, given the first was blue?

$$P(\text{2nd red}|\text{1st blue}) = \frac{3}{4}$$

After removing one blue ball, 3 red remain out of 4 total.

## Bayes' Theorem

$$P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}$$

This "reverses" conditional probabilities—crucial for updating beliefs with new evidence.

## Permutations and Combinations

### Permutations (Order Matters)

The number of ways to arrange $r$ items from $n$ items:

$$P(n,r) = \frac{n!}{(n-r)!}$$

**Example**: How many ways can 3 people finish 1st, 2nd, 3rd in a race of 8 people?

$$P(8,3) = \frac{8!}{5!} = 8 \times 7 \times 6 = 336$$

### Combinations (Order Doesn't Matter)

The number of ways to choose $r$ items from $n$ items:

$$C(n,r) = \binom{n}{r} = \frac{n!}{r!(n-r)!}$$

**Example**: How many ways can you choose 3 people from a group of 8?

$$C(8,3) = \frac{8!}{3!5!} = \frac{8 \times 7 \times 6}{3 \times 2 \times 1} = 56$$

## Discrete Random Variables

A **random variable** $X$ assigns numerical values to outcomes.

### Expected Value (Mean)

$$E(X) = \mu = \sum_{i} x_i \cdot P(x_i)$$

**Example**: A die roll has expected value:

$$E(X) = 1(\frac{1}{6}) + 2(\frac{1}{6}) + 3(\frac{1}{6}) + 4(\frac{1}{6}) + 5(\frac{1}{6}) + 6(\frac{1}{6}) = 3.5$$

### Variance and Standard Deviation

$$Var(X) = \sigma^2 = E[(X - \mu)^2] = E(X^2) - [E(X)]^2$$

$$\sigma = \sqrt{Var(X)}$$

## Binomial Distribution

For $n$ independent trials with success probability $p$:

$$P(X = k) = \binom{n}{k}p^k(1-p)^{n-k}$$

**Mean**: $\mu = np$

**Variance**: $\sigma^2 = np(1-p)$

**Example**: Flip a fair coin 10 times. Probability of exactly 6 heads?

$$P(X = 6) = \binom{10}{6}(0.5)^6(0.5)^4 = 210 \times 0.0009765625 \approx 0.205$$

## Normal Distribution

The **normal distribution** is the bell curve with probability density:

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}}e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

### Standard Normal Distribution

When $\mu = 0$ and $\sigma = 1$, we use $Z$:

$$Z = \frac{X - \mu}{\sigma}$$

This **z-score** tells you how many standard deviations from the mean.

### The 68-95-99.7 Rule

For normal distributions:
- 68% of data falls within 1 standard deviation of the mean
- 95% within 2 standard deviations
- 99.7% within 3 standard deviations

## Descriptive Statistics

### Measures of Center

**Mean**: $\bar{x} = \frac{\sum x_i}{n}$

**Median**: Middle value when data is ordered

**Mode**: Most frequent value

### Measures of Spread

**Range**: Maximum - Minimum

**Variance**: $s^2 = \frac{\sum(x_i - \bar{x})^2}{n-1}$

**Standard Deviation**: $s = \sqrt{s^2}$

**Interquartile Range (IQR)**: $Q_3 - Q_1$

## Correlation and Regression

### Correlation Coefficient

$$r = \frac{\sum(x_i - \bar{x})(y_i - \bar{y})}{(n-1)s_x s_y}$$

- $r = 1$: Perfect positive correlation
- $r = -1$: Perfect negative correlation
- $r = 0$: No linear correlation

### Linear Regression

Best-fit line: $\hat{y} = a + bx$

Slope: $b = r \cdot \frac{s_y}{s_x}$

Intercept: $a = \bar{y} - b\bar{x}$

## Practice Problems

1. A bag contains 4 red and 6 blue balls. Find the probability of drawing 2 red balls in succession without replacement.

2. In a class of 30 students, 18 play soccer, 15 play basketball, and 10 play both. What's the probability a random student plays at least one sport?

3. Calculate $C(12, 4)$

4. For a binomial distribution with $n = 20$ and $p = 0.3$, find the mean and standard deviation.

5. A dataset has values: 5, 8, 12, 15, 20. Calculate the mean and standard deviation.

## Key Takeaways

- Probability measures likelihood from 0 to 1
- Use permutations when order matters, combinations when it doesn't
- Expected value is the long-run average
- The normal distribution appears everywhere due to the Central Limit Theorem
- Correlation measures association, not causation
