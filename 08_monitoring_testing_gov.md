---
doc_id: econ_rev2
section: 08_monitoring_testing_gov
---

# 9. End‑to‑End Operational Flows

**Actors:** `PY` (Python services), `EA` (MT4 Execution Engine), `DB` (SQLite stores), `BR` (CSV Bridge), `FS` (Filesystem)  
**Transports:** CSV‑only per §2.1–§2.3 (atomic write: tmp→fsync→rename, `file_seq`, `checksum_sha256`, UTC)  
**Identifiers:** `CAL8`/`CAL5` (§3.2–§3.3), `HybridID` (§3.4)  
**Dimensions:** Outcome (§5.3), Duration (§5.4), Proximity (§5.5), Generation (§5.6)  
**Risk/Constraints:** PairEffect (§7.4), BrokerConstraints (§7.7), Exposure Caps (§8.1), Circuit Breakers (§6.7)  
**MT4 Contracts:** §16.4 (Execution Engine), §17 (Read/Write/Error)

---

## 9.100 — Event Lifecycle Flow (Calendar → Active Signals)

#### Acceptance Criteria — Calendar Intake
- *Freshness:* new weekly pull available ≤ 24h after vendor publish.
- *Completeness:* ≥ 95% of expected rows for High/Medium events for G7; gaps flagged.
- *Quality Score:* ≥ 0.90 average after normalization (field coverage + type validity).
- *Idempotency:* re‑running import with identical source does not change DB row hashes.
- *Tolerance:* vendor field rename or same‑second reschedule does not break pipeline.

#### Acceptance Criteria — PCL Failover
- *Detection:* transport failure detected in ≤ 3s.
- *Switch:* adapter switches to alternate transport in ≤ 2s.
- *Recovery:* primary transport retried with exponential back‑off (≤ 60s max interval).
- *Audit:* state transitions recorded with reason codes in `health_metrics.csv`.


**Pre‑Normalization (Auto‑Download & Transform)**
- **9.100A (PY/FS)** **Discover** the latest vendor CSV in the configured downloads path using prioritized glob patterns; select newest by mtime.
- **9.100B (PY)** **Parse** with flexible column mapping; compute **quality score** per row and discard sub‑threshold entries; standardize country/impact.
- **9.100C (PY)** **Generate anticipation** events for eligible families using configured hours (default 1,2,4,8,12); compute trigger times and sort.
- **9.100D (PY/DB)** **UPSERT** into `calendar_events` with unique keys; update `revision_seq`/`blocked` as needed; commit.
- **9.100E (PY)** **Minimum‑gap/debounce** pass to suppress clustered duplicates; proceed to active‑set calculation.

- **9.101 (PY/FS)** Read normalized calendar feed; verify SHA‑256 against sidecar. If unchanged, **GOTO 9.110**. (IDs: §3.2–§3.3)
- **9.102 (PY/DB)** For each event, compute `CAL8` and keep `CAL5` alias; upsert into `calendar_events` (DB) within a transaction (§7.2).
- **9.103 (PY)** Create anticipation entries (`ANTICIPATION_8HR`, `ANTICIPATION_1HR`) with configured, event‑type proximity thresholds (§4.5) and set `state=SCHEDULED` (§4.6).
- **9.104 (PY)** Merge session signals (TOKYO/LONDON/NY opens, lunch, close) with holiday/DST rules (§4.7). Assign `priority_weight` (§3.6).
- **9.105 (PY/DB)** Commit all events with initial `state`/`proximity` and revision flags. Ensure restart hydration markers saved (§4.9).
- **9.106 (PY)** Build **active set** for `[now−X, now+Y]` using event‑type proximity; map `PROX ∈ {IM, SH, LG, EX}` or `CD` for cooldown (§4.5).
- **9.107 (PY/FS)** Emit `active_calendar_signals.csv` atomically (§2.2–§2.3) with `file_seq`, `checksum_sha256`, UTC timestamps (§2.4).
- **9.108 (PY)** Debounce duplicates by `(symbol, cal8, signal_type, state)`; suppress lower‑weight duplicates (§3.6).
- **9.109 (PY/DB)** Store last emitted `file_seq` watermark for restart hydration (§4.9).
- **9.110** **END** (await scheduler tick or revision event).

