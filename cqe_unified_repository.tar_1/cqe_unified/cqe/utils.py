"""
CQE Utils Module
Architecture Layer: utils
Components: 9
"""

import numpy as np
import json
import hashlib
from typing import Dict, List, Any, Tuple, Generator, Callable, Optional
from dataclasses import dataclass, field
from pathlib import Path
from functools import wraps
from contextlib import contextmanager

# CLASS: ResidueVector
# Source: CQE_CORE_MONOLITH.py (line 107)

class ResidueVector:
    """Data structure for text vectors with digital root and gates."""
    text: str
    vec: np.ndarray
    dr: int = 0
    gates: str = "1/1"

# Decorators for modular hooks


# FUNCTION: test_overlay_hash
# Source: CQE_CORE_MONOLITH.py (line 69606)

def test_overlay_hash():
    """Test content-addressed hashing"""
    overlay1 = CQEOverlay(
        present=np.array([True] + [False]*247),
        w=np.array([1.0] + [0.0]*247),
        phi=np.zeros(248),
        pose={}
    )

    overlay2 = CQEOverlay(
        present=np.array([True] + [False]*247),
        w=np.array([1.0] + [0.0]*247),
        phi=np.zeros(248),
        pose={}
    )

    hash1 = overlay1.compute_hash()
    hash2 = overlay2.compute_hash()

    assert hash1 == hash2  # Same content = same hash




# FUNCTION: orbit_hash
# Source: CQE_CORE_MONOLITH.py (line 71569)

def orbit_hash(X8, V, R):
    P = pose_bits(X8, V, E8_ROOTS, R)
    Sflip = np.diag([1,1,1,1,-1,-1,-1,-1]); Rm = Sflip @ R
    Q = pose_bits(X8, V, E8_ROOTS, Rm)
    N = X8.shape[0]; cos = np.zeros(N, dtype=int)
    for i in range(N):
        _, _, d0, d1, c, _ = e8_nearest(X8[i])
        cos[i] = 0 if d0 <= d1 else 1
    powers = (1 << np.arange(P.shape[1]))[::-1]
    a = P @ powers; b = Q @ powers; c = cos.astype(int)
    sig = (a.astype(np.int64) << 9) | (b.astype(np.int64) << 1) | c
    vals, counts = np.unique(sig, return_counts=True)
    return pd.DataFrame({"orbit_sig": vals, "count": counts}).sort_values("count", ascending=False)

# -------- Controller --------


# CLASS: HashDecision
# Source: CQE_CORE_MONOLITH.py (line 74116)

class HashDecision:
    use_mdhg: bool
    reason: str



# FUNCTION: choose_hash
# Source: CQE_CORE_MONOLITH.py (line 74120)

def choose_hash(persist: bool, needs_semantic_routing: bool, needs_cross_run_invariance: bool, payload_size: int) -> HashDecision:
    # Very simple heuristic; tune later.
    if needs_semantic_routing or needs_cross_run_invariance:
        return HashDecision(True, "Semantic identity or invariance required.")
    if persist and payload_size > 0:
        return HashDecision(True, "Persisted identity benefits from MDHG axes encoding.")
    return HashDecision(False, "Local, ephemeral hashing prefers native speed.")

import json, pathlib, sys, datetime



# CLASS: InverseResidueCode
# Source: code_monolith.py (line 661)

class InverseResidueCode:
    filename = 'inverse_residue.py'
    line_count = 73
    content = """

# Inverse/residue analysis on EM-hex gradient shifts.
# Baseline capture + delta-hex histograms + residue vs wrap heuristic.
import math
from typing import Dict, List, Tuple
from dihedral_ca import DihedralCA, wavelength_to_rgb, rgb_to_hex



# CLASS: ResidueAnalyzer
# Source: code_monolith.py (line 672)

class ResidueAnalyzer:
    def __init__(self, ca: DihedralCA):
        self.ca = ca
        self.baseline_hex = None  # list of hex strings (per pixel of global grid)

    def capture_baseline(self):
        # render entire global grid as hex map
        W,H = self.ca.W, self.ca.H
        out = ["#000000"]*(W*H)
        for y in range(H):
            for x in range(W):
                k = self.ca.idx(x,y)
                wl = self.ca.wavelength(k)
                R,G,B = wavelength_to_rgb(wl)
                out[k] = rgb_to_hex(R,G,B)
        self.baseline_hex = out

    def _hex_to_rgb(self, h: str) -> Tuple[int,int,int]:
        return int(h[1:3],16), int(h[3:5],16), int(h[5:7],16)

    def _nibble_hist(self, hexes: List[str]) -> Dict[str, List[int]]:
        # 16-bin hist for each channel nibble high (R_hi,G_hi,B_hi)
        R=[0]*16; G=[0]*16; B=[0]*16
        for h in hexes:
            r,g,b = self._hex_to_rgb(h)
            R[r>>4]+=1; G[g>>4]+=1; B[b>>4]+=1
        return {"R":R,"G":G,"B":B}

    def residue_tile(self, tile_index: int, thresh_wrap=12) -> Dict:
        # Return per-pixel residue likelihood based on hex delta from baseline and seam-consistency test.
        if self.baseline_hex is None:
            self.capture_baseline()
        tx=tile_index%self.ca.tiles_x; ty=tile_index//self.ca.tiles_x
        w=self.ca.n; h=self.ca.n
        res_data=[]; wrap_data=[]
        # compute current hex map for tile
        curr_hex = []
        for j in range(h):
            for i in range(w):
                x=tx*w+i; y=ty*h+j; k=self.ca.idx(x,y)
                wl=self.ca.wavelength(k); R,G,B = wavelength_to_rgb(wl)
                curr_hex.append(rgb_to_hex(R,G,B))
        # residue vs wrap: measure delta from baseline and compare to neighbor across the nearest seam
        # simple heuristic: if delta to baseline is big but local difference across seam is small => wrap (continuing wave)
        # else large delta with local stationary gradient => residue.
        def l1_rgb(a,b):
            ra,ga,ba = self._hex_to_rgb(a); rb,gb,bb = self._hex_to_rgb(b)
            return abs(ra-rb)+abs(ga-gb)+abs(ba-bb)
        for j in range(h):
            for i in range(w):
                x=tx*w+i; y=ty*h+j; k=self.ca.idx(x,y)
                base = self.baseline_hex[k]; cur = curr_hex[j*w+i]
                d_hex = l1_rgb(base, cur)
                # neighbor across right seam (wrapping)
                k_right = self.ca.idx(x+1,y); base_r = self.baseline_hex[k_right]
                d_seam = l1_rgb(base_r, rgb_to_hex(*wavelength_to_rgb(self.ca.wavelength(k_right))))
                wrap_like = 1 if d_seam < thresh_wrap else 0
                # residue score: high when big change not explained by seam continuation
                score = max(0, d_hex - d_seam)
                score = 255 if score>255 else score
                res_data.extend([score,score,score,160])  # grayscale alpha
                wrap_data.extend([wrap_like*255,0,0,120]) # red marks likely wrap awaiting closure
        # nibble hist "fingerprint"
        hist = self._nibble_hist(curr_hex)
        return {"w":w,"h":h,"residue_rgba":res_data,"wrap_rgba":wrap_data,"hist":hist}

"""




