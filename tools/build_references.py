#!/usr/bin/env python3
"""Build the APA 7 reference list at the end of index.html.

Journal articles are listed by DOI and their details (authors, year, title,
journal, volume, issue, pages) come from Crossref, so they match the
publisher's record.  A few Crossref records are incomplete; those fields are
corrected in FIX below.  Software, data and web sources are in OTHER.

    python tools/build_references.py          # fetches Crossref, caches in tools/.cache/
    python tools/build_references.py --check  # print the plain-text list only

The list is written between <!-- REFERENCES:BEGIN --> and <!-- REFERENCES:END -->.
"""
import html
import json
import os
import re
import ssl
import sys
import time
import unicodedata
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CACHE = os.path.join(HERE, ".cache", "crossref.json")
PAGE = os.path.join(REPO, "index.html")

# What each source supports on the site, by DOI.
DOIS = [
    # Miocene apes
    "10.1016/j.jhevol.2015.03.009",   # McNulty 2015, Proconsul and Ekembo
    "10.1038/379156a0",               # Moyà-Solà & Köhler 1996, Dryopithecus skeleton
    "10.1098/rspb.2007.0750",         # Almécija 2007, Hispanopithecus hand
    "10.1016/j.jhevol.2014.05.009",   # Susanna 2014, Hispanopithecus vertebrae
    "10.1006/jhev.2001.0523",         # Kordos & Begun 2001, Rudabánya cranium
    "10.1038/295232a0",               # Pilbeam 1982, Sivapithecus face
    "10.1017/cbo9780511600449.015",   # Richmond & Whalen 2001, Sivapithecus forelimb
    "10.1073/pnas.1420275111",        # Morgan 2015, Sivapithecus innominate
    "10.1016/j.jhevol.2022.103309",   # Urciuoli & Alba 2023, Miocene ape systematics
    "10.1038/nature06113",            # Suwa 2007, Chororapithecus
    "10.1038/nature04008",            # McBrearty & Jablonski 2005, fossil chimpanzee
    "10.1073/pnas.1211740109",        # Langergraber 2012, ape divergence times
    # earliest hominins
    "10.1038/nature00879",            # Brunet 2002, Sahelanthropus
    "10.1016/s1251-8050(01)01529-4",  # Senut 2001, Orrorin
    "10.1126/science.1092978",        # Haile-Selassie 2004, Ardipithecus kadabba
    "10.1126/science.1175802",        # White 2009, Ardipithecus ramidus
    # australopiths
    "10.1038/376565a0",               # Leakey 1995, A. anamensis
    "10.1038/s41586-019-1513-8",      # Haile-Selassie 2019, MRD cranium
    "10.1126/science.104384",         # Johanson & White 1979, A. afarensis
    "10.1038/297676a0",               # Jungers 1982, Lucy's limbs
    "10.1073/pnas.1004527107",        # Haile-Selassie 2010, Woranso-Mille skeleton
    "10.1038/278317a0",               # Leakey & Hay 1979, Laetoli footprints
    "10.1038/nature05047",            # Alemseged 2006, Dikika child
    "10.1038/35068500",               # Leakey 2001, Kenyanthropus
    "10.1038/nature14464",            # Harmand 2015, Lomekwi stone tools
    "10.1038/115195a0",               # Dart 1925, Taung child
    "10.1038/nature14268",            # Granger 2015, Little Foot age
    "10.1016/j.jhevol.2019.05.015",   # Heaton 2019, Little Foot limbs
    "10.1126/science.1184944",        # Berger 2010, A. sediba
    "10.1126/science.284.5414.629",   # Asfaw 1999, A. garhi
    "10.1016/s0047-2484(02)90594-4",  # Richmond 2002, limb proportions
    "10.1007/978-1-4020-9980-9_9",    # Jungers 2009, interlimb proportions
    # robust australopiths
    "10.1038/322517a0",               # Walker 1986, Black Skull
    "10.1038/184491a0",               # Leakey 1959, Zinj
    "10.1073/pnas.1104627108",        # Cerling 2011, P. boisei diet
    "10.1126/science.aaw7293",        # Herries 2020, Drimolen ages
    # early Homo and H. erectus
    "10.1126/science.aaa1343",        # Villmoare 2015, LD 350-1
    "10.1038/202007a0",               # Leakey, Tobias & Napier 1964, H. habilis
    "10.1038/nature14224",            # Spoor 2015, OH 7
    "10.1038/nature11322",            # Leakey 2012, Koobi Fora early Homo
    "10.1038/316788a0",               # Brown 1985, Turkana Boy
    "10.1126/science.1238484",        # Lordkipanidze 2013, Dmanisi
    "10.1038/nature10372",            # Lepre 2011, Acheulean origin
    "10.1073/pnas.1117620109",        # Berna 2012, Wonderwerk fire
    "10.1038/s41586-019-1863-2",      # Rizal 2020, last H. erectus
    # later Homo
    "10.1038/s41586-020-2153-8",      # Welker 2020, H. antecessor proteome
    "10.7554/eLife.09560",            # Berger 2015, H. naledi
    "10.7554/eLife.24231",            # Dirks 2017, H. naledi age
    "10.1038/nature02999",            # Brown 2004, H. floresiensis
    "10.1038/nature17179",            # Sutikna 2016, Liang Bua chronology
    "10.1038/nature17999",            # van den Bergh 2016, Mata Menge
    "10.1038/s41586-019-1067-9",      # Détroit 2019, H. luzonensis
    "10.1016/j.quascirev.2023.108379",  # Grün & Stringer 2023, direct dating
    "10.1002/evan.21929",             # Roksandic 2022, H. bodoensis
    "10.1002/ajpa.22902",             # Wood & Boyle 2016, taxic diversity
    "10.1126/science.1253958",        # Arsuaga 2014, Sima de los Huesos
    "10.1038/nature17405",            # Meyer 2016, Sima de los Huesos DNA
    # ancient DNA and proteins
    "10.1126/science.1188021",        # Green 2010, Neandertal genome
    "10.1038/nature08976",            # Krause 2010, Denisova mtDNA
    "10.1038/nature09710",            # Reich 2010, Denisovan genome
    "10.1038/s41586-019-1139-x",      # Chen 2019, Xiahe mandible
    "10.1016/j.cell.2025.05.040",     # Fu 2025, Harbin mtDNA
    "10.1126/science.adu9677",        # Fu 2025, Harbin proteome
    "10.1126/science.ads3888",        # Tsutaya 2025, Penghu mandible
    "10.1038/nature13408",            # Huerta-Sánchez 2014, EPAS1
    "10.1038/s41586-018-0455-x",      # Slon 2018, Denny
    "10.1126/science.1147417",        # Lalueza-Fox 2007, Neanderthal MC1R
    # Homo sapiens
    "10.1038/nature22336",            # Hublin 2017, Jebel Irhoud
    "10.1038/nature12960",            # Olalde 2014, La Braña pigmentation
]

