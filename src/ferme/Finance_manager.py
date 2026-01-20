from typing import Dict, Any, List

class FinanceManager:

    def __init__(self):
        # CONSTANTES (Conformément aux règles du serveur)
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
        
        # 1. COMPTAGE RIGOUREUX (Champs achetés uniquement)
        nb_fields_analysis_bought = 0
        for f in fields_analysis:
            if f.get("bought", False):
                nb_fields_analysis_bought += 1

        nb_tractors_analysis = len(tractors_analysis)
        nb_loans_analysis = len(loans_analysis)
        
        # Simulation de la trésorerie
        current_cash = cash_analysis

        # 2. CALCUL DES CHARGES (Sécurité Anti-Faillite)
        # On provisionne les salaires et le remboursement mensuel des prêts
        payment_of_workers_With_marge = 1200  
        next_month_salary_burden = len(nb_employees) * payment_of_workers_With_marge  

        loan_monthly_cost = 0
        for loan in loans_analysis:
            # (Montant * 1.10) / 24 mois
            cout = (loan["amount"] * 1.10) / 24
            loan_monthly_cost += int(cout)

        # Cash net disponible pour investir
        available_cash = current_cash - self.SECURITY_BUFFER__S_T_O_P - next_month_salary_burden - loan_monthly_cost


        # 3. STRATÉGIE D'EMPRUNT "RATIO 1:1"
        # On veut : 1 Tracteur pour 1 Champ. Si déséquilibre -> Emprunt.
        
        # A. Besoin pour les Champs (On n'a pas atteint le max 5)
        needs_money_for_fields = (nb_fields_analysis_bought < self.MAX_FIELDS) and (available_cash < self.PRICE_FIELD)
        
        # B. Besoin pour les Tracteurs (CRITIQUE POUR EVITER L'ERREUR "ALREADY USED")
        # Si on a plus de champs que de tracteurs, il faut absolument de l'argent pour combler le trou
        missing_tractors = nb_fields_analysis_bought - nb_tractors_analysis
        needs_money_for_tractors = (missing_tractors > 0) and (available_cash < self.PRICE_TRACTOR)

        # C. Sécurité basique
        is_poor = available_cash <= 5000

        # Si l'une des conditions est vraie, on emprunte
        if (is_poor or needs_money_for_fields or needs_money_for_tractors) and nb_loans_analysis < self.MAX_LOANS:
             commandes.append(f"0 EMPRUNTER {self.LOAN_AMOUNT}")
             current_cash += self.LOAN_AMOUNT
             available_cash += self.LOAN_AMOUNT


        # 4. ACHAT DE CHAMPS
        while nb_fields_analysis_bought < self.MAX_FIELDS:
            if available_cash >= self.PRICE_FIELD:
                commandes.append("0 ACHETER_CHAMP")
                available_cash -= self.PRICE_FIELD
                nb_fields_analysis_bought += 1
            else:
                break 

    
        # 5. ACHAT DE TRACTEURS (Sécurisé)
        # RÈGLE D'OR : nb_tractors < nb_fields_bought
        # Cela garantit qu'on n'a jamais plus de tracteurs que de champs (inutile)
        # Mais surtout, grâce à l'emprunt ci-dessus, on force l'achat tant qu'on n'est pas à égalité.
        while nb_tractors_analysis < self.MAX_TRACTORS_GLOBAL and nb_tractors_analysis < nb_fields_analysis_bought: 
            if available_cash >= self.PRICE_TRACTOR:
                commandes.append("0 ACHETER_TRACTEUR")
                available_cash -= self.PRICE_TRACTOR
                nb_tractors_analysis += 1
            else:
                break

        return commandes