---
doc_id: huey_unified
section: 04_layout_navigation
---

## 4) Validation & Controls (Unified UX Layer)
**Goal:** One canonical validation spec applied app-wide (Config, Templates, Indicator params, Strategy rules).

### 4.1 Control types
- **Booleans:** Toggle or checkbox; inline help text; grouped by feature.
- **Numbers:** Min/max, step, units (pips, %, seconds); soft warnings vs hard errors; inter-field constraints (e.g., `TakeProfit > StopLoss`).
- **Enums:** Radio/select with descriptions; searchable for long lists.
- **Text:** Length and regex constraints; placeholders with examples.
- **Dynamic sections:** Conditional show/hide based on other fields or data availability.

### 4.2 Validation behaviors
- **Debounced validation** on change; immediate validation on apply.
- **Severity levels:** info, warn, error (with consistent toast styling).

### 4.3 Accessibility & help
- Inline descriptions, tooltips, error regions announced to screen readers.

### 4.4 Reusability
- Parameter specs power: form generation, import/export, API validation, and template diffs.

---

