import json
import re

txt_path = "C:/Users/paula/Documents/JMU/5/WB/Wortliste_Tolman.txt"
json_path = "C:/Users/paula/Documents/JMU/5/WB/Wörterbuch_Tolman.json"

txt_lemmas = []

with open(txt_path, encoding="utf8") as f:
    for line in f:
        line = line.strip()

        if not line:
            continue

        # Lemma = erstes Feld bis TAB
        lemma = line.split("\t")[0].strip()

        # Sternchen entfernen etc.
        lemma = lemma.lstrip("*").strip()

        txt_lemmas.append(lemma)

txt_set = set(txt_lemmas)

print("TXT lemmas:", len(txt_set))
with open(json_path, encoding="utf8") as f:
    data = json.load(f)

json_lemmas = {entry["lemma"] for entry in data}

print("JSON entries:", len(json_lemmas))

missing_in_json = txt_set - json_lemmas
extra_in_json   = json_lemmas - txt_set

print("\nFehlen im JSON:", len(missing_in_json))
print("Zu viel im JSON:", len(extra_in_json))

print("\n--- FEHLENDE EINTRÄGE ---")
for lemma in sorted(missing_in_json):
    print(lemma)

print("\n--- NUR IM JSON ---")
for lemma in sorted(extra_in_json):
    print(lemma)

with open(json_path, encoding="utf8") as f:
    data = json.load(f)

entries = data
print("Entries:", len(entries))

# --- Hilfssets bauen ---
lemma_set = {e["lemma"] for e in entries}

search_form_set = set()
for e in entries:
    for f in e.get("search_forms", []):
        search_form_set.add(f)

# --- Sammler ---
missing_pos = []
missing_pos_proper = []
empty_senses = []
missing_definition = []
broken_crossrefs = []
uncertain_words = []

for e in entries:
    lemma = e["lemma"]
    pos = e.get("morphology", {}).get("pos", "")
    senses = e.get("senses", [])

    # ---------------- POS prüfen ----------------
    if not pos:
        text_blob = str(e).lower()
        if "name of" in text_blob:
            missing_pos_proper.append(lemma)
        else:
            missing_pos.append(lemma)

    # ---------------- Bedeutungen ----------------
    if not senses and not e.get("is_cross_reference"):
        empty_senses.append(lemma)
    else:
        defs = [s.get("definition","").strip() for s in senses]
        if senses and not any(defs):
            missing_definition.append(lemma)

    # ---------------- Crossrefs prüfen ----------------
    if e.get("is_cross_reference"):
        target = e.get("see","").strip()

        if (
            target not in lemma_set and
            target not in search_form_set
        ):
            broken_crossrefs.append(f"{lemma} → {target}")

    # ---------------- Unsicher ----------------
    if "uncertain" in str(e).lower() or "?" in lemma:
        uncertain_words.append(lemma)

# --- REPORT ---
print("\n--- QUALITY REPORT ---")
print("Fehlendes POS (echte Lücken):", len(missing_pos))
print("Eigennamen ohne POS:", len(missing_pos_proper))
print("Keine Bedeutungen:", len(empty_senses))
print("Leere Bedeutungen:", len(missing_definition))
print("Defekte Crossrefs:", len(broken_crossrefs))
print("Unsichere Einträge:", len(uncertain_words))

print("\n--- DEFEKTE CROSSREFS ---")
for x in broken_crossrefs:
    print(x)