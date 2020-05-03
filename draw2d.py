import bpy
from mathutils import Vector
import gpu
import bgl
from gpu_extras import batch
from math import cos, sin, pi
import blf

def lerp(a, b, t):
    return (b * t) + (a * (1 - t))


def circle_point(center=(0, 0), radius=1, t=0):
    t = t * 2 * pi
    return Vector((center[0] + sin(t) * radius, center[1] + cos(t) * radius))


class Draw2D:
    def __init__(self):
        self.vertices = []
        self.colors = []
        self.text = []
        self.thickness = 2
        self.font_shadow = (0, 0, 0, 0.5)
        self.shader = gpu.shader.from_builtin("2D_FLAT_COLOR")
        self.batch_redraw = False
        self.batch = None
        self.handler = None

    def __call__(self):
        self.draw()

    def add_text(self, text, location, size, color=(0, 0, 0, 1), dpi=72):
        self.text.append((text, location, size, color, dpi))

    def add_circle(self, center, radius, resolution, color=(1, 0, 0, 1)):
        self.batch_redraw = True
        for i in range(resolution):
            line_point_a = circle_point(center, radius, i / resolution)
            line_point_b = circle_point(center, radius, (i + 1) / resolution)
            self.add_line(line_point_a, line_point_b, color)

    def add_line(self, point_a, point_b, color_a=(1, 0, 0, 1), color_b=None):
        self.batch_redraw = True
        self.vertices.append(point_a)
        self.vertices.append(point_b)
        self.colors.append(color_a)
        self.colors.append(color_b if color_b else color_a)

    def remove_last_line(self):
        self.batch_redraw = True
        self.vertices.pop(-1)
        self.vertices.pop(-1)

    def remove_last_text(self):
        self.batch_redraw = True
        self.text.pop(-1)

    def clear(self):
        self.batch_redraw = True
        self.vertices.clear()
        self.colors.clear()
        self.text.clear()

    def update_batch(self):
        self.batch_redraw = False
        self.batch = batch.batch_for_shader(self.shader, "LINES",
                                            {"pos": self.vertices, "color": self.colors})

    def setup_handler(self):
        self.handler = bpy.types.SpaceView3D.draw_handler_add(self, (), "WINDOW", "POST_PIXEL")

    def remove_handler(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.handler, "WINDOW")

    def draw(self):
        bgl.glEnable(bgl.GL_BLEND)
        if self.batch_redraw or not self.batch:
            self.update_batch()
        bgl.glLineWidth(self.thickness)
        self.shader.bind()
        self.batch.draw(self.shader)
        bgl.glLineWidth(1)

        for text, location, size, color, dpi in self.text:
            blf.position(0, location[0], location[1], 0)
            blf.size(0, size, dpi)
            blf.color(0, *color)
            blf.shadow(0, 3, *self.font_shadow)
            blf.draw(0, text)

        bgl.glDisable(bgl.GL_BLEND)


class VerticalSlider(Draw2D):
    def __init__(self, center=Vector((100, 100))):
        super().__init__()
        self.center = center
        self.eval_co = center

    def eval(self, co, text="Test", color=Vector((1, 0, 0, 0.5)), unit_scale=30, digits=3):
        x = Vector((1, 0))
        self.eval_co = co.copy()
        self.eval_co.x = self.center.x
        self.clear()
        self.add_line(self.center, self.eval_co, color)
        self.add_line(co, self.eval_co, color)
        self.add_line(self.center + x * 10, self.center - x * 10, color)
        val = (self.eval_co.y - self.center.y) / unit_scale
        self.add_text(f"{text:} {round(val, digits)}", self.eval_co + Vector((10, 10)), 20, color)
        return val
