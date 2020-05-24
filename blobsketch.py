import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

from . interact import InteractiveOperator, from_2d_to_3d_origin, from_3d_to_2d, from_2d_to_3d_normal, from_2d_to_3d, lerp, OperationFailed, scene_raycast
from .register import register_class


@register_class
class BlobSketch(InteractiveOperator):
    bl_idname = 'base_tools.blobsketch'
    bl_label = 'Blob Sketch'
    bl_options = {'REGISTER', 'UNDO'}

    def loop(self, context):
        event = yield {'RUNNING_MODAL'}
        event = yield {'RUNNING_MODAL'}

        points = []

        while True:

            if self.l_mouse:
                co = self.mouse_co
                if not points or (co - points[-1]).length > 10:
                    points.append(co)
                    points[-5:] = smooth_polyline(points[-5:])

            self.draw.clear()
            self.draw.add_circle(self.mouse_co, 3, 6, color=(0, 0, 0, 1))

            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                self.draw.add_line(p1.to_2d(), p2.to_2d(), color_a=(1, 0, 0, 1))

            context.area.tag_redraw()

            if self.l_mouse or self.wheel:
                update_circles = True
                event = yield {'RUNNING_MODAL'}

            elif event.type == 'RET':
                if not points:
                    return {'CANCELLED'}

                try:
                    create_blob(list(medial_approx(list(resample_loop(points, context.scene.base_tools.blobsketch_quality)))), context)
                    computed_circles = []
                    points = []
                    return {'FINISHED'}

                except CursorOutOfScreen:
                    self.report({'ERROR_INVALID_CONTEXT'}, message='Cursor must be visible for BlobSketch to work')
                    return {'CANCELLED'}

            elif event.type == 'ESC':
                return {'CANCELLED'}

            else:
                event = yield {'PASS_THROUGH'}


def create_blob(circles, context):
    plane_co, plane_no, size = get_cursor_plane(context)
    cursor_2d_pos = from_3d_to_2d(context.scene.cursor.location, context).to_3d()
    rotation = context.region_data.view_rotation
    bpy.ops.object.metaball_add()
    meta = context.active_object
    meta.rotation_mode = 'QUATERNION'
    meta.rotation_quaternion = rotation
    meta.data.threshold = 0.01
    meta.data.elements.remove(meta.data.elements[0])

    min_bound = Vector((float('inf'),) * 3)
    max_bound = Vector((float('-inf'),) * 3)

    for pt, radius in circles:
        elem = meta.data.elements.new()
        elem.co = (pt - cursor_2d_pos) * size
        min_bound = Vector(map(min, zip(min_bound, elem.co - Vector((size * radius,) * 3))))
        max_bound = Vector(map(max, zip(min_bound, elem.co + Vector((size * radius,) * 3))))
        elem.radius = radius * size

    for obj in context.selected_objects:
        obj.select_set(False)

    meta.select_set(True)
    context.view_layer.objects.active = meta
    meta.data.resolution = min(max_bound.xy - min_bound.xy) / context.scene.base_tools.blobsketch_resoluition
    bpy.ops.object.convert(target='MESH')



def smooth_polyline(points):
    yield points[0]
    for i in range(1, len(points) - 1):
        yield (points[i - 1] + points[i + 1]) / 2
    yield points[-1]


def kd_from_points(points):
    tree = KDTree(len(points))
    for i, p in enumerate(points):
        tree.insert(p, i)
    tree.balance()
    return tree


class CursorOutOfScreen(BaseException):
    pass

def get_cursor_plane(context):
    plane_co = context.scene.cursor.location
    plane_no = context.region_data.view_rotation @ Vector((0, 0, 1))
    cursor_2d_pos = from_3d_to_2d(context.scene.cursor.location, context)
    if cursor_2d_pos is None:
        raise CursorOutOfScreen

    pixel_size = (from_2d_to_3d(cursor_2d_pos + Vector((0, 100)), context, plane_co) - plane_co).length / 100

    return plane_co, plane_no, pixel_size


def resample_loop(points, n):
    segments = []
    lengths = []
    for p1, p2 in loop_segments_iter(points):
        segments.append((p1, p2))
        lengths.append((p1 - p2).length)

    tot_length = sum(lengths)

    step = tot_length / n

    curr_length_down = 0
    curr_length_up = 0
    curr_pos = 0

    while segments:
        segment = segments.pop(-1)
        length = lengths.pop(-1)
        curr_length_up += length
        while curr_pos < curr_length_up:
            t = (curr_pos - curr_length_down) / length
            yield lerp(segment[1], segment[0], t)
            curr_pos += step
        curr_length_down = curr_length_up


def loop_segments_iter(points):
    n = len(points)
    for i in range(n):
        yield points[i], points[(i + 1) % n]


def medial_approx(points_loop, precision=0.001):
    kd = kd_from_points(points_loop)
    bm = bmesh.new()
    verts = [bm.verts.new(v) for v in points_loop]
    face = bm.faces.new(verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    normal = face.normal
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bvh = BVHTree.FromBMesh(bm)

    def radius(pt):
        result, _, _, _ = bvh.ray_cast(pt + normal, -normal)
        if result:
            return kd.find(pt)[2]
        else:
            return 0

    for vert in bm.verts:
        if not vert.is_boundary:
            continue
        mid = vert.co
        evec = Vector()
        for edge in vert.link_edges:
            if edge.is_boundary:
                evec += (edge.verts[0].co - edge.verts[1].co).cross(edge.link_faces[0].normal)

        size = precision
        last_size = size
        incr = 2
        scr = radius(mid + evec * size)

        cap = 1 + precision
        while incr > cap:
            pt = mid + evec * size * incr
            scr1 = radius(pt)
            if scr1 > scr:
                scr = scr1
                last_size = size
                size *= incr
                continue

            else:
                incr = (incr + 1) / 2
                size = last_size
                scr = radius(mid + evec * size)

        yield mid + evec * size, scr


classes = [BlobSketch]
