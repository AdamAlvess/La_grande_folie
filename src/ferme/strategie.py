from ferme.cultiver import Cultiver
from ferme.employer import GestionnairePersonnel 
from ferme.usine import Usine

class FarmStrategy:
    def __init__(self, nom_ferme: str):
        self.nom_ferme = nom_ferme
        
        # On initialise nos experts
        self.cultivator = Cultiver()
        self.drh = GestionnairePersonnel(nom_ferme)
        self.chef_cuisine = Usine()

    def _extraire_ids_occupes(self, commandes: list[str]) -> list[int]:
        ids = []
        for cmd in commandes:
            parts = cmd.split()
            if parts[0].isdigit() and parts[0] != "0":
                ids.append(int(parts[0]))
        return ids

    def jouer_tour(self, game_data: dict) -> list[str]:
        commandes: list[str] = []
        
        ma_ferme = None
        for ferme in game_data["farms"]:
            if ferme["name"] == self.nom_ferme:
                ma_ferme = ferme
                break
        
        if not ma_ferme:
            return []
        
        if ma_ferme.get("blocked", False):
            print(f"🛑 [STRATÉGIE] Ferme bloquée au jour {game_data['day']}.")
            return []

        day = game_data["day"]
        cash = ma_ferme.get("cash", ma_ferme.get("money", 0))

        # --- 1. AGRICULTURE ---
        commandes_agriculture = self.cultivator.gerer_cultiver(ma_ferme, day, cash)
        commandes.extend(commandes_agriculture)
        
        # --- 2. USINE (Sécurité renforcée + Debug) ---
        
        # 1. Ceux qui travaillent ce tour-ci
        ids_commandes_jour = self._extraire_ids_occupes(commandes_agriculture)
        
        # 2. Ceux bloqués dans TA mémoire
        ids_memoire = [
            int(e_id) for e_id, fin in self.cultivator.employee_busy_until.items()
            if fin >= day
        ]
        
        # 3. Ceux bloqués par le SERVEUR (Sécurité ultime)
        # On force la conversion en int pour être sûr
        ids_serveur_occupes = []
        for emp in ma_ferme["employees"]:
            if emp.get("action", "IDLE") != "IDLE":
                ids_serveur_occupes.append(int(emp["id"]))
        
        # On combine tout (set élimine les doublons)
        tous_les_exclus = list(set(ids_commandes_jour + ids_memoire + ids_serveur_occupes))

        # DEBUG : Pour comprendre pourquoi ça plante, décommentez la ligne ci-dessous
        # print(f"🚫 EXCLUS USINE J{day}: {tous_les_exclus}")

        commandes_usine = self.chef_cuisine.execute(ma_ferme, day, excluded_ids=tous_les_exclus)
        commandes.extend(commandes_usine)

        # --- 3. RH ---
        commandes_rh = self.drh.gerer_effectifs(ma_ferme)
        commandes.extend(commandes_rh)

        return commandes