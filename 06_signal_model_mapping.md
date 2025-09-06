---
doc_id: huey_unified
section: 06_signal_model_mapping
---

## 5) Normalized Signal Model
A single envelope for all signal-producing components, enabling consistent routing, filtering, display, and analytics.

### 5.1 Core fields
- `id`, `ts`, `source` (indicator/strategy id), `symbol` (or basket), `kind` (e.g., breakout/momentum/mean_reversion/squeeze/other), `direction` (long/short/neutral), `strength` (0–100), `confidence` (LOW/MED/HIGH/VERY_HIGH), `ttl` (optional), `tags` (list).

### 5.2 Probability extension fields
- `trigger` (human-readable description), `target` (price move/threshold evaluated), `p` (probability 0–1), `n` (sample size), `state` (optional snapshot of relevant indicator states), `horizon` (evaluation window), `notes`.

### 5.3 Contract guarantees
- Versioned schema; missing optional fields → null; strict types; units included for quantitative values; trace id for data lineage.

## 5.1 Standardized Enums (Single Source of Truth)

```yaml
signal_direction:
  canonical: [LONG, SHORT, NEUTRAL]

confidence:
  canonical: [LOW, MED, HIGH, VERY_HIGH]
  
proximity:
  canonical: [IM, SH, LG, EX, CD]
  descriptions:
    IM: "Immediate (0-5m)"
    SH: "Short (5-30m)" 
    LG: "Long (30m-2h)"
    EX: "Extended (2h+)"
    CD: "Cooldown (post-event)"

alert_severity:
  canonical: [INFO, WARN, ERROR]
```

---

