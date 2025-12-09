Section 25 — README.md

# e8mdhg (packaged export)

A self-contained reference implementation of your MDHG-backed E8 lattice system.

## Features
- E8 roots (x2 integer model), exact reflections (rational arithmetic)
- Coxeter-plane projection (h=30), with fallback if NumPy absent
- MDHG content-addressed store, canonical hashing (float-stable)
- Lattice points, glyphs, shell/sector tagging
- Neighbor graph (ip=4), Delaunay triangles, facets, incidence, projected chambers
- Eisenstein E4 invariants + theta checks (k=1..2)
- Universe registry, Atlas snapshot + stable digest
- HTML viewer (v3) with toggles: points / neighbors / triangles / facets

## Quickstart
```python
from e8mdhg.demo import bootstrap_demo
ucid, ub, viewer = bootstrap_demo()
print("Universe CID:", ucid)
