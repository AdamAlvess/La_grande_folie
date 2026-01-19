from typing import Dict, Any, Optional

class FinanceManager:

    def __init__(self):
        # CONSTANTES
        self.PRICE_FIELD = 10_000
        self.PRICE_TRACTOR = 30_000
        self.MAX_FIELDS = 5
        self.MAX_TRACTORS_GLOBAL = 50
        self.MAX_LOANS = 10
        self.LOAN_AMOUNT = 100_000

        # SÉCURITÉ
        self.SECURITY_BUFFER__S_T_O_P = 15_000 
        self.nb_emprunts_total = 0 # Compteur pour respecter la limite de 10

    def get_manager_action(self, farm_data: Dict[str, Any], day: int) -> Optional[str]:
        
        # 0. ARRÊT DES INVESTISSEMENTS (Fin de partie proche -> On garde le cash pour le score)
        if day > 1680:
            return None

        # 1. ANALYSE DES DONNÉES
        cash_analysis = farm_data.get("cash", 0)
        fields_analysis = farm_data.get("fields", [])
        tractors_analysis = farm_data.get("tractors", [])
        loans_analysis = farm_data.get("loans", [])
        employees_list = farm_data.get("employees", [])
        
        nb_fields_analysis = len(fields_analysis)
        nb_tractors_analysis = len(tractors_analysis)
        
        # 2. CALCUL DU CASH RÉELLEMENT DISPONIBLE
        # Salaire : 1000 de base + marge sécu pour l'augmentation mensuelle
        payment_of_workers_With_marge = 1200  
        next_month_salary_burden = len(employees_list) * payment_of_workers_With_marge
        
        # Remboursement Emprunts : Formule (Montant * 1.10) / 24 mois
        # On doit soustraire ça du cash dispo sinon on ne pourra pas payer la banque !
        monthly_loan_repayment = sum([int((loan["amount"] * 1.10) / 24) for loan in loans_analysis])

        # Cash - Sécurité - Salaires à venir - Mensualité crédit
        available_cash = cash_analysis - self.SECURITY_BUFFER__S_T_O_P - next_month_salary_burden - monthly_loan_repayment

        # --- ARBRE DE DÉCISION (Priorité absolue à la survie) ---
        
        # A. SURVIE : EMPRUNTER SI TRÉSORERIE BASSE (OU JOUR 0)
        # Si on est sous le buffer OU qu'on est au jour 0 avec peu de cash
        if (cash_analysis < self.SECURITY_BUFFER__S_T_O_P) or (day == 0 and cash_analysis <= 1000):
            if self.nb_emprunts_total < self.MAX_LOANS:
                self.nb_emprunts_total += 1
                return f"0 EMPRUNTER {self.LOAN_AMOUNT}"

        # B. EXPANSION : ACHETER CHAMP
        if nb_fields_analysis < self.MAX_FIELDS:
            if available_cash >= self.PRICE_FIELD:
                return "0 ACHETER_CHAMP"

        # C. OPTIMISATION : ACHETER TRACTEUR
        # Règle : Pas plus de tracteurs que de champs (inutile)
        if nb_tractors_analysis < self.MAX_TRACTORS_GLOBAL: 
            desired_tractors = nb_fields_analysis
            if nb_tractors_analysis < desired_tractors:
                if available_cash >= self.PRICE_TRACTOR:
                    return "0 ACHETER_TRACTEUR"

        return None