---
layout: post
title: "[Science] Statistical Thinking for Scientists: Beyond P-Values"
---

Statistical literacy separates rigorous science from pseudoscience. This article presents essential statistical concepts that every researcher must internalize.

## The P-Value Problem

A p-value answers: "If the null hypothesis were true, how likely is data this extreme?"

It does **not** answer:
- Probability that the hypothesis is true
- Probability the result will replicate
- Magnitude of the effect

### The Replication Crisis

Studies with p < 0.05 fail to replicate at alarming rates:
- Psychology: ~40% replication rate
- Cancer biology: ~10-25% replication rate
- Economics: ~60% replication rate

Why? P-values are misunderstood and misused.

## Effect Sizes Matter

Statistical significance ≠ practical significance.

```
Example:
- Study A: Effect = 0.1, p = 0.001, n = 10,000
- Study B: Effect = 2.0, p = 0.06, n = 50

Study B is more practically important despite larger p-value.
```

### Common Effect Size Measures

**Cohen's d** (continuous outcomes):
- Small: d = 0.2
- Medium: d = 0.5
- Large: d = 0.8

**Odds Ratio** (binary outcomes):
- OR = 1: No effect
- OR = 2: Twice the odds
- OR = 0.5: Half the odds

**R²** (explained variance):
- Proportion of variance accounted for

Always report effect sizes alongside p-values.

## Confidence Intervals

A 95% CI means: If we repeated the study infinitely, 95% of intervals would contain the true value.

CIs provide more information than p-values:
- Point estimate (center)
- Precision (width)
- Significance (excludes null?)

```
Example interpretations:
- CI: [2.1, 5.3] → Significant positive effect
- CI: [-0.3, 4.2] → Not significant (includes 0)
- CI: [0.01, 0.03] → Significant but tiny effect
```

## Bayesian Thinking

### Prior → Likelihood → Posterior

```
P(Hypothesis|Data) ∝ P(Data|Hypothesis) × P(Hypothesis)
     Posterior     ∝    Likelihood      ×    Prior
```

Bayesian inference:
1. Start with prior belief
2. Update with evidence
3. Arrive at posterior belief

### Practical Application

Before seeing data, ask:
- What's my prior probability this is true?
- How much should this evidence update my belief?

Extraordinary claims require extraordinary evidence because priors are low.

## Sample Size and Power

### Power Analysis

Power = P(reject null | null is false)

Standard target: 80% power

```
Required sample size depends on:
- Expected effect size
- Desired power
- Significance level (α)
- Variance in data
```

### The Winner's Curse

Underpowered studies that achieve significance:
- Overestimate effect sizes
- Fail to replicate
- Waste resources

Calculate sample size before collecting data, not after.

## Multiple Comparisons

Testing many hypotheses inflates false positives.

**Bonferroni correction**: α_adjusted = α / number_of_tests
- Conservative (reduces power)
- Simple to apply

**False Discovery Rate (FDR)**: Control proportion of false positives among discoveries
- Less conservative
- Better for exploratory research

```
If testing 20 hypotheses at α = 0.05:
- Expected false positives: 1 (even if all null)
- Bonferroni threshold: 0.05/20 = 0.0025
```

## Practical Recommendations

### Before Data Collection

1. Define hypotheses precisely
2. Calculate required sample size
3. Pre-register analysis plan
4. Specify primary outcome

### During Analysis

1. Follow pre-registered plan
2. Report all outcomes, not just significant ones
3. Calculate effect sizes and CIs
4. Consider practical significance

### When Reporting

```
Template:
"We observed [effect] (95% CI: [lower, upper],
d = [effect size], p = [value], n = [sample]).
This [does/does not] represent a practically
significant effect because [reasoning]."
```

## Conclusion

Statistical thinking requires understanding what analyses can and cannot tell us. No statistical test substitutes for scientific reasoning about mechanisms and practical importance.
