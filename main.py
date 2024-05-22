from core.base import Base
from core_ext.camera import Camera
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from extras.movement_rig import MovementRig
from all_objects import ObjectCreator

class Main(Base):
    def initialize(self):
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=1200/800)
        self.camera_rig = MovementRig()
        self.camera_rig.add(self.camera)
        self.camera_rig.set_position([0.5, 0.9, 5.8])
        self.scene.add(self.camera_rig)

        self.objects = ObjectCreator(self)
        self.camera_follow_mode = True

    def camera_updates(self):
        if self.input.is_key_down("space"):
            self.camera_follow_mode = not self.camera_follow_mode

        if self.camera_follow_mode:
            self.camera_rig.follow_target(self.objects.jetSki, offset=[4, 2, 0])
        else:
            self.camera_rig.follow_target_look_at(self.objects.jetSki, self.objects.ball, 2, 5)


    def update(self):
        self.objects.jetSki.updateObject(self.input, self.delta_time)
        self.camera_updates()
        self.renderer.render(self.scene, self.camera)






if __name__ == "__main__":
    Main(screen_size=[1200, 800]).run()



