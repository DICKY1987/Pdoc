---
doc_id: huey_unified
section: 02_runtime_architecture
---

## 2) Architecture Overview

<!-- BEGIN:HUEY.002.001.001.ARCH.runtime_services -->
### 2.1 Core runtime services
- **EventBus (pub/sub):** Topics for data, UI, risk, signals, alerts; metrics for publish rates and subscriber counts.
- **StateManager:** Central, snapshot-oriented store (read-only views for UI components; writes via dispatched actions or events). Holds: connectivity, user prefs, risk posture, open positions summary, indicator statuses, alert stats, and selected template.
- **Feature Registry:** Registry for indicators, views, and tools. Provides discovery metadata (id, category, inputs/outputs, default params, render hints).
- **Theme System:** Semantic tokens (surface, outline, positive/neutral/negative, info/warn/error) and variants (light/dark/contrast). No hardcoded colors; tokens only.
- **Toast/Alert Manager:** Queues, priorities, cooldowns, deduplication, and persistence of last N alerts. Emits via EventBus; visible in UI and stored to history.
- **Risk Ribbon:** Compact, always-visible summary of risk posture (latency, data-health, leverage bands, exposure, guard flags). Integrates with alerts.
<!-- DEPS: HUEY.001.001.001 -->
<!-- AFFECTS: HUEY.007.001.001 -->
<!-- END:HUEY.002.001.001.ARCH.runtime_services -->

<!-- BEGIN:HUEY.002.002.001.ARCH.app_layout_navigation -->
### 2.2 App layout & navigation
- **Global frame:** Header (status/quick actions) → left navigation (tabs) → content area (grid-based panels).
- **Primary tabs:**
  1) **Live** — real-time overview & operator console
  2) **Config (Settings)** — global and per-indicator/strategy parameters
  3) **Signals** — normalized signal stream with probability fields
  4) **Templates** — save/load layouts & parameter bundles
  5) **Trade History** — executed orders with `hybrid_id`, `cal8`, `cal5`, `parameter_set_id` linkage, P/L metrics, filters & KPIs
  6) **History/Analytics** — logs, KPIs, exports (signals/alerts/config)
  7) **DDE Price Feed** — data feed controls, subscriptions, live table
  8) **Economic Calendar** — event ingestion, filters, exports
    9) **System Status** — health, diagnostics, controls
<!-- DEPS: HUEY.001.001.001 -->
<!-- AFFECTS: HUEY.007.001.001 -->
<!-- END:HUEY.002.002.001.ARCH.app_layout_navigation -->

<!-- BEGIN:HUEY.002.003.001.ARCH.grid_manager -->
### 2.3 Grid Manager (panels)
- **Cells:** 1×1, 2×1, 2×2 (extensible sizes). Drag/drop, resize, add/remove panels.
- **Panel contract:** `panel_id`, `title`, `render_mode` (overlay/inline/table/chart), `inputs` (symbols, timeframe), `outputs` (values/bands/states), `params` (schema), and `events_subscribed`.
- **Lifecycle hooks:** `mount`, `update(params/state)`, `unmount`.
- **Persistence:** Layout & params are versioned and stored per Template.
<!-- DEPS: HUEY.001.001.001 -->
<!-- AFFECTS: HUEY.007.001.001 -->
<!-- END:HUEY.002.003.001.ARCH.grid_manager -->

<!-- DEPS: HUEY.001.001.001 -->
<!-- AFFECTS: HUEY.007.001.001 -->
<!-- END:HUEY.002.001.001.ARCH.architecture_overview -->

---

