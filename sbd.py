import bpy
import os
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.types import Operator
import math
import numpy as np
import mathutils
import bmesh

ball_module = bpy.data.texts["ball.py"].as_module()

# ------------------------------------------------------------------------
#    Global Object Creation
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

ball_loaded = False

def update_ball(self, context):
    if ((ball is not None) and ball_loaded):
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
    if ((ball is not None) and ball_loaded):
        
        ball.set_pdf_options(bpy.context.scene.sbd_pdf_width, bpy.context.scene.sbd_pdf_height, bpy.context.scene.sbd_panel_lip_size, bpy.context.scene.sbd_edge_hole_num, bpy.context.scene.sbd_panel_hole_size)
        ball.update_pdf_mesh()
        pdf_faces_mesh, pdf_lips_mesh, pdf_holes_mesh, pdf_mesh = ball.get_pdf_mesh()

        # Remove old object
        for obj in pdf_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

        for col in pdf_collection.children:
            for obj in col.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col, do_unlink=True)

        if (bpy.context.scene.sbd_pdf_display):
            count = 0
            while (count < len(pdf_faces_mesh)):
                # Make the pdf face collection object
                soccer_ball_pdf_collection = bpy.data.collections.new("soccer_ball_pdf_" + str(count))

                translation = mathutils.Vector((ball.pdf_translations[count][0] + (ball.radius * 2), ball.pdf_translations[count][1], ball.pdf_translations[count][2]))
                rotation = mathutils.Vector((ball.pdf_rotations[count][0], ball.pdf_rotations[count][1], ball.pdf_rotations[count][2]))

                # make object from mesh
                new_face = bpy.data.objects.new("pdf_face_" + str(count), pdf_faces_mesh[count])
                new_face.lock_location = (False, False, True)
                new_face.lock_rotation = (True, True, False)
                new_face.location = translation
                new_face.rotation_euler = rotation

                soccer_ball_pdf_collection.objects.link(new_face)

                # Create face lip
                new_lip = bpy.data.objects.new("pdf_lip_" + str(count), pdf_lips_mesh[count])
                new_lip.display_type = 'WIRE'
                new_lip.lock_location = (False, False, True)
                new_lip.lock_rotation = (True, True, False)
                new_lip.location = translation
                new_lip.rotation_euler = rotation

                soccer_ball_pdf_collection.objects.link(new_lip)

                # Create face holes
                hole_count = 0
                while hole_count < len(pdf_holes_mesh[count]):
                    mesh = bpy.data.meshes.new("pdf_hole_" + str(count) + "_" + str(hole_count))
                    obj = bpy.data.objects.new("pdf_hole_" + str(count) + "_" + str(hole_count), mesh)
                    obj.lock_location = (False, False, True)
                    obj.lock_rotation = (True, True, False)
                    obj.location = translation
                    obj.rotation_euler = rotation

                    soccer_ball_pdf_collection.objects.link(obj)

                    #new bmesh
                    bm = bmesh.new()
                    # load in a mesh
                    bm.from_mesh(mesh)
                    # create circle
                    geom = bmesh.ops.create_circle(bm, segments=16, radius=ball.panel_hole_size)

                    verts = geom["verts"]

                    bmesh.ops.translate(         # Translate
                        bm,
                        verts=verts,
                        vec=(pdf_holes_mesh[count][hole_count][0], pdf_holes_mesh[count][hole_count][1], 0))

                    # write back to mesh
                    bm.to_mesh(mesh)

                    hole_count+=1

                pdf_collection.children.link(soccer_ball_pdf_collection)
                count += 1

            new_pdf = bpy.data.objects.new("soccer_ball_pdf", pdf_mesh)
            new_pdf.display_type = 'WIRE'
            new_pdf.lock_location = (True, True, True)
            new_pdf.lock_rotation = (True, True, True)
            pdf_collection.objects.link(new_pdf)

