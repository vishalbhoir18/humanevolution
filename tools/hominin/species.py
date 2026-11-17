"""Anatomical specifications for the seven stages.

Every number that shapes a model lives here, next to the fossil it comes from.
`head` parameters are documented in sculpt.HeadField; `limbs` are published
limb indices (the builder converts them to bone scales relative to a modern
human); `scales` are (lateral, length, fore-aft) factors in each bone's frame.

Soft tissue (skin colour, hair cover, ears, lips, nose cartilage, eye colour)
does not fossilise.  Those choices are flagged `inferred` in `evidence`.
"""

APE_LIPS = {
    "mouth/mouth-upperlip-volume-decr": 1.0,
    "mouth/mouth-lowerlip-volume-decr": 0.95,
    "mouth/mouth-cupidsbow-decr": 1.0,
    "mouth/mouth-philtrum-volume-decr": 0.8,
    "mouth/mouth-scale-horiz-incr": 1.0,
}

THIN_LIPS = {
    "mouth/mouth-upperlip-volume-decr": 0.8,
    "mouth/mouth-lowerlip-volume-decr": 0.6,
    "mouth/mouth-cupidsbow-decr": 0.7,
    "mouth/mouth-scale-horiz-incr": 0.7,
}

SPECIES = {}

# --------------------------------------------------------------- Homo sapiens
SPECIES["sapiens"] = dict(
    id="sapiens",
    macro=dict(gender=1.0, age=0.5, muscle=0.68, weight=0.45, african=0.6, asian=0.2, caucasian=0.2),
    targets={},
    head=dict(brow=0.12),
    head_length=0.202,
    limbs=dict(humerofemoral=71.5, brachial=78.0, crural=85.0),
    scales={},
    stature=1.72,
    hair_volume=dict(scalp=1.3, beard=0.5),
    wrap=dict(top=-66.0, bottom=-101.0, color=((96, 70, 48), (150, 116, 84))),
    stance=dict(kind="biped"),
)

# ------------------------------------------------------ Homo neanderthalensis
SPECIES["neander"] = dict(
    id="neander",
    macro=dict(gender=1.0, age=0.56, muscle=0.95, weight=0.68, african=0.15, asian=0.25, caucasian=0.6),
    targets={
        "mouth/mouth-scale-horiz-incr": 0.4,
        "mouth/mouth-upperlip-volume-decr": 0.3,
        "torso/torso-scale-depth-incr": 0.6,
    },
    head=dict(vault_h=0.84, vault_w=1.05, occiput=0.5, bun=1.1, forehead=1.9,
              brow=1.15, brow_arch=1.0, brow_sulcus=0.2, midface=1.3, muzzle=0.8,
              chin=1.4, nose_flat=-0.15, nose_w=0.8, upper_face=0.7, jaw_drop=0.35,
              gonial=0.25),
    head_length=0.218,
    limbs=dict(humerofemoral=72.0, brachial=73.0, crural=78.5),
    scales={
        "spine_03": (1.10, 1.0, 1.14), "spine_02": (1.13, 1.0, 1.16), "spine_01": (1.08, 1.0, 1.08),
        "pelvis": (1.07, 1.0, 1.04), "clavicle": (1.0, 1.07, 1.0),
        "upperarm": (1.10, 1.0, 1.10), "lowerarm": (1.10, 1.0, 1.10),
        "thigh": (1.08, 1.0, 1.08), "calf": (1.10, 1.0, 1.10),
        "neck_01": (1.14, 0.94, 1.14),
    },
    stature=1.66,
    hair_volume=dict(scalp=1.4, beard=0.9, hairline=dict(front=(0.6, 7.0))),
    wrap=dict(top=-64.0, bottom=-104.0, color=((70, 52, 38), (128, 100, 74))),
    stance=dict(kind="biped"),
)

