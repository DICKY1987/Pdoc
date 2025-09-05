# Hybrid ID Schema

## Format
`[CAL8|00000000]-[GEN]-[SIG]-[DUR]-[OUT]-[PROX]-[SYMBOL]`

## Components
- **CAL8**: 8-character calendar identifier or 00000000 for non-calendar
- **GEN**: Generation (O|R1|R2)
- **SIG**: Signal type from approved taxonomy
- **DUR**: Duration bucket (FL|QK|MD|LG|EX|NA)
- **OUT**: Outcome bucket (O1-O6)
- **PROX**: Proximity bucket (IM|SH|LG|EX|CD)
- **SYMBOL**: Trading symbol

## Examples
- `AUSHNF10-O-ECO_HIGH_USD-FL-O4-IM-EURUSD`
- `00000000-R1-VOLATILITY_SPIKE-QK-O2-SH-GBPUSD`

## Validation
- Total length must not exceed 64 characters
- Components must use only approved values
- Symbol must be valid trading instrument
