---
layout: post
title: "[ML Khmer] ជំពូក 10: K-Means Clustering"
date: 2026-06-29 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, kmeans, clustering, unsupervised, interactive]
thumbnail: /images/ml-series/ch10-kmeans.svg
---

មេរៀន​នេះ​ជា **unsupervised learning ​ដំបូង​នៃ​ series**។ ​មុន​នេះ — ​យើង​មាន $(x_i, y_i)$ ​​​​ ​​ — model ​​​​​​ត្រូវ​​យក $x$ ​មក ​ព្យាករ $y$។ ​ឥឡូវ — **យើង​មាន​ត្រឹម $x_i$** — ​ឥត​មាន label, ​ឥត​មាន ground truth។ ​គោល​ដៅ​៖ ​​​​បំ​បែក data ​​ជា **​ដុំ (clusters)** ​ដែល​ចំណុច​ខាង​ក្នុង​ដុំ​​​ស្រដៀង​គ្នា ​ហើយ​​​ដុំ​ផ្សេង​​​មាន​ភាព​ខុស​គ្នា។ K-Means ​ជា algorithm ​​​សាមញ្ញ​បំផុត​ដែល​​​​អ្នក​ប្រើ​ដំបូង — ​ត្រូវ​​ការ​ត្រឹម​ **2 step ​​ ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ ​ឆ្លាស់​គ្នា**៖ assign points → update centroids → assign → update → ​ស្លាប់​ៗ​ រហូត​ដល់ convergence។ មាន **រូបភាព interactive ៣**៖ ​animation ​ដែល​អ្នក​​ ​ដើរ​ជំហាន​ៗ, elbow method ​​​​សម្រាប់​​ជ្រើស $K$, ​​និង k-means++ vs random initialization។

---

# សង្ខេប

- **Objective**៖ $J = \sum_{k=1}^K \sum_{i \in C_k} \|x_i - \mu_k\|^2$ — within-cluster sum of squares (WCSS)
- **Lloyd's algorithm** (2 steps ឆ្លាស់​គ្នា)៖
  - **Assignment**៖ $C_k = \{i : \|x_i - \mu_k\| \le \|x_i - \mu_j\| \; \forall j\}$
  - **Update**៖ $\mu_k = \dfrac{1}{|C_k|} \sum_{i \in C_k} x_i$
- **Convergence**៖ $J$ ​​ដួល monotonically → ​ឈប់​នៅ local minimum (មិន​​​​ល្អ​បំផុត​​ច្បាស់!)
- **Initialization សំខាន់**៖ random → ​​ងាយ​ត្រូវ bad local min; **k-means++** ​​​ស្ថិត​ស្ថេរ​ច្បាស់​ជាង
- **​ជ្រើស $K$**៖ Elbow method, Silhouette score, Gap statistic
- **​ត្រូវ standardize ​មុន** — distance ​ឆ្លុះ feature scale!
- **​​​ខ្សោយ​នៅ​ពេល**៖ cluster ​មិន​មែន​​ ​​​មូល (non-spherical), ​​ ​ទំហំ​ខុស​គ្នា​ខ្លាំង, density ​ខុស​គ្នា
- **Connection to EM**៖ K-Means = hard-assignment EM ​សម្រាប់ Gaussian Mixture Model

---

# ហេតុ​អ្វី​សំខាន់?

Clustering ​ជា​ឧបករណ៍​មាស​ក្នុង​ឧស្សាហកម្ម — ​ច្រើន​ដង​​អ្នក​មាន data ​​ច្រើន​ ​ប៉ុន្តែ​​ឥត​មាន label។

**ឧស្សាហកម្ម​នៅ​កម្ពុជា​ដែល​ប្រើ​ផ្ទាល់​៖**

- **Wing customer segmentation** — ​បំ​បែក user 5M+ ​​ជា cluster ​​​អាស្រ័យ​លើ transaction pattern → marketing ​​ផ្ដោត​ច្បាស់
- **AMK borrower groups** — ​​បំ​បែក borrower ​ជា risk tier ​មុន scoring model — ​​​​ ​ឱ្យ​ underwriter ​យល់ portfolio
- **Khmer news topic discovery** — ​​​ច្រើន​ដង document ​​ឥត​មាន tag → cluster ​ដោយ TF-IDF → discover topic ​ដោយ​ខ្លួន
- **PP property market segments** — ​​បំ​បែក​ផ្ទះ​ជា tier (luxury / mid / budget) ​​ដោយ price + sqm + amenity
- **Smart/Cellcard subscriber profile** — ​​បំ​បែក subscriber ​ដោយ data usage + voice + SMS → ​​ផ្ដល់​ plan ​​ល្អ​បំផុត
- **Crop region clustering** — ​​​​បំ​បែក​ស្រែ​ជា zone ​ដោយ rainfall + soil → ​អនុសាសន៍​​​ដាំ​ដុះ
- **Anomaly detection** — ​​​ដុំ​​ "ធម្មតា" + outlier ​ឆ្ងាយ ​ច្បាស់​ = anomaly

**ច្បាប់​ស្នូល​៖** Clustering ​ឱ្យ​​​អ្នក "​មើល​ឃើញ​ structure ​ក្នុង data ​ដែល​មិន​មាន label"​​ — ​​​ ​​​ ​​​ ​​​ដំបូង​ ​​ដែល​​​អ្នក​ធ្វើ ​នៅ​ពេល​​​ឃើញ data set ​​​​ថ្មី​ — EDA + clustering ​មុន supervised model។

---

# ពាក្យ​បច្ចេកទេស​ថ្មី

| ខ្មែរ | English | កំណត់​សម្គាល់ |
|---|---|---|
| Clustering | clustering | ​​​​បំ​បែក data ​ជា​ ​ដុំ |
| Unsupervised learning | unsupervised | ​ឥត​មាន label |
| Cluster | cluster ($C_k$) | ​​ដុំ​នៃ​ចំណុច​ស្រដៀង |
| Centroid | centroid ($\mu_k$) | ​មធ្យម​នៃ cluster |
| K-Means | K-Means | algorithm ​​ដែល​​ស្វែង​រក $K$ ​ដុំ |
| WCSS / Inertia | within-cluster SS | $J = \sum \|x - \mu\|^2$ |
| Lloyd's algorithm | Lloyd's | assignment + update ​ឆ្លាស់​គ្នា |
| Hard assignment | hard | ​ចំណុច​ស្ថិត​ក្នុង cluster ​មួយ​ត្រឹម​តែ |
| Soft assignment | soft | probability ​សម្រាប់​ cluster ​នី​មួយ​ៗ (EM/GMM) |
| Local minimum | local min | $J$ ​​​​​តូច​ក្នុង neighborhood ​ ​ប៉ុន្តែ​មិន​​​ល្អ​បំផុត |
| k-means++ | k-means++ | smart initialization |
| Elbow method | elbow | $J$ vs $K$ — ​មាន "​ដៃ​"
| Silhouette score | silhouette | $\dfrac{b - a}{\max(a, b)}$ |
| Inter-cluster distance | inter | distance ​​​​​​​​​​​​រវាង centroid ​ផ្សេង​គ្នា |
| Intra-cluster distance | intra | distance ​ខាង​ក្នុង cluster |
| Voronoi diagram | Voronoi | ​​​​បំ​បែក space ​ដោយ centroid ជិត​បំផុត |

---


# គំនិត​វិចារណញ្ញាណ

## "​​​បំ​បែក​​ ​​​អតិថិជន​ជា​ក្រុម​​​​​​​ដោយ​ឯករា​ជ្យ"

ស្រមៃ​អ្នក​​ ​មាន customer 10,000 នាក់ — ​អ្នក​សង្ស័យ​មាន 3 ​ប្រភេទ​ (heavy user, casual user, dormant)។ ​អ្នក​​ត្រូវ៖

1. ​ជ្រើស​ centroid 3 ​ដំបូង​ដោយ​ random
2. ​សម្រាប់​​អតិថិជន​នី​មួយ​ៗ — រក centroid ​ជិត​បំផុត → ​ដាក់​ ​ក្នុង cluster ​នោះ
3. ​សម្រាប់​ cluster ​នី​មួយ​ៗ​ — គណនា​ centroid ​ថ្មី (mean ​នៃ​ ​ ​អតិថិជន​ខាង​ក្នុង)
4. ​ត្រឡប់​ទៅ​ step 2 ​រហូត​ដល់​ centroid ​ឈប់​ផ្លាស់​ប្ដូរ

