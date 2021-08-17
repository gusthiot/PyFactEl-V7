from traitement import AnnexeDetails
from traitement import AnnexeSubsides
from traitement import BilanPlates
from traitement import BilanUsages
from traitement import BilanConsos
from traitement import UserLabo
from datetime import datetime


class BilansTransacts(object):
    """
    Classe pour la création des csv des bilans des transactions
    """

    def __init__(self, edition):
        """
        initialisation des générateurs de bilans
        :param edition: paramètres d'édition
        """
        self.ann_dets = AnnexeDetails(edition)
        self.ann_subs = AnnexeSubsides(edition)
        self.bil_plat = BilanPlates(edition)
        self.bil_use = BilanUsages(edition)
        self.bil_conso = BilanConsos(edition)
        self.usr_lab = UserLabo(edition)

    def generer(self, transactions, grants, plafonds, paramtexte, paramannexe, dossier_destination):
        """
        tri des transactions et génération des bilans
        :param transactions: transactions générées
        :param grants: grants importés
        :param plafonds: plafonds importés
        :param paramtexte: paramètres textuels
        :param paramannexe: paramètres d'annexe
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        """
        par_client = {}
        par_plate = {}
        for key in transactions.valeurs.keys():
            transaction = transactions.valeurs[key]
            code_client = transaction['client-code']
            id_compte = transaction['proj-id']
            id_plateforme = transaction['platf-code']
            code_d = transaction['item-codeD']
            item = transaction['item-id']
            user_id = transaction['user-id']
            date = transaction['transac-date']

            if code_client not in par_client.keys():
                par_client[code_client] = {'transactions': [], 'comptes': {}}

            par_client[code_client]['transactions'].append(key)

            pcc = par_client[code_client]['comptes']
            if id_compte not in pcc.keys():
                pcc[id_compte] = {}
            pcd = pcc[id_compte]
            if code_d not in pcd.keys():
                pcd[code_d] = [key]
            else:
                pcd[code_d].append(key)

            if id_plateforme not in par_plate.keys():
                par_plate[id_plateforme] = {'clients': {}, 'items': {}, 'users': {}}

            ppc = par_plate[id_plateforme]['clients']
            if code_client not in ppc.keys():
                ppc[code_client] = {}
            ppd = ppc[code_client]
            if code_d not in ppd.keys():
                ppd[code_d] = [key]
            else:
                ppd[code_d].append(key)

            ppi = par_plate[id_plateforme]['items']
            if item not in ppi.keys():
                ppi[item] = [key]
            else:
                ppi[item].append(key)

            ppu = par_plate[id_plateforme]['users']
            if user_id not in ppu.keys():
                ppu[user_id] = {}
            if code_client not in ppu[user_id].keys():
                ppu[user_id][code_client] = {}
            day = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').day
            ppuc = ppu[user_id][code_client]
            if day not in ppuc.keys():
                ppuc[day] = key

        self.ann_dets.generer(transactions, paramtexte, paramannexe, par_client)
        self.ann_subs.generer(transactions, grants, plafonds, paramtexte, paramannexe, par_client)
        self.bil_plat.generer(transactions, paramtexte, dossier_destination, par_plate)
        self.bil_use.generer(transactions, paramtexte, dossier_destination, par_plate)
        self.bil_conso.generer(transactions, paramtexte, dossier_destination, par_plate)
        self.usr_lab.generer(transactions, paramtexte, dossier_destination, par_plate)
