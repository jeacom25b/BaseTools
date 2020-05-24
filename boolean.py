import bpy
import bmesh
from bpy import context
from . register import register_class


def bool_apply_objs(obj1, obj2, operation):
    md = obj1.modifiers.new(type='BOOLEAN', name='bool')
    md.operation = operation
    md.object = obj2
    old_active = bpy.context.active_object
    bpy.context.view_layer.objects.active = obj1
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.context.view_layer.objects.active = old_active


def remove_ngons(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    faces = [f for f in bm.faces if len(f.verts) > 4]
    bmesh.ops.triangulate(bm, faces=faces)
    bm.to_mesh(ob.data)


@register_class
class Boolean(bpy.types.Operator):
    bl_idname = 'base_tools.boolean'
    bl_label = 'Boolean'
    bl_options = {'REGISTER', 'UNDO'}

    operation: bpy.props.EnumProperty(
        name='Operation',
        items=[
            ('UNION', 'union', 'union'),
            ('DIFFERENCE', 'difference', 'difference'),
            ('INTERSECT', 'intersect', 'intersect'),
            ('SLICE', 'slice', 'cut objects using active as knife')
        ]
    )

    remove: bpy.props.BoolProperty(
        name='remove',
        description='Remove active object after operation',
        default=True
    )

    ngons: bpy.props.BoolProperty(
        name='ngons',
        description='allow ngons in mesh',
        default=True
    )

    def execute(self, context):
        meshes = [ob for ob in context.selected_objects if ob.type == 'MESH']

        if not context.active_object.type == 'MESH':
            self.report(type={'ERROR_INVALID_CONTEXT'}, message='active object must be a mesh')
            return {'CANCELLED'}

        if len(meshes) < 2:
            self.report(type={'ERROR_INVALID_CONTEXT'}, message='must have at least two meshes selected')
            return {'CANCELLED'}

        obj2 = context.active_object
        obj1s = [ob for ob in meshes if ob is not obj2]

        if not self.operation == 'SLICE':
            for obj1 in obj1s:
                bool_apply_objs(obj1, obj2, self.operation)
                if not self.ngons:
                    remove_ngons(obj1)
        else:
            obj2.select_set(False)
            for obj in context.selected_objects:
                if not obj.type == 'MESH':
                    ob.select_set(False)
            bpy.ops.object.duplicate()

            obj3s = list(context.selected_objects)

            for obj1 in obj1s:
                bool_apply_objs(obj1, obj2, 'DIFFERENCE')
                if not self.ngons:
                    remove_ngons(obj1)

            for obj3 in obj3s:
                bool_apply_objs(obj3, obj2, 'INTERSECT')
                if not self.ngons:
                    remove_ngons(obj1)

        if self.remove:
            bpy.data.objects.remove(obj2)

        return {'FINISHED'}
