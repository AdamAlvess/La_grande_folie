import pytest
from unittest.mock import MagicMock, patch
from ferme.minimal_logiciel import PlayerGameClient
from ferme.Finance_manager import FinanceManager
from ferme.employer import GestionnairePersonnel
from ferme.cultiver import Cultiver
from ferme.usine import Usine

# --- TEST CLIENT ---
def test_client_demarrage_jour_0():
    """Vérifie que le client envoie bien les commandes de départ."""
    with patch("chronobio.network.client.Client.__init__", return_value=None):
        bot = PlayerGameClient("bidon", 0, "La_grande_folie")
        bot.username = "La_grande_folie"
    
    donnees_entree = {
        "day": 0,
        "farms": [{"name": "La_grande_folie", "cash": 1000}]
    }
    
    bot.read_json = MagicMock(side_effect=[donnees_entree, StopIteration])
    bot.send_json = MagicMock()
    try:
        bot.run()
    except StopIteration:
        pass 
    
    assert bot.send_json.called
    message_envoye = bot.send_json.call_args[0][0]
    commandes = message_envoye["commands"]
    assert "0 EMPRUNTER 100000" in commandes

# --- TEST FINANCE MANAGER ---
class TestFinance:
    @pytest.fixture
    def manager(self):
        return FinanceManager()

    def test_jour_0_doit_emprunter(self, manager):
        # Jour 0 : On a 1000€, on doit emprunter
        fake_data = {
            "cash": 1000,
            "fields": [], "tractors": [], "loans": [], "employees": []
        }
        actions = manager.get_manager_action(fake_data, day=0)
        assert "0 EMPRUNTER 100000" in actions

    def test_emprunt_secours(self, manager):
        # Cash < 2000 -> Emprunt de secours
        fake_data = {
            "cash": 500, 
            "fields": [], "tractors": [], "loans": [], "employees": []
        }
        actions = manager.get_manager_action(fake_data, day=10)
        assert "0 EMPRUNTER 100000" in actions

    def test_pas_emprunt_si_riche(self, manager):
        # Cash 12000 > 2000 -> Pas d'emprunt
        fake_data = {
            "cash": 12000, 
            "fields": [], "tractors": [], "loans": [], "employees": []
        }
        actions = manager.get_manager_action(fake_data, day=10)
        # S'il n'y a pas d'achat possible, ça renvoie une liste vide
        assert "0 EMPRUNTER 100000" not in actions

    def test_achat_tracteur_prioritaire(self, manager):
        # 2 Champs achetés, 0 Tracteur -> Achat Tracteur
        fake_data = {
            "cash": 100000,
            "fields": [{"id": 1, "bought": True}, {"id": 2, "bought": True}],
            "tractors": [], 
            "loans": [], "employees": []
        }
        actions = manager.get_manager_action(fake_data, day=10)
        assert "0 ACHETER_TRACTEUR" in actions

    def test_achat_champ_si_equilibre(self, manager):
        # 1 Champ, 1 Tracteur -> Achat Champ 2
        fake_data = {
            "cash": 100000,
            "fields": [{"id": 1, "bought": True}],
            "tractors": [{"id": 1}], 
            "loans": [], "employees": []
        }
        actions = manager.get_manager_action(fake_data, day=10)
        assert "0 ACHETER_CHAMP" in actions

# --- TEST EMPLOYER (RH) ---
class TestRH:
    @pytest.fixture
    def drh(self):
        return GestionnairePersonnel("MaFerme")

    def test_rh_embauche(self, drh):
        # Assez d'argent + Besoin (1 champ = cible 9)
        fake_data = {
            "cash": 200000,
            "fields": [{"id": 1, "bought": True}],
            "employees": [] # 0 employé
        }
        cmds = drh.gerer_effectifs(fake_data)
        assert "0 EMPLOYER" in cmds

    def test_rh_licencie_crise(self, drh):
        # Crise (< 20k) et trop d'employés
        # On crée 50 employés pour être sûr d'être en sureffectif
        employees = [{"id": i, "salary": 1000} for i in range(50)]
        fake_data = {
            "cash": 5000, # Crise mais assez pour indemnité
            "fields": [{"id": 1, "bought": True}],
            "employees": employees
        }
        cmds = drh.gerer_effectifs(fake_data)
        # Doit licencier quelqu'un
        assert any("LICENCIER" in cmd for cmd in cmds)

