from outils import Outils
from traitement import Recap
from importes import DossierDestination


class AnnexeSubsides(Recap):
    """
    Classe pour la création du csv d'annexe subsides
    """

    cles = ['invoice-year', 'invoice-month', 'client-code', 'client-name', 'proj-id', 'proj-name', 'proj-subs',
            'item-codeD', 'item-labelcode', 'subsid-name', 'subsid-start', 'subsid-end', 'subsid-ok', 'subsid-maxproj',
            'subsid-maxmois', 'subsid-alrdygrant', 'subsid-CHF', 'subsid-deduct', 'subsid-bonus', 'subsid-reste']

    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        super().__init__(edition)
        self.version = edition.version
        self.nom = ""
        self.dossier = ""
        self.chemin = "./"
        self.prefixe = "Annexe-subsides_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + \
            str(edition.version)
        if edition.version > 0:
            self.prefixe += "_" + str(edition.client_unique)

    def generer(self, trans_vals, grants, plafonds, paramtexte, paramannexe, par_client):
        """
        génération des fichiers d'annexes subsides à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param grants: grants importés
        :param plafonds: plafonds importés
        :param paramtexte: paramètres textuels
        :param paramannexe: paramètres d'annexe
        :param par_client: tri des transactions par client, par compte, par code D
        """
        for donnee in paramannexe.donnees:
            if donnee['nom'] == 'Annexe-détails':
                self.chemin = donnee['chemin']
                self.dossier = donnee['dossier']
        dossier_destination = DossierDestination(self.chemin)

        for code in par_client.keys():
            self.valeurs = {}
            ii = 0
            self.nom = ""
            par_compte = par_client[code]['comptes']
            for id_compte in par_compte.keys():
                par_code = par_compte[id_compte]
                for code_d in par_code.keys():
                    tbtr = par_code[code_d]
                    base = trans_vals[tbtr[0]]
                    if self.nom == "":
                        self.nom = self.prefixe + "_" + code + "_" + base['client-name'] + ".csv"
                    donnee = []
                    for cle in range(2, len(self.cles)-6):
                        donnee.append(base[self.cles[cle]])
                    subside = 0
                    deduit = 0
                    discount = 0
                    bonus = 0
                    for indice in tbtr:
                        val = trans_vals[indice]
                        subside += val['subsid-CHF']
                        deduit += val['subsid-deduct']
                        discount += val['discount-bonus']
                        bonus += val['subsid-bonus']
                    g_id = id_compte + code_d
                    if g_id in grants.donnees.keys():
                        grant = grants.donnees[g_id]['montant']
                    else:
                        grant = 0

                    plaf = base['proj-subs'] + code_d
                    if plaf in plafonds.donnees.keys():
                        plafond = plafonds.donnees[plaf]
                        reste = plafond['max_compte'] - grant - subside

                        donnee += [round(grant, 2), round(subside, 2), round(deduit, 2), round(discount, 2),
                                   round(bonus, 2), round(reste, 2)]
                        self.ajouter_valeur(donnee, ii)
                        ii += 1
            if len(self.valeurs) > 0:
                self.csv(dossier_destination, paramtexte)
