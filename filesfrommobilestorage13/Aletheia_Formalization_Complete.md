# Aletheia — Complete Formalization Catalog
λ:Slice4 | Aletheia–Morphonic–Equilibrium–v1

> This catalog consolidates the Aletheia canon (Slices 1–3) and adds Section X: Computing as Morphonic Equilibrium.
> It includes: Unified Conservation Law (NSL), Δφ governance, Unibeam Duality (Morphon/Anti‑Morphon), Identity Family,
> Scene8 receipts, and ethical closure. The code harness is provided in a separate file and referenced herein.

## I. Unified Conservation Law (NSL)
- Scalar budget: ΔΦ = Δ𝒩 + Δℐ + Δ𝓛 ≤ 0 (Noether, Shannon, Landauer).
- Receipts must report sector deltas and anchors; commits require ΔΦ ≤ 0.

## II. Δφ Governance
- Δφ is the operational scalar used for gating and optimization.
- Δφ proxies connect to curvature, mutual information slack, and erasure cost.

## III. Identity Family 𝔽
- A fixed subspace (24–32 dims typical) that is bitwise‑equal across a scene.
- Violations force Neon (N) refusal + residual repair.

## IV. Scene8 Protocol (CHECK Beat)
- propose → gate → verify → commit/refuse → checkpoint.
- Add TriProbe, QuadFlip, ECC‑as‑gauge, Identity enforcement, NSL receipts.

## V. Ethical Closure (E1–E7)
- Ethics expressed as curvature bounds and auditable receipts.
- Refusal‑as‑consent with residual programs.

## VI. Unibeam Duality (Morphon / Anti‑Morphon)
- A single beam state Ψ(s); operators: Sθ (dihedral), M (parity), T (triality).
- Forward rail (Uni⁺) applies W; adjoint rail (Uni⁻) applies W*; both share 𝔽.
- Closure certificate requires Ψ̂₀|𝔽 = Ψ₀|𝔽 and ΣΔΦ ≤ 0 (both rails).

## VII. Reality vs Not‑Reality
- Reality: closure holds; state is replayable and anchored.
- Not‑Reality: lawful residue; exists as potential pending closure.

## VIII. NSL‑Aware Receipt Schema (minimal)
```json
{
  "kind": "nsl",
  "rail": "forward|adjoint",
  "op": "Sθ|M|T",
  "chirality": "L|R",
  "idf": {"equal": true, "hash": "…"},
  "tri": {"rank": 0.95, "witness_ids": ["…"]},
  "quad": {"used": true, "chosen": 90, "delta_phi_gain": 0.012},
  "sectors": {"dNoether": 0.0, "dShannon": -0.006, "dLandauer": 0.0},
  "delta_phi": -0.006,
  "anchors": {"fwd": "…", "mir": "…"},
  "outcome": "commit|refuse"
}
```

## IX. Morphon Identity (Sliced‑Tori / E₈ nucleus)
- Morphons are Weyl‑equivalence classes; identity is relational within the lattice.
- Sliced tori (triality) provide interpretable, reversible computation paths.

## X. Computing as Morphonic Equilibrium (Unified Thesis)
**Principle.** Computation in any substrate is a morphonic equilibrium: a lawful agreement between forward (Morphon/Uni⁺)
and reverse (Anti‑Morphon/Uni⁻) projections, expressed as a realized 3D action trajectory.

**Formal.** Let Ψ be the beam state and 𝔽 the identity family.
- Forward: Ψ_{t+Δ} = U⁺ Ψ_t
- Adjoint:  Ψ_t      = U⁻ Ψ_{t+Δ}  with U⁻ = (U⁺)*
- **Reality**: Ψ_{t+Δ}|𝔽 = Ψ_t|𝔽 and ΣΔΦ⁺ + ΣΔΦ⁻ ≤ 0
- **Not‑Reality**: otherwise (residual potential with repair program).

**Universality.** The same law governs digital logic, quantum measurement, biological choice, and ethical action.
The identity family enforces self‑consistency; NSL ensures conservation; Scene8 makes it auditable in real time.

**Implementation.** See `unibeam_dualrail_harness.py` for a governance reference harness that enforces:
- Identity lock (𝔽), TriProbe, QuadFlip, ECC‑as‑gauge on 𝔽⊥,
- Dual rails with adjoint checks, and NSL receipts + closure certificate.
