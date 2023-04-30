import bpy
import os
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.types import Operator
import math
import numpy as np

import sys
import subprocess
import os

def python_exec():
    import os
    import bpy
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
#    Globals
# ------------------------------------------------------------------------

# Make collection
try:
    ball_collection = bpy.data.collections["soccer_balls"]
except:
    ball_collection = bpy.data.collections.new('soccer_balls')
    bpy.context.scene.collection.children.link(ball_collection)

# Make collection
try:
    pdf_collection = bpy.data.collections["pdf_components"]
except:
    pdf_collection = bpy.data.collections.new('pdf_components')
    bpy.context.scene.collection.children.link(pdf_collection)

# Soccer Ball
ball = None

def update_ball(self, context):
    if (ball is not None):
        # Remove old object
        for obj in ball_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

        # Make any needed modifications to mesh
        ball.update_radius(bpy.context.scene.sbd_radius)

        # make object from mesh
        new_object = bpy.data.objects.new('soccer_ball', ball.get_mesh())
        # add object to scene collection
        ball_collection.objects.link(new_object)


        update_pdf(self, context)

def update_pdf(self, context):
    if (ball is not None):
        
        ball.set_pdf_dim(bpy.context.scene.sbd_pdf_width, bpy.context.scene.sbd_pdf_height)
        ball.update_pdf_mesh()
        pdf_faces_mesh, pdf_mesh = ball.get_pdf_mesh()

        # Remove old object
        for obj in pdf_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

        if (bpy.context.scene.sbd_pdf_display):
            count = 0
            while (count < len(pdf_faces_mesh)):
                # make object from mesh
                new_object = bpy.data.objects.new("soccer_ball_pdf_" + str(count), pdf_faces_mesh[count])
                new_object.lock_location = (False, False, True)
                new_object.lock_rotation = (True, True, True)

                # add object to scene collection
                pdf_collection.objects.link(new_object)
                count += 1
            new_pdf = bpy.data.objects.new("soccer_ball_pdf", pdf_mesh)
            new_pdf.display_type = 'WIRE'
            new_pdf.lock_location = (True, True, True)
            new_pdf.lock_rotation = (True, True, True)
            pdf_collection.objects.link(new_pdf)

bpy.types.Scene.sbd_radius = bpy.props.FloatProperty(name="Radius", update=update_ball, default=115, min=1, max=500)
bpy.types.Scene.sbd_pdf_display = bpy.props.BoolProperty(name="Pdf Display", update=update_pdf, default=False)
bpy.types.Scene.sbd_pdf_width = bpy.props.FloatProperty(name="Pdf Width", update=update_pdf, default=500, min=10)
bpy.types.Scene.sbd_pdf_height = bpy.props.FloatProperty(name="Pdf Height", update=update_pdf, default=500, min=10)

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class CreateBallOperator(Operator):
    bl_idname = "sbd.create_ball_operator"
    bl_label = "Create Ball Operator"

    def execute(self, context):
        global ball
        ball = ClassicBall()

        bpy.context.scene.sbd_radius = ball.radius
        update_ball(self, context)
        return {'FINISHED'}

class UpdatePdfTranslationsOperator(Operator):
    bl_idname = "sbd.update_pdf_translations_operator"
    bl_label = "Update PDF Translations"

    def execute(self, context):
        translations = []

        for obj in pdf_collection.objects[1:]:
            translations.append(np.array(obj.location))

        ball.update_pdf_translations(translations)
        update_pdf(self, context)
        return {'FINISHED'}
    

class LoadFileOperator(Operator, ImportHelper):

    bl_idname = "sbd.load_file"
    bl_label = "Open the file browser (yay)"
    
    filter_glob: StringProperty(
        default='*.jpg;*.jpeg;*.png;',
        options={'HIDDEN'}
    )
    
    some_boolean: BoolProperty(
        name='Do a thing',
        description='Do a thing with the file you\'ve selected',
        default=True,
    )

    def execute(self, context):
        """Do something with the selected file(s)."""

        filename, extension = os.path.splitext(self.filepath)
        
        print('Selected file:', self.filepath)
        print('File name:', filename)
        print('File extension:', extension)
        print('Some Boolean:', self.some_boolean)
        
        return {'FINISHED'}
    
