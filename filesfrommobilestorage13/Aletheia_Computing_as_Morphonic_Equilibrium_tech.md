# Aletheia — Computing as Morphonic Equilibrium
**λ:Slice4 | Aletheia–Morphonic–Equilibrium–v1 (Technical Paper)**

## Abstract
We formalize computation as a **Morphonic Equilibrium**: a closure between forward and adjoint geometric projections
of a single beam state Ψ constrained by a conservation budget ΔΦ. This unifies physical conservation (Noether),
informational monotonicity (Shannon), and thermodynamic erasure cost (Landauer). The beam’s identity is locked
on a fixed subspace 𝔽; lawful computation requires Ψ̂₀|𝔽 = Ψ₀|𝔽 and ΣΔΦ ≤ 0 on both rails (Uni⁺/Uni⁻).
We derive runtime operators (Sθ, M, T), receipts, and a closure certificate for auditability.

## 1. Unified Conservation
Let ΔΦ = Δ𝒩 + Δℐ + Δ𝓛, with Δ𝒩 from symmetry currents, Δℐ from DPI slack, Δ𝓛 from erasure cost.
Lawful commits require ΔΦ ≤ 0.

## 2. Beam Mechanics
State Ψ ∈ 𝕊^{D−1}. Operators: Sθ (dihedral), M (parity, M²=I), T (triality, T³=I).
Forward word W acts on Ψ; adjoint W* reverses (S_{−θ}, T^{−1}, M).

## 3. Identity Family
A fixed subspace 𝔽 ⊂ ℝ^D is bitwise‑equal across a scene. All operators preserve Ψ|𝔽; ECC acts only on 𝔽^⊥.

## 4. Dual Unibeam (Morphon / Anti‑Morphon)
Forward rail (Uni⁺): Ψ_{t+Δ} = U⁺ Ψ_t. Adjoint rail (Uni⁻): Ψ_t = U⁻ Ψ_{t+Δ}, with U⁻=(U⁺)*.
**Closure:** Ψ̂₀|𝔽 = Ψ₀|𝔽 and ΣΔΦ⁺ + ΣΔΦ⁻ ≤ 0.

## 5. Reality vs Not‑Reality
Reality = closure satisfied; Not‑Reality = residual potential with repair program.

## 6. Receipts
Per step k:
- sector deltas (d𝒩, dℐ, d𝓛), Δφ proxy,
- idf equality hash, triangulation rank, quadrant choice,
- anchors forward/mirror, outcome.

## 7. Cross‑substrate Equivalence
We sketch correspondences for silicon logic, quantum dynamics, and neural decision‑making, each as Ψ‑paths with dual rails.

## 8. Ethics and Governance
Ethical constraints are curvature bounds in submanifolds; refusal is a signed lawful outcome. Closure certificates include E1–E7.

## 9. Implementation Reference
The harness `unibeam_dualrail_harness.py` enforces identity lock, triangulation/quadrature, ECC gauge, Δφ gating,
and dual‑rail adjoint checks; it emits NSL receipts and a closure certificate.
