"""Texture baking.

Blender bakes a few auxiliary maps into UV space (canonical coordinates,
stance coordinates, procedural noise, ambient occlusion); the final PBR maps
are then composed in numpy, where every region mask is an explicit function
of canonical body coordinates.
"""
import os

import bpy
import numpy as np


def _new_image(name, size, is_float=True):
    img = bpy.data.images.new(name, size, size, alpha=False, float_buffer=is_float)
    img.colorspace_settings.name = "Non-Color"
    return img


def _pixels(img):
    n = img.size[0]
    a = np.empty(n * n * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(n, n, 4)[:, :, :3].copy()


def set_point_attr(obj, name, values):
    """Store an (n, 3) array as a per-vertex float colour attribute."""
    me = obj.data
    if name in me.color_attributes:
        me.color_attributes.remove(me.color_attributes[name])
    attr = me.color_attributes.new(name, "FLOAT_COLOR", "POINT")
    rgba = np.ones((len(me.vertices), 4), dtype=np.float32)
    rgba[:, :3] = values
    attr.data.foreach_set("color", rgba.reshape(-1))


class Baker:
    def __init__(self, obj, size=2048, margin=12):
        self.obj, self.size, self.margin = obj, size, margin
        scene = bpy.context.scene
        scene.render.engine = "CYCLES"
        scene.cycles.device = "CPU"
        self.mat = bpy.data.materials.new("bake")
        self.mat.use_nodes = True
        nt = self.mat.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        self.out = nt.nodes.new("ShaderNodeOutputMaterial")
        self.emit = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(self.emit.outputs[0], self.out.inputs[0])
        self.target = nt.nodes.new("ShaderNodeTexImage")
        obj.data.materials.clear()
        obj.data.materials.append(self.mat)
        self.nt = nt

    def _bake(self, name, bake_type, samples):
        scene = bpy.context.scene
        img = _new_image(name, self.size)
        self.target.image = img
        self.nt.nodes.active = self.target
        self.target.select = True
        bpy.ops.object.select_all(action="DESELECT")
        self.obj.select_set(True)
        bpy.context.view_layer.objects.active = self.obj
        scene.cycles.samples = samples
        scene.cycles.use_denoising = False
        scene.render.bake.margin = self.margin
        scene.render.bake.use_clear = True
        bpy.ops.object.bake(type=bake_type)
        px = _pixels(img)
        bpy.data.images.remove(img)
        return px

    def clear_links(self):
        for l in list(self.emit.inputs[0].links):
            self.nt.links.remove(l)

    def attribute(self, name):
        """Bake a per-vertex colour attribute (interpolated across faces)."""
        self.clear_links()
        n = self.nt.nodes.new("ShaderNodeAttribute")
        n.attribute_name = name
        self.nt.links.new(n.outputs["Color"], self.emit.inputs[0])
        px = self._bake("attr_" + name, "EMIT", 1)
        self.nt.nodes.remove(n)
        return px

    def noise(self, coord_attr, layers):
        """Bake up to three noise layers into R, G, B.

        layers: list of dict(scale=(sx, sy, sz), detail=, rough=, kind='noise'|'voronoi')
        evaluated on the coordinates stored in `coord_attr` (metres).
        """
        self.clear_links()
        nt = self.nt
        made = []
        attr = nt.nodes.new("ShaderNodeAttribute")
        attr.attribute_name = coord_attr
        made.append(attr)
        comb = nt.nodes.new("ShaderNodeCombineColor")
        made.append(comb)
        for k, lay in enumerate(layers[:3]):
            mp = nt.nodes.new("ShaderNodeMapping")
            mp.vector_type = "POINT"
            mp.inputs["Scale"].default_value = lay["scale"]
            mp.inputs["Location"].default_value = (17.3 * (k + 1), 3.1 * (k + 2), 7.7 * (k + 3))
            nt.links.new(attr.outputs["Color"], mp.inputs["Vector"])
            made.append(mp)
            if lay.get("kind", "noise") == "voronoi":
                tx = nt.nodes.new("ShaderNodeTexVoronoi")
                tx.feature = lay.get("feature", "F1")
                tx.inputs["Scale"].default_value = 1.0
                out = tx.outputs["Distance"]
            else:
                tx = nt.nodes.new("ShaderNodeTexNoise")
                tx.inputs["Scale"].default_value = 1.0
                tx.inputs["Detail"].default_value = lay.get("detail", 4.0)
                tx.inputs["Roughness"].default_value = lay.get("rough", 0.55)
                out = tx.outputs["Fac"] if "Fac" in tx.outputs else tx.outputs[0]
            nt.links.new(mp.outputs["Vector"], tx.inputs["Vector"])
            made.append(tx)
            nt.links.new(out, comb.inputs[k])
        nt.links.new(comb.outputs[0], self.emit.inputs[0])
        px = self._bake("noise", "EMIT", 1)
        for n in made:
            nt.nodes.remove(n)
        return px

    def ao(self, samples=24):
        return self._bake("ao", "AO", samples)[:, :, 0]


def blur(a, k):
    """Cheap separable box blur (k = radius in texels), applied twice."""
    from scipy.ndimage import uniform_filter
    return uniform_filter(uniform_filter(a, size=2 * k + 1, mode="nearest"), size=2 * k + 1, mode="nearest")


def height_to_normal(h, strength):
    """Tangent-space normal map (OpenGL / glTF convention) from a height map.
    Arrays are in Blender image layout: row 0 = v 0."""
    du = np.gradient(h, axis=1)
    dv = np.gradient(h, axis=0)
    n = np.stack([-du * strength, -dv * strength, np.ones_like(h)], axis=2)
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n * 0.5 + 0.5


def to_image(name, arr, srgb):
    """Float array (h, w, 3) in [0, 1] -> packed Blender image."""
    h, w = arr.shape[:2]
    img = bpy.data.images.new(name, w, h, alpha=False, float_buffer=False)
    img.colorspace_settings.name = "sRGB" if srgb else "Non-Color"
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :3] = np.clip(arr, 0, 1)
    img.pixels.foreach_set(rgba.reshape(-1))
    img.update()
    return img


def save_image(img, path, fmt="JPEG", quality=90):
    scene = bpy.context.scene
    s = scene.render.image_settings
    prev = (s.file_format, s.quality, s.color_mode)
    s.file_format, s.quality, s.color_mode = fmt, quality, "RGB"
    img.save_render(path, scene=scene)
    s.file_format, s.quality, s.color_mode = prev
    img.source = "FILE"
    img.filepath = path
    img.reload()
    return img


def srgb_to_linear(c):
    c = np.asarray(c, dtype=np.float32)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def load_mask(data_root, name, size):
    """MPFB UV-space region mask (white = region), resampled, Blender row order."""
    from PIL import Image
    p = os.path.join(data_root, "textures", f"mpfb_{name}.jpg")
    im = Image.open(p).convert("L").resize((size, size), Image.BILINEAR)
    return np.asarray(im, dtype=np.float32)[::-1] / 255.0


def pbr_material(name, color_img, normal_img=None, orm_img=None, roughness=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexImage")
    tc.image = color_img
    nt.links.new(tc.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = 0.0
    if normal_img is not None:
        tn = nt.nodes.new("ShaderNodeTexImage")
        tn.image = normal_img
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    if orm_img is not None:
        to = nt.nodes.new("ShaderNodeTexImage")
        to.image = orm_img
        sep = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(to.outputs["Color"], sep.inputs["Color"])
        nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    return m
