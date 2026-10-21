#!/usr/bin/env bash
# Installa per l'utente corrente i font del progetto (risorse/font/**/*.ttf) e aggiorna la cache,
# così PhotoCraft li vede in type.fonts. Da eseguire a ogni nuova sessione cloud.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p ~/.local/share/fonts
cp -f risorse/font/*/*.ttf ~/.local/share/fonts/
fc-cache -f >/dev/null 2>&1 || true
echo "Font installati: $(ls risorse/font/*/*.ttf | wc -l) (Bebas Neue, Anton, Montserrat, Kaushan Script)"