ច្បាស់​ៗ — ​​​​ដូច "​អ្នក​ដែល​​​ស្និទ្ធ​ស្នាល​មនុស្ស​មួយ​ក្រុម​ → ​ប្រែ​ទៅ​ជា​​​ ​​មនុស្ស​​ក្នុង​ក្រុម​នោះ"​​​​ ​បន្ទាប់​ ​ ​​ ​ ​ ​​ ​ "​ក្រុម​​​​​បំ​​​បែក​​ ​​​​​មនុស្ស​​ ​​​​ដែល​​​​​ ​ស្និទ្ធ​ស្នាល"​ ឆ្លាស់​គ្នា​​​ៗ​​​​ ​ ​រហូត​​ ​​​​ ​​​​​​​ឈប់។

## "Voronoi diagram = decision boundary នៃ K-Means"

​បន្ទាប់​ពី convergence — ​​​បំ​បែក​ feature space ​ដោយ "តើ centroid ​ណា​ជិត​បំផុត?" → ​​​ ​​​​​​បំ​បែក​ space ​ជា​​ polygon ​ដែល​​ ​ហៅ **Voronoi cells**។ ​​​​ខ្សែ​​​បំ​បែក = perpendicular bisector ​​​​​​​​​​​​រវាង centroid ពីរ។

## "Initialization សំខាន់​ខ្លាំង — ​មិន​ដូច linear regression"

Linear regression ​មាន convex objective → ​ដោះ​ស្រាយ ​ល្អ​បំផុត​ ​ច្បាស់ ​ឥត​អាស្រ័យ​លើ initialization។

K-Means **ឥត​មែន convex** → ​​ច្រើន local minima → initialization ​ខុស​គ្នា → លទ្ធផល​ខុស​គ្នា!

**ច្បាស់​ច្នេះ​​​** ​យើង​ឱ្យ៖
- Random initialization — ​សាក​​​ច្រើន​ដង (eg. n_init=10), ​ជ្រើស​ដែល​​​​ល្អ​បំផុត
- k-means++ — ​ជ្រើស centroid ​ដំបូង​ឱ្យ​ឆ្ងាយ​ពី​គ្នា → ​បាន local min ​ល្អ​ច្រើន​ដង

## "K-Means ​ស្រលាញ់ cluster ​មូល (spherical)"

K-Means ​​ឆ្លុះ​ Euclidean distance + "​មធ្យម" ​ជា centroid → ​ល្អ​​នៅ​ពេល cluster ​មាន​​​​​​ shape ​មូល​បាន​ប្រហែល​​ស្មើ​គ្នា។

**​ខូច​នៅ​ពេល​៖**
- Cluster ​មាន​​ shape ​ឆ្គង (eg. ​ប្រវែង​ឆ្គង) — DBSCAN ​ប្រសើរ
- Density ខុស​គ្នា​ខ្លាំង — Mean Shift, DBSCAN ​ប្រសើរ
- Cluster ​ច្រួល​ ​​​ ​ (eg. concentric circles) — spectral clustering ​ប្រសើរ

---


# និយមន័យ និង​គណិតវិទ្យា

## ១. ​​បញ្ហា​ formal

ឱ្យ data $\{x_1, \ldots, x_n\}$ ដែល $x_i \in \mathbb{R}^d$ ​ហើយ​​​ ចំនួន cluster $K$។

​ស្វែង​រក assignment $C: \{1, \ldots, n\} \to \{1, \ldots, K\}$ ​និង centroid $\mu_1, \ldots, \mu_K$ ​ដែល minimize៖

$$
J(C, \mu) = \sum_{i=1}^n \|x_i - \mu_{C(i)}\|^2 = \sum_{k=1}^K \sum_{i \in C_k} \|x_i - \mu_k\|^2
$$

​​​ដែល $C_k = \{i : C(i) = k\}$ ​ជា set ​នៃ index ​ដែល​ស្ថិត​ក្នុង cluster $k$។

**​បញ្ហា​ស្នូល​៖** $J$ ​ឥត​មែន convex ​នៅ​ $(C, \mu)$ ​ទាំង​ពីរ ​ ​​ ​​ ​​ ​ហើយ search space ​ធំ​ឥត​ឈប់ ($K^n$ ​​​​​អាច​ assignment) → ​មិន​អាច​ដោះ​ស្រាយ​ optimal ​ច្បាស់​ៗ ​សម្រាប់ $K, n$ ​ធំ → **NP-hard**!

→ ​យើង​ប្រើ heuristic — Lloyd's algorithm។

## ២. Lloyd's algorithm (Standard K-Means)

**Initialization**៖ ​​ជ្រើស​ $\mu_1^{(0)}, \ldots, \mu_K^{(0)}$ ​​​ដោយ random ​ឬ k-means++.

**Iteration $t$**៖

**Step A — Assignment** (fix centroid, minimize over assignment)៖

$$
C(i)^{(t)} = \arg\min_k \|x_i - \mu_k^{(t-1)}\|^2
$$

→ ​ដាក់​ចំណុច​នី​មួយ​ៗ​​ ​ ​ទៅ​​​​ centroid ​ជិត​បំផុត។

**Step B — Update** (fix assignment, minimize over centroid)៖

$$
\mu_k^{(t)} = \frac{1}{|C_k^{(t)}|} \sum_{i \in C_k^{(t)}} x_i
$$

→ centroid ​ថ្មី = mean ​នៃ​ចំណុច​ខាង​ក្នុង cluster។

**Convergence**៖ ​ឈប់​នៅ​ពេល $C^{(t)} = C^{(t-1)}$ (​ឥត​ផ្លាស់​ប្ដូរ) — ​ច្បាស់​ ​ ​នឹង​​​ឈប់ ​ច្រើន​ដង​ប្រហែល​ 10-50 iterations។

## ៣. ​ហេតុ​អ្វី $J$ ​ដួល monotonically?

**Step A** ​​​បង្ហាញ​៖ ​ដោយ​ assignment $C^{(t)}$ ​នេះ — ​ឥត​មាន $C'$ ​ផ្សេង​ដែល​ $J(C', \mu^{(t-1)}) < J(C^{(t)}, \mu^{(t-1)})$ ​ដោយ​សារ​​​ដោះ​ស្រាយ optimal ​ដោយ pointwise។

**Step B** ​​​បង្ហាញ​៖ ​ដោយ​ centroid $\mu^{(t)}$ ​​​​ថ្មី — ​ឥត​មាន $\mu'$ ​ផ្សេង​ដែល $J(C^{(t)}, \mu') < J(C^{(t)}, \mu^{(t)})$ ​ដោយ​សារ​ mean = optimal solution ​សម្រាប់​ sum of squares (Ch 7 normal equation)។

→ **$J^{(t)} \le J^{(t-1)}$** ​ច្បាស់​ៗ​ → $J$ ​ដួល monotonic → ​​​ឈប់​នៅ local min ​ច្បាស់ (search space ​មាន​ត្រឹម​ $K^n$ ​ ​​​​អាច​ assignment → finite)។

## ៤. k-means++ initialization

​ ​បញ្ហា​នៃ random init៖ centroid 2 ​​​ដែល​ random ​នៅ​ជិត​គ្នា → cluster ​មួយ​​​ត្រូវ "split" → bad local min ​ច្បាស់។

**k-means++** (Arthur & Vassilvitskii, 2007)៖

1. ​ជ្រើស $\mu_1$ uniform random ​ពី data
2. ​សម្រាប់ $k = 2, \ldots, K$៖
   - សម្រាប់​ចំណុច​នី​មួយ​ៗ — គណនា $d(x_i) = \min_{j < k} \|x_i - \mu_j\|$ (distance ​ទៅ centroid ​ជិត​បំផុត)
   - ​ជ្រើស $\mu_k = x_i$ ​ដោយ probability $\propto d(x_i)^2$
