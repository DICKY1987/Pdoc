# ECON Spec — Patch Bundle to Close Identified Gaps
# Generated: 2025-09-05_21-17-35


> Drop these blocks into your spec (anywhere appropriate). Each block is atomic and wrapped with BEGIN/END IDs for safe scripted merges.
> Then apply the bulk-renames JSON and run the linter to validate.

---

<!-- BEGIN:ECON.003.001.001.DEF.addressing_scheme -->
**Addressing Scheme (Canonical)**
- Grammar: `[DOC].[MAJOR].[MINOR].[PATCH].[TYPE].[ITEM_ID]`
- Example IDs:
  - `ECON.004.002.001.TABLE.calendar_events`
  - `ECON.007.003.002.ACCEPTANCE.pair_effect_integrity`
- TYPE ∈ { DEF, REQ, TABLE, FLOW, ALERT, ARCH, CTRL, EXAMPLE, ACCEPTANCE }
- ITEM_ID: lowercase snake_case

**Rules**
1. IDs are immutable once published (only PATCH increments).
2. Every BEGIN must have matching END with the same ID.
3. Every block MUST include `DEPS:` and `AFFECTS:` metadata (may be empty).

<!-- DEPS:  -->
<!-- AFFECTS: ECON.*** -->
<!-- END:ECON.003.001.001.DEF.addressing_scheme -->

---

<!-- BEGIN:ECON.003.005.001.DEF.enum_registry -->
**Enum Registry (Single Source of Truth)**

```yaml
impact:
  canonical: [High, Medium]
  aliases:
    H: High
    M: Medium

proximity:
  canonical: [IM, SH, MD, LG, EX, CD]   # Immediate, Short, Medium, Long, Extended, Cooldown
  descriptions:
    IM: "Event window ±0–5m"
    SH: "±5–30m"
    MD: "±30–120m"
    LG: "±2–8h"
    EX: "±8–24h"
    CD: "24h+ post-event stabilization"

duration:
  canonical: [FL, QK, MD, LG, EX, NA]   # Flash, Quick, Medium, Long, Extended, NotApplicable

outcome:
  canonical: [O1, O2, O3, O4, O5, O6]
  descriptions:
    O1: "Max loss"
    O2: "Half loss"
    O3: "Scratch/neutral"
    O4: "Half gain"
    O5: "Max gain"
    O6: "Extended gain (trail)"

event_type:
  canonical: [NF, CP, RD, PM, GDP, CPI, NFP, RATE, PMI, RETAIL, EMP, CB]
  notes: "Extend as needed; ensure CSV/DB/code share this source."

bias:
  canonical: [Long, Short, Neutral]

symbol:
  canonical: "Configured currency pairs universe, e.g., [EURUSD, GBPUSD, USDJPY, ...]"
```

**Contract**
- CSVs and DB constraints MUST use the canonical values.
- Aliases may appear in rendering but must map to canonical on write.

<!-- DEPS: ECON.003.001.001.DEF.addressing_scheme -->
<!-- AFFECTS: ECON.007.002.*, ECON.007.003.*, ECON.020.002.* -->
<!-- END:ECON.003.005.001.DEF.enum_registry -->

---

<!-- BEGIN:ECON.002.005.001.REQ.csv_dialect -->
**CSV Dialect & Timestamp Contract**
- delimiter: `,`
- quoting: `minimal`
- newline: `LF` (\n)
- encoding: `UTF-8`
- decimal: `.`
- timestamps: ISO‑8601 UTC `YYYY-MM-DDTHH:MM:SSZ`
- required meta fields for all artifacts: `file_seq` (uint, monotonic per artifact), `created_at_utc` (UTC), `checksum_sha256` (lowercase hex)

<!-- DEPS:  -->
<!-- AFFECTS: ECON.002.002.*, ECON.020.002.* -->
<!-- END:ECON.002.005.001.REQ.csv_dialect -->

---

