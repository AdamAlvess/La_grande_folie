#!/bin/bash

rm -rf .venv

# 1. On définit une fonction qui va tout tuer proprement
cleanup() {
    echo ""
    echo "🛑 Arrêt de la simulation (nettoyage des processus)..."
    # "kill 0" envoie un signal à tous les processus du groupe (le script et ses enfants)
    kill 0
}

# 2. On piège le signal de sortie (CTRL+C ou fin de script)
# Dès que le script s'arrête, il lance la fonction 'cleanup'
trap cleanup SIGINT EXIT

# 3. Sélection du port
PORT=$(uv run python -c "import random; print(random.randint(2000, 3000))")
echo "🎮 Port sélectionné : $PORT"
echo "-----------------------------------"

# 4. Lancement des commandes
# Le '&' à la fin lance la commande en tâche de fond (background)

echo "🚀 Lancement du SERVEUR..."
uv run python -m chronobio.game.server -p $PORT &
# On laisse une petite seconde pour être sûr que le serveur est up avant les autres
sleep 1 

echo "📺 Lancement du VIEWER..."
uv run python -m chronobio.viewer -p $PORT --width 1100 --height 700 &

echo "🚜 Lancement de la FERME..."
# IMPORTANT : La dernière commande, on ne met PAS de '&'.
# Comme ça, le script reste "bloqué" ici tant que la ferme tourne.
# Si tu fais Ctrl+C ici, ça déclenche le trap et tout le monde ferme.
uv run python -m ferme.minimal_logiciel -p $PORT