from unittest.mock import MagicMock, patch
from ferme.minimal_logiciel import PlayerGameClient
from ferme.employer import GestionnairePersonnel
import pytest
from ferme.cultiver import Cultiver

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


# --- FIXTURES (Données de base pour les tests) ---
@pytest.fixture
def strat():
    """Crée une instance toute neuve de Cultiver avant chaque test."""
    return Cultiver()

@pytest.fixture
def ferme_base():
    """Une ferme standard pour les tests."""
    return {
        "blocked": False,
        "money": 10000,
        "fields": [],
        "employees": [],
        "tractors": [],
        "soup_factory": {"stock": {"POTATO": 0}}
    }

# --- TESTS ---

def test_jour_0_ne_fait_rien(strat, ferme_base):
    # Au jour 0, on ne doit rien renvoyer
    cmds = strat.execute(ferme_base, day=0, cash=10000)
    assert cmds == []

def test_ferme_bloquee(strat, ferme_base):
    # Si la ferme est bloquée, silence radio
    ferme_base["blocked"] = True
    cmds = strat.execute(ferme_base, day=10, cash=10000)
    assert cmds == []

def test_semer_patate(strat, ferme_base):
    # SCÉNARIO : Champ 2 vide, Employé 2 libre, Assez d'argent
    ferme_base["fields"] = [
        {"content": "NONE", "needed_water": 0} # Champ 1 (ignoré par défaut par Cultiver?) Non, il prend tout maintenant
    ]
    # Attention: dans ton __init__, l'employé 1 est bloqué jusqu'au jour 6 !
    # On utilise donc l'employé 2 pour ce test.
    ferme_base["employees"] = [{"id": 2, "action": "IDLE"}]
    
    cmds = strat.execute(ferme_base, day=10, cash=5000)
    
    assert len(cmds) == 1
    assert "2 SEMER PATATE 1" in cmds[0]
    
    # Vérification du verrouillage mémoire (5 jours pour semer)
    assert strat.employee_busy_until[2] == 10 + 5
    assert strat.field_busy_until[1] == 10 + 5

def test_pas_d_argent_pour_semer(strat, ferme_base):
    # SCÉNARIO : Champ vide mais seulement 100€ en poche (il faut 1000)
    ferme_base["fields"] = [{"content": "NONE", "needed_water": 0}]
    ferme_base["employees"] = [{"id": 2, "action": "IDLE"}]
    
    cmds = strat.execute(ferme_base, day=10, cash=100) # Pauvre
    
    assert cmds == [] # Rien ne se passe

def test_arroser_champ(strat, ferme_base):
    # SCÉNARIO : Champ 1 a besoin d'eau
    ferme_base["fields"] = [{"content": "POTATO", "needed_water": 5}]
    ferme_base["employees"] = [{"id": 2, "action": "IDLE"}]
    
    cmds = strat.execute(ferme_base, day=10, cash=5000)
    
    assert len(cmds) == 1
    assert "2 ARROSER 1" in cmds[0]
    
    # Vérification du verrouillage mémoire (2 jours pour arroser)
    assert strat.employee_busy_until[2] == 10 + 2

def test_stocker_recolte(strat, ferme_base):
    # SCÉNARIO : Champ 1 prêt (Eau=0, Contenu!=NONE) + Tracteur dispo
    ferme_base["fields"] = [{"content": "POTATO", "needed_water": 0}]
    ferme_base["employees"] = [{"id": 2, "action": "IDLE"}]
    ferme_base["tractors"] = [{"id": 1, "content": "EMPTY"}]
    
    cmds = strat.execute(ferme_base, day=10, cash=5000)
    
    assert len(cmds) == 1
    assert "2 STOCKER 1 1" in cmds[0] # Emp 2, Champ 1, Tracteur 1
    
    # Vérification du verrouillage mémoire (5 jours pour stocker)
    assert strat.tractor_busy_until[1] == 10 + 5

def test_stocker_sans_tracteur(strat, ferme_base):
    # SCÉNARIO : Champ prêt MAIS aucun tracteur
    ferme_base["fields"] = [{"content": "POTATO", "needed_water": 0}]
    ferme_base["employees"] = [{"id": 2, "action": "IDLE"}]
    ferme_base["tractors"] = [] # Liste vide
    
    cmds = strat.execute(ferme_base, day=10, cash=5000)
    
    assert cmds == [] # On ne peut pas stocker sans tracteur

def test_employe_occupe_serveur(strat, ferme_base):
    # SCÉNARIO : L'employé travaille déjà selon le serveur
    ferme_base["fields"] = [{"content": "POTATO", "needed_water": 5}]
    ferme_base["employees"] = [{"id": 2, "action": "WATER"}] # Il bosse déjà
    
    cmds = strat.execute(ferme_base, day=10, cash=5000)
    
    assert cmds == [] # On ne doit pas lui donner d'ordre

def test_employe_occupe_memoire(strat, ferme_base):
    # SCÉNARIO : L'employé est libre pour le serveur, mais notre mémoire dit NON
    ferme_base["fields"] = [{"content": "POTATO", "needed_water": 5}]
    ferme_base["employees"] = [{"id": 2, "action": "IDLE"}]
    
    # On simule qu'il est occupé jusqu'au jour 15
    strat.employee_busy_until[2] = 15
    
    cmds = strat.execute(ferme_base, day=10, cash=5000)
    
    assert cmds == []

def test_employe_1_bloque_au_debut(strat, ferme_base):
    # SCÉNARIO : Vérifier que l'employé 1 est bien ignoré au début (fix J0)
    ferme_base["fields"] = [{"content": "NONE", "needed_water": 0}]
    ferme_base["employees"] = [{"id": 1, "action": "IDLE"}]
    
    # Au jour 3, il devrait être encore bloqué (lock jusqu'à 6)
    cmds = strat.execute(ferme_base, day=3, cash=5000)
    assert cmds == []
    
    # Au jour 7, il doit être libre
    cmds = strat.execute(ferme_base, day=7, cash=5000)
    assert len(cmds) == 1
    assert "1 SEMER" in cmds[0]


    