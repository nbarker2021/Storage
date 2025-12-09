"""
CQE Kakeya Analyzer
===================

Geometric shape analysis for embedding clouds using PCA projection
and spherical directional coverage metrics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from .config import CQEMetaConfig, get_config
from .embedding import EmbeddingReceipt


@dataclass
class KakeyaMetrics:
    """Metrics describing embedding cloud geometry."""
    
    n: int  # Number of samples
    K: float  # Directional coverage on S²
    vol_proxy: float  # Volume proxy from singular values
    dimension_estimate: Optional[int] = None  # Estimated intrinsic dimension
    
    def to_dict(self) -> Dict[str, float]:
        """Serialize to dictionary."""
        result = {
            "n": float(self.n),
            "K": self.K,
            "vol_proxy": self.vol_proxy
        }
        if self.dimension_estimate is not None:
            result["dimension_estimate"] = float(self.dimension_estimate)
        return result


class KakeyaAnalyzer:
    """Analyzer for geometric properties of embedding clouds."""
    
    def __init__(self, config: Optional[CQEMetaConfig] = None):
        self.config = config or get_config()
        self.n_az = self.config.kakeya.n_azimuth
        self.n_el = self.config.kakeya.n_elevation
        self.max_pairs = self.config.kakeya.max_pairs
        self.min_samples = self.config.kakeya.min_samples
        self.pca_dim = self.config.kakeya.pca_dimensions
    
    def analyze_embeddings(self, receipts: List[EmbeddingReceipt]) -> KakeyaMetrics:
        """Compute Kakeya metrics for a list of embedding receipts."""
        if not receipts:
            return KakeyaMetrics(n=0, K=0.0, vol_proxy=0.0)
        
        vecs = np.array([r.vec for r in receipts], dtype=float)
        return self.analyze_vectors(vecs)
    
    def analyze_vectors(self, vecs: np.ndarray) -> KakeyaMetrics:
        """Compute Kakeya metrics for raw embedding vectors."""
        n, d = vecs.shape
        
        if n < self.min_samples:
            return KakeyaMetrics(n=n, K=0.0, vol_proxy=0.0, dimension_estimate=0)
        
        # Center and perform SVD
        X = vecs - vecs.mean(axis=0, keepdims=True)
        _, S, Vt = np.linalg.svd(X, full_matrices=False)
        
        # Estimate intrinsic dimension (number of significant singular values)
        dim_estimate = self._estimate_dimension(S)
        
        # Project to top-k PCA directions
        k = min(self.pca_dim, d)
        V_k = Vt[:k].T
        Y = X @ V_k
        
        # Compute volume proxy
        s_norm = S[:k] / max(S[0], 1e-9)
        vol_proxy = float(np.prod(s_norm))
        
        # Compute directional coverage
        K = self._compute_directional_coverage(Y, n)
        
        return KakeyaMetrics(
            n=n,
            K=K,
            vol_proxy=vol_proxy,
            dimension_estimate=dim_estimate
        )
    
    def _estimate_dimension(self, singular_values: np.ndarray, threshold: float = 0.01) -> int:
        """Estimate intrinsic dimension from singular value spectrum."""
        if len(singular_values) == 0:
            return 0
        
        # Normalize
        s_norm = singular_values / singular_values[0]
        
        # Count values above threshold
        significant = np.sum(s_norm > threshold)
        return int(significant)
    
    def _compute_directional_coverage(self, Y: np.ndarray, n: int) -> float:
        """Compute directional coverage on S² from nearest-neighbor directions."""
        dirs = []
        m_pairs = min(self.max_pairs, n - 1)
        
        for i in range(m_pairs):
            j = (i + 1) % n
            diff = Y[j] - Y[i]
            norm_d = float(np.linalg.norm(diff))
            if norm_d < 1e-9:
                continue
            dirs.append(diff / norm_d)
        
        if not dirs:
            return 0.0
        
        dirs_arr = np.stack(dirs, axis=0)
        
        # Pad to 3D if needed
        if dirs_arr.shape[1] < 3:
            padded = np.zeros((dirs_arr.shape[0], 3), dtype=float)
            padded[:, :dirs_arr.shape[1]] = dirs_arr
            dirs_arr = padded
        
        return self._spherical_coverage(dirs_arr)
    
    def _spherical_coverage(self, directions: np.ndarray) -> float:
        """Compute fraction of S² bins covered by direction vectors."""
        if directions.size == 0:
            return 0.0
        
        hits = set()
        for d in directions:
            x, y, z = map(float, d)
            r = float(np.sqrt(x * x + y * y + z * z))
            if r < 1e-9:
                continue
            
            # Normalize to unit sphere
            x /= r
            y /= r
            z /= r
            
            # Compute azimuth and elevation
            az = float(np.arctan2(y, x))
            if az < 0:
                az += 2 * math.pi
            el = float(np.arctan2(z, np.sqrt(x * x + y * y)))
            
            # Bin indices
            az_bin = min(self.n_az - 1, int(az / (2 * math.pi) * self.n_az))
            el_bin = min(self.n_el - 1, int((el + math.pi / 2.0) / math.pi * self.n_el))
            
            hits.add((az_bin, el_bin))
        
        total_bins = self.n_az * self.n_el
        return len(hits) / float(total_bins)
    
    def analyze_clusters(
        self,
        clusters: Dict[str, List[EmbeddingReceipt]]
    ) -> Dict[str, KakeyaMetrics]:
        """Analyze multiple clusters and return metrics for each."""
        results = {}
        for cluster_name, receipts in clusters.items():
            results[cluster_name] = self.analyze_embeddings(receipts)
        return results
    
    def classify_geometry(self, metrics: KakeyaMetrics) -> str:
        """Classify embedding cloud geometry into archetypes."""
        if metrics.n < self.min_samples:
            return "insufficient_samples"
        
        K = metrics.K
        vol = metrics.vol_proxy
        
        # Geometric archetypes
        if K < 0.3:
            if vol < 0.01:
                return "filament"  # Low-dimensional, constrained
            elif vol < 0.3:
                return "needle"  # Constrained chaos
            else:
                return "folded_manifold"  # High-D but directionally constrained
        elif K < 0.5:
            if vol < 0.1:
                return "transition"  # Intermediate regime
            else:
                return "structured_volume"  # Some volumetric filling, structured
        else:  # K >= 0.5
            if vol > 0.3:
                return "ergodic_volume"  # Full space-filling, turbulent-like
            else:
                return "sparse_volume"  # Volumetric but sparse
    
    def compute_similarity(
        self,
        metrics_a: KakeyaMetrics,
        metrics_b: KakeyaMetrics
    ) -> float:
        """Compute geometric similarity between two clouds (0=identical, 1=maximally different)."""
        if metrics_a.n < self.min_samples or metrics_b.n < self.min_samples:
            return 1.0  # Maximally dissimilar
        
        # Weighted distance in (K, log(vol_proxy), log(n)) space
        k_dist = abs(metrics_a.K - metrics_b.K)
        
        vol_a = max(1e-12, metrics_a.vol_proxy)
        vol_b = max(1e-12, metrics_b.vol_proxy)
        vol_dist = abs(math.log10(vol_a) - math.log10(vol_b)) / 12.0  # Normalize by typical range
        
        n_dist = abs(math.log10(metrics_a.n) - math.log10(metrics_b.n)) / 3.0  # Normalize
        
        # Weighted combination
        distance = 0.5 * k_dist + 0.3 * vol_dist + 0.2 * n_dist
        return min(1.0, distance)
