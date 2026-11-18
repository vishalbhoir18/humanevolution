"""Landmark specifications for the seven lateral skull diagrams.

Units: millimetres.  Origin: porion (top of the ear opening).  x forward,
y up; the Frankfort horizontal (porion to the lowest point of the orbit
rim) is y = 0.  A point written (x, y, "c") or "NAME!" is a sharp corner.

Each skull follows a named specimen.  Its overall size comes from published
measurements of that specimen (cranial length glabella-opisthocranion, vault
height, facial height); the outline between landmarks is drawn freehand in
the spirit of a textbook figure.  Parts the specimen does not preserve are
listed in `reconstructed` and drawn dashed.

Lists that make up the outline, in order, starting from nasion N:
  front_up  N -> glabella G           (face group)
  vault     -> lambda L               (vault group)
  occiput   -> inion I                (occiput group)
  base      -> front of the mastoid   (base group)
  under     -> maxillary tuberosity   (face group: below the cheek arch)
  alveolar  -> prosthion pr           (face group: upper tooth row)
  face_up   -> back toward N          (face group: nose and mid-face)
"""

SKULLS = {}

# --------------------------------------------------------------- Homo sapiens
# Cro-Magnon 1 (Abri de Cro-Magnon, France, ~28 ka): cranial length ~202 mm,
# high rounded vault, vertical forehead, small brows, projecting chin.
SKULLS["sapiens"] = dict(
    specimen="after Cro-Magnon 1",
    reconstructed=(),
    pt=dict(N=(95, 24), G=(99, 35), B=(24, 126), V=(0, 129), L=(-72, 102), OP=(-102, 52), I=(-90, 14),
            MT=(-9, -34), pr=(103, -43), ans=(111, -21), rh=(109, 3), tub=(55, -45),
            cd=(9, -5), go=(16, -67), me=(91, -94), gn=(99, -91), pog=(104, -83), id=(100, -57), cor=(41, -15)),
    front_up=[(97, 29), "G"],
    vault=[(100, 47), (98, 64), (92, 82), (81, 99), (64, 113), (44, 122), "B", "V", (-26, 126), (-50, 117), "L"],
    occiput=[(-88, 86), (-99, 68), "OP", (-99, 33), "I"],
    base=[(-84, 0), (-72, -12), (-56, -20), (-38, -24), (-22, -27), "MT!", (-3, -21), (-1, -12)],
    under=[(7, -10), (15, -13), (22, -12), (36, -11), (52, -11), (64, -15), (70, -20), (66, -31), (60, -40), "tub!"],
    alveolar=[(80, -44.5), "pr!"],
    face_up=[(106, -33), (108, -26), "ans!", (103, -19), (100.5, -12), (102.5, -4), "rh!", (101, 15)],
    nasal=["ans", (103, -19), (100.5, -12), (102.5, -4), "rh"],
    orbit=[(93.5, 31), (89, 34), (85.5, 31), (84, 21), (84.5, 9), (87, 2), (92, 0.5), (96.5, 3.5), (97.5, 11), (95, 20), (93, 27)],
    eam=(0, -4, 3.6, 4.6),
    mf=(82, -72),
    zyg_upper=[(4, 3), (20, 3.5), (40, 3), (56, 5), (66, 11), (73, 22), (78, 32), (83, 38)],
    zyg_lower=[(64, -15), (70, -10), (76, -8), (84, -6)],
    temporal=[(86, 41), (80, 62), (64, 84), (38, 99), (6, 106), (-26, 102), (-52, 88), (-66, 66), (-68, 42), (-58, 22), (-40, 10), (-20, 6), (-2, 6)],
    coronal=["B", (32, 104), (42, 82), (49, 58), (55, 37)],
    squamosal=[(55, 37), (44, 46), (24, 52), (2, 52), (-18, 45), (-30, 32), (-36, 18)],
    lambdoid=["L", (-79, 82), (-77, 58), (-71, 36), (-60, 16)],
    pmastoid=[(-60, 16), (-48, 17), (-36, 18)],
    zygtemp=[(46, -11), (49, -3), (51, 4)],
    faint=[[(55, 37), (66, 35), (76, 29)], [(87, 1), (82, -6), (74, -14)]],
    mand=["cd", (3, -9), (5, -20), (8, -36), (12, -54), "go", (26, -74), (40, -78), (60, -84), (80, -91), "me", "gn",
          "pog", (102, -73), (98, -66), (99, -61), "id!", (80, -58.5), (56, -58), (50, -57, "c"),
          (46, -46), (43, -31), "cor!", (34, -21), (26, -24), (19, -19), (15, -13), (13, -6)],
    teeth=dict(
        upper=dict(x0=103, y_alv=-44.5, y_occ=-51.5, widths=[3.5, 3.5, 6, 6.5, 6.5, 9.5, 9, 8],
                   kinds="iicppmmm", canine_extra=0.6, tilt=8),
        lower=dict(x0=100, y_alv=-57.5, y_occ=-51.5, widths=[3.5, 3.5, 6, 6.5, 6.5, 10, 9.5, 9],
                   kinds="iicppmmm", canine_extra=0.4, tilt=4)),
    floor=[(-84, 10), (-74, -6), (-58, -15), (-40, -18), (-22, -14), (-8, -4), (6, 2), (20, 0), (34, 1),
           (46, 9), (54, 19), (66, 24), (80, 28), (91, 38)],
    vault_thickness=6,
    labels=[
        dict(text="Tall, round\nvault", at=(-24, 126), to=(-56, 138)),
        dict(text="Vertical\nforehead", at=(96, 74), to=(114, 84)),
        dict(text="Small brow", at=(98, 34), to=(114, 42)),
        dict(text="Bony chin", at="pog", to=(114, -84)),
    ],
)

