import bpy
from . draw2d import Draw2D
from mathutils import Vector
from bpy_extras.view3d_utils import (location_3d_to_region_2d,
                                     region_2d_to_origin_3d,
                                     region_2d_to_vector_3d,
                                     region_2d_to_location_3d)


class OperationFailed(BaseException):
    pass


def lerp(a, b, t):
    return a + (b - a) * t


def from_2d_to_3d_normal(mouse_vector, context):
    region = context.region
    rv3d = context.space_data.region_3d
    return region_2d_to_vector_3d(region, rv3d, mouse_vector[:2]).normalized()


def from_2d_to_3d_origin(mouse_vector, context):
    region = context.region
    rv3d = context.space_data.region_3d
    return region_2d_to_origin_3d(region, rv3d, mouse_vector[:2])


def from_3d_to_2d(world_vector, context):
    region = context.region
    rv3d = context.space_data.region_3d
    return location_3d_to_region_2d(region, rv3d, world_vector)


def scene_raycast(mouse_co, context):
    origin = from_2d_to_3d_origin(mouse_co, context)
    normal = from_2d_to_3d_origin(mouse_co, context)
    view_layer = context.view_layer
    return context.scene.ray_cast(view_layer, origin, normal)


class InteractiveOperator(bpy.types.Operator):
    bl_idname = "view3d.modal"
    bl_label = "Modal"

    l_mouse = False
    r_mouse = False
    middle = False
    wheel = 0
    press = False
    release = False
    loop_generator = None
    mouse_co = Vector((0, 0, 0))
    last_mouse = Vector((0, 0, 0))

    def press_release_check(self, event, compare, property):
        if event.type == compare:
            if event.value == 'PRESS':
                setattr(self, property, True)
            elif event.value == 'RELEASE':
                setattr(self, property, False)

    def handle_mouse(self, event):
        self.wheel = 0

        self.press = event.value == 'PRESS'
        self.release = event.value == 'RELEASE'

        if event.type in {'WHEELUPMOUSE', 'PAGE_UP'}:
            self.wheel = 1

        elif event.type in {'WHEELDOWNMOUSE', 'PAGE_DOWN'}:
            self.wheel = -1

        self.press_release_check(event, 'LEFTMOUSE', 'l_mouse')
        self.press_release_check(event, 'RIGHTMOUSE', 'r_mouse')
        self.press_release_check(event, 'MIDDLEMOUSE', 'middle')

        self.last_mouse = self.mouse_co
        self.mouse_co = Vector((event.mouse_region_x, event.mouse_region_y, 0))

    def finish(self, context, type):
        pass

    def loop(self, context):
        while True:
            event = yield {'RUNNING_MODAL'}

            if event.type == 'ESC':
                return {'FINISHED'}

            raise NotImplemented('insert code here')

    def modal(self, context, event):
        self.handle_mouse(event)
        try:
            ret = self.loop_generator.send(event)

        except StopIteration as e:
            ret = e.value

        except:
            self.draw.remove_handler()
            raise

        if 'FINISHED' in ret or 'CANCELED' in ret:
            self.draw.remove_handler()
            self.finish(context, type)
        return ret

    def invoke(self, context, event):
        self.draw = Draw2D()
        self.draw.setup_handler()
        self.loop_generator = self.loop(context)
        next(self.loop_generator)

        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}


classes = [InteractiveOperator]
