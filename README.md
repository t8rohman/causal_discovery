# Causal Discovery & Inference

**"Correlation is not causation."**

The age-old adage "correlation is not causation" highlights a critical limitation in data analysis. Traditionally, we rely on correlations to understand how variables are associated. However, correlation simply shows a link, not a cause-and-effect relationship.

A classic example is the link between ice cream sales and shark attacks. Data might show both rise during summer, tempting us to believe ice cream consumption somehow causes shark attacks! But the real culprit is likely a lurking third variable: hot weather. Hot weather naturally leads to people buying more ice cream and spending more time at the beach, increasing the chance of encountering sharks.

This is where causal discovery and inference come in. These fields aim to bridge the gap beyond correlation and understand true cause-and-effect relationships. They work in tandem:

- **Causal discovery** is like detective work. It  focuses on identifying  causal relationships from data. Imagine you have a bunch of observations: ice cream sales go up, and so do sunburn rates. Causal discovery helps you figure out if sunshine causes people to buy ice cream (direct cause) or if both are caused by a hot summer (indirect cause).
- **Causal inference** goes a step further. Once you have a suspected causal relationship, causal inference estimates the magnitude or strength of that effect. Continuing the ice cream example, causal inference helps you determine how much sunburn rates actually increase ice cream sales (by a specific percentage or amount).

By moving beyond correlation with causal inference, we can now make a more definitive statement: "X causes Y" instead of just "X is associated with Y". Understanding true cause-and-effect relationships is crucial for effective decision-making across various fields. In medicine, it can determine a new drug's true effectiveness. In marketing, it can reveal the factors that truly drive sales.

This notebook will go deep into the **theory behind causal discovery and inference, explore some algorithms used for these tasks, and introduce Python libraries** that can help you perform causal analysis. It's divided into several sections:

1. Introduction to Causal Graph
2. Confounders, Colliders, and Mediators
3. Causal Discovery with PC Algorithm
4. Causal Effect Size with Bayesian Network and SEM
