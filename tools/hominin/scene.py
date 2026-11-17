"""Blender-side helpers: scene reset, mesh/armature creation, QA renders."""
import math
import os

import bpy
import numpy as np
from mathutils import Matrix, Vector


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    return scene


def make_mesh(name, V, faces, face_uvs=None, uv=None, smooth=True):
    """Create a mesh object. `faces` index into V; `face_uvs` index into uv."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(p) for p in V], [], [tuple(f) for f in faces])
    mesh.update()
    if face_uvs is not None:
        layer = mesh.uv_layers.new(name="UVMap")
        flat = np.empty(len(mesh.loops) * 2, dtype=np.float32)
        k = 0
        for fu in face_uvs:
            for t in fu:
                flat[k] = uv[t][0]
                flat[k + 1] = uv[t][1]
                k += 2
        layer.data.foreach_set("uv", flat)
    if smooth:
        mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def bone_frame(head, tail, zref):
    """Rest orientation of a bone (columns = local X, Y, Z in world axes).

    Y runs head -> tail; Z is `zref` made perpendicular to Y.  Matches what
    EditBone.align_roll(zref) produces, so numpy and Blender agree.
    """
    y = np.asarray(tail, float) - np.asarray(head, float)
    y /= np.linalg.norm(y)
    z = np.asarray(zref, float) - np.dot(zref, y) * y
    n = np.linalg.norm(z)
    if n < 1e-6:
        alt = np.array([1.0, 0.0, 0.0]) if abs(y[0]) < 0.9 else np.array([0.0, 0.0, 1.0])
        z = alt - np.dot(alt, y) * y
        n = np.linalg.norm(z)
    z /= n
    x = np.cross(y, z)
    return np.stack([x, y, z], axis=1)


def make_armature(name, skel):
    """skel: {bone: dict(head, tail, zref, parent)} in world metres."""
    arm = bpy.data.armatures.new(name)
    obj = bpy.data.objects.new(name, arm)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    ebs = {}
    for b, d in skel.items():
        eb = arm.edit_bones.new(b)
        eb.head = Vector(d["head"])
        eb.tail = Vector(d["tail"])
        eb.align_roll(Vector(d["zref"]))
        ebs[b] = eb
    for b, d in skel.items():
        if d.get("parent"):
            ebs[b].parent = ebs[d["parent"]]
            ebs[b].use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in obj.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return obj


def bind(mesh_obj, arm_obj, W, bones, vert_ids, max_influences=4):
    """Assign vertex groups from dense weights W[vert_ids] and parent to rig."""
    Wl = W[vert_ids].copy()
    if max_influences:
        order = np.argsort(-Wl, axis=1)
        mask = np.zeros_like(Wl, dtype=bool)
        np.put_along_axis(mask, order[:, :max_influences], True, axis=1)
        Wl[~mask] = 0.0
        Wl /= Wl.sum(1, keepdims=True)
    for j, b in enumerate(bones):
        col = Wl[:, j]
        nz = np.nonzero(col > 1e-5)[0]
        if len(nz) == 0:
            continue
        vg = mesh_obj.vertex_groups.new(name=b)
        # group equal weights to cut the number of API calls
        for i in nz:
            vg.add([int(i)], float(col[i]), "REPLACE")
    mod = mesh_obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm_obj
    mesh_obj.parent = arm_obj


# --------------------------------------------------------------------- render
def setup_render(scene, samples=48, res=(640, 800)):
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.055, 0.05, 0.045, 1)
    bg.inputs[1].default_value = 0.6


def add_light(name, kind, loc, energy, size=2.0, color=(1, 1, 1), target=(0, 0, 0)):
    data = bpy.data.lights.new(name, kind)
    data.energy = energy
    data.color = color
    if kind == "AREA":
        data.size = size
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    bpy.context.scene.collection.objects.link(obj)
    d = Vector(target) - Vector(loc)
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return obj


def studio_lights(center, radius):
    c = Vector(center)
    r = radius
    add_light("Key", "AREA", c + Vector((-1.6 * r, -2.2 * r, 1.4 * r)), 70 * r * r, 2.0 * r, (1.0, 0.96, 0.9), c)
    add_light("Fill", "AREA", c + Vector((2.2 * r, -1.4 * r, 0.3 * r)), 14 * r * r, 3.0 * r, (0.85, 0.92, 1.0), c)
    add_light("Rim", "AREA", c + Vector((0.6 * r, 2.4 * r, 1.6 * r)), 45 * r * r, 2.0 * r, (1.0, 0.95, 0.85), c)


def render_view(path, center, extent, azimuth_deg, elevation_deg=0.0, ortho=True, res=None):
    """Render looking at `center`. azimuth 0 = front (camera at -Y), 90 = from +X."""
    scene = bpy.context.scene
    cam = scene.camera
    if cam is None:
        data = bpy.data.cameras.new("Cam")
        cam = bpy.data.objects.new("Cam", data)
        scene.collection.objects.link(cam)
        scene.camera = cam
    az, el = math.radians(azimuth_deg), math.radians(elevation_deg)
    dist = max(extent * 4.0, 2.0)
    off = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * dist
    c = Vector(center)
    cam.location = c + off
    cam.rotation_euler = (-off).to_track_quat("-Z", "Y").to_euler()
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = extent
    else:
        cam.data.type = "PERSP"
        cam.data.lens = 85
    cam.data.clip_start = 0.01
    cam.data.clip_end = 100
    if res:
        scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def clay_material(name="Clay", color=(0.72, 0.68, 0.62)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = 0.65
    return m


def montage(paths, out, cols=None, pad=4, bg=(14, 12, 11)):
    from PIL import Image
    ims = [Image.open(p).convert("RGB") for p in paths]
    cols = cols or len(ims)
    rows = (len(ims) + cols - 1) // cols
    w = max(i.width for i in ims)
    h = max(i.height for i in ims)
    sheet = Image.new("RGB", (cols * w + (cols + 1) * pad, rows * h + (rows + 1) * pad), bg)
    for k, im in enumerate(ims):
        r, c = divmod(k, cols)
        sheet.paste(im, (pad + c * (w + pad), pad + r * (h + pad)))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out)
    return out
