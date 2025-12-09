"""
CQE Meta - Geometric Computing Observatory
===========================================

Cross-world embedding analysis and geometric discovery infrastructure
for Conservation-Quantization-Equivalence (CQE) physics validators.

Main Components:
- config: Environment-flexible configuration
- embedding: Geometry-first embedding pipeline with provenance
- kakeya: Manifold shape analysis via PCA and S² coverage
- validators: Type-safe interfaces to CQE_PRODUCTION validators
- controller: Central orchestrator for cross-world queries

Quick Start:
    >>> from cqe_meta import MetaWorldController
    >>> controller = MetaWorldController()
    >>> controller.register_world("YM", ...)
    >>> summary = controller.get_world_summary()
"""

__version__ = "2.1.0"

from .config import CQEMetaConfig, PathConfig, get_config, set_config
from .controller import MetaWorldController
from .embedding import EmbeddingPipeline, EmbeddingReceipt, EmbeddingStore
from .kakeya import KakeyaAnalyzer, KakeyaMetrics
from .validators import (
    MockValidator,
    RiemannValidatorAdapter,
    ValidatorLoader,
    YangMillsValidatorAdapter,
    create_validator,
)

__all__ = [
    # Configuration
    "CQEMetaConfig",
    "PathConfig",
    "get_config",
    "set_config",
    # Controller
    "MetaWorldController",
    # Embedding
    "EmbeddingPipeline",
    "EmbeddingReceipt",
    "EmbeddingStore",
    # Analysis
    "KakeyaAnalyzer",
    "KakeyaMetrics",
    # Validators
    "ValidatorLoader",
    "YangMillsValidatorAdapter",
    "RiemannValidatorAdapter",
    "MockValidator",
    "create_validator",
]
