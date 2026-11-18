# 3D model pipeline

The seven figures in `models/` are **generated**, not hand-sculpted and not
scanned. `build_models.py` drives Blender from Python to turn one openly
licensed human body mesh into each stage, using published fossil
measurements, and exports a rigged, animated GLB for the page.

```
tools/
  fetch_assets.py      download the CC0 base data (once)
  build_models.py      build every model, poster and models.json / models.js
  hominin/
    species.py         ANATOMY  - every number that shapes a body, per stage
    looks.py           APPEARANCE - skin, hair, eyes (all inferred), with reasons
    sculpt.py          skull / face reshaping operators (brow ridge, vault, jaw ...)
    build.py           targets -> head sculpt -> limb proportions -> stance
    quadruped.py       four-legged stance and gait for the Miocene apes
    anim.py            walk and idle cycles (two-bone IK, no motion capture)
    skin.py texture.py baked colour / normal / roughness maps
    parts.py           eyeballs, hide wraps
```

## Rebuilding

Tested with Blender 5.3 (as the `bpy` Python module). About one minute per
model on a 4-core CPU; no GPU needed.

```bash
python -m venv .venv && . .venv/bin/activate     # Python 3.13 for bpy 5.3
pip install bpy==5.3.0 numpy pillow scipy
python tools/fetch_assets.py                      # ~50 MB into tools/.cache/
python tools/build_models.py                      # all seven
python tools/build_models.py neander sapiens      # or just some
```

With the Blender application instead of the `bpy` wheel:

```bash
blender --background --python tools/build_models.py -- neander
```

(Blender's bundled Python then needs `pillow` and `scipy` installed.)

### From a live Blender session (for example through Blender MCP)

```python
import sys; sys.path.insert(0, r"/path/to/humanevolution/tools")
import build_models as bm
from hominin.mhdata import MHData
bm.build_one(MHData(bm.DATA), "erectus")   # note: this clears the open scene first
```

The result is an ordinary armature + mesh in the scene, so it can be sculpted,
re-textured or re-posed by hand and exported again. Keep the three animation
names (`Idle`, `Walk`, `Rest`) and the page will pick the file up unchanged.

## What is evidence and what is not

| Fixed by fossils (in `species.py`) | Inferred (in `looks.py`) |
| --- | --- |
| stature, limb-segment ratios, trunk and hip breadth | skin colour |
| head length and breadth, vault height, brow ridge, facial projection, chin | hair colour and cover |
| stance (the apes' trunk angle is solved from their limb lengths) | ears, lips, nose cartilage, eye colour |
| | clothing |

Limb proportions are entered as published indices (humerofemoral, brachial,
crural) and applied as ratios against a modern human, so the model does not
depend on where the rig happens to put its joints.

Where a fossil does not settle something (Sivapithecus limb proportions,
Homo habilis arm-to-leg ratio, dryopithecine feet) the value is an assumption
and the page says so in the "Informed guesswork" panel. The wording shown to
visitors lives in `life.js` (`RECON`).

These are stylised scientific reconstructions. They are not photorealistic
and they are not a substitute for the fossils themselves.

## Swapping in better assets

The page only needs `models/<id>.glb` plus an entry in `models/models.js`
(file, poster, height, hotspot positions). A hand-sculpted model, or a scan of
a real fossil, can replace a generated one by using the same file name.

Scans of the actual fossils would be the strongest addition. Check the terms
before hosting any: the Smithsonian's hominin scans are view-only, and most
other collections (Digital Atlas of Ancient Life, MorphoSource, African
Fossils) are non-commercial, which does not fit this site's CC BY-SA licence.

## Licences

* Base mesh, morph targets, rig and skin weights: MakeHuman / MPFB2, **CC0 1.0**.
  Fetched from the `anny` package on PyPI, which redistributes them unchanged.
* `vendor/model-viewer.min.js`: Google `<model-viewer>`, **Apache-2.0**.
* The generated models and this code are part of the site and share its licence.

# Skull diagrams (specimen record → "Diagram")

The side-view skull diagrams are 2D vector drawings, not renders. Each skull
is a list of landmarks in millimetres in `tools/diagrams/skulls.py`, oriented
the standard craniometric way (origin at the ear opening, Frankfort
horizontal as the baseline). Every skull is drawn at the same scale, so their
sizes compare directly, and each follows a named specimen:

| Stage | Drawn after | Dashed (reconstructed) |
| --- | --- | --- |
| Dryopithecus | Rudapithecus RUD 77 and RUD 200 | back and base of the skull |
| Ramapithecus | Sivapithecus GSP 15000 (face) | the whole braincase |
| Australopithecus | Sts 5 "Mrs Ples" | lower jaw |
| Homo habilis | KNM-ER 1813 | lower jaw |
| Homo erectus | Sangiran 17 | lower jaw |
| Neanderthal | La Chapelle-aux-Saints 1 | none |
| Homo sapiens | Cro-Magnon 1 | none |

```bash
pip install numpy shapely
python tools/build_diagrams.py                 # -> diagrams/skulls.js
python tools/build_diagrams.py --preview DIR   # also writes DIR/<id>.svg to look at
```

The build prints each skull's brain-space area divided by the specimen's
cranial capacity to the power 2/3. Those numbers should stay close to one
another; an outlier means that skull's vault is drawn too big or too small.

To change a drawing, move its landmarks in `skulls.py` and rebuild. Labels
(`labels=`) name the features that matter for that stage; keep each line to
about 12 characters so the diagrams stay large.
