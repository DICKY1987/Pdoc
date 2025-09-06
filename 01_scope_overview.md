---
doc_id: econ_rev2
section: 01_scope_overview
---

# 0. Document Control

## 0.1 Title
Integrated Economic Calendar → Matrix → Re‑Entry System — Technical Specification (Hierarchical Indexed)

## 0.2 Purpose & Scope
Defines the architecture, identifiers, data contracts, and operational processes for integrating (A) the Economic Calendar subsystem, (B) the Multi‑Dimensional Matrix subsystem, and (C) the Re‑Entry subsystem, including Python/database components and MT4 (MQL4) bridges. Incorporates the latest fixes replacing prior inferior logic.

## 0.3 Audience
System architects, quant devs, Python engineers, MQL4 engineers, ops/SRE, QA.

## 0.4 Assumptions
- Trading execution occurs via MT4/MQL4 (no MQL5 language features).
- Calendar ingestion and decisioning run in Python/SQLite; MT4 communicates via CSV/IPC.
- All timestamps handled in UTC; UI converts for display.

## 0.5 Definitions
- **CAL5**: Legacy 5‑digit calendar strategy ID (country+impact).
- **CAL8**: Extended 8‑symbol identifier (Region|Country|Impact|EventType|RevisionFlag|Version) per §3.2.
- **Hybrid ID**: Composite key joining calendar and matrix context per §3.4.
- **PairEffect**: Per‑symbol effect model (bias/spread/cooldown) per §7.4.

---

# 1. System Overview

## 1.

## 1.x System Philosophy (Non-Implementation)

This system fuses **proactive** (calendar-driven anticipation) and **reactive** (outcome-driven re-entry) trading into a single, auditable pipeline. Signals are generated from a **calendar→matrix** path before events and from a **post‑event outcome** path after releases. Both paths converge into the **Decision Layer**, which emits decisions under strict contracts (atomic files, checksums, and health metrics). All timing and storage are **UTC-normalized**, with explicit handling for DST on acquisition schedules. Configuration determines aggressiveness and risk posture but does not change interface contracts.
1 Objectives
1) Fuse calendar awareness with outcome‑ and time‑aware re‑entries.
2) Standardize identifiers and data flows for reproducible decisions.
3) Enforce risk, exposure, and broker constraints.

## 1.2 System Components
- A) Economic Calendar Subsystem (§4)
- B) Multi‑Dimensional Matrix Subsystem (§5)
- C) Re‑Entry Subsystem (§6)
- D) Data & Storage Layer (§7)
- E) Risk & Portfolio Controls (§8)
- F) Integration & Communication Layer (§2)
- G) Monitoring, Testing, Governance (§13–§15)

## 1.3 High‑Level Data Flow
1) Calendar ingest → event 
#### Revisions Handling — Acceptance Test
- Verify same‑second reschedules are detected and merged without duplicate keys.
- Validate tolerant mapping handles vendor field renames (e.g., `act`→`actual_value`).
- Ensure matrix resolution preserves prior decisions unless new data exceeds confidence threshold.

normalization → CAL8/CAL5.
2) Real‑time proximity & state machine updates.
3) On trade‑close: compute matrix context (Outcome/Duration/Generation).
4) Build Hybrid ID; choose ParameterSet (with fallbacks & risk overlays).
5) Emit decision to MT4 via atomic CSV; MT4 executes.

---

