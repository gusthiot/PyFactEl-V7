from importes import Fichier
from outils import Outils
from traitement import Rabais


class NoShow(Fichier):
    """
    Classe pour l'importation des données de No Show
    """

    cles = ['annee', 'mois', 'date_debut', 'type', 'id_machine', 'id_user', 'id_compte', 'penalite']
    nom_fichier = "noshow.csv"
    libelle = "Pénalités No Show"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def est_coherent(self, comptes, machines, users):
        """
        vérifie que les données du fichier importé sont cohérentes (id compte parmi comptes,
        id machine parmi machines, id user parmi user), et efface les colonnes mois et année
        :param comptes: comptes importés
        :param machines: machines importées
        :param users: users importés
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
        donnees_list = []

        for donnee in self.donnees:
            if donnee['id_compte'] == "":
                msg += "le id compte de la ligne " + str(ligne) + " ne peut être vide\n"
            elif comptes.contient_id(donnee['id_compte']) == 0:
                msg += "le id compte '" + donnee['id_compte'] + "' de la ligne " + str(ligne) + " n'est pas référencé\n"

            if donnee['id_machine'] == "":
                msg += "le machine id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif machines.contient_id(donnee['id_machine']) == 0:
                msg += "le machine id '" + donnee['id_machine'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_user'] == "":
                msg += "le user id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif users.contient_id(donnee['id_user']) == 0:
                msg += "le user id '" + donnee['id_user'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            donnee['penalite'], info = Outils.est_un_nombre(donnee['penalite'], "la pénalité", ligne)
            msg += info

            del donnee['annee']
            del donnee['mois']
            donnees_list.append(donnee)

            ligne += 1

        self.donnees = donnees_list
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
