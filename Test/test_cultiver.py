import pytest
from ferme.cultiver import Cultiver

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