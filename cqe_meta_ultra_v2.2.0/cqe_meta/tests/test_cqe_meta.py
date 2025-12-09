#!/usr/bin/env python3
"""
CQE Meta Test Suite
===================

Comprehensive tests for the refactored CQE meta-infrastructure.
"""

import sys
import tempfile
from pathlib import Path

import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cqe_meta import (
    CQEMetaConfig,
    EmbeddingPipeline,
    EmbeddingReceipt,
    EmbeddingStore,
    KakeyaAnalyzer,
    MetaWorldController,
    MockValidator,
    PathConfig,
)


class TestRunner:
    """Simple test runner with result tracking."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name):
        def decorator(func):
            self.tests.append((name, func))
            return func
        return decorator
    
    def run(self):
        print("\n" + "="*70)
        print("CQE META-INFRASTRUCTURE TEST SUITE (Refactored)")
        print("="*70 + "\n")
        
        for name, func in self.tests:
            try:
                print(f"Testing: {name}...", end=" ")
                func()
                print("✓ PASS")
                self.passed += 1
            except AssertionError as e:
                print(f"✗ FAIL: {e}")
                self.failed += 1
            except Exception as e:
                print(f"✗ ERROR: {e}")
                self.failed += 1
        
        print("\n" + "="*70)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("="*70 + "\n")
        
        return self.failed == 0


runner = TestRunner()


# ========== Configuration Tests ==========

@runner.test("PathConfig resolves paths correctly")
def test_path_config():
    config = PathConfig(base_dir=Path("/test"), cqe_production_dir="CQE_v2")
    assert config.base_dir == Path("/test")
    assert config.sandbox_root == Path("/test/sandbox")
    assert config.cqe_root == Path("/test/sandbox/CQE_v2")


@runner.test("CQEMetaConfig from environment")
def test_config_from_env():
    config = CQEMetaConfig.from_env()
    assert config.paths.base_dir is not None
    assert config.embedding.schema_version == "2.1.0"


@runner.test("CQEMetaConfig to/from dict")
def test_config_serialization():
    config = CQEMetaConfig()
    config_dict = config.to_dict()
    assert "paths" in config_dict
    assert "embedding" in config_dict
    
    config2 = CQEMetaConfig.from_dict(config_dict)
    assert config2.embedding.schema_version == config.embedding.schema_version


# ========== Embedding Pipeline Tests ==========

@runner.test("EmbeddingReceipt serialization")
def test_embedding_receipt():
    receipt = EmbeddingReceipt(
        world="TEST",
        vec=[1.0, 2.0, 3.0],
        vec_dim=3,
        lane_feat=[0.7, 0.1, 0.8, 0.0],
        cqe_channel=7,
        delta_phi=0.1,
        rho_like=0.8,
        scope=False,
        schema_version="2.1.0",
        timestamp="2025-11-18T00:00:00Z"
    )
    
    # Serialize/deserialize
    data = receipt.to_dict()
    assert data["world"] == "TEST"
    assert data["schema_version"] == "2.1.0"
    
    receipt2 = EmbeddingReceipt.from_dict(data)
    assert receipt2.world == receipt.world
    assert receipt2.vec == receipt.vec


@runner.test("EmbeddingPipeline generates valid embeddings")
def test_embedding_pipeline():
    config = CQEMetaConfig()
    pipeline = EmbeddingPipeline(config)
    
    state = np.random.randn(8) * np.sqrt(2.0)
    receipt = pipeline.embed_state_vector(
        world="TEST",
        state_vector=state,
        channel=7,
        scope=False,
        sample_index=0
    )
    
    assert receipt.world == "TEST"
    assert len(receipt.vec) > 0
    assert receipt.cqe_channel == 7
    assert receipt.schema_version == "2.1.0"


@runner.test("EmbeddingStore save/load cycle")
def test_embedding_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test_embeddings.jsonl"
        store = EmbeddingStore(path)
        
        # Create test receipts
        receipts = []
        for i in range(5):
            receipt = EmbeddingReceipt(
                world="TEST",
                vec=[float(i), float(i+1)],
                vec_dim=2,
                lane_feat=[0.7, 0.0, 0.5, 0.0],
                cqe_channel=7,
                delta_phi=0.0,
                rho_like=0.5,
                scope=False,
                schema_version="2.1.0",
                timestamp="2025-11-18T00:00:00Z",
                sample_index=i
            )
            receipts.append(receipt)
        
        # Save
        n_saved = store.save(receipts)
        assert n_saved == 5
        
        # Load
        loaded = store.load()
        assert len(loaded) == 5
        assert loaded[0].sample_index == 0
        assert loaded[4].sample_index == 4


# ========== Kakeya Analyzer Tests ==========

@runner.test("KakeyaAnalyzer detects linear manifold")
def test_kakeya_linear():
    config = CQEMetaConfig()
    analyzer = KakeyaAnalyzer(config)
    
    # Create 1D line in 50D space
    n_samples = 50
    t = np.linspace(0, 2*np.pi, n_samples)
    vecs = np.zeros((n_samples, 50))
    vecs[:, 0] = np.cos(t)
    vecs[:, 1] = np.sin(t)
    
    metrics = analyzer.analyze_vectors(vecs)
    assert metrics.n == 50
    assert metrics.K < 0.5, f"Linear manifold should have low K: {metrics.K}"
    assert metrics.vol_proxy < 0.01, f"Linear manifold should have low vol_proxy: {metrics.vol_proxy}"


@runner.test("KakeyaAnalyzer classifies geometry types")
def test_kakeya_classification():
    config = CQEMetaConfig()
    analyzer = KakeyaAnalyzer(config)
    
    # Linear manifold
    vecs_linear = np.zeros((50, 50))
    vecs_linear[:, 0] = np.linspace(0, 1, 50)
    metrics_linear = analyzer.analyze_vectors(vecs_linear)
    geometry = analyzer.classify_geometry(metrics_linear)
    assert geometry in ("filament", "needle"), f"Got {geometry}"
    
    # Volumetric
    vecs_vol = np.random.randn(50, 50)
    metrics_vol = analyzer.analyze_vectors(vecs_vol)
    geometry_vol = analyzer.classify_geometry(metrics_vol)
    assert geometry_vol in ("ergodic_volume", "sparse_volume", "structured_volume"), f"Got {geometry_vol}"


@runner.test("KakeyaAnalyzer computes similarity")
def test_kakeya_similarity():
    config = CQEMetaConfig()
    analyzer = KakeyaAnalyzer(config)
    
    vecs1 = np.random.randn(50, 50)
    vecs2 = np.random.randn(50, 50)
    
    metrics1 = analyzer.analyze_vectors(vecs1)
    metrics2 = analyzer.analyze_vectors(vecs2)
    
    # Self-similarity should be low
    self_sim = analyzer.compute_similarity(metrics1, metrics1)
    assert self_sim < 0.1, f"Self-similarity should be near 0, got {self_sim}"
    
    # Different clouds should have non-zero similarity
    diff_sim = analyzer.compute_similarity(metrics1, metrics2)
    assert 0 <= diff_sim <= 1.0


# ========== Validator Tests ==========

@runner.test("MockValidator generates samples")
def test_mock_validator():
    validator = MockValidator(dimension=8, n_samples=100)
    samples = validator.generate_samples(50)
    
    assert samples.shape == (50, 8)
    assert not np.all(samples == 0)


# ========== Controller Tests ==========

@runner.test("MetaWorldController registers worlds")
def test_controller_registration():
    controller = MetaWorldController()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        embed_path = Path(tmpdir) / "test.jsonl"
        
        controller.register_world(
            world_id="TEST",
            name="Test World",
            description="Testing",
            embedding_path=embed_path,
            cqe_channel=7
        )
        
        assert "TEST" in controller.worlds
        assert controller.worlds["TEST"].world_id == "TEST"


@runner.test("MetaWorldController analyzes worlds")
def test_controller_analysis():
    controller = MetaWorldController()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test embeddings
        embed_path = Path(tmpdir) / "test.jsonl"
        store = EmbeddingStore(embed_path)
        
        receipts = []
        for i in range(20):
            vec = np.random.randn(50).tolist()
            receipt = EmbeddingReceipt(
                world="TEST",
                vec=vec,
                vec_dim=50,
                lane_feat=[0.7, 0.0, 0.5, 0.0],
                cqe_channel=7,
                delta_phi=0.0,
                rho_like=0.5,
                scope=False,
                schema_version="2.1.0",
                timestamp="2025-11-18T00:00:00Z"
            )
            receipts.append(receipt)
        
        store.save(receipts)
        
        # Register and analyze
        controller.register_world(
            world_id="TEST",
            name="Test",
            description="Test",
            embedding_path=embed_path,
            cqe_channel=7
        )
        
        metrics = controller.analyze_world("TEST")
        assert "all" in metrics
        assert metrics["all"].n == 20


@runner.test("MetaWorldController finds similar clusters")
def test_controller_similarity():
    controller = MetaWorldController()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create two test worlds
        for world_id in ["WORLD_A", "WORLD_B"]:
            embed_path = Path(tmpdir) / f"{world_id}.jsonl"
            store = EmbeddingStore(embed_path)
            
            receipts = []
            for i in range(15):
                vec = np.random.randn(50).tolist()
                receipt = EmbeddingReceipt(
                    world=world_id,
                    vec=vec,
                    vec_dim=50,
                    lane_feat=[0.7, 0.0, 0.5, 0.0],
                    cqe_channel=7,
                    delta_phi=0.0,
                    rho_like=0.5,
                    scope=False,
                    schema_version="2.1.0",
                    timestamp="2025-11-18T00:00:00Z"
                )
                receipts.append(receipt)
            
            store.save(receipts)
            
            controller.register_world(
                world_id=world_id,
                name=world_id,
                description="Test",
                embedding_path=embed_path,
                cqe_channel=7
            )
        
        # Find similar
        similar = controller.find_similar_clusters("WORLD_A", "all", ["WORLD_B"])
        assert len(similar) > 0
        assert similar[0][0] == "WORLD_B"


@runner.test("MetaWorldController generates curriculum")
def test_controller_curriculum():
    controller = MetaWorldController()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test worlds with different complexities
        for i, world_id in enumerate(["EASY", "MEDIUM", "HARD"]):
            embed_path = Path(tmpdir) / f"{world_id}.jsonl"
            store = EmbeddingStore(embed_path)
            
            receipts = []
            # More complex = higher dimensional spread
            complexity = (i + 1) * 5
            
            for j in range(20):
                vec = np.random.randn(complexity).tolist()
                receipt = EmbeddingReceipt(
                    world=world_id,
                    vec=vec,
                    vec_dim=complexity,
                    lane_feat=[0.7, 0.0, 0.5, 0.0],
                    cqe_channel=7,
                    delta_phi=0.0,
                    rho_like=0.5,
                    scope=False,
                    schema_version="2.1.0",
                    timestamp="2025-11-18T00:00:00Z"
                )
                receipts.append(receipt)
            
            store.save(receipts)
            
            controller.register_world(
                world_id=world_id,
                name=world_id,
                description="Test",
                embedding_path=embed_path,
                cqe_channel=7
            )
        
        # Generate curriculum
        curriculum = controller.generate_curriculum(difficulty_metric="K", ascending=True)
        assert len(curriculum) == 3


if __name__ == "__main__":
    success = runner.run()
    sys.exit(0 if success else 1)
