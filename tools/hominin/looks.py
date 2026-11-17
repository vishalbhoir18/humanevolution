"""Inferred soft-tissue appearance for each stage.

None of this fossilises.  Each entry records the reasoning so the site can
show visitors which parts of a reconstruction are evidence and which are
informed inference.  Colours are sRGB 0-255.

cover: fraction of skin hidden by body hair (0 bare .. 1 dense coat)
"""

LOOKS = {}

LOOKS["sapiens"] = dict(
    skin=(104, 70, 50), palm=(176, 132, 110), lips=(104, 60, 56), flush=(120, 56, 46), flush_amt=0.10,
    hair=((14, 12, 11), (44, 36, 30)), fur=((24, 19, 16), (60, 48, 40)),
    cover=dict(body=0.05, ventral=0.10, hands=0.03, head=0.0, face=0.0),
    scalp=1.0, beard=0.55, brows=1.0,
    sclera=(236, 230, 220), iris=((96, 60, 30), (44, 28, 16)),
    basis="Dark skin: genomes of early modern humans, including a ~7,000-year-old European "
          "hunter-gatherer (La Brana), carry the ancestral alleles for dark pigmentation. "
          "Hair form and beard are inferred.",
)

LOOKS["neander"] = dict(
    skin=(160, 116, 88), palm=(200, 156, 134), lips=(138, 84, 76), flush=(158, 78, 64), flush_amt=0.3, mottle=1.5,
    hair=((70, 38, 22), (136, 82, 46)), fur=((84, 52, 34), (150, 104, 70)),
    cover=dict(body=0.12, ventral=0.2, hands=0.08, head=0.0, face=0.0),
    scalp=1.0, beard=0.56, brows=1.0, hairline=dict(front=(0.6, 7.0)),
    sclera=(234, 228, 216), iris=((116, 92, 56), (60, 44, 26)),
    basis="Pale skin and reddish hair are one possibility: an MC1R variant found in two Neanderthals "
          "would reduce pigment. Other Neanderthal genomes point to darker skin and hair, so colouring varied.",
)

LOOKS["erectus"] = dict(
    skin=(92, 62, 46), palm=(160, 118, 98), lips=(88, 52, 48), flush=(108, 50, 42), flush_amt=0.08,
    hair=((14, 12, 11), (40, 33, 28)), fur=((22, 18, 15), (58, 46, 38)),
    cover=dict(body=0.14, ventral=0.18, hands=0.06, head=0.0, face=0.0),
    scalp=1.0, beard=0.4, brows=1.0, hairline=dict(front=(-0.6, 6.9)),
    sclera=(226, 216, 200), iris=((84, 52, 26), (38, 24, 14)),
    basis="Largely hairless, dark skin: the long-legged, heat-shedding build implies sweating "
          "over bare skin, and MC1R evidence suggests dark pigmentation by ~1.2 Ma.",
)

LOOKS["habilis"] = dict(
    skin=(82, 58, 46), palm=(150, 112, 96), lips=(78, 50, 46), flush=(98, 48, 42), flush_amt=0.07,
    hair=((16, 13, 12), (46, 38, 32)), fur=((20, 16, 14), (62, 50, 42)),
    cover=dict(body=0.5, ventral=0.36, hands=0.25, head=0.9, face=0.02),
    scalp=1.0, beard=0.25, brows=0.6, hairline=dict(front=(0.9, 5.6), temple=0.8), nails=(110, 88, 76),
    sclera=(190, 170, 146), iris=((78, 48, 24), (34, 22, 12)),
    basis="Body hair is drawn intermediate between ape and human. When hominins lost their coat "
          "is not known from fossils; this is a mid-way assumption.",
)

LOOKS["austra"] = dict(
    skin=(70, 52, 44), palm=(142, 108, 96), lips=(70, 48, 46), flush=(86, 46, 42), flush_amt=0.06,
    hair=((15, 12, 11), (52, 42, 35)), fur=((18, 15, 13), (64, 52, 43)),
    cover=dict(body=0.88, ventral=0.6, hands=0.5, head=0.95, face=0.03),
    scalp=1.0, beard=0.15, brows=0.3, hairline=dict(front=(1.4, 4.4), temple=0.4), nails=(70, 56, 50),
    sclera=(150, 122, 96), iris=((74, 46, 24), (32, 20, 12)),
    basis="Ape-like body hair over dark skin is the conventional reconstruction; "
          "no direct evidence of hair cover or skin colour survives.",
)

LOOKS["rama"] = dict(
    skin=(66, 50, 44), palm=(120, 92, 82), lips=(62, 44, 42), flush=(80, 44, 40), flush_amt=0.05,
    hair=((40, 22, 13), (98, 56, 30)), fur=((44, 24, 14), (108, 62, 34)),
    cover=dict(body=0.97, ventral=0.8, hands=0.6, head=0.98, face=0.03),
    scalp=1.0, beard=0.0, brows=0.0, hairline=dict(front=(1.6, 3.9), temple=0.3), strand=1.25, nails=(52, 40, 36),
    sclera=(96, 70, 52), iris=((70, 42, 22), (30, 18, 10)),
    basis="Rufous coat chosen only because the face of Sivapithecus resembles the orangutan's; "
          "coat colour is unknown.",
)

LOOKS["dryo"] = dict(
    skin=(62, 48, 42), palm=(116, 90, 80), lips=(58, 42, 40), flush=(76, 42, 38), flush_amt=0.05,
    hair=((13, 11, 10), (48, 40, 34)), fur=((15, 13, 12), (56, 46, 39)),
    cover=dict(body=0.97, ventral=0.75, hands=0.6, head=0.98, face=0.03),
    scalp=1.0, beard=0.0, brows=0.0, hairline=dict(front=(1.6, 3.9), temple=0.3), strand=1.15, nails=(46, 38, 35),
    sclera=(88, 66, 50), iris=((70, 44, 24), (30, 19, 11)),
    basis="Dark coat and dark sclera follow living African apes; neither is preserved in fossils.",
)
