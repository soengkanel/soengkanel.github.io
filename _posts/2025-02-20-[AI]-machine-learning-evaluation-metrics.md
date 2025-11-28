---
layout: post
title: "[AI] Machine Learning Evaluation: Choosing the Right Metrics"
tags: [Machine Learning, Metrics, Evaluation, Classification]
---

Model evaluation metrics determine what "good" means for your system. Choosing wrong metrics leads to optimizing the wrong objective. This article provides a framework for metric selection.

## Classification Metrics

### The Confusion Matrix

```
                 Predicted
              Positive  Negative
Actual  Positive   TP       FN
        Negative   FP       TN
```

All classification metrics derive from these four values.

### Core Metrics

**Accuracy** = (TP + TN) / (TP + TN + FP + FN)
- When to use: Balanced classes
- When to avoid: Imbalanced data (99% accuracy means nothing if 99% of data is one class)

**Precision** = TP / (TP + FP)
- Answers: Of predicted positives, how many are correct?
- Optimize when: False positives are costly (spam detection)

**Recall** = TP / (TP + FN)
- Answers: Of actual positives, how many did we find?
- Optimize when: False negatives are costly (disease screening)

**F1 Score** = 2 × (Precision × Recall) / (Precision + Recall)
- Harmonic mean of precision and recall
- Use when: Both FP and FN matter equally

### Threshold-Independent Metrics

**ROC-AUC**: Area under the Receiver Operating Characteristic curve
- Measures discrimination ability across all thresholds
- 0.5 = random, 1.0 = perfect

**PR-AUC**: Area under Precision-Recall curve
- Better for imbalanced datasets
- Focuses on positive class performance

## Regression Metrics

**MSE** (Mean Squared Error) = Σ(y - ŷ)² / n
- Penalizes large errors heavily
- Units are squared

**RMSE** = √MSE
- Same units as target variable
- More interpretable than MSE

**MAE** (Mean Absolute Error) = Σ|y - ŷ| / n
- Robust to outliers
- Linear penalty for all errors

**R²** (Coefficient of Determination) = 1 - (SS_res / SS_tot)
- Proportion of variance explained
- Can be negative for poor models

## Ranking Metrics

**MRR** (Mean Reciprocal Rank)
- Average of 1/rank of first relevant result
- Use for: Search engines, recommendation systems

**NDCG** (Normalized Discounted Cumulative Gain)
- Accounts for position and relevance grades
- Use for: Multi-level relevance ranking

**MAP** (Mean Average Precision)
- Average precision at each relevant item
- Use for: Information retrieval

## Selection Framework

Ask these questions:

1. **What decisions will this metric drive?**
   - If it won't change decisions, don't track it

2. **What are the costs of different errors?**
   - FP cost vs FN cost determines precision/recall tradeoff

3. **What is the class distribution?**
   - Imbalanced data needs appropriate metrics

4. **What is the baseline performance?**
   - Metrics mean nothing without comparison

## Multi-Metric Evaluation

Real systems require multiple metrics:

```
Primary metric: What to optimize
Secondary metrics: Constraints to satisfy
Guardrail metrics: Limits not to violate
```

Example for recommendation system:
- Primary: Click-through rate
- Secondary: Diversity score > 0.3
- Guardrail: Latency < 100ms

## Common Mistakes

1. **Optimizing proxy metrics**: Improving clicks while harming long-term engagement
2. **Ignoring distribution shift**: Test metrics don't reflect production
3. **Metric gaming**: System learns to exploit metric weaknesses
4. **Single metric obsession**: Missing important dimensions

## Conclusion

Metric selection is a design decision with significant consequences. Choose metrics that align with actual business objectives, not just what's easy to measure.
