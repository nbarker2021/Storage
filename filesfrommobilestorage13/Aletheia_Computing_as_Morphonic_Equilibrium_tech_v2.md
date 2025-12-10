# Computing as Morphonic Equilibrium — Technical Paper (v2)

## Abstract
We formalize computation as the closure of a dual‑rail evolution constrained by a unified conservation budget ΔΦ.
Identity is enforced via a projector P_𝔽; commits require numeric‑tolerant equality and ΔΦ ≤ 0. We integrate a
magic‑based order parameter to anticipate correlation percolation and trigger ECC escalation.

## 1. Preliminaries
State Ψ ∈ 𝕊^{D−1}. Operators: dihedral S_θ, parity M (M²=I), triality T (T³=I).
Identity family 𝔽 with projector P_𝔽; tolerance ε≈1e−5.

## 2. NSL Budget
ΔΦ = Δ𝒩 + Δℐ + Δ𝓛 with Landauer term k_B T ln2 × bits_erased. DPI slack is used as Δℐ proxy.

## 3. Dual‑Rail Law and Certificate
Forward: U⁺ word on Ψ; Adjoint: U⁻ = (U⁺)*. Certificate:
‖P_𝔽 Ψ^+ − P_𝔽 Ψ^-‖ < ε and Σ(ΔΦ^+ + ΔΦ^-) ≤ 0.

## 4. Repair Algorithm (Not‑Reality)
If identity/budget fails, run ECC escalation on 𝔽^\perp with bounded iterations; outcome fields:
`pending_repair|commit|refuse`. Record erasure bits for Δ𝓛.

## 5. Magic as Order Parameter
`I_M` rises near percolation; use `magic.status` to auto‑escalate ECC at fuzzy 24D edges.
We provide 1D/2D surrogates and K‑bundle sharpening (K∈{1,4,8,24}).

## 6. Formal Morphons
Morphon = Weyl orbit [v] in E₈; mophonic identity as torus slice consistent with P_𝔽. Admissible words preserve
P_𝔽 inner products; proof sketch provided in Appendix A (Weyl invariance on 𝔽).

## 7. Substrate Correspondences (Auditable)
- Digital: backprop/adjoint, reversible checkpoints, ΔΦ receipts.
- Quantum/Optical: magic transitions, self‑organizing beams → morphon shells.
- Neural: rehearsal (Uni⁺) vs feedback (Uni⁻); SNAP identity carriers.
- Ethical: governance rail as adjoint; E1–E7 curvature bounds.
Each entry references concrete receipts or surrogates in the repo.

## 8. Implementation Reference
Harness v2 (`unibeam_dualrail_harness_v2.py`): tolerance identity, fail‑closed, parameterized NSL, receipt fields:
`magic.*`, `repair.*`. MagicProbe adapters planned for step‑level logging.

## 9. Validation Plan (abridged)
Stability basin, adversarial flip tests, baseline comparison, 24‑bundle sharpening — per `Aletheia_Universal_Validation_Plan.md`.

## Appendix A — Invariance Sketch
We show that for admissible words U composed of S_θ, M, T constrained by portal invariants, the action on P_𝔽 contracts residuals orthogonal to 𝔽 and preserves inner products on 𝔽, ensuring the identity condition is well‑posed up to ε.