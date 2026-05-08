# Comando: /analizza

Analizza un file CSV di vendite applicando la logica predefinita a 4 fasi
definita in `skills/analisi-vendite/`.

## Utilizzo

```
/analizza <percorso-file>
```

## Esempi

```
/analizza data/vendite_esempio.csv
/analizza data/Q1_2025.csv
```

## Passi da eseguire

1. Verifica che il file esista: se non esiste, **fermati** e avvisa l'utente
2. Carica e leggi la skill: `skills/analisi-vendite/SKILL.md`
3. Segui il workflow della skill passo per passo
4. Al termine, mostra il sommario all'utente e il path del report generato

## Note

- Il report viene salvato in `output/report_<nome-file>_<data>.md`
- Se il file ha separatore `;` invece di `,`, passare `--sep ";"` allo script
