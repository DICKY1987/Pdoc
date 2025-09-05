# CSV Interface Contracts

## File Naming Convention
- Format: `{base_name}_{timestamp}_{sequence}.csv`
- Timestamp: UTC ISO8601 compact format (YYYYMMDDTHHMMSSZ)
- Sequence: Zero-padded 6-digit sequence number

## Common Headers
All CSV files must include:
- `file_seq`: Monotonic sequence number
- `created_at_utc`: Creation timestamp (UTC ISO8601)
- `checksum`: SHA-256 hash of content

## Active Calendar Signals CSV
**File**: `active_calendar_signals.csv`
**Columns**: symbol, cal8, cal5, signal_type, proximity, event_time_utc, state, priority_weight, file_seq, created_at_utc, checksum

## Re-entry Decisions CSV
**File**: `reentry_decisions.csv`
**Columns**: hybrid_id, parameter_set_id, lots, sl_points, tp_points, entry_offset_points, comment, file_seq, created_at_utc, checksum

## Atomic Write Protocol
1. Write to temporary file with `.tmp` extension
2. Calculate and include checksum
3. Fsync to ensure data persistence
4. Rename to final filename
