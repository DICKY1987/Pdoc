---
doc_id: econ_rev2
section: 06_reentry_subsystem
---

# 6. Re‑Entry Subsystem

## 6.
### 6.X Risk & Performance Mapping Defaults (NEW)
**Risk Score (0–100):**
- Base=50  
- WinRate Impact: `(WinRate - 50) * 0.6`  
- ProfitFactor Impact: `(ProfitFactor - 1) * 20`  
- Drawdown Penalty: `- DrawdownPercent * 2`  
- Recency Multiplier: last-7-days weight **×1.5**  
- Optional context adjustments (examples):  
  `consecutive_win_bonus = wins * 3`,  
  `volatility_penalty = vix_like_index * -0.5`,  
  `equity_close_penalty = (minutes_to_equity_close < 30 ? -10 : 0)`  
- Clamp to **[0,100]**.

**ParameterSet Bins (defaults):**
- `0–25` → **Conservative** (Set_1)
- `26–50` → **Moderate** (Set_2)
- `51–75` → **Aggressive** (Set_3)
- `76–100` → **Max** (Set_4)

1 Responsibilities
- On trade close, classify outcome/duration; compose Hybrid ID; select ParameterSet; overlay risk; emit decision.

## 6.2 Inputs
- Trade close data from MT4 (ticket group, prices, timestamps, initial SL/TP).
- Active signals (from calendar/session/vol engines).
- Risk overlays (drawdown, streaks, exposure caps).
- Broker constraints.

## 6.3 Outputs
- `reentry_decisions.csv` rows per §2.2.
- `trade_results` records with **frozen** parameter snapshots.

## 6.4 Parameter Overlay Policies
### 6.4 Parameter Overlay Precedence & Defaults (NEW)
**Goal:** Deterministic, layered parameter resolution.

**Precedence Order (top wins; stop on first concrete override):**
1. **PairEffect** (symbol-level overrides based on calendar influence)
2. **Broker Constraints** (min lot, step, stop distance, freeze levels)
3. **Risk Overlay** (from Risk Score & performance bins)
4. **Strategy/Matrix Defaults** (HybridID → ParameterSet)
5. **Global Fallbacks** (Tiered, see §6.8)

**Default Overlay Thresholds:**

| Overlay | Key | Default | Effect |
|---|---|---:|---|
| PairEffect | `exposure_cap_pct` | 3.0 | Max % balance exposed on symbol |
| Broker | `min_stop_points` | from EA | Enforce SL/TP ≥ broker min |
| Risk | `risk_floor_score` | 15 | Block entries below floor |
| Risk | `aggressive_cutover` | 75 | Switch to Set_3+ above |
| Strategy | `entry_offset_pts` | 0 | Add to pending orders |
| Global | `sl_tp_ratio_min` | 1.2 | Skip if TP/SL < 1.2 |

**Notes**
- When two overlays conflict at the same level, prefer the stricter risk stance (lower leverage, larger SL distance).
- All resolved parameters are **frozen on emit** (see schema §7.x below).


- Apply drawdown caps, streak dampeners, spread buffer, min stop buffers, portfolio exposure scaling, and broker rounding.

## 6.5 Re‑Entry Ledger (Generation Governance)
- Keyed by `PositionGroupID` (links partials/hedges/grids) to enforce max `R2` and prevent bypass.

## 6.6 Broker Constraints & Microstructure
- Enforce min lot step, min stop distance, freeze levels, max orders. Pre‑flight validation before OrderSend (in MQL4).
- Persist broker/platform constraints in a central repository per §7.7 and join them into the decision overlay at runtime.

## 6.7 Circuit Breakers
- Global kill‑switches: max daily loss, max consecutive losers, abnormal spread/slippage.

## 6.8 Component Relationship Matrix
### 6.8 Matrix Fallback Tiers (NEW)
**Problem:** Incomplete matches when looking up a ParameterSet by HybridID (e.g., missing duration or proximity bucket).

**Tiers**  
- **Tier-0 (Exact):** `HybridID = {CalendarID, ProximityBucket, DurationBucket, OutcomeClass}` → Use mapped `ParameterSetID`.
- **Tier-1 (Drop Duration):** `{CalendarID, ProximityBucket, OutcomeClass}` → If unique mapping exists, use it.
- **Tier-2 (Drop Proximity):** `{CalendarID, DurationBucket, OutcomeClass}` → If unique mapping exists, use it.
- **Tier-3 (Calendar Only):** `{CalendarID}` → Use Strategy Default Set.
- **Tier-4 (Global):** Use **Global Fallback Set** (safe conservative).

**Resolution Algorithm**
1. Attempt Tier-0; if **no** mapping or **multi-match**, escalate to Tier-1, then Tier-2, etc.
2. On each escalation, require a **unique** mapping; else continue.
3. Log the tier used into `mapping_audit` with `signal_id`, `resolved_tier`, and keys used.
4. If Tier-4 used, attach `comment="GLOBAL_FALLBACK"` to the emitted decision.

**Examples**
- **Case A:** Missing duration bucket → matched at **Tier-1** using `{CalendarID, Proximity, OutcomeClass}`.
- **Case B:** Sparse matrix for new event → falls back to **Tier-3** Strategy Default.
- **Case C:** Conflicting Tier-1 candidates → continue to **Tier-2**; if still ambiguous → Tier-3.



| Source Component | Target Component | Data Flow Type | Trigger | Source Doc |
|---|---|---|---|---|
| EA Trade Close Detector | Re‑Entry Subsystem | Trade close event | Order close | §9.201, §17.2 |
| Re‑Entry Subsystem | Re‑Entry Ledger | Generation update (`O→R1→R2`) | After decision result | §6.5, §9.260 |
| Re‑Entry Subsystem | Execution Engine (EA) | `reentry_decisions.csv` | Decision ready | §2.2–§2.3, §17.1 |
| Execution Engine (EA) | Re‑Entry Subsystem | `trade_results.csv` | After execute/close/modify | §17.2, §9.240 |
| Risk Calculator (DD/Streak/Exposure) | Re‑Entry Subsystem | Adjusted scalars/limits | Risk state change | §8.1–§8.3 |
| BrokerConstraints & PairEffect | Re‑Entry Subsystem | Overlay inputs | Pre‑decision | §7.7, §7.4 |
| Re‑Entry Subsystem | Metrics/Alerts | Fallback tier; coverage % | On decision | §14.1–§14.2 |

---

