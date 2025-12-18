class Cultiver:
    def __init__(self):
        # --- MÉMOIRES ---
        self.employee_busy_until = {1: 6}  
        self.field_busy_until = {}
        self.tractor_busy_until = {}     

    def execute(self, farm, day, cash) -> list[str]:
        commandes = [] 
        
        # --- 0. SÉCURITÉ ANTI-BAN ---
        if farm.get("blocked", False):
            print("🛑 ALERTE : La ferme est BLOQUÉE ! Silence radio.")
            return []

        fields = farm.get("fields", [])
        employees = farm.get("employees", [])
        tractors = farm.get("tractors", []) 
        
        # --- FIX STOCK : On va chercher dans l'usine de soupe ! ---
        soup_factory = farm.get("soup_factory", {})
        stock = soup_factory.get("stock", {})
        
        # --- DIAGNOSTIC CLAIR ---
        nb_patates = stock.get("POTATO", 0)
        # On affiche Patates + Cash pour voir si tu t'enrichis
        print(f"📊 [BILAN JOUR {day}] 🥔 Patates: {nb_patates} | 💰 Cash: {cash}")
        
        # On affiche le contenu des tracteurs pour suivre les livraisons
        for t in tractors:
            content = t.get("content", "EMPTY")
            if content != "EMPTY":
                print(f"   🚜 Tracteur {t['id']} transporte : {content}")

        if day == 0:
            return []

        # --- 1. IDENTIFICATION DES BESOINS ---
        task_stock = []   
        task_water = []   
        task_plant = []   

        for index, field in enumerate(fields, start=1):
            if day <= self.field_busy_until.get(index, -1):
                continue

            content = field["content"]
            needed_water = field.get("needed_water", 0)
            
            is_ready_to_harvest = (content != "NONE" and needed_water == 0)

            # Petit log discret pour les champs actifs
            if content != "NONE":
                # print(f"   [CHAMP {index}] {content} | Eau: {needed_water}") 
                pass

            if is_ready_to_harvest:
                task_stock.append(index)
            elif needed_water > 0 and content != "NONE":
                task_water.append(index)
            elif content == "NONE":
                task_plant.append(index)

        # --- 2. GESTION DES TRACTEURS ---
        available_tractors = []
        for t in tractors:
            t_id = t["id"]
            if day <= self.tractor_busy_until.get(t_id, -1):
                continue
            available_tractors.append(t_id)

        # --- 3. DISTRIBUTION DES TÂCHES ---
        for index_emp, emp in enumerate(employees, start=1):
            emp_id = emp.get("id", index_emp)
            
            if day <= self.employee_busy_until.get(emp_id, -1):
                continue
            
            action = emp.get("action", "IDLE")
            if action != "IDLE" and action is not None:
                continue

            # --- A. STOCKER ---
            if task_stock:
                if not available_tractors:
                    continue

                target_field = task_stock.pop(0)
                tractor_id = available_tractors.pop(0)
                
                cmd = f"{emp_id} STOCKER {target_field} {tractor_id}"
                commandes.append(cmd)
                
                lock = 5
                self.employee_busy_until[emp_id] = day + lock
                self.field_busy_until[target_field] = day + lock
                self.tractor_busy_until[tractor_id] = day + lock
                
                print(f"   🚜 {emp_id} -> STOCKER Champ {target_field} (Tracteur {tractor_id})")
                continue

            # --- B. ARROSER ---
            if task_water:
                target_field = task_water.pop(0)
                
                cmd = f"{emp_id} ARROSER {target_field}"
                commandes.append(cmd)
                
                lock = 2 
                
                self.employee_busy_until[emp_id] = day + lock
                self.field_busy_until[target_field] = day + lock
                print(f"   💧 {emp_id} -> ARROSE Champ {target_field}")
                continue

            # --- C. SEMER ---
            if task_plant and cash > 2000:
                target_field = task_plant.pop(0)
                
                cmd = f"{emp_id} SEMER PATATE {target_field}"
                commandes.append(cmd)
                
                lock = 5
                self.employee_busy_until[emp_id] = day + lock
                self.field_busy_until[target_field] = day + lock 
                
                cash -= 1000
                print(f"   🌱 {emp_id} -> SEME Champ {target_field}")
                continue
        
        return commandes