import bpy
import math
import numpy as np

# ------------------------------------------------------------------------
#    Weird Import Stuff
# ------------------------------------------------------------------------

import subprocess

def python_exec():
    try:
        path = bpy.app.binary_path_python
    except AttributeError:
        import sys
        path = sys.executable
    return os.path.abspath(path)

try:
    from reportlab.pdfgen import canvas
except:
    python_exe = python_exec()

    subprocess.call([python_exe, "-m", "ensurepip"])
    subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.call([python_exe, "-m", "pip", "install", "reportlab"])
    from reportlab.pdfgen import canvas

# ------------------------------------------------------------------------
#    Soccer Balls
# ------------------------------------------------------------------------

class SoccerBall:
    def __init__(self):
        self.verts = None
        self.edges = None
        self.faces = None

        self.verts_pdf = None
        self.edges_pdf = None
        self.faces_pdf = None

        self.pdf_width = None
        self.pdf_height = None

        self.pdf_translations = None
        self.pdf_rotations = None

        self.radius = None

        self.panel_lip_size = None

        # Num of holes per edge
        self.edge_hole_num = None

        # Radius
        self.panel_hole_size = None

    def get_mesh(self):
        mesh = bpy.data.meshes.new(name="Soccer Ball")
        mesh.from_pydata(self.verts, self.edges, self.faces)
        mesh.update()
        return mesh
    
    def get_pdf_mesh(self):
        face_meshes = []
        lip_meshes = []
        holes_meshes = []
        face_index = 0
        while (face_index < len(self.verts_pdf)):
            mesh = bpy.data.meshes.new(name="Soccer Ball PDF")
            mesh.from_pydata(self.verts_pdf[face_index], self.edges_pdf[face_index], self.faces_pdf[face_index])
            mesh.update()
            face_meshes.append(mesh)

            # Calculate lip mesh
            new_verts = []
            verts = self.verts_pdf[face_index]
            for vert in verts:
                vert_len = np.linalg.norm(np.array(vert))
                wanted_len = vert_len + self.panel_lip_size
                scale = wanted_len/vert_len
                new_verts.append(list(np.array(vert) * scale))
            mesh = bpy.data.meshes.new(name="Soccer Ball PDF")
            mesh.from_pydata(new_verts, self.edges_pdf[face_index], self.faces_pdf[face_index])
            mesh.update()
            lip_meshes.append(mesh)

            # Calculate holes
            holes = []
            first_vert = np.array(verts[self.faces_pdf[face_index][0][0]])
            last_vert = np.array(verts[self.faces_pdf[face_index][0][-1]])

            edge = first_vert - last_vert
            step = np.linalg.norm(edge)/(int(self.edge_hole_num)-1)
            for i in range(int(self.edge_hole_num)):
                wanted = i * step
                scale = wanted/np.linalg.norm(edge)

                holes.append((edge*scale) + last_vert)

            count = 0
            while count < len(self.faces_pdf[face_index][0]) - 1:
                first_vert = np.array(verts[self.faces_pdf[face_index][0][count]])
                last_vert = np.array(verts[self.faces_pdf[face_index][0][count + 1]])

                edge = first_vert - last_vert

                step = np.linalg.norm(edge)/(int(self.edge_hole_num)-1)
                for i in range(int(self.edge_hole_num)):
                    wanted = i * step
                    scale = wanted/np.linalg.norm(edge)

                    holes.append((edge*scale) + last_vert)
                count+=1

            holes_meshes.append(holes)

            face_index+=1

        pdf_mesh = bpy.data.meshes.new(name="PDF")
        pdf_mesh.from_pydata([[self.radius * 2, 0, 0],[self.radius * 2, self.pdf_height, 0],[self.radius * 2 + self.pdf_width, 0, 0],[self.radius * 2 + self.pdf_width, self.pdf_height, 0]], [], [[0,1,3,2]])
        pdf_mesh.update()
        return face_meshes, lip_meshes, holes_meshes, pdf_mesh

    def update_pdf_translations(self, translations):
        self.pdf_translations = translations

    def update_pdf_rotations(self, rotations):
        self.pdf_rotations = rotations
    
    def update_pdf_mesh(self):
        verts_pdf = []
        edges_pdf = []
        faces_pdf = []

        if (self.pdf_translations is None):
            self.pdf_translations = []
            for face in self.faces:
                self.pdf_translations.append(np.array([0, 0, 0]))

        for face in self.faces:
            # Make a vertex the new origin of the polygon
            translated_face = []
            base_vert = np.array(list(self.verts[face[0]]))
            for vert in face:
                v = np.array(list(self.verts[vert]))
                trans = v - base_vert
                translated_face.append(trans)
        
            # Rotate the vertices so that it rests on the xy plane
            v1 = translated_face[1]
            v2 = translated_face[2]

            normal = np.cross(v1, v2)
            normal /= np.linalg.norm(normal)

            a = normal
            b = np.array([0,0,1])

            v = np.cross(a, b)
            c = np.dot(a, b)

            vx = np.matrix([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])

            rot_matrix = np.eye(3) + vx + (vx @ vx) * (1/(1+c))

            rotated_face = [np.array([0, 0, 0])]
            vector_sum = np.array([0.0, 0.0, 0.0])

            for vector in translated_face[1:]:
                rot_v = rot_matrix @ vector
                rot_v = np.asarray(rot_v).reshape(-1)
                vector_sum += rot_v
                rotated_face.append(rot_v)

            centered_face = []
            for vector in rotated_face:
                centered_face.append(vector - (vector_sum/len(face)))

            # Add to pdf mesh list
            verts_pdf.append(list(centered_face))
            edges_pdf.append([])

            f = []
            i = 0
            while i < len(face):
                f.append(i)
                i+=1
            faces_pdf.append([f])

        self.verts_pdf = verts_pdf
        self.edges_pdf = edges_pdf
        self.faces_pdf = faces_pdf

    def set_pdf_options(self, width, height, lip, hole_num, hole_size):
        self.pdf_width = width
        self.pdf_height = height
        self.panel_lip_size = lip
        self.edge_hole_num = hole_num
        self.panel_hole_size = hole_size


    def update_radius(self, radius):
        self.radius = radius

        vert = self.verts[0]
        length = math.sqrt(math.pow(vert[0], 2) + math.pow(vert[1], 2) + math.pow(vert[2], 2))
        ratio = self.radius/length

        count = 0
        for vert in self.verts:
            self.verts[count] = (vert[0] * ratio, vert[1] * ratio, vert[2] * ratio)
            count+=1
    
    def import_ball(self):
        pass

    def save_ball(self):
        pass

    def export_ball(self, file_path, pdf_collection):
        pdf = canvas.Canvas(file_path, pagesize=((self.pdf_width/25.4) * 72, (self.pdf_height/25.4) * 72))

        # Loop through panels
        for obj in pdf_collection.objects:
            name_str = obj.name.split("_")
            if (name_str[0] + name_str[1] + name_str[2] == "soccerballpdf"):
                if (len(name_str) == 4):
                    pass
                    # Draw outline + lip
                    # Draw holes on outline

        pdf.save()

