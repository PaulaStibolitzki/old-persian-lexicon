import json

txt_path  = "C:/Users/paula/Documents/JMU/5/WB/Wortliste_Tolman.txt"
json_path = "C:/Users/paula/Documents/JMU/5/WB/Wörterbuch_Tolman.json"

with open(txt_path, encoding="utf8") as f:
    txt_set = {
        line.split("\t")[0].lstrip("*").strip()
        for line in f if line.strip()}

with open(json_path, encoding="utf8") as f:
    entries = json.load(f)

json_set = {e["lemma"] for e in entries}
missing_in_json = txt_set - json_set
extra_in_json   = json_set - txt_set

lemma_set = {e["lemma"] for e in entries}
search_form_set = {
    form for e in entries for form in e.get("search_forms", [])}

missing_pos = []
missing_pos_real = []
empty_senses = []
missing_definition = []
broken_crossrefs = []

for e in entries:
    lemma  = e["lemma"]
    pos    = e.get("morphology", {}).get("pos")
    senses = e.get("senses", [])

    if not pos:
        if "name of" in str(e).lower():
            missing_pos_real.append(lemma)
        else:
            missing_pos.append(lemma)

    if not senses and not e.get("is_cross_reference"):
        empty_senses.append(lemma)
    elif senses and not any(s.get("definition","").strip() for s in senses):
        missing_definition.append(lemma)

    if e.get("is_cross_reference"):
        target = e.get("see","").strip()
        if target not in lemma_set and target not in search_form_set:
            broken_crossrefs.append(f"{lemma} → {target}")

print("TXT lemmas:", len(txt_set))
print("JSON entries:", len(json_set))
print("Fehlende im JSON:", len(missing_in_json))
print("Zu viel im JSON:", len(extra_in_json))
print("Fehlende POS (echte Lücken):", len(missing_pos))
print("Eigennamen ohne POS:", len(missing_pos_real))
print("Keine Bedeutungen:", len(empty_senses))
print("Leere Bedeutungen:", len(missing_definition))
print("Falsche Verweise:", len(broken_crossrefs))