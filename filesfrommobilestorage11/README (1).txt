EM–CQE Test Harness (Synthetic) — README
========================================
What this is
------------
A minimal, offline harness that exercises the new gizmos:
  • Classical EM: interference/harmonics (Δ-harm) and polarization (Stokes/DoP)
  • QED statistics: g²(0) for coherent/thermal/antibunched regimes
  • Nonlinearity proxy: cubic term → harmonics + bicoherence
  • Hidden-sector mock: tiny oscillatory conversion (primary vs secondary channel)
  • 4-bit commit: b1(stats class), b2(polarization lock), b3(harmonic linearity), b4(nonlinearity)

Thresholds (inline defaults)
----------------------------
  g2_antibunch_max = 0.85     # antibunched if g²(0) < 0.85
  g2_poisson_tol   = 0.10     # coherent if |g²(0)-1| <= 0.10
  g2_thermal_min   = 1.30     # thermal if g²(0) >= 1.30
  dop_min          = 0.80     # polarization locked if DoP >= 0.80
  harm_rms_max     = 1.00 Hz  # harmonic RMS deviation threshold (Δ-harm)
  cartan_hit_min   = 0.60     # fraction of peaks sitting on integer multiples
  bico_min         = 0.05     # nonlinearity if bicoherence ≥ 0.05 and energy OK

Files
-----
  • EM_CQE_receipts_summary.csv : Tabular receipts and commit bits for T1..T4
  • This README

Interpreting the CSV
--------------------
Columns include:
  test, regime — scenario labels
  g2 — estimated g²(0)
  DoP, S_signs, pol_code — polarization receipts and code (3 sign bits -> 0..7)
  f0_est, delta_harm, cartan_hit — harmonic linearity receipts
  bicoherence, energy_ok — nonlinearity receipts
  b1, b1_class, b2, b3, b4 — the 4-bit commit and derived class

Notes
-----
  • All data here are synthetic; the shapes, thresholds, and receipts are engineered for demonstration.
  • Hidden-sector (“light-through-walls”) is represented as a provisional overlay only: do not commit.