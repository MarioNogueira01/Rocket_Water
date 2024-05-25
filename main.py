import time
import math
import pygame
import OpenGL.GL as GL
from pygame import freetype
from constants import *
from core.base import Base
from core_ext.camera import Camera
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from extras.movement_rig import MovementRig
from all_objects import ObjectCreator

class Main(Base):
    def initialize(self):
        pygame.init()
        pygame.freetype.init()
        self.font = pygame.freetype.Font("game_font.otf", 24)
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=SCREEN_WIDTH / SCREEN_HEIGHT)
        self.camera_rig = MovementRig()
        self.camera_rig.add(self.camera)
        self.scene.add(self.camera_rig)
        self.objects = ObjectCreator(self)
        self.camera_follow_mode = True
        self.last_time_fps = time.time()
        self.last_time_box = time.time()
        self.frame_count = 0
        self.fps = 0
        self.boost = 100
        self.objects.create_boost_box()
        self.boostsCounter = 0
        self.score = 0
        self.opponent_score = 0

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
            self.camera_rig.follow_target_look_at(self.objects.jetSki, self.objects.ball, CAMERA_FOLLOW_OFFSET_Y,
                                                  CAMERA_OFFSET_DISTANCE)

    ########################################################################################
    ########################################################################################
    # BALL COLLISION SYSTEM
    ########################################################################################
    ########################################################################################

    def check_ball_collision_with(self, jetski_pos):
        ball_pos = self.objects.ball.global_position

        distance = math.sqrt(
            (jetski_pos[0] - ball_pos[0]) ** 2 + (jetski_pos[1] - ball_pos[1]) ** 2 + (jetski_pos[2] - ball_pos[2]) ** 2)

        if distance < HITBOX_BUFFER:
            direction = [
                ball_pos[0] - jetski_pos[0],
                ball_pos[1] - jetski_pos[1]-0.1,
                ball_pos[2] - jetski_pos[2]
            ]
            magnitude = math.sqrt(direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2)
            if magnitude != 0:
                direction = [d / magnitude for d in direction]

            self.objects.ball_velocity = [d * BALL_SPEED for d in direction]

    def ball_collisions(self):
        self.check_ball_collision_with(self.objects.jetSki.global_position)
        self.check_ball_collision_with(self.objects.opponent.global_position)

        if self.objects.ball.get_position()[1] > 0.5:
            self.objects.ball_velocity[1] += BALL_GRAVITY * self.delta_time
        elif self.objects.ball_velocity[1] < 0 and self.objects.ball.get_position()[1] < 1:
            self.objects.ball_velocity[1] = -self.objects.ball_velocity[1] * BALL_BOUNCE

        self.objects.ball_velocity = [v * BALL_ATTRITION for v in self.objects.ball_velocity]
        self.objects.ball.velocity = self.objects.ball_velocity
        self.objects.ball.updateBall(self.delta_time)

    ########################################################################################
    ########################################################################################
    # WALL COLLISION SYSTEM
    ########################################################################################
    ########################################################################################

    def check_wall_collisions(self):
        ball_pos = self.objects.ball.global_position
        next_ball_pos = [ball_pos[i] + self.objects.ball.velocity[i] * self.delta_time for i in range(3)]

        # Flags to indicate collision with walls
        collided_with_horizontal_wall = False
        collided_with_vertical_wall = False

        # Check collision with each wall
        for wall in self.objects.walls:
            (min_x, max_x), (min_z, max_z) = wall.bounds

            # Check collision with horizontal walls (top and bottom)
            if wall in self.objects.walls[:2]:
                if min_x * 2 <= next_ball_pos[0] <= max_x * 2:
                    if next_ball_pos[2] < min_z or next_ball_pos[2] > max_z:
                        self.objects.ball_velocity[2] = -self.objects.ball_velocity[2]  # Invert Z velocity
                        collided_with_horizontal_wall = True
                        break

            # Check collision with vertical walls (left and right)
            else:
                if min_z * 2 <= next_ball_pos[2] <= max_z * 2:
                    if next_ball_pos[0] < min_x or next_ball_pos[0] > max_x:
                        self.objects.ball_velocity[0] = -self.objects.ball_velocity[0]  # Invert X velocity
                        collided_with_vertical_wall = True
                        break

        # Handle collision at the corners
        if collided_with_horizontal_wall and collided_with_vertical_wall:
            self.objects.ball_velocity[0] = -self.objects.ball_velocity[0]
            self.objects.ball.velocity[2] = -self.objects.ball.velocity[2]

    ########################################################################################
    ########################################################################################
    # SHOW FPS
    ########################################################################################
    ########################################################################################

    def showFPS(self):
        current_time = time.time()
        elapsed_time = time.time() - self.last_time_fps
        self.frame_count += 1

        if elapsed_time >= 1.0:
            self.fps = self.frame_count / elapsed_time
            print(f"FPS: {self.fps:.0f}")
            self.frame_count = 0
            self.tick_count = 0
            self.last_time_fps = current_time

    ########################################################################################
    ########################################################################################
    # JETSKI MOVEMENT
    ########################################################################################
    ########################################################################################

    def jetski_control(self):
        if self.input.is_key_pressed("k") and self.boost > 0:
            self.boost -= BOOST_COST
            self.objects.jetSki.updateJetSki(self.input, self.delta_time, True)
        else:
            self.objects.jetSki.updateJetSki(self.input, self.delta_time, False)

    ########################################################################################
    ########################################################################################
    # CIRCLE THAT FOLLOWS BALL ON THE GROUND
    ########################################################################################
    ########################################################################################

    def circle_following_ball_ground(self):
        self.objects.update_circle_position()

    ########################################################################################
    ########################################################################################
    # BOOST BAR
    ########################################################################################
    ########################################################################################

    def map_value(self, x, in_min=0, in_max=100, out_min=0.3, out_max=0.9):
        if x < in_min:
            x = in_min
        elif x > in_max:
            x = in_max
        return out_min + (x - in_min) * (out_max - out_min) / (in_max - in_min)

    def update_bar_boost(self):
        width = self.map_value(self.boost)
        new_vertices = [
            BAR_BOOST_LEFT, BAR_BOOST_BOTTOM, 0.0,  # Bottom left
            width, BAR_BOOST_BOTTOM, 0.0,  # Bottom right
            width, BAR_BOOST_TOP, 0.0,  # Top right
            width, BAR_BOOST_TOP, 0.0,  # Top right
            BAR_BOOST_LEFT, BAR_BOOST_BOTTOM, 0.0,  # Top left
            BAR_BOOST_LEFT, BAR_BOOST_TOP, 0.0  # Bottom left
        ]
        return new_vertices

    ########################################################################################
    ########################################################################################
    # SCORE DISPLAY
    ########################################################################################
    ########################################################################################

    def render_scores(self, player_score, opponent_score):
        # Render player score
        player_text_surface, player_rect = self.font.render(f"{player_score}", (0, 255, 0))
        player_text_data = pygame.image.tostring(player_text_surface, "RGBA", True)
        player_text_width = player_text_surface.get_width()
        
        # Render opponent score
        opponent_text_surface, opponent_rect = self.font.render(f"{opponent_score}", (255, 0, 0))
        opponent_text_data = pygame.image.tostring(opponent_text_surface, "RGBA", True)
        opponent_text_width = opponent_text_surface.get_width()
        
        # Calculate total width and position
        total_width = player_text_width + opponent_text_width + 20  # 20 pixels space between scores
        position_x = (SCREEN_WIDTH / 2) - (total_width / 2)
        
        # Draw player score
        GL.glWindowPos2d(position_x, SCREEN_HEIGHT - 30)
        GL.glDrawPixels(player_text_surface.get_width(), player_text_surface.get_height(), GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, player_text_data)
        
        # Draw opponent score
        GL.glWindowPos2d(position_x + player_text_width + 20, SCREEN_HEIGHT - 30)
        GL.glDrawPixels(opponent_text_surface.get_width(), opponent_text_surface.get_height(), GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, opponent_text_data)

        

    ########################################################################################
    ########################################################################################
    # BOOST SPAWN
    ########################################################################################
    ########################################################################################

    def boost_box_logic(self):
        if len(self.objects.boost_boxes) < BOOST_IN_MAP_LIMIT:
            current_time = time.time()
            elapsed_time = current_time - self.last_time_box
            if elapsed_time >= TIME_DELAY_SPAWN_BOOST:
                self.last_time_box = current_time
                self.objects.create_boost_box()
        self.check_boost_box_collision()

    def check_boost_box_collision(self):
        jetski_pos = self.objects.jetSki.global_position
        for boost_box in self.objects.boost_boxes:
            box_pos = boost_box.global_position
            distance = math.sqrt((jetski_pos[0] - box_pos[0]) ** 2 + (jetski_pos[2] - box_pos[2]) ** 2)
            if distance < HITBOX_BUFFER:
                self.boost += BOOST_AMOUNT
                self.boost = min(self.boost, MAX_BOOST)
                self.objects.remove_box(boost_box)
                break

    ########################################################################################
    ########################################################################################
    # CHECK FOR GOALS
    ########################################################################################
    ########################################################################################

    def check_goal_hitboxes(self):
        ball_pos = self.objects.ball.global_position
        next_ball_pos = [ball_pos[i] + self.objects.ball.velocity[i] * self.delta_time for i in range(3)]

        for i, hitBox in enumerate(self.objects.hitBoxes):
            (min_x, max_x), (min_z, max_z) = hitBox.bounds
            if i == 0:
                if min_x <= next_ball_pos[0] <= max_x and min_z - 3 <= next_ball_pos[2] <= max_z - 3:
                    self.goalScored(True)
                    break
            elif i == 1:
                if min_x <= next_ball_pos[0] <= max_x and min_z + 3 <= next_ball_pos[2] <= max_z + 3:
                    self.goalScored(False)
                    break


    def goalScored(self, playerScored):
        self.objects.ball.set_position([0.5, 0.5, -4])
        self.objects.ball_velocity = [0, 0, 0]
        self.objects.jetSki.set_position([0.5, 0.3, 5])
        self.objects.jetSki.set_rotate_y(math.pi * 1.5)
        self.objects.opponent.set_position([0.5, 0.3, -13])
        self.objects.opponent.set_rotate_y(math.pi * 1.5)
        if playerScored:
            self.score += 1
        else:
            self.opponent_score += 1

    ########################################################################################
    ########################################################################################
    # MAIN
    ########################################################################################
    ########################################################################################

    def opponentAI(self):
        # TO FIX
        # TODO
        print(f"BEFORE: {self.objects.opponent.global_position}")
        opponent_position = self.objects.opponent.global_position
        target_position = self.objects.ball.global_position
        target_position[0] = -0.5
        target_position[1] = 0
        # if target_position[0] - opponent_position[0] < 0.1 and target_position[2] - opponent_position[2] < 0.1:
            # return
        self.objects.opponent.look_at(target_position)
        self.objects.opponent.rotate_y(math.pi * 1.5)
        self.objects.opponent.updateOpponent(self.delta_time, JETSKI_SPEED)
        print(f"AFTER: {self.objects.opponent.global_position}")


    ########################################################################################
    ########################################################################################
    # MAIN
    ########################################################################################
    ########################################################################################

    def update(self):
        self.jetski_control()
        self.ball_collisions()
        self.check_wall_collisions()
        self.camera_updates()
        self.check_goal_hitboxes()
        self.showFPS()
        self.circle_following_ball_ground()
        self.boost_box_logic()
        if self.fps > 30:
            self.opponentAI()
        self.renderer.hud.update_boost_vertices(self.update_bar_boost())
        self.renderer.render(self.scene, self.camera)
        self.render_scores(self.score, self.opponent_score)

if __name__ == "__main__":
    Main(screen_size=[SCREEN_WIDTH, SCREEN_HEIGHT]).run()
