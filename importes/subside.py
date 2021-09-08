from importes import Fichier
from outils import Outils


class Subside(Fichier):
    """
    Classe pour l'importation des données de Subsides
    """

    nom_fichier = "subside.csv"
    cles = ['type', 'intitule', 'id_plateforme', 'code_n', 'code_client', 'id_machine']
    libelle = "Subsides"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__types = []

    def contient_type(self, ty):
        """
        vérifie si un subside contient le type donné
        :param ty: type à vérifier
        :return: 1 si id contenu, 0 sinon
        """
        if self.verifie_coherence == 1:
            if ty in self.__types:
                return 1
        else:
            for subside in self.donnees:
                if subside['type'] == ty:
                    return 1
        return 0

    def est_coherent(self, plateformes, clients, machines, generaux):
        """
        vérifie que les données du fichier importé sont cohérentes
        :param plateformes: plateformes importées
        :param clients: clients importés
        :param machines: machines importées
        :param generaux: paramètres généraux
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_dict = {}
        quintuplets = []

        del self.donnees[0]
        for donnee in self.donnees:
            donnee['type'], info = Outils.est_un_alphanumerique(donnee['type'], "le type subside", ligne)
            msg += info
            donnee['intitule'], info = Outils.est_un_texte(donnee['intitule'], "l'intitulé", ligne)
            msg += info

            if donnee['id_plateforme'] == "":
                msg += "l'id plateforme de la ligne " + str(ligne) + " ne peut être vide\n"
            elif plateformes.contient_id(donnee['id_plateforme']) == 0:
                msg += "l'id plateforme '" + donnee['id_plateforme'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['code_n'] != "0" and donnee['code_n'] not in generaux.obtenir_code_n():
                msg += "la code N de la ligne " + str(ligne) + " n'existe pas dans les codes N\n"

            if donnee['code_client'] != "0" and donnee['code_client'] not in clients.donnees:
                msg += "le code client " + donnee['code_client'] + " de la ligne " + str(ligne) + \
                       " n'est pas référencé\n"

            if donnee['id_machine'] != "0" and machines.contient_id(donnee['id_machine']) == 0:
                msg += "le machine id '" + donnee['id_machine'] + "' de la ligne " + str(ligne)\
                       + " n'est pas référencé\n"

            quintuplet = donnee['type'] + donnee['id_plateforme'] + donnee['code_n'] + donnee['code_client'] + \
                donnee['id_machine']

            if quintuplet not in quintuplets:
                quintuplets.append(quintuplet)
            else:
                msg += "le quintuplet de la ligne " + str(ligne) + \
                       " n'est pas unique\n"

            self.__types.append(donnee['type'])

            # niv1 = donnee['type'] + donnee['id_plateforme']
            # if niv1 not in donnees_dict:
            #     donnees_dict[niv1] = {}
            # if donnee['code_n'] not in donnees_dict[niv1]:
            #     donnees_dict[niv1][donnee['code_n']] = {}
            # dict_n = donnees_dict[niv1][donnee['code_n']]
            # if donnee['code_client'] not in dict_n:
            #     dict_n[donnee['code_client']] = {}
            # dict_c = dict_n[donnee['code_client']]
            # if donnee['id_machine'] not in dict_c:
            #     dict_c[donnee['id_machine']] = donnee
            #
            donnees_dict[donnee['type'] + donnee['id_plateforme'] + donnee['code_n']] = donnee

            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
