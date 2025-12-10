
# Conformance Suites (Modal) — Paper 14

This directory contains ABBA recipes and expectations for ΛΟψ (phonetic) and ΛΟγ (glyphic), plus minimal reference compilers.

## Files
- `abba_phon.yaml`, `expectations_phon.json`
- `abba_glyph.yaml`, `expectations_glyph.json`
- `compile_phon.py`, `compile_glyph.py` — minimal deterministic compilers
- `compiled_controls_phon_from_compiler.json` — output using `phon_example.json` + `phon_profile_demo.json`
- `compiled_controls_glyph_from_compiler.json` — output using `glyph_example.json` + `glyph_profile_demo.json`

**Usage (pseudo):**
1. Validate programs against `phon.schema.json` / `glyph.schema.json`.
2. Run the compiler with the corresponding profile to produce `compiled_controls*.json`.
3. Execute ABBA runs using the runtime (Paper 9) with matched accuracy.
4. Compare observed closures to `expectations_*.json` and emit certificates.

These are illustrative; production compilers should refine tap placement and delay laws per Paper 12’s aliasing bounds and defect models.
