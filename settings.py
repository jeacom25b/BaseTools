import bpy
from . register import register_class, register_func, unregister_func

@register_class
class BaseToolsSettings(bpy.types.PropertyGroup):
    blobsketch_resoluition: bpy.props.FloatProperty(
        name='Resolution',
        description='How dense resulting BlobSketch geometry is. (higher values = more dense)',
        min=0,
        default=5
    )

    blobsketch_quality: bpy.props.IntProperty(
        name='Quality',
        min=20,
        default=200,
    )

@register_func
def register():
    bpy.types.Scene.base_tools = bpy.props.PointerProperty(type=BaseToolsSettings)

@unregister_func
def unregister():
    del bpy.types.Scene.base_tools
