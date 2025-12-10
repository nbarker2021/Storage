# CQE Unified Build (Session)

## Modules
- ARC360 (snap/wrap, cascades, bridges)
- PRIME_COPRIME (prime closure, CRT corridors, recycle routes)
- SLICE_CALCULUS (viewers 6/10/8; equalizers; energies; keys; braid current)
- CQE_CONTROLLER (closed-loop controller; LPC + receipts)
- TORUS (closure sizes; periodicity hooks)
- Plus slice library: SACNUM, LATT, FRAC, RAMANUJAN, GAUSS, NOETHER, SHANNON, HODGE, E8_LEECH, TRANSLATE_RT, OPS_CSV, OPS_JSON, META_LEX, GOLDEN, FUZZER

## Artifacts
- Acceptance table: /mnt/data/cqe_unified_build/acceptance_table.csv
- Harness: /mnt/data/cqe_unified_build/cqe_unified_harness.yaml
- Slice registry: /mnt/data/cqe_unified_build/slice_registry.json

## Promotion gates
A) ARC360 strict tick closure AND any bridge
B) PRIME top-5 ≥ 0.60 AND CRT corridor present
C) Controller collapse: key dispersion ≤ 1 at W=80
D) ARC360 loose tick closure AND (residue-bridge OR prime-tunnel)

Decision rule: accept if ANY gate passes.
