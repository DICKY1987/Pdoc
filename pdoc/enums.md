# Signal Types
| Name | Description | Category |
|--- | --- | --- |
| ECO_HIGH_USD | High-impact USD economic event | calendar |
| ANTICIPATION_1HR_EUR | 1-hour anticipation signal for EUR events | anticipation |
| VOLATILITY_SPIKE | Market volatility spike detection | technical |

# Proximity Buckets
| Name | Description | Min_minutes | Max_minutes |
|--- | --- | --- | --- |
| IM | Immediate (0-20 minutes) | 0 | 20 |
| SH | Short (21-90 minutes) | 21 | 90 |

# Outcome Buckets
| Name | Description | Rr_min | Rr_max |
|--- | --- | --- | --- |
| O1 | Full SL or worse | None | -1.0 |
| O2 | Partial loss | -1.0 | -0.25 |
