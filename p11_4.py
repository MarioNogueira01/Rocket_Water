import math
from core.base import Base
from core_ext.camera import Camera
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from extras.movement_rig2 import MovementRig
from Objetos.object_creator import ObjectCreator

class Example(Base):
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

        # Control object is now the jet ski
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
            self.object_creator.jetSki.updateObject(self.input, self.delta_time)
            x,y,z = self.object_creator.JetskiCentralPointCalculator()
            print("Centro do jetski - X:", x, "Y:", y, "Z:", z) #depois é para retirar
            

        self.cameraUpdater(self.input, self.delta_time,x,y,z) 
        self.camera_rig.set_position([x, y+0.6, z+0.8])
        xC,yC,zC = self.camera_rig.get_position()
        print("Centro Camera : X= ", xC , "Y =", yC , "z=", zC)
        self.renderer.render(self.scene, self.camera)

    def cameraUpdater(self, input_object, delta_time,x,y,z):
        self.camera_rig.updateCamera(input_object, delta_time,x,y,z)
        


if __name__ == "__main__":
    Example(screen_size=[1200, 800]).run()
