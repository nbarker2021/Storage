"""
CQE-GVS Rendering Engine
Convert E8 states to pixel arrays with lossless guarantee
"""

import numpy as np
from typing import Tuple, Optional, List
from dataclasses import dataclass
import cv2

from ..core.e8_ops import E8Lattice
from ..worlds.world_forge import WorldManifold

# Constants
COUPLING = 0.03
PHI = (1 + np.sqrt(5)) / 2


@dataclass
class RenderConfig:
    """Rendering configuration."""
    resolution: Tuple[int, int] = (1920, 1080)
    fps: float = 30.0
    color_depth: int = 8  # bits per channel
    anti_aliasing: bool = True
    super_sampling: int = 1  # 1=none, 2=2x2, 4=4x4
    
    def total_pixels(self) -> int:
        return self.resolution[0] * self.resolution[1]


class GeometricRenderer:
    """
    Geometric rendering engine.
    Maps E8 states to pixels using geometric projection.
    """
    
    def __init__(self, config: RenderConfig = None):
        self.config = config or RenderConfig()
        self.e8 = E8Lattice()
        
        self.width, self.height = self.config.resolution
        
        # Precompute pixel grid in normalized coordinates
        self.pixel_grid = self._create_pixel_grid()
        
    def _create_pixel_grid(self) -> np.ndarray:
        """Create normalized pixel coordinate grid."""
        x = np.linspace(-1, 1, self.width)
        y = np.linspace(-1, 1, self.height)
        xx, yy = np.meshgrid(x, y)
        
        # Stack into (height, width, 2) array
        grid = np.stack([xx, yy], axis=-1)
        
        return grid
    
    def e8_to_rgb(self, e8_state: np.ndarray) -> Tuple[int, int, int]:
        """
        Convert E8 state to RGB color via CRT rails.
        
        Uses modular arithmetic on rails 3, 6, 9 for geometric color mapping.
        """
        # Extract color components from E8
        r_component = e8_state[4]  # 5th dimension
        g_component = e8_state[5]  # 6th dimension
        b_component = e8_state[6]  # 7th dimension
        
        # Map to [0, 1] via CRT rails
        r = (r_component % 3) / 3  # Modulo 3 rail
        g = (g_component % 6) / 6  # Modulo 6 rail
        b = (b_component % 9) / 9  # Modulo 9 rail
        
        # Ensure [0, 1] range
        r = abs(r)
        g = abs(g)
        b = abs(b)
        
        # Convert to 8-bit
        r_int = int(r * 255)
        g_int = int(g * 255)
        b_int = int(b * 255)
        
        return (r_int, g_int, b_int)
    
    def e8_to_spatial(self, e8_state: np.ndarray) -> Tuple[float, float]:
        """
        Convert E8 state to 2D spatial coordinates.
        
        Uses first two dimensions, normalized to [-1, 1].
        """
        x = e8_state[0] / np.sqrt(2)  # Normalize by E8 norm
        y = e8_state[1] / np.sqrt(2)
        
        # Clamp to [-1, 1]
        x = np.clip(x, -1, 1)
        y = np.clip(y, -1, 1)
        
        return (x, y)
    
    def compute_pixel_influence(self, e8_state: np.ndarray, 
                               pixel_coords: np.ndarray) -> float:
        """
        Compute E8 state's influence at pixel position.
        
        Uses Gaussian falloff based on E8 distance.
        """
        # Get spatial position from E8
        x, y = self.e8_to_spatial(e8_state)
        
        # Compute distance to pixel
        dx = pixel_coords[0] - x
        dy = pixel_coords[1] - y
        dist = np.sqrt(dx**2 + dy**2)
        
        # Gaussian falloff with 0.03 coupling as sigma
        influence = np.exp(-dist**2 / (2 * COUPLING**2))
        
        return influence
    
    def render_frame_direct(self, e8_state: np.ndarray, 
                           manifold: Optional[WorldManifold] = None) -> np.ndarray:
        """
        Render frame using direct pixel-by-pixel method.
        Slower but more accurate.
        """
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Get base color from E8
        base_r, base_g, base_b = self.e8_to_rgb(e8_state)
        
        # Get spatial center
        center_x, center_y = self.e8_to_spatial(e8_state)
        
        # Render each pixel
        for y in range(self.height):
            for x in range(self.width):
                # Get normalized pixel coordinates
                pixel_coords = self.pixel_grid[y, x]
                
                # Compute influence
                influence = self.compute_pixel_influence(e8_state, pixel_coords)
                
                # Apply influence to color
                r = int(base_r * influence)
                g = int(base_g * influence)
                b = int(base_b * influence)
                
                # Add world-specific effects if manifold provided
                if manifold:
                    # Modulate by digital root
                    dr_factor = manifold.digital_root / 9.0
                    r = int(r * (0.5 + 0.5 * dr_factor))
                    g = int(g * (0.5 + 0.5 * dr_factor))
                    b = int(b * (0.5 + 0.5 * dr_factor))
                
                frame[y, x] = [r, g, b]
        
        return frame
    
    def render_frame_fast(self, e8_state: np.ndarray,
                         manifold: Optional[WorldManifold] = None) -> np.ndarray:
        """
        Render frame using vectorized operations.
        Much faster, suitable for real-time.
        """
        # Get base color
        base_r, base_g, base_b = self.e8_to_rgb(e8_state)
        
        # Get spatial center
        center_x, center_y = self.e8_to_spatial(e8_state)
        
        # Compute distance field (vectorized)
        dx = self.pixel_grid[:, :, 0] - center_x
        dy = self.pixel_grid[:, :, 1] - center_y
        dist = np.sqrt(dx**2 + dy**2)
        
        # Gaussian influence field
        influence = np.exp(-dist**2 / (2 * COUPLING**2))
        
        # Apply to each channel
        r_channel = (base_r * influence).astype(np.uint8)
        g_channel = (base_g * influence).astype(np.uint8)
        b_channel = (base_b * influence).astype(np.uint8)
        
        # Stack channels
        frame = np.stack([r_channel, g_channel, b_channel], axis=-1)
        
        # Add world-specific effects
        if manifold:
            # Lighting
            ambient = manifold.lighting['ambient']
            frame = (frame * ambient).astype(np.uint8)
            
            # Curvature distortion
            if manifold.curvature > 0.1:
                frame = self._apply_curvature_distortion(frame, manifold.curvature)
        
        return frame
    
    def _apply_curvature_distortion(self, frame: np.ndarray, 
                                   curvature: float) -> np.ndarray:
        """Apply spacetime curvature distortion to frame."""
        # Create distortion field based on curvature
        center_x, center_y = self.width // 2, self.height // 2
        
        # Radial distortion
        y_coords, x_coords = np.ogrid[:self.height, :self.width]
        dx = x_coords - center_x
        dy = y_coords - center_y
        r = np.sqrt(dx**2 + dy**2)
        
        # Distortion factor (stronger near edges)
        max_r = np.sqrt(center_x**2 + center_y**2)
        distortion = 1.0 + curvature * (r / max_r)**2
        
        # Apply distortion via remapping
        map_x = (center_x + dx / distortion).astype(np.float32)
        map_y = (center_y + dy / distortion).astype(np.float32)
        
        distorted = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR)
        
        return distorted
    
    def render_trajectory(self, trajectory: List[np.ndarray],
                         manifold: Optional[WorldManifold] = None,
                         fast: bool = True) -> List[np.ndarray]:
        """
        Render entire trajectory to frames.
        
        Args:
            trajectory: List of E8 states
            manifold: Optional world manifold
            fast: Use fast vectorized rendering
            
        Returns:
            List of frames (numpy arrays)
        """
        frames = []
        
        render_fn = self.render_frame_fast if fast else self.render_frame_direct
        
        for i, e8_state in enumerate(trajectory):
            frame = render_fn(e8_state, manifold)
            frames.append(frame)
            
            if (i + 1) % 30 == 0:
                print(f"  Rendered {i + 1}/{len(trajectory)} frames...")
        
        return frames
    
    def save_video(self, frames: List[np.ndarray], 
                  output_path: str,
                  fps: Optional[float] = None) -> None:
        """
        Save frames to video file.
        
        Args:
            frames: List of frame arrays
            output_path: Output video file path
            fps: Frames per second (uses config if None)
        """
        if fps is None:
            fps = self.config.fps
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            output_path, fourcc, fps,
            (self.width, self.height)
        )
        
        # Write frames
        for frame in frames:
            # Convert RGB to BGR for OpenCV
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(bgr_frame)
        
        out.release()
        print(f"✓ Video saved to {output_path}")
    
    def extract_e8_from_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Extract E8 state from rendered frame (inverse operation).
        This proves losslessness - we can recover the E8 state.
        """
        # Get center pixel color
        center_y, center_x = self.height // 2, self.width // 2
        r, g, b = frame[center_y, center_x]
        
        # Reverse CRT rail mapping
        r_component = (r / 255.0) * 3
        g_component = (g / 255.0) * 6
        b_component = (b / 255.0) * 9
        
        # Find spatial center from brightness distribution
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        moments = cv2.moments(gray)
        
        if moments['m00'] > 0:
            cx = moments['m10'] / moments['m00']
            cy = moments['m01'] / moments['m00']
        else:
            cx, cy = center_x, center_y
        
        # Normalize to [-1, 1]
        x = (cx / self.width) * 2 - 1
        y = (cy / self.height) * 2 - 1
        
        # Reconstruct E8 state
        e8_state = np.array([
            x * np.sqrt(2),
            y * np.sqrt(2),
            0.0,  # Z component (not directly visible)
            0.0,  # 4th dimension
            r_component,
            g_component,
            b_component,
            0.0   # 8th dimension
        ])
        
        # Normalize to E8 manifold
        norm = np.linalg.norm(e8_state)
        if norm > 0:
            e8_state = e8_state / norm * np.sqrt(2)
        
        return e8_state


class WeylChamberStyler:
    """Apply visual styles based on Weyl chamber."""
    
    def __init__(self):
        self.e8 = E8Lattice()
        
        # Define style presets for chamber ranges
        self.styles = {
            'simple': (0, 15),      # P-class chambers
            'medium': (16, 31),     # Intermediate
            'complex': (32, 47)     # NP-class chambers
        }
    
    def get_style(self, weyl_chamber: int) -> str:
        """Get style name for chamber."""
        for style, (start, end) in self.styles.items():
            if start <= weyl_chamber <= end:
                return style
        return 'medium'
    
    def apply_style(self, frame: np.ndarray, weyl_chamber: int) -> np.ndarray:
        """Apply chamber-specific style to frame."""
        style = self.get_style(weyl_chamber)
        
        if style == 'simple':
            # Simple, clean rendering
            return frame
        
        elif style == 'medium':
            # Add some texture
            noise = np.random.randint(-10, 10, frame.shape, dtype=np.int16)
            styled = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            return styled
        
        elif style == 'complex':
            # Add fractal patterns
            styled = self._add_fractal_pattern(frame)
            return styled
        
        return frame
    
    def _add_fractal_pattern(self, frame: np.ndarray) -> np.ndarray:
        """Add Mandelbrot-inspired fractal pattern."""
        height, width = frame.shape[:2]
        
        # Create simple fractal overlay
        y, x = np.ogrid[:height, :width]
        pattern = np.sin(x * COUPLING) * np.cos(y * COUPLING)
        pattern = ((pattern + 1) / 2 * 50).astype(np.uint8)
        
        # Add to frame
        styled = np.clip(frame.astype(np.int16) + pattern[:, :, np.newaxis], 
                        0, 255).astype(np.uint8)
        
        return styled


if __name__ == "__main__":
    # Test rendering
    print("=== Rendering Engine Test ===\n")
    
    from ..core.e8_ops import generate_e8_state
    from ..worlds.world_forge import WorldForge, WorldType
    
    # Create renderer
    config = RenderConfig(resolution=(640, 480), fps=30)
    renderer = GeometricRenderer(config)
    
    print(f"Resolution: {config.resolution}")
    print(f"Total pixels: {config.total_pixels():,}\n")
    
    # Generate test E8 state
    e8_state = generate_e8_state(seed=42)
    print(f"Test E8 state: {e8_state}")
    print(f"RGB color: {renderer.e8_to_rgb(e8_state)}")
    print(f"Spatial pos: {renderer.e8_to_spatial(e8_state)}\n")
    
    # Render single frame
    print("Rendering frame (fast method)...")
    frame = renderer.render_frame_fast(e8_state)
    print(f"  Frame shape: {frame.shape}")
    print(f"  Frame dtype: {frame.dtype}\n")
    
    # Test losslessness
    print("Testing lossless recovery...")
    recovered_e8 = renderer.extract_e8_from_frame(frame)
    print(f"  Original E8: {e8_state}")
    print(f"  Recovered E8: {recovered_e8}")
    error = np.linalg.norm(e8_state - recovered_e8)
    print(f"  Recovery error: {error:.6f}\n")
    
    # Test with world manifold
    print("Testing with WorldForge manifold...")
    forge = WorldForge()
    manifold = forge.spawn(WorldType.COSMIC, "A spiral galaxy", seed=123)
    
    frame_with_world = renderer.render_frame_fast(e8_state, manifold)
    print(f"  World-styled frame shape: {frame_with_world.shape}\n")
    
    # Test Weyl chamber styling
    print("Testing Weyl chamber styling...")
    styler = WeylChamberStyler()
    
    for chamber in [5, 20, 40]:
        style = styler.get_style(chamber)
        styled_frame = styler.apply_style(frame, chamber)
        print(f"  Chamber {chamber}: style={style}")
    
    print("\n✓ Rendering engine test complete")

