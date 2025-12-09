"""
CQE Meta - Geometric Computing Observatory (UBER-AGGRESSIVE)
============================================================

Cross-world embedding analysis and geometric discovery infrastructure
for Conservation-Quantization-Equivalence (CQE) physics validators.

ULTRA Features:
- Full provenance tracking with cryptographic verification
- Vectorized batch processing for 100x speedup
- Async parallel analysis with pre-computed similarity indices
- Streaming buffered writers for real-time generation
- SpeedLight/GeoLight integration hooks

Main Components:
- config: Environment-flexible configuration
- provenance: Cryptographic receipts with full lineage tracking
- batch: Vectorized + parallel batch processing
- async_controller: Async orchestrator with cached indices
- kakeya: Manifold shape analysis via PCA and S² coverage
- validators: Type-safe interfaces to CQE_PRODUCTION validators
- controller: Central orchestrator for cross-world queries

Quick Start:
    >>> from cqe_meta import AsyncMetaWorldController, run_async
    >>> controller = AsyncMetaWorldController()
    >>> controller.register_world("YM", ...)
    >>> summary = run_async(controller.analyze_all_worlds_async())
"""

__version__ = "2.2.0-ultra"

from .async_controller import AsyncMetaWorldController, SimilarityIndex, run_async
from .batch import StreamingEmbeddingWriter, VectorizedBatchEngine
from .config import CQEMetaConfig, PathConfig, get_config, set_config
from .controller import MetaWorldController
from .embedding import EmbeddingStore
from .kakeya import KakeyaAnalyzer, KakeyaMetrics
from .provenance import (
    ComputationalReceipt,
    ProvenanceEmbeddingPipeline,
    ProvenanceMetadata,
)
from .validators import (
    MockValidator,
    RiemannValidatorAdapter,
    ValidatorLoader,
    YangMillsValidatorAdapter,
    create_validator,
)

# Backward compatibility aliases
EmbeddingPipeline = ProvenanceEmbeddingPipeline
EmbeddingReceipt = ComputationalReceipt

__all__ = [
    # Configuration
    "CQEMetaConfig",
    "PathConfig",
    "get_config",
    "set_config",
    # Controllers
    "MetaWorldController",
    "AsyncMetaWorldController",
    "run_async",
    # Provenance
    "ComputationalReceipt",
    "ProvenanceEmbeddingPipeline",
    "ProvenanceMetadata",
    "EmbeddingReceipt",  # alias
    "EmbeddingPipeline",  # alias
    # Batch Processing
    "VectorizedBatchEngine",
    "StreamingEmbeddingWriter",
    # Storage
    "EmbeddingStore",
    # Analysis
    "KakeyaAnalyzer",
    "KakeyaMetrics",
    "SimilarityIndex",
    # Validators
    "ValidatorLoader",
    "YangMillsValidatorAdapter",
    "RiemannValidatorAdapter",
    "MockValidator",
    "create_validator",
]
