---
doc_id: econ_rev2
section: 07_risk_portfolio_controls
---

# 7. Data & Storage Layer

## 7.

### 7.

### 7.z Signal Validation Policy (Pre‑Execution Gates)

All incoming signals MUST pass these gates before emission:
- **Symbol/Instrument Match** — instrument must be tradable and enabled.
- **Lot/Size Bounds** — within configured min/max and step increments.
- **Stop/TP Distance** — meets broker and strategy minimums.
- **Market Open/Session** — allowed session and not in restricted windows.
- **Risk Limits** — account-level drawdown and concentration limits.
- **Duplicate/Replay** — reject duplicate `file_seq` or stale TTL.

Failures are logged with a reason code; no partial emissions are permitted.


### 7.y Risk & Circuit-Breakers (Requirements-Level)

**Trigger Taxonomy (examples):**
- **Daily Drawdown**: equity drop exceeds configured % or currency amount.
- **Equity Floor Breach**: account equity below minimum threshold.
- **Consecutive Errors**: repeated adapter/bridge failures beyond tolerance.
- **Concentration Breach**: exposure per symbol/pair beyond limits.
- **Market State**: spread/volatility spikes beyond configured bounds.

**Required Actions:**
- **Pause New Decisions** (soft circuit-breaker).
- **Flatten/Close Open Positions** (hard breaker).
- **Cancel Open Orders** where applicable.
- **Escalate** via health metrics + alerting (page thresholds).

> These actions are configuration-driven and logged via `health_metrics.csv` and `system_status` tables.
x Signal Input Modes (Interface-Level, Source-Agnostic)

Accepted non-implementation signal sources (must conform to the Decision contract):
- **Calendar/Matrix** — anticipation and time-window entries.
- **Internal Indicators** — computed analytics from the indicator engine.
- **External Feeds** — CSV or socket-delivered signals from external systems.
- **Manual/Operator** — controlled inputs with the same schema and gating.
- **Time-Slot/Batch** — scheduled rebalances or routine health probes.

> All sources undergo the same **validation gates** and risk/circuit-breaker checks before emission.

### 7.2–7.7 Data Schemas (Calendar/Matrix/Params) (NEW)
All tables are **SQLite**. Text fields store UTC ISO8601 where applicable. Create indexes as noted.

#### 7.2 `calendar_events`
Columns:
- `id` INTEGER PK AUTOINCREMENT
- `cal8` TEXT NOT NULL UNIQUE
- `cal5` TEXT NOT NULL
- `event_time_utc` TEXT NOT NULL
- `country` TEXT NOT NULL
- `currency` TEXT NOT NULL
- `impact` TEXT CHECK(impact IN ('High','Medium')) NOT NULL
- `event_type` TEXT CHECK(event_type IN ('ORIGINAL','ANTICIPATION','EQUITY_OPEN')) NOT NULL
- `strategy_id_rci` TEXT NOT NULL  -- 5-digit RCI
- `hours_before` INTEGER DEFAULT 0  -- anticipation only
- `priority` INTEGER NOT NULL       -- ANT<ORIG<EQT ordering
- `offset_minutes` INTEGER DEFAULT 0
- `quality_score` REAL DEFAULT 1.0
Indexes:
- `idx_calendar_events_time` on (`event_time_utc`)
- `idx_calendar_events_country_impact` on (`country`,`impact`)

#### 7.3 `pair_effect`
Columns:
- `id` INTEGER PK
- `symbol` TEXT NOT NULL
- `cal8` TEXT NOT NULL
- `bias` TEXT CHECK(bias IN ('LONG','SHORT','NEUTRAL')) DEFAULT 'NEUTRAL'
- `exposure_cap_pct` REAL DEFAULT 3.0
- `note` TEXT
Unique:
- (`symbol`,`cal8`)
Indexes:
- `idx_pair_effect_symbol` on (`symbol`)

