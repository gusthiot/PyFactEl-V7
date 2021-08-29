from outils import Outils


class GrantedNew(object):
    """
    Classe pour la création du listing des montants de subsides comptabilisés
    """

    cles = ['id_compte', 'code_d', 'montant']
    noms = ['Id-Compte', 'Code_D', 'Montant comptabilisé']

    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        self.nom = "granted_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + ".csv"
        self.valeurs = {}

    def generer(self, grants, transactions):
        """
        génération des nouveaux fichiers de subventions consommées
        :param grants: grants importés
        :param transactions: transactions générées
        """

        for key in grants.donnees.keys():
            self.valeurs[key] = grants.donnees[key].copy()

        for key in transactions.comptabilises.keys():
            if key in self.valeurs.keys():
                self.valeurs[key]['montant'] = self.valeurs[key]['montant'] + transactions.comptabilises[key]['montant']
            else:
                self.valeurs[key] = transactions.comptabilises[key].copy()

    def csv(self, dossier_destination):
        """
        création du fichier csv
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        """
        with dossier_destination.writer(self.nom) as fichier_writer:
            ligne = []
            for nom in self.noms:
                ligne.append(nom)
            fichier_writer.writerow(ligne)

            for key in self.valeurs.keys():
                valeur = self.valeurs[key]
                ligne = []
                for i in range(0, len(self.cles)):
                    ligne.append(valeur[self.cles[i]])
                fichier_writer.writerow(ligne)
