#!/usr/bin/env python3
"""
Semantic Clarification Pass
Access semantic data ONLY to clarify geometric patterns discovered in embedding-first pass.
Focus: Understanding 360° structure and EM sphere constraints.
"""
import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

WORK_DIR = Path("/home/ubuntu/cqe_workspace")

def load_embedding_results():
    """Load embedding-first results"""
    with open(WORK_DIR / "embedding_first_results.json", 'r') as f:
        return json.load(f)

def load_semantic_data():
    """Load semantic data for clarification"""
    with open(WORK_DIR / "dual_processing_results.json", 'r') as f:
        return json.load(f)

def clarify_clusters_with_semantics(embedding_results, semantic_data):
    """Clarify what geometric clusters represent conceptually"""
    print("="*80)
    print("SEMANTIC CLARIFICATION: Geometric Cluster Interpretation")
    print("="*80)
    
    # Get K-Means cluster assignments
    kmeans_labels = embedding_results['clusters']['kmeans']['labels']
    
    # Build file index
    file_to_semantic = {}
    for archive in semantic_data['archives']:
        for file_result in archive['processed']:
            file_to_semantic[file_result['name']] = file_result.get('semantic', {})
    
    # Analyze each cluster
    cluster_interpretations = {}
    
    for cluster_id in range(5):
        print(f"\n{'='*80}")
        print(f"Cluster {cluster_id} Clarification")
        print(f"{'='*80}")
        
        # Get files in this cluster
        cluster_files = []
        for i, label in enumerate(kmeans_labels):
            if label == cluster_id:
                # Get file from semantic data
                file_idx = 0
                for archive in semantic_data['archives']:
                    for file_result in archive['processed']:
                        if file_idx == i:
                            cluster_files.append(file_result)
                            break
                        file_idx += 1
        
        print(f"\nFiles: {len(cluster_files)}")
        
        # Aggregate semantic patterns
        all_keywords = Counter()
        all_imports = []
        all_classes = []
        all_functions = []
        file_types = Counter()
        
        for file_result in cluster_files:
            file_types[file_result['ext']] += 1
            
            if 'semantic' in file_result and 'analysis' in file_result['semantic']:
                analysis = file_result['semantic']['analysis']
                
                for kw in analysis.get('keywords', []):
                    all_keywords[kw] += 1
                
                all_imports.extend(analysis.get('imports', []))
                all_classes.extend(analysis.get('classes', []))
                all_functions.extend(analysis.get('functions', []))
        
        print(f"\n📊 File types:")
        for ftype, count in file_types.most_common():
            print(f"  {ftype}: {count}")
        
        print(f"\n🔑 CQE concepts:")
        if all_keywords:
            for kw, count in all_keywords.most_common(5):
                print(f"  {kw}: {count}")
        else:
            print("  (No CQE keywords)")
        
        print(f"\n🏗️  Classes:")
        if all_classes:
            class_counts = Counter(all_classes)
            for cls, count in class_counts.most_common(3):
                print(f"  {cls}: {count}")
        else:
            print("  (No classes)")
        
        print(f"\n⚙️  Functions:")
        if all_functions:
            func_counts = Counter(all_functions)
            for func, count in func_counts.most_common(5):
                if func != '__init__':
                    print(f"  {func}: {count}")
        else:
            print("  (No functions)")
        
        # Interpretation
        interpretation = {
            'cluster_id': cluster_id,
            'size': len(cluster_files),
            'file_types': dict(file_types),
            'keywords': dict(all_keywords),
            'primary_concept': all_keywords.most_common(1)[0][0] if all_keywords else None,
            'geometric_signature': 'unknown'
        }
        
        # Determine geometric signature based on concepts
        if any(kw in all_keywords for kw in ['E8', 'Niemeier', 'lattice', 'cartan']):
            interpretation['geometric_signature'] = 'L0_geometric_substrate'
        elif any(kw in all_keywords for kw in ['lambda', 'receipt']):
            interpretation['geometric_signature'] = 'L1_execution_model'
        elif any(kw in all_keywords for kw in ['channel']):
            interpretation['geometric_signature'] = 'L3_audit_governance'
        elif any(kw in all_keywords for kw in ['embedding']):
            interpretation['geometric_signature'] = 'L4_data_layer'
        else:
            interpretation['geometric_signature'] = 'support_utilities'
        
        print(f"\n💡 Interpretation: {interpretation['geometric_signature']}")
        
        cluster_interpretations[cluster_id] = interpretation
    
    return cluster_interpretations

