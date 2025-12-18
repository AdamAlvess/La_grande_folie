from unittest.mock import MagicMock, patch
from ferme.minimal_logiciel import PlayerGameClient

def test_logique_metier_pure():
    # --- 1. PRÉPARATION (MOCK) ---
    with patch("chronobio.network.client.Client.__init__", return_value=None):
        bot = PlayerGameClient("bidon", 0, "La_grande_folie")
        bot.username = "La_grande_folie"


    # --- 2. INPUT (Ce que l'arbitre envoie) ---
    donnees_entree = {
        "day": 0,
        "farms": [
            {"name": "La_grande_folie", "cash": 1000}
        ]
    }
    bot.read_json = MagicMock(side_effect=[donnees_entree, StopIteration])
    bot.send_json = MagicMock()


    # --- 3. EXÉCUTION ---
    try:
        bot.run()
    except StopIteration:
        pass 
    assert bot.send_json.called, "Le bot n'a rien envoyé !"
    message_envoye = bot.send_json.call_args[0][0]
    commandes = message_envoye["commands"]

    print(f"Commandes générées : {commandes}")

    # --- 5. ASSERTIONS MÉTIER ---
    assert "0 EMPRUNTER 100000" in commandes
    assert commandes.count("0 ACHETER_CHAMP") == 3

    assert commandes.count("0 ACHETER_TRACTEUR") == 2

    assert commandes.count("0 EMPLOYER") == 2

    assert "1 SEMER PATATE 3" in commandes
