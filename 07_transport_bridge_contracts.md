---
doc_id: huey_unified
section: 07_transport_bridge_contracts
---

## 6) Conditional Probability Engine (Concept)
**Purpose:** Compute empirical probabilities for (trigger → target within horizon) across parameter grids to enrich signals and drive alerts/policies.

### 6.1 Parameter axes (M/W/K/T)
- **M** (trigger move size, pips)
- **W** (trigger detection window, minutes)
- **K** (target move size, pips)
- **T** (target evaluation window, minutes)

### 6.2 Outputs (p, n)
- `p` (success probability), `n` (sample count), confidence tier derived from (`p`, `n`), plus optional conditioning on states (e.g., volatility regime).

### 6.3 Confidence tiers
- **VERY_HIGH:** `p ≥ 0.70` and `n ≥ 500`
- **HIGH:** `p ≥ 0.60` and `n ≥ 250`
- **MEDIUM:** `p ≥ 0.55` and `n ≥ 150`
- **LOW:** below thresholds

### 6.4 Policy hooks
- Minimum sample size (`n_min`) per market/timeframe; optional cooling-off after regime shifts; outlier trimming rules; stale-data TTL.

### 6.5 Transparency & export
- Show `p` and `n` with last-updated timestamp; enable export of probability tables; log methodology and data coverage.

> Note: Only the **concept** is defined here—no concrete UI layout, panel placement, or engine wiring is specified.

---

<!-- BEGIN:HUEY.007.001.001.REQ.live_tab_overview -->
