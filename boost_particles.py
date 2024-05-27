import random
from constants import *
from core_ext.object3d import Object3D
from core_ext.mesh import Mesh
from geometry.sphere import SphereGeometry
from material.material import Material

class Particle(Object3D):
    def __init__(self, position, velocity, lifespan, scale=0.05):
        super().__init__()
        self.velocity = velocity
        self.lifespan = lifespan
        self.age = 0
        self.geometry = SphereGeometry(radius=scale, radius_segments=4, height_segments=4)
        
        # Create a material with a simple red color
        self.material = Material(vertex_shader_code, fragment_shader_code)
        self.material.add_uniform("vec3", "baseColor", [0, 0, 0.6])  # Red color
        self.material.locate_uniforms()
        
        self.mesh = Mesh(self.geometry, self.material)
        self.add(self.mesh)
        position[1] -= 0.2
        self.set_position(position)

    def update(self, delta_time):
        self.translate(self.velocity[0] * delta_time, self.velocity[1] * delta_time, self.velocity[2] * delta_time)
        self.age += delta_time
        return self.age < self.lifespan


class ParticleSystem(Object3D):
    def __init__(self, ):
        super().__init__()
        self.max_particles = MAX_BOOST_PARTICLES
        self.particles = []

    def create_particle(self, position):
        velocity = [random.uniform(-0.5, 0), random.uniform(0, 0.5), random.uniform(-0.5, 0)]
        lifespan = random.uniform(1, 3)
        particle = Particle(position, velocity, lifespan,scale=(random.uniform(0.03, 0.07)))
        self.particles.append(particle)
        self.add(particle)

    def update(self, delta_time):
        new_particles = []
        for particle in self.particles:
            if particle.update(delta_time):
                new_particles.append(particle)
            else:
                self.remove(particle)
        self.particles = new_particles

    def emit(self, position):
        if len(self.particles) < self.max_particles:
            self.create_particle(position)
            self.create_particle(position)
            self.create_particle(position)
            self.create_particle(position)


# Vertex shader code
vertex_shader_code = """
uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;
uniform mat4 modelMatrix;
in vec3 vertexPosition;
void main()
{
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
}
"""

# Fragment shader code
fragment_shader_code = """
uniform vec3 baseColor;
out vec4 fragColor;
void main()
{
    fragColor = vec4(baseColor, 1.0);
}
"""
