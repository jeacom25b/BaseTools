import bpy
import importlib


class RegisterStuff:
    all_classes = []
    register_fncs = []
    unregister_fncs = []
    imported_modules = []
    registered_classes = []
    module_names = []

    def __init__(self):
        raise RuntimeError("cant instantiate")

    def clear_classes():
        RegisterStuff.all_classes.clear()
        RegisterStuff.register_fncs.clear()
        RegisterStuff.unregister_fncs.clear()


def register_class(cls):
    RegisterStuff.all_classes.append(cls)
    return cls


def register_func(func):
    RegisterStuff.register_fncs.append(func)
    return func


def unregister_func(func):
    RegisterStuff.unregister_fncs.append(func)
    return func


def register():
    print('register')
    for cls in RegisterStuff.all_classes:
        bpy.utils.register_class(cls)
        print('register', cls)
        RegisterStuff.registered_classes.append(cls)

    for func in RegisterStuff.register_fncs:
        func()


def unregister():
    print('unregister')
    for cls in RegisterStuff.registered_classes:
        print('unregister', cls)
        bpy.utils.unregister_class(cls)

    RegisterStuff.registered_classes.clear()

    for func in RegisterStuff.unregister_fncs:
        func()


def import_modules():
    RegisterStuff.clear_classes()

    if RegisterStuff.imported_modules:
        print('reload')
        unregister()
        for module in RegisterStuff.imported_modules:
            importlib.reload(module)
        RegisterStuff.imported_modules.clear()

    for mdname in RegisterStuff.module_names:
        exec(f'from . import {mdname}')
        RegisterStuff.imported_modules.append(locals()[mdname])
        print('importing', locals()[mdname])


def add_modules(modules):
    for modname in modules:
        if modname not in RegisterStuff.module_names:
            RegisterStuff.module_names.append(modname)

    import_modules()


__all__ = [
    'register_class',
    'register_func',
    'unregister_func',
    'register',
    'unregister',
    'maybe_reload',
]
