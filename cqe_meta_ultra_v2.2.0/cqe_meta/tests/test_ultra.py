#!/usr/bin/env python3
"""
CQE Meta ULTRA Test Suite
==========================

Comprehensive validation of all uber-aggressive features:
- Provenance tracking with cryptographic verification
- Vectorized batch processing
- Async parallel analysis
- Streaming writers
- Similarity indices
"""

import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np

from cqe_meta import (
    AsyncMetaWorldController,
    ComputationalReceipt,
    EmbeddingStore,
    MockValidator,
    ProvenanceEmbeddingPipeline,
    StreamingEmbeddingWriter,
    VectorizedBatchEngine,
    run_async,
)


class TestRunner:
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
        print("CQE META ULTRA TEST SUITE")
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
                import traceback
                traceback.print_exc()
                self.failed += 1
        
        print("\n" + "="*70)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("="*70 + "\n")
        
        return self.failed == 0


runner = TestRunner()


# ========== Provenance Tests ==========

@runner.test("Provenance: Cryptographic verification")
def test_cryptographic_verification():
    pipeline = ProvenanceEmbeddingPipeline(validator_signature="test_v1.0.0")
    
    state = np.random.randn(8)
    receipt = pipeline.embed_with_provenance(
        world="TEST",
        state_vector=state,
        channel=7,
        scope=False
    )
    
    # Verify integrity
    assert receipt.provenance is not None
    assert receipt.verify_integrity(), "Integrity check should pass"
    
    # Tamper with data
    receipt.vec[0] += 1.0
    assert not receipt.verify_integrity(), "Integrity check should fail after tampering"


@runner.test("Provenance: Git commit tracking")
def test_git_commit():
    pipeline = ProvenanceEmbeddingPipeline()
    
    state = np.random.randn(8)
    receipt = pipeline.embed_with_provenance(
        world="TEST",
        state_vector=state,
        channel=7,
        scope=False
    )
    
    assert receipt.provenance.git_commit is not None
    assert len(receipt.provenance.git_commit) > 0


@runner.test("Provenance: Execution environment capture")
def test_execution_environment():
    pipeline = ProvenanceEmbeddingPipeline()
    
    state = np.random.randn(8)
    receipt = pipeline.embed_with_provenance(
        world="TEST",
        state_vector=state,
        channel=7,
        scope=False
    )
    
    env = receipt.provenance.execution_environment
    assert "python_version" in env
    assert "numpy_version" in env
    assert "platform" in env


@runner.test("Provenance: Computation time tracking")
def test_computation_time():
    pipeline = ProvenanceEmbeddingPipeline()
    
    state = np.random.randn(8)
    receipt = pipeline.embed_with_provenance(
        world="TEST",
        state_vector=state,
        channel=7,
        scope=False
    )
    
    assert receipt.provenance.computation_time_ms is not None
    assert receipt.provenance.computation_time_ms > 0


@runner.test("Provenance: Parent computation lineage")
def test_lineage_tracking():
    pipeline = ProvenanceEmbeddingPipeline()
    pipeline.set_parent_computations(["parent_1", "parent_2"])
    
    state = np.random.randn(8)
    receipt = pipeline.embed_with_provenance(
        world="TEST",
        state_vector=state,
        channel=7,
        scope=False
    )
    
    assert len(receipt.provenance.parent_computation_ids) == 2
    assert "parent_1" in receipt.provenance.parent_computation_ids


@runner.test("Provenance: SpeedLight linking")
def test_speedlight_linking():
    pipeline = ProvenanceEmbeddingPipeline()
    
    state = np.random.randn(8)
    receipt = pipeline.embed_with_provenance(
        world="TEST",
        state_vector=state,
        channel=7,
        scope=False
    )
    
    # Link to mock SpeedLight receipt
    receipt.link_to_speedlight("speedlight_receipt_42", "ledger_entry_100")
    
    assert receipt.provenance.speedlight_receipt_id == "speedlight_receipt_42"
    assert receipt.provenance.cqe_ledger_entry == "ledger_entry_100"


# ========== Batch Processing Tests ==========

@runner.test("Batch: Vectorized embedding generation")
def test_vectorized_batch():
    engine = VectorizedBatchEngine()
    
    # Generate batch
    validator = MockValidator(dimension=8)
    samples = validator.generate_samples(100)
    
    start = time.time()
    receipts = engine.embed_batch_vectorized(
        world="BATCH_TEST",
        state_vectors=samples,
        channel=7,
        scope=False
    )
    elapsed = time.time() - start
    
    assert len(receipts) == 100
    assert all(r.world == "BATCH_TEST" for r in receipts)
    print(f" ({len(receipts)/elapsed:.0f} embeddings/sec)", end="")


@runner.test("Batch: Parallel processing")
def test_parallel_batch():
    engine = VectorizedBatchEngine()
    
    validator = MockValidator(dimension=8)
    samples = validator.generate_samples(50)
    
    start = time.time()
    receipts = engine.embed_batch_parallel(
        world="PARALLEL_TEST",
        state_vectors=samples,
        channel=7,
        scope=False,
        n_workers=4
    )
    elapsed = time.time() - start
    
    assert len(receipts) == 50
    print(f" ({len(receipts)/elapsed:.0f} embeddings/sec)", end="")


