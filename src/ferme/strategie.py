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
        # C'est ici que la magie opère pour débloquer tes tracteurs.
        all_employees = ma_ferme.get("employees", [])
        
        employes_a_pied = []       # Ouvriers libres sans tracteur
        employes_motorises = []    # Ouvriers libres DEJA dans un tracteur (Chauffeurs)
        tracteurs_indisponibles = set() # IDs des tracteurs occupés ou réservés

        for emp in all_employees:
            eid = int(emp["id"])
            if eid == 0: continue 

            # Est-il occupé par le serveur ?
            est_occupe = emp.get("action_to_do") or emp.get("action", "IDLE") != "IDLE"
            
            # A-t-il un tracteur sous les fesses ?
            tid = int(emp["tractor"]["id"]) if emp.get("tractor") else None

            if est_occupe:
                if tid: tracteurs_indisponibles.add(tid)
            else:
                # Il est LIBRE
                if tid:
                    # C'est un CHAUFFEUR (il est libre mais assis dans un tracteur)
                    # On le garde couplé avec son tracteur !
                    employes_motorises.append((eid, tid))
                    tracteurs_indisponibles.add(tid)
                else:
                    # C'est un PIÉTON
                    employes_a_pied.append(eid)
        
        # On trie pour la stabilité
        employes_a_pied.sort()
        employes_motorises.sort() # Trie par ID ouvrier

        # 3. RECENSEMENT DES TRACTEURS VRAIMENT LIBRES (Au parking, vides)
        tracteurs_libres_parking = []
        tractors = ma_ferme.get("tractors", [])
        for t in tractors:
            tid = int(t["id"])
            if tid not in tracteurs_indisponibles:
                tracteurs_libres_parking.append(tid)
        
        tracteurs_libres_parking.sort()

        # 4. USINE (On priorise les piétons pour la cuisine, inutile de gâcher un tracteur)
        equipe_usine = []
        # On prend d'abord les piétons (ID 1-6 de préférence, ou n'importe qui)
        pietons_usine = [eid for eid in employes_a_pied if 1 <= eid <= 6]
        # Si pas assez de piétons "spécialistes", on prend les autres piétons
        if not pietons_usine:
             pietons_usine = [eid for eid in employes_a_pied]
        
        # On évite d'envoyer les chauffeurs en cuisine (ils doivent conduire !)
        # Sauf si vraiment personne d'autre
        
        # Sélection pour l'usine (on retire de la liste des dispos)
        for eid in list(pietons_usine):
             if len(equipe_usine) < 10: # Limite arbitraire pour laisser des gens aux champs
                 equipe_usine.append(eid)
                 if eid in employes_a_pied: employes_a_pied.remove(eid)

        cmd_usine = self.chef_cuisine.execute(ma_ferme, day, ids_autorises=equipe_usine)
        commandes.extend(cmd_usine)

        # 5. CHAMPS (Distribution des tâches avec logique de Chauffeur)
        fields = ma_ferme.get("fields", [])
        champs_achetes = [i for i, f in enumerate(fields) if f["bought"]]
        
        if champs_achetes:
            # On cycle sur les champs
            idx_cycle = 0
            
            # TANT QU'IL Y A DU MONDE (A pied ou en tracteur)
            while employes_motorises or employes_a_pied:
                field_idx = champs_achetes[idx_cycle]
                field_id = field_idx + 1
                field_data = fields[field_idx]
                
                # Analyse rapide du besoin pour savoir qui envoyer
                # (On duplique un peu la logique de cultiver pour le choix tactique)
                besoin_tracteur = False
                if field_data["content"] != "NONE" and field_data.get("needed_water", 0) == 0:
                    besoin_tracteur = True # Récolte = Tracteur OBLIGATOIRE

                worker_id = None
                assigned_tractor = -1

                if besoin_tracteur:
                    # PRIORITÉ 1 : Un Chauffeur déjà prêt (C'est ça qui débloque ton usine !)
                    if employes_motorises:
                        worker_id, assigned_tractor = employes_motorises.pop(0)
                    # PRIORITÉ 2 : Un Piéton + Un Tracteur du parking
                    elif employes_a_pied and tracteurs_libres_parking:
                        worker_id = employes_a_pied.pop(0)
                        assigned_tractor = tracteurs_libres_parking.pop(0)
                    else:
                        # Pas de ressources pour récolter ce champ, on passe au suivant
                        pass 
                else:
                    # Pas besoin de tracteur (Arrosage / Semis)
                    # PRIORITÉ 1 : Un Piéton (moins cher en essence/logique)
                    if employes_a_pied:
                        worker_id = employes_a_pied.pop(0)
                        assigned_tractor = -1 
                    # PRIORITÉ 2 : Un Chauffeur (il ira avec son tracteur, tant pis)
                    elif employes_motorises:
                        worker_id, assigned_tractor = employes_motorises.pop(0)
                
                # Si on a trouvé quelqu'un, on lance la commande
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
                
                # On arrête si tout le monde est occupé
                if not employes_motorises and not employes_a_pied:
                    break
                    
                idx_cycle = (idx_cycle + 1) % len(champs_achetes)

        # 6. RH 
        commandes.extend(self.drh.gerer_effectifs(ma_ferme, budget_actuel))

        return commandes