3. ​បន្ទាប់​ — ​​ដំ​ណើរ​​ Lloyd's algorithm ​ធម្មតា

**​លទ្ធផល**៖
- ​​​ប្រសើរ​ជាង random ​ច្បាស់​ៗ (proven $O(\log K)$-approximation ​លើ optimal)
- ​ឧស្សាហកម្ម​ default — sklearn ​ឱ្យ k-means++ ​​​ដោយ​​ default

## ៥. ​ការ​ជ្រើស $K$

### Elbow method

​​ដាក់ K-Means សម្រាប់ $K = 1, 2, \ldots, K_\max$, ​​​ ​​ ​​ ​​ ​​​​​ ​​ ​​​ ​បន្ទាប់​មក​ plot $J(K)$ vs $K$៖

- $K$ ​​​​​តូច → $J$ ​ខ្ពស់ (cluster ​ធំ ​​​​​ឆ្គង)
- $K$ ​ធំ → $J$ ​ដួល (cluster ​​​​​តូច, fit closer)
- $K = n$ → $J = 0$ (centroid = ចំណុច​​​ផ្ទាល់)

→ ​​ស្វែង​រក "elbow" — ​ចំណុច​ដែល $J$ ​ឈប់​ដួល​ខ្លាំង។

​ស្វែង​រក​​ដោយ​​ heuristic៖

$$
K^* = \arg\min_K \left[ J(K) + \alpha K \right]
$$

(​​ដាក់ penalty លើ $K$ — ​សាមញ្ញ​​មិន​ ​​ច្បាស់​ៗ)

### Silhouette score

​សម្រាប់​​ ​ចំណុច $x_i$៖

- $a_i$ = mean distance ​ទៅ​ចំណុច​ផ្សេង​ខាង​ក្នុង cluster ​ដូច​គ្នា
- $b_i$ = mean distance ​ទៅ​ចំណុច​​​ក្នុង​ cluster ​ផ្សេង​ដែល​​ជិត​បំផុត

$$
s_i = \frac{b_i - a_i}{\max(a_i, b_i)} \in [-1, 1]
$$

- $s_i \approx 1$ — ​ល្អ (​ខាង​ក្នុង cluster ​ជិត, ​ខាង​ក្រៅ​ឆ្ងាយ)
- $s_i \approx 0$ — ​ស្ថិត​នៅ​ boundary
- $s_i < 0$ — ​​ច្បាស់​ខុស cluster!

**Silhouette score = mean $s_i$** ​លើ​ data ​ទាំង​អស់។ ​​ ​​ជ្រើស $K$ ​​​ដែល​មាន silhouette score ​ខ្ពស់​បំផុត។

### Gap statistic

​ប្រៀប​ធៀប $J(K)$ ​លើ data ​ពិត vs $J(K)$ ​លើ reference data (uniform random)៖

$$
\text{Gap}(K) = \mathbb{E}_\text{ref}[\log J_\text{ref}(K)] - \log J(K)
$$

​​​ជ្រើស $K$ ​ដែល​ Gap ​ខ្ពស់​បំផុត។

## ៦. ​ភាព​ស្មុគ​ស្មាញ​ Computational

- Iteration ​មួយ​៖ $O(nKd)$ — ​ដោយ​សារ​ត្រូវ​គណនា​ distance ​ពី​ចំណុច​នី​មួយ​ៗ ​ទៅ centroid ​នី​មួយ​ៗ
- Total: $O(t \cdot nKd)$ ​ដែល $t$ ​ជា ចំនួន iterations (​ច្រើន​ដង 10-50)
- **Mini-batch K-Means** — ​ប្រើ subset ​នៃ data ​​​សម្រាប់ update ​នី​មួយ​ៗ → ​​ល្អ​​​សម្រាប់ $n > 10^6$

## ៧. Connection to EM (preview)

K-Means = "hard assignment" version ​នៃ EM ​សម្រាប់ **Gaussian Mixture Model (GMM)**៖

| | K-Means | GMM (soft) |
|---|---|---|
| Assignment | $C(i) \in \{1, \ldots, K\}$ (hard) | $p(z_i = k \mid x_i)$ (soft, sum to 1) |
| Cluster shape | Spherical, equal size | Ellipsoidal, arbitrary scale |
| Cluster representation | Centroid $\mu_k$ | $(\mu_k, \Sigma_k, \pi_k)$ |
| Algorithm | Lloyd's (2 steps) | EM (E-step + M-step) |

→ GMM ​ផ្ដល់​ probability ​​ច្បាស់ + cluster shape ​ច្រួល → ​​ល្អ​​ខ្លាំង​ជាង​​នៅ​ពេល data ​មិន​មែន spherical។ ​យើង​នឹង​ឃើញ EM ​នៅ​ ​​ ​ ​ ​ ​​ ​​ ​​​ ​​​​​​ ​​​ ​​ ​​​ ​​ ​​ ​​​ ​ ​​​ ​​ ​​ ​​ ​​​ ​​ ​​​ ​​​ ​​ ​​ ​​​ ​​ ​​ ​​​ ​​ ​​​ ​​​ ​​ ​​ ​​​ ​​ ​​ ​​​ ​​ ​​​ ​​​ ​​ ​​ ​​​ ​​ ​​ ​​​ ​​ ​​​ ​​​ ​​ ​​ ​​​ ​​ ​​ ​​​ ​​ ​​​ ​​​ ​​ ​​ ​​​ ​​ ​​ ​​​ ​​ ​​​ ​​​ ​​ ​​ ​​​ ​​ មេរៀន​ក្រោយ។

---


## 🎮 ​រូបភាព interactive ១៖ K-Means animation — step ​​ដោយ​​ដៃ

ដាក់ K-Means ​លើ data 2D — ​ចុច "Step" ​ដើម្បី​​​ដំ​ណើរ assignment / update ​ ​​ ​ឆ្លាស់​គ្នា — ​​​មើល centroid ​​ផ្លាស់​ប្ដូរ ​​ ​​​ហើយ J ​ដួល​ ​ ​​​ ​​​​ ​​ខ្លាំង​​ៗ។

