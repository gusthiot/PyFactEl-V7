from importes import Fichier
from outils import Outils


class Subside(Fichier):
    """
    Classe pour l'importation des données de Subsides
    """

    nom_fichier = "subside.csv"
    cles = ['type', 'intitule', 'id_plateforme', 'code_n']
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

    def est_coherent(self, plateformes, generaux):
        """
        vérifie que les données du fichier importé sont cohérentes
        :param plateformes: plateformes importées
        :param generaux: paramètres généraux
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_dict = {}

        del self.donnees[0]
        for donnee in self.donnees:
            if donnee['id_plateforme'] == "":
                msg += "l'id plateforme de la ligne " + str(ligne) + " ne peut être vide\n"
            elif plateformes.contient_id(donnee['id_plateforme']) == 0:
                msg += "l'id plateforme '" + donnee['id_plateforme'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"
            if donnee['code_n'] == "":
                msg += "la code N de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['code_n'] not in generaux.obtenir_code_n():
                msg += "la code N de la ligne " + str(ligne) + " n'existe pas dans les codes N\n"

            self.__types.append(donnee['type'])
            donnees_dict[donnee['type']+donnee['id_plateforme']+donnee['code_n']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
