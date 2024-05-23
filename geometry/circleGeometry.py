from geometry.geometry import Geometry
import math

class CircleGeometry(Geometry):
    def __init__(self, inner_radius=0.9, outer_radius=1, segments=32):
        super().__init__()
        angle_step = 2 * math.pi / segments
        positions = []
        for i in range(segments + 1):
            angle = i * angle_step
            x_inner = inner_radius * math.cos(angle)
            y_inner = 0
            z_inner = inner_radius * math.sin(angle)
            x_outer = outer_radius * math.cos(angle)
            y_outer = 0
            z_outer = outer_radius * math.sin(angle)
            positions.extend([[x_inner, y_inner, z_inner], [x_outer, y_outer, z_outer]])

        self.add_attribute("vec3", "vertexPosition", positions)
        self.count_vertices()