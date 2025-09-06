---
doc_id: huey_unified
section: 05_tabs_panels_controls
---

## 7) Live Tab
**Purpose:** Give operators a real-time, at-a-glance view and quick actions.

### 7.1 Key panels
<!-- DEPS: HUEY.002.001 -->
<!-- AFFECTS: HUEY.007.003 -->
<!-- END:HUEY.007.001.001.REQ.live_tab_overview -->
- Status cards: connectivity, latency, data-health, risk posture, open positions summary.
- Signal ticker: latest normalized signals with direction/strength/confidence (`p`, `n` when available).
- Quick actions: acknowledge alerts, pin signals, jump to related Config/History.

### 7.2 Filters & controls
- Symbol/timeframe filters; pause/resume auto-scroll; compact/detailed row density.

### 7.3 Acceptance criteria
- Live cards update ≤ 1s latency under expected load.
- Ticker deduplicates identical signals within TTL and shows ack state.
- All quick actions emit corresponding EventBus events and persist to History.

### 7.4 Controls & actions (buttons)
- **Acknowledge alert** (row & toolbar) — *Ack selected alert* → `alerts.acknowledge {alert_id}`; disables when none selected; side‑effect: ticker row marked ACK, toast confirms (tid:`live_ack_alert`).
- **Pin signal** (row) — *Pin to Live* → `signal.pin {signal_id}`; appears in Live ticker/cards; undo via row menu (tid:`live_pin_signal`).
- **Pause/Resume auto‑scroll** (toolbar toggle, ␣) — `ui.ticker_autoscroll_toggle`; persists in user prefs (tid:`live_autoscroll_toggle`).
- **Open in Config** (row) — navigate to source indicator/strategy form → `ui.navigate {target:"config", anchor}` (tid:`live_open_config`).
- **Copy trace id** (row) — copies normalized `trace_id` to clipboard (tid:`live_copy_trace`).
- **Refresh snapshot** (toolbar, ⟳) — force refresh Live cards → `ui.refresh_live` (guard: cooldown 3s) (tid:`live_refresh`).

---

## 8) Config (Settings) Tab
**Purpose:** Centralize global settings and per-indicator/strategy parameters with strong validation.

### 8.1 Global settings
- Data sources, update intervals, alert thresholds, theme, hotkeys.

### 8.1.1 Communications Bridge Settings
- **COMM_MODE:** Auto / CSV / Socket (default: Auto)
- **ListenPort:** Socket port (default: 5555, range: 1024-65535)
- **CommPollSeconds:** CSV polling interval (default: 5s, min: 1s)
- **EnableCSVSignals:** Enable CSV file transport (default: true)
- **EnableDLLSignals:** Enable socket/DLL transport (default: false)
- **DebugComm:** Verbose communication logging (default: false)
- **CSV_DIR:** Directory path for CSV artifacts
- **CHECKSUM:** Validation method (fixed: sha256)
- **SEQ_ENFORCE:** Enforce monotonic file_seq (default: true)


### 8.2 Per‑indicator/strategy forms
- Auto-generated forms from parameter specs with inline validation.

### 8.3 Dependency guardrails
- Disable/hide fields when upstream feeds or modes are incompatible.

### 8.4 Acceptance criteria
- Debounced validation on change; hard errors block Save; warnings allow Save with toast.
- Parameter changes are transactional and logged; rollback via Templates or History.
- Form generation is driven solely by parameter specs; no custom hand-wired fields.

### 8.5 Controls & actions (buttons)
- **Save** (primary, ⌘/Ctrl+S) — validate then persist params; emits `config.changed` on success; disabled on invalid (tid:`config_save`).
- **Revert** — discard unsaved edits in current form; confirmation dialog (tid:`config_revert`).
- **Validate now** — run full validation without saving; surfaces toasts (tid:`config_validate_now`).
- **Load defaults** — restore registered defaults for the current plugin (tid:`config_load_defaults`).
- **Import JSON** — load parameter JSON; schema check + diff preview (tid:`config_import_json`).
- **Export JSON** — export current parameters with checksum_sha256 (tid:`config_export_json`).
- **Copy deep‑link** — copies URL to this form/section for sharing (tid:`config_copy_link`).
- **Reconnect Socket** — drop & re-establish socket (guard: COMM_MODE=Socket) (tid:`config_comm_reconnect`).
- **Test Bridge** — send ping through current COMM_MODE and show round-trip & error count (tid:`config_comm_test`).

---

