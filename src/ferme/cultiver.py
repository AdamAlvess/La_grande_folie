import math
from typing import Optional, Dict, Any

class Cultiver:
    # CORRECTIONS ICI : Ajout des types dict[int, int]
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

    def gerer_un_champ_specifique(self, farm: dict, day: int, cash: int, target_field_id: int, assigned_workers: list[int], assigned_tractor_id: int) -> list[str]:
        
        self._nettoyage_nouvelle_partie(day)
        
        if farm.get("blocked", False):
            return []

        fields = farm.get("fields", [])
        if target_field_id - 1 >= len(fields): 
            return [] 
        target_field_data = fields[target_field_id - 1] 
        
        employees = farm.get("employees", [])
        tractors = farm.get("tractors", [])

        # --- FIX 1 : TRACTEUR MANQUANT ---
        tractor_obj = next((t for t in tractors if int(t["id"]) == assigned_tractor_id), None)
        
        if tractor_obj is None:
            return []

        tractor_is_ready = self.is_tractor_ready(tractor_obj, day)
        besoin = self.analyser_un_champ(target_field_data, target_field_id, day)
        commandes = []
        
        for e_id in assigned_workers:
            # --- FIX 2 : EMPLOYE FANTOME ---
            emp_data = next((e for e in employees if int(e["id"]) == e_id), None)
            
            if emp_data is None: 
                continue

            if not self.is_employee_free(e_id, emp_data, day):
                continue

            # 1. STOCKER
            if besoin == "stock" and tractor_is_ready:
                distance = abs(target_field_id - 6)
                travel_days = math.ceil(distance / 3)
                lock = (travel_days * 2) + 3 
                
                commandes.append(self.creer_commande(e_id, f"STOCKER {target_field_id} {assigned_tractor_id}", day, lock, "🚜 STOCKER", target_field_id, assigned_tractor_id, lock_field=True))
                
                tractor_is_ready = False 
                besoin = None 
                continue

            # 2. ARROSER
            if besoin == "water":
                lock = target_field_id + 3 
                commandes.append(self.creer_commande(e_id, f"ARROSER {target_field_id}", day, lock, "💧 ARROSE", target_field_id, lock_field=False))
                continue

            # 3. SEMER
            if besoin == "plant" and cash > 2000:
                index_legume = (target_field_id - 1) % len(self.LEGUMES_CYCLE)
                leg = self.LEGUMES_CYCLE[index_legume]
                
                lock = target_field_id + 4 
                
                commandes.append(self.creer_commande(e_id, f"SEMER {leg} {target_field_id}", day, lock, f"🌱 SEME ({leg})", target_field_id, lock_field=True))
                besoin = None
                cash -= 1000 
                continue

        return commandes

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
            
        raw_loc = tractor.get("location", "FARM")
        if raw_loc == "SOUP_FACTORY": 
            return False
        
        return True

    def is_employee_free(self, emp_id: int, emp_data: dict, day: int) -> bool:
        # 1. Vérification Mémoire
        if day <= Cultiver._MEMOIRE_OCCUPATION_EMP.get(emp_id, -1):
            return False
            
        # 2. Vérification Serveur
        action = emp_data.get("action", "IDLE")
        if action != "IDLE":
            Cultiver._MEMOIRE_OCCUPATION_EMP[emp_id] = day + 1
            return False
            
        return True

    def creer_commande(self, emp_id, action_str, day, lock_days, log_prefix, field_id, tractor_id=None, lock_field=True):
        Cultiver._MEMOIRE_OCCUPATION_EMP[emp_id] = day + lock_days
        
        if lock_field:
            Cultiver._MEMOIRE_OCCUPATION_CHAMP[field_id] = day + lock_days
        
        if tractor_id:
            Cultiver._MEMOIRE_OCCUPATION_TRACTEUR[tractor_id] = day + lock_days
        
        print(f"   {log_prefix} Champ {field_id} ({emp_id}) [Verrou {lock_days}j]")
        return f"{emp_id} {action_str}"