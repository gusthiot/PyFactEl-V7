from outils import Outils
from traitement import Recap


class BilanPlates(Recap):
    """
    Classe pour la création du csv de bilan plateformes
    """

    cles = ['invoice-year', 'invoice-month', 'invoice-ref', 'platf-code', 'platf-op', 'platf-sap', 'platf-name',
            'platf-cf', 'platf-fund', 'client-code', 'client-sap', 'client-name', 'client-class', 'client-labelclass',
            'item-codeD', 'item-labelcode', 'item-sap', 'valuation-brut', 'valuation-net', 'deduct-CHF',
            'subsid-deduct', 'total-fact', 'discount-bonus', 'subsid-bonus', 'OP-code']

    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        super().__init__(edition)
        self.nom = "Bilan-plateforme-client_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + ".csv"

    def generer(self, trans_vals, paramtexte, dossier_destination, par_plate):
        """
        génération du fichier de bilan des plateformes à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param paramtexte: paramètres textuels
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param par_plate: tri des transactions par plateforme, par client, par code D
        """
        ii = 0
        for id_plate in par_plate.keys():
            par_client = par_plate[id_plate]['clients']
            for code in par_client.keys():
                par_code = par_client[code]
                for code_d in par_code.keys():
                    tbtr = par_code[code_d]
                    base = trans_vals[tbtr[0]]
                    donnee = []
                    for cle in range(2, len(self.cles)-8):
                        donnee.append(base[self.cles[cle]])
                    avant = 0
                    compris = 0
                    deduit = 0
                    sub_ded = 0
                    fact = 0
                    remb = 0
                    sub_remb = 0
                    for indice in tbtr:
                        val = trans_vals[indice]
                        brut, info = Outils.est_un_nombre(val['valuation-brut'], "le brut", arrondi=2)
                        if info != "":
                            Outils.affiche_message(info)
                        avant += brut
                        net, info = Outils.est_un_nombre(val['valuation-net'], "le net", arrondi=2)
                        if info != "":
                            Outils.affiche_message(info)
                        compris += net
                        ded, info = Outils.est_un_nombre(val['deduct-CHF'], "le déduit", arrondi=2)
                        if info != "":
                            Outils.affiche_message(info)
                        deduit += ded
                        subded, info = Outils.est_un_nombre(val['subsid-deduct'], "le déduit de subside", arrondi=2)
                        if info != "":
                            Outils.affiche_message(info)
                        sub_ded += subded
                        total, info = Outils.est_un_nombre(val['total-fact'], "le total", arrondi=2)
                        if info != "":
                            Outils.affiche_message(info)
                        fact += total
                        disc, info = Outils.est_un_nombre(val['discount-bonus'], "le discount", arrondi=2)
                        if info != "":
                            Outils.affiche_message(info)
                        remb += disc
                        bonus, info = Outils.est_un_nombre(val['subsid-bonus'], "le bonus subside", arrondi=2)
                        if info != "":
                            Outils.affiche_message(info)
                        sub_remb += bonus
                    op = base['platf-op'] + base['client-class'] + str(self.annee)[2:4] + \
                        Outils.mois_string(self.mois) + code_d
                    donnee += [round(avant, 2), round(compris, 2), round(deduit, 2), round(sub_ded, 2), round(fact, 2),
                               round(remb, 2), round(sub_remb, 2), op]
                    self.ajouter_valeur(donnee, ii)
                    ii += 1

        self.csv(dossier_destination, paramtexte)
