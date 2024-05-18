from geometry.geometry import Geometry

class RectangleGeometry(Geometry):
    def __init__(self, width=1, height=1, tile_x=1, tile_y=1):
        super().__init__()
        # vertices
        p0 = [-width/2, -height/2, 0]
        p1 = [ width/2, -height/2, 0]
        p2 = [-width/2,  height/2, 0]
        p3 = [ width/2,  height/2, 0]
        # colors (mantidos iguais)
        c0, c1, c2, c3 = [1, 1, 1], [1, 0, 0], [0, 1, 0], [0, 0, 1]
        # texture coordinates ajustadas para tiling
        t0, t1, t2, t3 = [0, 0], [tile_x, 0], [0, tile_y], [tile_x, tile_y]
        # triangles p0-p1-p3 and p0-p3-p2
        position_data = [p0, p1, p3, p0, p3, p2]
        color_data = [c0, c1, c3, c0, c3, c2]
        uv_data = [t0, t1, t3, t0, t3, t2]
        self.add_attribute("vec3", "vertexPosition", position_data)
        self.add_attribute("vec3", "vertexColor", color_data)
        self.add_attribute("vec2", "vertexUV", uv_data)
        self.count_vertices()