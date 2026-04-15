import json
import xml.etree.ElementTree as ET

json_input = "C:/Users/paula/Documents/JMU/5/WB/Wörterbuch_Tolman.json"
tei_output = "C:/Users/paula/Documents/JMU/5/WB/Wörterbuch_Tolman_TEI.xml"

NS = "http://www.tei-c.org/ns/1.0"
def tei(tag):
    return f"{{{NS}}}{tag}"

ET.register_namespace("", NS)

with open(json_input, encoding="utf-8") as f:
    entries = json.load(f)

root = ET.Element(tei("TEI"))
text_el = ET.SubElement(root, tei("text"))
body_el = ET.SubElement(text_el, tei("body"))

for e in entries:
    entry_el = ET.SubElement(body_el, tei("entry"))

    lemma_el = ET.SubElement(entry_el, tei("form"), {"type": "lemma"})
    ET.SubElement(lemma_el, tei("orth")).text = e["lemma"]

    if "morphology" in e:
        morph = e["morphology"]
        if morph.get("pos"):
            ET.SubElement(entry_el, tei("pos")).text = morph["pos"]
        if morph.get("gender"):
            ET.SubElement(entry_el, tei("gen")).text = morph["gender"]

    if e.get("variants"):
        for v in e["variants"]:
            variant_el = ET.SubElement(entry_el, tei("form"), {"type": "variant"})
            ET.SubElement(variant_el, tei("orth")).text = v

    for sense in e.get("senses", []):
        sense_el = ET.SubElement(entry_el, tei("sense"))
        c = sense.get("construction")

        if isinstance(c, dict):
            note = ET.SubElement(sense_el, tei("note"), {"type": "construction"})

            if c.get("type") == "with prefix":
                text = f'with prefix {c.get("value", "")}'

                if "alternation" in c:
                    alt = c["alternation"]
                    text += f' (before {alt.get("before")} → {alt.get("variant")})'

                if c.get("negation"):
                    text += " (neg.)"

                note.text = text

            elif c.get("type") == "with case":
                note.text = f'with {c.get("case")}'

        ET.SubElement(sense_el, tei("def")).text = sense.get("definition", "")

tree = ET.ElementTree(root)
tree.write(tei_output, encoding="utf-8", xml_declaration=True)