# ------------------------------------------------------ Homo neanderthalensis
# La Chapelle-aux-Saints 1 (France, ~50 ka): cranial length ~208 mm, long low
# vault, occipital bun, double-arched brow, mid-face pulled forward, large
# nose, no chin, gap behind the last molar.
SKULLS["neander"] = dict(
    specimen="after La Chapelle-aux-Saints 1",
    reconstructed=(),
    pt=dict(N=(107, 28), G=(114, 40), B=(30, 114), V=(2, 116), L=(-74, 92), OP=(-98, 46), I=(-86, 16),
            MT=(-7, -28), pr=(120, -55), ans=(125, -30), rh=(123, 6), tub=(62, -55),
            cd=(12, -5), go=(18, -74), me=(105, -102), gn=(112, -97), pog=(116, -89), id=(117, -71), cor=(44, -15)),
    front_up=[(111, 33), "G", (111, 47)],
    vault=[(104, 50), (100, 62), (92, 79), (78, 95), (60, 106), "B", "V", (-28, 113), (-52, 105), "L"],
    occiput=[(-86, 80), (-96, 64), "OP", (-95, 30), "I"],
    base=[(-80, 2), (-68, -10), (-52, -18), (-36, -22), (-20, -24), "MT!", (-2, -19), (0, -12)],
    under=[(6, -10), (14, -13), (22, -12), (38, -11), (56, -12), (70, -17), (76, -24), (72, -38), (67, -48), "tub!"],
    alveolar=[(90, -55.5), "pr!"],
    face_up=[(121, -46), (123, -38), "ans!", (116, -27), (113, -17), (115, -5), "rh!", (115, 18)],
    nasal=["ans", (116, -27), (113, -17), (115, -5), "rh"],
    orbit=[(105, 37), (100, 40), (95, 38), (92, 28), (91.5, 14), (93, 4), (98, 0.5), (104, 3), (107, 12), (106.5, 22), (106, 30)],
    eam=(0, -4, 3.8, 4.8),
    mf=(80, -83),
    zyg_upper=[(4, 3), (22, 3), (42, 3), (60, 5), (72, 12), (80, 24), (86, 34), (91, 41)],
    zyg_lower=[(70, -17), (78, -12), (86, -8), (94, -6)],
    temporal=[(94, 44), (88, 62), (72, 80), (46, 94), (14, 99), (-18, 96), (-46, 86), (-62, 66), (-66, 44), (-58, 24), (-40, 10), (-20, 6), (-2, 6)],
    coronal=["B", (38, 94), (47, 72), (54, 52), (60, 36)],
    squamosal=[(60, 36), (48, 44), (28, 49), (6, 49), (-14, 43), (-28, 30), (-34, 16)],
    lambdoid=["L", (-82, 74), (-82, 52), (-74, 32), (-62, 14)],
    pmastoid=[(-62, 14), (-48, 15), (-34, 16)],
    zygtemp=[(48, -11), (51, -3), (53, 4)],
    faint=[[(60, 36), (72, 35), (84, 30)], [(98, 1), (90, -8), (80, -16)], [(-80, 60), (-94, 48)]],
    mand=["cd", (6, -10), (8, -24), (11, -42), (14, -60), "go", (30, -84), (55, -90), (80, -96), (100, -100), "me", "gn",
          "pog", (118, -79), "id!", (96, -71.5), (70, -70), (52, -69, "c"),
          (48, -56), (45, -40), "cor!", (35, -22), (27, -26), (19, -20), (15, -12), (14, -6)],
    teeth=dict(
        upper=dict(x0=120, y_alv=-56.5, y_occ=-63.5, widths=[4, 4, 6.5, 7, 6.5, 10.5, 9.5, 8.5],
                   kinds="iicppmmm", canine_extra=0.6, tilt=10),
        lower=dict(x0=117, y_alv=-70.5, y_occ=-63.5, widths=[4, 4, 6.5, 7, 7, 11, 10, 9],
                   kinds="iicppmmm", canine_extra=0.4, tilt=6)),
    floor=[(-80, 12), (-72, -4), (-56, -14), (-38, -18), (-20, -14), (-6, -4), (8, 2), (22, 0), (36, 1),
           (50, 9), (60, 20), (74, 26), (90, 31), (103, 43)],
    vault_thickness=7,
    labels=[
        dict(text="Long, low\nvault", at=(-26, 113), to=(-56, 128)),
        dict(text="Double\narched brow", at=(113, 40), to=(130, 54)),
        dict(text="Mid-face\npulled\nforward", at=(122, -12), to=(132, -6)),
        dict(text="Occipital\nbun", at=(-97, 56), to=(-106, 36)),
        dict(text="No chin", at="pog", to=(130, -92)),
    ],
)

