# CQE Meta - Geometric Computing Observatory

**Version:** 2.1.0  
**Framework:** Conservation-Quantization-Equivalence (CQE)

A clean, production-ready infrastructure for cross-world geometric analysis of physics validators. Enables geometric discovery across disparate physical systems through unified embedding spaces and manifold shape analysis.

---

## Architecture Overview

```
cqe_meta/
├── src/cqe_meta/           # Core package
│   ├── config.py           # Environment-flexible configuration
│   ├── embedding.py        # Geometry-first embedding pipeline
│   ├── kakeya.py           # Manifold shape analysis
│   ├── validators.py       # Type-safe validator interfaces
│   └── controller.py       # MetaWorldController orchestrator
├── tests/                  # Comprehensive test suite
├── config/                 # Configuration templates
├── docs/                   # Extended documentation
└── examples/               # Usage examples

```

---

## Key Features

### 1. Configuration Layer
- **Environment-driven**: Uses `CQE_BASE_DIR` and `CQE_SANDBOX` env vars
- **Programmatic overrides**: Full configuration via Python API
- **Schema versioning**: Track embedding format evolution
- **Path resolution**: Automatic discovery of CQE_PRODUCTION validators

### 2. Enhanced Embedding Pipeline
- **Self-describing receipts**: Embeddings carry complete provenance
- **Geometry-first features**: Radial-angular histograms + CQE lane metadata
- **Schema versioning**: `EmbeddingReceipt` tracks format version
- **Persistent storage**: JSONL format with append/load support

### 3. Kakeya Analyzer
- **Manifold shape metrics**: (K, vol_proxy, dimension_estimate)
- **Geometry classification**: Filament / Needle / Volume archetypes
- **Similarity computation**: Quantitative distance between clouds
- **PCA projection**: Dimensionality reduction for visualization

### 4. Validator Interfaces
- **Type-safe protocols**: Abstract `PhysicsValidator` interface
- **Adapters**: Yang-Mills and Riemann validator integration
- **Mock validators**: Testing without CQE_PRODUCTION
- **Dynamic loading**: Import validators at runtime

### 5. MetaWorldController
- **World registry**: Register multiple physics domains
- **Cross-world queries**: Find geometrically similar regimes
- **Curriculum generation**: Order by geometric complexity
- **Distance matrices**: Pairwise similarity across all worlds

---

## Quick Start

### Installation

```bash
# Add to PYTHONPATH
export PYTHONPATH="/path/to/cqe_meta/src:$PYTHONPATH"

# Set environment variables
export CQE_BASE_DIR="/mnt/data"
export CQE_SANDBOX="/mnt/data/sandbox"
```

### Basic Usage

```python
from cqe_meta import MetaWorldController, CQEMetaConfig
from pathlib import Path

# Initialize with custom config
config = CQEMetaConfig.from_env()
controller = MetaWorldController(config)

# Register a physics world
controller.register_world(
    world_id="YM",
    name="Yang-Mills E8",
    description="E8 gauge theory on root lattice",
    embedding_path=Path("/mnt/data/ym_embeddings.jsonl"),
    cqe_channel=7,
    validator_type="yangmills"
)

# Analyze geometric properties
metrics = controller.analyze_world("YM")
for cluster_name, m in metrics.items():
    print(f"{cluster_name}: K={m.K:.3f}, vol={m.vol_proxy:.3e}")

# Find similar clusters across worlds
similar = controller.find_similar_clusters(
    query_world="YM",
    query_cluster="YM_all",
    target_worlds=["PEND", "NS", "RIEMANN"]
)

# Generate learning curriculum
curriculum = controller.generate_curriculum(
    difficulty_metric="K",  # or "vol_proxy"
    ascending=True  # easy -> hard
)
```

### Generate Embeddings

```python
from cqe_meta import EmbeddingPipeline, EmbeddingStore, create_validator
import numpy as np

# Initialize pipeline
pipeline = EmbeddingPipeline()

# Use mock validator for testing
validator = create_validator("ym", use_mock=True)
samples = validator.generate_samples(100)

# Generate embeddings
receipts = []
baseline_energy = None

for i, sample in enumerate(samples):
    receipt = pipeline.embed_state_vector(
        world="YM",
        state_vector=sample,
        channel=7,
        scope=False,
        sample_index=i,
        baseline_energy=baseline_energy
    )
    
    if baseline_energy is None:
        baseline_energy = validator.compute_energy(sample)
    
    receipts.append(receipt)

# Save to disk
store = EmbeddingStore(Path("ym_embeddings.jsonl"))
store.save(receipts)
```

