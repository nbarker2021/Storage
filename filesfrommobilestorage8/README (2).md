
# CQE Harness (Pinned)

Deterministic runner for your 16 ACTIVE tori with 4-bit caps, octet+mirror viewers,
and compact receipts. Plugins allow drop-in adapters for real data later.

## Structure

- `configs/forms.json` — 16 active forms (tori), caps, viewers
- `configs/paused.json`, `configs/standby.json` — placeholders
- `schemas/*.json` — JSON Schemas for forms/receipts
- `plugins/*.py` — viewer stubs (EM, sound, thermo, axion, quantum)
- `cqe_harness.py` — runner
- `ledger/` — `pinned.json`, `receipts.jsonl`
- `reports/` — `summary.json`, `summary.md`

## Run

```bash
python3 cqe_harness.py
```

Outputs:
- `ledger/receipts.jsonl` — one JSON per form (4-bit cap, votes, echoes, hash)
- `reports/summary.json` — cap/echo histograms, hum gain estimate
- `reports/summary.md` — human-readable summary

## Notes

- Receipts are deterministic per run ID and form_id.
- Plugins return simple echo features; replace with real adapters when ready.
- 4-bit caps: 0000:REST, 0001:NOTCH, 0010:SWAP, 0011:REPH, 0100:CDET, 0101:CART, 0110:SUBH, 0111:HYST, 1000:THR, 1001:CMIR, 1010:OCT, 1011:ANOM, 1100:NOISE, 1101:ECHO, 1110:BOUND, 1111:CORE
