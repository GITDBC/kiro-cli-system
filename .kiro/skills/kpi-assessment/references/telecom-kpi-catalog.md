# Telecom KPI Catalog — Mobile Network

Reference KPI catalog for the kpi-analyst agent. Each KPI includes name, formula, unit,
typical PM counters (3GPP/vendor-neutral naming), and operational notes.

## Accessibility KPIs

### RRC Setup Success Rate

- **Formula:** `RRC_Setup_SR = (RRC_Conn_Setup_Succ / RRC_Conn_Setup_Att) × 100`
- **Unit:** %
- **Target:** ≥ 99.5%
- **Counters:**
  - `RRC_Conn_Setup_Att` — Total RRC Connection Setup Attempts
  - `RRC_Conn_Setup_Succ` — Total RRC Connection Setup Successes
- **Notes:** Split by cause (MO-data, MO-signaling, MT-access, emergency). Failures
  indicate congestion (max RRC connected users), admission control rejection, or RACH
  issues. Exclude re-establishments from attempts if measuring initial access only.

### E-RAB Setup Success Rate (LTE)

- **Formula:** `ERAB_Setup_SR = (ERAB_Setup_Succ / ERAB_Setup_Att) × 100`
- **Unit:** %
- **Target:** ≥ 99.0%
- **Counters:**
  - `ERAB_Setup_Att` — E-RAB Setup Attempts (initial + additional)
  - `ERAB_Setup_Succ` — E-RAB Setup Successes
- **Notes:** Includes both initial context setup and additional bearer setup. Separate
  QCI-specific counters (QCI 1 for VoLTE, QCI 9 for default). Low SR on QCI 1 impacts
  VoLTE call setup.

### RAN Setup Success Rate (Combined)

- **Formula:**
  `RAN_Setup_SR = (RRC_Conn_Setup_Succ / RRC_Conn_Setup_Att) × (ERAB_Setup_Succ / ERAB_Setup_Att) × 100`
- **Unit:** %
- **Target:** ≥ 98.5%
- **Counters:** Combination of RRC and E-RAB counters above.
- **Notes:** End-to-end RAN accessibility. This is the product of RRC and E-RAB success
  rates. Some vendors call this "Service Setup Success Rate" or "Initial Context Setup
  SR".

### CSSR — Call Setup Success Rate (Voice)

- **Formula:** `CSSR = (VoLTE_Calls_Setup_Succ / VoLTE_Calls_Setup_Att) × 100`
- **Unit:** %
- **Target:** ≥ 98.0%
- **Counters:**
  - `VoLTE_Calls_Setup_Att` — SIP INVITE attempts reaching RAN
  - `VoLTE_Calls_Setup_Succ` — QCI 1 bearer established + SIP 200 OK
- **Notes:** Measured end-to-end including IMS. RAN portion is QCI 1 E-RAB setup.

## Retainability KPIs

### Call Drop Rate

- **Formula:** `CDR = (Abnormal_Releases / (Normal_Releases + Abnormal_Releases)) × 100`
- **Unit:** %
- **Target:** ≤ 1.0%
- **Counters:**
  - `Abnormal_Releases` — E-RAB releases not initiated by UE/CN normal cause
  - `Normal_Releases` — E-RAB releases with normal cause
- **Notes:** Exclude releases due to handover (these are mobility, not drops). Filter by
  release cause: radio link failure (RLF), S1 reset, transport failure, etc.

### E-RAB Drop Rate

- **Formula:**
  `ERAB_Drop_Rate = (ERAB_Abnormal_Release / (ERAB_Normal_Release + ERAB_Abnormal_Release)) × 100`
- **Unit:** %
- **Target:** ≤ 0.5% (QCI 9), ≤ 0.3% (QCI 1)
- **Counters:**
  - `ERAB_Abnormal_Release` — E-RAB released abnormally (eNB-initiated, no HO)
  - `ERAB_Normal_Release` — E-RAB released normally
- **Notes:** Per-QCI analysis critical. High QCI 1 drops = VoLTE voice drops. Common
  causes: UL sync loss, max HARQ retransmissions, RLF timer expiry (T310/T311).

### RAN Abnormal Release Rate

- **Formula:**
  `RAN_Abn_Release = (UE_Context_Abnormal_Release / UE_Context_Release_Total) × 100`
- **Unit:** %
- **Target:** ≤ 1.0%
- **Counters:**
  - `UE_Context_Abnormal_Release` — UE context released due to RLF, S1 failure
  - `UE_Context_Release_Total` — All UE context releases
