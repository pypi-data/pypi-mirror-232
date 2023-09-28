import bpy
import os

from cioblender import util
from ciopath.gpath_list import PathList, GLOBBABLE_REGEX
from ciopath.gpath import Path

def resolve_payload(**kwargs):
    """
    Resolve the upload_paths field for the payload.

    """
    path_list = PathList()

    path_list.add(*auxiliary_paths(**kwargs))
    path_list.add(*extra_paths())
    # Todo: enable and test scan_assets
    # path_list.add(*scan_assets())

    return {"upload_paths": [p.fslash() for p in path_list]}

def auxiliary_paths(**kwargs):
    """ Get auxiliary paths"""
    path_list = PathList()
    blender_filepath = kwargs.get("blender_filepath")
    blender_filepath = blender_filepath.replace("\\", "/")

    path_list.add(blender_filepath)
    return path_list

def extra_paths():
    """Add extra assets"""
    scene = bpy.context.scene
    extra_assets_list = scene.extra_assets_list
    path_list = PathList()
    for asset in extra_assets_list:
        path_list.add(asset)

    return path_list

def scan_assets():

    # Create a set to store unique file paths

    path_list = PathList()

    try:
        # Iterate through all materials in the scene
        for material in bpy.data.materials:
            if material.node_tree:
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        path_list.add(node.image.filepath)

        # Iterate through all objects in the scene
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material and slot.material.use_nodes:
                        for node in slot.material.node_tree.nodes:
                            if node.type == 'TEX_IMAGE' and node.image:
                                path_list.add(node.image.filepath)

        # Iterate through all linked libraries
        """
        for library in bpy.data.libraries:
            if library.is_library:
                for block in library.blocks:
                    if block.library:
                        path_list.add(block.library.filepath)
        """
    except Exception as e:
        print("Unable to scan assets: {}".format(e))
        pass



    return path_list