@runner.test("Batch: Streaming buffered writer")
def test_streaming_writer():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "stream.jsonl"
        
        with StreamingEmbeddingWriter(output_path, buffer_size=10) as writer:
            pipeline = ProvenanceEmbeddingPipeline()
            
            # Write 25 receipts (should trigger 2 flushes + final)
            for i in range(25):
                state = np.random.randn(8)
                receipt = pipeline.embed_with_provenance(
                    world="STREAM",
                    state_vector=state,
                    channel=7,
                    scope=False,
                    sample_index=i
                )
                writer.write(receipt)
            
            assert writer.total_written == 20  # 2 flushes of 10
        
        # After close, all should be written
        store = EmbeddingStore(output_path)
        loaded = store.load()
        assert len(loaded) == 25


# ========== Async Controller Tests ==========

@runner.test("Async: Parallel world loading")
def test_async_loading():
    async def test():
        controller = AsyncMetaWorldController(n_workers=4)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create 3 worlds
            for i in range(3):
                world_id = f"ASYNC_WORLD_{i}"
                path = Path(tmpdir) / f"{world_id}.jsonl"
                
                # Create embeddings
                pipeline = ProvenanceEmbeddingPipeline()
                receipts = []
                for j in range(10):
                    state = np.random.randn(8)
                    receipt = pipeline.embed_with_provenance(
                        world=world_id,
                        state_vector=state,
                        channel=7,
                        scope=False
                    )
                    receipts.append(receipt)
                
                store = EmbeddingStore(path)
                store.save(receipts)
                
                controller.register_world(
                    world_id=world_id,
                    name=f"World {i}",
                    description="Test",
                    embedding_path=path,
                    cqe_channel=7
                )
            
            # Load all worlds in parallel
            start = time.time()
            results = await controller.analyze_all_worlds_async()
            elapsed = time.time() - start
            
            assert len(results) == 3
            print(f" ({elapsed*1000:.1f}ms for 3 worlds)", end="")
        
        controller.close()
    
    run_async(test())


@runner.test("Async: Similarity index building")
def test_similarity_index():
    async def test():
        controller = AsyncMetaWorldController()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create 2 worlds
            for i in range(2):
                world_id = f"INDEX_WORLD_{i}"
                path = Path(tmpdir) / f"{world_id}.jsonl"
                
                pipeline = ProvenanceEmbeddingPipeline()
                receipts = []
                for j in range(15):
                    state = np.random.randn(8)
                    receipt = pipeline.embed_with_provenance(
                        world=world_id,
                        state_vector=state,
                        channel=7,
                        scope=False
                    )
                    receipts.append(receipt)
                
                store = EmbeddingStore(path)
                store.save(receipts)
                
                controller.register_world(
                    world_id=world_id,
                    name=f"World {i}",
                    description="Test",
                    embedding_path=path,
                    cqe_channel=7
                )
            
            # Build index
            await controller.build_similarity_index_async()
            
            assert controller.similarity_index is not None
            assert len(controller.similarity_index.labels) == 2
        
        controller.close()
    
    run_async(test())


@runner.test("Async: Fast similarity queries")
def test_fast_queries():
    async def test():
        controller = AsyncMetaWorldController()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create worlds
            for i in range(3):
                world_id = f"QUERY_WORLD_{i}"
                path = Path(tmpdir) / f"{world_id}.jsonl"
                
                pipeline = ProvenanceEmbeddingPipeline()
                receipts = []
                for j in range(10):
                    state = np.random.randn(8)
                    receipt = pipeline.embed_with_provenance(
                        world=world_id,
                        state_vector=state,
                        channel=7,
                        scope=False
                    )
                    receipts.append(receipt)
                
                store = EmbeddingStore(path)
                store.save(receipts)
                
                controller.register_world(
                    world_id=world_id,
                    name=f"World {i}",
                    description="Test",
                    embedding_path=path,
                    cqe_channel=7
                )
            
            # Query with index
            start = time.time()
            similar = await controller.find_similar_fast("QUERY_WORLD_0", "all", top_k=2)
            elapsed = time.time() - start
            
            assert len(similar) <= 2
            print(f" ({elapsed*1000:.2f}ms query time)", end="")
        
        controller.close()
    
    run_async(test())


# ========== Integration Tests ==========

@runner.test("Integration: End-to-end pipeline")
def test_end_to_end():
    async def test():
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Generate batch with provenance
            engine = VectorizedBatchEngine()
            validator = MockValidator(dimension=8)
            samples = validator.generate_samples(50)
            
            receipts = engine.embed_batch_vectorized(
                world="E2E_TEST",
                state_vectors=samples,
                channel=7,
                scope=False,
                validator_signature="e2e_v1.0.0"
            )
            
            # 2. Stream to disk
            path = Path(tmpdir) / "e2e.jsonl"
            with StreamingEmbeddingWriter(path, buffer_size=20) as writer:
                for receipt in receipts:
                    writer.write(receipt)
            
            # 3. Load with async controller
            controller = AsyncMetaWorldController()
            controller.register_world(
                world_id="E2E_TEST",
                name="E2E",
                description="End-to-end test",
                embedding_path=path,
                cqe_channel=7
            )
            
            # 4. Analyze
            metrics = await controller.analyze_world_async("E2E_TEST")
            
            # 5. Verify provenance
            loaded = await controller.load_world_async("E2E_TEST")
            assert all(r.verify_integrity() for r in loaded)
            
            controller.close()
    
    run_async(test())


if __name__ == "__main__":
    success = runner.run()
    sys.exit(0 if success else 1)