# --------------------------------------------------------------- Homo erectus
# Sangiran 17 (Java, ~1.3-1.0 Ma): cranial length ~207 mm, very low vault,
# thick straight brow bar, sharply angled occiput, large projecting face.
# No mandible was found with it: the jaw is reconstructed.
SKULLS["erectus"] = dict(
    specimen="after Sangiran 17 · Java",
    reconstructed=("mandible",),
    pt=dict(N=(104, 26), G=(114, 38), B=(26, 98), V=(0, 100), L=(-70, 82), OP=(-96, 38), I=(-93, 29),
            MT=(-10, -28), pr=(126, -54), ans=(121, -28), rh=(116, 6), tub=(66, -54),
            cd=(12, -5), go=(20, -76), me=(114, -100), gn=(119, -95), pog=(120, -86), id=(123, -69), cor=(45, -16)),
    front_up=[(110, 30), "G", (110, 45)],
    vault=[(100, 47), (95, 57), (86, 70), (70, 84), (50, 93), "B", "V", (-26, 98), (-50, 92), "L"],
    occiput=[(-84, 70), (-93, 52), "OP!", "I"],
    base=[(-86, 14), (-74, -2), (-58, -12), (-40, -18), (-24, -22), "MT!", (-3, -20), (0, -12)],
    under=[(6, -10), (14, -13), (22, -12), (38, -11), (56, -12), (70, -14), (80, -20), (78, -32), (72, -44), "tub!"],
    alveolar=[(96, -54.5), "pr!"],
    face_up=[(126, -46), (124, -36), "ans!", (114, -26), (110.5, -17), (111.5, -6), "rh!", (108, 16)],
    nasal=["ans", (114, -26), (110.5, -17), (111.5, -6), "rh"],
    orbit=[(102, 35), (97, 38), (93, 35), (91, 26), (91, 13), (93, 4), (98, 0.5), (103, 3), (105.5, 11), (105, 20), (104, 29)],
    eam=(0, -4, 3.8, 4.8),
    mf=(86, -82),
    zyg_upper=[(4, 3), (22, 4), (44, 4), (62, 6), (74, 14), (82, 26), (88, 36), (93, 41)],
    zyg_lower=[(70, -14), (82, -10), (90, -6), (96, -4)],
    temporal=[(96, 42), (88, 58), (70, 74), (44, 86), (14, 91), (-18, 89), (-44, 80), (-60, 62), (-66, 42), (-58, 24), (-40, 10), (-20, 6), (-2, 6)],
    coronal=["B", (34, 80), (44, 62), (52, 46), (60, 32)],
    squamosal=[(60, 32), (40, 37), (14, 39), (-12, 36), (-30, 24), (-38, 14)],
    lambdoid=["L", (-80, 64), (-84, 46), (-80, 30), (-70, 16)],
    pmastoid=[(-70, 16), (-54, 15), (-38, 14)],
    zygtemp=[(48, -11), (51, -3), (53, 4)],
    lines=[[(-92, 46), (-84, 40), (-70, 34)]],
    faint=[[(98, 1), (90, -10), (80, -18)], [(110, 45), (100, 46)]],
    mand=["cd", (6, -10), (8, -26), (12, -46), (16, -64), "go", (34, -84), (56, -90), (84, -96), (106, -100), "me", "gn",
          "pog", (121, -78), "id!", (100, -69.5), (72, -68.5), (54, -68, "c"),
          (49, -55), (46, -40), "cor!", (36, -24), (28, -26), (20, -20), (16, -12), (15, -6)],
    teeth=dict(
        upper=dict(x0=126, y_alv=-55.5, y_occ=-62.5, widths=[4.5, 4.5, 7.5, 7.5, 7, 11, 10.5, 9.5],
                   kinds="iicppmmm", canine_extra=1.2, tilt=12),
        lower=dict(x0=123, y_alv=-69.5, y_occ=-62.5, widths=[4.5, 4.5, 7.5, 8, 7.5, 11.5, 11, 10],
                   kinds="iicppmmm", canine_extra=0.8, tilt=8)),
    floor=[(-86, 20), (-76, 4), (-60, -7), (-42, -12), (-24, -10), (-8, -2), (8, 2), (22, 0), (36, 1),
           (50, 9), (62, 20), (76, 26), (92, 30), (104, 40)],
    vault_thickness=9,
    labels=[
        dict(text="Long, low\nvault", at=(-24, 98), to=(-54, 114)),
        dict(text="Thick,\nstraight\nbrow bar", at=(113, 38), to=(134, 56)),
        dict(text="Angled\nocciput", at="OP", to=(-106, 54)),
        dict(text="Projecting\nface", at=(124, -38), to=(136, -32)),
        dict(text="No chin", at="pog", to=(134, -90)),
    ],
)

