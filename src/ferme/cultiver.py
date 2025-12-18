class Cultiver:
    def __init__(self):
        # --- MÉMOIRES ---
        # On bloque l'employé 1 au début à cause du script manuel du J0
        self.employee_busy_until = {1: 2}  
        self.field_busy_until = {}     

    def execute(self, client, farm, day, cash):
        """
        Cycle : SEMER -> ARROSER -> STOCKER (Dès que eau == 0) -> SEMER...
        Sur TOUS les champs !
        """
        fields = farm.get("fields", [])
        employees = farm.get("employees", [])
        tractors = farm.get("tractors", []) 
        stock = farm.get("stock", {})
        
        # --- 0. CHECK DU STOCK (Pour vérifier que ça rentre bien) ---
        # On l'affiche au début du tour pour voir le résultat des actions précédentes
        total_stock = sum(stock.values()) if stock else 0
        if total_stock > 0:
            print(f"📦 [STOCK HANGAR] Total: {total_stock} légumes -> {stock}")

        if day == 0:
            return

        # --- 1. IDENTIFIER LES BESOINS (SUR TOUS LES CHAMPS) ---
        task_stock = []   
        task_water = []   
        task_plant = []   

        for index, field in enumerate(fields, start=1):
            
            # --- PLUS DE RESTRICTION ! ON PREND TOUS LES CHAMPS ---
            # (J'ai supprimé le if index != 1)

            # Si le champ est verrouillé dans notre carnet, on passe
            if day <= self.field_busy_until.get(index, -1):
                continue

            content = field["content"]
            needed_water = field.get("needed_water", 0)
            
            # Si y'a une patate et qu'elle n'a plus soif -> ON STOCKE !
            is_ready_to_harvest = (content != "NONE" and needed_water == 0)

            # On affiche l'état seulement si le champ est actif (pas vide et pas verrouillé)
            if content != "NONE":
                print(f"   [CHAMP {index}] {content} | Eau: {needed_water} | Prêt: {is_ready_to_harvest}")

            if is_ready_to_harvest:
                task_stock.append(index)
            elif needed_water > 0 and content != "NONE":
                task_water.append(index)
            elif content == "NONE":
                task_plant.append(index)

        # --- 2. GESTION DES TRACTEURS DISPOS ---
        # On fait une liste des ID de tracteurs qu'on peut utiliser ce tour-ci
        available_tractors = [t["id"] for t in tractors]

        # --- 3. DISTRIBUTION DES TÂCHES ---
        for index_emp, emp in enumerate(employees, start=1):
            emp_id = emp.get("id", index_emp)
            
            # Vérif disponibilité (Mémoire + Serveur)
            if day <= self.employee_busy_until.get(emp_id, -1):
                continue
            
            action = emp.get("action", "IDLE")
            if action != "IDLE" and action is not None:
                continue

            # --- A. STOCKER (PRIORITÉ ABSOLUE) ---
            if task_stock:
                # On vérifie qu'il reste un tracteur dispo pour cet employé
                if not available_tractors:
                    print("⚠️ Plus de tracteur dispo pour stocker ce tour-ci !")
                    continue

                target_field = task_stock.pop(0)
                # On prend un tracteur et on le retire de la liste des dispos
                tractor_id = available_tractors.pop(0)
                
                # Commande : {OUVRIER} STOCKER {CHAMP} {TRACTEUR}
                client.add_command(f"{emp_id} STOCKER {target_field} {tractor_id}")
                
                self.employee_busy_until[emp_id] = day + 1
                self.field_busy_until[target_field] = day + 1 
                
                print(f"🚜 {emp_id} -> STOCKER Champ {target_field} (Tracteur {tractor_id})")
                continue

            # --- B. ARROSER ---
            if task_water:
                target_field = task_water.pop(0)
                client.add_command(f"{emp_id} ARROSER {target_field}")
                
                self.employee_busy_until[emp_id] = day + 1
                self.field_busy_until[target_field] = day + 1
                print(f"💧 {emp_id} -> ARROSE Champ {target_field}")
                continue

            # --- C. SEMER ---
            if task_plant and cash > 2000:
                target_field = task_plant.pop(0)
                client.add_command(f"{emp_id} SEMER PATATE {target_field}")
                
                # On verrouille 5 jours
                self.employee_busy_until[emp_id] = day + 5
                self.field_busy_until[target_field] = day + 5 
                
                cash -= 1000
                print(f"🌱 {emp_id} -> SEME Champ {target_field}")
                continue