<div id="viz1" style="width:100%;max-width:800px;margin:0 auto;height:500px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  K = <span id="viz1-k" style="font-weight:bold;color:#7c3aed">3</span>
  <input id="viz1-k-slider" type="range" min="2" max="6" step="1" value="3" style="width:30%;max-width:250px"><br>
  <button id="viz1-step" style="margin-top:6px;padding:5px 14px;font-weight:600;cursor:pointer">▶ Step</button>
  &nbsp;
  <button id="viz1-run" style="padding:5px 14px;cursor:pointer">⏩ Run to end</button>
  &nbsp;
  <button id="viz1-reset" style="padding:5px 14px;cursor:pointer">🔁 Reset</button>
  &nbsp;
  <button id="viz1-new" style="padding:5px 14px;cursor:pointer">🎲 ​ទិន្នន័យ​ថ្មី</button><br>
  <span style="font-size:1.05em;margin-top:6px;display:inline-block">
    Iteration = <span id="viz1-iter" style="font-weight:bold;color:#1e40af">0</span>
    &nbsp;|&nbsp;
    Phase = <span id="viz1-phase" style="font-weight:bold;color:#dc2626">init</span>
    &nbsp;|&nbsp;
    J = <span id="viz1-j" style="font-weight:bold;color:#0f766e">--</span>
  </span>
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
    var COLORS = ['#dc2626', '#1e40af', '#10b981', '#f59e0b', '#7c3aed', '#0891b2'];
    var DATA = null, CENT = null, ASSIGN = null, ITER = 0, PHASE = 'init', K = 3;
    function genData() {
      DATA = [];
      var nC = 3 + Math.floor(Math.random() * 2);
      for (var c = 0; c < nC; c++) {
        var cx = -4 + 8 * Math.random();
        var cy = -4 + 8 * Math.random();
        for (var i = 0; i < 30; i++) {
          DATA.push([cx + 0.7 * randn(), cy + 0.7 * randn()]);
        }
      }
    }
    function initCent(k) {
      CENT = [];
      var used = {};
      for (var i = 0; i < k; i++) {
        var idx;
        do { idx = Math.floor(Math.random() * DATA.length); } while (used[idx]);
        used[idx] = true;
        CENT.push([DATA[idx][0], DATA[idx][1]]);
      }
      ASSIGN = DATA.map(function () { return -1; });
      ITER = 0;
      PHASE = 'init';
    }
    function assign() {
      var changed = false;
      for (var i = 0; i < DATA.length; i++) {
        var best = 0, bd = Infinity;
        for (var k = 0; k < CENT.length; k++) {
          var dx = DATA[i][0] - CENT[k][0];
          var dy = DATA[i][1] - CENT[k][1];
          var d = dx * dx + dy * dy;
          if (d < bd) { bd = d; best = k; }
        }
        if (ASSIGN[i] !== best) changed = true;
        ASSIGN[i] = best;
      }
      return changed;
    }
    function update() {
      var sums = CENT.map(function () { return [0, 0, 0]; });
      for (var i = 0; i < DATA.length; i++) {
        var k = ASSIGN[i];
        sums[k][0] += DATA[i][0];
        sums[k][1] += DATA[i][1];
        sums[k][2]++;
      }
      for (var k = 0; k < CENT.length; k++) {
        if (sums[k][2] > 0) {
          CENT[k][0] = sums[k][0] / sums[k][2];
          CENT[k][1] = sums[k][1] / sums[k][2];
        }
      }
    }
    function computeJ() {
      var s = 0;
      for (var i = 0; i < DATA.length; i++) {
        var k = ASSIGN[i];
        if (k < 0) continue;
        var dx = DATA[i][0] - CENT[k][0];
        var dy = DATA[i][1] - CENT[k][1];
        s += dx * dx + dy * dy;
      }
      return s;
    }
    function step() {
      if (PHASE === 'init' || PHASE === 'update') {
        assign();
        PHASE = 'assign';
      } else {
        update();
        PHASE = 'update';
        ITER++;
      }
    }
    function plot() {
      var traces = [];
      for (var k = 0; k < CENT.length; k++) {
        var xs = [], ys = [];
        for (var i = 0; i < DATA.length; i++) {
          if (ASSIGN[i] === k) { xs.push(DATA[i][0]); ys.push(DATA[i][1]); }
        }
        traces.push({
          x: xs, y: ys, mode: 'markers', name: 'cluster ' + (k + 1),
          marker: { color: COLORS[k], size: 9, line: { color: '#fff', width: 1 } }
        });
        traces.push({
          x: [CENT[k][0]], y: [CENT[k][1]], mode: 'markers',
          name: 'centroid ' + (k + 1), showlegend: false,
          marker: { color: COLORS[k], size: 20, symbol: 'x', line: { color: '#1f2937', width: 3 } }
        });
      }
      // Unassigned (init)
      if (PHASE === 'init') {
        var xs = [], ys = [];
        for (var i = 0; i < DATA.length; i++) {
          if (ASSIGN[i] === -1) { xs.push(DATA[i][0]); ys.push(DATA[i][1]); }
        }
        traces.unshift({
          x: xs, y: ys, mode: 'markers', name: 'unassigned',
          marker: { color: '#9ca3af', size: 8 }
        });
      }
      return traces;
    }
    function render() {
      var j = (PHASE === 'init') ? NaN : computeJ();
      document.getElementById('viz1-iter').textContent = ITER;
      document.getElementById('viz1-phase').textContent = PHASE;
      document.getElementById('viz1-j').textContent = isFinite(j) ? j.toFixed(2) : '--';
      Plotly.react('viz1', plot(), layout);
    }
    var layout = {
      xaxis: { title: 'x₁', range: [-7, 7] },
      yaxis: { title: 'x₂', range: [-7, 7], scaleanchor: 'x' },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    genData(); initCent(K);
    Plotly.newPlot('viz1', plot(), layout, { responsive: true, displayModeBar: false });
    render();
    document.getElementById('viz1-step').addEventListener('click', function () { step(); render(); });
    document.getElementById('viz1-run').addEventListener('click', function () {
      for (var i = 0; i < 30; i++) {
        var prev = JSON.stringify(ASSIGN);
        step();
        if (PHASE === 'update' && JSON.stringify(ASSIGN) === prev) break;
      }
      render();
    });
    document.getElementById('viz1-reset').addEventListener('click', function () { initCent(K); render(); });
    document.getElementById('viz1-new').addEventListener('click', function () { genData(); initCent(K); render(); });
    document.getElementById('viz1-k-slider').addEventListener('input', function () {
      K = parseInt(this.value);
      document.getElementById('viz1-k').textContent = K;
      initCent(K); render();
    });
  }
  init();
})();
</script>

> **សាក​មើល៖** ​ចុច Step ​​​​​ដើម្បី​​ឃើញ assignment ​ដំបូង — ​ចំណុច​​​​ប្ដូរ​ពណ៌។ ​ចុច​​ Step ​ម្តង​ទៀត — centroid (×) ​ផ្លាស់​ទី​​​ទៅ​​ mean។ ​​ស្លាប់​ៗ​​ — J ​ដួល​យ៉ាង​ច្បាស់ ​​​​ ​រហូត​ដល់​ centroid ​ឈប់​ផ្លាស់​​​​ប្ដូរ។


## 🎮 ​រូបភាព interactive ២៖ Elbow method — ​ជ្រើស $K$

​​ដាក់ K-Means ​សម្រាប់ $K = 1, \ldots, 10$, ​​​បន្ទាប់​មក plot WCSS vs $K$ — ​ស្វែង​រក "elbow" — ​ចំណុច​ដែល​ $J$ ​ឈប់​ដួល​ខ្លាំង។

<div id="viz2" style="width:100%;max-width:800px;margin:0 auto;height:440px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  ​​​​ចំនួន clusters ​ពិត​ = <span id="viz2-true" style="font-weight:bold;color:#7c3aed">4</span>
  <input id="viz2-true-slider" type="range" min="2" max="7" step="1" value="4" style="width:30%;max-width:250px"><br>
  <button id="viz2-new" style="margin-top:6px;padding:5px 14px;cursor:pointer">🎲 ​ទិន្នន័យ​ថ្មី</button>
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
    var DATA = null;
    function gen(K_true) {
      DATA = [];
      for (var c = 0; c < K_true; c++) {
        var cx = -5 + 10 * Math.random();
        var cy = -5 + 10 * Math.random();
        for (var i = 0; i < 40; i++) {
          DATA.push([cx + 0.6 * randn(), cy + 0.6 * randn()]);
        }
      }
    }
    function kmeansJ(K) {
      // Run k-means++ init + Lloyd's, return final J
      var best = Infinity;
      for (var attempt = 0; attempt < 5; attempt++) {
        var cent = [DATA[Math.floor(Math.random() * DATA.length)].slice()];
        for (var k = 1; k < K; k++) {
          var dists = DATA.map(function (p) {
            var bd = Infinity;
            for (var j = 0; j < cent.length; j++) {
              var dx = p[0] - cent[j][0], dy = p[1] - cent[j][1];
              var d = dx * dx + dy * dy;
              if (d < bd) bd = d;
            }
            return bd;
          });
          var total = dists.reduce(function (a, b) { return a + b; }, 0);
          var r = Math.random() * total, acc = 0, idx = 0;
          for (var i = 0; i < dists.length; i++) {
            acc += dists[i];
            if (acc >= r) { idx = i; break; }
          }
          cent.push(DATA[idx].slice());
        }
        var assign = DATA.map(function () { return -1; });
        for (var it = 0; it < 30; it++) {
          var changed = false;
          for (var i = 0; i < DATA.length; i++) {
            var bk = 0, bd = Infinity;
            for (var k = 0; k < K; k++) {
              var dx = DATA[i][0] - cent[k][0], dy = DATA[i][1] - cent[k][1];
              var d = dx * dx + dy * dy;
              if (d < bd) { bd = d; bk = k; }
            }
            if (assign[i] !== bk) { assign[i] = bk; changed = true; }
          }
          if (!changed) break;
          var sums = cent.map(function () { return [0, 0, 0]; });
          for (var i = 0; i < DATA.length; i++) {
            var k = assign[i];
            sums[k][0] += DATA[i][0];
            sums[k][1] += DATA[i][1];
            sums[k][2]++;
          }
          for (var k = 0; k < K; k++) if (sums[k][2] > 0) {
            cent[k][0] = sums[k][0] / sums[k][2];
            cent[k][1] = sums[k][1] / sums[k][2];
          }
        }
        var J = 0;
        for (var i = 0; i < DATA.length; i++) {
          var k = assign[i];
          var dx = DATA[i][0] - cent[k][0], dy = DATA[i][1] - cent[k][1];
          J += dx * dx + dy * dy;
        }
        if (J < best) best = J;
      }
      return best;
    }
    function plot() {
      var Ks = [], Js = [];
      for (var K = 1; K <= 10; K++) {
        Ks.push(K);
        Js.push(kmeansJ(K));
      }
      return [
        { x: Ks, y: Js, mode: 'lines+markers', name: 'WCSS J(K)',
          line: { color: '#7c3aed', width: 3 },
          marker: { color: '#7c3aed', size: 11 } }
      ];
    }
    var layout = {
      xaxis: { title: 'K (number of clusters)', dtick: 1 },
      yaxis: { title: 'WCSS J(K)' },
      margin: { t: 20, b: 50, l: 70, r: 30 },
      legend: { x: 0.6, y: 0.95, bgcolor: 'rgba(255,255,255,0.85)' },
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    gen(4);
    Plotly.newPlot('viz2', plot(), layout, { responsive: true, displayModeBar: false });
    function render() {
      var K_true = parseInt(document.getElementById('viz2-true-slider').value);
      document.getElementById('viz2-true').textContent = K_true;
      gen(K_true);
      Plotly.react('viz2', plot(), layout);
    }
    document.getElementById('viz2-true-slider').addEventListener('input', render);
    document.getElementById('viz2-new').addEventListener('click', render);
  }
  init();
})();
</script>

