from typing import Optional, List

class Cultiver:
    _MEMOIRE_OCCUPATION_EMP = {}
    _MEMOIRE_OCCUPATION_CHAMP = {}
    _MEMOIRE_OCCUPATION_TRACTEUR = {}
    _DERNIER_JOUR_VU = -1

    def __init__(self):
        self.LEGUMES_CYCLE = ["PATATE", "POIREAU", "TOMATE", "OIGNON", "COURGETTE"]     

    def _nettoyage_nouvelle_partie(self, day: int):
        if day < Cultiver._DERNIER_JOUR_VU:
            Cultiver._MEMOIRE_OCCUPATION_EMP.clear()
            Cultiver._MEMOIRE_OCCUPATION_CHAMP.clear()
            Cultiver._MEMOIRE_OCCUPATION_TRACTEUR.clear()
        Cultiver._DERNIER_JOUR_VU = day

    def gerer_cultiver(self, farm: dict, day: int, cash: int, ids_autorises: Optional[List[int]] = None) -> List[str]:
        self._nettoyage_nouvelle_partie(day)
        if ids_autorises is None: 
            ids_autorises = []
        if not self.is_safe_to_operate(farm):
            return []

        self.afficher_diagnostics(farm, day, cash)

        fields = farm.get("fields", [])
        employees = farm.get("employees", [])   
        tractors = farm.get("tractors", [])

        besoins = self.analyser_champs(fields, day)
        
        # On récupère les tracteurs VRAIMENT disponibles
        tracteurs_dispos = self.get_tracteurs_dispos(tractors, day)
        
        return self.assigner_taches(employees, day, cash, besoins, tracteurs_dispos, ids_autorises)

    def is_safe_to_operate(self, farm: dict) -> bool:
        return not farm.get("blocked", False)

    def afficher_diagnostics(self, farm: dict, day: int, cash: int):
        soup_factory = farm.get("soup_factory", {})
        stock_usine = soup_factory.get("stock", {})
        total = sum(stock_usine.values())
        print(f"📊 [BILAN JOUR {day}] 🥗 Stock Usine: {total} | 💰 Cash: {cash}")

    def analyser_champs(self, fields: list, day: int) -> dict:
        besoins = {"stock": [], "water": [], "plant": []}
        for index, field in enumerate(fields, start=1):
            if not field["bought"]:
                continue
            if day <= Cultiver._MEMOIRE_OCCUPATION_CHAMP.get(index, -1): 
                continue

            content = field["content"]
            needed = field.get("needed_water", 0)
            
            if content != "NONE" and needed == 0:
                besoins["stock"].append(index)
            elif needed > 0 and content != "NONE":
                besoins["water"].append(index)
            elif content == "NONE":
                besoins["plant"].append(index)
        return besoins

    def get_tracteurs_dispos(self, tractors: list, day: int) -> list:
        dispos = []
        for t in tractors:
            t_id = int(t["id"])
            
            # 1. Vérif Mémoire (Le verrou local)
            if day <= Cultiver._MEMOIRE_OCCUPATION_TRACTEUR.get(t_id, -1):
                continue
                
            # 2. Vérif Contenu (Doit être vide)
            content = t.get("content", "EMPTY")
            if content != "EMPTY":
                continue

            # 3. Vérif Position (CORRECTION DU BUG 'FARM')
            raw_loc = t.get("location", "FARM")
            loc_id = 0 # Par défaut on dit qu'il est à la ferme (0)
            
            # On convertit le texte du serveur en ID numérique compréhensible
            if isinstance(raw_loc, int):
                loc_id = raw_loc
            elif raw_loc == "FARM":
                loc_id = 0
            elif raw_loc == "SOUP_FACTORY":
                loc_id = 6
            elif isinstance(raw_loc, str) and raw_loc.startswith("FIELD"):
                # Transforme "FIELD3" en 3
                try:
                    loc_id = int(raw_loc.replace("FIELD", ""))
                except:  # noqa: E722
                    loc_id = -1 # Erreur de lecture

            # Si le tracteur est à l'usine (6), on ne peut pas le prendre
            if loc_id == 6:
                 continue
                
            dispos.append(t_id)
        return dispos

    def assigner_taches(self, employees: list, day: int, cash: int, besoins: dict, tracteurs_dispos: list, ids_autorises: list) -> list[str]:
        commandes = []
        current_cash = cash
        compteur_eau = 0 
        ids_traites_ce_tour = set()

        for index_emp, emp in enumerate(employees, start=1):
            emp_id = int(emp.get("id", index_emp))
            
            if emp_id not in ids_autorises: 
                continue
            if emp_id in ids_traites_ce_tour: 
                continue
            if not self.is_employee_free(emp_id, emp, day): 
                continue

            # --- 1. STOCKER (PRIORITÉ ABSOLUE) ---
            if besoins["stock"] and len(tracteurs_dispos) > 0:
                target_field = besoins["stock"][0] 
                
                # === LOGIQUE TRACTEUR ATTITRÉ ===
                choix_tracteur = None
                
                if target_field in tracteurs_dispos:
                    choix_tracteur = target_field
                elif len(tracteurs_dispos) > 0:
                    choix_tracteur = tracteurs_dispos[0]
                
                if choix_tracteur is not None:
                    besoins["stock"].pop(0)
                    tracteurs_dispos.remove(choix_tracteur) 
                    
                    lock_duration = 40 
                    
                    commandes.append(self.creer_commande(emp_id, f"STOCKER {target_field} {choix_tracteur}", day, lock_duration, "🚜 STOCKER", target_field, choix_tracteur))
                    ids_traites_ce_tour.add(emp_id)
                    continue 

            # --- 2. ARROSER ---
            if besoins["water"]:
                target = besoins["water"][compteur_eau % len(besoins["water"])]
                lock_duration = target + 4 
                commandes.append(self.creer_commande(emp_id, f"ARROSER {target}", day, lock_duration, "💧 ARROSE", target))
                ids_traites_ce_tour.add(emp_id)
                compteur_eau += 1
                continue

            # --- 3. SEMER ---
            if besoins["plant"] and current_cash > 2000:
                target = besoins["plant"].pop(0)
                index_legume = (target - 1) % len(self.LEGUMES_CYCLE)
                leg = self.LEGUMES_CYCLE[index_legume]
                
                lock_duration = target + 5 
                commandes.append(self.creer_commande(emp_id, f"SEMER {leg} {target}", day, lock_duration, f"🌱 SEME ({leg})", target))
                ids_traites_ce_tour.add(emp_id)
                current_cash -= 1000
                continue
                
        return commandes

    def is_employee_free(self, emp_id: int, emp_data: dict, day: int) -> bool:
        if day <= Cultiver._MEMOIRE_OCCUPATION_EMP.get(emp_id, -1): 
            return False
        if emp_data.get("action", "IDLE") != "IDLE":
            return False
        return True

    def creer_commande(self, emp_id, action_str, day, lock_days, log_prefix, field_id, tractor_id=None):
        Cultiver._MEMOIRE_OCCUPATION_EMP[emp_id] = day + lock_days
        Cultiver._MEMOIRE_OCCUPATION_CHAMP[field_id] = day + lock_days
        
        if tractor_id:
            Cultiver._MEMOIRE_OCCUPATION_TRACTEUR[tractor_id] = day + lock_days
        
        print(f"   {log_prefix} Champ {field_id} [Verrou {lock_days}j]")
        return f"{emp_id} {action_str}"