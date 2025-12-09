
# Morphonic Geometry‑Native Lambda Calculus (MGLC) — Spec v1.0

This package formalizes a geometry‑native λ‑calculus for the Morphonic/CQE system.
It includes syntax, typing, and reductions (β, η, δ, μ), a modal layer (□/◇), and
a glyph/sound abstraction to bind visual tokens to λ‑constructs. A runtime bridges
evaluation to the SpeedLight sidecar for ledgered, content‑addressed caching.

## 1. Syntax (core)
Terms t ::= x | λx.t | t t | let x = t in t | const c | ⟨t,t⟩ | fst t | snd t | if t then t else t | μx.t

## 2. Types
τ ::= Bool | Nat | τ×τ | τ→τ | ⟦ΔΦ≤ε⟧
We treat ⟦ΔΦ≤ε⟧ as a grade used in governance receipts; it annotates effects/energy.

## 3. Reductions
- β: (λx.t) v → t[x:=v] when v is a value (λ, const, pair)
- η: λx.f x → f when x∉FV(f) [omitted in default engine, safe to enable]
- δ: primitive constants (succ, pred, iszero, …)
- μ: μx.t → t[x:=μx.t] (iso‑recursive unfolding)

## 4. Subject reduction & progress (sketch)
Under the provided typing rules and ΔΦ‑guarded β, δ steps, types are preserved
and well‑typed closed terms progress unless they are values or μ‑diverge.

## 5. Modal/Channel semantics
□t and ◇t frame necessity/possibility relative to CQE channels {3,6,9}; evaluation
policies can map □ to “no‑effect/ΔΦ≤0” lanes and ◇ to “may‑effect” lanes.

## 6. Glyph/Sound
A compact table maps runes (λ, μ, ×, ⊳, ⊲) to constructors and can be extended
to color/sound codes for operator selection in Scene8/WorldForge contexts.

## 7. Sidecar integration
`runtime.eval_with_sidecar(term, scope="lambda", channel=3)` executes with SpeedLight
caching + Merkle ledger; `result, cost, receipt_id = …`.