> **សាក​មើល៖** ​ប្ដូរ "​ចំនួន clusters ​ពិត​" ​ឆ្ពោះ​ទៅ 4 — ​មើល​​​ឃើញ elbow ​ច្បាស់​ៗ​​នៅ​ $K = 4$។ ​ប្ដូរ​ទៅ 6 — elbow ​ផ្លាស់​ទៅ $K = 6$។ Elbow method ​ល្អ​ខ្លាំង​សម្រាប់ data ​​​ ​​ដែល​មាន cluster ​ច្បាស់; ​​​​ ​ ​​​ខូច​ខ្លាំង​នៅ​ពេល cluster ​​​​​​ច្រៀក​ ​​ឆ្ងាយ​ៗ​​​។


## 🎮 ​រូបភាព interactive ៣៖ k-means++ vs random init

​សាក​ ​ដាក់​​ K-Means 30 ​ដង — ​មួយ​ដោយ random init, ​មួយ​ដោយ k-means++ — ​មើល histogram ​​​នៃ​ final $J$។

<div id="viz3" style="width:100%;max-width:800px;margin:0 auto;height:440px"></div>
<div style="max-width:800px;margin:8px auto;text-align:center;font-family:system-ui,sans-serif">
  K = <span id="viz3-k" style="font-weight:bold;color:#7c3aed">5</span>
  <input id="viz3-k-slider" type="range" min="2" max="8" step="1" value="5" style="width:30%;max-width:250px"><br>
  <button id="viz3-run" style="margin-top:6px;padding:5px 14px;font-weight:600;cursor:pointer">🔁 Run 30 trials</button>
  &nbsp;
  <button id="viz3-new" style="padding:5px 14px;cursor:pointer">🎲 ​ទិន្នន័យ​ថ្មី</button><br>
  <span style="font-size:1.05em;margin-top:6px;display:inline-block">
    Random mean J = <span id="viz3-r" style="font-weight:bold;color:#dc2626">--</span>
    &nbsp;|&nbsp;
    k-means++ mean J = <span id="viz3-pp" style="font-weight:bold;color:#0f766e">--</span>
  </span>
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
    var DATA = null;
    function gen() {
      DATA = [];
      var K_true = 5;
      for (var c = 0; c < K_true; c++) {
        var cx = -6 + 12 * Math.random();
        var cy = -6 + 12 * Math.random();
        for (var i = 0; i < 30; i++) {
          DATA.push([cx + 0.5 * randn(), cy + 0.5 * randn()]);
        }
      }
    }
    function lloyd(cent) {
      var assign = DATA.map(function () { return -1; });
      for (var it = 0; it < 30; it++) {
        var changed = false;
        for (var i = 0; i < DATA.length; i++) {
          var bk = 0, bd = Infinity;
          for (var k = 0; k < cent.length; k++) {
            var dx = DATA[i][0] - cent[k][0], dy = DATA[i][1] - cent[k][1];
            var d = dx * dx + dy * dy;
            if (d < bd) { bd = d; bk = k; }
          }
          if (assign[i] !== bk) { assign[i] = bk; changed = true; }
        }
        if (!changed) break;
        var sums = cent.map(function () { return [0, 0, 0]; });
        for (var i = 0; i < DATA.length; i++) {
          var k = assign[i];
          sums[k][0] += DATA[i][0]; sums[k][1] += DATA[i][1]; sums[k][2]++;
        }
        for (var k = 0; k < cent.length; k++) if (sums[k][2] > 0) {
          cent[k][0] = sums[k][0] / sums[k][2];
          cent[k][1] = sums[k][1] / sums[k][2];
        }
      }
      var J = 0;
      for (var i = 0; i < DATA.length; i++) {
        var k = assign[i];
        var dx = DATA[i][0] - cent[k][0], dy = DATA[i][1] - cent[k][1];
        J += dx * dx + dy * dy;
      }
      return J;
    }
    function initRandom(K) {
      var cent = [];
      var used = {};
      while (cent.length < K) {
        var idx = Math.floor(Math.random() * DATA.length);
        if (!used[idx]) { used[idx] = true; cent.push(DATA[idx].slice()); }
      }
      return cent;
    }
    function initPP(K) {
      var cent = [DATA[Math.floor(Math.random() * DATA.length)].slice()];
      while (cent.length < K) {
        var dists = DATA.map(function (p) {
          var bd = Infinity;
          for (var j = 0; j < cent.length; j++) {
            var dx = p[0] - cent[j][0], dy = p[1] - cent[j][1];
            var d = dx * dx + dy * dy;
            if (d < bd) bd = d;
          }
          return bd;
        });
        var total = dists.reduce(function (a, b) { return a + b; }, 0);
        var r = Math.random() * total, acc = 0, idx = 0;
        for (var i = 0; i < dists.length; i++) {
          acc += dists[i];
          if (acc >= r) { idx = i; break; }
        }
        cent.push(DATA[idx].slice());
      }
      return cent;
    }
    function run(K) {
      var Jr = [], Jpp = [];
      for (var t = 0; t < 30; t++) {
        Jr.push(lloyd(initRandom(K)));
        Jpp.push(lloyd(initPP(K)));
      }
      var meanR = Jr.reduce(function (a, b) { return a + b; }, 0) / Jr.length;
      var meanPP = Jpp.reduce(function (a, b) { return a + b; }, 0) / Jpp.length;
      document.getElementById('viz3-r').textContent = meanR.toFixed(1);
      document.getElementById('viz3-pp').textContent = meanPP.toFixed(1);
      return [
        { x: Jr, type: 'histogram', name: 'random init',
          marker: { color: 'rgba(220, 38, 38, 0.55)', line: { color: '#fff', width: 1 } },
          nbinsx: 15 },
        { x: Jpp, type: 'histogram', name: 'k-means++',
          marker: { color: 'rgba(15, 118, 110, 0.55)', line: { color: '#fff', width: 1 } },
          nbinsx: 15 }
      ];
    }
    var layout = {
      xaxis: { title: 'final J (WCSS)' },
      yaxis: { title: 'count' },
      margin: { t: 20, b: 50, l: 60, r: 30 },
      legend: { x: 0.6, y: 0.95, bgcolor: 'rgba(255,255,255,0.85)' },
      barmode: 'overlay',
      plot_bgcolor: '#fafafa', paper_bgcolor: 'rgba(0,0,0,0)'
    };
    gen();
    Plotly.newPlot('viz3', run(5), layout, { responsive: true, displayModeBar: false });
    function render() {
      var K = parseInt(document.getElementById('viz3-k-slider').value);
      document.getElementById('viz3-k').textContent = K;
      Plotly.react('viz3', run(K), layout);
    }
    document.getElementById('viz3-k-slider').addEventListener('input', render);
    document.getElementById('viz3-run').addEventListener('click', render);
    document.getElementById('viz3-new').addEventListener('click', function () { gen(); render(); });
  }
  init();
})();
</script>

