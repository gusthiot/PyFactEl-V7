

class Rabais(object):
    """
    Classe contenant les règles de rabais
    """

    @staticmethod
    def rabais_emolument(mt, emb):
        """
        calcule le rabais sur émolument
        :param mt: mt
        :param emb: émolument de base mensuel
        :return: em, er
        """

        em = emb

        if mt > 0:
            er = 0
        else:
            er = emb
        return em, er

    @staticmethod
    def rabais_reservation_petit_montant(rm, rmin):
        """
        si le montant ne dépasse pas un seuil minimum, un rabais égal à ce montant est appliqué
        :param rm: montant
        :param rmin: seuil
        :return: rabais
        """
        if rm < int(rmin):
            return rm
        else:
            return 0
