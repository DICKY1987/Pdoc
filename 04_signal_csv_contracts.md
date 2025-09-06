---
doc_id: econ_rev2
section: 04_signal_csv_contracts
---

# 5. Multi‑Dimensional Matrix Subsystem

## 5.1 Dimensions
- **SignalType** (§3.5), **Outcome**, **Duration**, **Proximity**, **Generation**.

## 5.2 SignalType Governance
- Registry defines for each signal: `durationless`, `proximity_sensitive`, `priority_weight`, conflict rules.

## 5.3 Outcome Buckets (Deterministic)
- Compute realized **RR** (PnL/initial risk). Map:
  - O1: ≤ −1.0 RR (Full SL or worse)
  - O2: −1.0 < RR ≤ −0.25
  - O3: −0.25 < RR ≤ +0.25 (BE zone)
  - O4: +0.25 < RR ≤ +1.0
  - O5: +1.0 < RR ≤ +2.0 (TP)
  - O6: > +2.0 (Beyond TP)

## 5.4 Duration Categories
- `FL, QK, MD, LG, EX` by elapsed time thresholds; allow `NA` for durationless signals.

## 5.5 Proximity Categories
- `IM, SH, LG, EX, CD` from §4.5; pulled live from calendar engine.

## 5.6 Generation Limits
- `O` (original), `R1`, `R2`; enforced by **Re‑Entry Ledger** (§6.5).

## 5.7 Matrix Population Strategy
- **Lazy materialization**: create mapping row on first encounter of a Hybrid ID, seeded from family template.
- Nightly backfill for popular combos.

## 5.8 Parameter Resolution (with Fallback Tiers)
Order of attempts:
1) Exact Hybrid ID.
2) Drop `DUR` (if durationless or flagged optional).
3) Drop `PROX`.
4) Replace `SIG` with `ALL_INDICATORS`.
5) **Safe Default** per family (conservative template).
- Emit coverage alert on any fallback tier > 0.

## 5.9 Audit & Versioning
- `mapping_audit` append‑only: old/new ParameterSetID, trigger, actor, stats snapshot, risk overlay diffs.

## 5.10 Component Relationship Matrix

| Source Component | Target Component | Data Flow Type | Trigger | Source Doc |
|---|---|---|---|---|
| Trade Close Ingest (EA → PY) | Outcome/Duration Classifier | TradeResult → O/D classification | Trade close ACK | §9.201, §5.3–§5.4 |
| Active Calendar Signals CSV | Signal Composer | CSV rows → CompositeSignal | On emission / tick | §3.6, §9.211 |
| Re‑Entry Ledger | Generation Selector | Ledger state (`O/R1/R2`) | Decision cycle | §6.5, §5.6 |
| HybridID Builder | Parameter Resolver | ID parts → lookup key | Post classification/composition | §3.4, §5.8 |
| Parameter Repository | Parameter Resolver | ParameterSet JSON | On lookup | §7.3, §5.8 |
| PairEffect Table | Overlay Engine | PairEffect row (buffers, cooldown) | Pre‑decision overlay | §7.4, §6.4 |
| BrokerConstraints Repo | Overlay Engine | Constraint row (lot/min stop/freeze) | Pre‑decision overlay | §7.7, §6.4 |
| Risk Controls (DD/Streak/Exposure) | Overlay Engine | Risk scalars | Before emit | §8.1, §8.3 |
| Parameter Resolver/Overlay | Decision Emitter | Final params | After overlays | §2.2, §9.224 |
| Fallback Detector | Mapping Audit | Append change record | Fallback tier>0 or manual change | §5.8–§5.9, §14.2 |

---