> **សាក​មើល៖** k-means++ histogram (បៃតង) ​​នៅ​ប្រហែល​ J ​ទាប​ៗ ​+ មាន variance ​​​​​​​​​តូច; random (ក្រហម) ​មាន distribution ​ឆ្ងាយ ​​​​+ tail ​ខ្ពស់ ($J$ ​ខ្ពស់) — ​​​បាន​ ​ bad local min ​ច្រើន​ដង។ K ​ធំ → ​ភាព​​​​ខុស​គ្នា​​​ ​ច្បាស់​ខ្លាំង​ជាង។

---


# ឧទាហរណ៍

## ឧទាហរណ៍ 1៖ K-Means ​ដោយ​ដៃ ($K = 2$)

ឱ្យ​ data 1D៖

| $i$ | $x_i$ |
|---|---|
| 1 | 1 |
| 2 | 2 |
| 3 | 4 |
| 4 | 5 |
| 5 | 10 |
| 6 | 11 |

​​​ដាក់ K-Means ​ដោយ $K = 2$, init $\mu_1 = 1, \mu_2 = 10$.

**Iter 1 — Assign**៖

| $i$ | $\|x_i - 1\|$ | $\|x_i - 10\|$ | Cluster |
|---|---|---|---|
| 1 | 0 | 9 | 1 |
| 2 | 1 | 8 | 1 |
| 3 | 3 | 6 | 1 |
| 4 | 4 | 5 | 1 |
| 5 | 9 | 0 | 2 |
| 6 | 10 | 1 | 2 |

$C_1 = \{1, 2, 3, 4\}, C_2 = \{5, 6\}$

**Iter 1 — Update**៖

$\mu_1 = (1+2+4+5)/4 = 3$

$\mu_2 = (10+11)/2 = 10.5$

**Iter 2 — Assign**៖

| $i$ | $\|x_i - 3\|$ | $\|x_i - 10.5\|$ | Cluster |
|---|---|---|---|
| 1 | 2 | 9.5 | 1 |
| 2 | 1 | 8.5 | 1 |
| 3 | 1 | 6.5 | 1 |
| 4 | 2 | 5.5 | 1 |
| 5 | 7 | 0.5 | 2 |
| 6 | 8 | 0.5 | 2 |

$C_1, C_2$ ​​​ដូច​ iter 1 → **converged!**

**Final**៖ $\mu_1 = 3, \mu_2 = 10.5$, $J = (1{-}3)^2 + (2{-}3)^2 + (4{-}3)^2 + (5{-}3)^2 + (10{-}10.5)^2 + (11{-}10.5)^2 = 4 + 1 + 1 + 4 + 0.25 + 0.25 = 10.5$

## ឧទាហរណ៍ 2៖ Bad initialization → bad local min

​សាក​ ​ដាក់ K-Means ​លើ data ​ដូច​គ្នា​ ​​​​​ប៉ុន្តែ init $\mu_1 = 2, \mu_2 = 4$ (close together)៖

**Iter 1 — Assign**៖

| $i$ | $\|x_i - 2\|$ | $\|x_i - 4\|$ | Cluster |
|---|---|---|---|
| 1 | 1 | 3 | 1 |
| 2 | 0 | 2 | 1 |
| 3 | 2 | 0 | 2 |
| 4 | 3 | 1 | 2 |
| 5 | 8 | 6 | 2 |
| 6 | 9 | 7 | 2 |

$C_1 = \{1, 2\}, C_2 = \{3, 4, 5, 6\}$

**Update**៖ $\mu_1 = 1.5, \mu_2 = 7.5$

**Iter 2 — Assign**៖

| $i$ | $\|x_i - 1.5\|$ | $\|x_i - 7.5\|$ | Cluster |
|---|---|---|---|
| 1 | 0.5 | 6.5 | 1 |
| 2 | 0.5 | 5.5 | 1 |
| 3 | 2.5 | 3.5 | 1 |
| 4 | 3.5 | 2.5 | 2 |
| 5 | 8.5 | 2.5 | 2 |
| 6 | 9.5 | 3.5 | 2 |

$C_1 = \{1, 2, 3\}, C_2 = \{4, 5, 6\}$ — ​ផ្លាស់​ប្ដូរ!

**Update**៖ $\mu_1 = 7/3 ≈ 2.33, \mu_2 = 26/3 ≈ 8.67$

**Iter 3 — Assign**៖ $C_1 = \{1, 2, 3, 4\}, C_2 = \{5, 6\}$ — ​បន្ត converge ​ទៅ​ solution ​ដូច​ឧទាហរណ៍ 1!

**លំ​អៀង**៖ ​ឧទាហរណ៍​ខាង​ឆ្វេង​​​ converge ​​លឿន (2 iter); ​ឧទាហរណ៍ ​​​​​​​​​​​​​​​នេះ​ ​​​​​យូរ​ ​​​​​​​​ (3+ iter)។ ​​​ច្បាស់​នៅ​ data ​ស្មុគ​ស្មាញ​ — bad init → local min ​​​​​អន់ ​ ​​​​​​​ច្បាស់​​!

## ឧទាហរណ៍ 3៖ Elbow analysis

ឱ្យ​ WCSS ​ដែល​​​បាន​ពី K-Means ​លើ data PP customer 1000៖

| K | WCSS |
|---|---|
| 1 | 8420 |
| 2 | 4250 |
| 3 | 1820 |
| 4 | 1180 |
| 5 | 980 |
| 6 | 850 |
| 7 | 760 |
| 8 | 700 |

**Drop ​ពី $K = k-1$ ​ទៅ $K$**៖

| K | Drop |
|---|---|
| 2 | -4170 |
| 3 | -2430 |
| **4** | **-640** ⭐ |
| 5 | -200 |
| 6 | -130 |

→ **Elbow ​នៅ $K = 4$** — ​បន្ទាប់​​​ពី $K = 4$, drop ​​ត្រូវ​មិន​សំខាន់​ច្បាស់​ៗ​​។ ​​​ ​​​ ​​​ ​​​​ ​​​​​ច្បាស់​ ​​ — segment customer ​ជា 4 tiers។

---


# កូដ Python

## K-Means basic

```python
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Pipeline: standardize → K-Means
pipe = Pipeline([
    ('scale', StandardScaler()),
    ('km', KMeans(n_clusters=4, init='k-means++', n_init=10, random_state=42))
])
pipe.fit(X)

# Inspect
km = pipe.named_steps['km']
print(f'Inertia (WCSS) = {km.inertia_:.2f}')
print(f'Centroids (in standardized space):')
print(km.cluster_centers_)

# Predict cluster for new point
labels = pipe.predict(X)
new_label = pipe.predict([[100, 3, 2]])
```

## Elbow method

```python
import matplotlib.pyplot as plt

ks = range(1, 11)
inertias = []
for k in ks:
    km = Pipeline([
        ('scale', StandardScaler()),
        ('km', KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=42))
    ])
    km.fit(X)
    inertias.append(km.named_steps['km'].inertia_)

plt.plot(ks, inertias, 'b-o')
plt.xlabel('K'); plt.ylabel('Inertia (WCSS)')
plt.title('Elbow method')
plt.axvline(4, color='red', ls='--', label='elbow at K=4')
plt.legend(); plt.show()
```

## Silhouette score

```python
from sklearn.metrics import silhouette_score, silhouette_samples

scores = []
for k in range(2, 11):  # silhouette ​មិន​ ​ឥត​មាន​​ន័យ​នៅ​ K=1
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_std)
    score = silhouette_score(X_std, km.labels_)
    scores.append(score)
    print(f'K={k}: silhouette={score:.3f}')

best_k = 2 + np.argmax(scores)
print(f'Best K = {best_k}')
```

## Per-sample silhouette ​ការ​​​​​មើល​​​ច្បាស់

