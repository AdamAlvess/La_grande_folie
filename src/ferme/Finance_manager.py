from typing import Dict, Any, List

class FinanceManager:

    def __init__(self):
        # CONSTANTES OFFICIELLES
        self.PRICE_FIELD = 10_000
        self.PRICE_TRACTOR = 30_000
        self.MAX_FIELDS = 5
        self.MAX_TRACTORS_GLOBAL = 50
        self.MAX_LOANS = 10
        self.LOAN_AMOUNT = 100_000

        # Buffer de sécurité (Salaires + Imprévus)
        self.SECURITY_BUFFER__S_T_O_P = 15_000 
        

    def get_manager_action(self, farm_data: Dict[str, Any], day: int) -> List[str]:
        commandes = []
        
        # Arrêt des investissements vers la fin (Jour 1680 sur 1825 jours total)
        if day > 1680:
            return commandes

        cash_analysis = farm_data.get("cash", 0)
        fields_analysis = farm_data.get("fields", [])
        tractors_analysis = farm_data.get("tractors", [])
        loans_analysis = farm_data.get("loans", [])
        nb_employees = farm_data.get("employees", [])
        
        # 1. COMPTAGE DES ACTIFS
        # On compte uniquement les champs dont on est propriétaire
        nb_fields_analysis_bought = 0
        for f in fields_analysis:
            if f.get("bought", False):
                nb_fields_analysis_bought += 1

        nb_tractors_analysis = len(tractors_analysis)
        nb_loans_analysis = len(loans_analysis)
        
        # Simulation de la trésorerie pour les achats en cascade
        current_cash = cash_analysis

        # 2. CALCUL DES CHARGES (Sécurité Anti-Faillite)
        # Salaires + Remboursement mensuel des prêts
        payment_of_workers_With_marge = 1200  
        next_month_salary_burden = len(nb_employees) * payment_of_workers_With_marge  

        loan_monthly_cost = 0
        for loan in loans_analysis:
            cout = (loan["amount"] * 1.10) / 24
            loan_monthly_cost += int(cout)

        available_cash = current_cash - self.SECURITY_BUFFER__S_T_O_P - next_month_salary_burden - loan_monthly_cost


        # 3. STRATÉGIE "TURBO" : EMPRUNTER SI BESOIN
        # Objectif : Avoir 5 champs et 5 tracteurs le plus vite possible.
        
        # A. Manque d'argent pour un champ ?
        needs_money_for_fields = (nb_fields_analysis_bought < self.MAX_FIELDS) and (available_cash < self.PRICE_FIELD)
        
        # B. Manque d'argent pour un tracteur manquant ? (CRITIQUE)
        # Si on a 3 champs et 2 tracteurs, c'est une URGENCE.
        missing_tractors = nb_fields_analysis_bought - nb_tractors_analysis
        needs_money_for_tractors = (missing_tractors > 0) and (available_cash < self.PRICE_TRACTOR)

        # C. Cash dangereusement bas ?
        is_poor = available_cash <= 5000

        if (is_poor or needs_money_for_fields or needs_money_for_tractors) and nb_loans_analysis < self.MAX_LOANS:
             commandes.append(f"0 EMPRUNTER {self.LOAN_AMOUNT}")
             current_cash += self.LOAN_AMOUNT
             available_cash += self.LOAN_AMOUNT


        # 4. ACHAT DE CHAMPS (Priorité 1)
        while nb_fields_analysis_bought < self.MAX_FIELDS:
            if available_cash >= self.PRICE_FIELD:
                commandes.append("0 ACHETER_CHAMP")
                available_cash -= self.PRICE_FIELD
                nb_fields_analysis_bought += 1
            else:
                break 

    
        # 5. ACHAT DE TRACTEURS (Priorité 2 - Sécurisée)
        # Tant qu'on a moins de tracteurs que de champs, on achète.
        # Grâce à l'emprunt "Turbo" au-dessus, on a forcément l'argent si on était bloqué.
        while nb_tractors_analysis < self.MAX_TRACTORS_GLOBAL and nb_tractors_analysis < nb_fields_analysis_bought: 
            if available_cash >= self.PRICE_TRACTOR:
                commandes.append("0 ACHETER_TRACTEUR")
                available_cash -= self.PRICE_TRACTOR
                nb_tractors_analysis += 1
            else:
                break

        return commandes