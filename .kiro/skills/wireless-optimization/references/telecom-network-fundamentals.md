# Telecom Network Fundamentals

Reference for the telecom-engineer agent. Covers cellular architecture, 3GPP interfaces,
protocol stacks, channel mapping, key procedures, and frequency bands for GSM/LTE/5G NR.

## Online References

## Cellular Architecture — Cell Hierarchy

| Cell Type | Radius     | Power (dBm) | Use Case                        |
| --------- | ---------- | ----------- | ------------------------------- |
| Macro     | 1–30 km    | 43–46       | Wide-area rural/urban coverage  |
| Micro     | 250 m–2 km | 30–38       | Urban hotspots, street-level    |
| Pico      | 50–250 m   | 23–30       | Indoor/outdoor capacity offload |
| Femto     | 10–50 m    | < 23        | Residential, enterprise indoor  |

### Frequency Reuse

- **Reuse Factor (N):** Number of cells in a cluster before frequencies repeat.
  - GSM classic: N=7 (or N=4 with fractional loading).
  - LTE/5G NR: N=1 (reuse 1) with ICIC/eICIC for interference management.
- **Sectorization:** Typically 3 sectors per site (120° each). Effective reuse = N ×
  sectors.
  - Sector antenna gain: 15–18 dBi typical for 65° beamwidth.

## 3GPP Interfaces — 4G/5G Mapping

| Function                | 4G (EPC/E-UTRAN) | 5G (5GC/NG-RAN) | Protocol           |
| ----------------------- | ---------------- | --------------- | ------------------ |
| UE ↔ RAN (air)          | Uu               | Uu (NR)         | RRC/NAS over radio |
| RAN ↔ Core (control)    | S1-MME           | N2 (gNB↔AMF)    | S1AP / NGAP        |
| RAN ↔ Core (user)       | S1-U             | N3 (gNB↔UPF)    | GTP-U              |
| RAN ↔ RAN               | X2 (eNB↔eNB)     | Xn (gNB↔gNB)    | X2AP / XnAP        |
| UE ↔ Core (NAS)         | NAS over S1-MME  | N1 (UE↔AMF)     | NAS-5G             |
| Core internal (session) | S5/S8 (SGW↔PGW)  | N4 (SMF↔UPF)    | GTP-C / PFCP       |

### Key Network Elements

```
4G:  UE → eNB → S-GW → P-GW → Internet
5G:  UE → gNB → UPF → DN
           ↕ N2        ↕ N4
          AMF ←→ SMF
```

- **AMF** (Access and Mobility Management Function): replaces MME control-plane.
- **SMF** (Session Management Function): replaces MME/SGW session signaling.
- **UPF** (User Plane Function): replaces SGW-U + PGW-U.

## Radio Protocol Stack

```
┌─────────────────────────────────────┐
│            NAS (Non-Access Stratum) │  ← UE ↔ AMF/MME (N1/S1-MME)
├─────────────────────────────────────┤
│            RRC (Radio Resource Ctrl)│  ← Connection setup, measurement config, HO
├─────────────────────────────────────┤
│            PDCP (Packet Data Conv.) │  ← Ciphering, integrity, header compression (ROHC)
├─────────────────────────────────────┤
│            RLC (Radio Link Control) │  ← Segmentation, ARQ (AM/UM/TM modes)
├─────────────────────────────────────┤
│            MAC (Medium Access Ctrl) │  ← Scheduling, HARQ, multiplexing, BSR, PHR
├─────────────────────────────────────┤
│            PHY (Physical Layer)     │  ← Modulation (QPSK/16QAM/64QAM/256QAM), coding
└─────────────────────────────────────┘
```

5G NR adds **SDAP** (Service Data Adaptation Protocol) above PDCP for QoS flow → DRB
mapping.

## Channel Mapping

### Downlink

| Logical Channel    | Transport Channel | Physical Channel | Purpose                 |
| ------------------ | ----------------- | ---------------- | ----------------------- |
| BCCH               | BCH               | PBCH             | MIB broadcast           |
| BCCH               | DL-SCH            | PDSCH            | SIB broadcast           |
| PCCH               | PCH               | PDSCH            | Paging                  |
| CCCH / DCCH / DTCH | DL-SCH            | PDSCH            | User/control data       |
| —                  | —                 | PDCCH            | DCI (scheduling grants) |
| —                  | —                 | DMRS/CSI-RS/SSB  | Reference signals       |

### Uplink

| Logical Channel    | Transport Channel | Physical Channel | Purpose                 |
| ------------------ | ----------------- | ---------------- | ----------------------- |
| CCCH / DCCH / DTCH | UL-SCH            | PUSCH            | User/control data       |
| —                  | RACH              | PRACH            | Random access preamble  |
| —                  | —                 | PUCCH            | UCI (HARQ-ACK, SR, CSI) |
| —                  | —                 | SRS              | UL channel sounding     |

