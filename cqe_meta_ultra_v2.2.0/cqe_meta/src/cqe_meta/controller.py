"""
CQE MetaWorld Controller
=========================

Central orchestrator for cross-world embedding analysis, similarity queries,
and geometric discovery across CQE physics validators.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .config import CQEMetaConfig, get_config
from .embedding import EmbeddingPipeline, EmbeddingReceipt, EmbeddingStore
from .kakeya import KakeyaAnalyzer, KakeyaMetrics
from .validators import YangMillsValidatorAdapter, RiemannValidatorAdapter


@dataclass
class WorldDescriptor:
    """Metadata describing a physics world."""
    
    world_id: str
    name: str
    description: str
    embedding_path: Path
    cqe_channel: int
    validator_type: Optional[str] = None


class ClusterManager:
    """Manages clustering logic for different worlds."""
    
    def __init__(self, config: Optional[CQEMetaConfig] = None):
        self.config = config or get_config()
    
    def cluster_by_metadata(
        self,
        receipts: List[EmbeddingReceipt],
        metadata_key: str,
        thresholds: Optional[Dict[str, Tuple[Optional[float], Optional[float]]]] = None
    ) -> Dict[str, List[EmbeddingReceipt]]:
        """Cluster receipts by a metadata field with optional thresholds."""
        if thresholds is None:
            # Group by exact value
            clusters: Dict[str, List[EmbeddingReceipt]] = {}
            for receipt in receipts:
                value = receipt.metadata.get(metadata_key, "unknown")
                key = str(value)
                clusters.setdefault(key, []).append(receipt)
            return clusters
        
        # Group by threshold bands
        clusters = {}
        for receipt in receipts:
            value = float(receipt.metadata.get(metadata_key, 0.0))
            
            # Find matching threshold band
            matched = False
            for band_name, (low, high) in thresholds.items():
                if low is not None and value < low:
                    continue
                if high is not None and value >= high:
                    continue
                clusters.setdefault(band_name, []).append(receipt)
                matched = True
                break
            
            if not matched:
                clusters.setdefault("other", []).append(receipt)
        
        return clusters
    
    def cluster_pendulum(self, receipts: List[EmbeddingReceipt]) -> Dict[str, List[EmbeddingReceipt]]:
        """Cluster pendulum embeddings by rho3."""
        thresholds = {
            "P_rho_low": (None, self.config.embedding.pendulum_rho_low_threshold),
            "P_rho_mid": (
                self.config.embedding.pendulum_rho_low_threshold,
                self.config.embedding.pendulum_rho_high_threshold
            ),
            "P_rho_high": (self.config.embedding.pendulum_rho_high_threshold, None),
        }
        return self.cluster_by_metadata(receipts, "rho3", thresholds)
    
    def cluster_ns(self, receipts: List[EmbeddingReceipt]) -> Dict[str, List[EmbeddingReceipt]]:
        """Cluster Navier-Stokes embeddings by viscosity."""
        smooth_thresh = self.config.embedding.ns_viscosity_smooth_threshold
        turb_thresh = self.config.embedding.ns_viscosity_turbulent_threshold
        
        smooth = []
        turbulent = []
        
        for receipt in receipts:
            visc = float(receipt.metadata.get("viscosity", 0.0))
            if visc >= smooth_thresh:
                smooth.append(receipt)
            elif visc <= turb_thresh:
                turbulent.append(receipt)
        
        return {"NS_smooth": smooth, "NS_turbulent": turbulent}
    
    def cluster_ym(self, receipts: List[EmbeddingReceipt]) -> Dict[str, List[EmbeddingReceipt]]:
        """Yang-Mills as single cluster."""
        return {"YM_all": receipts}
    
    def cluster_riemann(self, receipts: List[EmbeddingReceipt]) -> Dict[str, List[EmbeddingReceipt]]:
        """Cluster Riemann by label (e8_root, laplacian_row)."""
        return self.cluster_by_metadata(receipts, "label")


class MetaWorldController:
    """Central controller for cross-world geometric analysis."""
    
    def __init__(self, config: Optional[CQEMetaConfig] = None):
        self.config = config or get_config()
        self.pipeline = EmbeddingPipeline(config)
        self.kakeya = KakeyaAnalyzer(config)
        self.cluster_manager = ClusterManager(config)
        
        # World registry
        self.worlds: Dict[str, WorldDescriptor] = {}
        self._world_embeddings: Dict[str, List[EmbeddingReceipt]] = {}
        self._world_metrics: Dict[str, Dict[str, KakeyaMetrics]] = {}
    
    def register_world(
        self,
        world_id: str,
        name: str,
        description: str,
        embedding_path: Path,
        cqe_channel: int,
        validator_type: Optional[str] = None
    ) -> None:
        """Register a physics world for analysis."""
        self.worlds[world_id] = WorldDescriptor(
            world_id=world_id,
            name=name,
            description=description,
            embedding_path=embedding_path,
            cqe_channel=cqe_channel,
            validator_type=validator_type
        )
    
    def load_world(self, world_id: str) -> List[EmbeddingReceipt]:
        """Load embeddings for a world."""
        if world_id not in self.worlds:
            raise ValueError(f"Unknown world: {world_id}")
        
        if world_id in self._world_embeddings:
            return self._world_embeddings[world_id]
        
        world = self.worlds[world_id]
        store = EmbeddingStore(world.embedding_path, self.config)
        receipts = store.load()
        
        self._world_embeddings[world_id] = receipts
        return receipts
    
    def analyze_world(self, world_id: str) -> Dict[str, KakeyaMetrics]:
        """Analyze a world and return per-cluster metrics."""
        if world_id in self._world_metrics:
            return self._world_metrics[world_id]
        
        receipts = self.load_world(world_id)
        
        # Cluster based on world type
        if world_id == "PEND":
            clusters = self.cluster_manager.cluster_pendulum(receipts)
        elif world_id == "NS":
            clusters = self.cluster_manager.cluster_ns(receipts)
        elif world_id == "YM":
            clusters = self.cluster_manager.cluster_ym(receipts)
        elif world_id == "RIEMANN":
            clusters = self.cluster_manager.cluster_riemann(receipts)
        else:
            clusters = {"all": receipts}
        
        # Analyze each cluster
        metrics = self.kakeya.analyze_clusters(clusters)
        self._world_metrics[world_id] = metrics
        return metrics
    
    def get_world_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all registered worlds."""
        summary = {}
        for world_id in self.worlds:
            metrics = self.analyze_world(world_id)
            summary[world_id] = {
                "name": self.worlds[world_id].name,
                "n_embeddings": len(self.load_world(world_id)),
                "clusters": {
                    cluster_name: {
                        "n": m.n,
                        "K": m.K,
                        "vol_proxy": m.vol_proxy,
                        "geometry": self.kakeya.classify_geometry(m)
                    }
                    for cluster_name, m in metrics.items()
                }
            }
        return summary
    
    def find_similar_clusters(
        self,
        query_world: str,
        query_cluster: str,
        target_worlds: Optional[List[str]] = None,
        max_results: int = 5
    ) -> List[Tuple[str, str, float, str]]:
        """Find clusters geometrically similar to query cluster.
        
        Returns:
            List of (world_id, cluster_name, similarity_distance, geometry_type)
        """
        # Get query metrics
        query_metrics_dict = self.analyze_world(query_world)
        if query_cluster not in query_metrics_dict:
            raise ValueError(f"Unknown cluster {query_cluster} in world {query_world}")
        
        query_metrics = query_metrics_dict[query_cluster]
        
        # Search across target worlds
        if target_worlds is None:
            target_worlds = [w for w in self.worlds if w != query_world]
        
        results = []
        for world_id in target_worlds:
            world_metrics = self.analyze_world(world_id)
            for cluster_name, metrics in world_metrics.items():
                distance = self.kakeya.compute_similarity(query_metrics, metrics)
                geometry = self.kakeya.classify_geometry(metrics)
                results.append((world_id, cluster_name, distance, geometry))
        
        # Sort by similarity (lower distance = more similar)
        results.sort(key=lambda x: x[2])
        return results[:max_results]
    
    def query_by_geometry(
        self,
        geometry_type: str,
        worlds: Optional[List[str]] = None
    ) -> List[Tuple[str, str, KakeyaMetrics]]:
        """Find all clusters matching a geometry type."""
        if worlds is None:
            worlds = list(self.worlds.keys())
        
        matches = []
        for world_id in worlds:
            world_metrics = self.analyze_world(world_id)
            for cluster_name, metrics in world_metrics.items():
                if self.kakeya.classify_geometry(metrics) == geometry_type:
                    matches.append((world_id, cluster_name, metrics))
        
        return matches
    
    def compute_distance_matrix(self, worlds: Optional[List[str]] = None) -> np.ndarray:
        """Compute pairwise similarity matrix between all clusters."""
        if worlds is None:
            worlds = list(self.worlds.keys())
        
        # Collect all cluster metrics
        all_metrics = []
        labels = []
        
        for world_id in worlds:
            world_metrics = self.analyze_world(world_id)
            for cluster_name, metrics in world_metrics.items():
                all_metrics.append(metrics)
                labels.append(f"{world_id}/{cluster_name}")
        
        # Compute pairwise distances
        n = len(all_metrics)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                dist = self.kakeya.compute_similarity(all_metrics[i], all_metrics[j])
                matrix[i, j] = dist
                matrix[j, i] = dist
        
        return matrix, labels
    
    def generate_curriculum(
        self,
        difficulty_metric: str = "K",
        ascending: bool = True
    ) -> List[Tuple[str, str, float]]:
        """Generate ordered curriculum by geometric complexity.
        
        Args:
            difficulty_metric: "K" (directional) or "vol_proxy" (volumetric)
            ascending: True for easy->hard, False for hard->easy
        
        Returns:
            List of (world_id, cluster_name, difficulty_score)
        """
        curriculum = []
        
        for world_id in self.worlds:
            world_metrics = self.analyze_world(world_id)
            for cluster_name, metrics in world_metrics.items():
                if difficulty_metric == "K":
                    score = metrics.K
                elif difficulty_metric == "vol_proxy":
                    score = metrics.vol_proxy
                else:
                    raise ValueError(f"Unknown difficulty metric: {difficulty_metric}")
                
                curriculum.append((world_id, cluster_name, score))
        
        curriculum.sort(key=lambda x: x[2], reverse=not ascending)
        return curriculum
