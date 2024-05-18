import numpy as np
import math
import os

from core.base import Base
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.texture import Texture
from geometry.objGeo import ObjGeo
from geometry.rectangle import RectangleGeometry
from geometry.sphere import SphereGeometry
from material.texture import TextureMaterial
from extras.movement_rig2 import MovementRig

class Example(Base):
    def initialize(self):
        # Initialize renderer, scene, and camera
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=1200/800)
        self.camera_rig = MovementRig()
        self.camera_rig.add(self.camera)
        self.camera_rig.set_position([0.5, 1, 5])
        self.scene.add(self.camera_rig)

        # Add skysphere
        sky_geometry = SphereGeometry(radius=50)
        sky_material = TextureMaterial(texture=Texture(file_name="images/sky.jpg"))
        sky = Mesh(sky_geometry, sky_material)
        self.scene.add(sky)

        # Add grass floor
        grass_geometry = RectangleGeometry(width=1000, height=1000)
        grass_material = TextureMaterial(
            texture=Texture(file_name="images/sand2.jpg"),
            property_dict={"repeatUV": [50, 50]}
        )
        grass = Mesh(grass_geometry, grass_material)
        grass.rotate_x(-math.pi / 2)
        self.scene.add(grass)

        # Load first object from OBJ file
        obj_filename = 'bola_praia2.obj'
        script_dir = os.path.dirname(os.path.realpath(__file__))
        os.chdir(script_dir)
        geometry = ObjGeo(obj_filename)
        texture = Texture(file_name="images/texture.png")
        material = TextureMaterial(texture=texture)
        self.mesh = Mesh(geometry, material)
        self.object_rig = MovementRig()
        self.object_rig.add(self.mesh)
        self.object_rig.scale(0.3)
        self.object_rig.set_position([5, 0.5, -4])
        self.scene.add(self.object_rig)

        # Load second object from OBJ file
        second_obj_filename = 'umbrella.obj'
        second_geometry = ObjGeo(second_obj_filename)
        second_texture = Texture(file_name="images/umbrella.jpg")
        second_material = TextureMaterial(texture=second_texture)
        self.second_mesh = Mesh(second_geometry, second_material)
        self.second_object_rig = MovementRig()
        self.second_object_rig.add(self.second_mesh)
        self.second_object_rig.scale(1.3)
        self.second_object_rig.set_position([1, 1, -2])
        self.scene.add(self.second_object_rig)

        # Load third object from OBJ file
        third_obj_filename = 'jetSki.obj'
        third_geometry = ObjGeo(third_obj_filename)
        third_texture = Texture(file_name="images/jetSki.jpg")
        third_material = TextureMaterial(texture=third_texture)
        self.third_mesh = Mesh(third_geometry, third_material)
        self.third_object_rig = MovementRig()
        self.third_object_rig.add(self.third_mesh)
        self.third_object_rig.rotate_y(1.57)
        self.third_object_rig.scale(1)  # Adjust scale as needed
        self.third_object_rig.set_position([-2, 0.5, -1])  # Adjust position as needed
        self.scene.add(self.third_object_rig)

        # Load fourth object from OBJ file
        fourth_obj_filename = 'goal.obj'
        fourth_geometry = ObjGeo(fourth_obj_filename)
        fourth_texture = Texture(file_name="images/branco.jpg")
        fourth_material = TextureMaterial(texture=fourth_texture)
        self.fourth_mesh = Mesh(fourth_geometry, fourth_material)
        self.fourth_object_rig = MovementRig()
        self.fourth_object_rig.add(self.fourth_mesh)
        self.fourth_object_rig.rotate_y(3.14)
        self.fourth_object_rig.scale(5.0)  # Adjust scale as needed
        self.fourth_object_rig.set_position([8, 0.1, -4])  # Adjust position as needed
        self.scene.add(self.fourth_object_rig)


        self.control_object = True
        print("Controls:")
        print("Camera Move Forwards: 'w', Backwards: 's', Left: 'a', Right: 'd'")
        print("Camera Move Up: 'r', Down: 'f', Turn Left: 'q', Turn Right: 'e'")
        print("Camera Look Up: 't', Look Down: 'g'")
        print("Object Move Forwards: 'i', Backwards: 'k', Left: 'j', Right: 'l'")
        print("Object Turn Left: 'u', Turn Right: 'o'")
        # You can add more controls for the second object if needed


    def update(self):
        if self.control_object:
            self.object_rig.update(self.input, self.delta_time, True)
            # If you added controls for the second object, update it here as well
        self.camera_rig.update(self.input, self.delta_time, False)
        self.renderer.render(self.scene, self.camera)

if __name__ == "__main__":
    Example(screen_size=[1200, 800]).run()
