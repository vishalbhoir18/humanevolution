/* Life reconstructions in 3D + AR.
   Depends on: SPECIES / current / select() from index.html, HOMININ_MODELS
   from models/models.js, and the <model-viewer> element (vendor/). */
(function(){
"use strict";

/* ---------- What each model is built from, and what is guesswork ----------
   `fossils`  : specimen, where/when, what it contributes to the model
   `shows`    : what the bones establish
   `beyond`   : where current research differs from the syllabus table
   `notes`    : anatomy hotspots (keys match anchors in models/models.js)      */
const RECON = {
  dryo: {
    taxon: "Dryopithecine ape", sci: "Dryopithecus / Hispanopithecus",
    when: "Europe, about 12–9 million years ago",
    size: "about 39 kg; roughly 0.6 m at the back on all fours",
    fossils: [
      ["IPS 18800", "partial skeleton · Can Llobateres, Spain · 9.6 mya", "trunk, limbs and hand"],
      ["Rudabánya crania", "Hungary · about 10 mya", "small braincase and face"]
    ],
    shows: [
      "Broad, shallow chest and a short lower back, as in living apes",
      "No tail",
      "Long, curved fingers for hanging, with palms set flat when walking",
      "Arms longer than legs"
    ],
    assumed: "Exact arm-to-leg ratio (set close to a chimpanzee's), foot shape, and all soft tissue.",
    beyond: "The syllabus places Dryopithecus at 20–25 mya near Lake Victoria. Those East African fossils are now classified as Proconsul and Ekembo. Dryopithecus itself is European and younger, so the model follows the best-preserved dryopithecine skeleton.",
    notes: {
      braincase: ["Braincase", "Small and ape-sized. No measurement appears in the syllabus table; dryopithecine skulls from Hungary suggest a few hundred cc."],
      face: ["Jaws and teeth", "Projecting jaws with thin-enamelled teeth suited to soft fruit. Males carried large canines."],
      chest: ["Rib cage", "Broad and shallow, with the shoulder blades on the back: the ape body plan, already in place 9.6 million years ago."],
      hand: ["Hand", "Long, strongly curved fingers for hanging below branches. The same hand bones show the palm was placed flat on a support when walking, not on the knuckles."],
      pelvis: ["Lower back", "Short and fairly stiff, with no tail. Proconsul, older and from East Africa, still had a long, monkey-like back."],
      foot: ["Foot", "Drawn as a grasping foot with a big toe set apart, as in living apes. Dryopithecine feet are poorly known."]
    },
    refs: [
      "Moyà-Solà & Köhler 1996, Nature — A Dryopithecus skeleton and the origins of great-ape locomotion",
      "Almécija et al. 2007, Proc. R. Soc. B — Orang-like manual adaptations in Hispanopithecus laietanus",
      "Susanna et al. 2014, J. Hum. Evol. — Vertebral remains of Hispanopithecus laietanus"
    ]
  },

  rama: {
    taxon: "Sivapithecus", sci: "formerly “Ramapithecus”",
    when: "Siwalik Hills, about 12.5–8.5 million years ago",
    size: "a medium to large ape; about 0.6 m at the back on all fours",
    fossils: [
      ["GSP 15000", "partial skull · Potwar Plateau, Pakistan", "the face"],
      ["Siwalik limb bones", "two humeri and a hip bone (YGSP 41216, 12.3 mya)", "four-footed posture, narrow trunk"],
      ["Jaw fragments", "Haritalyangar and other Siwalik sites", "thick-enamelled teeth"]
    ],
    shows: [
      "An orangutan-like face: dished profile, tall eye sockets set close together",
      "Robust jaws with thick-enamelled molars",
      "A narrow trunk and curved upper-arm bones: it walked on four limbs above branches"
    ],
    assumed: "Arm-to-leg ratio (no skeleton preserves both), braincase size, body mass, and all soft tissue. The rufous coat is a nod to the orangutan-like face, nothing more.",
    beyond: "The syllabus calls Ramapithecus erect and man-like. That reading came from jaw fragments alone. After a face was found in Pakistan, Ramapithecus was merged into Sivapithecus, an ape related to orangutans, not a human ancestor, and its limb bones show it moved on all fours.",
    notes: {
      braincase: ["Braincase", "No complete braincase has been found. Its size here is scaled from the face and from apes of similar build."],
      brow: ["Eye region", "Tall, oval eye sockets set close together, with no continuous brow bar: the orangutan pattern."],
      face: ["Jaws and teeth", "Heavy jaws and thick-enamelled, low-cusped molars. These human-looking teeth are why early jaw fragments were once taken for a human ancestor."],
      chest: ["Trunk", "A hip bone from the Siwaliks indicates a narrow, monkey-like trunk rather than the broad chest of living apes."],
      arm: ["Upper arm", "The humerus shaft is curved like that of an animal walking on all fours, not straight like a hanging ape's."],
      foot: ["Foot", "Drawn as a grasping foot by comparison with other apes. No Sivapithecus foot is complete."]
    },
    refs: [
      "Pilbeam 1982, Nature — New hominoid skull material from the Miocene of Pakistan",
      "Richmond & Whalen 2001 — Forelimb function, bone curvature and phylogeny of Sivapithecus",
      "Morgan et al. 2014, PNAS — A partial hominoid innominate from the Miocene of Pakistan"
    ]
  },

  austra: {
    taxon: "Australopithecus", sci: "A. afarensis · A. africanus",
    when: "Africa, about 4–2 million years ago",
    size: "“Lucy”: about 1.05 m and under 30 kg. Males were much larger.",
    fossils: [
      ["AL 288-1 “Lucy”", "partial skeleton · Hadar, Ethiopia · 3.2 mya", "body size and limb proportions"],
      ["Sts 5 “Mrs Ples”, Taung child", "skulls · South Africa", "braincase and face"],
      ["Laetoli footprints", "Tanzania · about 3.7 mya", "upright stride"]
    ],
    shows: [
      "Walked upright: short, broad pelvis and thigh bones angled in to the knee",
      "Brain of about 450 cc, close to a chimpanzee's",
      "Arms of human length but short legs: humerus about 85% of femur length, against about 72% in us",
      "Curved fingers: climbing still mattered"
    ],
    assumed: "Skin colour, hair cover, nose, lips and ears. The ape-like coat is conventional, not evidence.",
    beyond: "The syllabus describes Australopithecus hunting with stone weapons. The oldest known stone tools are simple flakes and cores, and australopith teeth point to a mainly plant diet.",
    notes: {
      braincase: ["Braincase", "About 380–550 cc (450–600 cc in the syllabus table): roughly a third of ours, in a body that already walked upright. “A man with an ape's brain.”"],
      brow: ["Forehead", "Low and sloping behind modest brow ridges."],
      face: ["Jaws and teeth", "The lower face projects strongly. Chewing teeth are large, but the canines are far smaller than an ape's."],
      chin: ["Chin", "Absent: the front of the jaw slopes back."],
      arm: ["Arm and leg", "Lucy's humerus is about 85% the length of her femur. The arm is human-length; it is the leg that is short."],
      hand: ["Hand", "Finger bones are curved, a sign that climbing remained part of life."],
      pelvis: ["Pelvis", "Short, broad and bowl-shaped, unlike the tall, narrow pelvis of an ape. This is the clearest skeletal sign of upright walking."],
      knee: ["Knee", "The thigh bone angles inward from hip to knee, bringing the feet under the body."],
      foot: ["Foot", "The Laetoli footprints record a heel strike and a big toe in line with the other toes."]
    },
    refs: [
      "Jungers 1982, Nature — Lucy's limbs: skeletal allometry and locomotion in Australopithecus afarensis",
      "Haile-Selassie et al. 2010, PNAS — An early Australopithecus afarensis postcranium from Woranso-Mille",
      "Heaton et al. 2019, J. Hum. Evol. — The long limb bones of the StW 573 Australopithecus skeleton"
    ]
  },

  habilis: {
    taxon: "Homo habilis", sci: "“handy man”",
    when: "East Africa, about 2.4–1.4 million years ago",
    size: "about 1.0–1.35 m and 30–40 kg",
    fossils: [
      ["KNM-ER 1813", "skull · Koobi Fora, Kenya · 1.9 mya", "braincase and face"],
      ["OH 7, OH 8", "hand, jaw and foot · Olduvai Gorge, Tanzania", "the hand that named the species"],
      ["OH 62", "fragmentary skeleton · Olduvai Gorge", "small body size"]
    ],
    shows: [
      "A larger, rounder braincase than Australopithecus",
      "Smaller chewing teeth and a less projecting face",
      "A hand with a strong thumb, found with the earliest Olduvai stone tools",
      "An arched foot with the big toe in line"
    ],
    assumed: "Arm-to-leg ratio: OH 62 is too incomplete to settle it, so the model uses Lucy-like proportions. Body hair is drawn part-way between ape and human.",
    beyond: "The syllabus says Homo habilis probably did not eat meat. Cut-marked animal bones found with early stone tools show that toolmakers of this period butchered carcasses.",
    notes: {
      braincase: ["Braincase", "About 500–700 cc in the best-preserved skulls (650–800 cc in the syllabus table), clearly above Australopithecus."],
      brow: ["Brow", "A slight brow ridge above a forehead that begins to rise."],
      face: ["Jaws and teeth", "Lower jaw lightly built, molars smaller, the tooth row more like ours."],
      hand: ["Hand", "The OH 7 hand has a strong, mobile thumb suited to gripping stone, though the fingers stay curved."],
      arm: ["Arm and leg", "OH 62 hints at long arms and short legs, but the bones are too broken to measure with confidence."],
      foot: ["Foot", "The OH 8 foot is arched, with the big toe in line with the rest."]
    },
    refs: [
      "Richmond, Aiello & Wood 2002, J. Hum. Evol. — Early hominin limb proportions",
      "Jungers 2009 — Interlimb proportions in humans and fossil hominins"
    ]
  },

  erectus: {
    taxon: "Homo erectus", sci: "Java and Peking forms",
    when: "Africa and Asia, about 1.9 million to 110,000 years ago",
    size: "about 1.6–1.8 m and 50–65 kg as adults",
    fossils: [
      ["Sangiran 17, Trinil 2", "skulls · Java", "long, low braincase and brow bar"],
      ["Zhoukoudian skulls", "“Peking man” · China", "braincase of about 915–1,225 cc"],
      ["KNM-WT 15000", "“Turkana boy” skeleton · Kenya · 1.5 mya", "body proportions"]
    ],
    shows: [
      "Modern body proportions: long legs, shorter arms",
      "A long, low skull with a straight brow bar",
      "Brain of about 900–1,000 cc in the Asian skulls",
      "No chin; a projecting nose"
    ],
    assumed: "Skin and hair. Dark, mostly bare skin is argued from the heat-shedding build and from the age of pigmentation genes, not from fossils.",
    beyond: "The syllabus dates Homo erectus to 1.5 mya. The species lasted far longer, from about 1.9 million to roughly 110,000 years ago, and was the first human to leave Africa.",
    notes: {
      braincase: ["Braincase", "Long and low, widest near the base, with a slight keel along the top. About 900 cc in the syllabus table; 550–1,250 cc across the whole species."],
      brow: ["Brow ridge", "A straight, shelf-like bar of bone above the eyes with a groove behind it."],
      face: ["Jaws and teeth", "Massive jaws set forward of the brow, with large teeth."],
      chin: ["Chin", "Absent."],
      pelvis: ["Body build", "Tall and long-legged. In the Turkana boy the arm-to-leg ratio is essentially modern."],
      knee: ["Legs", "Long legs built for efficient walking and running over open ground."],
      foot: ["Foot", "Footprints at Ileret, Kenya (about 1.5 mya) show an arch and a modern-style stride."]
    },
    refs: [
      "Richmond, Aiello & Wood 2002, J. Hum. Evol. — Early hominin limb proportions",
      "Jungers 2009 — Interlimb proportions in humans and fossil hominins"
    ]
  },

  neander: {
    taxon: "Neanderthal", sci: "Homo neanderthalensis",
    when: "Europe and western Asia, about 400,000–40,000 years ago",
    size: "men about 1.65 m and 75–80 kg",
    fossils: [
      ["La Ferrassie 1", "skeleton · France", "skull and body build"],
      ["La Chapelle-aux-Saints 1", "skeleton · France", "skull"],
      ["Neanderthal 1", "Neander Valley, Germany · found 1856", "the type specimen"]
    ],
    shows: [
      "A very large brain: about 1,450 cc on average",
      "Long, low skull with a bulge at the back and a double-arched brow",
      "Mid-face pulled forward around a large nose; no projecting chin",
      "Wide chest and hips, short forearms and shins: a heavy, heat-saving build"
    ],
    assumed: "Skin and hair colour varied. One pigment-gene variant found in two individuals would give pale skin and reddish hair, the option shown here. The hide wrap is inferred from scraping tools and climate; no garment survives.",
    beyond: "The syllabus gives 100,000–40,000 years ago. Neanderthal features appear in European fossils from about 400,000 years ago. People alive today outside Africa carry a small share of Neanderthal DNA.",
    notes: {
      braincase: ["Braincase", "Long and low yet very large: 1,200–1,750 cc, averaging about 1,450 cc (1,400 cc in the syllabus table). The back bulges into an “occipital bun”."],
      brow: ["Brow ridge", "Prominent and double-arched, one arch over each eye."],
      face: ["Mid-face", "The whole middle of the face is drawn forward around a very large nasal opening. The forehead is low."],
      chin: ["Chin", "The jaw is deep but lacks a projecting chin."],
      chest: ["Rib cage", "Wide and deep, on a broad pelvis: a stocky trunk that holds heat."],
      arm: ["Forearm and shin", "Short relative to the upper arm and thigh, the pattern seen in cold-adapted people today."],
      knee: ["Limb bones", "Thick-walled and bowed, with large joints. The syllabus notes the outward-curved thigh bones."]
    },
    refs: [
      "Lalueza-Fox et al. 2007, Science — A melanocortin 1 receptor allele suggests varying pigmentation among Neanderthals"
    ]
  },

  sapiens: {
    taxon: "Homo sapiens", sci: "modern human",
    when: "Africa from about 300,000 years ago, then worldwide",
    size: "early modern men about 1.7–1.8 m",
    fossils: [
      ["Jebel Irhoud", "skulls · Morocco · about 300,000 years", "oldest fossils of our species"],
      ["Omo Kibish, Herto", "skulls · Ethiopia", "early modern anatomy"],
      ["Cro-Magnon 1", "skull · France · about 30,000 years", "the “after” skull on this page"]
    ],
    shows: [
      "Tall, rounded braincase over a small face",
      "A vertical forehead and reduced brow ridges",
      "A projecting bony chin, found in no other human",
      "A light, long-legged skeleton"
    ],
    assumed: "Hair form and beard. Dark skin follows ancient DNA: early modern humans, including a European hunter-gatherer who lived only about 7,000 years ago, carried the ancestral gene variants for dark pigmentation.",
    beyond: "The syllabus places the origin in the Ice Age, 75,000–10,000 years ago. The oldest Homo sapiens fossils are about 300,000 years old. Biologists now describe human diversity as gradual geographic variation rather than distinct races.",
    notes: {
      braincase: ["Braincase", "High and globe-shaped. About 1,350 cc on average today (1,450 cc in the syllabus table; Cro-Magnon 1 held about 1,600 cc)."],
      brow: ["Forehead", "Nearly vertical, with only slight brow ridges."],
      face: ["Face", "Small and tucked beneath the front of the braincase."],
      chin: ["Chin", "A true bony chin projects at the front of the jaw. No other human species has one."],
      pelvis: ["Hips", "Narrow hips and a light frame on long legs."],
      hand: ["Hand", "A long thumb and fine grip: by 18,000 years ago these hands were painting cave walls."]
    },
    refs: [
      "Hublin et al. 2017, Nature — New fossils from Jebel Irhoud, Morocco and the pan-African origin of Homo sapiens",
      "Olalde et al. 2014, Nature — Derived immune and ancestral pigmentation alleles in a 7,000-year-old Mesolithic European"
    ]
  }
};

const ORDER = ["braincase","brow","face","chin","shoulder","chest","arm","hand","pelvis","knee","foot"];
const MODELS = (window.HOMININ_MODELS || []).reduce((m, x) => (m[x.id] = x, m), {});
const $ = id => document.getElementById(id);
const mv = $("mv");
const stage = $("lifeStage");
if (!mv || !stage) return;

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let state = { id: null, anim: reduce ? "Rest" : "Idle", anatomy: false, view: "body", spin: false, active: null };

function esc(s){ return String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }
function metres(v){ return v.toFixed(2) + " m"; }

/* ---------- evidence panel ---------- */
function renderEvidence(s){
  const r = RECON[s.id], m = MODELS[s.id];
  $("lifeName").textContent = r.taxon;
  $("lifeSci").textContent = r.sci;
  $("lifeWhen").textContent = r.when;
  $("evFossils").innerHTML = r.fossils.map(f =>
    `<li><b>${esc(f[0])}</b><span>${esc(f[1])}</span><em>${esc(f[2])}</em></li>`).join("");
  $("evShows").innerHTML = r.shows.map(t => `<li>${esc(t)}</li>`).join("");
  $("evAssumed").textContent = r.assumed;
  $("evBeyond").textContent = r.beyond;
  $("evRefs").innerHTML = r.refs.map(t => `<li>${esc(t)}</li>`).join("");
  let facts = `<div><dt>In life</dt><dd>${esc(r.size)}</dd></div>`;
  if (m){
    facts += `<div><dt>Model height</dt><dd>${metres(m.height_m)}${m.stance==="quadruped" ? " on all fours" : ""}</dd></div>`;
    facts += `<div><dt>Head length</dt><dd>${m.head_length_cm.toFixed(1)} cm</dd></div>`;
    const hf = m.limb_ratio_vs_modern.humerofemoral;
    facts += `<div><dt>Arm : leg</dt><dd>${hf > 1.05 ? "arms " + Math.round((hf-1)*100) + "% longer for their legs than ours" : "as in living people"}</dd></div>`;
  }
  $("lifeFacts").innerHTML = facts;
}

/* ---------- hotspots ---------- */
function clearHotspots(){
  mv.querySelectorAll("[slot^='hotspot-']").forEach(n => n.remove());
  $("hsList").innerHTML = "";
  showNote(null);
}
function buildHotspots(s){
  clearHotspots();
  const r = RECON[s.id], m = MODELS[s.id];
  if (!m) return;
  let n = 0;
  ORDER.forEach(key => {
    if (!r.notes[key] || !m.hotspots[key]) return;
    n++;
    const h = m.hotspots[key];
    const b = document.createElement("button");
    b.className = "hs";
    b.slot = "hotspot-" + key;
    b.dataset.position = h.position.map(v => v + "m").join(" ");
    b.dataset.normal = h.normal.join(" ");
    b.dataset.visibilityAttribute = "visible";
    b.dataset.key = key;
    b.textContent = n;
    b.setAttribute("aria-label", r.notes[key][0]);
    b.addEventListener("click", e => { e.stopPropagation(); showNote(key); });
    mv.appendChild(b);
    const li = document.createElement("li");
    li.innerHTML = `<button type="button" data-key="${key}"><i>${n}</i>${esc(r.notes[key][0])}</button>`;
    li.firstChild.addEventListener("click", () => showNote(key));
    $("hsList").appendChild(li);
  });
}
function showNote(key){
  state.active = key;
  const note = $("hsNote");
  mv.querySelectorAll(".hs").forEach(b => b.classList.toggle("on", b.dataset.key === key));
  $("hsList").querySelectorAll("button").forEach(b => b.classList.toggle("on", b.dataset.key === key));
  if (!key){ note.hidden = true; return; }
  const r = RECON[state.id];
  $("hsTitle").textContent = r.notes[key][0];
  $("hsText").textContent = r.notes[key][1];
  note.hidden = false;
}

/* ---------- viewer state ---------- */
let ready = false;                       // true once <model-viewer> is defined
function applyAnim(){
  const name = state.anatomy ? "Rest" : state.anim;
  mv.setAttribute("animation-name", name);
  if (ready){
    if (name === "Rest" || (reduce && name !== "Walk")){ mv.pause(); try{ mv.currentTime = 0; }catch(e){} }
    else mv.play({ repetitions: Infinity });
  }
  // while the anatomy notes are open the figure holds still, so neither movement button is "on"
  document.querySelectorAll("[data-anim]").forEach(b => b.setAttribute("aria-pressed", String(!state.anatomy && b.dataset.anim === state.anim)));
}
function applyView(animate){
  const m = MODELS[state.id];
  if (!m) return;
  if (state.view === "head"){
    const a = m.hotspots.brow.position, c = m.hotspots.braincase.position, ch = m.hotspots.chin.position;
    const L = m.head_length_cm / 100;
    const t = [0, (ch[1] + c[1]) / 2, (a[2] + c[2]) / 2 - L * 0.2];
    mv.setAttribute("camera-target", t.map(v => v.toFixed(3) + "m").join(" "));
    mv.setAttribute("field-of-view", "26deg");
    mv.setAttribute("camera-orbit", `-32deg 82deg ${(L * 4.4).toFixed(2)}m`);
  } else {
    mv.setAttribute("field-of-view", "auto");
    mv.setAttribute("camera-target", "auto auto auto");
    mv.setAttribute("camera-orbit", (m.stance === "quadruped" ? "-52deg 76deg" : "-28deg 82deg") + " 108%");
  }
  if (!animate && ready && mv.jumpCameraToGoal) mv.jumpCameraToGoal();
  document.querySelectorAll("[data-view]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.view === state.view)));
}
function applyAnatomy(){
  stage.classList.toggle("anatomy", state.anatomy);
  $("btnAnatomy").setAttribute("aria-pressed", String(state.anatomy));
  $("hsPanel").hidden = !state.anatomy;
  if (!state.anatomy) showNote(null);
  applyAnim();
}
function applySpin(){
  if (state.spin && !state.anatomy) mv.setAttribute("auto-rotate", ""); else mv.removeAttribute("auto-rotate");
  $("btnSpin").setAttribute("aria-pressed", String(state.spin));
}

window.updateLife = function(s){
  if (!s || !RECON[s.id]) return;
  const changed = state.id !== s.id;
  state.id = s.id;
  renderEvidence(s);
  document.querySelectorAll("#lineup button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.id === s.id)));
  if (!changed) return;
  const m = MODELS[s.id];
  if (!m){ stage.classList.add("nomodel"); return; }
  state.view = "body";
  stage.classList.remove("loaded");
  $("mvPoster").src = m.poster;
  $("mvPoster").alt = RECON[s.id].taxon + ", life reconstruction";
  mv.setAttribute("alt", `3D life reconstruction of ${RECON[s.id].taxon}: ${RECON[s.id].size}.`);
  mv.setAttribute("src", m.file);
  buildHotspots(s);
  applyView(false);
  $("scaleChip").textContent = (m.stance === "quadruped" ? metres(m.height_m) + " at the back" : metres(m.height_m) + " tall") + " · shown life-size in AR";
};

mv.addEventListener("load", () => {
  stage.classList.add("loaded");
  applyAnim(); applyView(false); applySpin();
  const ok = !!mv.canActivateAR;
  $("arHint").textContent = ok
    ? "Tap “View life-size in your space”, then point the camera at the floor. On iPhone and iPad the AR figure stands still; on Android it moves."
    : "Life-size AR needs a phone or tablet: open this page in Chrome on Android or Safari on iPhone and iPad, then tap “View life-size in your space”.";
});
mv.addEventListener("error", () => { stage.classList.add("failed"); });
mv.addEventListener("progress", e => {
  const p = e.detail.totalProgress;
  $("mvBar").style.width = Math.round(p * 100) + "%";
  $("mvProg").hidden = p >= 1;
});
mv.addEventListener("ar-status", e => {
  if (e.detail.status === "failed") { $("arHint").hidden = false; $("arHint").textContent = "AR could not start on this device. The 3D view still works."; }
});

document.querySelectorAll("[data-anim]").forEach(b => b.addEventListener("click", () => {
  state.anim = b.dataset.anim;
  if (state.anatomy){ state.anatomy = false; applyAnatomy(); } else applyAnim();
}));
document.querySelectorAll("[data-view]").forEach(b => b.addEventListener("click", () => { state.view = b.dataset.view; applyView(true); }));
$("btnAnatomy").addEventListener("click", () => { state.anatomy = !state.anatomy; applyAnatomy(); applySpin(); });
$("btnSpin").addEventListener("click", () => { state.spin = !state.spin; applySpin(); });
$("hsClose").addEventListener("click", () => showNote(null));

/* ---------- to-scale line-up ---------- */
(function lineup(){
  const box = $("lineup");
  if (!box || !window.HOMININ_MODELS) return;
  const ppm = 86;                       // CSS px per metre at full size; the strip scales with --ppm
  window.HOMININ_MODELS.forEach(m => {
    const sp = SPECIES.findIndex(s => s.id === m.id);
    if (sp < 0) return;
    const b = document.createElement("button");
    b.type = "button"; b.dataset.id = m.id;
    b.setAttribute("aria-pressed", "false");
    b.style.setProperty("--h", m.poster_extent_m.toFixed(3));
    b.innerHTML = `<img src="${m.poster}" alt="" loading="lazy"><span>${esc(RECON[m.id].taxon)}</span><small>${metres(m.height_m)}</small>`;
    b.addEventListener("click", () => select(sp));
    box.appendChild(b);
  });
})();

if (!window.customElements || !Object.keys(MODELS).length) stage.classList.add("nomodel");
else customElements.whenDefined("model-viewer").then(() => { ready = true; if (mv.loaded) { applyAnim(); applyView(false); } });
if (location.protocol === "file:") stage.classList.add("failed");
if (typeof SPECIES !== "undefined") window.updateLife(SPECIES[typeof current === "number" ? current : 0]);
})();