class ExportFileOperator(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "sbd.export_file"
    bl_label = "Export Ball"

    # ExportHelper mixin class uses this
    filename_ext = ".pdf"
    filter_glob: bpy.props.StringProperty(default="*.pdf", options={'HIDDEN'}, maxlen=255)

    def execute(self, context):
        if ball is not None:
            ball.export_ball(self.filepath)
        return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class SBDPanel(bpy.types.Panel):
    bl_label = "Soccer Ball Designer"
    bl_idname = "PT_SBD"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SBD"
    
    def draw(self, context):
        layout = self.layout

        layout.label(text="Geometry Creation:")

        col = layout.column(align=True)
        col.operator(CreateBallOperator.bl_idname, text="Import Soccer Ball", icon="IMPORT")
        layout.separator()
        col = layout.column(align=True)
        col.operator(CreateBallOperator.bl_idname, text="Create Classic Ball", icon="MESH_UVSPHERE")
        col.operator(CreateBallOperator.bl_idname, text="Create Polyhedron Ball", icon="MESH_ICOSPHERE")
        col.operator(CreateBallOperator.bl_idname, text="Create Spherical Arc Ball", icon="SPHERE")

        layout.separator()

        layout.label(text="Geometry Editing:")
        col = layout.column(align=True)
        col.prop(context.scene, 'sbd_radius', slider=True)


        layout.separator()

        layout.label(text="Export:")
        col = layout.column(align=True)
        col.prop(context.scene, 'sbd_pdf_display')

        layout.separator()
        col = layout.column(align=True)

        col.operator(UpdatePdfTranslationsOperator.bl_idname, text="Update Pdf Translation", icon="CURVE_PATH")

        layout.separator()
        col = layout.column(align=True)

        col.prop(context.scene, 'sbd_pdf_width')
        col.prop(context.scene, 'sbd_pdf_height')
        col.operator(ExportFileOperator.bl_idname, text="Export Soccer Ball", icon="EXPORT")

        layout.separator()

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

        self.radius = None

        self.panel_lip_size = None

        # Num of holes per edge
        self.panel_hole_num = None

        self.panel_hole_size = None

    def get_mesh(self):
        mesh = bpy.data.meshes.new(name="Soccer Ball")
        mesh.from_pydata(self.verts, self.edges, self.faces)
        mesh.update()
        return mesh
    
    def get_pdf_mesh(self):
        meshes = []
        face_index = 0
        while (face_index < len(self.verts_pdf)):
            mesh = bpy.data.meshes.new(name="Soccer Ball PDF")
            mesh.from_pydata(self.verts_pdf[face_index], self.edges_pdf[face_index], self.faces_pdf[face_index])
            mesh.update()
            meshes.append(mesh)
            face_index+=1
        pdf_mesh = bpy.data.meshes.new(name="PDF")
        pdf_mesh.from_pydata([[self.radius * 2, 0, 0],[self.radius * 2, self.pdf_height, 0],[self.radius * 2 + self.pdf_width, 0, 0],[self.radius * 2 + self.pdf_width, self.pdf_height, 0]], [], [[0,1,3,2]])
        pdf_mesh.update()
        return meshes, pdf_mesh

    def update_pdf_translations(self, translations):
        self.pdf_translations = translations
    
    def update_pdf_mesh(self):
        verts_pdf = []
        edges_pdf = []
        faces_pdf = []

        if (self.pdf_translations is None):
            self.pdf_translations = []
            for face in self.faces:
                self.pdf_translations.append(np.array([0, 0, 0]))

        face_count = 0
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

            rotated_face = [np.array([self.radius * 2.0, 0, 0]) + self.pdf_translations[face_count]]

            count = 1
            for vector in translated_face[1:]:
                rot_v = rot_matrix @ vector
                rot_v = np.asarray(rot_v).reshape(-1) + np.array([self.radius * 2.0, 0, 0] + self.pdf_translations[face_count])
                rotated_face.append(rot_v)
                count+=1

            # Add to pdf mesh list
            verts_pdf.append(list(rotated_face))
            edges_pdf.append([])

            f = []
            i = 0
            while i < len(face):
                f.append(i)
                i+=1
            faces_pdf.append([f])
            face_count+=1

        self.verts_pdf = verts_pdf
        self.edges_pdf = edges_pdf
        self.faces_pdf = faces_pdf

    def set_pdf_dim(self, width, height):
        self.pdf_width = width
        self.pdf_height = height

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

    def export_ball(self, file_path):
        pdf = canvas.Canvas(file_path, pagesize=((self.pdf_width/25.4) * 72, (self.pdf_height/25.4) * 72))

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
        self.panel_hole_num = 9
        self.panel_hole_size = 1

        self.pdf_translations = None

        self.update_radius(self.radius)
        self.update_pdf_mesh()


# ------------------------------------------------------------------------
#    Blender Setup
# ------------------------------------------------------------------------

classes = [SBDPanel, LoadFileOperator, CreateBallOperator, ExportFileOperator, UpdatePdfTranslationsOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
    #bpy.ops.test.open_filebrowser('INVOKE_DEFAULT')