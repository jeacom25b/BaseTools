if 'bpy' in locals():
    import importlib
    import sys
    from os import path
    md_name = path.dirname(path.realpath(__file__)).split(path.sep)[-1]
    for module in sys.modules:
        if module.startswith(md_name):
            print(f'Reloading: {sys.modules[module]}')
            importlib.reload(sys.modules[module])


import bpy

bl_info = {
    'name': 'BaseTools',
    'description': 'Sculpting tools to improve workflow',
    'author': 'Jean Da Costa Machado',
    'version': (0, 0, 1),
    'blender': (2, 82, 0),
    'wiki_url': '',
    'category': 'Sculpt',
    'location': ''
}

from . import blobsketch
from . import utils
from . import ui

all_classes = blobsketch.classes + utils.classes + ui.classes

def register():
    for cls in all_classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in all_classes:
        bpy.utils.unregister_class(cls)
