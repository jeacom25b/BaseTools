import bpy
from .register import register_class

@register_class
class BaseTools_PT_BlobSketch(bpy.types.Panel):
    bl_category = 'base_tools'
    bl_label = 'Blob Sketch'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator('base_tools.blobsketch')
        col.prop(context.scene.base_tools, 'blobsketch_resoluition')
        col.prop(context.scene.base_tools, 'blobsketch_quality')

@register_class
class BaseTools_PT_Boolean(bpy.types.Panel):
    bl_category = 'base_tools'
    bl_label = 'Booleans'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator('base_tools.boolean', text='Union').operation = 'UNION'
        col.operator('base_tools.boolean', text='difference').operation = 'DIFFERENCE'
        col.operator('base_tools.boolean', text='intersect').operation = 'INTERSECT'
        col.operator('base_tools.boolean', text='slice').operation = 'slice'