- **Notes:** Broader than E-RAB drop — covers full UE context. Includes cases where all
  bearers drop simultaneously.

## Mobility KPIs

### Intra-Frequency Handover Success Rate

- **Formula:** `IntraFreq_HO_SR = (IntraFreq_HO_Succ / IntraFreq_HO_Att) × 100`
- **Unit:** %
- **Target:** ≥ 99.0%
- **Counters:**
  - `IntraFreq_HO_Att` — Intra-frequency HO attempts (X2 + S1)
  - `IntraFreq_HO_Succ` — Intra-frequency HO successes
- **Notes:** Most common HO type. Failures often due to late HO (UE already in RLF),
  missing neighbor relations, or target cell congestion.

### Inter-Frequency Handover Success Rate

- **Formula:** `InterFreq_HO_SR = (InterFreq_HO_Succ / InterFreq_HO_Att) × 100`
- **Unit:** %
- **Target:** ≥ 97.0%
- **Counters:**
  - `InterFreq_HO_Att` — Inter-frequency HO attempts
  - `InterFreq_HO_Succ` — Inter-frequency HO successes
- **Notes:** Requires measurement gaps. Lower SR than intra-freq is expected. Triggered
  by coverage (A2+A5 events) or load balancing (MLB).

### Inter-RAT Handover Success Rate

- **Formula:** `InterRAT_HO_SR = (InterRAT_HO_Succ / InterRAT_HO_Att) × 100`
- **Unit:** %
- **Target:** ≥ 95.0%
- **Counters:**
  - `InterRAT_HO_Att` — Inter-RAT HO attempts (LTE→3G, NR→LTE, etc.)
  - `InterRAT_HO_Succ` — Inter-RAT HO successes
- **Notes:** Typically LTE↔WCDMA or NR↔LTE fallback. Higher failure rate due to
  technology differences. CSFB and SRVCC counted separately.

### HO Preparation Success Rate

- **Formula:** `HO_Prep_SR = (HO_Prep_Succ / HO_Prep_Att) × 100`
- **Unit:** %
- **Counters:**
  - `HO_Prep_Att` — HO Request messages sent to target
  - `HO_Prep_Succ` — HO Request Acknowledge received from target
- **Notes:** Failure = target cell rejected HO (congestion, missing config, transport
  issue).

### HO Execution Success Rate

- **Formula:** `HO_Exec_SR = (HO_Exec_Succ / HO_Exec_Att) × 100`
- **Unit:** %
- **Counters:**
  - `HO_Exec_Att` — HO Command sent to UE (= HO_Prep_Succ)
  - `HO_Exec_Succ` — HO Complete received at target
- **Notes:** Failure = UE failed to access target cell (too late HO, RACH failure at
  target, radio conditions degraded during HO).

## Integrity KPIs

### DL User Throughput

- **Formula:** `DL_User_Tput = DL_Data_Volume_bits / DL_Active_Time_seconds`
- **Unit:** kbps or Mbps
- **Counters:**
  - `DL_Data_Volume` — Total DL PDCP SDU volume (bytes) for active UEs
  - `DL_Active_Time` — Time UE has data in DL buffer (seconds)
- **Notes:** Active time excludes idle/DRX periods. Per-UE average. Aggregate across
  cell = cell throughput. Vendor implementations vary — verify if PDCP or MAC layer
  volume.

### UL User Throughput

- **Formula:** `UL_User_Tput = UL_Data_Volume_bits / UL_Active_Time_seconds`
- **Unit:** kbps or Mbps
- **Counters:**
  - `UL_Data_Volume` — Total UL PDCP SDU volume (bytes)
  - `UL_Active_Time` — Time UE has data in UL buffer (seconds)
- **Notes:** Same methodology as DL. UL typically lower due to power-limited UE and
  asymmetric spectrum allocation.

### DL Cell Throughput

- **Formula:** `DL_Cell_Tput = Total_DL_Data_Volume_bits / Measurement_Period_seconds`
- **Unit:** Mbps
- **Notes:** Measures total cell capacity utilization. Not per-user. Useful for capacity
  planning.

### Latency (User Plane)

- **Formula:** `Latency = Avg(Packet_Arrival_Time - Packet_Sent_Time)`
- **Unit:** ms
- **Target:** ≤ 20 ms (LTE), ≤ 4 ms (5G NR eMBB), ≤ 1 ms (5G URLLC)
- **Notes:** Measured at PDCP layer or via probe. One-way delay. RTT = 2× one-way.
  Includes scheduling delay + TTI + HARQ retransmissions.

### DL BLER (Block Error Rate)

