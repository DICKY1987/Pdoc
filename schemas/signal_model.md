# Normalized Signal Model Schema

## Core Fields (Required)
- `id`: Unique signal identifier (UUID)
- `ts`: Timestamp (UTC ISO8601)
- `source`: Source component identifier
- `symbol`: Trading instrument
- `kind`: Signal type (breakout/momentum/mean_reversion/squeeze/other)
- `direction`: Direction (long/short/neutral)
- `strength`: Strength (0-100)
- `confidence`: Confidence level (LOW/MED/HIGH/VERY_HIGH)
- `ttl`: Time to live (optional)
- `tags`: Additional metadata (list)

## Probability Extension Fields (Optional)
- `trigger`: Human-readable description
- `target`: Price move/threshold
- `p`: Probability (0-1)
- `n`: Sample size
- `state`: Indicator state snapshot
- `horizon`: Evaluation window
- `notes`: Additional context

## Validation Rules
- `strength` must be 0-100
- `ts` must be valid UTC ISO8601
- `confidence` must be one of enumerated values
- `p` must be between 0 and 1 if present
