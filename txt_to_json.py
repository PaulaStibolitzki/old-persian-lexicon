import re
import json
from itertools import product

input_file = "C:/Users/paula/Documents/JMU/5/WB/Wortliste_Tolman.txt"
output_file = "C:/Users/paula/Documents/JMU/5/WB/Wörterbuch_Tolman.json"

pos_map = {
    "pers. pron.": "personal pronoun",
    "demon. pron. used as a relative": "demonstrative pronoun used as a relative",
    "demon. pron.": "demonstrative pronoun",
    "interrog. pronoun": "interrogative pronoun",
    "indef.": "indefinite pronoun",
    "prohibitive ptcl.": "prohibitive particle",
    "pron. encl.": "enclitic pronoun",
    "pron. stem": "pronominal stem",
    "conj. with subj.": "conjunction with subjunctive",
    "pron.": "pronoun",
    "verb": "verb",
    "v.": "verb",
    "part. fut. pass. / part. pres. act.": "participle future passive/participle present active",
    "adv.": "adverb",
    "adj. as subs.": "adjective as substantive",
    "adj.": "adjective",
    "encl. conj.": "enclitic conjunction",
    "encl. pcl.": "enclitic particle",
    "conj.": "conjunction",
    "prep.": "preposition",
    "postpos.": "postposition",
    "verbal prefix": "verbal prefix",
    "num.": "numeral",
    "part. pass.": "passive participle"}

GENDER_MAP = {
    "m.": "masculine",
    "f.": "feminine",
    "n.": "neuter"}

SEE_RE = re.compile(r"\[see\s+([^\]]+)\]", re.IGNORECASE)
def extract_see(def_text):
    match = re.search(r"\[see\s+([^\]]+)\]", def_text, re.IGNORECASE)
    return match.group(1).strip() if match else None

def split_lemma(lemma_raw):
    lemma_raw = lemma_raw.lstrip("\ufeff").strip()
    display_variants = []
    if "/" in lemma_raw:
        parts = [p.strip() for p in lemma_raw.split("/")]
        display_variants = parts[1:]
        slash_parts = parts
    else:
        slash_parts = [lemma_raw]

    all_forms = []
    for part in slash_parts:
        pieces = re.split(r'(\[.*?\])', part)
        options = []
        for piece in pieces:
            if piece.startswith('[') and piece.endswith(']'):
                inside = piece[1:-1]
                options.append(['', inside])
            else:
                options.append([piece])

        variants = [''.join(p) for p in product(*options)]
        all_forms.extend(variants)

    search_forms = list(set(all_forms))

    return search_forms, display_variants

def parse_pos(morph_raw):
    if not morph_raw:
        return None

    morph_raw = morph_raw.lower()
    mapped = []

    for key in sorted(pos_map.keys(), key=len, reverse=True):
        pattern = r'(?<!\w)' + re.escape(key.lower()) + r'(?!\w)'
        if re.search(pattern, morph_raw):
            mapped.append(pos_map[key])

    mapped = set(mapped)
    if any("pronoun" in m and m != "pronoun" for m in mapped):
        mapped.discard("pronoun")

    return "; ".join(sorted(mapped)) if mapped else None

def parse_gender(morph_raw):
    if not morph_raw:
        return None
    morph_raw = morph_raw.lower().strip()
    return GENDER_MAP.get(morph_raw)

def parse_construction(morph_raw):
    if not morph_raw:
        return None

    morph_raw = morph_raw.strip().lower()
    if "in composition" in morph_raw:
      return {
          "type": "composition"}

    match = re.search(r"with prefix\s+([a-zāīūθš]+)", morph_raw)
    if match:
        return {
            "type": "with prefix",
            "value": match.group(1) }
    
    match = re.search(r"with\s+(loc|acc|dat|gen|inst|abl|voc|ins|locative|accusative|dative|genitive|instrumental)", morph_raw)
    if match:
        case = match.group(1)
        case_map = {
            "locative": "loc",
            "accusative": "acc",
            "dative": "dat",
            "genitive": "gen",
            "instrumental": "inst",
            "ablative": "abl",
            "vocative": "voc" }

        case = case_map.get(case, case)

        return {
            "type": "with case",
            "case": case}

    return None

def split_senses(def_text, morph_raw):
    parts = re.split(r"\s*\d+\)\s*", def_text)
    senses = []

    for part in parts:
        part = part.strip(" ;")
        if not part:
            continue

        senses.append({
            "definition": part,
            "pos": parse_pos(morph_raw),
            "construction": parse_construction(morph_raw)  })

    if not senses:
        senses.append({
            "definition": def_text.strip(),
            "pos": parse_pos(morph_raw),
            "construction": parse_construction(morph_raw)})

    return senses

entries_dict = {}
with open(input_file, encoding="utf-8-sig") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        cols = line.split("\t")
        if len(cols) < 2:
            continue

        lemma_raw = cols[0]
        morph_raw = ""
        def_raw = ""

        if len(cols) == 2:
            def_raw = cols[1]
        else:
            morph_raw = cols[1]
            def_raw = cols[2]

        search_forms, display_variants = split_lemma(lemma_raw)
        lemma = lemma_raw.strip()

        pos = parse_pos(morph_raw)
        gender = parse_gender(morph_raw)
        see_target = extract_see(def_raw)

        if see_target:
          senses = []
        else:
          senses = split_senses(def_raw, morph_raw)

        if lemma not in entries_dict:
            entries_dict[lemma] = {
              "lemma": lemma,
              "senses": [],
              "search_forms": search_forms,                
              "variants": display_variants if display_variants else None,  
              "morphology": {},
              "see": see_target,
              "is_cross_reference": see_target is not None}

        entry = entries_dict[lemma]

        if pos:
            existing = entry["morphology"].get("pos")
            if existing:
                all_pos = set(existing.split("; ")) | set(pos.split("; "))
                entry["morphology"]["pos"] = "; ".join(sorted(all_pos))
            else:
                entry["morphology"]["pos"] = pos

        if gender:
            entry["morphology"]["gender"] = gender
            if "pos" not in entry["morphology"]:
                entry["morphology"]["pos"] = "noun"

        entry["senses"].extend(senses)

entries = list(entries_dict.values())

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)