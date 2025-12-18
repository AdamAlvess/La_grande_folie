import subprocess
import sys
import time
import random
import shutil
import os
import signal

# 1. Nettoyage initial (équivalent du rm -rf .venv)
# On le fait en Python pour que ça marche sur Windows aussi
if os.path.exists(".venv"):
    print("🧹 Suppression du dossier .venv...")
    try:
        shutil.rmtree(".venv")
    except PermissionError:
        print("⚠️ Impossible de supprimer .venv (peut-être utilisé ?), on continue quand même.")

# 2. Sélection du port
port = str(random.randint(2000, 3000))
print(f"🎮 Port sélectionné : {port}")
print("-----------------------------------")

# Liste pour stocker nos processus
processes = []

def kill_everything(signum=None, frame=None):
    """Fonction pour tout tuer proprement quand on quitte."""
    print("\n🛑 Arrêt de la simulation (nettoyage)...")
    for p in processes:
        # On tente de terminer proprement
        p.terminate()
        
    # Petite pause pour laisser le temps de fermer
    time.sleep(0.5)
    sys.exit(0)

# On intercepte le CTRL+C (SIGINT)
signal.signal(signal.SIGINT, kill_everything)
# Sur Windows, SIGTERM n'est pas toujours envoyé, mais on le met par sécurité
signal.signal(signal.SIGTERM, kill_everything)

try:
    # 3. Lancement des commandes
    # On utilise sys.executable pour être sûr d'utiliser le python courant si besoin, 
    # mais ici tu utilises 'uv', donc on appelle 'uv' directement.
    
    # Commande 1 : SERVEUR
    print("🚀 Lancement du SERVEUR...")
    p_server = subprocess.Popen(["uv", "run", "python", "-m", "chronobio.game.server", "-p", port])
    processes.append(p_server)
    time.sleep(1) # Pause de sécurité

    # Commande 2 : VIEWER
    print("📺 Lancement du VIEWER...")
    p_viewer = subprocess.Popen(["uv", "run", "python", "-m", "chronobio.viewer", "-p", port, "--width", "1100", "--height", "700"])
    processes.append(p_viewer)

    # Commande 3 : FERME
    print("🚜 Lancement de la FERME...")
    # Pour la dernière, on utilise Popen aussi pour garder la main sur le script python
    # et pouvoir intercepter le CTRL+C
    p_farm = subprocess.Popen(["uv", "run", "python", "-m", "ferme.minimal_logiciel", "-p", port])
    processes.append(p_farm)

    # 4. Boucle infinie pour garder le script en vie
    # On surveille si les processus sont encore en vie
    while True:
        time.sleep(1)
        # Si la ferme (notre "main" user interaction) est fermée, on peut tout couper ?
        # Ou on attend juste le Ctrl+C de l'utilisateur.
        # Ici on attend juste le Ctrl+C.
        if p_farm.poll() is not None:
            print("La ferme s'est arrêtée. Fermeture générale.")
            kill_everything()

except KeyboardInterrupt:
    # Ce bloc attrape le CTRL+C manuel
    kill_everything()