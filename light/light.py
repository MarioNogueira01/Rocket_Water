"""Lights"""

from py3d.core_ext.object3d import Object3D

class Light(Object3D):
    """Implements light types"""

    AMBIENT = 1
    DIRECTIONAL = 2
    POINT = 3

    def __init__(self, light_type=0):
        super().__init__()
        self.light_type = light_type
        self.color = [1, 1, 1]
        self.attenuation = [1, 0, 0]


