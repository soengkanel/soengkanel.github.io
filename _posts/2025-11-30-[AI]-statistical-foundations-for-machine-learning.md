---
layout: post
title: "[AI] Statistical Foundations for Machine Learning: A Practical Guide"
tags: [AI, Statistics, Machine Learning, Data Science]
thumbnail: /images/thumbnails/2025-11-30-[AI]-statistical-foundations-for-machine-learning.png
---

Machine Learning is built on statistics. You don't need to be a mathematician, but you need to understand how to look at data and make sense of it. Let's learn statistics by working with actual data, not just theory.

## Dataset: Student Test Scores

Throughout this guide, we'll use this simple dataset of 10 students' test scores:

| Student | Score |
|---------|-------|
| Alice   | 75    |
| Bob     | 82    |
| Carol   | 78    |
| David   | 95    |
| Emma    | 68    |
| Frank   | 72    |
| Grace   | 88    |
| Henry   | 76    |
| Ivy     | 81    |
| Jack    | 85    |

## 1. Mean (Average): The Center of Your Data

**Question:** What's the typical score?

**How to Calculate:**
Add all scores and divide by the number of students.

```
Mean = (75 + 82 + 78 + 95 + 68 + 72 + 88 + 76 + 81 + 85) ÷ 10
     = 800 ÷ 10
     = 80
```

**Result:** The average score is **80**.

**In Machine Learning:** If you're predicting student scores and you have no other information, your best guess is 80.

---

## 2. Median: The Middle Value

**Question:** What score is in the middle?

**How to Calculate:**
1. Sort the scores from lowest to highest
2. Find the middle value

**Sorted Scores:**
```
68, 72, 75, 76, 78, 81, 82, 85, 88, 95
```

Since we have 10 students (even number), the median is between the 5th and 6th values:
```
Median = (78 + 81) ÷ 2 = 79.5
```

**Result:** The median score is **79.5**.

### Why It Matters: Handling Outliers

Now imagine David didn't study and scored **15** instead of 95.

**New Data:**

| Student | Score |
|---------|-------|
| Alice   | 75    |
| Bob     | 82    |
| Carol   | 78    |
| David   | **15** |
| Emma    | 68    |
| Frank   | 72    |
| Grace   | 88    |
| Henry   | 76    |
| Ivy     | 81    |
| Jack    | 85    |

**New Mean:**
```
Mean = (75 + 82 + 78 + 15 + 68 + 72 + 88 + 76 + 81 + 85) ÷ 10
     = 720 ÷ 10
     = 72
```

**New Median:**
```
Sorted: 15, 68, 72, 75, 76, 78, 81, 82, 85, 88
Median = (76 + 78) ÷ 2 = 77
```

**Observation:**
- Mean dropped from **80 to 72** (huge change!)
- Median dropped from **79.5 to 77** (small change)

**Lesson:** Median is more reliable when you have outliers (extreme values).

---

## 3. Standard Deviation: How Spread Out Is the Data?

**Question:** Are students' scores similar, or all over the place?

Let's compare two classes:

**Class A (Our data):**
```
68, 72, 75, 76, 78, 81, 82, 85, 88, 95
```

**Class B:**
```
79, 79, 80, 80, 80, 80, 80, 81, 81, 81
```

Both classes have a mean of **80**, but they feel very different.

### Calculating Standard Deviation for Class A:

**Step 1:** Calculate each student's distance from the mean (80)

| Score | Distance from Mean | Squared Distance |
|-------|-------------------|------------------|
| 68    | 68 - 80 = -12     | 144              |
| 72    | 72 - 80 = -8      | 64               |
| 75    | 75 - 80 = -5      | 25               |
| 76    | 76 - 80 = -4      | 16               |
| 78    | 78 - 80 = -2      | 4                |
| 81    | 81 - 80 = 1       | 1                |
| 82    | 82 - 80 = 2       | 4                |
| 85    | 85 - 80 = 5       | 25               |
| 88    | 88 - 80 = 8       | 64               |
| 95    | 95 - 80 = 15      | 225              |

**Step 2:** Average the squared distances
```
Variance = (144 + 64 + 25 + 16 + 4 + 1 + 4 + 25 + 64 + 225) ÷ 10
         = 572 ÷ 10
         = 57.2
```

**Step 3:** Take the square root
```
Standard Deviation = √57.2 ≈ 7.6
```

**For Class B, the standard deviation is only 0.7** (students are very similar).

**In Machine Learning:**
- **Low standard deviation** (Class B): Data is consistent, easier to predict
- **High standard deviation** (Class A): Data varies a lot, harder to predict

---

## 4. Probability: Making Predictions

**Question:** If we pick a random student, what's the chance they scored above 80?

**Our Data:**
```
68, 72, 75, 76, 78, 81, 82, 85, 88, 95
```

**Students above 80:** 81, 82, 85, 88, 95 = **5 students**

**Probability:**
```
P(score > 80) = 5 ÷ 10 = 0.5 = 50%
```