---

## Configuration

### Environment Variables

```bash
# Base directory for CQE infrastructure
CQE_BASE_DIR=/mnt/data

# Sandbox root (overrides $CQE_BASE_DIR/sandbox)
CQE_SANDBOX=/custom/sandbox/path
```

### Programmatic Configuration

```python
from cqe_meta import CQEMetaConfig, PathConfig

config = CQEMetaConfig(
    paths=PathConfig(
        base_dir=Path("/mnt/data"),
        cqe_production_dir="CQE_PRODUCTION_v2.0.0_COMPLETE"
    ),
    embedding=EmbeddingConfig(
        radial_bins=16,
        angular_bins=16,
        schema_version="2.1.0"
    ),
    kakeya=KakeyaConfig(
        n_azimuth=8,
        n_elevation=4,
        max_pairs=500
    ),
    verbose=True
)

# Set as global default
from cqe_meta import set_config
set_config(config)
```

---

## Geometric Archetypes

The Kakeya analyzer classifies embedding clouds into geometric archetypes:

| Archetype | K Range | vol_proxy Range | Physical Examples |
|-----------|---------|------------------|-------------------|
| **Filament** | <0.3 | <0.01 | Laminar flow, quasi-periodic orbits |
| **Needle** | <0.3 | 0.01-0.3 | Constrained chaos, boundary layers |
| **Transition** | 0.3-0.5 | 0.1-0.3 | Intermittent dynamics |
| **Structured Volume** | 0.3-0.5 | >0.3 | Partially ergodic systems |
| **Ergodic Volume** | >0.5 | >0.3 | Fully-developed turbulence |
| **Sparse Volume** | >0.5 | <0.3 | High-D exploration, sparse sampling |

---

## API Reference

### Configuration

- `CQEMetaConfig` - Root configuration object
- `PathConfig` - Filesystem paths
- `EmbeddingConfig` - Embedding parameters
- `KakeyaConfig` - Analyzer parameters

### Embedding

- `EmbeddingReceipt` - Self-describing embedding with provenance
- `EmbeddingPipeline` - Generate embeddings from state vectors
- `EmbeddingStore` - Persistent JSONL storage

### Analysis

- `KakeyaAnalyzer` - Geometric shape analysis
- `KakeyaMetrics` - Shape descriptor (K, vol_proxy, dimension)

### Validators

- `ValidatorLoader` - Dynamic validator importing
- `YangMillsValidatorAdapter` - E8 Yang-Mills interface
- `RiemannValidatorAdapter` - Riemann Hypothesis interface
- `MockValidator` - Testing without CQE_PRODUCTION

### Controller

- `MetaWorldController` - Central orchestrator
  - `register_world()` - Add physics domain
  - `analyze_world()` - Compute Kakeya metrics
  - `find_similar_clusters()` - Cross-world similarity search
  - `generate_curriculum()` - Order by complexity
  - `compute_distance_matrix()` - Pairwise similarities

---

## Testing

```bash
cd cqe_meta
python3 tests/test_cqe_meta.py
```

**Test Coverage:**
- ✓ Configuration serialization
- ✓ Embedding generation and storage
- ✓ Kakeya analysis on synthetic data
- ✓ Validator interfaces
- ✓ MetaWorldController orchestration
- ✓ Cross-world similarity queries
- ✓ Curriculum generation

**14/14 tests passing**

---

## Design Principles

1. **Separation of Concerns**: Physics validators, embeddings, analysis, and orchestration are cleanly isolated

2. **Configuration over Hardcoding**: All paths and parameters configurable via environment or API

3. **Schema Versioning**: Embeddings carry version metadata for future-proof evolution

4. **Type Safety**: Protocol-based validator interfaces enable static type checking

5. **Self-Describing Data**: Embeddings include complete provenance and metadata

6. **Testability**: Mock validators allow testing without full CQE_PRODUCTION stack

---

## Future Enhancements

- **Provenance Tracking**: Cryptographic receipts for computational lineage
- **Streaming Embeddings**: Real-time embedding generation
- **Distributed Analysis**: Multi-node Kakeya computation
- **Visualization Tools**: Interactive 3D PCA projections
- **Transfer Learning**: Train on one world, test on another
- **Anomaly Detection**: Flag physics that violates geometric universality

---

## License

Part of the CQE (Conservation-Quantization-Equivalence) geometric computing platform.

---

## Contact

For questions about CQE meta-infrastructure, see the CQE_PRODUCTION documentation.
