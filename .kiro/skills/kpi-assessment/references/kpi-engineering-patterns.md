# KPI Engineering Patterns & Anti-Patterns

Reference for the kpi-analyst agent. Covers correct aggregation, percentile analysis,
edge-case handling, temporal normalization, cross-layer correlation, and catalog
templates.

## Online References

## Pattern: Explicit Numerator / Denominator

Every KPI must be defined as a ratio with clearly identified numerator and denominator
counters.

```yaml
kpi:
  name: "E-RAB Setup Success Rate"
  numerator:
    counter: "ERAB_Setup_Succ"
    description: "E-RAB successfully established"
  denominator:
    counter: "ERAB_Setup_Att"
    description: "E-RAB setup attempts"
  formula: "(numerator / denominator) × 100"
  unit: "%"
  direction: "higher_is_better"
```

Why: eliminates ambiguity about what is measured, enables automated validation, and
makes counter-to-KPI traceability auditable.

## Anti-Pattern: Averaging Averages

**Problem:** Computing a network-wide KPI by averaging per-cell KPI values.

```python
# WRONG — averaging averages
cell_kpis = [99.8, 99.5, 50.0]  # cell C has 2 attempts, 1 success
network_avg = sum(cell_kpis) / len(cell_kpis)  # 83.1% — misleading
```

This gives equal weight to a cell with 2 attempts and a cell with 10,000 attempts.

**Fix:** Always aggregate from raw counters, then compute the ratio.

```python
# CORRECT — weighted aggregation from counters
cells = [
    {"succ": 9980, "att": 10000},  # cell A: 99.8%
    {"succ": 4975, "att": 5000},   # cell B: 99.5%
    {"succ": 1,    "att": 2},      # cell C: 50.0%
]
total_succ = sum(c["succ"] for c in cells)  # 14956
total_att = sum(c["att"] for c in cells)    # 15002
network_kpi = (total_succ / total_att) * 100  # 99.69% — correct
```

**Rule:** `KPI_aggregated = Σ(numerator_i) / Σ(denominator_i) × 100`

This applies to all ratio KPIs: success rates, drop rates, utilization. The only
exception is throughput, where you must decide between per-user average and cell
aggregate.

## Pattern: Percentile Analysis vs Thresholds

Averages hide distribution tails. Use percentiles for integrity KPIs.

| Metric       | P50 (median) | P95      | P99      | Use Case                |
| ------------ | ------------ | -------- | -------- | ----------------------- |
| DL User Tput | 25 Mbps      | 5 Mbps   | 1.2 Mbps | User experience at edge |
| Latency      | 12 ms        | 45 ms    | 120 ms   | Real-time service SLA   |
| RSRP         | -85 dBm      | -110 dBm | -118 dBm | Coverage assessment     |

**When to use each:**

- **P50:** Typical user experience. Use for benchmarking and trending.
- **P95:** Worst 5% of users. Use for SLA compliance and coverage thresholds.
- **P99:** Extreme edge cases. Use for URLLC and mission-critical services.
- **Threshold-based:** `% cells with KPI > target`. Example: "95% of cells have DL PRB
  Util < 70%".

```python
import numpy as np

samples = [...]  # per-user throughput samples
p50 = np.percentile(samples, 50)
p95 = np.percentile(samples, 5)   # NOTE: for throughput, P95 = 5th percentile (worst 5%)
p99 = np.percentile(samples, 1)   # worst 1%

# For latency (higher is worse), P95 = 95th percentile
latency_p95 = np.percentile(latency_samples, 95)
```

**Key distinction:** For "higher is better" metrics (throughput), P95 worst = 5th
percentile. For "lower is better" metrics (latency, BLER), P95 worst = 95th percentile.

## Anti-Pattern: Silent Division by Zero

**Problem:** Cells with zero attempts produce `0/0 = NaN` or crash. Silently replacing
with 0% or 100% corrupts analysis.

```python
# WRONG — silent corruption
def calc_sr(succ, att):
    if att == 0:
        return 100.0  # assumes "no attempts = perfect" — WRONG
    return (succ / att) * 100
```

**Fix:** Exclude cells with denominator below a minimum threshold. Report them
separately.

```python
MIN_ATTEMPTS = 10  # configurable per KPI

def calc_sr(succ: int, att: int) -> float | None:
    """Returns SR or None if insufficient samples."""
    if att < MIN_ATTEMPTS:
        return None  # excluded from aggregation, flagged for review
    return (succ / att) * 100

# Aggregation: filter None values, report excluded cell count
results = [calc_sr(c["succ"], c["att"]) for c in cells]
valid = [(c, r) for c, r in zip(cells, results) if r is not None]
excluded_count = len(cells) - len(valid)

# Aggregate from raw counters of valid cells only
agg_succ = sum(c["succ"] for c, _ in valid)
agg_att = sum(c["att"] for c, _ in valid)
network_kpi = (agg_succ / agg_att) * 100 if agg_att > 0 else None
```

**Minimum attempt thresholds (typical):**

| KPI Type        | Min Attempts | Rationale                           |
| --------------- | ------------ | ----------------------------------- |
| RRC Setup SR    | 10           | Low-traffic cells excluded          |
| HO SR           | 5            | Some cells have few HO attempts     |
| PRB Utilization | N/A          | Always has denominator (total PRBs) |
| Throughput      | 10 samples   | Need statistical significance       |

