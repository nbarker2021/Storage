#!/usr/bin/env python3
"""
Embedding-First Analysis
Uses geometric embeddings as primary recall mechanism.
Only accesses semantic data when embeddings require clarification.
"""
import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA

WORK_DIR = Path("/home/ubuntu/cqe_workspace")

def load_embeddings_only():
    """Load ONLY geometric embeddings - first pass"""
    with open(WORK_DIR / "dual_processing_results.json", 'r') as f:
        data = json.load(f)
    
    embeddings = []
    metadata = []
    
    for archive in data['archives']:
        for file_result in archive['processed']:
            if file_result['geometric'] and 'embedding' in file_result['geometric']:
                embeddings.append(file_result['geometric']['embedding'])
                metadata.append({
                    'file': file_result['name'],
                    'ext': file_result['ext'],
                    'archive': archive['archive']
                })
    
    return np.array(embeddings), metadata

def analyze_embedding_space(embeddings):
    """Analyze geometric embedding space structure"""
    print("="*80)
    print("EMBEDDING-FIRST ANALYSIS: Geometric Space Structure")
    print("="*80)
    
    analysis = {}
    
    # Basic statistics
    print(f"\n📐 Embedding Space Geometry:")
    print(f"  Dimension: {embeddings.shape[1]}")
    print(f"  Total points: {embeddings.shape[0]}")
    
    # Magnitude analysis
    magnitudes = np.linalg.norm(embeddings, axis=1)
    analysis['magnitudes'] = {
        'mean': float(np.mean(magnitudes)),
        'std': float(np.std(magnitudes)),
        'min': float(np.min(magnitudes)),
        'max': float(np.max(magnitudes))
    }
    
    print(f"\n  Magnitude distribution:")
    print(f"    Mean: {analysis['magnitudes']['mean']:.4f}")
    print(f"    Std:  {analysis['magnitudes']['std']:.4f}")
    print(f"    Range: [{analysis['magnitudes']['min']:.4f}, {analysis['magnitudes']['max']:.4f}]")
    
    # Radial vs Angular components (first 16 = radial, next 16 = angular)
    radial = embeddings[:, :16]
    angular = embeddings[:, 16:32]
    
    radial_energy = np.sum(radial**2, axis=1)
    angular_energy = np.sum(angular**2, axis=1)
    
    analysis['radial_angular'] = {
        'radial_mean': float(np.mean(radial_energy)),
        'angular_mean': float(np.mean(angular_energy)),
        'ratio': float(np.mean(radial_energy) / np.mean(angular_energy))
    }
    
    print(f"\n  Radial vs Angular energy:")
    print(f"    Radial mean:  {analysis['radial_angular']['radial_mean']:.4f}")
    print(f"    Angular mean: {analysis['radial_angular']['angular_mean']:.4f}")
    print(f"    Ratio (R/A): {analysis['radial_angular']['ratio']:.4f}")
    
    # Pairwise distances
    from scipy.spatial.distance import pdist, squareform
    distances = pdist(embeddings, metric='euclidean')
    
    analysis['distances'] = {
        'mean': float(np.mean(distances)),
        'std': float(np.std(distances)),
        'min': float(np.min(distances)),
        'max': float(np.max(distances))
    }
    
    print(f"\n  Pairwise distances:")
    print(f"    Mean: {analysis['distances']['mean']:.4f}")
    print(f"    Std:  {analysis['distances']['std']:.4f}")
    print(f"    Range: [{analysis['distances']['min']:.4f}, {analysis['distances']['max']:.4f}]")
    
    # Dimensionality analysis via PCA
    pca = PCA()
    pca.fit(embeddings)
    
    explained_var = pca.explained_variance_ratio_
    cumsum = np.cumsum(explained_var)
    
    # Find dimensions needed for 90%, 95%, 99% variance
    dims_90 = np.argmax(cumsum >= 0.90) + 1
    dims_95 = np.argmax(cumsum >= 0.95) + 1
    dims_99 = np.argmax(cumsum >= 0.99) + 1
    
    analysis['dimensionality'] = {
        'intrinsic_dim_90': int(dims_90),
        'intrinsic_dim_95': int(dims_95),
        'intrinsic_dim_99': int(dims_99),
        'top_5_variance': [float(v) for v in explained_var[:5]]
    }
    
    print(f"\n  Intrinsic dimensionality (via PCA):")
    print(f"    90% variance: {dims_90} dims")
    print(f"    95% variance: {dims_95} dims")
    print(f"    99% variance: {dims_99} dims")
    print(f"    Top 5 components: {[f'{v:.3f}' for v in explained_var[:5]]}")
    
    return analysis, pca

