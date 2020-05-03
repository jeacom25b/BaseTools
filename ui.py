import bpy

class BlobSketch(bpy.types.Panel):
    bl_category = 'BaseTools'
    bl_label = 'Blob Sketch'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        layout.operator('basetools.blobsketch')

classes = [BlobSketch]
