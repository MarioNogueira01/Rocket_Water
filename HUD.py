import OpenGL.GL as GL
import numpy as np

class HUD:
    def __init__(self):
        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        self.shader_program = self.create_shader_program()

        # Define initial vertices for the boost bar
        self.boost_vertices = np.array([
            -0.9, -0.9, 0.0,  # Bottom left
             0.9, -0.9, 0.0,  # Bottom right
             0.9, -0.8, 0.0,  # Top right
             0.9, -0.8, 0.0,  # Top right
            -0.9, -0.8, 0.0,  # Top left
            -0.9, -0.9, 0.0   # Bottom left
        ], dtype=np.float32)

        self.setup_buffers()

    def setup_buffers(self):
        # Bind VAO
        GL.glBindVertexArray(self.vao)

        # Bind VBO and upload data for boost bar
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.boost_vertices.nbytes, None, GL.GL_DYNAMIC_DRAW)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, self.boost_vertices.nbytes, self.boost_vertices)

        # Define the layout of the vertex data
        position = GL.glGetAttribLocation(self.shader_program, "position")
        GL.glEnableVertexAttribArray(position)
        GL.glVertexAttribPointer(position, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

        # Unbind VAO
        GL.glBindVertexArray(0)

    def create_shader_program(self):
        # Vertex shader
        vertex_shader_source = """
        #version 330 core
        layout(location = 0) in vec3 position;
        void main() {
            gl_Position = vec4(position, 1.0);
        }
        """
        vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        GL.glShaderSource(vertex_shader, vertex_shader_source)
        GL.glCompileShader(vertex_shader)

        # Check for compilation errors
        if not GL.glGetShaderiv(vertex_shader, GL.GL_COMPILE_STATUS):
            raise Exception(GL.glGetShaderInfoLog(vertex_shader))

        # Fragment shader
        fragment_shader_source = """
        #version 330 core
        out vec4 color;
        void main() {
            color = vec4(1.0, 1.0, 1.0, 1.0);
        }
        """
        fragment_shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        GL.glShaderSource(fragment_shader, fragment_shader_source)
        GL.glCompileShader(fragment_shader)

        # Check for compilation errors
        if not GL.glGetShaderiv(fragment_shader, GL.GL_COMPILE_STATUS):
            raise Exception(GL.glGetShaderInfoLog(fragment_shader))

        # Link shaders to create the program
        shader_program = GL.glCreateProgram()
        GL.glAttachShader(shader_program, vertex_shader)
        GL.glAttachShader(shader_program, fragment_shader)
        GL.glLinkProgram(shader_program)

        # Check for linking errors
        if not GL.glGetProgramiv(shader_program, GL.GL_LINK_STATUS):
            raise Exception(GL.glGetProgramInfoLog(shader_program))

        # Clean up shaders as they are now linked into the program
        GL.glDeleteShader(vertex_shader)
        GL.glDeleteShader(fragment_shader)

        return shader_program

    def update_boost_vertices(self, new_vertices):
        self.boost_vertices = np.array(new_vertices, dtype=np.float32)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, self.boost_vertices.nbytes, self.boost_vertices)

    def render(self):
        GL.glUseProgram(self.shader_program)
        GL.glBindVertexArray(self.vao)

        # Draw boost bar
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)