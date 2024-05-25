import math
import random
import OpenGL.GL as GL

from constants import *
from core_ext.mesh import Mesh
from core_ext.texture import Texture
from geometry.circleGeometry import CircleGeometry
from geometry.objGeo import ObjGeo
from geometry.rectangle import RectangleGeometry
from geometry.sphere import SphereGeometry
from material.texture import TextureMaterial
from extras.movement_rig import MovementRig


class ObjectCreator:
    def __init__(self, example):
        self.example = example
        self.create_objects()
        self.create_field()
        self.create_contoured_invisible_walls()
        self.create_hitboxGoals()
        self.ball_velocity = [0, 0, 0]  # Initialize ball velocity
        self.boost_boxes = []  # List to store boost boxes


    def create_boost_box(self):
        box_geometry = RectangleGeometry(width=2, height=2)
        box_material = TextureMaterial(texture=Texture(file_name="images/preto.jpg"))
        boost_box = Mesh(box_geometry, box_material)
        random_x = random.uniform(-FIELD_WIDTH / 2 + FIELD_WIDTH_OFFSET, FIELD_WIDTH / 2 - FIELD_WIDTH_OFFSET)
        random_z = random.uniform(-FIELD_LENGTH / 2 + FIELD_LENGTH_OFFSET, FIELD_LENGTH / 2 - FIELD_LENGTH_OFFSET)
        boost_box.set_position([random_x, 0.5, random_z])
        self.boost_boxes.append(boost_box)
        self.example.scene.add(boost_box)

    def remove_box(self, box):
        self.boost_boxes.remove(box)
        self.example.scene.remove(box)

    def create_objects(self):
        # Add skysphere
        sky_geometry = SphereGeometry(radius=200)
        sky_material = TextureMaterial(texture=Texture(file_name="images/sky.jpg"))
        sky = Mesh(sky_geometry, sky_material)
        self.example.scene.add(sky)

        # Add sea floor
        sea_geometry = RectangleGeometry(width=1000, height=1000)
        sea_material = TextureMaterial(
            texture=Texture(file_name="images/sea.jpg"),
            property_dict={"repeatUV": [50, 50]}
        )
        sand = Mesh(sea_geometry, sea_material)
        sand.rotate_x(-math.pi / 2)
        self.example.scene.add(sand)

        # Load first object from OBJ file
        geometryball = ObjGeo('models/bola_praia.obj')
        textureball = Texture(file_name="images/texture.png")
        materialball = TextureMaterial(texture=textureball)
        self.meshball = Mesh(geometryball, materialball)
        self.ball = MovementRig()
        self.ball.add(self.meshball)
        self.ball.scale(0.3)
        self.ball.set_position([0.5, 0.5, -4])
        self.example.scene.add(self.ball)

        # Load jetski object from OBJ file
        jetSki_geometry = ObjGeo('models/jetSki.obj')
        jetSki_texture = Texture(file_name="images/jetSki.jpg")
        jetSki_material = TextureMaterial(texture=jetSki_texture)
        self.jetSki_mesh = Mesh(jetSki_geometry, jetSki_material)
        self.jetSki = MovementRig()
        self.jetSki.add(self.jetSki_mesh)
        self.jetSki.rotate_y((math.pi) * 1.5)
        self.jetSki.set_position([0.5, 0.3, 5])  # Adjust position as needed
        self.example.scene.add(self.jetSki)   

        # Create and add the circle
        circle_geometry = CircleGeometry(inner_radius=0.4, outer_radius=0.6, segments=64)
        circle_material = TextureMaterial(texture=Texture(file_name="images/branco.jpg"))  # Use an appropriate texture
        self.circle = Mesh(circle_geometry, circle_material)
        self.example.scene.add(self.circle)
        
        # Ensure initial position is correct
        self.update_circle_position()

    def update_circle_position(self):
        ball_pos = self.ball.get_position()
        self.circle.set_position([ball_pos[0], 0.1, ball_pos[2]])

    def create_field(self, goal_width=20, goal_depth=10):

        # Umbrella setup with increased scale
        umbrella_geometry = ObjGeo('models/umbrella.obj')
        umbrella_texture = Texture(file_name="images/umbrella.jpg")
        umbrella_material = TextureMaterial(texture=umbrella_texture)
        umbrella_scale = 3  # Increased scale for umbrellas

        # Positions for the four corners
        corner_positions = [
            [-FIELD_WIDTH / 2, 0, -FIELD_LENGTH / 2],
            [FIELD_WIDTH / 2, 0, -FIELD_LENGTH / 2],
            [-FIELD_WIDTH / 2, 0, FIELD_LENGTH / 2],
            [FIELD_WIDTH / 2, 0, FIELD_LENGTH / 2]
        ]
        
        # Create and place scaled umbrellas at each corner
        for pos in corner_positions:
            umbrella_mesh = Mesh(umbrella_geometry, umbrella_material)
            umbrella = MovementRig()
            umbrella.add(umbrella_mesh)
            umbrella.set_position(pos)
            umbrella.scale(umbrella_scale)  # Apply the scaling
            self.example.scene.add(umbrella)

        # Ring setup with precise placement
        ring_geometry = ObjGeo('models/ring.obj')
        ring_texture = Texture(file_name="images/ring.png")
        ring_material = TextureMaterial(texture=ring_texture)
        ring_scale = 0.05  # Smaller scale for rings

        # Centered gap calculation for goals based on the new goal width
        center_x = 0
        gap_start = center_x - goal_width / 2
        gap_end = center_x + goal_width / 2

        # Different number of rings for width and length to ensure tight fitting
        num_rings_width = 30
        num_rings_length = 40

        # Assume the original diameter of each ring is known (let's say 1 unit before scaling)
        original_ring_diameter = 1
        scaled_ring_diameter = original_ring_diameter * ring_scale  # e.g., 0.05 if scale is 0.05

        # Adjust ring spacing to ensure no overlap
        ring_spacing_width = max((FIELD_WIDTH / num_rings_width), scaled_ring_diameter)
        ring_spacing_length = max((FIELD_LENGTH / num_rings_length), scaled_ring_diameter)

        # Place rings along the width on both ends of the field (excluding goal areas)
        for i in range(num_rings_width):
            x_position = -FIELD_WIDTH / 2 + i * ring_spacing_width
            if not (gap_start < x_position < gap_end):  # Ensure rings are placed outside the goal gap
                for z_position in [-FIELD_LENGTH / 2, FIELD_LENGTH / 2]:
                    ring_mesh = Mesh(ring_geometry, ring_material)
                    ring = MovementRig()
                    ring.add(ring_mesh)
                    ring.scale(ring_scale)
                    ring.set_position([x_position, 0, z_position])
                    self.example.scene.add(ring)

        # Place rings along the length on both sides of the field, ensuring they do not extend beyond field ends
        for i in range(num_rings_length):
            z_position = -FIELD_LENGTH / 2 + i * ring_spacing_length
            if -FIELD_LENGTH / 2 < z_position < FIELD_LENGTH / 2:  # Ensure rings do not extend beyond field ends
                for x_position in [-FIELD_WIDTH / 2, FIELD_WIDTH / 2]:
                    ring_mesh = Mesh(ring_geometry, ring_material)
                    ring = MovementRig()
                    ring.add(ring_mesh)
                    ring.scale(ring_scale)
                    ring.set_position([x_position, 0, z_position])
                    self.example.scene.add(ring)

        # Goal setup with dynamic dimensions
        goal_geometry = ObjGeo('models/goal.obj')
        goal_texture = Texture(file_name="images/branco.jpg")
        goal_material = TextureMaterial(texture=goal_texture)

        # Assumptions about original model dimensions (update these if you know the exact dimensions)
        original_model_width = 1  # Original model width
        original_model_depth = 1  # Original model depth

        # Calculate scaling factors
        goal_scale_x = goal_width / original_model_width
        goal_scale_z = goal_depth / original_model_depth

        # Goal positions adjusted to center the goal
        goal_positions = [
            [-gap_start-2, 0, -FIELD_LENGTH / 2],  # Adjusted for correct centering
            [gap_start+2, 0, FIELD_LENGTH / 2]
        ]

        for idx, pos in enumerate(goal_positions):
            goal_mesh = Mesh(goal_geometry, goal_material)
            goal = MovementRig()
            goal.add(goal_mesh)
            goal.scale(goal_scale_x, 10, goal_scale_z)  # Apply non-uniform scaling
            goal.set_position(pos)
            goal.rotate_y(math.pi if idx == 0 else 0)  # Rotate goals correctly, simplifying rotation
            self.example.scene.add(goal)

    def create_contoured_invisible_walls(self):
        wall_thickness = 5  # More reasonable thickness for the walls
        exclusion_zone_width = 20  # Width of the exclusion zone around each goal
        scale_factor = 20.0  # Fator de escala para "diminuir" a imagem e repetir a textura

        # Criando o material para as paredes com a textura repetida
        wall_texture = Texture(file_name="images/field_wall.png", property_dict={"wrap": GL.GL_REPEAT}, scale_factor=scale_factor)
        wall_material = TextureMaterial(texture=wall_texture)
        wall_material.visible = True

        # Initialize the list of walls
        self.walls = []

        # Create wall geometries for horizontal (top and bottom) and vertical (left and right) walls
        horizontal_walls = [
            RectangleGeometry(width=FIELD_WIDTH, height=FIELD_LENGTH - 2 * wall_thickness),
            RectangleGeometry(width=FIELD_WIDTH, height=FIELD_LENGTH - 2 * wall_thickness),
            RectangleGeometry(width=FIELD_LENGTH, height=FIELD_LENGTH - 2 * wall_thickness),  # Subtracting the horizontal wall space
            RectangleGeometry(width=FIELD_LENGTH, height=FIELD_LENGTH - 2 * wall_thickness)
        ]

        # Wall positions assuming the center of the field as the origin
        wall_positions = [
            #paredes ao lado da baliza
            [0, 0, -(FIELD_LENGTH / 2 - wall_thickness / 2 + 1)],  # Bottom wall
            [0, 0, (FIELD_LENGTH / 2 - wall_thickness / 2 + 1)],   # Top wall
            #paredes laterais  x,z,
            [-(FIELD_WIDTH / 2 - wall_thickness / 2 + 1), 0, 0],   # Left wall
            [(FIELD_WIDTH / 2 - wall_thickness / 2 + 1), 0, 0]     # Right wall 
        ]

        # Loop to add horizontal and vertical walls
        for i, geom in enumerate(horizontal_walls):
            wall_mesh = Mesh(geom, wall_material)
            wall_mesh.set_position(wall_positions[i])
            if i < 2:  # Horizontal walls
                wall_mesh.bounds = ([-FIELD_WIDTH / 2 + exclusion_zone_width, FIELD_WIDTH / 2 - exclusion_zone_width],
                                    [-FIELD_LENGTH / 2, FIELD_LENGTH / 2])  # Fixed bounds for horizontal
            else:  # Behind Goal walls
                wall_mesh.rotate_y(-math.pi / 2) #rotate 90 degreas
                wall_mesh.bounds = ([-FIELD_WIDTH / 2, FIELD_WIDTH / 2],
                                    [-FIELD_LENGTH / 2 + wall_thickness, FIELD_LENGTH / 2 - wall_thickness])  # Fixed bounds for vertical
            self.example.scene.add(wall_mesh)
            self.walls.append(wall_mesh)

    def create_hitboxGoals(self):
        field_length = 120
        wall_thickness = 5
        scale_factor = 20.0

        hitBoxes_texture = Texture(file_name="images/field_wall.png", property_dict={"wrap": GL.GL_REPEAT}, scale_factor=scale_factor)
        hitBoxes_material = TextureMaterial(texture=hitBoxes_texture)
        hitBoxes_material.visible = True

        self.hitBoxes = []

        hitBoxesWalls = [
            RectangleGeometry(width=16, height=8),
            RectangleGeometry(width=16, height=8)
        ]

        hitBoxes_positions = [
            [0, 0, -(field_length / 2 - wall_thickness / 2 + 1)],
            [0, 0, (field_length / 2 - wall_thickness / 2 + 1)]
        ]

        for i, geom in enumerate(hitBoxesWalls):
            hitBoxes_mesh = Mesh(geom, hitBoxes_material)
            hitBoxes_mesh.set_position(hitBoxes_positions[i])

            pos_x, pos_y, pos_z = hitBoxes_positions[i]
            width = 16 / 2
            height = 8 / 2

            hitBoxes_mesh.bounds = (
                [pos_x - width, pos_x + width],
                [pos_z - height, pos_z + height]
            )

            self.example.scene.add(hitBoxes_mesh)
            self.hitBoxes.append(hitBoxes_mesh)
