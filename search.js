let data = {};
let activeLetter = "";
let entryMap = {}

fetch("Wörterbuch_Tolman.json")
  .then(r => r.json())
  .then(d => {
    data.entries = Object.values(d);  
    entryMap = {};
    for (let e of data.entries) {
      entryMap[e.lemma] = e;
}
    buildAlphabet();
    buildPosFilter();
    toggleFilters();
  });


function searchWord(){

    let query = document.getElementById("searchBox").value.toLowerCase()
    let posFilter = document.getElementById("posFilter").value
    let genderFilter = document.getElementById("genderFilter").value
    let results = []

    for(let e of data.entries){
        let match = true

        if(activeLetter){
            let lemmaMatch = e.lemma && e.lemma.toLowerCase().startsWith(activeLetter)
            let variantMatch = e.search_forms && e.search_forms.some(v => v.toLowerCase().startsWith(activeLetter))
            if(!lemmaMatch && !variantMatch) match = false
        }

        if(!match) continue

        if (query && query.length > 0) {

         let q = query.toLowerCase();
         let textMatch =
           e.lemma?.toLowerCase() === q;

        let variantMatch =
          e.search_forms?.some(v =>
              v.toLowerCase() === q
          );

      let prefixMatch =
          e.search_forms?.some(v =>
              v.toLowerCase().startsWith(q)
          );

      let defMatch =
        e.senses?.some(s => {
          let words = s.definition
              .toLowerCase()
              .split(/\s+/);   

          return words.includes(q);
    });

      match = textMatch || variantMatch || prefixMatch || defMatch;
}

        if(!match) continue
        if(posFilter){
            if(!e.morphology || !e.morphology.pos) continue

            let parts = e.morphology.pos.split(";").map(p => p.trim())

            if(!parts.includes(posFilter)) continue
        }
        if(genderFilter){
            if(!e.morphology || e.morphology.gender !== genderFilter) continue
        }

        results.push(e)
    }

    displayResults(results)
}

function displayResults(results) {
  let html = "";
  for (let e of results) {
    html += `<div class="result" onclick='showEntry(${JSON.stringify(e)})'>
               <b>${e.lemma}</b>

             </div>`;
  }
  document.getElementById("results").innerHTML = html;
}
const caseMap = {
  loc: "locative",
  acc: "accusative",
  dat: "dative",
  gen: "genitive",
  inst: "instrumental"
};

function normalizePos(posString) {
  if (!posString) return "";

  let parts = posString.split(";").map(p => p.trim());

  parts.sort((a, b) => b.length - a.length);

  return parts[0];
}

function showEntry(e) {
  let html = `<h2>${e.lemma}</h2>`;

  let globalPos = [];
  if (e.is_cross_reference) {
    let html = `<h2>${e.lemma}</h2>`;
    html += `<p><i>see → <a href="#" onclick="openEntry('${e.see}')">${e.see}</a></i></p>`;

    document.getElementById("entry").innerHTML = html;

    window.scrollTo({ top: 0, behavior: "smooth" });
    return;
}

  if (e.morphology && e.morphology.pos) {
    globalPos = e.morphology.pos.split(";").map(p => p.trim());
  }

  if (e.variants && e.variants.length > 0) {
    html += `<p><b>Variants:</b> ${e.variants.join(", ")}</p>`;
}

  if (e.morphology) {
    if (e.morphology.pos) html += `<p><b>POS:</b> ${normalizePos(e.morphology.pos)}</p>`;
    if (e.morphology.gender) html += `<p><b>Gender:</b> ${e.morphology.gender}</p>`;
  }

  if (e.senses && e.senses.length) {
    html += "<ol>";

    for (let s of e.senses) {

      let def = s.definition;

      let sensePos = s.pos ? s.pos.split(";").map(p => p.trim()) : [];

      let showPos = false;

      if (globalPos.length > 1) {
        showPos = true;
      } else if (sensePos.length && sensePos[0] !== globalPos[0]) {
        showPos = true;
      }

      if (s.pos && s.pos !== e.morphology.pos) {
        def += ` <b>[${s.pos}]</b>`;
}

      if (s.construction) {
        if (s.construction.type === "with prefix")
          def += ` <i>(with prefix ${s.construction.value})</i>`;

        if (s.construction.type === "with case")
          def += ` <i>(with ${caseMap[s.construction.case] || s.construction.case})</i>`;

        if (s.construction.type === "with word")
          def += ` <i>(with ${s.construction.value})</i>`;
        if (s.construction.type === "composition")
          def += ` <i>(in composition)</i>`;
        }

      html += `<li>${def}</li>`;
    }

    html += "</ol>";
  }

  document.getElementById("entry").innerHTML = html;
  window.scrollTo({ top: 0, behavior: "smooth" })
}
function openEntry(lemma) {
  let entry = entryMap[lemma];

  if (!entry) {
    console.log("Not found:", lemma);
    return;
  }

  showEntry(entry);
}
function buildAlphabet() {
  let letters = "AĀIUKXGCJTΘDNPFBMYRVSŠZH";
  let html = "";
  for (let l of letters) {
    html += `<button id="letter-${l}" onclick="searchLetter('${l}')">${l}</button> `;
  }
  document.getElementById("alphabet").innerHTML = html;
}

function searchLetter(letter){

    activeLetter = letter.toLowerCase()

    document.getElementById("searchBox").value = activeLetter

    document.querySelectorAll("#alphabet button")
        .forEach(b => b.classList.remove("active"))

    document.getElementById("letter-" + letter).classList.add("active")

    searchWord()  
}

function clearSearch(){

    activeLetter = ""

    document.getElementById("searchBox").value = ""
    document.getElementById("posFilter").value = ""
    document.getElementById("genderFilter").value = ""

    document.querySelectorAll("#alphabet button")
        .forEach(b => b.classList.remove("active"))

    displayResults([])
    document.getElementById("entry").innerHTML = ""
}

function toggleFilters() {
  let mode = document.getElementById("searchMode").value;
  let filters = document.getElementById("filters");
  let alphabet = document.getElementById("alphabet");

  if (mode === "lemma") {
    filters.style.display = "block";
    alphabet.style.display = "block";
  } else {
    filters.style.display = "none";
    alphabet.style.display = "none";
  }
}

function buildPosFilter(){

  let posSet = new Set()

  for(let e of data.entries){
    if(e.morphology && e.morphology.pos){
      
      let parts = e.morphology.pos.split(";")
      parts.forEach(p => posSet.add(p.trim()))
    }
  }

  let select = document.getElementById("posFilter")

  let html = `<option value="">All POS</option>`

  Array.from(posSet).sort().forEach(p => {
    html += `<option value="${p}">${p}</option>`
  })

  select.innerHTML = html
}