---
doc_id: huey_unified
section: 03_plugin_model
---

## 3) Indicator Plugin Model
- **Registration:** Each indicator registers with id, category (trend/oscillator/volatility/volume/custom/other), required feeds, and display hints.
- **Config schema:** Parameter spec with types, bounds, defaults, and dependencies. Used to auto-generate forms (see §4).
- **Execution:** Deterministic `calculate` producing typed outputs (values, bands, states). Performance budget per tick to protect UI.
- **Display:** Indicators render via the Grid Manager with their declared `render_mode` and `outputs`.
- **Safety:** Hot reload of params re-initializes internal buffers safely; param changes are transactional.

---