# Corrections where the Crossref record is incomplete or its title is in Title Case.
FIX = {
    "10.1016/s0047-2484(02)90594-4": dict(authors=[("Richmond", "B. G."), ("Aiello", "L. C."), ("Wood", "B. A.")]),
    "10.1073/pnas.1117620109": dict(page="E1215-E1220"),
    "10.1002/ajpa.22902": dict(authors=[("Wood", "B."), ("Boyle", "E. K.")]),
    "10.1007/978-1-4020-9980-9_9": dict(
        title="Interlimb proportions in humans and fossil hominins: Variability and scaling",
        book="In F. E. Grine, J. G. Fleagle, &amp; R. E. Leakey (Eds.), <i>The first humans: Origin and early evolution of the genus Homo</i>"),
    "10.1017/cbo9780511600449.015": dict(
        title="Forelimb function, bone curvature and phylogeny of <i>Sivapithecus</i>",
        book="In L. de Bonis, G. D. Koufos, &amp; P. Andrews (Eds.), <i>Hominoid evolution and climatic change in Europe: Vol. 2. "
             "Phylogeny of the Neogene hominoid primates of Eurasia</i>"),
    "10.1098/rspb.2007.0750": dict(title="Orang-like manual adaptations in the fossil hominoid <i>Hispanopithecus laietanus</i>: First steps towards great ape suspensory behaviours"),
    "10.1038/297676a0": dict(title="Lucy's limbs: Skeletal allometry and locomotion in <i>Australopithecus afarensis</i>"),
    "10.1126/science.1147417": dict(title="A melanocortin 1 receptor allele suggests varying pigmentation among Neanderthals"),
    "10.1126/science.1092978": dict(title="Late Miocene teeth from Middle Awash, Ethiopia, and early hominid dental evolution"),
    "10.1126/science.1175802": dict(title="<i>Ardipithecus ramidus</i> and the paleobiology of early hominids"),
    "10.1126/science.104384": dict(title="A systematic assessment of early African hominids"),
    "10.1038/115195a0": dict(title="<i>Australopithecus africanus</i>: The man-ape of South Africa"),
    "10.1126/science.1184944": dict(title="<i>Australopithecus sediba</i>: A new species of <i>Homo</i>-like australopith from South Africa"),
    "10.1126/science.284.5414.629": dict(title="<i>Australopithecus garhi</i>: A new species of early hominid from Ethiopia"),
    "10.1038/184491a0": dict(title="A new fossil skull from Olduvai"),
    "10.1126/science.aaw7293": dict(title="Contemporaneity of <i>Australopithecus</i>, <i>Paranthropus</i>, and early <i>Homo erectus</i> in South Africa"),
    "10.1126/science.aaa1343": dict(title="Early <i>Homo</i> at 2.8 Ma from Ledi-Geraru, Afar, Ethiopia"),
    "10.1038/202007a0": dict(title="A new species of the genus <i>Homo</i> from Olduvai Gorge"),
    "10.1126/science.1238484": dict(title="A complete skull from Dmanisi, Georgia, and the evolutionary biology of early <i>Homo</i>"),
    "10.1126/science.1188021": dict(title="A draft sequence of the Neandertal genome"),
    "10.1002/evan.21929": dict(title="Resolving the “muddle in the middle”: The case for <i>Homo bodoensis</i> sp. nov."),
    "10.1016/j.cell.2025.05.040": dict(title="Denisovan mitochondrial DNA from dental calculus of the &gt;146,000-year-old Harbin cranium"),
}

