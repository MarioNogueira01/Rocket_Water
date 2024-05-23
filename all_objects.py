import math

from core_ext.mesh import Mesh
from core_ext.texture import Texture
from geometry.objGeo import ObjGeo
from geometry.rectangle import RectangleGeometry
from geometry.sphere import SphereGeometry
from material.texture import TextureMaterial
from extras.movement_rig import MovementRig

class ObjectCreator:
    def __init__(self, example):
        self.example = example
        self.create_objects()
        self.ball_velocity = [0, 0, 0]  # Initialize ball velocity
        self.gravity = -0.5  # Gravity constant, negative to indicate downward force
        self.attrition = 0.995  # Attrition factor, slightly less than 1


    def create_objects(self):
        # Add skysphere
        sky_geometry = SphereGeometry(radius=50)
        sky_material = TextureMaterial(texture=Texture(file_name="images/sky.jpg"))
        sky = Mesh(sky_geometry, sky_material)
        self.example.scene.add(sky)

        # Add grass floor
        sand_geometry = RectangleGeometry(width=1000, height=1000)
        sand_material = TextureMaterial(
            texture=Texture(file_name="images/sand2.jpg"),
            property_dict={"repeatUV": [50, 50]}
        )
        sand = Mesh(sand_geometry, sand_material)
        sand.rotate_x(-math.pi / 2)
        self.example.scene.add(sand)

        # Load first object from OBJ file
        geometryball = ObjGeo('models/bola_praia.obj')
        textureball = Texture(file_name="images/texture.png")
        materialball = TextureMaterial(texture=textureball)
        self.meshball = Mesh(geometryball, materialball)
        self.ball = MovementRig()
        self.ball.add(self.meshball)
        self.ball.scale(0.3)
        self.ball.set_position([0.5, 0.5, -4])
        self.example.scene.add(self.ball)

        # Load jetski object from OBJ file
        jetSki_geometry = ObjGeo('models/jetSki.obj')
        jetSki_texture = Texture(file_name="images/jetSki.jpg")
        jetSki_material = TextureMaterial(texture=jetSki_texture)
        self.jetSki_mesh = Mesh(jetSki_geometry, jetSki_material)
        self.jetSki = MovementRig()
        self.jetSki.add(self.jetSki_mesh)
        self.jetSki.rotate_y((math.pi) * 1.5)
        self.jetSki.set_position([0.5, 0.3, 5])  # Adjust position as needed
        self.example.scene.add(self.jetSki)   
