"""
CQE Meta Configuration
======================

Environment-flexible configuration for CQE meta-infrastructure.
Supports YAML/TOML files, environment variables, and programmatic overrides.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class PathConfig:
    """File system path configuration."""
    
    base_dir: Path = field(default_factory=lambda: Path(os.getenv('CQE_BASE_DIR', '/mnt/data')))
    sandbox_root: Optional[Path] = None
    cqe_production_dir: str = "CQE_PRODUCTION_v2.0.0_COMPLETE"
    cqe_package_name: str = "CQE_PRODUCTION"
    
    def __post_init__(self):
        if self.sandbox_root is None:
            self.sandbox_root = self.base_dir / "sandbox"
        elif isinstance(self.sandbox_root, str):
            self.sandbox_root = Path(self.sandbox_root)
        
        if isinstance(self.base_dir, str):
            self.base_dir = Path(self.base_dir)
    
    @property
    def cqe_root(self) -> Path:
        """Root directory for CQE_PRODUCTION."""
        return self.sandbox_root / self.cqe_production_dir
    
    @property
    def cqe_package_root(self) -> Path:
        """Package root for CQE_PRODUCTION modules."""
        return self.cqe_root / self.cqe_package_name
    
    @property
    def validators_dir(self) -> Path:
        """Validators directory."""
        return self.cqe_package_root / "validators"
    
    def resolve_heart_package(self, package_key: str) -> Optional[Path]:
        """Resolve path to a heart package."""
        heart_packages = {
            "MorphonicLambda": ("Morphonic-LambdaSuite_v1", "Morphonic-LambdaSuite_v1"),
            "GeometryTransformer": ("GeometryOnlyTransformer_Standalone_v2", "GeometryOnlyTransformer_Standalone_v2"),
            "GeoTokenizer": ("GeoTokenizer_TieIn_v1", "GeoTokenizer_TieIn_v1"),
            "MonsterDB": ("MonsterMoonshineDB_v1", "MonsterMoonshineDB_v1"),
            "LatticeBuilder": ("LatticeBuilder_Validator_v1", "LatticeBuilder_Validator_v1"),
            "CoherenceSuite": ("CoherenceSuite_v1", "CoherenceSuite_v1"),
            "Viewer24_v1": ("Viewer24_Controller_v1", "Viewer24_Controller_v1"),
            "Viewer24_v2_CA": ("Viewer24_Controller_v2_CA", "Viewer24_Controller_v2_CA"),
            "Viewer24_v2_CA_Residue": ("Viewer24_Controller_v2_CA_Residue", "Viewer24_Controller_v2_CA_Residue"),
        }
        
        if package_key not in heart_packages:
            return None
        
        outer, inner = heart_packages[package_key]
        candidate = self.sandbox_root / outer / inner
        return candidate if candidate.exists() else None


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    
    # Histogram parameters
    radial_bins: int = 16
    angular_bins: int = 16
    
    # Moonshine feature parameters
    moonshine_dim: int = 32
    moonshine_seed: int = 1337
    
    # CQE channels
    channel_ym: int = 7
    channel_riemann: int = 9
    
    # Clustering thresholds
    pendulum_rho_low_threshold: float = 0.005
    pendulum_rho_high_threshold: float = 0.03
    ns_viscosity_smooth_threshold: float = 0.5
    ns_viscosity_turbulent_threshold: float = 0.05
    
    # Schema versioning
    schema_version: str = "2.1.0"


@dataclass
class KakeyaConfig:
    """Configuration for Kakeya analysis."""
    
    n_azimuth: int = 8
    n_elevation: int = 4
    max_pairs: int = 500
    min_samples: int = 8
    pca_dimensions: int = 3


@dataclass
class ValidatorConfig:
    """Configuration for validator loading."""
    
    timeout: int = 30
    enable_caching: bool = True
    ym_sample_size: int = 512
    
    # Validator-specific options
    ym_validator_name: str = "core_E8YangMillsValidator"
    riemann_validator_name: str = "core_RiemannHypothesisValidator"


@dataclass
class CQEMetaConfig:
    """Root configuration object."""
    
    paths: PathConfig = field(default_factory=PathConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    kakeya: KakeyaConfig = field(default_factory=KakeyaConfig)
    validator: ValidatorConfig = field(default_factory=ValidatorConfig)
    
    # Runtime options
    verbose: bool = False
    enable_profiling: bool = False
    
    @classmethod
    def from_env(cls) -> CQEMetaConfig:
        """Create configuration from environment variables."""
        base_dir = os.getenv('CQE_BASE_DIR', '/mnt/data')
        sandbox = os.getenv('CQE_SANDBOX')
        
        paths = PathConfig(
            base_dir=Path(base_dir),
            sandbox_root=Path(sandbox) if sandbox else None
        )
        
        return cls(paths=paths)
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> CQEMetaConfig:
        """Create configuration from dictionary."""
        paths_dict = config_dict.get('paths', {})
        embedding_dict = config_dict.get('embedding', {})
        kakeya_dict = config_dict.get('kakeya', {})
        validator_dict = config_dict.get('validator', {})
        
        return cls(
            paths=PathConfig(**paths_dict),
            embedding=EmbeddingConfig(**embedding_dict),
            kakeya=KakeyaConfig(**kakeya_dict),
            validator=ValidatorConfig(**validator_dict),
            verbose=config_dict.get('verbose', False),
            enable_profiling=config_dict.get('enable_profiling', False)
        )
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'paths': {
                'base_dir': str(self.paths.base_dir),
                'sandbox_root': str(self.paths.sandbox_root),
                'cqe_production_dir': self.paths.cqe_production_dir,
                'cqe_package_name': self.paths.cqe_package_name,
            },
            'embedding': {
                'radial_bins': self.embedding.radial_bins,
                'angular_bins': self.embedding.angular_bins,
                'moonshine_dim': self.embedding.moonshine_dim,
                'schema_version': self.embedding.schema_version,
            },
            'kakeya': {
                'n_azimuth': self.kakeya.n_azimuth,
                'n_elevation': self.kakeya.n_elevation,
                'max_pairs': self.kakeya.max_pairs,
            },
            'validator': {
                'timeout': self.validator.timeout,
                'ym_sample_size': self.validator.ym_sample_size,
            },
            'verbose': self.verbose,
            'enable_profiling': self.enable_profiling,
        }


# Global default configuration
_default_config: Optional[CQEMetaConfig] = None


def get_config() -> CQEMetaConfig:
    """Get the global configuration singleton."""
    global _default_config
    if _default_config is None:
        _default_config = CQEMetaConfig.from_env()
    return _default_config


def set_config(config: CQEMetaConfig) -> None:
    """Set the global configuration."""
    global _default_config
    _default_config = config
