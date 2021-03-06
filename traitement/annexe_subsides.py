from outils import Outils
from traitement import Recap
from importes import DossierDestination
from datetime import datetime
import calendar


class AnnexeSubsides(Recap):
    """
    Classe pour la création du csv d'annexe subsides
    """

    cles = ['invoice-year', 'invoice-month', 'client-code', 'client-name', 'proj-id', 'proj-name', 'proj-subs',
            'item-codeD', 'item-labelcode', 'subsid-name', 'subsid-start', 'subsid-end', 'subsid-maxproj',
            'subsid-maxmois', 'subsid-alrdygrant', 'subsid-CHF', 'subsid-reste']

    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        super().__init__(edition)
        self.version = edition.version
        self.unique = edition.client_unique
        self.nom = ""
        self.dossier = ""
        self.chemin = "./"
        self.prefixe = "Annexe-subsides_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + \
            str(edition.version)

    def generer(self, trans_vals, grants, plafonds, paramtexte, paramannexe, par_client, comptes, clients, subsides,
                generaux):
        """
        génération des fichiers d'annexes subsides à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param grants: grants importés
        :param plafonds: plafonds importés
        :param paramtexte: paramètres textuels
        :param paramannexe: paramètres d'annexe
        :param par_client: tri des transactions par client, par compte, par code D
        :param comptes: comptes importés
        :param clients: clients importés
        :param subsides: subsides importés
        :param generaux: paramètres généraux
        """
        for donnee in paramannexe.donnees:
            if donnee['nom'] == 'Annexe-détails':
                self.chemin = donnee['chemin']
                self.dossier = donnee['dossier']
        dossier_destination = DossierDestination(self.chemin)

        clients_comptes = {}
        for id_compte in comptes.donnees.keys():
            compte = comptes.donnees[id_compte]
            if self.version > 0 and self.unique != compte['code_client']:
                continue
            type_s = compte['type_subside']
            if type_s != "":
                if type_s in subsides.donnees.keys():
                    subside = subsides.donnees[type_s]
                    if subside['debut'] != 'NULL':
                        debut, info = Outils.est_une_date(subside['debut'], "la date de début")
                        if info != "":
                            Outils.affiche_message(info)
                    else:
                        debut = 'NULL'
                    if subside['fin'] != 'NULL':
                        fin, info = Outils.est_une_date(subside['fin'], "la date de fin")
                        if info != "":
                            Outils.affiche_message(info)
                    else:
                        fin = 'NULL'

                    premier, dernier = calendar.monthrange(self.annee, self.mois)
                    if debut == "NULL" or debut <= datetime(self.annee, self.mois, dernier):
                        if fin == "NULL" or fin >= datetime(self.annee, self.mois, 1):
                            code_client = compte['code_client']
                            if code_client not in clients_comptes:
                                clients_comptes[code_client] = []
                            clients_comptes[code_client].append(id_compte)

        for code in clients_comptes.keys():
            cc = clients_comptes[code]
            self.valeurs = {}
            ii = 0
            client = clients.donnees[code]
            self.nom = self.prefixe + "_" + code + "_" + client['abrev_labo'] + ".csv"
            for id_compte in cc:
                compte = comptes.donnees[id_compte]
                type_s = compte['type_subside']
                subside = subsides.donnees[type_s]
                for code_d in generaux.obtenir_code_d():
                    plaf = type_s + code_d
                    if plaf in plafonds.donnees.keys():
                        plafond = plafonds.donnees[plaf]
                        donnee = [client['code'], client['abrev_labo'], compte['id_compte'], compte['intitule'],
                                  compte['type_subside'], code_d, generaux.intitule_long_par_code_d(code_d),
                                  subside['intitule'], subside['debut'], subside['fin'], plafond['max_compte'],
                                  plafond['max_mois']]
                        subs = 0
                        g_id = id_compte + code_d
                        if g_id in grants.donnees.keys():
                            grant, info = Outils.est_un_nombre(grants.donnees[g_id]['montant'], "le montant de grant",
                                                               min=0, arrondi=2)
                            if info != "":
                                Outils.affiche_message(info)
                        else:
                            grant = 0
                        if code in par_client and id_compte in par_client[code]['comptes']:
                            par_code = par_client[code]['comptes'][id_compte]
                            if code_d in par_code.keys():
                                tbtr = par_code[code_d]
                                for indice in tbtr:
                                    val, info = Outils.est_un_nombre(trans_vals[indice]['subsid-CHF'], "le subside CHF",
                                                                     arrondi=2)
                                    subs += val

                        reste = plafond['max_compte'] - grant - subs
                        donnee += [round(grant, 2), round(subs, 2), round(reste, 2)]
                        self.ajouter_valeur(donnee, ii)
                        ii += 1
            self.csv(dossier_destination, paramtexte)
