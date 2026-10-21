# Stile: palette, caratteri, effetti

Il sistema grafico messo a punto sul volantino Nutrihangar / WHY. Riusalo com'è quando il cliente è lo stesso;
per un altro cliente tieni la struttura (un colore "mondo" per zona, oro per le promesse, bianco per il testo)
e cambia i colori di marchio.

## Palette

| Ruolo | Valore | Note |
|---|---|---|
| Oro metallico (titoli, badge, 25%) | gradiente a 5 tappe `#fff3c4 → #e8c058 → #fff8dc → #b8860b → #ffe9a8`, angolo 90° | `ORO` in `scripts/ricetta.py`; va su testo convertito in forma |
| Oro piatto (titoletti, punti elenco, evidenziazioni) | `#e8c058` | leggibile su fondo scuro a 8 pt |
| Traccia scura sotto l'oro | `#3a2a00` (oro) · `#2a1d00` (badge) | 2-7 px fuori dal glifo |
| Mondo "nature" | gradiente `#e4f5b0 → #8fc63f → #2c6410`, angolo -35° | verde WHY nature `#a6c839`; traccia `#1b4a06` |
| Mondo "sport" | gradiente `#e20613 → #7d0008 → #140000`, angolo -150° | rosso WHY sport `#e20613`; traccia `#3a0000` |
| Fondo scuro elegante (retro) | scena fotografica scura; centro del badge `#4a3612 → #0e0902` radiale | |
| Testo corrente | `#ffffff`; nota legale `#c8c8c8` | |
| Nomi di marchio nel testo | verde `#a6c839`, rosso `#e20613` (type.edit runs) | |

## Caratteri (tutti OFL, in `assets/font/`)

| Uso | Famiglia | Come |
|---|---|---|
| Numero / parola d'impatto (25%, BENESSERE, LIMITI, sito) | **Anton** | 46-92 pt, convertito in forma, oro o bianco-argento |
| Frase d'invito a mano (Inquadra il QR Code, Nutri il tuo) | **Kaushan Script** | 24-30 pt bianco, ombra + bagliore |
| Righe maiuscole spaziate (E OTTIENI SUBITO IL, IN COLLABORAZIONE CON) | **Montserrat** 700-800 | 8-13 pt, tracking 120-260 |
| Titoletti eleganti del footer (LO SCONTO È:) | **Cinzel** 700 | 8 pt oro, tracking 90; richiama i logotipi serif dorati |
| Testo corrente, elenchi, note | **Inter** 600 (righe) / 400 (note) | 7,5 pt righe, 5,5 pt note; punti elenco "•" a 10 pt in oro |
| Alternativa condensata per titoli | **Bebas Neue** | se Anton risulta troppo pesante |

Evita Raleway (e in genere i sans "sottili") sotto i 9 pt: in stampa non si legge. Misure minime: 7,5 pt per il
testo che il cliente deve leggere, 5,5 pt per le note legali, 10 pt per un indirizzo web.

## Ricette di effetto (stili di livello PhotoCraft)

- **Oro metallico**: `type.create` → `type.convertToShape` → `shape.edit fill=gradiente ORO` →
  `layer.layerStyle.replace` con dropShadow (nero 80 %, distanza 16, size 12), outerGlow (`#ffcf5a` 50 %, 40),
  bevelEmboss (inner, chiselHard, depth 260, size 10), stroke (6 px outside `#3a2a00`). → `scritta_oro()`
- **Bianco-argento** (DI SCONTO, LIMITI): stesso schema con gradiente `#ffffff → #ffe6e6` o bianco → `#ffe9b0`,
  bevel smooth depth 150 size 5, stroke 4-5 px scuro.
- **Corsivo luminoso**: Kaushan Script bianco, dropShadow (colore del mondo, 70 %), outerGlow (chiaro 60 %, 26),
  stroke 3 px del colore scuro del mondo. → `scritta_corsiva()`
- **Sigillo smerlato**: stella a 30 punte con starRatio 0,9 in oro, bevel smooth; cerchio scuro interno con bordo
  `#fff3c4` 3 px e ombra interna; titolo Anton oro; sottotitolo Inter 4,6-5 pt bianco. → `badge_sigillo()`
- **Inclinazione**: ruota ogni livello con `edit.transform matrix=rot_matrix(-7°, perno)` usando lo stesso perno
  per tutte le scritte di un gruppo, così restano allineate. -7° / -10° bastano: più inclinazione stanca.
- **Filo d'oro senza effetti**: bianco pieno + stroke 2 px `#e8c058`: per elementi che devono restare "puliti"
  (indirizzo web). → `scritta_bianca_filo_oro()`
- **Logo su fondo chiaro obbligato**: targa bianca arrotondata (radii 30) con ombra 35 %. → `targa()`
- **Separatore diagonale**: striscia bianca di 22 px con ombra 50 % size 28 tra due zone a gradiente. → `separatore()`

## Composizione che ha funzionato

- Fronte: due mondi separati da una diagonale (alto a sinistra → basso a destra), logo + slogan in un angolo,
  figura nell'angolo opposto, footer bianco con "In collaborazione con" e loghi partner grandi e centrati.
- Retro: logo in alto su fondo scuro, promessa gigante al centro (numero oro + parola bianca), riga con i nomi
  dei marchi nei loro colori, prodotti reali in proporzione su un piano, footer con termini a sinistra e QR a
  destra a tutta altezza, indirizzo web sopra al QR, nota legale in piccolo.
