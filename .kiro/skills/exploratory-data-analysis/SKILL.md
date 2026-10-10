---
name: exploratory-data-analysis
description: >
  Exploratory data analysis on data files. Use when a user provides a data file to
  explore, analyze, or summarize before further processing. Covers tabular data (CSV,
  Parquet, Excel, JSON), arrays (NPY, HDF5, Zarr), and time series. Generates a
  structured markdown report with quality metrics, statistical summaries, and downstream
  analysis recommendations. Not for implementing pipelines or ML models.
---

# Exploratory Data Analysis

## Invocation

Use when: user provides a data file to explore/summarize, needs a data quality report,
or asks what analysis fits a dataset.

Do NOT use when: building pipelines → `data-pipeline` · hypothesis testing →
`statistical-analysis` · ML training → `ml-model-testing`.

## Workflow

Single-agent: **senior-developer** (or **data-engineer** for large-scale pipeline
datasets).

### Step 1: File identification

- Identify format from extension, choose library, load with lazy evaluation when
  possible.

### Step 2: Structural analysis

- Dimensions, schema, memory footprint; sample >1M rows for initial exploration.

### Step 3: Data quality assessment

- Missing values: count, percentage, pattern (MCAR/MAR/MNAR)
- Duplicates: exact and near-duplicate detection
- Outliers: IQR and z-score for numerical columns
- Type consistency: mixed types within columns
- Range validation: implausible values

### Step 4: Statistical summary

Numerical: count, mean, std, min, P25, P50, P75, P95, P99, max, skewness, kurtosis.

Categorical: unique count, top-N frequencies, cardinality (low/medium/high).

Temporal: time range, gaps, sampling frequency, seasonality indicators.

### Step 5: Correlations

- Pearson (numerical), Cramér's V (categorical); highlight |r| > 0.7 and
  multicollinearity.

### Step 6: Generate report

Use `references/report_template.md`. Save as `{original_filename}_eda_report.md`.

## Key Libraries

| Format  | Library | Method                                |
| ------- | ------- | ------------------------------------- |
| CSV/TSV | Polars  | `pl.scan_csv()`                       |
| Parquet | Polars  | `pl.scan_parquet()`                   |
| Excel   | Polars  | `pl.read_excel()`                     |
| JSON    | Polars  | `pl.read_json()` / `pl.read_ndjson()` |
| HDF5    | h5py    | `h5py.File()`                         |
| NPY/NPZ | NumPy   | `np.load()`                           |
| Zarr    | zarr    | `zarr.open()`                         |

Always prefer Polars over Pandas. Use `pl.LazyFrame` for predicate and projection
pushdown.

## Output Format

Size each section to the dataset's actual findings; a clean dataset gets a short Data
Quality section, not a padded one.

Report must include:

1. **Executive Summary** — 3-5 line overview of key findings
2. **Basic Information** — file size, format, dimensions
3. **Data Quality** — completeness, validity, integrity
4. **Statistical Summary** — numerical and categorical statistics
5. **Key Findings** — notable patterns, issues, anomalies
6. **Recommendations** — preprocessing steps, suitable analyses, tools

## References

- `references/report_template.md` — Markdown template for EDA reports
- `references/general_scientific_formats.md` — Format-specific reading guidance

## Attribution

Based on the exploratory-data-analysis skill from
[K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)
(MIT License, K-Dense Inc.).
