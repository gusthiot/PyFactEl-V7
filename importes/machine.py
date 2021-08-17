from importes import Fichier
from outils import Outils


class Machine(Fichier):
    """
    Classe pour l'importation des données de Machines Cmi
    """

    cles = ['annee', 'mois', 'id_machine', 'nom', 'id_cat_mach', 'tx_rabais_hc', 'id_cat_mo', 'id_cat_plat',
            'id_cat_cher', 'id_cat_hp', 'id_cat_hc']
    nom_fichier = "machine.csv"
    libelle = "Machines"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contient_id(self, id_machine):
        """
        vérifie si une machine contient l'id donné
        :param id_machine: id à vérifier
        :return: 1 si id contenu, 0 sinon
        """
        if self.verifie_coherence == 1:
            if id_machine in self.donnees.keys():
                return 1
        else:
            for machine in self.donnees:
                if machine['id_machine'] == id_machine:
                    return 1
        return 0

    def est_coherent(self, categories):
        """
        vérifie que les données du fichier importé sont cohérentes, et efface les colonnes mois et année
        :param categories: catégories importées
        :return: 1 s'il y a une erreur, 0 sinon
        """
        if self.verifie_date == 0:
            info = self.libelle + ". vous devez vérifier la date avant de vérifier la cohérence"
            Outils.affiche_message(info)
            return 1

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        ids = []
        donnees_dict = {}

        for donnee in self.donnees:
            if donnee['id_machine'] == "":
                msg += "le machine id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['id_machine'] not in ids:
                ids.append(donnee['id_machine'])
            else:
                msg += "l'id machine '" + donnee['id_machine'] + "' de la ligne " + str(ligne) +\
                       " n'est pas unique\n"

            if donnee['id_cat_mach'] == "":
                msg += "l'id catégorie machine de la ligne " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_cat_mach']) == 0:
                msg += "l'id catégorie machine '" + donnee['id_cat_mach'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_cat_mo'] == "":
                msg += "l'id catégorie opérateur de la ligne " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_cat_mo']) == 0:
                msg += "l'id catégorie opérateur '" + donnee['id_cat_mo'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_cat_plat'] == "":
                msg += "l'id catégorie plateforme de la ligne " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_cat_plat']) == 0:
                msg += "l'id catégorie plateforme '" + donnee['id_cat_plat'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_cat_cher'] == "":
                msg += "l'id catégorie onéreux de la ligne " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_cat_cher']) == 0:
                msg += "l'id catégorie onéreux '" + donnee['id_cat_cher'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_cat_hp'] == "":
                msg += "l'id catégorie hp de la ligne " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_cat_hp']) == 0:
                msg += "l'id catégorie hp '" + donnee['id_cat_hp'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_cat_hc'] == "":
                msg += "l'id catégorie hc de la ligne " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_cat_hc']) == 0:
                msg += "l'id catégorie hc '" + donnee['id_cat_hc'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            donnee['tx_rabais_hc'], info = Outils.est_un_nombre(donnee['tx_rabais_hc'],
                                                                "le rabais heures creuses", ligne)
            msg += info
            if donnee['tx_rabais_hc'] < 0 or donnee['tx_rabais_hc'] > 100:
                msg += "le rabais heures creuse '" + str(donnee['tx_rabais_hc']) + "' de la ligne " + str(ligne) \
                       + " doit être entre 0 et 100\n"

            del donnee['annee']
            del donnee['mois']
            donnees_dict[donnee['id_machine']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
