---
layout: post
title: "[ML Khmer] ជំពូក 11: Naive Bayes"
date: 2026-06-30 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, naive-bayes, classification, probabilistic, text-classification, interactive]
thumbnail: /images/ml-series/ch11-naive-bayes.svg
---

មេរៀន​នេះ​ជា **classifier probabilistic ​ដំបូង​នៃ​ series**។ Naive Bayes ​ប្រើ Bayes' rule (មេរៀន 3) ​ផ្ទាល់ ​​​​+ ​​ការ​សន្មត​ "naive" ​​​មួយ​ដែល feature ​​ឯករា​ជ្យ ​​​​ឱ្យ class។ ​​សន្មត​​នេះ "ខុស" ​ច្រើន​ដង​ ​​ ​ ​ ​​ ​​ ​ ​ ​​ — ​ប៉ុន្តែ​ classifier ​ដំណើរ​ការ​ល្អ​​ខ្លាំង​៖ លឿន, ​ត្រូវ​ការ data ​​​​​តូច, explainable។ ​មាន​​ **រូប​ភាព interactive ៣**៖ Gaussian NB decision boundary, spam classifier ​​​ដែល​​​អ្នក​​ ​​​សាក​ type ​​សារ, ​​និង Laplace smoothing ​ដែល​​បង្ហាញ​ហេតុ​អ្វី​ត្រូវ​ការ។

---

# សង្ខេប

- **Bayes' rule**៖ $P(y \mid x) = \dfrac{P(x \mid y) \, P(y)}{P(x)}$
- **Naive assumption**៖ $P(x_1, \ldots, x_d \mid y) = \prod_j P(x_j \mid y)$ — feature ​ឯករា​ជ្យ ​ឱ្យ class
- **Decision rule**៖ $\hat y = \arg\max_y P(y) \prod_j P(x_j \mid y)$
- **Variants**៖
  - **Gaussian NB** — continuous feature ($P(x_j \mid y) = \mathcal{N}(\mu_{jy}, \sigma_{jy}^2)$)
  - **Multinomial NB** — count feature (word counts ​ក្នុង text)
  - **Bernoulli NB** — binary feature (word present/absent)
- **Laplace smoothing**៖ $P(x_j \mid y) = \dfrac{\text{count} + \alpha}{\text{total} + \alpha \cdot V}$ — ការ​ពារ zero probability
- **Log-space**៖ $\log P(y) + \sum_j \log P(x_j \mid y)$ — ការ​ពារ underflow
- **​ហេតុ​អ្វី​ដំណើរ​ការ​​ល្អ?** ​​សន្មត​ខុស ​​​ប៉ុន្តែ​ decision boundary ​​ ​​ ​​​​ ​​​​​ ​​​ ​​​​ ​​ ​​​​​ ​​ ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ច្រើន​ដង​នៅ​ត្រឹមត្រូវ
- **Connection to logistic regression**៖ Gaussian NB + ​​សន្មត $\sigma$ ​ដូច​គ្នា​​​​ ​= logistic regression ​​​ ​ ​​ច្រួល​​ឆ្គង

---


# ហេតុ​អ្វី​សំខាន់?

Naive Bayes ​​​ជា​ baseline ​មាស​សម្រាប់ text classification — ​លឿន​បំផុត, ​ត្រូវ​ការ data ​​​​​តូច, explainable ​ខ្លាំង​ៗ។ ​​​មុន​អ្នក​​ ​​សាក deep learning ​សម្រាប់ text — **ដាក់ Naive Bayes ​ដំបូង** — ​ច្រើន​ដង​ផ្ដល់ accuracy 80-90% ​ដែល​​ល្មម​ល្អ​ៗ​ៗ។

**ឧស្សាហកម្ម​នៅ​កម្ពុជា​ដែល​ប្រើ​ផ្ទាល់​៖**

- **Khmer SMS spam filter** — ​​ ​​ ​ ​ ​​ ​​​​​​​​​​​ ​​ច្បាស់ ​​Bernoulli/Multinomial NB ​សម្រាប់​ filter "​ឈ្នះ​រង្វាន់" / "​​​​ផ្ញើ OTP" spam
- **Khmer news sentiment** — positive / negative / neutral ​ដោយ Multinomial NB ​លើ TF-IDF
- **AMK loan default classifier** — Gaussian NB ​​​​​ ​​​​លើ income, debt, age (baseline ​មុន​​ ​ logistic regression)
- **Wing fraud rules** — categorical feature (transaction type, hour, location) → Bernoulli NB
- **Medical symptom screening** — binary symptom ​​ ​→ Bernoulli NB → "​ប្រូបាប៊ីលីតេ disease"
- **Customer support routing** — ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ ​នាំ ticket Khmer ​ទៅ​ team ​​ដែល​​ ​​ ​​ល្អ​បំផុត

**ច្បាប់​ស្នូល​៖** Naive Bayes ​ផ្ដល់ "​ភ័ស្តុតាង" ​​​ច្បាស់​ៗ — ​អ្នក​អាច​ប្រាប់ "​ពាក្យ X ​ឱ្យ​ probability spam +30%" — ​ច្បាស់​ៗ​​ ​​​​​​ ​​​ដែល​​​​ ​​​​ ​​​ explain ​ដល់​​ business stakeholder។

---

# ពាក្យ​បច្ចេកទេស​ថ្មី

| ខ្មែរ | English | កំណត់​សម្គាល់ |
|---|---|---|
| Naive Bayes | Naive Bayes | classifier ​ដែល​​ប្រើ Bayes + naive independence |
| Posterior | $P(y \mid x)$ | probability ​នៃ class ​ឱ្យ feature |
| Prior | $P(y)$ | probability ​នៃ class ​មុន​ឃើញ data |
| Likelihood | $P(x \mid y)$ | probability ​នៃ feature ​ឱ្យ class |
| Evidence | $P(x)$ | normalizing constant |
| Naive assumption | naive | feature ​​ឯករា​ជ្យ​ឱ្យ class |
| Gaussian NB | GaussianNB | continuous feature → Gaussian likelihood |
| Multinomial NB | MultinomialNB | count feature → multinomial likelihood |
| Bernoulli NB | BernoulliNB | binary feature → Bernoulli likelihood |
| Laplace smoothing | $\alpha$ smoothing | add pseudocount ការ​ពារ zero |
| Log-likelihood | log-likelihood | $\sum_j \log P(x_j \mid y)$ |
| MAP decision | MAP | $\arg\max P(y \mid x)$ |
| Generative model | generative | model $P(x, y)$ ​ផ្ទាល់ |
| Discriminative model | discriminative | model $P(y \mid x)$ ​​​​ផ្ទាល់ |
| Bag-of-words | BoW | text → word count vector |

