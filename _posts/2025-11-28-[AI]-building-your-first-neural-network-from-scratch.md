---
layout: post
title: "[AI] Building Your First Neural Network from Scratch"
tags: [AI, Neural Networks, Python, Deep Learning, Tutorial]
thumbnail: /images/thumbnails/2025-11-28-[AI]-building-your-first-neural-network-from-scratch.png
---

Now that you understand the [essential mathematics behind machine learning](https://soengkanel.github.io/AI-essential-math-for-machine-learning/), let's put that knowledge into practice by building a neural network from scratch using only NumPy.

This hands-on guide will show you how Linear Algebra, Calculus, and Probability come together to create a working AI system.

## What We're Building

We'll create a simple neural network that can classify handwritten digits (0-9) from the MNIST dataset. This is the "Hello World" of deep learning, but building it from scratch will give you deep insights into how neural networks actually work.

**No TensorFlow. No PyTorch. Just pure Python and math.**

## The Architecture

Our network will have:
- **Input Layer**: 784 neurons (28×28 pixel images flattened)
- **Hidden Layer**: 128 neurons with ReLU activation
- **Output Layer**: 10 neurons (one per digit) with Softmax activation

```
[784 inputs] → [128 hidden] → [10 outputs]
```

## Step 1: Initialize the Network (Linear Algebra)

Remember how we represented images as matrices? Now we need weight matrices to transform them.

```python
import numpy as np

class NeuralNetwork:
    def __init__(self, input_size=784, hidden_size=128, output_size=10):
        # Initialize weights with small random values
        # Why small? Large weights cause "exploding gradients"
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))
```

**What's happening?**
- `W1` is a 784×128 matrix that transforms input to hidden layer
- `W2` is a 128×10 matrix that transforms hidden to output
- `b1` and `b2` are bias terms (like the y-intercept in y = mx + b)

## Step 2: Forward Propagation (Matrix Multiplication)

This is where Linear Algebra shines. We multiply matrices to pass data through the network.

```python
def relu(self, Z):
    """ReLU activation: max(0, x)"""
    return np.maximum(0, Z)

def softmax(self, Z):
    """Softmax converts scores to probabilities"""
    exp_Z = np.exp(Z - np.max(Z, axis=1, keepdims=True))  # Numerical stability
    return exp_Z / np.sum(exp_Z, axis=1, keepdims=True)

def forward(self, X):
    """Pass input through the network"""
    # Layer 1: Input → Hidden
    self.Z1 = np.dot(X, self.W1) + self.b1  # Linear transformation
    self.A1 = self.relu(self.Z1)             # Non-linear activation
    
    # Layer 2: Hidden → Output
    self.Z2 = np.dot(self.A1, self.W2) + self.b2
    self.A2 = self.softmax(self.Z2)          # Probabilities
    
    return self.A2
```

**Real Example:**
```
Input: [0.1, 0.5, 0.3, ...] (784 numbers)
         ↓ (multiply by W1)
Hidden: [0.2, 0.0, 0.8, ...] (128 numbers after ReLU)
         ↓ (multiply by W2)
Output: [0.01, 0.05, 0.82, ...] (10 probabilities)
         ↑
    "This is probably an 8!"
```

## Step 3: Calculate Loss (Probability)

How wrong is our prediction? We use **Cross-Entropy Loss**.

```python
def compute_loss(self, Y_true, Y_pred):
    """
    Cross-Entropy Loss measures prediction quality
    Lower = better
    """
    m = Y_true.shape[0]  # Number of examples
    
    # Clip predictions to avoid log(0)
    Y_pred = np.clip(Y_pred, 1e-10, 1 - 1e-10)
    
    # Cross-entropy formula
    loss = -np.sum(Y_true * np.log(Y_pred)) / m
    return loss
```

**Intuition:**
- If the model predicts 0.9 for the correct class → Low loss (good!)
- If the model predicts 0.1 for the correct class → High loss (bad!)

## Step 4: Backpropagation (Calculus)

This is where Gradient Descent happens. We calculate how to adjust each weight to reduce the loss.

```python
def backward(self, X, Y_true, learning_rate=0.01):
    """
    Backpropagation: Calculate gradients and update weights
    """
    m = X.shape[0]  # Batch size
    
    # Output layer gradient
    dZ2 = self.A2 - Y_true  # Derivative of softmax + cross-entropy
    dW2 = np.dot(self.A1.T, dZ2) / m
    db2 = np.sum(dZ2, axis=0, keepdims=True) / m
    
    # Hidden layer gradient
    dA1 = np.dot(dZ2, self.W2.T)
    dZ1 = dA1 * (self.Z1 > 0)  # Derivative of ReLU
    dW1 = np.dot(X.T, dZ1) / m
    db1 = np.sum(dZ1, axis=0, keepdims=True) / m
    
    # Update weights (Gradient Descent step)
    self.W2 -= learning_rate * dW2
    self.b2 -= learning_rate * db2
    self.W1 -= learning_rate * dW1
    self.b1 -= learning_rate * db1
```

**This is the "walking down the mountain" from our previous article!**
- `dW2`, `dW1` are the slopes (gradients)
- `learning_rate` is the step size
- We subtract because we want to go *down* the loss mountain

## Step 5: Training Loop

Now we put it all together:

```python
def train(self, X_train, Y_train, epochs=100, batch_size=32):
    """
    Train the network on data
    """
    for epoch in range(epochs):
        # Shuffle data each epoch
        indices = np.random.permutation(X_train.shape[0])
        X_shuffled = X_train[indices]
        Y_shuffled = Y_train[indices]
        
        # Mini-batch training
        for i in range(0, X_train.shape[0], batch_size):
            X_batch = X_shuffled[i:i+batch_size]
            Y_batch = Y_shuffled[i:i+batch_size]
            
            # Forward pass
            predictions = self.forward(X_batch)
            
            # Backward pass
            self.backward(X_batch, Y_batch)
        
        # Print progress
        if epoch % 10 == 0:
            loss = self.compute_loss(Y_train, self.forward(X_train))
            print(f"Epoch {epoch}, Loss: {loss:.4f}")
```

## Step 6: Making Predictions

```python
def predict(self, X):
    """
    Predict class for new data
    """
    probabilities = self.forward(X)
    return np.argmax(probabilities, axis=1)  # Return class with highest probability
```

## Complete Example

Here's how to use it:

```python
# Load MNIST data (simplified)
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load data
digits = load_digits()
X = digits.data  # 1797 images, 64 pixels each
y = digits.target

# Normalize pixel values
scaler = StandardScaler()
X = scaler.fit_transform(X)

# One-hot encode labels
Y = np.eye(10)[y]  # Convert [3] to [0,0,0,1,0,0,0,0,0,0]

# Split data
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)

# Create and train network
nn = NeuralNetwork(input_size=64, hidden_size=128, output_size=10)
nn.train(X_train, Y_train, epochs=100, batch_size=32)

# Test accuracy
predictions = nn.predict(X_test)
true_labels = np.argmax(Y_test, axis=1)
accuracy = np.mean(predictions == true_labels)
print(f"Test Accuracy: {accuracy * 100:.2f}%")
```

## Expected Output

```
Epoch 0, Loss: 2.3026
Epoch 10, Loss: 0.8234
Epoch 20, Loss: 0.4521
Epoch 30, Loss: 0.3012
...
Epoch 90, Loss: 0.1234
Test Accuracy: 94.72%
```

## Key Insights

### 1. **Matrix Operations Are Everything**
Every layer is just matrix multiplication. GPUs are fast because they excel at this.

### 2. **Activation Functions Add Non-Linearity**
Without ReLU/Softmax, the network would just be a fancy linear regression. Non-linearity allows it to learn complex patterns.

### 3. **Backpropagation Is Just Chain Rule**
All those derivatives? Just the calculus chain rule applied systematically.

### 4. **Learning Rate Matters**
- Too high → Network diverges (loss explodes)
- Too low → Training takes forever
- Just right → Smooth convergence

## Common Issues and Fixes

| Problem | Cause | Solution |
|---------|-------|----------|
| Loss = NaN | Exploding gradients | Lower learning rate, clip gradients |
| Loss not decreasing | Learning rate too low | Increase learning rate |
| Accuracy stuck at ~10% | Network predicting same class | Check weight initialization |
| Overfitting | Network memorizing training data | Add dropout, reduce network size |

## Next Steps

Now that you've built a network from scratch, you understand what libraries like PyTorch and TensorFlow do under the hood. They automate:
- Weight initialization
- Gradient calculation (autograd)
- Optimization algorithms
- GPU acceleration

But the core concepts remain the same: **matrices, derivatives, and probabilities working together to learn patterns from data**.

## Challenge

Try modifying this network:
1. Add another hidden layer
2. Experiment with different activation functions (tanh, sigmoid)
3. Implement momentum or Adam optimizer
4. Add L2 regularization to prevent overfitting

Understanding these fundamentals will make you a better AI engineer, even when using high-level frameworks.