```python
km = KMeans(n_clusters=4, n_init=10, random_state=42).fit(X_std)
sample_scores = silhouette_samples(X_std, km.labels_)

# Plot ​​សម្រាប់​ inspect cluster ​ដែល​​ខូច
import matplotlib.pyplot as plt
y_lower = 10
for k in range(4):
    cluster_scores = sample_scores[km.labels_ == k]
    cluster_scores.sort()
    y_upper = y_lower + len(cluster_scores)
    plt.fill_betweenx(np.arange(y_lower, y_upper), 0, cluster_scores, alpha=0.7)
    y_lower = y_upper + 10
plt.axvline(sample_scores.mean(), color='red', ls='--')
plt.show()
```

## Mini-batch K-Means (large data)

```python
from sklearn.cluster import MiniBatchKMeans

# សម្រាប់ n > 100k ​ ​​​​​ — ​​លឿន​ខ្លាំង​​ ​ ​​ជាង KMeans
mb_km = MiniBatchKMeans(n_clusters=10, batch_size=1024,
                        n_init=10, random_state=42, max_iter=100)
mb_km.fit(X_large)
```

## ​មើល​ cluster profile

```python
# ​​មាន label ​​​​​​​ហើយ — ​​​​សួរ "តើ​​​អ្វី ​​ច្បាស់​ៗ ​​​​​​នៃ cluster នី​មួយ​ៗ?"
df['cluster'] = km.labels_
profile = df.groupby('cluster').agg({
    'transaction_count': ['mean', 'median'],
    'total_spend': ['mean', 'median'],
    'days_since_signup': 'mean',
    'days_inactive': 'mean'
})
print(profile)
```

## DBSCAN ​ ​​​សម្រាប់ non-spherical (preview)

```python
from sklearn.cluster import DBSCAN

# ​​​​​​​​​​​​​សម្រាប់ cluster ​មាន shape ​ឆ្គង​​ ​​ — DBSCAN ​​​​​​ល្អ​ជាង
dbscan = DBSCAN(eps=0.5, min_samples=5)
labels = dbscan.fit_predict(X_std)
# label = -1 → outlier (noise)
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
print(f'DBSCAN found {n_clusters} clusters + {(labels==-1).sum()} noise points')
```

---


# ​ការ​អនុវត្តន៍​ជាក់​ស្តែង

## Wing customer segmentation

Features: `transaction_count_30d`, `avg_amount`, `days_since_last_txn`, `category_diversity`, `peak_hour`

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

X = df[['txn_count_30d', 'avg_amount', 'days_inactive',
        'category_diversity', 'peak_hour']].values
X_std = StandardScaler().fit_transform(X)
km = KMeans(n_clusters=5, n_init=10, random_state=42).fit(X_std)

df['segment'] = km.labels_
profile = df.groupby('segment').mean()
```

**Result (typical)**៖
- Segment 0 — **Power user**: txn 60+/month, avg \$50
- Segment 1 — **Casual**: txn 10/month, avg \$15
- Segment 2 — **Dormant**: 90+ days inactive
- Segment 3 — **New**: <30 days signup
- Segment 4 — **Heavy diverse**: txn 40/month, ​ច្រើន category

→ Marketing campaign ​ផ្សេង​សម្រាប់ segment នី​មួយ​ៗ (eg. retention offer ​សម្រាប់ dormant; loyalty reward ​សម្រាប់ power user)។

## AMK borrower risk tiers

​មុន ​​ ​​​ដាក់ supervised model — ​​​ដាក់​ clustering ​ដើម្បី explore portfolio៖

```python
features = ['monthly_income', 'years_at_job', 'existing_debt',
            'past_repayment_rate', 'loan_amount_requested']
X = df[features].values
X_std = StandardScaler().fit_transform(X)

km = KMeans(n_clusters=4, n_init=10, random_state=42).fit(X_std)
df['risk_tier'] = km.labels_

# Compare default rate ​​ដោយ tier
default_by_tier = df.groupby('risk_tier')['defaulted'].mean()
print(default_by_tier)
# tier 0: 2%  → low risk
# tier 1: 8%  → medium
# tier 2: 18% → high
# tier 3: 35% → very high
```

→ ​ផ្ដល់​​ underwriter ​នូវ "natural grouping" ​​​ដើម្បី​​ default rate vs profile — ​​ឱ្យ​ design loan terms ​ច្បាស់​ៗ​ ​ ​សម្រាប់​ tier នី​មួយ​ៗ​​ ​​​ ​​​។

## Khmer news topic discovery

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Tokenize Khmer text → TF-IDF
tfidf = TfidfVectorizer(tokenizer=khmer_segment, max_features=5000,
                        min_df=5, max_df=0.5, sublinear_tf=True)
X_tfidf = tfidf.fit_transform(articles)

km = KMeans(n_clusters=10, n_init=10, random_state=42).fit(X_tfidf)

# Inspect top terms ​ក្នុង cluster នី​មួយ​ៗ
terms = tfidf.get_feature_names_out()
for k in range(10):
    centroid = km.cluster_centers_[k]
    top_idx = centroid.argsort()[-10:][::-1]
    print(f'Cluster {k}: {[terms[i] for i in top_idx]}')
```

→ Discover topic ​ដោយ​ខ្លួន — ​ច្បាស់​ដែល​ឃើញ "​នយោបាយ", "​កីឡា", "​សេដ្ឋកិច្ច", "​បច្ចេកវិទ្យា" ... ​ដោយ​មិន​ត្រូវ​ការ label!

## PP property market segments

```python
features = ['price_per_sqm', 'total_sqm', 'bedrooms', 'age',
            'lat', 'lon', 'has_garage', 'floors']
X = df[features].values
X_std = StandardScaler().fit_transform(X)

# Elbow + Silhouette → K = 3 (luxury / mid / budget)
km = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X_std)
df['tier'] = ['Luxury', 'Mid-market', 'Budget'][km.labels_]

# Visualization on map (PP coordinates)
import matplotlib.pyplot as plt
for tier, color in [('Luxury', 'gold'), ('Mid-market', 'blue'), ('Budget', 'green')]:
    sub = df[df['tier'] == tier]
    plt.scatter(sub['lon'], sub['lat'], c=color, label=tier, alpha=0.5)
plt.legend(); plt.title('PP property tiers'); plt.show()
```

## Wing anomaly detection

```python
# Cluster ​​​នៅ "ធម្មតា" → ​​ច្រើន​នៅ​​​ ​មួយ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​​ ​​ ​​​ ​​ ​​​ ​​ ​​ ​​​​​​​ ​​​ប្រភេទ — outlier ​ឆ្ងាយ​ពី centroid ទាំង​អស់
km = KMeans(n_clusters=10, n_init=10, random_state=42).fit(X_legit)

# សម្រាប់​ប្រតិបត្តិការ​ថ្មី
dists = km.transform(X_new)  # distance ​ទៅ​ centroid នី​មួយ​ៗ
min_dist = dists.min(axis=1)
threshold = np.percentile(km.transform(X_legit).min(axis=1), 99)
fraud_candidates = X_new[min_dist > threshold]
```

## Crop region clustering

​​ស្រែ​​​នៅ​​ភូមិ​ផ្សេង​ៗ — clustering ​ដោយ​ rainfall, soil, NDVI → ​ផ្ដល់​ recommendation ​ដាំ​ដុះ៖

```python
features = ['rainfall_mean', 'rainfall_std', 'soil_pH', 'NDVI_mean',
            'elevation', 'distance_to_water']
km = KMeans(n_clusters=5, n_init=10, random_state=42).fit(StandardScaler().fit_transform(X))

# Cluster 0: rice-friendly (high rain, low pH)
# Cluster 1: corn-friendly (medium rain, neutral pH)
# Cluster 2: fruit-friendly (low rain, high pH, high elevation)
# ...
```

---


# លំហាត់

### លំហាត់ 1 — K-Means ​ដោយ​ដៃ ($K = 2$)

ឱ្យ​ data 2D៖

| $i$ | $x_1$ | $x_2$ |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 2 | 1 |
| 3 | 4 | 3 |
| 4 | 5 | 4 |