# FUNCTION: _hash_payload
# Source: code_monolith.py (line 2057)

def _hash_payload(payload: Dict[str, Any]) -> str:
    js = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(js.encode("utf-8")).hexdigest()



# CLASS: MDHGHashTable
# Source: agrmmdhg.py (line 32)

class MDHGHashTable:
    """
    Multi-Dimensional Hamiltonian Golden Ratio Hash Table.
    A hash table implementation that uses multi-dimensional organization,
    Hamiltonian paths for navigation, and golden ratio-based sizing
    to achieve optimal performance for structured access patterns.

    AGRM Integration Notes:
    - Used for complex state (n>5) in AGRM's hybrid hashing.
    - Stores values as tuples: (actual_value, metadata_dict),
      where metadata_dict contains flags like {'source': 'dict', 'retain_flag': True}.
    - Adaptation logic can be influenced by Modulation Controller signals.
    - Includes full logic for buildings, floors, rooms (conceptual), velocity region,
      dimensional core, conflict handling, Hamiltonian path navigation, and dynamic adaptation.
    """
    def __init__(self, capacity: int = 1024, dimensions: int = 3, load_factor_threshold: float = 0.75, config: Dict = {}):
        """
        Initialize the hash table.
        Args:
            capacity: Initial capacity of the hash table
            dimensions: Number of dimensions for the hash space (tunable by AGRM context)
            load_factor_threshold: When to resize the table
            config: Dictionary for additional MDHG-specific parameters
        """
        self.PHI = (1 + math.sqrt(5)) / 2 # Golden ratio [cite: 1018-1019]
        self.config = config # Store config for internal use

        # Core configuration
        self.capacity = max(capacity, 16) # Ensure minimum capacity
        self.dimensions = max(dimensions, 1) # Ensure at least 1 dimension
        self.load_factor_threshold = load_factor_threshold
        self.size = 0

        # Multi-dimensional organization [cite: 1012-1017]
        self.buildings = self._initialize_buildings()
        self.location_map = {} # Maps keys to their current location (building_id, region_type, location_spec)

        # Navigation components
        self.hamiltonian_paths = {} # Pre-computed paths for critical points [cite: 1020-1022, 1037]
        self.path_cache = {} # Cache of paths between points or for key sets
        self.shortcuts = {} # Direct connections between buildings/regions [cite: 1022]

        # Access pattern tracking
        self.access_history = deque(maxlen=config.get("mdhg_access_history_len", 100)) # Track recent accesses
        self.access_frequency = Counter() # Track frequency of key access
        self.co_access_matrix = defaultdict(Counter) # Track keys accessed together [cite: 1022]
        self.path_usage = Counter() # Track usage of cached paths

        # Statistics
        self.stats = {
            'puts': 0, 'gets': 0, 'hits': 0, 'misses': 0, 'collisions': 0,
            'probes_total': 0, 'max_probes': 0, 'reorganizations': 0,
            'resizes': 0, 'promotions_velocity': 0, 'relocations_from_velocity': 0,
            'clusters_relocated': 0
        }

        # Optimization timing
        self.last_minor_optimization = time.time()
        self.last_major_optimization = time.time()
        self.operations_since_optimization = 0

        # Initialize the structure (compute initial paths, etc.)
        self._initialize_structure()
        print(f"MDHGHashTable initialized: Capacity={self.capacity}, Dimensions={self.dimensions}, Buildings={len(self.buildings)}")

    def _initialize_buildings(self) -> Dict:
        """ Initialize the building structure based on golden ratio proportions. """
        # Determine number of buildings, ensuring at least 1
        building_count = max(1, int(math.log(max(2, self.capacity), self.PHI)))
        buildings = {}
        # Ensure base capacity calculation avoids division by zero
        base_capacity_per_building = self.capacity // building_count if building_count > 0 else self.capacity
        if base_capacity_per_building < 16: base_capacity_per_building = 16 # Ensure minimum size

        print(f"  MDHG: Initializing {building_count} buildings, base capacity per building: {base_capacity_per_building}")

        for b in range(building_count):
            building_id = f"B{b}"
            # Calculate regions using golden ratio [cite: 1018]
            # Ensure minimum sizes for regions
            velocity_region_size = max(4, int(base_capacity_per_building / (self.PHI ** 2)))
            core_region_base_size = max(8, int(velocity_region_size * self.PHI)) # Base size before dimensioning

            dimension_sizes = self._calculate_dimension_sizes(core_region_base_size)
            # Actual core capacity is product of dimension sizes
            core_capacity = math.prod(dimension_sizes) if dimension_sizes else 0

            print(f"    Building {building_id}: Velocity Region Size={velocity_region_size}, Core Capacity={core_capacity}, Dim Sizes={dimension_sizes}")

            buildings[building_id] = {
                'velocity_region': [None] * velocity_region_size, # Fast access [cite: 1022]
                'dimensional_core': {}, # Main storage, dict maps coords -> (key, value_tuple) [cite: 1022]
                'conflict_structures': {}, # Handles collisions beyond path probing [cite: 1022]
                'dimension_sizes': dimension_sizes, # For coordinate calculation
                'hot_keys': set(), # Keys frequently accessed in this building
                'access_count': 0, # Track building usage
                'core_capacity': core_capacity # Store calculated core capacity
            }
        return buildings

    def _calculate_dimension_sizes(self, core_region_base_size: int) -> List[int]:
        """ Calculate sizes for each dimension using golden ratio proportions. """
        if self.dimensions <= 0: return []
        # Estimate base size per dimension
        # Using geometric mean approach: base_size ^ dimensions ≈ core_region_base_size
        # Add epsilon to avoid potential log(0) or root(0) issues if base_size is tiny
        safe_base_size = max(1, core_region_base_size)
        base_size = max(2.0, safe_base_size ** (1.0/self.dimensions)) # Use float for calculation

        sizes = []
        product = 1.0
        # Scale dimensions using PHI, ensuring minimum size 2
        for i in range(self.dimensions):
            # Example scaling: could use other GR-based factors
            # Ensure denominator is safe
            phi_exponent = i / max(1.0, float(self.dimensions - 1))
            size_float = base_size / (self.PHI ** phi_exponent)
            size = max(2, int(round(size_float))) # Round before int conversion
            sizes.append(size)
            product *= size

        # Optional: Adjust sizes slightly if product is too far off target
        # This part requires careful balancing logic to avoid infinite loops or drastic changes
        # print(f"      Calculated dimension sizes: {sizes} (Product: {product}, Target Base: {core_region_base_size})")
        return sizes

    def _initialize_structure(self):
        """ Initialize the hash table structure with navigation components. """
        # Pre-compute critical Hamiltonian paths for each building [cite: 1037]
        print("  MDHG: Initializing structure (paths, shortcuts)...")
        for building_id, building in self.buildings.items():
            self._initialize_building_paths(building_id, building)
        # Initialize shortcuts between buildings
        self._initialize_building_shortcuts()
        print("  MDHG: Structure initialization complete.")


    def _initialize_building_paths(self, building_id: str, building: Dict):
        """ Initialize Hamiltonian paths for critical points in a building. """
        dimension_sizes = building.get('dimension_sizes')
        if not dimension_sizes:
            # print(f"    Skipping path init for {building_id}: No dimensions.")
            return # Skip if no dimensions

        # Generate critical points (corners, center)
        critical_points = set()
        # Add corner points
        corners = self._generate_corner_points(dimension_sizes)
        critical_points.update(corners)
        # Add center point
        center = tuple(d // 2 for d in dimension_sizes)
        critical_points.add(center)

        # Compute and store paths for these critical points
        building_paths = {}
        computed_count = 0
        for point in critical_points:
            # Ensure point is valid within dimensions
            if len(point) != self.dimensions: continue
            valid_point = all(0 <= point[i] < dimension_sizes[i] for i in range(self.dimensions))

            if valid_point:
                path = self._compute_hamiltonian_path(building_id, point)
                if path: # Only store if path computation succeeds
                    path_key = (building_id, point)
                    building_paths[path_key] = path # Store paths per building first
                    computed_count += 1

        self.hamiltonian_paths.update(building_paths) # Add building paths to global store
        # print(f"    Initialized {computed_count} Hamiltonian paths for building {building_id}.")


    def _generate_corner_points(self, dimension_sizes: List[int]) -> List[Tuple]:
        """ Generate corner points for a multi-dimensional space. """
        if not dimension_sizes: return []
        corners = []
        num_dims = len(dimension_sizes)
        num_corners = 2 ** num_dims
        for i in range(num_corners):
            corner = []
            for d in range(num_dims):
                # Use bit masking to determine min (0) or max (size-1) for each dimension
                if (i >> d) & 1:
                    corner.append(max(0, dimension_sizes[d] - 1)) # Use max index
                else:
                    corner.append(0) # Use min index
            corners.append(tuple(corner))
        return corners

    def _initialize_building_shortcuts(self):
        """ Initialize shortcuts between buildings. """
        building_ids = list(self.buildings.keys())
        shortcuts_created = 0
        # Create shortcuts only if there's more than one building
        if len(building_ids) > 1:
            for i, b1 in enumerate(building_ids):
                for j, b2 in enumerate(building_ids):
                    if i != j:
                        # Create bidirectional shortcuts
                        if self._create_building_shortcut(b1, b2):
                            shortcuts_created += 1
        # print(f"  Initialized {shortcuts_created} building shortcuts.")

    def _create_building_shortcut(self, building1: str, building2: str) -> bool:
        """ Create a shortcut between two buildings with default connection points. """
        building1_data = self.buildings.get(building1)
        building2_data = self.buildings.get(building2)
        # Check if dimensions are valid before creating shortcut
        if not building1_data or not building2_data or \
           not building1_data.get('dimension_sizes') or not building2_data.get('dimension_sizes') or \
           len(building1_data['dimension_sizes']) != self.dimensions or \
           len(building2_data['dimension_sizes']) != self.dimensions:
            # print(f"Warning: Cannot create shortcut between {building1} and {building2} due to invalid dimensions.")
            return False # Cannot create shortcut if building data is incomplete

        # Use center points as default connection points
        center1 = tuple(d // 2 for d in building1_data['dimension_sizes'])
        center2 = tuple(d // 2 for d in building2_data['dimension_sizes'])

        shortcut_key = (building1, building2)
        self.shortcuts[shortcut_key] = {
            'entry_point': center1, # Entry point in building1
            'exit_point': center2,  # Exit point in building2 (conceptually)
            'cost': 1.0 / self.PHI, # Lower cost than regular traversal (heuristic)
            'usage_count': 0
        }
        return True

    def _compute_hamiltonian_path(self, building_id: str, start_coords: Tuple) -> List[Tuple]:
        """
        Compute a Hamiltonian-like path (visits many points uniquely) starting from coordinates.
        Uses GR steps. This is a heuristic path, not guaranteed to be truly Hamiltonian or optimal length.
        """
        building = self.buildings.get(building_id)
        if not building or not building.get('dimension_sizes'): return []
        dimension_sizes = building['dimension_sizes']

        # Basic validation of start_coords
        if len(start_coords) != self.dimensions: return []
        if not all(0 <= start_coords[i] < dimension_sizes[i] for i in range(self.dimensions)): return []

        path = [start_coords]
        current = list(start_coords)
        visited = {start_coords}

        # Determine path length heuristic
        total_core_points = math.prod(dimension_sizes) if dimension_sizes else 0
        if total_core_points == 0: return path # Path is just the start point

        path_length_limit = min(total_core_points, self.config.get("mdhg_path_length_limit", 1000))
        # Aim for a path length that covers a reasonable fraction, e.g., sqrt or similar heuristic
        path_length_target = max(self.dimensions * 2, int(math.sqrt(total_core_points) * 2)) # Cover more?
        path_length = min(path_length_limit, path_length_target)

        # Use golden ratio for dimension selection and step direction bias
        for step in range(1, path_length):
            # Choose dimension based on golden ratio progression [cite: 1021]
            dim_choice = int((step * self.PHI) % self.dimensions)

            # Determine step direction (+1 or -1) based on another GR sequence
            direction_bias = (step * self.PHI**2) % 1.0
            step_dir = 1 if direction_bias < 0.5 else -1

            # Try moving in the chosen dimension and direction
            next_coord_list = list(current)
            next_coord_list[dim_choice] = (next_coord_list[dim_choice] + step_dir + dimension_sizes[dim_choice]) % dimension_sizes[dim_choice] # Ensure positive result
            next_coords = tuple(next_coord_list)

            if next_coords not in visited:
                path.append(next_coords)
                visited.add(next_coords)
                current = next_coord_list
            else:
                # Collision: Try alternative dimensions or directions (simple linear probe)
                found_alternative = False
                for alt_offset in range(1, self.dimensions + 1): # Try all dimensions + opposite dir
                    # Try alternative dimension, original direction
                    alt_dim = (dim_choice + alt_offset) % self.dimensions
                    alt_coord_list = list(current)
                    alt_coord_list[alt_dim] = (alt_coord_list[alt_dim] + step_dir + dimension_sizes[alt_dim]) % dimension_sizes[alt_dim]
                    alt_coords = tuple(alt_coord_list)
                    if alt_coords not in visited:
                        path.append(alt_coords)
                        visited.add(alt_coords)
                        current = alt_coord_list
                        found_alternative = True
                        break

                    # Try alternative dimension, opposite direction
                    alt_coord_list = list(current)
                    alt_coord_list[alt_dim] = (alt_coord_list[alt_dim] - step_dir + dimension_sizes[alt_dim]) % dimension_sizes[alt_dim]
                    alt_coords = tuple(alt_coord_list)
                    if alt_coords not in visited:
                        path.append(alt_coords)
                        visited.add(alt_coords)
                        current = alt_coord_list
                        found_alternative = True
                        break

                # If no alternative found after checking all dims/dirs, stop path
                if not found_alternative:
                    # print(f"      Path generation stuck at step {step}, coords {current}")
                    break # Stop if stuck

        return path

    # --- Hashing Functions ---
    def _hash(self, key: Any) -> int:
        """ Primary hash function. Using MurmurHash for better distribution. """
        return self._murmur_hash(key)

    def _secondary_hash(self, key: Any) -> int:
        """ Secondary hash function for specific regions like velocity. Using FNV. """
        return self._fnv_hash(key)

    def _murmur_hash(self, key: Any) -> int:
        """ MurmurHash3 32-bit implementation. """
        key_bytes = str(key).encode('utf-8')
        length = len(key_bytes)
        seed = 0x9747b28c # Example seed
        c1 = 0xcc9e2d51
        c2 = 0x1b873593
        r1 = 15
        r2 = 13
        m = 5
        n = 0xe6546b64
        hash_value = seed

        nblocks = length // 4
        for i in range(nblocks):
            idx = i * 4
            k = (key_bytes[idx] |
                 (key_bytes[idx + 1] << 8) |
                 (key_bytes[idx + 2] << 16) |
                 (key_bytes[idx + 3] << 24))
            k = (k * c1) & 0xFFFFFFFF
            k = ((k << r1) | (k >> (32 - r1))) & 0xFFFFFFFF
            k = (k * c2) & 0xFFFFFFFF
            hash_value ^= k
            hash_value = ((hash_value << r2) | (hash_value >> (32 - r2))) & 0xFFFFFFFF
            hash_value = ((hash_value * m) + n) & 0xFFFFFFFF

        tail_index = nblocks * 4
        k = 0
        tail_size = length & 3
        if tail_size >= 3: k ^= key_bytes[tail_index + 2] << 16
        if tail_size >= 2: k ^= key_bytes[tail_index + 1] << 8
        if tail_size >= 1: k ^= key_bytes[tail_index]
        if tail_size > 0:
            k = (k * c1) & 0xFFFFFFFF
            k = ((k << r1) | (k >> (32 - r1))) & 0xFFFFFFFF
            k = (k * c2) & 0xFFFFFFFF
            hash_value ^= k

        hash_value ^= length
        hash_value ^= hash_value >> 16
        hash_value = (hash_value * 0x85ebca6b) & 0xFFFFFFFF
        hash_value ^= hash_value >> 13
        hash_value = (hash_value * 0xc2b2ae35) & 0xFFFFFFFF
        hash_value ^= hash_value >> 16

        return abs(hash_value) # Ensure positive

    def _fnv_hash(self, key: Any) -> int:
        """ FNV-1a 32-bit hash implementation. """
        key_bytes = str(key).encode('utf-8')
        fnv_prime = 0x01000193 # 16777619
        fnv_offset_basis = 0x811c9dc5 # 2166136261
        hash_value = fnv_offset_basis
        for byte in key_bytes:
            hash_value ^= byte
            hash_value = (hash_value * fnv_prime) & 0xFFFFFFFF
        return abs(hash_value) # Ensure positive

    def _hash_to_building(self, key: Any) -> str:
        """ Determine which building should contain a key using primary hash. """
        if not self.buildings: raise ValueError("MDHGHashTable has no buildings initialized.")
        hash_value = self._hash(key)
        building_idx = hash_value % len(self.buildings)
        return f"B{building_idx}"

    def _hash_to_velocity_index(self, key: Any, building_id: str) -> int:
        """ Calculate velocity region index using secondary hash. """
        building = self.buildings.get(building_id)
        if not building: raise ValueError(f"Building {building_id} not found.")
        velocity_size = len(building['velocity_region'])
        if velocity_size == 0: return 0
        return self._secondary_hash(key) % velocity_size

    def _hash_to_coords(self, key: Any, building_id: str) -> Optional[Tuple]:
        """ Calculate multi-dimensional coordinates using variations of primary hash. """
        building = self.buildings.get(building_id)
        if not building: raise ValueError(f"Building {building_id} not found.")
        dimension_sizes = building.get('dimension_sizes')
        if not dimension_sizes or len(dimension_sizes) != self.dimensions:
            return None # Cannot calculate coords if dimensions mismatch

        coords = []
        # Use primary hash and modify it for each dimension to get variation
        base_hash = self._hash(key)
        for i in range(self.dimensions):
            # Simple variation: XOR with dimension index and shift
            dim_hash = (base_hash ^ (i * 0x9e3779b9)) # Use golden ratio conjugate for mixing
            dim_hash = (dim_hash >> i) | (dim_hash << (32 - i)) & 0xFFFFFFFF # Rotate
            coord_val = abs(dim_hash) % dimension_sizes[i]
            coords.append(coord_val)
        return tuple(coords)

    def _hash_to_conflict_key(self, key: Any, coords: Tuple) -> int:
        """ Create a conflict key combining key hash and coordinates hash. """
        key_hash = self._hash(key)
        coords_hash = hash(coords) # Python's hash for tuple
        return abs(key_hash ^ coords_hash)

    # --- Core Put/Get/Remove ---

    def put(self, key: Any, value: Any) -> None:
        """
        Insert a key-value pair into the hash table.
        Handles routing, velocity region, core, collisions, and conflict structures.
        Value should be (actual_value, metadata_dict) for AGRM integration.
        """
        self.stats['puts'] += 1
        self.operations_since_optimization += 1

        # 1. Determine Target Building
        building_id = self._hash_to_building(key)
        building = self.buildings.get(building_id)
        if not building: # Fallback if building calculation failed somehow
            if not self.buildings: raise RuntimeError("MDHG Hash Table has no buildings.")
            building_id = list(self.buildings.keys())[0]
            building = self.buildings[building_id]
            print(f"Warning: Falling back to building {building_id} for key {key}.")
        building['access_count'] += 1

        # 2. Try Velocity Region
        velocity_idx = self._hash_to_velocity_index(key, building_id)
        if 0 <= velocity_idx < len(building['velocity_region']):
            velocity_entry = building['velocity_region'][velocity_idx]
            if velocity_entry is None:
                building['velocity_region'][velocity_idx] = (key, value)
                self.location_map[key] = (building_id, 'velocity', velocity_idx)
                self.size += 1
                self._update_access_patterns(key)
                self._check_optimization_and_resize()
                return
            elif velocity_entry[0] == key:
                building['velocity_region'][velocity_idx] = (key, value) # Update
                self._update_access_patterns(key)
                return
            # Else: Collision in velocity, proceed to core

        # 3. Try Dimensional Core
        coords = self._hash_to_coords(key, building_id)
        if coords is not None:
            if coords not in building['dimensional_core']:
                building['dimensional_core'][coords] = (key, value)
                self.location_map[key] = (building_id, 'dimensional', coords)
                self.size += 1
                self._update_access_patterns(key)
                self._check_optimization_and_resize()
                return
            elif building['dimensional_core'][coords][0] == key:
                building['dimensional_core'][coords] = (key, value) # Update
                self._update_access_patterns(key)
                return
            else:
                # Collision in dimensional core
                self.stats['collisions'] += 1
                # 4. Follow Hamiltonian Path
                new_coords, probes = self._follow_hamiltonian_path_for_put(building_id, coords)
                self.stats['probes_total'] += probes
                self.stats['max_probes'] = max(self.stats['max_probes'], probes)
                if new_coords:
                    building['dimensional_core'][new_coords] = (key, value)
                    self.location_map[key] = (building_id, 'dimensional', new_coords)
                    self.size += 1
                    self._update_access_patterns(key)
                    self._check_optimization_and_resize()
                    return
                # Else: Path probing failed, proceed to conflict structure
        else: # Coords calculation failed, go directly to conflict structure
             coords = tuple([0]*self.dimensions) # Use fallback coords for conflict key


        # 5. Use Conflict Structure
        conflict_key_hash = self._hash_to_conflict_key(key, coords)
        if conflict_key_hash not in building['conflict_structures']:
            building['conflict_structures'][conflict_key_hash] = {} # Use dict as simple conflict list

        # Store/update in conflict structure
        if key not in building['conflict_structures'][conflict_key_hash]:
            self.size += 1 # Increment size only if new key overall
        building['conflict_structures'][conflict_key_hash][key] = value
        self.location_map[key] = (building_id, 'conflict', conflict_key_hash)
        self._update_access_patterns(key)
        self._check_optimization_and_resize()


    def get(self, key: Any) -> Any:
        """ Retrieve value tuple (val, meta) or None. """
        self.stats['gets'] += 1
        self.operations_since_optimization += 1
        probes = 0

        # 1. Check Location Map Cache
        loc_info = self.location_map.get(key)
        if loc_info:
            building_id, region_type, location_spec = loc_info
            building = self.buildings.get(building_id)
            if building:
                building['access_count'] += 1
                value = None
                if region_type == 'velocity':
                    probes += 1
                    if 0 <= location_spec < len(building['velocity_region']):
                        entry = building['velocity_region'][location_spec]
                        if entry and entry[0] == key: value = entry[1]
                elif region_type == 'dimensional':
                    probes += 1
                    entry = building['dimensional_core'].get(location_spec)
                    if entry and entry[0] == key: value = entry[1]
                elif region_type == 'conflict':
                    probes += 1
                    conflict_map = building['conflict_structures'].get(location_spec)
                    if conflict_map: value = conflict_map.get(key)

                if value is not None:
                    self.stats['hits'] += 1
                    self._update_stats_and_patterns(key, probes)
                    return value
                else: # Location map was stale/incorrect
                     if key in self.location_map: del self.location_map[key]
            else: # Invalid building in map
                 if key in self.location_map: del self.location_map[key]
            # Fall through to full search if map check failed

        # 2. Full Search (if map failed or key not in map)
        primary_building_id = self._hash_to_building(key)
        value, building_probes = self._search_building(primary_building_id, key)
        probes += building_probes
        if value is not None:
            self._update_stats_and_patterns(key, probes)
            return value

        # 3. Search Other Buildings (Only if collisions can spill buildings - assumed NO for now)

        # 4. Key Not Found
        self.stats['misses'] += 1
        self._update_stats_and_patterns(key, probes, found=False)
        return None

    def _update_stats_and_patterns(self, key: Any, probes: int, found: bool = True):
         """ Helper to update stats and access patterns after a get attempt. """
         self.stats['probes_total'] += probes
         self.stats['max_probes'] = max(self.stats['max_probes'], probes)
         if found:
             self._update_access_patterns(key)


    def _search_building(self, building_id: str, key: Any) -> Tuple[Any, int]:
        """ Search for a key within a specific building. Returns (Value, probes). """
        building = self.buildings.get(building_id)
        if not building: return None, 0
        building['access_count'] += 1
        probes = 0

        # Check velocity
        velocity_idx = self._hash_to_velocity_index(key, building_id)
        probes += 1
        if 0 <= velocity_idx < len(building['velocity_region']):
            entry = building['velocity_region'][velocity_idx]
            if entry and entry[0] == key:
                self.stats['hits'] += 1
                self.location_map[key] = (building_id, 'velocity', velocity_idx)
                return entry[1], probes

        # Check dimensional core primary
        coords = self._hash_to_coords(key, building_id)
        if coords is not None:
            probes += 1
            entry = building['dimensional_core'].get(coords)
            if entry and entry[0] == key:
                self.stats['hits'] += 1
                self.location_map[key] = (building_id, 'dimensional', coords)
                return entry[1], probes

            # Check conflict structure based on primary coords
            conflict_key_hash = self._hash_to_conflict_key(key, coords)
            probes += 1
            conflict_map = building['conflict_structures'].get(conflict_key_hash)
            if conflict_map and key in conflict_map:
                self.stats['hits'] += 1
                self.location_map[key] = (building_id, 'conflict', conflict_key_hash)
                return conflict_map[key], probes

            # Follow Hamiltonian path if not found yet
            value, path_probes = self._search_path(building_id, coords, key)
            probes += path_probes
            if value is not None:
                # Hit, location map update happen inside _search_path
                return value, probes

        else: # Coords failed, check conflict based on fallback
            fallback_coords = tuple([0]*self.dimensions)
            conflict_key_hash = self._hash_to_conflict_key(key, fallback_coords)
            probes += 1
            conflict_map = building['conflict_structures'].get(conflict_key_hash)
            if conflict_map and key in conflict_map:
                self.stats['hits'] += 1
                self.location_map[key] = (building_id, 'conflict', conflict_key_hash)
                return conflict_map[key], probes

        # Key not found in this building
        return None, probes


    def _search_path(self, building_id: str, start_coords: Tuple, key: Any) -> Tuple[Any, int]:
         """ Search for a key along a Hamiltonian path starting near coords. """
         building = self.buildings.get(building_id)
         if not building or not self.hamiltonian_paths: return None, 0

         nearest_path_key = self._find_nearest_path_key(building_id, start_coords)
         if not nearest_path_key: return None, 0
         path = self.hamiltonian_paths[nearest_path_key]
         if not path: return None, 0

         start_idx = self._find_path_start_index(path, start_coords)
         max_probes = self.config.get("mdhg_max_search_probes", 20)
         probes = 0
         path_len = len(path)
         forward_steps = 0
         backward_steps = 0

         while probes < max_probes and (forward_steps + backward_steps) < path_len:
             # Check forward
             idx = (start_idx + forward_steps) % path_len
             check_coords = path[idx]
             probes += 1
             entry = building['dimensional_core'].get(check_coords)
             if entry and entry[0] == key:
                 self.stats['hits'] += 1
                 self.location_map[key] = (building_id, 'dimensional', check_coords)
                 return entry[1], probes
             forward_steps += 1

             if probes >= max_probes or (forward_steps + backward_steps) >= path_len: break

             # Check backward (if path has more than one point)
             if backward_steps < forward_steps and path_len > 1:
                 idx = (start_idx - backward_steps - 1 + path_len) % path_len
                 check_coords = path[idx]
                 probes += 1
                 entry = building['dimensional_core'].get(check_coords)
                 if entry and entry[0] == key:
                     self.stats['hits'] += 1
                     self.location_map[key] = (building_id, 'dimensional', check_coords)
                     return entry[1], probes
                 backward_steps += 1

         return None, probes # Not found along path segment

    def _follow_hamiltonian_path_for_put(self, building_id: str, start_coords: Tuple) -> Tuple[Optional[Tuple], int]:
        """ Follow a Hamiltonian path to find an empty slot for insertion. """
        building = self.buildings.get(building_id)
        if not building or not self.hamiltonian_paths: return None, 0

        nearest_path_key = self._find_nearest_path_key(building_id, start_coords)
        if not nearest_path_key: return None, 0
        path = self.hamiltonian_paths[nearest_path_key]
        if not path: return None, 0

        start_idx = self._find_path_start_index(path, start_coords)
        max_probes = self.config.get("mdhg_max_put_probes", 20)
        probes = 0
        path_len = len(path)
        forward_steps = 0
        backward_steps = 0

        while probes < max_probes and (forward_steps + backward_steps) < path_len:
            # Check forward
            idx = (start_idx + forward_steps) % path_len
            coords = path[idx]
            probes += 1
            if coords not in building['dimensional_core']:
                return coords, probes
            forward_steps += 1

            if probes >= max_probes or (forward_steps + backward_steps) >= path_len: break

            # Check backward
            if backward_steps < forward_steps and path_len > 1:
                idx = (start_idx - backward_steps - 1 + path_len) % path_len
                coords = path[idx]
                probes += 1
                if coords not in building['dimensional_core']:
                    return coords, probes
                backward_steps += 1

        return None, probes # No empty slot found

    def remove(self, key: Any) -> bool:
        """ Remove a key-value pair. """
        # 1. Check Location Map first
        loc_info = self.location_map.get(key)
        removed = False
        if loc_info:
            building_id, region_type, location_spec = loc_info
            building = self.buildings.get(building_id)
            if building:
                if region_type == 'velocity':
                    if 0 <= location_spec < len(building['velocity_region']):
                        entry = building['velocity_region'][location_spec]
                        if entry and entry[0] == key:
                            building['velocity_region'][location_spec] = None
                            removed = True
                elif region_type == 'dimensional':
                    entry = building['dimensional_core'].get(location_spec)
                    if entry and entry[0] == key:
                        del building['dimensional_core'][location_spec]
                        removed = True
                elif region_type == 'conflict':
                    conflict_map = building['conflict_structures'].get(location_spec)
                    if conflict_map and key in conflict_map:
                        del conflict_map[key]
                        if not conflict_map: del building['conflict_structures'][location_spec]
                        removed = True

                if removed:
                    del self.location_map[key]
                    self.size -= 1
                    return True
                else: # Location map was stale
                    del self.location_map[key]
            else: # Invalid building in map
                 del self.location_map[key]

        # 2. Full Search if map failed or key not in map
        primary_building_id = self._hash_to_building(key)
        if self._remove_from_building(primary_building_id, key):
            return True

        # 3. Search other buildings (if spillover possible - assuming not)

        return False # Key not found

    def _remove_from_building(self, building_id: str, key: Any) -> bool:
         """ Removes key from a specific building. Helper for remove(). """
         building = self.buildings.get(building_id)
         if not building: return False

         # Check velocity
         velocity_idx = self._hash_to_velocity_index(key, building_id)
         if 0 <= velocity_idx < len(building['velocity_region']):
             entry = building['velocity_region'][velocity_idx]
             if entry and entry[0] == key:
                 building['velocity_region'][velocity_idx] = None
                 if key in self.location_map: del self.location_map[key]
                 self.size -= 1
                 return True

         # Check core and conflict (primary coords)
         coords = self._hash_to_coords(key, building_id)
         if coords is not None:
             entry = building['dimensional_core'].get(coords)
             if entry and entry[0] == key:
                 del building['dimensional_core'][coords]
                 if key in self.location_map: del self.location_map[key]
                 self.size -= 1
                 return True

             conflict_key_hash = self._hash_to_conflict_key(key, coords)
             conflict_map = building['conflict_structures'].get(conflict_key_hash)
             if conflict_map and key in conflict_map:
                 del conflict_map[key]
                 if not conflict_map: del building['conflict_structures'][conflict_key_hash]
                 if key in self.location_map: del self.location_map[key]
                 self.size -= 1
                 return True

             # Search path if necessary (more complex removal)
             # Simplified: Assume if not at primary/velocity/conflict, it's not easily removable

         else: # Coords failed, check conflict based on fallback
              fallback_coords = tuple([0]*self.dimensions)
              conflict_key_hash = self._hash_to_conflict_key(key, fallback_coords)
              conflict_map = building['conflict_structures'].get(conflict_key_hash)
              if conflict_map and key in conflict_map:
                  del conflict_map[key]
                  if not conflict_map: del building['conflict_structures'][conflict_key_hash]
                  if key in self.location_map: del self.location_map[key]
                  self.size -= 1
                  return True

         return False

    # --- Helper methods for path finding ---
    def _find_nearest_path_key(self, building_id: str, coords: Tuple) -> Optional[Tuple]:
        """ Find the key (building_id, start_coords) of the nearest pre-computed path. """
        min_dist_sq = float('inf')
        nearest_key = None
        if coords is None: return None

        # Filter paths belonging to the target building
        building_paths = {k: v for k, v in self.hamiltonian_paths.items() if k[0] == building_id}
        if not building_paths: return None

        for path_key, path_data in building_paths.items():
            path_start_coords = path_key[1]
            # Ensure coordinates have same dimension before calculating distance
            if len(coords) != len(path_start_coords): continue
            # Calculate squared Euclidean distance for efficiency
            dist_sq = sum((c1 - c2)**2 for c1, c2 in zip(coords, path_start_coords))
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest_key = path_key
        return nearest_key

    def _find_path_start_index(self, path: List[Tuple], coords: Tuple) -> int:
        """ Find the index in a path closest to the given coordinates. """
        if not path: return 0
        if coords is None: return 0

        min_dist_sq = float('inf')
        best_idx = 0
        for i, path_coords in enumerate(path):
             # Ensure coordinates have same dimension
             if len(coords) != len(path_coords): continue
             dist_sq = sum((c1 - c2)**2 for c1, c2 in zip(coords, path_coords))
             if dist_sq < min_dist_sq:
                 min_dist_sq = dist_sq
                 best_idx = i
             if min_dist_sq == 0: break # Exact match found
        return best_idx

    # --- Dynamic Adaptation & Optimization (Placeholders - Require full logic) ---

    def _update_access_patterns(self, key: Any) -> None:
        """ Update access frequency, history, and co-access matrix. """
        self.access_history.append(key)
        self.access_frequency[key] += 1
        # Update co-access (simplified)
        if len(self.access_history) > 1:
            last_key = self.access_history[-2]
            if last_key != key:
                self.co_access_matrix[last_key][key] += 1
                self.co_access_matrix[key][last_key] += 1

        # Trigger potential promotion based on frequency
        promo_threshold = self.config.get("mdhg_velocity_promo_threshold", 10)
        if self.access_frequency[key] >= promo_threshold:
            if key in self.location_map:
                building_id = self.location_map[key][0]
                self._consider_velocity_promotion(key, building_id)


    def _consider_velocity_promotion(self, key: Any, building_id: str) -> None:
         """ Consider promoting a key to the velocity region if beneficial. """
         building = self.buildings.get(building_id)
         if not building or key not in self.location_map: return

         current_loc = self.location_map[key]
         if current_loc[1] == 'velocity': return # Already there

         target_idx = self._hash_to_velocity_index(key, building_id)
         if not (0 <= target_idx < len(building['velocity_region'])): return # Invalid index

         current_entry = building['velocity_region'][target_idx]
         key_freq = self.access_frequency.get(key, 0)
         should_promote = False

         if current_entry is None:
             should_promote = True
         else:
             occupant_key = current_entry[0]
             occupant_freq = self.access_frequency.get(occupant_key, 0)
             # Promote if new key is significantly more frequent (using PHI ratio)
             if key_freq > occupant_freq * self.PHI:
                 should_promote = True
                 # Relocate the occupant if it's being evicted
                 print(f"    MDHG: Evicting {occupant_key} (freq {occupant_freq}) from velocity for {key} (freq {key_freq})")
                 self._relocate_from_velocity(occupant_key, current_entry[1], building_id)
                 self.stats['relocations_from_velocity'] += 1

         if should_promote:
             # Get current value (get() handles finding it)
             value_tuple = self.get(key) # This will update access patterns again
             if value_tuple is not None:
                 print(f"    MDHG: Promoting key {key} to velocity region in {building_id}")
                 # Remove from old location BEFORE putting in new one
                 self._remove_from_current_location(key) # Removes from core/conflict
                 building['velocity_region'][target_idx] = (key, value_tuple)
                 self.location_map[key] = (building_id, 'velocity', target_idx) # Update location map
                 self.stats['promotions_velocity'] += 1


    def _relocate_from_velocity(self, key: Any, value: Any, building_id: str) -> None:
        """ Relocate a key evicted from velocity region back to core/conflict. """
        # This is essentially a 'put' operation, but we know it's not in velocity.
        # We need to ensure size isn't incremented again.
        building = self.buildings.get(building_id)
        if not building: return

        # Try dimensional core first
        coords = self._hash_to_coords(key, building_id)
        if coords is not None:
            if coords not in building['dimensional_core']:
                building['dimensional_core'][coords] = (key, value)
                self.location_map[key] = (building_id, 'dimensional', coords)
                return
            else: # Collision
                new_coords, _ = self._follow_hamiltonian_path_for_put(building_id, coords)
                if new_coords:
                    building['dimensional_core'][new_coords] = (key, value)
                    self.location_map[key] = (building_id, 'dimensional', new_coords)
                    return
        # Fallback to conflict structure
        fallback_coords = coords if coords is not None else tuple([0]*self.dimensions)
        conflict_key_hash = self._hash_to_conflict_key(key, fallback_coords)
        if conflict_key_hash not in building['conflict_structures']:
            building['conflict_structures'][conflict_key_hash] = {}
        building['conflict_structures'][conflict_key_hash][key] = value
        self.location_map[key] = (building_id, 'conflict', conflict_key_hash)


    def _remove_from_current_location(self, key: Any) -> None:
        """ Helper to remove key from core/conflict AFTER checking location map. """
        if key not in self.location_map: return
        building_id, region_type, location_spec = self.location_map[key]
        building = self.buildings.get(building_id)
        if not building: return

        removed = False
        if region_type == 'dimensional':
            if location_spec in building['dimensional_core'] and building['dimensional_core'][location_spec][0] == key:
                del building['dimensional_core'][location_spec]
                removed = True
        elif region_type == 'conflict':
            conflict_map = building['conflict_structures'].get(location_spec)
            if conflict_map and key in conflict_map:
                del conflict_map[key]
                if not conflict_map: del building['conflict_structures'][location_spec]
                removed = True
        # Note: We don't delete from location map here, caller handles final update


    def _check_optimization_and_resize(self) -> None:
        """ Check if optimization or resize is needed based on operations or time. """
        current_time = time.time()
        ops_threshold_minor = self.config.get("mdhg_ops_thresh_minor", 100)
        time_threshold_minor = self.config.get("mdhg_time_thresh_minor", 1.0)
        ops_threshold_major = self.config.get("mdhg_ops_thresh_major", 1000)
        time_threshold_major = self.config.get("mdhg_time_thresh_major", 5.0)

        needs_minor_opt = (self.operations_since_optimization > 0 and self.operations_since_optimization % ops_threshold_minor == 0) or \
                          (current_time - self.last_minor_optimization >= time_threshold_minor)
        needs_major_opt = (self.operations_since_optimization > 0 and self.operations_since_optimization % ops_threshold_major == 0) or \
                          (current_time - self.last_major_optimization >= time_threshold_major)

        if needs_major_opt:
            # print("    MDHG: Performing major optimization...")
            self._perform_major_optimization()
            self.last_major_optimization = current_time
            self.last_minor_optimization = current_time # Reset minor timer too
            self.operations_since_optimization = 0 # Reset counter
        elif needs_minor_opt:
            # print("    MDHG: Performing minor optimization...")
            self._perform_minor_optimization()
            self.last_minor_optimization = current_time
            # Don't reset major timer or op counter on minor opt

        # Check resize AFTER potential optimizations
        current_load_factor = self.size / self.capacity if self.capacity > 0 else 1.0
        if current_load_factor > self.load_factor_threshold:
            print(f"    MDHG: Load factor {current_load_factor:.2f} exceeds threshold {self.load_factor_threshold}. Resizing.")
            self._resize()

    def _perform_minor_optimization(self) -> None:
        """ Perform minor optimizations like promoting hot keys. """
        hot_key_count = self.config.get("mdhg_hot_key_count", 100)
        hot_key_min_freq = self.config.get("mdhg_hot_key_min_freq", 5)
        hot_keys_global = self.access_frequency.most_common(hot_key_count)
        promoted_count = 0
        for key, freq in hot_keys_global:
            if freq < hot_key_min_freq: break
            if key in self.location_map:
                building_id = self.location_map[key][0]
                # This call might result in promotion
                self._consider_velocity_promotion(key, building_id)
                # Check if promotion actually happened (location map changed)
                if key in self.location_map and self.location_map[key][1] == 'velocity':
                     promoted_count += 1
        # if promoted_count > 0: print(f"      MDHG Minor Opt: Considered {len(hot_keys_global)} hot keys, promoted {promoted_count} to velocity.")


    def _perform_major_optimization(self) -> None:
        """ Perform major structural reorganizations. """
        self.stats['reorganizations'] += 1
        start_time = time.time()
        # print("      MDHG Major Opt: Updating shortcuts...")
        # self._update_shortcuts() # Placeholder
        # print("      MDHG Major Opt: Identifying and relocating clusters...")
        # self._identify_and_relocate_key_clusters() # Placeholder
        # print("      MDHG Major Opt: Pruning path cache...")
        # self._prune_path_cache() # Placeholder
        end_time = time.time()
        print(f"    MDHG: Major optimization complete in {end_time - start_time:.4f}s (Placeholders used).")


    def _update_shortcuts(self) -> None:
        """ Placeholder: Update shortcuts based on observed usage patterns. """
        # Requires tracking inter-building traversals or using co-access matrix across buildings
        pass

    def _identify_and_relocate_key_clusters(self) -> None:
        """ Placeholder: Identify clusters of co-accessed keys and move them closer. """
        # Requires graph analysis of co_access_matrix and complex relocation logic
        clusters_found = 0
        # ... implementation needed ...
        if clusters_found > 0:
            self.stats['clusters_relocated'] += clusters_found
            # print(f"        MDHG Cluster Opt: Relocated {clusters_found} key clusters.")
        pass

    def _prune_path_cache(self) -> None:
        """ Placeholder: Prune the path cache based on usage or recency. """
        max_cache_size = self.config.get("mdhg_path_cache_max_size", 100)
        if len(self.path_cache) > max_cache_size:
            # Simple prune: Keep top 50% most used
            keep_count = max_cache_size // 2
            sorted_usage = sorted(self.path_usage.items(), key=lambda item: item[1], reverse=True)
            keys_to_keep = {key for key, usage in sorted_usage[:keep_count]}
            old_size = len(self.path_cache)
            self.path_cache = {k: v for k, v in self.path_cache.items() if k in keys_to_keep}
            self.path_usage = {k: v for k, v in self.path_usage.items() if k in keys_to_keep}
            # print(f"        MDHG Cache Prune: Reduced path cache from {old_size} to {len(self.path_cache)} entries.")
        pass

    def _resize(self) -> None:
        """ Resize the hash table when load factor is exceeded. """
        self.stats['resizes'] += 1
        old_capacity = self.capacity
        # Increase capacity using golden ratio
        new_capacity = max(old_capacity + 1, int(old_capacity * self.PHI * 1.1)) # Add buffer
        print(f"    MDHG Resize: Increasing capacity from {old_capacity} to {new_capacity}")

        # Store old data temporarily
        old_items = []
        for key, loc_info in self.location_map.items():
            # Retrieve value from old structure before wiping it
            building_id_old, region_type_old, location_spec_old = loc_info
            building_old = self.buildings.get(building_id_old)
            value_tuple = None
            if building_old:
                if region_type_old == 'velocity':
                    if 0 <= location_spec_old < len(building_old['velocity_region']):
                        entry = building_old['velocity_region'][location_spec_old]
                        if entry and entry[0] == key: value_tuple = entry[1]
                elif region_type_old == 'dimensional':
                    entry = building_old['dimensional_core'].get(location_spec_old)
                    if entry and entry[0] == key: value_tuple = entry[1]
                elif region_type_old == 'conflict':
                    conflict_map = building_old['conflict_structures'].get(location_spec_old)
                    if conflict_map: value_tuple = conflict_map.get(key)
            if value_tuple is not None:
                old_items.append((key, value_tuple))
            # else: print(f"Warning: Could not retrieve value for key {key} during resize.")

        # Re-initialize with new capacity
        self.capacity = new_capacity
        self.size = 0 # Reset size, will be repopulated
        self.buildings = self._initialize_buildings()
        self.location_map = {} # Clear location map
        self._initialize_structure() # Recompute paths etc. for new structure

        # Rehash all elements
        print(f"    MDHG Resize: Rehashing {len(old_items)} elements...")
        rehash_start_time = time.time()
        for key, value_tuple in old_items:
            self.put(key, value_tuple) # Re-insert into the new structure
        rehash_end_time = time.time()
        print(f"    MDHG Resize: Rehashing complete in {rehash_end_time - rehash_start_time:.4f}s. New size: {self.size}")

        # Reset optimization timers after resize
        self.last_minor_optimization = time.time()
        self.last_major_optimization = time.time()
        self.operations_since_optimization = 0

# ==============================
# === AGRM State Management ===
# ==============================



