import psycopg2


class Stat_joueur:
    """Classe définissant une statistique de joueur"""

    def __init__(self, id_joueur, id_match, code_equipe, arrets, arrets_decisifs, ballons_touches,
                 ballons_perdus, buts_int_surface, buts_hors_surface, centres, centres_reussis,
                 duels_aeriens_perdus, duels_aeriens_gagnes, duels_gagnes, duels_perdus,
                 fautes, fautes_subies, passes, passes_decisives, passes_reussies,
                 tirs_cadres_hors_surface, tirs_cadres_int_surface, tirs_non_cadres_hors_surface,
                 tirs_non_cadres_int_surface, tacles, tacles_reussis
                 ):
        self.id_joueur = id_joueur
        self.id_match = id_match
        self.code_equipe = code_equipe
        self.arrets = arrets
        self.arrets_decisifs = arrets_decisifs
        self.ballons_touches = ballons_touches
        self.ballons_perdus = ballons_perdus
        self.buts_int_surface = buts_int_surface
        self.buts_hors_surface = buts_hors_surface
        self.centres = centres
        self.centres_reussis = centres_reussis
        self.duels_aeriens_perdus = duels_aeriens_perdus
        self.duels_aeriens_gagnes = duels_aeriens_gagnes
        self.duels_gagnes = duels_gagnes
        self.duels_perdus = duels_perdus
        self.fautes = fautes
        self.fautes_subies = fautes_subies
        self.passes = passes
        self.passes_decisives = passes_decisives
        self.passes_reussies = passes_reussies
        self.tirs_cadres_hors_surface = tirs_cadres_hors_surface
        self.tirs_cadres_int_surface = tirs_cadres_int_surface
        self.tirs_non_cadres_hors_surface = tirs_non_cadres_hors_surface
        self.tirs_non_cadres_int_surface = tirs_non_cadres_int_surface
        self.tacles = tacles
        self.tacles_reussis = tacles_reussis


    def create_request_insert(self):
        request_insert = "INSERT INTO stat_joueur_par_match ("
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

        try:
            request_insert, values = self.create_request_insert()
            cur = conn.cursor()
            cur.execute(request_insert, values)
            conn.commit()
            cur.close()
        except psycopg2.Error as e:
            print(e.pgerror)


def get_stat_fromDB(id_joueur, id_match, conn):
    """Méthode pour récupérer les stats d'équipe de la base"""
    cur = conn.cursor()
    cur.execute(
        "SELECT id_joueur, id_match, code_equipe, arrets, arrets_decisifs, ballons_touches,"
        "ballons_perdus, buts_int_surface, buts_hors_surface, centres, centres_reussis,"
        "duels_aeriens_perdus, duels_aeriens_gagnes, duels_gagnes, duels_perdus,"
        "fautes, fautes_subies, passes, passes_decisives, passes_reussies,"
        "tirs_cadres_hors_surface, tirs_cadres_int_surface, tirs_non_cadres_hors_surface,"
        "tirs_non_cadres_int_surface, tacles, tacles_reussis WHERE id_joueur = (%s) and id_match = (%s)",
        (id_joueur, id_match))

    try:
        stat = cur.fetchone()
        cur.close()
        return Stat_joueur(stat[0], stat[1], stat[2], stat[3], stat[4], stat[5],
                           stat[6], stat[7], stat[8], stat[9], stat[10], stat[11],
                           stat[12], stat[13], stat[14], stat[15], stat[16], stat[17],
                           stat[18], stat[19], stat[20], stat[21], stat[22], stat[23], stat[24], stat[25])

    except:
        print("La stat de joueur n'existe pas en base")
