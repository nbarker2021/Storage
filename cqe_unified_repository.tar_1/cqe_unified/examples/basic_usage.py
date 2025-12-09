#!/usr/bin/env python3
"""
CQE Basic Usage Examples
Demonstrates how to use the extracted CQE modules
"""

# Example 1: Using L0 Geometric Substrate
def example_e8_lattice():
    """Example of E8 lattice operations"""
    from cqe.L0_geometric import E8Lattice
    
    # Create E8 lattice instance
    lattice = E8Lattice()
    
    # Generate roots
    roots = lattice.generate_roots()
    print(f"E8 lattice has {len(roots)} roots")
    
    # Compute Weyl chambers
    chambers = lattice.weyl_chambers()
    print(f"E8 has {len(chambers)} Weyl chambers")
    
    return lattice

# Example 2: Using L1 Execution Model
def example_alena_operators():
    """Example of ALENA operators"""
    from cqe.L1_execution import ALENAOps
    import numpy as np
    
    # Create ALENA operator instance
    alena = ALENAOps()
    
    # Perform Rθ snap
    vector = np.array([1.0, 2.0, 3.0])
    snapped = alena.r_theta_snap(vector)
    print(f"Original: {vector}")
    print(f"Snapped: {snapped}")
    
    # Perform Weyl flip
    flipped = alena.weyl_flip(vector)
    print(f"Flipped: {flipped}")
    
    return alena

# Example 3: Using L2 Core Engine
def example_cqe_core():
    """Example of CQE core operations"""
    from cqe.L2_core import CQEKernal
    
    # Create CQE kernel instance
    kernel = CQEKernal()
    
    # Compute equivalence class
    point = [1, 2, 3, 4, 5, 6, 7, 8]
    equiv_class = kernel.equivalence_class(point)
    print(f"Equivalence class for {point}: {equiv_class}")
    
    # Check Φ-conservation
    phi_conserved = kernel.check_phi_conservation()
    print(f"Φ-conservation: {phi_conserved}")
    
    return kernel

# Example 4: Using L3 Audit & Governance
def example_morsr():
    """Example of MORSR receipt generation"""
    from cqe.L3_audit import EnhancedMORSRExplorer
    
    # Create MORSR explorer
    morsr = EnhancedMORSRExplorer()
    
    # Generate receipt for operation
    operation = {"type": "lattice_op", "data": [1, 2, 3]}
    receipt = morsr.generate_receipt(operation)
    print(f"Receipt ID: {receipt['id']}")
    print(f"Merkle root: {receipt['merkle_root']}")
    
    return morsr

# Example 5: Using Storage Module
def example_storage():
    """Example of universal atom storage"""
    from cqe.storage import UniversalAtom
    
    # Create universal atom
    atom = UniversalAtom(data={"key": "value"})
    
    # Store atom
    atom_id = atom.store()
    print(f"Stored atom with ID: {atom_id}")
    
    # Retrieve atom
    retrieved = UniversalAtom.retrieve(atom_id)
    print(f"Retrieved atom: {retrieved.data}")
    
    return atom

# Example 6: Using RAG Module
def example_rag():
    """Example of semantic graph RAG"""
    from cqe.rag import CQERAG
    
    # Create RAG instance
    rag = CQERAG()
    
    # Add documents
    rag.add_document("doc1", "E8 lattice has 240 roots")
    rag.add_document("doc2", "Niemeier lattices are 24-dimensional")
    
    # Query
    results = rag.query("What is E8?")
    print(f"Query results: {results}")
    
    return rag

# Example 7: Complete Workflow
def example_complete_workflow():
    """Example of complete CQE workflow"""
    from cqe.L0_geometric import E8Lattice
    from cqe.L1_execution import ALENAOps
    from cqe.L2_core import CQEKernal
    from cqe.L3_audit import EnhancedMORSRExplorer
    import numpy as np
    
    print("="*60)
    print("CQE Complete Workflow Example")
    print("="*60)
    
    # Step 1: Initialize geometric substrate (L0)
    print("\n[L0] Initializing E8 lattice...")
    lattice = E8Lattice()
    roots = lattice.generate_roots()
    print(f"  ✓ Generated {len(roots)} E8 roots")
    
    # Step 2: Apply execution operators (L1)
    print("\n[L1] Applying ALENA operators...")
    alena = ALENAOps()
    vector = np.random.randn(8)
    snapped = alena.r_theta_snap(vector)
    print(f"  ✓ Snapped vector to lattice")
    
    # Step 3: Compute equivalence (L2)
    print("\n[L2] Computing CQE equivalence...")
    kernel = CQEKernal()
    equiv = kernel.equivalence_class(snapped.tolist())
    print(f"  ✓ Computed equivalence class: {equiv}")
    
    # Step 4: Generate receipt (L3)
    print("\n[L3] Generating MORSR receipt...")
    morsr = EnhancedMORSRExplorer()
    receipt = morsr.generate_receipt({
        "operation": "cqe_workflow",
        "vector": snapped.tolist(),
        "equivalence": equiv
    })
    print(f"  ✓ Receipt ID: {receipt['id']}")
    
    print("\n" + "="*60)
    print("Workflow complete!")
    print("="*60)

if __name__ == "__main__":
    print("CQE Usage Examples\n")
    
    # Note: These examples assume the modules have been properly extracted
    # and the necessary classes/functions exist. Adjust imports as needed.
    
    print("Run individual examples by uncommenting:")
    print("  example_e8_lattice()")
    print("  example_alena_operators()")
    print("  example_cqe_core()")
    print("  example_morsr()")
    print("  example_storage()")
    print("  example_rag()")
    print("  example_complete_workflow()")