## Key Procedures

The four procedures below occur in this order during typical UE lifecycle: attach,
handover, paging, and bearer setup.

### Attach / Registration

```
UE → PRACH (preamble) → eNB/gNB
UE ← RAR (Random Access Response) on PDSCH
UE → RRC Setup Request (CCCH on PUSCH)
UE ← RRC Setup (SRB1 established)
UE → RRC Setup Complete + NAS Attach/Registration Request
eNB/gNB → S1AP/NGAP: Initial UE Message → MME/AMF
    MME/AMF: Authentication (AKA), Security Mode Command
    MME/AMF → SGW/SMF+UPF: Create Session / PDU Session Establishment
UE ← NAS Attach Accept + RRC Reconfiguration (DRB setup)
UE → RRC Reconfiguration Complete
```

### Handover (X2/Xn-based)

```
Source eNB/gNB: Measurement Report from UE (event A3: neighbor > serving + offset)
Source → Target: Handover Request (X2AP/XnAP)
Target → Source: Handover Request Acknowledge (with RRC Reconfiguration)
Source → UE: RRC Reconfiguration (HO command)
UE → Target: RACH + RRC Reconfiguration Complete
Target → Source: UE Context Release
Target → MME/AMF: Path Switch Request
MME/AMF → Target: Path Switch Ack (S1/N2 path updated)
```

### Paging

```
MME/AMF → eNBs/gNBs in Tracking Area: Paging message (S-TMSI/5G-S-TMSI)
eNB/gNB → PDCCH: P-RNTI in paging occasion (DRX cycle based)
eNB/gNB → PDSCH: Paging message
UE wakes at paging occasion, decodes PDCCH, reads PDSCH
UE → Service Request / RRC Resume
```

### Bearer / PDU Session Setup

- **4G:** Default EPS Bearer (QCI 9) at attach; Dedicated Bearer for VoLTE (QCI 1, GBR).
- **5G:** PDU Session with QoS Flows. Each flow has 5QI (maps to QCI). DRB ↔ QoS Flow
  via SDAP.

## Common Frequency Bands

### FDD Bands (LTE / 5G NR)

| Band      | Frequency (DL) | Bandwidth | Typical Use              |
| --------- | -------------- | --------- | ------------------------ |
| B1 / n1   | 2110–2170 MHz  | 2×60 MHz  | Urban capacity           |
| B3 / n3   | 1805–1880 MHz  | 2×75 MHz  | Urban/suburban primary   |
| B7 / n7   | 2620–2690 MHz  | 2×70 MHz  | Capacity layer           |
| B8 / n8   | 925–960 MHz    | 2×35 MHz  | Rural coverage (900 MHz) |
| B20 / n20 | 791–821 MHz    | 2×30 MHz  | Coverage layer (800 MHz) |
| B28 / n28 | 758–803 MHz    | 2×45 MHz  | Coverage (700 MHz, APT)  |

### TDD Bands (5G NR)

| Band | Frequency      | Max BW  | Typical Use            |
| ---- | -------------- | ------- | ---------------------- |
| n41  | 2496–2690 MHz  | 100 MHz | Mid-band TDD capacity  |
| n77  | 3300–4200 MHz  | 100 MHz | C-band (global 5G)     |
| n78  | 3300–3800 MHz  | 100 MHz | C-band (Europe/Asia)   |
| n258 | 24.25–27.5 GHz | 400 MHz | mmWave, ultra-capacity |
| n260 | 37–40 GHz      | 400 MHz | mmWave                 |

### NR Numerologies

| μ   | SCS (kHz) | Slot Duration (ms) | Typical Band    |
| --- | --------- | ------------------ | --------------- |
| 0   | 15        | 1.0                | Sub-1 GHz (FDD) |
| 1   | 30        | 0.5                | Sub-6 GHz (TDD) |
| 2   | 60        | 0.25               | Sub-6 / mmWave  |
| 3   | 120       | 0.125              | mmWave (FR2)    |

## Quick Dimensioning Reference

- **PRB count by BW (LTE, SCS=15kHz):** 5 MHz→25, 10 MHz→50, 15 MHz→75, 20 MHz→100.
- **PRB count by BW (NR, SCS=30kHz):** 20 MHz→51, 40 MHz→106, 60 MHz→162, 100 MHz→273.
- **Max DL throughput (LTE):** ~150 Mbps (Cat 4, 20 MHz, 2×2 MIMO, 64QAM).
- **Max DL throughput (NR):** ~4.2 Gbps (100 MHz, 4×4 MIMO, 256QAM, FR1).
- **Link budget margin:** 8–10 dB log-normal shadow fading margin (σ=8 dB, 90%
  coverage).
- **MAPL (Maximum Allowable Path Loss):** TX EIRP − Rx Sensitivity − Margins.
