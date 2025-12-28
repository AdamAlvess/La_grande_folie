import math

class GestionnairePersonnel:
    def __init__(self, nom_ferme: str):
        self.nom_ferme = nom_ferme
        self.MAX_EMPLOYES = 300
        self.SALAIRE_BASE = 1000

    def estimer_cout_licenciement(self, salaire_actuel: int) -> int:
        salaire_prochain_mois = math.ceil(salaire_actuel * 1.01)
        return salaire_prochain_mois

    def gerer_effectifs(self, ma_ferme: dict) -> list[str]:
        
        if ma_ferme.get("blocked", False):
            # On ne fait rien si la ferme est bloquée, sinon on spamme le serveur pour rien
            return []
        commandes = []
        employes = ma_ferme["employees"]
        champs = ma_ferme["fields"]
        cash = ma_ferme.get("cash", ma_ferme.get("money", 0))
        nb_employes = len(employes)
        nb_champs = len(champs)
        # 1 ouvrier par champ + 2 à l'usine (si on a des champs)
        if nb_champs > 0:
            cible = nb_champs + 2
        else:
            cible = 0
        # Règle absolue du jeu : pas plus de 300
        cible = min(cible, self.MAX_EMPLOYES)

        # On somme les salaires actuels pour voir si on survit au prochain paiement
        masse_salariale_totale = sum(e.get("salary", self.SALAIRE_BASE) for e in employes)


        # ON EMBAUCHE
        if nb_employes < cible:
            if nb_employes >= self.MAX_EMPLOYES:
                print("🛑 RH: Limite de 300 employés atteinte.")
                return []

            # Coût du nouvel employé le premier mois
            cout_nouvel_employe = self.SALAIRE_BASE
            if cash > (masse_salariale_totale + cout_nouvel_employe + 2000): # +2000€ de marge de sécurité
                commandes.append("0 EMPLOYER")
                print(f"🤝 RH: Embauche lancée (Effectif: {nb_employes} -> {nb_employes+1})")
            else:
                print(f"💸 RH: Pas assez de cash pour embaucher ({cash}€ dispo)")

        # ON LICENCIE 
        elif nb_employes > cible:
            #Virer celui qui a le plus gros salaire pour alléger la masse salariale
            # On trie les employés
            employes_tries = sorted(employes, key=lambda x: x.get("salary", 0), reverse=True)
            
            candidat_depart = employes_tries[0] # Le plus cher
            id_ouvrier = candidat_depart["id"] 
            salaire_actuel = candidat_depart.get("salary", self.SALAIRE_BASE)
            cout_indemnite = self.estimer_cout_licenciement(salaire_actuel)

            # On vérifie si on a le cash pour payer l'indemnité 
            if cash > cout_indemnite:
                commandes.append(f"0 LICENCIER {id_ouvrier}")
                print(f"Licenciement de l'ouvrier {id_ouvrier} (Coût: {cout_indemnite}€)")
            else:
                print("On veut licencier mais on ne peut pas payer l'indemnité !")
        return commandes