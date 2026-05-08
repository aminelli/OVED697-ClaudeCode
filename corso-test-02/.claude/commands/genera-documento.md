# Comando: /genera-documento

Genera un documento Markdown/HTML strutturato (report, analisi, brief) a partire da dati CSV.

## Utilizzo

```
/genera-documento <tipo> <percorso-csv>
```

## Tipi disponibili

| Tipo | Artifact usato | Output |
|------|---------------|--------|
| `report-mensile` | `artifacts/report-mensile/` | Markdown con KPI e tabelle |

## Esempi

```
/genera-documento report-mensile data/vendite_punti_vendita.csv
```

## Passi da eseguire

1. Verifica che `<tipo>` corrisponda a una cartella in `artifacts/`; se non esiste mostra i tipi disponibili
2. Verifica che il CSV esista
3. Leggi `artifacts/<tipo>/artifact.md`
4. Leggi `skills/artifact-generator/SKILL.md`
5. Segui il workflow della skill per generare il documento
6. Salva con il naming convention definito in `artifact.md`