### Revisions & Reschedules
- **9.121 (PY/DB)** On upstream revision, increment CAL8 revision flag `F`; recompute `state/proximity`; mark prior emissions stale (§4.8).
- **9.122 (PY/FS)** Re‑emit `active_calendar_signals.csv` with next `file_seq`; increment `calendar_revisions_processed` (§14.1).

---

## 9.200 — Trade‑Close Decision Flow (Close → Decision → Execution)

- **9.201 (EA)** Detect trade **close**; capture open/close UTC, prices, initial SL/TP, lots, symbol (§17.2). Append ACK to `trade_results.csv` (atomic, append, UTC) (§2.2, §17.2).
- **9.210 (PY/DB)** Classify **Outcome** O1..O6 by realized **RR** (§5.3). Compute **Duration** (`FL/QK/MD/LG/EX`) or `NA` for durationless families (§5.4, §3.5).
- **9.211 (PY)** Query **active signals** for symbol; compute composite top signal via priority weights (§3.6) and blocklist conflicts. Extract `SIG`, `CAL8|00000000`, live `PROX` (§5.5).
- **9.212 (PY)** Determine **Generation** from the Re‑Entry Ledger (`O→R1→R2`); if limit exceeded, mark terminal and **GOTO 9.280** (§5.6, §6.5).
- **9.213 (PY)** Compose **HybridID** = `[CAL8|00000000]-[GEN]-[SIG]-[DUR]-[OUT]-[PROX]-[SYMBOL]` (§3.4).
- **9.220 (PY/DB)** Resolve **ParameterSet** (tiers): exact → drop `DUR` → drop `PROX` → `SIG→ALL_INDICATORS` → Safe Default (§5.8; params in §7.3). Record `fallback_tier` and raise coverage alert if `tier>0` (§14.2).
- **9.222 (PY)** Apply overlays: PairEffect (§7.4), drawdown/streak dampeners, session caps, **portfolio exposure caps** (§8.1).
- **9.223 (PY)** Apply **BrokerConstraints** rounding/min‑stops/freeze levels (§7.7) to yield final `lots, sl_points, tp_points, entry_offset_points`.
- **9.224 (PY/FS)** Emit **decision** to `reentry_decisions.csv` atomically with `file_seq`, `checksum_sha256`, UTC and `parameter_set_id@version` (§2.2–§2.3).
- **9.230 (EA/FS)** Ingest decision per §17.1: verify monotonic `file_seq` + checksum_sha256; ignore stale/non‑matching symbols.
- **9.231 (EA)** Pre‑flight: re‑apply BrokerConstraints (§7.7) + PairEffect (§7.4); apply **circuit breakers** (§6.7) and **exposure caps** (§8.1). If blocked, log non‑execution and **GOTO 9.260**.
- **9.232 (EA)** Execute order(s) per decision; use SafeOrder wrappers and slippage guards (§16.4.4). Respect MT4 limits (MQL4‑only).
- **9.240 (EA/FS)** Append final execution to `trade_results.csv` (UTC, seq, checksum_sha256) with realized slippage and broker data (§17.2).
- **9.250 (PY/DB)** Persist to per‑symbol `trade_results` with **frozen** params and HybridID (§7.2, §7.3).
- **9.260 (PY)** Update Re‑Entry Ledger; if next gen ≤ R2, loop to **9.210**; else **GOTO 9.280** (§6.5).
- **9.280 (PY)** Mark chain **CLOSED**; emit metrics and end flow (§14.1).

---

## 9.300 — Restart Hydration Flow (Cold/Warm Start)

