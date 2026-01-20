import subprocess
import sys
import time
import random
import shutil
import os
import signal

# 1. Nettoyage initial (équivalent du rm -rf .venv)
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
processes = []

def kill_everything(signum=None, frame=None):
    """Fonction pour tout tuer proprement quand on quitte."""
    print("\n🛑 Arrêt de la simulation (nettoyage)...")
    for p in processes:
        p.terminate()
        
    time.sleep(0.5)
    sys.exit(0)

signal.signal(signal.SIGINT, kill_everything)
signal.signal(signal.SIGTERM, kill_everything)

try:
    # 3. Lancement des commandes
    print("🚀 Lancement du SERVEUR...")
    p_server = subprocess.Popen(["uv", "run", "python", "-m", "chronobio.game.server", "-p", port])
    processes.append(p_server)
    time.sleep(1) 

    # Commande 2 : VIEWER
    print("📺 Lancement du VIEWER...")
    p_viewer = subprocess.Popen(["uv", "run", "python", "-m", "chronobio.viewer", "-p", port, "--width", "1100", "--height", "700"])
    processes.append(p_viewer)

    # Commande 3 : FERME
    print("🚜 Lancement de la FERME...")
    p_farm = subprocess.Popen(["uv", "run", "python", "-m", "ferme.minimal_logiciel", "-p", port])
    processes.append(p_farm)

    # 4. Boucle infinie pour garder le script en vie
    while True:
        time.sleep(1)
        if p_farm.poll() is not None:
            print("La ferme s'est arrêtée. Fermeture générale.")
            kill_everything()

except KeyboardInterrupt:
    kill_everything()