"""
CQE Meta - Ultra-Aggressive Provenance System
=============================================

Full computational receipt system with cryptographic verification,
lineage tracking, and SpeedLight integration.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .config import CQEMetaConfig, get_config


def compute_merkle_root(data: List[float]) -> str:
    """Compute cryptographic hash of vector data."""
    vec_bytes = json.dumps(data, sort_keys=True).encode('utf-8')
    return hashlib.sha256(vec_bytes).hexdigest()


def get_git_commit() -> str:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=1
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return "unknown"


def get_execution_environment() -> Dict[str, str]:
    """Capture execution environment details."""
    import platform
    import sys
    
    return {
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "platform": platform.platform(),
        "hostname": platform.node()
    }


@dataclass
class ProvenanceMetadata:
    """Complete provenance information for an embedding."""
    
    # Cryptographic verification
    merkle_root: str
    validator_signature: str
    
    # Computational lineage
    parent_computation_ids: List[str] = field(default_factory=list)
    git_commit: str = field(default_factory=get_git_commit)
    execution_environment: Dict[str, str] = field(default_factory=get_execution_environment)
    
    # Timing
    generation_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    computation_time_ms: Optional[float] = None
    
    # SpeedLight integration
    speedlight_receipt_id: Optional[str] = None
    cqe_ledger_entry: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "merkle_root": self.merkle_root,
            "validator_signature": self.validator_signature,
            "parent_computation_ids": self.parent_computation_ids,
            "git_commit": self.git_commit,
            "execution_environment": self.execution_environment,
            "generation_timestamp": self.generation_timestamp,
            "computation_time_ms": self.computation_time_ms,
            "speedlight_receipt_id": self.speedlight_receipt_id,
            "cqe_ledger_entry": self.cqe_ledger_entry,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProvenanceMetadata:
        return cls(
            merkle_root=data["merkle_root"],
            validator_signature=data["validator_signature"],
            parent_computation_ids=data.get("parent_computation_ids", []),
            git_commit=data.get("git_commit", "unknown"),
            execution_environment=data.get("execution_environment", {}),
            generation_timestamp=data.get("generation_timestamp", ""),
            computation_time_ms=data.get("computation_time_ms"),
            speedlight_receipt_id=data.get("speedlight_receipt_id"),
            cqe_ledger_entry=data.get("cqe_ledger_entry"),
        )


@dataclass
class ComputationalReceipt:
    """Self-validating embedding with full provenance."""
    
    # Core data
    world: str
    vec: List[float]
    vec_dim: int
    
    # CQE metadata
    lane_feat: List[float]
    cqe_channel: int
    delta_phi: float
    rho_like: float
    scope: bool
    
    # Schema
    schema_version: str
    timestamp: str
    sample_index: Optional[int] = None
    
    # World-specific metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Geometric signature
    kakeya_signature: Optional[Tuple[float, float, float]] = None
    
    # PROVENANCE (new!)
    provenance: Optional[ProvenanceMetadata] = None
    
    def verify_integrity(self) -> bool:
        """Cryptographically verify this receipt hasn't been tampered with."""
        if self.provenance is None:
            return False
        
        computed_hash = compute_merkle_root(self.vec)
        return computed_hash == self.provenance.merkle_root
    
    def link_to_speedlight(self, receipt_id: str, ledger_entry: Optional[str] = None) -> None:
        """Link this embedding to a SpeedLight receipt."""
        if self.provenance is None:
            raise ValueError("Cannot link: no provenance metadata")
        
        self.provenance.speedlight_receipt_id = receipt_id
        if ledger_entry:
            self.provenance.cqe_ledger_entry = ledger_entry
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize with full provenance."""
        result = {
            "world": self.world,
            "vec": self.vec,
            "vec_dim": self.vec_dim,
            "lane_feat": self.lane_feat,
            "cqe_channel": self.cqe_channel,
            "delta_phi": self.delta_phi,
            "rho_like": self.rho_like,
            "scope": self.scope,
            "schema_version": self.schema_version,
            "timestamp": self.timestamp,
        }
        
        if self.sample_index is not None:
            result["sample_index"] = self.sample_index
        
        if self.metadata:
            result["metadata"] = self.metadata
        
        if self.kakeya_signature is not None:
            n, k, vol = self.kakeya_signature
            result["kakeya_signature"] = {"n": n, "K": k, "vol_proxy": vol}
        
        if self.provenance is not None:
            result["provenance"] = self.provenance.to_dict()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ComputationalReceipt:
        """Deserialize with provenance."""
        kakeya_sig = None
        if "kakeya_signature" in data:
            ks = data["kakeya_signature"]
            kakeya_sig = (ks["n"], ks["K"], ks["vol_proxy"])
        
        provenance = None
        if "provenance" in data:
            provenance = ProvenanceMetadata.from_dict(data["provenance"])
        
        return cls(
            world=data["world"],
            vec=data["vec"],
            vec_dim=data["vec_dim"],
            lane_feat=data["lane_feat"],
            cqe_channel=data["cqe_channel"],
            delta_phi=data["delta_phi"],
            rho_like=data["rho_like"],
            scope=data["scope"],
            schema_version=data["schema_version"],
            timestamp=data["timestamp"],
            sample_index=data.get("sample_index"),
            metadata=data.get("metadata", {}),
            kakeya_signature=kakeya_sig,
            provenance=provenance
        )


class ProvenanceEmbeddingPipeline:
    """Enhanced pipeline with full provenance tracking."""
    
    def __init__(self, config: Optional[CQEMetaConfig] = None, validator_signature: Optional[str] = None):
        from .embedding import GeometryFeatureExtractor, CQELaneEncoder, MoonshineFeatureGenerator
        
        self.config = config or get_config()
        self.geom_extractor = GeometryFeatureExtractor(config)
        self.lane_encoder = CQELaneEncoder(config)
        self.moonshine_gen = MoonshineFeatureGenerator(config)
        
        self.validator_signature = validator_signature or "mock_v1.0.0"
        self.parent_computation_ids: List[str] = []
    
    def set_parent_computations(self, parent_ids: List[str]) -> None:
        """Set lineage for embeddings generated by this pipeline."""
        self.parent_computation_ids = parent_ids
    
    def embed_with_provenance(
        self,
        world: str,
        state_vector: np.ndarray,
        channel: int,
        scope: bool,
        sample_index: Optional[int] = None,
        baseline_energy: Optional[float] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> ComputationalReceipt:
        """Generate embedding with full provenance tracking."""
        
        import time
        start_time = time.time()
        
        # Extract geometric features
        points = self.geom_extractor.flatten_to_2d_points(state_vector)
        geom_feat = self.geom_extractor.radial_angle_histogram(points)
        
        # Compute energy metrics
        energy = float(np.sum(state_vector ** 2))
        delta_phi, baseline = self.geom_extractor.compute_energy_metrics(
            energy, baseline_energy
        )
        
        # Compute concentration
        import math
        magnitudes = [math.hypot(x, y) for x, y in points]
        rho_like = self.geom_extractor.compute_concentration(magnitudes)
        
        # Encode lane features
        lane_feat = self.lane_encoder.encode_lane(channel, delta_phi, rho_like, scope)
        
        # Generate moonshine features
        moon_seed = self.config.embedding.moonshine_seed + (sample_index or 0)
        moon_feat = self.moonshine_gen.generate(seed=moon_seed)
        
        # Fuse features
        vec = self._fuse_features({
            "cqe": lane_feat,
            "geom": geom_feat,
            "moonshine": moon_feat
        })
        
        # Compute provenance
        computation_time = (time.time() - start_time) * 1000  # ms
        merkle_root = compute_merkle_root(vec)
        
        provenance = ProvenanceMetadata(
            merkle_root=merkle_root,
            validator_signature=self.validator_signature,
            parent_computation_ids=self.parent_computation_ids.copy(),
            computation_time_ms=computation_time
        )
        
        # Create receipt
        return ComputationalReceipt(
            world=world,
            vec=vec,
            vec_dim=len(vec),
            lane_feat=lane_feat,
            cqe_channel=channel,
            delta_phi=delta_phi,
            rho_like=rho_like,
            scope=scope,
            schema_version=self.config.embedding.schema_version,
            timestamp=datetime.utcnow().isoformat() + "Z",
            sample_index=sample_index,
            metadata=extra_metadata or {},
            provenance=provenance
        )
    
    def _fuse_features(self, features: Dict[str, List[float]]) -> List[float]:
        """Fuse feature groups in stable order."""
        vec: List[float] = []
        for key in sorted(features.keys()):
            vec.extend(features[key])
        return vec


# Backward compatibility alias
EmbeddingReceipt = ComputationalReceipt
EmbeddingPipeline = ProvenanceEmbeddingPipeline
