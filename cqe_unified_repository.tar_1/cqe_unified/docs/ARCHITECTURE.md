# CQE Architecture

## Overview

The CQE (Cartan Quadratic Equivalence) system is organized into a 7-layer architecture (L0-L6) that provides geometric computation from substrate to reality layer.

## L0-L6 Layer System

### L0: Geometric Substrate

The foundation layer providing geometric structures and operations.

**Key Components:**
- E8 lattice (240 roots, 48 Weyl chambers)
- Niemeier lattices (24-dimensional)
- Toroidal geometry
- Dihedral symmetry (D24)
- Cartan subalgebra

**Module**: `L0_geometric.py`  
**Components**: 148 classes/functions  
**Lines**: ~11,000

### L1: Execution Model

Lambda calculus and execution operators.

**Key Components:**
- Lambda calculus (Pure Math, Structural, Semantic, Chaos)
- ALENA operators (Rθ snap, Weyl flip, midpoint ECC)
- Receipt-based computation

**Module**: `L1_execution.py`  
**Components**: 12 classes/functions  
**Lines**: ~600

### L2: Core Engine (CQE)

The central CQE computation engine.

**Key Components:**
- Geometric operations
- Equivalence classes
- Φ-conservation law
- Combination engines

**Module**: `L2_core.py`  
**Components**: 100 classes/functions  
**Lines**: ~23,600

### L3: Audit & Governance (MORSR)

Receipt-based audit trail and governance.

**Key Components:**
- Immutable receipts
- Channel governance (propose/verify/finalize)
- Merkle-chained ledgers
- Parity channels

**Module**: `L3_audit.py`  
**Components**: 65 classes/functions  
**Lines**: ~6,500

### L4: Execution Wrapper (Sidecar)

Universal execution wrapper and projection interface.

**Key Components:**
- E8 projection interface
- SpeedLight protocol
- Content-addressed storage
- Universal wrapper

**Module**: `L4_wrapper.py`  
**Components**: 25 classes/functions  
**Lines**: ~1,600

### L5: Tool & Application Layer

Applications and validation tools.

**Key Components:**
- Unibeam tool
- SpeedLight tool
- CQE-GVS application
- Validators (Riemann, Yang-Mills, Navier-Stokes, Hodge)

**Module**: `L5_tools.py`  
**Components**: 38 classes/functions  
**Lines**: ~6,300

### L6: Observation & Reality Layer

Observer integration and reality propagation.

**Key Components:**
- Integration of observer receipts
- WorldForge manifold spawning
- Universe crafting
- Reality propagation

**Module**: `L6_reality.py`  
**Components**: 10 classes/functions  
**Lines**: ~800

## Functional Modules

### Storage
Universal atoms and database operations.

**Module**: `storage.py`  
**Components**: 13 classes/functions

### RAG
Semantic graph and retrieval-augmented generation.

**Module**: `rag.py`  
**Components**: 2 classes/functions

### Compression
Shelling compressor and glyph encoding.

**Module**: `compression.py`  
**Components**: 7 classes/functions

### Schema
Schema expansion and handshake data.

**Module**: `schema.py`  
**Components**: 3 classes/functions

### Slices
Face/slice observables and stratification.

**Module**: `slices.py`  
**Components**: 19 classes/functions

### Movie Production
Movie production assistant and corpus management.

**Module**: `movie.py`  
**Components**: 7 classes/functions

### Towers
N-Hyper towers and superpermutation structures.

**Module**: `towers.py`  
**Components**: 1 class/function

### Weighting
5W5H weighting for context-adaptive task slicing.

**Module**: `weighting.py`  
**Components**: 5 classes/functions

### Utils
Helper functions, hashing, residue vectors.

**Module**: `utils.py`  
**Components**: 9 classes/functions

### Misc
Domain-specific CQE components (MainSpace, Actuators, Policy, etc.).

**Module**: `misc.py`  
**Components**: 711 classes/functions

## System Statistics

- **Total Components**: 1,175 (609 classes, 566 functions)
- **Total Modules**: 17
- **Source Files**: 6 monolithic files
- **Total Lines**: ~96,000
- **Original Lines**: 90,310 (from monoliths)

## Source Files

Extracted from:
1. `CQE_CORE_MONOLITH.py` (77,442 lines, 792 segments)
2. `code_monolith.py` (7,842 lines, 337 segments)
3. `CQE_GVS_MONOLITH.py` (2,043 lines, 15 segments)
4. `agrmmdhg.py` (2,557 lines, 9 segments)
5. `forge_monolith.py` (182 lines, 13 segments)
6. `aletheia_monolith.py` (244 lines, 9 segments)

## Usage

```python
# Import by layer
from cqe import L0_geometric, L1_execution, L2_core

# Import functional modules
from cqe import storage, rag, compression

# Use components
from cqe.L0_geometric import E8Lattice
from cqe.L1_execution import ALENAOps
from cqe.L2_core import CQEKernal
```

## Design Principles

1. **Geometric First**: All computation grounded in E8/Niemeier lattice geometry
2. **Receipt-Based**: Every operation generates immutable receipts
3. **Layered Architecture**: Clear separation of concerns across L0-L6
4. **Toroidal Closure**: Lossless guarantee through toroidal geometry
5. **Dihedral Symmetry**: D24 local law enforcement
6. **Φ-Conservation**: Golden ratio preservation throughout