# ------------------------------------------------------------------------
#    Properties
# ------------------------------------------------------------------------

bpy.types.Scene.sbd_radius = bpy.props.FloatProperty(name="Radius", update=update_ball, default=115, min=1, max=500)

bpy.types.Scene.sbd_panel_lip_size = bpy.props.FloatProperty(name="Panel Lip Size", update=update_pdf, default=115, min=0)
bpy.types.Scene.sbd_edge_hole_num = bpy.props.FloatProperty(name="Edge Hole Num", update=update_pdf, default=115, min=0)
bpy.types.Scene.sbd_panel_hole_size = bpy.props.FloatProperty(name="Panel Hole Size", update=update_pdf, default=115, min=0)

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
        global ball_loaded
        ball = ball_module.ClassicBall()

        ball_loaded = False

        bpy.context.scene.sbd_radius = ball.radius

        bpy.context.scene.sbd_panel_lip_size = ball.panel_lip_size
        bpy.context.scene.sbd_edge_hole_num = ball.edge_hole_num
        bpy.context.scene.sbd_panel_hole_size = ball.panel_hole_size

        ball_loaded = True

        update_ball(self, context)
        return {'FINISHED'}
    
class SaveBallOperator(Operator):
    bl_idname = "sbd.save_ball_operator"
    bl_label = "Save Ball Operator"

    def execute(self, context):
        return {'FINISHED'}
    
class ExportBallOperator(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "sbd.export_ball_operator"
    bl_label = "Export Ball Operator"

    # ExportHelper mixin class uses this
    filename_ext = ".pdf"
    filter_glob: bpy.props.StringProperty(default="*.pdf", options={'HIDDEN'}, maxlen=255)

    def execute(self, context):
        if ball is not None:
            ball.export_ball(self.filepath, pdf_collection)
        return {'FINISHED'}

class SavePdfLayoutOperator(Operator):
    bl_idname = "sbd.save_pdf_layout_operator"
    bl_label = "Save PDF Layout Operator"

    def execute(self, context):
        translations = []
        rotations = []

        count = 0
        for face in ball.faces:
            obj = pdf_collection.children["soccer_ball_pdf_" + str(count)].objects["pdf_face_" + str(count)]
            translations.append(np.array([obj.location[0] - (ball.radius * 2), obj.location[1], obj.location[2]]))
            rotations.append(np.array([0.0, 0.0, obj.rotation_euler[2]]))
            count+=1

        ball.update_pdf_translations(translations)
        ball.update_pdf_rotations(rotations)
        update_pdf(self, context)
        return {'FINISHED'}
    

class LoadFileOperator(Operator, ImportHelper):

    bl_idname = "sbd.load_file_operator"
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

        col.operator(SavePdfLayoutOperator.bl_idname, text="Save Pdf Layout", icon="EDITMODE_HLT")

        layout.separator()
        col = layout.column(align=True)

        col.prop(context.scene, 'sbd_pdf_width')
        col.prop(context.scene, 'sbd_pdf_height')

        layout.separator()
        col = layout.column(align=True)

        col.prop(context.scene, 'sbd_panel_lip_size')
        col.prop(context.scene, 'sbd_edge_hole_num')
        col.prop(context.scene, 'sbd_panel_hole_size')


        layout.separator()
        col = layout.column(align=True)

        col.operator(SaveBallOperator.bl_idname, text="Save Soccer Ball", icon="EXPORT")
        col.operator(ExportBallOperator.bl_idname, text="Export Soccer Ball PDF", icon="EXPORT")

        layout.separator()

# ------------------------------------------------------------------------
#    Blender Setup
# ------------------------------------------------------------------------

classes = [SBDPanel, LoadFileOperator, CreateBallOperator, SaveBallOperator, ExportBallOperator, SavePdfLayoutOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
    #bpy.ops.test.open_filebrowser('INVOKE_DEFAULT')