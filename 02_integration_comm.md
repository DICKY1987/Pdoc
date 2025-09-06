---
doc_id: econ_rev2
section: 02_integration_comm
---

# 2. Integration & Communication Layer

## 2.

### 2.y Communication Bridge Contracts (Interface-Level)

**Supported Transports:**
- **CSV (primary)** — atomic write + checksum_sha256; pull/poll semantics.
- **Socket (optional via PCL)** — push semantics with heartbeat/health.
- **Named Pipes (optional/future)** — MAY be enabled without changing decision schema.

**Decision CSV (contract reminder):**
- Required columns: `file_seq`, `ts_utc`, `symbol`, `side`, `size`, `price` (optional), `sl`, `tp`, `ttl`, `checksum_sha256`.
- Atomic write with temp‑rename; idempotency enforced by `file_seq` + hash.
- Health: adapter mode/state transitions recorded in `health_metrics.csv`.


## 2.x High-Level Architecture & Data Flow (Conceptual)

**Primary Flow:**  
Calendar Intake → Normalization → Matrix Resolution → Decision Layer → PCL Transport → Execution → Outcome Ingest → Re‑Entry Evaluation → Decision Layer

**Data Contracts:**  
- **Calendar/Matrix**: normalized event keys (CAL8), quality scores, debounce/min-gap rules.  
- **Decisions**: atomic CSV with `file_seq`, SHA-256, and idempotent write semantics.  
- **Health**: `health_metrics.csv` and `performance_metrics` tables for SLO tracking.

**Resilience:**  
CSV is **primary transport**; **socket** is optional via the Python Communication Layer (PCL) with automatic failover and stateful health reporting. Named pipes may be added as an optional future transport without changing decision contracts.
1 Inter‑Process Contracts
- **Transport**: CSV file drops on shared path; optional TCP/IPC later.
- **Atomicity**: Writers output `*.tmp`, include `file_seq`, `created_at_utc`, `checksum_sha256`, then rename to final path (§2.3).
- **Consumption Rule**: Readers process only strictly increasing `file_seq` with valid checksum_sha256.

## 2.2 CSV Artifacts
#### 2.2.4 `health_metrics.csv` (NEW)
Columns:
- `timestamp` (UTC ISO8601)
- `database_connected` (0/1)
- `ea_bridge_connected` (0/1)
- `last_heartbeat` (UTC ISO8601)
- `error_count` (int)
- `warning_count` (int)
- `cpu_usage` (float, %)
- `memory_usage` (float, MB)
- `win_rate` (float, %)
- `max_drawdown` (float, %)

Notes:
- Produced by the Python service, sourced from `system_status` and `
#### Coverage Alert Thresholds
- *Warn:* fallback_rate ≥ 5% for 5 consecutive minutes **or** conflict_rate ≥ 2% over last 100 decisions.
- *Page:* fallback_rate ≥ 15% for 3 consecutive minutes **or** p99_latency_ms > 2000 for 5 minutes.
- *Info:* socket_uptime_pct or csv_uptime_pct drops below 99.5% rolling 1h.

performance_metrics` tables.
- Atomic write: temp → checksum_sha256 → rename.


- `active_calendar_signals.csv`: `symbol, cal8, cal5, signal_type, proximity, event_time_utc, state, priority_weight, file_seq, created_at_utc, checksum_sha256`
- `reentry_decisions.csv`: `hybrid_id, parameter_set_id, lots, sl_points, tp_points, entry_offset_points, comment, file_seq, created_at_utc, checksum_sha256`
- `trade_results.csv`: `file_seq, ts_utc, account_id, symbol, ticket, direction, lots, entry_price, close_price, profit_ccy, pips, open_time_utc, close_time_utc, sl_price, tp_price, magic_number, close_reason, signal_source, checksum_sha256`
- `health_metrics.csv`: rolling KPIs (§14.2)

## 2.3 Atomic Write Procedure
1) Serialize rows → temp file with `file_seq`.
2) Compute `checksum_sha256` field; fsync.
3) Rename `*.tmp` → final; notify via file watcher (optional).

## 2.4 Time & Timezone
### 2.4.1 Time & Timezone — Broker Skew Rules (NEW)
**Purpose:** Ensure time alignment across UTC normalization, broker clock, and calendar triggers.

**Inputs**
- `utc_now` (system UTC time)
- `broker_time` (EA-reported time via bridge)
- `last_offset_update_ts` (UTC)
- `max_skew_seconds` = **120**
- `max_offset_age_seconds` = **900** (15 minutes)

**Rules**
1. **Offset Calculation:** `offset = broker_time - utc_now` (signed seconds).
2. **Skew Check:** If `abs(offset) > max_skew_seconds` → **DEGRADED**.
3. **Staleness Check:** If `utc_now - last_offset_update_ts > max_offset_age_seconds` → **DEGRADED**.
4. **Degraded Mode Behavior:**
   - Set `ea_bridge_connected=0` in `health_metrics.csv`.
   - **Do not** emit `reentry_decisions.csv`.
   - Re-attempt broker sync every **60s**; return to **NORMAL** only after two consecutive healthy checks.
5. **Audit:** Record transitions NORMAL↔DEGRADED in `error_log` with the measured skew.


#### 2.4 (UPDATED) Skew Handling
- **Max broker skew:** ±120 seconds vs UTC heartbeat.
- **Stale offset policy:** if offset older than **15 minutes**, mark `ea_bridge_connected=0`, pause emissions, raise `warning_count`.
- **Degraded mode:** if skew exceeds max or offset stale, do not emit new `reentry_decisions.csv`; retry sync every 60s.


- All times UTC in payloads. MT4 converts using live `broker_offset_minutes` provided by control file `broker_clock.csv` (updated hourly).

