from outils import Outils
from traitement import Recap
from importes import DossierDestination


class AnnexeDetails(Recap):
    """
    Classe pour la création du csv d'annexe détails
    """

    cles = ['invoice-year', 'invoice-month', 'invoice-ref', 'platf-name', 'client-code', 'client-name', 'oper-name',
            'oper-note', 'staff-note', 'mach-name', 'user-sciper', 'user-name', 'user-first', 'proj-nbr', 'proj-name',
            'proj-subs', 'proj-start', 'proj-end', 'item-nbr', 'item-name', 'item-unit', 'transac-date',
            'transac-quantity', 'valuation-price', 'valuation-brut', 'discount-type', 'discount-CHF', 'deduct-CHF',
            'valuation-net', 'subsid-name', 'subsid-maxproj', 'subsid-maxmois', 'subsid-reste', 'subsid-CHF',
            'subsid-deduct', 'discount-bonus', 'subsid-bonus', 'total-fact']

    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        super().__init__(edition)
        self.version = edition.version
        self.nom = ""
        self.prefixe = "Annexe-détails_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + \
            str(edition.version)
        if edition.version > 0:
            self.prefixe += "_" + str(edition.client_unique)

    def generer(self, trans_vals, paramtexte, paramannexe, par_client):
        """
        génération des fichiers d'annexes détails à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param paramtexte: paramètres textuels
        :param paramannexe: paramètres d'annexe
        :param par_client: tri des transactions par client
        """
        destination = "./"
        for donnee in paramannexe.donnees:
            if donnee['nom'] == 'Annexe-détails':
                destination = donnee['chemin']
        dossier_destination = DossierDestination(destination)

        for code in par_client.keys():
            tbtr = par_client[code]['transactions']
            base = trans_vals[tbtr[0]]
            self.nom = self.prefixe + "_" + code + "_" + base['client-name'] + ".csv"
            self.valeurs = {}
            ii = 0
            for indice in tbtr:
                val = trans_vals[indice]
                donnee = []
                for cle in range(2, len(self.cles)):
                    donnee.append(val[self.cles[cle]])
                self.ajouter_valeur(donnee, ii)
                ii += 1
            self.csv(dossier_destination, paramtexte)
