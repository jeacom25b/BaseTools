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

        active = context.active_object
        targets = [ob for ob in meshes if ob is not active]

        if not self.operation == 'SLICE':
            for ob in targets:
                bool_apply_objs(ob, active, self.operation)
                if not self.ngons:
                    remove_ngons(ob)
        else:
            thicc = active.modifiers.new(type='SOLIDIFY', name='solid')
            thicc.thickness = 0.00001
            for ob in targets:
                bool_apply_objs(ob, active, 'DIFFERENCE')
                if not self.ngons:
                    remove_ngons(ob)

            active.select_set(False)
            context.view_layer.objects.active = ob
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode='OBJECT')
            active.select_set(True)
            context.view_layer.objects.active = active


        if self.remove:
            bpy.data.objects.remove(active)

        return {'FINISHED'}
