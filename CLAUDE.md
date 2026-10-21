# Volantino A6 — istruzioni per Claude

Obiettivo: progettare un volantino A6 (fronte e retro) pronto per la tipografia,
usando le app ArtCraft tramite MCP. Le specifiche di stampa sono nel README.

## All'avvio della sessione

1. Controlla che `photocraft-cli --version` funzioni.
   - Se manca: esegui `bash scripts/installa-artcraft.sh` (circa 7 minuti), poi
     di' all'utente di aprire una nuova sessione perché i tool MCP compaiono solo all'avvio.
     Nel frattempo puoi lavorare con la CLI (`photocraft-cli run/convert/info`).
2. Se i tool MCP `photocraft` sono disponibili, usali al posto della CLI.

## Regole di lavoro

- Formato file: 1311 × 1819 px a 300 dpi (A6 + 3 mm di abbondanza).
  Testi e loghi a almeno 95 px dal bordo del file.
- Sorgenti modificabili in `lavoro/` (`fronte.pcraft`, `retro.pcraft`), mai solo l'export.
- File finali e anteprime in `export/`. Prima di dire che un file è pronto,
  genera un'anteprima (`doc_render_preview` o export PNG) e guardala.
- Materiale fornito dall'utente in `risorse/`: non modificarlo, lavora su copie.
- La modalità "bridged" (agganciarsi all'app aperta sul PC) non funziona nel cloud:
  si lavora solo sui file.
- I contenuti (testi, offerta, contatti, stile) li decide l'utente: chiedili
  prima di impaginare, non inventarli.
