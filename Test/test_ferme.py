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



#TEST FINANCE MANAGER INDÉPENDANT



                # JOUR 0
def test_jour_0_doit_emprunter_massivement(self):
    fake_data = {
        "cash": 1_000,
        "fields": [],
        "tractors": [],
        "loans": [], # 0 -> emprunt
        "employees": []
    }
    
    action = self.manager.get_manager_action(fake_data, day=0)
    
    assert action == "0 EMPRUNTER 100000"

            # SURVIE FINANCIÈRE
def test_doit_emprunter_si_tresorerie_basse(self):
#DOIT EMPRUNTER OU NON ???
    fake_data = {
        "cash": 16_000,
        "fields": [],
        "tractors": [],
        "loans": [{"amount": 100_000}], #existant?
        "employees": [] 
    }

    action = self.manager.get_manager_action(fake_data, day=10)
    
    assert action == "0 EMPRUNTER 100000"

            # LES CHAMPS
def test_achat_champ_si_assez_argent(self):
    #dans l'idée, si j'ai au moins 15K, je peux acheter un champ
    fake_data = {
        "cash": 30000,
        "fields": [{"id": 1}], # J'ai 1 champ, je peux en avoir jusqu'à 5 max
        "tractors": [],
        "loans": [{"amount": 100_000}] * 3, # On bloque les emprunts pour tester l'achat
        "employees": []
    }

    action = self.manager.get_manager_action(fake_data, day=5)
    
    assert action == "0 ACHETER_CHAMP"

def test_stop_achat_champ_si_max_atteint(self):
    # J'ai déjà 5 champs (Max)
    fake_data = {
        "cash": 100_000,
        "fields": [{"id": i} for i in range(5)], 
        "tractors": [],
        "loans": [{"amount": 100_000}] * 3,
        "employees": []
    }

    action = self.manager.get_manager_action(fake_data, day=5)
    
# NE DOIT PAS acheter de champ. VOIR POUR ACHETER TRACTEUR D'URGENCE 
    assert action == "0 ACHETER_TRACTEUR"

                # TRACTEURS
def test_achat_tracteur_si_besoin(self): # J'ai 2 champs mais 0 tracteur -> Besoin de tracteur
    fake_data = {
        "cash": 50000, # Large niveau argent
        "fields": [{"id": 1}, {"id": 2}],
        "tractors": [],
        "loans": [{"amount": 100000}] * 3,
        "employees": []
    }

    action = self.manager.get_manager_action(fake_data, day=5)
    
    assert action == "0 ACHETER_TRACTEUR"

def test_tracteur_limite_globale_50(self):
    # J'ai déjà 50 tracteurs -> IN-TER-DICTION d'en acheter
    fake_data = {
        "cash": 900000,
        "fields": [{"id": i} for i in range(5)],
        "tractors": [{"id": i} for i in range(50)], # 50 tracteurs
        "loans": [{"amount": 100000}] * 3,
        "employees": []
    }

    action = self.manager.get_manager_action(fake_data, day=5)
    
    assert action is None # Rien à faire, on est au max partout

# --- TEST 5 : SALAIRES ET SÉCURITÉ ---
def test_salaires_bloquent_investissements(self):
    """Test crucial : vérifie que le salaire des employés est déduit du cash dispo."""
    
    # CALCUL MATHÉMATIQUE : Cash total : 35 000
    #Buffer sécu : - 15 000
    # Salaires : 10 employés * 1200 (marge) = - 12 000
    
    # Cash vraiment disponible = 35k - 15k - 12k = 8 000
    
    # 8 000 < 10 000 (Prix champ) -> On ne peut PAS acheter le champ
    # 8 000 > 5 000 (Seuil emprunt) -> On n'a pas besoin d'emprunter

    # Résultat attendu : None
    
    fake_data = {
        "cash": 35000,
        "fields": [],
        "tractors": [],
        "loans": [{"amount": 100000}] * 3, # Pas d'emprunt possible
        "employees": [{"id": i} for i in range(10)]
    }

    action = self.manager.get_manager_action(fake_data, day=5)
    
    assert action is None