# --------------------------------------------------------------- Homo habilis
# KNM-ER 1813 (Koobi Fora, Kenya, ~1.9 Ma): small (510 cc) but rounded
# braincase, slight brows, moderately projecting face, small teeth.
# No mandible: the jaw is reconstructed after Olduvai jaws (OH 7, OH 13).
SKULLS["habilis"] = dict(
    specimen="after KNM-ER 1813",
    reconstructed=("mandible",),
    pt=dict(N=(72, 20), G=(78, 29), B=(12, 85), V=(-4, 86), L=(-54, 65), OP=(-71, 30), I=(-60, 10),
            MT=(-6, -23), pr=(90, -40), ans=(87, -23), rh=(82, 4), tub=(45, -41),
            cd=(8, -4), go=(14, -56), me=(83, -78), gn=(87, -75), pog=(89, -68), id=(89, -53), cor=(31, -13)),
    front_up=[(76, 24), "G", (76, 34)],
    vault=[(74.5, 40), (73, 49), (67, 59), (57, 70), (43, 78), (26, 83), "B", "V", (-22, 83), (-40, 75), "L"],
    occiput=[(-64, 53), (-70, 40), "OP", (-67, 18), "I"],
    base=[(-56, 0), (-48, -8), (-36, -14), (-24, -17), (-14, -19), "MT!", (-2, -16), (0, -10)],
    under=[(5, -8), (11, -10), (17, -9), (30, -9), (44, -10), (54, -13), (60, -18), (58, -28), (52, -36), "tub!"],
    alveolar=[(70, -41), "pr!"],
    face_up=[(90, -32), (89, -27), "ans!", (81, -21), (78.5, -14), (79.5, -6), "rh!", (77, 12)],
    nasal=["ans", (81, -21), (78.5, -14), (79.5, -6), "rh"],
    orbit=[(71, 27), (67, 29), (64, 27), (62.5, 19), (63, 8), (65, 2), (69, 0.5), (73, 2.5), (74.5, 9), (73.5, 16), (72, 22)],
    eam=(0, -3.5, 3.2, 4),
    mf=(66, -63),
    zyg_upper=[(3, 2), (16, 2.5), (32, 2), (46, 4), (54, 10), (60, 20), (64, 28)],
    zyg_lower=[(54, -13), (62, -9), (68, -6), (73, -4)],
    temporal=[(66, 31), (59, 44), (46, 58), (26, 69), (2, 72), (-22, 70), (-40, 59), (-50, 42), (-50, 28), (-42, 14), (-28, 6), (-14, 4), (-2, 4)],
    coronal=["B", (20, 70), (28, 53), (34, 39), (40, 27)],
    squamosal=[(40, 27), (30, 34), (14, 38), (-2, 38), (-14, 32), (-22, 22), (-26, 12)],
    lambdoid=["L", (-60, 50), (-61, 35), (-55, 20), (-45, 10)],
    pmastoid=[(-45, 10), (-35, 11), (-26, 12)],
    zygtemp=[(36, -9), (38, -3), (40, 2)],
    faint=[[(40, 27), (50, 26), (58, 22)], [(69, 1), (64, -6), (58, -12)]],
    mand=["cd", (3, -8), (5, -18), (8, -32), (11, -46), "go", (24, -63), (40, -68), (60, -73), (76, -77), "me", "gn",
          "pog", (89.5, -60), "id!", (70, -53.5), (46, -52.5), (37, -52, "c"),
          (34, -42), (32, -29), "cor!", (24, -19), (18, -21), (12, -16), (10, -10), (9, -5)],
    teeth=dict(
        upper=dict(x0=90, y_alv=-41.5, y_occ=-47.5, widths=[3, 3, 5.5, 6, 6, 8.5, 8, 7],
                   kinds="iicppmmm", canine_extra=0.8, tilt=10),
        lower=dict(x0=88, y_alv=-53, y_occ=-47.5, widths=[3, 3, 5.5, 6, 6, 9, 8.5, 8],
                   kinds="iicppmmm", canine_extra=0.6, tilt=6)),
    floor=[(-58, 8), (-52, -4), (-40, -11), (-27, -13), (-14, -10), (-4, -3), (6, 1), (16, 0), (26, 1),
           (36, 7), (44, 15), (54, 19), (64, 23), (72, 30)],
    vault_thickness=5,
    labels=[
        dict(text="Rounder,\nlarger\nbraincase", at=(-18, 84), to=(-44, 104)),
        dict(text="Slight brow", at=(77, 29), to=(100, 36)),
        dict(text="Smaller face\nand teeth", at=(88, -36), to=(100, -30)),
    ],
)

