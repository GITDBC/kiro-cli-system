---
name: statistical-analysis
description: >
  Guided statistical analysis with test selection and reporting. Use when choosing
  appropriate statistical tests, checking assumptions, calculating effect sizes,
  conducting power analyses, or reporting results in APA format. Covers hypothesis
  testing (t-test, ANOVA, chi-square, non-parametric), regression, correlation, and
  Bayesian methods. Not for implementing ML models or data pipelines.
---

# Statistical Analysis

## Invocation

Use when: choosing statistical tests, checking assumptions, running hypothesis tests,
regression/correlation, effect sizes, power analysis, APA reporting, Bayesian analysis.

Do NOT use when: building ML models → `ml-model-testing` · data pipelines →
`data-pipeline` · exploring data → `exploratory-data-analysis`.

## Workflow

Single-agent: **kpi-analyst** (+ `senior-developer` for implementing the analysis in
code, e.g. running the chosen test in a notebook or script).

### Phase 1: Test selection

Use `references/test_selection_guide.md`:

- 2 groups → t-test / Mann-Whitney
- 3+ groups → ANOVA / Kruskal-Wallis
- Relationships → Pearson/Spearman, regression
- Categorical outcomes → chi-square, Fisher's exact, logistic regression
- Time-to-event → Log-rank, Cox proportional hazards

### Phase 2: Assumption checking

Use `references/assumptions_and_diagnostics.md` and `references/assumption_checks.py`:

1. Independence (study design review)
2. Normality (Shapiro-Wilk + Q-Q plot; robust for n > 30)
3. Homogeneity of variance (Levene's test)
4. Linearity (residual plots for regression)
5. Multicollinearity (VIF < 5 for regression)

Violations: mild + large n → proceed (document) · moderate → non-parametric · severe →
transform or robust methods.

### Phase 3: Analysis execution

| Library       | Use case                                      |
| ------------- | --------------------------------------------- |
| `scipy.stats` | Core tests (t-test, chi-square, Mann-Whitney) |
| `pingouin`    | User-friendly tests with effect sizes         |
| `statsmodels` | Regression, GLM, time series, diagnostics     |
| `pymc`        | Bayesian modeling                             |
| `arviz`       | Bayesian diagnostics and visualization        |

### Phase 4: Effect sizes

Always calculate alongside p-values. See `references/effect_sizes_and_power.md`:

| Test        | Effect size | Small | Medium | Large |
| ----------- | ----------- | ----- | ------ | ----- |
| t-test      | Cohen's d   | 0.20  | 0.50   | 0.80  |
| ANOVA       | η²_p        | 0.01  | 0.06   | 0.14  |
| Correlation | r           | 0.10  | 0.30   | 0.50  |
| Regression  | R²          | 0.02  | 0.13   | 0.26  |
| Chi-square  | Cramér's V  | 0.07  | 0.21   | 0.35  |

### Phase 5: Reporting

Follow `references/reporting_standards.md`. Every report includes:

1. Descriptive statistics (M, SD, n per group)
2. Test statistic, degrees of freedom, exact p-value
3. Effect size with confidence interval
4. Assumption checks performed and results
5. All planned analyses (including non-significant)

APA example:

> Group A (n = 48, M = 75.2, SD = 8.5) scored significantly higher than Group B (n = 52,
> M = 68.3, SD = 9.2), t(98) = 3.82, p < .001, d = 0.77, 95% CI [0.36, 1.18].

## Bayesian Analysis

Use when: prior information available · direct probability statements needed · quantify
evidence for null · small samples.

See `references/bayesian_statistics.md` for prior selection, model specification,
convergence diagnostics, and reporting.

## Common Pitfalls

- P-hacking: don't test multiple ways until significant
- Confusing significance with importance (effect size matters)
- Ignoring assumptions without documenting
- Not correcting for multiple comparisons (Bonferroni, FDR)
- Post-hoc power analysis (use sensitivity analysis instead)

## References

- `references/test_selection_guide.md` — Decision tree for test selection
- `references/assumptions_and_diagnostics.md` — Checking and handling violations
- `references/effect_sizes_and_power.md` — Effect sizes, CIs, power analysis
- `references/bayesian_statistics.md` — Bayesian methods guide
- `references/reporting_standards.md` — APA reporting guidelines
- `references/assumption_checks.py` — Automated assumption checking script

## Attribution

Based on the statistical-analysis skill from
[K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)
(MIT License, K-Dense Inc.).
