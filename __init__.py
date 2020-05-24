from .register import register, unregister, add_modules
import bpy

bl_info = {
    'name': 'base_tools',
    'description': 'Sculpting tools to improve workflow',
    'author': 'Jean Da Costa Machado',
    'version': (0, 0, 1),
    'blender': (2, 82, 0),
    'wiki_url': '',
    'category': 'Sculpt',
    'location': ''
}


add_modules(
    [
        'blobsketch',
        'boolean',
        'draw2d',
        'interact',
        'ui',
        'settings'
    ]
)