ដាក់ K-Means ​ដោយ $K = 2$, init $\mu_1 = (1, 1), \mu_2 = (5, 4)$.

(a) Iter 1 — assignment + update<br>
(b) Iter 2 — assignment<br>
(c) ​​​​Converge ​ត្រឹម​ iter ​ប៉ុនមាន?

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**(a) Iter 1 — Assign**៖

| $i$ | $d_1^2$ | $d_2^2$ | Cluster |
|---|---|---|---|
| 1 | 0 | 25 | 1 |
| 2 | 1 | 18 | 1 |
| 3 | 13 | 2 | 2 |
| 4 | 25 | 0 | 2 |

$C_1 = \{1, 2\}, C_2 = \{3, 4\}$

**Update**: $\mu_1 = (1.5, 1), \mu_2 = (4.5, 3.5)$

**(b) Iter 2 — Assign**៖

| $i$ | $d_1^2$ | $d_2^2$ | Cluster |
|---|---|---|---|
| 1 | 0.25 | 18.5 | 1 |
| 2 | 0.25 | 12.5 | 1 |
| 3 | 10.25 | 0.5 | 2 |
| 4 | 21.25 | 0.5 | 2 |

$C_1, C_2$ ​​​ដូច iter 1 → **converged!**

**(c)** Converge ​ត្រឹម iter 2 (assignment ​ឥត​ផ្លាស់​ប្ដូរ​ពី iter 1)។

</details>

### លំហាត់ 2 — Elbow analysis

ឱ្យ WCSS៖

| K | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| J | 1200 | 600 | 280 | 200 | 170 | 145 | 130 | 120 |

តើ elbow ​នៅ​ $K$ ប៉ុនមាន?

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

Drop ​ពី $K-1 \to K$៖

| K | Drop | % drop |
|---|---|---|
| 2 | -600 | -50% |
| 3 | -320 | -53% |
| **4** | **-80** | **-29%** |
| 5 | -30 | -15% |
| 6 | -25 | -15% |
| 7 | -15 | -10% |
| 8 | -10 | -8% |

**Elbow ​នៅ $K = 4$** — drop ​ដួល​ខ្លាំង​​​ពី -320 (53%) ​ទៅ -80 (29%); ​បន្ទាប់​ ​​​​ ​​ — drop ​​ ​​​​​តូច​ខ្លាំង។

​ច្បាស់​​ៗ — $K = 4$ ​ល្អ​បំផុត​សម្រាប់ data ​នេះ។

</details>


### លំហាត់ 3 — Silhouette ​ដោយ​ដៃ

ឱ្យ​ data 1D ​ដែល​ត្រូវ​ ​ត្រូវ​ដាក់​ ​ ​ ​ ​​​ ​ ​​​ ​ដោយ K-Means $K = 2$៖

| $i$ | $x_i$ | Cluster |
|---|---|---|
| 1 | 1 | A |
| 2 | 2 | A |
| 3 | 3 | A |
| 4 | 7 | B |
| 5 | 8 | B |
| 6 | 9 | B |

​គណនា $s_3$ (silhouette ​សម្រាប់​​ point $i = 3$).

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

Point $i = 3$, $x_3 = 3$, ​ស្ថិត​ក្នុង cluster A.

**$a_3$** = mean distance ​ទៅ​ point ​ផ្សេង​ខាង​ក្នុង cluster A៖

$$
a_3 = \frac{|3 - 1| + |3 - 2|}{2} = \frac{2 + 1}{2} = 1.5
$$

**$b_3$** = mean distance ​ទៅ​ point ​នៅ​ cluster B (មាន​ត្រឹម​ B)៖

$$
b_3 = \frac{|3 - 7| + |3 - 8| + |3 - 9|}{3} = \frac{4 + 5 + 6}{3} = 5
$$

**Silhouette**៖

$$
s_3 = \frac{b_3 - a_3}{\max(a_3, b_3)} = \frac{5 - 1.5}{5} = \frac{3.5}{5} = 0.7
$$

**​ការ​បកស្រាយ​៖** $s_3 = 0.7$ — ​ល្អ​ច្បាស់​ៗ (close to 1) → point 3 ​​ស្ថិត​​ត្រឹមត្រូវ​​​​ក្នុង cluster A ​ច្បាស់​ៗ​​ — ​ឆ្ងាយ​ពី cluster B ​​ខ្លាំង។

</details>


### លំហាត់ 4 — ​អំពី K-Means

ឆ្លើយ​ True/False + ​​​បកស្រាយ​:

(a) K-Means ​ឱ្យ​ global optimum ​​​ច្បាស់​​ៗ<br>
(b) K-Means ​​ដំណើរ​ការ​​ល្អ​សម្រាប់ cluster ​ច្រួល (concentric circles)<br>
(c) ​​​​ត្រូវ standardize ​មុន K-Means​<br>
(d) Mini-batch K-Means ​ល្អ​ជាង​ KMeans ​​នៅ​ពេល $n$ ​​​​​តូច

<details markdown="1">
<summary><strong>បង្ហាញ​ចម្លើយ</strong></summary>

**(a) FALSE** — K-Means ​ឥត​មែន convex → ​ឈប់​នៅ local min ​ត្រឹម​ ​​ ​​​​ ​ ​អាស្រ័យ​លើ initialization។ ​ត្រូវ​សាក​ច្រើន​ដង (n_init=10) ​ឬ​ប្រើ k-means++ ​ដើម្បី​បាន local min ​​​ល្អ។

**(b) FALSE** — Concentric circles ​មាន cluster ​​​ ​​ច្រួល​មិន spherical → K-Means ​ខូច​​​ខ្លាំង; ​ត្រូវ​ប្រើ **spectral clustering** ​ឬ **DBSCAN**។ ​ច្បាស់​ច្នេះ​​ — K-Means ​ឆ្លុះ "​​​មធ្យម" → cluster ​​​​ ​មូល​ប្រហែល​ស្មើ​គ្នា​​ ​ ​​​​ ​​​ ​ល្អ​បំផុត។

**(c) TRUE** — Feature scale ​ផ្សេង​គ្នា → distance ​ឆ្លុះ​ feature ​​ធំ​ខ្លាំង → cluster ​​​​​ ​​ ​​​ ​​ខូច​ច្បាស់​ៗ​​។ ​​ច្បាស់​ច្នេះ — `StandardScaler` ​​មុន `KMeans`។

**(d) FALSE** — Mini-batch ​​​មាន​​ ​​​ប្រយោជន៍​​ ​នៅ​ពេល $n$ ​ធំ ($> 10^5$) — ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ច្បាស់​ៗ ​សម្រាប់ data ​ធំ​ ​ខ្លាំង។ ​នៅ​ពេល $n$ ​​​​​​តូច — KMeans ​ត្រូវ ​​​​ល្អ​ជាង (sampling noise ​​​​​ បាត់​ច្បាស់​ៗ)។

</details>

---

**​មេរៀន​បន្ទាប់ (ជំពូក 11):** Naive Bayes — model **probabilistic ​ដំបូង** ​ដែល​​​ យើង​ប្រើ​​ Bayes' rule ​ផ្ទាល់ + ​ការ​សន្មត​ "naive" ​​​ថា feature ​​ឯករា​ជ្យ ​​​ឱ្យ class។ ​យើង​ប្រើ​​ MLE ​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​​ ​ពី​មេរៀន 4 ​​​ ​ ​ ​ ​ ​​ ​​​ ​ ​​​ ​​​​​​​ ​​​ ​​ ​​ ​​​ ​​​ ​​ ​​ ​​​ ​​ ​​ ​​​ ​​ ​​ ​​​ ​​ ​​​​​​​ ​ ​ ​​​​​ ​​​ដើម្បី​ estimate parameter ​ច្បាស់​ៗ​ — ​ស្នូល Bayesian ​​ដែល​យើង​ ​​​​បាន ​​​​​ ​ ​​ ​ ​​ឃើញ​​ ​​​ ​​​ ​​​ ​ ​​​ ​ ​​​ដោយ​ ​ ​​​ ​ ​ផ្ទាល់។ Spam classifier, document classifier, Khmer text categorization — ​ច្រើន​ដង​ប្រើ Naive Bayes ​ដំបូង។
