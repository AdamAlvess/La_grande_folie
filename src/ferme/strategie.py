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
        
        # --- INITIALISATION DU BUDGET GLISSANT ---
        budget_actuel = ma_ferme.get("cash", ma_ferme.get("money", 0))
        print(f"💰 [DEBUT TOUR] Cash: {budget_actuel}")

        # 1. FINANCE
        actions_finance, cout_finance = self.finance.get_manager_action(ma_ferme, day)
        if actions_finance:
            commandes.extend(actions_finance)
            budget_actuel -= cout_finance 
            print(f"💰 [FINANCE] Dépense : {cout_finance} | Reste : {budget_actuel}")

        # 2. EQUIPE USINE (Ne coûte rien en cash direct pour l'instant)
        equipe_usine = [1, 2, 3, 4, 5, 6]
        cmd_usine = self.chef_cuisine.execute(ma_ferme, day, ids_autorises=equipe_usine)
        commandes.extend(cmd_usine)

        # 3. EQUIPES AGRICOLES
        fields = ma_ferme.get("fields", [])
        current_worker_id = 7 
        workers_per_field = 3 

        for i, field in enumerate(fields):
            field_id = i + 1 
            
            if not field["bought"]:
                current_worker_id += workers_per_field
                continue

            equipe_champ = []
            for _ in range(workers_per_field):
                equipe_champ.append(current_worker_id)
                current_worker_id += 1

            tracteur_attitre = field_id 
            cmds_champ, cout_champ = self.cultivator.gerer_un_champ_specifique(
                ma_ferme, day, budget_actuel, 
                target_field_id=field_id, 
                assigned_workers=equipe_champ, 
                assigned_tractor_id=tracteur_attitre
            )
            
            if cmds_champ:
                commandes.extend(cmds_champ)
                budget_actuel -= cout_champ

        # 4. RH 
        commandes.extend(self.drh.gerer_effectifs(ma_ferme, budget_actuel))

        print(f"🛑 [FIN TOUR] Cash estimé restant : {budget_actuel}")
        return commandes