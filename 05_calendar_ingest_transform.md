---
doc_id: econ_rev2
section: 05_calendar_ingest_transform
---

# 4. Economic Calendar Subsystem

## 4.1 Responsibilities

#### Default Debounce / Min‑Gap by Event Family (Configurable)

| Event Family         | Debounce Window | Min Gap Before/After |
|----------------------|-----------------|----------------------|
| Rate Decision (RD)   | 15m             | 10m / 10m            |
| Non-Farm Payroll (NF)| 10m             | 5m / 5m              |
| CPI (CP)             | 10m             | 5m / 5m              |
| GDP (GD)             | 8m              | 4m / 4m              |
| Other (OT)           | 5m              | 3m / 3m              |

> These are safe defaults; tune per broker/liquidity and archive outcomes.

- Ingest calendar feed(s); normalize events; assign CAL8/CAL5.
- Compute real‑time proximity buckets; manage event lifecycle states.
- Emit active signals per symbol with priority weights.

## 4.2 Inputs
- Primary calendar feed (e.g., ForexFactory or similar, mapped to schema).
- Holiday/session calendars (per market) for session‑type signals.

## 4.3 Outputs
- `active_calendar_signals.csv` (per §2.2) continuously updated.
- DB table `calendar_events` with state & proximity history.

## 4.4 Event Normalization & ID Assignment
- Map feed fields → (Region, Country, Impact, EventType); set `V=1` initially.
- Initialize `F` (revision flag) = `0`; increment on official revisions/reschedules; propagate to CAL8.

## 4.5 Proximity Model (Event‑Type Aware)
- Buckets are **event‑type configurable**:
  - CPI: IM=0–20m, SH=21–90m, LG=91–300m, EX=>300m
  - NFP: IM=0–30m, SH=31–120m, LG=121–360m, EX=>360m
  - PMI: IM=0–10m, SH=11–45m, LG=46–180m, EX=>180m
- Cooldown `CD`: 30–60m post `ACTIVE` per event‑type rule.

## 4.6 Lifecycle States
`SCHEDULED → ANTICIPATION_8HR → ANTICIPATION_1HR → ACTIVE (±window) → COOLDOWN → EXPIRED`.
- State transitions recompute `proximity`; emit new rows when state changes.

## 4.7 Holiday & Session Logic
- Maintain session calendar with DST/holiday rules.
- Suppress session signals (`*_OPEN`, `*_CLOSE`) if market closed or emit with reduced weight.

## 4.8 Data Quality & Revisions
- Validate ingest (schema, uniqueness, monotonicity).
- On revision: bump `F`, re‑emit proximity/state; invalidate stale projections.

## 4.9 Performance & Resilience
- Restart hydration: rebuild active set from DB (states ∈ {ANT_8H, ANT_1H, ACTIVE, COOLDOWN}).

## 4.10 Component Relationship Matrix

| Source Component | Target Component | Data Flow Type | Trigger | Source Doc |
|---|---|---|---|---|
| Primary Calendar Feed | Calendar Normalizer | Raw rows → Normalized EventModel | Scheduled import / manual refresh | §4.4 |
| Holiday/Session Calendar | Session Signal Generator | Session/Holiday tables | Daily build / DST/holiday change | §4.7 |
| Calendar Normalizer | Calendar Events DB | SQL upsert (`calendar_events`) | New or revised event | §4.4, §7.2 |
| Calendar Events DB | Active Signal Builder | Event rows → Active set | Scheduler tick / proximity change | §4.5, §4.6 |
| Active Signal Builder | Active Calendar Signals CSV | CSV (`active_calendar_signals.csv`) | State/proximity change; revision | §2.2–§2.3, §4.3 |
| Revision Listener | Calendar Events DB | CAL8 `F` bump; state/prox recompute | Upstream revision/reschedule | §4.8, §3.2 |
| Active Signal Builder | Metrics/Alerts | Counters; `calendar_revisions_processed` | On emission | §14.1–§14.2 |

## 4.11 Automatic Download & Transformation (Detailed)
#### 4.11 (UPDATED) Calendar Intake & Transformation — Implementation Details
- **Acquisition Scheduler:Every Sunday 12:00 in America/Chicago (CST/CDT), or 17:00/18:00 UTC depending on DST; retry hourly up to 24h.
- **File detection patterns:** `ff_calendar*.csv`, `*calendar*thisweek*.csv`
- **Validation:** “fresh today”, size > 1KB, schema check.
- **Filters:Include High/Medium by default; currency allow/deny list configurable (e.g., default deny CHF=true).
- **Anticipation events:** generate **5** anticipation rows per base event at **1h, 2h, 4h, 8h, 12h** before.
- **Equity events:** inject **Tokyo/London/New York** opens.
- **ID scheme:** **5-digit RCI** (Region-Country-Impact) for StrategyID.
- **Ordering & conflicts:** unified chronological sort with “offset minutes” and stable priority merge (ANTICIPATION < ORIGINAL < EQUITY_OPEN on equal timestamps).
- **Output columns:**  
  `Date, Time, Event Name, Country, Currency, Impact, Event Type, Strategy ID, Hours Before, Priority, Offset Minutes`



