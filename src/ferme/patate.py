class Strategy:
    def __init__(self):
        # --- MÉMOIRES ---
        # On garde le fix du prof pour l'employé 1
        self.employee_busy_until = {1: 2}  
        self.field_busy_until = {}     

    def execute(self, client, farm, day, cash):
        fields = farm.get("fields", [])
        employees = farm.get("employees", [])
        stock = farm.get("stock", {})
        
        if day == 0:
            return

        # --- 1. IDENTIFIER LES BESOINS (FOCUS CHAMP 1) ---
        fields_to_harvest = []
        fields_to_water = []
        fields_to_plant = []

        for index, field in enumerate(fields, start=1):
            if index >= 1: continue # On reste focus sur le champ 1

            # Check mémoire interne
            if day <= self.field_busy_until.get(index, -1):
                continue

            content = field["content"]
            needed_water = field.get("needed_water", 0)
            is_ripe = field.get("ripe", False)
            
            print(f"   [ETAT CHAMP {index}] Contenu: {content}, Soif: {needed_water}, Mûr: {is_ripe}")

            if is_ripe:
                fields_to_harvest.append(index)
            elif needed_water > 0 and content != "NONE":
                fields_to_water.append(index)
            elif content == "NONE" and needed_water == 0:
                fields_to_plant.append(index)

        # --- 2. DISTRIBUTION DES TÂCHES ---
        for index_emp, emp in enumerate(employees, start=1):
            emp_id = emp.get("id", index_emp)
            
            if day <= self.employee_busy_until.get(emp_id, -1):
                continue
            
            action = emp.get("action", "IDLE")
            if action != "IDLE" and action is not None:
                continue

            # --- ASSIGNATION ---
            
            # A. RÉCOLTE
            if fields_to_harvest:
                target = fields_to_harvest.pop(0)
                client.add_command(f"{emp_id} RECOLTER {target}")
                self.employee_busy_until[emp_id] = day + 1
                self.field_busy_until[target] = day + 1 
                print(f"💰 {emp_id} -> RECOLTE Champ {target}")
                continue

            # B. ARROSAGE
            if fields_to_water:
                target = fields_to_water.pop(0)
                client.add_command(f"{emp_id} ARROSER {target}")
                self.employee_busy_until[emp_id] = day + 1
                self.field_busy_until[target] = day + 1
                print(f"💧 {emp_id} -> ARROSE Champ {target}")
                continue

            # C. PLANTATION (LE FIX EST ICI)
            if fields_to_plant and cash > 2000:
                target = fields_to_plant.pop(0)
                client.add_command(f"{emp_id} SEMER PATATE {target}")
                
                # ON AUGMENTE LA SÉCURITÉ A 5 JOURS !
                self.employee_busy_until[emp_id] = day + 5
                self.field_busy_until[target] = day + 5 
                
                cash -= 1000
                print(f"🌱 {emp_id} -> SEME Champ {target} (Verrouillé 5 jours)")
                continue
        
        # --- 3. VENTE ---
        stock_count = sum(stock.values()) if stock else 0
        if stock_count >= 1:
            print(f"🚚 Vente de {stock_count} légumes")
            client.add_command("0 VENDRE")