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

    # On retourne bien Tuple[List[str], int]
    def gerer_un_champ_specifique(self, farm: dict, day: int, cash_dispo: int, target_field_id: int, assigned_workers: list[int], assigned_tractor_id: int) -> Tuple[List[str], int]:
        self._nettoyage_nouvelle_partie(day)
        
        # ⚠️ ATTENTION AUX RETURN ICI ⚠️
        if farm.get("blocked", False):
            return [], 0 

        fields = farm.get("fields", [])
        if target_field_id - 1 >= len(fields): 
            return [], 0  
            
        target_field_data = fields[target_field_id - 1] 
        
        employees = farm.get("employees", [])
        tractors = farm.get("tractors", [])

        # FIX 1 : TRACTEUR MANQUANT
        tractor_obj = next((t for t in tractors if int(t["id"]) == assigned_tractor_id), None)
        if tractor_obj is None:
            return [], 0  # <--- C'EST SOUVENT CELUI-LA QUI PLANTE LE CODE

        # ... (Le reste de la logique ne change pas) ...
        tractor_is_ready = self.is_tractor_ready(tractor_obj, day)
        besoin = self.analyser_un_champ(target_field_data, target_field_id, day)
        commandes = []
        cout_total = 0 # On initialise le coût
        
        for e_id in assigned_workers:
            emp_data = next((e for e in employees if int(e["id"]) == e_id), None)
            if emp_data is None: 
                continue

            if not self.is_employee_free(e_id, emp_data, day):
                continue

            # LOGIQUE ACTIONS...
            if besoin == "stock" and tractor_is_ready:
                dist = abs(target_field_id - 6)
                travel = math.ceil(dist / 3)
                lock = (travel * 2) + 3 
                commandes.append(self.creer_commande(e_id, f"STOCKER {target_field_id} {assigned_tractor_id}", day, lock, "🚜 STOCKER", target_field_id, assigned_tractor_id, lock_field=True))
                tractor_is_ready = False 
                besoin = None 
                continue

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
                    
                    # Mise à jour budget local
                    cout_total += cout_semence
                    cash_dispo -= cout_semence
                    continue

        # RETURN FINAL
        return commandes, cout_total

    # ... (Le reste des méthodes copier-coller du fichier précédent)
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

    def creer_commande(self, emp_id, action_str, day, lock_days, log_prefix, field_id, tractor_id=None, lock_field=True):
        Cultiver._MEMOIRE_OCCUPATION_EMP[emp_id] = day + lock_days
        if lock_field:
            Cultiver._MEMOIRE_OCCUPATION_CHAMP[field_id] = day + lock_days
        if tractor_id:
            Cultiver._MEMOIRE_OCCUPATION_TRACTEUR[tractor_id] = day + lock_days
        return f"{emp_id} {action_str}"