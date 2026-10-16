# KPI Engineering Patterns & Anti-Patterns

Reference for the kpi-analyst agent: aggregation rules, the percentile-direction
convention, minimum-attempt thresholds, normalization periods, the cross-layer fault
matrix, and the catalog and measurement-request templates.

## Aggregation Rules

- Every KPI is a ratio of named numerator and denominator counters, never an implicit
  definition.
- Aggregate from raw counters, never by averaging per-cell KPI values:
  `KPI_aggregated = Σ(numerator_i) / Σ(denominator_i) × 100`. The one exception is
  throughput, where per-user average and cell aggregate must be chosen explicitly.

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

## Low-Denominator Cells

Never replace `0/0` with 0% or 100%. Exclude cells whose denominator is below a per-KPI
minimum from aggregation, aggregate the remaining cells from raw counters, and report
the excluded cell count.

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