---


# គំនិត​វិចារណញ្ញាណ

## "​មើល​ evidence ​​​មួយ​ៗ​ → ​​​​​​បូក​សរុប → ​​សម្រេច"

​អ្នក​ស្រូបយក​ SMS ​ថ្មី — ​មាន​ពាក្យ "​ឈ្នះ", "​រង្វាន់", "ចុច link"։ ​អ្នក​សួរ៖ "​មាន​អ្វី ​​​​សម្រាប់ spam ​​​​​​​​​ច្រើន​ដង​មាន​ពាក្យ​​ ​ ​ ​​​នេះ?" + "​​​​​ spam ​មាន​ប្រូបាប៊ីលីតេ​មុន​​​ ​​​ឃើញ​អ្វី?" → ​​​បូក​ evidence → ​​​​សម្រេច "spam ​ឬ​ ham?"

​នេះ​ច្បាស់​​ ​នូវ Naive Bayes ​ ​នៅ​​​ ​ស្នូល​៖ ​​​បូក​ evidence ​​​​​មួយ​ៗ​ ​​​​​ដោយ Bayes' rule។

## "​ការ​សន្មត​ naive — ខុស ​​ប៉ុន្តែ​ល្អ"

NB ​​សន្មត​ feature ​​ឯករា​ជ្យ​ឱ្យ class៖

$$
P(\text{“ឈ្នះ”, “រង្វាន់”} \mid \text{spam}) = P(\text{“ឈ្នះ”} \mid \text{spam}) \cdot P(\text{“រង្វាន់”} \mid \text{spam})
$$

​ប៉ុន្តែ​​ "​ឈ្នះ" + "​រង្វាន់" ​មក​ជា​​មួយ​​ច្រើន​ដង​​ៗ​ ​​​នៅ​​​ក្នុង spam — ​ឥត​មែន​​ ​ឯករា​ជ្យ​​!

​ច្បាស់ — ​​ការ​សន្មត​ខុស ​​​​​ប៉ុន្តែ៖
- Probability ​ច្បាស់​ៗ​​ មិន​ត្រឹមត្រូវ (overconfident)
- **​ប៉ុន្តែ​ ​​​​ decision** (argmax) ​ច្រើន​ដង​ត្រឹមត្រូវ — ​​​សម្រាប់ classification, ​យើង​ត្រូវ​ការ ​​ argmax ​ត្រឹម​តែ ​មិន​ត្រូវ​ការ​ probability ​ជាក់​លាក់

## "Generative vs discriminative"

- **Generative** (NB)៖ model $P(x, y) = P(x \mid y) P(y)$ → ​អាច​ generate $x$ ​ដោយ​ខ្លួន​​​ (sample)
- **Discriminative** (logistic, SVM, neural net)៖ model $P(y \mid x)$ ​ផ្ទាល់ → ​មិន​អាច generate $x$

**Trade-off**៖
- Generative — ​ត្រូវ​ការ data ​​​​​តូច​ជាង ​​ (sample-efficient) ​​​​​ប៉ុន្តែ​ ​​​​ ​​​អន់​នៅ​ពេល assumption ​ខូច
- Discriminative — ​ល្អ​​​ ​​​​​​​បំផុត​​​នៅ​ពេល data ​ច្រើន ​​ ​​​ ​ ​​ ​​​​ ​​​ ​​​ប៉ុន្តែ​ ​​​​​ត្រូវ data ​ច្រើន​ជាង

## "Zero probability — ​បញ្ហា​ស្នូល"

ឧបមា​ training set ​មិន​មាន "Khmer Pop" ​ក្នុង class "សុខភាព" → $P(\text{“Khmer Pop”} \mid \text{health}) = 0$ → ​សរុប​ posterior = 0 ​ច្បាស់​ៗ​!

​ច្រើន​ដង​ — ​ច្រើន​ document ​​​ប្រហែល​មាន​ពាក្យ​ដែល​មិន​ដែល​ឃើញ​​ → ​ឥត​មាន classification ​​!

**ដំណោះ​ស្រាយ**៖ **Laplace smoothing** — បន្ថែម pseudocount $\alpha$ ​ច្បាស់​ៗ៖

$$
P(x_j \mid y) = \frac{\text{count}(x_j, y) + \alpha}{\text{count}(y) + \alpha \cdot V}
$$

​​ដោយ $V$ ​​​ជា vocabulary size។ $\alpha = 1$ ​​​​​ (Laplace), $\alpha < 1$ (Lidstone) — sklearn default $\alpha = 1$។

---


# និយមន័យ និង​គណិតវិទ្យា

## ១. Bayes' theorem ​សម្រាប់ classification

ឱ្យ​ class $y \in \{1, \ldots, C\}$ ​និង feature $x = (x_1, \ldots, x_d) \in \mathbb{R}^d$។

**Posterior**៖

$$
P(y \mid x) = \frac{P(x \mid y) \, P(y)}{P(x)}
$$

**MAP decision** (maximum a posteriori)៖

$$
\hat y = \arg\max_y P(y \mid x) = \arg\max_y P(x \mid y) \, P(y)
$$

(​យក $P(x)$ ​ចេញ — ​ដូច​គ្នា​សម្រាប់ class ​ទាំង​អស់ → ​ឥត​ប៉ះ argmax)

## ២. Naive independence assumption

​​ ​​​បញ្ហា​៖ $P(x \mid y)$ ​នៅ $\mathbb{R}^d$ → ​ត្រូវ​​ estimate $C \cdot V^d$ parameter (រ​ីករាយ​ច្នេះ​ ​​​ ​​​ ​ ​មិន​អាច​!)

**​ការ​សន្មត​ naive**៖

$$
P(x \mid y) = P(x_1, x_2, \ldots, x_d \mid y) = \prod_{j=1}^d P(x_j \mid y)
$$

→ ​ត្រូវ​​ estimate ត្រឹម​ $C \cdot d \cdot V$ parameter (linear ​ក្នុង $d$ — ​​​អាច​ច្នេះ​​!)

**Decision rule**៖

$$
\boxed{\;\; \hat y = \arg\max_y P(y) \prod_{j=1}^d P(x_j \mid y) \;\;}
$$

​សម្រាប់​​ underflow protection — ​ប្រើ log-space៖

$$
\hat y = \arg\max_y \left[ \log P(y) + \sum_{j=1}^d \log P(x_j \mid y) \right]
$$

## ៣. ​ការ estimate prior $P(y)$