# --------------------------------------------------------------- Homo erectus
SPECIES["erectus"] = dict(
    id="erectus",
    macro=dict(gender=1.0, age=0.5, muscle=0.78, weight=0.4, african=0.5, asian=0.4, caucasian=0.1),
    targets={**THIN_LIPS, "mouth/mouth-scale-horiz-incr": 0.5},
    head=dict(vault_h=0.74, vault_w=1.0, vault_w_top=0.84, occiput=0.3, bun=0.9, forehead=2.6,
              brow=1.3, brow_arch=0.2, brow_sulcus=0.45, midface=0.25, muzzle=1.6,
              chin=1.6, nose_flat=0.35, nose_w=0.65, jaw_drop=0.25, zygo=0.35, gonial=0.35,
              crest=0.25, nuchal=0.5),
    head_length=0.206,
    limbs=dict(humerofemoral=73.0, brachial=79.0, crural=86.0),
    scales={"neck_01": (1.08, 1.0, 1.08)},
    stature=1.63,
    hair_volume=dict(scalp=1.0, beard=0.4, hairline=dict(front=(-0.6, 6.9))),
    stance=dict(kind="biped"),
)

# --------------------------------------------------------------- Homo habilis
SPECIES["habilis"] = dict(
    id="habilis",
    macro=dict(gender=0.8, age=0.5, muscle=0.72, weight=0.42, african=1.0, asian=0.0, caucasian=0.0),
    targets={**THIN_LIPS},
    head=dict(vault_h=0.72, vault_w=0.88, vault_w_top=0.80, forehead=2.0, brow=0.8, brow_arch=0.5,
              brow_sulcus=0.25, muzzle=2.3, muzzle_w=4.4, chin=1.7, nose_flat=1.0, nose_bridge=0.5,
              nose_w=0.75, upper_face=0.5, jaw_drop=0.6, zygo=0.45, gonial=0.3, nuchal=0.4),
    head_length=0.165,
    limbs=dict(humerofemoral=85.0, brachial=82.0, crural=83.5),
    scales={"neck_01": (1.08, 0.92, 1.1), "pelvis": (1.06, 1.0, 1.0)},
    finger_scale=1.05,
    stature=1.30,
    hair_volume=dict(scalp=0.8, beard=0.3, hairline=dict(front=(0.9, 5.6), temple=0.8)),
    stance=dict(kind="biped", pitch={"neck_01": 5.0, "head": -3.0}),
)

# ----------------------------------------------------------- Australopithecus
SPECIES["austra"] = dict(
    id="austra",
    macro=dict(gender=0.5, age=0.46, muscle=0.72, weight=0.46, african=1.0, asian=0.0, caucasian=0.0),
    targets={**APE_LIPS, "mouth/mouth-scale-horiz-incr": 0.9},
    head=dict(vault_h=0.62, vault_w=0.78, vault_w_top=0.72, occiput=-1.5, forehead=2.4,
              brow=0.75, brow_arch=0.3, brow_sulcus=0.2, muzzle=3.6, muzzle_w=4.6, chin=2.2,
              nose_flat=1.5, nose_bridge=0.9, nose_w=0.9, upper_face=0.4, jaw_drop=0.8,
              zygo=0.9, gonial=0.6, nuchal=1.0),
    head_length=0.162,
    limbs=dict(humerofemoral=85.1, brachial=87.0, crural=84.0),
    scales={
        "pelvis": (1.15, 1.0, 1.0), "spine_02": (1.06, 1.0, 1.08), "spine_03": (0.95, 1.0, 1.0),
        "clavicle": (1.0, 0.95, 1.0), "neck_01": (1.1, 0.8, 1.15), "foot": (1.05, 1.08, 1.0),
    },
    finger_scale=1.08,
    stature=1.07,
    hair_volume=dict(scalp=0.7, beard=0.3, hairline=dict(front=(1.4, 4.4), temple=0.4)),
    stance=dict(kind="biped", pitch={"neck_01": 8.0, "head": -4.0}),
)

