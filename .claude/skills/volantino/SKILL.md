---
name: volantino
description: Progetta volantini, flyer, cartoline, locandine e pieghevoli pronti per la tipografia (A6, A5, A4, DL, fronte e retro) con PhotoCraft/ArtCraft in locale, con lo stile Nutrihangar/WHY già collaudato - base con abbondanza e guide, immagini generate dall'IA su prompt scritti da Claude, loghi scontornati, prodotti veri appoggiati su scene generate, scritte a effetto (oro metallico, corsivo, sigilli), QR code, termini dell'offerta, esportazione PDF CMYK FOGRA39. Usala ogni volta che l'utente parla di volantino, flyer, cartolina, locandina, depliant, materiale da stampare o da mandare in tipografia, offerta o sconto da stampare, QR code su carta, anche se non nomina PhotoCraft e anche solo per un prompt per le immagini o per l'esportazione in CMYK.
---

# Volantino: dal brief al PDF per la tipografia

Il flusso è quello con cui è nato il volantino A6 Nutrihangar / WHY nature / WHY sport, in locale, con PhotoCraft
pilotato dai tool MCP `photocraft` o da `scripts/pc.py`. Stile, mattoni e lezioni sono nei file `references/`:
leggi `stile.md` prima di impaginare, `prompt-immagini.md` quando servono immagini, `ricette.md` quando scrivi
una ricetta, `lezioni.md` quando qualcosa non torna.

## 1. Avvio (una volta per progetto)

1. `photocraft-cli --version`. Se manca, chiedi all'utente di installare PhotoCraft (le release includono la CLI).
2. Se i tool MCP `photocraft` ci sono, usali. Se `doc_save`/`doc_place` rispondono "write authority is absent",
   il server è partito senza radici di scrittura: copia `assets/mcp.json` in `.mcp.json` del progetto (vale
   dalla prossima sessione) e intanto usa `python3 <skill>/scripts/pc.py ricetta.json`, che parla con
   `photocraft-cli serve` sulla cartella corrente con gli stessi comandi engine.
3. `bash <skill>/scripts/installa-font.sh` (Anton, Bebas Neue, Cinzel, Inter, Kaushan Script, Montserrat; OFL).
4. Cartelle: `risorse/` (materiale dell'utente, mai modificato: loghi, foto, prodotti, QR), `lavoro/` (sorgenti
   `.pcraft` e ritagli), `export/` (anteprime e `stampa/`), `scripts/` (generatori e ricette). Lavora in un repo
   git e committa a ogni versione mostrata.

## 2. Brief: chiedi, non inventare

Prima di impaginare servono: formato e lati; scopo; testi (slogan, offerta, termini, contatti); loghi e foto
(chiedi i vettoriali o almeno 1000 px); colori di marchio; indirizzo del QR o il PNG del QR. Proponi slogan
solo se mancano. Se l'utente dà le indicazioni a pezzi, impagina quello che c'è e chiedi il resto in chiusura,
con un elenco numerato di ciò che manca.

Misure: `python3 <skill>/scripts/nuova_base.py --formato A6 --out lavoro/base-a6.pcraft` crea la base a 300 dpi
con abbondanza 3 mm (A6 → 1311 × 1819 px), guide rosse sul rifilo e verdi sull'area sicura (5 mm dal rifilo
= 95 px dal bordo) e stampa le misure da usare nelle ricette. Altri formati con `--formato A5|A4|DL` o `--mm LxH`.

## 3. Flusso per ogni lato

1. **Struttura**: zone a gradiente, separatore, targhe per i loghi, footer (bianco sul fronte, scuro sul retro).
2. **Immagini**: scrivi i prompt (vedi `references/prompt-immagini.md`) e falle generare all'utente; scegli la
   tecnica: figure su fondo piatto da ritagliare, composizione intera con il volantino come riferimento, scena
   vuota su cui appoggiare i prodotti veri. Le scritte generate dall'IA si rifanno sempre con testi veri.
3. **Scritte**: i mattoni di `scripts/ricetta.py` (`scritta_oro`, `scritta_corsiva`, `scritta_spaziata`,
   `badge_sigillo`, `blocco_centrato`...) con palette e caratteri di `references/stile.md`.
4. **Verifica**: salva il sorgente, esporta l'anteprima PNG e guardala; esporta anche l'anteprima rifilata
   (`image.crop` alla misura finita): è quella su cui si giudicano centrature e margini. Controlla che testi e
   loghi stiano dentro l'area sicura, che i corpi non scendano sotto 7,5 pt (note 5,5 pt), che il QR sia
   almeno 2 cm. Se qualcosa sfora, dillo all'utente con la misura.
5. **Consegna della versione**: commit, invia l'anteprima (rifilata, se il formato ha abbondanza) e due righe su
   cosa è cambiato e cosa resta da decidere. Aspettati molte iterazioni: per questo tutto passa da una ricetta.

## 4. La ricetta è la verità

Ogni lato è un generatore Python (`scripts/genera_<lato>.py`) che scrive una lista di passi JSON eseguita da
`pc.py` o dai tool MCP. Modifica il generatore, non il file: ricostruire da zero costa dieci secondi e l'utente
cambia idea spesso. Esempi completi in `references/esempi/`. Regole che hanno retto tredici versioni del retro:

- Una costante per ogni misura che l'utente può voler cambiare (perni, altezze, colori, testi).
- Misura i testi con `misura_bounds()` prima di centrarli: l'occhio sbaglia, i bounds no.
- Prodotti in proporzione reale: chiedi le altezze in cm e usa `prodotti_su_piano()` con un fattore px/cm.
- Le figure "appoggiano" grazie a ombra ampia + ombra di contatto sopra a un riflesso quasi invisibile; mai
  un'ombra esterna attorno al ritaglio.
- Rotazioni con lo stesso perno per tutte le scritte di un gruppo.
- `select.deselect` con `"continue": true`.

## 5. Immagine generata usata com'è

Se l'utente preferisce l'immagine generata intera (è successo per il fronte), adattala al formato
(`references/ricette.md`, sezione "Adattare un'immagine generata"): ridimensiona a 300 dpi, estendi la tela con
abbondanza riempiendo i bordi, rimetti loghi e testi piccoli veri, aggiungi le guide, controlla i margini.
Tieni comunque la versione a livelli come alternativa.

## 6. Esportazione per la tipografia

`bash <skill>/scripts/esporta-stampa.sh -o export/stampa -n volantino-a6 lavoro/fronte.pcraft lavoro/retro.pcraft`
appiattisce, converte in CMYK Coated FOGRA39 (profilo in `assets/profili/`, CC0) tramite la CLI e produce: un
PDF per lato alla misura con abbondanza, senza crocini, Flate senza perdita, profilo incorporato; un PDF unico
a più pagine; in `alternative/` TIFF CMYK e PDF RGB; una prova colore a video per lato; `LEGGIMI.txt` per la
tipografia. Guarda le prove colore prima di consegnare e invia i PDF all'utente. Se la tipografia chiede altro
(RGB, TIFF, crocini), parti dagli stessi sorgenti.

## 7. Comunicazione con l'utente

L'utente giudica a vista e risponde in modo diretto ("aloni", "font orribile", "non appoggiano"): rispondi con
la correzione fatta, non con spiegazioni; se un difetto nasce da una scelta tecnica, dillo in una riga e proponi
l'alternativa. Quando lo strumento non arriva a un risultato (ritagli imperfetti, etichette generate), proponi
subito la via che funziona (rigenerare su fondo piatto, scena vuota + file veri) invece di insistere.
