from importes import Fichier
from outils import Outils


class Plateforme(Fichier):
    """
    Classe pour l'importation des données de Plateformes
    """

    nom_fichier = "plateforme.csv"
    cles = ['id_plateforme', 'code_p', 'centre', 'fonds', 'intitule', 'grille']
    libelle = "Plateformes"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contient_id(self, id_plat):
        """
        vérifie si une plateforme contient l'id donné
        :param id_plat: id à vérifier
        :return: 1 si id contenu, 0 sinon
        """
        if self.verifie_coherence == 1:
            if id_plat in self.donnees.keys():
                return 1
        else:
            for plat in self.donnees:
                if plat['id_plateforme'] == id_plat:
                    return 1
        return 0

    def est_coherent(self, clients):
        """
        vérifie que les données du fichier importé sont cohérentes
        :param clients: clients importés
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_dict = {}
        ids = []

        del self.donnees[0]
        for donnee in self.donnees:
            if donnee['id_plateforme'] == "":
                msg += "l'id plateforme " + str(ligne) + " ne peut être vide\n"
            elif donnee['id_plateforme'] not in clients.obtenir_codes():
                msg += "l'id plateforme de la ligne " + str(ligne) + " n'existe pas dans les clients \n"
            elif donnee['id_plateforme'] not in ids:
                ids.append(donnee['id_plateforme'])
            else:
                msg += "l'id plateforme de la ligne " + str(ligne) + " n'est pas unique \n"

            donnees_dict[donnee['id_plateforme']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
