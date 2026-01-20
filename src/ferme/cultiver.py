import math
from typing import Optional, Dict, Any, Tuple, List

class Cultiver:
    _MEMOIRE_OCCUPATION_EMP: dict[int, int] = {}
    _MEMOIRE_OCCUPATION_CHAMP: dict[int, int] = {} 
    _MEMOIRE_OCCUPATION_TRACTEUR: dict[int, int] = {}
    _DERNIER_JOUR_VU = -1

    def __init__(self):
        self.LEGUMES_CYCLE = ["PATATE", "POIREAU", "TOMATE", "OIGNON", "COURGETTE"]     

    def _nettoyage_nouvelle_partie(self, day: int):
        if day < Cultiver._DERNIER_JOUR_VU:
            Cultiver._MEMOIRE_OCCUPATION_EMP.clear()
            Cultiver._MEMOIRE_OCCUPATION_CHAMP.clear()
            Cultiver._MEMOIRE_OCCUPATION_TRACTEUR.clear()
        Cultiver._DERNIER_JOUR_VU = day

    def is_tractor_ready(self, tractor: Optional[Dict[str, Any]], day: int) -> bool:
        if not tractor:
            return False 
        t_id = int(tractor["id"])
        if day <= Cultiver._MEMOIRE_OCCUPATION_TRACTEUR.get(t_id, -1): 
            return False
        if tractor.get("content", "EMPTY") != "EMPTY":
            return False
        if tractor.get("location", "FARM") == "SOUP_FACTORY": 
            return False
        return True

    def is_employee_free(self, emp_id: int, emp_data: dict, day: int) -> bool:
        if day <= Cultiver._MEMOIRE_OCCUPATION_EMP.get(emp_id, -1):
            return False
        if emp_data.get("action", "IDLE") != "IDLE":
            Cultiver._MEMOIRE_OCCUPATION_EMP[emp_id] = day + 1
            return False
        return True

    def analyser_un_champ(self, field: dict, field_id: int, day: int) -> Optional[str]:
        if day <= Cultiver._MEMOIRE_OCCUPATION_CHAMP.get(field_id, -1): 
            return None
        content = field["content"]
        needed = field.get("needed_water", 0)
        if content != "NONE" and needed == 0: 
            return "stock"
        elif needed > 0 and content != "NONE": 
            return "water"
        elif content == "NONE":
            return "plant"
        return None

    def creer_commande(self, emp_id, action_str, day, lock_days, log_prefix, field_id, tractor_id=None, lock_field=True):
        Cultiver._MEMOIRE_OCCUPATION_EMP[emp_id] = day + lock_days
        if lock_field:
            Cultiver._MEMOIRE_OCCUPATION_CHAMP[field_id] = day + lock_days
        if tractor_id:
            Cultiver._MEMOIRE_OCCUPATION_TRACTEUR[tractor_id] = day + lock_days
        return f"{emp_id} {action_str}"

    def gerer_un_champ_specifique(self, farm: dict, day: int, cash_dispo: int, target_field_id: int, assigned_workers: list[int], assigned_tractor_id: int) -> Tuple[List[str], int]:
        self._nettoyage_nouvelle_partie(day)
        
        if farm.get("blocked", False):
            return [], 0 

        fields = farm.get("fields", [])
        if target_field_id - 1 >= len(fields): 
            return [], 0  
            
        target_field_data = fields[target_field_id - 1] 
        employees = farm.get("employees", [])
        tractors = farm.get("tractors", [])

        # --- CORRECTION MAJEURE ICI ---
        # On cherche le tracteur, mais s'il n'est pas là (None), CE N'EST PAS GRAVE !
        # On continue pour voir si on peut arroser ou planter.
        tractor_obj = next((t for t in tractors if int(t["id"]) == assigned_tractor_id), None)
        
        # On vérifie si le tracteur est prêt (False si tractor_obj est None)
        tractor_is_ready = self.is_tractor_ready(tractor_obj, day)

        besoin = self.analyser_un_champ(target_field_data, target_field_id, day)
        commandes = []
        cout_total = 0 
        
        for e_id in assigned_workers:
            emp_data = next((e for e in employees if int(e["id"]) == e_id), None)
            if emp_data is None: 
                continue

            if not self.is_employee_free(e_id, emp_data, day):
                continue

            # LOGIQUE ACTIONS...
            if besoin == "stock":
                # Pour stocker, il faut IMPÉRATIVEMENT un tracteur prêt
                if tractor_is_ready:
                    dist = abs(target_field_id - 6)
                    travel = math.ceil(dist / 3)
                    lock = (travel * 2) + 3 
                    commandes.append(self.creer_commande(e_id, f"STOCKER {target_field_id} {assigned_tractor_id}", day, lock, "🚜 STOCKER", target_field_id, assigned_tractor_id, lock_field=True))
                    tractor_is_ready = False 
                    besoin = None 
                    continue
                else:
                    # Pas de tracteur dispo ? On ne fait rien pour le stock, mais on ne quitte pas !
                    # On laisse la boucle continuer au cas où (mais ici besoin restera "stock" donc on ne fera rien d'autre)
                    pass

            if besoin == "water":
                lock = target_field_id + 3 
                commandes.append(self.creer_commande(e_id, f"ARROSER {target_field_id}", day, lock, "💧 ARROSE", target_field_id, lock_field=False))
                continue

            if besoin == "plant":
                cout_semence = 1000
                if cash_dispo >= cout_semence:
                    idx = (target_field_id - 1) % len(self.LEGUMES_CYCLE)
                    leg = self.LEGUMES_CYCLE[idx]
                    lock = target_field_id + 4 
                    commandes.append(self.creer_commande(e_id, f"SEMER {leg} {target_field_id}", day, lock, f"🌱 SEME ({leg})", target_field_id, lock_field=True))
                    besoin = None
                    
                    cout_total += cout_semence
                    cash_dispo -= cout_semence
                    continue

        return commandes, cout_total