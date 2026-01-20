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
        budget_actuel = ma_ferme.get("money", 0)

        # 1. FINANCE
        actions_finance, cout_finance = self.finance.get_manager_action(ma_ferme, day)
        if actions_finance:
            commandes.extend(actions_finance)
            budget_actuel -= cout_finance 

        # 2. TRI INTELLIGENT DES OUVRIERS (PIÉTONS vs CHAUFFEURS)
        all_employees = ma_ferme.get("employees", [])
        employes_a_pied = []
        employes_motorises = []
        tracteurs_indisponibles = set()
        for emp in all_employees:
            eid = int(emp["id"])
            if eid == 0: 
                continue 
            est_occupe = emp.get("action_to_do") or emp.get("action", "IDLE") != "IDLE"
            tid = int(emp["tractor"]["id"]) if emp.get("tractor") else None
            if est_occupe:
                if tid:
                    tracteurs_indisponibles.add(tid)
            else:
                if tid:
                    employes_motorises.append((eid, tid))
                    tracteurs_indisponibles.add(tid)
                else:
                    employes_a_pied.append(eid)
        
        employes_a_pied.sort()
        employes_motorises.sort()

        # 3. RECENSEMENT DES TRACTEURS VRAIMENT LIBRES
        tracteurs_libres_parking = []
        tractors = ma_ferme.get("tractors", [])
        for t in tractors:
            tid = int(t["id"])
            if tid not in tracteurs_indisponibles:
                tracteurs_libres_parking.append(tid)
        tracteurs_libres_parking.sort()

        # 4. USINE 
        equipe_usine = []
        pietons_usine = [eid for eid in employes_a_pied if 1 <= eid <= 6]
        if not pietons_usine:
            pietons_usine = [eid for eid in employes_a_pied]
        for eid in list(pietons_usine):
            if len(equipe_usine) < 10:  
                equipe_usine.append(eid)
                if eid in employes_a_pied:
                    employes_a_pied.remove(eid)
        cmd_usine = self.chef_cuisine.execute(ma_ferme, day, ids_autorises=equipe_usine)
        commandes.extend(cmd_usine)

        # 5. CHAMPS (Distribution des tâches avec logique de Chauffeur)
        fields = ma_ferme.get("fields", [])
        champs_achetes = [i for i, f in enumerate(fields) if f["bought"]]
        if champs_achetes:
            idx_cycle = 0
            while employes_motorises or employes_a_pied:
                field_idx = champs_achetes[idx_cycle]
                field_id = field_idx + 1
                field_data = fields[field_idx]
                besoin_tracteur = False
                if field_data["content"] != "NONE" and field_data.get("needed_water", 0) == 0:
                    besoin_tracteur = True
                worker_id = None
                assigned_tractor = -1

                if besoin_tracteur:
                    if employes_motorises:
                        worker_id, assigned_tractor = employes_motorises.pop(0)
                    elif employes_a_pied and tracteurs_libres_parking:
                        worker_id = employes_a_pied.pop(0)
                        assigned_tractor = tracteurs_libres_parking.pop(0)
                    else:
                        pass 
                else:
                    if employes_a_pied:
                        worker_id = employes_a_pied.pop(0)
                        assigned_tractor = -1 
                    elif employes_motorises:
                        worker_id, assigned_tractor = employes_motorises.pop(0)
                if worker_id:
                    cmds_champ, cout_champ = self.cultivator.gerer_un_champ_specifique(
                        ma_ferme, day, budget_actuel, 
                        target_field_id=field_id, 
                        assigned_workers=[worker_id], 
                        assigned_tractor_id=assigned_tractor
                    )
                    if cmds_champ:
                        commandes.extend(cmds_champ)
                        budget_actuel -= cout_champ
                if not employes_motorises and not employes_a_pied:
                    break
                idx_cycle = (idx_cycle + 1) % len(champs_achetes)

        # 6. RH 
        commandes.extend(self.drh.gerer_effectifs(ma_ferme, budget_actuel))

        return commandes