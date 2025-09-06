---
doc_id: huey_unified
section: 08_qc_acceptance_telemetry
---

## 9) Signals Tab
**Purpose:** Provide a unified, filterable stream/table of normalized signals.

### 9.1 Columns
- Time, symbol, kind, direction, strength, confidence, p, n, horizon, tags, source, backend_id
- **Identifiers (visible):** `backend_id`, `hybrid_id`, `cal8`, `cal5`, and Hybrid components: `GEN`, `SIG`, `DUR`, `OUT`, `PROX`, `SYMBOL`
- **Provenance (detail drawer):** `file_seq`, `checksum_sha256`, adapter mode (CSV/socket), last revision id
- **Probability fields:** `p` (0-1), `n` (sample size), `confidence` (LOW/MED/HIGH/VERY_HIGH)

### 9.2 Interactions
- Multi-filter (symbol, timeframe, kind, confidence tier, `p`/`n` ranges, tags).
- **Click-throughs:**
  - From any signal row → open corresponding **Reentry Matrix** slice using the `hybrid_id`/components.
  - From calendar-sourced rows → open **Economic Calendar** event detail.
- Actions: flag, copy, export selection, open in History/Analytics, pin to Live.

### 9.3 Acceptance criteria
- Infinite scroll/pagination without UI jank; stable column widths.
- Filters persist per user/session; exports respect filters and include visible identifier fields.
- Every row resolves to a source (trace id) for auditability, including `file_seq`/`checksum_sha256` when present.
- Backend integration: `backend_id` from backend service present for all rows; mismatches trigger error tile.

### 9.4 Controls & actions (buttons)
- **Save filter preset** — stores current filters under a name (tid:`signals_filter_save`).
- **Clear filters** — reset all filters to defaults (tid:`signals_filter_clear`).
- **Export** (CSV/JSON) — exports visible rows incl. identifiers (tid:`signals_export`).
- **Open in Matrix** (row) — navigate using `hybrid_id` (tid:`signals_open_matrix`).
- **Open in Calendar** (row, when applicable) — open event drawer (tid:`signals_open_calendar`).
- **Pin to Live** (row) — `signal.pin` (tid:`signals_pin_live`).
- **Column picker** — show/hide columns, persist per user (tid:`signals_column_picker`).

---

## 10) Templates Tab
**Purpose:** Save/load dashboard layouts and parameter bundles.

### 10.1 Features (versioning, diff, import/export)
- Versioned templates; diff & rollback; import/export with integrity checks.
- Graceful handling of missing plugins with clear remediation prompts.

### 10.2 Acceptance criteria
- Applying a template updates layout and params atomically.
- Import fails safely with a readable error when checksums or required plugins mismatch.

### 10.3 Controls & actions (buttons)
- **Save template** (primary) — write over current version (tid:`tpl_save`).
- **Save as…** — create new version with notes (tid:`tpl_save_as`).
- **Load** — apply selected template atomically (tid:`tpl_load`).
- **Diff vs current** — side‑by‑side param/layout diff (tid:`tpl_diff`).
- **Export** / **Import** — with integrity checks (tid:`tpl_export`, `tpl_import`).
- **Rollback** — restore a previous version (tid:`tpl_rollback`).

---

## 11) Trade History Tab
**Purpose:** Dedicated view for executed trades and performance KPIs.

### 11.1 Table fields
- Time, symbol, side, size, entry/exit price, SL/TP, realized P/L (amount & %), fees, tags, strategy/indicator origin (if available).
- **Identifiers (visible):** `hybrid_id`, `cal8`, `cal5`, `parameter_set_id`; detail drawer shows Hybrid components `GEN/SIG/DUR/OUT/PROX/SYMBOL`.

### 11.2 Filters & KPIs
- Date range, symbol, side, strategy/tag; KPIs: win rate, avg R, expectancy, P/L by bucket.
- **Re-entry ledger view:** In the detail drawer, show chain **O → R1 → R2** with overlay flags and enforcement indicator (e.g., “max R2 reached”).

### 11.3 Acceptance criteria
- Exports (CSV/JSON) reflect current filters; totals reconcile with broker statements.
- Row click opens a detail drawer with timeline, identifiers (CAL8/CAL5/Hybrid), and linked matrix slice.

