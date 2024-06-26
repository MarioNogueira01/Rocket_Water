import math
import numpy as np
from constants import *
from core_ext.object3d import Object3D

class MovementRig(Object3D):
    """
    Add moving forwards and backwards, left and right, 
    up and down (all local translations), as well as 
    turning left and right, and looking up and down
    """
    def __init__(self, units_per_second=1, degrees_per_second=30):
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
        self.jump_velocity  = 0
        self.is_jumping = False

    # Adding and removing objects applies to look attachment.
    # Override functions from the Object3D class.
    def add(self, child):
        self._look_attachment.add(child)

    def remove(self, child):
        self._look_attachment.remove(child)

    def updateJetSki(self, input_object, delta_time, withBoost):
        if withBoost:
            move_amount = JETSKI_SPEED * JETSKI_SPEED_BOOST * delta_time
        else:
            move_amount = JETSKI_SPEED * delta_time

        if self.is_jumping:
            move_amount += AIR_SPEED_BOOST

        rotate_amount = self._degrees_per_second * (math.pi / 180) * delta_time

        if input_object.is_key_pressed("w"):
            self.translate(-move_amount, 0, 0)
        if input_object.is_key_pressed("s"):
            self.translate(move_amount, 0, 0)
            if input_object.is_key_pressed("a"):
                self.rotate_y(-rotate_amount)
            if input_object.is_key_pressed("d"):
                self.rotate_y(rotate_amount)
        else:   
            if input_object.is_key_pressed("a"):
                self.rotate_y(rotate_amount)
            if input_object.is_key_pressed("d"):
                self.rotate_y(-rotate_amount)   

        if input_object.is_key_pressed("l") and not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = JETSKI_JUMP_STRENGTH

        if self.is_jumping:
            self.update_jump(delta_time)

    def update_jump(self, delta_time):
        jetski_pos = self.get_position()
        jetski_pos[1] += self.jump_velocity * delta_time
        self.jump_velocity += BALL_GRAVITY * delta_time
        if jetski_pos[1] <= GROUND:
            jetski_pos[1] = GROUND
            self.is_jumping = False
            self.jump_velocity = 0
        self.set_position(jetski_pos)

       
    def updateBall(self, delta_time):
        self.translate(self.velocity[0] * delta_time, self.velocity[1] * delta_time, self.velocity[2] * delta_time)

    def updateOpponent(self, delta_time, x, y):
        self.set_position( [self.global_position[0], y, self.global_position[2]])
        self.translate(-x * delta_time,0,0)

    def get_position(self):
        return self.global_position

    def follow_target(self, target, offset):
        target_position = target.global_position
        target_matrix = target.global_matrix

        offset_position = [
            target_matrix[0, 0] * offset[0] + target_matrix[0, 1] * offset[1] + target_matrix[0, 2] * offset[2],
            target_matrix[1, 0] * offset[0] + target_matrix[1, 1] * offset[1] + target_matrix[1, 2] * offset[2],
            target_matrix[2, 0] * offset[0] + target_matrix[2, 1] * offset[1] + target_matrix[2, 2] * offset[2]
        ]
        new_camera_position = [
            target_position[0] + offset_position[0],
            target_position[1] + offset_position[1],
            target_position[2] + offset_position[2]
        ]
        self.set_position(new_camera_position)

        target_position[1] += 1
        self.look_at(target_position)


    def follow_target_look_at(self, target, look_at_target, y_elevate, distance):
        target_position = target.global_position
        look_at_position = look_at_target.global_position

        target_position[1] += y_elevate

        direction = np.array(look_at_position) - np.array(target_position)
        direction = direction / np.linalg.norm(direction)

        new_camera_position = np.array(target_position) - direction * distance

        self.set_position(new_camera_position.tolist())
        self.look_at(look_at_position)

