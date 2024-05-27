from geometry.geometry import Geometry
import math

class CircleGeometry(Geometry):
    def __init__(self, radius=1, segments=128):
        super().__init__()
        angle_step = 2 * math.pi / segments
        positions = []
        indices = []

        # Center of the circle
        positions.append([0, 0.3, 0])

        # Perimeter vertices
        for i in range(segments + 1):
            angle = i * angle_step
            x = radius * math.cos(angle)
            y = 0.3
            z = radius * math.sin(angle)
            positions.append([x, y, z])

        # Generating indices for triangle fan
        for i in range(1, segments):
            indices.extend([0, i, i + 1])
        # Closing the circle
        indices.extend([0, segments, 1])

        self.add_attribute("vec3", "vertexPosition", positions)
        self.set_indices(indices)
        self.count_vertices()

    def set_indices(self, indices):
        self.indices = indices