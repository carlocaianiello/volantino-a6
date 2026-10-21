# Volantino A6 — istruzioni per Claude

Obiettivo: progettare un volantino A6 (fronte e retro) pronto per la tipografia,
usando le app ArtCraft tramite MCP. Le specifiche di stampa sono nel README.

## All'avvio della sessione

1. Controlla che `photocraft-cli --version` funzioni.
   - Se manca: esegui `bash scripts/installa-artcraft.sh` (circa 7 minuti), poi
     di' all'utente di aprire una nuova sessione perché i tool MCP compaiono solo all'avvio.
     Nel frattempo puoi lavorare con la CLI (`photocraft-cli run/convert/info`).
2. Esegui `bash scripts/installa-font.sh` (installa i font di `risorse/font/` per PhotoCraft).
3. Se i tool MCP `photocraft` sono disponibili, usali al posto della CLI.
   Se `doc_save`/`doc_place` rispondono "write authority is absent", il server è partito
   senza radici di lettura/scrittura: usa `python3 scripts/pc.py passi.json`, che parla
   con `photocraft-cli serve` sulla cartella del progetto (stessi comandi engine).

## Regole di lavoro

- Formato file: 1311 × 1819 px a 300 dpi (A6 + 3 mm di abbondanza).
  Testi e loghi a almeno 95 px dal bordo del file.
- Sorgenti modificabili in `lavoro/` (`fronte.pcraft`, `retro.pcraft`), mai solo l'export.
  `lavoro/base-a6.pcraft` è la base vuota con le guide (rifilo in rosso, area sicura in verde).
  Il fronte scelto dall'utente è `lavoro/fronte.pcraft`: la composizione generata su Higgsfield
  (`risorse/ai/composizione-ai.webp`) adattata all'A6 con `scripts/fronte-ai.json`
  (ridimensionata a 1311 px, sfondo esteso in alto e in basso con riempimento in base al contenuto).
  La versione a livelli (scritte vettoriali, sfondi sfocati, personaggi ritagliati) è
  `lavoro/fronte-livelli.pcraft`, ricostruibile con `python3 scripts/genera_fronte.py` e poi
  `python3 scripts/pc.py scripts/fronte.json`: modifica la ricetta, non solo il file.
- Loghi ritagliati (con trasparenza) in `lavoro/loghi/`; prompt per le immagini AI in
  `risorse/ai/PROMPT-IMMAGINI.md`. Il connettore Higgsfield non genera immagini e il proxy
  blocca i link CloudFront: le immagini le genera l'utente e le allega in chat.
- File finali e anteprime in `export/`. Prima di dire che un file è pronto,
  genera un'anteprima (`doc_render_preview` o export PNG) e guardala.
- Materiale fornito dall'utente in `risorse/`: non modificarlo, lavora su copie.
- La modalità "bridged" (agganciarsi all'app aperta sul PC) non funziona nel cloud:
  si lavora solo sui file.
- I contenuti (testi, offerta, contatti, stile) li decide l'utente: chiedili
  prima di impaginare, non inventarli.
