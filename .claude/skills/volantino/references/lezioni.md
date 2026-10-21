# Lezioni imparate (errori già fatti, da non rifare)

## Strumenti
- Il server MCP di PhotoCraft deve partire con `--automation-read-root` e `--automation-write-root` sulla
  cartella del progetto (vedi `assets/mcp.json`), altrimenti `doc_save`/`doc_place` rispondono
  "write authority is absent". Se succede, usa `scripts/pc.py`: stessi comandi, via `photocraft-cli serve`.
- I comandi che leggono file dal disco con un percorso proprio (`image.mode.cmyk` con profilo .icc,
  `edit.profileInfo`, `layer.smartObjects.rasterize`) sono disabilitati nel server headless: usali dalla CLI
  `photocraft-cli run file --cmd ... --out ...`. L'esportazione CMYK è fatta così.
- `select.deselect` è un errore se non c'è selezione: nelle ricette mettigli `"continue": true`.
- `layer.layerMask.hideSelection` dopo `revealSelection` non ha dato l'effetto atteso: per togliere pezzi da una
  maschera usa `select.lasso`/`select.rect` + `edit.fill contents=black target=mask`.
- `select.lasso` riempie il poligono (non solo il contorno). `paint.gradient` con `target=mask` sfuma una maschera.
- `doc.render` restituisce PNG in base64; con pc.py usa `"out": "file.png"`. Oppure salva un PNG con `doc.save`.
- `type.create` restituisce i bounds reali del testo: misurali in un documento di prova (`misura_bounds()`) per
  centrare un blocco. A 72 dpi i bounds sono diversi: misura sempre sulla base a 300 dpi.
- Con `doc.save` su PDF l'immagine è Flate (senza perdita) e la pagina prende le misure del documento in mm.
- La modalità bridge (app aperta) funziona in locale; le ricette qui sono pensate per il server headless, ma i
  comandi engine sono gli stessi.

## Immagini e ritagli
- Un riflesso specchiato di un prodotto bianco crea una striscia chiara proprio nel punto di contatto: tienilo
  debolissimo (12 %), solo sotto la linea d'appoggio, e metti le ombre sopra al riflesso.
- Un'ombra esterna attorno a una figura ritagliata produce un bordo scuro che sembra un errore di ritaglio: per
  "appoggiare" una figura usa un'ombra di contatto sotto i piedi, non un dropShadow sul livello.
- Il riempimento in base al contenuto di un buco grande (una persona intera) lascia una sagoma chiara: riempi
  con un gradiente dei colori accanto e sfoca tutto dopo aver deselezionato.
- `select.object` (Object Finder) su una porzione piccola è più preciso di `select.subject` su tutta la scena
  quando ci sono più soggetti; su fondo piatto `select.subject` è quasi perfetto.
- I PNG ufficiali dei prodotti hanno spesso un'ombra grigia incorporata sotto la base: mascherala sotto la linea
  d'appoggio prima di aggiungere le tue ombre.
- Loghi piccoli (meno di 1000 px) ingranditi al doppio escono morbidi in stampa: chiedi i vettoriali.

## Impaginazione e testi
- Le anteprime con l'abbondanza ingannano l'occhio sulla centratura: giudica sull'anteprima rifilata
  (`image.crop` alla misura finita dopo aver salvato il sorgente).
- Il QR deve essere grande (almeno 2 cm di lato in stampa) ma può arrivare a 3,5 mm dal taglio solo se l'utente
  accetta il rischio; il testo che deve essere letto resta dentro i 5 mm.
- Un sottotitolo dentro un badge rotondo deve stare nella corda del cerchio scuro: se tocca l'anello oro,
  bianco su oro sparisce (è successo con "IN OGNI PACCO").
- "Non cumulabile con altre offerte in corso" non ci stava accanto al QR: tagliare parole è lecito se lo dici.
- Quando l'omaggio stava sotto al "programma fedeltà" sembrava valere solo dal secondo ordine: l'ordine delle
  righe cambia il significato; rileggi i termini come li leggerebbe un cliente.
- Il carattere "piccolo ed elegante" (Raleway) è illeggibile a 7-8 pt: usa Inter.
- Un indirizzo web funziona meglio pulito (bianco, filo d'oro) che con gli effetti dei titoli.

## Processo
- Chiedi i contenuti prima di impaginare; proponi slogan solo se l'utente non ne ha.
- Ogni modifica passa dalla ricetta (script → JSON → pc.py), mai solo dal file: l'utente cambia idea spesso e
  rifare da zero in 10 secondi è ciò che rende sostenibili 13 versioni del retro.
- Dopo ogni versione: anteprima guardata, commit, anteprima inviata all'utente con due righe su cosa è cambiato.
