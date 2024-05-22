from core.base import Base
from core_ext.camera import Camera
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from extras.movement_rig import MovementRig
from all_objects import ObjectCreator

class Main(Base):
    def initialize(self):
        # Initialize renderer, scene, and camera
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=1200/800)
        self.camera_rig = MovementRig()
        self.camera_rig.add(self.camera)
        self.camera_rig.set_position([0.5, 0.9, 5.8])
        self.scene.add(self.camera_rig)

        # Create objects using ObjectCreator
        self.object_creator = ObjectCreator(self)

    def update(self):
        self.object_creator.jetSki.updateObject(self.input, self.delta_time)
        x,y,z = self.object_creator.jetSki.get_position()
        self.camera_rig.updateCamera(self.input, self.delta_time,x,y,z)
        self.camera_rig.set_position([x, y+0.6, z+0.8])
        self.renderer.render(self.scene, self.camera)

if __name__ == "__main__":
    Main(screen_size=[1200, 800]).run()
