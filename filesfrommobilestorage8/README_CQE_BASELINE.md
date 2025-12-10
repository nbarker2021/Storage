# CQE Baseline System (v0.1)

Shapes-first token orchestration wired to E8, Golay-24/Leech core-24 checks, de Bruijn parity-lane sims,
and Stage-1/2/3 flow per the master playbook.

## Run

```bash
# Plan
python -m cqe.cli.cqe_plan --request "Your corpus/task description here" --outdir runs/plan

# Stage 2
python -m cqe.cli.cqe_step2 --request "Your corpus/task description here" --outdir runs/step2

# Stage 3
python -m cqe.cli.cqe_step3 --request "Your corpus/task description here" --outdir runs/step3
```

## Notes
- E8 snapping: two-coset nearest-plane (even Z^8 vs half-integer with odd parity).
- Golay[24,12,8]: exact H with coset-leader ≤3 decoder.
- Leech (Λ24): Construction-A style lift sufficient for gating and receipts.
- Receipts: blake2b-256 over canonical JSON; Merkle leaves included at bucket creation.