# --- TEST CULTIVER (NOUVELLE LOGIQUE) ---
class TestCultiver:
    @pytest.fixture
    def strat(self):
        return Cultiver()

    def test_ne_fait_rien_si_pas_de_tracteur(self, strat):
        # Champ 1, Ouvrier 7, Tracteur 1 assigné MAIS PAS DANS LA LISTE
        farm = {
            "blocked": False,
            "fields": [{"id": 1, "bought": True, "content": "NONE", "needed_water": 0}],
            "employees": [{"id": "7", "action": "IDLE"}],
            "tractors": [] # Pas de tracteur acheté
        }
        
        # On appelle la nouvelle fonction
        cmds = strat.gerer_un_champ_specifique(
            farm, day=10, cash=5000, 
            target_field_id=1, assigned_workers=[7], assigned_tractor_id=1
        )
        # DOIT ÊTRE VIDE (Pas de tracteur = Pas de plantation)
        assert cmds == []

    def test_ne_fait_rien_si_employe_fantome(self, strat):
        # On demande à l'employé 7 de travailler, mais il n'est pas dans la liste
        farm = {
            "blocked": False,
            "fields": [{"id": 1, "bought": True, "content": "NONE", "needed_water": 0}],
            "employees": [{"id": "1", "action": "IDLE"}], # Seul l'employé 1 existe
            "tractors": [{"id": "1", "content": "EMPTY", "location": "FARM"}]
        }
        
        cmds = strat.gerer_un_champ_specifique(
            farm, day=10, cash=5000, 
            target_field_id=1, assigned_workers=[7], assigned_tractor_id=1
        )
        # DOIT ÊTRE VIDE (Ouvrier 7 n'existe pas)
        assert cmds == []

    def test_seme_si_tout_ok(self, strat):
        # Tout est là : Ouvrier 7, Tracteur 1, Champ 1 vide
        farm = {
            "blocked": False,
            "fields": [{"id": 1, "bought": True, "content": "NONE", "needed_water": 0}],
            "employees": [{"id": "7", "action": "IDLE"}],
            "tractors": [{"id": "1", "content": "EMPTY", "location": "FARM"}]
        }
        
        cmds = strat.gerer_un_champ_specifique(
            farm, day=10, cash=5000, 
            target_field_id=1, assigned_workers=[7], assigned_tractor_id=1
        )
        assert len(cmds) == 1
        assert "7 SEMER" in cmds[0]

# --- TEST USINE ---
class TestUsine:
    @pytest.fixture
    def usine(self):
        return Usine()

    def test_usine_cuisine(self, usine):
        farm = {
            "blocked": False,
            "soup_factory": {"stock": {"POTATO": 100}},
            "employees": [{"id": "1", "action": "IDLE"}]
        }
        # On utilise ids_autorises
        cmds = usine.execute(farm, day=10, ids_autorises=[1])
        assert len(cmds) == 1
        assert "1 CUISINER" in cmds[0]

    def test_usine_respecte_whitelist(self, usine):
        farm = {
            "blocked": False,
            "soup_factory": {"stock": {"POTATO": 100}},
            "employees": [{"id": "99", "action": "IDLE"}] # Ouvrier 99
        }
        # On autorise seulement l'ID 1
        cmds = usine.execute(farm, day=10, ids_autorises=[1])
        # L'ouvrier 99 ne doit pas cuisiner
        assert cmds == []