- **9.301 (PY/DB)** Read `calendar_events` where `state ∈ {ANT_8H, ANT_1H, ACTIVE, COOLDOWN}`; rebuild active signals; recompute `PROX` from `now_utc` (§4.9).
- **9.302 (PY/DB)** Restore **Re‑Entry Ledger** for open chains (§6.5).
- **9.303 (PY/FS)** Read last `file_seq` for `active_calendar_signals.csv` and `reentry_decisions.csv`; set monotonic baselines (§2.3).
- **9.304 (PY/FS)** Validate CSV integrity (seq gaps, checksum_sha256). If gaps, re‑emit latest state with next `file_seq` and raise alert (§14.2).
- **9.305 (PY/FS)** Emit fresh `active_calendar_signals.csv` (atomic) and start timers/jobs (§4.9).

---

## 9.400 — Real‑Time Updates & Conflict Arbitration

- **9.401 (PY)** On EA heartbeat, compute decision latency (decision write → EA ACK); append to metrics (§14.1).
- **9.402 (PY)** On calendar revision, run **9.121→9.122**; recompute composite signals; if hard conflict with a running chain, pause next gen and flag for review (§3.6, §4.8).
- **9.403 (PY)** On modeled **spread spike** for current `SIG/PROX`, reduce size and widen stops; escalate if persistent (§8.2).

---

## 9.500 — Health, Metrics & Coverage

- **9.501 (PY/DB)** Update `metrics` table and `health_metrics.csv` with coverage %, fallback rate, decision latency p95/p99, slippage delta, spread vs model, conflict rate, calendar revisions processed, circuit‑breaker triggers (§14.1, §14.3).
- **9.502 (PY)** Raise alerts on thresholds: excessive fallbacks, checksum_sha256 failure, broker drift, heartbeat timeout, proximity rebuild failure (§14.2).

---

## 9.600 — Error Handling & Recovery (Scope §9)

- **9.601 (PY)** On decision write contention, backoff (250–1000ms, jitter, max 10). If exhausted, queue for retry and alert (§10).
- **9.602 (EA)** On order send/modify fatal error, follow retry taxonomy then emit `REJECT_TRADE`; if repeated, trip circuit breaker and annotate metrics (§6.7, §16.4.4).
- **9.603 (PY)** On mapping miss (fallback tier>0), log coverage violation and enqueue mapping task (§5.8, §14.2).

---

## 9.700 — Test Cues (Atomic, §9 Focus)

- **9.701** Inject calendar revision mid‑chain → expect recomputed `PROX` and no seq regression in emissions (§4.8, §2.3).
- **9.702** Simulate broker min stop increase → overlays clamp; EA pre‑flight rejects if violated (§7.7, §17.3).
- **9.703** Force fallback tier 3 → expect coverage alert + Safe Default usage (§5.8, §14.2).
- **9.704** Kill EA then restart → expect hydration 9.300 and heartbeat recovery (§4.9, §17).
- **9.705** Widen spread above model → reduced size/wider stops and metric flag (§8.2, §14.1).

---

## Appendix — Owner & SLA Matrix (Selected §9 Steps)

| Step — Action | Owner / SLA |
|---|---|
| 9.101 — Verify calendar hash | PY (FS) • 300ms |
| 9.105 — Write calendar_events (txn) | PY (DB) • 100ms |
| 9.107 — Emit active_calendar_signals.csv | PY (FS) • 80ms |
| 9.121 — Apply revision & recompute | PY • 150ms |
| 9.201 — Append trade_results.csv | EA (FS) • 120ms |
| 9.210 — Classify outcome/duration | PY • 25ms |
| 9.220 — Parameter resolution (tiered) | PY (DB) • 40ms |
| 9.224 — Emit decision (atomic) | PY (FS) • 60ms |
| 9.230 — Ingest decision | EA • ≤5s detection |
| 9.232 — Execute order(s) | EA • broker latency ≤800ms |
| 9.250 — Persist trade_result to DB | PY (DB) • 50ms |
| 9.303 — Inspect last file_seq | PY (FS) • 40ms |
| 9.304 — CSV integrity check | PY • 60ms |
| 9.401 — Compute latency from heartbeat | PY • 20ms |
| 9.501 — Metrics update | PY (DB) • 30ms |
| 9.602 — Order send retry then reject | EA • per policy |
| 9.704 — Restart hydration success | PY • ≤2s |

