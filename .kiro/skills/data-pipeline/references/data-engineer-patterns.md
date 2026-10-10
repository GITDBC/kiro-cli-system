# Data Engineer — Technical Patterns

Reference patterns for the data-engineer agent. Load when building pipelines, schema
validation, or data quality checks.

## Spark Pipeline (PySpark + Delta Lake)

```python
import logging
from datetime import datetime, UTC

from delta.tables import DeltaTable
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    current_timestamp,
    desc,
    lit,
    row_number,
)
from pyspark.sql.window import Window

logger = logging.getLogger(__name__)


def ingest_bronze(
    spark: SparkSession,
    source_path: str,
    bronze_table: str,
    source_system: str,
) -> int:
    """
    Ingest raw data into the bronze layer (append-only).

    Args:
        spark: Active Spark session.
        source_path: Path to source data files.
        bronze_table: Delta table path for bronze layer.
        source_system: Name of the source system.

    Returns:
        Number of records ingested.
    """

    df = (
        spark.read.format("json")
        .option("inferSchema", "true")
        .load(source_path)
    )
    df = (
        df.withColumn("_ingested_at", current_timestamp())
        .withColumn("_source_system", lit(source_system))
        .withColumn("_source_file", col("_metadata.file_path"))
    )
    df.write.format("delta").mode("append").option(
        "mergeSchema", "true"
    ).save(bronze_table)

    count = df.count()
    logger.info("[INFO] Ingested %d records into bronze.", count)
    return count


def upsert_silver(
    spark: SparkSession,
    bronze_table: str,
    silver_table: str,
    pk_cols: list[str],
) -> None:
    """
    Cleanse and deduplicate bronze data into silver layer.

    Args:
        spark: Active Spark session.
        bronze_table: Delta table path for bronze layer.
        silver_table: Delta table path for silver layer.
        pk_cols: Primary key columns for deduplication.

    Returns:
        None.
    """

    source = spark.read.format("delta").load(bronze_table)

    window = Window.partitionBy(*pk_cols).orderBy(
        desc("_ingested_at")
    )
    source = (
        source.withColumn("_rank", row_number().over(window))
        .filter(col("_rank") == 1)
        .drop("_rank")
    )

    if DeltaTable.isDeltaTable(spark, silver_table):
        target = DeltaTable.forPath(spark, silver_table)
        merge_cond = " AND ".join(
            f"target.{c} = source.{c}" for c in pk_cols
        )
        (
            target.alias("target")
            .merge(source.alias("source"), merge_cond)
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )
    else:
        source.write.format("delta").mode("overwrite").save(
            silver_table
        )

    logger.info("[INFO] Silver upsert completed.")
```

## dbt Data Quality Contract

```yaml
# models/silver/schema.yml
version: 2

models:
  - name: silver_orders
    description: "Cleansed, deduplicated order records. SLA: refreshed every 15 min."
    config:
      contract:
        enforced: true
    columns:
      - name: order_id
        data_type: string
        constraints:
          - type: not_null
          - type: unique
        tests:
          - not_null
          - unique
      - name: customer_id
        data_type: string
        tests:
          - not_null
          - relationships:
              to: ref('silver_customers')
              field: customer_id
      - name: revenue
        data_type: decimal(18, 2)
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 1000000
      - name: order_date
        data_type: date
        tests:
          - not_null
    tests:
      - dbt_utils.recency:
          datepart: hour
          field: _updated_at
          interval: 1
```

## Pipeline Observability

```python
import logging
from dataclasses import dataclass
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


@dataclass(slots=True, kw_only=True)
class QualityCheckResult:
    """
    Result of a data quality validation.

    Attributes:
        check_name: Name of the quality check.
        passed: Whether the check passed.
        evaluated: Number of expectations evaluated.
        failed: Number of expectations that failed.
        checked_at: Timestamp of the check.
    """

    check_name: str
    passed: bool
    evaluated: int
    failed: int
    checked_at: datetime


def validate_silver_layer(
    df_stats: dict[str, int],
    check_name: str,
) -> QualityCheckResult:
    """
    Validate silver layer data quality.

    Args:
        df_stats: Dictionary with quality check statistics.
        check_name: Name for this quality check run.

    Returns:
        Quality check result with pass/fail status.

    Raises:
        ValueError: If critical quality checks fail.
    """

    result = QualityCheckResult(
        check_name=check_name,
        passed=df_stats["failed"] == 0,
        evaluated=df_stats["evaluated"],
        failed=df_stats["failed"],
        checked_at=datetime.now(tz=UTC),
    )

    if not result.passed:
        error_message = (
            f"[ERROR] Quality check '{check_name}' failed: "
            f"{result.failed}/{result.evaluated} checks failed."
        )
        logger.error(error_message)
        raise ValueError(error_message)

    logger.info(
        "[INFO] Quality check '%s' passed: %d/%d.",
        check_name,
        result.evaluated,
        result.evaluated,
    )

    return result
```
