from outils import Outils
from traitement import Recap
from dateutil.parser import parse


class Transactions(Recap):
    """
    Classe pour la création des transactions
    """

    cles = ['invoice-year', 'invoice-month', 'invoice-ref', 'client-code', 'client-sap', 'client-name', 'client-class',
            'client-labelclass', 'oper-id', 'oper-name', 'oper-note', 'staff-note', 'mach-id', 'mach-name', 'user-id',
            'user-sciper', 'user-name', 'user-first', 'proj-id', 'proj-nbr', 'proj-name', 'proj-expl', 'proj-subs',
            'proj-start', 'proj-end', 'item-id', 'item-type', 'item-nbr', 'item-name', 'item-unit', 'item-codeD',
            'item-labelcode', 'item-sap', 'item-extra', 'platf-code', 'platf-op', 'platf-sap', 'platf-name', 'platf-cf',
            'platf-fund', 'transac-date', 'transac-quantity', 'transac-usage', 'valuation-price', 'valuation-brut',
            'discount-type', 'discount-CHF', 'deduct-CHF', 'valuation-net', 'subsid-code', 'subsid-name',
            'subsid-maxproj', 'subsid-maxmois', 'subsid-reste', 'subsid-CHF', 'subsid-deduct', 'discount-bonus',
            'subsid-bonus', 'total-fact']
    
    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        super().__init__(edition)
        self.version = edition.version
        self.nom = "Transaction_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + \
            str(edition.version)
        if edition.version > 0:
            self.nom += "_" + str(edition.client_unique)
        self.nom += ".csv"
        self.comptabilises = {}

    def generer(self, acces, noshows, livraisons, prestations, machines, categprix, comptes, clients, users,
                droits, plateformes, generaux, articles, tarifs, subsides, plafonds, grants, paramtexte):
        """
        génération du fichier des transactions
        :param acces: accès importés
        :param noshows: no show importés
        :param livraisons: livraisons importées
        :param prestations: prestations importées
        :param machines: machines importées
        :param categprix: catégories de prix importées
        :param comptes: comptes importés
        :param clients: clients importés
        :param users: users importés
        :param droits: droits importés
        :param plateformes: plateformes importées
        :param generaux: paramètres généraux
        :param articles: articles générés
        :param tarifs: tarifs générés
        :param subsides: subsides importés
        :param plafonds: plafonds importés
        :param grants: grants importés
        :param paramtexte: paramètres textuels
        """

        pt = paramtexte.donnees
        transacts = {}

        for entree in acces.donnees:
            compte = comptes.donnees[entree['id_compte']]
            client = clients.donnees[compte['code_client']]
            code_n = client['nature']
            id_machine = entree['id_machine']
            machine = machines.donnees[id_machine]
            ref_client = self.ref_client(generaux, client)
            operateur = users.donnees[entree['id_op']]
            ope = [entree['id_op'], operateur['prenom'] + " " + operateur['nom'], entree['remarque_op'],
                   entree['remarque_staff'], id_machine, machine['nom']]
            util_proj = self.util_proj(entree['id_user'], users, compte, droits)
            date = parse(entree['date_login'])

            # K3 CAE-run #
            if entree['duree_machine_hp'] > 0 or entree['duree_machine_hc'] > 0:
                article = articles.valeurs[machine['id_cat_plat']]
                tarif = tarifs.valeurs[code_n + machine['id_cat_plat']]
                art = self.art_plate(article, plateformes, clients)
                if article['platf-code'] == compte['code_client']:
                    usage = 0
                else:
                    usage = 1
                trans = [entree['date_login'], 1, usage]
                val = [tarif['valuation-price'], tarif['valuation-price'], "", 0, 0, tarif['valuation-price']]
                self.put_in_transacts(transacts, date, ref_client, ope, util_proj, art, trans, val, 0)

            # K1 CAE-HP #
            duree_hp = round(entree['duree_machine_hp']/60, 4)
            if duree_hp > 0:
                article = articles.valeurs[machine['id_cat_mach']]
                art = self.art_plate(article, plateformes, clients)
                if article['platf-code'] == compte['code_client'] and compte['exploitation'] == "TRUE":
                    usage = 0
                else:
                    usage = duree_hp
                trans = [entree['date_login'], duree_hp, usage]
                tarif = tarifs.valeurs[code_n + machine['id_cat_mach']]
                prix = round(duree_hp * tarif['valuation-price'], 2)
                val = [tarif['valuation-price'], prix, "", 0, 0, prix]
                self.put_in_transacts(transacts, date, ref_client, ope, util_proj, art, trans, val, 0)

            # K1 CAE-HC #
            duree_hc = round(entree['duree_machine_hc']/60, 4)
            if duree_hc > 0:
                article = articles.valeurs[machine['id_cat_mach']]
                art = self.art_plate(article, plateformes, clients)
                if article['platf-code'] == compte['code_client'] and compte['exploitation'] == "TRUE":
                    usage = 0
                else:
                    usage = duree_hc
                trans = [entree['date_login'], duree_hc, usage]
                tarif = tarifs.valeurs[code_n + machine['id_cat_mach']]
                prix = round(duree_hc * tarif['valuation-price'], 2)
                reduc = round(tarif['valuation-price'] * machine['tx_rabais_hc']/100 * duree_hc, 2)
                if generaux.avantage_hc_par_code_n(code_n) == "RABAIS":
                    deduit = reduc
                    remb = 0
                else:
                    if generaux.avantage_hc_par_code_n(code_n) == "BONUS":
                        deduit = 0
                        remb = reduc
                    else:
                        deduit = 0
                        remb = 0
                val = [tarif['valuation-price'], prix, pt['discount-HC'] + " -" + str(machine['tx_rabais_hc']) + "%",
                       reduc, deduit, prix-deduit]
                self.put_in_transacts(transacts, date, ref_client, ope, util_proj, art, trans, val, remb)

            # K2 CAE-MO #
            duree_op = round(entree['duree_operateur']/60, 4)
            if duree_op > 0:
                article = articles.valeurs[machine['id_cat_mo']]
                art = self.art_plate(article, plateformes, clients)
                if article['platf-code'] == compte['code_client']:
                    usage = 0
                else:
                    usage = duree_op
                trans = [entree['date_login'], duree_op, usage]
                tarif = tarifs.valeurs[code_n + machine['id_cat_mo']]
                prix = round(duree_op * tarif['valuation-price'], 2)
                val = [tarif['valuation-price'], prix, "", 0, 0, prix]
                self.put_in_transacts(transacts, date, ref_client, ope, util_proj, art, trans, val, 0)

            # K4 CAE-Extra #
            prix_extra = categprix.donnees[code_n + machine['id_cat_cher']]['prix_unit']
            if prix_extra > 0:
                article = articles.valeurs[machine['id_cat_cher']]
                duree = duree_hp + duree_hc
                if article['platf-code'] == compte['code_client'] and compte['exploitation'] == "TRUE":
                    usage = 0
                else:
                    usage = duree
                trans = [entree['date_login'], duree, usage]
                art = self.art_plate(article, plateformes, clients)
                tarif = tarifs.valeurs[code_n + machine['id_cat_cher']]
                prix = round(duree * tarif['valuation-price'], 2)
                val = [tarif['valuation-price'], prix, "", 0, 0, prix]
                self.put_in_transacts(transacts, date, ref_client, ope, util_proj, art, trans, val, 0)

        for entree in noshows.donnees:
            compte = comptes.donnees[entree['id_compte']]
            client = clients.donnees[compte['code_client']]
            code_n = client['nature']
            ref_client = self.ref_client(generaux, client)
            id_machine = entree['id_machine']
            machine = machines.donnees[id_machine]
            if entree['type'] == 'HP':
                # K5 NoShow-HP #
                article = articles.valeurs[machine['id_cat_hp']]
                tarif = tarifs.valeurs[code_n + machine['id_cat_hp']]
            else:
                # K6 NoShow-HC #
                article = articles.valeurs[machine['id_cat_hc']]
                tarif = tarifs.valeurs[code_n + machine['id_cat_hc']]
            ope = ["", "", "", "", id_machine, machine['nom']]
            art = self.art_plate(article, plateformes, clients)
            util_proj = self.util_proj(entree['id_user'], users, compte, droits)
            trans = [entree['date_debut'], entree['penalite'], 0]
            prix = round(entree['penalite'] * tarif['valuation-price'], 2)
            val = [tarif['valuation-price'], prix, "", 0, 0, prix]
            date = parse(entree['date_debut'])
            self.put_in_transacts(transacts, date, ref_client, ope, util_proj, art, trans, val, 0)

        for entree in livraisons.donnees:
            compte = comptes.donnees[entree['id_compte']]
            client = clients.donnees[compte['code_client']]
            code_n = client['nature']
            ref_client = self.ref_client(generaux, client)
            id_prestation = entree['id_prestation']
            prestation = prestations.donnees[id_prestation]
            operateur = users.donnees[entree['id_operateur']]
            id_machine = prestation['id_machine']
            article = articles.valeurs[id_prestation]
            art = self.art_plate(article, plateformes, clients)
            if id_machine == "0":
                # LVR-mag #
                idm = ""
                nm = ""
            else:
                # LVR-mach #
                idm = id_machine
                machine = machines.donnees[id_machine]
                nm = machine['nom']
            ope = [entree['id_operateur'], operateur['prenom'] + " " + operateur['nom'],
                   pt['oper-PO'] + " " + entree['date_commande'], entree['remarque'], idm, nm]
            util_proj = self.util_proj(entree['id_user'], users, compte, droits)
            trans = [entree['date_livraison'], entree['quantite'], 0]
            tarif = tarifs.valeurs[code_n + id_prestation]
            if entree['rabais'] > 0:
                discount = pt['discount-LVR']
            else:
                discount = ""
            if generaux.rabais_excep_par_code_n(code_n) == "RABAIS":
                rabais = - entree['rabais']
                remb = 0
            else:
                if generaux.rabais_excep_par_code_n(code_n) == "BONUS":
                    rabais = 0
                    remb = entree['rabais']
                else:
                    rabais = 0
                    remb = 0
            prix = round(entree['quantite'] * tarif['valuation-price'], 2)
            val = [tarif['valuation-price'], prix, discount, - entree['rabais'], rabais, prix-rabais]
            date = parse(entree['date_livraison'])
            self.put_in_transacts(transacts, date, ref_client, ope, util_proj, art, trans, val, remb)

        i = 0
        for tr in sorted(transacts.keys()):
            tarray = transacts[tr]
            for transact in tarray:
                id_compte = transact['up'][4]
                compte = comptes.donnees[id_compte]
                article = articles.valeurs[transact['art'][0]]
                code_n = transact['rc'][4]
                dans = self.date_dans_projet(transact['trans'][0], transact['up'][0], compte, droits)
                subs = self.subsides(subsides, plafonds, grants, compte, code_n, article, dans, transact['val'][5],
                                     generaux)
                if generaux.subsides_par_code_n(code_n) == "BONUS":
                    remb = subs[5]
                else:
                    remb = 0
                if article['platf-code'] == compte['code_client']:
                    tot = 0
                else:
                    tot = transact['val'][5] - subs[6]
                mont = [transact['remb'], remb, tot]
                donnee = transact['rc'] + transact['ope'] + transact['up'] + transact['art'] + transact['trans'] + \
                    transact['val'] + subs + mont
                self.ajouter_valeur(donnee, i)
                i = i + 1

    def ref_client(self, generaux, client):
        """
        ajout de la référence et des valeurs issues du client
        :param generaux: paramètres généraux
        :param client: client de la transaction
        :return tableau contenant la référence et les valeurs du client
        """
        code_ref = generaux.code_ref_par_code_n(client['nature'])
        reference = code_ref + str(self.annee)[2:] + Outils.mois_string(self.mois) + "." + client['code']
        if self.version > 0:
            reference += "-" + str(self.version)
        return [reference, client['code'], client['code_sap'], client['abrev_labo'], client['nature'],
                generaux.intitule_n_par_code_n(client['nature'])]

    @staticmethod
    def util_proj(id_user, users, compte, droits):
        """
        ajout des valeurs issues de l'utilisateur et du projet (compte)
        :param id_user: id de l'utilisateur de la transaction
        :param users: users importés
        :param compte: compte de la transaction
        :param droits: droits importés
        :return tableau contenant les valeurs de l'utilisateur et du projet
        """
        user = users.donnees[id_user]
        id_droit = id_user + compte['id_compte']
        if id_droit in droits.donnees.keys():
            debut = droits.donnees[id_droit]['debut']
            fin = droits.donnees[id_droit]['fin']
        else:
            debut = "N/A"
            fin = "N/A"

        return [user['id_user'], user['sciper'], user['nom'], user['prenom'], compte['id_compte'], compte['numero'],
                compte['intitule'], compte['exploitation'], compte['type_subside'], debut, fin]

    @staticmethod
    def art_plate(article, plateformes, clients):
        """
        ajout des valeurs issues de l'article et de la plateforme
        :param article: article de la transaction
        :param plateformes: plateformes importées
        :param clients: clients importés
        :return tableau contenant les valeurs de l'article et de la plateforme
        """
        plateforme = plateformes.donnees[article['platf-code']]
        client = clients.donnees[plateforme['id_plateforme']]
        return [article['item-id'], article['item-type'], article['item-nbr'], article['item-name'],
                article['item-unit'], article['item-codeD'], article['item-labelcode'], article['item-sap'],
                article['item-extra'], article['platf-code'], plateforme['code_p'], client['code_sap'],
                plateforme['intitule'], plateforme['centre'], plateforme['fonds']]

    def subsides(self, subsides, plafonds, grants, compte, code_n, article, dans, montant, generaux):
        """
        ajout des valeurs issues des subsides
        :param subsides: subsides importés
        :param plafonds: plafonds importés
        :param grants: grants importés
        :param compte: compte de la transaction
        :param code_n: code N de la transaction
        :param article: article de la transaction
        :param dans: si la transaction est dans la période de subside
        :param montant: montant de la transaction
        :param generaux: paramètres généraux
        :return tableau contenant les valeurs de subsides
        """
        type_s = compte['type_subside']
        if type_s != "" and type_s != "STD" and dans:
            plaf = type_s + article['item-codeD']
            if plaf in plafonds.donnees.keys():
                plafond = plafonds.donnees[plaf]
                sub = type_s + article['platf-code'] + code_n
                if sub in subsides.donnees.keys():
                    subside = subsides.donnees[sub]
                    cg_id = compte['id_compte'] + article['item-codeD']
                    if cg_id in grants.donnees.keys():
                        grant = grants.donnees[cg_id]['montant']
                    else:
                        grant = 0
                    if cg_id in self.comptabilises.keys():
                        comptabilise = self.comptabilises[cg_id]['montant']
                    else:
                        comptabilise = 0
                    res_compte = plafond['max_compte'] - (grant + comptabilise)
                    res_mois = plafond['max_mois'] - comptabilise
                    res = max(min(res_compte, res_mois), 0)
                    mon = min(montant, res)
                    if cg_id not in self.comptabilises.keys():
                        self.comptabilises[cg_id] = {'id_compte': compte['id_compte'], 'code_d': article['item-codeD'],
                                                     'montant': mon}
                    else:
                        self.comptabilises[cg_id]['montant'] = self.comptabilises[cg_id]['montant'] + mon
                    if generaux.subsides_par_code_n(code_n) == "RABAIS":
                        ded = mon
                    else:
                        ded = 0
                    return [subside['type'], subside['intitule'], plafond['max_compte'], plafond['max_mois'], res, mon,
                            ded]
        return ["", "", 0, 0, 0, 0, 0]

    @staticmethod
    def date_dans_projet(date, id_user, compte, droits):
        """
        vérifie si la transaction est dans la période de subside
        :param date: date de la transaction
        :param id_user: id de l'utilisateur de la transaction
        :param compte: compte de la transaction
        :param droits: droits importés
        """
        id_droit = id_user + compte['id_compte']
        if id_droit not in droits.donnees.keys():
            return False
        debut = droits.donnees[id_droit]['debut']
        fin = droits.donnees[id_droit]['fin']
        if debut != "NULL" and parse(date) < parse(debut):
            return False
        if fin != "NULL" and parse(date) > parse(fin):
            return False
        return True

    @staticmethod
    def put_in_transacts(transacts, date, ref_client, ope, util_proj, art, trans, val, remb):
        """
        rajoute une ligne de transaction (avant tri chronologique et traitement des subsides)
        :param transacts: tableau des transactions
        :param date: date de la transaction
        :param ref_client: référence et valeurs issues du client
        :param ope: valeurs issues de l'opérateur
        :param util_proj: valeurs issues de l'utilisateur et du projet
        :param art: valeurs issues de l'article et de la plateforme
        :param trans: valeurs de transaction
        :param val: valeurs d'évaluation
        :param remb: valeurs de remboursement
        """
        if date not in transacts.keys():
            transacts[date] = []
        transacts[date].append({'rc': ref_client, 'ope': ope, 'up': util_proj, 'art': art, 'trans': trans, 'val': val,
                                'remb': remb})

    @staticmethod
    def ouvrir_csv(dossier_source, fichier):
        """
        ouverture d'un csv comme string
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param fichier: nom du fichier csv
        :return: donnees du csv modifiées en tant que string
        """
        donnees_csv = []
        try:
            fichier_reader = dossier_source.reader(fichier)
            for ligne in fichier_reader:
                if ligne == -1:
                    continue
                donnees_csv.append(ligne)
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : " + fichier)
        return donnees_csv

    def recuperer_valeurs_de_fichier(self, dossier_source, fichier):
        valeurs = {}
        trans_tab = self.ouvrir_csv(dossier_source, fichier)
        valeur = {}
        for j in range(0, len(trans_tab)):
            ligne = trans_tab[j]
            for i in range(0, len(ligne)):
                valeur[self.cles[i]] = ligne[i]
            valeurs[j] = valeur
        return valeurs