class PolyhedronBall(SoccerBall):
    def __init__(self):
        pass

class SphericalArcBall(SoccerBall):
    def __init__(self):
        pass
    
    def import_ball(self):
        pass

    def save_ball(self):
        pass

    def export_ball(self):
        pass

class ClassicBall(PolyhedronBall):
    def __init__(self):
        self.verts = [(-0.29814159870147705, 0.0, -0.815738320350647), 
                      (-0.09212832152843475, 0.2835466265678406, -0.815738320350647), 
                      (0.24119998514652252, 0.17523999512195587, -0.815738320350647), 
                      (0.24119998514652252, -0.17523999512195587, -0.815738320350647), 
                      (-0.09212832152843475, -0.2835466265678406, -0.815738320350647), 
                      (0.7235999703407288, -0.17524001002311707, -0.4472149908542633), 
                      (0.7805416584014893, -0.35048002004623413, -0.14907169342041016), 
                      (0.5745283365249634, -0.6340266466140747, -0.14907169342041016), 
                      (0.3902716636657715, -0.6340266466140747, -0.4472149908542633), 
                      (0.48240000009536743, -0.35048002004623413, -0.631476640701294), 
                      (-0.1842566877603531, -0.5670933723449707, -0.631476640701294), 
                      (0.056943297386169434, -0.7423333525657654, -0.4472149908542633), 
                      (-0.09212836623191833, -0.8506399989128113, -0.14907169342041016), 
                      (-0.4254566431045532, -0.7423333525657654, -0.14907169342041016), 
                      (-0.4823983311653137, -0.5670933723449707, -0.4472149908542633), 
                      (-0.5962833762168884, 0.0, -0.631476640701294), 
                      (-0.6884116530418396, -0.28354665637016296, -0.4472149908542633), 
                      (-0.837483286857605, -0.17523999512195587, -0.14907169342041016), 
                      (-0.837483286857605, 0.17523999512195587, -0.14907169342041016), 
                      (-0.6884116530418396, 0.28354665637016296, -0.4472149908542633), 
                      (-0.1842566877603531, 0.5670933723449707, -0.631476640701294), 
                      (-0.4823983311653137, 0.5670933723449707, -0.4472149908542633), 
                      (-0.4254566431045532, 0.7423333525657654, -0.14907169342041016), 
                      (-0.09212836623191833, 0.8506399989128113, -0.14907169342041016), 
                      (0.056943297386169434, 0.7423333525657654, -0.4472149908542633), 
                      (0.7235999703407288, 0.17524001002311707, -0.4472149908542633), 
                      (0.48240000009536743, 0.35048002004623413, -0.631476640701294), 
                      (0.3902716636657715, 0.6340266466140747, -0.4472149908542633), 
                      (0.5745283365249634, 0.6340266466140747, -0.14907169342041016), 
                      (0.7805416584014893, 0.35048002004623413, -0.14907169342041016), 
                      (0.09212836623191833, -0.8506399989128113, 0.14907169342041016), 
                      (0.4254566431045532, -0.7423333525657654, 0.14907169342041016), 
                      (0.4823983311653137, -0.5670933723449707, 0.4472149908542633), 
                      (0.1842566877603531, -0.5670933723449707, 0.631476640701294), 
                      (-0.056943297386169434, -0.7423333525657654, 0.4472149908542633), 
                      (-0.7805416584014893, -0.35048002004623413, 0.14907169342041016), 
                      (-0.5745283365249634, -0.6340266466140747, 0.14907169342041016), 
                      (-0.3902716636657715, -0.6340266466140747, 0.4472149908542633), 
                      (-0.48240000009536743, -0.35048002004623413, 0.631476640701294), 
                      (-0.7235999703407288, -0.17524001002311707, 0.4472149908542633), 
                      (-0.5745283365249634, 0.6340266466140747, 0.14907169342041016), 
                      (-0.7805416584014893, 0.35048002004623413, 0.14907169342041016), 
                      (-0.7235999703407288, 0.17524001002311707, 0.4472149908542633), 
                      (-0.48240000009536743, 0.35048002004623413, 0.631476640701294), 
                      (-0.3902716636657715, 0.6340266466140747, 0.4472149908542633), 
                      (0.4254566431045532, 0.7423333525657654, 0.14907169342041016), 
                      (0.09212836623191833, 0.8506399989128113, 0.14907169342041016), 
                      (-0.056943297386169434, 0.7423333525657654, 0.4472149908542633), 
                      (0.1842566877603531, 0.5670933723449707, 0.631476640701294), 
                      (0.4823983311653137, 0.5670933723449707, 0.4472149908542633), 
                      (0.837483286857605, -0.17523999512195587, 0.14907169342041016), 
                      (0.837483286857605, 0.17523999512195587, 0.14907169342041016), 
                      (0.6884116530418396, 0.28354665637016296, 0.4472149908542633), 
                      (0.5962833762168884, 0.0, 0.631476640701294), 
                      (0.6884116530418396, -0.28354665637016296, 0.4472149908542633), 
                      (0.09212832152843475, -0.2835466265678406, 0.815738320350647), 
                      (0.29814159870147705, 0.0, 0.815738320350647), 
                      (0.09212832152843475, 0.2835466265678406, 0.815738320350647), 
                      (-0.24119998514652252, 0.17523999512195587, 0.815738320350647), 
                      (-0.24119998514652252, -0.17523999512195587, 0.815738320350647)]
        
        self.edges = []
        self.faces = [[5, 9, 3, 2, 26, 25], 
                      [1, 0, 15, 19, 21, 20], 
                      [4, 3, 9, 8, 11, 10], 
                      [2, 1, 20, 24, 27, 26], 
                      [12, 11, 8, 7, 31, 30], 
                      [7, 6, 50, 54, 32, 31], 
                      [6, 5, 25, 29, 51, 50], 
                      [13, 12, 30, 34, 37, 36], 
                      [18, 17, 35, 39, 42, 41], 
                      [23, 22, 40, 44, 47, 46], 
                      [17, 16, 14, 13, 36, 35], 
                      [22, 21, 19, 18, 41, 40], 
                      [28, 27, 24, 23, 46, 45], 
                      [29, 28, 45, 49, 52, 51], 
                      [33, 32, 54, 53, 56, 55], 
                      [38, 37, 34, 33, 55, 59], 
                      [43, 42, 39, 38, 59, 58], 
                      [48, 47, 44, 43, 58, 57], 
                      [53, 52, 49, 48, 57, 56], 
                      [0, 1, 2, 3, 4], 
                      [5, 6, 7, 8, 9], 
                      [10, 11, 12, 13, 14], 
                      [15, 16, 17, 18, 19], 
                      [20, 21, 22, 23, 24], 
                      [25, 26, 27, 28, 29], 
                      [30, 31, 32, 33, 34], 
                      [35, 36, 37, 38, 39], 
                      [40, 41, 42, 43, 44], 
                      [45, 46, 47, 48, 49], 
                      [50, 51, 52, 53, 54], 
                      [55, 56, 57, 58, 59], 
                      [0, 4, 10, 14, 16, 15]]
        
        self.radius = 115
        self.panel_lip_size = 3
        self.edge_hole_num = 9
        self.panel_hole_size = 1

        self.pdf_translations = []
        self.pdf_rotations = []
        for face in self.faces:
            self.pdf_translations.append(np.array([0.0, 0.0, 0.0]))
            self.pdf_rotations.append(np.array([0.0, 0.0, 0.0]))

        self.update_radius(self.radius)
        self.update_pdf_mesh()
