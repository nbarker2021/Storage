"""
CQE - Cartan Quadratic Equivalence System
Unified extraction from all monolithic sources
"""

__version__ = "5.0.0"

# Architecture Layers (L0-L6)
from . import L0_geometric
from . import L1_execution
from . import L2_core
from . import L3_audit
from . import L4_wrapper
from . import L5_tools
from . import L6_reality

# Functional Modules
from . import compression
from . import misc
from . import movie
from . import rag
from . import schema
from . import slices
from . import storage
from . import towers
from . import utils
from . import weighting