**MLE** ​​​ (មេរៀន 4)៖

$$
\hat P(y = c) = \frac{n_c}{n}
$$

​ដែល $n_c$ = ​ចំនួន training example ​នៃ class $c$, $n$ = ​សរុប។

## ៤. Gaussian Naive Bayes (continuous feature)

ឱ្យ feature ​លេខ (eg. income, age) — ​​​​​ ​សន្មត $P(x_j \mid y)$ ​ជា Gaussian៖

$$
P(x_j \mid y = c) = \frac{1}{\sqrt{2\pi \sigma_{jc}^2}} \exp\left( -\frac{(x_j - \mu_{jc})^2}{2 \sigma_{jc}^2} \right)
$$

**MLE estimate** (សម្រាប់ class $c$, feature $j$)៖

$$
\hat \mu_{jc} = \frac{1}{n_c} \sum_{i: y_i = c} x_{ij}
$$

$$
\hat \sigma_{jc}^2 = \frac{1}{n_c} \sum_{i: y_i = c} (x_{ij} - \hat \mu_{jc})^2
$$

**Decision rule (log-space)**៖

$$
\hat y = \arg\max_c \left[ \log P(y = c) - \sum_{j=1}^d \frac{(x_j - \mu_{jc})^2}{2 \sigma_{jc}^2} - \sum_{j=1}^d \log \sigma_{jc} \right]
$$

(​យក​ constant ($\log \sqrt{2\pi}$) ​ចេញ — ​ឥត​ប៉ះ argmax)

## ៥. Multinomial Naive Bayes (count feature — text!)

​សម្រាប់ document ​ដែល​​​​​បំ​លែង ​ជា word count vector $x = (x_1, \ldots, x_V)$ ​​ដែល $x_j$ = ​ ​​ ​ចំនួន​ដែល​​​​​​ ពាក្យ $j$ ​​​​​​​​​​លេច​មាន។

$$
P(x \mid y = c) = \frac{(\sum_j x_j)!}{\prod_j x_j!} \prod_{j=1}^V \theta_{jc}^{x_j}
$$

​ដែល $\theta_{jc} = P(\text{ពាក្យ}_j \mid c)$ ​ ​​ ​ ​​ ​ ​​​​​ ​​​​ ​​​​ ​ ​ ​​​​​​​​ ​​​​ ​​​​ ​​​​ ​​​​ ​​​​​ ​ច្បាស់​ៗ​​​ ​សម្រាប់​ class $c$។ ​​​​ យក​ log + ​យក​ constant ​ចេញ​​៖

$$
\log P(x \mid y = c) \propto \sum_{j=1}^V x_j \log \theta_{jc}
$$

**MLE estimate** ​​​ ​ ​​ ​​​​ (​ដោយ​មិន​មាន smoothing)៖

$$
\hat \theta_{jc} = \frac{\sum_{i: y_i = c} x_{ij}}{\sum_{i: y_i = c} \sum_{j'} x_{ij'}}
$$

(ចំនួន​ដែល​ពាក្យ $j$ ​​​​​​លេច​មាន​​​​នៅ​​ ​ class $c$ / ​ ចំនួន​ពាក្យ​សរុប​ក្នុង class $c$)

**Laplace smoothing** ($\alpha = 1$)៖

$$
\hat \theta_{jc} = \frac{\sum_{i: y_i = c} x_{ij} + \alpha}{\sum_{i: y_i = c} \sum_{j'} x_{ij'} + \alpha V}
$$

---


## ៦. Bernoulli Naive Bayes (binary feature)

