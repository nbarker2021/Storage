
# ΛΟχ Schemas & Palette (Paper 11)

Files:
- `chrom.schema.json` — JSON Schema for chromatic programs (profile + program).
- `compiled_controls.schema.json` — JSON Schema for compiled controls (ΛΟχ → ΛΟ).
- `expectations.schema.json` — JSON Schema for expected closures/plateaus in conformance tests.
- `palette_v1.json` — Canonical 12-hue palette with dihedral expectations.

Notes:
- All schemas are JSON Schema 2020-12.
- `dtau_fraction` = hue_deg/360; multiply by κ_τ (from calibration) to get absolute Δτ.
- `taps_table` in the profile fixes harmony→tap mappings; use radians in [0, 2π).
