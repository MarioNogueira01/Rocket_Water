import math
import numpy as np
from core_ext.object3d import Object3D

class MovementRig(Object3D):
    """
    Add moving forwards and backwards, left and right, 
    up and down (all local translations), as well as 
    turning left and right, and looking up and down
    """
    def __init__(self, units_per_second=1, degrees_per_second=60):
        # Initialize base Object3D.
        # Controls movement and turn left/right.
        super().__init__()
        # Initialize attached Object3D; controls look up/down
        self._look_attachment = Object3D()
        self.children_list = [self._look_attachment]
        self._look_attachment.parent = self
        # Control rate of movement
        self._units_per_second = units_per_second
        self._degrees_per_second = degrees_per_second

        # Customizable key mappings.
        # Defaults: W, A, S, D, R, F (move), Q, E (turn), T, G (look)
        self.KEY_MOVE_FORWARDS = "w"
        self.KEY_MOVE_BACKWARDS = "s"
        self.KEY_MOVE_LEFT = "a"
        self.KEY_MOVE_RIGHT = "d"

        self.KEY_MOVE_FORWARDS2 = "w"
        self.KEY_MOVE_BACKWARDS2 = "s"
        self.KEY_MOVE_LEFT2 = "a"
        self.KEY_MOVE_RIGHT2 = "d"
        self.KEY_TURN_LEFT2 = "q"
        self.KEY_TURN_RIGHT2 = "e"

        self.KEY_MOVE_UP = "r"
        self.KEY_MOVE_DOWN = "f"
        self.KEY_TURN_LEFT = "q"
        self.KEY_TURN_RIGHT = "e"
        self.KEY_LOOK_UP = "t"
        self.KEY_LOOK_DOWN = "g"

    # Adding and removing objects applies to look attachment.
    # Override functions from the Object3D class.
    def add(self, child):
        self._look_attachment.add(child)

    def remove(self, child):
        self._look_attachment.remove(child)

    def updateObject(self, input_object, delta_time):
        move_amount = self._units_per_second * delta_time
        rotate_amount = self._degrees_per_second * (math.pi / 180) * delta_time

        if input_object.is_key_pressed("w"):
            self.translate(-move_amount, 0, 0)
        if input_object.is_key_pressed("s"):
            self.translate(move_amount, 0, 0)
        if input_object.is_key_pressed("a"):
            self.rotate_y(rotate_amount)
        if input_object.is_key_pressed("d"):
            self.rotate_y(-rotate_amount)
            

    def rotateCamera(self,rotate_amount,x,y,z):
        
        self.rotate_y(rotate_amount)
        self.translate(x,y,z)
        self.translate(-x,-y,-z)


    def get_position(self):
        return self.global_position

    def follow_target(self, target, offset):
        # Get the global position and orientation of the target (jetski)
        target_position = target.global_position
        target_matrix = target.global_matrix

        # Calculate the offset position in the local space of the target
        offset_position = [
            target_matrix[0, 0] * offset[0] + target_matrix[0, 1] * offset[1] + target_matrix[0, 2] * offset[2],
            target_matrix[1, 0] * offset[0] + target_matrix[1, 1] * offset[1] + target_matrix[1, 2] * offset[2],
            target_matrix[2, 0] * offset[0] + target_matrix[2, 1] * offset[1] + target_matrix[2, 2] * offset[2]
        ]

        # Set the camera position based on the offset from the target
        new_camera_position = [
            target_position[0] + offset_position[0],
            target_position[1] + offset_position[1],
            target_position[2] + offset_position[2]
        ]
        self.set_position(new_camera_position)

        target_position[1] += 1
        self.look_at(target_position)


    def follow_target_look_at(self, target, look_at_target, y_elevate, distance):
        # Get the global position of the target (jetski) and the look_at_target (ball)
        target_position = target.global_position
        look_at_position = look_at_target.global_position


        # Calculate the direction from the jetski to the ball
        direction = np.array(look_at_position) - np.array(target_position)
        direction = direction / np.linalg.norm(direction)  # Normalize the direction

        # Calculate the new camera position based on the offset distance behind the jetski along the direction
        new_camera_position = np.array(target_position) - direction * distance

        # Add the elevation offset
        new_camera_position[1] += y_elevate

        # Set the camera position
        self.set_position(new_camera_position.tolist())

        # Orient the camera to look at the ball
        self.look_at(look_at_position)