​សម្រាប់ feature binary $x_j \in \{0, 1\}$ (eg. ​ពាក្យ "​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​លេច មាន​ឬ​ទេ​​)៖

$$
P(x_j \mid y = c) = p_{jc}^{x_j} (1 - p_{jc})^{1 - x_j}
$$

​ដែល $p_{jc} = P(x_j = 1 \mid y = c)$។

**MLE + Laplace**៖

$$
\hat p_{jc} = \frac{(\text{ចំនួន}\ x_{ij} = 1\ \text{ក្នុង class}\ c) + \alpha}{n_c + 2 \alpha}
$$

(2α ​ដោយ​សារ binary)

**ភាព​ខុស​គ្នា Bernoulli vs Multinomial**៖

- Bernoulli — ​ ​ ​​ ​​ ​​ ​​ "ពាក្យ​ ​នេះ​មាន​​​​​​​​​​​លេច​​​​មាន​ឬ​ទេ?" (yes/no) ​ ​​​+ ​​ ​​​ ​មាន​ penalty ​សម្រាប់ ​ ​​​​​ ​​ ​​​​ ​​ ​​​​​​ "ឥត​មាន"
- Multinomial — "ប៉ុនមាន ​ ​​​ ​​​​​​ដង?" (count) + ​​​​​​​​​​​​ឥត​មាន penalty ​ច្បាស់ៗ ​​​​ ​​​ ​​​​សម្រាប់ "ឥត​មាន"

​​ច្រើន​ដង​ — Multinomial ​ល្អ​ជាង​សម្រាប់ document ​វែង; Bernoulli ​ល្អ​ ​​ជាង​សម្រាប់ document ​​​​​តូច (eg. SMS, tweet)។

## ៧. Log-likelihood + log-sum-exp

​ជាក់​ស្តែង — ​​​សម្រាប់ posterior ច្បាស់​ៗ​​ (ឥត​ត្រឹម​ argmax)៖

$$
P(y = c \mid x) = \frac{P(y = c) \prod_j P(x_j \mid y = c)}{\sum_{c'} P(y = c') \prod_j P(x_j \mid y = c')}
$$

ដាក់ log-space៖

$$
\log P(y = c \mid x) = \log P(y = c) + \sum_j \log P(x_j \mid y = c) - \text{LSE}_{c'}
$$

​ដែល **log-sum-exp** ​ជា៖

$$
\text{LSE}_{c'} = \log \sum_{c'} \exp\left[ \log P(y = c') + \sum_j \log P(x_j \mid y = c') \right]
$$

→ **Trick numerical**៖ ​យក $M = \max_{c'} [...]$ ​ចេញ​មុន​៖

$$
\text{LSE} = M + \log \sum_{c'} \exp([\ldots]_{c'} - M)
$$

→ ការ​ពារ overflow!

## ៨. Connection to logistic regression

​សម្រាប់ 2-class Gaussian NB ​ដោយ​ $\sigma$ ​ដូច​គ្នា​សម្រាប់ class ​ទាំង​ពីរ ​+ feature ​​​​​ឯករាជ្យ​ច្រួល​៖

$$
\log \frac{P(y = 1 \mid x)}{P(y = 0 \mid x)} = w^\top x + b
$$

→ **linear decision boundary**! ​ច្បាស់​ច្នេះ​ — Gaussian NB ​មាន decision boundary ​ដូច logistic regression ​​​​​ ​​​​​ ​​​​​ ​​​​ ​​​​​​​ប៉ុន្តែ​ ​​​​​ estimate parameter ​ខុស​គ្នា​៖
- NB — estimate $\mu, \sigma$ ​​​​​ ​ដោយ closed-form ​ (MLE) → ​ ​​លឿន
- Logistic — estimate $w$ ​​ដោយ gradient descent → ​ ​​យឺត​ ​​​ ​​​​ប៉ុន្តែ ​​​​​​​​ ល្អ​​​បំផុត​​​ ​​សម្រាប់​​ ​ data ​​​​​ច្រើន

---


## 🎮 ​រូបភាព interactive ១៖ Gaussian NB decision boundary

​ប្ដូរ class prior $P(y = 1)$ — ​មើល decision boundary ​ផ្លាស់​ប្ដូរ​​​ ​​ ​​​ ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ច្បាស់​ៗ​​​​។

<div id="viz1" style="width:100%;max-width:800px;margin:0 auto;height:480px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  P(y=1) = <span id="viz1-p" style="font-weight:bold;color:#7c3aed">0.50</span>
  <input id="viz1-p-slider" type="range" min="0.1" max="0.9" step="0.05" value="0.5" style="width:30%;max-width:250px"><br>
  <button id="viz1-new" style="margin-top:6px;padding:5px 14px;cursor:pointer">🎲 ​ទិន្នន័យ​ថ្មី</button>
</div>

<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    function randn() {
      var u = 0, v = 0;
      while (u === 0) u = Math.random();
      while (v === 0) v = Math.random();
      return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
    }
    var DATA0 = null, DATA1 = null;
    function gen() {
      DATA0 = []; DATA1 = [];
      var mx0 = -1.5, my0 = -1, sx0 = 0.9, sy0 = 0.9;
      var mx1 = 1.5,  my1 = 1.2,  sx1 = 1.0, sy1 = 0.7;
      for (var i = 0; i < 50; i++) {
        DATA0.push([mx0 + sx0 * randn(), my0 + sy0 * randn()]);
        DATA1.push([mx1 + sx1 * randn(), my1 + sy1 * randn()]);
      }
    }
    function stats(D) {
      var n = D.length, mx = 0, my = 0;
      for (var i = 0; i < n; i++) { mx += D[i][0]; my += D[i][1]; }
      mx /= n; my /= n;
      var vx = 0, vy = 0;
      for (var i = 0; i < n; i++) {
        vx += (D[i][0] - mx) * (D[i][0] - mx);
        vy += (D[i][1] - my) * (D[i][1] - my);
      }
      return { mx: mx, my: my, vx: vx / n + 1e-3, vy: vy / n + 1e-3 };
    }
    function logp(x, y, s, prior) {
      var dx = x - s.mx, dy = y - s.my;
      return Math.log(prior) - 0.5 * Math.log(s.vx) - 0.5 * Math.log(s.vy)
           - dx * dx / (2 * s.vx) - dy * dy / (2 * s.vy);
    }
    function plot(prior1) {
      var s0 = stats(DATA0), s1 = stats(DATA1);
      var N = 60, xs = [], ys = [], zs = [];
      for (var j = 0; j < N; j++) {
        var row = [], y = -4 + 8 * j / (N - 1);
        ys.push(y);
        for (var i = 0; i < N; i++) {
          var x = -4 + 8 * i / (N - 1);
          if (j === 0) xs.push(x);
          var p0 = logp(x, y, s0, 1 - prior1);
          var p1 = logp(x, y, s1, prior1);
          row.push(p1 > p0 ? 1 : 0);
        }
        zs.push(row);
      }
      return [
        { x: xs, y: ys, z: zs, type: 'heatmap', showscale: false,
          colorscale: [[0, 'rgba(59,130,246,0.35)'], [1, 'rgba(220,38,38,0.35)']],
          hoverinfo: 'skip' },
        { x: DATA0.map(function (p) { return p[0]; }), y: DATA0.map(function (p) { return p[1]; }),
          mode: 'markers', name: 'class 0',
          marker: { color: '#1e40af', size: 10, line: { color: '#fff', width: 1.5 } } },
        { x: DATA1.map(function (p) { return p[0]; }), y: DATA1.map(function (p) { return p[1]; }),
          mode: 'markers', name: 'class 1',
          marker: { color: '#dc2626', size: 10, line: { color: '#fff', width: 1.5 } } }
      ];
    }
    var layout = {
      xaxis: { title: 'x₁', range: [-4, 4] },
      yaxis: { title: 'x₂', range: [-4, 4], scaleanchor: 'x' },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    gen();
    Plotly.newPlot('viz1', plot(0.5), layout, { responsive: true, displayModeBar: false });
    function render() {
      var p = parseFloat(document.getElementById('viz1-p-slider').value);
      document.getElementById('viz1-p').textContent = p.toFixed(2);
      Plotly.react('viz1', plot(p), layout);
    }
    document.getElementById('viz1-p-slider').addEventListener('input', render);
    document.getElementById('viz1-new').addEventListener('click', function () { gen(); render(); });
  }
  init();
})();
</script>

> **សាក​មើល៖** $P(y=1) = 0.5$ → boundary នៅ​​មធ្យម។ ​ដាក់ prior 0.9 → boundary ​​ ​​​ផ្លាស់​ឆ្ពោះ​ទៅ class 0 (red expand) — ​យើង​​​ឱ្យ probability ​ច្រើន ​​ ​​​ ​​ ​ដល់ class 1 ​មុន​​ ​​ ​​ ​​ ​ឃើញ data។ ​​​​​ ​​ច្បាស់​​ច្នេះ​​ ​​​នូវ Bayes' rule!


## 🎮 ​រូបភាព interactive ២៖ Spam classifier — word evidence

​សាក type ​សារ — ​មើល​ probability spam ​​​​​​​ ​​ឆ្លុះ​​ ​​ ​ ​​​ ​ផ្ទាល់​​ ​​​​​+ word-level evidence ​​​​​​​​​ ​​​នី​មួយ​ៗ។

<div style="max-width:800px;margin:0 auto;font-family:system-ui,sans-serif">
  <textarea id="viz2-text" rows="2" style="width:100%;font-size:16px;padding:8px;box-sizing:border-box"
    placeholder="សាក type ​សារ​​នៅ​​​នេះ​..."></textarea>
  <div style="margin-top:10px;text-align:center">
    <span style="font-size:1.1em">P(spam) = <span id="viz2-p" style="font-weight:bold;color:#dc2626;font-size:1.3em">--</span></span>
    &nbsp;|&nbsp;
    Prediction = <span id="viz2-pred" style="font-weight:bold">--</span>
  </div>
  <div id="viz2-bars" style="margin-top:10px;height:280px"></div>
</div>


<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    var SPAM_W = {
      'ឈ្នះ': 0.85, 'រង្វាន់': 0.88, 'free': 0.75, 'ឥតគិតថ្លៃ': 0.82,
      'click': 0.70, 'link': 0.65, 'ចុច': 0.62, 'OTP': 0.78, 'pin': 0.72,
      'urgent': 0.80, 'បន្ទាន់': 0.78, 'លុយ': 0.55, 'transfer': 0.60,
      'congratulations': 0.85, 'អបអរ': 0.55, 'winner': 0.90,
      'សួស្តី': 0.15, 'អរគុណ': 0.10, 'អូខេ': 0.20, 'hello': 0.20,
      'ok': 0.15, 'thanks': 0.10, 'ម៉ោង': 0.25, 'ថ្ងៃ': 0.25,
      'ម៉េស្សា': 0.30, 'meeting': 0.20, 'ច្បាប់': 0.20
    };
    var PRIOR_SPAM = 0.3;
    function tokenize(t) {
      return t.toLowerCase().split(/[\s,.!?;៖។​]+/).filter(function (w) { return w.length > 0; });
    }
    function classify(text) {
      var tokens = tokenize(text);
      var logS = Math.log(PRIOR_SPAM);
      var logH = Math.log(1 - PRIOR_SPAM);
      var contribs = [];
      for (var i = 0; i < tokens.length; i++) {
        var w = tokens[i];
        var pSpam = SPAM_W[w];
        if (pSpam == null) continue;
        var ls = Math.log(pSpam), lh = Math.log(1 - pSpam);
        logS += ls; logH += lh;
        contribs.push({ word: w, delta: ls - lh });
      }
      var maxL = Math.max(logS, logH);
      var p = Math.exp(logS - maxL) / (Math.exp(logS - maxL) + Math.exp(logH - maxL));
      return { p: p, contribs: contribs };
    }
    function render() {
      var text = document.getElementById('viz2-text').value;
      if (!text.trim()) {
        document.getElementById('viz2-p').textContent = '--';
        document.getElementById('viz2-pred').textContent = '--';
        Plotly.purge('viz2-bars');
        return;
      }
      var r = classify(text);
      document.getElementById('viz2-p').textContent = (r.p * 100).toFixed(1) + '%';
      var pred = r.p > 0.5 ? '🚫 SPAM' : '✅ HAM';
      document.getElementById('viz2-pred').textContent = pred;
      document.getElementById('viz2-pred').style.color = r.p > 0.5 ? '#dc2626' : '#10b981';
      if (r.contribs.length === 0) { Plotly.purge('viz2-bars'); return; }
      r.contribs.sort(function (a, b) { return b.delta - a.delta; });
      var trace = {
        x: r.contribs.map(function (c) { return c.delta; }),
        y: r.contribs.map(function (c) { return c.word; }),
        type: 'bar', orientation: 'h',
        marker: { color: r.contribs.map(function (c) { return c.delta > 0 ? '#dc2626' : '#10b981'; }) }
      };
      Plotly.newPlot('viz2-bars', [trace], {
        xaxis: { title: 'log P(word|spam) − log P(word|ham)', zeroline: true, zerolinecolor: '#1f2937', zerolinewidth: 2 },
        yaxis: { automargin: true },
        margin: { t: 10, b: 50, l: 100, r: 20 },
        plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
      }, { responsive: true, displayModeBar: false });
    }
    document.getElementById('viz2-text').addEventListener('input', render);
    document.getElementById('viz2-text').value = 'ឈ្នះ រង្វាន់ free ចុច link';
    render();
  }
  init();
})();
</script>

