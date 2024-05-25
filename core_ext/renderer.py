import OpenGL.GL as GL
import pygame

from HUD import HUD
from core_ext.mesh import Mesh


class Renderer:
    def __init__(self, clear_color=[0, 0, 0]):
        GL.glEnable(GL.GL_DEPTH_TEST)
        # required for antialiasing
        GL.glEnable(GL.GL_MULTISAMPLE)
        GL.glClearColor(clear_color[0], clear_color[1], clear_color[2], 1)
        self.window_size = pygame.display.get_surface().get_size()
        self.hud = HUD()  # Initialize the HUD

    def render(self, scene, camera, clear_color=True, clear_depth=True, render_target=None):
        # activate render target
        if render_target == None:
            # set render to window
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
            GL.glViewport(0, 0, self.window_size[0], self.window_size[1])
        else:
            # set render target properties
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, render_target.framebuffer_ref)
            GL.glViewport(0, 0, render_target.width, render_target.height)
            
        if clear_color:
            # Clear color
            GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        if clear_depth:
            # Clear depth
            GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
        # blending
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        # Update camera view (calculate inverse)
        camera.update_view_matrix()
        # Extract list of all Mesh objects in scene
        descendant_list = scene.descendant_list
        mesh_filter = lambda x: isinstance(x, Mesh)
        mesh_list = list(filter(mesh_filter, descendant_list))

        for mesh in mesh_list:
            # If this object is not visible, continue to next object in list
            if not mesh.visible:
                continue
            GL.glUseProgram(mesh.material.program_ref)
            # Bind VAO
            GL.glBindVertexArray(mesh.vao_ref)
            # Update uniform values stored outside of material
            mesh.material.uniform_dict["modelMatrix"].data = mesh.global_matrix
            mesh.material.uniform_dict["viewMatrix"].data = camera.view_matrix
            mesh.material.uniform_dict["projectionMatrix"].data = camera.projection_matrix
            # Update uniforms stored in material
            for uniform_object in mesh.material.uniform_dict.values():
                uniform_object.upload_data()
            # Update render settings
            mesh.material.update_render_settings()
            GL.glDrawArrays(mesh.material.setting_dict["drawStyle"], 0, mesh.geometry.vertex_count)

        # Render the HUD
        self.render_hud()

    def render_hud(self):
        # Disable depth test for HUD rendering
        GL.glDisable(GL.GL_DEPTH_TEST)
        self.hud.render()
        # Re-enable depth test for 3D rendering
        GL.glEnable(GL.GL_DEPTH_TEST)
