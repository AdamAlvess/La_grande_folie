from ferme.cultiver import Cultiver
from ferme.employer import GestionnairePersonnel 
from ferme.usine import Usine

class FarmStrategy:
    def __init__(self, nom_ferme: str):
        self.nom_ferme = nom_ferme
        self.cultivator = Cultiver()
        self.drh = GestionnairePersonnel(nom_ferme)
        self.chef_cuisine = Usine()

    def jouer_tour(self, game_data: dict) -> list[str]:
        commandes: list[str] = []
        ma_ferme = next((f for f in game_data["farms"] if f["name"] == self.nom_ferme), None)
        
        if not ma_ferme or ma_ferme.get("blocked", False):
            return []

        day = game_data["day"]
        cash = ma_ferme.get("cash", ma_ferme.get("money", 0))

        # --- SPECIALISATION ---
        equipe_usine = []
        # ID 4 et + -> CHAMPS
        equipe_champs = []

        for emp in ma_ferme["employees"]:
            e_id = int(emp["id"])
            if e_id <= 3: # 1, 2 et 3
                equipe_usine.append(e_id)
            else:
                equipe_champs.append(e_id)

        # 1. USINE
        cmd_usine = self.chef_cuisine.execute(ma_ferme, day, ids_autorises=equipe_usine)
        commandes.extend(cmd_usine)

        # 2. AGRICULTURE
        cmd_agri = self.cultivator.gerer_cultiver(ma_ferme, day, cash, ids_autorises=equipe_champs)
        commandes.extend(cmd_agri)
        
        # 3. RH
        commandes.extend(self.drh.gerer_effectifs(ma_ferme))

        return commandes