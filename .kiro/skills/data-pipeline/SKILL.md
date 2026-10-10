---
name: data-pipeline
description: >
  Data pipeline with ML workflow. Use when designing or building a data pipeline that
  includes machine learning components. Covers architecture, ingestion, transformation,
  model integration, and quality gates. Not for pure data analysis without pipeline
  orchestration or ML-free ETL scripts.
---

# Data Pipeline Workflow

## Invocation

Use when: designing a batch or streaming pipeline, adding ML inference to an existing
pipeline, building ETL/ELT with quality gates, or integrating multiple data sources.

Do NOT use when: ML training/evaluation only (`ml-model-testing`), pure application
development (`spec-to-dev`), or infrastructure provisioning without data flow
(`cicd-pipeline-design`).

## Workflow

1. **software-architect** — Pipeline architecture:
   - Choose pattern: medallion (bronze/silver/gold), event-driven, or lambda.
   - Define data contracts between stages.
   - Identify sources, sinks, and transformation boundaries.
   - Specify SLAs (latency, freshness, completeness).

2. **data-engineer** — Implementation:
   - Build ingestion layer (connectors, schema validation). For connector and
     schema-validation patterns, load `references/data-engineer-patterns.md`.
   - Implement transformations (cleaning, enrichment, aggregation). For SQL
     transformation examples (window functions, incremental merges), load
     `references/data-engineer-sql.md`.
   - Add data quality checks at each stage boundary.
   - Configure orchestration (Airflow, dbt, or equivalent).
   - Ensure idempotency and exactly-once semantics where required.

3. **ai-engineer** — ML integration (if applicable):
   - Add model inference stage (batch or real-time).
   - Implement feature engineering pipeline.
   - Add model monitoring (drift detection, performance metrics).
   - Configure model versioning and A/B routing.

## Success Criteria

- Pipeline runs end-to-end without manual intervention.
- Data quality checks pass at each stage boundary.
- SLA targets met (latency, freshness).
- Schema changes handled gracefully (backward compatibility).
- Monitoring and alerting configured for pipeline health.
