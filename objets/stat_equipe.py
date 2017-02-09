import psycopg2


class Stat_equipe:
    """Classe définissant une équipe caractérisée par :
    - son nom ;
    - son poste ;
    - sa date de naissance ;
    - sa taille ;
    - son poids """

    def __init__(self, code_equipe, code_adversaire, id_match, domicile, victoire,
                 possession, nbr_buts_mis, nbr_buts_pris, nbr_tirs, nbr_tirs_cadres,
                 nbr_passes, nbr_passes_reussies, pc_passes_reussies, nbr_hors_jeu,
                 nbr_duels_gagnes, nbr_fautes_commises, classement_avant_match,
                 classement_apres_match):
        self.code_equipe = code_equipe
        self.code_adversaire = code_adversaire
        self.id_match = id_match
        self.domicile = domicile
        self.victoire = victoire
        self.possession = possession
        self.nbr_buts_mis = nbr_buts_mis
        self.nbr_buts_pris = nbr_buts_pris
        self.nbr_tirs = nbr_tirs
        self.nbr_tirs_cadres = nbr_tirs_cadres
        self.nbr_passes = nbr_passes
        self.nbr_passes_reussies = nbr_passes_reussies
        self.pc_passes_reussies = pc_passes_reussies
        self.nbr_hors_jeu = nbr_hors_jeu
        self.nbr_duels_gagnes = nbr_duels_gagnes
        self.nbr_fautes_commises = nbr_fautes_commises
        self.classement_avant_match = classement_avant_match
        self.classement_apres_match = classement_apres_match

    def create_stat(self, conn):
        """Méthode appelée quand on souhaite ajouter une state dans la base"""
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO stat_equipe_par_match (code_equipe, code_adversaire, id_match, domicile,"
            "victoire, possession, nbr_buts_mis, nbr_buts_pris, nbr_tirs, "
            "nbr_tirs_cadres, nbr_passes, nbr_passes_reussies, pc_passes_reussies,"
            "nbr_hors_jeu, nbr_duels_gagnes, nbr_fautes_commises, classement_avant_match,"
            "classement_apres_match) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                self.code_equipe, self.code_adversaire, self.id_match, self.domicile, self.victoire,
                self.possession, self.nbr_buts_mis, self.nbr_buts_pris, self.nbr_tirs, self.nbr_tirs_cadres,
                self.nbr_passes, self.nbr_passes_reussies, self.pc_passes_reussies, self.nbr_hors_jeu,
                self.nbr_duels_gagnes, self.nbr_fautes_commises, self.classement_avant_match,
                self.classement_apres_match
            ))
        conn.commit()
        cur.close()


def get_stat_fromDB(code_equipe, id_match, conn):
    """Méthode pour récupérer les stats d'équipe de la base"""
    cur = conn.cursor()
    cur.execute(
        "SELECT code_equipe, code_adversaire, id_match, domicile,"
        "victoire, possession, nbr_buts_mis, nbr_buts_pris, nbr_tirs, "
        "nbr_tirs_cadres, nbr_passes, nbr_passes_reussies, pc_passes_reussies,"
        "nbr_hors_jeu, nbr_duels_gagnes, nbr_fautes_commises, classement_avant_match,"
        "classement_apres_match "
        " FROM stat_equipe_par_match WHERE code_equipe = (%s) and id_match = (%s)",
        (code_equipe, id_match))

    try:
        stat = cur.fetchone()
        cur.close()
        return Stat_equipe(stat[0], stat[1], stat[2], stat[3], stat[4], stat[5],
                           stat[6], stat[7], stat[8], stat[9], stat[10], stat[11],
                           stat[12], stat[13], stat[14], stat[15], stat[16], stat[17])

    except:
        print("La stat d'équipe n'existe pas en base")
