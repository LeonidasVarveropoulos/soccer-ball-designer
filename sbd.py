import bpy
import os
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.types import Operator

# ------------------------------------------------------------------------
#    Globals
# ------------------------------------------------------------------------

# Make collection
try:
    ball_collection = bpy.data.collections["soccer_balls"]
except:
    ball_collection = bpy.data.collections.new('soccer_balls')
    bpy.context.scene.collection.children.link(ball_collection)

# Soccer Ball
ball = None

def update_ball():
    if (ball is not None):
        # Remove old object
        try:
          bpy.ops.object.select_all(action='DESELECT')
          ball_collection.objects["soccer_ball"].select_set(True)
          bpy.ops.object.delete() 
        except:
          pass

        # make object from mesh
        new_object = bpy.data.objects.new('soccer_ball', ball.get_mesh())
        # add object to scene collection
        ball_collection.objects.link(new_object)


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class CreateBallOperator(Operator):
    bl_idname = "sbw.create_ball_operator"
    bl_label = "Create Ball Operator"

    def execute(self, context):
        global ball
        ball = ClassicBall()
        update_ball()
        return {'FINISHED'}

class LoadFileOperator(Operator, ImportHelper):

    bl_idname = "sbw.load_file"
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
    bl_idname = "sbw.export_file"
    bl_label = "Export Ball"

    # ExportHelper mixin class uses this
    filename_ext = ".pdf"
    filter_glob: bpy.props.StringProperty(default="*.pdf", options={'HIDDEN'}, maxlen=255)

    def execute(self, context):
        print(self.filepath)
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


        layout.separator()

        layout.label(text="Export:")
        col = layout.column(align=True)
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

    def get_mesh(self):
        mesh = bpy.data.meshes.new(name="Soccer Ball")
        mesh.from_pydata(self.verts, self.edges, self.faces)
        mesh.update()
        return mesh
    
    def import_ball(self):
        pass

    def save_ball(self):
        pass

    def export_ball(self):
        pass

class PolyhedronBall(SoccerBall):
    def __init__(self):
        pass

class SphericalArcBall(SoccerBall):
    def __init__(self):
        pass

class ClassicBall(SoccerBall):
    def __init__(self):
        self.generate()

    def generate(self):
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

# ------------------------------------------------------------------------
#    Blender Setup
# ------------------------------------------------------------------------

classes = [SBDPanel, LoadFileOperator, CreateBallOperator, ExportFileOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
    #bpy.ops.test.open_filebrowser('INVOKE_DEFAULT')