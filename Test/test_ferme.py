from unittest.mock import MagicMock, patch
from ferme.minimal_logiciel import PlayerGameClient
from ferme.employer import GestionnairePersonnel

def test_client_demarrage_jour_0():
    """
    Vérifie que le client lance bien les commandes de démarrage obligatoires
    lorsque le serveur annonce le jour 0.
    """
    with patch("chronobio.network.client.Client.__init__", return_value=None):
        bot = PlayerGameClient("bidon", 0, "La_grande_folie")
        bot.username = "La_grande_folie"
    donnees_entree = {
        "day": 0,
        "farms": [{"name": "La_grande_folie", "cash": 1000}]
    }
    
    # On configure le bot pour lire ces données puis s'arrêter
    bot.read_json = MagicMock(side_effect=[donnees_entree, StopIteration])
    bot.send_json = MagicMock()
    try:
        bot.run()
    except StopIteration:
        pass 
    
    # Vérifications
    assert bot.send_json.called, "Le bot aurait dû envoyer des commandes !"
    message_envoye = bot.send_json.call_args[0][0]
    commandes = message_envoye["commands"]

    # On vérifie la liste des courses du jour 0
    assert "0 EMPRUNTER 100000" in commandes
    assert commandes.count("0 ACHETER_CHAMP") == 3
    assert commandes.count("0 ACHETER_TRACTEUR") == 2
    assert commandes.count("0 EMPLOYER") == 2
    assert "1 SEMER PATATE 3" in commandes


def test_rh_doit_embaucher():
    """
    Scénario : J'ai 1 champ et de l'argent.
    Règle : Cible = 1 champ + 2 = 3 employés.
    Actuel : 0 employé.
    Résultat attendu : Commande '0 EMPLOYER'.
    """
    drh = GestionnairePersonnel("MaFerme")
    
    donnees_entree = {
        "cash": 50000,
        "fields": [{"id": 1}],        
        "employees": []         
    }

    commandes = drh.gerer_effectifs(donnees_entree)

    assert "0 EMPLOYER" in commandes


def test_rh_doit_licencier():
    """
    Scénario : J'ai 0 champ (suite à une vente ou faillite) mais 2 employés.
    Règle : Cible = 0 employé.
    Actuel : 2 employés.
    Résultat attendu : Licencier le plus cher (ici celui à 2000€).
    """
    drh = GestionnairePersonnel("MaFerme")
    
    donnees_entree = {
        "cash": 50000,   # Assez d'argent pour payer l'indemnité
        "fields": [],    # 0 champ -> On doit vider les effectifs
        "employees": [
            {"id": 10, "salary": 1000},
            {"id": 20, "salary": 2000}  # Le plus cher, il doit partir en premier
        ]
    }

    commandes = drh.gerer_effectifs(donnees_entree)

    # On vérifie qu'il y a bien une commande de licenciement pour l'ID 20
    assert "0 LICENCIER 20" in commandes