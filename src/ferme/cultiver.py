class Cultiver:
    def __init__(self):
        # --- MÉMOIRES ---
        self.employee_busy_until = {1: 2}  
        self.field_busy_until = {}     

    # On a retiré 'client' des arguments et on précise qu'on renvoie une liste de str
    def execute(self, farm, day, cash) -> list[str]:
        """
        Cycle : SEMER -> ARROSER -> STOCKER
        Retourne une liste de commandes (strings).
        """
        commands = []  # La liste qu'on va remplir
        
        fields = farm.get("fields", [])
        employees = farm.get("employees", [])
        tractors = farm.get("tractors", []) 
        stock = farm.get("stock", {})
        
        total_stock = sum(stock.values()) if stock else 0
        if total_stock > 0:
            print(f"📦 [STOCK HANGAR] Total: {total_stock} légumes -> {stock}")

        if day == 0:
            return [] # On retourne une liste vide

        # --- 1. IDENTIFIER LES BESOINS ---
        task_stock = []   
        task_water = []   
        task_plant = []   

        for index, field in enumerate(fields, start=1):
            if day <= self.field_busy_until.get(index, -1):
                continue

            content = field["content"]
            needed_water = field.get("needed_water", 0)
            is_ready_to_harvest = (content != "NONE" and needed_water == 0)

            if content != "NONE":
                print(f"   [CHAMP {index}] {content} | Eau: {needed_water} | Prêt: {is_ready_to_harvest}")

            if is_ready_to_harvest:
                task_stock.append(index)
            elif needed_water > 0 and content != "NONE":
                task_water.append(index)
            elif content == "NONE":
                task_plant.append(index)

        # --- 2. TRACTEURS DISPOS ---
        available_tractors = [t["id"] for t in tractors]

        # --- 3. DISTRIBUTION ---
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
                    print("⚠️ Plus de tracteur dispo !")
                    continue

                target_field = task_stock.pop(0)
                tractor_id = available_tractors.pop(0)
                
                # ICI : On ajoute à la liste commands au lieu d'envoyer au client
                commands.append(f"{emp_id} STOCKER {target_field} {tractor_id}")
                
                self.employee_busy_until[emp_id] = day + 1
                self.field_busy_until[target_field] = day + 1 
                
                print(f"🚜 {emp_id} -> STOCKER Champ {target_field} (Tracteur {tractor_id})")
                continue

            # --- B. ARROSER ---
            if task_water:
                target_field = task_water.pop(0)
                commands.append(f"{emp_id} ARROSER {target_field}")
                
                self.employee_busy_until[emp_id] = day + 1
                self.field_busy_until[target_field] = day + 1
                print(f"💧 {emp_id} -> ARROSE Champ {target_field}")
                continue

            # --- C. SEMER ---
            if task_plant and cash > 2000:
                target_field = task_plant.pop(0)
                commands.append(f"{emp_id} SEMER PATATE {target_field}")
                
                self.employee_busy_until[emp_id] = day + 5
                self.field_busy_until[target_field] = day + 5 
                
                cash -= 1000
                print(f"🌱 {emp_id} -> SEME Champ {target_field}")
                continue
        
        return commands