<!-- BEGIN:ECON.002.002.002.TABLE.health_metrics -->
**health_metrics.csv — Schema**
| column             | type      | unit/format           | constraints                                  | description |
|--------------------|-----------|-----------------------|----------------------------------------------|-------------|
| ts_utc             | TIMESTAMP | ISO‑8601 UTC          | NOT NULL                                     | Metric time |
| ea_bridge_connected| BOOLEAN   |                       | NOT NULL                                     | EA bridge connectivity |
| csv_uptime_pct     | REAL      | % (0–100)             | 0 ≤ v ≤ 100                                  | CSV writer uptime |
| socket_uptime_pct  | REAL      | % (0–100)             | 0 ≤ v ≤ 100                                  | Socket uptime |
| p99_latency_ms     | INTEGER   | ms                    | v ≥ 0                                        | End‑to‑end ingest p99 |
| fallback_rate      | REAL      | % (0–100)             | 0 ≤ v ≤ 100                                  | Fraction of ops in fallback mode |
| conflict_rate      | REAL      | % (0–100)             | 0 ≤ v ≤ 100                                  | File/seq conflicts per hour |
| file_seq           | INTEGER   |                       | NOT NULL, monotonic                          | Artifact sequence counter |
| created_at_utc     | TIMESTAMP | ISO‑8601 UTC          | NOT NULL                                     | Row creation time |
| checksum_sha256    | TEXT      | lowercase hex         | NOT NULL, len=64                             | Row checksum |

**Indexes**
- `(ts_utc)`
- `(file_seq)` unique

<!-- DEPS: ECON.002.005.001.REQ.csv_dialect -->
<!-- AFFECTS: ECON.002.007.*, ECON.020.002.* -->
<!-- END:ECON.002.002.002.TABLE.health_metrics -->

---

<!-- BEGIN:ECON.002.006.001.ACCEPTANCE.atomic_write -->
**Acceptance — Atomic CSV Write**
- Writer MUST:
  1) Write to `*.tmp`
  2) fsync()
  3) Atomic rename to final path
- Reader MUST:
  - Ignore files with missing/invalid `checksum_sha256`.
  - Ignore rows with `file_seq` ≤ last processed `file_seq`.
  - Fail closed on malformed timestamps (not `...Z`).
- Tests:
  - Simulate power loss before/after rename.
  - Corrupt checksum_sha256 → reader discards.
  - Non‑monotonic `file_seq` → reader ignores.

<!-- DEPS: ECON.002.005.001.REQ.csv_dialect -->
<!-- AFFECTS: ECON.020.002.* -->
<!-- END:ECON.002.006.001.ACCEPTANCE.atomic_write -->

---

<!-- BEGIN:ECON.002.007.001.ACCEPTANCE.skew_rules -->
**Acceptance — Time Skew & Degraded Mode**
- Broker vs system UTC skew:
  - |skew| ≤ 1s: NORMAL
  - 1s < |skew| ≤ 5s: WARN → write `health_metrics.csv` with elevated `p99_latency_ms`
  - |skew| > 5s or monotonic clock violation: DEGRADED
- In DEGRADED:
  - Halt new trade signals
  - Continue ingest with `fallback_rate` increment
  - Emit runtime health signal: `runtime.skew.degraded=true`

**Tests**
- Inject 6s positive skew → system transitions to DEGRADED and writes metrics row.
- Restore skew → system returns to NORMAL and logs recovery.

<!-- DEPS: ECON.002.002.002.TABLE.health_metrics -->
<!-- AFFECTS: ECON.014.*, ECON.020.002.* -->
<!-- END:ECON.002.007.001.ACCEPTANCE.skew_rules -->

---

<!-- BEGIN:ECON.002.008.001.REQ.runtime_health_signals -->
**Runtime Health Signals (for Alerts)**
- `runtime.skew.degraded` ∈ {true,false}
- `runtime.csv.writer_uptime_pct` ∈ [0,100]
- `runtime.socket.uptime_pct` ∈ [0,100]
- `runtime.ea_bridge.connected` ∈ {true,false}
- `runtime.conflict.rate` per hour

**Emission**
- Signals derived from `health_metrics.csv` at least once per minute.

<!-- DEPS: ECON.002.002.002.TABLE.health_metrics -->
<!-- AFFECTS: ECON.015.*, ECON.016.* -->
<!-- END:ECON.002.008.001.REQ.runtime_health_signals -->

