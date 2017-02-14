import psycopg2


class Stat_equipe:
    """Classe définissant une équipe caractérisée par :
    - son nom ;
    - son poste ;
    - sa date de naissance ;
    - sa taille ;
    - son poids """

    def __init__(self, code_equipe, code_adversaire, id_match, domicile, victoire,
                 possession, nbr_buts_mis, nbr_buts_pris, nbr_tirs, nbr_tirs_contres, nbr_tirs_contres_def,  nbr_tirs_cadres, nbr_tirs_non_cadres,
                 nbr_passes, nbr_passes_reussies, nbr_corners, nbr_corners_def, nbr_hors_jeu, nbr_occasions, nbr_occasions_def,
                 nbr_duels_gagnes, nbr_duels_perdus, nbr_fautes_commises, nbr_cjaunes, nbr_crouges, classement_avant_match,
                 classement_apres_match, tactique):
        self.code_equipe = code_equipe
        self.code_adversaire = code_adversaire
        self.id_match = id_match
        self.domicile = domicile
        self.victoire = victoire
        self.possession = possession
        self.nbr_buts_mis = nbr_buts_mis
        self.nbr_buts_pris = nbr_buts_pris
        self.nbr_tirs = nbr_tirs
        self.nbr_tirs_contres = nbr_tirs_contres
        self.nbr_tirs_contres_def = nbr_tirs_contres_def
        self.nbr_tirs_cadres = nbr_tirs_cadres
        self.nbr_tirs_Non_cadres = nbr_tirs_non_cadres
        self.nbr_passes = nbr_passes
        self.nbr_passes_reussies = nbr_passes_reussies
        self.nbr_corners = nbr_corners
        self.nbr_corners_def = nbr_corners_def
        self.nbr_hors_jeu = nbr_hors_jeu
        self.nbr_occasions = nbr_occasions
        self.nbr_occasions_def = nbr_occasions_def
        self.nbr_duels_gagnes = nbr_duels_gagnes
        self.nbr_duels_perdus = nbr_duels_perdus
        self.nbr_fautes_commises = nbr_fautes_commises
        self.nbr_cjaunes = nbr_cjaunes
        self.nbr_crouges = nbr_crouges
        self.classement_avant_match = classement_avant_match
        self.classement_apres_match = classement_apres_match
        self.tactique = tactique


    def create_request_insert(self):
        request_insert = "INSERT INTO stat_equipe_par_match ("
        values = []
        nb_attribut = 0
        for attribut, value in self.__dict__.items():
            if not value == "":
                request_insert += str(attribut) + ","
                values.append(value)
                nb_attribut += 1
        request_insert = request_insert[:-1] + ") VALUES (" + nb_attribut * "%s,"
        request_insert = request_insert[:-1] + ")"

        return request_insert, values


    def create_stat(self, conn):
        """Méthode appelée quand on souhaite ajouter une state dans la base"""

        request_insert, values = self.create_request_insert()
        cur = conn.cursor()
        cur.execute(request_insert, values)
        conn.commit()
        cur.close()


def get_stat_fromDB(code_equipe, id_match, conn):
    """Méthode pour récupérer les stats d'équipe de la base"""
    cur = conn.cursor()
    cur.execute(
        "SELECT code_equipe, code_adversaire, id_match, domicile,"
        "victoire, possession, nbr_buts_mis, nbr_buts_pris, nbr_tirs, nbr_tirs_contres"
        "nbr_tirs_contres_def, nbr_tirs_cadres, nbr_tirs_non_cadres, nbr_passes, pc_passes_reussies, nbr_corners, nbr_corners_def"
        "nbr_hors_jeu, nbr_occasions, nbr_occasions_def, nbr_duels_gagnes, nbr_duels_perdus, nbr_fautes_commises,"
        "nbr_cjaunes, nbr_crouges, classement_avant_match, classement_apres_match, tactique "
        " FROM stat_equipe_par_match WHERE code_equipe = (%s) and id_match = (%s)",
        (code_equipe, id_match))

    try:
        stat = cur.fetchone()
        cur.close()
        return Stat_equipe(stat[0], stat[1], stat[2], stat[3], stat[4], stat[5],
                           stat[6], stat[7], stat[8], stat[9], stat[10], stat[11],
                           stat[12], stat[13], stat[14], stat[15], stat[16], stat[17],
                           stat[18], stat[19], stat[20], stat[21], stat[22], stat[23], stat[24], stat[25], stat[26], stat[27])

    except:
        print("La stat d'équipe n'existe pas en base")