#### 7.4 `parameters` (versioned)
Columns:
- `id` INTEGER PK
- `parameter_set_id` TEXT NOT NULL
- `param_version` TEXT NOT NULL   -- semver "1.2.0"
- `created_at_utc` TEXT NOT NULL
- `order_type` TEXT CHECK(order_type IN('Market','Limit','Stop')) NOT NULL
- `lot_method` TEXT CHECK(lot_method IN('Fixed','RiskBased')) NOT NULL
- `lot_value` REAL NOT NULL
- `sl_points` INTEGER NOT NULL
- `tp_points` INTEGER NOT NULL
- `entry_offset_points` INTEGER DEFAULT 0
- `sl_tp_ratio_min` REAL DEFAULT 1.2
Unique:
- (`parameter_set_id`,`param_version`)
Indexes:
- `idx_parameters_set` on (`parameter_set_id`)

#### 7.5 `matrix_combinations`
Maps HybridID features to a ParameterSet **version**.
Columns:
- `id` INTEGER PK
- `calendar_id` TEXT NOT NULL   -- cal8 or cal5
- `proximity_bucket` TEXT       -- nullable for fallbacks
- `duration_bucket` TEXT        -- nullable for fallbacks
- `outcome_class` TEXT          -- nullable for fallbacks
- `parameter_set_id` TEXT NOT NULL
- `param_version` TEXT NOT NULL
- `active` INTEGER DEFAULT 1
Unique:
- (`calendar_id`,`proximity_bucket`,`duration_bucket`,`outcome_class`)
Indexes:
- `idx_matrix_calendar` on (`calendar_id`)

#### 7.6 `mapping_audit`
Columns:
- `id` INTEGER PK
- `timestamp_utc` TEXT NOT NULL
- `signal_id` TEXT NOT NULL
- `calendar_id` TEXT
- `proximity_bucket` TEXT
- `duration_bucket` TEXT
- `outcome_class` TEXT
- `resolved_tier` INTEGER NOT NULL  -- 0..4 (see §6.8)
- `parameter_set_id` TEXT
- `param_version` TEXT
- `comment` TEXT

#### 7.7 `trade_results` (augment if missing)
Add columns if not present:
- `stop_loss` REAL NULL
- `take_profit` REAL NULL
- `current_profit` REAL NULL

> **Freeze Rules:** On **emit**, copy the **exact** `parameter_set_id` + `param_version` used into the outbound CSV and any downstream persistence; never rewrite historical fills.

1 Topology
- **Per‑symbol** SQLite DBs: `EURUSD_matrix.db`, etc.
- **Central** `parameters.db` shared across symbols.

## 7.2 Core Tables (Per‑Symbol DB)
- `matrix_map(hybrid_id PK, cal8, cal5, gen, sig, dur, out, prox, symbol, parameter_set_id, active, assigned_at, assigned_by, notes)`
- `trade_results(exec_id PK, hybrid_id, parameter_set_id, param_version, params_frozen_json, open_time_utc, close_time_utc, prices..., outcome_bucket, rr, pips, duration_cat)`
- `calendar_events(event_id PK, cal8, cal5, title, ccy, impact, event_time_utc, state, proximity, revision_seq)`
- `metrics(ts_utc, key, value)`

## 7.3 Parameter Repository (Central DB)
- `parameter_sets(parameter_set_id PK, category, risk_level, version, json_config, created_at, perf_score, usage_count)`

## 7.4 PairEffect Model (Per‑Symbol)
- Table `pair_effects(symbol PK, direction_bias, expected_spread_x, cooldown_minutes, lot_multiplier)`; joined at decision time.

## 7.5 Indexing & Performance
- Composite indexes: (`sig`,`prox`), (`out`,`dur`), (`parameter_set_id`).
- Sub‑ms lookups targeted under normal load.

## 7.6 Backup & Recovery
- Daily incremental + weekly full; automated integrity checks; export scripts for DR.

---