## Pattern: Temporal Normalization

Raw counters are cumulative over the measurement period (typically 15 min or 1 hour).
Normalize for comparison.

### Busy Hour Analysis

```python
# Identify busy hour: hour with highest traffic volume
hourly_volumes = df.groupby(df["timestamp"].dt.hour)["dl_volume_bytes"].sum()
busy_hour = hourly_volumes.idxmax()

# Filter KPIs to busy hour only for capacity assessment
bh_data = df[df["timestamp"].dt.hour == busy_hour]
```

**Busy Hour definition (ITU-T):** The continuous 1-hour period with the highest traffic
load. In practice, use the hour with the highest DL data volume or highest PRB
utilization.

### Normalization periods

| Analysis Type    | Period    | Use Case                                |
| ---------------- | --------- | --------------------------------------- |
| Real-time alarm  | 15 min    | Immediate degradation detection         |
| Daily trending   | 1 hour    | Busy hour identification, daily pattern |
| Weekly reporting | Busy hour | Capacity planning, SLA reporting        |
| Dimensioning     | Busy hour | Network design, traffic forecast        |

### Rate normalization

```python
# Convert volume counter to rate
dl_rate_mbps = (dl_volume_bytes * 8) / (period_seconds * 1e6)

# Convert event counter to rate
ho_attempts_per_hour = ho_att_count * (3600 / period_seconds)
```

## Pattern: Cross-Layer Correlation

Problems rarely exist in a single layer. Correlate radio, transport, and core KPIs.

### Correlation Matrix — Common Fault Scenarios

| Symptom (Radio)         | Check (Transport)   | Check (Core)        | Likely Root Cause        |
| ----------------------- | ------------------- | ------------------- | ------------------------ |
| High ERAB Drop Rate     | S1 link utilization | MME pool load       | Transport congestion     |
| Low DL Throughput       | Backhaul throughput | PGW/UPF load        | Backhaul bottleneck      |
| High HO Failure Rate    | X2 link status      | —                   | X2 transport failure     |
| High RRC Setup Failure  | —                   | MME overload reject | Core congestion          |
| High BLER + low RSRP    | —                   | —                   | RF coverage issue        |
| High BLER + normal RSRP | —                   | —                   | Interference (PCI clash) |

### Correlation workflow

```
1. Identify degraded KPI (e.g., ERAB Drop Rate > threshold)
2. Check time correlation: did degradation start at a specific time?
3. Check spatial correlation: single cell, cluster, or network-wide?
   - Single cell → RF/hardware issue
   - Cluster → shared transport/parameter change
   - Network-wide → core/platform issue
4. Check cross-layer counters at same time/location
5. Narrow root cause using correlation matrix above
```

## Template: KPI Catalog Entry (Markdown)

Use this template when defining new KPIs:

```markdown
### <KPI Name>

- **ID:** `<DOMAIN>-<SEQ>` (e.g., ACC-001)
- **Domain:** Accessibility | Retainability | Mobility | Integrity | Availability |
  Utilization
- **Formula:** `<KPI> = (<numerator_counter> / <denominator_counter>) × 100`
- **Unit:** % | Mbps | ms | count
- **Direction:** higher_is_better | lower_is_better
- **Target:** <operator-defined threshold>
- **Granularity:** Cell | Sector | Site | Cluster | Region | Network
- **Period:** 15 min | 1 hour | Busy Hour | Daily
- **Counters:**
  - `<counter_name>` — <description>
  - `<counter_name>` — <description>
- **Filters:** <exclude conditions, e.g., "exclude cells with att < 10">
- **Notes:** <operational context, common pitfalls>
```

## Template: Measurement Request List

When requesting PM data extraction, use this format:

```markdown
## Measurement Request

- **Scope:** <Region / Cluster / Cell list>
- **Period:** <start_date> to <end_date>
- **Granularity:** <15min | 1hour | daily>
- **Object level:** <Cell | Site>

### Required Counters

| #   | Counter Name        | Description                | Layer |
| --- | ------------------- | -------------------------- | ----- |
| 1   | RRC_Conn_Setup_Att  | RRC setup attempts         | Radio |
| 2   | RRC_Conn_Setup_Succ | RRC setup successes        | Radio |
| 3   | ERAB_Setup_Att      | E-RAB setup attempts       | Radio |
| 4   | ERAB_Setup_Succ     | E-RAB setup successes      | Radio |
| 5   | DL_PRB_Used_Avg     | Avg DL PRBs used per TTI   | Radio |
| 6   | DL_Data_Volume      | DL PDCP SDU volume (bytes) | Radio |

### Derived KPIs

| KPI               | Formula                                     |
| ----------------- | ------------------------------------------- |
| RRC Setup SR (%)  | (Counter_2 / Counter_1) × 100               |
| ERAB Setup SR (%) | (Counter_4 / Counter_3) × 100               |
| DL PRB Util (%)   | (Counter_5 / Total_DL_PRBs) × 100           |
| DL Throughput     | (Counter_6 × 8) / Period_seconds / 1e6 Mbps |

### Filters & Exclusions

- Exclude cells with < 10 attempts in denominator
- Exclude cells administratively locked during period
- Report excluded cell count per KPI
```
