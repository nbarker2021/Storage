#!/usr/bin/env python3
"""
CQE Meta Usage Examples
=======================

Comprehensive examples demonstrating the refactored CQE meta-infrastructure.
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np

from cqe_meta import (
    CQEMetaConfig,
    EmbeddingPipeline,
    EmbeddingStore,
    KakeyaAnalyzer,
    MetaWorldController,
    MockValidator,
    PathConfig,
)


def example_1_basic_embedding():
    """Example 1: Generate embeddings from mock validator"""
    print("\n" + "="*70)
    print("Example 1: Basic Embedding Generation")
    print("="*70 + "\n")
    
    # Create pipeline
    pipeline = EmbeddingPipeline()
    
    # Create mock validator
    validator = MockValidator(dimension=8, n_samples=50)
    samples = validator.generate_samples()
    
    print(f"Generated {len(samples)} E8-like samples")
    
    # Generate embeddings
    receipts = []
    baseline_energy = None
    
    for i, sample in enumerate(samples[:10]):  # First 10 for demo
        receipt = pipeline.embed_state_vector(
            world="MOCK_YM",
            state_vector=sample,
            channel=7,
            scope=False,
            sample_index=i,
            baseline_energy=baseline_energy,
            extra_metadata={"validator": "mock"}
        )
        
        if baseline_energy is None:
            baseline_energy = validator.compute_energy(sample)
        
        receipts.append(receipt)
    
    # Print receipt info
    print(f"\nGenerated {len(receipts)} embedding receipts")
    print(f"Schema version: {receipts[0].schema_version}")
    print(f"Vector dimension: {receipts[0].vec_dim}")
    print(f"Sample receipt: {receipts[0].to_dict()}")
    
    return receipts


def example_2_kakeya_analysis():
    """Example 2: Analyze geometric properties with Kakeya"""
    print("\n" + "="*70)
    print("Example 2: Kakeya Geometric Analysis")
    print("="*70 + "\n")
    
    analyzer = KakeyaAnalyzer()
    
    # Create different geometric patterns
    n_samples = 50
    
    # Pattern 1: Linear manifold (circle in 2D)
    t = np.linspace(0, 2*np.pi, n_samples)
    vecs_linear = np.zeros((n_samples, 50))
    vecs_linear[:, 0] = np.cos(t)
    vecs_linear[:, 1] = np.sin(t)
    
    # Pattern 2: Volumetric cloud (3D Gaussian)
    vecs_volume = np.zeros((n_samples, 50))
    vecs_volume[:, :3] = np.random.randn(n_samples, 3)
    
    # Pattern 3: Needle (high-D random on sphere)
    vecs_needle = np.random.randn(n_samples, 50)
    vecs_needle /= np.linalg.norm(vecs_needle, axis=1, keepdims=True)
    
    # Analyze each
    for name, vecs in [
        ("Linear (Circle)", vecs_linear),
        ("Volumetric (3D Gaussian)", vecs_volume),
        ("Needle (High-D Sphere)", vecs_needle)
    ]:
        metrics = analyzer.analyze_vectors(vecs)
        geometry = analyzer.classify_geometry(metrics)
        
        print(f"\n{name}:")
        print(f"  n={metrics.n}")
        print(f"  K={metrics.K:.3f} (directional coverage)")
        print(f"  vol_proxy={metrics.vol_proxy:.3e} (volume)")
        print(f"  dimension_estimate={metrics.dimension_estimate}")
        print(f"  Classified as: {geometry}")


def example_3_controller_workflow():
    """Example 3: Complete workflow with MetaWorldController"""
    print("\n" + "="*70)
    print("Example 3: MetaWorldController Workflow")
    print("="*70 + "\n")
    
    import tempfile
    
    # Create controller
    controller = MetaWorldController()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create mock worlds
        for world_id in ["WORLD_A", "WORLD_B", "WORLD_C"]:
            print(f"\nCreating world: {world_id}")
            
            # Generate embeddings
            validator = MockValidator(dimension=8, n_samples=30)
            samples = validator.generate_samples()
            
            pipeline = EmbeddingPipeline()
            receipts = []
            
            for i, sample in enumerate(samples):
                receipt = pipeline.embed_state_vector(
                    world=world_id,
                    state_vector=sample,
                    channel=7,
                    scope=False,
                    sample_index=i
                )
                receipts.append(receipt)
            
            # Save
            embed_path = tmpdir / f"{world_id}.jsonl"
            store = EmbeddingStore(embed_path)
            store.save(receipts)
            
            # Register with controller
            controller.register_world(
                world_id=world_id,
                name=f"Mock World {world_id}",
                description=f"Generated for testing",
                embedding_path=embed_path,
                cqe_channel=7
            )
            
            print(f"  Created {len(receipts)} embeddings")
        
        # Get summary
        print("\n" + "-"*70)
        print("World Summary:")
        print("-"*70)
        
        summary = controller.get_world_summary()
        for world_id, info in summary.items():
            print(f"\n{world_id} ({info['name']}):")
            print(f"  Total embeddings: {info['n_embeddings']}")
            for cluster_name, cluster_info in info['clusters'].items():
                print(f"  {cluster_name}:")
                print(f"    n={cluster_info['n']}")
                print(f"    K={cluster_info['K']:.3f}")
                print(f"    geometry={cluster_info['geometry']}")
        
        # Find similar clusters
        print("\n" + "-"*70)
        print("Similarity Search:")
        print("-"*70)
        
        similar = controller.find_similar_clusters(
            query_world="WORLD_A",
            query_cluster="all",
            target_worlds=["WORLD_B", "WORLD_C"],
            max_results=2
        )
        
        print(f"\nClusters similar to WORLD_A/all:")
        for world, cluster, distance, geometry in similar:
            print(f"  {world}/{cluster}: distance={distance:.3f}, geometry={geometry}")
        
        # Generate curriculum
        print("\n" + "-"*70)
        print("Learning Curriculum (by directional complexity):")
        print("-"*70)
        
        curriculum = controller.generate_curriculum(
            difficulty_metric="K",
            ascending=True
        )
        
        for i, (world, cluster, score) in enumerate(curriculum, 1):
            print(f"  {i}. {world}/{cluster}: K={score:.3f}")
        
        # Distance matrix
        print("\n" + "-"*70)
        print("Distance Matrix:")
        print("-"*70)
        
        matrix, labels = controller.compute_distance_matrix()
        print(f"\nShape: {matrix.shape}")
        print(f"Labels: {labels}")
        print(f"\nSample distances:")
        for i in range(min(3, len(labels))):
            for j in range(i+1, min(3, len(labels))):
                print(f"  {labels[i]} <-> {labels[j]}: {matrix[i, j]:.3f}")


def example_4_custom_configuration():
    """Example 4: Custom configuration"""
    print("\n" + "="*70)
    print("Example 4: Custom Configuration")
    print("="*70 + "\n")
    
    # Create custom config
    config = CQEMetaConfig(
        paths=PathConfig(
            base_dir=Path("/custom/path"),
            cqe_production_dir="CQE_PRODUCTION_v2.0.0"
        ),
        verbose=True
    )
    
    print("Custom configuration created:")
    print(f"  Base dir: {config.paths.base_dir}")
    print(f"  Sandbox: {config.paths.sandbox_root}")
    print(f"  CQE root: {config.paths.cqe_root}")
    print(f"  Schema version: {config.embedding.schema_version}")
    
    # Serialize
    config_dict = config.to_dict()
    print(f"\nSerialized config has {len(config_dict)} top-level keys:")
    for key in config_dict:
        print(f"  - {key}")
    
    # Reconstruct
    config2 = CQEMetaConfig.from_dict(config_dict)
    print(f"\nReconstructed config matches: {config2.embedding.schema_version == config.embedding.schema_version}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("CQE META USAGE EXAMPLES")
    print("="*70)
    
    example_1_basic_embedding()
    example_2_kakeya_analysis()
    example_3_controller_workflow()
    example_4_custom_configuration()
    
    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70 + "\n")