## 2.5 System‑Wide Relationship Matrix (Consolidated)

| Source Component | Target Component | Data Flow Type | Trigger | Source Doc |
|---|---|---|---|---|
| Calendar Normalizer | Calendar Events DB | SQL upsert (`calendar_events`) | New/revised event | §4.4, §7.2 |
| Calendar Events DB | Active Signal Builder | Event rows → Active set | Scheduler tick / proximity change | §4.5–§4.6 |
| Active Signal Builder | Active Calendar Signals CSV | CSV (`active_calendar_signals.csv`) | State/proximity change; revision | §2.2–§2.3, §4.3 |
| EA Trade Close Detector | Trade Results CSV | Append ACK row | Order close | §17.2, §9.201 |
| Trade Results CSV | Outcome/Duration Classifier | ETL ingest → O/D | New trade result row | §5.3–§5.4, §9.210 |
| Active Calendar Signals CSV | Signal Composer (Matrix) | CSV rows → CompositeSignal | On emission / tick | §3.6, §9.211 |
| Re‑Entry Ledger | Generation Selector | Ledger state (`O/R1/R2`) | Decision cycle | §6.5, §5.6 |
| HybridID Builder | Parameter Resolver | ID parts → lookup key | Post classification/composition | §3.4, §5.8 |
| Parameter Repository (central) | Parameter Resolver | ParameterSet JSON | On lookup | §7.3 |
| PairEffect Table | Overlay Engine | Buffers/cooldown multipliers | Pre‑decision overlay | §7.4, §6.4 |
| BrokerConstraints Repository | Overlay Engine | Lot/min‑stop/freeze/rounding | Pre‑decision overlay | §7.7, §6.4 |
| Risk Controllers (Exposure/DD/Streak) | Overlay Engine | Scalars / blocks | Risk state change | §8.1–§8.3 |
| Decision Emitter | Execution Engine (EA) | `reentry_decisions.csv` | New decision (`file_seq`↑) | §2.2–§2.3, §17.1 |
| Execution Engine (EA) | Trade Results CSV | `trade_results.csv` append | After open/modify/close | §17.2, §9.240 |
| Metrics Emitters | Metrics/Alerts | KPI rows, alert triggers | On events / thresholds | §14.1–§14.2 |
| Configuration/Change Mgmt | All Components | Hot‑reload configs / mappings | Publish/approve | §15.1 |
| Lifecycle/Restart Manager | All Components | State hydration | Startup/restart | §9.300, §4.9 |

## 2.6 Python Communication Layer (PCL)
**Purpose.** Provide a unified, pluggable transport between Python services (§4–§8) and the MT4 Execution Engine (§16.4), with automatic failover and health reporting.

**Design.**
- **Adapters:** `CSVAdapter` (file‑based) and `SocketAdapter` (DLL/port 5555/9999). Both expose the same interface:
  - `emit_decision(decision_row)`, `emit_metrics(metric_rows)`, `append_trade_result(row)`
  - `watch_signals(callback)`, `watch_health(callback)`
- **Router:** `CommRouter` selects the active adapter with policy: Socket preferred when healthy → otherwise CSV. Policy is stateful, uses heartbeats & error counters (§2.8).
- **Integrity Guard:** Validates `file_seq` monotonicity, SHA‑256 checksum_sha256 (CSV), and JSON schema (socket) before delivery.

## 2.7 Transport Adapters — Contracts
**CSVAdapter (Production Default).**
- **Paths:** `<MT4_DATA_FOLDER>/eafix/` by default; alias to spec filenames: 
  - `trading_signals.csv` ⇄ **`reentry_decisions.csv`**
  - `trade_responses.csv` ⇄ **`trade_results.csv`**
  - `system_status.csv` ⇄ **`health_metrics.csv`**
- **Polling/Detection:** EA detects updates on ≤5s timer (§17.1, SLA table). Writer uses atomic temp‑rename (§2.3). 
- **Semantics:** Writer appends rows with `file_seq`, `ts_utc`, `checksum_sha256`. Reader validates then processes.

**SocketAdapter (Optional / Low‑Latency).**
- **Server:** MT4 starts DLL socket server; newline‑terminated UTF‑8 JSON messages (≤4096 bytes). Single Python client allowed.
- **Client:** Python `MT4Bridge` maintains connection, send/receive threads, and message handlers (signals, status, trade updates).
- **Health:** Heartbeats every 30s from EA; adapter demotes on missed beacons or send/recv errors.

## 2.8 Failover & Health Policy
- **Primary:** Socket when `status==CONNECTED` and last 3 cycles error‑free; otherwise CSV.
- **Demotion Triggers:** socket connect/refused, heartbeat missed, JSON parse error, queue overflow.
- **Promotion Triggers:** stable socket for ≥60s with heartbeats.
- **Metrics:** Emit adapter state, last transition reason, decision latency deltas (§14.1, §9.401).

## 2.9 Configuration Flags (EA & Python)
- EA: `EnableCSVSignals=true/false`, `EnableDLLSignals=true/false`, `ListenPort=5555`, `CommPollSeconds=5` (min 1s), `DebugComm=false` (§17.1–§17.4).
- Python: `COMM_MODE=auto|csv|socket`, `CSV_DIR=<path>`, `SOCKET_HOST=localhost`, `SOCKET_PORT=5555`, `CHECKSUM=sha256`, `SEQ_ENFORCE=true`.

## 2.10 Troubleshooting Hooks
- Ship `simple_socket_test.py` and CSV integrity checker. Health panel surfaces: seq gaps, checksum_sha256 failures, socket status, last heartbeat (§14.3).

---