---

<!-- BEGIN:ECON.003.006.001.ACCEPTANCE.hybrid_id_valid -->
**Acceptance — HybridID Validation**
- Pattern (PCRE): `^(?P<SIG>[A-Z0-9_]+)\.(?P<SYMBOL>[A-Z]{3,6})\.(?P<DUR>FL|QK|MD|LG|EX|NA)\.(?P<OUT>O[1-6])\.(?P<PROX>IM|SH|MD|LG|EX|CD)$`
- Constraints:
  - `SIG` ∈ configured signal set
  - `SYMBOL` ∈ enum `symbol`
  - `DUR`, `OUT`, `PROX` ∈ enum registry

**Tests**
- Valid: `RSI_BREAKOUT.EURUSD.MD.O4.SH`
- Invalid: wrong prox `ZZ` → reject

<!-- DEPS: ECON.003.005.001.DEF.enum_registry -->
<!-- AFFECTS: ECON.020.002.* -->
<!-- END:ECON.003.006.001.ACCEPTANCE.hybrid_id_valid -->

---

<!-- BEGIN:ECON.007.002.002.ACCEPTANCE.calendar_events_integrity -->
**Acceptance — calendar_events Integrity**
- `cal8` is unique per event; parseable; `impact` ∈ enum impact
- `event_time_utc` parseable ISO‑8601 UTC
- Foreign key to `event_type` ∈ enum registry

**Tests**
- Row with `impact='H'` maps to `High` and passes.
- Row with `impact='Low'` fails (not in enum).

<!-- DEPS: ECON.003.005.001.DEF.enum_registry -->
<!-- AFFECTS: ECON.007.003.* -->
<!-- END:ECON.007.002.002.ACCEPTANCE.calendar_events_integrity -->

---

<!-- BEGIN:ECON.007.003.002.ACCEPTANCE.pair_effect_integrity -->
**Acceptance — pair_effect Integrity**
- Unique (`symbol`,`cal8`)
- `bias` ∈ enum bias
- `exposure_cap_pct` ∈ [0,100]

**Tests**
- Duplicate (`EURUSD`,`20250131...`) rejected.
- `exposure_cap_pct=150` rejected.

<!-- DEPS: ECON.003.005.001.DEF.enum_registry -->
<!-- AFFECTS: ECON.014.* -->
<!-- END:ECON.007.003.002.ACCEPTANCE.pair_effect_integrity -->

---

<!-- BEGIN:ECON.020.002.001.EXAMPLE.csv_rows -->
**Canonical CSV Row Examples**

*calendar_events.csv*
```csv
file_seq,created_at_utc,checksum_sha256,cal8,event_time_utc,event_type,impact,title
1,2025-01-31T12:00:00Z,5c3b...e1,20250131_US_CPI_H,2025-01-31T13:30:00Z,CPI,High,US CPI (YoY)
```

*pair_effect.csv*
```csv
file_seq,created_at_utc,checksum_sha256,symbol,cal8,bias,exposure_cap_pct
42,2025-01-31T12:05:00Z,ab19...77,EURUSD,20250131_US_CPI_H,Long,15.0
```

*trade_results.csv*
```csv
file_seq,created_at_utc,checksum_sha256,hybrid_id,order_id,pl_pips,closed_at_utc
77,2025-01-31T15:00:00Z,9f0a...cc,RSI_BREAKOUT.EURUSD.MD.O4.SH,1002345,18.4,2025-01-31T14:59:58Z
```

*health_metrics.csv*
```csv
file_seq,created_at_utc,checksum_sha256,ts_utc,ea_bridge_connected,csv_uptime_pct,socket_uptime_pct,p99_latency_ms,fallback_rate,conflict_rate
9,2025-01-31T12:10:00Z,7d1e...aa,2025-01-31T12:10:00Z,true,99.9,99.5,210,0.0,0.0
```
<!-- DEPS: ECON.002.005.001.REQ.csv_dialect, ECON.002.002.002.TABLE.health_metrics -->
<!-- AFFECTS: ECON.020.*** -->
<!-- END:ECON.020.002.001.EXAMPLE.csv_rows -->
