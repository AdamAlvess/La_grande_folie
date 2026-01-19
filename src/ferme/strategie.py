from ferme.cultiver import Cultiver
from ferme.employer import GestionnairePersonnel 
from ferme.usine import Usine
from ferme.Finance_manager import FinanceManager 

class FarmStrategy:
    def __init__(self, nom_ferme: str):
        self.nom_ferme = nom_ferme
        self.cultivator = Cultiver()
        self.drh = GestionnairePersonnel(nom_ferme)
        self.chef_cuisine = Usine()
        self.finance = FinanceManager()

    def jouer_tour(self, game_data: dict) -> list[str]:
        commandes: list[str] = []
        ma_ferme = next((f for f in game_data["farms"] if f["name"] == self.nom_ferme), None)
        
        if not ma_ferme or ma_ferme.get("blocked", False):
            return []

        day = game_data["day"]
        cash = ma_ferme.get("cash", ma_ferme.get("money", 0))

        # --- 0. FINANCE ---
        # On récupère une LISTE d'actions (ex: ["ACHETER_CHAMP", "ACHETER_TRACTEUR"])
        actions_finance = self.finance.get_manager_action(ma_ferme, day)
        if actions_finance:
            commandes.extend(actions_finance)
            print(f"💰 [FINANCE] Actions : {actions_finance}")

        # --- REPARTITION DES EQUIPES ---
        equipe_usine = []
        equipe_champs = []

        for emp in ma_ferme["employees"]:
            e_id = int(emp["id"])
            # On laisse 3 ouvriers à l'usine pour le rendement max des soupes
            if e_id <= 3: 
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