# -------------------------------------------------- Dryopithecus (dryopithecine)
# Body: Hispanopithecus (= Dryopithecus) laietanus partial skeleton IPS 18800,
# Can Llobateres, ~9.6 Ma.  Cranium: Rudapithecus RUD 77 / RUD 200 (~305-330 cc).
SPECIES["dryo"] = dict(
    id="dryo",
    macro=dict(gender=0.9, age=0.5, muscle=0.9, weight=0.62, african=1.0, asian=0.0, caucasian=0.0),
    targets={**APE_LIPS},
    head=dict(vault_h=0.52, vault_w=0.70, vault_w_top=0.62, occiput=-2.2, forehead=2.6,
              brow=0.9, brow_arch=0.5, brow_sulcus=0.3, muzzle=5.2, muzzle_w=4.9, chin=3.0,
              nose_flat=1.9, nose_bridge=1.3, nose_w=1.1, upper_face=0.6, jaw_drop=1.2,
              zygo=1.0, gonial=0.8, nuchal=1.6),
    head_length=0.128,
    limbs=dict(humerus=1.12, humerofemoral=100.0, brachial=94.0, crural=84.0),
    scales={
        "spine_03": (1.12, 0.98, 0.95), "spine_02": (1.12, 0.98, 0.97), "spine_01": (1.06, 0.92, 1.0),
        "pelvis": (1.05, 1.0, 1.0), "clavicle": (1.0, 1.05, 1.0), "neck_01": (1.2, 0.7, 1.25),
        "hand": (1.1, 1.15, 1.1), "foot": (1.1, 1.1, 1.0),
        "thigh": (0.95, 1.0, 0.95), "calf": (0.92, 1.0, 0.92),
    },
    finger_scale=1.25, thumb_scale=0.8, hallux_abduct=32.0,
    stature=1.10,
    hair_volume=dict(scalp=0.6, beard=0.0, hairline=dict(front=(1.6, 3.9), temple=0.3)),
    stance=dict(kind="quadruped", hip_height=0.70),
)

# ------------------------------------------- Ramapithecus (= Sivapithecus)
# Face: GSP 15000 (Sivapithecus indicus, Potwar Plateau, ~8.5 Ma): narrow
# interorbital, tall orbits, dished mid-face, flaring cheek bones.
# Limb proportions are not known from an associated skeleton (assumed).
SPECIES["rama"] = dict(
    id="rama",
    macro=dict(gender=0.85, age=0.5, muscle=0.85, weight=0.64, african=1.0, asian=0.0, caucasian=0.0),
    targets={**APE_LIPS},
    head=dict(vault_h=0.56, vault_w=0.72, vault_w_top=0.64, occiput=-2.0, forehead=2.2,
              brow=0.35, brow_arch=1.0, muzzle=4.6, muzzle_w=4.6, chin=2.8,
              nose_flat=1.9, nose_bridge=1.7, nose_w=0.9, upper_face=0.9, jaw_drop=1.3,
              zygo=1.5, gonial=0.9, interorb=0.6, orbit_h=0.35, nuchal=1.4),
    head_length=0.138,
    limbs=dict(humerus=1.06, humerofemoral=95.0, brachial=92.0, crural=84.0),
    scales={
        "spine_03": (1.0, 1.0, 1.08), "spine_02": (1.02, 1.0, 1.10), "pelvis": (1.02, 1.0, 1.0),
        "neck_01": (1.2, 0.72, 1.25), "hand": (1.08, 1.1, 1.08), "foot": (1.1, 1.1, 1.0),
        "thigh": (0.97, 1.0, 0.97), "calf": (0.94, 1.0, 0.94),
    },
    finger_scale=1.25, thumb_scale=0.85, hallux_abduct=30.0,
    stature=1.15,
    hair_volume=dict(scalp=0.6, beard=0.0, hairline=dict(front=(1.6, 3.9), temple=0.3)),
    stance=dict(kind="quadruped", hip_height=0.76),
)

ORDER = ("dryo", "rama", "austra", "habilis", "erectus", "neander", "sapiens")

BIPEDS = ("austra", "habilis", "erectus", "neander", "sapiens")
