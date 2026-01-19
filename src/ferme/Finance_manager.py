from typing import Dict, Any, List

class FinanceManager:

    def __init__(self):
        # CONSTANTES
        self.PRICE_FIELD = 10_000
        self.PRICE_TRACTOR = 30_000
        self.MAX_FIELDS = 5
        self.MAX_TRACTORS_GLOBAL = 50
        self.MAX_LOANS = 10
        self.LOAN_AMOUNT = 100_000
        
        # SÉCURITÉ (Buffer augmenté à 15k pour être sûr)
        self.SECURITY_BUFFER = 15_000 

    def get_manager_action(self, farm_data: Dict[str, Any], day: int) -> List[str]:
        commandes = []
        
        # 1. ANALYSE DES DONNÉES
        cash = farm_data.get("cash", 0)
        fields = farm_data.get("fields", [])
        tractors = farm_data.get("tractors", [])
        loans = farm_data.get("loans", [])
        employees = farm_data.get("employees", [])
        
        # On compte ce qu'on possède
        # Note: len(fields) suffit car la liste ne contient que les champs achetés
        nb_fields_bought = len(fields) 
        nb_tractors = len(tractors)
        nb_loans = len(loans)
        
        # On simule le cash actuel pour enchaîner les achats dans la même journée
        current_cash = cash 

        # --- 2. CALCUL DES CHARGES (L'amélioration cruciale) ---
        # Si on ne compte pas ça, on dépense trop et on meurt le lendemain
        mensualite_emprunts = sum([int((l["amount"] * 1.10) / 24) for l in loans])
        salaire_previsionnel = len(employees) * 1200 # 1000 + marge
        
        charges_incompressibles = mensualite_emprunts + salaire_previsionnel + self.SECURITY_BUFFER

        # --- 3. GESTION DES EMPRUNTS (SURVIE) ---
        # Si on est pauvre OU au jour 0, on emprunte
        if (current_cash < self.SECURITY_BUFFER or (day == 0 and current_cash <= 1000)) and nb_loans < self.MAX_LOANS:
             # Correction format: on s'assure que c'est bien une chaîne propre
             cmd = f"0 EMPRUNTER {self.LOAN_AMOUNT}"
             commandes.append(cmd)
             current_cash += self.LOAN_AMOUNT

        # --- 4. CALCUL DU CASH INVESTISSABLE ---
        # On ne dépense que ce qui dépasse de nos charges
        cash_investissable = current_cash - charges_incompressibles

        # Arrêt des investissements vers la fin du jeu (Jour 1680+)
        if day > 1680:
            return commandes

        # --- 5. ACHAT DE CHAMPS ---
        while nb_fields_bought < self.MAX_FIELDS and cash_investissable >= self.PRICE_FIELD:
            commandes.append("0 ACHETER_CHAMP")
            cash_investissable -= self.PRICE_FIELD
            nb_fields_bought += 1 

        # --- 6. ACHAT DE TRACTEURS ---
        # On n'achète pas plus de tracteurs que de champs
        while nb_tractors < nb_fields_bought and nb_tractors < self.MAX_TRACTORS_GLOBAL:
            if cash_investissable >= self.PRICE_TRACTOR:
                commandes.append("0 ACHETER_TRACTEUR")
                cash_investissable -= self.PRICE_TRACTOR
                nb_tractors += 1
            else:
                break 

        return commandes