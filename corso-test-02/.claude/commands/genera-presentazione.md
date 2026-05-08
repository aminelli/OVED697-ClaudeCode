# Comando: /genera-presentazione

Genera una presentazione HTML slide-deck a partire da un CSV di vendite.

## Utilizzo

```
/genera-presentazione <percorso-csv>
```

## Esempi

```
/genera-presentazione data/vendite_punti_vendita.csv
```

## Passi da eseguire

1. Verifica che il CSV esista
2. Leggi `artifacts/presentazione-kpi/artifact.md`
3. Leggi `skills/artifact-generator/SKILL.md`
4. Segui il workflow della skill
5. Salva in `output/presentazione_<nome-file>_<YYYYMMDD>.html`
6. Indica all'utente come navigare le slide (tasti ← → oppure click)