> **សាក​មើល៖** ​សាក type "ឈ្នះ រង្វាន់ free" → P(spam) ​​​​លោត​ឡើង​​ ​​​​ខ្ពស់; ​សាក type "សួស្តី អរគុណ ម៉ោង" → P(spam) ​ដួល។ Bar plot ​បង្ហាញ "evidence" ​នៃ​ពាក្យ​នី​មួយ​ៗ — ​​​​ ​​ ​​​ ​​​​​​​​​ ​​​ ​​ ​​​ ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ច្បាស់​ ៗ ​​​ ​​​​​​explainable​​ ខ្លាំង!


## 🎮 ​រូបភាព interactive ៣៖ Laplace smoothing

ឱ្យ vocabulary 20 words ​នៅ​ training, ​ ​ ​ ​ ​​ ​​​​​ប៉ុន្តែ​​ ​ ​ ​​ ​​ ​មាន​ត្រឹម​ 5 ​​​​​លេច​​ មាន​នៅ class "spam"។ ​ប្ដូរ smoothing $\alpha$ — មើល​ probability ​ដែល​ឱ្យ "unseen" word ​ផ្លាស់​ប្ដូរ​​​ច្បាស់​ៗ​។

<div id="viz3" style="width:100%;max-width:800px;margin:0 auto;height:420px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  α (smoothing) = <span id="viz3-a" style="font-weight:bold;color:#7c3aed">1.00</span>
  <input id="viz3-a-slider" type="range" min="0" max="3" step="0.05" value="1.0" style="width:40%;max-width:350px"><br>
  <span style="font-size:1.05em;margin-top:6px;display:inline-block">
    P(unseen word | spam) = <span id="viz3-unseen" style="font-weight:bold;color:#dc2626">--</span>
  </span>
</div>


