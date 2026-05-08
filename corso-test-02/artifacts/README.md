# Guida al Sistema Artifact

Questa cartella contiene le **definizioni degli artifact** che Claude può generare
in questo progetto. Ogni sotto-cartella rappresenta un tipo di output specifico.

---

## Struttura di una definizione artifact

```
artifacts/<nome>/
├── artifact.md     ← ★ la definizione: frontmatter YAML + regole
└── template.*      ←   la struttura base (HTML, Markdown, …)
```

### `artifact.md` — il frontmatter è il contratto

Il frontmatter YAML di ogni `artifact.md` definisce il **contratto** tra
Claude e l'utente: cosa Claude si impegna a produrre e in quale forma.

Campi del frontmatter:

| Campo | Obbligatorio | Descrizione |
|-------|-------------|-------------|
| `artifact:type` | ✓ | Classificazione tecnica (vedi tipi sotto) |
| `artifact:title` | ✓ | Nome leggibile |
| `artifact:description` | ✓ | Cosa fa + USE/NON USARE |
| `artifact:input` | ✓ | Dati che Claude deve leggere prima |
| `artifact:output` | ✓ | Path, formato, self-contained? |
| `artifact:dependencies` | — | CDN, script esterni ammessi |
| `artifact:quality-rules` | ✓ | Vincoli che l'output deve rispettare |
| `artifact:version` | ✓ | Versione della spec |

### `template.*` — la struttura base

Il template usa `{{PLACEHOLDER}}` per i valori che Claude sostituirà
con i dati reali letti dal CSV. Esempio:

```html
<h1>{{TITOLO}}</h1>
<script>
  const DATI = {{DATA_JSON}};
</script>
```

---

## Tipi di artifact supportati

| Tipo | Tecnologia | Caso d'uso tipico |
|------|-----------|-------------------|
| `html-interactive` | HTML + Chart.js | Dashboard con filtri e grafici |
| `markdown-doc` | Markdown | Report, analisi, brief |
| `html-presentation` | HTML + CSS | Slide deck nel browser |
| `html-component` | HTML + CSS + JS | Componente UI standalone |

---

## Artifact disponibili in questo progetto

| Cartella | Tipo | Output |
|----------|------|--------|
| `dashboard-vendite/` | `html-interactive` | Dashboard filtri + grafici |
| `report-mensile/` | `markdown-doc` | Report KPI con tabelle |
| `presentazione-kpi/` | `html-presentation` | Slide deck navigabile |
| `componente-card/` | `html-component` | Card prodotto/punto vendita |

---

## Differenza tra Artifact e Skill

- La **skill** (`skills/artifact-generator/SKILL.md`) definisce il *processo*:
  come leggere il CSV, come popolare il template, come salvare il file.
- L'**artifact** (`artifact.md`) definisce il *risultato*:
  che tipo di file produrre, con quali dati, con quali vincoli.

Analogia: la skill è la *ricetta* (passi da seguire),
l'artifact è la *scheda prodotto* (cosa deve essere il piatto finito).
