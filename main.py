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

    def camera_updates(self):
        if self.input.is_key_down("space"):
            self.camera_follow_mode = not self.camera_follow_mode

        if self.camera_follow_mode:
            self.camera_rig.follow_target(self.objects.jetSki, offset=[CAMERA_OFFSET_DISTANCE, CAMERA_OFFSET_Y, 0])
        else:
            self.camera_rig.follow_target_look_at(self.objects.jetSki, self.objects.ball, CAMERA_OFFSET_Y, CAMERA_OFFSET_DISTANCE)

    def check_collision(self):
        jetski_pos = self.objects.jetSki.global_position
        ball_pos = self.objects.ball.global_position

        distance = math.sqrt((jetski_pos[0] - ball_pos[0]) ** 2 + (jetski_pos[1] - ball_pos[1]) ** 2 + (jetski_pos[2] - ball_pos[2]) ** 2)
        collision_distance = 0.5  # Assume both have radius 0.25

        if distance < collision_distance:
            # Collision response: move the ball in the opposite direction
            direction = [
                ball_pos[0] - jetski_pos[0],
                ball_pos[1] - jetski_pos[1],
                ball_pos[2] - jetski_pos[2]
            ]
            magnitude = math.sqrt(direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2)
            if magnitude != 0:
                direction = [d / magnitude for d in direction]

            # Update ball velocity
            self.objects.ball_velocity = [d * 7 for d in direction]  # Adjust speed as needed

    def update(self):
        self.objects.jetSki.updateObject(self.input, self.delta_time, True)
        self.check_collision()

        # Apply gravity to the ball
        if self.objects.ball.get_position()[1] > 0.5:
            self.objects.ball_velocity[1] += self.objects.gravity * self.delta_time  # Gravity effect on the y-axis
        elif self.objects.ball_velocity[1] < 0 and self.objects.ball.get_position()[1] < 1:
            self.objects.ball_velocity[1] = 0

        # Apply attrition to the ball's velocity
        self.objects.ball_velocity = [v * self.objects.attrition for v in self.objects.ball_velocity]

        # Update ball position based on velocity
        self.objects.ball.velocity = self.objects.ball_velocity
        self.objects.ball.updateObject(self.input, self.delta_time, False)

        self.camera_updates()
        self.renderer.render(self.scene, self.camera)

if __name__ == "__main__":
    Main(screen_size=[SCREEN_WIDTH, SCREE_HEIGHT]).run()