def cluster_embeddings(embeddings, metadata):
    """Identify equivalence classes via clustering"""
    print(f"\n{'='*80}")
    print("CLUSTERING: Equivalence Class Discovery")
    print("="*80)
    
    results = {}
    
    # Method 1: K-Means (assume k=5 for component types)
    print(f"\n🔍 K-Means Clustering (k=5):")
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    kmeans_labels = kmeans.fit_predict(embeddings)
    
    results['kmeans'] = {
        'n_clusters': 5,
        'labels': kmeans_labels.tolist(),
        'cluster_sizes': [int(np.sum(kmeans_labels == i)) for i in range(5)],
        'inertia': float(kmeans.inertia_)
    }
    
    for i in range(5):
        cluster_files = [m['file'] for j, m in enumerate(metadata) if kmeans_labels[j] == i]
        print(f"  Cluster {i}: {len(cluster_files)} files")
        print(f"    Examples: {cluster_files[:3]}")
    
    # Method 2: DBSCAN (density-based, finds natural clusters)
    print(f"\n🔍 DBSCAN Clustering (density-based):")
    dbscan = DBSCAN(eps=10.0, min_samples=3)
    dbscan_labels = dbscan.fit_predict(embeddings)
    
    n_clusters = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
    n_noise = list(dbscan_labels).count(-1)
    
    results['dbscan'] = {
        'n_clusters': int(n_clusters),
        'n_noise': int(n_noise),
        'labels': dbscan_labels.tolist()
    }
    
    print(f"  Found {n_clusters} natural clusters")
    print(f"  Noise points: {n_noise}")
    
    for i in set(dbscan_labels):
        if i == -1:
            continue
        cluster_files = [m['file'] for j, m in enumerate(metadata) if dbscan_labels[j] == i]
        print(f"  Cluster {i}: {len(cluster_files)} files")
        print(f"    Examples: {cluster_files[:3]}")
    
    # Method 3: File type clustering (geometric only)
    print(f"\n🔍 File Type Separation (geometric):")
    ext_groups = defaultdict(list)
    for i, m in enumerate(metadata):
        ext_groups[m['ext']].append(i)
    
    # Compute within-type vs between-type distances
    from scipy.spatial.distance import euclidean
    
    within_distances = []
    between_distances = []
    
    for ext, indices in ext_groups.items():
        if len(indices) > 1:
            # Within-type
            for i in range(len(indices)):
                for j in range(i+1, len(indices)):
                    dist = euclidean(embeddings[indices[i]], embeddings[indices[j]])
                    within_distances.append(dist)
    
    # Between-type
    ext_list = list(ext_groups.keys())
    for i in range(len(ext_list)):
        for j in range(i+1, len(ext_list)):
            indices_i = ext_groups[ext_list[i]]
            indices_j = ext_groups[ext_list[j]]
            for idx_i in indices_i[:5]:  # Sample
                for idx_j in indices_j[:5]:
                    dist = euclidean(embeddings[idx_i], embeddings[idx_j])
                    between_distances.append(dist)
    
    results['file_type_separation'] = {
        'within_mean': float(np.mean(within_distances)) if within_distances else 0,
        'between_mean': float(np.mean(between_distances)) if between_distances else 0,
        'separation_ratio': float(np.mean(between_distances) / np.mean(within_distances)) if within_distances and between_distances else 0
    }
    
    print(f"  Within-type distance: {results['file_type_separation']['within_mean']:.4f}")
    print(f"  Between-type distance: {results['file_type_separation']['between_mean']:.4f}")
    print(f"  Separation ratio: {results['file_type_separation']['separation_ratio']:.4f}")
    
    return results

