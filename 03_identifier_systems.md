---
doc_id: econ_rev2
section: 03_identifier_systems
---

# 3. Identifier Systems (Standardization)
 Identifier Systems (Standardization)

## 3.1 Rationale
Earlier coarse IDs conflated distinct event types. The expanded scheme preserves learning granularity and backward compatibility.

## 3.2 CAL8 (Extended Calendar Identifier)
Format: `R1C2I1E2V1F1` → 8 symbols encoded as fields:
- **R (1)**: Region code (e.g., A=Americas, E=Europe, P=APAC).
- **C (2)**: Country/currency (e.g., US, EU, GB, JP).
- **I (1)**: Impact (H=High, M=Med).
- **E (2)**: Event type (e.g., NF=Nonfarm payrolls, CP=CPI, RD=Rate decision, PM=PMI).
- **V (1)**: Version/ingest schema rev.
- **F (1)**: Revision flag sequence (0=no revision, 1..9 revision order).

**Examples**: `AUS H NF 1 0` → `AUSHNF10`; `EGB MCP 1 0` → `EGBMCP10` (space added for readability; stored as 8 chars).

## 3.3 CAL5 (Legacy Alias)
- Maintain CAL5 for continuity; store both CAL8 and CAL5 on all records.

## 3.4 Hybrid ID (Primary Key)
Format: `[CAL8|00000000]-[GEN]-[SIG]-[DUR]-[OUT]-[PROX]-[SYMBOL]`
- **GEN**: `O|R1|R2`
- **SIG**: e.g., `ECO_HIGH_USD`, `ANTICIPATION_1HR_EUR`, `VOLATILITY_SPIKE`, `ALL_INDICATORS`.
- **DUR**: `FL|QK|MD|LG|EX|NA` (NA for durationless signals).
- **OUT**: `O1..O6` (Full SL → Beyond TP, §5.3).
- **PROX**: `IM|SH|LG|EX|CD` (Immediate/Short/Long/Extended/Cooldown).

**Example**: `AUSHNF10-O-ECO_HIGH_USD-FL-O4-IM-EURUSD`.

## 3.5 Signal Taxonomy (Families)
- Calendar: `ECO_HIGH_[CCY]`, `ECO_MED_[CCY]`
- Anticipation: `ANTICIPATION_8HR_[CCY]`, `ANTICIPATION_1HR_[CCY]` (durationless allowed)
- Sessions: `TOKYO_OPEN`, `LONDON_OPEN`, `NY_OPEN`, `NY_LUNCH`, `NY_CLOSE`
- Non‑calendar: `VOLATILITY_SPIKE`, `CORRELATION_BREAK`
- Fallback/technical bundle: `ALL_INDICATORS`

## 3.6 Priority & Composition
- **Scoring** (preferred over rigid suppression): Assign weights (e.g., High=1.0, Med=0.8, Ant1H=0.6, Ant8H=0.4, Session=0.5, VolSpike=0.4, All=0.2). Combine non‑conflicting signals; block known conflicts by rule list.

---

