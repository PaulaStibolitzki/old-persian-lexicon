import xml.etree.ElementTree as ET
import json
import re
import html

NS = {"tei": "http://www.tei-c.org/ns/1.0"}

tree = ET.parse("C:/Users/paula/Documents/JMU/5/WB/Wörterbuch_Tolman_TEI.xml")
root = tree.getroot()

from itertools import product

def expand_optional_brackets(word):
    parts = re.split(r'(\[.*?\])', word)

    options = []
    for part in parts:
        if part.startswith('[') and part.endswith(']'):
            inside = part[1:-1]
            options.append(['', inside])
        else:
            options.append([part])

    return [''.join(p) for p in product(*options)]

def generate_search_forms(lemma):
    lemma = lemma.strip()
    slash_parts = [p.strip() for p in lemma.split("/")]
    all_forms = []

    for part in slash_parts:
        bracket_forms = expand_optional_brackets(part)

        for form in bracket_forms:
            no_parens = re.sub(r"[()]", "", form)
            base = re.sub(r"\([^)]*\)", "", form)
            all_forms.extend([form, no_parens, base])
    return {f.lower() for f in all_forms if f}

entries = {}
index = {}

for entry in root.findall(".//tei:entry", NS):

    lemma_el = entry.find(".//tei:form[@type='lemma']/tei:orth", NS)
    lemma = lemma_el.text.strip() if lemma_el is not None and lemma_el.text else ""

    eid = entry.get("{http://www.w3.org/XML/1998/namespace}id") or lemma

    pos_el = entry.find(".//tei:pos", NS)
    pos = pos_el.text if pos_el is not None else ""

    gen_el = entry.find(".//tei:gen", NS)
    gender = gen_el.text if gen_el is not None else ""

    constructions = []
    for note in entry.findall(".//tei:note[@type='construction']", NS):
        if note.text:
            constructions.append(note.text.strip())

    defs = []
    for d in entry.findall(".//tei:def", NS):
        if d.text:
            defs.append(d.text.strip())

    definition = "; ".join(defs)
    search_forms = generate_search_forms(lemma)
    entries[eid] = {
      "id": eid,
      "lemma": lemma,
      "search_forms": list(search_forms),   
      "pos": pos,
      "gender": gender,
      "construction": constructions,
      "definition": definition
}

    text = lemma + " " + definition
    words = re.findall(r"\w+", text.lower())

    for w in words:
        index.setdefault(w, []).append(eid)

    for form in search_forms:
      tokens = re.findall(r"\w+", form)
      for t in tokens:
          index.setdefault(t, []).append(eid)

data = {"entries": entries, "index": index}
with open("C:/Users/paula/Documents/JMU/5/WB/index.json", "w", encoding="utf8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)