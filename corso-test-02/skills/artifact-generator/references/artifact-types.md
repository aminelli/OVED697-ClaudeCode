# Riferimento: Tipi di Artifact

Per ogni `artifact:type` supportato, questa guida documenta:
- la tecnologia da usare
- i pattern da applicare
- cosa evitare tassativamente

---

## `html-interactive`

**Tecnologia:** HTML5 + Chart.js 4 (CDN) + JavaScript vanilla

**Casi d'uso:** dashboard con filtri, grafici interattivi, tabelle dinamiche

### Pattern obbligatori

1. **Data injection**
   I dati CSV devono essere embedded nel tag `<script>` come costante JS:
   ```js
   const DATI = [{"punto_vendita":"Milano","fatturato":48320.50,...}, ...];
   ```
   Serializzare con `json.dumps(rows, ensure_ascii=False)`. I valori numerici
   devono essere `float`, non stringhe.

2. **Filtri reattivi**
   Tutti i grafici e le tabelle devono ricalcolarsi quando l'utente cambia un filtro.
   Usare un'unica funzione `render()` chiamata a ogni `change` event dei select.

3. **CDN Chart.js**
   Usare sempre:
   ```html
   <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
   ```
   Non usare versioni diverse o CDN alternativi senza motivo.

4. **Destroy prima di redraw**
   Prima di ricreate un grafico Chart.js, chiamare sempre `chart.destroy()`.
   Altrimenti Chart.js si lamenta in console e i grafici si sovrappongono.

### Da evitare

- ❌ File JS o CSS esterni (tutto inline o CDN)
- ❌ `fetch()` o `XMLHttpRequest` (nessuna richiesta di rete per i dati)
- ❌ Framework (React, Vue, Angular) — solo vanilla JS
- ❌ Dati hardcoded diversi dal CSV — tutti i valori dal JSON embedded

---

## `markdown-doc`

**Tecnologia:** Markdown standard (GitHub Flavored Markdown)

**Casi d'uso:** report periodici, brief, documentazione

### Pattern obbligatori

1. **Pipe tables**
   Usare il formato standard:
   ```markdown
   | Colonna 1 | Colonna 2 | Colonna 3 |
   |-----------|-----------|-----------|
   | valore    | valore    | valore    |
   ```

2. **Formattazione valori monetari**
   Sempre in formato italiano: `€ 1.234,56`
   Usare Python: `f"€ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")`

3. **Variazioni MoM**
   Mostrare sempre con segno e freccia: `+12.3% ▲` oppure `-4.1% ▼`
   Calcolo: `(val_corrente - val_precedente) / abs(val_precedente) * 100`

4. **Nessun placeholder residuo**
   Prima di salvare, il file non deve contenere nessun `{{...}}`.

### Da evitare

- ❌ HTML dentro il Markdown (rende il file non portabile)
- ❌ Immagini esterne o link a file locali
- ❌ Tabelle con colonne troppo larghe (max ~80 caratteri di larghezza totale)

---

## `html-presentation`

**Tecnologia:** HTML5 + CSS3 + JavaScript vanilla (nessuna CDN)

**Casi d'uso:** slide deck navigabili nel browser, presentazioni da allegare via email

### Pattern obbligatori

1. **Navigazione tastiera**
   Sempre implementare `keydown` per `ArrowLeft`/`ArrowRight`.

2. **Slide visibili una alla volta**
   Usare `overflow: hidden` sul container + `transform: translateX(-N * 100vw)`.
   Ogni slide ha `min-width: 100vw; height: 100vh`.

3. **Counter slide**
   Ogni slide deve mostrare `N / TOTALE` in posizione fissa.

4. **Font size scalabile**
   Usare `clamp()` per i titoli: `font-size: clamp(1.4rem, 3vw, 2.2rem)`.

5. **Self-contained assoluto**
   Nessuna CDN, nessun file esterno. CSS e JS solo inline.

### Da evitare

- ❌ Reveal.js o librerie slide esterne
- ❌ Animazioni CSS che rallentano su hardware debole
- ❌ Più di 8 slide (il template ne prevede 5)
- ❌ Immagini esterne

---

## `html-component`

**Tecnologia:** HTML5 + CSS3 scoped (prefisso classe)

**Casi d'uso:** componenti riutilizzabili, mockup UI, snippet per copy-paste

### Pattern obbligatori

1. **CSS scoped con prefisso**
   Ogni regola CSS deve usare un prefisso classe per non inquinare il contesto
   in cui il componente viene embedato:
   ```css
   .pvcard { ... }
   .pvcard__header { ... }
   .pvcard__body { ... }
   ```
   (BEM-like naming: `.<componente>__<elemento>`)

2. **Larghezza fissa**
   I componenti card hanno `width: 320px` (mobile-first, 1 colonna).

3. **Dimostrazione standalone**
   Il file HTML deve avere anche un `<body>` che mostra il componente centrato
   su sfondo neutro, in modo che sia leggibile aprendo il file direttamente.

4. **Nessuna dipendenza**
   Solo CSS/HTML inline, nessuna CDN, nessun JS esterno.

### Da evitare

- ❌ Stili globali (`body { color: red }`) che impattano il contesto parent
- ❌ Componenti troppo grandi (restare sotto 400px di larghezza)
- ❌ JavaScript complesso in un componente card