# ----------------------------------------------------------- Australopithecus
# Sts 5 "Mrs Ples" (Sterkfontein, South Africa, ~2.1 Ma; A. africanus):
# cranial length ~146 mm, 485 cc, low sloping forehead, flat nose, long
# projecting jaws.  No mandible: reconstructed after other Sterkfontein jaws.
SKULLS["austra"] = dict(
    specimen="after Sts 5 · A. africanus",
    reconstructed=("mandible",),
    pt=dict(N=(70, 20), G=(78, 30), B=(4, 78), V=(-12, 79), L=(-52, 58), OP=(-65, 26), I=(-56, 6),
            MT=(-5, -23), pr=(108, -44), ans=(84, -17), rh=(76, 4), tub=(48, -44),
            cd=(9, -4), go=(16, -62), me=(90, -82), gn=(97, -79), pog=(102, -72), id=(108, -58), cor=(30, -12)),
    front_up=[(74, 24), "G", (75, 35)],
    vault=[(69, 38), (64, 44), (56, 53), (44, 62), (30, 70), (16, 76), "B", "V", (-28, 76), (-42, 68), "L"],
    occiput=[(-60, 46), (-64, 36), "OP", (-62, 14), "I"],
    base=[(-52, -3), (-44, -10), (-34, -15), (-22, -18), (-12, -20), "MT!", (-1, -16), (0, -10)],
    under=[(5, -8), (11, -10), (17, -9), (30, -9), (46, -10), (60, -12), (70, -16), (72, -24), (64, -35), "tub!"],
    alveolar=[(78, -43.5), "pr!"],
    face_up=[(102, -35), (94, -26), "ans", (79, -13), (75, -6), "rh!", (73, 12)],
    nasal=[(86, -19), (79, -13), (75, -6), "rh"],
    orbit=[(68, 27), (64, 29), (61, 27), (59.5, 19), (60, 8), (62, 2), (66, 0.5), (70, 2.5), (71, 9), (70.5, 16), (70, 22)],
    eam=(0, -3.5, 3.2, 4),
    mf=(78, -68),
    zyg_upper=[(3, 2), (16, 3), (32, 3), (48, 5), (55, 10), (59, 20), (62, 28)],
    zyg_lower=[(70, -16), (76, -10), (80, -6)],
    temporal=[(64, 31), (56, 44), (42, 57), (22, 67), (0, 71), (-22, 68), (-38, 57), (-46, 40), (-46, 24), (-40, 10), (-26, 4), (-12, 3), (-2, 3)],
    coronal=["B", (12, 62), (20, 46), (28, 32), (36, 24)],
    squamosal=[(36, 24), (26, 30), (10, 33), (-6, 32), (-18, 26), (-24, 16), (-28, 8)],
    lambdoid=["L", (-58, 44), (-58, 30), (-52, 16), (-44, 6)],
    pmastoid=[(-44, 6), (-36, 7), (-28, 8)],
    zygtemp=[(38, -9), (40, -3), (42, 3)],
    faint=[[(36, 24), (46, 25), (56, 22)], [(66, 1), (70, -8), (72, -16)]],
    mand=["cd", (3, -9), (5, -22), (8, -38), (12, -52), "go", (28, -70), (48, -76), (70, -80), (84, -82), "me", "gn",
          "pog", (106, -64), "id!", (80, -58.5), (52, -58), (36, -57, "c"),
          (33, -45), (31, -30), "cor!", (23, -18), (17, -20), (12, -15), (10, -9), (10, -4)],
    teeth=dict(
        upper=dict(x0=108, y_alv=-44.5, y_occ=-52, widths=[4, 4, 7, 7.5, 7.5, 11.5, 12, 11],
                   kinds="iicppmmm", canine_extra=2.0, tilt=22),
        lower=dict(x0=107, y_alv=-58, y_occ=-52, widths=[4, 4, 7, 8, 8, 12.5, 13, 12],
                   kinds="iicppmmm", canine_extra=1.5, tilt=18)),
    floor=[(-56, 4), (-50, -6), (-38, -12), (-25, -14), (-13, -11), (-3, -3), (6, 1), (16, 0), (26, 1),
           (36, 7), (44, 15), (52, 20), (62, 23), (70, 30)],
    vault_thickness=5,
    labels=[
        dict(text="Small\nbraincase", at=(-16, 79), to=(-42, 96)),
        dict(text="Low, sloping\nforehead", at=(62, 47), to=(92, 60)),
        dict(text="Flat nose", at=(78, -4), to=(96, 6)),
        dict(text="Projecting\njaws", at=(102, -36), to=(116, -30)),
    ],
)

