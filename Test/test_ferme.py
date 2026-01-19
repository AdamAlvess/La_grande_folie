import pytest
from unittest.mock import MagicMock, patch

# --- C'EST ICI QUE J'AI CORRIGÉ L'IMPORT POUR GARDER TON NOM DE FICHIER ---
from ferme.Finance_manager import FinanceManager 

# Si tu as besoin du client pour le premier test :
from ferme.minimal_logiciel import PlayerGameClient 

# --- TESTS DU CLIENT (JOUR 0) ---

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


# --- TESTS FINANCE MANAGER INDÉPENDANT ---

class TestFinance:
    
    @pytest.fixture
    def manager(self):
        return FinanceManager()

    # --- JOUR 0 ---
    def test_jour_0_doit_emprunter_massivement(self, manager):
        fake_data = {
            "cash": 1_000,
            "fields": [],
            "tractors": [],
            "loans": [], 
            "employees": []
        }
        # Au jour 0, le manager doit sécuriser 100k direct
        action = manager.get_manager_action(fake_data, day=0)
        assert action == "0 EMPRUNTER 100000"

    # --- SURVIE FINANCIÈRE ---
    def test_doit_emprunter_si_tresorerie_basse(self, manager):
        # DOIT EMPRUNTER OU NON ??? 
        # Cash 12k < Buffer 15k -> OUI
        fake_data = {
            "cash": 12_000,
            "fields": [],
            "tractors": [],
            "loans": [{"amount": 100_000}], # Déjà un emprunt en cours
            "employees": [] 
        }
        # On force le compteur interne pour dire qu'on n'a pas atteint le max
        manager.nb_emprunts_total = 1 
        
        action = manager.get_manager_action(fake_data, day=10)
        assert action == "0 EMPRUNTER 100000"

    # --- LES CHAMPS ---
    def test_achat_champ_si_assez_argent(self, manager):
        # Cash 40k. Buffer 15k. Reste 25k. Prix champ 10k. -> OK
        fake_data = {
            "cash": 40_000,
            "fields": [{"id": 1}], # 1 champ existant
            "tractors": [{"id": 1}],
            "loans": [],
            "employees": []
        }
        action = manager.get_manager_action(fake_data, day=5)
        assert action == "0 ACHETER_CHAMP"

    def test_stop_achat_champ_si_max_atteint(self, manager):
        # J'ai déjà 5 champs (Max) -> Doit passer aux tracteurs
        fake_data = {
            "cash": 100_000,
            "fields": [{"id": i} for i in range(5)], 
            "tractors": [],
            "loans": [],
            "employees": []
        }
        action = manager.get_manager_action(fake_data, day=5)
        
        # NE DOIT PAS acheter de champ. DOIT ACHETER TRACTEUR
        assert action == "0 ACHETER_TRACTEUR"

    # --- TRACTEURS ---
    def test_achat_tracteur_si_besoin(self, manager): 
        # J'ai 2 champs mais 0 tracteur -> Besoin de tracteur
        fake_data = {
            "cash": 80_000, # Riche
            "fields": [{"id": 1}, {"id": 2}],
            "tractors": [],
            "loans": [],
            "employees": []
        }
        action = manager.get_manager_action(fake_data, day=5)
        assert action == "0 ACHETER_TRACTEUR"

    def test_tracteur_limite_globale_50(self, manager):
        # J'ai déjà 50 tracteurs -> IN-TER-DICTION d'en acheter
        fake_data = {
            "cash": 900_000,
            "fields": [{"id": i} for i in range(5)],
            "tractors": [{"id": i} for i in range(50)], 
            "loans": [],
            "employees": []
        }
        action = manager.get_manager_action(fake_data, day=5)
        assert action is None # On est au max partout

    # --- TEST CRUCIAL : SALAIRES ET EMPRUNTS ---
    def test_charges_bloquent_investissements(self, manager):
        """
        Vérifie que le remboursement des prêts + salaires bloque l'achat.
        Scenario:
        Cash: 35 000
        - Buffer: 15 000
        - Salaires (10 emp): ~12 000
        - Emprunt (100k): ~4 583 ((100000*1.1)/24)
        
        Reste dispo : 35000 - 15000 - 12000 - 4583 = 3 417 €
        Prix Tracteur : 30 000 € -> IMPOSSIBLE
        Prix Champ : 10 000 € -> IMPOSSIBLE
        """
        fake_data = {
            "cash": 35_000,
            "fields": [],
            "tractors": [],
            "loans": [{"amount": 100_000}], 
            "employees": [{"id": i} for i in range(10)]
        }
        action = manager.get_manager_action(fake_data, day=5)
        assert action is None

    # --- FIN DE PARTIE ---
    def test_fin_de_partie_stop_investissements(self, manager):
        """Vérifie qu'on arrête d'acheter à la fin pour garder le cash (Score)."""
        fake_data = {
            "cash": 1_000_000, 
            "fields": [],
            "tractors": [],
            "loans": [],
            "employees": []
        }
        # Jour 1750 (Fin du jeu proche)
        action = manager.get_manager_action(fake_data, day=1750)
        assert action is None