def analyze_360_structure(embedding_results, semantic_data):
    """Analyze 360° structure in embeddings and semantic patterns"""
    print(f"\n{'='*80}")
    print("360° STRUCTURE ANALYSIS: EM Sphere Constraints")
    print("="*80)
    
    # Load raw embeddings
    embeddings = []
    for archive in semantic_data['archives']:
        for file_result in archive['processed']:
            if file_result['geometric'] and 'embedding' in file_result['geometric']:
                embeddings.append(file_result['geometric']['embedding'])
    
    embeddings = np.array(embeddings)
    
    # Angular components (bins 16-31)
    angular = embeddings[:, 16:32]
    
    print(f"\n📐 Angular Histogram Analysis (16 bins):")
    print(f"  Bins represent: 360° / 16 = 22.5° per bin")
    
    # Analyze angular distribution
    angular_sums = np.sum(angular, axis=0)
    
    print(f"\n  Angular energy distribution:")
    for i, energy in enumerate(angular_sums):
        angle_start = i * 22.5
        angle_end = (i + 1) * 22.5
        print(f"    Bin {i:2d} [{angle_start:5.1f}° - {angle_end:5.1f}°]: {energy:8.4f}")
    
    # Find dominant angles
    dominant_bins = np.argsort(angular_sums)[-5:][::-1]
    
    print(f"\n  Dominant angular bins:")
    for bin_idx in dominant_bins:
        angle_center = (bin_idx + 0.5) * 22.5
        print(f"    Bin {bin_idx}: {angle_center:.1f}° (energy: {angular_sums[bin_idx]:.4f})")
    
    # Check for 90°, 180°, 270° alignments (cardinal directions)
    cardinal_bins = [4, 8, 12]  # 90°, 180°, 270° (bin 0 is 0°)
    cardinal_energy = sum(angular_sums[b] for b in cardinal_bins)
    total_energy = sum(angular_sums)
    
    print(f"\n  Cardinal direction energy (90°, 180°, 270°):")
    print(f"    Total: {cardinal_energy:.4f}")
    print(f"    Percentage: {cardinal_energy/total_energy*100:.2f}%")
    
    # Radial components (bins 0-15)
    radial = embeddings[:, :16]
    radial_sums = np.sum(radial, axis=0)
    
    print(f"\n📏 Radial Histogram Analysis (16 bins):")
    print(f"  Bins represent: Distance from origin")
    
    print(f"\n  Radial energy distribution:")
    for i, energy in enumerate(radial_sums):
        print(f"    Bin {i:2d}: {energy:8.4f}")
    
    # Check for harmonic structure (multiples of fundamental frequency)
    # In EM sphere, expect harmonics at 360/n for integer n
    harmonics = [1, 2, 3, 4, 6, 8, 9, 12]  # Divisors of 360
    
    print(f"\n  Harmonic analysis (360° divisors):")
    for h in harmonics:
        bin_idx = int(16 * h / 16)  # Map to 16 bins
        if bin_idx < 16:
            angle = 360 / h
            print(f"    {h}th harmonic (360°/{h} = {angle:.1f}°): bin {bin_idx}, energy {angular_sums[bin_idx % 16]:.4f}")
    
    # Ratio analysis
    print(f"\n  Ratio analysis (looking for 360-based attractors):")
    
    # Radial/Angular ratio
    radial_total = np.sum(radial_sums)
    angular_total = np.sum(angular_sums)
    ratio = radial_total / angular_total
    
    print(f"    Radial/Angular: {ratio:.4f}")
    print(f"    Closest to 360/n: 360/{360/ratio:.1f} ≈ {ratio:.4f}")
    
    # Check if ratio is close to simple fraction of 360
    for n in range(1, 20):
        for m in range(1, 20):
            test_ratio = (360 * m) / (360 * n)
            if abs(test_ratio - ratio) < 0.1:
                print(f"    Matches: {m}×360 / {n}×360 = {test_ratio:.4f}")
                break
    
    return {
        'angular_distribution': angular_sums.tolist(),
        'radial_distribution': radial_sums.tolist(),
        'dominant_angles': [float((bin_idx + 0.5) * 22.5) for bin_idx in dominant_bins],
        'cardinal_energy_pct': float(cardinal_energy/total_energy*100),
        'radial_angular_ratio': float(ratio)
    }

