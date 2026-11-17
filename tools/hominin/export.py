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


def fix_quaternion_continuity(path):
    """Make consecutive rotation keys in a .glb take the short way round.

    q and -q are the same rotation, and the exporter may alternate between
    them from one sampled frame to the next.  Viewers that interpolate the
    raw components would then spin the joint through 360 degrees between two
    frames.  This flips signs in place so neighbouring keys always agree.
    """
    import json
    import struct

    import numpy as np
    with open(path, "rb") as f:
        blob = bytearray(f.read())
    jlen = struct.unpack_from("<I", blob, 12)[0]
    doc = json.loads(bytes(blob[20:20 + jlen]))
    base = 20 + jlen + 8
    done, flips = set(), 0
    for a in doc.get("animations", []):
        for ch in a["channels"]:
            if ch["target"]["path"] != "rotation":
                continue
            ai = a["samplers"][ch["sampler"]]["output"]
            if ai in done:
                continue
            done.add(ai)
            acc = doc["accessors"][ai]
            if acc["componentType"] != 5126 or acc["type"] != "VEC4":
                continue
            bv = doc["bufferViews"][acc["bufferView"]]
            off = base + bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
            q = np.frombuffer(bytes(blob[off:off + acc["count"] * 16]), dtype="<f4").reshape(-1, 4).copy()
            for i in range(1, len(q)):
                if float(np.dot(q[i], q[i - 1])) < 0:
                    q[i] = -q[i]
                    flips += 1
            blob[off:off + acc["count"] * 16] = q.astype("<f4").tobytes()
            if "min" in acc:
                acc["min"], acc["max"] = [float(v) for v in q.min(0)], [float(v) for v in q.max(0)]
    new_json = json.dumps(doc, separators=(",", ":")).encode()
    new_json += b" " * ((4 - len(new_json) % 4) % 4)
    out = bytearray(blob[:12])
    out += struct.pack("<I", len(new_json)) + b"JSON" + new_json + bytes(blob[20 + jlen:])
    struct.pack_into("<I", out, 8, len(out))
    with open(path, "wb") as f:
        f.write(out)
    return flips
