"""
CQE Validator Interfaces
=========================

Abstract interfaces and concrete implementations for physics validators.
Provides type-safe integration with CQE_PRODUCTION validators.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

import numpy as np

from .config import CQEMetaConfig, get_config


class PhysicsValidator(Protocol):
    """Protocol for physics validators that generate state samples."""
    
    def generate_samples(self, n_samples: int) -> np.ndarray:
        """Generate n state samples."""
        ...
    
    def compute_energy(self, state: np.ndarray) -> float:
        """Compute energy-like metric for state."""
        ...


class ValidatorLoader:
    """Dynamic loader for CQE_PRODUCTION validators."""
    
    def __init__(self, config: Optional[CQEMetaConfig] = None):
        self.config = config or get_config()
        self._loaded_validators: Dict[str, Any] = {}
    
    def load_validator(self, validator_name: str) -> Any:
        """Load a validator by name from CQE_PRODUCTION."""
        if validator_name in self._loaded_validators:
            return self._loaded_validators[validator_name]
        
        validator_path = self.config.paths.validators_dir / f"{validator_name}.py"
        if not validator_path.exists():
            raise FileNotFoundError(f"Validator not found: {validator_path}")
        
        # Add to path
        validator_dir = str(self.config.paths.validators_dir)
        if validator_dir not in sys.path:
            sys.path.insert(0, validator_dir)
        
        # Import module
        try:
            module = importlib.import_module(validator_name)
            self._loaded_validators[validator_name] = module
            return module
        except ImportError as e:
            raise ImportError(f"Failed to import validator {validator_name}: {e}")
    
    def get_validator_class(self, validator_name: str, class_name: str) -> type:
        """Get a specific class from a validator module."""
        module = self.load_validator(validator_name)
        if not hasattr(module, class_name):
            raise AttributeError(f"Validator {validator_name} has no class {class_name}")
        return getattr(module, class_name)


class YangMillsValidatorAdapter:
    """Adapter for E8 Yang-Mills validator."""
    
    def __init__(self, config: Optional[CQEMetaConfig] = None):
        self.config = config or get_config()
        self.loader = ValidatorLoader(config)
        self._validator_instance: Optional[Any] = None
    
    def _ensure_loaded(self) -> Any:
        """Lazy load the validator."""
        if self._validator_instance is None:
            val_name = self.config.validator.ym_validator_name
            try:
                cls = self.loader.get_validator_class(val_name, "E8YangMillsValidator")
                self._validator_instance = cls()
            except (FileNotFoundError, ImportError, AttributeError) as e:
                raise RuntimeError(f"Cannot load Yang-Mills validator: {e}")
        return self._validator_instance
    
    def generate_samples(self, n_samples: Optional[int] = None) -> np.ndarray:
        """Generate E8 root samples."""
        validator = self._ensure_loaded()
        n_samples = n_samples or self.config.validator.ym_sample_size
        
        # Try different methods
        if hasattr(validator, "generate_e8_roots_sample"):
            try:
                return validator.generate_e8_roots_sample(num_samples=n_samples)
            except TypeError:
                return validator.generate_e8_roots_sample()
        elif hasattr(validator, "generate_e8_roots"):
            return validator.generate_e8_roots()
        else:
            raise AttributeError("Validator has no root generation method")
    
    def compute_energy(self, state: np.ndarray) -> float:
        """Compute energy-like norm for E8 state."""
        return float(np.sum(state ** 2))


class RiemannValidatorAdapter:
    """Adapter for Riemann Hypothesis validator."""
    
    def __init__(self, config: Optional[CQEMetaConfig] = None):
        self.config = config or get_config()
        self.loader = ValidatorLoader(config)
        self._validator_instance: Optional[Any] = None
    
    def _ensure_loaded(self) -> Any:
        """Lazy load the validator."""
        if self._validator_instance is None:
            val_name = self.config.validator.riemann_validator_name
            try:
                cls = self.loader.get_validator_class(val_name, "RiemannHypothesisValidator")
                self._validator_instance = cls()
            except (FileNotFoundError, ImportError, AttributeError) as e:
                raise RuntimeError(f"Cannot load Riemann validator: {e}")
        return self._validator_instance
    
    def get_e8_roots(self) -> np.ndarray:
        """Get E8 roots from validator."""
        validator = self._ensure_loaded()
        if hasattr(validator, "e8_roots"):
            return validator.e8_roots
        raise AttributeError("Validator has no e8_roots attribute")
    
    def get_laplacian(self) -> np.ndarray:
        """Get E8 Laplacian from validator."""
        validator = self._ensure_loaded()
        if hasattr(validator, "construct_e8_laplacian"):
            try:
                return validator.construct_e8_laplacian()
            except TypeError:
                raise RuntimeError("construct_e8_laplacian() requires arguments")
        raise AttributeError("Validator has no construct_e8_laplacian method")
    
    def compute_energy(self, state: np.ndarray) -> float:
        """Compute energy-like norm."""
        return float(np.sum(state ** 2))


class MockValidator:
    """Mock validator for testing without CQE_PRODUCTION."""
    
    def __init__(self, dimension: int = 8, n_samples: int = 100):
        self.dimension = dimension
        self.n_samples = n_samples
    
    def generate_samples(self, n_samples: Optional[int] = None) -> np.ndarray:
        """Generate mock samples."""
        n = n_samples or self.n_samples
        return np.random.randn(n, self.dimension) * np.sqrt(2.0)
    
    def compute_energy(self, state: np.ndarray) -> float:
        """Compute mock energy."""
        return float(np.sum(state ** 2))


def create_validator(
    validator_type: str,
    config: Optional[CQEMetaConfig] = None,
    use_mock: bool = False
) -> Any:
    """Factory function to create validators."""
    if use_mock:
        return MockValidator()
    
    if validator_type.lower() in ("ym", "yangmills", "yang-mills"):
        return YangMillsValidatorAdapter(config)
    elif validator_type.lower() in ("riemann", "rh"):
        return RiemannValidatorAdapter(config)
    else:
        raise ValueError(f"Unknown validator type: {validator_type}")