# --------------------------------------------- Sivapithecus ("Ramapithecus")
# GSP 15000 (Potwar Plateau, Pakistan, ~8 Ma): an orangutan-like face, with
# tall close-set orbits, no brow ridge, a concave profile and a projecting
# muzzle.  Jaws and teeth from other Siwalik finds.  No braincase is known.
SKULLS["rama"] = dict(
    specimen="after Sivapithecus GSP 15000 (face)",
    reconstructed=("vault", "occiput", "base"),
    pt=dict(N=(62, 24), G=(65, 36), B=(10, 71), V=(-6, 72), L=(-48, 56), OP=(-64, 24), I=(-56, 4),
            MT=(-4, -21), pr=(118, -40), ans=(103, -19), rh=(69, 4), tub=(48, -42),
            cd=(8, -4), go=(16, -62), me=(92, -78), gn=(100, -77), pog=(108, -72), id=(116, -56), cor=(33, -12)),
    front_up=[(64, 30), "G"],
    vault=[(62, 44), (54, 54), (42, 62), (26, 68), "B", "V", (-22, 70), (-36, 64), "L"],
    occiput=[(-56, 46), (-62, 34), "OP", (-62, 12), "I"],
    base=[(-50, -4), (-42, -10), (-32, -14), (-20, -16), (-10, -18), "MT!", (-1, -15), (0, -9)],
    under=[(5, -8), (11, -10), (17, -9), (30, -9), (44, -10), (56, -12), (66, -14), (74, -20), (72, -30), (64, -38), "tub!"],
    alveolar=[(84, -41.5), "pr!"],
    face_up=[(116, -33), (110, -25), "ans", (93, -15), (83, -8), (75, -1), "rh!", (64, 14)],
    nasal=[(98, -17), (93, -15), (83, -8), (75, -1), "rh"],
    orbit=[(60, 34), (56, 37), (53, 34), (51.5, 24), (51.5, 12), (53, 4), (57, 1), (61, 3), (62.5, 10), (62.3, 18), (62, 27)],
    eam=(0, -3, 3, 3.8),
    mf=(84, -66),
    zyg_upper=[(3, 2), (18, 3), (32, 3), (40, 6), (45, 14), (47, 24), (50, 34)],
    zyg_lower=[(74, -20), (80, -14), (86, -10)],
    temporal=[(56, 36), (48, 48), (36, 58), (18, 65), (-2, 68), (-20, 65), (-34, 55), (-42, 40), (-42, 24), (-34, 10), (-20, 4), (-8, 3), (-1, 3)],
    faint=[[(57, 1), (64, -8), (70, -16)]],
    mand=["cd", (2, -8), (4, -22), (8, -40), (12, -54), "go", (24, -68), (38, -72), (58, -75), (78, -78), "me", "gn",
          "pog", (113, -64), "id!", (90, -56.5), (60, -56), (42, -55, "c"),
          (38, -42), (35, -28), "cor!", (26, -19), (18, -21), (12, -15), (10, -9), (9, -4)],
    teeth=dict(
        upper=dict(x0=118, y_alv=-41.5, y_occ=-49, widths=[5, 5, 9, 8, 7.5, 11, 11, 10.5],
                   kinds="iicppmmm", canine_extra=14, tilt=25, gaps={1: 4}),
        lower=dict(x0=116, y_alv=-56, y_occ=-49, widths=[4, 4, 8, 10, 8, 11.5, 12, 12],
                   kinds="iicppmmm", canine_extra=8, tilt=30)),
    floor=[(-56, 2), (-50, -6), (-40, -11), (-28, -13), (-16, -10), (-6, -3), (4, 1), (14, 0), (24, 2),
           (32, 8), (38, 16), (46, 22), (56, 26), (62, 32)],
    vault_thickness=5,
    labels=[
        dict(text="Braincase\nunknown\n(dashed)", at=(-24, 70), to=(-50, 92)),
        dict(text="No brow\nridge", at=(64, 34), to=(84, 46)),
        dict(text="Dished face,\nlong muzzle", at=(98, -14), to=(124, -6)),
        dict(text="Large canine", at=(99.5, -58), to=(124, -66)),
    ],
)