# Software, data and web sources: (sort key, HTML)
OTHER = [
    ("blender", "Blender Foundation. (n.d.). <i>Blender</i> (Version 5.3) [Computer software]. "
                '<a href="https://www.blender.org/">https://www.blender.org/</a>'),
    ("bostock", "Bostock, M. (n.d.). <i>world-atlas</i> (Version 2.0.2) [Computer software]. "
                '<a href="https://github.com/topojson/world-atlas">https://github.com/topojson/world-atlas</a>'),
    ("bregier r 2026", "Brégier, R. (2026). <i>anny</i> (Version 0.6.2) [Computer software]. NAVER LABS Europe. "
                '<a href="https://pypi.org/project/anny/">https://pypi.org/project/anny/</a>'),
    ("google", "Google. (n.d.). <i>&lt;model-viewer&gt;</i> (Version 4.4.0) [Computer software]. "
               '<a href="https://modelviewer.dev/">https://modelviewer.dev/</a>'),
    ("makehuman", "MakeHuman Community. (2020). <i>MakeHuman base mesh hm08, morph targets and rigs</i> [Data set]. "
                  '<a href="http://www.makehumancommunity.org/">http://www.makehumancommunity.org/</a>'),
    ("natural earth", "Natural Earth. (n.d.). <i>1:50m cultural and physical vectors</i> (Version 4.1.0) [Data set]. "
                      '<a href="https://www.naturalearthdata.com/">https://www.naturalearthdata.com/</a>'),
    ("smithsonian", "Smithsonian Institution. (n.d.). <i>Human evolution evidence</i>. Smithsonian National Museum of Natural History, "
                    'Human Origins Program. <a href="https://humanorigins.si.edu/evidence">https://humanorigins.si.edu/evidence</a>'),
]

# names Crossref splits or spells differently from the published byline
NAME_FIX = {"de Castro, J. M. B.": "Bermúdez de Castro, J. M."}

GENERA = r"Australopithecus|Homo|Paranthropus|Ardipithecus|Hispanopithecus|Dryopithecus|Proconsul|Sivapithecus|Kenyanthropus|Sahelanthropus|Orrorin"
EPITHETS = r"afarensis|africanus|sediba|garhi|boisei|ramidus|sapiens|erectus|habilis|naledi|floresiensis|antecessor|laietanus|bodoensis|luzonensis"


def fetch(doi):
    ctx = ssl.create_default_context()
    if os.path.exists("/root/.ccr/ca-bundle.crt"):
        ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
    for attempt in range(4):
        try:
            req = urllib.request.Request("https://api.crossref.org/works/" + doi,
                                         headers={"User-Agent": "humanevolution-reference-list/1.0"})
            with urllib.request.urlopen(req, timeout=40, context=ctx) as r:
                return json.load(r)["message"]
        except Exception:
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("Crossref lookup failed for " + doi)


def load():
    cache = {}
    if os.path.exists(CACHE):
        with open(CACHE) as f:
            cache = json.load(f)
    changed = False
    for doi in DOIS:
        if doi.lower() not in cache:
            cache[doi.lower()] = fetch(doi)
            changed = True
            time.sleep(0.3)
    if changed:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, "w") as f:
            json.dump(cache, f)
    return cache


