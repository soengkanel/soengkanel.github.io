---
layout: post
title: "[ML Khmer] Ch 0: បុព្វកថា"
date: 2026-06-13 09:00:00 +0700
categories: machine-learning
tags: [ml-khmer, preface]
---

ស្វាគមន៍មកកាន់ស៊េរីប្លុក **ការរៀនម៉ាស៊ីនមូលដ្ឋាន** ជាភាសាខ្មែរ។ ប្រកាសនេះគឺជា Day 1 — ការណែនាំទូទៅអំពីស៊េរី, ខ្លឹមសារ, និងតម្រូវការចំណេះដឹង។

ស៊េរីនេះគឺជាការសម្របសម្រួលជាភាសាខ្មែរនៃសៀវភៅ *Machine Learning cơ bản* របស់លោក **Vũ Hữu Tiệp** ដោយមានការអនុញ្ញាតពីអ្នកនិពន្ធ។

---

# AI, ML, និង DL

មួយរយៈនេះ **បញ្ញាសិប្បនិម្មិត** (artificial intelligence, AI) បានជ្រៀតចូលក្នុងស្ទើរគ្រប់វិស័យនៃជីវភាពរស់នៅ — រថយន្តបើកដោយខ្លួនឯង, ប្រព័ន្ធ tag មុខលើ Facebook, Siri, ប្រព័ន្ធណែនាំ Netflix, Google Translate, AlphaGo...

- **AI** — បញ្ញាសិប្បនិម្មិត (វាលធំជាងគេ)
- **ML** — ការរៀនម៉ាស៊ីន (machine learning) — សំណុំរងនៃ AI
- **DL** — ការរៀនជ្រៅ (deep learning) — សំណុំរងនៃ ML

![ទំនាក់ទំនងរវាង AI, ML, និង DL](/images/ml-series/dl_gray.png)

> **កំណត់សម្គាល់៖** DL ⊂ ML ⊂ AI

---

# រចនាសម្ព័ន្ធស៊េរី

ស៊េរីនេះត្រូវបានបែងចែកជា ៨ ផ្នែកដូចសៀវភៅដើម៖

| ផ្នែក | ប្រធានបទ |
|---|---|
| ១ | គណិតវិទ្យាមូលដ្ឋាន (linear algebra, matrix calculus, probability) |
| ២ | គំនិតទូទៅនៃ ML, feature engineering, linear regression, overfitting |
| ៣ | គំរូ ML សាមញ្ញ — KNN, K-means, Naive Bayes |
| ៤ | បណ្តាញសរសៃប្រសាទ — perceptron, logistic regression, softmax, MLP |
| ៥ | ប្រព័ន្ធណែនាំ (recommendation systems) |
| ៦ | ការកាត់បន្ថយវិមាត្រ — SVD, PCA, LDA |
| ៧ | Convex Optimization |
| ៨ | Support Vector Machines (SVM) |

---

# តម្រូវការចំណេះដឹង

មុនពេលចាប់ផ្តើម, អ្នកគួរស្គាល់៖

- **គណិតវិទ្យា៖** linear algebra, matrix calculus, probability and statistics
- **ភាសាសរសេរកម្មវិធី៖** Python (ប្រើ **numpy** និង **scikit-learn**)

ប្រសិនបើខ្វះចំណេះដឹងគណិតវិទ្យាខ្លះ, កុំបារម្ភ — ផ្នែកទី ១ នឹងរំឭកចំណុចសំខាន់ៗ។

---

# វិធីសាស្ត្រ

រៀង​ក្បួនដោះស្រាយ ML នីមួយៗនឹងបង្ហាញតាម ៣ ជំហាន៖

1. **គំនិតវិចារណញ្ញាណ** (intuition) — តើមនុស្សគិតយ៉ាងណាដើម្បីដោះស្រាយបញ្ហានេះ?
2. **គំរូគណិតវិទ្យា** — បង្កើតជាបញ្ហាបង្កើនប្រសិទ្ធភាព (optimization problem)
3. **កូដ Python** — ផ្ទៀងផ្ទាត់លទ្ធផលជាមួយ numpy / scikit-learn

> **គោលការណ៍មួយ៖** *តែងតែចាប់ផ្តើមពីរបស់សាមញ្ញ*។ ក្បួនដោះស្រាយសាមញ្ញឱ្យយើងយល់បញ្ហាបានលឿន មុននឹងផ្លាស់ទៅរកគំរូស្មុគស្មាញ។

---

# អំពីការដាក់សញ្ញា

- ពាក្យបច្ចេកទេសខ្មែរនឹងភ្ជាប់ជាមួយពាក្យអង់គ្លេសដើមនៅពេលលើកឡើងលើកដំបូង — ឧ. *ការរៀនម៉ាស៊ីន (machine learning, ML)*។
- ឈ្មោះបណ្ណាល័យ Python (numpy, scikit-learn) — រក្សាជាភាសាអង់គ្លេស។
- កូដប្រភពនឹងបង្ហាញក្នុង Jupyter notebook នៅចុងជំពូកនីមួយៗ។

---

# ប្រភពយោងបន្ថែម

ប្រសិនបើអ្នកចង់ស្វែងយល់បន្ថែម៖

- វគ្គសិក្សា **Machine Learning** របស់ Andrew Ng លើ Coursera
- វគ្គ **Deep Learning Specialization** លើ Coursera
- *Pattern Recognition and Machine Learning* — C. Bishop, Springer 2006
- *Deep Learning* — I. Goodfellow et al., MIT Press 2016
- *Convex Optimization* — S. Boyd, Cambridge 2004

---

# អំពីប្រភពដើម

ស៊េរីនេះគឺជាការបកប្រែ/សម្របសម្រួលជាភាសាខ្មែរនៃសៀវភៅ **Machine Learning cơ bản** របស់លោក **Vũ Hữu Tiệp**, ដោយមានការអនុញ្ញាតពីអ្នកនិពន្ធ។

- ប្រភពដើម៖ [machinelearningcoban.com](https://machinelearningcoban.com)
- កូដប្រភពសៀវភៅ៖ [github.com/tiepvupsu/ebookMLCB](https://github.com/tiepvupsu/ebookMLCB)

---

**ថ្ងៃបន្ទាប់ (Day 2):** ផ្នែកទី ១ — ការរំឭកគណិតវិទ្យាសម្រាប់ ML (linear algebra មូលដ្ឋាន)។
