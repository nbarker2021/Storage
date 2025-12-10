
# Morphonic Tool Bundle (Schemas & Examples)

This bundle includes first-pass schemas and example payloads for the ΛΟ decision layers and runtime.

## Included
- `phon.schema.json` / `phon_example.json` — Modal audio (ΛΟψ) program spec + example.
- `glyph.schema.json` / `glyph_example.json` — Modal glyph (ΛΟγ) program spec + example.
- `compiled_controls_phon_example.json` / `compiled_controls_glyph_example.json` — Illustrative outputs conforming to `compiled_controls.schema.json`.
- `phi_model.schema.json` / `phi_model_example.json` — φ-model (compute→energy) spec + example.
- `run_config.schema.json` / `run_config_example.yaml` — Runtime config spec + example.

**Previously delivered** (Paper 11):
- `chrom.schema.json` / `palette_v1.json`
- `compiled_controls.schema.json`
- `expectations.schema.json`
- `ΛΟχ_schemas_README.md`

## Notes
- All JSON Schemas target draft 2020-12.
- Example compiled-controls are illustrative; real values should be produced by the respective compilers.
- `run_config_example.yaml` aligns with Paper 9’s API and SOPs.
