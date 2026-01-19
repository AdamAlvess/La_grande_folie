class Cultiver:
    def __init__(self):
        """
        Initialisation de la mémoire du cultivateur.
        """
        # --- MÉMOIRES (State) ---
        # On garde les sécurités initiales pour le scénario du Jour 0
        self.employee_busy_until = {1: 6}  
        self.field_busy_until = {3: 6} 
        self.tractor_busy_until = {}     

    def gerer_cultiver(self, farm: dict, day: int, cash: int) -> list[str]:
        """
        MÉTHODE PRINCIPALE (Public API)
        C'est la seule méthode que strategie.py a besoin d'appeler.
        Elle orchestre tout le processus.
        """
        # 1. Vérification de sécurité (Anti-Ban)
        if not self.is_safe_to_operate(farm):
            return []

        if day == 0:
            return []

        # 2. Affichage du bilan (Logs)
        self.afficher_diagnostics(farm, day, cash)

        # 3. Extraction des données brutes
        fields = farm.get("fields", [])
        employees = farm.get("employees", [])
        tractors = farm.get("tractors", [])

        besoins = self.analyser_champs(fields, day)
        
        tracteurs_dispos = self.get_tracteurs_dispos(tractors, day)

        commandes = self.assigner_taches(employees, day, cash, besoins, tracteurs_dispos)
        
        return commandes


    def is_safe_to_operate(self, farm: dict) -> bool:
        """Retourne False si la ferme est bloquée par le serveur."""
        if farm.get("blocked", False):
            return False
        return True

    def afficher_diagnostics(self, farm: dict, day: int, cash: int):
        """Affiche les logs de stock et de tracteurs."""
        soup_factory = farm.get("soup_factory", {})
        stock_usine = soup_factory.get("stock", {})
        nb_patates = stock_usine.get("POTATO", 0)
        
        print(f"📊 [BILAN JOUR {day}] 🥔 Patates: {nb_patates} | 💰 Cash: {cash}")
        
        for t in farm.get("tractors", []):
            content = t.get("content", "EMPTY")
            if content != "EMPTY":
                print(f"   🚜 Tracteur {t['id']} transporte : {content}")

    def analyser_champs(self, fields: list, day: int) -> dict:
        """
        Scanne tous les champs et retourne un dictionnaire de besoins.
        Output: {'stock': [id, id], 'water': [id], 'plant': [id]}
        """
        besoins = {
            "stock": [],
            "water": [],
            "plant": []
        }

        for index, field in enumerate(fields, start=1):
            # 1. Est-ce que le champ est à nous ?
            if not field["bought"]:
                continue

            # 2. Est-ce que le champ est occupé (mémoire) ?
            if day <= self.field_busy_until.get(index, -1):
                continue

            # 3. Analyse de l'état
            content = field["content"]
            needed_water = field.get("needed_water", 0)
            
            # Règle : On récolte si ce n'est pas vide et qu'il n'y a plus besoin d'eau
            is_ready_to_harvest = (content != "NONE" and needed_water == 0)

            if is_ready_to_harvest:
                besoins["stock"].append(index)
            elif needed_water > 0 and content != "NONE":
                besoins["water"].append(index)
            elif content == "NONE":
                besoins["plant"].append(index)
        
        return besoins

    def get_tracteurs_dispos(self, tractors: list, day: int) -> list:
        """Filtre les tracteurs pour ne garder que ceux disponibles (mémoire)."""
        dispos = []
        for t in tractors:
            t_id = t["id"]
            # Si le tracteur est marqué occupé dans notre carnet, on l'ignore
            if day <= self.tractor_busy_until.get(t_id, -1):
                continue
            dispos.append(t_id)
        return dispos

    def assigner_taches(self, employees: list, day: int, cash: int, besoins: dict, tracteurs_dispos: list) -> list[str]:
        """
        Le cœur de la stratégie : attribue les tâches aux employés disponibles.
        """
        commandes = []
        current_cash = cash  # On travaille sur une copie locale du cash

        for index_emp, emp in enumerate(employees, start=1):
            emp_id = emp.get("id", index_emp)
            
            # Si l'employé n'est pas libre, on passe au suivant
            if not self.is_employee_free(emp_id, emp, day):
                continue

            # --- PRIORITÉ 1 : STOCKER (Rapporte de l'argent) ---
            if besoins["stock"]:
                if not tracteurs_dispos:
                    continue # Pas de tracteur, pas de chocolat
                
                target_field = besoins["stock"].pop(0)
                tractor_id = tracteurs_dispos.pop(0)
                
                cmd = self.creer_commande_stocker(emp_id, target_field, tractor_id, day)
                commandes.append(cmd)
                continue

            # --- PRIORITÉ 2 : ARROSER (Maintient en vie) ---
            if besoins["water"]:
                target_field = besoins["water"].pop(0)
                
                cmd = self.creer_commande_arroser(emp_id, target_field, day)
                commandes.append(cmd)
                continue

            # --- PRIORITÉ 3 : SEMER (Investissement) ---
            if besoins["plant"] and current_cash > 2000:
                target_field = besoins["plant"].pop(0)
                
                cmd = self.creer_commande_semer(emp_id, target_field, day)
                commandes.append(cmd)
                current_cash -= 1000 # On déduit virtuellement le coût
                continue

        return commandes

    def is_employee_free(self, emp_id: int, emp_data: dict, day: int) -> bool:
        """Vérifie disponibilité Mémoire + Serveur."""
        # 1. Mémoire interne
        if day <= self.employee_busy_until.get(emp_id, -1):
            return False
        # 2. État serveur (double sécurité)
        action = emp_data.get("action", "IDLE")
        if action != "IDLE" and action is not None:
            return False
        return True

    # =========================================================================
    # --- GÉNÉRATEURS DE COMMANDES (Avec Verrouillage) ---
    # =========================================================================

    def creer_commande_stocker(self, emp_id: int, field_id: int, tractor_id: int, day: int) -> str:
        """Génère la commande et applique les verrous (5 jours)."""
        lock = 5
        self.employee_busy_until[emp_id] = day + lock
        self.field_busy_until[field_id] = day + lock
        self.tractor_busy_until[tractor_id] = day + lock
        
        print(f"   🚜 {emp_id} -> STOCKER Champ {field_id} (Tracteur {tractor_id})")
        return f"{emp_id} STOCKER {field_id} {tractor_id}"

    def creer_commande_arroser(self, emp_id: int, field_id: int, day: int) -> str:
        """Génère la commande et applique les verrous (2 jours)."""
        lock = 2
        self.employee_busy_until[emp_id] = day + lock
        self.field_busy_until[field_id] = day + lock
        
        print(f"   💧 {emp_id} -> ARROSE Champ {field_id}")
        return f"{emp_id} ARROSER {field_id}"

    def creer_commande_semer(self, emp_id: int, field_id: int, day: int) -> str:
        """Génère la commande et applique les verrous (5 jours)."""
        lock = 5
        self.employee_busy_until[emp_id] = day + lock
        self.field_busy_until[field_id] = day + lock
        
        print(f"   🌱 {emp_id} -> SEME Champ {field_id}")
        return f"{emp_id} SEMER PATATE {field_id}"