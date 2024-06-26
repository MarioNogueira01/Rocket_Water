import time
import math
import pygame
import OpenGL.GL as GL
from pygame import freetype
from boost_particles import ParticleSystem
from constants import *
from core.base import Base
from core_ext.camera import Camera
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from extras.movement_rig import MovementRig
from all_objects import ObjectCreator
from light.ambient import AmbientLight
from light.directional import DirectionalLight
from light.point import PointLight
from main_menu import MainMenu

class Main(Base):
    def initialize(self):
        pygame.init()
        pygame.freetype.init()
        pygame.mixer.init()
        pygame.mixer.music.load("music.mp3")
        pygame.mixer.music.set_volume(0.05)
        pygame.mixer.music.play(-1)
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
        self.boost_camera = 0
        ambient_light = AmbientLight(color=[0.65, 0.65, 0.65])
        self.scene.add(ambient_light)
        self.directional_light = DirectionalLight(color=[0.8, 0.8, 0.8], direction=[-1, -1, 0])
        self.scene.add(self.directional_light)

        if not LOW_SPEC:
            self.particle_system = ParticleSystem()
            self.scene.add(self.particle_system)


    ########################################################################################
    ########################################################################################
    # CAMERA SYSTEM
    ########################################################################################
    ########################################################################################

    def camera_updates(self):
        if self.input.is_key_down("space"):
            self.camera_follow_mode = not self.camera_follow_mode

        if self.camera_follow_mode:
            self.camera_rig.follow_target(self.objects.jetSki, offset=[CAMERA_OFFSET_DISTANCE + self.boost_camera, CAMERA_OFFSET_Y, 0])
        else:
            self.camera_rig.follow_target_look_at(self.objects.jetSki, self.objects.ball, CAMERA_FOLLOW_OFFSET_Y,
                                                  CAMERA_OFFSET_DISTANCE + self.boost_camera )

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
        self.check_ball_collision_with(self.objects.opponent.global_position)
        self.check_ball_collision_with(self.objects.jetSki.global_position)
        ball_pos = self.objects.ball.get_position()

        if ball_pos[1] > BALL_GROUND:
            self.objects.ball_velocity[1] += BALL_GRAVITY * self.delta_time
        if self.objects.ball_velocity[1] < 0 and ball_pos[1] <= BALL_GROUND:
            self.objects.ball.set_position([ball_pos[0], BALL_GROUND, ball_pos[2]])
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

        collided_with_horizontal_wall = False
        collided_with_vertical_wall = False

        for wall in self.objects.walls:
            (min_x, max_x), (min_z, max_z) = wall.bounds

            if wall in self.objects.walls[:2]:
                if min_x * 2 <= next_ball_pos[0] <= max_x * 2:
                    if next_ball_pos[2] < min_z or next_ball_pos[2] > max_z:
                        self.objects.ball_velocity[2] = -self.objects.ball_velocity[2]  # Invert Z velocity
                        collided_with_horizontal_wall = True
                        break
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

        if elapsed_time >= 1:
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
            if not LOW_SPEC:
                self.particle_system.emit(self.objects.jetSki.get_position())
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
        font_size = 48  # Increase the font size to 48, you can adjust this as needed

        # Render player score
        player_text_surface, player_rect = self.font.render(f"{player_score}", (0, 0, 255), size=font_size)
        player_text_data = pygame.image.tostring(player_text_surface, "RGBA", True)
        player_text_width = player_text_surface.get_width()
        
        # Render opponent score
        opponent_text_surface, opponent_rect = self.font.render(f"{opponent_score}", (255, 0, 0), size=font_size)
        opponent_text_data = pygame.image.tostring(opponent_text_surface, "RGBA", True)
        opponent_text_width = opponent_text_surface.get_width()
        
        # Calculate total width and position
        total_width = player_text_width + opponent_text_width + 20  # 20 pixels space between scores
        position_x = (SCREEN_WIDTH / 2) - (total_width / 2)
        
        # Draw player score
        GL.glWindowPos2d(position_x, SCREEN_HEIGHT - 70)
        GL.glDrawPixels(player_text_surface.get_width(), player_text_surface.get_height(), GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, player_text_data)
        
        # Draw opponent score
        GL.glWindowPos2d(position_x + player_text_width + 20, SCREEN_HEIGHT - 70)
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
        for boost_box_rig, circle_rig, _ in self.objects.boost_boxes:  # Extract the rig from the tuple
            box_pos = boost_box_rig.global_position
            distance = math.sqrt((jetski_pos[0] - box_pos[0]) ** 2 + (jetski_pos[2] - box_pos[2]) ** 2)
            if distance < HITBOX_BUFFER:
                self.boost += BOOST_AMOUNT
                self.boost = min(self.boost, MAX_BOOST)
                self.objects.remove_box(boost_box_rig,circle_rig)  # Pass the rig to remove_box
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
        self.objects.ball.set_position(BALL_START_POSITION)
        self.objects.ball_velocity = [0, 0, 0]
        self.objects.jetSki.set_position(PLAYER_START_POSITION)
        self.objects.jetSki.set_rotate_y(math.pi * 1.75)
        self.objects.opponent.set_position(OPPONENT_START_POSITION)
        self.objects.opponent.set_rotate_y(math.pi * 1.75)
        self.boost = 50
        if playerScored:
            self.score += 1
        else:
            self.opponent_score += 1

    ########################################################################################
    ########################################################################################
    # OPPONENT AI
    ########################################################################################
    ########################################################################################

    def opponentAI(self):
        ball_position = self.objects.ball.global_position
        opponent_position = self.objects.opponent.global_position
        player_goal_position = [0.5, 0.5, FIELD_LENGTH / 2]

        direction_to_goal = [
            player_goal_position[0] - ball_position[0],
            player_goal_position[1] - ball_position[1],
            player_goal_position[2] - ball_position[2]
        ]

        magnitude = math.sqrt(direction_to_goal[0]**2 + direction_to_goal[1]**2 + direction_to_goal[2]**2)
        direction_to_goal = [d / magnitude for d in direction_to_goal]

        hit_position = [
            ball_position[0] - direction_to_goal[0],
            ball_position[1] - direction_to_goal[1],
            ball_position[2] - direction_to_goal[2]
        ]

        self.objects.opponent.look_at(hit_position)
        self.objects.opponent.rotate_y(math.pi * 1.5)
        self.objects.opponent.updateOpponent(self.delta_time, JETSKI_SPEED * OPPONENT_DIFFICULTY, GROUND)

        # Check if the opponent is close enough to the ball to hit it
        distance_to_ball = math.sqrt(
            (opponent_position[0] - ball_position[0]) ** 2 +
            (opponent_position[1] - ball_position[1]) ** 2 +
            (opponent_position[2] - ball_position[2]) ** 2
        )

        if distance_to_ball < HITBOX_BUFFER:
            # Calculate the direction to apply to the ball
            direction = [
                ball_position[0] - opponent_position[0],
                ball_position[1] - opponent_position[1],
                ball_position[2] - opponent_position[2]
            ]
            magnitude = math.sqrt(direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2)
            if magnitude != 0:
                direction = [d / magnitude for d in direction]

            self.objects.ball_velocity = [d * BALL_SPEED for d in direction]


    def rotate_blue_red_labels(self):
        self.objects.blue.rotate_y(0.1 * self.delta_time)
        self.objects.red.rotate_y(0.1 * self.delta_time)
    

    ########################################################################################
    ########################################################################################
    # SPECTATORS MOVEMENT
    ########################################################################################
    ########################################################################################

    def update_sine_wave_spectators(self):
        for sphere_rig, frequency in self.objects.spheres:
            original_position = sphere_rig.global_position
            new_y = GROUND + 0.2 + SPECTATORS_JUMP_AMPLITUDE * math.sin(frequency * time.time())
            sphere_rig.set_position([original_position[0], new_y, original_position[2]])

    ########################################################################################
    ########################################################################################
    # SPECTATORS MOVEMENT
    ########################################################################################
    ########################################################################################

    def update_sine_wave_boost_box(self):
        for boost_box_rig, _, frequency in self.objects.boost_boxes:
            original_position = boost_box_rig.global_position
            new_y = BOOST_GROUND + BOOST_JUMP_AMPLITUDE * math.sin(frequency * time.time())
            boost_box_rig.set_position([original_position[0], new_y, original_position[2]])




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

        if not LOW_SPEC:
            self.particle_system.update(self.delta_time)
            self.rotate_blue_red_labels()
            self.update_sine_wave_spectators()
            self.update_sine_wave_boost_box()
            self.objects.update_sine_wave_field()

        if self.fps > 25: # fixes weird bug for some reason
            self.opponentAI()

        self.renderer.hud.update_boost_vertices(self.update_bar_boost())
        self.renderer.render(self.scene, self.camera)
        self.render_scores(self.score, self.opponent_score)

        if self.input.is_key_down("escape"):
            self.quit_to_main_menu()

    def quit_to_main_menu(self):
        pygame.display.quit()
        pygame.display.init()
        pygame.freetype.init()
        menu = MainMenu()
        menu.run()

def run_game():
    Main(screen_size=[SCREEN_WIDTH, SCREEN_HEIGHT]).run()


if __name__ == "__main__":
    run_game()