- **Discovery**: The importer discovers the most recent download using prioritized patterns (e.g., `*ff*calendar*.csv`, `*economic*calendar*.csv`) in the configured downloads path; newest by mtime wins. If none found, it yields an empty run and emits a health metric.
- **Parsing**: Uses a tolerant CSV reader with **flexible column mapping** (Title/Event/Name; Country/Currency; Date/Day; Time/Hour; Impact/Importance). Rows with missing required fields are skipped. Non‑strict parsers handle different vendor layouts.
- **Quality scoring**: Each parsed row receives a **quality score (0–100)**; rows under threshold are dropped. High/Medium impact rows are retained; Low impact ignored by default.
- **Normalization**: Country/currency are standardized; impact normalized to `High|Medium`. Canonical fields are derived for downstream CAL8 assignment. Event timestamps remain in UTC.
- **Anticipation generation**: For eligible families (e.g., high‑impact releases), anticipation events are generated using configured hours (default 1,2,4,8,12) and appended to the event set.
- **Trigger time computation**: For each original/anticipation event, the engine computes trigger times with event‑type offsets; results are sorted chronologically.

## 4.12 Import Scheduler, Emergency Controls & Watchers

- **Scheduler**: Cron‑style **AsyncIO** scheduler executes imports on `import_day`/`import_hour`; manual rest endpoints (or CLI flag) support ad‑hoc runs.
- **Emergency stop / resume**: Emergency **STOP** pauses jobs **and** marks current/future events `BLOCKED`; **RESUME** unblocks and restarts the schedule. State changes rebroadcast to downstream listeners.
- **File watchers**: Optional watchdog observes incoming paths (e.g., `signals_in/`) and posts work **back to the event loop** safely; debounce rules prevent repeated triggers.

## 4.13 SQLite Persistence & Idempotency (Calendar Domain)

- **Schema**: `calendar_events(event_id PK, cal8, cal5, title, ccy, impact, event_time_utc, state, proximity, revision_seq, quality_score, blocked)` with **UNIQUE** composite key across canonical fields to prevent duplicates.
- **UPSERT**: Imports use transactional **UPSERT** to update rows in place (e.g., state, revision, blocked) while preserving identity; revision bumps increment `revision_seq` and propagate to CAL8 `F`.
- **Indexes**: Covering indexes on `(state, event_time_utc)` and `(ccy, impact)` for active‑set scans.
- **Hydration**: On restart, rebuild the active set for states `{ANT_8H, ANT_1H, ACTIVE, COOLDOWN}` and recompute proximity from `now_utc`.

## 4.14 Minimum‑Gap & Debounce Policies

- **Minimum gap**: EventProcessor enforces a per‑family **minimum gap** (minutes) between triggers to avoid clustered emissions. Lower‑priority duplicates are suppressed or time‑shifted.
- **Debounce**: Emissions of identical `(symbol, cal8, signal_type, state)` within the debounce window are coalesced.

## 4.15 Signal Export/Import Integration

- **Export**: Active signals and decisions are exported with **microsecond + UUID** file naming to avoid collisions when configured for socket/CSV hybrids.
- **Import**: Optional **import inbox** allows manual or third‑party calendar CSV drops to be auto‑parsed using the discovery pipeline. Invalid files are quarantined with an error code.

## 4.16 Configuration Model

- **Config surface**: `database_path`, `signals_export_path`, `signals_import_path`, `static_dir`, `import_day`, `import_hour`, `minimum_gap_minutes`, plus environment variable overrides.
- **Defaults**: Sensible defaults are generated on first run; required folders are created as needed.

## 4.17 Web Dashboard & Telemetry Hooks

- **JSON & WebSocket** endpoints broadcast imports, state changes, and metrics to any local dashboard clients. When a static directory exists, a lightweight status page is mounted; otherwise the API runs headless.
- **Metrics**: Calendar‑specific counters (imports run, revisions processed, rows parsed/dropped by reason, active‑set size) stream to §14 and are mirrored to `health_metrics.csv`.

---

