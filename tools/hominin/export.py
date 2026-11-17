"""glTF export and animation preview helpers."""
import bpy


def preview(arm, name):
    """Make the named action the active one (for renders)."""
    ad = arm.animation_data
    for tr in ad.nla_tracks:
        tr.mute = True
    act = bpy.data.actions.get(name)
    ad.action = act
    if act is not None:
        try:
            ad.action_slot = act.slots[0]
        except Exception:
            pass


def end_preview(arm):
    ad = arm.animation_data
    ad.action = None
    for tr in ad.nla_tracks:
        tr.mute = False
    for pb in arm.pose.bones:
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)


def export_glb(path, objects, jpeg_quality=88):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True,
        export_apply=False, export_yup=True,
        export_texcoords=True, export_normals=True, export_tangents=False,
        export_materials="EXPORT", export_image_format="AUTO", export_jpeg_quality=jpeg_quality,
        export_skins=True, export_influence_nb=4, export_def_bones=False,
        export_rest_position_armature=True,
        export_animations=True, export_animation_mode="NLA_TRACKS",
        export_force_sampling=True, export_optimize_animation_size=True,
        export_morph=False, export_cameras=False, export_lights=False, export_extras=False,
    )
    return path