## 7.7 Broker Constraints Repository
- **Purpose:** Central, authoritative source of broker/platform microstructure limits used across all symbols.
- **Scope:** Values may be global per account or symbol‑specific overrides.
- **Schema (central DB):**
  - `broker_id` (PK), `account_id` (nullable), `symbol` (nullable for global rows)
  - `min_lot`, `lot_step`, `max_lot`
  - `min_stop_points`, `freeze_level_points`
  - `max_orders_total`, `max_orders_symbol`
  - `slippage_limit_points`, `execution_mode` (e.g., MARKET/INSTANT)
  - `last_checked_utc`, `source` (auto‑probe/manual), `notes`
- **Indexes:** (`broker_id`,`symbol`), (`account_id`,`symbol`).
- **Usage:** Joined by `broker_id/account_id/symbol` during parameter overlay (§6.4) and pre‑flight checks (§6.6). Values clamp/round lots and distances before OrderSend.

## 7.8 Component Relationship Matrix

| Source Component | Target Component | Data Flow Type | Trigger | Source Doc |
|---|---|---|---|---|
| All Compute Services | Per‑Symbol DBs | SQL upserts/queries | Persist/read events/decisions/results | §7.2 |
| Parameter Authoring Tool | Parameter Repository (central) | ParameterSet create/update | Publish/approve | §7.3, §15.1 |
| Backup Scheduler | Storage/WAL | Snapshots & integrity checks | Daily (inc) / Weekly (full) | §7.6 |
| Metrics Emitters | Metrics Table | KPI rows | Per tick / on events | §14.1 |
| Calendar Ingest | Calendar Events Table | Upsert | Import/revision | §4.4, §4.8 |
| EA (via CSV ETL) | Trade Results Table | Appends → ETL | Order updates | §17.2, §9.240 |
| Audit Writers | Mapping Audit | Append-only diffs | On mapping change | §5.9, §15.1 |

# 8. Risk & Portfolio Controls

## 8.

## 8.x Re‑Entry Logic Model (Domain Rules)

**Outcome Classification (illustrative six-bucket model):**
- **R** — Reversal beyond tolerance
- **ML** — Minor Loss
- **B** — Baseline / Neutral
- **MG** — Minor Gain
- **G** — Gain (Meets target)
- **X** — Exceptional / Outlier

**Action Schema (per bucket):**
- `action_type` *(hold|reduce|add|exit|reenter)*
- `size_multiplier` *(real, e.g., 0.5, 1.0, 1.5)*
- `delay` *(duration, e.g., 30s, 5m)*
- `confidence_adjustment` *(−1.0..+1.0)*
- `validity_window` *(duration)*

**Profiles:** `Conservative`, `Balanced`, `Aggressive` — profiles select per-bucket parameters only; interface contracts remain unchanged.
1 Exposure Caps
- Caps by `base_ccy` and `quote_ccy`; block/scale new entries when breached.

## 8.2 Spread/Latency Modeling
- `expected_spread_x` and `min_stop_buffer_points` per signal family & proximity.

## 8.3 Drawdown & Streak Policies
- Rolling 4h/12h drawdown dampening; consecutive‑loss throttle.

## 8.4 Component Relationship Matrix

| Source Component | Target Component | Data Flow Type | Trigger | Source Doc |
|---|---|---|---|---|
| Decision Engine (Matrix/Re‑Entry) | Exposure Controller | Position intents | Before emit | §8.1, §9.222 |
| Exposure Controller | Decision Engine | Size scaling / blocks | Caps breached/cleared | §8.1 |
| Spread/Latency Model | Decision Engine & EA | `expected_spread_x`, `min_stop_buffer_points` | Proximity/session change | §8.2 |
| Circuit Breakers | Execution Engine (EA) | Trip/Reset signals | Threshold breaches | §6.7, §16.4 |
| Drawdown/Streak Monitor | Decision Engine | Risk dampeners | Rolling window updates | §8.3 |
| Metrics/Alerting | Ops/SRE | Breach notifications | On threshold | §14.2 |

---