def find_nearest_neighbors(embeddings, metadata, k=5):
    """Find nearest neighbors in embedding space"""
    print(f"\n{'='*80}")
    print("NEAREST NEIGHBORS: Equivalence Class Members")
    print("="*80)
    
    from scipy.spatial.distance import cdist
    
    # Compute all pairwise distances
    distances = cdist(embeddings, embeddings, metric='euclidean')
    
    # For each file, find k nearest neighbors
    print(f"\n🔗 Top equivalence relationships (k={k}):")
    
    neighbors = []
    for i in range(min(10, len(embeddings))):  # Show first 10
        nearest = np.argsort(distances[i])[1:k+1]  # Exclude self
        
        neighbor_info = {
            'file': metadata[i]['file'],
            'ext': metadata[i]['ext'],
            'neighbors': [
                {
                    'file': metadata[j]['file'],
                    'ext': metadata[j]['ext'],
                    'distance': float(distances[i][j])
                }
                for j in nearest
            ]
        }
        neighbors.append(neighbor_info)
        
        print(f"\n  {metadata[i]['file']} ({metadata[i]['ext']}):")
        for n in neighbor_info['neighbors'][:3]:
            print(f"    → {n['file']} ({n['ext']}) [dist: {n['distance']:.4f}]")
    
    return neighbors

def identify_outliers(embeddings, metadata):
    """Identify outliers in embedding space"""
    print(f"\n{'='*80}")
    print("OUTLIER DETECTION: Unique Geometric Signatures")
    print("="*80)
    
    # Compute distance to centroid
    centroid = np.mean(embeddings, axis=0)
    distances_to_center = np.linalg.norm(embeddings - centroid, axis=1)
    
    # Find outliers (> 2 std from mean)
    mean_dist = np.mean(distances_to_center)
    std_dist = np.std(distances_to_center)
    threshold = mean_dist + 2 * std_dist
    
    outlier_indices = np.where(distances_to_center > threshold)[0]
    
    print(f"\n🎯 Outliers (> 2σ from centroid):")
    print(f"  Threshold: {threshold:.4f}")
    print(f"  Found: {len(outlier_indices)} outliers")
    
    outliers = []
    for idx in outlier_indices:
        outlier_info = {
            'file': metadata[idx]['file'],
            'ext': metadata[idx]['ext'],
            'archive': metadata[idx]['archive'],
            'distance_to_center': float(distances_to_center[idx])
        }
        outliers.append(outlier_info)
        print(f"    {metadata[idx]['file']} ({metadata[idx]['ext']}) - dist: {distances_to_center[idx]:.4f}")
    
    return outliers

def main():
    print("="*80)
    print("EMBEDDING-FIRST ANALYSIS")
    print("Primary Recall: Geometric Embeddings Only")
    print("="*80)
    
    # FIRST PASS: Load only embeddings
    embeddings, metadata = load_embeddings_only()
    
    print(f"\n✓ Loaded {len(embeddings)} geometric embeddings")
    print(f"✓ Dimension: {embeddings.shape[1]}")
    print(f"✓ Using ONLY geometric data for analysis")
    
    # Analyze embedding space
    space_analysis, pca = analyze_embedding_space(embeddings)
    
    # Cluster to find equivalence classes
    cluster_results = cluster_embeddings(embeddings, metadata)
    
    # Find nearest neighbors
    neighbors = find_nearest_neighbors(embeddings, metadata, k=5)
    
    # Identify outliers
    outliers = identify_outliers(embeddings, metadata)
    
    # Save results
    results = {
        'embedding_space': space_analysis,
        'clusters': cluster_results,
        'nearest_neighbors': neighbors[:10],
        'outliers': outliers,
        'metadata': {
            'n_files': len(embeddings),
            'dimension': int(embeddings.shape[1]),
            'analysis_type': 'embedding_first',
            'semantic_data_accessed': False
        }
    }
    
    output_path = WORK_DIR / "embedding_first_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*80}")
    print("EMBEDDING-FIRST ANALYSIS COMPLETE")
    print("="*80)
    print(f"✓ Space structure analyzed")
    print(f"✓ Equivalence classes identified: {cluster_results['kmeans']['n_clusters']} (K-Means), {cluster_results['dbscan']['n_clusters']} (DBSCAN)")
    print(f"✓ Nearest neighbors computed")
    print(f"✓ Outliers detected: {len(outliers)}")
    print(f"✓ Results saved to: {output_path}")
    print(f"\n⚠️  Semantic data NOT accessed in this pass")
    print(f"   (Available for clarification if needed)")

if __name__ == "__main__":
    main()