def correlate_geometry_semantics(embedding_results, semantic_data, cluster_interpretations):
    """Correlate geometric patterns with semantic concepts"""
    print(f"\n{'='*80}")
    print("GEOMETRY ↔ SEMANTICS CORRELATION")
    print("="*80)
    
    # For each CQE concept, find its geometric signature
    concept_geometries = defaultdict(list)
    
    file_idx = 0
    for archive in semantic_data['archives']:
        for file_result in archive['processed']:
            if 'semantic' in file_result and 'analysis' in file_result['semantic']:
                keywords = file_result['semantic']['analysis'].get('keywords', [])
                
                if file_result['geometric'] and 'embedding' in file_result['geometric']:
                    embedding = file_result['geometric']['embedding']
                    
                    for kw in keywords:
                        concept_geometries[kw].append({
                            'file': file_result['name'],
                            'embedding': embedding,
                            'magnitude': float(np.linalg.norm(embedding))
                        })
            
            file_idx += 1
    
    print(f"\n🔗 Concept → Geometric Signature Mapping:")
    
    for concept in ['E8', 'Niemeier', 'lambda', 'receipt', 'channel', 'embedding']:
        if concept in concept_geometries:
            embeddings = [item['embedding'] for item in concept_geometries[concept]]
            embeddings_array = np.array(embeddings)
            
            mean_magnitude = np.mean([item['magnitude'] for item in concept_geometries[concept]])
            
            # Analyze angular distribution for this concept
            angular = embeddings_array[:, 16:32]
            angular_mean = np.mean(angular, axis=0)
            dominant_angle_bin = np.argmax(angular_mean)
            dominant_angle = (dominant_angle_bin + 0.5) * 22.5
            
            print(f"\n  {concept}:")
            print(f"    Files: {len(concept_geometries[concept])}")
            print(f"    Mean magnitude: {mean_magnitude:.4f}")
            print(f"    Dominant angle: {dominant_angle:.1f}°")
            
            # Check if angle aligns with 360° harmonics
            for h in [1, 2, 3, 4, 6, 8, 9, 12]:
                harmonic_angle = 360 / h
                if abs(dominant_angle - harmonic_angle) < 22.5:
                    print(f"    → Aligns with {h}th harmonic (360°/{h} = {harmonic_angle:.1f}°)")

def main():
    print("="*80)
    print("SEMANTIC CLARIFICATION PASS")
    print("Accessing semantic data to clarify geometric patterns")
    print("="*80)
    
    # Load embedding-first results
    embedding_results = load_embedding_results()
    
    # Load semantic data
    semantic_data = load_semantic_data()
    
    print(f"\n✓ Loaded embedding-first results")
    print(f"✓ Loaded semantic data for clarification")
    
    # Clarify clusters
    cluster_interpretations = clarify_clusters_with_semantics(embedding_results, semantic_data)
    
    # Analyze 360° structure
    angular_analysis = analyze_360_structure(embedding_results, semantic_data)
    
    # Correlate geometry and semantics
    correlate_geometry_semantics(embedding_results, semantic_data, cluster_interpretations)
    
    # Save results
    results = {
        'cluster_interpretations': cluster_interpretations,
        'angular_360_analysis': angular_analysis,
        'em_sphere_hypothesis': {
            'description': 'All ratios and measures are attractors tied to 360° or 360 as whole number',
            'reason': 'Governed by Earth\'s EM sphere - how light behaves, how all things behave inside observation',
            'evidence': {
                'radial_angular_ratio': angular_analysis['radial_angular_ratio'],
                'cardinal_energy_pct': angular_analysis['cardinal_energy_pct'],
                'dominant_angles': angular_analysis['dominant_angles']
            }
        }
    }
    
    output_path = WORK_DIR / "semantic_clarification_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*80}")
    print("SEMANTIC CLARIFICATION COMPLETE")
    print("="*80)
    print(f"✓ Clusters interpreted via semantic concepts")
    print(f"✓ 360° structure analyzed")
    print(f"✓ Geometry ↔ Semantics correlated")
    print(f"✓ Results saved to: {output_path}")

if __name__ == "__main__":
    main()
