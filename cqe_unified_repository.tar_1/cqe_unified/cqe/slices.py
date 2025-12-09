"""
CQE Slices Module
Architecture Layer: slices
Components: 19
"""

import numpy as np
import json
import hashlib
from typing import Dict, List, Any, Tuple, Generator, Callable, Optional
from dataclasses import dataclass, field
from pathlib import Path
from functools import wraps
from contextlib import contextmanager

# CLASS: Face
# Source: CQE_CORE_MONOLITH.py (line 679)

class Face:
    """A 'face' is a small numeric stream view (mod 10 / mod 8) for slice calculus.
    values: base-M integers in [0, M-1].
    base:   M (10 for decagon, 8 for octagon)
    label:  free-form (e.g., 'decagon'/'octagon')
    """
    values: List[int]
    base: int
    label: str




# FUNCTION: text_to_faces
# Source: CQE_CORE_MONOLITH.py (line 690)

def text_to_faces(text: str) -> Tuple[Face, Face]:
    """Map text into two aligned numeric streams: mod10 (decagon) and mod8 (octagon).
    Deterministic, lossy by design (shape-first)."""
    # Simple deterministic mapping: bytes → rolling hash → digits
    h = 1469598103934665603  # FNV offset
    d10: List[int] = []
    d8: List[int] = []
    for ch in text.encode("utf-8", errors="ignore"):
        h ^= ch
        h *= 1099511628211
        h &= (1 << 64) - 1
        d10.append((h // 2654435761) % 10)
        d8.append((h // 11400714819323198485) % 8)
    if not d10:
        d10 = [0]
        d8 = [0]
    return Face(d10, 10, "decagon"), Face(d8, 8, "octagon")

# --------------------------------------------------------------------------------------
# Slice lattice & observables
# --------------------------------------------------------------------------------------

@dc.dataclass


# CLASS: SliceObservables
# Source: CQE_CORE_MONOLITH.py (line 713)

class SliceObservables:
    theta: List[float]                 # lattice angles
    extreme_idx: List[int]             # i(θ): index of extreme sample
    quadrant_bins: List[Tuple[int,int,int,int]]  # q(θ): counts per quadrant-like bin
    chord_hist: List[Counter]          # hΔ(θ): histogram of chord steps
    perm: List[List[int]]              # π(θ): permutation of sample order (top-k simplified)
    braid_current: List[int]           # B(θ): adjacent transposition count per step
    energies: Dict[str, float]         # Dirichlet energies over chosen signals




# CLASS: SliceSensors
# Source: CQE_CORE_MONOLITH.py (line 723)

class SliceSensors:
    def __init__(self, W: int = 80, topk: int = 16):
        self.W = W
        self.topk = topk
        self.theta = [2 * math.pi * m / W for m in range(W)]

    # --- projections & helpers ---
    @staticmethod
    def _project_stream(vals: Sequence[int], base: int, theta: float) -> List[float]:
        # Treat each sample as a point on its base-gon; project onto direction θ
        out: List[float] = []
        for v in vals:
            ang = 2 * math.pi * (v % base) / base
            out.append(math.cos(ang - theta))
        return out

    @staticmethod
    def _argmax_idx(arr: Sequence[float]) -> int:
        best, idx = -1e9, 0
        for i, x in enumerate(arr):
            if x > best:
                best, idx = x, i
        return idx

    @staticmethod
    def _quadrant_bins(vals: Sequence[int], base: int, theta: float) -> Tuple[int,int,int,int]:
        # Bin positions after rotation; 4 equal arcs on the circle
        bins = [0,0,0,0]
        for v in vals:
            ang = (2 * math.pi * (v % base) / base - theta) % (2 * math.pi)
            q = int((ang / (2 * math.pi)) * 4.0) % 4
            bins[q] += 1
        return tuple(bins)  # type: ignore

    @staticmethod
    def _chord_hist(vals: Sequence[int], base: int) -> Counter:
        # Count step differences mod base for consecutive samples
        c = Counter()
        for a, b in zip(vals, vals[1:]):
            step = (b - a) % base
            c[step] += 1
        return c

    @staticmethod
    def _perm_by_projection(vals: Sequence[int], base: int, theta: float, topk: int) -> List[int]:
        # Sort indices by projection descending; return top-k indices
        proj = SliceSensors._project_stream(vals, base, theta)
        order = sorted(range(len(vals)), key=lambda i: proj[i], reverse=True)
        return order[:min(topk, len(order))]

    @staticmethod
    def _adjacent_transpositions(prev: List[int], curr: List[int]) -> int:
        # Count adjacent transpositions needed to go from prev order to curr order
        pos_prev = {v: i for i, v in enumerate(prev)}
        pos_curr = {v: i for i, v in enumerate(curr)}
        common = [v for v in prev if v in pos_curr]
        # Count inversions between common subsequences
        mapped = [pos_curr[v] for v in common]
        # Fenwick-like O(n^2) simple count (topk is small)
        inv = 0
        for i in range(len(mapped)):
            for j in range(i + 1, len(mapped)):
                if mapped[i] > mapped[j]:
                    inv += 1
        return inv

    def compute(self, face: Face) -> SliceObservables:
        W, base, vals = self.W, face.base, face.values
        theta = self.theta
        extreme_idx: List[int] = []
        quadrant_bins: List[Tuple[int,int,int,int]] = []
        chord_hist: List[Counter] = []
        perm: List[List[int]] = []
        braid_current: List[int] = []

        prev_order: Optional[List[int]] = None
        for th in theta:
            proj = self._project_stream(vals, base, th)
            extreme_idx.append(self._argmax_idx(proj))
            quadrant_bins.append(self._quadrant_bins(vals, base, th))
            chord_hist.append(self._chord_hist(vals, base))  # independent of θ
            order = self._perm_by_projection(vals, base, th, self.topk)
            perm.append(order)
            if prev_order is None:
                braid_current.append(0)
            else:
                braid_current.append(self._adjacent_transpositions(prev_order, order))
            prev_order = order

        # Energies (Dirichlet) on discrete circle for extreme index and q-bin imbalance
        def dirichlet_energy_int(seq: Sequence[int]) -> float:
            # use circular second differences
            n = len(seq)
            acc = 0.0
            for i in range(n):
                a = seq[(i + 1) % n]
                b = seq[i]
                c = seq[(i - 1) % n]
                acc += float((a - 2 * b + c) ** 2)
            return acc / float(n)

        def q_imbalance_energy(qbins: Sequence[Tuple[int,int,int,int]]) -> float:
            e = 0.0
            for q in qbins:
                m = sum(q) / 4.0
                e += sum((qi - m) ** 2 for qi in q)
            return e / float(len(qbins))

        energies = {
            "E_extreme": dirichlet_energy_int(extreme_idx),
            "E_quads": q_imbalance_energy(quadrant_bins),
            "Crossings": float(sum(braid_current)),
        }
        return SliceObservables(theta, extreme_idx, quadrant_bins, chord_hist, perm, braid_current, energies)

# --------------------------------------------------------------------------------------
# Repairs, lattice switch, clone tiling
# --------------------------------------------------------------------------------------



# CLASS: Face
# Source: CQE_CORE_MONOLITH.py (line 1282)

class Face:
    """A 'face' is a small numeric stream view (mod 10 / mod 8) for slice calculus."""
    values: List[int]
    base: int
    label: str



# FUNCTION: text_to_faces
# Source: CQE_CORE_MONOLITH.py (line 1288)

def text_to_faces(text: str) -> Tuple[Face, Face]:
    """Map text into two aligned numeric streams: mod10 (decagon) and mod8 (octagon). Deterministic."""
    # FNV-1a 64-bit rolling hash over bytes; split into bases.
    h = 0xcbf29ce484222325  # FNV offset
    d10: List[int] = []
    d8: List[int] = []
    for ch in text.encode("utf-8", errors="ignore"):
        h ^= ch
        h = (h * 0x100000001b3) & ((1<<64)-1)  # FNV prime
        d10.append((h // 2654435761) % 10)
        d8.append((h // 11400714819323198485) % 8)
    if not d10:
        d10 = [0]; d8 = [0]
    return Face(d10, 10, "decagon"), Face(d8, 8, "octagon")

# -----------------------------------------------------------------------------
# Slice lattice & observables
# -----------------------------------------------------------------------------

@dc.dataclass


# CLASS: SliceObservables
# Source: CQE_CORE_MONOLITH.py (line 1308)

class SliceObservables:
    theta: List[float]                         # lattice angles (radians)
    extreme_idx: List[int]                     # i(θ): index of extreme sample (by projection on θ)
    quadrant_bins: List[Tuple[int,int,int,int]]  # q(θ): counts per quadrant-like bin
    chord_hist: List[Dict[int,int]]            # hΔ(θ): histogram of chord steps (constant in this simple model)
    perm: List[List[int]]                      # π(θ): top-k order (indices) by projection
    braid_current: List[int]                   # B(θ): adjacent transposition count per step
    energies: Dict[str, float]                 # Dirichlet energies over chosen signals



# CLASS: SliceSensors
# Source: CQE_CORE_MONOLITH.py (line 1317)

class SliceSensors:
    def __init__(self, W: int = 80, topk: int = 16):
        self.W = W
        self.topk = topk
        self.theta = [2.0 * math.pi * m / W for m in range(W)]

    # --- projections & helpers ---
    @staticmethod
    def _project_stream(vals: Sequence[int], base: int, theta: float) -> List[float]:
        # Treat each sample as a point on its base-gon; project onto direction θ
        out: List[float] = []
        for v in vals:
            ang = 2.0 * math.pi * (v % base) / base
            out.append(math.cos(ang - theta))
        return out

    @staticmethod
    def _argmax_idx(arr: Sequence[float]) -> int:
        best = -1e9; idx = 0
        for i, x in enumerate(arr):
            if x > best:
                best = x; idx = i
        return idx

    @staticmethod
    def _quadrant_bins(vals: Sequence[int], base: int, theta: float) -> Tuple[int,int,int,int]:
        # Bin positions after rotation; 4 equal arcs on the circle
        bins = [0,0,0,0]
        for v in vals:
            ang = (2.0 * math.pi * (v % base) / base - theta) % (2.0 * math.pi)
            q = int((ang / (2.0 * math.pi)) * 4.0) % 4
            bins[q] += 1
        return (bins[0], bins[1], bins[2], bins[3])

    @staticmethod
    def _chord_hist(vals: Sequence[int], base: int) -> Dict[int,int]:
        c: Dict[int,int] = {}
        for a, b in zip(vals, vals[1:]):
            step = (b - a) % base
            c[step] = c.get(step, 0) + 1
        return c

    @staticmethod
    def _perm_by_projection(vals: Sequence[int], base: int, theta: float, topk: int) -> List[int]:
        proj = SliceSensors._project_stream(vals, base, theta)
        order = sorted(range(len(vals)), key=lambda i: proj[i], reverse=True)
        return order[:min(topk, len(order))]

    @staticmethod
    def _adjacent_transpositions(prev: List[int], curr: List[int]) -> int:
        # Count inversions between adjacent elements moving from prev to curr (small topk, O(n^2) ok)
        pos_curr = {v: i for i, v in enumerate(curr)}
        common = [v for v in prev if v in pos_curr]
        mapped = [pos_curr[v] for v in common]
        inv = 0
        for i in range(len(mapped)):
            for j in range(i+1, len(mapped)):
                if mapped[i] > mapped[j]:
                    inv += 1
        return inv

    def compute(self, face: Face) -> SliceObservables:
        W, base, vals = self.W, face.base, face.values
        theta = self.theta
        extreme_idx: List[int] = []
        quadrant_bins: List[Tuple[int,int,int,int]] = []
        chord_hist: List[Dict[int,int]] = []
        perm: List[List[int]] = []
        braid_current: List[int] = []

        prev_order: Optional[List[int]] = None
        for th in theta:
            proj = self._project_stream(vals, base, th)
            extreme_idx.append(self._argmax_idx(proj))
            quadrant_bins.append(self._quadrant_bins(vals, base, th))
            chord_hist.append(self._chord_hist(vals, base))  # independent of θ in this simple model
            order = self._perm_by_projection(vals, base, th, self.topk)
            perm.append(order)
            if prev_order is None:
                braid_current.append(0)
            else:
                braid_current.append(self._adjacent_transpositions(prev_order, order))
            prev_order = order

        # Energies (Dirichlet) on discrete circle
        def dirichlet_energy_int(seq: Sequence[int]) -> float:
            n = len(seq); acc = 0.0
            for i in range(n):
                a = seq[(i+1) % n]; b = seq[i]; c = seq[(i-1) % n]
                acc += float((a - 2*b + c)**2)
            return acc / float(max(1, n))

        def q_imbalance_energy(qbins: Sequence[Tuple[int,int,int,int]]) -> float:
            e = 0.0
            for q in qbins:
                m = sum(q) / 4.0
                e += sum((qi - m)**2 for qi in q)
            return e / float(max(1, len(qbins)))

        energies = {
            "E_extreme": dirichlet_energy_int(extreme_idx),
            "E_quads": q_imbalance_energy(quadrant_bins),
            "Crossings": float(sum(braid_current)),
        }
        return SliceObservables(theta, extreme_idx, quadrant_bins, chord_hist, perm, braid_current, energies)

# -----------------------------------------------------------------------------
# Actuators
# -----------------------------------------------------------------------------



# CLASS: InterfaceType
# Source: CQE_CORE_MONOLITH.py (line 15363)

class InterfaceType(Enum):
    """Types of interfaces supported"""
    COMMAND_LINE = "command_line"
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
    NATURAL_LANGUAGE = "natural_language"
    VISUAL = "visual"
    VOICE = "voice"
    GESTURE = "gesture"
    BRAIN_COMPUTER = "brain_computer"
    CQE_NATIVE = "cqe_native"



# CLASS: InterfaceRequest
# Source: CQE_CORE_MONOLITH.py (line 15397)

class InterfaceRequest:
    """Represents a request to the CQE system"""
    request_id: str
    interface_type: InterfaceType
    interaction_mode: InteractionMode
    content: Any
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass


# CLASS: InterfaceResponse
# Source: CQE_CORE_MONOLITH.py (line 15411)

class InterfaceResponse:
    """Represents a response from the CQE system"""
    response_id: str
    request_id: str
    status: str  # success, error, partial, pending
    content: Any
    format: ResponseFormat
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    processing_time: float = 0.0
    confidence: float = 1.0

@dataclass


# CLASS: Face
# Source: CQE_CORE_MONOLITH.py (line 71748)

class Face:
    """A 'face' is a small numeric stream view (mod 10 / mod 8) for slice calculus.
    values: base-M integers in [0, M-1].
    base:   M (10 for decagon, 8 for octagon)
    label:  free-form (e.g., 'decagon'/'octagon')
    """
    values: List[int]
    base: int
    label: str




# FUNCTION: text_to_faces
# Source: CQE_CORE_MONOLITH.py (line 71759)

def text_to_faces(text: str) -> Tuple[Face, Face]:
    """Map text into two aligned numeric streams: mod10 (decagon) and mod8 (octagon).
    Deterministic, lossy by design (shape-first)."""
    # Simple deterministic mapping: bytes → rolling hash → digits
    h = 1469598103934665603  # FNV offset
    d10: List[int] = []
    d8: List[int] = []
    for ch in text.encode("utf-8", errors="ignore"):
        h ^= ch
        h *= 1099511628211
        h &= (1 << 64) - 1
        d10.append((h // 2654435761) % 10)
        d8.append((h // 11400714819323198485) % 8)
    if not d10:
        d10 = [0]
        d8 = [0]
    return Face(d10, 10, "decagon"), Face(d8, 8, "octagon")

# --------------------------------------------------------------------------------------
# Slice lattice & observables
# --------------------------------------------------------------------------------------

@dc.dataclass


# CLASS: SliceObservables
# Source: CQE_CORE_MONOLITH.py (line 71782)

class SliceObservables:
    theta: List[float]                 # lattice angles
    extreme_idx: List[int]             # i(θ): index of extreme sample
    quadrant_bins: List[Tuple[int,int,int,int]]  # q(θ): counts per quadrant-like bin
    chord_hist: List[Counter]          # hΔ(θ): histogram of chord steps
    perm: List[List[int]]              # π(θ): permutation of sample order (top-k simplified)
    braid_current: List[int]           # B(θ): adjacent transposition count per step
    energies: Dict[str, float]         # Dirichlet energies over chosen signals




# CLASS: SliceSensors
# Source: CQE_CORE_MONOLITH.py (line 71792)

class SliceSensors:
    def __init__(self, W: int = 80, topk: int = 16):
        self.W = W
        self.topk = topk
        self.theta = [2 * math.pi * m / W for m in range(W)]

    # --- projections & helpers ---
    @staticmethod
    def _project_stream(vals: Sequence[int], base: int, theta: float) -> List[float]:
        # Treat each sample as a point on its base-gon; project onto direction θ
        out: List[float] = []
        for v in vals:
            ang = 2 * math.pi * (v % base) / base
            out.append(math.cos(ang - theta))
        return out

    @staticmethod
    def _argmax_idx(arr: Sequence[float]) -> int:
        best, idx = -1e9, 0
        for i, x in enumerate(arr):
            if x > best:
                best, idx = x, i
        return idx

    @staticmethod
    def _quadrant_bins(vals: Sequence[int], base: int, theta: float) -> Tuple[int,int,int,int]:
        # Bin positions after rotation; 4 equal arcs on the circle
        bins = [0,0,0,0]
        for v in vals:
            ang = (2 * math.pi * (v % base) / base - theta) % (2 * math.pi)
            q = int((ang / (2 * math.pi)) * 4.0) % 4
            bins[q] += 1
        return tuple(bins)  # type: ignore

    @staticmethod
    def _chord_hist(vals: Sequence[int], base: int) -> Counter:
        # Count step differences mod base for consecutive samples
        c = Counter()
        for a, b in zip(vals, vals[1:]):
            step = (b - a) % base
            c[step] += 1
        return c

    @staticmethod
    def _perm_by_projection(vals: Sequence[int], base: int, theta: float, topk: int) -> List[int]:
        # Sort indices by projection descending; return top-k indices
        proj = SliceSensors._project_stream(vals, base, theta)
        order = sorted(range(len(vals)), key=lambda i: proj[i], reverse=True)
        return order[:min(topk, len(order))]

    @staticmethod
    def _adjacent_transpositions(prev: List[int], curr: List[int]) -> int:
        # Count adjacent transpositions needed to go from prev order to curr order
        pos_prev = {v: i for i, v in enumerate(prev)}
        pos_curr = {v: i for i, v in enumerate(curr)}
        common = [v for v in prev if v in pos_curr]
        # Count inversions between common subsequences
        mapped = [pos_curr[v] for v in common]
        # Fenwick-like O(n^2) simple count (topk is small)
        inv = 0
        for i in range(len(mapped)):
            for j in range(i + 1, len(mapped)):
                if mapped[i] > mapped[j]:
                    inv += 1
        return inv

    def compute(self, face: Face) -> SliceObservables:
        W, base, vals = self.W, face.base, face.values
        theta = self.theta
        extreme_idx: List[int] = []
        quadrant_bins: List[Tuple[int,int,int,int]] = []
        chord_hist: List[Counter] = []
        perm: List[List[int]] = []
        braid_current: List[int] = []

        prev_order: Optional[List[int]] = None
        for th in theta:
            proj = self._project_stream(vals, base, th)
            extreme_idx.append(self._argmax_idx(proj))
            quadrant_bins.append(self._quadrant_bins(vals, base, th))
            chord_hist.append(self._chord_hist(vals, base))  # independent of θ
            order = self._perm_by_projection(vals, base, th, self.topk)
            perm.append(order)
            if prev_order is None:
                braid_current.append(0)
            else:
                braid_current.append(self._adjacent_transpositions(prev_order, order))
            prev_order = order

        # Energies (Dirichlet) on discrete circle for extreme index and q-bin imbalance
        def dirichlet_energy_int(seq: Sequence[int]) -> float:
            # use circular second differences
            n = len(seq)
            acc = 0.0
            for i in range(n):
                a = seq[(i + 1) % n]
                b = seq[i]
                c = seq[(i - 1) % n]
                acc += float((a - 2 * b + c) ** 2)
            return acc / float(n)

        def q_imbalance_energy(qbins: Sequence[Tuple[int,int,int,int]]) -> float:
            e = 0.0
            for q in qbins:
                m = sum(q) / 4.0
                e += sum((qi - m) ** 2 for qi in q)
            return e / float(len(qbins))

        energies = {
            "E_extreme": dirichlet_energy_int(extreme_idx),
            "E_quads": q_imbalance_energy(quadrant_bins),
            "Crossings": float(sum(braid_current)),
        }
        return SliceObservables(theta, extreme_idx, quadrant_bins, chord_hist, perm, braid_current, energies)

# --------------------------------------------------------------------------------------
# Repairs, lattice switch, clone tiling
# --------------------------------------------------------------------------------------



# CLASS: Face
# Source: CQE_CORE_MONOLITH.py (line 72351)

class Face:
    """A 'face' is a small numeric stream view (mod 10 / mod 8) for slice calculus."""
    values: List[int]
    base: int
    label: str



# FUNCTION: text_to_faces
# Source: CQE_CORE_MONOLITH.py (line 72357)

def text_to_faces(text: str) -> Tuple[Face, Face]:
    """Map text into two aligned numeric streams: mod10 (decagon) and mod8 (octagon). Deterministic."""
    # FNV-1a 64-bit rolling hash over bytes; split into bases.
    h = 0xcbf29ce484222325  # FNV offset
    d10: List[int] = []
    d8: List[int] = []
    for ch in text.encode("utf-8", errors="ignore"):
        h ^= ch
        h = (h * 0x100000001b3) & ((1<<64)-1)  # FNV prime
        d10.append((h // 2654435761) % 10)
        d8.append((h // 11400714819323198485) % 8)
    if not d10:
        d10 = [0]; d8 = [0]
    return Face(d10, 10, "decagon"), Face(d8, 8, "octagon")

# -----------------------------------------------------------------------------
# Slice lattice & observables
# -----------------------------------------------------------------------------

@dc.dataclass


# CLASS: SliceObservables
# Source: CQE_CORE_MONOLITH.py (line 72377)

class SliceObservables:
    theta: List[float]                         # lattice angles (radians)
    extreme_idx: List[int]                     # i(θ): index of extreme sample (by projection on θ)
    quadrant_bins: List[Tuple[int,int,int,int]]  # q(θ): counts per quadrant-like bin
    chord_hist: List[Dict[int,int]]            # hΔ(θ): histogram of chord steps (constant in this simple model)
    perm: List[List[int]]                      # π(θ): top-k order (indices) by projection
    braid_current: List[int]                   # B(θ): adjacent transposition count per step
    energies: Dict[str, float]                 # Dirichlet energies over chosen signals



# CLASS: SliceSensors
# Source: CQE_CORE_MONOLITH.py (line 72386)

class SliceSensors:
    def __init__(self, W: int = 80, topk: int = 16):
        self.W = W
        self.topk = topk
        self.theta = [2.0 * math.pi * m / W for m in range(W)]

    # --- projections & helpers ---
    @staticmethod
    def _project_stream(vals: Sequence[int], base: int, theta: float) -> List[float]:
        # Treat each sample as a point on its base-gon; project onto direction θ
        out: List[float] = []
        for v in vals:
            ang = 2.0 * math.pi * (v % base) / base
            out.append(math.cos(ang - theta))
        return out

    @staticmethod
    def _argmax_idx(arr: Sequence[float]) -> int:
        best = -1e9; idx = 0
        for i, x in enumerate(arr):
            if x > best:
                best = x; idx = i
        return idx

    @staticmethod
    def _quadrant_bins(vals: Sequence[int], base: int, theta: float) -> Tuple[int,int,int,int]:
        # Bin positions after rotation; 4 equal arcs on the circle
        bins = [0,0,0,0]
        for v in vals:
            ang = (2.0 * math.pi * (v % base) / base - theta) % (2.0 * math.pi)
            q = int((ang / (2.0 * math.pi)) * 4.0) % 4
            bins[q] += 1
        return (bins[0], bins[1], bins[2], bins[3])

    @staticmethod
    def _chord_hist(vals: Sequence[int], base: int) -> Dict[int,int]:
        c: Dict[int,int] = {}
        for a, b in zip(vals, vals[1:]):
            step = (b - a) % base
            c[step] = c.get(step, 0) + 1
        return c

    @staticmethod
    def _perm_by_projection(vals: Sequence[int], base: int, theta: float, topk: int) -> List[int]:
        proj = SliceSensors._project_stream(vals, base, theta)
        order = sorted(range(len(vals)), key=lambda i: proj[i], reverse=True)
        return order[:min(topk, len(order))]

    @staticmethod
    def _adjacent_transpositions(prev: List[int], curr: List[int]) -> int:
        # Count inversions between adjacent elements moving from prev to curr (small topk, O(n^2) ok)
        pos_curr = {v: i for i, v in enumerate(curr)}
        common = [v for v in prev if v in pos_curr]
        mapped = [pos_curr[v] for v in common]
        inv = 0
        for i in range(len(mapped)):
            for j in range(i+1, len(mapped)):
                if mapped[i] > mapped[j]:
                    inv += 1
        return inv

    def compute(self, face: Face) -> SliceObservables:
        W, base, vals = self.W, face.base, face.values
        theta = self.theta
        extreme_idx: List[int] = []
        quadrant_bins: List[Tuple[int,int,int,int]] = []
        chord_hist: List[Dict[int,int]] = []
        perm: List[List[int]] = []
        braid_current: List[int] = []

        prev_order: Optional[List[int]] = None
        for th in theta:
            proj = self._project_stream(vals, base, th)
            extreme_idx.append(self._argmax_idx(proj))
            quadrant_bins.append(self._quadrant_bins(vals, base, th))
            chord_hist.append(self._chord_hist(vals, base))  # independent of θ in this simple model
            order = self._perm_by_projection(vals, base, th, self.topk)
            perm.append(order)
            if prev_order is None:
                braid_current.append(0)
            else:
                braid_current.append(self._adjacent_transpositions(prev_order, order))
            prev_order = order

        # Energies (Dirichlet) on discrete circle
        def dirichlet_energy_int(seq: Sequence[int]) -> float:
            n = len(seq); acc = 0.0
            for i in range(n):
                a = seq[(i+1) % n]; b = seq[i]; c = seq[(i-1) % n]
                acc += float((a - 2*b + c)**2)
            return acc / float(max(1, n))

        def q_imbalance_energy(qbins: Sequence[Tuple[int,int,int,int]]) -> float:
            e = 0.0
            for q in qbins:
                m = sum(q) / 4.0
                e += sum((qi - m)**2 for qi in q)
            return e / float(max(1, len(qbins)))

        energies = {
            "E_extreme": dirichlet_energy_int(extreme_idx),
            "E_quads": q_imbalance_energy(quadrant_bins),
            "Crossings": float(sum(braid_current)),
        }
        return SliceObservables(theta, extreme_idx, quadrant_bins, chord_hist, perm, braid_current, energies)

# -----------------------------------------------------------------------------
# Actuators
# -----------------------------------------------------------------------------



