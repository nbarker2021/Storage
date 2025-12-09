"""
CQE Meta Embedding Pipeline
============================

Enhanced embedding generation with configuration support, schema versioning,
and proper abstraction layers.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .config import CQEMetaConfig, get_config


@dataclass
class EmbeddingReceipt:
    """Self-describing embedding with provenance metadata."""
    
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
    
    # Provenance
    schema_version: str
    timestamp: str
    sample_index: Optional[int] = None
    
    # World-specific metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Geometric signature (computed lazily)
    kakeya_signature: Optional[Tuple[float, float, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON storage."""
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
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EmbeddingReceipt:
        """Deserialize from dictionary."""
        kakeya_sig = None
        if "kakeya_signature" in data:
            ks = data["kakeya_signature"]
            kakeya_sig = (ks["n"], ks["K"], ks["vol_proxy"])
        
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
            kakeya_signature=kakeya_sig
        )


class GeometryFeatureExtractor:
    """Extract geometric features from state vectors."""
    
    def __init__(self, config: Optional[CQEMetaConfig] = None):
        self.config = config or get_config()
    
    def radial_angle_histogram(
        self,
        points: List[Tuple[float, float]],
        rbins: Optional[int] = None,
        abins: Optional[int] = None
    ) -> List[float]:
        """Build radial-angle histogram from 2D points."""
        rbins = rbins or self.config.embedding.radial_bins
        abins = abins or self.config.embedding.angular_bins
        
        hist = [[0.0 for _ in range(abins)] for _ in range(rbins)]
        
        for x, y in points:
            r = math.hypot(x, y)
            a = math.atan2(y, x)
            if a < 0:
                a += 2 * math.pi
            
            r_norm = min(1.0, r)
            ri = min(rbins - 1, int(r_norm * rbins))
            ai = min(abins - 1, int(a / (2 * math.pi) * abins))
            hist[ri][ai] += 1.0
        
        flat = [v for row in hist for v in row]
        total = sum(flat) or 1.0
        return [v / total for v in flat]
    
    def flatten_to_2d_points(self, vector: np.ndarray) -> List[Tuple[float, float]]:
        """Flatten high-dimensional vector to 2D point pairs."""
        flat = vector.reshape(-1)
        points = []
        for i in range(0, len(flat), 2):
            x = float(flat[i])
            y = float(flat[i + 1]) if i + 1 < len(flat) else 0.0
            points.append((x, y))
        return points
    
    def compute_energy_metrics(
        self,
        current_energy: float,
        baseline_energy: Optional[float] = None
    ) -> Tuple[float, float]:
        """Compute ΔΦ-like energy change."""
        if baseline_energy is None or abs(baseline_energy) < 1e-9:
            return 0.0, current_energy
        
        delta_phi = (current_energy - baseline_energy) / abs(baseline_energy)
        return delta_phi, baseline_energy
    
    def compute_concentration(self, magnitudes: List[float], top_fraction: float = 0.1) -> float:
        """Compute ρ-like concentration metric (top-k% / total)."""
        if not magnitudes:
            return 0.0
        
        sorted_mags = sorted(magnitudes, reverse=True)
        split = max(1, int(len(sorted_mags) * top_fraction))
        top_sum = sum(sorted_mags[:split])
        total_sum = sum(sorted_mags) or 1.0
        return top_sum / total_sum


class CQELaneEncoder:
    """Encode CQE lane metadata."""
    
    def __init__(self, config: Optional[CQEMetaConfig] = None):
        self.config = config or get_config()
    
    def encode_lane(
        self,
        channel: int,
        delta_phi: float,
        rho_like: float,
        scope: bool
    ) -> List[float]:
        """Encode CQE lane feature vector."""
        ch_norm = channel / 10.0
        scope_bit = 1.0 if scope else 0.0
        return [ch_norm, float(delta_phi), float(rho_like), scope_bit]


class MoonshineFeatureGenerator:
    """Generate moonshine-compatible stub features."""
    
    def __init__(self, config: Optional[CQEMetaConfig] = None):
        self.config = config or get_config()
    
    def generate(
        self,
        dim: Optional[int] = None,
        seed: Optional[int] = None
    ) -> List[float]:
        """Generate deterministic moonshine feature."""
        dim = dim or self.config.embedding.moonshine_dim
        seed = seed or self.config.embedding.moonshine_seed
        
        rng = np.random.RandomState(seed)
        return rng.uniform(-1.0, 1.0, size=dim).astype(float).tolist()


class EmbeddingPipeline:
    """Complete embedding generation pipeline."""
    
    def __init__(self, config: Optional[CQEMetaConfig] = None):
        self.config = config or get_config()
        self.geom_extractor = GeometryFeatureExtractor(config)
        self.lane_encoder = CQELaneEncoder(config)
        self.moonshine_gen = MoonshineFeatureGenerator(config)
    
    def embed_state_vector(
        self,
        world: str,
        state_vector: np.ndarray,
        channel: int,
        scope: bool,
        sample_index: Optional[int] = None,
        baseline_energy: Optional[float] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> EmbeddingReceipt:
        """Generate complete embedding from state vector."""
        
        # Extract geometric features
        points = self.geom_extractor.flatten_to_2d_points(state_vector)
        geom_feat = self.geom_extractor.radial_angle_histogram(points)
        
        # Compute energy metrics
        energy = float(np.sum(state_vector ** 2))
        delta_phi, baseline = self.geom_extractor.compute_energy_metrics(
            energy, baseline_energy
        )
        
        # Compute concentration
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
        
        # Create receipt
        return EmbeddingReceipt(
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
            metadata=extra_metadata or {}
        )
    
    def _fuse_features(self, features: Dict[str, List[float]]) -> List[float]:
        """Fuse feature groups in stable order."""
        vec: List[float] = []
        for key in sorted(features.keys()):
            vec.extend(features[key])
        return vec


class EmbeddingStore:
    """Persistent storage for embeddings."""
    
    def __init__(self, path: Path, config: Optional[CQEMetaConfig] = None):
        self.path = path
        self.config = config or get_config()
    
    def save(self, receipts: List[Any]) -> int:
        """Save embeddings to JSONL file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.path, 'w', encoding='utf-8') as f:
            for receipt in receipts:
                f.write(json.dumps(receipt.to_dict()) + '\n')
        
        return len(receipts)
    
    def load(self) -> List[Any]:
        """Load embeddings from JSONL file."""
        if not self.path.exists():
            return []
        
        # Import here to avoid circular dependency
        try:
            from .provenance import ComputationalReceipt
            receipt_class = ComputationalReceipt
        except ImportError:
            receipt_class = EmbeddingReceipt
        
        receipts = []
        with open(self.path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                receipts.append(receipt_class.from_dict(data))
        
        return receipts
    
    def append(self, receipt: Any) -> None:
        """Append single embedding to file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(receipt.to_dict()) + '\n')