- **Formula:** `DL_BLER = (DL_CRC_NACK / (DL_CRC_ACK + DL_CRC_NACK)) × 100`
- **Unit:** %
- **Target:** Initial BLER target = 10% (OLLA target for throughput optimization)
- **Notes:** BLER after 1st transmission (before HARQ retx). Residual BLER (after all
  HARQ) should be < 1%. High initial BLER with low residual = normal AMC operation. High
  residual BLER = real problem.

## Availability KPIs

### Cell Availability

- **Formula:** `Cell_Avail = ((Total_Time - Cell_Downtime) / Total_Time) × 100`
- **Unit:** %
- **Target:** ≥ 99.9%
- **Counters:**
  - `Cell_Downtime` — Time cell is administratively locked or out of service
  - `Total_Time` — Measurement period duration
- **Notes:** Exclude planned maintenance windows if measuring unplanned unavailability.
  Per-cell metric. A 3-sector site with 1 cell down = 66.7% site availability.

### Site Availability

- **Formula:** `Site_Avail = ((Total_Time - Site_Downtime) / Total_Time) × 100`
- **Unit:** %
- **Target:** ≥ 99.5%
- **Notes:** Site is down when ALL cells at the site are unavailable. Partial outage (1
  of 3 sectors) = site still available but degraded. Track both metrics.

## Utilization KPIs

### PRB Utilization — Downlink

- **Formula:** `DL_PRB_Util = (DL_PRBs_Used / DL_PRBs_Available) × 100`
- **Unit:** %
- **Threshold:** > 70% = congested, consider capacity action
- **Counters:**
  - `DL_PRBs_Used` — Average DL PRBs used per TTI
  - `DL_PRBs_Available` — Total DL PRBs (e.g., 100 for 20 MHz LTE)
- **Notes:** Measured per TTI, reported as average over measurement period. Busy hour
  PRB utilization is the key capacity metric. Include control channel overhead in
  available PRBs calculation.

### PRB Utilization — Uplink

- **Formula:** `UL_PRB_Util = (UL_PRBs_Used / UL_PRBs_Available) × 100`
- **Unit:** %
- **Threshold:** > 60% = congested (UL more sensitive due to interference)
- **Notes:** UL congestion threshold lower than DL because UL interference rises faster
  with load (open-loop power control).

### RRC Connected Users

- **Formula:** `RRC_Connected_Users = Avg(RRC_Connected_UE_Count)` per measurement
  period
- **Unit:** count
- **Counters:**
  - `RRC_Connected_UE_Count` — Sampled count of UEs in RRC Connected state
- **Notes:** Peak vs average distinction critical. License limits often on max
  simultaneous RRC connected users. Typical sampling: every 1 second, reported as 15-min
  average and max.

### Active Users

- **Formula:** `Active_Users = Avg(UEs_with_data_in_buffer)` per measurement period
- **Unit:** count
- **Notes:** Subset of RRC Connected users that actually have data to send/receive. More
  relevant for throughput analysis than RRC Connected count.

## Quick Reference — KPI Summary Table

| Domain        | KPI                 | Formula (short)            | Unit  | Target            |
| ------------- | ------------------- | -------------------------- | ----- | ----------------- |
| Accessibility | RRC Setup SR        | Succ / Att × 100           | %     | ≥ 99.5%           |
| Accessibility | E-RAB Setup SR      | Succ / Att × 100           | %     | ≥ 99.0%           |
| Accessibility | RAN Setup SR        | RRC_SR × ERAB_SR           | %     | ≥ 98.5%           |
| Retainability | Call Drop Rate      | Abnormal / Total × 100     | %     | ≤ 1.0%            |
| Retainability | E-RAB Drop Rate     | Abnormal / Total × 100     | %     | ≤ 0.5%            |
| Mobility      | Intra-freq HO SR    | Succ / Att × 100           | %     | ≥ 99.0%           |
| Mobility      | Inter-freq HO SR    | Succ / Att × 100           | %     | ≥ 97.0%           |
| Mobility      | Inter-RAT HO SR     | Succ / Att × 100           | %     | ≥ 95.0%           |
| Integrity     | DL User Throughput  | Volume / Active_Time       | Mbps  | network-dependent |
| Integrity     | DL BLER             | NACK / (ACK+NACK) × 100    | %     | ~10% initial      |
| Availability  | Cell Availability   | (Total-Down) / Total × 100 | %     | ≥ 99.9%           |
| Utilization   | DL PRB Utilization  | Used / Available × 100     | %     | < 70%             |
| Utilization   | RRC Connected Users | Avg sampled count          | count | license-dependent |
