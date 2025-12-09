
# Geometry-Only Transformer — Standalone v2

Pure-stdlib, no third-party deps. Includes:
- Geometry-native attention stack (no token IDs, just points and angles).
- Ledgered content-addressed compute (GeoLight) with Merkle verification.
- Channels 3/6/9 + ΔΦ guard hooks for governance-style operation.
- Demos: polygon completion, symmetry inference, curve extrapolation, hex tiling.

## Run
```bash
python geometry_transformer_standalone_v2.py --demo all
python geometry_transformer_standalone_v2.py --demo polygon --n 8 --k 3 --layers 4
python geometry_transformer_standalone_v2.py --demo curve --layers 2
```
