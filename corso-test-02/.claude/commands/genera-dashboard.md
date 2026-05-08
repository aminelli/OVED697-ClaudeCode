# Comando: /genera-dashboard

Genera la dashboard HTML interattiva a partire da un CSV di vendite per punto vendita.

## Utilizzo

```
/genera-dashboard <percorso-csv>
```

## Esempi

```
/genera-dashboard data/vendite_punti_vendita.csv
/genera-dashboard data/Q2_2025.csv
```

## Passi da eseguire

1. Verifica che il file CSV esista; se non esiste **fermati** e avvisa l'utente
2. Leggi la definizione artifact: `artifacts/dashboard-vendite/artifact.md`
3. Leggi la skill: `skills/artifact-generator/SKILL.md`
4. Segui il workflow della skill per generare la dashboard
5. Salva in `output/dashboard_<nome-file>_<YYYYMMDD>.html`
6. Conferma all'utente il path e le istruzioni per aprirla nel browser