### 11.4 Controls & actions (buttons)
- **Export** (CSV/JSON) — filtered trades with identifiers (tid:`hist_export`).
- **Save filter preset** / **Clear** — manage history filters (tid:`hist_filter_save`, `hist_filter_clear`).
- **Open in Equity & Risk** — deep‑link current filters to §24 (tid:`hist_open_equity_dashboard`).
- **Open re‑entry ledger** (row) — show O→R1→R2 chain (tid:`hist_open_ledger`).
- **Copy trade** (row) — copy minimal trade summary to clipboard (tid:`hist_copy_trade`).

---

## 12) History/Analytics Tab
**Purpose:** Logs and analytics for signals, alerts, and configuration changes.

### 12.1 Logs
- Signal emissions, alert lifecycle, config/template changes.
- **Data integrity:** log calendar/matrix file ingestion with `file_seq`/`checksum_sha256`, promotion/demotion reasons, and detected sequence gaps.

### 12.2 KPIs
- Hit rate by source/kind, average target time, confidence distribution, false-positive analysis.

### 12.3 Acceptance criteria
- Time-bucketed charts and tables remain responsive on 100k+ rows (virtualized).
- Drill-down preserves filter context when navigating from Signals or Live.

### 12.4 Controls & actions (buttons)
- **Export logs** — CSV/JSON of current log view (tid:`analytics_export_logs`).
- **Add chart** — create a KPI chart from current query (tid:`analytics_add_chart`).
- **Save chart preset** — store visualization + query (tid:`analytics_save_preset`).
- **Clear filters** — reset analytics query (tid:`analytics_clear`).

---

## 13) DDE Price Feed Tab
**Purpose:** Operate market data connections and symbol subscriptions (UI-level only; no engine wiring specified here).

### 13.1 Prereqs & environment
- Windows OS; MetaTrader 4 (MT4) with **Enable DDE server** checked.
- Python dependency: `pywin32` for DDE client access.
- Symbols must be visible in MT4 **Market Watch**; names must match exactly.

### 13.2 Controls
- Connect/Disconnect; endpoint/profile selector; heartbeat/latency indicator; retry policy toggle.

### 13.3 Subscriptions & live table
- Symbol list with add/remove; per-symbol subscribe/unsubscribe; live table of **Symbol, Bid, Ask, Spread, Last Update (ISO8601), Status, Latency (ms)**; status badges per symbol.

### 13.4 Data contract (UI-level)
- `symbol: str`, `bid: float`, `ask: float`, `spread: float` (points/pips), `ts: datetime` (UTC ISO8601), `status: {ACTIVE, STALE, ERROR}`, `latency_ms: float`, `source: "MT4_DDE"`.
- Validation: `bid < ask`; non-negative `spread`; `ts` monotonic per symbol; stale if no update within TTL.

### 13.5 Retry/backoff policy
- Exponential backoff on disconnect: start 1s, ×2 up to 60s; reset on success.
- After 5 consecutive failures: WARN toast with troubleshooting tips; continue backoff attempts.
- All transitions (connect, retry, success, give-up) emit auditable events.

### 13.6 Troubleshooting
- Ensure MT4 is running and DDE enabled; confirm symbols in Market Watch.
- Check profile server name and firewall permissions.
- Restart MT4/app if handshake fails repeatedly.

### 13.7 Testing hooks & matrix
- **Unit:** connect success/fail, add/remove subscription, schema validation.
- **Integration:** simulate disconnects; verify auto-reconnect/backoff; stale detection; toast lifecycle.
- **Performance:** under N symbols, table updates ≤ 1s; CPU/memory within budget.

### 13.8 Acceptance criteria
- Connection state reflects accurately within ≤ 1s; retries surface as toasts with backoff info.
- Adding/removing a symbol updates the live table immediately and persists across sessions.
- Data contract validation enforced with actionable errors.

### 13.9 Controls & actions (buttons)
- **Connect** / **Disconnect** — manage session (tid:`dde_connect`, `dde_disconnect`).
- **Add symbol** / **Remove** — modify watchlist (tid:`dde_add_symbol`, `dde_remove_symbol`).
- **Subscribe all** / **Unsubscribe all** — toggle subscriptions (tid:`dde_sub_all`, `dde_unsub_all`).
- **Retry now** — trigger immediate reconnect/backoff reset (tid:`dde_retry_now`).
- **Latency test** — send ping request; shows round‑trip (tid:`dde_latency_test`).
- **Export snapshot** — CSV of current table (tid:`dde_export_snapshot`).

---