### Real Example: Email Spam Filter

You have 100 emails:

| Type      | Contains word "FREE" | Doesn't contain "FREE" | Total |
|-----------|----------------------|------------------------|-------|
| Spam      | 40                   | 10                     | 50    |
| Not Spam  | 5                    | 45                     | 50    |
| **Total** | 45                   | 55                     | 100   |

**Question:** If an email contains "FREE", what's the probability it's spam?

```
P(Spam | "FREE") = Number of spam with "FREE" ÷ Total emails with "FREE"
                 = 40 ÷ 45
                 = 0.89 = 89%
```

**Your spam filter learns:** If "FREE" appears, there's an 89% chance it's spam.

---

## 5. A/B Testing: Is the Difference Real?

**Scenario:** You changed your website button color.

**Before (Blue Button):**
- 1,000 visitors
- 50 clicked
- **Click rate: 5.0%**

**After (Red Button):**
- 1,000 visitors
- 57 clicked
- **Click rate: 5.7%**

**Question:** Is red really better, or was this just luck?

### Simple Rule of Thumb

If the difference is **more than 2 × standard error**, it's probably real.

```
Standard Error ≈ √(0.05 × 0.95 ÷ 1000) ≈ 0.007 = 0.7%

Difference = 5.7% - 5.0% = 0.7%
```

Since **0.7% is equal to 1 × standard error**, the improvement might just be luck. You need more data.

**After 10,000 visitors:**
- Blue: 500 clicks (5.0%)
- Red: 570 clicks (5.7%)

```
Standard Error ≈ √(0.05 × 0.95 ÷ 10000) ≈ 0.002 = 0.2%

Difference = 5.7% - 5.0% = 0.7%
```

Now **0.7% is 3.5 × standard error**. This is statistically significant! Red button is better.

---

## 6. Correlation: Do Two Things Move Together?

**Question:** Does study time affect test scores?

| Student | Study Hours | Test Score |
|---------|-------------|------------|
| Alice   | 2           | 75         |
| Bob     | 5           | 82         |
| Carol   | 3           | 78         |
| David   | 8           | 95         |
| Emma    | 1           | 68         |
| Frank   | 2           | 72         |
| Grace   | 6           | 88         |
| Henry   | 3           | 76         |
| Ivy     | 5           | 81         |
| Jack    | 6           | 85         |

Looking at the data, you can see: **more study hours → higher scores**.

**Correlation coefficient** (a number from -1 to +1):
- **+1:** Perfect positive relationship
- **0:** No relationship
- **-1:** Perfect negative relationship

For this data, correlation ≈ **+0.95** (very strong positive correlation)

### Correlation ≠ Causation

**Famous Example:**

| Year | Ice Cream Sales | Drowning Deaths |
|------|----------------|-----------------|
| Jan  | Low            | Low             |
| Feb  | Low            | Low             |
| ...  | ...            | ...             |
| Jul  | High           | High            |
| Aug  | High           | High            |

**Correlation is strong**, but does ice cream cause drowning? No!

**Real cause:** Summer (hot weather) → people buy ice cream AND people swim more

**In Machine Learning:** Your model might find correlations that don't make sense. You need to think about causation.

---

## 7. Overfitting: Memorizing vs. Learning

Imagine you're teaching a student about animals with these examples:

**Training Data:**

| Animal | Has Fur? | Has 4 Legs? | Barks? | Is it a Dog? |
|--------|----------|-------------|--------|--------------|
| Rex    | Yes      | Yes         | Yes    | Yes          |
| Fluffy | Yes      | Yes         | No     | No (Cat)     |
| Tweety | No       | No          | No     | No (Bird)    |

**Student A (Underfitting - Too Simple):**
"If it has 4 legs, it's a dog."
- **Problem:** Thinks cats are dogs!

**Student B (Good Model):**
"If it has fur AND 4 legs AND barks, it's a dog."
- **Perfect!**

**Student C (Overfitting - Too Specific):**
"If it has brown fur AND 4 legs AND barks AND name starts with R, it's a dog."
- **Problem:** Won't recognize a dog named "Buddy"!

**In Machine Learning:**
- **Underfitting:** Model is too simple, misses patterns
- **Good Fit:** Model learns the real pattern
- **Overfitting:** Model memorizes training data, fails on new data

---

## Conclusion: Statistics = Making Sense of Data

You've learned the essential statistical concepts:

1. **Mean & Median:** Understanding the center of your data
2. **Standard Deviation:** Understanding how spread out your data is
3. **Probability:** Making predictions from patterns
4. **A/B Testing:** Knowing if differences are real or random
5. **Correlation:** Finding relationships (but not assuming causation)
6. **Overfitting:** The difference between memorizing and learning

**Next time you train a model:**
- Look at your data in tables
- Calculate mean and standard deviation
- Check for outliers
- Think about whether correlations make sense
- Test if your improvements are real

Statistics isn't scary. It's just asking good questions about your data.
