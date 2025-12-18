from typing import Dict, Any, Optional

class FinanceManager:

    def __init__(self):
        self.PRICE_FIELD = 10_000
        self.PRICE_TRACTOR = 30_000
        self.MAX_FIELDS = 5
        self.MAX_TRACTORS_GLOBAL = 50
        self.MAX_LOANS = 10
        self.LOAN_AMOUNT = 100_000

        self.SECURITY_BUFFER__S_T_O_P = 15_000 
        

    def get_manager_action(self, farm_data: Dict[str, Any], day: int) -> Optional[str]:
        
        cash_analysis = farm_data.get("cash", 0)
        fields_analysis = farm_data.get("fields", [])
        tractors_analysis = farm_data.get("tractors", [])
        loans_analysis = farm_data.get("loans", [])
        nb_employees = farm_data.get("employees", [])
        
        nb_fields_analysis = len(fields_analysis)
        nb_tractors_analysis = len(tractors_analysis)
        nb_loans_analysis = len(loans_analysis)
        cash_min_available = 5000
        payment_of_workers = 1000
        payment_of_workers_With_marge = payment_of_workers * 1.2  


        next_month_salary_burden = len(nb_employees) * payment_of_workers_With_marge  
        available_cash = cash_analysis - self.SECURITY_BUFFER__S_T_O_P - next_month_salary_burden

        if day == 0 and nb_loans_analysis < 3:
             return f"0 EMPRUNTER {self.LOAN_AMOUNT}"
        

        #PK PAS FAIRE DES BOUCLES ICI
        if available_cash < cash_min_available and nb_loans_analysis < self.MAX_LOANS:
            return f"0 EMPRUNTER {self.LOAN_AMOUNT}"


        if nb_fields_analysis < self.MAX_FIELDS:
            if available_cash >= self.PRICE_FIELD:
                return "0 ACHETER_CHAMP"

    
        if nb_tractors_analysis < self.MAX_TRACTORS_GLOBAL: #Vérif. nb max.
            desired_tractors = nb_fields_analysis
            if nb_tractors_analysis < desired_tractors:
                if available_cash >= self.PRICE_TRACTOR:
                    return "0 ACHETER_TRACTEUR"

        return None