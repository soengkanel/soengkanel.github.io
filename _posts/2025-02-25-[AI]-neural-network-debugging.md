---
layout: post
title: "[AI] Neural Network Debugging: A Systematic Approach"
tags: [Neural Networks, Debugging, Deep Learning, Troubleshooting]
---

Neural networks fail in opaque ways. Systematic debugging separates productive troubleshooting from random experimentation. This article presents a structured methodology.

## The Debugging Hierarchy

Address issues in this order:

1. **Data** (most common source of problems)
2. **Implementation** (bugs in code)
3. **Hyperparameters** (configuration issues)
4. **Architecture** (model capacity/design)

## Data Debugging

### Sanity Checks

Before training, verify:

```python
# Check for NaN/Inf values
assert not np.isnan(X).any()
assert not np.isinf(X).any()

# Check label distribution
print(pd.Series(y).value_counts(normalize=True))

# Check feature scales
print(X.describe())
```

### Common Data Issues

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Loss = NaN | Inf/NaN in data | Clean data, clip values |
| No learning | Labels misaligned | Verify data pipeline |
| Oscillating loss | Inconsistent preprocessing | Standardize pipeline |
| Perfect training accuracy | Data leakage | Audit features |

### Data Pipeline Verification

Visualize what the model actually sees:

```python
# For images
plt.imshow(X_batch[0])
print(f"Label: {y_batch[0]}")

# For text
print(tokenizer.decode(input_ids[0]))
```

## Implementation Debugging

### Gradient Checking

Verify backpropagation with numerical gradients:

```python
def gradient_check(model, X, y, epsilon=1e-7):
    params = model.get_params()
    numerical_grads = []

    for i, param in enumerate(params):
        # f(x + epsilon)
        params[i] += epsilon
        loss_plus = compute_loss(model, X, y)

        # f(x - epsilon)
        params[i] -= 2 * epsilon
        loss_minus = compute_loss(model, X, y)

        # Numerical gradient
        numerical_grad = (loss_plus - loss_minus) / (2 * epsilon)
        numerical_grads.append(numerical_grad)

        params[i] += epsilon  # Restore

    return numerical_grads
```

### Overfit Test

Verify the model can memorize a tiny dataset:

```python
# Use 10-100 samples
small_X, small_y = X[:100], y[:100]

# Train until loss approaches zero
# If it can't overfit, there's a bug
```

### Single Batch Test

Train repeatedly on one batch:

```python
for epoch in range(1000):
    loss = train_step(single_batch)
    print(f"Epoch {epoch}: Loss = {loss}")

# Loss should decrease monotonically to ~0
```

## Hyperparameter Debugging

### Learning Rate Diagnosis

| Symptom | Learning Rate |
|---------|---------------|
| Loss explodes | Too high |
| Loss decreases very slowly | Too low |
| Loss oscillates wildly | Too high |
| Loss plateaus early | Too low or wrong schedule |

### Learning Rate Finder

```python
lrs = np.logspace(-7, 0, 100)
losses = []

for lr in lrs:
    model.reset()
    optimizer.lr = lr
    loss = train_one_batch()
    losses.append(loss)

# Plot and find steepest descent point
plt.plot(np.log10(lrs), losses)
```

## Architecture Debugging

### Capacity Check

**Underfitting indicators**:
- Training loss high
- Validation loss ≈ Training loss
- Solution: Increase capacity

**Overfitting indicators**:
- Training loss low
- Validation loss >> Training loss
- Solution: Regularization, more data

### Layer-by-Layer Analysis

Check activations at each layer:

```python
for name, layer in model.named_modules():
    activation = get_activation(layer, X)
    print(f"{name}: mean={activation.mean():.4f}, "
          f"std={activation.std():.4f}, "
          f"dead={( activation == 0).mean():.2%}")
```

Look for:
- Dead neurons (always zero)
- Saturated activations (always ±1)
- Vanishing values (approaching zero)

## Debugging Checklist

```
[ ] Data loads correctly (visualize samples)
[ ] Labels match inputs (verify manually)
[ ] Loss decreases on tiny dataset (overfit test)
[ ] Gradients flow (gradient check)
[ ] Activations are healthy (no dead/saturated)
[ ] Learning rate is appropriate (LR finder)
[ ] Model has sufficient capacity (training loss)
[ ] Regularization prevents overfitting (validation loss)
```

## Conclusion

Systematic debugging transforms frustrating trial-and-error into methodical problem-solving. Most neural network issues trace back to data problems—start there before adjusting architecture.
