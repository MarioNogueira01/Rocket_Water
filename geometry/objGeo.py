import random

from geometry.geometry import Geometry

class ObjGeo(Geometry):
    """Subclass of Geometry for loading OBJ files and applying colors per face."""
    
    def __init__(self, filename):
        super().__init__()  # Initialize the Geometry base class
        self.load_from_obj(filename)  # Load data from the OBJ file upon instantiation

    def load_from_obj(self, filename):
        """Reads vertices and UVs from an OBJ file, duplicates vertices per face for unique coloring."""
        original_vertices = []
        uvs = []  # Assuming we might also have UVs to process similarly
        face_vertices = []  # To store duplicated vertices per face
        face_colors = []  # Colors assigned per face
        face_uvs = []  # UVs duplicated per face
        
        with open(filename, 'r') as obj_file:
            for line in obj_file:
                if line.startswith('v '):  # Vertex position
                    original_vertices.append([float(value) for value in line.strip().split()[1:]])
                elif line.startswith('vt '):  # Texture coordinate
                    uvs.append([float(value) for value in line.strip().split()[1:]])
                elif line.startswith('f '):  # Face
                    # Generate a random color for this face
                    face_color = [random.random() for _ in range(3)]
                    indices = [int(part.split('/')[0]) - 1 for part in line.strip().split()[1:]]
                    for index in indices:
                        face_vertices.append(original_vertices[index])
                        face_colors.append(face_color)
                        if index < len(uvs):  # Check if there's a corresponding UV
                            face_uvs.append(uvs[index])
                        else:
                            face_uvs.append([0.0, 0.0])  # Default UV if none is available

        # Now we have duplicated vertices per face, with each set of face vertices having a unique color
        self.add_attribute("vec3", "vertexPosition", face_vertices)
        self.add_attribute("vec3", "vertexColor", face_colors)
        if face_uvs:  # Add UVs only if we have them
            self.add_attribute("vec2", "vertexUV", face_uvs)

        self.count_vertices()  # Update the vertex count based on duplicated vertices