<script>
(function () {
  function init() {
    if (typeof Plotly === 'undefined') { setTimeout(init, 200); return; }
    var V = 20;
    var COUNTS = [12, 8, 5, 4, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
    var TOTAL = COUNTS.reduce(function (a, b) { return a + b; }, 0);
    function compute(alpha) {
      return COUNTS.map(function (c) {
        return (c + alpha) / (TOTAL + alpha * V);
      });
    }
    function plot(alpha) {
      var p = compute(alpha);
      var unseenP = (0 + alpha) / (TOTAL + alpha * V);
      document.getElementById('viz3-unseen').textContent = unseenP.toFixed(4);
      var labels = COUNTS.map(function (c, i) {
        return c > 0 ? ('w' + (i + 1)) : ('unseen ' + (i - 4));
      });
      var colors = COUNTS.map(function (c) {
        return c > 0 ? '#1e40af' : '#dc2626';
      });
      return [{
        x: labels, y: p, type: 'bar',
        marker: { color: colors, line: { color: '#fff', width: 1 } }
      }];
    }
    var layout = {
      xaxis: { title: 'word (blue = seen, red = unseen)', tickangle: -40 },
      yaxis: { title: 'P(word | spam)', range: [0, 0.5] },
      margin: { t: 20, b: 100, l: 70, r: 30 },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    Plotly.newPlot('viz3', plot(1.0), layout, { responsive: true, displayModeBar: false });
    function render() {
      var a = parseFloat(document.getElementById('viz3-a-slider').value);
      document.getElementById('viz3-a').textContent = a.toFixed(2);
      Plotly.react('viz3', plot(a), layout);
    }
    document.getElementById('viz3-a-slider').addEventListener('input', render);
    render();
  }
  init();
})();
</script>

> **សាក​មើល៖** $\alpha = 0$ → unseen word ​​​មាន P = 0 → ​បាន​ ​​​ ​​ដួល​ ​​ posterior ​ទាំង​មូល​ទៅ 0 (catastrophic)។ $\alpha = 1$ (Laplace default) → unseen ​មាន $\approx 0.03$ — ​ល្មម​ៗ​​​​​​។ $\alpha = 3$ → seen words ​​​​​ ​​​​ "​​​ ​​​ស្រួល​​​​​​​​​ខ្លាំង​​​​ ​ៗ" — bias ​​​​ ​​​ខ្ពស់​ច្បាស់​ៗ​​ ​​។ Trade-off ​ច្បាស់!

---


# ឧទាហរណ៍

## ឧទាហរណ៍ 1៖ Spam classifier ​ដោយ​ដៃ (Multinomial NB)

ឱ្យ training set (vocabulary = {"​ឈ្នះ", "​សួស្តី", "free", "​ម៉ោង"})​៖

| Doc | ​ឈ្នះ | សួស្តី | free | ម៉ោង | class |
|---|---|---|---|---|---|
| 1 | 2 | 0 | 1 | 0 | spam |
| 2 | 1 | 0 | 2 | 0 | spam |
| 3 | 0 | 2 | 0 | 1 | ham |
| 4 | 0 | 1 | 0 | 2 | ham |

**Prior**៖ $P(\text{spam}) = 2/4 = 0.5$, $P(\text{ham}) = 0.5$

**Word totals**៖
- Spam: ​ឈ្នះ=3, សួស្តី=0, free=3, ម៉ោង=0, total=6
- Ham: ​ឈ្នះ=0, សួស្តី=3, free=0, ម៉ោង=3, total=6

**Likelihood ​ដោយ Laplace ($\alpha = 1, V = 4$)**៖

| Word | $P(\cdot \mid$spam$)$ | $P(\cdot \mid$ham$)$ |
|---|---|---|
| ​ឈ្នះ | $(3+1)/(6+4) = 0.40$ | $(0+1)/(6+4) = 0.10$ |
| សួស្តី | $(0+1)/10 = 0.10$ | $(3+1)/10 = 0.40$ |
| free | $(3+1)/10 = 0.40$ | $(0+1)/10 = 0.10$ |
| ម៉ោង | $(0+1)/10 = 0.10$ | $(3+1)/10 = 0.40$ |

**Classify** ​សារ​​ថ្មី $x = $ "​ឈ្នះ free" (counts: ​ឈ្នះ=1, free=1)៖

$$
\log P(\text{spam}) + 1 \cdot \log 0.40 + 1 \cdot \log 0.40 = \log 0.5 - 1.83 = -2.52
$$

$$
\log P(\text{ham}) + 1 \cdot \log 0.10 + 1 \cdot \log 0.10 = \log 0.5 - 4.61 = -5.30
$$

→ **spam** ​ច្បាស់​ៗ​​!

**Posterior**៖ $P(\text{spam} \mid x) = e^{-2.52} / (e^{-2.52} + e^{-5.30}) \approx 0.94$

## ឧទាហរណ៍ 2៖ Gaussian NB — AMK loan

ឱ្យ training (income in \$K)៖

| Income | Default? |
|---|---|
| 2.0 | yes |
| 2.5 | yes |
| 3.0 | yes |
| 5.0 | no |
| 5.5 | no |
| 6.0 | no |

**Prior**៖ $P(\text{default}) = 3/6 = 0.5$

**MLE**៖
- Default: $\mu = 2.5, \sigma^2 = (0.25 + 0 + 0.25)/3 \approx 0.167$
- No default: $\mu = 5.5, \sigma^2 = (0.25 + 0 + 0.25)/3 \approx 0.167$

**Classify** ​អតិថិជន income = \$4.0K​៖

$$
\log P(x = 4 \mid \text{default}) \propto -\frac{(4 - 2.5)^2}{2 \cdot 0.167} = -6.74
$$

$$
\log P(x = 4 \mid \text{no default}) \propto -\frac{(4 - 5.5)^2}{2 \cdot 0.167} = -6.74
$$

→ **​ស្មើ​គ្នា!** (4 ​នៅ​​​មធ្យម​ច្បាស់​ៗ​​​)។ ​យក prior → $\hat y = $ ​ស្មើ​មួយ​មួយ — 50/50។

​ច្បាស់​ច្នេះ​ — income = \$4K ​ជា boundary។ income < 4 → default ច្បាស់​​​; income > 4 → ​​​មិន​ default។


---

# កូដ Python

## Multinomial NB — text classification

```python
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, GridSearchCV

# Khmer text — ​ត្រូវ tokenize ​មុន (khmer-nltk ​ឬ​ segmenter ​ដទៃ)
texts = ['ឈ្នះ រង្វាន់ free ចុច', 'សួស្តី ម៉ោង ប្រជុំ', ...]
labels = ['spam', 'ham', ...]

pipe = Pipeline([
    ('vec', CountVectorizer(tokenizer=khmer_segment, min_df=2)),
    ('nb', MultinomialNB(alpha=1.0))  # Laplace
])

# CV ​ដើម្បី tune alpha
grid = GridSearchCV(pipe, {'nb__alpha': [0.01, 0.1, 0.5, 1.0, 2.0, 5.0]},
                    cv=5, scoring='f1_macro', n_jobs=-1)
grid.fit(texts, labels)
print(f'Best alpha = {grid.best_params_["nb__alpha"]}')
print(f'Best F1 = {grid.best_score_:.3f}')
```

## Gaussian NB — continuous features

```python
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler

# Standardize ​ឥត​សំខាន់​សម្រាប់ NB (probability ​មិន​ប៉ះ​ដោយ scale) ​​​ ​​​​​ ​​​ ​ ​ប៉ុន្តែ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ ​​ល្អ​​ ​​ ​​​ ​​ ​សម្រាប់​​ ​ debugging
nb = GaussianNB()
nb.fit(X_train, y_train)

# Inspect
print(f'Class priors: {nb.class_prior_}')
print(f'Class means (per feature): {nb.theta_}')
print(f'Class variances: {nb.var_}')

# Predict + probability
y_pred = nb.predict(X_test)
y_proba = nb.predict_proba(X_test)  # P(y=c | x) ​​​សម្រាប់ class នី​មួយ​ៗ
```

## Bernoulli NB — binary features

```python
from sklearn.naive_bayes import BernoulliNB

# សម្រាប់ binary feature (symptom present/absent, word seen/unseen)
nb_b = BernoulliNB(alpha=1.0, binarize=0.0)
nb_b.fit(X_train_binary, y_train)
```

## ​ការ explain decision

```python
# សម្រាប់ MultinomialNB — log_prob_ ​​​​ផ្ដល់ log P(word | class)
nb = grid.best_estimator_.named_steps['nb']
vec = grid.best_estimator_.named_steps['vec']
vocab = vec.get_feature_names_out()

# Top words ​​​សម្រាប់ spam
log_p_spam = nb.feature_log_prob_[1]  # class 1 = spam
log_p_ham  = nb.feature_log_prob_[0]
score = log_p_spam - log_p_ham
top_spam_idx = score.argsort()[-15:][::-1]
print('Top 15 spam indicators:')
for i in top_spam_idx:
    print(f'  {vocab[i]:20s}: {score[i]:+.2f}')
```

## ​​​ ​​​ Calibration ​សម្រាប់​ probability ​ត្រឹមត្រូវ

NB ​​ច្រើន​ដង​ overconfident → probability ​មិន​ត្រឹម​ត្រូវ​​ៗ ​​​ ​​​ ​​​​​ ​ ​​​​ ​ ​​ ​ ​​​ប៉ុន្តែ​​ argmax ​ត្រឹម​ត្រូវ។ ​បើ​អ្នក​ត្រូវ​ការ​ probability ​​​​ ​ ​​​ត្រឹម​ត្រូវ​៖

```python
from sklearn.calibration import CalibratedClassifierCV

calib_nb = CalibratedClassifierCV(MultinomialNB(), cv=5, method='isotonic')
calib_nb.fit(X_train, y_train)
y_proba_calib = calib_nb.predict_proba(X_test)
```


---

# ​ការ​អនុវត្តន៍​ជាក់​ស្តែង

## Khmer SMS spam filter

```python
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

df = pd.read_csv('khmer_sms.csv')  # columns: text, label
X_train, X_test, y_train, y_test = train_test_split(
    df['text'], df['label'], test_size=0.2, stratify=df['label'])

pipe = Pipeline([
    ('tfidf', TfidfVectorizer(tokenizer=khmer_segment,
                              ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
    ('nb', MultinomialNB(alpha=0.5))
])
pipe.fit(X_train, y_train)
print(classification_report(y_test, pipe.predict(X_test)))
```

**Result ​ច្រើន​ដង​៖** Precision spam 95%+, Recall spam 90%+ — baseline ​ដ៏​​ល្អ​មុន deep learning។

## AMK loan default — Gaussian NB baseline

```python
from sklearn.naive_bayes import GaussianNB

features = ['monthly_income', 'years_at_job', 'existing_debt',
            'past_repayment_rate', 'age']
X = df[features].values
y = df['defaulted'].values

nb = GaussianNB()
scores = cross_val_score(nb, X, y, cv=5, scoring='roc_auc')
print(f'AUC: {scores.mean():.3f} ± {scores.std():.3f}')
# AUC 0.75-0.80 ​​ច្រើន​ដង​ — ​ល្អ​សម្រាប់​ baseline
```


## Khmer news sentiment

```python
# 3-class: positive / negative / neutral
pipe = Pipeline([
    ('tfidf', TfidfVectorizer(tokenizer=khmer_segment, max_features=10000,
                              ngram_range=(1, 2))),
    ('nb', MultinomialNB(alpha=1.0))
])
pipe.fit(articles_train, sentiment_train)

# Per-class top features
nb = pipe.named_steps['nb']
vocab = pipe.named_steps['tfidf'].get_feature_names_out()
for c_idx, c_name in enumerate(['negative', 'neutral', 'positive']):
    top = nb.feature_log_prob_[c_idx].argsort()[-10:][::-1]
    print(f'{c_name}: {[vocab[i] for i in top]}')
```

## Wing fraud — Bernoulli NB (categorical features)

```python
from sklearn.preprocessing import OneHotEncoder

# Convert categorical → binary feature matrix
cat_features = ['hour_bucket', 'merchant_type', 'is_weekend',
                'is_foreign', 'amount_bucket']
encoder = OneHotEncoder(sparse_output=False)
X_binary = encoder.fit_transform(df[cat_features])

nb = BernoulliNB(alpha=1.0)
nb.fit(X_binary, y_fraud)

# Predict + explain
proba = nb.predict_proba(X_new_binary)
# ​ ​​​ ​​​ ​​​ ​​​ ​​​ ​​​ ​​​ ​​ ​ Inspect feature_log_prob_ ​​ដើម្បី explain
```

## Medical symptom screening

​​សម្រាប់ pre-diagnosis app ​​​​ — patient ​ ឆ្លើយ binary symptom ​​​​ → P(disease)៖

```python
symptoms = ['fever', 'cough', 'fatigue', 'headache', 'rash']  # binary
X = df[symptoms].values
y = df['has_dengue'].values

nb = BernoulliNB(alpha=1.0)
nb.fit(X, y)

# Probability ​សម្រាប់ patient ​ថ្មី
new_patient = [[1, 1, 1, 0, 0]]  # fever + cough + fatigue
print(f'P(dengue) = {nb.predict_proba(new_patient)[0, 1]:.2%}')
```


---

# លំហាត់

### លំហាត់ 1 — Multinomial NB ​ដោយ​ដៃ

ឱ្យ​ training៖

| Doc | "buy" | "now" | "hi" | class |
|---|---|---|---|---|
| 1 | 3 | 2 | 0 | spam |
| 2 | 2 | 1 | 0 | spam |
| 3 | 0 | 0 | 2 | ham |
| 4 | 0 | 1 | 3 | ham |

​Classify $x = $ "buy hi" (count: buy=1, hi=1) ​ដោយ $\alpha = 1, V = 3$.

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**Prior**៖ $P(\text{spam}) = 0.5, P(\text{ham}) = 0.5$

**Totals**៖
- Spam: buy=5, now=3, hi=0 → total 8
- Ham: buy=0, now=1, hi=5 → total 6

**Likelihood ($\alpha = 1, V = 3$)**៖

| Word | spam | ham |
|---|---|---|
| buy | $(5+1)/(8+3) = 6/11$ | $(0+1)/(6+3) = 1/9$ |
| now | $(3+1)/11 = 4/11$ | $(1+1)/9 = 2/9$ |
| hi | $(0+1)/11 = 1/11$ | $(5+1)/9 = 6/9$ |

**Score $x = $ "buy hi"**៖

$\log P(\text{spam}) + \log(6/11) + \log(1/11) = \log 0.5 - 0.606 - 2.398 = -3.69$

$\log P(\text{ham}) + \log(1/9) + \log(6/9) = \log 0.5 - 2.197 - 0.405 = -3.30$

→ **ham** (​​​អង់ −3.30 > −3.69)

**Posterior**៖ $P(\text{ham} \mid x) = e^{-3.30}/(e^{-3.30} + e^{-3.69}) \approx 0.60$

​ច្បាស់​​ — "hi" ​​ ​​មាន evidence ham ​ខ្លាំង​ខ្លាំង → ​​បំ​ផ្លាញ "buy" → ​​​​ ham ​ច្បាស់​ៗ​​​។

</details>

### លំហាត់ 2 — Gaussian NB ​ដោយ​ដៃ

ឱ្យ feature ​មួយ (age)៖

| Age | class |
|---|---|
| 25 | A |
| 30 | A |
| 35 | A |
| 55 | B |
| 60 | B |
| 65 | B |

Classify age = 45.

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**Prior**៖ $P(A) = P(B) = 0.5$

**MLE**៖
- $\mu_A = 30, \sigma_A^2 = ((25-30)^2 + 0 + (35-30)^2)/3 = 50/3 \approx 16.67$
- $\mu_B = 60, \sigma_B^2 = 50/3 \approx 16.67$

**Log-likelihood ​សម្រាប់ age = 45**៖

$\log P(45 \mid A) \propto -(45-30)^2 / (2 \cdot 16.67) = -6.75$

$\log P(45 \mid B) \propto -(45-60)^2 / (2 \cdot 16.67) = -6.75$

→ **​ស្មើ​គ្នា ​ច្បាស់!** (45 ​នៅ midpoint)

→ ​​យក prior → 50/50 — boundary ​ច្បាស់​​ៗ​ ​​ ​​​​​​នៅ​ 45។

</details>


### លំហាត់ 3 — Laplace smoothing

ឱ្យ vocabulary $V = 10$, training class "spam" ​មាន 50 ​ពាក្យ​សរុប; ​ពាក្យ "free" លេច 0 ​ដង។

(a) ​​បើ $\alpha = 0$ — $P(\text{free} \mid \text{spam}) = ?$<br>
(b) ​​បើ $\alpha = 1$ (Laplace) — ?<br>
(c) ​​បើ $\alpha = 0.1$ (Lidstone) — ?

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

​​សម្រាប់​ "free": count = 0, total = 50, V = 10.

**(a)** $\alpha = 0$ → $P = 0 / 50 = 0$ → ​ ​​​​បំ​ផ្លាញ posterior ​ទាំង​មូល​ ​ច្បាស់​ៗ​​​

**(b)** $\alpha = 1$ → $P = (0+1)/(50+1 \cdot 10) = 1/60 \approx 0.0167$

**(c)** $\alpha = 0.1$ → $P = (0+0.1)/(50+0.1 \cdot 10) = 0.1/51 \approx 0.00196$

→ $\alpha$ ​​​​​តូច → smoothing ​​​​​តូច; $\alpha$ ​ធំ → smoothing ​ខ្លាំង (push ឆ្ពោះ​ uniform)។ $\alpha = 1$ ​ស្តង់​ដារ; tune ​ដោយ CV ​សម្រាប់ task ជាក់​លាក់។

</details>


### លំហាត់ 4 — True/False ​អំពី NB

(a) NB ​ផ្ដល់ probability ​ត្រឹមត្រូវ ​ច្បាស់​ៗ​<br>
(b) NB ​ត្រូវ​ការ data ​ច្រើន​ជាង logistic regression<br>
(c) NB ​​ដំណើរ​ការ​ល្អ​នៅ​ពេល feature មាន correlation ​ខ្លាំង<br>
(d) Multinomial NB ​ល្អ​ជាង Bernoulli NB ​សម្រាប់ document ​វែង

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**(a) FALSE** — NB ​​​ច្រើន​ដង overconfident (probability extreme); argmax ត្រឹមត្រូវ ​ប៉ុន្តែ​ probability ​មិន​ trust ​បាន​ច្បាស់​ៗ → ​ត្រូវ calibrate

**(b) FALSE** — NB ​ត្រូវ​ការ data ​​​​​តូច​ជាង (generative, sample-efficient) — ​ល្អ​សម្រាប់ low-data regime

**(c) FALSE** — Correlation ​ខ្លាំង​ → naive assumption ​ខូច​ខ្លាំង → probability extreme​ ច្បាស់​ៗ ​​; argmax អាច​នៅ​ត្រឹមត្រូវ​​​បន្តិច

**(d) TRUE** — Multinomial ​ឆ្លុះ count → document ​វែង (article) ​ល្អ​បំផុត; Bernoulli ​ឆ្លុះ presence ​ត្រឹម → document ​​​​​តូច (SMS, tweet) ​ល្អ​បំផុត

</details>

---

**​មេរៀន​បន្ទាប់ (ជំពូក 12):** Gradient Descent — ​ យើង​ឃើញ optimization ​ជា​​​ស្នូល​ៗ​នៃ​ ML ​ទាំង​មូល។ Linear regression ​មាន closed-form; ​​​​ប៉ុន្តែ logistic, neural net, ​​ច្រើន​ដង​ ​ឥត​មាន​ដំណោះ​ស្រាយ​ច្បាស់​ — ​ត្រូវ gradient descent។ ​យើង​ឃើញ​ batch / SGD / mini-batch, momentum, Adam, learning rate schedules — ​ស្នូល​នៃ​​​ការ train neural net ​ ​​​ ​​​ ​​​ ​​​ ​​​ ​​ ​​​ ​​​ ​​ ​ ​ ​​​ ​ ​​​ ​ ​​​ ​​​​​ទាំង​មូល។