def initials(given):
    out = []
    for part in re.split(r"\s+", given.replace(".", ". ").strip()):
        if not part:
            continue
        if 1 < len(part) <= 3 and part.isalpha() and part.isupper():  # "HGM" -> H. G. M.
            out += [c + "." for c in part]
            continue
        sub = [s for s in part.split("-") if s]
        out.append("-".join(s[0].upper() + "." for s in sub))
    return " ".join(out)


def family(name):
    """Old records give surnames in capitals (DART): use normal case."""
    if name.isupper() and len(name) > 1:
        return "-".join(w.capitalize() for w in name.lower().split("-"))
    return name


def authors(m, fix):
    if "authors" in fix:
        names = [f"{fam}, {ini}" for fam, ini in fix["authors"]]
    else:
        names = []
        for a in m.get("author", []):
            if "family" in a:
                names.append(f"{family(a['family'])}, {initials(a.get('given', ''))}".rstrip(", "))
            elif "name" in a:
                names.append(a["name"])
    names = [html.escape(NAME_FIX.get(n, n)) for n in names]
    if len(names) == 1:
        return names[0], names
    if len(names) <= 20:
        return ", ".join(names[:-1]) + ", &amp; " + names[-1], names
    return ", ".join(names[:19]) + ", . . . " + names[-1], names


def italicise(t):
    return re.sub(rf"\b({GENERA})\b(\s(?:{EPITHETS})\b)?", lambda m: f"<i>{m.group(0)}</i>", t)


def year(m):
    for k in ("published-print", "published", "issued"):
        dp = (m.get(k) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]:
            return dp[0][0]
    return "n.d."


def entry(doi, m):
    fix = FIX.get(doi, {})
    auth, names = authors(m, fix)
    title = fix.get("title")
    if not title:
        title = re.sub(r"<[^>]+>", "", (m.get("title") or [""])[0])
        title = re.sub(r"\s+", " ", title).strip()
        title = italicise(html.escape(title, quote=False))
    url = f"https://doi.org/{m.get('DOI', doi)}"
    link = f'<a href="{url}">{url}</a>'
    page = (fix.get("page") or m.get("page") or "").replace("-", "–")
    if m.get("type") == "book-chapter":
        body = f"{title}. {fix['book']} (pp. {page}). {html.escape(m.get('publisher', ''))}. {link}"
    else:
        journal = html.escape((m.get("container-title") or [""])[0])
        vol = m.get("volume")
        iss = m.get("issue")
        art = m.get("article-number")
        loc = f"<i>{journal}</i>"
        if vol:
            loc += f", <i>{vol}</i>"
        if iss:
            loc += f"({iss})"
        if page and "–" not in page and (len(page) > 4 or page[0].isalpha()):
            art, page = page, ""
        if page:
            loc += f", {page}"
        elif art:
            loc += f", Article {art}"
        body = f"{title}. {loc}. {link}"
    body = re.sub(r"([.?!])\. ", r"\1 ", body, count=1)          # no doubled stop after a title ending in ? or .
    plain = lambda n: unicodedata.normalize("NFKD", html.unescape(n)).encode("ascii", "ignore").decode().lower()
    sortkey = " ".join(re.sub(r"[^a-z ]", "", plain(n).replace(",", " ")) for n in names) + f" {year(m)}"
    return sortkey, f"{auth} ({year(m)}). {body}"


def main(argv):
    cache = load()
    items = [entry(doi, cache[doi.lower()]) for doi in DOIS]
    items += [(k, v) for k, v in OTHER]
    items.sort(key=lambda kv: kv[0])
    if "--check" in argv:
        for _, h in items:
            print(html.unescape(re.sub(r"<[^>]+>", "", h)))
        return
    lis = "\n".join(f"        <li>{h}</li>" for _, h in items)
    with open(PAGE) as f:
        page = f.read()
    a = page.index("<!-- REFERENCES:BEGIN -->") + len("<!-- REFERENCES:BEGIN -->")
    b = page.index("<!-- REFERENCES:END -->")
    page = page[:a] + "\n" + lis + "\n        " + page[b:]
    page = re.sub(r'(<span class="ref-count" id="refCount">)\d*(</span>)', rf"\g<1>{len(items)}\2", page)
    with open(PAGE, "w") as f:
        f.write(page)
    print(f"wrote {len(items)} references into index.html")


if __name__ == "__main__":
    main(sys.argv[1:])
