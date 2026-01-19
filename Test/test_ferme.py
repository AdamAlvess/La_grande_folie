import math 
from unittest.mock import MagicMock, patch
from ferme.finance import GestionnaireFinance
from ferme.employer import GestionnairePersonnel
from ferme.cultiver import Cultiver
import pytest


class GestionnaireFinance:
    def __init__(self):
        self.nb_emprunts = 0
        self.max_champs = 5
        self.max_tracteurs = 50
        self.buffer_secu = 15_000 # Buffer, pour éviter la banqueroute

    def get_manager_action(self, data: Dict, day: int) -> Optional[str]:
        # Arrêt des investissements à la fin du jeu (5 ans = 1800 jours), on garde le cash pour le score final à partir du jour 1680
        if day > 1679:
            return None

        cash = data.get("cash", 0)
        champs = data.get("fields", [])
        tracteurs = data.get("tractors", [])
        loans = data.get("loans", [])
        employees = data.get("employees", [])

        # CALCUL MATHÉMATIQUE DES CHARGES ; salaires estimés : nb_emp * 1200 (marge incluse)
        frais_salaires = len(employees) * 1200
        
        # Remboursements : (Somme * 1.1) / 24 mois ; Note : On calcule la mensualité pour vérifier la solvabilité mensuelle
        frais_emprunts = sum([int((l["amount"] * 1.1) / 24) for l in loans])
        
        charges_totales = frais_salaires + frais_emprunts
        cash_disponible = cash - self.buffer_secu - charges_totales

        # --- DÉCISION DU GÉRANT (1 action max par jour) ---

        # 1. SURVIE : Emprunter si cash trop bas
        # Attention : Limite de 10 emprunts sur toute la partie
        if cash < self.buffer_secu and self.nb_emprunts < 10:
            self.nb_emprunts += 1
            return "0 EMPRUNTER 100000"

        # 2. EXPANSION : Acheter un champ (10 000€)
        if len(champs) < self.max_champs and cash_disponible >= 10000:
            return "0 ACHETER_CHAMP"

        # 3. OPTIMISATION : Acheter un tracteur (30 000€)
        # On n'achète un tracteur que si on a un champ qui n'en a pas
        if len(tracteurs) < len(champs) and len(tracteurs) < self.max_tracteurs and cash_disponible >= 30000:
            return "0 ACHETER_TRACTEUR"

        return None


# --- TEST FINANCE MANAGER INDÉPENDANT ---

class TestFinance:
    @pytest.fixture
    def manager(self):
        return GestionnaireFinance()

    # JOUR 0
    def test_jour_0_doit_emprunter_massivement(self, manager):
        fake_data = {
            "cash": 1_000,
            "fields": [],
            "tractors": [],
            "loans": [], 
            "employees": []
        }
        # Au jour 0, priorité absolue à l'argent
        action = manager.get_manager_action(fake_data, day=0)
        assert action == "0 EMPRUNTER 100000"

    # SURVIE FINANCIÈRE
    def test_doit_emprunter_si_tresorerie_basse(self, manager):
        # DOIT EMPRUNTER OU NON ??? Oui car 12k < 15k buffer + charges
        fake_data = {
            "cash": 12_000,
            "fields": [],
            "tractors": [],
            "loans": [],
            "employees": [] 
        }
        action = manager.get_manager_action(fake_data, day=10)
        assert action == "0 EMPRUNTER 100000"

    # LES CHAMPS
    def test_achat_champ_si_assez_argent(self, manager):
        # dans l'idée, si j'ai au moins 15K + charges, je peux acheter un champ
        fake_data = {
            "cash": 40000,
            "fields": [{"id": 1}], # J'ai 1 champ, je peux en avoir jusqu'à 5 max
            "tractors": [{"id": 1}], # J'ai déjà un tracteur pour ce champ
            "loans": [],
            "employees": []
        }
        action = manager.get_manager_action(fake_data, day=5)
        assert action == "0 ACHETER_CHAMP"

    def test_stop_achat_champ_si_max_atteint(self, manager):
        # J'ai déjà 5 champs (Max)
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

    # TRACTEURS
    def test_achat_tracteur_si_besoin(self, manager): 
        # J'ai 2 champs mais 0 tracteur -> Besoin de tracteur
        fake_data = {
            "cash": 80000, # Large niveau argent
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
            "cash": 900000,
            "fields": [{"id": i} for i in range(5)],
            "tractors": [{"id": i} for i in range(50)], 
            "loans": [],
            "employees": []
        }
        action = manager.get_manager_action(fake_data, day=5)
        assert action is None # On est au max partout

    # --- TEST 5 : SALAIRES ET SÉCURITÉ ---
    def test_salaires_bloquent_investissements(self, manager):
        """Test crucial : vérifie que le salaire des employés est déduit du cash dispo."""
        # CALCUL MATHÉMATIQUE : Cash total : 35 000
        # Buffer sécu : - 15 000
        # Salaires : 10 employés * 1200 (marge) = - 12 000
        # Cash vraiment disponible = 35k - 15k - 12k = 8 000
        # 8 000 < 10 000 (Prix champ) -> On ne peut PAS acheter le champ
        
        fake_data = {
            "cash": 35000,
            "fields": [],
            "tractors": [],
            "loans": [],
            "employees": [{"id": i} for i in range(10)]
        }
        action = manager.get_manager_action(fake_data, day=5)
        assert action is None

    def test_fin_de_partie_stop_investissements(self, manager):
        """Vérifie qu'on arrête d'acheter à la fin pour garder le cash (Score)."""
        fake_data = {
            "cash": 1_000_000, # Riche
            "fields": [],
            "tractors": [],
            "loans": [],
            "employees": []
        }
        # Jour 1750 (Fin du jeu proche)
        action = manager.get_manager_action(fake_data, day=1750)
        assert action is None