# 10. Error Handling & Resilience

## 10.1 CSV Race Conditions
- Avoided via atomic writes, sequences, checksums.

## 10.2 Time Drift & DST
- Broker offset monitored; all core logic uses UTC.

## 10.3 Data Quality Guards
- Quarantine invalid ingest; dual‑source reconcile if available.

---

# 11. Performance Targets (SLOs)

## 11.1 Latency
- Decision time from trade close → CSV emit ≤ 150 ms (p95).

## 11.2 Throughput
- Support ≥ 50 concurrent symbols without missed emissions.

## 11.3 Availability
- 99.5% decision service availability during trading hours.

---

# 12. Security & Permissions

## 12.

### 12.y Performance Benchmarks (Targets)

- **Calendar Import**: weekly pull & normalize ≤ 5 minutes (p95).
- **Decision Latency**: end‑to‑end emit ≤ 500 ms (p95), ≤ 1000 ms (p99).
- **DB/Storage Ops**: critical queries ≤ 100 ms (p95).
- **Transport Uptime**: CSV and Socket ≥ 99.5% rolling 1h.
- **Failover Recovery**: switch to alternate transport ≤ 2 seconds.

Benchmarks are enforced via `performance_metrics` and alert thresholds defined in this spec.


## 12.x Data Model & Analytics Entities (Logical, Non-SQL)

- **`trades`** — executed orders with link to originating decision and re‑entry chain id.
- **`reentry_chains`** — chain/group identifier with generation counters and status.
- **`reentry_performance`** — per-bucket aggregates (win rate, avg MAE/MFE, expectancy).
- **`calendar_events`** — normalized events with CAL8 key and vendor lineage.
- **`system_metrics`** — operational SLOs and adapter transitions (joins `health_metrics.csv`).

**Core KPIs:** decision latency (p95/p99), fallback rate, conflict rate, socket/csv uptime %, chain expectancy per profile, and drawdown recovery time.
1 File Access
- Least‑privilege on shared folders; read‑only for MT4 where applicable.

## 12.2 Integrity
- Checksums on all outbound CSVs; audit trail for mapping/param changes.

---

# 13. Testing & Validation

## 13.1 Backtest Fidelity
- Rebuild historical proximity/state using stored schedules with `revision_seq`.

## 13.2 Property‑Based Tests
- Invariants: `lot(R2) ≤ lot(O)` under same overlays; `fallback_tier` non‑increasing with mapping completeness.

## 13.3 Canary & A/B
- Enable new signals on subset of symbols with reduced sizes until sample thresholds.

---

# 14. Monitoring & Telemetry

## 14.1 Metrics (emitted to `metrics` & `health_metrics.csv`)
- Mapping coverage %, fallback rate, decision latency, slippage vs expected, spread vs model, conflict rate, calendar revisions processed, circuit‑breaker triggers.

## 14.2 Alerts
- Coverage violation, checksum_sha256 failure, broker drift > threshold, excessive fallbacks, proximity/state rebuild failures.

## 14.3 Metrics Panel (UI Contract)
- **Purpose:** Single screen for live operational health.
- **Data Source:** `metrics` table and `health_metrics.csv`.
- **Refresh Cadence:** 1s (configurable), rolling 15m/1h aggregates.
- **Core Tiles:** Mapping coverage %, fallback rate (tier>0), decision latency p95/p99, slippage delta (actual−expected), spread vs model, signal conflict rate, calendar revisions processed, circuit‑breaker triggers, CSV integrity (seq gaps / checksum_sha256 failures).
- **Drill‑downs:** Per‑symbol hybrid‑ID hit distribution; top unmapped combos; per‑family performance.
- **Alarms:** Visual badges linked to §14.2 thresholds.

# 15. Change Management & Governance

## 15.1 Parameter & Mapping Changes
- PR‑style workflow; automated diffs; time‑boxed rollbacks; append‑only `mapping_audit`.

## 15.2 Manual Overrides
- Require scope, TTL, reason; auto‑revert; tag resulting trades for separate PnL.

---

