import time
import math
from constants import *
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
        self.camera = Camera(aspect_ratio=SCREEN_WIDTH/SCREE_HEIGHT)
        self.camera_rig = MovementRig()
        self.camera_rig.add(self.camera)
        self.scene.add(self.camera_rig)
        self.objects = ObjectCreator(self)
        self.camera_follow_mode = True
        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0

########################################################################################
########################################################################################
# CAMERA SYSTEM
########################################################################################
########################################################################################

    def camera_updates(self):
        if self.input.is_key_down("space"):
            self.camera_follow_mode = not self.camera_follow_mode

        if self.camera_follow_mode:
            self.camera_rig.follow_target(self.objects.jetSki, offset=[CAMERA_OFFSET_DISTANCE, CAMERA_OFFSET_Y, 0])
        else:
            self.camera_rig.follow_target_look_at(self.objects.jetSki, self.objects.ball, CAMERA_FOLLOW_OFFSET_Y, CAMERA_OFFSET_DISTANCE)

########################################################################################
########################################################################################
# BALL COLLISION SYSTEM
########################################################################################
########################################################################################

    def check_collision(self):
        jetski_pos = self.objects.jetSki.global_position
        ball_pos = self.objects.ball.global_position

        distance = math.sqrt((jetski_pos[0] - ball_pos[0]) ** 2 + (jetski_pos[1] - ball_pos[1]) ** 2 + (jetski_pos[2] - ball_pos[2]) ** 2)
        collision_distance = HITBOX_BUFFER 

        if distance < collision_distance:
            direction = [
                ball_pos[0] - jetski_pos[0],
                ball_pos[1] - jetski_pos[1],
                ball_pos[2] - jetski_pos[2]
            ]
            magnitude = math.sqrt(direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2)
            if magnitude != 0:
                direction = [d / magnitude for d in direction]

            self.objects.ball_velocity = [d * BALL_SPEED for d in direction] 

    def ball_collisions(self):
        self.check_collision()

        if self.objects.ball.get_position()[1] > 0.5:
            self.objects.ball_velocity[1] += BALL_GRAVITY * self.delta_time
        elif self.objects.ball_velocity[1] < 0 and self.objects.ball.get_position()[1] < 1:
            self.objects.ball_velocity[1] =  -self.objects.ball_velocity[1] * BALL_BOUNCE

        self.objects.ball_velocity = [v * BALL_ATTRITION for v in self.objects.ball_velocity]
        self.objects.ball.velocity = self.objects.ball_velocity
        self.objects.ball.updateBall(self.delta_time)

########################################################################################
########################################################################################
# WALL COLLISION SYSTEM
########################################################################################
########################################################################################

    def check_wall_collisions(self):
        ball_pos = self.objects.ball.get_position()
        next_ball_pos = [ball_pos[i] + self.objects.ball_velocity[i] * self.delta_time for i in range(3)]

        # Check collision with each wall
        for wall in self.objects.walls:
            (min_x, max_x), (min_z, max_z) = wall.bounds
            if min_x <= next_ball_pos[0] <= max_x and min_z <= next_ball_pos[2] <= max_z:
                # If collision is detected, reverse the appropriate component of velocity
                # Assuming walls are either horizontal or vertical
                if wall in self.objects.walls[:2]:  # Horizontal walls
                    self.objects.ball_velocity[2] = -self.objects.ball_velocity[2]
                else:  # Vertical walls
                    self.objects.ball_velocity[0] = -self.objects.ball_velocity[0]
                break




########################################################################################
########################################################################################
# SHOW FPS
########################################################################################
########################################################################################

    def showFPS(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_time
        self.frame_count += 1
        
        if elapsed_time >= 1.0:
            self.fps = self.frame_count / elapsed_time
            print(f"FPS: {self.fps:.2f}")
            self.frame_count = 0
            self.tick_count = 0
            self.last_time = current_time

########################################################################################
########################################################################################
# JETSKI MOVEMENT
########################################################################################
########################################################################################

    def jetski_control(self):
        self.objects.jetSki.updateJetSki(self.input, self.delta_time)

########################################################################################
########################################################################################
# CIRCLE THAT FOLLOWS BALL ON THE GROUND
########################################################################################
########################################################################################

    def circle_following_ball_ground(self):
        self.objects.update_circle_position()

########################################################################################
########################################################################################
# MAIN
########################################################################################
########################################################################################

    def update(self):            
        self.jetski_control()
        self.ball_collisions()
        #self.check_wall_collisions()
        self.camera_updates()
        self.showFPS()
        self.circle_following_ball_ground()
        self.renderer.render(self.scene, self.camera)



if __name__ == "__main__":
    Main(screen_size=[SCREEN_WIDTH, SCREE_HEIGHT]).run()
