/* Human evolution as a branching tree.
   Plain SVG built from the TAXA table below (no library).
   Time runs left to right; each lineage has its own row; its bar spans the
   known fossils.  Branch lines: solid = broadly accepted descent,
   dashed = debated.  Dotted arrows = interbreeding shown by ancient DNA.
   Depends on SPECIES / select() from index.html (optional). */
(function () {
"use strict";
const host = document.getElementById("treeChart");
if (!host) return;
const NS = "http://www.w3.org/2000/svg";
const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* ------------------------------------------------------------------ scale */
const W = 1100, X_NOW = 830, TOP = 70, ROW = 27, HEAD = 22, AXIS = 50;
/* the last 7 million years get 620 units on a square-root scale; 25-7 mya are compressed */
function x(t) { return t <= 7 ? X_NOW - 620 * Math.sqrt(t / 7) : X_NOW - 620 - 180 * Math.min(t - 7, 18) / 18; }

const KIND = {
  apes:      { label: "Apes",                 color: "#a09279" },
  early:     { label: "Earliest hominins",    color: "#b8803f" },
  austra:    { label: "Australopiths",        color: "#dcbb84" },
  robust:    { label: "Robust australopiths", color: "#c8765a" },
  earlyhomo: { label: "Early Homo",           color: "#a3c99b" },
  homo:      { label: "Later Homo",           color: "#5fb3a1" },
  sapiens:   { label: "Homo sapiens",         color: "#f1e9d8" }
};

/* ------------------------------------------------------------------- data
   start/end: oldest and youngest fossils, millions of years ago.
   parent: [id, branch time (mya), "solid" | "dashed"]. */
const TAXA = {
  stem: { name: "Ancestral apes", kind: "apes", start: 25, end: 7.6, ghostOnly: true, labelAt: "start",
    where: "Africa, later also Europe and Asia",
    shows: "The lineage that led to today's great apes and to us. Judging from DNA and the oldest hominin fossils, the last common ancestor of humans and chimpanzees lived roughly 7–6 million years ago. It has not been identified among known fossils." },

  proconsul: { name: "Proconsul & kin", sci: "Proconsul, Ekembo", kind: "apes", start: 21, end: 17, parent: ["stem", 22, "dashed"],
    where: "Kenya and Uganda (Rusinga Island, Lake Victoria)",
    fossils: "KNM-RU 7290 skull (1948); Ekembo partial skeletons", brain: "about 150–170 cc",
    shows: "An early ape: no tail, but a monkey-like body that walked along the tops of branches.",
    syllabus: "The syllabus places Dryopithecus at Lake Victoria 20–25 million years ago. Those East African fossils are now called Proconsul and Ekembo." },
  dryo: { name: "Dryopithecines", sci: "Dryopithecus, Hispanopithecus, Rudapithecus", kind: "apes", start: 12.5, end: 9.5, parent: ["stem", 13.5, "dashed"], stage: "dryo",
    where: "Europe (Spain, France, Hungary)",
    fossils: "IPS 18800 skeleton, Can Llobateres (Spain); RUD 77 and RUD 200, Rudabánya (Hungary)", brain: "about 305–330 cc (Rudapithecus)",
    shows: "Great apes with a broad chest, a short lower back and long arms for hanging. Part of the radiation that produced the living great apes; which branch they sit on is debated." },
  siva: { name: "Sivapithecus", sci: "formerly “Ramapithecus”", kind: "apes", start: 12.5, end: 8.5, tail: "→ living orangutans", parent: ["stem", 15, "dashed"], stage: "rama",
    where: "Siwalik Hills, India and Pakistan",
    fossils: "GSP 15000 face (Potwar Plateau, Pakistan)", brain: "not known",
    shows: "An orangutan-like face on a body that walked on four limbs. Jaw fragments called Ramapithecus were once taken for a human ancestor, until this face was described in 1982." },
  gorillas: { name: "Gorillas", kind: "apes", start: 9, end: 0, living: true, parent: ["stem", 9, "solid"],
    where: "Central Africa", fossils: "very few; Chororapithecus (Ethiopia, about 8 mya) may be an early relative",
    shows: "The gorilla lineage split from the line leading to chimpanzees and humans about 9–8 million years ago, estimated from DNA." },
  chimps: { name: "Chimpanzees & bonobos", kind: "apes", start: 7.6, end: 0, living: true, parent: ["stem", 7.6, "solid"],
    where: "Central and West Africa", fossils: "a few teeth about 500,000 years old (Kenya)",
    shows: "Our closest living relatives. The chimpanzee and human lineages split roughly 7–6 million years ago." },

  sahel: { name: "Sahelanthropus tchadensis", nick: "“Toumaï”", kind: "early", start: 7.2, end: 6.8, parent: ["stem", 7.6, "dashed"],
    where: "Chad (Djurab Desert)", fossils: "TM 266 skull (2001)", brain: "about 360 cc",
    shows: "A chimp-sized brain with a short face and small canines. The skull base hints at a head held above an upright body.",
    debate: "Whether it walked upright, and whether it is a hominin at all, is disputed." },
  orrorin: { name: "Orrorin tugenensis", kind: "early", start: 6.1, end: 5.7, parent: ["stem", 7.6, "dashed"],
    where: "Kenya (Tugen Hills)", fossils: "thigh bones, teeth and jaw fragments (2000)", brain: "not known",
    shows: "Its thigh bones have a neck built to carry the body's weight on two legs: strong early evidence of upright walking." },
  kadabba: { name: "Ardipithecus kadabba", kind: "early", start: 5.8, end: 5.2, parent: ["stem", 7.6, "dashed"],
    where: "Ethiopia (Middle Awash)", fossils: "teeth, jaw fragments and a toe bone", brain: "not known",
    shows: "Known mostly from teeth. A toe bone suggests it pushed off the ground the way upright walkers do." },
  ramidus: { name: "Ardipithecus ramidus", nick: "“Ardi”", kind: "early", start: 4.5, end: 4.3, parent: ["kadabba", 5.2, "dashed"],
    where: "Ethiopia (Aramis, Middle Awash)", fossils: "ARA-VP-6/500 “Ardi” partial skeleton", brain: "about 300–350 cc",
    shows: "Walked upright on the ground with a partly reshaped pelvis, yet kept a grasping big toe for climbing. Upright walking came long before big brains." },

  anamensis: { name: "Australopithecus anamensis", kind: "austra", start: 4.2, end: 3.8, parent: ["ramidus", 4.3, "dashed"],
    where: "Kenya and Ethiopia", fossils: "Kanapoi shin bone; MRD skull, Woranso-Mille (3.8 mya)", brain: "about 365–370 cc",
    shows: "The earliest Australopithecus. Its shin bone has a human-like knee and ankle joint for upright walking.",
    debate: "The MRD skull shows it overlapped in time with A. afarensis, so the change from one to the other was not a simple single line." },
  afarensis: { name: "Australopithecus afarensis", nick: "“Lucy”", kind: "austra", start: 3.9, end: 2.9, parent: ["anamensis", 3.9, "solid"], stage: "austra",
    where: "Ethiopia, Kenya, Tanzania", fossils: "AL 288-1 “Lucy”; Laetoli footprints (3.66 mya); Dikika child", brain: "about 380–550 cc",
    shows: "A fully upright walker with an ape-sized brain; curved fingers show it still climbed trees." },
  kenyan: { name: "Kenyanthropus platyops", kind: "austra", start: 3.5, end: 3.3, parent: ["anamensis", 3.8, "dashed"],
    where: "Kenya (Lomekwi, West Turkana)", fossils: "KNM-WT 40000 skull (1999)", brain: "not known",
    shows: "A flatter face than other hominins of its time. The oldest known stone tools (Lomekwi 3, 3.3 mya) come from the same area, but who made them is unknown.",
    debate: "The skull is badly distorted, so whether it is a separate genus is debated." },
  africanus: { name: "Australopithecus africanus", kind: "austra", start: 3.0, end: 2.1, parent: ["afarensis", 3.0, "dashed"], stage: "austra",
    where: "South Africa (Taung, Sterkfontein, Makapansgat)", fossils: "Taung child (1924); Sts 5 “Mrs Ples”; Sts 14 skeleton", brain: "about 450 cc on average",
    shows: "The first australopith found. A rounder skull and smaller face than A. afarensis, on a similar small body.",
    debate: "The 3.67-million-year-old Little Foot skeleton may belong here or to a separate species." },
  sediba: { name: "Australopithecus sediba", kind: "austra", start: 1.98, end: 1.97, parent: ["africanus", 2.1, "dashed"],
    where: "South Africa (Malapa)", fossils: "MH1 and MH2 partial skeletons (2008)", brain: "about 420 cc",
    shows: "A mosaic: a small brain and climbing arms, with a fairly human-like hand and pelvis. Possibly close to the origin of Homo, though it is younger than the oldest Homo fossils." },
  garhi: { name: "Australopithecus garhi", kind: "austra", start: 2.5, end: 2.48, parent: ["afarensis", 2.9, "dashed"],
    where: "Ethiopia (Bouri, Middle Awash)", fossils: "BOU-VP-12/130 skull (1999)", brain: "about 450 cc",
    shows: "Found near antelope bones with stone-tool cut marks of about the same age; one candidate for the ancestor of Homo." },

  aethiopicus: { name: "Paranthropus aethiopicus", nick: "“Black Skull”", kind: "robust", start: 2.7, end: 2.3, parent: ["afarensis", 2.9, "dashed"],
    where: "Ethiopia and Kenya", fossils: "KNM-WT 17000 “Black Skull” (1985)", brain: "about 410 cc",
    shows: "The earliest robust australopith: very large chewing teeth and a bony crest on top of the skull for huge jaw muscles." },
  boisei: { name: "Paranthropus boisei", nick: "“Nutcracker Man”", kind: "robust", start: 2.3, end: 1.3, parent: ["aethiopicus", 2.3, "solid"],
    where: "Tanzania, Kenya, Ethiopia, Malawi", fossils: "OH 5 “Zinj” (Olduvai Gorge, 1959)", brain: "about 475–545 cc",
    shows: "The biggest molars of any hominin. Despite the nickname, tooth wear and chemistry point to tough grasses and sedges, not nuts. It lived alongside early Homo for about a million years." },
  robustus: { name: "Paranthropus robustus", kind: "robust", start: 2.0, end: 1.0, parent: ["aethiopicus", 2.3, "dashed"],
    where: "South Africa (Swartkrans, Kromdraai, Drimolen)", fossils: "SK 48; DNH 7 (Drimolen, about 2.0 mya)", brain: "about 450–530 cc",
    shows: "The South African robust australopith, with the same heavy jaws and big molars.",
    debate: "It may descend from P. aethiopicus, or have evolved its heavy jaws separately from A. africanus." },

  earlyhomo: { name: "Earliest Homo", sci: "LD 350-1 jaw", kind: "earlyhomo", start: 2.8, end: 2.75, parent: ["afarensis", 2.95, "dashed"],
    where: "Ethiopia (Ledi-Geraru, Afar)", fossils: "LD 350-1 lower jaw (2013)", brain: "not known",
    shows: "A lower jaw that mixes Australopithecus and Homo traits: the oldest fossil placed in our own genus." },
  habilis: { name: "Homo habilis", nick: "“Handy man”", kind: "earlyhomo", start: 2.4, end: 1.4, parent: ["earlyhomo", 2.75, "dashed"], stage: "habilis",
    where: "Tanzania, Kenya, Ethiopia", fossils: "OH 7 (1960); OH 24; KNM-ER 1813; OH 62", brain: "about 510–825 cc",
    shows: "A larger brain and smaller teeth than the australopiths, found with Oldowan stone tools; still small-bodied, with long arms.",
    debate: "Some researchers argue it belongs in Australopithecus." },
  rudolfensis: { name: "Homo rudolfensis", kind: "earlyhomo", start: 2.1, end: 1.8, parent: ["earlyhomo", 2.75, "dashed"],
    where: "Kenya (Koobi Fora)", fossils: "KNM-ER 1470 skull (1972); KNM-ER 62000 face", brain: "about 750 cc",
    shows: "A larger brain and a long, flat face: evidence that several kinds of early Homo lived side by side." },

  erectus: { name: "Homo erectus", kind: "homo", start: 2.0, end: 0.11, parent: ["habilis", 2.1, "dashed"], stage: "erectus",
    where: "Africa, Georgia, China, Indonesia", fossils: "Turkana Boy; Dmanisi skulls (Georgia); Trinil and Sangiran (Java); Zhoukoudian “Peking Man”", brain: "about 550–1,250 cc",
    shows: "Human-like body proportions, with long legs for walking and running. Made hand axes from 1.76 million years ago, is the first hominin whose fossils are found outside Africa, and survived in Java until about 110,000 years ago." },
  antecessor: { name: "Homo antecessor", kind: "homo", start: 0.9, end: 0.77, parent: ["erectus", 1.2, "dashed"],
    where: "Spain (Gran Dolina, Atapuerca)", fossils: "ATD6-69 child's face and other remains", brain: "about 1,000 cc (estimated)",
    shows: "Among the earliest humans in western Europe, with a strikingly modern-looking mid-face. Ancient proteins (2020) place it close to the common ancestor of Neanderthals, Denisovans and Homo sapiens." },

  naledi: { name: "Homo naledi", kind: "homo", start: 0.335, end: 0.236, parent: ["habilis", 1.8, "dashed"],
    where: "South Africa (Rising Star Cave)", fossils: "more than 1,500 fossils from at least 15 individuals", brain: "about 465–610 cc",
    shows: "A small brain on a body with human-like hands and feet, alive at the same time as early Homo sapiens. Where it joins the tree is unresolved: its ancestors would have left no fossils for over a million years.",
    debate: "Claims (2023) that it buried its dead are disputed." },
  floresiensis: { name: "Homo floresiensis", nick: "“the Hobbit”", kind: "homo", start: 0.7, end: 0.06, segments: [[0.71, 0.69], [0.1, 0.06]], parent: ["erectus", 1.0, "dashed"],
    where: "Indonesia (Flores)", fossils: "LB1 skeleton, Liang Bua (2003); Mata Menge jaw and teeth", brain: "about 420 cc",
    shows: "About 1.1 m tall. Skeletons at Liang Bua are 100,000–60,000 years old, and small hominins already lived on Flores 700,000 years ago.",
    debate: "It may descend from Homo erectus that shrank on the island, or from an earlier small-bodied Homo." },
  luzonensis: { name: "Homo luzonensis", kind: "homo", start: 0.15, end: 0.13, parent: ["erectus", 0.8, "dashed"],
    where: "Philippines (Callao Cave, Luzon)", fossils: "teeth, hand and foot bones (2019)", brain: "not known",
    shows: "Tiny teeth and curved finger and toe bones: a second island lineage in Southeast Asia. Re-dating (2023) shows the fossils are at least 134,000 years old.",
    debate: "Its ancestry is unknown." },

  heidelbergensis: { name: "Homo heidelbergensis", kind: "homo", start: 0.7, end: 0.2, parent: ["erectus", 0.9, "dashed"],
    where: "Africa and Europe", fossils: "Mauer jaw (Germany, 1907); Kabwe 1 (Zambia); Bodo (Ethiopia)", brain: "about 1,100–1,325 cc",
    shows: "Large-brained Middle Pleistocene humans, often placed near the common ancestor of Neanderthals, Denisovans and Homo sapiens.",
    debate: "Researchers disagree on its name and on which fossils belong to it; some African fossils are called H. rhodesiensis or H. bodoensis." },
  denisovans: { name: "Denisovans", kind: "homo", start: 0.2, end: 0.05, parent: ["neanderthals", 0.45, "solid"],
    where: "Asia: Siberia, Tibet, China, Taiwan, Laos", fossils: "finger bone and teeth (Denisova Cave); Xiahe jaw (Tibet); Harbin skull (China); Penghu jaw (Taiwan)", brain: "about 1,420 cc, if the Harbin skull is typical",
    shows: "First identified from DNA in a finger bone (2010). In 2025, ancient proteins and DNA linked the Harbin skull to them, giving Denisovans a face for the first time. They are the sister group of the Neanderthals.",
    mixing: "They interbred with Neanderthals and with Homo sapiens. People in New Guinea and Australia carry a few percent of Denisovan DNA, and Tibetans owe a high-altitude gene variant (EPAS1) to them." },
  neanderthals: { name: "Neanderthals", sci: "Homo neanderthalensis", kind: "homo", start: 0.43, end: 0.04, parent: ["heidelbergensis", 0.6, "solid"], stage: "neander",
    where: "Europe and western and central Asia", fossils: "Neanderthal 1 (1856); La Chapelle-aux-Saints 1; Shanidar; Sima de los Huesos (430,000 years, early members)", brain: "about 1,200–1,750 cc",
    shows: "Big-brained, stocky, cold-adapted humans who used fire, made complex stone tools and buried some of their dead.",
    mixing: "Most people outside Africa carry about 1–2% Neanderthal DNA." },
  sapiens: { name: "Homo sapiens", kind: "sapiens", start: 0.315, end: 0, parent: ["heidelbergensis", 0.6, "dashed"], stage: "sapiens",
    where: "Africa, then worldwide", fossils: "Jebel Irhoud, Morocco (about 315,000 years); Omo Kibish; Herto; Cro-Magnon 1", brain: "about 1,350 cc on average",
    shows: "A globular braincase, a small face and a chin. Spread out of Africa mainly after about 60,000 years ago, meeting Neanderthals and Denisovans and interbreeding with both." }
};

/* rows, top to bottom.  Multi-member groups collapse into one row. */
const GROUPS = [
  { id: "g1", label: "Dryopithecus", num: 1, stage: "dryo", members: ["proconsul", "dryo"] },
  { id: "g2", label: "Ramapithecus (Sivapithecus)", num: 2, stage: "rama", members: ["siva"] },
  { id: "ggor", members: ["gorillas"] },
  { id: "gchi", members: ["chimps"] },
  { id: "gstem", members: ["stem"] },
  { id: "gearly", label: "Earliest hominins", members: ["sahel", "orrorin", "kadabba", "ramidus"] },
  { id: "g3", label: "Australopithecus", num: 3, stage: "austra", members: ["anamensis", "afarensis", "kenyan", "africanus", "sediba", "garhi"] },
  { id: "grob", label: "Robust australopiths", members: ["aethiopicus", "boisei", "robustus"] },
  { id: "g4", label: "Homo habilis", num: 4, stage: "habilis", members: ["earlyhomo", "habilis", "rudolfensis"] },
  { id: "g5", label: "Homo erectus", num: 5, stage: "erectus", members: ["erectus", "antecessor"] },
  { id: "gside", label: "Island & small-brained Homo", members: ["naledi", "floresiensis", "luzonensis"] },
  { id: "gheid", members: ["heidelbergensis"] },
  { id: "gden", members: ["denisovans"] },
  { id: "g6", label: "Neanderthals", num: 6, stage: "neander", members: ["neanderthals"] },
  { id: "g7", label: "Homo sapiens", num: 7, stage: "sapiens", members: ["sapiens"] }
];
const GROUP = {}; GROUPS.forEach(g => { GROUP[g.id] = g; g.members.forEach(m => TAXA[m].group = g); });

const GENEFLOW = [
  { from: "neanderthals", to: "sapiens", t: 0.052 },
  { from: "denisovans", to: "sapiens", t: 0.043 },
  { from: "neanderthals", to: "denisovans", t: 0.09, both: true }
];

const MILESTONES = [
  { id: "walk",   t: 6.5,  tier: 0, text: "Upright walking begins?" },
  { id: "ardi",   t: 4.4,  tier: 1, text: "Ardi: walks, still climbs" },
  { id: "laet",   t: 3.66, tier: 2, text: "Laetoli footprints" },
  { id: "tools",  t: 3.3,  tier: 0, text: "Oldest stone tools" },
  { id: "afr",    t: 1.8,  tier: 1, text: "Out of Africa" },
  { id: "axe",    t: 1.76, tier: 2, text: "Hand axes" },
  { id: "fire",   t: 1.0,  tier: 0, text: "Fire" },
  { id: "sap",    t: 0.315, tier: 1, text: "Homo sapiens" },
  { id: "mix",    t: 0.05, tier: 2, text: "Interbreeding" }
];

const LEAPS = [
  { title: "Walking upright came first", when: "about 7–3.7 million years ago", milestones: ["walk", "ardi", "laet"],
    taxa: ["sahel", "orrorin", "kadabba", "ramidus", "anamensis", "afarensis"],
    text: "Thigh bones of Orrorin, the pelvis of Ardi and the Laetoli footprints show hominins walking on two legs millions of years before brains grew. Ardi's brain, about 4.4 million years ago, was no bigger than a chimpanzee's." },
  { title: "Stone tools", when: "from 3.3 million years ago", milestones: ["tools", "axe"],
    taxa: ["kenyan", "garhi", "earlyhomo", "habilis", "erectus"],
    text: "Simple flakes from Lomekwi, Kenya are 3.3 million years old, older than any Homo fossil, so australopiths may have made them. Oldowan tools follow from about 2.6 million years ago, and Homo erectus began shaping hand axes 1.76 million years ago." },
  { title: "Bigger brains and longer journeys", when: "after 2 million years ago", milestones: ["afr", "fire"],
    taxa: ["habilis", "rudolfensis", "erectus", "antecessor", "heidelbergensis"],
    text: "Brain size climbed from about 500 cc to over 1,000 cc in Homo. Homo erectus, with long legs and human body proportions, reached Georgia by 1.8 million years ago and later China and Java. Signs of fire use date back about a million years." },
  { title: "Many kinds of human at once", when: "the last 300,000 years", milestones: ["sap", "mix"],
    taxa: ["sapiens", "neanderthals", "denisovans", "floresiensis", "luzonensis", "naledi", "erectus"],
    text: "When Homo sapiens appeared, at least five other kinds of human were alive. Our ancestors met Neanderthals and Denisovans and had children with them: their DNA survives in people today." }
];

/* ------------------------------------------------------------- helpers */
function el(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}
function esc(s) { return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }
function span(a) {
  if (a.living) return `split ${a.start} mya`;
  if (a.ghostOnly) return "";
  if (a.start >= 1 && a.end >= 1) return `${+a.start.toFixed(2)}–${+a.end.toFixed(2)} mya`;
  if (a.end === 0) return `${Math.round(a.start * 1000)},000 yrs ago–now`;
  if (a.start < 1) return `${Math.round(a.start * 1000)},000–${Math.round(a.end * 1000)},000 yrs ago`;
  return `${+a.start.toFixed(2)} mya–${Math.round(a.end * 1000)},000 yrs ago`;
}
function isBinomial(a) { return /^(Homo|Australopithecus|Paranthropus|Ardipithecus|Sahelanthropus|Orrorin|Kenyanthropus|Sivapithecus) /.test(a.name) || a.name === "Sivapithecus"; }
function stageIndex(stage) { return typeof SPECIES !== "undefined" ? SPECIES.findIndex(s => s.id === stage) : -1; }

/* ------------------------------------------------------------- state */
const expanded = new Set();
let selected = null;        // taxon id or "g:<groupId>"
let focus = null;           // {taxa:Set, milestones:Set} from a key-leap card
let stageHL = null;         // stage id from the rest of the page
let rows = [], rowOfTaxon = {}, height = 0;
const rowEls = new Map();

/* ------------------------------------------------------------- svg skeleton */
const svg = el("svg", { viewBox: `0 0 ${W} 400`, class: "tree-svg", role: "img", "aria-label": "Branching tree of human evolution" }, host);
const defs = el("defs", null, svg);
const mk = el("marker", { id: "tr-arrow", viewBox: "0 0 10 10", refX: "8", refY: "5", markerWidth: "5", markerHeight: "5", orient: "auto-start-reverse" }, defs);
el("path", { d: "M0,0 L10,5 L0,10 z", class: "tr-arrowhead" }, mk);
const gGrid = el("g", { class: "tr-grid" }, svg);
const gMile = el("g", { class: "tr-miles" }, svg);
const gLinks = el("g", { class: "tr-links" }, svg);
const gFlow = el("g", { class: "tr-flow" }, svg);
const gRows = el("g", { class: "tr-rows" }, svg);
const gAxis = el("g", { class: "tr-axis" }, svg);

/* milestones: labels in a band at the top, lines down through the rows */
const mileEls = {};
MILESTONES.forEach(m => {
  const g = el("g", { class: "tr-mile", "data-id": m.id }, gMile);
  const ty = 16 + m.tier * 15;
  el("line", { x1: x(m.t), x2: x(m.t), y1: ty + 4, y2: 400, class: "tr-mile-line" }, g);
  el("circle", { cx: x(m.t), cy: ty + 4, r: 2.2, class: "tr-mile-dot" }, g);
  const t = el("text", { x: x(m.t) + 5, y: ty + 7.5, class: "tr-mile-text" }, g);
  t.textContent = m.text;
  mileEls[m.id] = g;
});

/* ------------------------------------------------------------- layout */
function computeRows() {
  const out = [];
  let y = TOP;
  GROUPS.forEach(g => {
    const multi = g.members.length > 1;
    if (multi && expanded.has(g.id)) {
      out.push({ key: "h:" + g.id, type: "header", g, y: y + HEAD / 2 }); y += HEAD;
      g.members.forEach(m => { out.push({ key: "t:" + m, type: "taxon", g, ids: [m], y: y + ROW / 2 }); y += ROW; });
    } else {
      out.push({ key: multi ? "g:" + g.id : "t:" + g.members[0], type: multi ? "group" : "taxon", g, ids: g.members.slice(), y: y + ROW / 2 });
      y += ROW;
    }
  });
  return { rows: out, height: y };
}

function barEnd(r) {
  let e = 0;
  r.ids.forEach(id => { const a = TAXA[id]; const xe = a.living ? X_NOW : x(a.end); e = Math.max(e, xe); });
  return e;
}

function buildRow(r) {
  const g = el("g", { class: `tr-row tr-${r.type}`, "data-key": r.key });
  if (r.type === "header") {
    const grp = r.g;
    const lab = el("g", { class: "tr-label tr-toggle", tabindex: 0, role: "button", "aria-expanded": "true",
      "aria-label": `${grp.label}: show fewer` }, g);
    const t0 = Math.max(...grp.members.map(m => TAXA[m].start));
    const left = Math.max(34, x(t0) - 12);
    const anchor = x(t0) - 12 > 190 ? "end" : "start";
    const t = el("text", { x: anchor === "end" ? left : 34, y: 4, "text-anchor": anchor, class: "tr-head-text" }, lab);
    t.innerHTML = `${grp.num ? `<tspan class="tr-num">${grp.num} ·</tspan> ` : ""}${esc(grp.label.toUpperCase())}<tspan class="tr-chip"> ▾ fewer</tspan>`;
    lab.addEventListener("click", () => toggleGroup(grp.id));
    return g;
  }
  const isGroup = r.type === "group";
  r.ids.forEach(id => {
    const a = TAXA[id];
    const col = KIND[a.kind].color;
    const mg = el("g", { class: "tr-marks", "data-id": id }, g);
    if (a.ghostOnly) {
      el("line", { x1: x(a.start), x2: x(a.end), y1: 0, y2: 0, class: "tr-ghost" }, mg);
    } else if (a.living) {
      el("line", { x1: x(a.start), x2: X_NOW, y1: 0, y2: 0, class: "tr-living", stroke: col }, mg);
    } else {
      const segs = a.segments || [[a.start, a.end]];
      if (segs.length > 1) el("line", { x1: x(segs[0][1]), x2: x(segs[segs.length - 1][0]), y1: 0, y2: 0, class: "tr-ghost" }, mg);
      segs.forEach(([s, e]) => {
        const x0 = x(s), w = Math.max(6, x(e) - x0);
        el("rect", { x: x0, y: -5.5, width: w, height: 11, rx: 3, fill: col, class: "tr-bar" }, mg);
      });
      if (a.tail) {
        el("line", { x1: x(a.end), x2: X_NOW, y1: 0, y2: 0, class: "tr-living tr-tail-line", stroke: col }, mg);
        const tt = el("text", { x: X_NOW + 6, y: 3.5, class: "tr-tail" }, mg);
        tt.textContent = a.tail;
      }
    }
    if (!isGroup) mg.addEventListener("click", () => selectTaxon(id));
  });

  g.dataset.x0 = Math.min(...r.ids.map(id => x(TAXA[id].start))).toFixed(1);
  // label
  const a0 = TAXA[r.ids[0]];
  const grp = r.g;
  const lab = el("g", { class: "tr-label", tabindex: 0, role: "button" }, g);
  let lx, anchor = "start", ly = 4;
  if (!isGroup && a0.labelAt === "start") { lx = x(a0.start) + 2; ly = -7; }
  else if (!isGroup && a0.tail) lx = x(a0.end) + 8;
  else lx = barEnd(r) + (r.ids.some(id => TAXA[id].living) ? -150 : 8);
  if (!isGroup && a0.living) { lx = X_NOW + 8; }
  const t = el("text", { x: lx, y: ly, "text-anchor": anchor, class: "tr-text" + (a0.ghostOnly ? " tr-text-ghost" : "") }, lab);
  const num = grp.num && (isGroup || TAXA[r.ids[0]].stage === grp.stage || grp.members.length === 1) ? grp.num : 0;
  let html = num ? `<tspan class="tr-num">${num} ·</tspan> ` : "";
  if (isGroup) {
    const n = grp.members.length;
    const s0 = Math.max(...grp.members.map(m => TAXA[m].start)), s1 = Math.min(...grp.members.map(m => TAXA[m].end));
    html += `<tspan class="tr-name">${esc(grp.label)}</tspan><tspan class="tr-date" dx="7">${esc(span({ start: s0, end: s1 }))}</tspan>`
         + `<tspan class="tr-chip" dx="7">▸ ${grp.num ? `+${n - 1} more` : `${n} species`}</tspan>`;
    lab.setAttribute("aria-expanded", "false");
    lab.setAttribute("aria-label", `${grp.label}, ${n} species. Show all`);
    lab.addEventListener("click", () => toggleGroup(grp.id));
  } else {
    const name = grp.num && grp.members.length === 1 && grp.label !== a0.name ? grp.label : a0.name;
    html += `<tspan class="tr-name${isBinomial(a0) && name === a0.name ? " tr-ital" : ""}">${esc(name)}</tspan>`;
    if (a0.nick) html += `<tspan class="tr-nick" dx="5">${esc(a0.nick)}</tspan>`;
    const sp = span(a0);
    if (sp) html += `<tspan class="tr-date" dx="7">${esc(sp)}</tspan>`;
    lab.setAttribute("aria-label", `${a0.name}, ${sp}. Details`);
    lab.addEventListener("click", () => selectTaxon(r.ids[0]));
  }
  t.innerHTML = html;
  return g;
}

/* keep labels inside the chart: drop the nickname, then move the label to
   the left of the bars; and stop a tail line short of its label */
function fitRow(g) {
  const text = g.querySelector(".tr-label text");
  if (!text || text.classList.contains("tr-text-ghost")) return;
  let bb = text.getBBox();
  const limit = W - 6;
  if (bb.x + bb.width > limit) {
    const nick = text.querySelector(".tr-nick");
    if (nick) { nick.remove(); bb = text.getBBox(); }
  }
  if (bb.x + bb.width > limit && g.dataset.x0) {
    text.setAttribute("text-anchor", "end");
    text.setAttribute("x", (+g.dataset.x0 - 8).toFixed(1));
    bb = text.getBBox();
  }
  const tail = g.querySelector(".tr-tail-line");
  if (tail) tail.setAttribute("x1", Math.max(+tail.getAttribute("x1"), bb.x + bb.width + 6).toFixed(1));
}

/* ------------------------------------------------------------- render */
function render(animate) {
  const prev = new Map(rows.map(r => [r.key, r.y]));
  const res = computeRows();
  rows = res.rows; height = res.height;
  rowOfTaxon = {};
  rows.forEach(r => { if (r.ids) r.ids.forEach(id => rowOfTaxon[id] = r); });
  const H = height + AXIS;
  const oldH = +svg.getAttribute("viewBox").split(" ")[3];
  svg.setAttribute("viewBox", `0 0 ${W} ${Math.max(H, animate ? oldH : 0)}`);

  const live = new Set(rows.map(r => r.key));
  // remove rows that disappeared: slide them into their group row, then fade
  rowEls.forEach((elx, key) => {
    if (live.has(key)) return;
    const gid = (key.startsWith("t:") ? TAXA[key.slice(2)].group.id : key.slice(2));
    const dest = rows.find(r => r.key === "g:" + gid);
    if (dest && animate) elx.style.transform = `translate(0px, ${dest.y}px)`;
    elx.style.opacity = "0";
    setTimeout(() => elx.remove(), animate ? 380 : 0);
    rowEls.delete(key);
  });
  rows.forEach(r => {
    let g = rowEls.get(r.key);
    if (!g) {
      g = buildRow(r);
      const from = prev.get("g:" + r.g.id) ?? r.y;
      g.style.transform = `translate(0px, ${animate ? from : r.y}px)`;
      if (animate) g.style.opacity = "0";
      gRows.appendChild(g);
      rowEls.set(r.key, g);
      fitRow(g);
      if (animate) requestAnimationFrame(() => requestAnimationFrame(() => { g.style.opacity = ""; g.style.transform = `translate(0px, ${r.y}px)`; }));
    } else {
      g.style.transform = `translate(0px, ${r.y}px)`;
    }
  });
  // order the DOM so keyboard focus follows the rows
  rows.forEach(r => gRows.appendChild(rowEls.get(r.key)));

  const finish = () => {
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    drawGrid(); drawLinks(); drawFlow();
    MILESTONES.forEach(m => mileEls[m.id].querySelector("line").setAttribute("y2", height + 4));
    gLinks.style.opacity = gFlow.style.opacity = "1";
    applyClasses();
  };
  if (animate && !reduce) {
    gLinks.style.opacity = gFlow.style.opacity = "0";
    setTimeout(finish, 380);
  } else finish();
  applyClasses();
  syncButtons();
}

function drawGrid() {
  gGrid.innerHTML = "";
  gAxis.innerHTML = "";
  const yb = height + 8;
  [25, 20, 15, 10, 7, 5, 4, 3, 2, 1, 0.5, 0.2, 0].forEach(t => {
    el("line", { x1: x(t), x2: x(t), y1: TOP - 10, y2: yb, class: t === 7 ? "tr-grid-break" : "tr-grid-line" }, gGrid);
    el("line", { x1: x(t), x2: x(t), y1: yb, y2: yb + 5, class: "tr-tick" }, gAxis);
    const tx = el("text", { x: x(t), y: yb + 17, "text-anchor": "middle", class: "tr-axis-text" }, gAxis);
    tx.textContent = t === 0 ? "now" : String(t);
  });
  el("line", { x1: x(25), x2: X_NOW, y1: yb, y2: yb, class: "tr-axis-line" }, gAxis);
  const cap = el("text", { x: X_NOW, y: yb + 36, "text-anchor": "end", class: "tr-axis-cap" }, gAxis);
  cap.textContent = "millions of years ago · scale stretched toward the present";
  const cap2 = el("text", { x: x(25), y: yb + 36, class: "tr-axis-cap" }, gAxis);
  cap2.textContent = "← compressed before 7 mya";
}

function linkList() {
  const best = new Map();
  Object.keys(TAXA).forEach(id => {
    const a = TAXA[id];
    if (!a.parent) return;
    const [p, tb, style] = a.parent;
    const rp = rowOfTaxon[p], rc = rowOfTaxon[id];
    if (!rp || !rc || rp === rc) return;
    const key = rp.key + ">" + rc.key;
    const cur = best.get(key);
    if (!cur || tb > cur.tb) best.set(key, { key, rp, rc, tb, style, child: id });
  });
  return [...best.values()];
}

function drawLinks() {
  gLinks.innerHTML = "";
  linkList().forEach(L => {
    const xb = x(L.tb), y1 = L.rp.y, y2 = L.rc.y, xc = x(TAXA[L.child].start);
    const r = Math.min(7, Math.abs(y2 - y1) / 2), dir = y2 > y1 ? 1 : -1;
    let d = `M${xb.toFixed(1)},${y1} V${(y2 - dir * r).toFixed(1)}`;
    if (xc > xb + r) d += ` Q${xb.toFixed(1)},${y2} ${(xb + r).toFixed(1)},${y2} H${xc.toFixed(1)}`;
    else d += ` V${y2}`;
    el("path", { d, class: `tr-link tr-${L.style}`, "data-key": L.key }, gLinks);
  });
}

function drawFlow() {
  gFlow.innerHTML = "";
  GENEFLOW.forEach(f => {
    const ra = rowOfTaxon[f.from], rb = rowOfTaxon[f.to];
    if (!ra || !rb || ra === rb) return;
    const xx = x(f.t), dir = rb.y > ra.y ? 1 : -1;
    const attrs = { x1: xx, x2: xx, y1: ra.y + dir * 6, y2: rb.y - dir * 7, class: "tr-flow-line", "marker-end": "url(#tr-arrow)" };
    if (f.both) attrs["marker-start"] = "url(#tr-arrow)";
    el("line", attrs, gFlow);
  });
}

/* ------------------------------------------------------------- highlighting */
function ancestry(id) {
  const chain = [];
  let cur = id;
  while (cur && TAXA[cur] && chain.length < 30) { chain.push(cur); cur = TAXA[cur].parent ? TAXA[cur].parent[0] : null; }
  return chain;
}

function applyClasses() {
  const onRows = new Set(), onLinks = new Set(), selRows = new Set(), litRows = new Set();
  if (selected && !selected.startsWith("g:")) {
    const chain = ancestry(selected).map(id => rowOfTaxon[id]).filter(Boolean);
    chain.forEach(r => onRows.add(r.key));
    for (let i = 0; i + 1 < chain.length; i++) onLinks.add(chain[i + 1].key + ">" + chain[i].key);
    const r = rowOfTaxon[selected]; if (r) selRows.add(r.key);
  } else if (selected) selRows.add(selected);
  if (stageHL && !focus) rows.forEach(r => {
    if ((r.type === "group" || r.type === "taxon") && (r.g.stage === stageHL) &&
        (r.type === "group" || r.g.members.length === 1 || TAXA[r.ids[0]].stage === stageHL)) litRows.add(r.key);
  });
  if (focus) rows.forEach(r => { if (r.ids && r.ids.some(id => focus.taxa.has(id))) litRows.add(r.key); });
  svg.classList.toggle("tr-focusing", !!focus);
  rowEls.forEach((g, key) => {
    g.classList.toggle("on-path", onRows.has(key));
    g.classList.toggle("is-selected", selRows.has(key));
    g.classList.toggle("is-lit", litRows.has(key));
  });
  gLinks.querySelectorAll(".tr-link").forEach(p => p.classList.toggle("on-path", onLinks.has(p.dataset.key)));
  MILESTONES.forEach(m => mileEls[m.id].classList.toggle("is-lit", !!(focus && focus.milestones.has(m.id))));
}

/* ------------------------------------------------------------- actions */
function toggleGroup(id) {
  if (expanded.has(id)) expanded.delete(id); else expanded.add(id);
  if (selected === "g:" + id) selected = null;
  render(true);
  if (expanded.has(id)) showGroup(id);
  // keep keyboard focus on the toggled group
  setTimeout(() => {
    const key = expanded.has(id) ? "h:" + id : "g:" + id;
    const g = rowEls.get(key);
    const lab = g && g.querySelector(".tr-label");
    if (lab && document.activeElement && host.contains(document.activeElement)) lab.focus({ preventScroll: true });
  }, reduce ? 0 : 400);
}
function setAll(open) {
  GROUPS.forEach(g => { if (g.members.length > 1) { if (open) expanded.add(g.id); else expanded.delete(g.id); } });
  render(true);
}
function selectTaxon(id) {
  selected = id;
  focus = null;
  applyClasses();
  showTaxon(id);
  document.querySelectorAll("#treeLeaps .leap").forEach(c => c.classList.remove("on"));
}

/* ------------------------------------------------------------- detail card */
const card = document.getElementById("treeCard");
function showIntro() {
  if (!card) return;
  card.innerHTML = `<p class="tc-intro">Click any branch to read about it. Numbered rows are the seven stages of the syllabus; <b>▸</b> opens the species grouped inside a row.</p>`;
}
function showTaxon(id) {
  if (!card) return;
  const a = TAXA[id], col = KIND[a.kind].color;
  const chain = ancestry(id).slice(1).map(p => TAXA[p].name).reverse();
  const idx = a.stage ? stageIndex(a.stage) : -1;
  const style = a.parent ? a.parent[2] : null;
  card.innerHTML =
    `<div class="tc-head"><span class="tc-sw" style="background:${col}"></span>`
    + `<h3 class="${isBinomial(a) ? "tc-ital" : ""}">${esc(a.name)}</h3>${a.nick ? `<span class="tc-nick">${esc(a.nick)}</span>` : ""}`
    + `${a.group.num ? `<span class="tc-stage">syllabus stage ${a.group.num}</span>` : ""}</div>`
    + `<div class="tc-meta">${a.sci ? `<i>${esc(a.sci)}</i> · ` : ""}${esc(span(a) || "")}${a.where ? ` · ${esc(a.where)}` : ""}</div>`
    + `<p>${esc(a.shows)}</p>`
    + (a.mixing ? `<p>${esc(a.mixing)}</p>` : "")
    + `<dl class="tc-facts">`
    + (a.fossils ? `<div><dt>Key fossils</dt><dd>${esc(a.fossils)}</dd></div>` : "")
    + (a.brain ? `<div><dt>Brain size</dt><dd>${esc(a.brain)}</dd></div>` : "")
    + `<div><dt>Group</dt><dd>${esc(KIND[a.kind].label)}</dd></div></dl>`
    + (a.debate ? `<p class="tc-debate"><b>Debated:</b> ${esc(a.debate)}</p>` : "")
    + (a.syllabus ? `<p class="tc-debate"><b>Syllabus note:</b> ${esc(a.syllabus)}</p>` : "")
    + (chain.length ? `<p class="tc-path">Possible line of descent: ${chain.map(esc).join(" → ")} → <b>${esc(a.name)}</b>${style === "dashed" ? " <span>(the last link is debated)</span>" : ""}</p>` : "")
    + (idx >= 0 ? `<button type="button" class="tc-open" data-i="${idx}">See stage ${a.group.num} in 3D ↑</button>` : "");
  const b = card.querySelector(".tc-open");
  if (b) b.addEventListener("click", () => {
    if (typeof select === "function") select(+b.dataset.i);
    const life = document.getElementById("life");
    if (life) life.scrollIntoView({ behavior: reduce ? "auto" : "smooth" });
  });
}
function showGroup(gid) {
  if (!card) return;
  const g = GROUP[gid];
  card.innerHTML = `<div class="tc-head"><h3>${esc(g.label)}</h3>${g.num ? `<span class="tc-stage">syllabus stage ${g.num}</span>` : ""}</div>`
    + `<p>${g.members.length} species in this group. Choose one:</p>`
    + `<div class="tc-members">${g.members.map(m => `<button type="button" data-id="${m}" class="${isBinomial(TAXA[m]) ? "tc-ital" : ""}">${esc(TAXA[m].name)}</button>`).join("")}</div>`;
  card.querySelectorAll(".tc-members button").forEach(b => b.addEventListener("click", () => selectTaxon(b.dataset.id)));
}

/* ------------------------------------------------------------- controls, legend, leaps */
const bSimple = document.getElementById("treeSimple"), bAll = document.getElementById("treeAll");
function syncButtons() {
  const multi = GROUPS.filter(g => g.members.length > 1);
  const all = multi.every(g => expanded.has(g.id)), none = multi.every(g => !expanded.has(g.id));
  if (bSimple) bSimple.setAttribute("aria-pressed", String(none));
  if (bAll) bAll.setAttribute("aria-pressed", String(all));
}
if (bSimple) bSimple.addEventListener("click", () => { focus = null; setAll(false); });
if (bAll) bAll.addEventListener("click", () => setAll(true));

const legend = document.getElementById("treeLegend");
if (legend) {
  legend.innerHTML = Object.values(KIND).map(k => `<span><i class="lg-sw" style="background:${k.color}"></i>${esc(k.label)}</span>`).join("")
    + `<span><i class="lg-ln"></i>accepted descent</span><span><i class="lg-ln lg-dash"></i>debated link</span>`
    + `<span><i class="lg-ln lg-dot"></i>no fossils yet</span><span><i class="lg-flow"></i>interbreeding</span>`;
}

const leapsBox = document.getElementById("treeLeaps");
if (leapsBox) {
  LEAPS.forEach((L, i) => {
    const c = document.createElement("article");
    c.className = "leap";
    c.innerHTML = `<div class="leap-when">${esc(L.when)}</div><h4>${esc(L.title)}</h4><p>${esc(L.text)}</p>`
      + `<button type="button">Show on the tree ↑</button>`;
    c.querySelector("button").addEventListener("click", () => {
      L.taxa.forEach(id => { const g = TAXA[id].group; if (g.members.length > 1) expanded.add(g.id); });
      focus = { taxa: new Set(L.taxa), milestones: new Set(L.milestones) };
      selected = null;
      render(true);
      leapsBox.querySelectorAll(".leap").forEach(x2 => x2.classList.toggle("on", x2 === c));
      if (card) card.innerHTML = `<div class="tc-head"><h3>${esc(L.title)}</h3><span class="tc-stage">${esc(L.when)}</span></div><p>${esc(L.text)}</p>`
        + `<p class="tc-path">Highlighted: ${L.taxa.map(id => esc(TAXA[id].name)).join(", ")}.</p>`;
      const sec = document.getElementById("tree");
      if (sec) host.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
    });
    leapsBox.appendChild(c);
  });
}

/* keyboard: Enter / Space activate focused labels */
host.addEventListener("keydown", e => {
  const lab = e.target.closest && e.target.closest(".tr-label");
  if (!lab) return;
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); lab.dispatchEvent(new MouseEvent("click", { bubbles: true })); }
});

/* the rest of the page tells the tree which stage is selected */
window.updateTree = function (s) {
  stageHL = s && s.id;
  applyClasses();
};

render(false);
showIntro();
if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => rowEls.forEach(fitRow));
if (typeof SPECIES !== "undefined" && typeof current === "number") window.updateTree(SPECIES[current]);
})();