# -------------------------------------------------------- Dryopithecine ape
# Composite after Rudapithecus (Rudabanya, Hungary, ~10 Ma: RUD 77 partial
# cranium, RUD 200 face) and Hispanopithecus jaws: small braincase, brow
# ridge, moderately projecting face tilted downward, large canines.
SKULLS["dryo"] = dict(
    specimen="composite after Rudapithecus (RUD 77, RUD 200)",
    reconstructed=("occiput", "base"),
    pt=dict(N=(56, 22), G=(61, 32), B=(8, 69), V=(-8, 70), L=(-48, 54), OP=(-63, 22), I=(-54, 3),
            MT=(-4, -21), pr=(96, -36), ans=(86, -18), rh=(63, 4), tub=(42, -37),
            cd=(7, -4), go=(14, -54), me=(82, -68), gn=(88, -64), pog=(92, -57), id=(96, -47), cor=(27, -11)),
    front_up=[(58, 25), "G", (58, 37)],
    vault=[(54, 39), (52, 44), (46, 52), (36, 60), (22, 66), "B", "V", (-24, 68), (-38, 62), "L"],
    occiput=[(-56, 44), (-61, 32), "OP", (-60, 10), "I"],
    base=[(-48, -5), (-40, -11), (-30, -15), (-19, -17), (-10, -19), "MT!", (-1, -15), (0, -9)],
    under=[(5, -8), (11, -10), (17, -9), (28, -9), (40, -10), (50, -12), (58, -15), (62, -22), (58, -30), "tub!"],
    alveolar=[(70, -37), "pr!"],
    face_up=[(94, -30), (90, -24), "ans", (80, -14), (74, -8), (68, -1), "rh!", (59, 13)],
    nasal=[(84, -17), (80, -14), (74, -8), (68, -1), "rh"],
    orbit=[(55, 30), (51, 33), (48, 30), (46.5, 22), (46.5, 11), (48, 4), (52, 1), (56, 3), (57.5, 10), (57, 17), (56, 24)],
    eam=(0, -3, 3, 3.8),
    mf=(72, -57),
    zyg_upper=[(3, 2), (16, 3), (28, 3), (36, 5), (41, 12), (43, 22), (46, 30)],
    zyg_lower=[(58, -15), (64, -11), (70, -8)],
    temporal=[(50, 36), (44, 48), (32, 58), (14, 64), (-6, 67), (-24, 64), (-36, 54), (-42, 38), (-42, 22), (-34, 9), (-20, 4), (-8, 3), (-1, 3)],
    coronal=["B", (14, 54), (20, 40), (26, 28), (30, 22)],
    squamosal=[(30, 22), (20, 27), (6, 29), (-8, 28), (-18, 22), (-24, 13), (-27, 6)],
    faint=[[(52, 1), (58, -8), (62, -16)]],
    mand=["cd", (2, -8), (3, -18), (6, -32), (10, -46), "go", (24, -60), (40, -64), (58, -67), (74, -69), "me", "gn",
          "pog", (94, -51), "id!", (74, -48.5), (46, -47.5), (33, -47, "c"),
          (30, -36), (28, -24), "cor!", (21, -16), (15, -18), (10, -13), (8, -8), (8, -4)],
    teeth=dict(
        upper=dict(x0=96, y_alv=-37, y_occ=-43.5, widths=[4, 4, 8, 7, 6.5, 9.5, 9.5, 9],
                   kinds="iicppmmm", canine_extra=9, tilt=20, gaps={1: 3}),
        lower=dict(x0=96, y_alv=-48, y_occ=-43.5, widths=[3.5, 3.5, 7, 9, 7, 10, 10, 10],
                   kinds="iicppmmm", canine_extra=6, tilt=25)),
    floor=[(-50, 2), (-44, -6), (-34, -11), (-23, -13), (-12, -10), (-3, -3), (5, 1), (14, 0), (22, 2),
           (30, 8), (36, 15), (43, 20), (50, 24), (56, 32)],
    vault_thickness=4.5,
    labels=[
        dict(text="Small\nbraincase", at=(-12, 70), to=(-40, 86)),
        dict(text="Brow ridge", at="G", to=(82, 42)),
        dict(text="Projecting\njaws", at=(92, -30), to=(106, -24)),
        dict(text="Large canine", at=(81, -50), to=(106, -60)),
    ],
)
