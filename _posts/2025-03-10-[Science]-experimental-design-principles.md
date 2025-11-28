---
layout: post
title: "[Science] Experimental Design: Principles for Valid Inference"
tags: [Experimental Design, Causality, Research Methods, Inference]
---

Poor experimental design produces uninterpretable results regardless of statistical sophistication. This article covers fundamental design principles for causal inference.

## The Causal Inference Problem

We want to know: Does X cause Y?

The fundamental problem: We cannot observe the same unit with and without treatment.

Solution: Design experiments that make causal inference valid.

## Core Design Principles

### 1. Randomization

Randomly assign units to conditions.

**Why it works**: Randomization ensures that:
- Treatment groups are comparable on average
- Confounders are balanced (observed and unobserved)
- Statistical inference is valid

**Implementation**:
```python
import random

def randomize(units, n_treatment):
    shuffled = random.sample(units, len(units))
    treatment = shuffled[:n_treatment]
    control = shuffled[n_treatment:]
    return treatment, control
```

### 2. Control Groups

Compare treatment to appropriate baseline.

**Types of controls**:
- **No treatment**: Natural baseline
- **Placebo**: Controls for expectation effects
- **Active control**: Compares to existing treatment
- **Wait-list**: Delayed treatment access

Choose control based on research question.

### 3. Blinding

Prevent knowledge of condition from affecting outcomes.

**Single-blind**: Participants don't know their condition
**Double-blind**: Participants and administrators don't know
**Triple-blind**: Analysts also don't know

Blinding prevents:
- Placebo effects
- Observer bias
- Demand characteristics

### 4. Replication

Multiple independent observations strengthen inference.

**Within-study replication**: Multiple trials per condition
**Across-study replication**: Independent research groups

Report: Number of replications and consistency of effects.

## Common Design Types

### Between-Subjects Design

Different participants in each condition.

```
Group A → Treatment → Measure
Group B → Control   → Measure
Compare: Group A vs Group B
```

**Pros**: No carryover effects
**Cons**: Requires more participants, individual differences add noise

### Within-Subjects Design

Same participants in all conditions.

```
Participant → Condition 1 → Measure → Condition 2 → Measure
Compare: Condition 1 vs Condition 2 (within person)
```

**Pros**: Controls individual differences, fewer participants needed
**Cons**: Order effects, carryover, demand characteristics

**Mitigation**: Counterbalance condition order

### Factorial Design

Cross multiple factors to study interactions.

```
           Factor B
           Low    High
Factor A  ┌──────┬──────┐
Low       │  A1B1│  A1B2│
          ├──────┼──────┤
High      │  A2B1│  A2B2│
          └──────┴──────┘
```

Allows testing:
- Main effect of A
- Main effect of B
- A × B interaction

## Threats to Validity

### Internal Validity Threats

| Threat | Description | Mitigation |
|--------|-------------|------------|
| Selection | Groups differ at baseline | Randomization |
| History | External events affect outcome | Control group |
| Maturation | Natural change over time | Control group |
| Attrition | Differential dropout | Intent-to-treat analysis |
| Testing | Measurement affects outcome | Control group |
| Instrumentation | Measurement changes | Standardization |

### External Validity Threats

| Threat | Description | Mitigation |
|--------|-------------|------------|
| Sample | Unrepresentative participants | Diverse sampling |
| Setting | Artificial environment | Field studies |
| Time | Results don't generalize temporally | Replication |
| Treatment | Specific implementation | Multiple operationalizations |

## Power and Sample Size

### Minimum Detectable Effect

Given your sample size, what's the smallest effect you can detect?

```
Inputs:
- Sample size (n)
- Significance level (α)
- Power (1 - β)
- Variance (σ²)

Output: Minimum detectable effect (MDE)
```

### Sample Size Calculation

Given desired effect detection, how many participants needed?

```python
from scipy import stats

def sample_size_ttest(effect_size, alpha=0.05, power=0.8):
    """Two-sample t-test sample size per group"""
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)
    n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
    return int(np.ceil(n))
```

## Pre-Registration

Commit to analysis plan before seeing data.

**Pre-registration includes**:
1. Hypotheses
2. Sample size justification
3. Exclusion criteria
4. Primary outcome measure
5. Statistical analysis plan

**Benefits**:
- Prevents HARKing
- Distinguishes confirmatory from exploratory
- Increases credibility

## Conclusion

Experimental design is the foundation of causal inference. No statistical analysis can compensate for design flaws. Invest time in design before collecting data.
