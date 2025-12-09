"""
CQE Meta - Async Controller with Similarity Indices
===================================================

High-performance async controller with pre-computed similarity matrices
and cached analysis results.
"""

from __future__ import annotations

import asyncio
import pickle
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from .config import CQEMetaConfig, get_config
from .controller import ClusterManager, MetaWorldController, WorldDescriptor
from .kakeya import KakeyaAnalyzer, KakeyaMetrics
from .provenance import ComputationalReceipt


class SimilarityIndex:
    """Pre-computed similarity index for fast queries."""
    
    def __init__(self):
        self.distance_matrix: Optional[np.ndarray] = None
        self.labels: List[str] = []
        self.label_to_idx: Dict[str, int] = {}
        self.metrics_cache: Dict[str, KakeyaMetrics] = {}
    
    def build(
        self,
        world_clusters: Dict[str, Dict[str, List[ComputationalReceipt]]],
        analyzer: KakeyaAnalyzer
    ) -> None:
        """Build similarity index from world clusters."""
        
        # Collect all metrics
        all_metrics = []
        self.labels = []
        
        for world_id, clusters in world_clusters.items():
            for cluster_name, receipts in clusters.items():
                metrics = analyzer.analyze_embeddings(receipts)
                label = f"{world_id}/{cluster_name}"
                
                all_metrics.append(metrics)
                self.labels.append(label)
                self.label_to_idx[label] = len(self.labels) - 1
                self.metrics_cache[label] = metrics
        
        # Compute pairwise distances
        n = len(all_metrics)
        self.distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                dist = analyzer.compute_similarity(all_metrics[i], all_metrics[j])
                self.distance_matrix[i, j] = dist
                self.distance_matrix[j, i] = dist
    
    def query_similar(self, label: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find top-k most similar clusters to query label."""
        if label not in self.label_to_idx:
            return []
        
        idx = self.label_to_idx[label]
        distances = self.distance_matrix[idx]
        
        # Sort by distance (excluding self)
        sorted_indices = np.argsort(distances)
        results = []
        
        for i in sorted_indices:
            if i == idx:
                continue
            results.append((self.labels[i], distances[i]))
            if len(results) >= top_k:
                break
        
        return results
    
    def save(self, path: Path) -> None:
        """Save index to disk."""
        with open(path, 'wb') as f:
            pickle.dump({
                'distance_matrix': self.distance_matrix,
                'labels': self.labels,
                'label_to_idx': self.label_to_idx,
                'metrics_cache': self.metrics_cache
            }, f)
    
    def load(self, path: Path) -> None:
        """Load index from disk."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.distance_matrix = data['distance_matrix']
            self.labels = data['labels']
            self.label_to_idx = data['label_to_idx']
            self.metrics_cache = data['metrics_cache']


class AsyncMetaWorldController:
    """Async version of MetaWorldController with caching and parallel processing."""
    
    def __init__(self, config: Optional[CQEMetaConfig] = None, n_workers: int = 4):
        self.config = config or get_config()
        self.kakeya = KakeyaAnalyzer(config)
        self.cluster_manager = ClusterManager(config)
        
        self.worlds: Dict[str, WorldDescriptor] = {}
        self._world_embeddings: Dict[str, List[ComputationalReceipt]] = {}
        self._world_metrics: Dict[str, Dict[str, KakeyaMetrics]] = {}
        
        # Async components
        self.executor = ThreadPoolExecutor(max_workers=n_workers)
        self.similarity_index: Optional[SimilarityIndex] = None
        self._index_dirty = True
    
    def register_world(
        self,
        world_id: str,
        name: str,
        description: str,
        embedding_path: Path,
        cqe_channel: int,
        validator_type: Optional[str] = None
    ) -> None:
        """Register a world (marks index as dirty)."""
        self.worlds[world_id] = WorldDescriptor(
            world_id=world_id,
            name=name,
            description=description,
            embedding_path=embedding_path,
            cqe_channel=cqe_channel,
            validator_type=validator_type
        )
        self._index_dirty = True
    
    async def load_world_async(self, world_id: str) -> List[ComputationalReceipt]:
        """Asynchronously load world embeddings."""
        if world_id in self._world_embeddings:
            return self._world_embeddings[world_id]
        
        loop = asyncio.get_event_loop()
        receipts = await loop.run_in_executor(
            self.executor,
            self._load_world_sync,
            world_id
        )
        
        self._world_embeddings[world_id] = receipts
        return receipts
    
    def _load_world_sync(self, world_id: str) -> List[ComputationalReceipt]:
        """Synchronous world loading (for executor)."""
        from .embedding import EmbeddingStore
        
        world = self.worlds[world_id]
        store = EmbeddingStore(world.embedding_path, self.config)
        return store.load()
    
    async def analyze_world_async(self, world_id: str) -> Dict[str, KakeyaMetrics]:
        """Asynchronously analyze a world."""
        if world_id in self._world_metrics:
            return self._world_metrics[world_id]
        
        receipts = await self.load_world_async(world_id)
        
        loop = asyncio.get_event_loop()
        metrics = await loop.run_in_executor(
            self.executor,
            self._analyze_clusters_sync,
            world_id,
            receipts
        )
        
        self._world_metrics[world_id] = metrics
        return metrics
    
    def _analyze_clusters_sync(
        self,
        world_id: str,
        receipts: List[ComputationalReceipt]
    ) -> Dict[str, KakeyaMetrics]:
        """Synchronous cluster analysis (for executor)."""
        
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
        
        return self.kakeya.analyze_clusters(clusters)
    
    async def analyze_all_worlds_async(self) -> Dict[str, Dict[str, KakeyaMetrics]]:
        """Analyze all registered worlds in parallel."""
        tasks = [self.analyze_world_async(world_id) for world_id in self.worlds]
        results = await asyncio.gather(*tasks)
        
        return {
            world_id: metrics
            for world_id, metrics in zip(self.worlds.keys(), results)
        }
    
    async def build_similarity_index_async(self) -> None:
        """Build similarity index from all worlds."""
        if not self._index_dirty and self.similarity_index is not None:
            return
        
        # Load all world clusters
        world_clusters = {}
        for world_id in self.worlds:
            receipts = await self.load_world_async(world_id)
            
            # Cluster
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
            
            world_clusters[world_id] = clusters
        
        # Build index
        loop = asyncio.get_event_loop()
        index = SimilarityIndex()
        await loop.run_in_executor(
            self.executor,
            index.build,
            world_clusters,
            self.kakeya
        )
        
        self.similarity_index = index
        self._index_dirty = False
    
    async def find_similar_fast(
        self,
        query_world: str,
        query_cluster: str,
        top_k: int = 5
    ) -> List[Tuple[str, str, float]]:
        """Fast similarity query using pre-computed index."""
        
        # Ensure index is built
        await self.build_similarity_index_async()
        
        if self.similarity_index is None:
            return []
        
        label = f"{query_world}/{query_cluster}"
        similar = self.similarity_index.query_similar(label, top_k)
        
        # Parse labels back into (world, cluster, distance)
        results = []
        for sim_label, distance in similar:
            parts = sim_label.split('/', 1)
            if len(parts) == 2:
                results.append((parts[0], parts[1], distance))
        
        return results
    
    def close(self) -> None:
        """Shutdown executor."""
        self.executor.shutdown(wait=True)


# Convenience function for async usage
def run_async(coro):
    """Run async coroutine in event loop."""
    return asyncio.run(coro)
